# Release verification

Version: 1.5.1
Date: 2026-10-24

## Automated checks

- Omarchy 4.0.6-1 native plugin validator passed.
- Qt 6 qmlformat parsed Panel.qml successfully.
- Bash syntax checks passed for all eight scripts.
- All 19 installer and policy tests passed on Python 3.14.
- systemd-analyze verified all four unit files.
- Public-source inspection found no local VPN endpoint, trusted network UUID, VPN DNS address, trusted gateway, credentials, or WireGuard private keys.

## Live installation

The public GitHub repository is MIT-licensed and installed through Omarchy. The first system-install attempt stopped during preflight because nmcli escaped the endpoint colon. Version 1.5.1 requests unescaped values and adds endpoint validation and IPv6 DNS restoration regression tests. The corrected live system installation is pending.

## Remaining limits

A full reboot and use on a different physical network have not been tested for this packaged release. Reconnection tests will be reported separately from boot verification.
