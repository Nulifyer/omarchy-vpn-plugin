# Project decisions

## Binding decisions

- User requested `/home/nulifyer/Project/omarchy-vpn-plugin`, public GitHub publication, MIT licensing, installation from GitHub through Omarchy, and post-install verification.
- Retain the existing plugin ID and backend paths to adopt the working installation without a parallel VPN controller.
- Keep personal configuration and existing WireGuard secrets on the host. Publish examples only.
- Keep the bar plugin lifecycle separate from privileged system setup. Disabling a widget must not disable network protection.
- Keep the current panel design and behavior. Reuse Omarchy UI primitives and its plugin CLI.

## Open decisions

None.

## Superseded decisions

None.
