#!/usr/bin/env python3
"""
WDW 10K MSEP - Interactive Web-Based Fairy Light Color Calibrator
Serves a live slider UI at http://127.0.0.1:8765 and streams UDP frames (port 4210)
to the ESP32 costume shirt at 20 FPS.
"""

import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTTP_PORT = 8767
UDP_PORT = 4210

state_lock = threading.Lock()
state = {
    "target_ip": "255.255.255.255",
    "float_id": 0,
    "streaming": True,
    "window_only": False,
    "preset_name": "Drum Yellow",
    "panel_r": 255,
    "panel_g": 204,
    "panel_b": 21,
    "panel_bri": 100,
    "fairy_r": 255,
    "fairy_g": 50,
    "fairy_b": 8,
    "fairy_bri": 100,
}

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def send_udp_frame():
    with state_lock:
        ip = (state["target_ip"] or "255.255.255.255").strip()
        fid = int(state["float_id"]) & 0xFF
        p_bri = max(0, min(100, int(state.get("panel_bri", 100))))
        f_bri = max(0, min(100, int(state.get("fairy_bri", 100))))
        pr = (int(state["panel_r"]) * p_bri) // 100
        pg = (int(state["panel_g"]) * p_bri) // 100
        pb = (int(state["panel_b"]) * p_bri) // 100
        fr = (int(state["fairy_r"]) * f_bri) // 100
        fg = (int(state["fairy_g"]) * f_bri) // 100
        fb = (int(state["fairy_b"]) * f_bri) // 100
        win_only = bool(state["window_only"])

    matrix_bytes = bytearray(256 * 3)
    for row in range(16):
        for col in range(16):
            idx = row * 16 + (col if row % 2 == 0 else 15 - col)
            if (not win_only) or (4 <= row <= 11 and 4 <= col <= 11):
                matrix_bytes[idx * 3] = pr
                matrix_bytes[idx * 3 + 1] = pg
                matrix_bytes[idx * 3 + 2] = pb

    back_pkt = b"MSEP" + bytes([0x04, fid]) + (256).to_bytes(2, "big") + bytes(matrix_bytes)
    try:
        udp_sock.sendto(back_pkt, (ip, UDP_PORT))
    except OSError:
        pass

    fairy_bytes = bytes([fr, fg, fb]) * 25
    if fid != 0:
        front_hdr = b"MSEP" + bytes([0x02, fid]) + (306).to_bytes(2, "big")
    else:
        front_hdr = b"MSEP" + bytes([0x01]) + (306).to_bytes(2, "big")
    front_pkt = front_hdr + bytes(matrix_bytes) + fairy_bytes + fairy_bytes
    try:
        udp_sock.sendto(front_pkt, (ip, UDP_PORT))
    except OSError:
        pass


def udp_stream_worker():
    while True:
        with state_lock:
            active = state["streaming"]
        if active:
            send_udp_frame()
        time.sleep(0.05)


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>MSEP Fairy Light Color Calibrator</title>
<style>
  :root { --bg: #0f1219; --card: #181c26; --border: #2a3142; --text: #f1f5f9; --muted: #94a3b8; }
  * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
  body { margin: 0; padding: 14px; background: var(--bg); color: var(--text); }
  h1 { margin: 0 0 10px; font-size: 18px; color: #fbbf24; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin-bottom: 12px; }
  .row { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
  label { font-size: 12px; color: var(--muted); }
  input[type="text"], input[type="number"] {
    background: #0b0e14; color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 5px 8px; font-family: Consolas, monospace; font-size: 13px;
  }
  .presets { display: grid; grid-template-columns: repeat(auto-fill, minmax(115px, 1fr)); gap: 6px; margin-top: 8px; }
  .preset-btn {
    border: 1px solid rgba(255,255,255,0.18); border-radius: 7px; padding: 7px 6px;
    font-weight: 700; font-size: 12px; cursor: pointer; transition: transform 0.08s;
  }
  .preset-btn:active { transform: scale(0.97); }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  @media (max-width: 640px) { .grid2 { grid-template-columns: 1fr; } }
  .swatch {
    height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 13px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.2);
  }
  .slider-row { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
  .slider-row .lbl { width: 58px; font-size: 12px; font-weight: 700; }
  .slider-row input[type="range"] { flex: 1; accent-color: #38bdf8; cursor: pointer; }
  .slider-row .val { width: 38px; text-align: right; font-family: Consolas, monospace; font-weight: 700; font-size: 13px; }
  .nudge {
    background: #0b0e14; color: var(--text); border: 1px solid var(--border);
    border-radius: 5px; width: 26px; height: 26px; font-weight: 700; cursor: pointer;
  }
  .btn {
    border: none; border-radius: 7px; padding: 8px 14px; font-weight: 700; font-size: 13px; cursor: pointer;
  }
  .btn-sec { background: #334155; color: #fff; }
  .btn-save { background: #16a34a; color: #fff; }
  .btn-copy { background: #2563eb; color: #fff; margin-left: auto; }
  textarea {
    width: 100%; height: 140px; background: #0b0e14; color: #e2e8f0; border: 1px solid var(--border);
    border-radius: 8px; padding: 8px; font-family: Consolas, monospace; font-size: 12px; resize: vertical;
  }
</style>
</head>
<body>
  <h1>✨ MSEP Fairy Light Color Calibrator</h1>

  <div class="card row">
    <div><label>Target IP</label><br><input id="target_ip" type="text" value="255.255.255.255" style="width:140px" onchange="pushState()" /></div>
    <div><label>Float ID (0=All, 2=Drum)</label><br><input id="float_id" type="number" min="0" max="7" value="0" style="width:65px" onchange="pushState()" /></div>
    <label style="color:#4ade80; font-weight:700; cursor:pointer;"><input id="streaming" type="checkbox" checked onchange="pushState()" /> Live Stream (20 FPS)</label>
    <label style="color:#f1f5f9; cursor:pointer;"><input id="window_only" type="checkbox" onchange="pushState()" /> Center 8×8 Window Only</label>
  </div>

  <div class="card">
    <div style="font-size:13px; font-weight:700; color:#fbbf24;">1. Pick Parade Reference Color (16×16 Chest &amp; Back Panels)</div>
    <div class="presets" id="presets"></div>
  </div>

  <div class="grid2">
    <div class="card">
      <div style="font-size:13px; font-weight:700; margin-bottom:8px;">16×16 Panel Reference</div>
      <div class="swatch" id="panel_swatch"></div>
      <div class="slider-row"><span class="lbl" style="color:#ef4444">Panel R</span><button class="nudge" onclick="nudge('panel_r',-1)">-</button><input id="panel_r" type="range" min="0" max="255" value="255" oninput="onSlider()"><button class="nudge" onclick="nudge('panel_r',1)">+</button><span class="val" id="val_panel_r">255</span></div>
      <div class="slider-row"><span class="lbl" style="color:#22c55e">Panel G</span><button class="nudge" onclick="nudge('panel_g',-1)">-</button><input id="panel_g" type="range" min="0" max="255" value="204" oninput="onSlider()"><button class="nudge" onclick="nudge('panel_g',1)">+</button><span class="val" id="val_panel_g">204</span></div>
      <div class="slider-row"><span class="lbl" style="color:#3b82f6">Panel B</span><button class="nudge" onclick="nudge('panel_b',-1)">-</button><input id="panel_b" type="range" min="0" max="255" value="21" oninput="onSlider()"><button class="nudge" onclick="nudge('panel_b',1)">+</button><span class="val" id="val_panel_b">21</span></div>
      <div class="slider-row"><span class="lbl" style="color:#fbbf24">Bright %</span><button class="nudge" onclick="nudge('panel_bri',-5,100)">-</button><input id="panel_bri" type="range" min="0" max="100" value="100" oninput="onSlider()"><button class="nudge" onclick="nudge('panel_bri',5,100)">+</button><span class="val" id="val_panel_bri">100</span></div>
    </div>

    <div class="card">
      <div style="font-size:13px; font-weight:700; color:#38bdf8; margin-bottom:8px;">2. Dial Fairy Lights to Match</div>
      <div class="swatch" id="fairy_swatch"></div>
      <div class="slider-row"><span class="lbl" style="color:#ef4444">Fairy R</span><button class="nudge" onclick="nudge('fairy_r',-1)">-</button><input id="fairy_r" type="range" min="0" max="255" value="255" oninput="onSlider()"><button class="nudge" onclick="nudge('fairy_r',1)">+</button><span class="val" id="val_fairy_r">255</span></div>
      <div class="slider-row"><span class="lbl" style="color:#22c55e">Fairy G</span><button class="nudge" onclick="nudge('fairy_g',-1)">-</button><input id="fairy_g" type="range" min="0" max="255" value="50" oninput="onSlider()"><button class="nudge" onclick="nudge('fairy_g',1)">+</button><span class="val" id="val_fairy_g">50</span></div>
      <div class="slider-row"><span class="lbl" style="color:#3b82f6">Fairy B</span><button class="nudge" onclick="nudge('fairy_b',-1)">-</button><input id="fairy_b" type="range" min="0" max="255" value="8" oninput="onSlider()"><button class="nudge" onclick="nudge('fairy_b',1)">+</button><span class="val" id="val_fairy_b">8</span></div>
      <div class="slider-row"><span class="lbl" style="color:#fbbf24">Bright %</span><button class="nudge" onclick="nudge('fairy_bri',-5,100)">-</button><input id="fairy_bri" type="range" min="0" max="100" value="100" oninput="onSlider()"><button class="nudge" onclick="nudge('fairy_bri',5,100)">+</button><span class="val" id="val_fairy_bri">100</span></div>
    </div>
  </div>

  <div class="card row">
    <button class="btn btn-sec" onclick="copyPanelToFairy()">Copy Panel RGB → Fairy</button>
    <button class="btn btn-save" onclick="saveMatch()">Save Match for Current Color</button>
    <button class="btn btn-copy" onclick="copyReport()">Copy Report</button>
  </div>

  <div class="card">
    <div style="font-size:13px; font-weight:700; color:var(--muted); margin-bottom:6px;">3. Saved Color Matches (Paste these back in chat when done!)</div>
    <textarea id="report" readonly placeholder="Adjust Fairy R/G/B sliders until the fairy bulbs match the chest panel, then click 'Save Match'..."></textarea>
  </div>

<script>
const PRESETS = [
  ["Drum Yellow",   255, 204, 21],
  ["Parade Gold",   255, 180, 0],
  ["Red",           255, 0,   0],
  ["Blue",          0,   60,  255],
  ["Green",         0,   220, 40],
  ["White",         255, 255, 255],
  ["Magenta",       255, 20,  140],
];

let activePreset = "Drum Yellow";
const saved = {};

function estimateFairyWire(r, g, b) {
  const rLin = Math.floor((r * r) / 255);
  const gLin = Math.floor((g * g) / 255);
  let bLin = Math.floor((b * b) / 255);
  if (r > 200 && g > 100 && b < 25) {
    bLin = Math.max(bLin, 10);
  }
  return [
    rLin,
    Math.floor((gLin * 96) / 255),
    Math.floor((bLin * 187) / 255),
  ];
}

const presetsEl = document.getElementById("presets");
PRESETS.forEach(([name, r, g, b]) => {
  const btn = document.createElement("button");
  btn.className = "preset-btn";
  btn.textContent = name;
  btn.style.background = `rgb(${r},${g},${b})`;
  const lum = 0.299*r + 0.587*g + 0.114*b;
  btn.style.color = lum > 140 ? "#111" : "#fff";
  btn.onclick = () => {
    activePreset = name;
    if (saved[name]) {
      document.getElementById("panel_r").value = saved[name].pr;
      document.getElementById("panel_g").value = saved[name].pg;
      document.getElementById("panel_b").value = saved[name].pb;
      document.getElementById("panel_bri").value = saved[name].pbri;
      document.getElementById("fairy_r").value = saved[name].wr;
      document.getElementById("fairy_g").value = saved[name].wg;
      document.getElementById("fairy_b").value = saved[name].wb;
      document.getElementById("fairy_bri").value = saved[name].fbri;
    } else {
      document.getElementById("panel_r").value = r;
      document.getElementById("panel_g").value = g;
      document.getElementById("panel_b").value = b;
      const [fr, fg, fb] = estimateFairyWire(r, g, b);
      document.getElementById("fairy_r").value = fr;
      document.getElementById("fairy_g").value = fg;
      document.getElementById("fairy_b").value = fb;
    }
    onSlider();
  };
  presetsEl.appendChild(btn);
});

function nudge(id, d, maxVal = 255) {
  const el = document.getElementById(id);
  el.value = Math.max(0, Math.min(maxVal, parseInt(el.value, 10) + d));
  onSlider();
}

function copyPanelToFairy() {
  document.getElementById("fairy_r").value = document.getElementById("panel_r").value;
  document.getElementById("fairy_g").value = document.getElementById("panel_g").value;
  document.getElementById("fairy_b").value = document.getElementById("panel_b").value;
  onSlider();
}

function updateSwatches() {
  const ids = ["panel_r","panel_g","panel_b","panel_bri","fairy_r","fairy_g","fairy_b","fairy_bri"];
  ids.forEach(id => { document.getElementById("val_" + id).textContent = document.getElementById(id).value; });
  const pbri = +panel_bri.value, fbri = +fairy_bri.value;
  const pr = Math.floor((+panel_r.value * pbri) / 100), pg = Math.floor((+panel_g.value * pbri) / 100), pb = Math.floor((+panel_b.value * pbri) / 100);
  const fr = Math.floor((+fairy_r.value * fbri) / 100), fg = Math.floor((+fairy_g.value * fbri) / 100), fb = Math.floor((+fairy_b.value * fbri) / 100);
  const ps = document.getElementById("panel_swatch");
  ps.style.background = `rgb(${pr},${pg},${pb})`;
  ps.style.color = (0.299*pr + 0.587*pg + 0.114*pb) > 140 ? "#111" : "#fff";
  ps.textContent = `${activePreset}: (${pr}, ${pg}, ${pb}) @ ${pbri}%`;

  const fs = document.getElementById("fairy_swatch");
  fs.style.background = `rgb(${fr},${fg},${fb})`;
  fs.style.color = (0.299*fr + 0.587*fg + 0.114*fb) > 140 ? "#111" : "#fff";
  fs.textContent = `Wire RGB: (${fr}, ${fg}, ${fb}) @ ${fbri}%`;
}

let pushTimer = null;
function onSlider() {
  updateSwatches();
  clearTimeout(pushTimer);
  pushTimer = setTimeout(pushState, 20);
}

function pushState() {
  fetch("/api/state", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_ip: document.getElementById("target_ip").value,
      float_id: +document.getElementById("float_id").value,
      streaming: document.getElementById("streaming").checked,
      window_only: document.getElementById("window_only").checked,
      preset_name: activePreset,
      panel_r: +panel_r.value, panel_g: +panel_g.value, panel_b: +panel_b.value, panel_bri: +panel_bri.value,
      fairy_r: +fairy_r.value, fairy_g: +fairy_g.value, fairy_b: +fairy_b.value, fairy_bri: +fairy_bri.value,
    })
  });
}

function saveMatch() {
  const pbri = +panel_bri.value, fbri = +fairy_bri.value;
  const pr = +panel_r.value, pg = +panel_g.value, pb = +panel_b.value;
  const wr = +fairy_r.value, wg = +fairy_g.value, wb = +fairy_b.value;
  const epr = Math.floor((pr * pbri) / 100), epg = Math.floor((pg * pbri) / 100), epb = Math.floor((pb * pbri) / 100);
  const ewr = Math.floor((wr * fbri) / 100), ewg = Math.floor((wg * fbri) / 100), ewb = Math.floor((wb * fbri) / 100);
  const xr = Math.floor((ewr * 176) / 255), xg = ewg, xb = Math.floor((ewb * 240) / 255);
  saved[activePreset] = { pr, pg, pb, pbri, wr, wg, wb, fbri, epr, epg, epb, ewr, ewg, ewb, xr, xg, xb };
  const lines = Object.entries(saved).map(([n, m]) =>
    `${n.padEnd(14)} | Panel(${m.epr},${m.epg},${m.epb} @${m.pbri}%) -> Wire(${m.ewr},${m.ewg},${m.ewb} @${m.fbri}%) | Physical(${m.xr},${m.xg},${m.xb})`
  );
  document.getElementById("report").value = lines.join("\\n");
}

function copyReport() {
  const ta = document.getElementById("report");
  ta.select();
  document.execCommand("copy");
}

updateSwatches();
</script>
</body>
</html>
"""


class CalibratorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/state":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            with state_lock:
                for k in ("target_ip", "float_id", "streaming", "window_only", "preset_name",
                          "panel_r", "panel_g", "panel_b", "panel_bri",
                          "fairy_r", "fairy_g", "fairy_b", "fairy_bri"):
                    if k in data:
                        state[k] = data[k]
            if state["streaming"]:
                send_udp_frame()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    t = threading.Thread(target=udp_stream_worker, daemon=True)
    t.start()
    server = ThreadingHTTPServer(("127.0.0.1", HTTP_PORT), CalibratorHandler)
    print(f"MSEP Fairy Color Calibrator running at http://127.0.0.1:{HTTP_PORT}")
    server.serve_forever()
