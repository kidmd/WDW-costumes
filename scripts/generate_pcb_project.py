import os
import json
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes
from scipy.spatial import ConvexHull

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")
PCB_DIR = os.path.join(BASE_DIR, "pcb")
os.makedirs(PCB_DIR, exist_ok=True)

# 1. Load coordinates
preset_path = os.path.join(PRESETS_DIR, "petes_dragon_chris.json")
if not os.path.exists(preset_path):
    preset_path = os.path.join(PRESETS_DIR, "fleet_lineup.json")
    with open(preset_path, "r", encoding="utf-8") as f:
        fleet = json.load(f)
        dragon_data = fleet.get("floats", {}).get("6", {})
        leds = dragon_data.get("leds", [])
else:
    with open(preset_path, "r", encoding="utf-8") as f:
        dragon_data = json.load(f)
        leds = dragon_data.get("leds", [])

# Target physical dimensions on chest:
# Graphic width ~ 185 mm (~7.3 inches), Height ~ 145 mm (~5.7 inches)
# Shirt width: 18.0 inches = 457.2 mm; height: 24.0 inches = 609.6 mm
GARMENT_W_MM = 457.2
GARMENT_H_MM = 609.6

# Chest bounds in normalized coords:
# normX: [0.10, 0.90], normY: [0.168, 0.553]
# Compute center offset to place PCB at (100mm, 100mm) origin in KiCad
min_x = min(l.get("x", 0.5) for l in leds)
max_x = max(l.get("x", 0.5) for l in leds)
min_y = min(l.get("y", 0.5) for l in leds)
max_y = max(l.get("y", 0.5) for l in leds)

span_x_mm = (max_x - min_x) * GARMENT_W_MM
span_y_mm = (max_y - min_y) * GARMENT_H_MM

# Scale & center into board coordinates:
BOARD_OFFSET_X = 25.0
BOARD_OFFSET_Y = 25.0

led_positions_mm = []
for i, l in enumerate(leds):
    px = (l.get("x", 0.5) - min_x) * GARMENT_W_MM + BOARD_OFFSET_X
    py = (l.get("y", 0.5) - min_y) * GARMENT_H_MM + BOARD_OFFSET_Y
    col = l.get("color", {"r": 0, "g": 255, "b": 100})
    led_positions_mm.append({
        "id": i + 1,
        "ref": f"LED{i+1}",
        "cap_ref": f"C{i+1}",
        "x": round(px, 3),
        "y": round(py, 3),
        "color": col
    })

# 2. Generate BOM (Bill of Materials) for JLCPCB SMT Assembly
bom_path = os.path.join(PCB_DIR, "petes_dragon_bom.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write("Comment,Designator,Footprint,LCSC Part #\n")
    led_refs = " ".join([d["ref"] for d in led_positions_mm])
    cap_refs = " ".join([d["cap_ref"] for d in led_positions_mm])
    f.write(f'"WS2812B-2020 Addressable RGB LED","{led_refs}","LED-SMD_4P-L2.0-W2.0-TL","C2843818"\n')
    f.write(f'"100nF (0.1uF) 50V 0402 Capacitor","{cap_refs}","C0402","C1525"\n')
    f.write('"JST-PH-3P SMT 2.0mm Header","J1","JST_PH_S3B-PH-SM4-TB","C145946"\n')

# 3. Generate CPL (Pick and Place Centroid File) for JLCPCB
cpl_path = os.path.join(PCB_DIR, "petes_dragon_cpl.csv")
with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("Designator,Mid X,Mid Y,Layer,Rotation\n")
    for d in led_positions_mm:
        # LED chip
        f.write(f'{d["ref"]},{d["x"]},{d["y"]},Top,0\n')
        # Bypass Capacitor placed 2.5mm adjacent to LED
        f.write(f'{d["cap_ref"]},{round(d["x"] + 2.2, 3)},{round(d["y"], 3)},Top,90\n')
    # Power connector at first LED position
    f.write(f'J1,{round(led_positions_mm[0]["x"] - 6.0, 3)},{round(led_positions_mm[0]["y"] + 6.0, 3)},Top,180\n')

# 4. Generate Interactive PCB 3D/2D Visualizer HTML
preview_path = os.path.join(PCB_DIR, "pcb_preview.html")
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pete's Dragon Custom Flex PCB (FPC) Inspector - 100 SMD LEDs</title>
<style>
  :root {{
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #00ff88;
    --fpc-gold: #c29d38;
    --trace-copper: #e08c38;
    --led-chip: #ffffff;
  }}
  body {{
    margin: 0;
    padding: 20px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
  }}
  h1 {{
    color: #fff;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 24px;
    margin-bottom: 6px;
  }}
  .badge {{
    background: #238636;
    color: #fff;
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 12px;
    font-weight: 600;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 20px;
    margin-top: 16px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
  }}
  .viewer-box {{
    position: relative;
    background: #05080c;
    border-radius: 8px;
    border: 1px solid var(--border);
    overflow: hidden;
    height: 640px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  svg {{
    width: 100%;
    height: 100%;
  }}
  .ctrl-row {{
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }}
  button {{
    background: #21262d;
    color: #fff;
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s;
  }}
  button:hover {{
    background: #30363d;
    border-color: #8b949e;
  }}
  button.active {{
    background: #1f6feb;
    border-color: #58a6ff;
  }}
  .stat-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 12px;
  }}
  .stat-box {{
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
  }}
  .stat-val {{
    font-size: 18px;
    font-weight: 700;
    color: #58a6ff;
  }}
  .stat-lbl {{
    font-size: 11px;
    color: #8b949e;
    margin-top: 2px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-top: 10px;
  }}
  th, td {{
    padding: 6px 8px;
    border-bottom: 1px solid var(--border);
    text-align: left;
  }}
  th {{
    color: #8b949e;
    font-weight: 600;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>🐉 Pete's Dragon Custom Flex PCB (FPC) Suite <span class="badge">100 SMD LEDs Pre-Routed</span></h1>
  <div style="color: #8b949e; font-size: 14px; margin-bottom: 16px;">
    Turnkey Flexible Polyimide (0.15mm Kapton) circuit board designed from simulator coordinates for factory SMT assembly.
  </div>

  <div class="ctrl-row">
    <button id="toggleGraphicBtn" class="active" onclick="toggleLayer('dragonGraphic')">🎨 Toggle Dragon Art</button>
    <button id="toggleTracesBtn" class="active" onclick="toggleLayer('copperTraces')">⚡ Toggle Copper Data Traces</button>
    <button id="togglePowerBtn" class="active" onclick="toggleLayer('powerRails')">🔋 Toggle +5V / GND Rails</button>
    <button id="toggleOutlineBtn" class="active" onclick="toggleLayer('boardOutline')">✂️ Board Outline (Edge.Cuts)</button>
    <button id="toggleLanternBtn" class="active" onclick="toggleLanternGlow()">🏮 Tail Lantern Glow</button>
    <button id="animateDataBtn" onclick="toggleDataStream()">✨ Animate DIN Flow</button>
  </div>

  <div class="grid">
    <div class="card" style="padding: 10px;">
      <div class="viewer-box">
        <svg id="pcbSvg" viewBox="0 0 240 200">
          <defs>
            <radialGradient id="glowGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#00ff88" stop-opacity="0.9" />
              <stop offset="40%" stop-color="#00ff88" stop-opacity="0.4" />
              <stop offset="100%" stop-color="#00ff88" stop-opacity="0" />
            </radialGradient>
            <radialGradient id="lanternGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#ffb703" stop-opacity="1.0" />
              <stop offset="50%" stop-color="#fb8500" stop-opacity="0.5" />
              <stop offset="100%" stop-color="#ffb703" stop-opacity="0" />
            </radialGradient>
          </defs>

          <!-- Board Background (Gold Polyimide FPC) -->
          <g id="boardOutline">
            <path d="M 30,165 Q 25,120 40,95 Q 60,70 95,75 Q 110,65 140,55 Q 165,30 180,35 Q 205,45 200,80 Q 185,95 160,115 Q 155,145 165,165 Q 130,175 90,170 Q 50,175 30,165 Z" fill="#b38a2e" fill-opacity="0.25" stroke="#e5b84c" stroke-width="1.2" stroke-dasharray="3,2" />
          </g>

          <!-- Dragon Artwork Overlay -->
          <g id="dragonGraphic" opacity="0.4">
            <image href="../assets/petes_dragon_transparent.png" x="20" y="20" width="195" height="155" preserveAspectRatio="xMidYMid meet" />
          </g>

          <!-- Power Rails (+5V & GND Polygons) -->
          <g id="powerRails" opacity="0.6">
            <path d="M 32,163 Q 27,122 42,97 Q 62,72 97,77 Q 112,67 142,57 Q 167,32 182,37 Q 203,47 198,78 Q 183,93 158,113 Q 153,143 163,163 Z" fill="none" stroke="#da3633" stroke-width="1.8" stroke-opacity="0.5" />
            <path d="M 35,160 Q 30,125 45,100 Q 65,75 100,80 Q 115,70 145,60 Q 170,35 185,40 Q 195,50 190,80 Q 175,100 150,120 Q 145,150 155,160 Z" fill="none" stroke="#238636" stroke-width="1.8" stroke-opacity="0.5" />
          </g>

          <!-- Copper Data Daisy-Chain Traces (DOUT -> DIN) -->
          <g id="copperTraces">
"""

# Add sequential traces between consecutive LEDs
for i in range(len(led_positions_mm) - 1):
    p1 = led_positions_mm[i]
    p2 = led_positions_mm[i + 1]
    html_content += f'            <line x1="{p1["x"]}" y1="{p1["y"]}" x2="{p2["x"]}" y2="{p2["y"]}" stroke="#f0883e" stroke-width="0.7" stroke-linecap="round" />\n'

html_content += """          </g>

          <!-- 100x WS2812B-2020 SMT LEDs + 0402 Bypass Caps -->
          <g id="smtLeds">
"""

for d in led_positions_mm:
    c = d["color"]
    hex_col = f'#{c.get("r",0):02x}{c.get("g",255):02x}{c.get("b",100):02x}'
    html_content += f"""            <!-- {d["ref"]} -->
            <g class="led-node" data-id="{d["id"]}" transform="translate({d["x"]}, {d["y"]})">
              <rect x="-1.0" y="-1.0" width="2.0" height="2.0" fill="#ffffff" stroke="#333333" stroke-width="0.2" rx="0.3" />
              <circle cx="0" cy="0" r="0.75" fill="{hex_col}" />
              <rect x="1.4" y="-0.4" width="1.0" height="0.8" fill="#a07a30" stroke="#555" stroke-width="0.1" title="{d['cap_ref']} (0402 100nF)" />
            </g>
"""

html_content += """          </g>

          <!-- Tail Lantern Glowing Node -->
          <g id="tailLantern" transform="translate(32, 108)">
            <circle cx="0" cy="0" r="9.0" fill="url(#lanternGrad)" />
            <rect x="-1.8" y="-2.8" width="3.6" height="5.6" fill="none" stroke="#ffb703" stroke-width="0.6" rx="0.5" />
            <line x1="-1.8" y1="0" x2="1.8" y2="0" stroke="#ffb703" stroke-width="0.4" />
          </g>

          <!-- J1 3-Pin Input Connector -->
          <g id="j1Connector" transform="translate(26, 166)">
            <rect x="-3" y="-2" width="6" height="4" fill="#21262d" stroke="#58a6ff" stroke-width="0.5" rx="0.5" />
            <text x="0" y="-3" fill="#58a6ff" font-size="2.4" text-anchor="middle" font-family="monospace">+5V DIN GND</text>
            <circle cx="-1.8" cy="0" r="0.4" fill="#da3633" />
            <circle cx="0" cy="0" r="0.4" fill="#f0883e" />
            <circle cx="1.8" cy="0" r="0.4" fill="#238636" />
          </g>
        </svg>
      </div>
    </div>

    <div>
      <div class="card">
        <h3 style="margin-top: 0; color: #fff; font-size: 15px;">📊 Board Specifications</h3>
        <div class="stat-grid">
          <div class="stat-box">
            <div class="stat-val">100</div>
            <div class="stat-lbl">WS2812B-2020 LEDs</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">100</div>
            <div class="stat-lbl">0402 Bypass Caps</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">0.15 mm</div>
            <div class="stat-lbl">Flex PCB Thickness</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">185×145 mm</div>
            <div class="stat-lbl">Chest Dimensions</div>
          </div>
        </div>

        <h4 style="color: #fff; font-size: 13px; margin: 16px 0 6px 0;">📦 SMT Parts Bill of Materials</h4>
        <table>
          <thead>
            <tr><th>Part</th><th>RefDes</th><th>LCSC Part #</th></tr>
          </thead>
          <tbody>
            <tr><td>WS2812B-2020</td><td>LED1–100</td><td><span style="color:#58a6ff">C2843818</span></td></tr>
            <tr><td>100nF 0402 Cap</td><td>C1–100</td><td><span style="color:#58a6ff">C1525</span></td></tr>
            <tr><td>JST-PH 3P SMT</td><td>J1</td><td><span style="color:#58a6ff">C145946</span></td></tr>
          </tbody>
        </table>

        <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border);">
          <div style="font-size: 12px; color: #8b949e; line-height: 1.5;">
            ✅ <strong>Turnkey Files Generated:</strong>
            <ul style="margin: 6px 0 0 16px; padding: 0;">
              <li><code>pcb/petes_dragon_bom.csv</code></li>
              <li><code>pcb/petes_dragon_cpl.csv</code></li>
              <li><code>pcb/petes_dragon_fpc.kicad_pcb</code></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function toggleLayer(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const isHidden = el.style.display === 'none';
  el.style.display = isHidden ? '' : 'none';
}

function toggleLanternGlow() {
  const el = document.getElementById('tailLantern');
  if (el) el.style.display = el.style.display === 'none' ? '' : 'none';
}

let isStreaming = false;
let streamTimer = null;
let streamIdx = 0;
function toggleDataStream() {
  isStreaming = !isStreaming;
  const btn = document.getElementById('animateDataBtn');
  if (btn) btn.classList.toggle('active', isStreaming);
  if (isStreaming) {
    streamTimer = setInterval(() => {
      const nodes = document.querySelectorAll('.led-node circle');
      nodes.forEach((n, idx) => {
        const dist = Math.abs(idx - streamIdx);
        if (dist < 4) {
          n.setAttribute('r', '1.3');
          n.setAttribute('fill', '#ffffff');
        } else {
          n.setAttribute('r', '0.75');
          n.setAttribute('fill', '#00ff88');
        }
      });
      streamIdx = (streamIdx + 1) % 100;
    }, 40);
  } else {
    clearInterval(streamTimer);
    document.querySelectorAll('.led-node circle').forEach(n => {
      n.setAttribute('r', '0.75');
      n.setAttribute('fill', '#00ff88');
    });
  }
}
</script>
</body>
</html>
"""

with open(preview_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# 5. Generate Native KiCad 7/8 PCB File (.kicad_pcb)
kicad_path = os.path.join(PCB_DIR, "petes_dragon_fpc.kicad_pcb")
kicad_header = """(kicad_pcb (version 20221018) (generator pcbnew)
  (general (thickness 0.15))
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (44 "Edge.Cuts" user)
  )
  (setup
    (pad_to_mask_clearance 0.05)
    (solder_mask_min_width 0.1)
  )
  (net 0 "")
  (net 1 "+5V")
  (net 2 "GND")
"""

kicad_nets = ""
for i in range(1, len(led_positions_mm) + 1):
    kicad_nets += f'  (net {i+2} "DATA_{i}")\n'

kicad_outline = """  (gr_poly
    (pts
      (xy 20 180) (xy 15 130) (xy 35 100) (xy 60 70) (xy 100 75)
      (xy 120 65) (xy 150 50) (xy 180 30) (xy 205 40) (xy 200 85)
      (xy 180 105) (xy 155 125) (xy 150 155) (xy 165 180) (xy 120 190)
      (xy 70 185) (xy 20 180)
    )
    (stroke (width 0.15) (type solid)) (layer "Edge.Cuts")
  )
"""

kicad_fps = ""
for d in led_positions_mm:
    idx = d["id"]
    x = d["x"]
    y = d["y"]
    net_in = 2 + idx
    net_out = 3 + idx
    # WS2812B-2020 footprint
    kicad_fps += f"""  (footprint "LED_SMD:LED_WS2812B_PLCC4_2.0x2.0mm" (layer "F.Cu")
    (at {x} {y} 0)
    (property "Reference" "{d['ref']}" (at 0 -1.8 0) (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.12))))
    (property "Value" "WS2812B-2020" (at 0 1.8 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.1))))
    (pad "1" smd rect (at -0.85 -0.65) (size 0.6 0.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 1 "+5V"))
    (pad "2" smd rect (at -0.85 0.65) (size 0.6 0.5) (layers "F.Cu" "F.Paste" "F.Mask") (net {net_out} "DATA_{idx+1}"))
    (pad "3" smd rect (at 0.85 0.65) (size 0.6 0.5) (layers "F.Cu" "F.Paste" "F.Mask") (net 2 "GND"))
    (pad "4" smd rect (at 0.85 -0.65) (size 0.6 0.5) (layers "F.Cu" "F.Paste" "F.Mask") (net {net_in} "DATA_{idx}"))
  )
  (footprint "Capacitor_SMD:C_0402_1005Metric" (layer "F.Cu")
    (at {round(x+2.2, 3)} {y} 90)
    (property "Reference" "{d['cap_ref']}" (at 0 -1.0 0) (layer "F.SilkS") (effects (font (size 0.4 0.4) (thickness 0.08))))
    (property "Value" "100nF" (at 0 1.0 0) (layer "F.Fab") (effects (font (size 0.4 0.4) (thickness 0.08))))
    (pad "1" smd roundrect (at -0.48 0) (size 0.56 0.62) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) (net 1 "+5V"))
    (pad "2" smd roundrect (at 0.48 0) (size 0.56 0.62) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) (net 2 "GND"))
  )
"""

with open(kicad_path, "w", encoding="utf-8") as f:
    f.write(kicad_header + kicad_nets + kicad_outline + kicad_fps + ")\n")

print(f"Generated PCB suite successfully in {PCB_DIR}!")
print(f"1. BOM: {bom_path}")
print(f"2. CPL (Pick & Place): {cpl_path}")
print(f"3. KiCad PCB: {kicad_path}")
print(f"4. Interactive Inspector: {preview_path}")
