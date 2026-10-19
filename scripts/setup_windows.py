"""Windows 11 x64 setup: fixed wheels, hashes and project-owned venv."""

import os
import platform
import shutil
import struct
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def supported():
    return (
        sys.platform == "win32"
        and sys.getwindowsversion().build >= 22000
        and platform.machine().upper() in {"AMD64", "X86_64"}
        and struct.calcsize("P") == 8
        and sys.version_info[:2] == (3, 14)
    )


def clean_env():
    env = dict(os.environ)
    for name in ("PYTHONHOME", "PYTHONPATH"):
        env.pop(name, None)
    env.update(
        PYTHONUTF8="1",
        OLLAMA_HOST="127.0.0.1:11434",
        OLLAMA_NO_CLOUD="1",
        OLLAMA_MAX_LOADED_MODELS="1",
        OLLAMA_NUM_PARALLEL="1",
        NO_PROXY="localhost,127.0.0.1,::1",
        no_proxy="localhost,127.0.0.1,::1",
    )
    return env


def install(root=ROOT):
    if not supported():
        raise RuntimeError("Requires Windows 11 x64 and CPython 3.14 x64 (not ARM/WSL).")
    root = Path(root).resolve()
    if not shutil.which("ollama"):
        raise RuntimeError("Install official Ollama, reopen terminal, check ollama --version.")
    lock = root / "requirements-windows-hashed.lock.txt"
    if not lock.is_file() or not (root / "main.py").is_file():
        raise RuntimeError("Incomplete project folder.")
    folder = root / ".venv"
    python = folder / "Scripts/python.exe"
    if folder.exists():
        if not python.is_file() or not (folder / "pyvenv.cfg").is_file():
            raise RuntimeError(
                "Existing .venv is incomplete or from another OS; preserved. Back it up first."
            )
    else:
        venv.EnvBuilder(with_pip=True).create(folder)
    env = clean_env()
    result = subprocess.run(
        [
            str(python),
            "-c",
            "import sys,struct; print(sys.prefix); print(sys.version_info[:2]); print(struct.calcsize('P'))",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=30,
    ).stdout.splitlines()
    if len(result) != 3 or Path(result[0]).resolve() != folder or result[1:] != ["(3, 14)", "8"]:
        raise RuntimeError(
            "Existing venv prefix, Python version or architecture mismatch; preserved."
        )
    subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "--isolated",
            "install",
            "--disable-pip-version-check",
            "--require-hashes",
            "--only-binary=:all:",
            "--index-url",
            "https://pypi.org/simple",
            "-r",
            str(lock),
        ],
        check=True,
        cwd=root,
        env=env,
    )
    subprocess.run([str(python), "-m", "pip", "check"], check=True, env=env)
    subprocess.run(
        [
            str(python),
            "-c",
            "from PySide6 import QtWidgets,QtNetwork,QtMultimedia; print('Qt imports OK')",
        ],
        check=True,
        env=env,
        timeout=30,
    )
    print(
        "Package installation complete. Use restore_windows.cmd for model setup, run_windows.cmd to launch."
    )


if __name__ == "__main__":
    try:
        install()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print("Installation failed: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
