import serial
import time

class ArduinoController:
    def __init__(self, port="COM7", baud=9600):
        self.port = port
        self.baud = baud
        self.connection = None
        self.is_connected = False
        
        self.connect()

    def connect(self):
        print(f"🔌 Connecting to Arduino at {self.port}...")
        try:
            self.connection = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2) 
            self.is_connected = True
            print("✅ Arduino Connected!")
        except Exception as e:
            print(f"⚠️ Arduino connection failed: {e}")
            print("⚠️ Running in DUMMY MODE (Simulation)")
            self.is_connected = False

    def send(self, command):
        if self.is_connected and self.connection:
            try:
               
                full_cmd = command.strip() + "\n"
                self.connection.write(full_cmd.encode())
                print(f"[ARDUINO] Sent: {command}")
            except Exception as e:
                print(f"❌ Error sending to Arduino: {e}")
                self.is_connected = False # Assume disconnected on error
        else:
            print(f"[DUMMY ARDUINO] (Simulated) Sent: {command}")

    def send_scan_start(self):
        self.send("START_SCAN")

    def send_scan_completed(self):
        self.send("SCAN_COMPLETED")

    def send_emergency(self):
        self.send("EMERGENCY_STOP")
         
    def send_reset(self):
        self.send("RESET")

    def close(self):
        if self.connection:
            self.connection.close()
            print("🔌 Arduino connection closed.")