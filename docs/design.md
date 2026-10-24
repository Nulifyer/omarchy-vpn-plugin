# Plugin and system ownership

`manifest.json` declares one third-party `bar-widget`, with `Panel.qml` as its
entry point and the stable ID `nulifyer.vpn`. It follows the manifest and panel
patterns in the installed Omarchy 4 shell. It uses shared `Panel`,
`BarIconButton`, `KeyboardPanel`, keyboard navigation, theme, and style
interfaces from `qs.Ui` and `qs.Commons`. It does not replace the bar or edit
packaged Omarchy files.

The panel reads `/usr/local/bin/nulifyer-vpn-status --json` without elevation.
Mode changes use a fixed control executable through Polkit. The generated
Polkit rule grants that executable to one named, local, active user. The
executable dispatches only fixed VPN operations. It cannot execute an arbitrary
command supplied by the panel.

The repository and installed plugin checkout belong to the user. System
helpers are regular root-owned files under `/usr/local`, rather than symlinks
to that checkout. Root-owned configuration lives in `/etc/nulifyer-vpn`.
Runtime status and locks live under `/run/nulifyer-vpn`. Persistent mode,
endpoint cache, and private installation backups live under
`/var/lib/nulifyer-vpn`.

The policy monitor owns trusted/public network decisions and tunnel health.
The guard owns its named nftables output table. The reply helper owns its
exact UFW input exceptions. The DNS helper snapshots the properties it manages
and can restore them. Shared locks serialize policy, firewall, and reply-rule
changes. Endpoint reply rules are checked before insertion and replaced when
the live endpoint changes.

`scripts/system.py` owns installation and removal. It parses configuration
without executing shell code, validates inputs and the existing NetworkManager
profile, saves original files once, and writes each privileged file through an
atomic replacement. Repeated installation updates helpers while retaining
the original restoration data. Staging with `--root /temporary/directory`
performs filesystem work only and never operates on the host's services.

Omarchy's plugin add, update, disable, and remove commands manage the widget
checkout. They do not have a privileged system-install hook. Backend upgrades
therefore require an explicit system install after updating the plugin. Widget
disable and shell restarts have no authority over the kill switch.

The project supports one existing NetworkManager-managed IPv4 full-tunnel
WireGuard peer, UFW, nftables, and DNSCrypt-proxy. It does not configure VPN
servers or distribute WireGuard secrets. Trusted networks are identified by
saved NetworkManager UUID, so users must mark them deliberately.

Automated policy tests execute the Bash scripts against command doubles and
temporary paths. They cover policy decisions and emitted rules. A live check
must still validate actual packet handling, the shell's QML loading, and the
installed system services. A full reboot is a separate verification step.
