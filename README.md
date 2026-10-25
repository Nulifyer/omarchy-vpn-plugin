# Omarchy VPN plugin

A native Omarchy bar panel for an existing NetworkManager WireGuard connection.
It shows tunnel health, handshake age, DNS, routing, and kill-switch state.
The system backend reconnects automatically and blocks ordinary traffic while
the tunnel is unhealthy.

## Modes

- **Off** uses direct networking.
- **Auto** uses direct networking on trusted NetworkManager connection UUIDs and
  requires the VPN on other Wi-Fi and Ethernet networks.
- **On** requires the VPN on every network.

Left-click the shield to open the panel. Right-click to cycle Off, Auto, and On.
Inside the panel, use arrows or `j`/`k`, Enter, and Escape. `a` selects Auto,
`o` selects On, `f` selects Off, and `r` refreshes status.

## Requirements

- Omarchy 4 with its Quickshell plugin host and `qs.Ui` components. Tested with
  Omarchy 4.0.6-1. This does not target the older Waybar-based desktop.
- One existing NetworkManager WireGuard profile with one IPv4 endpoint,
  `0.0.0.0/0` peer routes, a fixed client listen port, and an IPv4 VPN DNS server
  that answers ICMP health probes.
- NetworkManager using systemd-resolved, an active UFW firewall, nftables,
  wireguard-tools, DNSCrypt-proxy, Polkit, Python 3.11+, jq, and standard Arch
  command-line tools.
- DNSCrypt-proxy listening on `127.0.0.1:53` and `[::1]:53`, with encrypted DNS
  upstream addresses matching `DOH_IPV4`. A Quad9 configuration is included.

Install missing packages through Omarchy:

```bash
omarchy pkg add wireguard-tools nftables ufw dnscrypt-proxy python jq
```

WireGuard profiles and keys remain in NetworkManager. This repository does not
provide a VPN account, import credentials, or provision a VPN server.

## Install the plugin

```bash
omarchy plugin add https://github.com/Nulifyer/omarchy-vpn-plugin.git --enable
omarchy bar move nulifyer.vpn --after omarchy.network
```

Omarchy clones the repository into `~/.config/omarchy/plugins/nulifyer.vpn`,
validates its root manifest, and enables the widget. System setup is a separate
administrator operation. Loading the widget never installs privileged code.

## Set up the system backend

If `/etc/nulifyer-vpn/config` already exists from this VPN setup, adopt it with:

```bash
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py install --user "$USER"
```

For a new setup, copy the example outside the Git checkout:

```bash
mkdir -p ~/.config/nulifyer-vpn
cp ~/.config/omarchy/plugins/nulifyer.vpn/examples/config ~/.config/nulifyer-vpn/config
${EDITOR:-nano} ~/.config/nulifyer-vpn/config
```

Set the connection name, interface, endpoint, ports, and VPN DNS address to
match your existing WireGuard profile. The installer checks these against
NetworkManager before changing system files. Configure the profile's VPN DNS
as the default DNS route with a negative priority, for example:

```bash
nmcli connection modify wgclient ipv4.dns 10.66.0.1 \
  ipv4.dns-search '~.' ipv4.dns-priority -100
```

Find a trusted network's UUID with:

```bash
nmcli -g connection.uuid connection show 'Home Wi-Fi'
```

Leave `TRUSTED_UUIDS` empty to trust no networks. If you add trusted UUIDs, set
`TRUSTED_DNS` to that network's DNS server. Set `TRUSTED_INTERFACE` and
`TRUSTED_GATEWAY` together only when the home router needs a WireGuard hairpin
reply exception. Other networks are treated as public.

Install the helpers and bundled Quad9 DoH configuration:

```bash
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py install --user "$USER" \
  --config "$HOME/.config/nulifyer-vpn/config" --configure-dnscrypt
```

Omit `--configure-dnscrypt` when you already have a compatible DNSCrypt-proxy
configuration. The installer preserves the existing VPN mode. A new backend
starts in Auto mode. It preserves the WireGuard profile and its keys.

## Updates

```bash
omarchy plugin update nulifyer.vpn
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py install --user "$USER"
sudo python3 scripts/system.py check
```

The first command updates the panel and repository files. The explicit system
install updates the root-owned helpers and services. It preserves the local
configuration, current mode, and the original installation backup.

## Check the connection

```bash
nulifyer-vpn-status --json
nulifyer-vpn verify
systemctl status nulifyer-vpn-monitor.timer
```

A healthy tunnel reports `connected`, a reachable probe, a recent handshake,
`guard=ready`, and protected traffic. NetworkManager activation alone does not
prove the tunnel works. The backend requires both a successful probe and a
recent WireGuard handshake before opening the guard.

To reconnect while retaining the selected mode and kill switch:

```bash
nulifyer-vpn reconnect
```

The panel also shows waiting, connecting, failed, and stale or unavailable
status. Inspect system logs with:

```bash
journalctl -b -u nulifyer-vpn-monitor -u NetworkManager
```

## Remove or disable

Disabling or removing the bar widget leaves the system protection running:

```bash
omarchy plugin disable nulifyer.vpn
```

To remove the system setup, restore saved files and settings first:

```bash
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py uninstall
omarchy plugin remove nulifyer.vpn
```

The uninstaller restores files and service settings saved before installation,
restores managed DNS settings and the original VPN autoconnect policy, and
keeps its backup locally. When adopting an earlier installation, it restores
those earlier helpers and their enabled services. It does not delete your
WireGuard connection, keys, or unrelated VPN data.

## Networking behavior

The kill switch is installed before NetworkManager at boot. A systemd timer
checks network policy and tunnel health every five seconds. NetworkManager
pre-up and transition hooks close the guard before the physical network changes.

While connecting, the guard permits loopback, DHCP, required IPv6 neighbor
discovery, the configured encrypted DNS bootstrap, the exact WireGuard
endpoint, and the marked tunnel health probe. Ordinary direct traffic remains
blocked. Protected traffic can use the WireGuard interface after its health
check passes. IPv6 traffic outside that interface remains blocked in protected
modes. The current configuration contract is for an IPv4 tunnel.

Some startup replies are rejected by UFW's connection tracking. The backend
adds an exception for the endpoint IP, endpoint UDP source port, and client UDP
destination port before UFW's invalid-packet drop. It uses the locally cached
endpoint before the tunnel exists and reconciles the rule when the endpoint
changes or UFW reloads. It also supports the optional trusted-router hairpin
reply rule. The monitor has 45 seconds to finish its 15-second activation
attempt and subsequent health checks.

Encrypted DNS bootstrap HTTPS connections use the physical default route,
even while WireGuard owns the full-tunnel route. The exception covers only
TCP port 443 at the configured `DOH_IPV4` addresses. The guard removes its
policy-routing rules in Off mode and during uninstall. Other traffic to those
addresses still follows the normal VPN policy.

If an activated peer has no resolved endpoint at startup, the monitor seeds
its runtime endpoint from the local cache. It preserves the hostname in the
NetworkManager profile and never replaces an already resolved endpoint.
A tunnel that remains unhealthy for `CONNECT_TIMEOUT` is deactivated with the
guard closed. Subsequent monitor passes reconnect it, with recovery attempts
limited to once per minute. These retries preserve the selected mode.

## Development

```bash
python3 scripts/check.py
```

Checks cover shell syntax, the manifest, QML parsing when Qt tools are present,
staged installation and restoration, and policy regression cases. On Omarchy,
the same command runs the native plugin validator. The staged tests change no
host services, network profiles, or firewall rules. See
[the design notes](docs/design.md) for ownership and compatibility details.

MIT licensed. See [LICENSE](LICENSE).
