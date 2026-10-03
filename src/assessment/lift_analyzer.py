from collections import deque
from enum import Enum


class LiftState(Enum):

    CALIBRATING = "CALIBRATING"
    READY = "READY"
    LOWERING = "LOWERING"
    BOTTOM = "BOTTOM"
    LIFTING = "LIFTING"
    COMPLETE = "COMPLETE"


class LiftAnalyzer:

    def __init__(
        self,
        calibration_frames=60
    ):

        self.calibration_frames = (
            calibration_frames
        )

        self.state = (
            LiftState.CALIBRATING
        )

        self.calibration_data = []

        self.baseline_knee = None
        self.baseline_torso = None
        self.baseline_wrist = None

        self.knee_history = deque(
            maxlen=5
        )

        self.torso_history = deque(
            maxlen=5
        )

        self.wrist_history = deque(
            maxlen=5
        )

        self.current_frames = []

        self.min_knee = None
        self.max_torso = None
        self.min_wrist = None

        self.complete_hold_frames = 0

        self.last_completed_lift = None

        self.lift_count = 0

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def average(values):

        if not values:
            return 0.0

        return (
            sum(values)
            / len(values)
        )

    def reset_current_lift(self):

        self.current_frames = []

        self.min_knee = None
        self.max_torso = None
        self.min_wrist = None

        self.complete_hold_frames = 0

    # =====================================================
    # CALIBRATION
    # =====================================================

    def calibrate(
        self,
        metrics
    ):

        self.calibration_data.append(
            {
                "knee": metrics[
                    "average_knee_angle"
                ],

                "torso": metrics[
                    "torso_lean"
                ],

                "wrist": metrics[
                    "wrist_height"
                ],
            }
        )

        if (
            len(self.calibration_data)
            <
            self.calibration_frames
        ):

            return

        self.baseline_knee = self.average(
            [
                item["knee"]
                for item
                in self.calibration_data
            ]
        )

        self.baseline_torso = self.average(
            [
                item["torso"]
                for item
                in self.calibration_data
            ]
        )

        self.baseline_wrist = self.average(
            [
                item["wrist"]
                for item
                in self.calibration_data
            ]
        )

        self.state = (
            LiftState.READY
        )

        print()
        print(
            "MotionAI calibration complete."
        )

        print(
            f"Baseline knee: "
            f"{self.baseline_knee:.1f}"
        )

        print(
            f"Baseline torso: "
            f"{self.baseline_torso:.1f}"
        )

        print()

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        metrics
    ):

        if metrics is None:

            return self.get_status()

        # Avoid analyzing badly tracked frames.
        if (
            metrics["body_visibility"]
            < 0.55
        ):

            return self.get_status()

        # =================================================
        # CALIBRATION
        # =================================================

        if (
            self.state
            ==
            LiftState.CALIBRATING
        ):

            self.calibrate(
                metrics
            )

            return self.get_status()

        # =================================================
        # SMOOTHING
        # =================================================

        self.knee_history.append(
            metrics[
                "average_knee_angle"
            ]
        )

        self.torso_history.append(
            metrics[
                "torso_lean"
            ]
        )

        self.wrist_history.append(
            metrics[
                "wrist_height"
            ]
        )

        knee = self.average(
            self.knee_history
        )

        torso = self.average(
            self.torso_history
        )

        wrist = self.average(
            self.wrist_history
        )

        # =================================================
        # READY
        # =================================================

        if (
            self.state
            ==
            LiftState.READY
        ):

            knee_change = (
                self.baseline_knee
                - knee
            )

            torso_change = (
                torso
                - self.baseline_torso
            )

            wrist_drop = (
                self.baseline_wrist
                - wrist
            )

            if (
                knee_change > 10.0
                or
                torso_change > 8.0
                or
                wrist_drop > 0.07
            ):

                self.state = (
                    LiftState.LOWERING
                )

                self.reset_current_lift()

                print(
                    "Lift started."
                )

        # =================================================
        # LOWERING
        # =================================================

        if (
            self.state
            ==
            LiftState.LOWERING
        ):

            self.current_frames.append(
                dict(metrics)
            )

            if (
                self.min_knee is None
                or
                knee < self.min_knee
            ):

                self.min_knee = knee

            if (
                self.max_torso is None
                or
                torso > self.max_torso
            ):

                self.max_torso = torso

            if (
                self.min_wrist is None
                or
                wrist < self.min_wrist
            ):

                self.min_wrist = wrist

            deep_knee_change = (
                self.baseline_knee
                - knee
            )

            deep_torso_change = (
                torso
                - self.baseline_torso
            )

            deep_wrist_drop = (
                self.baseline_wrist
                - wrist
            )

            if (
                deep_knee_change > 20.0
                or
                deep_torso_change > 15.0
                or
                deep_wrist_drop > 0.12
            ):

                self.state = (
                    LiftState.BOTTOM
                )

        # =================================================
        # BOTTOM
        # =================================================

        elif (
            self.state
            ==
            LiftState.BOTTOM
        ):

            self.current_frames.append(
                dict(metrics)
            )

            if (
                knee < self.min_knee
            ):

                self.min_knee = knee

            if (
                torso > self.max_torso
            ):

                self.max_torso = torso

            if (
                wrist < self.min_wrist
            ):

                self.min_wrist = wrist

            knee_recovery = (
                knee
                - self.min_knee
            )

            wrist_recovery = (
                wrist
                - self.min_wrist
            )

            torso_recovery = (
                self.max_torso
                - torso
            )

            if (
                knee_recovery > 7.0
                or
                wrist_recovery > 0.05
                or
                torso_recovery > 5.0
            ):

                self.state = (
                    LiftState.LIFTING
                )

                print(
                    "Lifting phase detected."
                )

        # =================================================
        # LIFTING
        # =================================================

        elif (
            self.state
            ==
            LiftState.LIFTING
        ):

            self.current_frames.append(
                dict(metrics)
            )

            knee_near_baseline = (
                knee
                >
                self.baseline_knee
                - 12.0
            )

            torso_near_baseline = (
                torso
                <
                self.baseline_torso
                + 10.0
            )

            if (
                knee_near_baseline
                and
                torso_near_baseline
            ):

                self.complete_hold_frames += 1

            else:

                self.complete_hold_frames = 0

            if (
                self.complete_hold_frames
                >= 8
            ):

                self.state = (
                    LiftState.COMPLETE
                )

                self.lift_count += 1

                self.last_completed_lift = {
                    "lift_number": (
                        self.lift_count
                    ),

                    "frames": list(
                        self.current_frames
                    ),

                    "min_knee_angle": (
                        self.min_knee
                    ),

                    "max_torso_lean": (
                        self.max_torso
                    ),

                    "min_wrist_height": (
                        self.min_wrist
                    ),

                    "baseline_knee_angle": (
                        self.baseline_knee
                    ),

                    "baseline_torso_lean": (
                        self.baseline_torso
                    ),

                    "baseline_wrist_height": (
                        self.baseline_wrist
                    ),
                }

                print()
                print(
                    "=" * 40
                )

                print(
                    f"LIFT "
                    f"{self.lift_count} "
                    f"COMPLETE"
                )

                print(
                    "=" * 40
                )

        # =================================================
        # COMPLETE
        # =================================================

        elif (
            self.state
            ==
            LiftState.COMPLETE
        ):

            if (
                knee
                >
                self.baseline_knee
                - 8.0
                and
                torso
                <
                self.baseline_torso
                + 7.0
            ):

                self.state = (
                    LiftState.READY
                )

                self.reset_current_lift()

        return self.get_status()

    # =====================================================
    # STATUS
    # =====================================================

    def get_status(self):

        calibration_progress = 1.0

        if (
            self.state
            ==
            LiftState.CALIBRATING
        ):

            calibration_progress = (
                len(
                    self.calibration_data
                )
                /
                self.calibration_frames
            )

            calibration_progress = min(
                calibration_progress,
                1.0
            )

        return {
            "state": (
                self.state.value
            ),

            "lift_count": (
                self.lift_count
            ),

            "calibration_progress": (
                calibration_progress
            ),

            "last_completed_lift": (
                self.last_completed_lift
            ),
        }
