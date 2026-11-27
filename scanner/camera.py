
import cv2


class Camera:
    """
    Handles camera initialization, frame capture,
    and camera release using OpenCV.
    """

    def __init__(self, camera_index=0, width=1280, height=720):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

    def start(self):
        """Initialize and start the camera."""

        if self.cap is not None and self.cap.isOpened():
            return True

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print("Error: Unable to open camera.")
            self.cap = None
            return False

        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print("Camera started successfully.")
        return True

    def read_frame(self):
        """Capture and return one camera frame."""

        if self.cap is None or not self.cap.isOpened():
            print("Error: Camera is not running.")
            return None

        ret, frame = self.cap.read()

        if not ret or frame is None:
            print("Warning: Unable to capture frame.")
            return None

        return frame

    def stop(self):
        """Release the camera."""

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        print("Camera stopped.")

    def is_running(self):
        """Check whether the camera is active."""

        return self.cap is not None and self.cap.isOpened()


# Standalone camera testing
if __name__ == "__main__":

    camera = Camera(camera_index=0)

    if camera.start():

        try:
            while True:
                frame = camera.read_frame()

                if frame is None:
                    break

                cv2.imshow("PLICKERS 2.0 - Camera", frame)

                # Press Q to stop
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            camera.stop()
            cv2.destroyAllWindows()
