from enum import IntEnum
import math

import numpy as np


class PoseLandmark(IntEnum):
    NOSE = 0

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14

    LEFT_WRIST = 15
    RIGHT_WRIST = 16

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    LEFT_HEEL = 29
    RIGHT_HEEL = 30

    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


# =========================================================
# LANDMARK HELPERS
# =========================================================

def landmark_xy(landmark):

    return np.array(
        [
            float(landmark.x),
            float(landmark.y)
        ],
        dtype=np.float32
    )


def midpoint(
    landmark_a,
    landmark_b
):

    point_a = landmark_xy(
        landmark_a
    )

    point_b = landmark_xy(
        landmark_b
    )

    return (
        point_a
        + point_b
    ) / 2.0


# =========================================================
# VISIBILITY
# =========================================================

def visibility(
    landmark
):

    value = getattr(
        landmark,
        "visibility",
        None
    )

    if value is None:
        return 0.0

    return float(
        value
    )


def average_visibility(
    landmarks,
    landmark_indices
):

    values = []

    for index in landmark_indices:

        if index >= len(landmarks):
            continue

        values.append(
            visibility(
                landmarks[index]
            )
        )

    if not values:
        return 0.0

    return float(
        np.mean(
            values
        )
    )


# =========================================================
# JOINT ANGLE
# =========================================================

def calculate_angle(
    point_a,
    point_b,
    point_c
):
    """
    Returns angle ABC in degrees.

    point_b is the vertex.

    Example:
    hip -> knee -> ankle

    gives knee flexion angle.
    """

    a = np.array(
        point_a,
        dtype=np.float32
    )

    b = np.array(
        point_b,
        dtype=np.float32
    )

    c = np.array(
        point_c,
        dtype=np.float32
    )

    vector_a = (
        a - b
    )

    vector_c = (
        c - b
    )

    magnitude_a = float(
        np.linalg.norm(
            vector_a
        )
    )

    magnitude_c = float(
        np.linalg.norm(
            vector_c
        )
    )

    if (
        magnitude_a < 1e-8
        or magnitude_c < 1e-8
    ):
        return 0.0

    cosine = (
        np.dot(
            vector_a,
            vector_c
        )
        /
        (
            magnitude_a
            * magnitude_c
        )
    )

    cosine = float(
        np.clip(
            cosine,
            -1.0,
            1.0
        )
    )

    return float(
        math.degrees(
            math.acos(
                cosine
            )
        )
    )


# =========================================================
# TORSO LEAN
# =========================================================

def torso_lean_from_vertical(
    shoulder_center,
    hip_center
):
    """
    Returns absolute torso angle away from vertical.

    0 degrees = upright
    larger angle = greater forward/backward lean
    """

    vector = (
        shoulder_center
        - hip_center
    )

    dx = float(
        vector[0]
    )

    dy = float(
        vector[1]
    )

    if (
        abs(dx) < 1e-8
        and abs(dy) < 1e-8
    ):
        return 0.0

    angle = math.degrees(
        math.atan2(
            abs(dx),
            abs(dy)
        )
    )

    return float(
        angle
    )


# =========================================================
# SHOULDER TILT
# =========================================================

def horizontal_tilt(
    point_a,
    point_b
):
    """
    Angle of a line relative to horizontal.

    Useful for shoulder or hip imbalance.
    """

    dx = float(
        point_b[0]
        - point_a[0]
    )

    dy = float(
        point_b[1]
        - point_a[1]
    )

    if (
        abs(dx) < 1e-8
        and abs(dy) < 1e-8
    ):
        return 0.0

    angle = math.degrees(
        math.atan2(
            dy,
            dx
        )
    )

    return float(
        abs(angle)
    )