import argparse
import time

import cv2

from src.ui.rcon_display import (
    create_canvas,
    draw_menu_screen,
    draw_calibration_screen,
    draw_active_screen,
    draw_result_screen,
    draw_final_screen
)


WINDOW_NAME = (
    "MotionAI - R-CON 2026 Preview"
)


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "MotionAI R-CON 2026 "
            "camera-free UI preview"
        )
    )

    parser.add_argument(
        "--fullscreen",
        action="store_true"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    state = "MENU"

    calibration_started = None

    result_started = None

    current_lift = 1

    results = []

    latest_result = None

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        WINDOW_NAME,
        1280,
        720
    )

    if args.fullscreen:

        cv2.setWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

    while True:

        frame = create_canvas(
            1280,
            720
        )

        now = (
            time.perf_counter()
        )

        # =================================================
        # MENU
        # =================================================

        if state == "MENU":

            draw_menu_screen(
                frame
            )

        # =================================================
        # CALIBRATION
        # =================================================

        elif state == "CALIBRATING":

            elapsed = (
                now
                - calibration_started
            )

            progress = min(
                elapsed / 2.5,
                1.0
            )

            draw_calibration_screen(
                frame,
                progress
            )

            if progress >= 1.0:

                state = "READY"

        # =================================================
        # ACTIVE
        # =================================================

        elif state == "READY":

            draw_active_screen(
                frame,
                current_lift,
                results
            )

        # =================================================
        # RESULT
        # =================================================

        elif state == "RESULT":

            draw_result_screen(
                frame,
                latest_result[
                    "result"
                ],
                latest_result[
                    "score"
                ],
                latest_result[
                    "feedback"
                ],
                current_lift,
                results
            )

            if (
                now
                - result_started
                >= 3.0
            ):

                if (
                    latest_result[
                        "result"
                    ]
                    ==
                    "RETRY"
                ):

                    state = "READY"

                elif len(results) >= 5:

                    state = "COMPLETE"

                else:

                    current_lift += 1

                    state = "READY"

        # =================================================
        # FINAL
        # =================================================

        elif state == "COMPLETE":

            draw_final_screen(
                frame,
                results
            )

        # =================================================
        # DISPLAY
        # =================================================

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

        key = (
            cv2.waitKey(16)
            & 0xFF
        )

        # =================================================
        # EXIT
        # =================================================

        if (
            key == ord("q")
            or
            key == 27
        ):

            break

        # =================================================
        # BEGIN
        # =================================================

        if (
            state == "MENU"
            and
            key == 32
        ):

            state = "CALIBRATING"

            calibration_started = (
                time.perf_counter()
            )

        # =================================================
        # SIMULATE PASS
        # =================================================

        if (
            state == "READY"
            and
            key == ord("p")
        ):

            latest_result = {
                "result": "PASS",
                "score": 88.0,
                "feedback": (
                    "CONTROLLED MOVEMENT DETECTED"
                ),
            }

            results.append(
                latest_result.copy()
            )

            result_started = (
                time.perf_counter()
            )

            state = "RESULT"

        # =================================================
        # SIMULATE FAIL
        # =================================================

        if (
            state == "READY"
            and
            key == ord("f")
        ):

            latest_result = {
                "result": "FAIL",
                "score": 58.0,
                "feedback": (
                    "EXCESSIVE FORWARD LEAN DETECTED"
                ),
            }

            results.append(
                latest_result.copy()
            )

            result_started = (
                time.perf_counter()
            )

            state = "RESULT"

        # =================================================
        # SIMULATE RETRY
        # =================================================

        if (
            state == "READY"
            and
            key == ord("t")
        ):

            latest_result = {
                "result": "RETRY",
                "score": 0.0,
                "feedback": (
                    "TRACKING LOST - FULL BODY REQUIRED"
                ),
            }

            result_started = (
                time.perf_counter()
            )

            state = "RESULT"

        # =================================================
        # RESET
        # =================================================

        if key == ord("r"):

            state = "MENU"

            calibration_started = None

            result_started = None

            current_lift = 1

            results = []

            latest_result = None

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()
