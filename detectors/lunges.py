import time
from core.base_exercise import BaseExercise


class LungesDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.4
    BALANCE_TOLERANCE = 0.10

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None
        self.stage_start_time = None
        self.last_rep_time = time.time()
        self.min_knee_angle = 180

    def process(self, landmarks) -> dict:
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE),
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE),
        )

        if left_knee_angle is None or right_knee_angle is None:
            return {
                "reps": self.reps,
                "pose_detected": True,
                "inactivity_warning": False
            }

        if left_knee_angle <= right_knee_angle:
            front_knee_angle = left_knee_angle
            front_hip_idx, front_knee_idx, front_ankle_idx = self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE
            shoulder_idx_for_torso = self.LEFT_SHOULDER
        else:
            front_knee_angle = right_knee_angle
            front_hip_idx, front_knee_idx, front_ankle_idx = self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE
            shoulder_idx_for_torso = self.RIGHT_SHOULDER

        now = time.time()
        speed_status = "NORMAL"
        partial_rep = False

        if self.stage == "down":
            self.min_knee_angle = min(self.min_knee_angle, front_knee_angle)

        key_landmarks_visible = (
            landmarks[front_hip_idx].visibility > self.MIN_VISIBILITY and
            landmarks[front_knee_idx].visibility > self.MIN_VISIBILITY and
            landmarks[front_ankle_idx].visibility > self.MIN_VISIBILITY
        )

        if key_landmarks_visible:
            if front_knee_angle < self.DOWN_THRESHOLD:
                if self.stage != "down":
                    self.stage = "down"
                    self.stage_start_time = now
                    self.min_knee_angle = front_knee_angle

            if front_knee_angle > self.UP_THRESHOLD and self.stage == "down":
                rep_duration = now - (self.stage_start_time or now)
                self.stage = "up"

                if self.min_knee_angle > (self.DOWN_THRESHOLD - 5):
                    partial_rep = True

                if rep_duration < 0.85:
                    speed_status = "TOO FAST"
                else:
                    speed_status = "CONTROLLED"

                self.reps += 1
                self.last_rep_time = now
                self.min_knee_angle = 180

        inactivity = (now - self.last_rep_time > 8.0) and (self.stage != "down")

        torso_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx_for_torso),
            self.get_point(landmarks, front_hip_idx),
            self.get_point(landmarks, front_knee_idx),
        )
        if torso_angle is None:
            torso_angle = 180

        shoulder_mid_x = (landmarks[self.LEFT_SHOULDER].x + landmarks[self.RIGHT_SHOULDER].x) / 2
        hip_mid_x = (landmarks[self.LEFT_HIP].x + landmarks[self.RIGHT_HIP].x) / 2
        lateral_offset = abs(shoulder_mid_x - hip_mid_x)

        if lateral_offset <= self.BALANCE_TOLERANCE:
            balance_status = "BALANCED"
        else:
            balance_status = "OFF BALANCE"

        rom_status = "PARTIAL" if partial_rep else ("FULL" if front_knee_angle < self.DOWN_THRESHOLD else "NORMAL")

        return {
            "reps": self.reps,
            "front_knee_angle": int(front_knee_angle),
            "torso_angle": int(torso_angle),
            "balance_status": balance_status,
            "speed_status": speed_status,
            "rom_status": rom_status,
            "partial_rep": partial_rep,
            "inactivity_warning": inactivity,
            "pose_detected": True
        }