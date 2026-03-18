/*
 * MagCrawler — ESP32-CAM  (AI Thinker)
 * ======================================
 * • Streams MJPEG video  →  http://<IP>/stream
 * • Snapshot             →  http://<IP>/capture
 * • Motor control        →  http://<IP>/forward | /backward | /left | /right | /stop
 * • Status ping          →  http://<IP>/status
 *
 * Board    : AI Thinker ESP32-CAM  (select in Arduino IDE)
 * Partition: "Huge APP (3MB No OTA)" — required for camera+OV2640
 *
 * Wiring (L298N motor driver):
 *   IN1 → GPIO 12   (Motor A dir-1)
 *   IN2 → GPIO 13   (Motor A dir-2)
 *   IN3 → GPIO 15   (Motor B dir-1)
 *   IN4 → GPIO 14   (Motor B dir-2)
 *
 * ⚠ GPIO 2, 4, 16 are used by the SD/PSRAM/FLASH on AI-Thinker — don't touch them.
 * ⚠ GPIO 0 is also BOOT — only safe as output after boot if you remove the jumper.
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// ─── WiFi credentials ────────────────────────────────────────────────────────
const char* WIFI_SSID = "ESP_TEST";       // ← your network SSID
const char* WIFI_PASS = "12345678";       // ← your network password

// ─── Camera model (AI-Thinker pinout) ────────────────────────────────────────
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ─── Motor GPIO pins ─────────────────────────────────────────────────────────
// Avoid 2, 4, 16 (camera/psram), 0 (boot), 32-39 (camera sensors)
#define IN1  12
#define IN2  13
#define IN3  15
#define IN4  14

// ─── Motor helpers ───────────────────────────────────────────────────────────
void motorsStop()    { digitalWrite(IN1,LOW);  digitalWrite(IN2,LOW);  digitalWrite(IN3,LOW);  digitalWrite(IN4,LOW);  Serial.println("[Motor] STOP"); }
void motorsForward() { digitalWrite(IN1,HIGH); digitalWrite(IN2,LOW);  digitalWrite(IN3,HIGH); digitalWrite(IN4,LOW);  Serial.println("[Motor] FORWARD"); }
void motorsBackward(){ digitalWrite(IN1,LOW);  digitalWrite(IN2,HIGH); digitalWrite(IN3,LOW);  digitalWrite(IN4,HIGH); Serial.println("[Motor] BACKWARD"); }
void motorsLeft()    { digitalWrite(IN1,LOW);  digitalWrite(IN2,HIGH); digitalWrite(IN3,HIGH); digitalWrite(IN4,LOW);  Serial.println("[Motor] LEFT"); }
void motorsRight()   { digitalWrite(IN1,HIGH); digitalWrite(IN2,LOW);  digitalWrite(IN3,LOW);  digitalWrite(IN4,HIGH); Serial.println("[Motor] RIGHT"); }

// ─── CORS helper ─────────────────────────────────────────────────────────────
static esp_err_t addCORSHeaders(httpd_req_t* req) {
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin",  "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, OPTIONS");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
  return ESP_OK;
}

// ─── HTTP handlers ────────────────────────────────────────────────────────────

// GET /status
static esp_err_t statusHandler(httpd_req_t* req) {
  addCORSHeaders(req);
  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, "{\"status\":\"ok\",\"device\":\"MagCrawler\"}");
  return ESP_OK;
}

// GET /forward | /backward | /left | /right | /stop
static esp_err_t motionHandler(httpd_req_t* req) {
  addCORSHeaders(req);
  String uri = String(req->uri);
  if      (uri == "/forward")  { motorsForward();  httpd_resp_sendstr(req, "{\"action\":\"forward\"}"); }
  else if (uri == "/backward") { motorsBackward(); httpd_resp_sendstr(req, "{\"action\":\"backward\"}"); }
  else if (uri == "/left")     { motorsLeft();     httpd_resp_sendstr(req, "{\"action\":\"left\"}"); }
  else if (uri == "/right")    { motorsRight();    httpd_resp_sendstr(req, "{\"action\":\"right\"}"); }
  else                         { motorsStop();     httpd_resp_sendstr(req, "{\"action\":\"stop\"}"); }
  httpd_resp_set_type(req, "application/json");
  return ESP_OK;
}

// GET /capture  — single JPEG snapshot
static esp_err_t captureHandler(httpd_req_t* req) {
  addCORSHeaders(req);
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) { httpd_resp_send_500(req); return ESP_FAIL; }
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  esp_err_t res = httpd_resp_send(req, (const char*)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return res;
}

// GET /stream  — MJPEG stream
#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY     = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART         = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

static esp_err_t streamHandler(httpd_req_t* req) {
  addCORSHeaders(req);
  esp_err_t res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  char partBuf[64];
  while (true) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) { Serial.println("[CAM] Frame grab failed"); break; }

    res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
    if (res == ESP_OK) {
      size_t hlen = snprintf(partBuf, sizeof(partBuf), STREAM_PART, fb->len);
      res = httpd_resp_send_chunk(req, partBuf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
    }
    esp_camera_fb_return(fb);
    if (res != ESP_OK) break;
  }
  return res;
}

// ─── Start HTTP server ───────────────────────────────────────────────────────
static httpd_handle_t startWebServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port    = 80;
  config.max_uri_handlers = 10;

  httpd_handle_t server = NULL;
  if (httpd_start(&server, &config) != ESP_OK) {
    Serial.println("[HTTP] Failed to start server");
    return NULL;
  }

  auto reg = [&](const char* uri, esp_err_t (*handler)(httpd_req_t*)) {
    httpd_uri_t h = { uri, HTTP_GET, handler, NULL };
    httpd_register_uri_handler(server, &h);
  };

  reg("/status",   statusHandler);
  reg("/stream",   streamHandler);
  reg("/capture",  captureHandler);
  reg("/forward",  motionHandler);
  reg("/backward", motionHandler);
  reg("/left",     motionHandler);
  reg("/right",    motionHandler);
  reg("/stop",     motionHandler);

  return server;
}

// ─── Camera init ─────────────────────────────────────────────────────────────
bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode    = CAMERA_GRAB_LATEST;

  if (psramFound()) {
    config.frame_size   = FRAMESIZE_VGA;   // 640×480 — good balance
    config.jpeg_quality = 12;              // lower = better quality
    config.fb_count     = 2;
    config.fb_location  = CAMERA_FB_IN_PSRAM;
  } else {
    config.frame_size   = FRAMESIZE_QVGA;  // 320×240 fallback
    config.jpeg_quality = 15;
    config.fb_count     = 1;
    config.fb_location  = CAMERA_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CAM] Init failed: 0x%x\n", err);
    return false;
  }

  // Improve image quality
  sensor_t* s = esp_camera_sensor_get();
  s->set_brightness(s, 0);
  s->set_contrast(s, 0);
  s->set_saturation(s, 0);
  s->set_special_effect(s, 0);
  s->set_whitebal(s, 1);
  s->set_awb_gain(s, 1);
  s->set_wb_mode(s, 0);
  s->set_exposure_ctrl(s, 1);
  s->set_aec2(s, 0);
  s->set_aec_value(s, 300);
  s->set_gain_ctrl(s, 1);
  s->set_agc_gain(s, 0);
  s->set_gainceiling(s, (gainceiling_t)0);
  s->set_bpc(s, 0);
  s->set_wpc(s, 1);
  s->set_raw_gma(s, 1);
  s->set_lenc(s, 1);
  s->set_hmirror(s, 0);
  s->set_vflip(s, 0);
  s->set_dcw(s, 1);
  s->set_colorbar(s, 0);

  Serial.println("[CAM] Initialized successfully");
  return true;
}

// ─── Setup ───────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n[System] MagCrawler ESP32-CAM booting…");

  // Motor pins
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  motorsStop();

  // Camera
  if (!initCamera()) {
    Serial.println("[CAM] FATAL — check wiring / board selection");
    while (true) delay(1000);
  }

  // WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("[WiFi] Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("[WiFi] Connected! IP address : ");
  Serial.println(WiFi.localIP());

  // HTTP Server
  if (startWebServer()) {
    Serial.println("[HTTP] Server started.");
    Serial.print("[HTTP] Stream  → http://");
    Serial.print(WiFi.localIP()); Serial.println("/stream");
    Serial.print("[HTTP] Control → http://");
    Serial.print(WiFi.localIP()); Serial.println("/forward  /backward  /left  /right  /stop");
  }
}

// ─── Loop ────────────────────────────────────────────────────────────────────
void loop() {
  // Everything is handled by the HTTP server tasks.
  // You can add sensor reads / telemetry here.
  delay(10);
}
