from flask import Flask, render_template, jsonify
from core_logic.state_manager import state_manager_instance

app = Flask(__name__)

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
        return "EMERGENCY", "⚠ Emergency stop activated!"

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
        "message": message
    })

@app.route("/reset", methods=["POST"])
def reset_system():
    state_manager_instance.set_state("IDLE")
    return jsonify({"status": "reset done"})

def start_dashboard():
    app.run(debug=False, use_reloader=False)