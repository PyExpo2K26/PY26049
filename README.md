# Safety Monitoring & Control System

A next-generation industrial control interface that combines **Computer Vision**, **Voice Recognition**, and a **Web Dashboard** into a unified safety system.

![Dashboard Preview](dashboard_preview.png)
*(Note: Run the system to see the live dashboard)*

## 🚀 Features

- **Multi-Modal Control**:
  - **Gesture**: Control the system using hand signs (Open Hand to Start, Fist to Stop).
  - **Voice**: Speak commands like "Start Scan", "Emergency", or ask "Status".
  - **Web**: Manual buttons and text command input via a modern dashboard.
- **Face Verification**: System operations are locked if an authorized operator (detected face) is not present.
- **Real-Time Dashboard**: Monochromatic "Sci-Fi" style UI showing live camera feed, system logs, and hardware status.
- **Emergency Protocols**: Dedicated gesture/voice commands to trigger an immediate system halt.

## 🛠️ Installation

1. **Prerequisites**:
   - Python 3.9+
   - A Webcam
   - A Microphone
   - (Optional) Arduino connected via USB for hardware control.

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Key libraries: `flask`, `opencv-python`, `mediapipe`, `speechrecognition`, `pyaudio`.*

## ▶️ How to Run

1. **Start the Application**:
   ```bash
   python main.py
   ```
2. **Access the Dashboard**:
   - Open your browser and navigate to: `http://127.0.0.1:5000`

## 🎮 Controls

### 1. Gesture Control
Ensure you are visible to the camera.
- **Start Scan**: ✋ Open Hand (All fingers extended)
- **Stop**: ✊ Fist (Closed hand)
- **Complete Task**: ✌️ Peace Sign
- **Emergency Stop**: 👍 Thumbs Up

### 2. Voice Commands
The system listens continuously. Speak clearly.
- **"Start Scan"**
- **"Stop Scan"**
- **"Emergency"** / **"Emergency Stop"**
- **"Reset"**
- **"Status"** / **"Report"** (To get current state)
- **"Why is it stopped?"** (Context-aware query)

### 3. Dashboard (Manual Override)
- **Buttons**: Click START, STOP, RESET, EMERGENCY, or COMPLETE on the right panel.
- **Command Input**: Type commands (e.g., "start", "why stuck") in the bottom-left text box and press Enter.

## ⚠️ Troubleshooting

**"Access Denied - No Face"**
- The system requires a face to be detected in the camera frame to operate. Stand in front of the camera.

**"Manual Buttons check logs"**
- If buttons don't work, check the Python console for `DEBUG` messages. Ensure no JavaScript blockers are running.

**"Arduino Connection Failed"**
- The system will automatically switch to **Dummy Mode** if no Arduino is found on `COM7`. This is normal for testing without hardware.

## 📂 Project Structure

Please refer to [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed breakdown of the internal logic and data flow.
