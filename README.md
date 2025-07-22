# 🎯 Good Guy, Bad Guy Detector

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-RealTime-red)
![MediaPipe](https://img.shields.io/badge/Mediapipe-Hand%20%26%20Face%20Mesh-orange)
![License](https://img.shields.io/badge/license-MIT-green)

> 🧠 Real-time AI-powered sniper vision that locks onto your forehead if you get detected as bad guy.
> A terrifyingly fun project using OpenCV + MediaPipe

---

## 🧠 How It Works

Detects your hand gestures and checks if only the middle finger is getting shown.

Finds forehead and locks the target.

If you show middle finger - Boom You are targeted.

UI shows text like "Bad Guy Detected"

---

## 🧩 Features

- 🖐️ Detects **middle finger gesture** using MediaPipe Hands
- 😳 Tracks **forehead position** with Face Mesh landmarks
- 🎯 Animated **crosshair UI** locks onto hostile targets
- 🧟‍♂️ Switches between *"Good Guy"* and *"Bad Guy Detected"*

---

## 🚀 Getting Started

### 1. Clone this Repo

```bash
git clone https://github.com/izharashiq/GoodGuy-BadGuy-Detector.git
```

```bash
cd GoodGuy-BadGuy-Detector
```

### 2. Install Dependencies
Install required packages using requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Run the program

```bash
python Detector.py
```
Then point your webcam at yourself and raise that middle finger (for science 👀).


*✨ Made by @IzharAshiq – Because why just wave, when you can target? 😎*