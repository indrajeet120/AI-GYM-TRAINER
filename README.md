# 🏋️ AI Real-Time GYM TRAINER

<p align="center">
  <b>An AI-powered personal fitness assistant using Computer Vision, MediaPipe, and Real-Time Voice Coaching</b>
</p>

<p align="center">
  Track Workouts • Count Repetitions • Form Analysis • Real-Time Voice Coaching • Cloud & Local Ready
</p>

---

## 🚀 Project Overview

**AI Real-Time GYM TRAINER** is an intelligent, full-stack AI fitness application built with **Python, Streamlit, MediaPipe Pose, OpenCV, gTTS, and SQLite**.

The system tracks human body landmarks via live webcam feeds, calculates joint angles in real time, evaluates movement form, counts completed repetitions, and provides **proactive, human-like voice coaching** without interrupting video streaming or forcing page reruns.

It supports deployment on both **local machines** (using Pygame speaker audio) and **Streamlit Cloud** (using native browser HTML5 audio).

---

## ✨ Key Features

### 🎥 30+ FPS WebRTC Video Stream
- High-speed real-time pose tracking with MediaPipe Pose (`model_complexity=1`).
- 480x360 downscaled inference for low-latency CPU processing.
- Smooth 15–30 FPS webcam feed through `streamlit-webrtc`.

### 💪 Multi-Exercise Form & Rep Tracking
Automatically counts reps and evaluates posture for 5 core exercises:

| Exercise | Tracked Metrics | Form Checks |
|---|---|---|
| 🏋️ **Squats** | Knee Angle, Back Angle | Depth (Too High / Full), Torso Collapse, Leaning |
| 🤸 **Push-ups** | Elbow Angle, Hip Height | Body Alignment, Sagging / Piked Hips, Range of Motion |
| 💪 **Biceps Curl** | Elbow Angle, Shoulder | Shoulder Stability, Arm Swing Detection |
| 🔥 **Shoulder Press** | Elbow Angle, Extension | Overhead Lockout, Excessive Back Arch |
| 🦵 **Lunges** | Front Knee, Torso Angle | Knee Alignment, Balance & Stability |

### 🎙️ Asynchronous Dual-Mode AI Voice Coach
- **Thread-Safe `AudioManager` Singleton**: Asynchronous background worker thread with `PriorityQueue`.
- **Dual-Mode Audio Engine**:
  - *Local Mode*: Direct system speaker output via `pygame.mixer` with zero latency.
  - *Cloud Mode*: Native Streamlit `st.audio(..., autoplay=True)` browser playback.
- **Human-Like Coaching**:
  - Experience-based phrase pools (**Beginner**, **Intermediate**, **Advanced**).
  - Priority-based cues: Posture Errors > Range of Motion / Speed > Rep Praise > Inactivity Warnings.
  - 3.5s cooldowns to prevent overlapping speech or repetitive phrases.

### 📊 Workout History & Persistent Storage
- Built-in **SQLite database** (`gym_trainer.db`).
- Tracks user sessions, exercise logs, completed sets, reps, and workout duration.
- Interactive historical summary table in the Streamlit UI.

---

## 🏗️ System Architecture

```
                 Webcam Stream (streamlit-webrtc)
                                |
                                ↓
                    OpenCV Frame Preprocessing
                                |
                                ↓
                MediaPipe Pose Detection (480x360)
                                |
                                ↓
                      Landmark Smoothing
                                |
                                ↓
               Joint Angle & Form Metric Engine
                                |
          ---------------------------------------------
          |                                           |
          ↓                                           ↓
  Rep & Form Counter                         Voice Pipeline Engine
          |                                           |
          ↓                                           ↓
   SQLite Database                           AudioManager Singleton
          |                                  (Async Queue Worker)
          |                                           |
          ---------------------------------------------
                                |
                                ↓
                  Streamlit Live UI + Voice Output
                  (Local Speakers / Browser HTML5)
```

---

## 🛠️ Tech Stack

- **Core & Logic**: Python 3.11, NumPy, Pandas, SQLite
- **Computer Vision & Pose**: OpenCV 4.10.0, MediaPipe 0.10.14
- **Web App & Video Stream**: Streamlit 1.54.0, Streamlit-WebRTC 0.64.5
- **Audio & Speech**: gTTS (Google Text-to-Speech), Pygame Mixer 2.6.1

---

## 📂 Project Structure

```
AI-GYM-TRAINER
├── main.py                          # Main Streamlit Application Entrypoint
├── requirements.txt                 # Python Dependencies
├── packages.txt                     # Debian Linux System Dependencies (for Streamlit Cloud)
├── .python-version                  # Python Runtime Specification (3.11)
├── README.md                        # Documentation
│
├── detectors/                       # Exercise Pose Detectors
│   ├── squat.py                     # Squat Detector
│   ├── pushup.py                    # Push-up Detector
│   ├── biceps_curl.py               # Biceps Curl Detector
│   ├── shoulder_press.py            # Shoulder Press Detector
│   └── lunges.py                    # Lunges Detector
│
├── services/                        # Application Services & Architecture
│   ├── auth/                        # User Authentication Wall
│   ├── coaching/                    # AI Voice & Audio Management
│   │   ├── audio_manager.py         # Thread-Safe Singleton Audio Manager
│   │   ├── voice_pipeline.py        # Phrase Selection & Async Cue Dispatch
│   │   └── tts.py                   # Thread-Safe gTTS Speech Synthesizer
│   ├── config/                      # Workout Configurations & Phrase Pools
│   ├── persistence/                 # SQLite Database Repository
│   ├── state/                       # Session State Defaults
│   ├── tracking/                    # Real-time Metrics Synchronization
│   ├── ui/                          # Custom CSS & Audio Player Renderers
│   └── vision/                      # WebRTC Video Processor
│       └── exercise_video_processor.py
│
└── static/                          # Custom CSS & Font Assets
```

---

## ⚙️ Installation & Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/indrajeet120/AI-GYM-TRAINER.git
cd AI-GYM-TRAINER
```

### 2. Create & Activate Virtual Environment

```bash
# Create environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Locally

```bash
streamlit run main.py
```

Access the app in your browser at: `http://localhost:8501`

---

## ☁️ Deployment on Streamlit Cloud

The repository is fully configured for zero-error deployment on **Streamlit Cloud**:

1. Fork/Push this repository to GitHub.
2. Connect your GitHub repository to [share.streamlit.io](https://share.streamlit.io/).
3. Set Main File Path to `main.py`.
4. Streamlit Cloud will automatically install system dependencies from `packages.txt` (`libgl1`, `libglib2.0-0t64`, `libsm6`, `libxext6`, `libxrender1`) and run Python 3.11.

---

## 👨‍💻 Developer & Author

**Indrajeet Yadav**  
*B.Tech Electronics Engineering*  
- **GitHub**: [github.com/indrajeet120](https://github.com/indrajeet120)  
- **LinkedIn**: [linkedin.com/in/indrajeet-yadav](https://www.linkedin.com/in/indrajeet-yadav12)

---

## 📜 License

This project is open-source and developed for educational, fitness, and research purposes.
