/*
 * MagCrawler – ESP32 Motor Controller
 * ------------------------------------
 * Hardware : ESP32 Dev Board
 * Libraries: Blynk (BlynkSimpleEsp32), WiFi
 *
 * Virtual Pin Mapping (set from Flask/Blynk dashboard):
 *   V0 → Forward
 *   V1 → Backward
 *   V2 → Left
 *   V3 → Right
 *
 * Wiring (L298N / L293D motor driver):
 *   IN1 → GPIO 26  (Motor A – direction 1)
 *   IN2 → GPIO 27  (Motor A – direction 2)
 *   IN3 → GPIO 14  (Motor B – direction 1)
 *   IN4 → GPIO 12  (Motor B – direction 2)
 *   ENA → GPIO 25  (PWM speed – Motor A)  [optional]
 *   ENB → GPIO 33  (PWM speed – Motor B)  [optional]
 */

#define BLYNK_TEMPLATE_ID "TMPL3qABODsfp"
#define BLYNK_TEMPLATE_NAME "MagCrawler"
#define BLYNK_AUTH_TOKEN "YokJALrU6eVfSaqKMp-rPHhtj982vpNu" // Replace

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

// ── WiFi credentials ─────────────────────────────────────────
const char* ssid     = "Nothing 2a";      // Replace
const char* password = "1234567891";  // Replace

// ── Motor GPIO pins ───────────────────────────────────────────
#define IN1 26
#define IN2 27
#define IN3 14
#define IN4 12

// ── Motor helper functions ────────────────────────────────────
void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  Serial.println("[Motor] STOP");
}

void moveForward() {
  stopMotors();
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("[Motor] FORWARD");
}

void moveBackward() {
  stopMotors();
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  Serial.println("[Motor] BACKWARD");
}

void turnLeft() {
  stopMotors();
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("[Motor] LEFT");
}

void turnRight() {
  stopMotors();
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  Serial.println("[Motor] RIGHT");
}

// ── Blynk Virtual Pin Handlers ────────────────────────────────

// V0 → Forward
BLYNK_WRITE(V0) {
  int val = param.asInt();
  if (val == 1) moveForward();
  else          stopMotors();
}

// V1 → Backward
BLYNK_WRITE(V1) {
  int val = param.asInt();
  if (val == 1) moveBackward();
  else          stopMotors();
}

// V2 → Left
BLYNK_WRITE(V2) {
  int val = param.asInt();
  if (val == 1) turnLeft();
  else          stopMotors();
}

// V3 → Right
BLYNK_WRITE(V3) {
  int val = param.asInt();
  if (val == 1) turnRight();
  else          stopMotors();
}

// ── Setup ─────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Motor pins as output
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  stopMotors();

  Serial.println("[System] Connecting to WiFi…");
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, password);
  Serial.println("[System] Connected! Blynk ready.");
}

// ── Loop ──────────────────────────────────────────────────────
void loop() {
  Blynk.run();
}
