# R-CON MotionAI webcam demo

This increment adds a local webcam, skeleton overlay, projected torso/knee/hip
angles, wrist height/reach and relative hand speed, automatic lift segmentation,
configurable pass/fail reasons, optional Windows speech, and optional JSONL results.
It evaluates observed human movement, not box sizes, stacking order, grip, or placement.
The original Rokoko prototype and its requirements remain independent.

## Launch on Windows

Open PowerShell in `C:\Users\Ekalk\Desktop\Rcon_MotionAi`:

```powershell
.\Setup-Camera.ps1
.\Start-Camera.ps1
.\Start-MotionAI.ps1 -Voice
```

Setup makes a separate `.venv-camera` environment, installs the camera dependencies,
and downloads Google's lightweight pose model once. Subsequent runs work offline.
If PowerShell script execution is disabled, use these equivalent commands:

```powershell
python -m venv .venv-camera
.\.venv-camera\Scripts\python.exe -m pip install -r requirements-camera.txt
.\.venv-camera\Scripts\python.exe -m demo.setup_camera
.\.venv-camera\Scripts\python.exe -m src.vision.camera
.\.venv-camera\Scripts\python.exe -m demo.stacking_assessment --voice
```

First close the camera preview with Q or Escape before starting the assessment.
Use `-Camera 1` on either launcher if the desired webcam is the second device.
Close other camera applications if opening fails. Check Windows camera access
for desktop applications. Actual dimensions and FPS depend on the webcam.

## Participant setup

Keep one participant's shoulder, wrist, hip, knee and ankle in view. Place the
camera approximately side-on, steady, level, and far enough away for the entire
movement to remain visible. Select the anatomical side nearest the camera:
` .\Start-MotionAI.ps1 -Side right -Voice ` (default: left).
Use good lighting and avoid boxes occluding the selected arm and leg.

1. Stand tall until the display says READY.
2. Bend/reach for the box, then lift and stand tall with the hand raised.
3. Hold briefly to finish. Read the last-attempt result and spoken explanation.
4. Stand tall again before the next attempt. R clears the session; Q/Escape exits.

The state machine detects a bend-and-rise pattern. It does not detect object
contact or confirm a real box lift. A practice movement can also count. Carrying,
placing at a high shelf, partial lifts, and lifts without the required bend/rise
may not segment correctly. These need later task-specific calibration.

Tracking uncertainty pauses measurement. A gap longer than 0.25 seconds during
an attempt produces UNASSESSED and requires a fresh start. An incomplete attempt
times out after 15 seconds. No pose or multiple detected poses blocks measurement.
The detector can still miss an additional person; keep the demonstration area clear.

## Rules and interpretation

Edit `config/assessment_rules.json` to tune thresholds. All defaults are illustrative
engineering values, not validated clinical, ergonomic, or workplace safety limits.
PASS means the visible movement met these rules. FAIL supplies the rules it missed.
UNASSESSED means there was insufficient continuous tracking or no completed cycle.

Angles use image-plane pixel coordinates, correcting the image aspect ratio.
Only the selected side is measured; the visible skeleton includes both sides when
confident. Distances use torso lengths (TL), not meters. Speed measures hand motion
relative to the hip in TL/second; changing pose perspective also affects it.
Torso, reach, and speed rules use their 90th percentile during the attempt to
reduce isolated jitter. Knee bend uses the smallest observed knee angle.
Single-camera projection and occlusion prevent reliable claims about true spinal
flexion, twisting, load weight, grip quality, balance, or injury risk.

## Optional results and tests

```powershell
.\.venv-camera\Scripts\python.exe -m demo.stacking_assessment --results results\camera-session.jsonl
.\.venv-camera\Scripts\python.exe -m unittest discover -s tests -p test_camera_assessment.py -v
```

No video or images are saved. Optional results contain timestamps, attempt numbers,
rules, metrics and reasons. R resets the displayed attempt count; it does not erase
an existing results file. Use a new filename per participant/session.

Hardware-independent tests cover camera fallback and cleanup, geometry, rule
outcomes, full-cycle counting, timeout, tracking loss, and camera stalls. A real
participant trial is required to tune thresholds and confirm voice/visual behavior.

Pose integration follows Google's MediaPipe Tasks VIDEO API:
https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python
