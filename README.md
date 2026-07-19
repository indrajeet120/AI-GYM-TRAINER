# 🏋️ AI Real-Time GYM TRAINER

<p align="center">
  <b>An AI-powered personal fitness assistant using Computer Vision and Pose Estimation</b>
</p>

<p align="center">
  Track workouts • Count repetitions • Analyze posture • Get real-time AI coaching
</p>

---

## 🚀 Project Overview

**AI Real-Time GYM TRAINER** is an intelligent fitness assistant that uses **Computer Vision, MediaPipe Pose Estimation, and Artificial Intelligence** to analyze human body movements through a webcam.

The system detects body landmarks, calculates joint angles, identifies exercise movements, counts repetitions automatically, and provides real-time feedback to improve workout form.

It works like a virtual AI fitness coach that helps users perform exercises correctly without requiring a physical trainer.

---

## ✨ Features

### 🎥 Real-Time Pose Detection
- Real-time human pose tracking using MediaPipe.
- Detects body landmarks from webcam input.
- Works with live video streaming.

### 💪 Exercise Recognition & Rep Counting

Supported exercises:

| Exercise | Status |
|---|---|
| 🏋️ Squats | ✅ |
| 🤸 Push-ups | ✅ |
| 💪 Biceps Curl | ✅ |
| 🔥 Shoulder Press | ✅ |
| 🦵 Lunges | ✅ |

The AI counts repetitions automatically by analyzing body movement patterns.

---

## 🧠 AI Form Analysis

The trainer analyzes workout posture and provides corrections:

✅ Squat depth checking  
✅ Back posture monitoring  
✅ Elbow angle analysis  
✅ Body alignment detection  
✅ Range of motion tracking  


Example feedback:

```
✔ Good Rep!

⚠ Keep your back straight

⚠ Go deeper

⚠ Maintain proper posture
```

---

# 🔊 AI Voice Coach

The application provides audio feedback using Text-To-Speech technology.

Voice guidance includes:

- Rep completion feedback
- Form correction suggestions
- Workout instructions
- Motivation messages


Technology:

- gTTS
- Python Audio Processing
- Voice Pipeline System

---

# 🏗️ System Architecture


```
                Webcam Input
                     |
                     ↓
             OpenCV Processing
                     |
                     ↓
          MediaPipe Pose Detection
                     |
                     ↓
          Body Landmark Extraction
                     |
                     ↓
            Angle Calculation
                     |
                     ↓
          Exercise Detection Engine
                     |
        -------------------------
        |                       |
        ↓                       ↓
 Rep Counter             Form Analysis
        |                       |
        -------------------------
                     |
                     ↓
            AI Voice Feedback
```


---

# 🛠️ Tech Stack


## Programming Language

- Python


## Computer Vision

- OpenCV
- MediaPipe


## AI / ML

- Pose Estimation
- Human Body Landmark Detection
- Movement Analysis


## Web Application

- Streamlit
- Streamlit WebRTC


## Audio System

- gTTS
- pygame


## Data Processing

- NumPy
- Pandas


---

# 📂 Project Structure


```
AI-GYM-TRAINER
│
├── main.py
├── requirements.txt
├── README.md
│
├── core
│   └── base_exercise.py
│
├── detectors
│   ├── squat.py
│   ├── pushup.py
│   ├── biceps_curl.py
│   ├── shoulder_press.py
│   └── lunges.py
│
├── services
│   │
│   ├── coaching
│   │   ├── voice_pipeline.py
│   │   └── tts.py
│   │
│   └── config
│       └── workout_config.py
│
├── models
│   └── pose_landmarker_full.task
│
└── utils
    └── helpers.py

```

---

# ⚙️ Installation & Setup


## 1. Clone Repository

```bash
git clone https://github.com/indrajeet120/AI-GYM-TRAINER.git
```

Navigate into project:

```bash
cd AI-GYM-TRAINER
```


---

## 2. Create Virtual Environment


```bash
python -m venv .venv
```


Activate environment:


### Windows

```bash
.venv\Scripts\activate
```


### Linux / Mac

```bash
source .venv/bin/activate
```


---

## 3. Install Dependencies


```bash
pip install -r requirements.txt
```


---

# ▶️ Run Application


Start Streamlit application:


```bash
streamlit run main.py
```


Open browser:


```
http://localhost:8501
```


---

# 📸 Working Process


### Step 1
User opens webcam.


### Step 2
AI detects body landmarks.


### Step 3
System calculates joint angles.


### Step 4
Exercise movement is identified.


### Step 5
Repetitions are counted.


### Step 6
AI provides voice guidance.


---

# 📐 Pose Angle Calculation


The system uses joint angles for movement detection.


Example:


```
Squat:

Standing Position
Knee Angle > 160°

        ↓

Squat Down
Knee Angle < 100°

        ↓

Rep Completed
```


---

# 🎯 Key Highlights


⭐ Real-time AI workout monitoring  
⭐ Computer vision based exercise tracking  
⭐ Automatic repetition counting  
⭐ Smart posture correction  
⭐ Voice-based fitness guidance  
⭐ Modular detector architecture  


---

# 🚧 Future Improvements


- [ ] User authentication system
- [ ] Workout history dashboard
- [ ] Calories burned estimation
- [ ] AI fitness chatbot
- [ ] Mobile application
- [ ] Cloud deployment
- [ ] Personalized workout plans


---

# 👨‍💻 Developer


## Indrajeet Yadav

B.Tech Electronics Engineering


GitHub:
```
https://github.com/indrajeet120
```


LinkedIn:
```
https://linkedin.com/in/indrajeet-yadav
```


---

# ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub.


---

# 📜 License

This project is developed for educational and research purposes.
