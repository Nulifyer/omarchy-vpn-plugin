# Project status

Updated: 2026-10-24
State: correcting live preflight

## Project state

The public MIT repository is installed through Omarchy. The initial hosted CI passed. Authentication succeeded, but preflight rejected a matching endpoint because nmcli escapes colon separators by default.

## Current batch

Publish the unescaped-value fix and finish live system adoption.

## In progress

Version 1.5.1 requests unescaped nmcli values consistently. Regression coverage includes endpoint validation and IPv6 DNS restoration. See docs/verification.md.

## Next action

Push the verified correction, update the installed plugin through Omarchy, and rerun its system installer.

## Blockers

None beyond the desktop authentication required by system installation.

## Verification

The 19 focused tests and native plugin checks pass. Live system installation, reconnection, and traffic-blocking checks remain pending. A full reboot remains untested.
