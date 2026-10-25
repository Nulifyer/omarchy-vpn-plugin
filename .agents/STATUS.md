# Project status

Updated: 2026-10-25
State: installed and verified, cold boot pending

## Project state

Release 1.5.2 is public and installed through Omarchy. Its root-owned helpers match the GitHub checkout. Auto mode currently reports healthy protected traffic.

## Current batch

Repair DNS bootstrap routing and recovery of unhealthy activated tunnels.

## In progress

None. See docs/verification.md for exact checks and limits.

## Next action

Check VPN startup after the next user-initiated reboot.

## Blockers

None. Full cold-boot behavior remains unverified for this release.

## Verification

The regression suite and CI passed. Live checks verified encrypted DNS bootstrap routing, guarded reconnection, ordinary traffic protection, and return to healthy Auto mode. Detailed evidence belongs in docs/verification.md.
