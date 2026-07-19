
import os
import cv2
import av
import numpy as np
import mediapipe as mp
import threading
import time

from streamlit_webrtc import VideoProcessorBase
from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector

from services.config.workout_config import POSE_CONNECTIONS


class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"
        self.frame_count = 0
        self.process_every = 3  
        self.last_processed_frame = None
        self.prev_landmarks = None

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.7
        )
        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }

    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()

    def set_exercise(self, exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self._exercise_type
        
    def smooth_points(self, landmarks, alpha=0.65):
        if self.prev_landmarks is None:
            self.prev_landmarks = landmarks
            return landmarks
        smooth = []
        for prev, curr in zip(self.prev_landmarks, landmarks):
            lm = type(curr)()
            lm.x = alpha * prev.x + (1-alpha) * curr.x
            lm.y = alpha * prev.y + (1-alpha) * curr.y
            lm.z = alpha * prev.z + (1-alpha) * curr.z
            lm.visibility = curr.visibility
            smooth.append(lm)
        self.prev_landmarks = smooth
        return smooth

    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]
        if not landmarks:
            return
        for start_idx, end_idx in POSE_CONNECTIONS:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                p1 = landmarks[start_idx]
                p2 = landmarks[end_idx]
                cv2.line(img, (int(p1.x * w), int(p1.y * h)), (int(p2.x * w), int(p2.y * h)), (0, 255, 0), 2)

    def _draw_no_pose_warnings(self, img):
        cv2.putText(img, "NO POSE DETECTED", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def recv(self, frame):
        try:
            image = frame.to_ndarray(format="bgr24")
            image = cv2.flip(image, 1)
            self.frame_count += 1
            
            if self.frame_count % self.process_every != 0:
                if self.last_processed_frame is not None:
                    return av.VideoFrame.from_ndarray(self.last_processed_frame, format="bgr24")
                return av.VideoFrame.from_ndarray(image, format="bgr24")

            image = cv2.convertScaleAbs(image, alpha=1.2, beta=20)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                landmarks = self.smooth_points(landmarks)
                self._draw_skeleton(image, landmarks)

                ex_type = self.get_exercise()
                detector = self._detectors.get(ex_type)

                if detector:
                    try:
                        metrics = detector.process(landmarks)
                        if metrics is None:
                            metrics = self.get_latest_metrics() or {"reps": 0, "pose_detected": True}
                    except Exception as e:
                        metrics = self.get_latest_metrics() or {"reps": 0, "pose_detected": True}

                    metrics["pose_detected"] = True 
                    self.set_latest_metrics(metrics)
                else:
                    self.set_latest_metrics({"pose_detected": True, "reps": 0})
            else:
                old_m = self.get_latest_metrics() or {"reps": 0}
                old_m["pose_detected"] = False
                self.set_latest_metrics(old_m)
            
            self.last_processed_frame = image.copy()
            return av.VideoFrame.from_ndarray(image, format="bgr24")
        except Exception as e:
            print("VIDEO PROCESSOR ERROR:", e)
            return av.VideoFrame.from_ndarray(image, format="bgr24")