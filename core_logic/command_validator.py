
from core_logic.state_manager import (
    INIT,
    IDLE,
    INITIALIZING,
    SCANNING,
    COMPLETED,
    STOPPING,
    EMERGENCY
)

START_SCAN = "START_SCAN"
STOP_SCAN = "STOP_SCAN"
SCAN_COMPLETE = "SCAN_COMPLETE"
EMERGENCY_STOP = "EMERGENCY_STOP"
RESET = "RESET"

RESET_SYSTEM = "RESET_SYSTEM"

VALID_COMMANDS = [
    START_SCAN,
    STOP_SCAN,
    SCAN_COMPLETE,
    EMERGENCY_STOP,
    RESET,
    RESET_SYSTEM
]


def validate_and_process(command, current_state):
    """
    Validates commands and decides:
    - next state
    - hardware command
    - system message
    """

    if command not in VALID_COMMANDS:
        return {
            "next_state": current_state,
            "arduino_command": None,
            "message": "Invalid command"
        }

   
    if command == EMERGENCY_STOP:
        return {
            "next_state": EMERGENCY,
            "arduino_command": "EMERGENCY_STOP",
            "message": "Emergency stop activated"
        }

    if command == RESET:
        if current_state == "EMERGENCY":
            return {
                "next_state": "IDLE",
                "arduino_command": "RESET",
                "message": "System reset from emergency"
            }
        else:
            return {
                "next_state": current_state,
                "arduino_command": None,
                "message": "Reset not allowed"
            }

    if command == RESET_SYSTEM:
        if current_state == EMERGENCY:
            return {
                "next_state": IDLE,
                "arduino_command": "RESET",
                "message": "System reset from emergency"
            }
        else:
            return {
                "next_state": current_state,
                "arduino_command": None,
                "message": "Reset not required"
            }

    if command == RESET_SYSTEM:
        return {
            "next_state": IDLE,
            "arduino_command": "RESET",
            "message": "System reset to IDLE"
        }

 
    if command == START_SCAN and current_state == IDLE:
        return {
            "next_state": INITIALIZING,
            "arduino_command": "INITIALIZE_SYSTEM",
            "message": "Initializing scan system"
        }

    if current_state == INITIALIZING and command == START_SCAN:
        return {
            "next_state": SCANNING,
            "arduino_command": "START_SCAN",
            "message": "Scan started"
        }

    
    if command == SCAN_COMPLETE and current_state == SCANNING:
        return {
            "next_state": COMPLETED,
            "arduino_command": "SCAN_COMPLETED",
            "message": "Scan completed successfully"
        }

    if command == STOP_SCAN and current_state == SCANNING:
        return {
            "next_state": STOPPING,
            "arduino_command": "STOP_SCAN",
            "message": "Stopping scan safely"
        }

    if current_state == STOPPING:
        return {
            "next_state": IDLE,
            "arduino_command": None,
            "message": "System safely stopped"
        }

    
    return {
        "next_state": current_state,
        "arduino_command": None,
        "message": "Command not allowed in current state"
    }