"""Launch only the local service if absent, then run the desktop app."""

import http.client
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from setup_windows import ROOT, clean_env, supported


def api(path):
    connection = http.client.HTTPConnection("127.0.0.1", 11434, timeout=3)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        data = response.read(1024 * 1024 + 1)
        if response.status != 200 or len(data) > 1024 * 1024:
            raise ValueError("Invalid local service response")
        value = json.loads(data)
        if not isinstance(value, dict):
            raise ValueError("Invalid local service JSON")
        return value
    finally:
        connection.close()


def ensure_service(root=ROOT):
    try:
        api("/api/version")
        return
    except (OSError, ValueError, http.client.HTTPException):
        pass
    program = shutil.which("ollama")
    if not program:
        raise RuntimeError("Ollama CLI missing; install Ollama and reopen terminal.")
    logs = Path(root) / ".logs"
    logs.mkdir(exist_ok=True)
    with (logs / "ollama.log").open("ab") as output:
        process = subprocess.Popen(
            [program, "serve"],
            env=clean_env(),
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
        )
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        try:
            api("/api/version")
            return
        except (OSError, ValueError, http.client.HTTPException):
            if process.poll() is not None:
                break
            time.sleep(0.5)
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    raise RuntimeError(
        "Ollama could not start; see .logs/ollama.log. Existing services are not stopped."
    )


def main():
    if not supported() or Path(sys.prefix).resolve() != ROOT / ".venv":
        raise RuntimeError("Run via this project's Windows .venv using run_windows.cmd.")
    if sys.argv[1:] == ["--check"]:
        return subprocess.call(
            [sys.executable, str(ROOT / "scripts/check_install.py")], env=clean_env(), cwd=ROOT
        )
    if sys.argv[1:]:
        raise RuntimeError("Only --check is supported.")
    ensure_service()
    return subprocess.call([sys.executable, str(ROOT / "main.py")], cwd=ROOT, env=clean_env())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print("Launch failed: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
