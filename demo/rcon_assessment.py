import argparse
import time
from pathlib import Path

import cv2

from src.vision.camera import Camera
from src.vision.pose_tracker import PoseTracker
from src.assessment.movement_metrics import MovementMetrics
from src.assessment.lift_analyzer import LiftAnalyzer
from src.assessment.scoring import LiftScorer
from src.assessment.session_manager import AssessmentSession
from src.feedback.voice import VoiceFeedback


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL = (
    PROJECT_ROOT
    / "models"
    / "pose_landmarker_full.task"
)


def parse_args():

    parser = argparse.ArgumentParser(
        description="MotionAI R-CON Five Box Assessment"
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0
    )

    parser.add_argument(
        "--model",
        type=str,
        default=str(DEFAULT_MODEL)
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


def draw_text(
    frame,
    text,
    x,
    y,
    scale=0.6,
    color=(255, 255, 255),
    thickness=2
):

    cv2.putText(
        frame,
        text,
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def draw_center(
    frame,
    text,
    y,
    scale=1.0,
    color=(255, 255, 255),
    thickness=2
):

    size = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        thickness
    )[0]

    x = (
        frame.shape[1] - size[0]
    ) // 2

    draw_text(
        frame,
        text,
        x,
        y,
        scale,
        color,
        thickness
    )


def darken(
    frame,
    x1,
    y1,
    x2,
    y2,
    opacity=0.75
):

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (x1, y1),
        (x2, y2),
        (0, 0, 0),
        -1
    )

    return cv2.addWeighted(
        overlay,
        opacity,
        frame,
        1.0 - opacity,
        0
    )


def feedback_text(
    assessment
):

    result = assessment.get(
        "result",
        "RETRY"
    )

    reasons = assessment.get(
        "reasons",
        []
    )

    if result == "RETRY":

        return "Keep your full body visible and retry."

    if reasons:

        reason = reasons[0].lower()

        if "torso" in reason:

            return "Reduce forward torso lean."

        if "knee" in reason:

            return "Use more lower-body movement."

        if "alignment" in reason:

            return "Maintain more balanced movement."

        if "see enough" in reason:

            return "Keep your full body visible."

        return reasons[0][:60]

    return "Controlled movement detected."


def draw_progress(
    frame,
    session
):

    summary = session.get_summary()

    spacing = 105
    total_width = spacing * 4

    start_x = (
        frame.shape[1] // 2
        - total_width // 2
    )

    y = frame.shape[0] - 55

    for index in range(5):

        number = index + 1

        x = (
            start_x
            + index * spacing
        )

        color = (
            90,
            90,
            90
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
            number
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
            (x, y),
            25,
            color,
            -1
        )

        draw_text(
            frame,
            str(number),
            x - 7,
            y + 7,
            0.55,
            (0, 0, 0),
            2
        )


def draw_final_screen(
    frame,
    session
):

    summary = (
        session.get_summary()
    )

    height, width = (
        frame.shape[:2]
    )

    frame = darken(
        frame,
        100,
        70,
        width - 100,
        height - 80,
        0.88
    )

    draw_center(
        frame,
        "ASSESSMENT COMPLETE",
        145,
        1.15,
        (255, 255, 255),
        3
    )

    draw_center(
        frame,
        (
            f"{summary['pass_count']} / "
            f"{summary['total']} PASSED"
        ),
        225,
        1.35,
        (0, 255, 0),
        3
    )

    draw_center(
        frame,
        (
            "OVERALL SCORE: "
            f"{summary['average_score']:.0f}"
        ),
        290,
        0.90
    )

    x_start = (
        width // 2 - 275
    )

    for index, result in enumerate(
        summary["results"]
    ):

        x = (
            x_start
            + index * 135
        )

        if (
            result["result"]
            ==
            "PASS"
        ):

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
                f"BOX "
                f"{result['box_number']}"
            ),
            x,
            375,
            0.48
        )

        draw_text(
            frame,
            result["result"],
            x,
            410,
            0.58,
            color
        )

    if summary["primary_issue"]:

        fake_assessment = {
            "result": "FAIL",
            "reasons": [
                summary[
                    "primary_issue"
                ]
            ],
        }

        draw_center(
            frame,
            "PRIMARY FEEDBACK",
            485,
            0.58,
            (190, 190, 190)
        )

        draw_center(
            frame,
            feedback_text(
                fake_assessment
            ),
            530,
            0.70,
            (0, 200, 255)
        )

    else:

        draw_center(
            frame,
            "Strong movement across all five lifts.",
            510,
            0.70,
            (0, 255, 0)
        )

    draw_center(
        frame,
        "Press R for a new assessment",
        610,
        0.55,
        (190, 190, 190)
    )

    return frame


def main():

    args = parse_args()

    print()
    print("=" * 70)
    print("MOTIONAI")
    print("R-CON FIVE BOX ASSESSMENT")
    print("=" * 70)
    print()

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

    scorer = LiftScorer()

    session = (
        AssessmentSession(
            total_boxes=5
        )
    )

    voice = VoiceFeedback(
        enabled=not args.mute,
        rate=0,
        volume=100
    )

    latest_score = None

    last_scored_lift = 0

    result_until = 0.0

    calibration_announced = False

    previous_state = (
        "CALIBRATING"
    )

    final_voice_announced = False

    show_debug = False

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
                    "with your full body visible."
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
                        metrics is not None
                        and
                        not session.is_complete
                    ):

                        lift_status = (
                            lift_analyzer
                            .update(
                                metrics
                            )
                        )

                current_state = (
                    lift_status[
                        "state"
                    ]
                )

                # =========================================
                # CALIBRATION FINISHED
                # =========================================

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

                    calibration_announced = (
                        True
                    )

                    voice.say(
                        (
                            "Calibration complete. "
                            "Box one. "
                            "Lift when you are ready."
                        )
                    )

                previous_state = (
                    current_state
                )

                # =========================================
                # SCORE COMPLETED LIFT
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

                        box_number = (
                            session.current_box
                        )

                        assessment = (
                            scorer.score(
                                completed_lift
                            )
                        )

                        latest_score = (
                            assessment
                        )

                        last_scored_lift = (
                            lift_number
                        )

                        session.record_assessment(
                            assessment
                        )

                        result_until = (
                            time.perf_counter()
                            + 3.5
                        )

                        print()
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

                        voice.announce_assessment(
                            assessment,
                            box_number
                        )

                        if (
                            assessment[
                                "result"
                            ]
                            ==
                            "RETRY"
                        ):

                            voice.say(
                                (
                                    f"Retry box "
                                    f"{box_number}."
                                )
                            )

                        elif (
                            not session.is_complete
                        ):

                            voice.say(
                                (
                                    f"Prepare for box "
                                    f"{session.current_box}."
                                )
                            )

                # =========================================
                # FINAL VOICE
                # =========================================

                if (
                    session.is_complete
                    and
                    not final_voice_announced
                ):

                    final_voice_announced = (
                        True
                    )

                    summary = (
                        session.get_summary()
                    )

                    message = (
                        "Assessment complete. "
                        f"You passed "
                        f"{summary['pass_count']} "
                        f"out of five lifts. "
                        f"Your overall score was "
                        f"{summary['average_score']:.0f} "
                        f"out of 100."
                    )

                    if summary[
                        "primary_issue"
                    ]:

                        message += (
                            " Primary feedback. "
                            + feedback_text(
                                {
                                    "result": "FAIL",
                                    "reasons": [
                                        summary[
                                            "primary_issue"
                                        ]
                                    ],
                                }
                            )
                        )

                    voice.say(
                        message
                    )

                # =========================================
                # FINAL SCREEN
                # =========================================

                if session.is_complete:

                    frame = draw_final_screen(
                        frame,
                        session
                    )

                else:

                    height, width = (
                        frame.shape[:2]
                    )

                    # -------------------------------------
                    # TOP HEADER
                    # -------------------------------------

                    frame = darken(
                        frame,
                        20,
                        20,
                        width - 20,
                        105,
                        0.72
                    )

                    draw_text(
                        frame,
                        "MOTIONAI",
                        45,
                        58,
                        1.0
                    )

                    draw_text(
                        frame,
                        "AI HUMAN MOVEMENT ASSESSMENT",
                        45,
                        86,
                        0.48,
                        (190, 190, 190),
                        1
                    )

                    draw_text(
                        frame,
                        (
                            f"BOX "
                            f"{session.current_box} "
                            f"OF 5"
                        ),
                        width - 245,
                        67,
                        0.78,
                        (0, 255, 255)
                    )

                    # -------------------------------------
                    # CALIBRATION
                    # -------------------------------------

                    if (
                        current_state
                        ==
                        "CALIBRATING"
                    ):

                        progress = (
                            lift_status[
                                "calibration_progress"
                            ]
                            * 100
                        )

                        frame = darken(
                            frame,
                            285,
                            230,
                            width - 285,
                            455,
                            0.82
                        )

                        draw_center(
                            frame,
                            "CALIBRATING",
                            305,
                            1.3,
                            (0, 255, 255),
                            3
                        )

                        draw_center(
                            frame,
                            "Stand upright with your full body visible",
                            360,
                            0.58
                        )

                        draw_center(
                            frame,
                            f"{progress:.0f}%",
                            420,
                            1.1
                        )

                    # -------------------------------------
                    # NO PERSON
                    # -------------------------------------

                    elif not detected:

                        frame = darken(
                            frame,
                            300,
                            245,
                            width - 300,
                            430,
                            0.82
                        )

                        draw_center(
                            frame,
                            "STEP INTO VIEW",
                            325,
                            1.15,
                            (0, 165, 255),
                            3
                        )

                        draw_center(
                            frame,
                            "Keep your full body visible",
                            385,
                            0.62
                        )

                    # -------------------------------------
                    # SHOW RESULT
                    # -------------------------------------

                    elif (
                        latest_score
                        and
                        now < result_until
                    ):

                        frame = darken(
                            frame,
                            285,
                            195,
                            width - 285,
                            510,
                            0.85
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

                        draw_center(
                            frame,
                            result,
                            290,
                            1.8,
                            result_color,
                            4
                        )

                        draw_center(
                            frame,
                            (
                                "SCORE "
                                f"{latest_score['overall_score']:.0f}"
                            ),
                            355,
                            0.9
                        )

                        draw_center(
                            frame,
                            feedback_text(
                                latest_score
                            ),
                            420,
                            0.66
                        )

                        if result == "RETRY":

                            next_text = (
                                f"Retry Box "
                                f"{session.current_box}"
                            )

                        else:

                            next_text = (
                                f"Next: Box "
                                f"{session.current_box}"
                            )

                        draw_center(
                            frame,
                            next_text,
                            475,
                            0.55,
                            (190, 190, 190)
                        )

                    # -------------------------------------
                    # ACTIVE MOVEMENT
                    # -------------------------------------

                    else:

                        if (
                            current_state
                            ==
                            "READY"
                        ):

                            instruction = (
                                "LIFT WHEN READY"
                            )

                            color = (
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

                            color = (
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

                            color = (
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

                            color = (
                                0,
                                255,
                                255
                            )

                        else:

                            instruction = (
                                current_state
                            )

                            color = (
                                255,
                                255,
                                255
                            )

                        draw_center(
                            frame,
                            instruction,
                            155,
                            0.9,
                            color,
                            2
                        )

                    # -------------------------------------
                    # PROGRESS
                    # -------------------------------------

                    draw_progress(
                        frame,
                        session
                    )

                    # -------------------------------------
                    # DEBUG
                    # -------------------------------------

                    if (
                        show_debug
                        and
                        metrics
                    ):

                        frame = darken(
                            frame,
                            20,
                            125,
                            325,
                            315,
                            0.72
                        )

                        draw_text(
                            frame,
                            f"State: {current_state}",
                            40,
                            155,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                "Torso: "
                                f"{metrics['torso_lean']:.1f}"
                            ),
                            40,
                            185,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                "Knee: "
                                f"{metrics['average_knee_angle']:.1f}"
                            ),
                            40,
                            215,
                            0.46
                        )

                        draw_text(
                            frame,
                            (
                                "Visibility: "
                                f"{metrics['body_visibility'] * 100:.0f}%"
                            ),
                            40,
                            245,
                            0.46
                        )

                # =========================================
                # FOOTER
                # =========================================

                draw_text(
                    frame,
                    "R Restart   D Debug   Q Exit",
                    20,
                    frame.shape[0] - 15,
                    0.42,
                    (180, 180, 180),
                    1
                )

                cv2.imshow(
                    "MotionAI - R-CON Assessment",
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

                if key == ord("d"):

                    show_debug = (
                        not show_debug
                    )

                if key == ord("r"):

                    print()
                    print(
                        "New assessment started."
                    )

                    session = (
                        AssessmentSession(
                            total_boxes=5
                        )
                    )

                    lift_analyzer = (
                        LiftAnalyzer(
                            calibration_frames=60
                        )
                    )

                    latest_score = None

                    last_scored_lift = 0

                    result_until = 0.0

                    calibration_announced = False

                    final_voice_announced = False

                    previous_state = (
                        "CALIBRATING"
                    )

                    voice.say(
                        (
                            "Starting a new assessment. "
                            "Please stand upright and still "
                            "with your full body visible."
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