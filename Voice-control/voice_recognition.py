import speech_recognition as sr
import threading
from difflib import SequenceMatcher
from core_logic.command_validator import RESET
from core_logic.log_shared import log_shared_instance


from core_logic.command_validator import (
    validate_and_process,
    START_SCAN,
    STOP_SCAN,
    EMERGENCY_STOP
)


def start_voice_control(state_manager, arduino):
    """
    Starts voice recognition in a background thread.
    Voice → Command Validator → State Manager → Arduino
    """

    def listen():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("🎤 Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)

        print("🎤 Voice control started")
        print("Say: start scan | stop scan | emergency")

        SIMILARITY_THRESHOLD = 0.8

        def is_similar(input_text, target_cmd):
             return SequenceMatcher(None, input_text, target_cmd).ratio() > SIMILARITY_THRESHOLD

        while True:
            try:
                log_shared_instance.update_transcript("", "listening")
                print("👂 Listening...")
                with mic as source:
                    audio = recognizer.listen(
                        source, timeout=3, phrase_time_limit=3
                    )

                log_shared_instance.update_transcript("", "processing")
                print("🧠 Processing audio...")
                text = recognizer.recognize_google(audio).lower()
                print(f"[VOICE HEARD]: '{text}'")
                
                # Update live transcript and log the recognized speech
                log_shared_instance.update_transcript(f'"{text}"', "text")
                log_shared_instance.add_log("[VOICE]", f"Heard: \"{text}\"", "info")

                command = None
                
                if is_similar(text, "start scan") or "start scan" in text or "scanning" in text:
                    command = START_SCAN
                elif is_similar(text, "stop scan") or "stop scan" in text:
                    command = STOP_SCAN

                elif "reset" in text or "clear emergency" in text:
                    command = RESET
                elif "emergency" in text or is_similar(text, "emergency stop"):
                    command = EMERGENCY_STOP

                # --- New Status/Query Logic ---
                elif "why" in text and ("stopped" in text or "not working" in text):
                    # Check for face detection issue first
                    if not state_manager.is_face_detected():
                        response = "Face is not detected. Please stand in front of the camera."
                        log_shared_instance.add_log("[SYSTEM]", response, "warn")
                        print(f"🤖 REPLY: {response}")
                    
                    # Check if system is explicitly stopped/idle
                    elif state_manager.get_state() in ["IDLE", "STOPPED", "EMERGENCY"]:
                        state = state_manager.get_state()
                        response = f"System is currently {state}. Say 'Start Scan' to begin."
                        log_shared_instance.add_log("[SYSTEM]", response, "info")
                        print(f"🤖 REPLY: {response}")
                    
                    else:
                        response = f"System is in {state_manager.get_state()} mode."
                        log_shared_instance.add_log("[SYSTEM]", response, "info")
                        print(f"🤖 REPLY: {response}")
                    
                    continue # Skip command processing for queries

                elif "status" in text or "report" in text:
                    state = state_manager.get_state()
                    face = "Detected" if state_manager.is_face_detected() else "Not Detected"
                    response = f"System State: {state} | Face: {face}"
                    log_shared_instance.add_log("[SYSTEM]", response, "info")
                    print(f"🤖 REPLY: {response}")
                    continue
                # ------------------------------

                if not command:
                    print("⚠️ No valid command detected")
                    log_shared_instance.add_log("[VOICE]", "Command not recognized", "warn")
                    continue

                print("STATE BEFORE:", state_manager.get_state())


                result = validate_and_process(
                    command, state_manager.get_state()
                )

                state_manager.set_state(result["next_state"])

                print("STATE AFTER:", state_manager.get_state())

                if result["arduino_command"]:
                    arduino.send(result["arduino_command"])

                print("✅", result["message"])
                log_shared_instance.add_log("[VOICE]", f"Command: {command} - {result['message']}", "success")
                print("-" * 30)

            except Exception as e:
                print("Voice error:", e)

    threading.Thread(target=listen, daemon=True).start()