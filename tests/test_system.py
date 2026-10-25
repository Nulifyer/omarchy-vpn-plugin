import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("vpn_system", REPO / "scripts/system.py")
system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(system)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.host = system.System(self.root)
        self.args = argparse.Namespace(user="testuser", config=str(REPO / "examples/config"), configure_dnscrypt=True)

    def test_install_update_and_uninstall_restore_existing_files(self):
        target = self.host.path("/usr/local/bin/nulifyer-vpn")
        target.parent.mkdir(parents=True)
        target.write_text("old helper\n")
        target.chmod(0o750)
        mode = self.host.path("/var/lib/nulifyer-vpn/mode")
        mode.parent.mkdir(parents=True)
        mode.write_text("on\n")
        link = self.host.path("/etc/NetworkManager/dispatcher.d/pre-up.d/90-nulifyer-vpn")
        link.parent.mkdir(parents=True)
        link.symlink_to("../previous-dispatcher")
        self.host.install(self.args)
        self.host.check()
        self.assertEqual(mode.read_text(), "on\n")
        self.assertFalse(target.is_symlink())
        config = self.host.path(system.CONFIG)
        config.write_text(config.read_text().replace("HANDSHAKE_MAX_AGE=150", "HANDSHAKE_MAX_AGE=180"))
        self.args.config = None
        self.host.install(self.args)
        self.assertEqual(system.read_config(config)["HANDSHAKE_MAX_AGE"], "180")
        self.host.check()
        self.host.uninstall()
        self.assertEqual(target.read_text(), "old helper\n")
        self.assertEqual(target.stat().st_mode & 0o777, 0o750)
        self.assertEqual(os.readlink(link), "../previous-dispatcher")
        self.assertEqual(mode.read_text(), "on\n")
        self.assertFalse(config.exists())
        self.assertFalse(self.host.state.exists())

    def test_fresh_install_uses_auto_and_removes_only_owned_files(self):
        unrelated = self.host.path("/var/lib/nulifyer-vpn/unrelated")
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("keep")
        self.host.install(self.args)
        self.assertEqual(self.host.path("/var/lib/nulifyer-vpn/mode").read_text(), "auto\n")
        self.assertIn('subject.user === "testuser"', self.host.path("/etc/polkit-1/rules.d/49-nulifyer-vpn.rules").read_text())
        self.host.uninstall()
        self.assertEqual(unrelated.read_text(), "keep")
        self.assertFalse(self.host.path("/usr/local/libexec/nulifyer-vpn-control").exists())

    def test_check_detects_modified_helper(self):
        self.host.install(self.args)
        self.host.path("/usr/local/libexec/nulifyer-vpn-control").write_text("changed")
        with self.assertRaisesRegex(ValueError, "differs"):
            self.host.check()

    def test_invalid_config_fails_before_installing_files(self):
        config = self.root / "bad-config"
        config.write_text((REPO / "examples/config").read_text().replace("VPN_INTERFACE='wgclient'", "VPN_INTERFACE='wg;bad'"))
        self.args.config = str(config)
        with self.assertRaises(ValueError):
            self.host.install(self.args)
        self.assertFalse(self.host.state.exists())

    def test_config_is_parsed_without_executing_shell(self):
        config = self.root / "bad-config"
        sentinel = self.root / "executed"
        config.write_text((REPO / "examples/config").read_text().replace("vpn.example.com", "$(touch " + str(sentinel) + ")"))
        with self.assertRaises(ValueError):
            system.read_config(config)
        self.assertFalse(sentinel.exists())


class ProfileValidationTests(unittest.TestCase):
    def setUp(self):
        self.config = system.read_config(REPO / "examples/config")
        self.peers = "test-peer allowed-ips=0.0.0.0/0 endpoint=vpn.example.com:51820\n"

    def query(self, *args, **kwargs):
        if args[0] == "ufw":
            value = "Status: active\n"
        else:
            field = args[args.index("-g") + 1]
            values = {"connection.type": "wireguard", "wireguard.listen-port": "51820",
                      "connection.interface-name": "wgclient", "ipv4.dns": "10.66.0.1",
                      "wireguard.peer-routes": "yes", "ipv4.dns-priority": "-100",
                      "ipv4.dns-search": "~.", "wireguard.peers": self.peers}
            value = values[field]
            # Match nmcli's observed default escaping of colon separators.
            if "--escape" not in args or args[args.index("--escape") + 1] != "no":
                value = value.replace(":", "\\:")
            value += "\n"
        return subprocess.CompletedProcess(args, 0, value, "")

    def validate(self):
        with tempfile.TemporaryDirectory() as root:
            with patch.object(system, "run", side_effect=self.query), patch.object(system.shutil, "which", return_value="/usr/bin/tool"):
                system.System(root).preflight(self.config, REPO / "examples/dnscrypt-proxy.toml")

    def test_matching_endpoint_passes_without_nmcli_separator_escaping(self):
        self.validate()

    def test_different_endpoint_is_still_rejected(self):
        self.peers = self.peers.replace("vpn.example.com", "other.example.com")
        with self.assertRaisesRegex(ValueError, "matching VPN_ENDPOINT_HOST"):
            self.validate()

    def test_multiple_peers_or_missing_default_route_are_rejected(self):
        original = self.peers
        for peers in [original + original, original.replace("0.0.0.0/0", "10.66.0.0/24")]:
            self.peers = peers
            with self.subTest(peers=peers), self.assertRaisesRegex(ValueError, "full-tunnel peer"):
                self.validate()


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for command in ["nmcli", "ip", "wg", "ping", "iptables", "nft", "test-guard", "test-home-reply"]:
            (self.bin / command).symlink_to(REPO / "tests/fake_system.py")
        self.state_file = self.root / "fake-state.json"
        self.state_file.write_text("{}")
        self.config_dir = self.root / "etc"
        self.config_dir.mkdir()
        self.config = self.config_dir / "config"
        self.config.write_text((REPO / "examples/config").read_text())
        self.run_dir = self.root / "run"
        self.run_dir.mkdir()
        self.var = self.root / "var"
        self.var.mkdir()
        (self.var / "mode").write_text("auto\n")
        (self.var / "endpoint-ip").write_text("198.51.100.1\n")
        self.env = {**os.environ, "PATH": str(self.bin) + ":" + os.environ["PATH"], "VPN_TEST_STATE": str(self.state_file)}

    def state(self, **values):
        current = json.loads(self.state_file.read_text())
        current.update(values)
        self.state_file.write_text(json.dumps(current))
        return current

    def execute(self, name, *args):
        source = (REPO / "libexec" / ("nulifyer-vpn-" + name)).read_text()
        source = source.replace('/etc/nulifyer-vpn', str(self.config_dir))
        source = source.replace('/run/nulifyer-vpn', str(self.run_dir))
        source = source.replace('/var/lib/nulifyer-vpn', str(self.var))
        source = source.replace('/usr/local/libexec/nulifyer-vpn-guard', str(self.bin / "test-guard"))
        source = source.replace('/usr/local/libexec/nulifyer-vpn-home-reply', str(self.bin / "test-home-reply"))
        source = source.replace('[[ $EUID -eq 0 ]]', '[[ 0 -eq 0 ]]')
        script = self.root / (name + ".bash")
        script.write_text(source)
        self.output = subprocess.run(["bash", str(script), *args], check=True, env=self.env, capture_output=True, text=True).stdout
        return self.state()

    def status(self):
        return (self.run_dir / "status").read_text().splitlines()[0]

    def test_public_auto_connects_and_opens_guard_only_after_health_checks(self):
        state = self.execute("monitor")
        self.assertTrue(state["active"])
        self.assertEqual(state["guard"], "ready")
        self.assertEqual(self.status(), "connected")
        guards = [call[1] for call in state["calls"] if call[0] == "test-guard"]
        self.assertEqual(guards, ["connecting", "ready"])

    def test_no_upstream_keeps_guard_closed(self):
        self.state(upstream=False, active=True)
        state = self.execute("monitor")
        self.assertEqual(state["guard"], "connecting")
        self.assertFalse(state["active"])
        self.assertEqual(self.status(), "waiting")

    def test_off_deactivates_tunnel_and_releases_guard(self):
        (self.var / "mode").write_text("off\n")
        self.state(active=True)
        state = self.execute("monitor")
        self.assertFalse(state["active"])
        self.assertEqual(state["guard"], "off")
        self.assertEqual(self.status(), "off")

    def test_activation_failure_keeps_guard_closed(self):
        self.state(activation_ok=False)
        state = self.execute("monitor")
        self.assertEqual(state["guard"], "connecting")
        self.assertEqual(self.status(), "connecting")

    def test_on_requires_vpn_even_on_trusted_network(self):
        trusted = "11111111-1111-4111-8111-111111111111"
        self.config.write_text(self.config.read_text().replace("TRUSTED_UUIDS=''", "TRUSTED_UUIDS='" + trusted + "'"))
        (self.var / "mode").write_text("on\n")
        state = self.execute("monitor")
        self.assertTrue(state["active"])
        self.assertEqual(state["guard"], "ready")

    def test_trusted_auto_disables_tunnel(self):
        trusted = "11111111-1111-4111-8111-111111111111"
        self.config.write_text(self.config.read_text().replace("TRUSTED_UUIDS=''", "TRUSTED_UUIDS='" + trusted + "'"))
        self.state(active=True)
        state = self.execute("monitor")
        self.assertFalse(state["active"])
        self.assertEqual(state["guard"], "off")
        self.assertEqual(self.status(), "off")

    def test_failed_probe_or_stale_handshake_never_opens_guard(self):
        for values in [{"reachable": False, "handshake_age": 1}, {"reachable": True, "handshake_age": 200}]:
            with self.subTest(values=values):
                self.state(active=True, **values)
                state = self.execute("monitor")
                self.assertEqual(state["guard"], "connecting")
                self.assertEqual(self.status(), "connecting")

    def test_unresolved_active_peer_uses_cached_endpoint_without_rewriting_profile(self):
        self.state(active=True, live_endpoint=False)
        state = self.execute("monitor")
        self.assertEqual(state["endpoint"], "198.51.100.1")
        self.assertEqual(state["guard"], "ready")
        self.assertIn(["wg", "set", "wgclient", "peer", "test-peer", "endpoint", "198.51.100.1:51820"], state["calls"])
        self.assertFalse(any(call[0] == "nmcli" and "wireguard.peers" in call for call in state["calls"]))

    def test_resolved_endpoint_is_not_replaced_by_cache(self):
        self.state(active=True, endpoint="198.51.100.2")
        state = self.execute("monitor")
        self.assertFalse(any(call[:2] == ["wg", "set"] for call in state["calls"]))

    def test_stuck_active_tunnel_retries_with_guard_closed_and_rate_limit(self):
        self.state(active=True, reachable=False)
        (self.run_dir / "unhealthy-since").write_text(str(int(time.time()) - 120))
        state = self.execute("monitor")
        self.assertFalse(state["active"])
        self.assertEqual(state["guard"], "connecting")
        self.assertEqual(self.status(), "failed")
        self.assertEqual((self.var / "mode").read_text(), "auto\n")
        self.state(active=True, calls=[])
        state = self.execute("monitor")
        self.assertTrue(state["active"])
        self.assertFalse(any(call[0] == "nmcli" and "down" in call for call in state["calls"]))

    def test_bootstrap_routes_are_port_scoped_idempotent_and_removed(self):
        state = self.execute("guard", "connecting")
        self.assertEqual(len(state["bootstrap_rules"]), 2)
        for rule in state["bootstrap_rules"]:
            self.assertEqual(rule[-8:], ["ipproto", "tcp", "dport", "443", "table", "main", "protocol", "242"])
        self.assertEqual(len(self.execute("guard", "connecting")["bootstrap_rules"]), 2)
        self.config.write_text(self.config.read_text().replace("9.9.9.9, 149.112.112.9", "192.0.2.53"))
        rules = self.execute("guard", "connecting")["bootstrap_rules"]
        self.assertEqual(len(rules), 1)
        self.assertIn("192.0.2.53/32", rules[0])
        self.assertEqual(self.execute("guard", "off")["bootstrap_rules"], [])

    def test_verify_reports_inactive_tunnel_instead_of_exiting_silently(self):
        failing_wg = self.bin / "wg"
        failing_wg.unlink()
        failing_wg.write_text("#!/bin/sh\nexit 1\n")
        failing_wg.chmod(0o755)
        systemctl = self.bin / "systemctl"
        systemctl.write_text("#!/bin/sh\necho active\n")
        systemctl.chmod(0o755)
        (self.run_dir / "status").write_text(f"off\n{int(time.time())}\n0\nunavailable\n")
        (self.run_dir / "guard-mode").write_text("off\n")
        self.execute("control", "verify")
        self.assertIn("vpn_nm=\n", self.output)
        self.assertIn("handshake_age_seconds=none\n", self.output)
        self.assertIn("guard=off\n", self.output)

    def test_exact_endpoint_reply_is_idempotent_updates_and_removes(self):
        self.execute("home-reply")
        state = self.execute("home-reply")
        self.assertEqual(len(state["input_rules"]), 1)
        self.assertEqual(state["insert_positions"], ["3"])
        self.assertIn("198.51.100.1", state["input_rules"][0])
        self.assertIn("--sport", state["input_rules"][0])
        self.state(endpoint="198.51.100.2")
        state = self.execute("home-reply")
        self.assertEqual(len(state["input_rules"]), 1)
        self.assertIn("198.51.100.2", state["input_rules"][0])
        (self.var / "mode").write_text("off\n")
        self.assertEqual(self.execute("home-reply")["input_rules"], [])

    def test_reply_exception_uses_cached_endpoint_before_tunnel_exists(self):
        self.state(live_endpoint=False)
        state = self.execute("home-reply")
        self.assertIn("198.51.100.1", state["input_rules"][0])

    def test_dns_snapshot_and_restore_preserve_ipv6_address(self):
        profile = "11111111-1111-4111-8111-111111111111"
        original = {f"ipv{version}.{key}": value for version in (4, 6)
                    for key, value in [("ignore-auto-dns", "no"), ("dns", ""),
                                       ("dns-search", ""), ("dns-priority", "0")]}
        original["ipv6.dns"] = "2001:db8::53"
        self.state(properties=original)
        self.execute("configure-dns", profile)
        self.assertEqual((self.var / "profiles" / profile / "ipv6_dns").read_text(), "2001:db8::53\n")
        state = self.execute("configure-dns", "--restore-all")
        self.assertEqual(state["properties"]["ipv6.dns"], "2001:db8::53")

    def test_guard_blocks_normal_tunnel_traffic_until_ready(self):
        state = self.execute("guard", "connecting")
        self.assertNotIn('oifname "wgclient" accept', [line.strip() for line in state["nft_rules"].splitlines()])
        self.assertIn("counter drop", state["nft_rules"])
        self.assertIn("198.51.100.1 udp dport 51820 accept", state["nft_rules"])
        state = self.execute("guard", "ready")
        self.assertIn('oifname "wgclient" accept', state["nft_rules"])
        self.assertFalse(self.execute("guard", "off")["table"])


if __name__ == "__main__":
    unittest.main()
