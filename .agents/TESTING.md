# Testing and evidence

## Evidence standard

Staged installer tests and command doubles prove file restoration, idempotence, and policy decisions without host changes. They do not prove actual packet handling or shell loading.

## Fast checks

```bash
python3 scripts/check.py
```

This runs Bash syntax checks, manifest and QML parsing when tools are present, installer lifecycle tests, and policy regression cases. On Omarchy it also runs the native plugin validator.

## Full checks

Run the fast checks, then verify the installed Git remote and revision, widget bar placement, no new QML errors, root-owned helper receipt, active system services, a recent handshake, reachable probe, VPN DNS, protected routing, and reconnection with direct traffic blocked.

## Environment

Python 3.11+, Bash, and Git. Native UI validation requires Omarchy 4 and Qt tools. System dependencies are listed in README.md.

## Known gaps

A reconnect does not prove boot ordering after a full reboot. Report that limit unless a full reboot was observed. Exact release evidence belongs in docs/verification.md.
