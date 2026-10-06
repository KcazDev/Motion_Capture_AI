from dataclasses import dataclass


@dataclass
class ScoringThresholds:
    """
    Prototype MotionAI lifting criteria.

    These values are for the R-CON demonstration and
    are not certified medical, OSHA, or ergonomic standards.
    """

    # Torso
    max_torso_lean: float = 45.0

    # Lower-body involvement
    min_knee_flexion: float = 20.0

    # Camera / pose quality
    min_visibility: float = 0.70

    # Overall passing score
    minimum_score: float = 75.0


class LiftScorer:
    """
    Evaluates one completed lifting cycle.

    Current scoring:
    - torso control
    - lower-body involvement
    - movement consistency/alignment
    - tracking quality
    """

    def __init__(
        self,
        thresholds=None
    ):

        self.thresholds = (
            thresholds
            if thresholds is not None
            else ScoringThresholds()
        )

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def clamp(
        value,
        minimum=0.0,
        maximum=100.0
    ):

        return max(
            minimum,
            min(
                maximum,
                value
            )
        )

    # =====================================================
    # COMPONENT SCORES
    # =====================================================

    def torso_score(
        self,
        max_torso_lean
    ):

        if max_torso_lean <= 20.0:
            return 100.0

        if max_torso_lean >= 60.0:
            return 0.0

        score = (
            100.0
            -
            (
                (max_torso_lean - 20.0)
                / 40.0
                * 100.0
            )
        )

        return self.clamp(
            score
        )

    def lower_body_score(
        self,
        knee_flexion
    ):

        if knee_flexion <= 5.0:
            return 0.0

        if knee_flexion >= 45.0:
            return 100.0

        score = (
            (knee_flexion - 5.0)
            / 40.0
            * 100.0
        )

        return self.clamp(
            score
        )

    def alignment_score(
        self,
        average_tilt
    ):

        if average_tilt <= 5.0:
            return 100.0

        if average_tilt >= 25.0:
            return 0.0

        score = (
            100.0
            -
            (
                (average_tilt - 5.0)
                / 20.0
                * 100.0
            )
        )

        return self.clamp(
            score
        )

    def visibility_score(
        self,
        visibility
    ):

        if visibility >= 0.95:
            return 100.0

        if visibility <= 0.50:
            return 0.0

        score = (
            (visibility - 0.50)
            / 0.45
            * 100.0
        )

        return self.clamp(
            score
        )

    # =====================================================
    # SCORE COMPLETE LIFT
    # =====================================================

    def score(
        self,
        completed_lift
    ):

        if not completed_lift:

            return None

        frames = completed_lift.get(
            "frames",
            []
        )

        if not frames:

            return {
                "result": "RETRY",
                "overall_score": 0.0,
                "reasons": [
                    "Not enough movement data was captured."
                ],
                "strengths": [],
                "metrics": {},
            }

        # =================================================
        # EXTRACT VALUES
        # =================================================

        torso_values = [
            frame["torso_lean"]
            for frame in frames
        ]

        knee_values = [
            frame["average_knee_angle"]
            for frame in frames
        ]

        visibility_values = [
            frame["body_visibility"]
            for frame in frames
        ]

        shoulder_tilt_values = [
            frame["shoulder_tilt"]
            for frame in frames
        ]

        hip_tilt_values = [
            frame["hip_tilt"]
            for frame in frames
        ]

        # =================================================
        # SUMMARY METRICS
        # =================================================

        max_torso_lean = max(
            torso_values
        )

        minimum_knee_angle = min(
            knee_values
        )

        average_visibility = (
            sum(
                visibility_values
            )
            /
            len(
                visibility_values
            )
        )

        average_shoulder_tilt = (
            sum(
                shoulder_tilt_values
            )
            /
            len(
                shoulder_tilt_values
            )
        )

        average_hip_tilt = (
            sum(
                hip_tilt_values
            )
            /
            len(
                hip_tilt_values
            )
        )

        average_body_tilt = (
            average_shoulder_tilt
            + average_hip_tilt
        ) / 2.0

        baseline_knee = (
            completed_lift.get(
                "baseline_knee_angle"
            )
        )

        if baseline_knee is None:

            baseline_knee = max(
                knee_values
            )

        knee_flexion = (
            baseline_knee
            - minimum_knee_angle
        )

        # =================================================
        # COMPONENT SCORES
        # =================================================

        torso = self.torso_score(
            max_torso_lean
        )

        lower_body = (
            self.lower_body_score(
                knee_flexion
            )
        )

        alignment = (
            self.alignment_score(
                average_body_tilt
            )
        )

        visibility = (
            self.visibility_score(
                average_visibility
            )
        )

        # =================================================
        # TOTAL
        # =================================================

        overall_score = (
            torso * 0.40
            +
            lower_body * 0.35
            +
            alignment * 0.10
            +
            visibility * 0.15
        )

        overall_score = round(
            overall_score,
            1
        )

        # =================================================
        # FIRST: VERIFY CAMERA DATA
        # =================================================

        if (
            average_visibility
            <
            self.thresholds.min_visibility
        ):

            return {
                "result": "RETRY",

                "overall_score": overall_score,

                "torso_score": round(
                    torso,
                    1
                ),

                "lower_body_score": round(
                    lower_body,
                    1
                ),

                "alignment_score": round(
                    alignment,
                    1
                ),

                "visibility_score": round(
                    visibility,
                    1
                ),

                "reasons": [
                    (
                        "MotionAI could not see enough "
                        "of your body to reliably "
                        "evaluate the lift."
                    )
                ],

                "strengths": [],

                "metrics": {
                    "max_torso_lean": round(
                        max_torso_lean,
                        1
                    ),

                    "knee_flexion": round(
                        knee_flexion,
                        1
                    ),

                    "average_visibility": round(
                        average_visibility * 100.0,
                        1
                    ),
                },
            }

        # =================================================
        # PASS / FAIL CHECKS
        # =================================================

        torso_pass = (
            max_torso_lean
            <=
            self.thresholds.max_torso_lean
        )

        knee_pass = (
            knee_flexion
            >=
            self.thresholds.min_knee_flexion
        )

        reasons = []
        strengths = []

        # -------------------------------------------------
        # TORSO
        # -------------------------------------------------

        if torso_pass:

            strengths.append(
                (
                    "Torso movement remained within "
                    "the current target range."
                )
            )

        else:

            reasons.append(
                (
                    "Excessive forward torso lean "
                    "was detected during the lift."
                )
            )

        # -------------------------------------------------
        # LOWER BODY
        # -------------------------------------------------

        if knee_pass:

            strengths.append(
                (
                    "Good lower-body movement was "
                    "detected during the lift."
                )
            )

        else:

            reasons.append(
                (
                    "Limited knee movement was "
                    "detected during pickup."
                )
            )

        # -------------------------------------------------
        # ALIGNMENT
        # -------------------------------------------------

        if average_body_tilt <= 15.0:

            strengths.append(
                (
                    "Body alignment remained "
                    "reasonably controlled."
                )
            )

        elif average_body_tilt > 25.0:

            reasons.append(
                (
                    "Large body alignment changes "
                    "were detected during the lift."
                )
            )

        # =================================================
        # RESULT
        # =================================================

        critical_pass = (
            torso_pass
            and knee_pass
        )

        score_pass = (
            overall_score
            >=
            self.thresholds.minimum_score
        )

        if (
            critical_pass
            and score_pass
        ):

            result = "PASS"

        else:

            result = "FAIL"

        # =================================================
        # OUTPUT
        # =================================================

        return {
            "result": result,

            "overall_score": overall_score,

            "torso_score": round(
                torso,
                1
            ),

            "lower_body_score": round(
                lower_body,
                1
            ),

            "alignment_score": round(
                alignment,
                1
            ),

            "visibility_score": round(
                visibility,
                1
            ),

            "checks": {
                "torso_control": torso_pass,
                "lower_body_use": knee_pass,
            },

            "reasons": reasons,

            "strengths": strengths,

            "metrics": {
                "max_torso_lean": round(
                    max_torso_lean,
                    1
                ),

                "minimum_knee_angle": round(
                    minimum_knee_angle,
                    1
                ),

                "knee_flexion": round(
                    knee_flexion,
                    1
                ),

                "average_body_tilt": round(
                    average_body_tilt,
                    1
                ),

                "average_visibility": round(
                    average_visibility * 100.0,
                    1
                ),
            },
        }
