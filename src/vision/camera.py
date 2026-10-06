import cv2


class Camera:
    """
    MotionAI webcam interface.

    Supports:
    - Windows webcams
    - Context manager usage
    - Resolution/FPS configuration
    - Clean shutdown
    """

    def __init__(
        self,
        camera_index=0,
        width=1280,
        height=720,
        fps=30
    ):
        self.camera_index = int(camera_index)
        self.width = int(width)
        self.height = int(height)
        self.target_fps = int(fps)

        self.capture = None

    # =====================================================
    # OPEN
    # =====================================================

    def open(self):

        if (
            self.capture is not None
            and self.capture.isOpened()
        ):
            return self

        print()
        print("=" * 60)
        print("MOTIONAI CAMERA")
        print("=" * 60)

        print()
        print(
            f"Opening camera index "
            f"{self.camera_index}..."
        )

        # DirectShow usually behaves well
        # with USB webcams on Windows.
        self.capture = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_DSHOW
        )

        # Fall back if DirectShow fails.
        if not self.capture.isOpened():

            print(
                "DirectShow failed. "
                "Trying default backend..."
            )

            self.capture.release()

            self.capture = cv2.VideoCapture(
                self.camera_index
            )

        if not self.capture.isOpened():

            raise RuntimeError(
                f"Could not open camera "
                f"index {self.camera_index}."
            )

        # MJPG often helps webcams deliver
        # higher resolution / FPS.
        self.capture.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(
                *"MJPG"
            )
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        self.capture.set(
            cv2.CAP_PROP_FPS,
            self.target_fps
        )

        actual_width = int(
            self.capture.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        actual_height = int(
            self.capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        actual_fps = float(
            self.capture.get(
                cv2.CAP_PROP_FPS
            )
        )

        print()
        print("Camera connected.")

        print(
            f"Resolution: "
            f"{actual_width} x "
            f"{actual_height}"
        )

        print(
            f"Requested FPS: "
            f"{self.target_fps}"
        )

        print(
            f"Camera reported FPS: "
            f"{actual_fps:.2f}"
        )

        print()

        return self

    # =====================================================
    # READ
    # =====================================================

    def read(self):

        if (
            self.capture is None
            or not self.capture.isOpened()
        ):

            raise RuntimeError(
                "Camera is not open."
            )

        success, frame = (
            self.capture.read()
        )

        if not success:

            return False, None

        return True, frame

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self):

        self.open()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        self.release()

        return False

    # =====================================================
    # RELEASE
    # =====================================================

    def release(self):

        if self.capture is not None:

            self.capture.release()

            self.capture = None

        cv2.destroyAllWindows()