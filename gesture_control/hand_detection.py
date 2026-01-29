
from core_logic.command_validator import RESET
import cv2
import mediapipe as mp
import threading
import time

from core_logic.command_validator import (
    START_SCAN,
    STOP_SCAN,
    SCAN_COMPLETE,
    EMERGENCY_STOP,
    validate_and_process
)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils



def get_finger_states(hand):
    """
    Returns a list of booleans: True if finger is extended, False if folded.
    [Thumb, Index, Middle, Ring, Pinky]
    Using geometric heuristics for better accuracy.
    """
    cnt = 0
    fingers = []
    
    if hand.landmark[4].x < hand.landmark[3].x: 
        fingers.append(True)
    else:
        fingers.append(False)

    
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18] 
    
    for tip, pip in zip(tips, pips):
        if hand.landmark[tip].y < hand.landmark[pip].y:
            fingers.append(True)
        else:
            fingers.append(False)
            
    return fingers



def get_gesture_refined(fingers):
    """
    fingers: [Thumb, Index, Middle, Ring, Pinky]
    """

    count = fingers.count(True)
    
    if count == 5:
        return START_SCAN, "OPEN HAND (Start)"

 
    if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
        return SCAN_COMPLETE, "PEACE SIGN (Complete)"

    if fingers[0] and not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
        return EMERGENCY_STOP, "THUMB UP (Emergency)"


    if count == 0:
        return STOP_SCAN, "FIST (Stop)"

    return None, "UNKNOWN"



def start_gesture_control(state_manager, arduino):

    def run():
       

        print("⏳ Warming up gesture system...")
        time.sleep(3) 
        print("✅ Gesture system ready")
        print("✋ Gesture control started")

        reset_hold_start = None
        RESET_HOLD_TIME = 2  
        cap = cv2.VideoCapture(0)

        last_time = 0
        COOLDOWN = 2  
        
        current_gesture_name = "NONE"

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            command = None
            current_gesture_name = "NONE"

            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(
                    frame, hand, mp_hands.HAND_CONNECTIONS
                )

            
                fingers = get_finger_states(hand)
                command, current_gesture_name = get_gesture_refined(fingers)

            if command == SCAN_COMPLETE:
                if state_manager.get_state() == "EMERGENCY":
                    if reset_hold_start is None:
                        reset_hold_start = time.time()
                        print(f"🕒 Hold reset... {RESET_HOLD_TIME - (time.time() - reset_hold_start):.1f}s")
                    elif time.time() - reset_hold_start >= RESET_HOLD_TIME:
                        command = RESET
                        current_gesture_name = "RESET TRIGGERED"
                        reset_hold_start = None
                else:
                    reset_hold_start = None
            else:
                reset_hold_start = None

            if command:
                current_state = state_manager.get_state()

 
                if command == EMERGENCY_STOP and current_state != "SCANNING":
                    pass 
                    if current_state != "SCANNING":
                         command = None 

                if command == STOP_SCAN and current_state == "EMERGENCY":
                    command = None


            now = time.time()
            if command and (command == RESET or (now - last_time) > COOLDOWN):
                response = validate_and_process(
                    command,
                    state_manager.get_state()
                )

                state_manager.set_state(response["next_state"])

                if response["arduino_command"]:
                    arduino.send(response["arduino_command"])

                print(f"[GESTURE] {command} → {response['message']}")
                last_time = now

            
            cv2.putText(
                frame,
                f"STATE: {state_manager.get_state()}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
        
            color = (0, 255, 255) if command else (200, 200, 200)
            cv2.putText(
                frame,
                f"GESTURE: {current_gesture_name}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )


            cv2.imshow("Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=run, daemon=True).start()
