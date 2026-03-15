import threading
import time
from abc import ABC, abstractmethod

class BaseCamera(ABC):
    def __init__(self, cfg):
        self.cfg = cfg
        self.width = int(cfg.get("width", 640))
        self.height = int(cfg.get("height", 480))
        self.fps = int(cfg.get("fps", 30))
        self.running = False
        self.thread = None
        self.raw_frames = {}
        self.lock = threading.Lock()
        self.last_error = None
        self.frame_counter = 0

    def start(self):
        if self.running:
            return
        self._initialize()
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        frame_time = 1.0 / self.fps
        while self.running:
            start = time.time()
            try:
                self._capture_frame()
                self.frame_counter += 1
            except Exception as e:
                self.last_error = str(e)

            elapsed = time.time() - start
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_raw_frame(self, stream_name):
        with self.lock:
            return self.raw_frames.get(stream_name)

    def get_status(self):
        streams = self.cfg.get("stream_sources", list(self.raw_frames.keys()))
        return {
            "running": self.running,
            "camera_source": self.__class__.__name__,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frame_counter": self.frame_counter,
            "last_error": self.last_error,
            "available_streams": streams
        }

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self._cleanup()

    @abstractmethod
    def _initialize(self):
        pass

    @abstractmethod
    def _capture_frame(self):
        pass

    @abstractmethod
    def _cleanup(self):
        pass


def create_camera(source, cfg):
    if source == "opencv":
        from .opencv_camera import OpenCVCamera
        return OpenCVCamera(cfg)
    elif source == "realsense":
        from .realsense_camera import RealsenseCamera
        return RealsenseCamera(cfg)
    else:
        raise ValueError(f"Unknown camera source: {source}")


__all__ = ["BaseCamera", "create_camera"]