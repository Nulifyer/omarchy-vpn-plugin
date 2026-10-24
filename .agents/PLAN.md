# Project plan

## Goal

Publish the existing VPN panel and repaired networking policy as the public MIT-licensed Nulifyer/omarchy-vpn-plugin repository, then install it from GitHub through Omarchy.

## Scope

Include the existing Off, Auto, and On modes, trusted-network policy, WireGuard health checks, DNS policy, kill switch, exact endpoint reply allowance, system setup and removal, documentation, and focused tests.

Exclude VPN subscriptions, server provisioning, profile/key distribution, new VPN protocols, and changing packaged Omarchy files.

## Product boundaries

Target Omarchy 4.0.6 and its schemaVersion 1 plugin contract, NetworkManager, systemd, nftables, UFW, and DNSCrypt-proxy. Support one existing IPv4 full-tunnel WireGuard profile. Preserve local configuration during adoption and upgrades. System setup is an explicit privileged command, independent of loading the panel.

## Architecture boundaries

Keep the Omarchy widget independent of root-owned systemd helpers. Installation is explicit, idempotent, and preserves local secrets and mode. See docs/design.md.

## Success conditions

- The repository validates with Omarchy and has an MIT license.
- Installation, repeated installation, and restoration pass staged filesystem tests.
- No machine-specific networking data is published.
- GitHub confirms a public repository, and Omarchy installs its Git checkout.
- The installed panel loads and the backend reports healthy protected traffic.
- Reconnection succeeds while direct traffic remains blocked.

## Phases

1. Package the plugin and system lifecycle, then run focused checks.
2. Publish the verified repository and install through `omarchy plugin add`.
3. Verify the installed checkout and live VPN behavior.

## Open planning questions

None.
