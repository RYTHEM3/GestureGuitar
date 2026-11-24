# 🎸 GestureGuitar

### A Virtual Guitar Controlled by Hand Gestures

GestureGuitar is a Python-based virtual guitar application that allows users to play musical chords using real-time hand gestures captured through a webcam.

Using computer vision and hand landmark detection, the application recognizes finger combinations and converts them into musical chords.

No physical guitar is required!

## ✨ Features

- Real-time hand tracking using MediaPipe.
- Webcam-based finger detection.
- 24 unique major and minor chord combinations.
- Gesture-based chord playback.
- Mouse-based chord selection.
- Continuous sustained chord playback.
- Interactive desktop interface built with PyQt6.
- Built-in finger-to-chord reference guide.
- Synthesized audio using NumPy and Pygame.

## 🎵 Supported Chords

**Major Chords**
- C Major
- C# Major
- D Major
- D# Major
- E Major
- F Major
- F# Major
- G Major
- G# Major
- A Major
- A# Major
- B Major

**Minor Chords**
- C Minor
- C# Minor
- D Minor
- D# Minor
- E Minor
- F Minor
- F# Minor
- G Minor
- G# Minor
- A Minor
- A# Minor
- B Minor

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Webcam access and image processing |
| MediaPipe | Hand landmark detection |
| NumPy | Audio signal generation |
| Pygame | Audio playback |
| PyQt6 | Desktop graphical interface |

## 📁 Project Structure

```text
GestureGuitar/
│
├── assets/
│   └── chords/
│
├── models/
│   └── hand_landmarker.task
│
├── src/
│   ├── main.py
│   ├── audio_engine.py
│   ├── chord_mapping.py
│   ├── chord_gui.py
│   ├── finger_detection.py
│   ├── gesture_recognition.py
│   ├── hand_tracking.py
│   └── test_audio.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project directory

```bash
cd GestureGuitar
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run GestureGuitar

```bash
python src/main.py
```

## 🎮 How to Use

1. Launch the application.
2. Allow webcam access.
3. Select Gesture Control or Mouse Control.
4. In Gesture Control mode, show a supported finger combination to play its corresponding chord.
5. In Mouse Control mode, select any chord from the chord library.
6. Use Stop Audio to stop playback.
7. Open the Finger-Chord Guide to view all 24 finger combinations.

## 🧠 How It Works

GestureGuitar follows this processing pipeline:

```text
Webcam Input
     ↓
Hand Detection
     ↓
Finger Landmark Detection
     ↓
Finger Combination Recognition
     ↓
Chord Mapping
     ↓
Audio Synthesis
     ↓
Continuous Chord Playback
```

MediaPipe identifies hand landmarks, the application determines which fingers are raised or folded, and the resulting combination is mapped to a musical chord.

NumPy generates the audio waveform, while Pygame handles playback.

## 🚀 Future Improvements

- More realistic acoustic guitar sound.
- Improved finger detection and gesture calibration.
- Support for additional instruments.
- Customizable gesture mappings.
- Chord progression and recording features.
- Improved audio transitions.

## 👨‍💻 Author

Developed as a computer vision and audio-processing project.

## 📜 License

License information will be added before public distribution.
```

**Important:** We'll replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL after creating the GitHub repository.

### Step 8 — Confirm

Save `README.md`.

Then run:

```powershell
git status
```

Tell me when it's done.

Next, we'll create your GitHub repository and push GestureGuitar for the first time.