# Image Web Monitor - Design Document

**Date:** 2026-03-15
**Status:** Draft
**Goal:** Complete the image web stream project with both OpenCV and RealSense camera support

## 1. Overview

A Flask-based web application that streams camera feeds (RGB, depth, combined) from either OpenCV webcams or Intel RealSense depth cameras. The UI displays multiple streams with real-time status updates.

## 2. Current State

**Completed:**
- Flask server routes (`/`, `/stream/<name>`, `/api/status`)
- UI with dark theme, grid layout, status polling
- Base camera class structure
- Config files (config.yaml, cfg/opencv.yaml, cfg/realsense.yaml)

**Missing:**
- Config loader utility
- Camera initialization and factory pattern
- Frame capture with threading
- Image process for streams
- OpenCV camera implementation
- RealSense camera implementation
- Error handling and status reporting
- Video Recording function in the web ui. Add a button for windows of each stream source
- Full screen function(for earch windows of each source)

## 3. Architecture

### 3.1 Component Structure

```
camera/
  __init__.py          # BaseCamera + factory
  opencv_camera.py     # OpenCVCamera implementation
  realsense_camera.py  # RealsenseCamera implementation
server.py              # Flask app (needs camera init)
cfg/
  opencv.yaml          # OpenCV config
  realsense.yaml       # RealSense config
config.yaml            # Main config (selects camera source)
```

### 3.2 Camera Class Design

**BaseCamera** (abstract):
- Threading for continuous frame capture
- Frame buffer management (latest frame per stream)
- Status tracking (running, errors, frame counter)
- Abstract methods: `_initialize()`, `_capture_frame()`, `_cleanup()`

**OpenCVCamera**:
- Uses cv2.VideoCapture for webcam
- Streams: `rgb` only
- JPEG encoding with configurable quality

**RealsenseCamera**:
- Uses pyrealsense2 SDK
- Streams: `depth`, `color`, `combined` (side-by-side)
- Depth colorization for visualization
- Optional depth-to-color alignment

### 3.3 Configuration

**config.yaml:**
```yaml
server:
  host: "0.0.0.0"
  port: 5050
  debug: false

camera:
  source: "opencv"  # or "realsense"
  config_file: "cfg/opencv.yaml"  # or "cfg/realsense.yaml"
```

**cfg/opencv.yaml:**
```yaml
stream_sources: [rgb]
webcam_index: 0
width: 640
height: 480
fps: 30
quality: 85
```

**cfg/realsense.yaml:**
```yaml
stream_sources: [depth, color, combined] # config which, show which in the web ui
width: 640
height: 480
fps: 30
align_depth: true
depth_mode: "colorized"
```

## 4. Implementation Plan

### Phase 1: Core Infrastructure
1. Config loader (`load_config()` in server.py)
2. BaseCamera with threading and frame management
3. Camera factory function

### Phase 2: OpenCV Implementation
4. OpenCVCamera class with webcam capture
5. RGB stream with JPEG encoding
6. Test with webcam

### Phase 3: RealSense Implementation
7. RealsenseCamera class with pyrealsense2
8. Depth stream with colorization
9. Color stream
10. Combined stream (side-by-side)
11. Test with RealSense device

### Phase 4: Integration
12. Wire camera factory into server.py
13. Update UI template path (templates/ → ui/)
14. Test both camera sources
15. Error handling and status API

### Phase 5: UI Enhancements
16. Add fullscreen button for each stream window
17. Add recording button for each stream window
18. Recording API endpoint (start/stop recording)
19. Save recordings with timestamps

## 5. Key Technical Decisions

**Threading Model:**
- Background thread continuously captures frames
- Main thread serves latest frame from buffer
- Thread-safe frame access with locks

**Stream Format:**
- MJPEG (multipart/x-mixed-replace)
- JPEG encoding per frame
- Boundary delimiter: `--frame`

**Error Handling:**
- Graceful degradation (return None if no frame)
- Status API reports errors
- Camera auto-restart on failure (optional)

**Dependencies:**
- opencv-python (OpenCV)
- pyrealsense2 (RealSense)
- Flask
- PyYAML

## 6. Success Criteria

- [ ] OpenCV camera streams RGB from webcam
- [ ] RealSense camera streams depth, color, combined
- [ ] UI displays all streams without errors
- [ ] Status API reports camera state accurately
- [ ] Config switching works (opencv ↔ realsense)
- [ ] Clean shutdown (camera.stop() on exit)
- [ ] No frame drops under normal load

## 7. Out of Scope

- Recording/saving streams
- Multi-camera support
- Authentication/authorization
- Stream quality adaptation
