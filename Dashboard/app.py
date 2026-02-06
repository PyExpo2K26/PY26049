from flask import Flask, render_template, jsonify, Response
from core_logic.camera_shared import camera_shared_instance
from core_logic.log_shared import log_shared_instance
import cv2
import time
from core_logic.state_manager import state_manager_instance
from core_logic.command_validator import (
    validate_and_process,
    START_SCAN,
    STOP_SCAN,
    EMERGENCY_STOP,
    RESET,
    SCAN_COMPLETE
)
from flask import request
from difflib import SequenceMatcher

app = Flask(__name__)
arduino_instance = None

def set_arduino(arduino):
    global arduino_instance
    arduino_instance = arduino

def map_state(state):
    if state == "IDLE":
        return "READY", "System ready. Waiting for command."
    if state == "INITIALIZING":
        return "STARTING", "Initializing scan system..."
    if state == "SCANNING":
        return "SCANNING", "Scan in progress. Please remain still."
    if state == "STOPPING":
        return "STOPPING", "Stopping scan safely..."
    if state == "COMPLETED":
        return "COMPLETED", "Scan completed successfully."
    if state == "EMERGENCY":
        return "EMERGENCY", "⚠ EMERGENCY STOP ACTIVE"
    if state == "STOPPED":
        return "STOPPED", "System Halted."

    return "UNKNOWN", "Unknown state"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    current_state = state_manager_instance.get_state()
    mode, message = map_state(current_state)
    return jsonify({
        "mode": mode,
        "message": message,
        "face_detected": state_manager_instance.is_face_detected()
    })

@app.route("/logs")
def get_logs():
    """Return recent log entries for the dashboard."""
    logs = log_shared_instance.get_recent_logs(50)
    return jsonify({"logs": logs})

@app.route("/transcript")
def get_transcript():
    """Return current voice transcript."""
    transcript = log_shared_instance.get_transcript()
    return jsonify({"transcript": transcript})

@app.route("/reset", methods=["POST"])
def reset_system():
    print("DEBUG: /reset called")
    cmd = RESET
    result = validate_and_process(cmd, state_manager_instance.get_state())
    state_manager_instance.set_state(result["next_state"])
    if result["arduino_command"] and arduino_instance:
        arduino_instance.send(result["arduino_command"])

    log_shared_instance.add_log("[MANUAL]", f"Reset: {result['message']}", "info")
    return jsonify({"status": "reset done", "new_state": result["next_state"]})

@app.route("/start", methods=["POST"])
def start_system():
    print("DEBUG: /start called")
    cmd = START_SCAN
    result = validate_and_process(cmd, state_manager_instance.get_state())
    
    if result["next_state"] != state_manager_instance.get_state():
        state_manager_instance.set_state(result["next_state"])
        if result["arduino_command"] and arduino_instance:
            arduino_instance.send(result["arduino_command"])
        log_shared_instance.add_log("[MANUAL]", f"Start: {result['message']}", "success")
        return jsonify({"status": "started", "new_state": result["next_state"]})
        
    return jsonify({"status": "ignored", "message": result["message"]})

@app.route("/stop", methods=["POST"])
def stop_system():
    print("DEBUG: /stop called")
    cmd = STOP_SCAN
    result = validate_and_process(cmd, state_manager_instance.get_state())
    state_manager_instance.set_state(result["next_state"])
    if result["arduino_command"] and arduino_instance:
        arduino_instance.send(result["arduino_command"])
    
    log_shared_instance.add_log("[MANUAL]", f"Stop: {result['message']}", "warn")
    return jsonify({"status": "stopping", "new_state": result["next_state"]})

@app.route("/emergency", methods=["POST"])
def emergency_stop():
    print("DEBUG: /emergency called")
    cmd = EMERGENCY_STOP
    result = validate_and_process(cmd, state_manager_instance.get_state())
    state_manager_instance.set_state(result["next_state"])
    if result["arduino_command"] and arduino_instance:
        arduino_instance.send(result["arduino_command"])
    
    log_shared_instance.add_log("[MANUAL]", f"Emergency: {result['message']}", "error")
    return jsonify({"status": "emergency", "new_state": result["next_state"]})

@app.route("/complete", methods=["POST"])
def complete_scan():
    print("DEBUG: /complete called")
    cmd = SCAN_COMPLETE
    result = validate_and_process(cmd, state_manager_instance.get_state())
    state_manager_instance.set_state(result["next_state"])
    if result["arduino_command"] and arduino_instance:
        arduino_instance.send(result["arduino_command"])
    
    log_shared_instance.add_log("[MANUAL]", f"Complete: {result['message']}", "success")
    return jsonify({"status": "completed", "new_state": result["next_state"]})

@app.route("/execute_command", methods=["POST"])
def execute_command_route():
    data = request.json
    text = data.get("command", "").lower()
    
    response_text = "Command not recognized"
    command = None
    
    # Query Logic matching Voice Recognition
    if "why" in text and ("stopped" in text or "not working" in text):
        if not state_manager_instance.is_face_detected():
            response_text = "Face is not detected. Please stand in front of the camera."
        elif state_manager_instance.get_state() in ["IDLE", "STOPPED", "EMERGENCY"]:
             response_text = f"System is currently {state_manager_instance.get_state()}. Say 'Start Scan' to begin."
        else:
             response_text = f"System is in {state_manager_instance.get_state()} mode."
        
        log_shared_instance.add_log("[BOT]", response_text, "info")
        return jsonify({"status": "query", "response": response_text})

    if "status" in text or "report" in text:
        state = state_manager_instance.get_state()
        face = "Detected" if state_manager_instance.is_face_detected() else "Not Detected"
        response_text = f"System State: {state} | Face: {face}"
        log_shared_instance.add_log("[BOT]", response_text, "info")
        return jsonify({"status": "query", "response": response_text})
        
    # Command Logic
    SIMILARITY_THRESHOLD = 0.8
    def is_similar(a, b): return SequenceMatcher(None, a, b).ratio() > SIMILARITY_THRESHOLD

    if is_similar(text, "start scan") or "start scan" in text:
        command = START_SCAN
    elif is_similar(text, "stop scan") or "stop scan" in text:
        command = STOP_SCAN
    elif "reset" in text:
        command = RESET
    elif "emergency" in text:
        command = EMERGENCY_STOP

    if command:
        result = validate_and_process(command, state_manager_instance.get_state())
        state_manager_instance.set_state(result["next_state"])
        
        if result["arduino_command"] and arduino_instance:
            arduino_instance.send(result["arduino_command"])
            
        log_shared_instance.add_log("[CMD]", f"Executed: {command}", "success")
        return jsonify({"status": "executed", "response": result["message"]})

    log_shared_instance.add_log("[CMD]", f"Unknown: {text}", "warn")
    return jsonify({"status": "unknown", "response": "Unknown command"})

def gen_frames():
    while True:
        frame = camera_shared_instance.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
            
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_dashboard():
    app.run(debug=False, use_reloader=False)