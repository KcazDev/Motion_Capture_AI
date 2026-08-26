import json
import math
from dataclasses import asdict

from src.motion_frame import JointData, MotionFrame, MotionSession


def make_joint(x, y, z=0.0):
    return JointData(position=[x, y, z])


def main():

    fps = 60
    duration_seconds = 3
    total_frames = fps * duration_seconds

    session = MotionSession(
        session_id="test_motion_001",
        activity="right_arm_raise",
        fps=fps,
        subject_id="subject_001",
        source="synthetic"
    )

    for frame_number in range(total_frames):

        timestamp = frame_number / fps

        # Motion progresses smoothly from 0 → 1
        progress = frame_number / (total_frames - 1)

        # Right arm moves from pointing down to pointing up
        start_angle = -math.pi / 2
        end_angle = math.pi / 2

        angle = start_angle + (end_angle - start_angle) * progress

        frame = MotionFrame(timestamp=timestamp)

        # -------------------------
        # Core body
        # -------------------------

        frame.joints["pelvis"] = make_joint(0.0, 1.0)
        frame.joints["spine"] = make_joint(0.0, 1.3)
        frame.joints["neck"] = make_joint(0.0, 1.65)
        frame.joints["head"] = make_joint(0.0, 1.85)

        # -------------------------
        # Shoulders
        # -------------------------

        left_shoulder = (-0.25, 1.6)
        right_shoulder = (0.25, 1.6)

        frame.joints["left_shoulder"] = make_joint(*left_shoulder)
        frame.joints["right_shoulder"] = make_joint(*right_shoulder)

        # -------------------------
        # Left arm — stationary
        # -------------------------

        frame.joints["left_elbow"] = make_joint(-0.25, 1.25)
        frame.joints["left_wrist"] = make_joint(-0.25, 0.90)

        # -------------------------
        # Right arm — moving
        # -------------------------

        upper_arm_length = 0.35
        forearm_length = 0.35

        elbow_x = right_shoulder[0] + upper_arm_length * math.cos(angle)
        elbow_y = right_shoulder[1] + upper_arm_length * math.sin(angle)

        wrist_x = elbow_x + forearm_length * math.cos(angle)
        wrist_y = elbow_y + forearm_length * math.sin(angle)

        frame.joints["right_elbow"] = make_joint(
            elbow_x,
            elbow_y
        )

        frame.joints["right_wrist"] = make_joint(
            wrist_x,
            wrist_y
        )

        # -------------------------
        # Legs
        # -------------------------

        frame.joints["left_hip"] = make_joint(-0.15, 0.95)
        frame.joints["right_hip"] = make_joint(0.15, 0.95)

        frame.joints["left_knee"] = make_joint(-0.15, 0.50)
        frame.joints["right_knee"] = make_joint(0.15, 0.50)

        frame.joints["left_ankle"] = make_joint(-0.15, 0.05)
        frame.joints["right_ankle"] = make_joint(0.15, 0.05)

        session.frames.append(frame)

    # -------------------------
    # Save motion data
    # -------------------------

    output_path = "data/samples/test_motion_001.json"

    with open(output_path, "w") as file:
        json.dump(asdict(session), file, indent=4)

    print("Motion generation complete!")
    print()
    print("Session:", session.session_id)
    print("Activity:", session.activity)
    print("FPS:", session.fps)
    print("Duration:", duration_seconds, "seconds")
    print("Frames:", len(session.frames))
    print()
    print("Saved to:")
    print(output_path)

    print()
    print("Starting wrist position:")
    print(session.frames[0].joints["right_wrist"].position)

    print()
    print("Ending wrist position:")
    print(session.frames[-1].joints["right_wrist"].position)


if __name__ == "__main__":
    main()