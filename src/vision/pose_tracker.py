from pathlib import Path
import time

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PoseTracker:
    """
    MotionAI human pose tracker.

    Uses MediaPipe Tasks PoseLandmarker.

    Produces:
    - 33 normalized body landmarks
    - 33 world-space landmarks
    - skeleton overlay
    """

    def __init__(
        self,
        model_path=None,
        min_detection_confidence=0.6,
        min_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    ):

        # =================================================
        # MODEL PATH
        # =================================================

        if model_path is None:

            project_root = (
                Path(__file__)
                .resolve()
                .parents[2]
            )

            model_path = (
                project_root
                / "models"
                / "pose_landmarker_full.task"
            )

        self.model_path = Path(
            model_path
        ).resolve()

        if not self.model_path.exists():

            raise FileNotFoundError(
                "\nPose model not found:\n"
                f"{self.model_path}\n"
            )

        # =================================================
        # MEDIAPIPE
        # =================================================

        base_options = (
            python.BaseOptions(
                model_asset_path=str(
                    self.model_path
                )
            )
        )

        options = (
            vision.PoseLandmarkerOptions(
                base_options=base_options,

                running_mode=(
                    vision.RunningMode.VIDEO
                ),

                num_poses=1,

                min_pose_detection_confidence=(
                    min_detection_confidence
                ),

                min_pose_presence_confidence=(
                    min_presence_confidence
                ),

                min_tracking_confidence=(
                    min_tracking_confidence
                ),

                output_segmentation_masks=False,
            )
        )

        self.landmarker = (
            vision.PoseLandmarker
            .create_from_options(
                options
            )
        )

        self.connections = [
            (
                connection.start,
                connection.end
            )
            for connection
            in (
                vision
                .PoseLandmarksConnections
                .POSE_LANDMARKS
            )
        ]

        self.start_time = (
            time.perf_counter()
        )

        self.last_timestamp_ms = -1

    # =====================================================
    # PROCESS FRAME
    # =====================================================

    def process(
        self,
        frame
    ):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        rgb_frame = (
            rgb_frame.copy()
        )

        mp_image = mp.Image(
            image_format=(
                mp.ImageFormat.SRGB
            ),
            data=rgb_frame
        )

        timestamp_ms = int(
            (
                time.perf_counter()
                - self.start_time
            )
            * 1000
        )

        # MediaPipe requires strictly
        # increasing timestamps.
        if (
            timestamp_ms
            <= self.last_timestamp_ms
        ):

            timestamp_ms = (
                self.last_timestamp_ms
                + 1
            )

        self.last_timestamp_ms = (
            timestamp_ms
        )

        result = (
            self.landmarker
            .detect_for_video(
                mp_image,
                timestamp_ms
            )
        )

        return result

    # =====================================================
    # DETECTION STATUS
    # =====================================================

    @staticmethod
    def person_detected(
        results
    ):

        return bool(
            results
            and results.pose_landmarks
        )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        frame,
        results
    ):

        if not self.person_detected(
            results
        ):

            return frame

        landmarks = (
            results.pose_landmarks[0]
        )

        height, width = (
            frame.shape[:2]
        )

        pixel_points = []

        for landmark in landmarks:

            x = int(
                landmark.x
                * width
            )

            y = int(
                landmark.y
                * height
            )

            pixel_points.append(
                (x, y)
            )

        # -------------------------------------------------
        # CONNECTIONS
        # -------------------------------------------------

        for start, end in (
            self.connections
        ):

            if (
                start >= len(landmarks)
                or end >= len(landmarks)
            ):

                continue

            start_landmark = (
                landmarks[start]
            )

            end_landmark = (
                landmarks[end]
            )

            start_visibility = (
                start_landmark.visibility
                if start_landmark.visibility
                is not None
                else 1.0
            )

            end_visibility = (
                end_landmark.visibility
                if end_landmark.visibility
                is not None
                else 1.0
            )

            if (
                start_visibility < 0.4
                or end_visibility < 0.4
            ):

                continue

            cv2.line(
                frame,
                pixel_points[start],
                pixel_points[end],
                (0, 255, 0),
                3,
                cv2.LINE_AA
            )

        # -------------------------------------------------
        # LANDMARK POINTS
        # -------------------------------------------------

        for index, point in enumerate(
            pixel_points
        ):

            landmark = (
                landmarks[index]
            )

            visibility = (
                landmark.visibility
                if landmark.visibility
                is not None
                else 1.0
            )

            if visibility < 0.4:

                continue

            cv2.circle(
                frame,
                point,
                5,
                (0, 165, 255),
                -1,
                cv2.LINE_AA
            )

        return frame

    # =====================================================
    # NORMALIZED LANDMARK
    # =====================================================

    def get_landmark(
        self,
        results,
        landmark_index
    ):

        if not self.person_detected(
            results
        ):

            return None

        if hasattr(
            landmark_index,
            "value"
        ):

            landmark_index = (
                landmark_index.value
            )

        landmarks = (
            results.pose_landmarks[0]
        )

        if not (
            0
            <= landmark_index
            < len(landmarks)
        ):

            return None

        point = (
            landmarks[
                landmark_index
            ]
        )

        return {
            "x": float(
                point.x
            ),
            "y": float(
                point.y
            ),
            "z": float(
                point.z
            ),
            "visibility": float(
                point.visibility
                if point.visibility
                is not None
                else 0.0
            ),
        }

    # =====================================================
    # WORLD LANDMARK
    # =====================================================

    def get_world_landmark(
        self,
        results,
        landmark_index
    ):

        if (
            results is None
            or not (
                results
                .pose_world_landmarks
            )
        ):

            return None

        if hasattr(
            landmark_index,
            "value"
        ):

            landmark_index = (
                landmark_index.value
            )

        landmarks = (
            results
            .pose_world_landmarks[0]
        )

        if not (
            0
            <= landmark_index
            < len(landmarks)
        ):

            return None

        point = (
            landmarks[
                landmark_index
            ]
        )

        return {
            "x": float(
                point.x
            ),
            "y": float(
                point.y
            ),
            "z": float(
                point.z
            ),
            "visibility": float(
                point.visibility
                if point.visibility
                is not None
                else 0.0
            ),
        }

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        if self.landmarker is not None:

            self.landmarker.close()

            self.landmarker = None

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        self.close()

        return False