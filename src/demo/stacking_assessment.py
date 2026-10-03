import argparse
import time
from pathlib import Path

import cv2

from src.vision.camera import Camera
from src.vision.pose_tracker import PoseTracker
from src.assessment.movement_metrics import MovementMetrics
from src.assessment.scoring import LiftScorer


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DEFAULT_MODEL = (
    PROJECT_ROOT
    / "models"
    / "pose_landmarker_full.task"
)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "MotionAI live human "
            "movement assessment."
        )
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0
    )

    parser.add_argument(
        "--model",
        type=str,
        default=str(
            DEFAULT_MODEL
        )
    )

    parser.add_argument(
        "--width",
        type=int,
        default=1280
    )

    parser.add_argument(
        "--height",
        type=int,
        default=720
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=30
    )

    return parser.parse_args()


def draw_metric(
    frame,
    label,
    value,
    y_position,
    suffix="deg"
):

    text = (
        f"{label}: "
        f"{value:.1f}"
    )

    if suffix:
        text += (
            f" {suffix}"
        )

    cv2.putText(
        frame,
        text,
        (25, y_position),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


def main():

    args = parse_arguments()

    print()
    print("=" * 70)
    print("MOTIONAI")
    print("LIVE MOVEMENT METRICS")
    print("=" * 70)

    tracker = PoseTracker(
        model_path=args.model
    )

    metrics_engine = (
        MovementMetrics()
    )

    previous_time = (
        time.perf_counter()
    )

    smoothed_fps = 0.0

    try:

        with Camera(
            camera_index=args.camera,
            width=args.width,
            height=args.height,
            fps=args.fps
        ) as camera:

            print()
            print("MotionAI ready.")
            print(
                "Keep your full body visible."
            )
            print(
                "Q / ESC = Exit"
            )
            print()

            while True:

                success, frame = (
                    camera.read()
                )

                if not success:
                    continue

                frame = cv2.flip(
                    frame,
                    1
                )

                # =========================================
                # POSE TRACKING
                # =========================================

                results = (
                    tracker.process(
                        frame
                    )
                )

                person_detected = (
                    tracker.person_detected(
                        results
                    )
                )

                metrics = None

                if person_detected:

                    frame = tracker.draw(
                        frame,
                        results
                    )

                    metrics = (
                        metrics_engine.analyze(
                            results
                        )
                    )

                # =========================================
                # FPS
                # =========================================

                current_time = (
                    time.perf_counter()
                )

                delta = (
                    current_time
                    - previous_time
                )

                previous_time = (
                    current_time
                )

                if delta > 0:

                    instant_fps = (
                        1.0 / delta
                    )

                    if smoothed_fps == 0:

                        smoothed_fps = (
                            instant_fps
                        )

                    else:

                        smoothed_fps = (
                            smoothed_fps
                            * 0.90
                            +
                            instant_fps
                            * 0.10
                        )

                # =========================================
                # PANEL
                # =========================================

                overlay = (
                    frame.copy()
                )

                cv2.rectangle(
                    overlay,
                    (0, 0),
                    (440, 385),
                    (0, 0, 0),
                    -1
                )

                frame = cv2.addWeighted(
                    overlay,
                    0.62,
                    frame,
                    0.38,
                    0
                )

                # =========================================
                # TITLE
                # =========================================

                cv2.putText(
                    frame,
                    "MOTIONAI",
                    (25, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.05,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    frame,
                    "LIVE MOVEMENT METRICS",
                    (25, 72),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (200, 200, 200),
                    2,
                    cv2.LINE_AA
                )

                # =========================================
                # PERSON STATUS
                # =========================================

                if person_detected:

                    status = (
                        "PERSON DETECTED"
                    )

                    status_color = (
                        0,
                        255,
                        0
                    )

                else:

                    status = (
                        "FULL BODY NOT DETECTED"
                    )

                    status_color = (
                        0,
                        165,
                        255
                    )

                cv2.putText(
                    frame,
                    status,
                    (25, 108),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.66,
                    status_color,
                    2,
                    cv2.LINE_AA
                )

                # =========================================
                # METRICS
                # =========================================

                if metrics:

                    draw_metric(
                        frame,
                        "Torso Lean",
                        metrics[
                            "torso_lean"
                        ],
                        145
                    )

                    draw_metric(
                        frame,
                        "Left Knee",
                        metrics[
                            "left_knee_angle"
                        ],
                        175
                    )

                    draw_metric(
                        frame,
                        "Right Knee",
                        metrics[
                            "right_knee_angle"
                        ],
                        205
                    )

                    draw_metric(
                        frame,
                        "Average Hip",
                        metrics[
                            "average_hip_angle"
                        ],
                        235
                    )

                    draw_metric(
                        frame,
                        "Shoulder Tilt",
                        metrics[
                            "shoulder_tilt"
                        ],
                        265
                    )

                    draw_metric(
                        frame,
                        "Hip Tilt",
                        metrics[
                            "hip_tilt"
                        ],
                        295
                    )

                    visibility_percent = (
                        metrics[
                            "body_visibility"
                        ]
                        * 100.0
                    )

                    draw_metric(
                        frame,
                        "Body Visibility",
                        visibility_percent,
                        325,
                        "%"
                    )

                cv2.putText(
                    frame,
                    (
                        f"FPS: "
                        f"{smoothed_fps:.1f}"
                    ),
                    (25, 355),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.52,
                    (200, 200, 200),
                    1,
                    cv2.LINE_AA
                )

                cv2.putText(
                    frame,
                    "Q / ESC = Exit",
                    (25, 378),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (180, 180, 180),
                    1,
                    cv2.LINE_AA
                )

                # =========================================
                # DISPLAY
                # =========================================

                cv2.imshow(
                    (
                        "MotionAI - "
                        "Movement Metrics"
                    ),
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if (
                    key == ord("q")
                    or key == 27
                ):

                    break

    finally:

        tracker.close()

        cv2.destroyAllWindows()

        print()
        print(
            "MotionAI closed."
        )


if __name__ == "__main__":

    main()