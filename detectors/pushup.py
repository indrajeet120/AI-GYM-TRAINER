import time
from core.base_exercise import BaseExercise


class PushUpDetector(BaseExercise):
    DOWN_THRESHOLD = 90
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.4
    HIP_SAG_TOLERANCE = 0.08

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

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
            hip_idx, ankle_idx = self.LEFT_HIP, self.LEFT_ANKLE
        else:
            shoulder_idx, elbow_idx, wrist_idx = self.RIGHT_SHOULDER, self.RIGHT_ELBOW, self.RIGHT_WRIST
            hip_idx, ankle_idx = self.RIGHT_HIP, self.RIGHT_ANKLE

        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )

        if elbow_angle is None or body_angle is None:
            return {"reps": self.reps, "pose_detected": True, "inactivity_warning": False}

        shoulder_y = landmarks[shoulder_idx].y
        ankle_y = landmarks[ankle_idx].y
        hip_y = landmarks[hip_idx].y

        expected_hip_y = (shoulder_y + ankle_y) / 2
        hip_deviation = hip_y - expected_hip_y

        now = time.time()
        speed_status = "NORMAL"
        partial_rep = False

        if self.stage == "down":
            self.min_elbow_angle = min(self.min_elbow_angle, elbow_angle)

        if elbow_angle < self.DOWN_THRESHOLD:
            if self.stage != "down":
                self.stage = "down"
                self.stage_start_time = now
                self.min_elbow_angle = elbow_angle

        if elbow_angle > self.UP_THRESHOLD and self.stage == "down":
            rep_duration = now - (self.stage_start_time or now)
            self.stage = "up"

            if self.min_elbow_angle > (self.DOWN_THRESHOLD - 5):
                partial_rep = True

            if rep_duration < 0.75:
                speed_status = "TOO FAST"
            else:
                speed_status = "CONTROLLED"

            self.reps += 1
            self.last_rep_time = now
            self.min_elbow_angle = 180

        inactivity = (now - self.last_rep_time > 8.0) and (self.stage != "down")

        if body_angle > 160:
            body_alignment = "Straight"
        elif body_angle > 140:
            body_alignment = "Slight Bend"
        else:
            body_alignment = "Poor Form"

        if abs(hip_deviation) <= self.HIP_SAG_TOLERANCE:
            hip_status = "LEVEL"
        elif hip_deviation > self.HIP_SAG_TOLERANCE:
            hip_status = "SAGGING"
        else:
            hip_status = "PIKED UP"

        rom_status = "PARTIAL" if partial_rep else ("FULL" if elbow_angle < self.DOWN_THRESHOLD else "NORMAL")

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "body_alignment": body_alignment,
            "hip_status": hip_status,
            "speed_status": speed_status,
            "rom_status": rom_status,
            "partial_rep": partial_rep,
            "inactivity_warning": inactivity,
            "pose_detected": True
        }