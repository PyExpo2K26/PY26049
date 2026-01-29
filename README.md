# Multimodal Voice & Gesture Controlled Radiology System

INTRODUCTION

Radiology and medical imaging devices involve exposure to ionizing radiation, which can pose serious health risks to radiology technicians during prolonged operation. To improve safety and reduce radiation exposure, this project presents a multimodal voice-command and hand-gesture controlled system that enables technicians to operate radiology equipment remotely from outside high-radiation zones.
In this system, voice commands and hand gestures are processed using Python, and the corresponding control signals are transmitted to an Arudino Uno microcontroller, which executes the required actions. This approach enhances safety, efficiency, and hands-free operation without direct physical interaction with the equipment.

STRATEGIC INTENT:

a. Reduce radiation exposure to radiology technicians.

b. Enable remote, hands-free control of imaging equipment.

c. Improve safety and workflow efficiency in hazardous environments.

LOGIC FLOW:

Voice commands are captured using a microphone.

Hand gestures are detected using a camera.

Audio and visual inputs are processed using Python.

Interpreted commands are sent to the Arduino Uno via serial communication.

The Arudino Uno executes the corresponding control actions using connected outputs.

ACTION ITEMS

1.HARDWARE:

a.1 × Arudino Uno Board

b.USB Cable (USB-A to Type-B)

c.Computer/Laptop with microphone and camera

d.(Optional) Relay module / LEDs / actuators for demonstrating control actions

2.SOFTWARE:

a.Python 3.x

b.Arudino IDE

c.Python Libraries Used:

d.Speech Recognition

e.OpenCV

f.MediaPipe

g.NumPy

EXECUTION METHODOLOGY:

a. Capture voice commands using a microphone.

b. Detect and track hand gestures using a camera.

c. Process voice and gesture inputs in Python.

d. Convert recognized commands into predefined control signals.

e. Transmit commands to the Arduino Uno via serial communication.

f. Execute control actions through Arduino digital/analog outputs.

INTERFACE & APPLICATION AREAS:

a.Radiology and medical imaging rooms

b.Hands-free and contactless equipment control

c.Operation in hazardous or high-radiation environments

d.Demonstration platforms for medical automation systems

CONCLUSION

This project demonstrates a simple, cost-effective, and reliable solution for operating radiology machines using voice commands and hand gestures with an Arudino Uno microcontroller. By minimizing direct human presence in radiation-prone areas, the system significantly reduces health risks while improving operational efficiency and safety. The system can be further enhanced for real-world medical automation and smart healthcare applications.