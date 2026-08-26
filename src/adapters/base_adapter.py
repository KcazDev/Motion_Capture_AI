from abc import ABC, abstractmethod

from src.motion_frame import MotionSession


class MocapAdapter(ABC):
    """
    Base interface for every motion-capture system used by MotionAI.

    Any future mocap suit adapter should convert its native data
    into a MotionSession.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def load_session(self, source: str) -> MotionSession:
        """
        Load motion data from a source and convert it into
        MotionAI's standard MotionSession format.
        """
        pass

    def supports_live_stream(self) -> bool:
        """
        Override this when a mocap system supports live streaming.
        """
        return False

    def start_stream(self):
        """
        Future interface for real-time mocap streaming.
        """
        raise NotImplementedError(
            f"{self.name} does not support live streaming."
        )