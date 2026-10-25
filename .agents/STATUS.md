# Project status

Updated: 2026-10-25
State: installed and verified after reboot

## Project state

Release 1.5.2 is public and installed through Omarchy. Its root-owned helpers match the GitHub checkout. Auto mode currently reports healthy protected traffic.

## Current batch

Verify automatic startup after a user-initiated reboot.

## In progress

None. See docs/verification.md for exact checks and limits.

## Next action

No pending implementation. Diagnose only if another connectivity issue is reported.

## Blockers

None.

## Verification

The regression suite and CI passed. A full reboot now also passed on the current network, with healthy Auto mode, VPN DNS, protected routing, and direct traffic blocked. Detailed evidence belongs in docs/verification.md.
