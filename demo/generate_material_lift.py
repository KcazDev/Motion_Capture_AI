import json
from dataclasses import asdict

from src.motion_frame import JointData, MotionFrame, MotionSession


FPS = 60
DURATION = 6
TOTAL_FRAMES = FPS * DURATION


def joint(x, y, z=0.0):
    return JointData(position=[x, y, z])


def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * t


def smoothstep(t):
    """Makes transitions less robotic."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def phase_progress(time, start, end):
    """
    Returns smooth progress from 0 → 1
    during a specified time range.
    """
    if time <= start:
        return 0.0

    if time >= end:
        return 1.0

    t = (time - start) / (end - start)
    return smoothstep(t)


def main():

    session = MotionSession(
        session_id="material_lift_001",
        activity="ground_to_table_lift",
        fps=FPS,
        subject_id="synthetic_worker_001",
        source="synthetic"
    )

    for frame_number in range(TOTAL_FRAMES):

        time = frame_number / FPS

        frame = MotionFrame(timestamp=time)

        # ---------------------------------------------------------
        # MOTION PHASES
        #
        # 0.0 - 1.0  Standing
        # 1.0 - 2.0  Squat / reach
        # 2.0 - 3.2  Lift material
        # 3.2 - 4.2  Move toward table
        # 4.2 - 5.2  Place material
        # 5.2 - 6.0  Return neutral
        # ---------------------------------------------------------

        squat = phase_progress(time, 1.0, 2.0)

        lift = phase_progress(time, 2.0, 3.2)

        travel = phase_progress(time, 3.2, 4.2)

        place = phase_progress(time, 4.2, 5.2)

        reset = phase_progress(time, 5.2, 6.0)

        # ---------------------------------------------------------
        # BODY HEIGHT
        # ---------------------------------------------------------

        standing_pelvis_y = 1.00
        squat_pelvis_y = 0.62

        # Squat down
        pelvis_y = lerp(
            standing_pelvis_y,
            squat_pelvis_y,
            squat
        )

        # Stand back up while lifting
        pelvis_y = lerp(
            pelvis_y,
            standing_pelvis_y,
            lift
        )

        # ---------------------------------------------------------
        # HORIZONTAL BODY MOVEMENT
        # ---------------------------------------------------------

        pelvis_x = lerp(
            0.0,
            0.55,
            travel
        )

        pelvis_x = lerp(
            pelvis_x,
            0.0,
            reset
        )

        # Slight forward lean in Z axis
        torso_z = lerp(
            0.0,
            0.25,
            squat
        )

        torso_z = lerp(
            torso_z,
            0.0,
            lift
        )

        # ---------------------------------------------------------
        # CORE BODY
        # ---------------------------------------------------------

        frame.joints["pelvis"] = joint(
            pelvis_x,
            pelvis_y,
            0.0
        )

        frame.joints["spine"] = joint(
            pelvis_x,
            pelvis_y + 0.32,
            torso_z
        )

        frame.joints["neck"] = joint(
            pelvis_x,
            pelvis_y + 0.62,
            torso_z
        )

        frame.joints["head"] = joint(
            pelvis_x,
            pelvis_y + 0.82,
            torso_z
        )

        # ---------------------------------------------------------
        # HIPS / LEGS
        # ---------------------------------------------------------

        hip_spacing = 0.16

        frame.joints["left_hip"] = joint(
            pelvis_x - hip_spacing,
            pelvis_y - 0.05,
            0.0
        )

        frame.joints["right_hip"] = joint(
            pelvis_x + hip_spacing,
            pelvis_y - 0.05,
            0.0
        )

        # Knees move forward during squat
        knee_forward = lerp(
            0.0,
            0.20,
            squat
        )

        knee_y = lerp(
            0.52,
            0.32,
            squat
        )

        knee_y = lerp(
            knee_y,
            0.52,
            lift
        )

        knee_forward = lerp(
            knee_forward,
            0.0,
            lift
        )

        frame.joints["left_knee"] = joint(
            pelvis_x - hip_spacing,
            knee_y,
            knee_forward
        )

        frame.joints["right_knee"] = joint(
            pelvis_x + hip_spacing,
            knee_y,
            knee_forward
        )

        frame.joints["left_ankle"] = joint(
            pelvis_x - hip_spacing,
            0.05,
            0.05
        )

        frame.joints["right_ankle"] = joint(
            pelvis_x + hip_spacing,
            0.05,
            0.05
        )

        # ---------------------------------------------------------
        # SHOULDERS
        # ---------------------------------------------------------

        shoulder_y = pelvis_y + 0.57

        frame.joints["left_shoulder"] = joint(
            pelvis_x - 0.25,
            shoulder_y,
            torso_z
        )

        frame.joints["right_shoulder"] = joint(
            pelvis_x + 0.25,
            shoulder_y,
            torso_z
        )

        # ---------------------------------------------------------
        # ARMS
        # ---------------------------------------------------------

        # Normal arm positions
        left_elbow_x = pelvis_x - 0.30
        right_elbow_x = pelvis_x + 0.30

        elbow_y = shoulder_y - 0.30
        wrist_y = shoulder_y - 0.58

        elbow_z = torso_z
        wrist_z = torso_z

        # During squat, reach toward the ground/object
        reach_amount = squat

        elbow_y = lerp(
            elbow_y,
            0.48,
            reach_amount
        )

        wrist_y = lerp(
            wrist_y,
            0.22,
            reach_amount
        )

        elbow_z = lerp(
            elbow_z,
            0.28,
            reach_amount
        )

        wrist_z = lerp(
            wrist_z,
            0.38,
            reach_amount
        )

        # Lift hands up with material
        carry_height = 1.05

        elbow_y = lerp(
            elbow_y,
            1.20,
            lift
        )

        wrist_y = lerp(
            wrist_y,
            carry_height,
            lift
        )

        elbow_z = lerp(
            elbow_z,
            0.18,
            lift
        )

        wrist_z = lerp(
            wrist_z,
            0.28,
            lift
        )

        # Move arms with worker toward table
        left_elbow_x += pelvis_x
        right_elbow_x += pelvis_x

        # Correct double-offset from pelvis
        left_elbow_x -= pelvis_x
        right_elbow_x -= pelvis_x

        # Placement motion: extend arms slightly
        extension = lerp(
            0.0,
            0.18,
            place
        )

        wrist_z += extension
        elbow_z += extension * 0.5

        # Lower slightly onto surface
        wrist_y = lerp(
            wrist_y,
            0.92,
            place
        )

        # Reset arms
        elbow_y = lerp(
            elbow_y,
            shoulder_y - 0.30,
            reset
        )

        wrist_y = lerp(
            wrist_y,
            shoulder_y - 0.58,
            reset
        )

        elbow_z = lerp(
            elbow_z,
            0.0,
            reset
        )

        wrist_z = lerp(
            wrist_z,
            0.0,
            reset
        )

        frame.joints["left_elbow"] = joint(
            pelvis_x - 0.30,
            elbow_y,
            elbow_z
        )

        frame.joints["right_elbow"] = joint(
            pelvis_x + 0.30,
            elbow_y,
            elbow_z
        )

        frame.joints["left_wrist"] = joint(
            pelvis_x - 0.20,
            wrist_y,
            wrist_z
        )

        frame.joints["right_wrist"] = joint(
            pelvis_x + 0.20,
            wrist_y,
            wrist_z
        )

        session.frames.append(frame)

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    output_path = "data/samples/material_lift_001.json"

    with open(output_path, "w") as file:
        json.dump(
            asdict(session),
            file,
            indent=4
        )

    print()
    print("Rcon MotionAI")
    print("-----------------------------")
    print("Construction motion generated!")
    print()
    print("Session:", session.session_id)
    print("Task:", session.activity)
    print("Source:", session.source)
    print("FPS:", session.fps)
    print("Duration:", DURATION, "seconds")
    print("Frames:", len(session.frames))
    print()
    print("Saved:")
    print(output_path)


if __name__ == "__main__":
    main()