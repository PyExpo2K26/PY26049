from flask import Flask, render_template, jsonify, Response, request
import requests
import time

app = Flask(__name__)

# ── ESP32-CAM Configuration ──────────────────────────────────────────────────
ESP32_IP = "172.25.123.90"   # ← Replace with actual IP from Serial Monitor
ESP32_BASE = f"http://{ESP32_IP}"
START_TIME = time.time()


def esp32_get(path: str):
    """Send a GET request to the ESP32 and return (ok, json_response)."""
    try:
        url = f"{ESP32_BASE}{path}"
        resp = requests.get(url, timeout=3)
        return resp.status_code == 200, resp.json() if resp.content else {}
    except requests.RequestException as e:
        print(f"[ESP32] Error on {path}: {e}")
        return False, {"error": str(e)}


# ── Page Routes ──────────────────────────────────────────────────────────────
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/dashboard")
def index():
    return render_template("index.html", esp32_ip=ESP32_IP)


@app.route("/admin")
def admin():
    return render_template("admin.html", esp32_ip=ESP32_IP)


# ── Camera proxy (avoids CORS issues in browser) ─────────────────────────────
@app.route("/camera/stream")
def camera_stream():
    """Proxy the MJPEG stream from the ESP32-CAM so the browser only talks to Flask."""
    def generate():
        try:
            with requests.get(f"{ESP32_BASE}/stream", stream=True, timeout=10) as r:
                for chunk in r.iter_content(chunk_size=4096):
                    yield chunk
        except Exception as e:
            print(f"[Stream] Error: {e}")
            yield b""

    return Response(
        generate(),
        content_type="multipart/x-mixed-replace; boundary=123456789000000000000987654321"
    )


@app.route("/camera/capture")
def camera_capture():
    """Proxy a single JPEG snapshot from the ESP32-CAM."""
    try:
        resp = requests.get(f"{ESP32_BASE}/capture", timeout=5)
        return Response(resp.content, content_type="image/jpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 503


# ── Control Routes ────────────────────────────────────────────────────────────
@app.route("/control/<action>")
def control(action: str):
    valid = {"forward", "backward", "left", "right", "stop"}
    if action not in valid:
        return jsonify({"error": "unknown action"}), 400
    ok, data = esp32_get(f"/{action}")
    return jsonify({"action": action, "ok": ok, **data})


# Legacy routes kept for backward compat
@app.route("/forward")
def fwd():  return control("forward")

@app.route("/back")
def bck():  return control("backward")

@app.route("/left")
def lft():  return control("left")

@app.route("/right")
def rgt():  return control("right")

@app.route("/stop")
def stp():  return control("stop")


# ── Status ────────────────────────────────────────────────────────────────────
@app.route("/status")
def status():
    ok, data = esp32_get("/status")
    return jsonify({"flask": "ok", "esp32_reachable": ok, "esp32": data,
                    "esp32_ip": ESP32_IP})


# ── Admin Status API ──────────────────────────────────────────────────────────
@app.route("/api/admin/status")
def admin_status():
    ok, data = esp32_get("/status")
    uptime_sec = int(time.time() - START_TIME)
    hours, rem = divmod(uptime_sec, 3600)
    minutes, seconds = divmod(rem, 60)
    # check camera stream reachability
    try:
        r = requests.head(f"{ESP32_BASE}/stream", timeout=2)
        cam_ok = r.status_code < 400
    except Exception:
        cam_ok = False
    return jsonify({
        "esp32_ip": ESP32_IP,
        "esp32_reachable": ok,
        "camera_ok": cam_ok,
        "uptime": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        "flask": "ok"
    })


# ── Config (update ESP32 IP at runtime) ──────────────────────────────────────
@app.route("/config", methods=["POST"])
def set_config():
    global ESP32_IP, ESP32_BASE
    data = request.get_json(force=True)
    if "ip" in data:
        ESP32_IP   = data["ip"].strip()
        ESP32_BASE = f"http://{ESP32_IP}"
        print(f"[Config] ESP32 IP updated → {ESP32_IP}")
    return jsonify({"esp32_ip": ESP32_IP})


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[Config] Expecting ESP32-CAM at http://{ESP32_IP}")
    print("[Config] Update ESP32_IP in app.py to match your Serial Monitor output")
    app.run(debug=True, host="0.0.0.0", port=5000)
