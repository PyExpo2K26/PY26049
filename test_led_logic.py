
import sys
import os
import time


sys.path.append(os.getcwd())

from core_logic.state_manager import StateManager
from arudino_control.serial_comm import ArduinoController
from core_logic.command_validator import validate_and_process, START_SCAN, SCAN_COMPLETE, EMERGENCY_STOP, RESET


class MockSerial:
    def __init__(self):
        self.last_write = None
    
    def write(self, data):
        self.last_write = data.decode().strip()
    
    def close(self):
        pass

def test_logic():
    print("🧪 Starting LED Logic Test...")
    
 
    state_manager = StateManager()
    state_manager.set_state("IDLE")
    
    arduino = ArduinoController()

    arduino.connection = MockSerial()
    arduino.is_connected = True
    

    print("\n👉 Test 1: Start Scan (IDLE -> INITIALIZING)")
    res = validate_and_process(START_SCAN, state_manager.get_state())
    state_manager.set_state(res["next_state"])
    if res["arduino_command"]:
        arduino.send(res["arduino_command"])
    
    expected_cmd = "INITIALIZE_SYSTEM"
    actual_cmd = arduino.connection.last_write
    print(f"   State: {state_manager.get_state()}")
    print(f"   Command Sent: {actual_cmd}")
    if actual_cmd == expected_cmd:
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL (Expected {expected_cmd})")
        
 
    print("\n👉 Test 2: Confirm Start (INITIALIZING -> SCANNING)")
    res = validate_and_process(START_SCAN, state_manager.get_state())
    state_manager.set_state(res["next_state"])
    if res["arduino_command"]:
        arduino.send(res["arduino_command"])
        
    expected_cmd = "START_SCAN"
    actual_cmd = arduino.connection.last_write
    print(f"   State: {state_manager.get_state()}")
    print(f"   Command Sent: {actual_cmd}")
    if actual_cmd == expected_cmd:
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL (Expected {expected_cmd})")


    print("\n👉 Test 3: Complete Scan (SCANNING -> COMPLETED)")
    res = validate_and_process(SCAN_COMPLETE, state_manager.get_state())
    state_manager.set_state(res["next_state"])
    if res["arduino_command"]:
        arduino.send(res["arduino_command"])
        
    expected_cmd = "SCAN_COMPLETED"
    actual_cmd = arduino.connection.last_write
    print(f"   State: {state_manager.get_state()}")
    print(f"   Command Sent: {actual_cmd}")
    if actual_cmd == expected_cmd:
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL (Expected {expected_cmd})")

    print("\n👉 Test 4: Emergency Stop")
    res = validate_and_process(EMERGENCY_STOP, state_manager.get_state())
    state_manager.set_state(res["next_state"])
    if res["arduino_command"]:
        arduino.send(res["arduino_command"])

    expected_cmd = "EMERGENCY_STOP"
    actual_cmd = arduino.connection.last_write
    print(f"   State: {state_manager.get_state()}")
    print(f"   Command Sent: {actual_cmd}")
    if actual_cmd == expected_cmd:
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL (Expected {expected_cmd})")

    print("\n✅ Test sequence complete.")

if __name__ == "__main__":
    test_logic()
