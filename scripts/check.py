#!/usr/bin/env python3
"""Run local checks without changing the host's VPN or firewall."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    print("+ " + " ".join(map(str, args)), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["schemaVersion"] == 1
    assert manifest["id"] == "nulifyer.vpn"
    assert manifest["license"] == "MIT"
    assert manifest["kinds"] == ["bar-widget"]
    assert manifest["entryPoints"] == {"barWidget": "Panel.qml"}
    assert "MIT License" in (ROOT / "LICENSE").read_text()
    for directory in ["bin", "libexec", "networkmanager"]:
        for script in sorted((ROOT / directory).iterdir()):
            run("bash", "-n", str(script.relative_to(ROOT)))
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        assert not path.is_symlink(), f"Plugin repositories must not contain symlinks: {path}"
        assert path.suffix not in {".key", ".nmconnection"}, f"Private data: {path}"
    native = shutil.which("omarchy-plugin-validate")
    if native:
        run(native, str(ROOT))
    else:
        print("Omarchy validator unavailable; native validation remains required on the target host.")
    formatter = shutil.which("qmlformat") or "/usr/lib/qt6/bin/qmlformat"
    if Path(formatter).is_file():
        print("+ Parse Panel.qml with qmlformat", flush=True)
        subprocess.run([formatter, "--normalize", str(ROOT / "Panel.qml")], check=True, stdout=subprocess.DEVNULL)
    else:
        print("qmlformat unavailable; QML parsing remains required on the target host.")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    print("Checks passed. Live networking and full reboot checks are separate.")


if __name__ == "__main__":
    main()
