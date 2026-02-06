INIT = "INIT"
IDLE = "IDLE"
INITIALIZING = "INITIALIZING"
SCANNING = "SCANNING"
COMPLETED = "COMPLETED"
STOPPING = "STOPPING"
STOPPED = "STOPPED"
EMERGENCY = "EMERGENCY"


class StateManager:
    """
    Central authority for managing system state.
    All modules (voice, gesture, dashboard, hardware)
    must read/update state ONLY through this class.
    """

    def __init__(self):
        self._state = INIT
        self._face_detected = False

    def set_face_detected(self, detected: bool):
        self._face_detected = detected

    def is_face_detected(self):
        return self._face_detected

    def get_state(self):
        return self._state

    def set_state(self, new_state):
        valid_states = [
            INIT,
            IDLE,
            INITIALIZING,
            SCANNING,
            COMPLETED,
            STOPPING,
            STOPPED,
            EMERGENCY
        ]

        if new_state in valid_states:
            self._state = new_state
            return True
        return False

    def reset(self):
        self._state = IDLE
state_manager_instance = StateManager()