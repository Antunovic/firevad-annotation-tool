# Fire-VAD Annotation Tool

A desktop tool for annotating videos of the fire-VAD dataset (RGB and thermal/IR
camera). In one window, the annotator marks the frame where each new segment starts
and writes the captions for every segment.

Ready-made apps for Windows, macOS and Linux: no Python and no installation needed.

## 1. Download

1. **The app:** open the [latest release](https://github.com/Antunovic/firevad-annotation-tool/releases/latest)
   and download the file for your computer:

   | System | File |
   |---|---|
   | Windows | `FireVAD-Annotator-Windows.zip` |
   | Mac with Apple chip (M1, M2, M3, ...) | `FireVAD-Annotator-macOS-AppleSilicon.zip` |
   | Mac with Intel processor | `FireVAD-Annotator-macOS-Intel.zip` |
   | Linux | `FireVAD-Annotator-Linux.tar.gz` |

   On a Mac, **Apple menu → About This Mac** shows *Chip: Apple M…* or *Processor: Intel*.

2. **The videos:** `test_VAD.zip` (about 3 GB). The coordinator sends you the Google Drive link.
   Google Drive says it cannot scan such a large file for viruses; click **Download anyway**.

3. Extract both ZIP files, for example into *Downloads*. Keep the folder `test_VAD`
   next to the app folder or in the same parent folder; the app finds it by itself
   (extra folders created by extracting, such as `test_VAD/test_VAD`, are fine).
   If it does not find the videos, it asks you to select the folder.

## 2. Start

### Windows

1. Right-click the ZIP → **Properties**, tick **Unblock**, click **OK** (this avoids most warnings).
   Then right-click → **Extract All…**. Do not start the app from inside the ZIP.
2. Open the extracted folder and double-click **`FireVAD-Annotator.exe`**.
3. If *Windows protected your PC* appears: **More info** → **Run anyway**.

### macOS

1. Double-click the ZIP to extract it. Drag **FireVAD-Annotator** into *Applications* (optional).
2. Double-click the app. The app is not signed by Apple, so macOS first refuses to open it
   (*"FireVAD-Annotator" cannot be opened*). Then:
   - **macOS 15 and newer:** close the message, open **System Settings → Privacy & Security**, scroll down,
     click **Open Anyway** next to *FireVAD-Annotator* and confirm.
   - **Older macOS:** right-click (Control-click) the app → **Open** → **Open**.
   - Or in the **Terminal** app: `xattr -dr com.apple.quarantine /path/to/FireVAD-Annotator.app`
     (drag the app into the Terminal window instead of typing the path).

   This is needed only the first time.
3. If macOS asks whether the app may access the *Downloads* folder, click **Allow**.

### Linux

```bash
tar -xzf FireVAD-Annotator-Linux.tar.gz
./FireVAD-Annotator/FireVAD-Annotator
```

Built on Ubuntu 22.04; it needs a desktop session (X11, or Wayland with XWayland).

## 3. First start

On the first start you are asked for your **full name**. It identifies all your annotation
files, so always type it the same way. **Change annotator…** changes it later;
**Change dataset folder…** changes the folder with the videos.

Your work is saved in the folder **`FireVAD-Annotator` in your home folder**
(Windows: `C:\Users\<you>\FireVAD-Annotator`, macOS: `/Users/<you>/FireVAD-Annotator`):

```
FireVAD-Annotator/
  annotator_config.json                              saved name and videos location
  annotations/<your_name>/environment_<X>/<Y>.json   one file per video
```

The videos are never modified. Do not delete this folder; unfinished work continues from there.

## 4. Annotating

1. Select a scene, press **Open scene**. Three synchronized panels open:
   **RGB**, **IR – relative** (contrast stretched per frame, shows structure) and
   **IR – absolute** (fixed temperature scale: type the range or press
   **Video range**). Hovering the mouse over an IR panel shows the exact
   temperature in °C.
2. Pause at the frame where a new segment starts and press **B**. A new segment
   starts when something appears or disappears, or when a person changes their
   action. Segments are consecutive and cover the whole video.
3. Write short captions **in English**. The **first segment** (the start of the video)
   gets all four: RGB initial state, RGB dynamics, IR initial state, IR dynamics.
   Every **later segment** gets only the two dynamics captions; its initial-state
   fields are greyed out. Preset buttons insert standard sentences for common cases
   ("No changes", "No temperature differences", …).
4. Save with **Ctrl+S** (macOS: **Cmd+S**). You can stop at any time and continue later.
5. When you are done, click **Export all my annotations** and **Yes** to open the folder.
   Send the file **`combined_export.json`** to the coordinator.

| Key | Action |
|---|---|
| Space | play / pause |
| ← / → | one frame back / forward |
| ↑ / ↓ | 10 frames back / forward |
| Home / End | first / last frame |
| B | a new segment starts at the current frame |
| Delete | remove the start boundary of the selected segment |
| F1 | help |

## Troubleshooting

| Problem | Fix |
|---|---|
| Windows or macOS refuses to start the app | See "Start" above: **Run anyway** (Windows), **Open Anyway** (macOS). |
| `No fire-VAD videos were found` | Extract `test_VAD.zip` and select the folder with **Change dataset folder…**. |
| The app closes with an error message | Send the coordinator the file it names (`error.log` in the `FireVAD-Annotator` folder). |
| Anything else | Send the coordinator a screenshot. |

## Run from source (developers)

Needs Python 3.9+ with **Tk 8.6+** (`tkinter` comes with Python; on Linux
`sudo apt install python3-tk`; on macOS use Python from python.org, because Apple's bundled
Python has Tk 8.5 and shows a blank window), plus the packages in `requirements.txt`:

```bash
git clone https://github.com/Antunovic/firevad-annotation-tool.git
cd firevad-annotation-tool
pip install -r requirements.txt
python annotate_gui.py
```

When run from source, the config and annotations are stored in the repository folder instead.
`python annotate_gui.py --selftest` runs a headless self-check. The apps are built
by the *build-apps* workflow (PyInstaller); pushing a tag such as `v1.0.1` publishes a new release.
