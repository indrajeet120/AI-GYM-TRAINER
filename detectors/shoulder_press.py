import time
from core.base_exercise import BaseExercise


class ShoulderPressDetector(BaseExercise):
    UP_THRESHOLD = 160
    DOWN_THRESHOLD = 90
    MIN_VISIBILITY = 0.4

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None
        self.stage_start_time = None
        self.last_rep_time = time.time()
        self.max_elbow_angle = 0
        self.last_extension_status = None
        self.last_back_arch_status = None

    def process(self, landmarks):
        if landmarks is None or len(landmarks) < 33:
            return {
                "reps": self.reps,
                "elbow_angle": 0,
                "extension_status": "N/A",
                "back_arch_status": "N/A",
                "inactivity_warning": False
            }

        try:
            left_vis = landmarks[self.LEFT_ELBOW].visibility
            right_vis = landmarks[self.RIGHT_ELBOW].visibility

            if left_vis >= right_vis:
                shoulder_idx, elbow_idx, wrist_idx = self.LEFT_SHOULDER, self.LEFT_ELBOW, self.LEFT_WRIST
                hip_idx, knee_idx = self.LEFT_HIP, self.LEFT_KNEE
            else:
                shoulder_idx, elbow_idx, wrist_idx = self.RIGHT_SHOULDER, self.RIGHT_ELBOW, self.RIGHT_WRIST
                hip_idx, knee_idx = self.RIGHT_HIP, self.RIGHT_KNEE

            elbow_angle = self.calculate_angle(
                self.get_point(landmarks, shoulder_idx),
                self.get_point(landmarks, elbow_idx),
                self.get_point(landmarks, wrist_idx),
            )

            if elbow_angle is None:
                elbow_angle = 0

            now = time.time()
            speed_status = "NORMAL"
            partial_rep = False

            if self.stage == "up":
                self.max_elbow_angle = max(self.max_elbow_angle, elbow_angle)

            if elbow_angle <= self.DOWN_THRESHOLD:
                if self.stage != "down":
                    self.stage = "down"
                    self.stage_start_time = now

            elif elbow_angle >= self.UP_THRESHOLD and self.stage == "down":
                rep_duration = now - (self.stage_start_time or now)
                self.stage = "up"

                if self.max_elbow_angle < (self.UP_THRESHOLD - 5):
                    partial_rep = True

                if rep_duration < 0.75:
                    speed_status = "TOO FAST"
                else:
                    speed_status = "CONTROLLED"

                self.reps += 1
                self.last_rep_time = now
                self.max_elbow_angle = 0

            inactivity = (now - self.last_rep_time > 8.0) and (self.stage != "up")

            if elbow_angle >= 162:
                extension_status = "FULL EXTENSION"
            elif elbow_angle >= 140:
                extension_status = "NEARLY EXTENDED"
            elif elbow_angle >= 90:
                extension_status = "PRESSING"
            else:
                extension_status = "START POSITION"

            back_angle = self.calculate_angle(
                self.get_point(landmarks, shoulder_idx),
                self.get_point(landmarks, hip_idx),
                self.get_point(landmarks, knee_idx),
            )
            if back_angle is None:
                back_angle = 180

            if back_angle >= 160:
                back_arch_status = "Neutral"
            elif back_angle >= 140:
                back_arch_status = "Slight Arch"
            else:
                back_arch_status = "Excessive Arch"

            state_changed = extension_status != self.last_extension_status
            self.last_extension_status = extension_status

            rom_status = "PARTIAL" if partial_rep else ("FULL" if extension_status == "FULL EXTENSION" else "NORMAL")

            return {
                "reps": self.reps,
                "elbow_angle": int(elbow_angle),
                "extension_status": extension_status,
                "back_arch_status": back_arch_status,
                "speed_status": speed_status,
                "rom_status": rom_status,
                "partial_rep": partial_rep,
                "inactivity_warning": inactivity,
                "state_changed": state_changed,
                "pose_detected": True
            }

        except Exception as e:
            print("ShoulderPressDetector ERROR:", e)
            return {
                "reps": self.reps,
                "elbow_angle": 0,
                "extension_status": "N/A",
                "back_arch_status": "N/A",
                "inactivity_warning": False
            }