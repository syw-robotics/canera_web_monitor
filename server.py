import atexit
import yaml
import cv2
import os
import webbrowser
import threading
from datetime import datetime
from flask import Flask, Response, jsonify, render_template

recordings = {}
recording_lock = threading.Lock()

def load_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    source = config["camera"]["source"]
    with open(f"cfg/{source}.yaml") as f:
        config["camera"].update(yaml.safe_load(f))
    return config

config = load_config("config.yaml")
app = Flask(__name__, template_folder="ui")

from camera import create_camera
camera = create_camera(config["camera"]["source"], config["camera"])
camera.start()


@app.route("/")
def index():
    return render_template("index.html")


def gen_stream(stream_name):
    import time
    while True:
        raw = camera.get_raw_frame(stream_name)
        if raw is None:
            continue

        _, jpeg = cv2.imencode('.jpg', raw)
        frame = jpeg.tobytes()

        with recording_lock:
            if stream_name in recordings:
                rec = recordings[stream_name]
                current_time = time.time()
                if rec["last_time"] is None or (current_time - rec["last_time"]) >= rec["frame_interval"]:
                    rec["writer"].write(raw)
                    rec["last_time"] = current_time

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/stream/<stream_name>")
def stream_feed(stream_name):
    return Response(
        gen_stream(stream_name),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/status")
def camera_status():
    return jsonify(camera.get_status())


@app.route("/api/recording/<stream>/start", methods=["POST"])
def start_recording(stream):
    with recording_lock:
        if stream in recordings:
            return jsonify({"error": "Already recording"}), 400

        raw_frame = camera.get_raw_frame(stream)
        if raw_frame is None:
            return jsonify({"error": "No frame available"}), 400

        output_dir = config.get("recording", {}).get("output_dir", "recordings")
        video_format = config.get("recording", {}).get("format", "avi")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{stream}_{timestamp}.{video_format}"

        h, w = raw_frame.shape[:2]

        fourcc = cv2.VideoWriter_fourcc(*'mp4v') if video_format == "mp4" else cv2.VideoWriter_fourcc(*'XVID')

        writer = cv2.VideoWriter(filename, fourcc, camera.fps, (w, h))
        recordings[stream] = {
            "writer": writer,
            "filename": filename,
            "last_time": None,
            "frame_interval": 1.0 / camera.fps
        }

        return jsonify({"status": "started", "filename": filename, "message": f"Recording {stream} stream..."})


@app.route("/api/recording/<stream>/stop", methods=["POST"])
def stop_recording(stream):
    with recording_lock:
        if stream not in recordings:
            return jsonify({"error": "Not recording"}), 400

        try:
            recordings[stream]["writer"].release()
            filename = recordings[stream]["filename"]
            del recordings[stream]
            return jsonify({"status": "stopped", "filename": filename, "message": f"Video saved to {filename}"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


atexit.register(camera.stop)


if __name__ == "__main__":
    host = config["server"]["host"]
    port = config["server"]["port"]
    url = f"http://127.0.0.1:{port}"

    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    app.run(
        host=host,
        port=port,
        debug=config["server"]["debug"],
        threaded=True,
    )
