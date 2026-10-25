# Omarchy VPN

Your WireGuard VPN, right in the Omarchy bar.

Connect automatically on public networks, stay off the VPN at home, or require
VPN protection everywhere. A shield in your bar shows whether your connection
is protected, with a panel for switching modes and checking connection health.

## Why use it?

- **Automatic protection.** Connect on untrusted Wi-Fi and Ethernet networks.
- **Your choice of mode.** Switch between Auto, On, and Off from the panel.
- **A built-in kill switch.** Block ordinary internet traffic while a required
  VPN connection is unavailable.
- **Automatic recovery.** Reconnect after startup and recover stalled connections.
- **Bring your own VPN.** Use an existing WireGuard connection in NetworkManager.

This plugin does not provide a VPN account or server.

## What you need

- Omarchy 4 with shell plugin support.
- A NetworkManager WireGuard profile with one IPv4 peer, full-tunnel routing
  (`0.0.0.0/0`), and a fixed client listen port.
- A DNS server reachable through your VPN that responds to ping.
- NetworkManager using systemd-resolved and an active UFW firewall.

Install the supporting packages:

```bash
omarchy pkg add wireguard-tools nftables ufw dnscrypt-proxy python jq
```

## Setup

### 1. Add the plugin

```bash
omarchy plugin add https://github.com/Nulifyer/omarchy-vpn-plugin.git --enable
omarchy bar move nulifyer.vpn --after omarchy.network
```

### 2. Configure your connection

Copy the example settings to your personal configuration folder:

```bash
mkdir -p ~/.config/nulifyer-vpn
cp ~/.config/omarchy/plugins/nulifyer.vpn/examples/config ~/.config/nulifyer-vpn/config
${EDITOR:-nano} ~/.config/nulifyer-vpn/config
```

Match the connection name, interface, endpoint, ports, and VPN DNS address to
your WireGuard profile. The [example configuration](examples/config) explains
each setting.

Configure the profile to use your VPN DNS for all domains. Replace `wgclient`
and `10.66.0.1` below with your connection name and VPN DNS address:

```bash
nmcli connection modify wgclient wireguard.peer-routes yes \
  ipv4.dns 10.66.0.1 ipv4.dns-search '~.' ipv4.dns-priority -100
```

To allow direct networking at home in Auto mode, add your home connection's
UUID to `TRUSTED_UUIDS` and set `TRUSTED_DNS` to its DNS server. Find its UUID
with:

```bash
nmcli -g connection.uuid connection show 'Home Wi-Fi'
```

Leave `TRUSTED_UUIDS` empty to require the VPN on every network in Auto mode.

### 3. Finish installation

```bash
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py install --user "$USER" \
  --config "$HOME/.config/nulifyer-vpn/config" --configure-dnscrypt
```

This enables VPN protection and configures encrypted DNS using Quad9. Your
existing WireGuard profile and keys are preserved. A new installation starts
in Auto mode.

If you already use DNSCrypt-proxy, you can omit `--configure-dnscrypt` when it
listens on `127.0.0.1:53` and `[::1]:53` and its upstream IPv4 addresses match
`DOH_IPV4` in your configuration.

If this plugin's system configuration already exists, use this command instead:

```bash
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py install --user "$USER"
```

## Everyday use

Left-click the shield to open the panel. Right-click to cycle through modes.

| Mode | Behavior |
| --- | --- |
| Auto | Use the VPN on untrusted networks and connect directly on trusted networks. |
| On | Require the VPN on every network. |
| Off | Use your normal internet connection without the plugin's protection. |

The panel shows connection health and whether traffic is protected. To request
a reconnect while keeping your selected mode:

```bash
nulifyer-vpn reconnect
```

## Update

```bash
omarchy plugin update nulifyer.vpn
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py install --user "$USER"
```

Your settings and selected mode are preserved.

## Remove

Uninstall the system setup before removing the bar plugin:

```bash
cd ~/.config/omarchy/plugins/nulifyer.vpn
sudo python3 scripts/system.py uninstall
omarchy plugin remove nulifyer.vpn
```

This restores settings saved before installation and keeps your WireGuard
connection and keys.

To hide the widget while keeping VPN protection running:

```bash
omarchy plugin disable nulifyer.vpn
```

## License

[MIT](LICENSE).
