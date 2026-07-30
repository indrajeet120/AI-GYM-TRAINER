import math
import time
from core.base_exercise import BaseExercise


class BicepsCurlDetector(BaseExercise):
    UP_THRESHOLD = 50
    DOWN_THRESHOLD = 160
    MIN_VISIBILITY = 0.4
    ELBOW_DRIFT_TOLERANCE = 0.06
    SWING_THRESHOLD = 15

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None
        self.stage_start_time = None
        self.last_rep_time = time.time()
        self.min_elbow_angle = 180

    def process(self, landmarks) -> dict:
        try:
            left_vis = landmarks[self.LEFT_ELBOW].visibility
            right_vis = landmarks[self.RIGHT_ELBOW].visibility
        except Exception:
            return None

        if left_vis >= right_vis:
            shoulder_idx, elbow_idx, wrist_idx = self.LEFT_SHOULDER, self.LEFT_ELBOW, self.LEFT_WRIST
        else:
            shoulder_idx, elbow_idx, wrist_idx = self.RIGHT_SHOULDER, self.RIGHT_ELBOW, self.RIGHT_WRIST

        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        if elbow_angle is None:
            return {"reps": self.reps, "pose_detected": True, "inactivity_warning": False}

        now = time.time()
        speed_status = "NORMAL"
        partial_rep = False

        if self.stage == "up":
            self.min_elbow_angle = min(self.min_elbow_angle, elbow_angle)

        if elbow_angle < self.UP_THRESHOLD:
            if self.stage != "up":
                self.stage = "up"
                self.stage_start_time = now
                self.min_elbow_angle = elbow_angle

        if elbow_angle > self.DOWN_THRESHOLD and self.stage == "up":
            rep_duration = now - (self.stage_start_time or now)
            self.stage = "down"

            if self.min_elbow_angle > (self.UP_THRESHOLD + 10):
                partial_rep = True

            if rep_duration < 0.7:
                speed_status = "TOO FAST"
            else:
                speed_status = "CONTROLLED"

            self.reps += 1
            self.last_rep_time = now
            self.min_elbow_angle = 180

        inactivity = (now - self.last_rep_time > 8.0) and (self.stage != "up")

        shoulder_x = landmarks[shoulder_idx].x
        elbow_x = landmarks[elbow_idx].x
        elbow_drift = abs(elbow_x - shoulder_x)

        if elbow_drift <= self.ELBOW_DRIFT_TOLERANCE:
            shoulder_status = "STABLE"
        else:
            shoulder_status = "ELBOW DRIFTING"

        shoulder_mid_x = (landmarks[self.LEFT_SHOULDER].x + landmarks[self.RIGHT_SHOULDER].x) / 2
        shoulder_mid_y = (landmarks[self.LEFT_SHOULDER].y + landmarks[self.RIGHT_SHOULDER].y) / 2
        hip_mid_x = (landmarks[self.LEFT_HIP].x + landmarks[self.RIGHT_HIP].x) / 2
        hip_mid_y = (landmarks[self.LEFT_HIP].y + landmarks[self.RIGHT_HIP].y) / 2

        dx = shoulder_mid_x - hip_mid_x
        dy = shoulder_mid_y - hip_mid_y
        torso_angle = self._safe_angle(dx, dy)

        if torso_angle <= self.SWING_THRESHOLD:
            swing_status = "NO SWING"
        else:
            swing_status = "SWINGING"

        rom_status = "PARTIAL" if partial_rep else ("FULL" if elbow_angle < self.UP_THRESHOLD else "NORMAL")

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "shoulder_status": shoulder_status,
            "swing_status": swing_status,
            "speed_status": speed_status,
            "rom_status": rom_status,
            "partial_rep": partial_rep,
            "inactivity_warning": inactivity,
            "pose_detected": True
        }

    def _safe_angle(self, dx, dy):
        return math.degrees(math.atan2(abs(dx), abs(dy))) if dy != 0 else 0.0