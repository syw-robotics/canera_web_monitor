import cv2
import numpy as np
import pyrealsense2 as rs
from . import BaseCamera


class RealsenseCamera(BaseCamera):
    def _initialize(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
        config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)
        self.pipeline.start(config)

        self.align = rs.align(rs.stream.color) if self.cfg.get("align_depth", True) else None
        self.colorizer = rs.colorizer()

    def _capture_frame(self):
        frames = self.pipeline.wait_for_frames()
        if self.align:
            frames = self.align.process(frames)

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            return

        depth_colorized = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Ensure both images have same dimensions for combined view
        if depth_colorized.shape[:2] != color_image.shape[:2]:
            depth_colorized = cv2.resize(depth_colorized, (color_image.shape[1], color_image.shape[0]))

        combined = np.hstack((depth_colorized, color_image))

        with self.lock:
            self.raw_frames["depth"] = depth_colorized
            self.raw_frames["color"] = color_image
            self.raw_frames["combined"] = combined

    def _cleanup(self):
        if hasattr(self, 'pipeline'):
            self.pipeline.stop()