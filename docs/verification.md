# Release verification

Version: 1.5.1
Date: 2026-10-24

## Automated checks

- Omarchy 4.0.6-1 native plugin validation passed.
- Qt 6 qmlformat parsed Panel.qml successfully.
- Bash syntax checks passed for all eight scripts.
- All 19 installer, profile validation, DNS restoration, and policy tests passed on Python 3.14.
- systemd-analyze verified all four unit files.
- GitHub CI passed for the release code: https://github.com/Nulifyer/omarchy-vpn-plugin/actions/runs/40129319457.
- Public-source inspection found no local VPN endpoint, trusted network UUID, VPN DNS address, trusted gateway, credentials, or WireGuard private keys.

## Live installation

The public MIT-licensed repository was installed through `omarchy plugin add`, then updated through `omarchy plugin update`. The installed checkout matched the published release code at commit `2304b79`.

The system installer ran successfully from the GitHub checkout and verified its installed-file hashes and root ownership. Existing VPN configuration, WireGuard keys, and Auto mode were preserved. The existing bar configuration remained identical, with one VPN widget in its original position.

The panel opened through its native IPC handler and was visually checked. It displayed the selected Auto mode, reachable probe, handshake age, protected traffic, full-tunnel route, VPN DNS, and ready guard. No plugin load or JavaScript errors appeared in the verification interval.

The guard service, reply service, and monitor timer were enabled. The monitor used its 45-second timeout and completed successfully. There were no failed system services after installation and reconnection.

`nulifyer-vpn reconnect` retained Auto mode and first reported `guard=connecting`. A direct HTTP request bound to the physical Wi-Fi interface was blocked. The same HTTP endpoint returned status 301 through the WireGuard interface. The VPN then returned to connected status with a one-second-old handshake, reachable probe, protected traffic, VPN DNS, and a ready guard. Routing inspection selected the WireGuard interface for an external IPv4 address, and systemd-resolved selected the VPN DNS server with the default DNS routing domain.

The first preflight attempt exposed nmcli's default colon escaping. Version 1.5.1 requests unescaped values consistently and includes regression cases for matching endpoints, wrong endpoints, multiple peers, missing default routes, and IPv6 DNS snapshot restoration.

## Remaining limits

A full reboot and use on a different physical network have not been tested for this packaged release. The successful live reconnection does not establish cold-boot behavior. File restoration and uninstall behavior were verified in staged filesystems rather than by removing the live working installation.
