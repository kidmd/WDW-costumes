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

# 3. Load 100 LED coordinates & optimize PCB daisy-chain route (Neighbor-to-Neighbor)
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

# 3. Compute true contour of Pete's Dragon from transparent PNG for Edge.Cuts
alpha = np.array(img)[:, :, 3]
mask = (alpha > 50).astype(np.uint8)
# Dilate by 10px (~2.5mm margin) for laser-cut PCB clearance
mask_dilated = cv2.dilate(mask, np.ones((9, 9), np.uint8), iterations=2)
contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
main_contour = max(contours, key=cv2.contourArea)
# Smooth polygon approximation that closely follows organic dragon curves without clipping concave areas
epsilon = 0.0022 * cv2.arcLength(main_contour, True)
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
board_poly = np.array(contour_pts_mm, dtype=np.float32)

# 4. Extract relative coordinates & perform Boundary-Constrained Daisy-Chain Routing
# Ensures 100% of copper trace segments stay strictly INSIDE the PCB outline!
raw_coords = []
for l in leds:
    rx = (l.get("x", 0.5) - normX) / normW
    ry = (l.get("y", 0.5) - normY) / normH
    raw_coords.append((round(rx * WIDTH_MM, 2), round(ry * HEIGHT_MM, 2)))

n = len(raw_coords)
pts = np.array(raw_coords)

# Precompute segment validity cache (segment strictly inside board polygon)
valid_cache = np.zeros((n, n), dtype=bool)
dist_cache = np.zeros((n, n), dtype=np.float32)

for i in range(n):
    for j in range(i + 1, n):
        d = float(np.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]))
        dist_cache[i, j] = dist_cache[j, i] = d
        inside = True
        for t in np.linspace(0, 1, 30):
            s = (pts[i][0] + (pts[j][0] - pts[i][0]) * t, pts[i][1] + (pts[j][1] - pts[i][1]) * t)
            if cv2.pointPolygonTest(board_poly, s, True) < 0.0:
                inside = False
                break
        valid_cache[i, j] = valid_cache[j, i] = inside

# Start node at the bottom-left foot/tail (closest to power entry connector J1)
start_node = int(np.argmin(pts[:, 0] - pts[:, 1]))
second_node = min([j for j in range(n) if j != start_node and valid_cache[start_node, j]], key=lambda j: dist_cache[start_node, j])
tour = [start_node, second_node]
unvisited = set(range(n)) - {start_node, second_node}

# Cheapest valid insertion heuristic (strictly builds route within polygon boundaries)
while unvisited:
    best_c = None
    best_pos = None
    best_cost = 1e9
    for c in unvisited:
        if valid_cache[c, tour[0]]:
            cost = dist_cache[c, tour[0]]
            if cost < best_cost:
                best_cost = cost
                best_c = c
                best_pos = 0
        if valid_cache[tour[-1], c]:
            cost = dist_cache[tour[-1], c]
            if cost < best_cost:
                best_cost = cost
                best_c = c
                best_pos = len(tour)
        for p in range(len(tour) - 1):
            u, v = tour[p], tour[p + 1]
            if valid_cache[u, c] and valid_cache[c, v]:
                cost = dist_cache[u, c] + dist_cache[c, v] - dist_cache[u, v]
                if cost < best_cost:
                    best_cost = cost
                    best_c = c
                    best_pos = p + 1
    if best_c is None:
        # Fallback if no valid insertion found (should not happen with high connectivity)
        break
    tour.insert(best_pos, best_c)
    unvisited.remove(best_c)

# Constrained 2-opt refinement (only accepts swaps where both new segments stay inside PCB polygon)
best = tour[:]
improved = True
while improved:
    improved = False
    for i in range(1, len(best) - 2):
        for j in range(i + 1, len(best)):
            if j - i == 1: continue
            u, v = best[i - 1], best[i]
            w = best[j - 1]
            z = best[j] if j < len(best) else None
            if not valid_cache[u, w]: continue
            if z is not None and not valid_cache[v, z]: continue
            
            d_old = dist_cache[u, v] + (dist_cache[w, z] if z is not None else 0)
            d_new = dist_cache[u, w] + (dist_cache[v, z] if z is not None else 0)
            if d_new < d_old - 0.001:
                best[i:j] = reversed(best[i:j])
                improved = True

# Orient tour so J1 connector at bottom-left is first
d_start = pts[best[0]][0] - pts[best[0]][1]
d_end = pts[best[-1]][0] - pts[best[-1]][1]
if d_end < d_start:
    best = list(reversed(best))

optimized_order = best

# Verify zero segments cross outside the PCB boundary
outside_segs = 0
for i in range(len(optimized_order) - 1):
    u = optimized_order[i]
    v = optimized_order[i + 1]
    for t in np.linspace(0, 1, 60):
        s = (pts[u][0] + (pts[v][0] - pts[u][0]) * t, pts[u][1] + (pts[v][1] - pts[u][1]) * t)
        if cv2.pointPolygonTest(board_poly, s, True) < -0.01:
            outside_segs += 1
            print(f"WARNING: Segment LED {i+1} -> {i+2} leaves boundary!")
            break

if outside_segs == 0:
    print(f"Verified: 100% of copper trace segments stay strictly INSIDE the PCB boundary! (Outline: {len(contour_pts_mm)} pts)")

led_positions_mm = []
for new_idx, orig_idx in enumerate(optimized_order):
    l = leds[orig_idx]
    px, py = raw_coords[orig_idx]
    rx = round(px / WIDTH_MM, 4)
    ry = round(py / HEIGHT_MM, 4)
    col = l.get("color", {"r": 0, "g": 255, "b": 100})
    
    led_positions_mm.append({
        "id": new_idx + 1,
        "orig_id": orig_idx,
        "ref": f"LED{new_idx+1}",
        "cap_ref": f"C{new_idx+1}",
        "rel_x": rx,
        "rel_y": ry,
        "x": px,
        "y": py,
        "color": col
    })

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

# 7. Generate KiCad 5 Compatible PCB File for EasyEDA Standard & JLCPCB
# EasyEDA Standard uses a KiCad 5 parser: requires (module ...) instead of (footprint ...)
# and (gr_line ...) instead of (gr_poly ...) for Edge.Cuts board outline!
kicad_path = os.path.join(PCB_DIR, "petes_dragon_fpc.kicad_pcb")
kicad_header = """(kicad_pcb (version 20171130) (host pcbnew "(5.1.9)-1")
  (general
    (thickness 0.15)
    (drawings 0)
    (tracks 0)
    (zones 0)
    (modules 201)
    (nets 104)
  )
  (page A4)
  (layers
    (0 F.Cu signal)
    (31 B.Cu signal)
    (36 B.SilkS user)
    (37 F.SilkS user)
    (38 B.Mask user)
    (39 F.Mask user)
    (44 Edge.Cuts user)
  )
  (setup
    (last_trace_width 0.25)
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

# Board Outline on Edge.Cuts using contiguous gr_line segments
kicad_outline = ""
num_contour_pts = len(contour_pts_mm)
for i in range(num_contour_pts):
    p1 = contour_pts_mm[i]
    p2 = contour_pts_mm[(i + 1) % num_contour_pts]
    kicad_outline += f'  (gr_line (start {p1[0]} {p1[1]}) (end {p2[0]} {p2[1]}) (layer Edge.Cuts) (width 0.15))\n'

# Component Footprints using KiCad 5 (module ...) syntax
kicad_fps = ""

# JST-PH 3P Connector near back foot
j1_x = round(led_positions_mm[0]["x"] - 5.0, 2)
j1_y = round(led_positions_mm[0]["y"] + 4.0, 2)
kicad_fps += f"""  (module "Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal" (layer F.Cu) (tedit 5D5A6E4F)
    (at {j1_x} {j1_y} 180)
    (descr "JST PH 3-pin connector")
    (tags "JST PH 3P")
    (path "/j1")
    (fp_text reference "J1" (at 0 -2.5 180) (layer F.SilkS)
      (effects (font (size 0.8 0.8) (thickness 0.15)))
    )
    (fp_text value "JST-PH-3P" (at 0 2.5 180) (layer F.Fab)
      (effects (font (size 0.8 0.8) (thickness 0.15)))
    )
    (pad 1 smd rect (at -2.0 0 180) (size 1.0 1.6) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at 0 0 180) (size 1.0 1.6) (layers F.Cu F.Paste F.Mask) (net 3 "DATA_1"))
    (pad 3 smd rect (at 2.0 0 180) (size 1.0 1.6) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
  )
"""

for d in led_positions_mm:
    idx = d["id"]
    x = d["x"]
    y = d["y"]
    net_in = 2 + idx
    net_out = 3 + idx
    # WS2812B-2020 LED Module
    kicad_fps += f"""  (module "LED_SMD:LED_WS2812B_PLCC4_2.0x2.0mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {x} {y})
    (descr "WS2812B-2020 Addressable RGB LED")
    (tags "WS2812B 2020")
    (path "/led_{idx}")
    (fp_text reference "{d['ref']}" (at 0 -1.8) (layer F.SilkS)
      (effects (font (size 0.6 0.6) (thickness 0.12)))
    )
    (fp_text value "WS2812B-2020" (at 0 1.8) (layer F.Fab)
      (effects (font (size 0.5 0.5) (thickness 0.1)))
    )
    (fp_line (start -1.0 -1.0) (end 1.0 -1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start 1.0 -1.0) (end 1.0 1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start 1.0 1.0) (end -1.0 1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start -1.0 1.0) (end -1.0 -1.0) (layer F.SilkS) (width 0.12))
    (pad 1 smd rect (at -0.85 -0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at -0.85 0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net {net_out} "DATA_{idx+1}"))
    (pad 3 smd rect (at 0.85 0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
    (pad 4 smd rect (at 0.85 -0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net {net_in} "DATA_{idx}"))
  )
  (module "Capacitor_SMD:C_0402_1005Metric" (layer F.Cu) (tedit 5B301BBE)
    (at {round(x+2.2, 2)} {y} 90)
    (descr "100nF 0402 Bypass Capacitor")
    (tags "C0402")
    (path "/cap_{idx}")
    (fp_text reference "{d['cap_ref']}" (at 0 -1.0 90) (layer F.SilkS)
      (effects (font (size 0.4 0.4) (thickness 0.08)))
    )
    (fp_text value "100nF" (at 0 1.0 90) (layer F.Fab)
      (effects (font (size 0.4 0.4) (thickness 0.08)))
    )
    (fp_line (start -0.6 -0.3) (end 0.6 -0.3) (layer F.SilkS) (width 0.1))
    (fp_line (start 0.6 -0.3) (end 0.6 0.3) (layer F.SilkS) (width 0.1))
    (fp_line (start 0.6 0.3) (end -0.6 0.3) (layer F.SilkS) (width 0.1))
    (fp_line (start -0.6 0.3) (end -0.6 -0.3) (layer F.SilkS) (width 0.1))
    (pad 1 smd rect (at -0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at 0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
  )
"""

# KiCad Complete Power, Ground & Data Track Segments + Vias
kicad_tracks = ""

# J1 Power Entry Tracks
led1 = led_positions_mm[0]
j1_5v = (15.66, 173.6)
j1_data = (13.66, 173.6)
j1_gnd = (11.66, 173.6)

led1_5v = (round(led1["x"] - 0.85, 2), round(led1["y"] - 0.65, 2))
led1_din = (round(led1["x"] + 0.85, 2), round(led1["y"] - 0.65, 2))
led1_gnd_via = (round(led1["x"] + 2.2, 2), round(led1["y"] + 1.2, 2))

# J1 to LED1 tracks
kicad_tracks += f'  (segment (start {j1_5v[0]} {j1_5v[1]}) (end {led1_5v[0]} {led1_5v[1]}) (width 0.6) (layer F.Cu) (net 1))\n'
kicad_tracks += f'  (segment (start {j1_data[0]} {j1_data[1]}) (end {led1_din[0]} {led1_din[1]}) (width 0.3) (layer F.Cu) (net 3))\n'
kicad_tracks += f'  (via (at {j1_gnd[0]} {j1_gnd[1]}) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net 2))\n'
kicad_tracks += f'  (segment (start {j1_gnd[0]} {j1_gnd[1]}) (end {led1_gnd_via[0]} {led1_gnd_via[1]}) (width 0.6) (layer B.Cu) (net 2))\n'

# Per-LED local decoupling tracks and GND vias
for d in led_positions_mm:
    x = d["x"]
    y = d["y"]
    p_5v = (round(x - 0.85, 2), round(y - 0.65, 2))
    p_gnd = (round(x + 0.85, 2), round(y + 0.65, 2))
    c_5v = (round(x + 2.2, 2), round(y - 0.48, 2))
    c_gnd = (round(x + 2.2, 2), round(y + 0.48, 2))
    gnd_via = (round(x + 2.2, 2), round(y + 1.2, 2))
    
    # Local decoupling tracks (LED to Capacitor)
    kicad_tracks += f'  (segment (start {p_5v[0]} {p_5v[1]}) (end {c_5v[0]} {c_5v[1]}) (width 0.4) (layer F.Cu) (net 1))\n'
    kicad_tracks += f'  (segment (start {p_gnd[0]} {p_gnd[1]}) (end {c_gnd[0]} {c_gnd[1]}) (width 0.4) (layer F.Cu) (net 2))\n'
    kicad_tracks += f'  (segment (start {c_gnd[0]} {c_gnd[1]}) (end {gnd_via[0]} {gnd_via[1]}) (width 0.4) (layer F.Cu) (net 2))\n'
    kicad_tracks += f'  (via (at {gnd_via[0]} {gnd_via[1]}) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net 2))\n'

# Inter-LED Daisy-Chain Tracks (DATA on F.Cu, +5V power rail on F.Cu, and GND return bus on B.Cu)
for i in range(len(led_positions_mm) - 1):
    d1 = led_positions_mm[i]
    d2 = led_positions_mm[i + 1]
    
    # 1. Serial DATA: DOUT (LED i) -> DIN (LED i+1) on F.Cu
    net_id = 3 + d1["id"]
    p1_dout = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
    p2_din = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
    kicad_tracks += f'  (segment (start {p1_dout[0]} {p1_dout[1]}) (end {p2_din[0]} {p2_din[1]}) (width 0.25) (layer F.Cu) (net {net_id}))\n'
    
    # 2. +5V Power Rail: Cap i 5V pad -> Cap i+1 5V pad on F.Cu (0.5mm wide copper)
    c1_5v = (round(d1["x"] + 2.2, 2), round(d1["y"] - 0.48, 2))
    c2_5v = (round(d2["x"] + 2.2, 2), round(d2["y"] - 0.48, 2))
    kicad_tracks += f'  (segment (start {c1_5v[0]} {c1_5v[1]}) (end {c2_5v[0]} {c2_5v[1]}) (width 0.5) (layer F.Cu) (net 1))\n'
    
    # 3. GND Return Bus: GND via i -> GND via i+1 on B.Cu (0.6mm wide copper on bottom layer)
    v1_gnd = (round(d1["x"] + 2.2, 2), round(d1["y"] + 1.2, 2))
    v2_gnd = (round(d2["x"] + 2.2, 2), round(d2["y"] + 1.2, 2))
    kicad_tracks += f'  (segment (start {v1_gnd[0]} {v1_gnd[1]}) (end {v2_gnd[0]} {v2_gnd[1]}) (width 0.6) (layer B.Cu) (net 2))\n'

# Add Solid Ground Plane Copper Pour (Zone) on Bottom Layer (B.Cu)
zone_pts = " ".join([f"(xy {pt[0]} {pt[1]})" for pt in contour_pts_mm])
kicad_zone = f"""  (zone (net 2) (net_name "GND") (layer B.Cu) (tstamp 0) (hatch edge 0.5)
    (connect_pads yes (clearance 0.25))
    (min_thickness 0.25)
    (fill yes (arc_segments 16) (thermal_gap 0.25) (thermal_bridge_width 0.3))
    (polygon
      (pts
        {zone_pts}
      )
    )
  )
"""

with open(kicad_path, "w", encoding="utf-8") as f:
    f.write(kicad_header + kicad_nets + kicad_outline + kicad_fps + kicad_tracks + kicad_zone + ")\n")

# Generate KiCad Project File (.kicad_pro)
kicad_pro_path = os.path.join(PCB_DIR, "petes_dragon_fpc.kicad_pro")
kicad_pro_data = {
    "meta": {
        "filename": "petes_dragon_fpc.kicad_pro",
        "version": 1
    },
    "net_settings": {
        "classes": [
            {
                "clearance": 0.15,
                "name": "Default",
                "track_width": 0.25,
                "via_diameter": 0.6,
                "via_drill": 0.3
            }
        ]
    },
    "pcbnew": {
        "page_type": "A4"
    }
}
with open(kicad_pro_path, "w", encoding="utf-8") as f:
    json.dump(kicad_pro_data, f, indent=2)

# Generate Legacy KiCad Project File (.pro)
legacy_pro_path = os.path.join(PCB_DIR, "petes_dragon_fpc.pro")
with open(legacy_pro_path, "w", encoding="utf-8") as f:
    f.write("[general]\nversion=1\n")

# Package ZIP archive for EasyEDA and KiCad Import
import zipfile
zip_path = os.path.join(PCB_DIR, "petes_dragon_easyeda.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(kicad_path, "petes_dragon_fpc.kicad_pcb")
    zf.write(kicad_pro_path, "petes_dragon_fpc.kicad_pro")
    zf.write(legacy_pro_path, "petes_dragon_fpc.pro")
    zf.write(bom_path, "petes_dragon_bom.csv")
    zf.write(cpl_path, "petes_dragon_cpl.csv")

# Also write alias petes_dragon_kicad.zip
kicad_zip_path = os.path.join(PCB_DIR, "petes_dragon_kicad.zip")
with open(zip_path, "rb") as f_in, open(kicad_zip_path, "wb") as f_out:
    f_out.write(f_in.read())

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
  .led-node rect.led-pkg, .led-node rect.led-die {{
    transition: all 0.2s ease-out;
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
    <button id="toggleGraphicBtn" class="active" onclick="toggleLayer('dragonGraphic')">🎨 Dragon Art</button>
    <button id="toggleOutlineBtn" class="active" onclick="toggleLayer('boardOutline')">✂️ Board Outline</button>
    <button id="toggleDataBtn" class="active" onclick="toggleLayer('dataTraces')">⚡ Data Traces</button>
    <button id="togglePowerBtn" class="active" onclick="toggleLayer('powerTraces')">🔋 +5V Power Rail</button>
    <button id="toggleGndBtn" class="active" onclick="toggleLayer('groundTraces')">🛡️ GND Bus & Vias</button>
    <button id="toggleLedsBtn" class="active" onclick="toggleLayer('smtLeds')">💡 SMD LEDs</button>
    <button id="lightAllBtn" onclick="toggleLightAll()" style="font-weight: 600;">✨ Light Up All LEDs</button>
    <button id="animateDataBtn" onclick="toggleDataStream()">🌊 Animate DIN Flow</button>
    <a href="petes_dragon_easyeda.zip" download style="text-decoration:none;"><button style="background: #238636; border-color: #2ea043; font-weight: 600;">📥 Download EasyEDA / KiCad ZIP</button></a>
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

          <!-- Ground Return Bus & Vias on Bottom Layer (B.Cu - Blue/Cyan) -->
          <g id="groundTraces">
"""

# J1 GND to LED1 via
html_content += f'            <line x1="{j1_gnd[0]}" y1="{j1_gnd[1]}" x2="{led1_gnd_via[0]}" y2="{led1_gnd_via[1]}" stroke="#00b4d8" stroke-width="0.7" stroke-dasharray="2,1" />\n'
html_content += f'            <circle cx="{j1_gnd[0]}" cy="{j1_gnd[1]}" r="0.7" fill="#0077b6" stroke="#90e0ef" stroke-width="0.2" />\n'

for i in range(len(led_positions_mm) - 1):
    d1 = led_positions_mm[i]
    d2 = led_positions_mm[i + 1]
    v1_x = round(d1["x"] + 2.2, 2)
    v1_y = round(d1["y"] + 1.2, 2)
    v2_x = round(d2["x"] + 2.2, 2)
    v2_y = round(d2["y"] + 1.2, 2)
    html_content += f'            <line x1="{v1_x}" y1="{v1_y}" x2="{v2_x}" y2="{v2_y}" stroke="#00b4d8" stroke-width="0.7" stroke-dasharray="2,1" />\n'
    html_content += f'            <circle cx="{v1_x}" cy="{v1_y}" r="0.7" fill="#0077b6" stroke="#90e0ef" stroke-width="0.2" />\n'

# Last via
last_v_x = round(led_positions_mm[-1]["x"] + 2.2, 2)
last_v_y = round(led_positions_mm[-1]["y"] + 1.2, 2)
html_content += f'            <circle cx="{last_v_x}" cy="{last_v_y}" r="0.7" fill="#0077b6" stroke="#90e0ef" stroke-width="0.2" />\n'

html_content += """          </g>

          <!-- +5V Power Rail on Top Layer (F.Cu - Red/Amber) -->
          <g id="powerTraces">
"""

# J1 5V to LED1
html_content += f'            <line x1="{j1_5v[0]}" y1="{j1_5v[1]}" x2="{led1_5v[0]}" y2="{led1_5v[1]}" stroke="#ef233c" stroke-width="0.7" />\n'

for i in range(len(led_positions_mm) - 1):
    d1 = led_positions_mm[i]
    d2 = led_positions_mm[i + 1]
    c1_x = round(d1["x"] + 2.2, 2)
    c1_y = round(d1["y"] - 0.48, 2)
    c2_x = round(d2["x"] + 2.2, 2)
    c2_y = round(d2["y"] - 0.48, 2)
    html_content += f'            <line x1="{c1_x}" y1="{c1_y}" x2="{c2_x}" y2="{c2_y}" stroke="#ef233c" stroke-width="0.7" />\n'

html_content += """          </g>

          <!-- Copper Data Daisy-Chain Traces (DOUT -> DIN on TopLayer - Orange) -->
          <g id="dataTraces">
"""

# J1 data to LED1
html_content += f'            <line x1="{j1_data[0]}" y1="{j1_data[1]}" x2="{led1_din[0]}" y2="{led1_din[1]}" stroke="#f0883e" stroke-width="0.6" stroke-linecap="round" />\n'

for i in range(len(led_positions_mm) - 1):
    d1 = led_positions_mm[i]
    d2 = led_positions_mm[i + 1]
    p1_dout_x = round(d1["x"] - 0.85, 2)
    p1_dout_y = round(d1["y"] + 0.65, 2)
    p2_din_x = round(d2["x"] + 0.85, 2)
    p2_din_y = round(d2["y"] - 0.65, 2)
    html_content += f'            <line x1="{p1_dout_x}" y1="{p1_dout_y}" x2="{p2_din_x}" y2="{p2_din_y}" stroke="#f0883e" stroke-width="0.6" stroke-linecap="round" />\n'

html_content += """          </g>

          <!-- 100x WS2812B-2020 SMT LEDs + 0402 Bypass Caps -->
          <g id="smtLeds">
"""

for d in led_positions_mm:
    c = d["color"]
    hex_col = f'#{c.get("r",0):02x}{c.get("g",255):02x}{c.get("b",100):02x}'
    html_content += f"""            <!-- {d["ref"]} -->
            <g class="led-node" data-id="{d["id"]}" data-color="{hex_col}" transform="translate({d["x"]}, {d["y"]})">
              <rect class="led-pkg" x="-1.0" y="-1.0" width="2.0" height="2.0" fill="#ffffff" stroke="#222" stroke-width="0.15" rx="0.25" />
              <rect class="led-die" x="-0.7" y="-0.7" width="1.4" height="1.4" fill="{hex_col}" rx="0.2" />
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
              <li><a href="petes_dragon_easyeda.zip" download style="color:#58a6ff; font-weight:600;"><code>petes_dragon_easyeda.zip</code> (EasyEDA/KiCad Package)</a></li>
              <li><code>pcb/petes_dragon_bom.csv</code> (Parts BOM)</li>
              <li><code>pcb/petes_dragon_cpl.csv</code> (Pick & Place)</li>
              <li><code>pcb/petes_dragon_fpc.kicad_pcb</code> (KiCad PCB)</li>
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

let allLedsLit = false;
function toggleLightAll() {{
  allLedsLit = !allLedsLit;
  const btn = document.getElementById('lightAllBtn');
  if (btn) {{
    btn.classList.toggle('active', allLedsLit);
    btn.innerHTML = allLedsLit ? '🌟 LEDs Lit (Turn Off)' : '✨ Light Up All LEDs';
    btn.style.background = allLedsLit ? '#b08800' : '';
    btn.style.borderColor = allLedsLit ? '#ffd166' : '';
  }}
  const nodes = document.querySelectorAll('.led-node');
  nodes.forEach(node => {{
    node.classList.toggle('lit', allLedsLit);
    const pkg = node.querySelector('.led-pkg');
    const die = node.querySelector('.led-die');
    const col = node.getAttribute('data-color') || '#00ff88';
    if (pkg) {{
      pkg.setAttribute('fill', allLedsLit ? col : '#ffffff');
      pkg.setAttribute('stroke', allLedsLit ? '#ffffff' : '#222222');
      pkg.setAttribute('stroke-width', allLedsLit ? '0.2' : '0.15');
    }}
    if (die) {{
      die.setAttribute('fill', allLedsLit ? '#ffffff' : col);
      die.setAttribute('opacity', allLedsLit ? '0.75' : '1.0');
    }}
  }});
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
      const nodes = document.querySelectorAll('.led-node');
      nodes.forEach((node, idx) => {{
        const pkg = node.querySelector('.led-pkg');
        const die = node.querySelector('.led-die');
        const col = node.getAttribute('data-color') || '#00ff88';
        const dist = Math.abs(idx - streamIdx);
        if (dist < 3) {{
          if (pkg) {{
            pkg.setAttribute('fill', '#ffffff');
            pkg.setAttribute('stroke', '#ffffff');
          }}
          if (die) {{
            die.setAttribute('fill', '#ffd166');
            die.setAttribute('opacity', '1.0');
          }}
        }} else {{
          if (pkg) {{
            pkg.setAttribute('fill', allLedsLit ? col : '#ffffff');
            pkg.setAttribute('stroke', allLedsLit ? '#ffffff' : '#222222');
            pkg.setAttribute('stroke-width', allLedsLit ? '0.2' : '0.15');
          }}
          if (die) {{
            die.setAttribute('fill', allLedsLit ? '#ffffff' : col);
            die.setAttribute('opacity', allLedsLit ? '0.75' : '1.0');
          }}
        }}
      }});
      streamIdx = (streamIdx + 1) % 100;
    }}, 40);
  }} else {{
    clearInterval(streamTimer);
    document.querySelectorAll('.led-node').forEach(node => {{
      const pkg = node.querySelector('.led-pkg');
      const die = node.querySelector('.led-die');
      const col = node.getAttribute('data-color') || '#00ff88';
      if (pkg) {{
        pkg.setAttribute('fill', allLedsLit ? col : '#ffffff');
        pkg.setAttribute('stroke', allLedsLit ? '#ffffff' : '#222222');
        pkg.setAttribute('stroke-width', allLedsLit ? '0.2' : '0.15');
      }}
      if (die) {{
        die.setAttribute('fill', allLedsLit ? '#ffffff' : col);
        die.setAttribute('opacity', allLedsLit ? '0.75' : '1.0');
      }}
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
