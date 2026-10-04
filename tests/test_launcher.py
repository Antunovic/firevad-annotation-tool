"""Launcher and app regressions.

    python -m unittest discover -s tests -v

Run with a Python that has numpy, Pillow and tkinter (e.g. the one in
.venv-annotator). Launcher tests for the other operating system are skipped.
"""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("annotate_gui", PROJECT / "annotate_gui.py")
gui = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gui)

STUB_APP = ("import json, sys\nprint('ARGS=' + json.dumps(sys.argv[1:]))\n"
            "sys.exit(7 if '--fail' in sys.argv else 0)\n")


class TempDirTest(unittest.TestCase):
    def setUp(self):
        # A space in the path catches quoting bugs in the launchers.
        self.temp = tempfile.TemporaryDirectory(prefix="firevad launcher ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)


class LauncherContract:
    """Behaviour shared by run_mac.command / run_linux.sh and run_windows.bat."""

    launcher_files = ()

    def setUp(self):
        super().setUp()
        for name in self.launcher_files:
            shutil.copy2(PROJECT / name, self.root / name)
        self.launcher = self.root / self.launcher_files[-1]
        (self.root / "annotate_gui.py").write_text(STUB_APP, encoding="utf-8")
        self.env = dict(os.environ, FIREVAD_PYTHON=sys.executable, PYTHONPATH="",
                        FIREVAD_NONINTERACTIVE="1")
        self.env.pop("FIREVAD_GUITEST_NAME", None)

    def run_launcher(self, *args):
        raise NotImplementedError

    def test_check_runtime_does_not_launch_or_install(self):
        result = self.run_launcher("--check-runtime")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(" / Tk ", result.stdout)
        self.assertNotIn("ARGS=", result.stdout)
        self.assertFalse((self.root / ".venv-annotator").exists())
        self.assertFalse((self.root / "annotator_config.json").exists())

    def test_rejects_obsolete_tk_even_when_import_succeeds(self):
        (self.root / "tkinter.py").write_text("TkVersion = 8.5\n")
        self.env["PYTHONPATH"] = str(self.root)
        result = self.run_launcher("--check-runtime")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Tk 8.5 is too old", result.stdout)
        self.assertNotIn("ARGS=", result.stdout)

    def test_rejects_python_without_tk(self):
        (self.root / "tkinter.py").write_text("raise ImportError('no _tkinter')\n")
        self.env["PYTHONPATH"] = str(self.root)
        result = self.run_launcher("--check-runtime")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no tkinter support", result.stdout)

    def test_invalid_override_does_not_silently_fall_back(self):
        self.env["FIREVAD_PYTHON"] = str(self.root / "missing-python")
        result = self.run_launcher("--check-runtime")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FIREVAD_PYTHON not found", result.stdout)

    def test_arguments_and_paths_with_spaces(self):
        result = self.run_launcher("--dataset-root", "/tmp/dataset with spaces")
        self.assertEqual(result.returncode, 0, result.stdout)
        line = next(line for line in result.stdout.splitlines() if line.startswith("ARGS="))
        self.assertEqual(json.loads(line[5:]), ["--dataset-root", "/tmp/dataset with spaces"])
        self.assertIn("Keep this window open", result.stdout)

    def test_app_error_exit_code_is_preserved_without_hanging(self):
        result = self.run_launcher("--fail")
        self.assertEqual(result.returncode, 7, result.stdout)
        self.assertIn("error (code 7)", result.stdout)

    def test_explains_running_from_an_unextracted_zip(self):
        (self.root / "annotate_gui.py").unlink()
        result = self.run_launcher()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Extract", result.stdout)

    def make_venv(self, path):
        """Return (python, site-packages) of a new pip-less virtual environment."""
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(path)],
                       check=True, timeout=120)
        if os.name == "nt":
            return path / "Scripts" / "python.exe", path / "Lib" / "site-packages"
        return (path / "bin" / "python",
                path / "lib" / ("python%d.%d" % sys.version_info[:2]) / "site-packages")

    def test_override_without_packages_reuses_the_existing_environment(self):
        bare, _ = self.make_venv(self.root / "bare python")
        _, site = self.make_venv(self.root / ".venv-annotator")
        # Stand-ins for numpy and Pillow: the launcher only checks that they import.
        (site / "numpy.py").write_text("")
        (site / "PIL").mkdir()
        for module in ("__init__", "Image", "ImageTk"):
            (site / "PIL" / (module + ".py")).write_text("")
        self.env["FIREVAD_PYTHON"] = str(bare)
        result = self.run_launcher("--x")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('ARGS=["--x"]', result.stdout)
        started = next(line for line in result.stdout.splitlines()
                       if line.startswith("Starting with:"))
        self.assertIn(".venv-annotator", started)


@unittest.skipIf(os.name == "nt", "macOS/Linux launcher")
class MacLauncherTests(LauncherContract, TempDirTest):
    launcher_files = ("run_mac.command",)

    def run_launcher(self, *args):
        return subprocess.run(
            ["/bin/bash", str(self.launcher), *args], cwd="/",
            env=self.env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60,
        )


@unittest.skipIf(os.name == "nt", "macOS/Linux launcher")
class LinuxLauncherTests(MacLauncherTests):
    launcher_files = ("run_mac.command", "run_linux.sh")


@unittest.skipUnless(os.name == "nt", "Windows launcher")
class WindowsLauncherTests(LauncherContract, TempDirTest):
    launcher_files = ("run_windows.bat",)

    def run_launcher(self, *args):
        # /s: strip only the outer quotes, so quoted paths with spaces survive.
        line = subprocess.list2cmdline([str(self.launcher), *args])
        return subprocess.run(
            'cmd /d /s /c "%s"' % line, cwd=os.path.abspath(os.sep),
            env=self.env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120,
        )


class RepositoryTests(unittest.TestCase):
    def test_batch_file_uses_crlf_line_endings(self):
        # cmd can misread labels in LF-only batch files (.gitattributes keeps CRLF).
        data = (PROJECT / "run_windows.bat").read_bytes()
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))

    def test_shell_launchers_use_lf_line_endings(self):
        for name in ("run_mac.command", "run_linux.sh"):
            self.assertNotIn(b"\r", (PROJECT / name).read_bytes(), name)


class AppTests(TempDirTest):
    def test_app_rejects_old_tk_before_creating_a_window(self):
        with patch.object(gui.tk, "TkVersion", 8.5):
            with self.assertRaisesRegex(RuntimeError, "blank window"):
                gui.AnnotationApp()

    def make_dataset(self, path):
        (path / "environment_1").mkdir(parents=True)
        return path

    def test_dataset_discovery_beside_gui_directory(self):
        tool = self.root / "GUI"
        tool.mkdir()
        dataset = self.make_dataset(self.root / "test_VAD")
        with patch.object(gui, "SCRIPT_DIR", str(tool)):
            self.assertEqual(gui.default_dataset_root(), str(dataset))

    def test_dataset_inside_gui_takes_precedence(self):
        tool = self.root / "GUI"
        local = self.make_dataset(tool / "test_VAD")
        self.make_dataset(self.root / "test_VAD")
        with patch.object(gui, "SCRIPT_DIR", str(tool)):
            self.assertEqual(gui.default_dataset_root(), str(local))

    def test_test_vad_is_preferred_over_other_dataset_folders(self):
        tool = self.root / "GUI"
        tool.mkdir()
        self.make_dataset(self.root / "archive")
        dataset = self.make_dataset(self.root / "test_VAD")
        with patch.object(gui, "SCRIPT_DIR", str(tool)):
            self.assertEqual(gui.default_dataset_root(), str(dataset))

    def test_windows_extract_all_wrapper_folder_is_found(self):
        tool = self.root / "GUI"
        tool.mkdir()
        dataset = self.make_dataset(self.root / "test_VAD" / "test_VAD")
        with patch.object(gui, "SCRIPT_DIR", str(tool)):
            self.assertEqual(gui.default_dataset_root(), str(dataset))

    def test_dataset_beside_double_nested_github_download(self):
        downloads = self.root / "Downloads"
        tool = downloads / "firevad-annotation-tool-main" / "firevad-annotation-tool-main"
        tool.mkdir(parents=True)
        dataset = self.make_dataset(downloads / "test_VAD" / "test_VAD")
        with patch.object(gui, "SCRIPT_DIR", str(tool)):
            self.assertEqual(gui.default_dataset_root(), str(dataset))

    def test_home_folder_is_never_searched(self):
        home = self.root / "home"
        tool = home / "firevad-annotation-tool"
        tool.mkdir(parents=True)
        self.make_dataset(home / "test_VAD")
        with patch.object(gui, "SCRIPT_DIR", str(tool)), \
                patch.object(gui, "_user_home", lambda: str(home)):
            self.assertEqual(gui.dataset_search_folders(), [str(tool)])
            self.assertIsNone(gui.locate_dataset_near_tool())
            self.assertEqual(gui.default_dataset_root(), str(tool / "test_VAD"))

    def test_picked_folder_may_be_a_parent_of_the_dataset(self):
        dataset = self.make_dataset(self.root / "Downloads" / "videos" / "test_VAD")
        self.assertEqual(gui.find_dataset_root(str(self.root / "Downloads")), str(dataset))
        self.assertEqual(gui.find_dataset_root(str(dataset)), str(dataset))
        (self.root / "empty").mkdir()
        self.assertIsNone(gui.find_dataset_root(str(self.root / "empty")))
        self.assertIsNone(gui.find_dataset_root(str(self.root / "missing")))
        self.assertIsNone(gui.find_dataset_root(str(self.root), max_depth=1))

    def test_environment_files_do_not_count_as_a_dataset(self):
        (self.root / "environment_1").write_text("not a folder")
        self.assertFalse(gui.looks_like_dataset_root(str(self.root)))

    def test_output_and_config_stay_inside_gui(self):
        tool = self.root / "GUI"
        with patch.object(gui, "PROJECT_DIR", str(tool)):
            self.assertEqual(gui.config_path(), str(tool / "annotator_config.json"))
            self.assertEqual(gui.annotations_root(), str(tool / "annotations"))

    def test_annotator_folder_names_are_readable_ascii(self):
        self.assertEqual(gui.sanitize_annotator_dir("Ivana Šimić"), "Ivana_Simic")
        self.assertEqual(gui.sanitize_annotator_dir("Đurđa Kovačević"), "Djurdja_Kovacevic")
        self.assertEqual(gui.sanitize_annotator_dir("Ana M."), "Ana_M")
        self.assertEqual(gui.sanitize_annotator_dir(".."), "annotator")
        self.assertEqual(gui.sanitize_annotator_dir("   "), "annotator")

    def test_discovers_archive_format_scene_and_loads_frames(self):
        dataset = self.root / "test_VAD"
        scene = dataset / "environment_7" / "99"
        (scene / "RGB").mkdir(parents=True)
        stack = np.arange(3 * 4 * 5, dtype=np.float16).reshape(3, 4, 5)
        np.savez_compressed(scene / "IR.npz", frames=stack)
        for i in range(3):
            Image.new("RGB", (5, 4)).save(scene / "RGB" / ("%d.jpg" % i))
        # A stale legacy IR/ folder must not shadow the archive.
        (scene / "IR").mkdir()
        np.save(scene / "IR" / "0.npy", np.zeros((4, 5), dtype=np.float16))

        scenes = gui.discover_scenes(str(dataset))
        self.assertEqual(len(scenes), 1)
        sc = scenes[0]
        self.assertEqual((sc["environment"], sc["scene"]), (7, 99))
        self.assertEqual(sc["ir_format"], "archive")
        self.assertEqual(sc["ir_count"], 3)
        self.assertEqual(sc["n_frames"], 3)
        loader, n = gui.make_ir_loader(sc)
        self.assertEqual(n, 3)
        self.assertTrue(np.array_equal(loader(0), stack[0]))
        self.assertTrue(np.array_equal(loader(2), stack[2]))
        self.assertTrue(np.array_equal(loader(50), stack[2]))  # clamped to last frame

    def test_discovers_legacy_folder_format_scene(self):
        dataset = self.root / "test_VAD"
        scene = dataset / "environment_1" / "3"
        (scene / "IR").mkdir(parents=True)
        (scene / "RGB").mkdir()
        for i in range(2):
            np.save(scene / "IR" / ("%d.npy" % i),
                    np.full((4, 5), float(i), dtype=np.float16))
            Image.new("RGB", (5, 4)).save(scene / "RGB" / ("%d.jpg" % i))
        scenes = gui.discover_scenes(str(dataset))
        self.assertEqual(len(scenes), 1)
        sc = scenes[0]
        self.assertEqual(sc["ir_format"], "folder")
        self.assertEqual(sc["ir_count"], 2)
        loader, n = gui.make_ir_loader(sc)
        self.assertEqual(n, 2)
        self.assertEqual(float(loader(1)[0, 0]), 1.0)


if __name__ == "__main__":
    unittest.main()
