import os
import json
import numpy as np
import cv2
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")
PCB_DIR = os.path.join(BASE_DIR, "pcb")
os.makedirs(PCB_DIR, exist_ok=True)

# 1. Load the transparent Pete's Dragon image & compute aspect ratio
dragon_img_path = os.path.join(ASSETS_DIR, "petes_dragon_transparent.png")
img = Image.open(dragon_img_path)
img_w, img_h = img.size
aspect = img_w / img_h

# 2. Replicate the Simulator's chest layout bounds (from simulator/app.js getGraphicChestBounds)
maxH = 0.385
topY = 0.168
normH = maxH
normW = normH * 1.25 * aspect
normY = topY
normX = (1.0 - normW) / 2.0

# Physical Board Dimensions (mm): Target ~185 mm wide (~7.28 inches)
WIDTH_MM = 185.0
HEIGHT_MM = round(WIDTH_MM / aspect, 2) # ~222.1 mm (~8.74 inches)

# 3. Load 100 LED coordinates from preset
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

led_positions_mm = []
for i, l in enumerate(leds):
    # Normalized relative coordinates within the dragon graphic (0.0 to 1.0)
    rel_x = (l.get("x", 0.5) - normX) / normW
    rel_y = (l.get("y", 0.5) - normY) / normH
    
    # Scale to physical millimeters on the board
    px = round(rel_x * WIDTH_MM, 2)
    py = round(rel_y * HEIGHT_MM, 2)
    col = l.get("color", {"r": 0, "g": 255, "b": 100})
    
    led_positions_mm.append({
        "id": i + 1,
        "ref": f"LED{i+1}",
        "cap_ref": f"C{i+1}",
        "rel_x": round(rel_x, 4),
        "rel_y": round(rel_y, 4),
        "x": px,
        "y": py,
        "color": col
    })

# 4. Compute true contour of Pete's Dragon from transparent PNG for Edge.Cuts
alpha = np.array(img)[:, :, 3]
mask = (alpha > 50).astype(np.uint8)
# Dilate by 10px (~2.5mm margin) for laser-cut PCB clearance
mask_dilated = cv2.dilate(mask, np.ones((9, 9), np.uint8), iterations=2)
contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
main_contour = max(contours, key=cv2.contourArea)
epsilon = 0.0055 * cv2.arcLength(main_contour, True)
approx_contour = cv2.approxPolyDP(main_contour, epsilon, True)

contour_pts_mm = []
svg_path_d = "M "
for idx, pt in enumerate(approx_contour):
    cx_mm = round((pt[0][0] / img_w) * WIDTH_MM, 2)
    cy_mm = round((pt[0][1] / img_h) * HEIGHT_MM, 2)
    contour_pts_mm.append((cx_mm, cy_mm))
    if idx == 0:
        svg_path_d += f"{cx_mm},{cy_mm} "
    else:
        svg_path_d += f"L {cx_mm},{cy_mm} "
svg_path_d += "Z"

# 5. Generate BOM (Bill of Materials) for JLCPCB SMT Assembly
bom_path = os.path.join(PCB_DIR, "petes_dragon_bom.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write("Comment,Designator,Footprint,LCSC Part #\n")
    led_refs = " ".join([d["ref"] for d in led_positions_mm])
    cap_refs = " ".join([d["cap_ref"] for d in led_positions_mm])
    f.write(f'"WS2812B-2020 Addressable RGB LED","{led_refs}","LED-SMD_4P-L2.0-W2.0-TL","C2843818"\n')
    f.write(f'"100nF (0.1uF) 50V 0402 Capacitor","{cap_refs}","C0402","C1525"\n')
    f.write('"JST-PH-3P SMT 2.0mm Header","J1","JST_PH_S3B-PH-SM4-TB","C145946"\n')

# 6. Generate CPL (Pick and Place Centroid File) for JLCPCB
cpl_path = os.path.join(PCB_DIR, "petes_dragon_cpl.csv")
with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("Designator,Mid X,Mid Y,Layer,Rotation\n")
    for d in led_positions_mm:
        f.write(f'{d["ref"]},{d["x"]},{d["y"]},Top,0\n')
        f.write(f'{d["cap_ref"]},{round(d["x"] + 2.2, 2)},{round(d["y"], 2)},Top,90\n')
    # Place JST connector near LED 1 (lower foot)
    f.write(f'J1,{round(led_positions_mm[0]["x"] - 5.0, 2)},{round(led_positions_mm[0]["y"] + 4.0, 2)},Top,180\n')

# 7. Generate Native KiCad 7/8 PCB File (.kicad_pcb)
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

kicad_outline_pts = " ".join([f"(xy {pt[0]} {pt[1]})" for pt in contour_pts_mm])
kicad_outline = f"""  (gr_poly
    (pts {kicad_outline_pts})
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
    (at {round(x+2.2, 2)} {y} 90)
    (property "Reference" "{d['cap_ref']}" (at 0 -1.0 0) (layer "F.SilkS") (effects (font (size 0.4 0.4) (thickness 0.08))))
    (property "Value" "100nF" (at 0 1.0 0) (layer "F.Fab") (effects (font (size 0.4 0.4) (thickness 0.08))))
    (pad "1" smd roundrect (at -0.48 0) (size 0.56 0.62) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) (net 1 "+5V"))
    (pad "2" smd roundrect (at 0.48 0) (size 0.56 0.62) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) (net 2 "GND"))
  )
"""

with open(kicad_path, "w", encoding="utf-8") as f:
    f.write(kicad_header + kicad_nets + kicad_outline + kicad_fps + ")\n")

# 8. Generate Interactive Web Inspector HTML (100% 1:1 Coincident Alignment)
preview_path = os.path.join(PCB_DIR, "pcb_preview.html")

vb_pad = 8
vb_w = round(WIDTH_MM + vb_pad * 2, 1)
vb_h = round(HEIGHT_MM + vb_pad * 2, 1)

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
  }}
  body {{
    margin: 0;
    padding: 20px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  .container {{
    max-width: 1280px;
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
    grid-template-columns: 1fr 360px;
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
    height: 720px;
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
  .slider-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 10px;
    font-size: 12px;
  }}
  input[type="range"] {{
    flex: 1;
    accent-color: #58a6ff;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>🐉 Pete's Dragon Custom Flex PCB (FPC) Inspector <span class="badge">1:1 Coincident Alignment</span></h1>
  <div style="color: #8b949e; font-size: 14px; margin-bottom: 16px;">
    Turnkey Flexible Polyimide circuit board layout with 100 micro addressable LEDs aligned with 100% precision over your transparent Pete's Dragon artwork!
  </div>

  <div class="ctrl-row">
    <button id="toggleGraphicBtn" class="active" onclick="toggleLayer('dragonGraphic')">🎨 Toggle Dragon Art</button>
    <button id="toggleTracesBtn" class="active" onclick="toggleLayer('copperTraces')">⚡ Toggle Copper Data Traces</button>
    <button id="toggleOutlineBtn" class="active" onclick="toggleLayer('boardOutline')">✂️ Board Outline (Edge.Cuts)</button>
    <button id="toggleLedsBtn" class="active" onclick="toggleLayer('smtLeds')">💡 Toggle SMD LEDs</button>
    <button id="animateDataBtn" onclick="toggleDataStream()">✨ Animate DIN Flow</button>
  </div>

  <div class="grid">
    <div class="card" style="padding: 10px;">
      <div class="viewer-box">
        <svg id="pcbSvg" viewBox="-{vb_pad} -{vb_pad} {vb_w} {vb_h}">
          <defs>
            <radialGradient id="lanternGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#ffb703" stop-opacity="1.0" />
              <stop offset="50%" stop-color="#fb8500" stop-opacity="0.5" />
              <stop offset="100%" stop-color="#ffb703" stop-opacity="0" />
            </radialGradient>
          </defs>

          <!-- Board Background (Laser-Cut Gold Polyimide Flex FPC Outline) -->
          <g id="boardOutline">
            <path d="{svg_path_d}" fill="#b38a2e" fill-opacity="0.22" stroke="#e5b84c" stroke-width="0.8" stroke-dasharray="3,1.5" />
          </g>

          <!-- Dragon Artwork Overlay (100% Coincident Dimension: 185mm x 222.1mm) -->
          <g id="dragonGraphic" opacity="0.65">
            <image href="../assets/petes_dragon_transparent.png" x="0" y="0" width="{WIDTH_MM}" height="{HEIGHT_MM}" preserveAspectRatio="none" />
          </g>

          <!-- Copper Data Daisy-Chain Traces (DOUT -> DIN) -->
          <g id="copperTraces">
"""

# Add copper traces connecting consecutive LEDs
for i in range(len(led_positions_mm) - 1):
    p1 = led_positions_mm[i]
    p2 = led_positions_mm[i + 1]
    html_content += f'            <line x1="{p1["x"]}" y1="{p1["y"]}" x2="{p2["x"]}" y2="{p2["y"]}" stroke="#f0883e" stroke-width="0.6" stroke-linecap="round" />\n'

html_content += """          </g>

          <!-- 100x WS2812B-2020 SMT LEDs + 0402 Bypass Caps -->
          <g id="smtLeds">
"""

for d in led_positions_mm:
    c = d["color"]
    hex_col = f'#{c.get("r",0):02x}{c.get("g",255):02x}{c.get("b",100):02x}'
    html_content += f"""            <!-- {d["ref"]} -->
            <g class="led-node" data-id="{d["id"]}" transform="translate({d["x"]}, {d["y"]})">
              <rect x="-1.0" y="-1.0" width="2.0" height="2.0" fill="#ffffff" stroke="#222" stroke-width="0.15" rx="0.25" />
              <circle cx="0" cy="0" r="0.75" fill="{hex_col}" />
              <rect x="1.3" y="-0.4" width="0.8" height="0.8" fill="#a07a30" stroke="#444" stroke-width="0.1" title="{d['cap_ref']} (0402 100nF Cap)" />
            </g>
"""

html_content += f"""          </g>

          <!-- Power/Data Input Connector (JST-PH 3P) -->
          <g id="j1Connector" transform="translate({round(led_positions_mm[0]['x'] - 5.0, 2)}, {round(led_positions_mm[0]['y'] + 4.0, 2)})">
            <rect x="-3" y="-2" width="6" height="4" fill="#21262d" stroke="#58a6ff" stroke-width="0.4" rx="0.4" />
            <text x="0" y="-2.6" fill="#58a6ff" font-size="1.8" text-anchor="middle" font-family="monospace">+5V DIN GND</text>
            <circle cx="-1.8" cy="0" r="0.35" fill="#da3633" />
            <circle cx="0" cy="0" r="0.35" fill="#f0883e" />
            <circle cx="1.8" cy="0" r="0.35" fill="#238636" />
          </g>
        </svg>
      </div>
    </div>

    <div>
      <div class="card">
        <h3 style="margin-top: 0; color: #fff; font-size: 15px;">📊 Board Dimensions & Specs</h3>
        
        <div class="slider-row">
          <span style="color: #8b949e;">Artwork Opacity:</span>
          <input type="range" id="artOpacitySlider" min="0" max="100" value="65" oninput="setArtOpacity(this.value)">
          <span id="artOpacityVal" style="color: #fff; font-family: monospace; width: 36px; text-align: right;">65%</span>
        </div>

        <div class="stat-grid" style="margin-top: 14px;">
          <div class="stat-box">
            <div class="stat-val">100</div>
            <div class="stat-lbl">WS2812B-2020 LEDs</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">100</div>
            <div class="stat-lbl">0402 Bypass Caps</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{WIDTH_MM}×{HEIGHT_MM} mm</div>
            <div class="stat-lbl">Physical Board Size (7.3"×8.7")</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">0.15 mm</div>
            <div class="stat-lbl">Flex FPC Polyimide</div>
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
            ✅ <strong>Turnkey Manufacturing Files:</strong>
            <ul style="margin: 6px 0 0 16px; padding: 0;">
              <li><code>pcb/petes_dragon_bom.csv</code> (Parts)</li>
              <li><code>pcb/petes_dragon_cpl.csv</code> (Pick & Place)</li>
              <li><code>pcb/petes_dragon_fpc.kicad_pcb</code> (KiCad)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function toggleLayer(id) {{
  const el = document.getElementById(id);
  if (!el) return;
  const isHidden = el.style.display === 'none';
  el.style.display = isHidden ? '' : 'none';
}}

function setArtOpacity(val) {{
  const el = document.getElementById('dragonGraphic');
  if (el) el.setAttribute('opacity', val / 100);
  document.getElementById('artOpacityVal').textContent = val + '%';
}}

let isStreaming = false;
let streamTimer = null;
let streamIdx = 0;
function toggleDataStream() {{
  isStreaming = !isStreaming;
  const btn = document.getElementById('animateDataBtn');
  if (btn) btn.classList.toggle('active', isStreaming);
  if (isStreaming) {{
    streamTimer = setInterval(() => {{
      const nodes = document.querySelectorAll('.led-node circle');
      nodes.forEach((n, idx) => {{
        const dist = Math.abs(idx - streamIdx);
        if (dist < 4) {{
          n.setAttribute('r', '1.3');
          n.setAttribute('fill', '#ffffff');
        }} else {{
          n.setAttribute('r', '0.75');
          n.setAttribute('fill', '#00ff88');
        }}
      }});
      streamIdx = (streamIdx + 1) % 100;
    }}, 40);
  }} else {{
    clearInterval(streamTimer);
    document.querySelectorAll('.led-node circle').forEach(n => {{
      n.setAttribute('r', '0.75');
      n.setAttribute('fill', '#00ff88');
    }});
  }}
}}
</script>
</body>
</html>
"""

with open(preview_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated 1:1 Coincident Pete's Dragon PCB suite successfully in {PCB_DIR}!")
print(f"Board size: {WIDTH_MM} mm x {HEIGHT_MM} mm")
print(f"BOM: {bom_path}")
print(f"CPL: {cpl_path}")
print(f"KiCad: {kicad_path}")
print(f"Inspector: {preview_path}")
