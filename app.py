import os
import sys
import base64
import time
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, make_response

# Set writable cache dir for matplotlib/mediapipe
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"

from vision.detector import PoseDetector
from vision.actions import ActionClassifier
from vision.smoothing import ActionStabilizer
from vision.cinematic import get_cinematic_scene, CINEMATIC_MODES

app = Flask(__name__)

print("=" * 50)
print("🎬 INITIALIZING DIRECTOR'S CUT ENGINE...")
print("=" * 50)

detector = PoseDetector("models/pose_landmarker_lite.task")
classifier = ActionClassifier()
stabilizer = ActionStabilizer(window_size=4, min_agreement_ratio=0.55, cooldown_seconds=1.2)

print(f"🎬 Detector Status: {'READY' if detector.initialized else 'ERROR: ' + str(detector.error_message)}")
print("=" * 50)

@app.after_request
def add_no_cache_headers(response):
    """Disable caching so replacement soundtracks and script edits take effect immediately."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy" if detector.initialized else "degraded",
        "detector_initialized": detector.initialized,
        "detector_error": detector.error_message,
        "model_file": detector.model_path,
        "timestamp": time.time()
    })

@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Resets classifier state when a new movie is started."""
    global classifier, stabilizer
    classifier = ActionClassifier()
    stabilizer = ActionStabilizer(window_size=4, min_agreement_ratio=0.55, cooldown_seconds=1.2)
    return jsonify({"status": "ok", "message": "Session reset successfully"})

@app.route("/api/detect", methods=["POST"])
def detect_action():
    """
    Receives webcam frame.
    Processes with MediaPipe -> Action Recognition -> Temporal Smoothing -> Cinematic Mapping.
    """
    data = request.get_json(silent=True)
    if not data or "image" not in data:
        return jsonify({"status": "error", "message": "No image provided"}), 400

    try:
        # Decode base64 image
        img_data = data["image"]
        if "," in img_data:
            img_data = img_data.split(",", 1)[1]
        
        image_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Failed to decode image frame"}), 400

        # Step 1: Detect Pose with MediaPipe
        landmarks, meta = detector.detect(frame)

        # Step 2: Classify Action (Strictly 1 of the 6 actions)
        raw_action, confidence, details = classifier.classify(landmarks)

        # Step 3: Temporal Stabilization & Cooldown
        stabilized_action, scene_changed, stats = stabilizer.update(raw_action, confidence)

        # Step 4: Map to Cinematic Scene
        scene = get_cinematic_scene(stabilized_action)

        return jsonify({
            "status": "ok",
            "raw_action": raw_action,
            "action": stabilized_action,
            "confidence": confidence,
            "scene_changed": scene_changed,
            "mode": scene["id"],
            "genre": scene["genre"],
            "caption": scene["caption"],
            "drama_meter": scene["drama_meter"],
            "vfx_class": scene["vfx_class"],
            "bgm": scene["bgm"],
            "meme": scene["meme"],
            "details": details,
            "smoothing": stats,
            "has_landmarks": landmarks is not None and len(landmarks) > 0,
            "landmarks": landmarks if data.get("return_landmarks", False) else None
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Default to 5050 to avoid macOS AirPlay Receiver port 5000 conflict
    port = int(os.environ.get("PORT", 5050))
    print(f"🎬 DIRECTOR'S CUT starting on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
