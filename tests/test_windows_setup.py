"""Windows setup safety can be tested without modifying this host's environment."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
restore_windows = importlib.import_module("restore_windows")
run_windows = importlib.import_module("run_windows")
setup_windows = importlib.import_module("setup_windows")


class WindowsSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fixture(self):
        (self.root / "main.py").touch()
        (self.root / "requirements-windows-hashed.lock.txt").touch()

    def test_unsupported_host_never_creates_environment(self):
        with patch.object(setup_windows, "supported", return_value=False):
            with self.assertRaises(RuntimeError):
                setup_windows.install(self.root)
        self.assertFalse((self.root / ".venv").exists())

    def test_foreign_environment_is_preserved(self):
        self.fixture()
        (self.root / ".venv").mkdir()
        marker = self.root / ".venv/keep.txt"
        marker.write_text("keep")
        with (
            patch.object(setup_windows, "supported", return_value=True),
            patch.object(setup_windows.shutil, "which", return_value="ollama.exe"),
        ):
            with self.assertRaisesRegex(RuntimeError, "preserved"):
                setup_windows.install(self.root)
        self.assertEqual(marker.read_text(), "keep")

    def test_install_uses_isolated_hashed_binary_wheels(self):
        self.fixture()
        folder = self.root / ".venv"
        (folder / "Scripts").mkdir(parents=True)
        (folder / "Scripts/python.exe").touch()
        (folder / "pyvenv.cfg").touch()
        with (
            patch.object(setup_windows, "supported", return_value=True),
            patch.object(setup_windows.shutil, "which", return_value="ollama.exe"),
            patch.object(setup_windows.subprocess, "run") as run,
        ):
            run.return_value = SimpleNamespace(stdout=f"{folder}\n(3, 14)\n8\n")
            setup_windows.install(self.root)
            command = run.call_args_list[1].args[0]
            for expected in (
                "--isolated",
                "--require-hashes",
                "--only-binary=:all:",
                "https://pypi.org/simple",
            ):
                self.assertIn(expected, command)

    def test_existing_service_is_not_spawned_or_stopped(self):
        with (
            patch.object(run_windows, "api", return_value={"version": "test"}),
            patch.object(run_windows.subprocess, "Popen") as spawn,
        ):
            run_windows.ensure_service(self.root)
            spawn.assert_not_called()

    def test_owned_failed_service_is_reaped(self):
        with (
            patch.object(run_windows, "api", side_effect=OSError),
            patch.object(run_windows.shutil, "which", return_value="ollama.exe"),
            patch.object(run_windows.subprocess, "CREATE_NEW_PROCESS_GROUP", 1, create=True),
            patch.object(run_windows.subprocess, "DETACHED_PROCESS", 2, create=True),
            patch.object(run_windows.subprocess, "Popen") as spawn,
            patch.object(run_windows.time, "monotonic", side_effect=[0, 50]),
        ):
            spawn.return_value.poll.return_value = None
            with self.assertRaises(RuntimeError):
                run_windows.ensure_service(self.root)
            spawn.return_value.terminate.assert_called_once()
            spawn.return_value.wait.assert_called_once_with(timeout=5)

    def test_model_mismatch_never_overwrites_existing(self):
        baseline = restore_windows.catalog()
        name = baseline["profiles"]["basic"][0]
        with (
            patch.object(restore_windows, "inventory", return_value={name: "0" * 64}),
            patch.object(restore_windows.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(RuntimeError, "digest"):
                restore_windows.models_for("basic", baseline, {})
            run.assert_not_called()

    def test_new_model_is_checked_after_download(self):
        baseline = restore_windows.catalog()
        name = baseline["profiles"]["basic"][0]
        with (
            patch.object(restore_windows, "inventory", side_effect=[{}, {name: "0" * 64}]),
            patch.object(restore_windows.shutil, "which", return_value="ollama.exe"),
            patch.object(restore_windows.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(RuntimeError, "digest"):
                restore_windows.models_for("basic", baseline, {})
            self.assertEqual(run.call_args.args[0], ["ollama.exe", "pull", name])

    def test_without_consent_no_install(self):
        with (
            patch.object(sys, "argv", ["restore_windows.py"]),
            patch.object(restore_windows.sys.stdin, "isatty", return_value=False),
            patch.object(restore_windows, "install") as install,
        ):
            with self.assertRaisesRegex(RuntimeError, "confirmed"):
                restore_windows.main()
            install.assert_not_called()

    def test_environment_does_not_leak_python_or_remote_ollama_overrides(self):
        with patch.dict(
            setup_windows.os.environ,
            {"PYTHONHOME": "bad", "PYTHONPATH": "bad", "OLLAMA_HOST": "remote"},
        ):
            env = setup_windows.clean_env()
        self.assertNotIn("PYTHONHOME", env)
        self.assertNotIn("PYTHONPATH", env)
        self.assertEqual(env["OLLAMA_HOST"], "127.0.0.1:11434")
        self.assertEqual(env["OLLAMA_NO_CLOUD"], "1")

    def test_excluded_image_and_mac_launchers_absent(self):
        root = SCRIPTS.parent
        for name in (
            "測試圖/機器人視角：病房跌倒偵測.jpg",
            "run.command",
            "install.command",
            "restore.command",
        ):
            self.assertFalse((root / name).exists())
        self.assertEqual(len(list((root / "測試圖").glob("*.jpg"))), 6)
