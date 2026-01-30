# Radiology Voice & Gesture Control System

## 🎯 PROBLEM STATEMENT
Radiology equipment operation involves repetitive and safety-critical actions.  
Human errors such as incorrect command sequencing, delayed emergency response, or operator distraction can lead to unsafe situations during operation.

Conventional control methods require constant manual interaction, which increases the chance of mistakes, especially in high-pressure environments.  
Therefore, there is a need for a safer and more controlled interaction method that can help reduce human error.

---

## 💡 PROPOSED SOLUTION
The proposed system provides a **voice- and hand-gesture-based control interface** for radiology equipment operations.

Key aspects of the solution:
- Voice and gesture inputs are used as **hands-free command methods**
- All commands pass through a **central state validation logic**
- Commands are executed **only if they are valid for the current system state**
- Emergency actions are given **highest priority**
- System status is displayed using a **dashboard and hardware indicators**

This design helps reduce human error by preventing unsafe or illogical operations and ensuring predictable system behavior.

---

## 🛠 Materials / Tools Used

### Software Tools
- Python  
- SpeechRecognition (voice input)  
- OpenCV (camera input)  
- MediaPipe (hand gesture detection)  
- Flask (dashboard)  
- PySerial (Arduino communication)  

### Hardware Components
- Arduino Uno  
- Breadboard  
- LEDs (Green, Yellow, Red)  
- Resistors (220Ω)  
- USB cable  

### Input Devices
- Microphone / Headset  
- Web Camera  

---
