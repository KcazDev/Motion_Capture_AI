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

from src.assessment.session_manager import (
    AssessmentSession
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
            "MotionAI R-CON "
            "Box Stacking Assessment"
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
        action="store_true"
    )

    return parser.parse_args()


# =========================================================
# DRAWING
# =========================================================

def draw_text(
    frame,
    text,
    x,
    y,
    size=0.6,
    color=(255, 255, 255),
    thickness=2
):

    cv2.putText(
        frame,
        text,
        (
            int(x),
            int(y)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
        cv2.LINE_AA
    )


def draw_centered_text(
    frame,
    text,
    y,
    size=1.0,
    color=(255, 255, 255),
    thickness=2
):

    text_size = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        thickness
    )[0]

    x = int(
        (
            frame.shape[1]
            - text_size[0]
        )
        / 2
    )

    draw_text(
        frame,
        text,
        x,
        y,
        size,
        color,
        thickness
    )


def dark_panel(
    frame,
    x1,
    y1,
    x2,
    y2,
    opacity=0.72
):

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (
            x1,
            y1
        ),
        (
            x2,
            y2
        ),
        (
            0,
            0,
            0
        ),
        -1
    )

    return cv2.addWeighted(
        overlay,
        opacity,
        frame,
        1.0 - opacity,
        0
    )


# =========================================================
# FRIENDLY FEEDBACK
# =========================================================

def short_feedback(
    assessment
):

    reasons = assessment.get(
        "reasons",
        []
    )

    strengths = assessment.get(
        "strengths",
        []
    )

    result = assessment.get(
        "result",
        "RETRY"
    )

    if result == "RETRY":

        return (
            "Step fully into view "
            "and try again."
        )

    if reasons:

        reason = reasons[0].lower()

        if "torso" in reason:

            return (
                "Reduce forward torso lean."
            )

        if "knee" in reason:

            return (
                "Use more lower-body movement."
            )

        if "alignment" in reason:

            return (
                "Keep your body more balanced."
            )

        if "see enough" in reason:

            return (
                "Keep your full body visible."
            )

        return reasons[0]

    if strengths:

        return (
            "Controlled movement detected."
        )

    return (
        "Assessment complete."
    )


# =========================================================
# BOX PROGRESS
# =========================================================

def draw_box_progress(
    frame,
    session
):

    summary = (
        session.get_summary()
    )

    width = frame.shape[1]

    start_x = int(
        width / 2 - 235
    )

    y = 675

    spacing = 115

    for index in range(
        session.total_boxes
    ):

        box_number = (
            index + 1
        )

        center_x = (
            start_x
            + index * spacing
        )

        color = (
            100,
            100,
            100
        )

        label = str(
            box_number
        )

        if index < len(
            summary["results"]
        ):

            result = (
                summary[
                    "results"
                ][index][
                    "result"
                ]
            )

            if result == "PASS":

                color = (
                    0,
                    255,
                    0
                )

            else:

                color = (
                    0,
                    0,
                    255
                )

        elif (
            not session.is_complete
            and
            box_number
            ==
            session.current_box
        ):

            color = (
                0,
                255,
                255
            )

        cv2.circle(
            frame,
            (
                center_x,
                y
            ),
            27,
            color,
            -1
        )

        text_size = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            2
        )[0]

        draw_text(
            frame,
            label,
            center_x
            - int(
                text_size[0] / 2
            ),
            y + 7,
            0.6,
            (
                0,
                0,
                0
            ),
            2
        )


# =========================================================
# FINAL SCREEN
# =========================================================

def draw_final_summary(
    frame,
    session
):

    summary = (
        session.get_summary()
    )

    height, width = (
        frame.shape[:2]
    )

    frame = dark_panel(
        frame,
        120,
        70,
        width - 120,
        height - 95,
        0.87
    )

    draw_centered_text(
        frame,
        "ASSESSMENT COMPLETE",
        140,
        1.15,
        (
            255,
            255,
            255
        ),
        3
    )

    result_text = (
        f"{summary['pass_count']} / "
        f"{summary['total']} PASSED"
    )

    draw_centered_text(
        frame,
        result_text,
        220,
        1.25,
        (
            0,
            255,
            0
        ),
        3
    )

    draw_centered_text(
        frame,
        (
            "OVERALL SCORE: "
            f"{summary['average_score']:.1f}"
        ),
        285,
        0.9
    )

    draw_centered_text(
        frame,
        "LIFT RESULTS",
        350,
        0.65,
        (
            190,
            190,
            190
        )
    )

    start_x = int(
        width / 2 - 270
    )

    for index, result in enumerate(
        summary["results"]
    ):

        x = (
            start_x
            + index * 135
        )

        if result[
            "result"
        ] == "PASS":

            color = (
                0,
                255,
                0
            )

        else:

            color = (
                0,
                0,
                255
            )

        draw_text(
            frame,
            (
                f"B{result['box_number']}"
            ),
            x,
            395,
            0.55
        )

        draw_text(
            frame,
            result[
                "result"
            ],
            x,
            425,
            0.55,
            color
        )

    primary_issue = (
        summary[
            "primary_issue"
        ]
    )

    if primary_issue:

        draw_centered_text(
            frame,
            "PRIMARY FEEDBACK",
            490,
            0.62,
            (
                190,
                190,
                190
            )
        )

        friendly = short_feedback(
            {
                "result": "FAIL",
                "reasons": [
                    primary_issue
                ],
                "strengths": [],
            }
        )

        draw_centered_text(
            frame,
            friendly,
            535,
            0.67,
            (
                0,
                200,
                255
            )
        )

    else:

        draw_centered_text(
            frame,
            "Strong movement across all five lifts.",
            520,
            0.67,
            (
                100,
                255,
                100
            )
        )

    draw_centered_text(
        frame,
        "Press R to start a new assessment",
        605,
        0.55,
        (
            180,
            180,
            180
        )
    )

    return frame


# =========================================================
# MAIN
# =========================================================

def main():

    args = parse_arguments()

    print()
    print("=" * 70)
    print("MOTIONAI")
    print("R-CON BOX STACKING ASSESSMENT")
    print("=" * 70)

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

    session = (
        AssessmentSession(
            total_boxes=5
        )
    )

    voice = VoiceFeedback(
        enabled=(
            not args.mute
        ),
        rate=0,
        volume=100
    )

    latest_score = None

    last_scored_lift = 0

    result_display_until = 0.0

    previous_state = (
        "CALIBRATING"
    )

    calibration_announced = False

    session_complete_announced = False

    show_debug = False

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

            voice.say(
                (
                    "Welcome to Motion AI. "
                    "Please stand upright and still "
                    "while I calibrate."
                )
            )

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

                now = (
                    time.perf_counter()
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

                    if (
                        metrics
                        and
                        not session.is_complete
                    ):

                        lift_status = (
                            lift_analyzer
                            .update(
                                metrics
                            )
                        )

                # =========================================
                # CALIBRATION FINISHED
                # =========================================

                current_state = (
                    lift_status[
                        "state"
                    ]
                )

                if (
                    previous_state
                    ==
                    "CALIBRATING"
                    and
                    current_state
                    ==
                    "READY"
                    and
                    not calibration_announced
                ):

                    calibration_announced = True

                    voice.say(
                        (
                            "Calibration complete. "
                            "Box one. "
                            "Lift and place the box "
                            "when you are ready."
                        )
                    )

                previous_state = (
                    current_state
                )

                # =========================================
                # NEW COMPLETED LIFT
                # =========================================

                completed_lift = (
                    lift_status[
                        "last_completed_lift"
                    ]
                )

                if (
                    completed_lift
                    and
                    not session.is_complete
                ):

                    lift_number = (
                        completed_lift[
                            "lift_number"
                        ]
                    )

                    if (
                        lift_number
                        != last_scored_lift
                    ):

                        assessment = (
                            lift_scorer.score(
                                completed_lift
                            )
                        )

                        latest_score = (
                            assessment
                        )

                        last_scored_lift = (
                            lift_number
                        )

                        box_number = (
                            session.current_box
                        )

                        event = (
                            session
                            .record_assessment(
                                assessment
                            )
                        )

                        result_display_until = (
                            time.perf_counter()
                            + 3.5
                        )

                        print()
                        print(
                            "=" * 60
                        )

                        print(
                            f"BOX {box_number}"
                        )

                        print(
                            "RESULT:",
                            assessment[
                                "result"
                            ]
                        )

                        print(
                            "SCORE:",
                            assessment[
                                "overall_score"
                            ]
                        )

                        print(
                            "=" * 60
                        )

                        # =================================
                        # VOICE RESULT
                        # =================================

                        voice.announce_assessment(
                            assessment,
                            box_number
                        )

                        # =================================
                        # NEXT BOX
                        # =================================

                        if (
                            assessment[
                                "result"
                            ]
                            ==
                            "RETRY"
                        ):

                            voice.say(
                                (
                                    f"Please retry box "
                                    f"{box_number}."
                                )
                            )

                        elif session.is_complete:

                            summary = (
                                session
                                .get_summary()
                            )

                            message = (
                                "Assessment complete. "
                                f"You passed "
                                f"{summary['pass_count']} "
                                f"out of "
                                f"{summary['total']} lifts. "
                                f"Your overall movement "
                                f"score was "
                                f"{summary['average_score']:.0f} "
                                f"out of 100."
                            )

                            if (
                                summary[
                                    "primary_issue"
                                ]
                            ):

                                message += (
                                    " Your primary feedback is. "
                                    + short_feedback(
                                        {
                                            "result": "FAIL",
                                            "reasons": [
                                                summary[
                                                    "primary_issue"
                                                ]
                                            ],
                                            "strengths": [],
                                        }
                                    )
                                )

                            voice.say(
                                message
                            )

                            session_complete_announced = (
                                True
                            )

                        else:

                            voice.say(
                                (
                                    f"Prepare for box "
                                    f"{session.current_box}."
                                )
                            )

                # =========================================
                # FPS
                # =========================================

                delta = (
                    now
                    - previous_time
                )

                previous_time = now

                if delta > 0:

                    instant_fps = (
                        1.0
                        / delta
                    )

                    if smoothed_fps == 0:

                        smoothed_fps = (
                            instant_fps
                        )

                    else:

                        smoothed_fps = (
                            smoothed_fps
                            * 0.9
                            +
                            instant_fps
                            * 0.1
                        )

                # =========================================
                # FINAL SUMMARY
                # =========================================

                if session.is_complete:

                    frame = draw_final_summary(
                        frame,
                        session
                    )

                else:

                    # =====================================
                    # HEADER
                    # =====================================

                    frame = dark_panel(
                        frame,
                        20,
                        20,
                        frame.shape[1] - 20,
                        105,
                        0.72
                    )

                    draw_text(
                        frame,
                        "MOTIONAI",
                        45,
                        58,
                        1.0,
                        (
                            255,
                            255,
                            255
                        ),
                        2
                    )

                    draw_text(
                        frame,
                        (
                            "AI HUMAN MOVEMENT "
                            "ASSESSMENT"
                        ),
                        45,
                        87,
                        0.48,
                        (
                            180,
                            180,
                            180
                        ),
                        1
                    )

                    # =====================================
                    # CURRENT BOX
                    # =====================================

                    draw_text(
                        frame,
                        (
                            f"BOX "
                            f"{session.current_box} "
                            f"OF "
                            f"{session.total_boxes}"
                        ),
                        frame.shape[1] - 260,
                        58,
                        0.82,
                        (
                            0,
                            255,
                            255
                        ),
                        2
                    )

                    # =====================================
                    # CALIBRATION
                    # =====================================

                    if (
                        current_state
                        ==
                        "CALIBRATING"
                    ):

                        percentage = (
                            lift_status[
                                "calibration_progress"
                            ]
                            * 100
                        )

                        frame = dark_panel(
                            frame,
                            260,
                            245,
                            frame.shape[1] - 260,
                            470,
                            0.78
                        )

                        draw_centered_text(
                            frame,
                            "CALIBRATING",
                            315,
                            1.35,
                            (
                                0,
                                255,
                                255
                            ),
                            3
                        )

                        draw_centered_text(
                            frame,
                            (
                                "Stand upright "
                                "and remain still"
                            ),
                            365,
                            0.66
                        )

                        draw_centered_text(
                            frame,
                            (
                                f"{percentage:.0f}%"
                            ),
                            430,
                            1.1
                        )

                    # =====================================
                    # NOT DETECTED
                    # =====================================

                    elif not detected:

                        frame = dark_panel(
                            frame,
                            300,
                            260,
                            frame.shape[1] - 300,
                            435,
                            0.78
                        )

                        draw_centered_text(
                            frame,
                            "STEP INTO VIEW",
                            330,
                            1.15,
                            (
                                0,
                                165,
                                255
                            ),
                            3
                        )

                        draw_centered_text(
                            frame,
                            "Keep your full body visible",
                            390,
                            0.62
                        )

                    # =====================================
                    # RECENT RESULT
                    # =====================================

                    elif (
                        latest_score
                        and
                        time.perf_counter()
                        <
                        result_display_until
                    ):

                        frame = dark_panel(
                            frame,
                            270,
                            205,
                            frame.shape[1] - 270,
                            510,
                            0.84
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

                        draw_centered_text(
                            frame,
                            result,
                            290,
                            1.8,
                            result_color,
                            4
                        )

                        draw_centered_text(
                            frame,
                            (
                                "SCORE "
                                f"{latest_score['overall_score']:.0f}"
                            ),
                            355,
                            0.9
                        )

                        feedback = (
                            short_feedback(
                                latest_score
                            )
                        )

                        draw_centered_text(
                            frame,
                            feedback,
                            420,
                            0.67
                        )

                        if result == "RETRY":

                            next_text = (
                                f"Retry Box "
                                f"{session.current_box}"
                            )

                        elif not session.is_complete:

                            next_text = (
                                f"Next: Box "
                                f"{session.current_box}"
                            )

                        else:

                            next_text = ""

                        if next_text:

                            draw_centered_text(
                                frame,
                                next_text,
                                475,
                                0.55,
                                (
                                    190,
                                    190,
                                    190
                                )
                            )

                    # =====================================
                    # ACTIVE LIFT
                    # =====================================

                    else:

                        if (
                            current_state
                            ==
                            "READY"
                        ):

                            instruction = (
                                "LIFT WHEN READY"
                            )

                            instruction_color = (
                                0,
                                255,
                                0
                            )

                        elif (
                            current_state
                            ==
                            "LOWERING"
                        ):

                            instruction = (
                                "MOVEMENT DETECTED"
                            )

                            instruction_color = (
                                0,
                                255,
                                255
                            )

                        elif (
                            current_state
                            ==
                            "BOTTOM"
                        ):

                            instruction = (
                                "LIFT THE BOX"
                            )

                            instruction_color = (
                                0,
                                165,
                                255
                            )

                        elif (
                            current_state
                            ==
                            "LIFTING"
                        ):

                            instruction = (
                                "COMPLETE THE LIFT"
                            )

                            instruction_color = (
                                0,
                                255,
                                255
                            )

                        else:

                            instruction = (
                                current_state
                            )

                            instruction_color = (
                                255,
                                255,
                                255
                            )

                        draw_centered_text(
                            frame,
                            instruction,
                            155,
                            0.9,
                            instruction_color,
                            2
                        )

                    # =====================================
                    # FIVE BOX PROGRESS
                    # =====================================

                    draw_box_progress(
                        frame,
                        session
                    )

                    # =====================================
                    # DEBUG INFO
                    # =====================================

                    if (
                        show_debug
                        and
                        metrics
                    ):

                        frame = dark_panel(
                            frame,
                            20,
                            125,
                            330,
                            345,
                            0.70
                        )

                        draw_text(
                            frame,
                            (
                                f"State: "
                                f"{current_state}"
                            ),
                            40,
                            155,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                f"Torso: "
                                f"{metrics['torso_lean']:.1f}"
                            ),
                            40,
                            185,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                f"Knee L: "
                                f"{metrics['left_knee_angle']:.1f}"
                            ),
                            40,
                            215,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                f"Knee R: "
                                f"{metrics['right_knee_angle']:.1f}"
                            ),
                            40,
                            245,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                f"Visibility: "
                                f"{metrics['body_visibility'] * 100:.0f}%"
                            ),
                            40,
                            275,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                f"FPS: "
                                f"{smoothed_fps:.1f}"
                            ),
                            40,
                            305,
                            0.46
                        )

                # =========================================
                # FOOTER
                # =========================================

                draw_text(
                    frame,
                    "R = Restart   D = Debug   Q = Exit",
                    20,
                    frame.shape[0] - 15,
                    0.42,
                    (
                        180,
                        180,
                        180
                    ),
                    1
                )

                # =========================================
                # DISPLAY
                # =========================================

                cv2.imshow(
                    (
                        "MotionAI - "
                        "R-CON Assessment"
                    ),
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                # -----------------------------------------
                # EXIT
                # -----------------------------------------

                if (
                    key == ord("q")
                    or
                    key == 27
                ):

                    break

                # -----------------------------------------
                # DEBUG TOGGLE
                # -----------------------------------------

                if key == ord("d"):

                    show_debug = (
                        not show_debug
                    )

                # -----------------------------------------
                # RESET
                # -----------------------------------------

                if key == ord("r"):

                    print()
                    print(
                        "Starting new MotionAI session."
                    )

                    session.reset()

                    lift_analyzer = (
                        LiftAnalyzer(
                            calibration_frames=60
                        )
                    )

                    latest_score = None

                    last_scored_lift = 0

                    result_display_until = 0.0

                    previous_state = (
                        "CALIBRATING"
                    )

                    calibration_announced = (
                        False
                    )

                    session_complete_announced = (
                        False
                    )

                    voice.say(
                        (
                            "Starting a new assessment. "
                            "Please stand upright and still "
                            "while I calibrate."
                        )
                    )

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