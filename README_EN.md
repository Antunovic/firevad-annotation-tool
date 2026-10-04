# Fire-VAD annotation tool

[![Tests](https://github.com/Antunovic/firevad-annotation-tool/actions/workflows/tests.yml/badge.svg)](https://github.com/Antunovic/firevad-annotation-tool/actions/workflows/tests.yml)

A tool for writing text annotations for the videos of the fire-VAD dataset (RGB and
thermal/IR camera). It runs on Windows, macOS and Linux. *Hrvatski: [README.md](README.md).*

## 1. Download

1. **Tool:** [firevad-annotation-tool-main.zip](https://github.com/Antunovic/firevad-annotation-tool/archive/refs/heads/main.zip)
   (or, at the top of this page, the green **Code** button → **Download ZIP**).
2. **Videos:** `test_VAD.zip` (about 3 GB); the project coordinator sends you the Google Drive link.
   Google Drive warns that it cannot scan such a large file for viruses;
   click **Download anyway**.
3. Extract **both** ZIP files into the same folder, for example *Downloads*:

   ```text
   Downloads/
     firevad-annotation-tool-main/    ← the tool
     test_VAD/                        ← the videos
       environment_1/
       environment_2/
       ...
   ```

   - **Windows:** right-click the ZIP → **Extract All…** → **Extract**.
     Tip: before extracting, right-click the ZIP → **Properties**, tick **Unblock** and
     click **OK**. Windows then shows no security warnings for the tool later.
   - **macOS:** double-click the ZIP (Safari usually extracts it by itself).

   Extra folders created by extracting (such as `test_VAD\test_VAD\`) are fine.
   If the tool does not find the videos, it asks you where they are.

## 2. Start

The first start takes a minute or two and needs internet: the tool installs the Python
packages numpy and Pillow into its own `.venv-annotator` folder. Nothing else is installed
on the system, except Python itself if it is missing. Later starts work offline.

### Windows

1. In the tool folder, double-click **`run_windows.bat`**.
2. If *Windows protected your PC* appears, click **More info**, then **Run anyway**.
   For *Open File – Security Warning*, click **Run**.
3. If the computer has no Python, the script offers to install it: press **Y**.
   If that fails, install Python 3.13 from [python.org](https://www.python.org/downloads/windows/)
   (*Windows installer (64-bit)*, default options) and start `run_windows.bat` again.
4. Keep the black window open while you work.

### macOS

1. In the tool folder, double-click **`run_mac.command`**.
2. If macOS says it cannot open the file (*Apple could not verify…* or
   *unidentified developer*), close the message, then:
   - macOS 15 and newer: **System Settings** → **Privacy & Security**; near the bottom, next
     to *run_mac.command*, click **Open Anyway** and confirm;
   - older macOS: right-click (Control-click) `run_mac.command` → **Open** → **Open**.

   Without any warning: open the **Terminal** app, type `bash ` (with a trailing space),
   drag `run_mac.command` into the Terminal window and press **Enter**.
3. If the Mac has no suitable Python, python.org opens: download and install the
   *macOS 64-bit universal2 installer*, then start `run_mac.command` again.
4. If macOS asks whether Terminal may access the *Downloads* folder, click **Allow**.
   Keep the Terminal window open while you work.

### Linux

In a terminal, in the tool folder, run `bash run_linux.sh`.
It needs Python 3 with Tk and venv, for example on Ubuntu/Debian:
`sudo apt install python3 python3-tk python3-venv`.

## 3. First start

- Enter your **full name**. It identifies all your annotations, so always type it the
  same way. The tool remembers it; **Change annotator…** changes it.
- The tool finds the `test_VAD` folder by itself. If it does not, select the folder you
  extracted `test_VAD.zip` into. **Change dataset folder…** changes it later.

## 4. Annotating

1. Select a scene and click **Open scene** (or double-click the scene).
2. Three synchronized videos are shown:
   - **RGB**: the normal video,
   - **IR – relative**: thermal image with the contrast adapted to each frame (shows shapes),
   - **IR – absolute**: thermal image on a fixed temperature scale (type the range into
     **Abs. range (°C)**, or click **Video range** for the range of the whole video).

   With the mouse over an IR view, you see the temperature in °C.
3. **Segments:** stop the video at the frame where a new segment starts and press **B**.
   A new segment starts when something appears or disappears, or when a person changes
   their action. Segments follow each other and cover the whole video.
4. **Captions:** for each segment (select it in the list on the left), write four short
   captions **in English**:

   | Field | What to describe |
   |---|---|
   | 1. RGB initial state | initial state: relevant objects and persons and where they are |
   | 2. Dynamics in RGB | actions, events and changes during the segment (RGB only) |
   | 3. IR initial state | what is warmer or colder than its surroundings at the start, and where |
   | 4. Dynamics in IR | whether the temperature rises, falls or stays stable; whether the warm area grows or shrinks |

   Write objectively, only what is visible: do not interpret danger or people's intentions,
   and avoid vague words such as *slightly*, *slowly* or *rapidly*. Do not refer to previous
   segments. The buttons next to the fields insert standard sentences (e.g. **No changes**).
   Detailed guidelines are in the tool: **Boundary instructions…** and **Caption instructions…**.
5. Save with **Ctrl+S** (Mac: **Cmd+S**). You can save unfinished work and continue later.

| Key | Action |
|---|---|
| Space | play / pause |
| ← / → | one frame back / forward |
| ↑ / ↓ | 10 frames back / forward |
| B | a new segment starts at this frame |
| Delete | remove the start boundary of the selected segment |
| F1 | help |

## 5. Sending your annotations

1. In the main window, click **Export all my annotations**, then **Yes** to open the folder.
2. Send the file **`combined_export.json`** to the project coordinator.

Annotations are saved in the tool folder, in `annotations/<your_name>/`. Do not delete it.

## 6. Updating the tool

1. Download and extract the new version (see step 1). Keep the old folder for now.
2. Copy the **`annotations`** folder and the **`annotator_config.json`** file from the old
   tool folder into the new one.
3. Start the new version and check that your annotations are there. Only then delete the old folder.

## Troubleshooting

| Problem | Solution |
|---|---|
| A blank (white) window on a Mac | Start the tool with `run_mac.command`, not with `python3 annotate_gui.py`. If that does not help, install Python 3.13 from python.org. |
| *annotate_gui.py not found* | The ZIP was not extracted. Extract it (step 1) and start the tool from the extracted folder. |
| *No fire-VAD videos were found* | Extract `test_VAD.zip` and select the extracted folder. |
| Installing numpy/Pillow fails | Check the internet connection and start again. If it still fails, install Python 3.13 and delete the `.venv-annotator` folder in the tool folder (on a Mac, **Cmd+Shift+.** shows hidden folders). |
| Anything else | Send the coordinator a screenshot of the black window (Windows) or the Terminal window (macOS). |

## For developers

### Repository layout

| Path | Purpose |
|---|---|
| `annotate_gui.py` | the whole application (Tkinter, numpy, Pillow) |
| `run_windows.bat`, `run_mac.command`, `run_linux.sh` | launchers: select Python 3.9+ with Tk 8.6+, create `.venv-annotator`, install `requirements.txt`, start the app |
| `tests/` | unit and launcher tests, synthetic dataset generator |
| `tools/` | dataset maintenance: `convert_ir_to_npz.py`, `make_dataset_zip.py` |
| `.github/workflows/tests.yml` | CI on Windows, macOS and Linux |

**Download ZIP** leaves out `tests/`, `tools/` and `.github/` (`export-ignore` in
`.gitattributes`); clone the repository to get them.

### Tests

From the repository folder, with a Python that has numpy, Pillow and tkinter (for example
`.venv-annotator/bin/python` after the first start):

```bash
python -m unittest discover -s tests -v                       # unit and launcher tests
python tests/make_test_dataset.py /tmp/firevad-data --wrap    # small synthetic dataset
python annotate_gui.py --selftest --dataset-root /tmp/firevad-data
python annotate_gui.py --guitest --dataset-root /tmp/firevad-data   # opens windows
```

On a headless Linux machine, run the GUI test with `xvfb-run -a`. CI starts each launcher
the way annotators do (new `.venv-annotator`, pip install), then runs the steps above on
Windows (Python 3.13 and 3.14), macOS (3.13) and Linux (3.9 and 3.13).

### Launcher options

- `--check-runtime` prints the selected Python and Tk and changes nothing.
- `FIREVAD_PYTHON=/path/to/python` selects the interpreter. An unusable one is an error;
  the launcher does not silently fall back to another Python.
- `FIREVAD_NONINTERACTIVE=1` never waits for a key, opens a browser or installs Python.
- All other arguments go to `annotate_gui.py`, for example `--dataset-root PATH` or `--selftest`.

### Dataset format

```text
test_VAD/
  environment_1/
    2/                 scene (video_id 2)
      RGB/0.jpg ...    RGB frames
      IR.npz           key "frames": float16 °C matrices, shape (N, 400, 540)
      annotations.csv  per-frame labels: maintainers only, never shown or shipped
```

Older scenes with one `IR/<frame>.npy` file per frame also work.
`tools/convert_ir_to_npz.py` packs them into `IR.npz`; it verifies each archive before it
deletes the old files (`--dry-run` only reports).

### Publishing the videos

```bash
python tools/make_dataset_zip.py ../test_VAD    # writes ../test_VAD.zip
```

The ZIP leaves out `annotations.csv` and OS files, and it is verified (CRC, file list,
sizes) before it gets its final name. Upload it to Google Drive, share it with
*Anyone with the link*, and put the link into both READMEs.

### Output

One file per video, `annotations/<annotator>/environment_<X>/<Y>.json`:

```json
{
  "video_id": 2,
  "environment": 1,
  "anomaly_subtype": null,
  "annotator_id": "Ivana Šimić",
  "segments": [
    {
      "segment_id": 0,
      "start_frame": 0,
      "end_frame": 50,
      "caption_rgb_initial": "...",
      "caption_rgb_dynamics": "...",
      "caption_ir_initial": "...",
      "caption_ir_dynamics": "...",
      "temp_min_c": 18.2,
      "temp_max_c": 22.0
    }
  ]
}
```

The folder name is an ASCII version of the annotator's name (`Ivana_Simic`).
**Export all my annotations** collects all files into
`annotations/<annotator>/combined_export.json` (`annotator_id`, `generated_at`,
`dataset_root`, `annotations`). `annotator_config.json` and `annotations/` are personal
and ignored by git.
