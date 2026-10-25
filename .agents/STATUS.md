# Project status

Updated: 2026-10-25
State: recovery fix awaiting installation

## Project state

The public MIT repository and installed checkout match release 1.5.1. This boot stalled before DNS became available. Selecting Auto after DNS recovery restored protected connectivity.

## Current batch

Release 1.5.2 repairs encrypted DNS bootstrap routing, missing runtime endpoint recovery, and retries for unhealthy active tunnels.

## In progress

Publish the tested fix, update the Omarchy checkout, and install the root-owned helpers.

## Next action

Install and verify release 1.5.2 from the GitHub checkout.

## Blockers

System-helper installation requires desktop administrator authentication. A full reboot has not been tested for the fix.

## Verification

The staged suite covers bootstrap-rule lifecycle, cached endpoint seeding, and guarded retry rate limits. Live release verification is pending. Exact results belong in docs/verification.md.
