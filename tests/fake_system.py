#!/usr/bin/env python3
"""Bounded command doubles for executing policy scripts without host changes."""

import json
import os
from pathlib import Path
import sys
import time

command = Path(sys.argv[0]).name
args = sys.argv[1:]
# The nft producer queries the table before it writes the piped rules. Consume
# that pipe before reading shared state so the two command doubles cannot race.
nft_input = sys.stdin.read() if command == "nft" and args == ["-f", "-"] else ""
path = Path(os.environ["VPN_TEST_STATE"])
state = json.loads(path.read_text())
state.setdefault("calls", []).append([command, *args])
output = ""
result = 0
if command == "ip":
    if args[:2] == ["-4", "rule"]:
        operation = args[2]
        rule = args[3:]
        rules = state.setdefault("bootstrap_rules", [])
        if operation == "show":
            output = "matching bootstrap rule\n" if rule in rules else ""
        elif operation == "add":
            rules.append(rule)
        elif operation == "del":
            rules.remove(rule)
        else:
            raise RuntimeError(f"Unexpected ip rule call: {args}")
    elif state.get("upstream", True):
        output = "default via 192.0.2.1 dev eth0 proto dhcp\n"
elif command == "nmcli":
    joined = " ".join(args)
    if "GENERAL.STATE" in args:
        output = "activated\n" if state.get("active", False) else "\n"
    elif "GENERAL.CON-UUID" in args:
        output = state.get("uuid", "11111111-1111-4111-8111-111111111111") + "\n"
    elif "connection.autoconnect" in args and "show" in args:
        output = state.get("autoconnect", "yes") + "\n"
    elif "modify" in args:
        properties = args[args.index("modify") + 2:]
        for key, value in zip(properties[::2], properties[1::2]):
            if key == "connection.autoconnect":
                state["autoconnect"] = value
            else:
                state.setdefault("properties", {})[key] = value
    elif "connection up" in joined:
        state["active"] = state.get("activation_ok", True)
        result = 0 if state["active"] else 1
    elif "connection down" in joined:
        state["active"] = False
    elif "--active" in args:
        output = state.get("uuid", "11111111-1111-4111-8111-111111111111") + "\n"
    elif "-g" in args:
        field = args[args.index("-g") + 1]
        defaults = {"connection.type": "802-11-wireless", "ipv6.method": "auto", "GENERAL.DEVICES": ""}
        value = state.get("properties", {}).get(field, defaults.get(field, ""))
        output = value if "--escape" in args and args[args.index("--escape") + 1] == "no" else value.replace(":", "\\:")
        output += "\n"
    elif args[:2] == ["connection", "show"]:
        pass
    else:
        raise RuntimeError(f"Unexpected nmcli call: {args}")
elif command == "wg":
    if "latest-handshakes" in args:
        output = "test-peer\t" + str(int(time.time()) - state.get("handshake_age", 1)) + "\n"
    elif "endpoints" in args:
        if state.get("live_endpoint", True):
            output = "test-peer\t" + state.get("endpoint", "198.51.100.1") + ":51820\n"
        elif state.get("active", False):
            output = "test-peer\t(none)\n"
    elif "peers" in args:
        output = "test-peer\n"
    elif args[:1] == ["set"]:
        state["endpoint"] = args[-1].rsplit(":", 1)[0]
        state["live_endpoint"] = True
    else:
        raise RuntimeError(f"Unexpected wg call: {args}")
elif command == "ping":
    result = 0 if state.get("reachable", True) else 1
elif command == "test-guard":
    state["guard"] = args[0]
elif command == "test-home-reply":
    pass
elif command == "iptables":
    if args[:2] == ["-nL", "ufw-before-input"]:
        result = 0 if state.get("ufw", True) else 1
    else:
        rules = state.setdefault("input_rules", [])
        operation = args[0]
        rule = args[2:]
        if operation == "-I":
            state.setdefault("insert_positions", []).append(rule.pop(0))
            rules.append(rule)
        elif operation == "-C":
            result = 0 if rule in rules else 1
        elif operation == "-D":
            rules.remove(rule)
        else:
            raise RuntimeError(f"Unexpected iptables call: {args}")
elif command == "nft":
    if args[:2] == ["list", "table"]:
        result = 0 if state.get("table", False) else 1
    elif args[:2] == ["delete", "table"]:
        state["table"] = False
    elif args == ["-f", "-"]:
        state["nft_rules"] = nft_input
        state["table"] = True
    else:
        raise RuntimeError(f"Unexpected nft call: {args}")
else:
    raise RuntimeError(f"Unexpected command: {command}")
path.write_text(json.dumps(state))
sys.stdout.write(output)
sys.exit(result)
