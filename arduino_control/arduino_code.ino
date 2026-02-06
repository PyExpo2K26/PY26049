const int PIN_MOTOR = 5;
const int PIN_LIGHT1 = 8;
const int PIN_LIGHT2 = 9;
const int PIN_BUZZER = 10;

// System States
enum SystemState {
  STATE_IDLE,
  STATE_START,
  STATE_SCANNING,
  STATE_STOPPING,
  STATE_COMPLETED,
  STATE_EMERGENCY
};

SystemState currentState = STATE_IDLE;
bool faceDetected = false;

// Blink Control
unsigned long lastBlinkTime = 0;
const int BLINK_INTERVAL = 300; // ms
int blinkCount = 0;
bool blinkLedState = false;
bool isBlinking = false;

String inputBuffer = "";

void setup() {
  Serial.begin(9600);
  
  pinMode(PIN_MOTOR, OUTPUT);
  pinMode(PIN_LIGHT1, OUTPUT);
  pinMode(PIN_LIGHT2, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  
  // Initial state
  resetSystem();
}

void loop() {
  // 1. Handle Serial Input
  handleSerial();
  
  // 2. Handle Blinking Logic (Non-blocking)
  handleBlink();
  
  // 3. Update Hardware Outputs based on State
  updateHardware();
}

void handleSerial() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else if (inChar != '\r') { // Ignore carriage return
      inputBuffer += inChar;
    }
  }
}

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.length() == 0) return;

  // Face Monitoring Commands
  if (cmd == "FACE_DETECTED") {
    faceDetected = true;
    return;
  } else if (cmd == "FACE_LOST") {
    faceDetected = false;
    return;
  }
  
  // State Machine Commands
  if (cmd == "START") {
    // Only switch if not already in start (though effect is same)
    currentState = STATE_START;
    isBlinking = false;
  } else if (cmd == "SCANNING") {
    currentState = STATE_SCANNING;
    isBlinking = false;
  } else if (cmd == "STOPPING") {
    // Prevent repeated blinking if same command repeats or if already stopping
    if (currentState != STATE_STOPPING) {
      currentState = STATE_STOPPING;
      startBlinkSequence();
    }
  } else if (cmd == "COMPLETED") {
    currentState = STATE_COMPLETED;
    isBlinking = false;
  } else if (cmd == "EMERGENCY") {
    currentState = STATE_EMERGENCY;
    isBlinking = false;
  } else if (cmd == "RESET") {
    resetSystem();
  }
}

void startBlinkSequence() {
  isBlinking = true;
  blinkCount = 0;
  blinkLedState = true; // Start ON
  lastBlinkTime = millis();
}

void handleBlink() {
  if (currentState == STATE_STOPPING && isBlinking) {
    unsigned long currentMillis = millis();
    if (currentMillis - lastBlinkTime >= BLINK_INTERVAL) {
      lastBlinkTime = currentMillis;
      blinkLedState = !blinkLedState;
      
      // We flip state every interval.
      // 5 blinks means ON-OFF 5 times. 
      // That is 10 state changes if we start from OFF->ON.
      // sequence: ON (wait), OFF (wait), ON (wait), OFF (wait)...
      
      blinkCount++;
      if (blinkCount >= 10) { // 5 Full Blinks
        isBlinking = false;
        blinkLedState = false; // Ensure off at end
      }
    }
  }
}

void updateHardware() {
  // Motor Control
  // Logic: Motor is ON if face is detected, UNLESS in Reset or Emergency state.
  bool motorState = false;
  if (currentState != STATE_IDLE && currentState != STATE_EMERGENCY) {
      motorState = faceDetected;
  }
  digitalWrite(PIN_MOTOR, motorState ? HIGH : LOW);

  // Buzzer Control
  digitalWrite(PIN_BUZZER, (currentState == STATE_EMERGENCY) ? HIGH : LOW);

  // Lights Control
  bool l1 = false;
  bool l2 = false;

  switch (currentState) {
    case STATE_IDLE:
      l1 = false;
      l2 = false;
      break;
    case STATE_START:
      l1 = true;
      l2 = false;
      break;
    case STATE_SCANNING:
      // SCANNING -> Turn ON Light 2
      // Assuming Light 1 turns off to distinguish phases
      l1 = false;
      l2 = true;
      break;
    case STATE_STOPPING:
      if (isBlinking) {
        l1 = blinkLedState;
        l2 = blinkLedState;
      } else {
        l1 = false;
        l2 = false;
      }
      break;
    case STATE_COMPLETED:
      l1 = true;
      l2 = true;
      break;
    case STATE_EMERGENCY:
      l1 = false;
      l2 = false;
      break;
  }
  
  digitalWrite(PIN_LIGHT1, l1 ? HIGH : LOW);
  digitalWrite(PIN_LIGHT2, l2 ? HIGH : LOW);
}

void resetSystem() {
  currentState = STATE_IDLE;
  faceDetected = false;
  isBlinking = false;
  blinkLedState = false;
}