"""Dataset maintenance tools in tools/.

    python -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "make_dataset_zip", PROJECT / "tools" / "make_dataset_zip.py")
make_dataset_zip = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(make_dataset_zip)


class DatasetZipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="firevad tools ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dataset = self.root / "test_VAD"
        scene = self.dataset / "environment_1" / "2"
        (scene / "RGB").mkdir(parents=True)
        (scene / "RGB" / "0.jpg").write_bytes(b"jpeg data")
        (scene / "IR.npz").write_bytes(b"npz data")
        (scene / "annotations.csv").write_text("frame,label\n0,fire\n")
        (scene / "IR.tmp.npz").write_bytes(b"interrupted conversion")
        (scene / "RGB" / "._0.jpg").write_bytes(b"macOS metadata")
        (self.dataset / ".DS_Store").write_bytes(b"macOS metadata")
        (self.dataset / "environment_1" / "Thumbs.db").write_bytes(b"Windows metadata")
        (self.dataset / ".hidden").mkdir()
        (self.dataset / ".hidden" / "notes.txt").write_text("private")
        (self.dataset / "README.txt").write_text("dataset notes")

    def run_tool(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = make_dataset_zip.main([str(a) for a in args])
        return status, out.getvalue()

    def test_zip_leaves_out_labels_and_os_files(self):
        status, log = self.run_tool(self.dataset)
        self.assertEqual(status, 0, log)
        with zipfile.ZipFile(self.root / "test_VAD.zip") as zf:
            self.assertIsNone(zf.testzip())
            self.assertEqual(sorted(zf.namelist()), [
                "test_VAD/README.txt",
                "test_VAD/environment_1/2/IR.npz",
                "test_VAD/environment_1/2/RGB/0.jpg",
            ])
            self.assertEqual(zf.getinfo("test_VAD/environment_1/2/IR.npz").compress_type,
                             zipfile.ZIP_STORED)
            self.assertEqual(zf.read("test_VAD/environment_1/2/RGB/0.jpg"), b"jpeg data")
        self.assertIn("annotations.csv", log)
        self.assertFalse((self.root / "test_VAD.zip.partial").exists())
        # The dataset itself is left as it was.
        self.assertTrue((self.dataset / "environment_1" / "2" / "annotations.csv").exists())

    def test_existing_zip_is_kept_unless_forced(self):
        target = self.root / "out.zip"
        target.write_bytes(b"older upload")
        status, log = self.run_tool(self.dataset, "-o", target)
        self.assertNotEqual(status, 0)
        self.assertEqual(target.read_bytes(), b"older upload")
        status, log = self.run_tool(self.dataset, "-o", target, "--force")
        self.assertEqual(status, 0, log)
        self.assertTrue(zipfile.is_zipfile(target))

    def test_rejects_folders_without_environments_and_output_inside(self):
        (self.root / "empty").mkdir()
        self.assertNotEqual(self.run_tool(self.root / "empty")[0], 0)
        self.assertNotEqual(self.run_tool(self.dataset, "-o", self.dataset / "x.zip")[0], 0)
        self.assertFalse((self.dataset / "x.zip").exists())


if __name__ == "__main__":
    unittest.main()
