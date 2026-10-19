"""Install packages and download a chosen, digest-verified local model profile."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from run_windows import api, ensure_service
from setup_windows import ROOT, clean_env, install


def catalog(root=ROOT):
    value = json.loads((Path(root) / "environment.lock.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("format") != 1:
        raise ValueError("Invalid catalog format")
    profiles, models = value["profiles"], value["models"]
    if (
        not isinstance(profiles, dict)
        or not isinstance(models, dict)
        or set(profiles) != {"basic", "full"}
    ):
        raise ValueError("Invalid profile catalog")
    for name, row in models.items():
        if (
            not isinstance(name, str)
            or not isinstance(row, dict)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,200}", name)
            or not re.fullmatch(r"[a-f0-9]{64}", str(row.get("digest", "")))
        ):
            raise ValueError("Invalid model catalog")
    if any(
        not isinstance(names, list)
        or not names
        or any(not isinstance(n, str) or n not in models for n in names)
        for names in profiles.values()
    ):
        raise ValueError("Invalid model profile")
    return value


def inventory():
    rows = api("/api/tags").get("models")
    if not isinstance(rows, list) or any(
        not isinstance(r, dict)
        or not isinstance(r.get("name"), str)
        or not isinstance(r.get("digest"), str)
        for r in rows
    ):
        raise ValueError("Invalid model inventory")
    return {r["name"]: r["digest"].removeprefix("sha256:") for r in rows}


def models_for(profile, baseline, env):
    current = inventory()
    for name in baseline["profiles"][profile]:
        if name not in current:
            subprocess.run(
                [shutil.which("ollama"), "pull", name], check=True, env=env, timeout=3600
            )
            current = inventory()
        if current.get(name) != baseline["models"][name]["digest"]:
            raise RuntimeError("Model digest mismatch; existing models preserved: " + name)
        print("Verified: " + name, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("basic", "full"), default="basic")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    baseline = catalog()
    print(
        "basic: 1 image/text model (~2.68GB); full: 9 models (~20GB). Windows speech is not included.",
        flush=True,
    )
    if not args.yes and (
        not sys.stdin.isatty() or input("Download packages/models? Type YES: ").strip() != "YES"
    ):
        raise RuntimeError("Download not confirmed; no installation started.")
    install()
    ensure_service()
    models_for(args.profile, baseline, clean_env())
    subprocess.run(
        [
            str(ROOT / ".venv/Scripts/python.exe"),
            str(ROOT / "scripts/check_install.py"),
            "--require-model",
        ],
        check=True,
        cwd=ROOT,
        env=clean_env(),
    )
    env = clean_env()
    env["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(
        [str(ROOT / ".venv/Scripts/python.exe"), str(ROOT / "scripts/smoke_local.py")],
        check=True,
        cwd=ROOT,
        env=env,
        timeout=330,
    )
    print(
        "Setup checks passed. Double-click run_windows.cmd; verify native UI and exports manually."
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        print("Restore failed: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        raise SystemExit(130) from None
