# Release verification

Version: 1.5.2
Date: 2026-10-25
Code commit: `7654dd3`

## Failure investigated

The installed checkout and root helpers initially matched release 1.5.1.
The VPN was Off when inspected, with its monitor running successfully.
The current boot journal showed an activated WireGuard connection, followed
by DNSCrypt-proxy reporting an unreachable encrypted DNS upstream. DNS became
available after Off was selected. Selecting Auto then restored connectivity.

Inspection showed that encrypted DNS bootstrap HTTPS traffic used the
WireGuard full-tunnel table. The firewall permitted that traffic, but routing
still depended on the tunnel. The monitor also left an activated but unhealthy
tunnel running indefinitely. This sequence is consistent with a DNS bootstrap
dependency. The failed peer's runtime endpoint was not captured before Off,
so an unresolved endpoint during that boot remains an inference.

## Automated checks

- Omarchy native plugin validation and Qt 6 QML parsing passed.
- Bash syntax checks passed for all eight scripts.
- All 24 installer, profile validation, DNS restoration, and policy tests passed.
- New cases cover port-scoped bootstrap rule reconciliation and removal,
  cached endpoint seeding, preservation of resolved endpoints, guarded retry
  rate limits, and diagnostic output with an absent tunnel.
- GitHub CI passed for the release code:
  https://github.com/Nulifyer/omarchy-vpn-plugin/actions/runs/40220385766.
- Project continuity validation and Git whitespace checks passed.

## Live installation and checks

The release was published to the existing public MIT repository and installed
with `omarchy plugin update nulifyer.vpn --yes`. The system installer completed
from that GitHub checkout and verified its receipt. Installed helper and unit
bytes matched the checkout, and those files were root-owned. Local VPN
configuration and Auto mode were preserved. Native panel open and close IPC
commands completed successfully.

IPv4 policy inspection selected the physical Wi-Fi default route for TCP port
443 at a configured encrypted DNS upstream. UDP port 53 at the same address
and ordinary external traffic still selected the WireGuard full-tunnel table.
A certificate-verified HTTPS DNS request to the bootstrap upstream returned
HTTP 200 over Wi-Fi. Ordinary HTTP traffic bound to Wi-Fi timed out, while the
same HTTP target returned 301 through WireGuard.

A live reconnect retained Auto mode and initially reported a closed connecting
guard with no active VPN interface. An encrypted DNS HTTPS request succeeded
during reconnection, while the ordinary Wi-Fi HTTP request remained blocked.
The tunnel returned to connected status with a reachable probe, recent
handshake, protected traffic, VPN DNS, and ready guard. A subsequent DNS query
used the WireGuard link. The monitor completed successfully with its 45-second
timeout, and there were no failed system services.

## Remaining limits

A full reboot has not been tested with release 1.5.2. The reconnect and routing
checks establish live behavior, not cold-boot ordering. Cached endpoint seeding
and timed recovery were verified through command doubles rather than by
removing a live peer or disabling the VPN server. Uninstall and file restoration
were tested in staged filesystems. Another physical network remains untested.
