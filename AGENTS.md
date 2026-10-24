# Repository instructions

Read `.agents/README.md` for the current project contract and work state.

- This is a third-party Omarchy 4 shell plugin. Keep `manifest.json` and `Panel.qml` at the repository root.
- Preserve plugin ID `nulifyer.vpn` and the established system helper names for in-place upgrades.
- Never commit machine configuration, WireGuard profiles or keys, endpoint caches, credentials, or runtime state.
- Privileged files must be copied into root-owned locations. Never execute user-writable plugin files through a passwordless root helper.
- Keep the panel on Omarchy's shared `qs.Ui` and `qs.Commons` interfaces. Networking policy belongs to systemd and NetworkManager.
- Run `python3 scripts/check.py` before delivery. Public commits use scoped Conventional Commits.
