#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pack a fire-VAD dataset folder into the ZIP that annotators download.

Dataset maintenance tool (annotators do not need it). Left out of the ZIP:
  * annotations.csv - the per-frame ground-truth labels annotators must not see,
  * hidden and OS files and folders (.DS_Store, ._*, Thumbs.db, desktop.ini),
  * leftovers of interrupted runs (*.tmp, IR.tmp.npz).

The ZIP holds one top-level folder named like the dataset folder, so it
extracts to test_VAD/environment_1/... . JPEG frames and IR.npz archives are
already compressed and are stored as they are; other files are deflated.
The ZIP is written to a temporary file and only renamed to its final name
after every member's CRC was checked and the member list and sizes were
compared with the source files. The dataset itself is only read.

Usage, from the repository folder (any Python 3.9+; no extra packages):

    python tools/make_dataset_zip.py ../test_VAD                  # -> ../test_VAD.zip
    python tools/make_dataset_zip.py ../test_VAD -o ~/test_VAD.zip
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import zipfile

EXCLUDED_NAMES = {"annotations.csv", "thumbs.db", "desktop.ini"}
STORED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".npz", ".zip"}


def is_excluded(name):
    lower = name.lower()
    return (name.startswith(".") or lower in EXCLUDED_NAMES
            or lower.endswith(".tmp") or lower.endswith(".tmp.npz"))


def collect(root):
    """Return (included, excluded) paths relative to root, in archive order."""
    included, excluded = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        for d in sorted(dirnames):
            if d.startswith("."):
                excluded.append(os.path.relpath(os.path.join(dirpath, d), root) + os.sep)
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for name in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            (excluded if is_excluded(name) else included).append(rel)
    return included, excluded


def arcname(top, rel):
    return top + "/" + rel.replace(os.sep, "/")


def is_inside(parent, path):
    try:
        return os.path.commonpath([parent, path]) == parent
    except ValueError:          # different drives on Windows
        return False


def write_zip(root, top, files, path):
    with zipfile.ZipFile(path, "w", allowZip64=True, strict_timestamps=False) as zf:
        for k, rel in enumerate(files, 1):
            ext = os.path.splitext(rel)[1].lower()
            method = zipfile.ZIP_STORED if ext in STORED_EXTENSIONS else zipfile.ZIP_DEFLATED
            zf.write(os.path.join(root, rel), arcname(top, rel), compress_type=method)
            if k % 1000 == 0:
                print("  %d / %d files" % (k, len(files)), flush=True)


def verify_zip(root, top, files, path):
    """Return a list of problems (empty when the ZIP matches the source)."""
    problems = []
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad:
            problems.append("CRC error in %s" % bad)
        infos = zf.infolist()
    names = [i.filename for i in infos]
    expected = [arcname(top, rel) for rel in files]
    if names != expected:
        problems.append("member list differs from the source files")
    for info, rel in zip(infos, files):
        if info.file_size != os.path.getsize(os.path.join(root, rel)):
            problems.append("size differs: %s" % info.filename)
    leaked = [n for n in names if any(is_excluded(part) for part in n.split("/"))]
    if leaked:
        problems.append("excluded files inside the ZIP: %s" % ", ".join(leaked[:5]))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Pack a fire-VAD dataset folder into the annotators' ZIP "
                    "(without annotations.csv and OS files).")
    parser.add_argument("dataset", help="dataset folder with environment_* subfolders")
    parser.add_argument("-o", "--output", default=None,
                        help="ZIP to create (default: <dataset>.zip beside the folder)")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing output file")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.dataset)
    top = os.path.basename(root.rstrip(os.sep))
    out = os.path.abspath(args.output or root.rstrip(os.sep) + ".zip")
    env_dirs = sorted(e for e in os.listdir(root) if re.fullmatch(r"environment_\d+", e)
                      and os.path.isdir(os.path.join(root, e))) if os.path.isdir(root) else []
    if not env_dirs:
        print("ERROR: %s has no environment_* folders." % root)
        return 1
    if is_inside(root, out):
        print("ERROR: the ZIP must not be written inside the dataset folder.")
        return 1
    if os.path.exists(out) and not args.force:
        print("ERROR: %s already exists (use --force to replace it)." % out)
        return 1

    files, excluded = collect(root)
    total = sum(os.path.getsize(os.path.join(root, rel)) for rel in files)
    print("Dataset: %s (%s)" % (root, ", ".join(env_dirs)))
    print("Packing %d files, %.2f GB; leaving out %d:" % (len(files), total / 1e9, len(excluded)))
    for rel in excluded:
        print("  - %s" % rel)

    started = time.time()
    partial = out + ".partial"
    try:
        write_zip(root, top, files, partial)
        print("Verifying %s ..." % os.path.basename(out), flush=True)
        problems = verify_zip(root, top, files, partial)
        if problems:
            print("ERROR: verification failed, no ZIP was created:")
            for p in problems:
                print("  - %s" % p)
            return 1
        os.replace(partial, out)
    finally:
        if os.path.exists(partial):
            os.remove(partial)
    print("OK: %s (%.2f GB, %d files, %.0fs)"
          % (out, os.path.getsize(out) / 1e9, len(files), time.time() - started))
    return 0


if __name__ == "__main__":
    sys.exit(main())
