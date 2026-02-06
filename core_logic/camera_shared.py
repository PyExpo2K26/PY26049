import threading

class CameraShared:
    """
    Shared camera instance for thread-safe frame sharing between
    gesture control (producer) and dashboard (consumer).
    """
    def __init__(self):
        self.current_frame = None
        self.lock = threading.Lock()

    def update_frame(self, frame):
        """Called by gesture control to update the current frame."""
        with self.lock:
            self.current_frame = frame.copy() if frame is not None else None

    def get_frame(self):
        """Called by dashboard to get the latest frame."""
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None


# Global shared instance
camera_shared_instance = CameraShared()