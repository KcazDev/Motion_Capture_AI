from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class JointData:
    """
    Stores the motion data for one joint at one moment in time.
    """

    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    # Quaternion rotation:
    # [w, x, y, z]
    rotation: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0, 0.0])


@dataclass
class MotionFrame:
    """
    Represents one frame of human motion.
    """

    timestamp: float

    root_position: List[float] = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    root_rotation: List[float] = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 0.0]
    )

    joints: Dict[str, JointData] = field(default_factory=dict)


@dataclass
class MotionSession:
    """
    Represents an entire recorded motion sequence.
    """

    session_id: str
    activity: str
    fps: float

    frames: List[MotionFrame] = field(default_factory=list)

    subject_id: str = "unknown"
    source: str = "unknown"