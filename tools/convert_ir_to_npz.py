#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert legacy IR frame folders (IR/*.npy) to single compressed IR.npz archives.

Dataset maintenance tool (annotators do not need it). Each scene's IR/ folder
of per-frame .npy temperature matrices is packed into one IR.npz holding a
stacked 'frames' array, the format the annotation tool reads fastest:

    IR.npz -> {"frames": (N, H, W) float16 °C matrices}
    (written with np.savez_compressed)

Safety rules:
  * The archive is written to IR.tmp.npz first and verified with exact array
    equality against the source frames before it is renamed to IR.npz.
  * Only after successful verification is the scene's IR/ folder deleted.
  * If a scene already has both IR.npz and an IR/ folder (e.g. a previously
    interrupted run), the archive is verified against the folder and the
    folder is deleted only when the data matches exactly; otherwise the scene
    is reported as FAILED and left untouched.
  * RGB folders, annotations.csv and everything else are never modified.

Usage, from the repository folder (any Python 3.9+ with numpy and Pillow; the
tool's .venv-annotator has both):

    .venv-annotator/bin/python tools/convert_ir_to_npz.py            # test_VAD beside the repo
    .venv-annotator/bin/python tools/convert_ir_to_npz.py --dry-run  # report only
    .venv-annotator/bin/python tools/convert_ir_to_npz.py --dataset-root /path/to/dataset
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import time

import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from annotate_gui import (  # noqa: E402  (single source of truth for the format)
    IR_ARCHIVE_KEY,
    IR_ARCHIVE_NAME,
    IR_DIR_NAME,
    list_frame_files,
    looks_like_dataset_root,
)

TMP_ARCHIVE_NAME = "IR.tmp.npz"


def default_dataset_root():
    """test_VAD beside the repository folder, else inside it."""
    beside = os.path.join(os.path.dirname(PROJECT_DIR), "test_VAD")
    return beside if looks_like_dataset_root(beside) else \
        os.path.join(PROJECT_DIR, "test_VAD")


def iter_scene_dirs(root):
    for entry in sorted(os.listdir(root)):
        if not re.fullmatch(r"environment_\d+", entry):
            continue
        env_dir = os.path.join(root, entry)
        if not os.path.isdir(env_dir):
            continue
        for sub in sorted(os.listdir(env_dir)):
            try:
                int(sub)
            except ValueError:
                continue
            scene_dir = os.path.join(env_dir, sub)
            if os.path.isdir(scene_dir):
                yield scene_dir


def folder_bytes(ir_dir):
    total = 0
    for name in os.listdir(ir_dir):
        path = os.path.join(ir_dir, name)
        if os.path.isfile(path):
            total += os.path.getsize(path)
    return total


def load_stack(files):
    """Stack the sorted per-frame .npy files into one (N, H, W) array."""
    first = np.load(files[0][1])
    stack = np.empty((len(files),) + first.shape, dtype=first.dtype)
    for k, (idx, path) in enumerate(files):
        arr = np.load(path)
        if arr.shape != first.shape or arr.dtype != first.dtype:
            raise ValueError("frame %d has shape %s dtype %s, expected %s %s"
                             % (idx, arr.shape, arr.dtype, first.shape, first.dtype))
        stack[k] = arr
    return stack


def archive_matches(archive, stack):
    """True when the archive holds exactly the same frames as the stack."""
    with np.load(archive) as z:
        if IR_ARCHIVE_KEY not in z.files:
            return False
        return np.array_equal(z[IR_ARCHIVE_KEY], stack)


def convert_scene(scene_dir, dry_run=False):
    """Pack one scene's IR/*.npy into IR.npz.

    Returns (status, message, frames, bytes_before, bytes_after) where status
    is one of: done, pruned, skipped, FAILED.
    """
    archive = os.path.join(scene_dir, IR_ARCHIVE_NAME)
    tmp = os.path.join(scene_dir, TMP_ARCHIVE_NAME)
    ir_dir = os.path.join(scene_dir, IR_DIR_NAME)
    files = list_frame_files(ir_dir, {".npy"})
    has_archive = os.path.isfile(archive)
    has_folder = bool(files)

    if has_archive and not has_folder:
        return "skipped", "IR.npz already present (no IR/ folder left)", 0, 0, 0
    if not has_archive and not has_folder:
        return "skipped", "no IR data found (neither IR.npz nor IR/*.npy)", 0, 0, 0

    bytes_before = folder_bytes(ir_dir)
    try:
        stack = load_stack(files)
    except Exception as e:
        return "FAILED", "could not read IR frames: %s" % e, 0, bytes_before, 0

    note = ""
    indices = [idx for idx, _ in files]
    if indices != list(range(len(files))):
        note = " (non-contiguous frame indices, packed in sorted order)"

    if has_archive:
        # Interrupted previous run: verify, then prune the folder.
        if not archive_matches(archive, stack):
            return "FAILED", "existing IR.npz does not match IR/ frames; folder kept", \
                len(files), bytes_before, os.path.getsize(archive)
        if not dry_run:
            shutil.rmtree(ir_dir)
        return "pruned", "existing IR.npz verified against IR/; folder deleted" + note, \
            len(files), bytes_before, os.path.getsize(archive)

    if dry_run:
        return "done*", "would pack %d frames %s %s%s" % (
            len(files), stack.shape[1:], stack.dtype, note), len(files), bytes_before, 0

    np.savez_compressed(tmp, **{IR_ARCHIVE_KEY: stack})
    if not archive_matches(tmp, stack):
        os.remove(tmp)
        return "FAILED", "written archive failed verification; originals kept", \
            len(files), bytes_before, 0
    os.replace(tmp, archive)
    bytes_after = os.path.getsize(archive)
    shutil.rmtree(ir_dir)
    return "done", "packed %d frames %s %s -> %s; IR/ folder deleted%s" % (
        len(files), stack.shape[1:], stack.dtype, archive, note), \
        len(files), bytes_before, bytes_after


def main():
    parser = argparse.ArgumentParser(
        description="Convert legacy IR/*.npy folders to single IR.npz archives "
                    "(verified, then originals are deleted).")
    parser.add_argument("--dataset-root", default=None,
                        help="dataset root (folder with environment_* subfolders); "
                             "default: test_VAD beside the repository folder")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would happen without writing or deleting")
    args = parser.parse_args()

    root = os.path.abspath(args.dataset_root or default_dataset_root())
    if not looks_like_dataset_root(root):
        print("ERROR: %s does not look like a dataset root "
              "(no environment_* subfolders)." % root)
        return 1

    scene_dirs = list(iter_scene_dirs(root))
    print("Fire-VAD IR.npz converter%s" % (" (dry run)" if args.dry_run else ""))
    print("Dataset root: %s" % root)
    print("Scenes found: %d" % len(scene_dirs))
    print("-" * 72)

    counts = {}
    failures = []
    total_frames = 0
    total_before = 0
    total_after = 0
    started = time.time()
    for scene_dir in scene_dirs:
        rel = os.path.relpath(scene_dir, root)
        t0 = time.time()
        status, msg, frames, before, after = convert_scene(scene_dir, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1
        if status == "FAILED":
            failures.append(rel)
        if status in ("done", "done*", "pruned"):
            total_frames += frames
            total_before += before
            total_after += after
        print("[%-6s] %-24s %s (%.1fs)"
              % (status.upper(), rel, msg, time.time() - t0), flush=True)

    print("-" * 72)
    print("Scenes: %s | frames packed: %d" % (counts, total_frames))
    if total_before or total_after:
        print("IR storage: %.2f GB -> %.2f GB (freed %.2f GB)"
              % (total_before / 1e9, total_after / 1e9,
                 (total_before - total_after) / 1e9))
    if args.dry_run:
        print("Dry run: nothing was written or deleted.")
    if failures:
        print("FAILED scenes (left untouched):")
        for rel in failures:
            print("  - %s" % rel)
        return 1
    print("All scenes OK (%.1fs total)." % (time.time() - started))
    return 0


if __name__ == "__main__":
    sys.exit(main())
