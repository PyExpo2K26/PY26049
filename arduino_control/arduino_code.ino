
const int PIN_GREEN = 8;
const int PIN_YELLOW = 9;
const int PIN_RED = 10;

String command = "";

void setup() {
  Serial.begin(9600);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_RED, OUTPUT);


  digitalWrite(PIN_GREEN, LOW);
  digitalWrite(PIN_YELLOW, LOW);
  digitalWrite(PIN_RED, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim(); 

    if (command == "START_SCAN" || command == "INITIALIZE_SYSTEM") {
      setLedState(true, false, false); 
    } else if (command == "SCAN_COMPLETED") {
      setLedState(false, true, false); 
    } else if (command == "STOP_SCAN") {
      setLedState(false, true, false); 
    } else if (command == "EMERGENCY_STOP" || command == "EMERGENCY") {
      setLedState(false, false, true); 
    } else if (command == "RESET") {
      setLedState(false, false, false); 
    }
  }
}

void setLedState(bool green, bool yellow, bool red) {
  digitalWrite(PIN_GREEN, green ? HIGH : LOW);
  digitalWrite(PIN_YELLOW, yellow ? HIGH : LOW);
  digitalWrite(PIN_RED, red ? HIGH : LOW);
}