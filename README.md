# SynchroForge – Robotic Control System

Welcome to the **SynchroForge Robotic Control System**, a custom-built web interface designed to pilot a magnetic crawler robot via an ESP32-CAM module.

This project uses a lightweight Python Flask backend to proxy video streams and command routes, providing a seamless, real-time control interface over an aesthetically pleasing, responsive web dashboard.

## 🚀 Features

*   **Modern SynchroForge Frontend**: A beautiful gradient-styled landing page combining futuristic aesthetics and sleek typography (`Orbitron` & `Share Tech Mono`).
*   **Live MJPEG Stream Proxy**: View the ESP32-CAM feed in real-time directly on the dashboard without hitting browser CORS or mixed-content blockers.
*   **Real-Time Dashboard Controls**: Control directional movements (Forward, Backward, Left, Right) and trigger the emergency stop.
*   **Keyboard Support**: Drive the robot naturally using `WASD` or Arrow Keys.
*   **Admin Panel**: A dedicated `/admin` configuration page that polls actual system health. Monitor ESP32 reachability and configure the robot's IP on the fly.
*   **High-Contrast UI**: Crisp blue-white global UI combined with a high-visibility, dark navy aesthetic for the central control panel.

---

## 📂 Architecture Overview

```text
code/
├── app.py                  # Core Flask server mapping routes and proxying ESP32 endpoints
├── esp32/                  # Firmware for the ESP32 controller
│   └── esp32cam_stream_motor.ino
├── static/
│   └── style.css           # Global custom styles (Blue-White and Dark-Navy themes)
└── templates/
    ├── admin.html          # Dynamic admin panel showing status/uptime and IP configuration
    ├── index.html          # Main Control Dashboard (camera feed + D-Pad)
    └── landing.html        # SynchroForge hero splash page
```

---

## 🛠️ Prerequisites

*   **Python 3.8+**
*   **Flask** (`pip install flask`)
*   **Requests** (`pip install requests`)
*   An **ESP32-CAM** connected to the same local network as the host machine running this Flask app.

> **Note on Hardware:** The ESP32-CAM must be running firmware that exposes `/stream` (MJPEG video feed) and the directional control routes (`/forward`, `/backward`, `/left`, `/right`, `/stop`).

---

## 🏃 Getting Started

### 1. Run the Flask Server
Navigate to the root directory and start the proxy server:

```bash
cd robot-dashboard
python app.py
```

*By default, the server runs on `http://0.0.0.0:5000`.*

### 2. Configure the Robot IP Address
1. Check your Arduino Serial Monitor when the ESP32-CAM boots up to find its local IP address (e.g., `192.168.1.100`).
2. Open your web browser and go to the Admin Panel: `http://localhost:5000/admin`
3. Enter the ESP32 IP address into the configuration form and click **SAVE IP**.
4. *Alternatively, you can hardcode this IP via the `ESP32_IP` variable inside `app.py`.*

### 3. Drive the Robot
Navigate to the Control Dashboard:
`http://localhost:5000/dashboard`

You should see the live camera feed labeled `CAM-01`.
Click the interactive D-Pad commands or press `WASD`/Arrow keys on your keyboard to navigate the crawler.

---

## 📡 API Reference

When commands are issued in the dashboard, the following proxy endpoints on Flask are triggered. Flask then relays these to the physical ESP32.

*   **System Endpoints**
    *   `/api/admin/status` — Returns overall system health (Flask uptime, ESP32 reachability, camera signal).
    *   `/config` (POST) — Dynamically sets the `ESP32_IP`.

*   **Movement Proxy**
    *   `/control/forward` or `/forward`
    *   `/control/backward` or `/backward`
    *   `/control/left` or `/left`
    *   `/control/right` or `/right`
    *   `/control/stop` or `/stop`

*   **Camera Proxy**
    *   `/camera/stream` — Continuous MJPEG relay.
    *   `/camera/capture` — Grabs a single JPEG frame.

---

## 🎨 Theme Details
*   **Backgrounds**: `var(--bg)` -> `#f0f6ff` (Ice Blue)
*   **Accents**: `--primary` -> `#1a56db` (SynchroForge Blue)
*   **Dashboard Control Pad**: `#0f1520` (Dark Navy for maximum visibility)

***
> Built for Team SynchroForge. Powered by Python Flask and ESP32 architecture.
