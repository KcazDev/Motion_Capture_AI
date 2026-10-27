# MotionAI

### Human Movement Assessment and Spatial Intelligence  
**GIMM at Boise State University | R CON 2026**

MotionAI is a human movement analysis project that combines motion capture data, computer vision, and machine learning.

The project started with Rokoko motion capture recordings and later expanded into a camera based system that can track a person using a normal webcam.

The goal of the project was to explore whether detailed motion capture data could be used as a reference while a simpler camera based system was used for live movement analysis.

MotionAI was developed through the Games, Interactive Media, and Mobile Technology program at Boise State University and was demonstrated at R CON 2026.

---

## Project Overview

A lot of motion analysis systems require things like motion capture suits, wearable sensors, special cameras, or lab equipment.

For this project, I wanted to explore whether some of that information could be made more accessible using a normal webcam.

The system uses two main parts.

The first part uses Rokoko motion capture data to create detailed reference motion.

The second part uses MediaPipe and a webcam to track a person live.

The project then converts both systems into similar movement measurements so they can be compared at a higher level.

```text id="m8q3di"
Rokoko Motion Capture
        ↓
FBX Motion Data
        ↓
MotionAI Conversion
        ↓
Reference Motion Profiles
        ↓
Shared Movement Features
        ↑
MediaPipe Pose Tracking
        ↑
Webcam
```

---

# Technologies Used

MotionAI was built with:

* Python
* OpenCV
* MediaPipe Pose Landmarker
* NumPy
* scikit learn
* Rokoko Studio
* Rokoko SmartSuit Pro
* Rokoko Smartgloves
* Blender
* FBX motion data
* Windows System Speech

---

# Motion Capture Dataset

The MotionAI dataset contains 25 full body motion capture recordings.

There are five activity classes with five recordings each.

| Activity | Recordings |
|---|---:|
| Box Lift | 5 |
| Box Carry | 5 |
| Hammer Strike | 5 |
| Material Place | 5 |
| Overhead Work | 5 |
| Total | 25 |

Each recording was captured at 30 FPS and contains around 75 tracked bones per frame.

The Rokoko recordings were exported as FBX files and then converted into JSON files for use in MotionAI.

Example project data structure:

```text id="yl1o6u"
data/
├── raw/
│   ├── box_lift_001.fbx
│   ├── box_carry_001.fbx
│   ├── hammer_strike_001.fbx
│   ├── material_place_001.fbx
│   └── overhead_work_001.fbx
│
├── processed/
│   ├── box_lift_001.json
│   ├── box_carry_001.json
│   └── ...
│
├── ml/
│   ├── features.npy
│   ├── labels.npy
│   └── metadata.json
│
└── reference/
    └── motion_profiles.json
```

---

# Motion Data Format

Each converted motion file stores information about the recording and the body joints for every frame.

```text id="6pg7b4"
Session
├── Activity
├── FPS
├── Subject
├── Source
├── Metadata
└── Frames
      ├── Timestamp
      ├── Root Position
      ├── Root Rotation
      └── Joints
            ├── Position
            └── Rotation
```

The coordinate system used in the project is:

```text id="4zv8gh"
X = Side
Y = Height
Z = Forward
```

This makes it possible to measure both body posture and movement through space.

---

# Shared Movement Features

One of the main problems I had to solve was that Rokoko and MediaPipe do not use the same skeleton.

Rokoko gives detailed 3D joint data while MediaPipe uses 33 pose landmarks.

Because of that, I did not directly compare the raw skeletons.

Instead, both systems are converted into higher level movement features.

These features include:

## Posture

* Torso lean
* Left and right knee angles
* Average knee angle
* Hip angles
* Shoulder tilt
* Hip tilt

## Hand and Work Height

* Wrist position
* Hand height
* Hand height relative to the hips
* Hand height relative to the shoulders
* Overhead movement

## Spatial Movement

* Pelvis position
* Horizontal displacement
* Forward and backward movement
* Total body path
* Workspace travel
* Direction of movement
* Movement normalized by body size

## Timing

* Movement duration
* Maximum torso lean
* Minimum knee angle
* Movement range
* Time spent above shoulder height

The main idea is:

```text id="8djvr9"
Rokoko Skeleton
       ↓
Movement Features
       ↓
   MotionAI
       ↑
Movement Features
       ↑
MediaPipe Pose
```

---

# Reference Motion Profiles

All 25 motion capture recordings were processed into reference profiles.

The recordings showed different movement patterns depending on the activity.

Average results from the dataset:

| Activity | Max Torso Lean | Min Knee Angle | Max Hand Height | Overhead Ratio | Horizontal Displacement |
|---|---:|---:|---:|---:|---:|
| Box Lift | 33.66° | 48.98° | 0.794 | 0.000 | 0.239 |
| Box Carry | 37.55° | 49.20° | 0.794 | 0.000 | 1.390 |
| Hammer Strike | 9.00° | 143.44° | 0.798 | 0.000 | 1.890 |
| Material Place | 36.14° | 39.85° | 0.795 | 0.000 | 1.114 |
| Overhead Work | 21.56° | 143.57° | 1.033 | 0.438 | 0.849 |

Some values are normalized using estimated body dimensions.

For example, the overhead work recordings spent about 43.8 percent of the recording with both hands above shoulder level.

The lifting recordings showed more lower body movement and deeper knee angles.

These numbers are only reference values from the recorded dataset.

They are not professional ergonomic or safety standards.

---

# Activity Recognition

I also built a machine learning pipeline to recognize the five recorded activities.

Each motion recording was converted into about 415 features.

A Random Forest classifier was trained using the 25 recorded samples.

During the project evaluation, the model correctly classified all five held out samples and also reached 100 percent accuracy during five fold stratified cross validation.

```text id="9pgdjv"
5 out of 5 held out predictions correct
100 percent five fold cross validation accuracy
```

These results are from a very small dataset.

The recordings were also collected in a limited environment, so this should not be treated as real world accuracy.

The result mainly showed that the five recorded motion classes were very different from each other inside this dataset.

A much larger dataset with multiple people would be needed to test generalization.

---

# Camera Based Tracking

The live part of MotionAI uses MediaPipe Pose Landmarker and a standard webcam.

The camera tracks body landmarks such as:

```text id="91jhfw"
Shoulders
Elbows
Wrists
Hips
Knees
Ankles
```

The system then calculates movement measurements including:

```text id="ynl2at"
Torso Lean
Knee Angle
Hip Angle
Shoulder Tilt
Hip Tilt
Wrist Height
Body Visibility
Movement State
```

This allows the camera version of MotionAI to work without the Rokoko suit.

---

# Movement State Detection

Instead of looking at only one frame, MotionAI tracks movement over time.

For example, the lifting system uses states like:

```text id="6co8kg"
CALIBRATING
     ↓
READY
     ↓
LOWERING
     ↓
BOTTOM
     ↓
LIFTING
     ↓
COMPLETE
```

This helped the system understand when a lift started, when the person reached the bottom of the movement, and when the lift was completed.

---

# R CON Demonstration

For R CON 2026, MotionAI was built into an interactive demonstration.

People could stand in front of the camera and perform physical movements while the system tracked their body position and movement.

The final project focused on a basic material handling workflow:

```text id="3vf4f2"
PICKUP
   ↓
TRANSPORT
   ↓
HIGH WORK
   ↓
PLACEMENT
```

The goal was to move beyond detecting one pose and instead look at how a person moves through a task over time.

---

# Movement Assessment

The prototype assessment system looks at several movement measurements.

These include:

* Torso movement
* Knee movement
* Hip movement
* Body alignment
* Tracking quality
* Movement completion
* Spatial movement
* Hand and work height

The system can return:

```text id="0avlwv"
PASS
FAIL
RETRY
```

RETRY is used when the camera does not have enough tracking information to make a good assessment.

---

# Feedback

MotionAI provides both visual and spoken feedback.

Examples include:

```text id="j1d2t9"
Reduce forward torso lean.

Use more lower body movement.

Maintain more balanced movement.

Keep your full body visible.
```

The goal was to make the results understandable instead of only showing a score.

---

# R CON Interface

The final R CON interface includes:

* Live webcam feed
* Pose skeleton overlay
* Movement state
* Assessment progress
* PASS, FAIL, or RETRY results
* Movement score
* Participant instructions
* Debug information
* Final assessment results

The final branding used during the project was:

```text id="tyrw7p"
MOTIONAI
GIMM Boise State University
R CON 2026
```

---

# Project Structure

```text id="e7wvu3"
Rcon_MotionAi/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── ml/
│   └── reference/
│
├── demo/
│   ├── rcon_assessment.py
│   ├── stacking_assessment.py
│   └── rcon_ui_preview.py
│
├── models/
│   ├── pose_landmarker_full.task
│   └── activity_classifier.pkl
│
├── Scripts/
│   ├── convert_rokoko_fbx.py
│   ├── batch_convert_rokoko.py
│   ├── build_ml_dataset.py
│   ├── evaluate_activity_classifier.py
│   ├── inspect_processed_dataset.py
│   ├── build_reference_profiles.py
│   └── test_shared_motion_features.py
│
└── src/
    ├── analysis/
    │   └── shared_motion_features.py
    │
    ├── assessment/
    │   ├── lift_analyzer.py
    │   ├── movement_metrics.py
    │   ├── scoring.py
    │   └── session_manager.py
    │
    ├── feedback/
    │   └── voice.py
    │
    ├── ui/
    │   └── rcon_display.py
    │
    ├── vision/
    │   ├── camera.py
    │   ├── landmark_utils.py
    │   └── pose_tracker.py
    │
    └── motion_frame.py
```

---

# Running the Camera Demo

Create a Python virtual environment.

```powershell id="t2op0f"
python -m venv .venv
.\.venv\Scripts\activate
```

Install the required dependencies.

Then run:

```powershell id="woepmm"
python -m demo.rcon_assessment
```

To run without voice feedback:

```powershell id="rf6vss"
python -m demo.rcon_assessment --mute
```

Camera settings can also be changed:

```powershell id="a09keb"
python -m demo.rcon_assessment --camera 0 --width 1280 --height 720 --fps 30
```

---

# UI Preview

A camera free preview is also included.

Run:

```powershell id="u20b95"
python -m demo.rcon_ui_preview
```

Fullscreen:

```powershell id="4cbhtm"
python -m demo.rcon_ui_preview --fullscreen
```

Controls:

```text id="s26rcv"
SPACE   Start
P       Simulate PASS
F       Simulate FAIL
T       Simulate RETRY
R       Restart
Q       Exit
```

---

# Project Development

MotionAI changed a lot during development.

## Motion Capture

The project first focused on collecting detailed human movement using the Rokoko suit and gloves.

## Machine Learning

The motion capture recordings were converted into structured data and used to train an activity classifier.

## Webcam Tracking

MediaPipe was added so the project could track movement using a normal camera.

## Live Assessment

The webcam tracking was combined with movement detection, scoring, voice feedback, and a user interface.

## Spatial Movement

The final part of the project focused on connecting the detailed motion capture data with the simpler webcam tracking using shared movement features.

This changed the project from only being about lifting into a broader system for looking at how people perform physical tasks.

---

# Possible Future Work

Some things I would like to explore in the future include:

* Recording more people
* Building a larger motion dataset
* Adding more physical activities
* Improving camera to motion capture comparison
* Using multiple cameras
* Adding depth cameras
* Testing sports movements
* Baseball swing analysis
* Automatic task detection
* Better movement reports
* Web based visualization
* More advanced machine learning models

---

# Limitations

MotionAI is still a research prototype.

Current limitations include:

* Small dataset
* Limited number of participants
* Webcam depth limitations
* Camera placement affects tracking
* Occlusion can affect landmarks
* Prototype scoring rules
* No medical validation
* No professional ergonomic validation
* No workplace safety certification

The project should not be used as a replacement for medical, ergonomic, or professional safety evaluation.

---

# What I Learned

This project gave me experience working with several different areas of technology in one system.

I worked with:

* Motion capture
* Computer vision
* Pose estimation
* Machine learning
* Data processing
* 3D coordinates
* Human movement analysis
* User interface design
* Real time systems
* Voice feedback

One of the biggest things I learned was that collecting the data is only part of the problem.

The harder part was figuring out how to take information from different systems and turn it into measurements that could actually be compared.

---

# R CON 2026

MotionAI was developed through Boise State University's GIMM program and demonstrated at R CON 2026.

The final project combined:

```text id="uisbmg"
Computer Vision
+
Machine Learning
+
Motion Capture
+
Human Movement Analysis
+
Interactive Media
```

---

# Author

**Zackery Lake**

AI Developer and Student Researcher  
Games, Interactive Media, and Mobile Technology  
Boise State University

Portfolio:

**https://kcazdev.github.io**

GitHub:

**https://github.com/KcazDev**

LinkedIn:

**https://www.linkedin.com/in/kcazdev**

---

# Disclaimer

MotionAI is an experimental student research project.

The movement scores, classifications, and feedback generated by the system are prototype results.

They should not be treated as medical advice, professional ergonomic analysis, or certified workplace safety guidance.

---

## Boise State University

**Games, Interactive Media, and Mobile Technology**

**R CON 2026**
