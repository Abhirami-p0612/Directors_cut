import os
import cv2
import numpy as np
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

class PoseDetector:
    def __init__(self, model_path="models/pose_landmarker_lite.task"):
        self.model_path = model_path
        self.landmarker = None
        self.initialized = False
        self.error_message = None
        self._init_landmarker()

    def _init_landmarker(self):
        if not os.path.exists(self.model_path):
            alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.model_path)
            if os.path.exists(alt_path):
                self.model_path = alt_path
            else:
                self.error_message = f"Model file not found at {self.model_path}"
                print(f"[ERROR] {self.error_message}")
                return

        try:
            options = PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=self.model_path),
                running_mode=RunningMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.landmarker = PoseLandmarker.create_from_options(options)
            self.initialized = True
            print(f"[SUCCESS] MediaPipe PoseLandmarker initialized from {self.model_path}")
        except Exception as e:
            self.error_message = str(e)
            print(f"[ERROR] Failed to initialize PoseLandmarker: {e}")

    def detect(self, frame_bgr):
        """
        Accepts a BGR frame from OpenCV / base64 decode.
        Returns:
            landmarks: list of dicts [{'x': float, 'y': float, 'z': float, 'visibility': float}, ...] or None
            annotated_frame: None or can be used for drawing
            meta: dict with detection status and pose count
        """
        if not self.initialized or self.landmarker is None:
            return None, {"status": "error", "message": self.error_message or "Detector not initialized"}

        try:
            # MediaPipe expects RGB format
            rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            result = self.landmarker.detect(mp_image)

            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                pose = result.pose_landmarks[0]
                landmarks = [
                    {
                        "x": float(lm.x),
                        "y": float(lm.y),
                        "z": float(lm.z),
                        "visibility": float(lm.visibility if hasattr(lm, "visibility") and lm.visibility is not None else 1.0)
                    }
                    for lm in pose
                ]
                return landmarks, {"status": "ok", "pose_detected": True}
            else:
                return None, {"status": "ok", "pose_detected": False}

        except Exception as e:
            print(f"[WARNING] Detection error: {e}")
            return None, {"status": "error", "message": str(e)}

    def close(self):
        if self.landmarker:
            try:
                self.landmarker.close()
            except Exception:
                pass
            self.landmarker = None
            self.initialized = False
