#!/usr/bin/env python3
"""Write a small synthetic fire-VAD dataset for CI and local testing.

    python tests/make_test_dataset.py OUTPUT_DIR          # OUTPUT_DIR/environment_*/...
    python tests/make_test_dataset.py OUTPUT_DIR --wrap   # OUTPUT_DIR/test_VAD/test_VAD/...

--wrap reproduces what Windows "Extract All" makes of test_VAD.zip, so the tool
has to find the dataset inside the extra folders.  The scenes cover both IR
storage formats:

    environment_1/1   IR.npz archive, 150 frames (long enough for --guitest)
    environment_1/2   legacy IR/<frame>.npy folder, 60 frames
    environment_2/3   IR.npz archive, 40 frames
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

IR_H, IR_W = 400, 540          # temperature matrix size of the real dataset
RGB_W, RGB_H = 640, 480
SCENES = [(1, 1, 150, "archive"), (1, 2, 60, "folder"), (2, 3, 40, "archive")]

_YY, _XX = np.mgrid[0:IR_H, 0:IR_W]


def ir_frame(i, n):
    """Room-temperature gradient with a hot spot that grows and heats up (°C)."""
    t = i / max(n - 1, 1)
    frame = 18.0 + 4.0 * _XX / IR_W
    radius = 10 + 60 * t
    hot = (_YY - IR_H * 0.6) ** 2 + (_XX - IR_W * 0.4) ** 2 < radius ** 2
    frame[hot] = 80.0 + 200.0 * t
    return frame.astype(np.float16)


def rgb_frame(i, n):
    t = i / max(n - 1, 1)
    img = Image.new("RGB", (RGB_W, RGB_H), (90, 90, 100))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 300, 600, 470], fill=(120, 100, 80))      # "table"
    r = 8 + 50 * t
    cx, cy = RGB_W * 0.4, RGB_H * 0.6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 140, 0))
    return img


def write_scene(root, env, scene, n_frames, ir_format):
    scene_dir = os.path.join(root, "environment_%d" % env, str(scene))
    os.makedirs(os.path.join(scene_dir, "RGB"), exist_ok=True)
    frames = [ir_frame(i, n_frames) for i in range(n_frames)]
    if ir_format == "archive":
        np.savez_compressed(os.path.join(scene_dir, "IR.npz"), frames=np.stack(frames))
    else:
        os.makedirs(os.path.join(scene_dir, "IR"), exist_ok=True)
        for i, frame in enumerate(frames):
            np.save(os.path.join(scene_dir, "IR", "%d.npy" % i), frame)
    for i in range(n_frames):
        rgb_frame(i, n_frames).save(os.path.join(scene_dir, "RGB", "%d.jpg" % i), quality=85)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("output", help="folder to create the dataset in")
    parser.add_argument("--wrap", action="store_true",
                        help="nest the dataset as OUTPUT/test_VAD/test_VAD")
    args = parser.parse_args()

    root = args.output
    if args.wrap:
        root = os.path.join(root, "test_VAD", "test_VAD")
    for env, scene, n_frames, ir_format in SCENES:
        write_scene(root, env, scene, n_frames, ir_format)
    print("Synthetic dataset with %d scenes written to %s" % (len(SCENES), root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
