import json

from src.adapters.base_adapter import MocapAdapter
from src.motion_frame import JointData, MotionFrame, MotionSession


class JsonMotionAdapter(MocapAdapter):

    @property
    def name(self) -> str:
        return "MotionAI JSON Adapter"

    def load_session(self, source: str) -> MotionSession:

        with open(source, "r") as file:
            data = json.load(file)

        session = MotionSession(
            session_id=data["session_id"],
            activity=data["activity"],
            fps=data["fps"],
            subject_id=data.get("subject_id", "unknown"),
            source=data.get("source", "unknown")
        )

        for raw_frame in data["frames"]:

            frame = MotionFrame(
                timestamp=raw_frame["timestamp"],
                root_position=raw_frame.get(
                    "root_position",
                    [0.0, 0.0, 0.0]
                ),
                root_rotation=raw_frame.get(
                    "root_rotation",
                    [1.0, 0.0, 0.0, 0.0]
                )
            )

            for joint_name, raw_joint in raw_frame["joints"].items():

                frame.joints[joint_name] = JointData(
                    position=raw_joint.get(
                        "position",
                        [0.0, 0.0, 0.0]
                    ),
                    rotation=raw_joint.get(
                        "rotation",
                        [1.0, 0.0, 0.0, 0.0]
                    )
                )

            session.frames.append(frame)

        return session