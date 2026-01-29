
import time

from core_logic.state_manager import state_manager_instance
from dashboard.app import start_dashboard
from Voice_control.voice_recognition import start_voice_control
from gesture_control.hand_detection import start_gesture_control
from arduino_control.serial_comm import ArduinoController


arduino = ArduinoController(port="COM7", baud=9600)

def main():
    print("🚀 System starting...")

    state_manager_instance.set_state("IDLE")

    import threading
    threading.Thread(
        target=start_dashboard,
        daemon=True
    ).start()

    start_voice_control(state_manager_instance, arduino)

    start_gesture_control(state_manager_instance, arduino)

    print("✅ System READY")
    print("🎤 Say: start scan | stop scan | emergency")
    print("✋ Use gestures to control the system")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")

if __name__ == "__main__":
    main()