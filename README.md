# Radiology Voice & Gesture Control System

## Overview
This work is a Python tool that lets you use your voice and your hands to make choices while using radiology machines. It is built to help stop people from making small or big mistakes when they use these tools.  
This tool shows how you can use no hands, just your voice or moves, to do your work more safe and clear. This helps with hard jobs where being safe matters a lot.

⚠️ **Note:** This project is a prototype developed for academic and demonstration purposes only.  
It is **not intended for direct clinical or hospital deployment**.

---

## 🎯 Problem Statement
Radiology equipment operation involves repetitive and safety-critical actions.  

Human errors such as incorrect command sequencing, delayed emergency response, or operator distraction can lead to unsafe situations.

This project focuses on:
- Reducing human error through **state-based command validation**

- Preventing unsafe operations by **blocking invalid commands**

- Improving operator workflow using **hands-free interaction**

---

## 🧠 Core Idea
All system interactions—whether voice or gesture—are processed through a **centralized state machine**.  
Commands are executed **only if they are valid for the current system state**.

This ensures:
- Predictable system behavior

- Emergency actions always have priority

- Accidental or unsafe commands are ignored

---

## 🏗 System Architecture
Voice Input ┐

├──> Command Validator ──> State Manager ──> Arduino (LEDs)

Gesture Input ┘ │

Dashboard


- Input modules do **not** directly control hardware 

- The validator enforces safety rules  

- Hardware acts only as an execution layer  

---

## 🧩 Module Description

### 1️⃣ Voice Control (`voice_control/`)

- Uses Python `SpeechRecognition`

- Converts speech to predefined command keywords

- Sends commands to the central validator

- Voice input never directly controls hardware

### 2️⃣ Gesture Control (`gesture_control/`)

- Uses OpenCV and MediaPipe for hand detection

- Recognizes simple hand gestures

- Maps gestures to system commands

- Emergency gestures have highest priority

### 3️⃣ Core Logic (`core_logic/`)

- Central state manager

- Validates all commands

- Blocks invalid or unsafe transitions

- Ensures consistent system behavior

### 4️⃣ Dashboard (`dashboard/`)

- Built using Flask

- Displays real-time system state

- Provides clear visual feedback

- Allows manual reset after emergency state

### 5️⃣ Arduino Control (`arduino_control/`)

- Represents the hardware execution layer

- Receives serial commands from Python

- Uses LEDs to simulate system states

---

## 🔌 Hardware Indicators

| LED Color | Meaning |
|---------|--------|
| 🟢 Green | Scanning |
| 🟡 Yellow | Completed / Stopped |
| 🔴 Red | Emergency |

---

## 🛠 Technologies Used

- Python

- SpeechRecognition

- OpenCV

- MediaPipe

- Flask

- Arduino (Serial Communication)

---

## ▶️ How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
