import cv2
import numpy as np


# =========================================================
# MOTIONAI - R-CON 2026 INDUSTRIAL UI
#
# OpenCV uses BGR color order.
# =========================================================

BACKGROUND = (22, 23, 24)

PANEL = (35, 36, 38)
PANEL_LIGHT = (55, 57, 60)

WHITE = (245, 245, 245)
MUTED = (165, 168, 172)

SAFETY_YELLOW = (0, 210, 255)

GREEN = (70, 210, 85)
RED = (70, 70, 235)
AMBER = (0, 165, 255)

DARK = (12, 13, 14)


# =========================================================
# CANVAS
# =========================================================

def create_canvas(
    width=1280,
    height=720
):

    return np.full(
        (
            height,
            width,
            3
        ),
        BACKGROUND,
        dtype=np.uint8
    )


# =========================================================
# TEXT
# =========================================================

def draw_text(
    frame,
    text,
    x,
    y,
    scale=0.6,
    color=WHITE,
    thickness=2
):

    cv2.putText(
        frame,
        str(text),
        (
            int(x),
            int(y)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def draw_centered_text(
    frame,
    text,
    y,
    scale=0.8,
    color=WHITE,
    thickness=2
):

    text = str(text)

    size = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        thickness
    )[0]

    x = int(
        (
            frame.shape[1]
            - size[0]
        )
        / 2
    )

    draw_text(
        frame,
        text,
        x,
        y,
        scale,
        color,
        thickness
    )


# =========================================================
# PANELS
# =========================================================

def draw_panel(
    frame,
    x1,
    y1,
    x2,
    y2,
    border=True
):

    cv2.rectangle(
        frame,
        (
            int(x1),
            int(y1)
        ),
        (
            int(x2),
            int(y2)
        ),
        PANEL,
        -1
    )

    if border:

        cv2.rectangle(
            frame,
            (
                int(x1),
                int(y1)
            ),
            (
                int(x2),
                int(y2)
            ),
            PANEL_LIGHT,
            2
        )


def draw_hazard_accent(
    frame,
    x,
    y,
    width,
    height=5
):

    cv2.rectangle(
        frame,
        (
            int(x),
            int(y)
        ),
        (
            int(x + width),
            int(y + height)
        ),
        SAFETY_YELLOW,
        -1
    )


# =========================================================
# HEADER
# =========================================================

def draw_header(
    frame,
    right_text=None
):

    width = frame.shape[1]

    # Top safety stripe
    draw_hazard_accent(
        frame,
        0,
        0,
        width,
        7
    )

    # -----------------------------------------------------
    # PRODUCT / SCHOOL / EVENT
    # -----------------------------------------------------

    draw_text(
        frame,
        "MOTIONAI",
        42,
        49,
        1.0,
        WHITE,
        3
    )

    draw_text(
        frame,
        "GIMM Boise State University",
        44,
        73,
        0.40,
        WHITE,
        1
    )

    draw_text(
        frame,
        "R-CON 2026",
        44,
        97,
        0.50,
        SAFETY_YELLOW,
        2
    )

    # -----------------------------------------------------
    # PRODUCT DESCRIPTION
    # -----------------------------------------------------

    draw_text(
        frame,
        "HUMAN MOVEMENT ASSESSMENT",
        315,
        52,
        0.55,
        MUTED,
        1
    )

    # -----------------------------------------------------
    # RIGHT STATUS
    # -----------------------------------------------------

    if right_text:

        text_size = cv2.getTextSize(
            right_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            2
        )[0]

        draw_text(
            frame,
            right_text,
            width - text_size[0] - 45,
            57,
            0.60,
            SAFETY_YELLOW,
            2
        )

    # Divider
    cv2.line(
        frame,
        (
            40,
            115
        ),
        (
            width - 40,
            115
        ),
        PANEL_LIGHT,
        1
    )


# =========================================================
# FOOTER
# =========================================================

def draw_footer(
    frame,
    controls=""
):

    height = frame.shape[0]
    width = frame.shape[1]

    y = height - 42

    cv2.line(
        frame,
        (
            40,
            y
        ),
        (
            width - 40,
            y
        ),
        PANEL_LIGHT,
        1
    )

    draw_text(
        frame,
        (
            "Prototype assessment criteria "
            "- demonstration system"
        ),
        42,
        height - 17,
        0.35,
        MUTED,
        1
    )

    if controls:

        size = cv2.getTextSize(
            controls,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            1
        )[0]

        draw_text(
            frame,
            controls,
            width - size[0] - 42,
            height - 17,
            0.35,
            MUTED,
            1
        )


# =========================================================
# STATUS ROW
# =========================================================

def draw_status_row(
    frame,
    x,
    y,
    label,
    status,
    color
):

    cv2.circle(
        frame,
        (
            x,
            y - 5
        ),
        7,
        color,
        -1
    )

    draw_text(
        frame,
        label,
        x + 22,
        y,
        0.47,
        WHITE,
        1
    )

    status_size = cv2.getTextSize(
        status,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        1
    )[0]

    draw_text(
        frame,
        status,
        x + 365 - status_size[0],
        y,
        0.43,
        color,
        1
    )


# =========================================================
# WORKER MOVEMENT PLACEHOLDER
# =========================================================

def draw_worker_placeholder(
    frame,
    x1,
    y1,
    x2,
    y2
):

    draw_panel(
        frame,
        x1,
        y1,
        x2,
        y2
    )

    draw_text(
        frame,
        "WORKER MOVEMENT TRACKING",
        x1 + 23,
        y1 + 35,
        0.47,
        MUTED,
        1
    )

    center_x = int(
        (
            x1 + x2
        )
        / 2
    )

    # Head
    cv2.circle(
        frame,
        (
            center_x,
            y1 + 105
        ),
        30,
        SAFETY_YELLOW,
        3
    )

    # Neck / torso
    cv2.line(
        frame,
        (
            center_x,
            y1 + 135
        ),
        (
            center_x,
            y1 + 250
        ),
        SAFETY_YELLOW,
        3
    )

    # Left arm
    cv2.line(
        frame,
        (
            center_x,
            y1 + 165
        ),
        (
            center_x - 75,
            y1 + 220
        ),
        SAFETY_YELLOW,
        3
    )

    # Right arm
    cv2.line(
        frame,
        (
            center_x,
            y1 + 165
        ),
        (
            center_x + 75,
            y1 + 220
        ),
        SAFETY_YELLOW,
        3
    )

    # Left leg
    cv2.line(
        frame,
        (
            center_x,
            y1 + 250
        ),
        (
            center_x - 55,
            y1 + 350
        ),
        SAFETY_YELLOW,
        3
    )

    # Right leg
    cv2.line(
        frame,
        (
            center_x,
            y1 + 250
        ),
        (
            center_x + 55,
            y1 + 350
        ),
        SAFETY_YELLOW,
        3
    )

    draw_text(
        frame,
        "TRACKING READY",
        x1 + 23,
        y2 - 24,
        0.44,
        GREEN,
        2
    )


# =========================================================
# LIFT PROGRESS
# =========================================================

def draw_lift_progress(
    frame,
    results,
    current_lift,
    total_lifts=5,
    y=605
):

    width = frame.shape[1]

    spacing = 130

    start_x = int(
        width / 2
        -
        (
            spacing
            * (
                total_lifts - 1
            )
            / 2
        )
    )

    for index in range(
        total_lifts
    ):

        number = (
            index + 1
        )

        x = (
            start_x
            + index * spacing
        )

        color = (
            90,
            92,
            95
        )

        # Completed lift
        if index < len(
            results
        ):

            result = (
                results[index][
                    "result"
                ]
            )

            if result == "PASS":

                color = GREEN

            elif result == "FAIL":

                color = RED

            else:

                color = AMBER

        # Current lift
        elif (
            number
            ==
            current_lift
        ):

            color = SAFETY_YELLOW

        cv2.circle(
            frame,
            (
                int(x),
                int(y)
            ),
            23,
            color,
            -1
        )

        number_size = cv2.getTextSize(
            str(number),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            2
        )[0]

        draw_text(
            frame,
            str(number),
            x - number_size[0] / 2,
            y + 7,
            0.52,
            DARK,
            2
        )

        label = (
            f"LIFT {number}"
        )

        label_size = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.32,
            1
        )[0]

        draw_text(
            frame,
            label,
            x - label_size[0] / 2,
            y + 42,
            0.32,
            MUTED,
            1
        )


# =========================================================
# OPENING / MENU SCREEN
# =========================================================

def draw_menu_screen(
    frame
):

    draw_header(
        frame
    )

    draw_centered_text(
        frame,
        "HUMAN MOVEMENT ASSESSMENT",
        190,
        1.02,
        WHITE,
        2
    )

    draw_centered_text(
        frame,
        (
            "REAL-TIME  |  CAMERA-BASED  |  "
            "NO WEARABLES"
        ),
        235,
        0.48,
        SAFETY_YELLOW,
        1
    )

    draw_panel(
        frame,
        250,
        280,
        frame.shape[1] - 250,
        530
    )

    draw_hazard_accent(
        frame,
        250,
        280,
        780,
        6
    )

    draw_centered_text(
        frame,
        "LIFTING TECHNIQUE DEMO",
        350,
        0.82,
        WHITE,
        2
    )

    draw_centered_text(
        frame,
        "Step into the assessment zone",
        405,
        0.56,
        MUTED,
        1
    )

    draw_centered_text(
        frame,
        "Keep your full body visible",
        440,
        0.56,
        MUTED,
        1
    )

    draw_centered_text(
        frame,
        "[  PRESS SPACE TO BEGIN  ]",
        495,
        0.68,
        SAFETY_YELLOW,
        2
    )

    draw_footer(
        frame,
        "SPACE Begin   Q Exit"
    )


# =========================================================
# CALIBRATION SCREEN
# =========================================================

def draw_calibration_screen(
    frame,
    progress
):

    draw_header(
        frame,
        "SYSTEM CALIBRATION"
    )

    draw_centered_text(
        frame,
        "CALIBRATING",
        220,
        1.30,
        SAFETY_YELLOW,
        3
    )

    draw_centered_text(
        frame,
        "Stand upright and remain still",
        270,
        0.58,
        MUTED,
        1
    )

    bar_x = 315
    bar_y = 340

    bar_width = 650
    bar_height = 24

    # Background bar
    cv2.rectangle(
        frame,
        (
            bar_x,
            bar_y
        ),
        (
            bar_x + bar_width,
            bar_y + bar_height
        ),
        PANEL_LIGHT,
        -1
    )

    # Progress
    filled = int(
        bar_width
        * progress
    )

    cv2.rectangle(
        frame,
        (
            bar_x,
            bar_y
        ),
        (
            bar_x + filled,
            bar_y + bar_height
        ),
        SAFETY_YELLOW,
        -1
    )

    draw_centered_text(
        frame,
        f"{progress * 100:.0f}%",
        425,
        1.05,
        WHITE,
        2
    )

    draw_centered_text(
        frame,
        "ESTABLISHING WORKER MOVEMENT BASELINE",
        475,
        0.45,
        MUTED,
        1
    )

    draw_centered_text(
        frame,
        "Full-body tracking required",
        515,
        0.43,
        MUTED,
        1
    )

    draw_footer(
        frame,
        "R Restart   Q Exit"
    )


# =========================================================
# ACTIVE ASSESSMENT SCREEN
# =========================================================

def draw_active_screen(
    frame,
    current_lift,
    results
):

    draw_header(
        frame,
        (
            f"LIFT ASSESSMENT "
            f"{current_lift} OF 5"
        )
    )

    # -----------------------------------------------------
    # CAMERA / MOVEMENT PANEL
    # -----------------------------------------------------

    draw_worker_placeholder(
        frame,
        45,
        140,
        750,
        530
    )

    # -----------------------------------------------------
    # TECHNIQUE PANEL
    # -----------------------------------------------------

    draw_panel(
        frame,
        780,
        140,
        1235,
        530
    )

    draw_text(
        frame,
        "TECHNIQUE STATUS",
        810,
        182,
        0.57,
        WHITE,
        2
    )

    draw_hazard_accent(
        frame,
        810,
        200,
        180,
        4
    )

    draw_status_row(
        frame,
        815,
        255,
        "TORSO CONTROL",
        "MONITORING",
        SAFETY_YELLOW
    )

    draw_status_row(
        frame,
        815,
        310,
        "LOWER BODY",
        "MONITORING",
        SAFETY_YELLOW
    )

    draw_status_row(
        frame,
        815,
        365,
        "BALANCE",
        "MONITORING",
        SAFETY_YELLOW
    )

    cv2.line(
        frame,
        (
            810,
            405
        ),
        (
            1205,
            405
        ),
        PANEL_LIGHT,
        1
    )

    draw_text(
        frame,
        "TRACKING",
        810,
        442,
        0.45,
        MUTED,
        1
    )

    draw_status_row(
        frame,
        815,
        490,
        "WORKER",
        "LOCKED",
        GREEN
    )

    # -----------------------------------------------------
    # INSTRUCTION
    # -----------------------------------------------------

    draw_centered_text(
        frame,
        "LIFT WHEN READY",
        575,
        0.88,
        GREEN,
        2
    )

    # -----------------------------------------------------
    # PROGRESS
    # -----------------------------------------------------

    draw_lift_progress(
        frame,
        results,
        current_lift,
        y=615
    )

    draw_footer(
        frame,
        "P Pass   F Fail   T Retry   R Restart   Q Exit"
    )


# =========================================================
# RESULT SCREEN
# =========================================================

def draw_result_screen(
    frame,
    result,
    score,
    feedback,
    lift_number,
    results
):

    draw_header(
        frame,
        f"LIFT {lift_number} COMPLETE"
    )

    width = frame.shape[1]

    # =====================================================
    # RESULT TYPE
    # =====================================================

    if result == "PASS":

        result_color = GREEN

        headline = (
            "MOVEMENT WITHIN TARGET RANGE"
        )

        recommendation = (
            "Maintain the same controlled "
            "lifting pattern."
        )

    elif result == "FAIL":

        result_color = RED

        headline = feedback

        upper_feedback = (
            feedback.upper()
        )

        if (
            "FORWARD LEAN"
            in upper_feedback
            or
            "TORSO"
            in upper_feedback
        ):

            recommendation = (
                "Increase lower-body involvement "
                "and maintain torso control."
            )

        elif (
            "KNEE"
            in upper_feedback
        ):

            recommendation = (
                "Use more lower-body movement "
                "through the lifting phase."
            )

        elif (
            "BALANCE"
            in upper_feedback
        ):

            recommendation = (
                "Maintain a more balanced "
                "and controlled body position."
            )

        else:

            recommendation = (
                "Review movement technique "
                "before the next lift."
            )

    else:

        result_color = AMBER

        headline = (
            "TRACKING QUALITY INSUFFICIENT"
        )

        recommendation = (
            "Keep your full body visible "
            "and repeat the same lift."
        )

    # =====================================================
    # MAIN PANEL
    # =====================================================

    draw_panel(
        frame,
        175,
        140,
        width - 175,
        535
    )

    # Thick status stripe
    cv2.rectangle(
        frame,
        (
            175,
            140
        ),
        (
            190,
            535
        ),
        result_color,
        -1
    )

    draw_centered_text(
        frame,
        "LIFT ASSESSMENT RESULT",
        185,
        0.46,
        MUTED,
        1
    )

    # =====================================================
    # PASS / FAIL
    # =====================================================

    draw_centered_text(
        frame,
        result,
        270,
        1.90,
        result_color,
        4
    )

    # =====================================================
    # SCORE
    # =====================================================

    if result != "RETRY":

        draw_centered_text(
            frame,
            "MOVEMENT SCORE",
            315,
            0.40,
            MUTED,
            1
        )

        draw_centered_text(
            frame,
            f"{score:.0f} / 100",
            360,
            1.0,
            WHITE,
            2
        )

    # =====================================================
    # OBSERVATION
    # =====================================================

    draw_hazard_accent(
        frame,
        390,
        390,
        500,
        4
    )

    draw_centered_text(
        frame,
        "PRIMARY OBSERVATION",
        425,
        0.40,
        MUTED,
        1
    )

    draw_centered_text(
        frame,
        headline,
        462,
        0.62,
        result_color,
        2
    )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    draw_centered_text(
        frame,
        "RECOMMENDED ACTION",
        495,
        0.38,
        MUTED,
        1
    )

    draw_centered_text(
        frame,
        recommendation,
        522,
        0.43,
        WHITE,
        1
    )

    # =====================================================
    # PROGRESS
    # =====================================================

    draw_lift_progress(
        frame,
        results,
        lift_number,
        y=610
    )

    draw_footer(
        frame,
        "R Restart   Q Exit"
    )


# =========================================================
# FINAL SESSION REPORT
# =========================================================

def draw_final_screen(
    frame,
    results
):

    draw_header(
        frame,
        "SESSION ASSESSMENT"
    )

    width = frame.shape[1]

    # =====================================================
    # DATA
    # =====================================================

    passed = sum(
        1
        for item in results
        if item["result"] == "PASS"
    )

    failed = [
        item
        for item in results
        if item["result"] == "FAIL"
    ]

    scores = [
        item["score"]
        for item in results
        if item["result"] != "RETRY"
    ]

    if scores:

        average = (
            sum(scores)
            / len(scores)
        )

    else:

        average = 0.0

    # =====================================================
    # TITLE
    # =====================================================

    draw_centered_text(
        frame,
        "SESSION ASSESSMENT",
        155,
        0.95,
        WHITE,
        2
    )

    draw_centered_text(
        frame,
        "LIFTING TECHNIQUE SUMMARY",
        188,
        0.44,
        MUTED,
        1
    )

    # =====================================================
    # LEFT SUMMARY
    # =====================================================

    draw_panel(
        frame,
        90,
        225,
        455,
        520
    )

    draw_text(
        frame,
        "SESSION RESULT",
        120,
        265,
        0.42,
        MUTED,
        1
    )

    draw_hazard_accent(
        frame,
        120,
        280,
        130,
        4
    )

    draw_text(
        frame,
        f"{passed} / 5",
        120,
        360,
        1.60,
        GREEN,
        4
    )

    draw_text(
        frame,
        "LIFTS PASSED",
        120,
        400,
        0.52,
        WHITE,
        2
    )

    draw_text(
        frame,
        "OVERALL MOVEMENT SCORE",
        120,
        455,
        0.40,
        MUTED,
        1
    )

    draw_text(
        frame,
        f"{average:.0f} / 100",
        120,
        495,
        0.78,
        WHITE,
        2
    )

    # =====================================================
    # RIGHT RESULTS
    # =====================================================

    draw_panel(
        frame,
        490,
        225,
        width - 90,
        520
    )

    draw_text(
        frame,
        "LIFT RESULTS",
        520,
        265,
        0.42,
        MUTED,
        1
    )

    draw_hazard_accent(
        frame,
        520,
        280,
        130,
        4
    )

    start_x = 545
    spacing = 130

    for index, item in enumerate(
        results
    ):

        x = (
            start_x
            + index * spacing
        )

        result = item[
            "result"
        ]

        if result == "PASS":

            color = GREEN

        elif result == "FAIL":

            color = RED

        else:

            color = AMBER

        cv2.circle(
            frame,
            (
                x,
                345
            ),
            29,
            color,
            -1
        )

        number_text = str(
            index + 1
        )

        size = cv2.getTextSize(
            number_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.56,
            2
        )[0]

        draw_text(
            frame,
            number_text,
            x - size[0] / 2,
            352,
            0.56,
            DARK,
            2
        )

        result_size = cv2.getTextSize(
            result,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            1
        )[0]

        draw_text(
            frame,
            result,
            x - result_size[0] / 2,
            397,
            0.38,
            color,
            1
        )

        score_text = (
            f"{item['score']:.0f}"
        )

        score_size = cv2.getTextSize(
            score_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            1
        )[0]

        draw_text(
            frame,
            score_text,
            x - score_size[0] / 2,
            430,
            0.43,
            WHITE,
            1
        )

    # =====================================================
    # PRIMARY OBSERVATION
    # =====================================================

    if failed:

        primary = (
            failed[0][
                "feedback"
            ]
        )

        draw_text(
            frame,
            "PRIMARY OBSERVATION",
            520,
            472,
            0.38,
            MUTED,
            1
        )

        draw_text(
            frame,
            primary,
            520,
            505,
            0.46,
            AMBER,
            2
        )

    else:

        draw_text(
            frame,
            "MOVEMENT PROFILE",
            520,
            472,
            0.38,
            MUTED,
            1
        )

        draw_text(
            frame,
            (
                "CONTROLLED MOVEMENT "
                "ACROSS ALL LIFTS"
            ),
            520,
            505,
            0.46,
            GREEN,
            2
        )

    # =====================================================
    # SESSION COMPLETE MESSAGE
    # =====================================================

    draw_centered_text(
        frame,
        "ASSESSMENT COMPLETE",
        575,
        0.62,
        SAFETY_YELLOW,
        2
    )

    draw_centered_text(
        frame,
        "Press R to begin a new assessment",
        610,
        0.43,
        MUTED,
        1
    )

    draw_footer(
        frame,
        "R New Assessment   Q Exit"
    )