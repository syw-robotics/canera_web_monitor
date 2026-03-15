import cv2
from . import BaseCamera


class OpenCVCamera(BaseCamera):
    def _initialize(self):
        self.cap = cv2.VideoCapture(self.cfg.get("webcam_index", 0))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def _capture_frame(self):
        ret, frame = self.cap.read()
        if ret:
            with self.lock:
                self.raw_frames["rgb"] = frame

    def _cleanup(self):
        if hasattr(self, 'cap'):
            self.cap.release()