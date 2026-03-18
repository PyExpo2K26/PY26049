/**
 * MagCrawler — Robot Control Script
 * ─────────────────────────────────
 * Each function is wired to a UI button and ready
 * to be extended with Blynk HTTP API or WebSocket calls.
 */

// ── Config ─────────────────────────────────────────────────────────────────
// ⚠ ONLY LINE TO CHANGE when ESP32-CAM gets a new IP:
//   1. Open Arduino Serial Monitor at 115200 baud
//   2. Press RST on the ESP32-CAM
//   3. Copy the IP printed next to "IP address :"
//   4. Paste it into cameraIp below

const CONFIG = {
  // Stream is proxied through Flask to avoid CORS issues
  streamUrl:   '/camera/stream',
  captureUrl:  '/camera/capture',
  controlBase: '/control',          // /control/forward, /control/stop, etc.
};

// Automatically wire the stream URL to the <img> tag
// so the HTML never needs to be touched when the IP changes
document.addEventListener('DOMContentLoaded', () => {
  const img = document.getElementById('cam-stream');
  if (img) {
    img.src = CONFIG.streamUrl;
    log(`Camera stream → ${CONFIG.streamUrl}`);
  }

  // Allow updating ESP32 IP from the dashboard without restarting Flask
  const ipInput = document.getElementById('esp32-ip-input');
  const ipBtn   = document.getElementById('esp32-ip-btn');
  if (ipBtn && ipInput) {
    ipBtn.addEventListener('click', async () => {
      const ip = ipInput.value.trim();
      if (!ip) return;
      try {
        const res = await fetch('/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip })
        });
        const data = await res.json();
        log(`ESP32 IP updated → ${data.esp32_ip}`);
        // Reload stream with new IP
        if (img) { img.src = ''; img.src = CONFIG.streamUrl + '?t=' + Date.now(); }
      } catch (e) { log('IP update failed: ' + e.message, 'error'); }
    });
  }
});

// ── State ──────────────────────────────────────────────────────────────────

let currentSpeed   = 50;
let currentMode    = 'STANDBY';
let cleanMode      = 'SWEEP';
let isEmergency    = false;

// ── ESP32 Direct Control ───────────────────────────────────────────────────

/**
 * Send a motor command to the ESP32 via Flask proxy.
 * @param {string} action  - 'forward' | 'backward' | 'left' | 'right' | 'stop'
 */
async function sendControl(action) {
  try {
    const res  = await fetch(`${CONFIG.controlBase}/${action}`);
    const data = await res.json();
    if (!data.ok) log(`Control warning: ESP32 did not confirm ${action}`, 'warn');
  } catch (err) {
    log(`Control error (${action}): ${err.message}`, 'error');
  }
}

// Legacy alias kept so existing calls compile
function blynkWrite(pin, value) { /* no-op — replaced by sendControl */ }

// ── Core Control Functions ─────────────────────────────────────────────────

/**
 * Move the robot forward.
 */
function moveForward() {
  if (isEmergency) return guardEmergency();
  setMode('MOVING · FWD');
  sendControl('forward');
  log('Move FORWARD');
  flashButton('[title="Forward"]');
  updateLastAction('Forward');
}

/**
 * Move the robot backward.
 */
function moveBackward() {
  if (isEmergency) return guardEmergency();
  setMode('MOVING · BWD');
  sendControl('backward');
  log('Move BACKWARD');
  flashButton('[title="Backward"]');
  updateLastAction('Backward');
}

/**
 * Turn the robot left.
 */
function moveLeft() {
  if (isEmergency) return guardEmergency();
  setMode('TURNING · LEFT');
  sendControl('left');
  log('Turn LEFT');
  flashButton('[title="Left"]');
  updateLastAction('Left');
}

/**
 * Turn the robot right.
 */
function moveRight() {
  if (isEmergency) return guardEmergency();
  setMode('TURNING · RIGHT');
  sendControl('right');
  log('Turn RIGHT');
  flashButton('[title="Right"]');
  updateLastAction('Right');
}

/**
 * Stop all wheel movement (not a full e-stop).
 */
function haltMovement() {
  if (isEmergency) return;
  setMode('STANDBY');
  sendControl('stop');
  log('Movement halted', 'warn');
  updateLastAction('Stop');
}

/**
 * Activate the cleaning brush / pump.
 */
function startCleaning() {
  if (isEmergency) return guardEmergency();
  setMode(`CLEANING · ${cleanMode}`);
  blynkWrite(CONFIG.pins.startCleaning, 1);
  log(`Cleaning started — mode: ${cleanMode}`);
  updateLastAction('Start Cleaning');
}

/**
 * Stop the cleaning brush / pump.
 */
function stopCleaning() {
  if (isEmergency) return;
  setMode('STANDBY');
  blynkWrite(CONFIG.pins.stopCleaning, 1);
  log('Cleaning stopped', 'warn');
  updateLastAction('Stop Cleaning');
}

/**
 * Emergency stop — halts all systems immediately.
 * Must be manually reset by calling resetEmergency().
 */
function emergencyStop() {
  isEmergency = true;
  setMode('⚠  E-STOP ACTIVE');

  // Halt all motion on ESP32
  sendControl('stop');

  // Visual feedback
  const btn = document.querySelector('.estop-btn');
  btn.classList.add('triggered');
  btn.textContent = ''; // rebuild
  btn.innerHTML = `
    <span class="estop-stripe"></span>
    <span class="relative z-10 flex items-center justify-center gap-3" style="font-family:var(--font-display);font-size:1.1rem;font-weight:900;letter-spacing:.2em">
      ⚠ E-STOP ACTIVE — TAP TO RESET ⚠
    </span>`;
  btn.onclick = resetEmergency;

  log('⚠ EMERGENCY STOP TRIGGERED — all systems halted', 'error');
}

/**
 * Reset emergency state.
 */
function resetEmergency() {
  isEmergency = false;
  setMode('STANDBY');
  sendControl('stop'); // ensure motors are stopped on reset

  const btn = document.querySelector('.estop-btn');
  btn.classList.remove('triggered');
  btn.innerHTML = `
    <span class="estop-stripe"></span>
    <span class="relative z-10 flex items-center justify-center gap-3">
      <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      EMERGENCY STOP
      <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
    </span>`;
  btn.onclick = emergencyStop;

  log('Emergency reset. Systems nominal.', 'warn');
}

/**
 * Set drive speed (0–100).
 * @param {number} value
 */
function setSpeed(value) {
  currentSpeed = parseInt(value, 10);
  document.getElementById('speed-label').textContent = `${currentSpeed}%`;
  blynkWrite(CONFIG.pins.speed, currentSpeed);
}

/**
 * Set cleaning mode label.
 * @param {HTMLElement} el
 * @param {string} mode
 */
function setCleanMode(el, mode) {
  cleanMode = mode;
  document.querySelectorAll('.mode-pill').forEach(p => p.classList.remove('active-pill'));
  el.classList.add('active-pill');
  log(`Clean mode → ${mode}`);
}

// ── UI Helpers ─────────────────────────────────────────────────────────────

function setMode(label) {
  currentMode = label;
  const el = document.getElementById('mode-display');
  el.textContent = label;
}

function updateLastAction(action) {
  document.getElementById('last-action').textContent = `Last: ${action}`;
}

function guardEmergency() {
  log('⚠ E-Stop active — reset before issuing commands', 'error');
}

/**
 * Append a line to the command log.
 * @param {string} message
 * @param {'info'|'warn'|'error'} level
 */
function log(message, level = 'info') {
  const logEl = document.getElementById('log');
  const ts     = new Date().toTimeString().slice(0, 8);
  const div    = document.createElement('div');
  div.className = `log-entry${level !== 'info' ? ' ' + level : ''}`;
  div.innerHTML = `<span style="color:#2a5a3a">${ts}</span> ${message}`;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;

  // Keep last 50 entries
  while (logEl.children.length > 50) logEl.removeChild(logEl.firstChild);
}

// ── Keyboard Control ───────────────────────────────────────────────────────

const keyMap = {
  ArrowUp:    moveForward,
  ArrowDown:  moveBackward,
  ArrowLeft:  moveLeft,
  ArrowRight: moveRight,
  KeyW:       moveForward,
  KeyS:       moveBackward,
  KeyA:       moveLeft,
  KeyD:       moveRight,
  Space:      haltMovement,
  Escape:     emergencyStop,
};

const keysDown = new Set();

document.addEventListener('keydown', (e) => {
  if (keysDown.has(e.code)) return; // prevent repeat
  keysDown.add(e.code);
  if (keyMap[e.code]) {
    e.preventDefault();
    keyMap[e.code]();
  }
});

document.addEventListener('keyup', (e) => {
  keysDown.delete(e.code);
  // Auto-halt on arrow/WASD release
  const moveKeys = new Set(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','KeyW','KeyS','KeyA','KeyD']);
  if (moveKeys.has(e.code) && !isEmergency) {
    // Only halt if no other move key is held
    const anyMove = [...keysDown].some(k => moveKeys.has(k));
    if (!anyMove) haltMovement();
  }
});

// ── Clock ──────────────────────────────────────────────────────────────────

function updateClock() {
  document.getElementById('clock').textContent = new Date().toTimeString().slice(0, 8);
}
setInterval(updateClock, 1000);
updateClock();

// ── Simulated telemetry (replace with real Blynk reads) ───────────────────

function simulateTelemetry() {
  const battery = parseInt(document.getElementById('stat-battery').textContent);
  const newBat  = Math.max(0, battery - (Math.random() > 0.8 ? 1 : 0));
  document.getElementById('stat-battery').textContent = `${newBat}%`;
  document.querySelector('.stat-card:nth-child(1) .stat-bar-fill').style.width = `${newBat}%`;

  const sig = -55 - Math.floor(Math.random() * 20);
  document.getElementById('stat-signal').textContent = `${sig} dBm`;
  document.querySelector('.stat-card:nth-child(2) .stat-bar-fill').style.width = `${Math.max(0, 100 + sig)}%`;

  const temp = 35 + Math.floor(Math.random() * 8);
  document.getElementById('stat-temp').textContent = `${temp}°C`;
  document.querySelector('.stat-card:nth-child(3) .stat-bar-fill').style.width = `${temp}%`;

  const mag = (3.8 + Math.random() * 0.8).toFixed(1);
  document.getElementById('stat-mag').textContent = `${mag} N`;
}

setInterval(simulateTelemetry, 3000);

// ── ESP32-CAM Stream Handlers ──────────────────────────────────────────────

/**
 * Called by the <img> onload event when the first frame arrives.
 * Fades the stream in and marks the badge as LIVE.
 */
function handleStreamLoad() {
  const img    = document.getElementById('cam-stream');
  const dot    = document.getElementById('stream-dot');
  const badge  = document.getElementById('stream-badge');
  const offline = document.getElementById('cam-offline');

  img.classList.add('loaded');
  if (offline) offline.classList.add('hidden');

  if (dot)   { dot.style.background = '#00ff88'; }
  if (badge) { badge.textContent = 'LIVE'; badge.style.color = '#00ff88'; }

  log('Camera stream connected via Flask proxy');
}

/**
 * Called by the <img> onerror event when the stream is unreachable.
 * Shows the offline fallback and retries every 5 s.
 */
function handleStreamError() {
  const img    = document.getElementById('cam-stream');
  const dot    = document.getElementById('stream-dot');
  const badge  = document.getElementById('stream-badge');
  const offline = document.getElementById('cam-offline');

  img.classList.remove('loaded');
  if (offline) offline.classList.remove('hidden');

  if (dot)   { dot.style.background = '#ff3a3a'; }
  if (badge) { badge.textContent = 'OFFLINE'; badge.style.color = '#ff6a6a'; }

  log('Camera stream offline — retrying in 5 s…', 'warn');

  // Retry: reassign src after delay to trigger a fresh connection attempt
  setTimeout(() => {
    if (img) {
      img.src = '';
      img.src = CONFIG.streamUrl + '?t=' + Date.now();
      if (badge) { badge.textContent = 'CONNECTING'; badge.style.color = '#ffaa44'; }
    }
  }, 5000);
}

/**
 * Visual "press" feedback for the d-pad buttons (used by flashButton).
 * Adds the .pressing class briefly so CSS handles the animation.
 */
function flashButton(selector) {
  const btn = document.querySelector(selector);
  if (!btn) return;
  btn.classList.add('pressing');
  setTimeout(() => btn.classList.remove('pressing'), 180);
}

// ── Init ───────────────────────────────────────────────────────────────────
log('Dashboard ready. Keyboard: WASD / Arrows · ESC = E-Stop');