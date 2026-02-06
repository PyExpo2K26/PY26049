import threading
from datetime import datetime
from collections import deque

class LogShared:
    """
    Shared log buffer for thread-safe logging from multiple sources
    (voice recognition, gestures, system events) to the dashboard.
    """
    def __init__(self, max_logs=100):
        self.logs = deque(maxlen=max_logs)
        self.lock = threading.Lock()
        self.current_transcript = "👂 Listening..."
        self.transcript_lock = threading.Lock()

    def add_log(self, tag, message, log_type="info"):
        """
        Add a log entry.
        
        Args:
            tag: Log tag like "[VOICE]", "[GESTURE]", "[SYSTEM]"
            message: Log message text
            log_type: Type for styling: "info", "success", "warn", "error", "system"
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_entry = {
            "timestamp": timestamp,
            "tag": tag,
            "message": message,
            "type": log_type
        }
        
        with self.lock:
            self.logs.append(log_entry)

    def get_recent_logs(self, count=50):
        """Get the most recent log entries."""
        with self.lock:
            return list(self.logs)[-count:]

    def update_transcript(self, text, status="text"):
        """
        Update the current voice transcript.
        
        Args:
            text: The transcript text
            status: Status type - "listening", "processing", "text"
        """
        with self.transcript_lock:
            if status == "listening":
                self.current_transcript = "👂 Listening..."
            elif status == "processing":
                self.current_transcript = "🧠 Processing audio..."
            else:
                self.current_transcript = text

    def get_transcript(self):
        """Get the current voice transcript."""
        with self.transcript_lock:
            return self.current_transcript


# Global shared instance
log_shared_instance = LogShared()