from src.vision.landmark_utils import (
    PoseLandmark,
    landmark_xy,
    midpoint,
    calculate_angle,
    torso_lean_from_vertical,
    horizontal_tilt,
    average_visibility
)


class MovementMetrics:
    """
    Calculates live human movement measurements
    from MediaPipe pose landmarks.
    """

    IMPORTANT_LANDMARKS = [
        PoseLandmark.LEFT_SHOULDER,
        PoseLandmark.RIGHT_SHOULDER,

        PoseLandmark.LEFT_ELBOW,
        PoseLandmark.RIGHT_ELBOW,

        PoseLandmark.LEFT_WRIST,
        PoseLandmark.RIGHT_WRIST,

        PoseLandmark.LEFT_HIP,
        PoseLandmark.RIGHT_HIP,

        PoseLandmark.LEFT_KNEE,
        PoseLandmark.RIGHT_KNEE,

        PoseLandmark.LEFT_ANKLE,
        PoseLandmark.RIGHT_ANKLE,
    ]

    # =====================================================
    # ANALYZE FRAME
    # =====================================================

    def analyze(
        self,
        results
    ):

        if (
            results is None
            or not results.pose_landmarks
        ):

            return None

        landmarks = (
            results.pose_landmarks[0]
        )

        # =================================================
        # BODY POINTS
        # =================================================

        left_shoulder = landmarks[
            PoseLandmark.LEFT_SHOULDER
        ]

        right_shoulder = landmarks[
            PoseLandmark.RIGHT_SHOULDER
        ]

        left_hip = landmarks[
            PoseLandmark.LEFT_HIP
        ]

        right_hip = landmarks[
            PoseLandmark.RIGHT_HIP
        ]

        left_knee = landmarks[
            PoseLandmark.LEFT_KNEE
        ]

        right_knee = landmarks[
            PoseLandmark.RIGHT_KNEE
        ]

        left_ankle = landmarks[
            PoseLandmark.LEFT_ANKLE
        ]

        right_ankle = landmarks[
            PoseLandmark.RIGHT_ANKLE
        ]

        left_wrist = landmarks[
            PoseLandmark.LEFT_WRIST
        ]

        right_wrist = landmarks[
            PoseLandmark.RIGHT_WRIST
        ]

        # =================================================
        # MIDPOINTS
        # =================================================

        shoulder_center = midpoint(
            left_shoulder,
            right_shoulder
        )

        hip_center = midpoint(
            left_hip,
            right_hip
        )

        # =================================================
        # TORSO LEAN
        # =================================================

        torso_lean = (
            torso_lean_from_vertical(
                shoulder_center,
                hip_center
            )
        )

        # =================================================
        # KNEE ANGLES
        # =================================================

        left_knee_angle = (
            calculate_angle(
                landmark_xy(
                    left_hip
                ),
                landmark_xy(
                    left_knee
                ),
                landmark_xy(
                    left_ankle
                )
            )
        )

        right_knee_angle = (
            calculate_angle(
                landmark_xy(
                    right_hip
                ),
                landmark_xy(
                    right_knee
                ),
                landmark_xy(
                    right_ankle
                )
            )
        )

        # =================================================
        # HIP ANGLES
        # =================================================

        left_hip_angle = (
            calculate_angle(
                landmark_xy(
                    left_shoulder
                ),
                landmark_xy(
                    left_hip
                ),
                landmark_xy(
                    left_knee
                )
            )
        )

        right_hip_angle = (
            calculate_angle(
                landmark_xy(
                    right_shoulder
                ),
                landmark_xy(
                    right_hip
                ),
                landmark_xy(
                    right_knee
                )
            )
        )

        # =================================================
        # SHOULDER TILT
        # =================================================

        shoulder_tilt = (
            horizontal_tilt(
                landmark_xy(
                    left_shoulder
                ),
                landmark_xy(
                    right_shoulder
                )
            )
        )

        # =================================================
        # HIP TILT
        # =================================================

        hip_tilt = (
            horizontal_tilt(
                landmark_xy(
                    left_hip
                ),
                landmark_xy(
                    right_hip
                )
            )
        )

        # =================================================
        # WRIST HEIGHT
        # =================================================

        average_wrist_y = (
            (
                float(
                    left_wrist.y
                )
                +
                float(
                    right_wrist.y
                )
            )
            / 2.0
        )

        # MediaPipe Y increases downward.
        # Smaller Y means hands are higher.
        wrist_height = (
            1.0
            - average_wrist_y
        )

        # =================================================
        # VISIBILITY
        # =================================================

        body_visibility = (
            average_visibility(
                landmarks,
                [
                    int(index)
                    for index
                    in self.IMPORTANT_LANDMARKS
                ]
            )
        )

        # =================================================
        # AVERAGES
        # =================================================

        average_knee_angle = (
            left_knee_angle
            + right_knee_angle
        ) / 2.0

        average_hip_angle = (
            left_hip_angle
            + right_hip_angle
        ) / 2.0

        # =================================================
        # OUTPUT
        # =================================================

        return {
            "torso_lean": (
                torso_lean
            ),

            "left_knee_angle": (
                left_knee_angle
            ),

            "right_knee_angle": (
                right_knee_angle
            ),

            "average_knee_angle": (
                average_knee_angle
            ),

            "left_hip_angle": (
                left_hip_angle
            ),

            "right_hip_angle": (
                right_hip_angle
            ),

            "average_hip_angle": (
                average_hip_angle
            ),

            "shoulder_tilt": (
                shoulder_tilt
            ),

            "hip_tilt": (
                hip_tilt
            ),

            "wrist_height": (
                wrist_height
            ),

            "body_visibility": (
                body_visibility
            ),
        }