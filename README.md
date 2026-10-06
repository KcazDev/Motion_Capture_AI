# MotionAI

### Human Movement Assessment for R-CON 2026  
**GIMM — Boise State University**

MotionAI is a camera-based human movement assessment system designed to evaluate physical task performance in real time.

Using a standard webcam, computer vision, pose estimation, and explainable movement scoring, MotionAI tracks how a person performs a lifting task, identifies key body mechanics, evaluates the completed movement, and immediately provides visual and spoken feedback.

The current prototype was developed for **R-CON 2026** as an interactive construction-technology demonstration.

---

## Overview

Traditional motion-analysis systems often require specialized motion-capture suits, wearable sensors, or dedicated laboratory equipment.

MotionAI explores a different question:

> **Can meaningful human movement assessment be performed using only a standard camera?**

The current system demonstrates that workflow through a box-lifting and stacking challenge.

A participant steps into the assessment area, completes a series of lifts, and receives immediate feedback based on their observed movement.

```text
Camera
  ↓
Human Pose Detection
  ↓
Body Landmarks
  ↓
Movement Metrics
  ↓
Lift Phase Detection
  ↓
Technique Assessment
  ↓
PASS / FAIL / RETRY
  ↓
Visual + Voice Feedback
