import argparse
import time
from pathlib import Path

import cv2

from src.vision.camera import Camera
from src.vision.pose_tracker import PoseTracker

from src.assessment.movement_metrics import (
    MovementMetrics
)

from src.assessment.lift_analyzer import (
    LiftAnalyzer
)

from src.assessment.scoring import (
    LiftScorer
)

from src.feedback.voice import (
    VoiceFeedback
)


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


# =========================================================
# ARGUMENTS
# =========================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "MotionAI camera-based "
            "human movement assessment."
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

    parser.add_argument(
        "--mute",
        action="store_true",
        help=(
            "Disable MotionAI voice feedback."
        )
    )

    return parser.parse_args()


# =========================================================
# TEXT
# =========================================================

def draw_text(
    frame,
    text,
    x,
    y,
    size=0.55,
    color=(255, 255, 255),
    thickness=2
):

    cv2.putText(
        frame,
        text,
        (
            x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
        cv2.LINE_AA
    )


# =========================================================
# MAIN
# =========================================================

def main():

    args = parse_arguments()

    print()
    print("=" * 70)
    print("MOTIONAI")
    print("BOX STACKING MOVEMENT ASSESSMENT")
    print("=" * 70)

    # =====================================================
    # MOTIONAI SYSTEMS
    # =====================================================

    tracker = PoseTracker(
        model_path=args.model
    )

    metrics_engine = (
        MovementMetrics()
    )

    lift_analyzer = (
        LiftAnalyzer(
            calibration_frames=60
        )
    )

    lift_scorer = (
        LiftScorer()
    )

    voice = VoiceFeedback(
        enabled=(
            not args.mute
        ),
        rate=0,
        volume=100
    )

    # =====================================================
    # STATE
    # =====================================================

    latest_score = None

    last_scored_lift = 0

    previous_lift_state = (
        "CALIBRATING"
    )

    ready_announced = False

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
            print(
                "Stand upright and still "
                "during calibration."
            )

            print()

            voice.say(
                (
                    "Welcome to Motion AI. "
                    "Please stand upright and still "
                    "while I calibrate."
                )
            )

            while True:

                # =========================================
                # CAMERA
                # =========================================

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
                # POSE
                # =========================================

                results = (
                    tracker.process(
                        frame
                    )
                )

                detected = (
                    tracker.person_detected(
                        results
                    )
                )

                metrics = None

                lift_status = (
                    lift_analyzer
                    .get_status()
                )

                if detected:

                    frame = tracker.draw(
                        frame,
                        results
                    )

                    metrics = (
                        metrics_engine
                        .analyze(
                            results
                        )
                    )

                    if metrics:

                        lift_status = (
                            lift_analyzer
                            .update(
                                metrics
                            )
                        )

                # =========================================
                # LIFT STATE CHANGE
                # =========================================

                current_lift_state = (
                    lift_status[
                        "state"
                    ]
                )

                if (
                    previous_lift_state
                    ==
                    "CALIBRATING"
                    and
                    current_lift_state
                    ==
                    "READY"
                    and
                    not ready_announced
                ):

                    voice.announce_ready()

                    ready_announced = True

                previous_lift_state = (
                    current_lift_state
                )

                # =========================================
                # SCORE NEW COMPLETE LIFT
                # =========================================

                completed = (
                    lift_status[
                        "last_completed_lift"
                    ]
                )

                if completed:

                    lift_number = (
                        completed[
                            "lift_number"
                        ]
                    )

                    if (
                        lift_number
                        != last_scored_lift
                    ):

                        latest_score = (
                            lift_scorer.score(
                                completed
                            )
                        )

                        last_scored_lift = (
                            lift_number
                        )

                        # -----------------------------
                        # TERMINAL
                        # -----------------------------

                        print()
                        print("=" * 60)

                        print(
                            f"MOTIONAI LIFT "
                            f"{lift_number} "
                            f"ASSESSMENT"
                        )

                        print("=" * 60)

                        print(
                            "RESULT:",
                            latest_score[
                                "result"
                            ]
                        )

                        print(
                            "SCORE:",
                            latest_score[
                                "overall_score"
                            ]
                        )

                        for reason in (
                            latest_score[
                                "reasons"
                            ]
                        ):

                            print(
                                "ISSUE:",
                                reason
                            )

                        for strength in (
                            latest_score[
                                "strengths"
                            ]
                        ):

                            print(
                                "GOOD:",
                                strength
                            )

                        # -----------------------------
                        # VOICE
                        # -----------------------------

                        voice.announce_assessment(
                            latest_score,
                            lift_number
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

                    instant = (
                        1.0 / delta
                    )

                    if smoothed_fps == 0:

                        smoothed_fps = (
                            instant
                        )

                    else:

                        smoothed_fps = (
                            smoothed_fps
                            * 0.9
                            +
                            instant
                            * 0.1
                        )

                # =========================================
                # LEFT PANEL
                # =========================================

                overlay = (
                    frame.copy()
                )

                cv2.rectangle(
                    overlay,
                    (
                        0,
                        0
                    ),
                    (
                        465,
                        430
                    ),
                    (
                        0,
                        0,
                        0
                    ),
                    -1
                )

                frame = cv2.addWeighted(
                    overlay,
                    0.62,
                    frame,
                    0.38,
                    0
                )

                draw_text(
                    frame,
                    "MOTIONAI",
                    25,
                    40,
                    1.05
                )

                draw_text(
                    frame,
                    (
                        "AI HUMAN MOVEMENT "
                        "ASSESSMENT"
                    ),
                    25,
                    72,
                    0.55,
                    (
                        200,
                        200,
                        200
                    )
                )

                # =========================================
                # DETECTION STATUS
                # =========================================

                if detected:

                    draw_text(
                        frame,
                        "PERSON DETECTED",
                        25,
                        108,
                        0.65,
                        (
                            0,
                            255,
                            0
                        )
                    )

                else:

                    draw_text(
                        frame,
                        "STEP INTO VIEW",
                        25,
                        108,
                        0.65,
                        (
                            0,
                            165,
                            255
                        )
                    )

                # =========================================
                # LIVE METRICS
                # =========================================

                if metrics:

                    draw_text(
                        frame,
                        (
                            "Torso Lean: "
                            f"{metrics['torso_lean']:.1f} deg"
                        ),
                        25,
                        145
                    )

                    draw_text(
                        frame,
                        (
                            "Left Knee: "
                            f"{metrics['left_knee_angle']:.1f} deg"
                        ),
                        25,
                        175
                    )

                    draw_text(
                        frame,
                        (
                            "Right Knee: "
                            f"{metrics['right_knee_angle']:.1f} deg"
                        ),
                        25,
                        205
                    )

                    draw_text(
                        frame,
                        (
                            "Hip Angle: "
                            f"{metrics['average_hip_angle']:.1f} deg"
                        ),
                        25,
                        235
                    )

                    draw_text(
                        frame,
                        (
                            "Visibility: "
                            f"{metrics['body_visibility'] * 100:.0f}%"
                        ),
                        25,
                        265
                    )

                # =========================================
                # LIFT STATUS
                # =========================================

                state = (
                    lift_status[
                        "state"
                    ]
                )

                if state == "READY":

                    state_color = (
                        0,
                        255,
                        0
                    )

                elif state == "CALIBRATING":

                    state_color = (
                        0,
                        255,
                        255
                    )

                elif state == "COMPLETE":

                    state_color = (
                        0,
                        255,
                        0
                    )

                else:

                    state_color = (
                        0,
                        165,
                        255
                    )

                draw_text(
                    frame,
                    (
                        f"Lift State: "
                        f"{state}"
                    ),
                    25,
                    310,
                    0.62,
                    state_color
                )

                draw_text(
                    frame,
                    (
                        "Lifts Completed: "
                        f"{lift_status['lift_count']}"
                    ),
                    25,
                    342,
                    0.62
                )

                if (
                    state
                    ==
                    "CALIBRATING"
                ):

                    percentage = (
                        lift_status[
                            "calibration_progress"
                        ]
                        * 100.0
                    )

                    draw_text(
                        frame,
                        (
                            "Calibration: "
                            f"{percentage:.0f}%"
                        ),
                        25,
                        378,
                        0.60,
                        (
                            0,
                            255,
                            255
                        )
                    )

                draw_text(
                    frame,
                    (
                        f"FPS: "
                        f"{smoothed_fps:.1f}"
                    ),
                    25,
                    410,
                    0.48,
                    (
                        190,
                        190,
                        190
                    ),
                    1
                )

                # =========================================
                # RESULT PANEL
                # =========================================

                if latest_score:

                    height, width = (
                        frame.shape[:2]
                    )

                    panel_left = (
                        width - 460
                    )

                    result_overlay = (
                        frame.copy()
                    )

                    cv2.rectangle(
                        result_overlay,
                        (
                            panel_left,
                            20
                        ),
                        (
                            width - 20,
                            340
                        ),
                        (
                            0,
                            0,
                            0
                        ),
                        -1
                    )

                    frame = cv2.addWeighted(
                        result_overlay,
                        0.72,
                        frame,
                        0.28,
                        0
                    )

                    result = (
                        latest_score[
                            "result"
                        ]
                    )

                    if result == "PASS":

                        result_color = (
                            0,
                            255,
                            0
                        )

                    elif result == "FAIL":

                        result_color = (
                            0,
                            0,
                            255
                        )

                    else:

                        result_color = (
                            0,
                            255,
                            255
                        )

                    draw_text(
                        frame,
                        "LIFT ASSESSMENT",
                        panel_left + 25,
                        55,
                        0.60,
                        (
                            200,
                            200,
                            200
                        )
                    )

                    draw_text(
                        frame,
                        result,
                        panel_left + 25,
                        108,
                        1.30,
                        result_color,
                        3
                    )

                    draw_text(
                        frame,
                        (
                            "Score: "
                            f"{latest_score['overall_score']:.1f}"
                        ),
                        panel_left + 25,
                        150,
                        0.74
                    )

                    y = 190

                    # ---------------------------------
                    # FAIL / RETRY FEEDBACK
                    # ---------------------------------

                    if latest_score[
                        "reasons"
                    ]:

                        for reason in (
                            latest_score[
                                "reasons"
                            ][:3]
                        ):

                            # Shorten UI text.
                            if (
                                "torso"
                                in reason.lower()
                            ):

                                display_reason = (
                                    "Excessive torso lean"
                                )

                            elif (
                                "knee"
                                in reason.lower()
                            ):

                                display_reason = (
                                    "Limited knee movement"
                                )

                            elif (
                                "body"
                                in reason.lower()
                                and
                                "see"
                                in reason.lower()
                            ):

                                display_reason = (
                                    "Tracking quality too low"
                                )

                            else:

                                display_reason = (
                                    reason[:45]
                                )

                            draw_text(
                                frame,
                                (
                                    "- "
                                    + display_reason
                                ),
                                panel_left + 25,
                                y,
                                0.48,
                                (
                                    0,
                                    180,
                                    255
                                ),
                                1
                            )

                            y += 38

                    # ---------------------------------
                    # PASS FEEDBACK
                    # ---------------------------------

                    else:

                        for strength in (
                            latest_score[
                                "strengths"
                            ][:3]
                        ):

                            if (
                                "lower-body"
                                in strength.lower()
                            ):

                                display_strength = (
                                    "Good lower-body movement"
                                )

                            elif (
                                "torso"
                                in strength.lower()
                            ):

                                display_strength = (
                                    "Controlled torso movement"
                                )

                            elif (
                                "alignment"
                                in strength.lower()
                            ):

                                display_strength = (
                                    "Balanced body alignment"
                                )

                            else:

                                display_strength = (
                                    strength[:45]
                                )

                            draw_text(
                                frame,
                                (
                                    "+ "
                                    + display_strength
                                ),
                                panel_left + 25,
                                y,
                                0.48,
                                (
                                    100,
                                    255,
                                    100
                                ),
                                1
                            )

                            y += 38

                # =========================================
                # DISPLAY
                # =========================================

                cv2.imshow(
                    (
                        "MotionAI - "
                        "Box Stacking Assessment"
                    ),
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if (
                    key == ord("q")
                    or
                    key == 27
                ):

                    break

    finally:

        voice.close()

        tracker.close()

        cv2.destroyAllWindows()

        print()
        print(
            "MotionAI closed."
        )


if __name__ == "__main__":

    main()

