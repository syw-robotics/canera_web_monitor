# Image Web Monitor

Web-based camera streaming application supporting OpenCV webcams and Intel RealSense depth cameras.

## Features

- Multi-stream display (RGB, Depth, Combined)
- Real-time status monitoring
- Fullscreen mode for each stream
- Video recording with toggle control
- Dark theme UI

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to select camera source:

```yaml
camera:
  source: "opencv"  # or "realsense"
```

Camera-specific configs in `cfg/opencv.yaml` and `cfg/realsense.yaml`.

## Usage

```bash
python server.py
```

Open browser: http://localhost:5050

## Controls

- Click image for fullscreen
- Record button: toggle recording (saves to `recordings/`)
