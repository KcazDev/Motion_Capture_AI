from pathlib import Path

from src.adapters.base_adapter import MocapAdapter
from src.motion_frame import MotionSession


class RokokoAdapter(MocapAdapter):
    """
    Adapter for Rokoko motion-capture data.

    This adapter will eventually convert Rokoko-specific
    recordings or live-stream data into MotionAI's
    standardized MotionSession format.

    Current status:
        Adapter architecture ready.
        Rokoko input format pending hardware/software testing.
    """

    @property
    def name(self) -> str:
        return "Rokoko MotionAI Adapter"

    def load_session(self, source: str) -> MotionSession:
        """
        Load a recorded Rokoko motion file.

        The exact parsing implementation will be added once
        we confirm which Rokoko export format will be used
        (BVH, FBX, CSV, SDK stream, etc.).
        """

        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Rokoko motion file not found: {source_path}"
            )

        extension = source_path.suffix.lower()

        if extension == ".bvh":
            return self._load_bvh(source_path)

        elif extension == ".csv":
            return self._load_csv(source_path)

        elif extension == ".fbx":
            return self._load_fbx(source_path)

        elif extension == ".json":
            return self._load_json(source_path)

        else:
            raise ValueError(
                "Unsupported Rokoko motion format: "
                f"{extension or 'no extension'}"
            )

    # -----------------------------------------------------
    # FORMAT LOADERS
    # -----------------------------------------------------

    def _load_bvh(self, source_path: Path) -> MotionSession:
        """
        Future Rokoko BVH parser.
        """

        raise NotImplementedError(
            "BVH support is ready to be implemented once "
            "a real Rokoko BVH recording is available."
        )

    def _load_csv(self, source_path: Path) -> MotionSession:
        """
        Future Rokoko CSV parser.
        """

        raise NotImplementedError(
            "CSV support is ready to be implemented once "
            "a real Rokoko CSV recording is available."
        )

    def _load_fbx(self, source_path: Path) -> MotionSession:
        """
        Future Rokoko FBX parser.
        """

        raise NotImplementedError(
            "FBX support is ready to be implemented once "
            "a real Rokoko FBX recording is available."
        )

    def _load_json(self, source_path: Path) -> MotionSession:
        """
        Reserved for future Rokoko SDK/live-stream recordings
        that may be stored as JSON.
        """

        raise NotImplementedError(
            "Rokoko JSON support will be implemented once "
            "the SDK or stream format is confirmed."
        )

    # -----------------------------------------------------
    # LIVE STREAMING
    # -----------------------------------------------------

    def supports_live_stream(self) -> bool:
        """
        MotionAI is designed to support future live Rokoko
        streaming, but this remains disabled until the
        available Rokoko interface is confirmed.
        """

        return False

    def start_stream(self):
        """
        Future entry point for receiving live Rokoko motion.
        """

        raise NotImplementedError(
            "Live Rokoko streaming has not been configured yet."
        )

    # -----------------------------------------------------
    # JOINT NORMALIZATION
    # -----------------------------------------------------

    @staticmethod
    def normalize_joint_name(joint_name: str) -> str:
        """
        Convert a Rokoko joint name into a standardized
        MotionAI-style joint name.

        More mappings will be added after inspecting
        actual Rokoko skeleton data.
        """

        name = joint_name.strip()

        known_joints = {
            "Hips": "pelvis",
            "Spine": "spine",
            "Neck": "neck",
            "Head": "head",

            "LeftShoulder": "left_shoulder",
            "LeftArm": "left_shoulder",
            "LeftForeArm": "left_elbow",
            "LeftHand": "left_wrist",

            "RightShoulder": "right_shoulder",
            "RightArm": "right_shoulder",
            "RightForeArm": "right_elbow",
            "RightHand": "right_wrist",

            "LeftUpLeg": "left_hip",
            "LeftLeg": "left_knee",
            "LeftFoot": "left_ankle",

            "RightUpLeg": "right_hip",
            "RightLeg": "right_knee",
            "RightFoot": "right_ankle",
        }

        if name in known_joints:
            return known_joints[name]

        # Generic fallback:
        # "RightForeArm" -> "right_fore_arm"
        result = ""

        for index, character in enumerate(name):

            if (
                character.isupper()
                and index > 0
                and name[index - 1].islower()
            ):
                result += "_"

            result += character.lower()

        return result

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    def status(self) -> dict:
        """
        Useful for showing the current integration state
        in development tools or future interfaces.
        """

        return {
            "adapter": self.name,
            "manufacturer": "Rokoko",
            "recorded_input": "pending",
            "live_stream": "pending",
            "motionai_output": "MotionSession",
            "ready_for_real_data": True
        }