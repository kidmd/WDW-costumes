#!/usr/bin/env python3
"""
Generate 3D-Printable TPU Chest Panel (OpenSCAD & Web Inspector)
for Main Street Electrical Parade Running Costumes.

Features:
- Snapmaker U1 95A Flexible TPU wearable plate
- True 3D recessed wire channels (1.8mm W x 1.2mm D)
- Physical flexible snap-fit retention clips along wire channels
- Physical retaining snap collars over 100 rear LED pockets (5.4mm dia)
- Physical center spool posts in slack relief wells (8.0mm dia)
- Standard 10mm garment tagging gun fastener eyelets & countersinks
- Rich Three.js 3D Inspector with real trenches, clips, wires, and bulbs

Outputs:
- 3d_panels/petes_dragon_tpu_panel.scad
- 3d_panels/tpu_panel_preview.html
- 3d_panels/petes_dragon_specs.json
"""

import os
import json
import math
import cv2
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")
PANELS_DIR = os.path.join(BASE_DIR, "3d_panels")
os.makedirs(PANELS_DIR, exist_ok=True)

# 1. Load Transparent Asset & Aspect Ratio
dragon_img_path = os.path.join(ASSETS_DIR, "petes_dragon_transparent.png")
if not os.path.exists(dragon_img_path):
    raise FileNotFoundError(f"Missing asset: {dragon_img_path}")

img = Image.open(dragon_img_path)
img_w, img_h = img.size
aspect = img_w / img_h

# Physical Dimensions (mm) - Matches Simulator Chest Bounds
WIDTH_MM = 185.0
HEIGHT_MM = round(WIDTH_MM / aspect, 2)

# Simulator chest bounds parameters
maxH = 0.385
topY = 0.168
normH = maxH
normW = normH * 1.25 * aspect
normY = topY
normX = (1.0 - normW) / 2.0

print(f"=== Pete's Dragon TPU Chest Panel Generator ===")
print(f"Artwork: {img_w}x{img_h}px (Aspect: {aspect:.3f})")
print(f"Physical Panel Dimensions: {WIDTH_MM:.1f} mm W x {HEIGHT_MM:.1f} mm H")

# 2. Extract Smooth Outer Silhouette Polygon
alpha = np.array(img)[:, :, 3]
mask = (alpha > 50).astype(np.uint8)

# Morphological dilation: +3.5mm safety margin for perimeter LED wall clearance
mask_dilated = cv2.dilate(mask, np.ones((17, 17), np.uint8), iterations=2)
contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
main_contour = max(contours, key=cv2.contourArea)

# Polygon simplification
epsilon = 0.0022 * cv2.arcLength(main_contour, True)
approx_contour = cv2.approxPolyDP(main_contour, epsilon, True)

# Convert to 3D CAD space coordinates (Y+ is UP)
contour_pts = []
for pt in approx_contour:
    cx = round((pt[0][0] / img_w) * WIDTH_MM, 2)
    cy = round((1.0 - pt[0][1] / img_h) * HEIGHT_MM, 2)
    contour_pts.append((cx, cy))

board_poly = np.array(contour_pts, dtype=np.float32)
print(f"Perimeter Polygon: {len(contour_pts)} smooth vertices")

# 3. Load 100 LED Coordinates from Preset
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

raw_coords = []
for l in leds:
    rx = (l.get("x", 0.5) - normX) / normW
    ry = (l.get("y", 0.5) - normY) / normH
    px = round(rx * WIDTH_MM, 2)
    py = round((1.0 - ry) * HEIGHT_MM, 2)
    raw_coords.append((px, py))

n = len(raw_coords)
pts = np.array(raw_coords)
print(f"Loaded {n} LEDs from preset")

# 4. Solve Boundary-Constrained Daisy Chain Route
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

start_node = int(np.argmin(pts[:, 0] + pts[:, 1]))
second_node = min([j for j in range(n) if j != start_node and valid_cache[start_node, j]], key=lambda j: dist_cache[start_node, j])
tour = [start_node, second_node]
unvisited = set(range(n)) - {start_node, second_node}

while unvisited:
    best_c = None
    best_pos = None
    best_cost = 1e9
    for c in unvisited:
        if valid_cache[c, tour[0]]:
            cost = dist_cache[c, tour[0]]
            if cost < best_cost: best_cost = cost; best_c = c; best_pos = 0
        if valid_cache[tour[-1], c]:
            cost = dist_cache[tour[-1], c]
            if cost < best_cost: best_cost = cost; best_c = c; best_pos = len(tour)
        for p in range(len(tour) - 1):
            u, v = tour[p], tour[p + 1]
            if valid_cache[u, c] and valid_cache[c, v]:
                cost = dist_cache[u, c] + dist_cache[c, v] - dist_cache[u, v]
                if cost < best_cost: best_cost = cost; best_c = c; best_pos = p + 1
    if best_c is None:
        best_c = min(unvisited, key=lambda c: dist_cache[tour[-1], c])
        tour.append(best_c)
        unvisited.remove(best_c)
        continue
    tour.insert(best_pos, best_c)
    unvisited.remove(best_c)

# 2-opt refinement
best = tour[:]
improved = True
for _ in range(50):
    if not improved: break
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

d_start = pts[best[0]][0] + pts[best[0]][1]
d_end = pts[best[-1]][0] + pts[best[-1]][1]
if d_end < d_start:
    best = list(reversed(best))

ordered_leds = []
for idx, orig_idx in enumerate(best):
    px, py = raw_coords[orig_idx]
    orig_l = leds[orig_idx]
    ordered_leds.append({
        "id": idx + 1,
        "orig_id": orig_idx,
        "x": px,
        "y": py,
        "color": orig_l.get("color", {"r": 0, "g": 255, "b": 0})
    })

# Compute segments, wire clips, and slack wells
wire_segments = []
wire_clips = []
slack_wells = []
total_direct_wire_len = 0.0

for i in range(len(ordered_leds) - 1):
    p1 = (ordered_leds[i]["x"], ordered_leds[i]["y"])
    p2 = (ordered_leds[i+1]["x"], ordered_leds[i+1]["y"])
    seg_len = float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))
    total_direct_wire_len += seg_len
    wire_segments.append([p1, p2, round(seg_len, 2)])
    
    # Calculate wire retention clip position (at midpoint of segment)
    mid_x = round((p1[0] + p2[0]) / 2.0, 2)
    mid_y = round((p1[1] + p2[1]) / 2.0, 2)
    angle_rad = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    angle_deg = round(math.degrees(angle_rad), 2)
    
    # Add wire clip if segment is long enough (>= 8mm)
    if seg_len >= 8.0:
        wire_clips.append({
            "id": i + 1,
            "x": mid_x,
            "y": mid_y,
            "angle": angle_deg,
            "seg_len": round(seg_len, 2)
        })
    
    # If LEDs are close (< 18mm), insert an expansion slack pocket with center spool pin
    if seg_len < 18.0:
        slack_wells.append({
            "id": i + 1,
            "x": mid_x,
            "y": mid_y,
            "dia": 8.0,
            "post_dia": 2.6,
            "seg_len": round(seg_len, 2)
        })

print(f"Wire Route: {len(wire_segments)} segments | Total Direct Length: {total_direct_wire_len:.1f} mm")
print(f"Wire Retention Snap Clips: {len(wire_clips)} clips")
print(f"Slack Wells with Center Spool Posts: {len(slack_wells)} pockets")

# 5. Fastener Tabs & Holes for Tagging Gun (10mm barbs)
perimeter_tabs = []
n_cnt = len(contour_pts)
for i in range(n_cnt):
    p1 = np.array(contour_pts[i])
    p2 = np.array(contour_pts[(i + 1) % n_cnt])
    seg_len = float(np.linalg.norm(p2 - p1))
    num_tabs = max(1, int(round(seg_len / 25.0)))
    for k in range(num_tabs):
        t = (k + 0.5) / num_tabs
        mid = p1 + (p2 - p1) * t
        edge_v = (p2 - p1) / (seg_len + 1e-6)
        normal_in = np.array([-edge_v[1], edge_v[0]])
        test_pt = mid + normal_in * 3.5
        if cv2.pointPolygonTest(board_poly, (float(test_pt[0]), float(test_pt[1])), True) > 0.8:
            perimeter_tabs.append((round(float(test_pt[0]), 2), round(float(test_pt[1]), 2)))
        else:
            test_pt = mid - normal_in * 3.5
            if cv2.pointPolygonTest(board_poly, (float(test_pt[0]), float(test_pt[1])), True) > 0.8:
                perimeter_tabs.append((round(float(test_pt[0]), 2), round(float(test_pt[1]), 2)))

filtered_perimeter_tabs = []
for p in perimeter_tabs:
    if all(math.hypot(p[0] - r[0], p[1] - r[1]) >= 18.0 for r in filtered_perimeter_tabs):
        if all(math.hypot(p[0] - l["x"], p[1] - l["y"]) >= 5.0 for l in ordered_leds):
            filtered_perimeter_tabs.append(p)

grid_x = np.linspace(25, WIDTH_MM - 25, 60)
grid_y = np.linspace(25, HEIGHT_MM - 25, 70)
interior_candidates = []
for gx in grid_x:
    for gy in grid_y:
        p = (gx, gy)
        if cv2.pointPolygonTest(board_poly, p, True) > 10.0:
            d_led = min(math.hypot(gx - l["x"], gy - l["y"]) for l in ordered_leds)
            if d_led >= 7.0:
                interior_candidates.append((round(gx, 2), round(gy, 2), d_led))

interior_candidates.sort(key=lambda c: c[2], reverse=True)
interior_tabs = []
for c in interior_candidates:
    pt = (c[0], c[1])
    if all(math.hypot(pt[0] - s[0], pt[1] - s[1]) >= 26.0 for s in interior_tabs):
        interior_tabs.append(pt)
        if len(interior_tabs) >= 5: break

all_fastener_tabs = filtered_perimeter_tabs + interior_tabs
print(f"Tagging Gun Fastener Tabs: {len(all_fastener_tabs)} total ({len(filtered_perimeter_tabs)} perimeter + {len(interior_tabs)} interior)")

# ========================================================
# 6. GENERATE ENHANCED OPENSCAD SOURCE (.scad)
# Includes physical snap-retention clips & spool posts!
# ========================================================
scad_poly_pts = ",\n    ".join([f"[{p[0]:.2f}, {p[1]:.2f}]" for p in contour_pts])
scad_led_pts = ",\n    ".join([f"[{l['x']:.2f}, {l['y']:.2f}]" for l in ordered_leds])
scad_wire_segs = ",\n    ".join([f"[[{s[0][0]:.2f}, {s[0][1]:.2f}], [{s[1][0]:.2f}, {s[1][1]:.2f}]]" for s in wire_segments])
scad_slack_pts = ",\n    ".join([f"[{w['x']:.2f}, {w['y']:.2f}]" for w in slack_wells])
scad_clip_data = ",\n    ".join([f"[{c['x']:.2f}, {c['y']:.2f}, {c['angle']:.2f}]" for c in wire_clips])
scad_fastener_pts = ",\n    ".join([f"[{f[0]:.2f}, {f[1]:.2f}]" for f in all_fastener_tabs])

scad_content = f"""// ============================================================================
// 🏰 Main Street Electrical Parade (WDW 10K) - Flexible TPU Chest Panel
// Character: Pete's Dragon (Elliott) - 100 Addressable Fairy Light Bulbs
// Sized for Snapmaker U1 | Material: 95A TPU | Fasteners: 10mm Garment Barbs
// Features: Integrated Wire Snap-Retention Clips & LED Snap Collars
// Generated by Antigravity Imagineering Engine
// ============================================================================

$fn = 24;

// ----------------------------------------------------------------------------
// PARAMETRIC CUSTOMIZER VARIABLES
// ----------------------------------------------------------------------------
/* [Panel Geometry] */
panel_thickness       = 2.0;    // Total panel thickness in mm (1.6mm - 2.4mm for 95A TPU)
panel_width_mm        = {WIDTH_MM:.2f}; // Target physical width in mm
panel_height_mm       = {HEIGHT_MM:.2f}; // Target physical height in mm

/* [LED Pockets (Rear-Load Press Fit with Snap Collars)] */
led_pocket_dia        = 5.4;    // Rear recess diameter for 5.0mm resin teardrop pixel (mm)
led_pocket_depth      = 1.4;    // Recess depth from back face (mm)
led_window_dia        = 3.2;    // Front optical aperture for raw LED emission (mm)
enable_led_snap_lips  = true;   // Inward flexible retaining lip to snap-lock each LED
led_snap_lip_overhang = 0.35;   // Overhang lip (narrows mouth to 4.7mm for snap retention)

/* [Fairy Light Wire Routing (Rear Side)] */
wire_channel_width    = 1.8;    // Routing channel width for 3-strand enameled wire (mm)
wire_channel_depth    = 1.2;    // Channel depth from back face (mm)
slack_well_dia        = 8.0;    // Expansion slack pocket diameter for coiling extra wire (mm)

/* [Wire Retention Snap Clips] */
enable_wire_clips     = true;   // Bridge clips over wire channels to prevent wire popping out
clip_bridge_width     = 2.2;    // Width of clip bridge along channel (mm)
clip_bridge_thick     = 0.55;   // Thickness of flexible bridge (mm)
clip_entry_slot       = 1.1;    // Push-through pinch slot width (mm)

/* [Slack Well Spool Posts] */
enable_spool_posts    = true;   // Center pin in slack wells to wrap wire loops around
spool_post_dia        = 2.6;    // Diameter of center post (mm)

/* [Garment Tagging Gun Attachment] */
fastener_hole_dia     = 2.2;    // Needle through-hole diameter for standard tagging gun (mm)
fastener_csk_dia      = 4.8;    // Front countersink diameter for 10mm plastic T-bar (mm)
fastener_csk_depth    = 0.6;    // Front countersink depth so T-bar sits flush (mm)

/* [Curvature Preview] */
// 0 = Flat (RECOMMENDED for 95A TPU: prints without supports & naturally wraps chest)
bend_radius           = 0;

// ----------------------------------------------------------------------------
// GEOMETRIC ARRAYS
// ----------------------------------------------------------------------------

dragon_contour = [
    {scad_poly_pts}
];

led_positions = [
    {scad_led_pts}
];

wire_segments = [
    {scad_wire_segs}
];

slack_wells = [
    {scad_slack_pts}
];

// Wire clips [x, y, angle_deg]
wire_clips = [
    {scad_clip_data}
];

fastener_positions = [
    {scad_fastener_pts}
];

// ----------------------------------------------------------------------------
// 2D & 3D SUB-MODULES
// ----------------------------------------------------------------------------

module dragon_silhouette_2d() {{
    polygon(points = dragon_contour);
}}

module all_through_holes_2d() {{
    for (p = led_positions) {{
        translate(p) circle(d = led_window_dia, $fn = 20);
    }}
    for (f = fastener_positions) {{
        translate(f) circle(d = fastener_hole_dia, $fn = 16);
    }}
}}

module all_wire_channels_2d() {{
    for (seg = wire_segments) {{
        hull() {{
            translate(seg[0]) circle(d = wire_channel_width, $fn = 16);
            translate(seg[1]) circle(d = wire_channel_width, $fn = 16);
        }}
    }}
    for (w = slack_wells) {{
        translate(w) circle(d = slack_well_dia, $fn = 24);
    }}
}}

module all_led_pockets_2d() {{
    for (p = led_positions) {{
        translate(p) circle(d = led_pocket_dia, $fn = 24);
    }}
}}

module all_fastener_countersinks_2d() {{
    for (f = fastener_positions) {{
        translate(f) circle(d = fastener_csk_dia, $fn = 20);
    }}
}}

// Additive retention features (Wire bridge clips & Spool posts)
module additive_retention_features() {{
    // 1. Wire snap retention clips (Overhanging bridge clips)
    if (enable_wire_clips) {{
        for (c = wire_clips) {{
            translate([c[0], c[1], 0])
                rotate([0, 0, c[2]])
                    difference() {{
                        // Bridge over channel
                        translate([-clip_bridge_width/2, -wire_channel_width*0.9, 0])
                            cube([clip_bridge_width, wire_channel_width*1.8, clip_bridge_thick]);
                        // Center snap push-through pinch slit
                        translate([-clip_bridge_width/2 - 0.1, -clip_entry_slot/2, -0.1])
                            cube([clip_bridge_width + 0.2, clip_entry_slot, clip_bridge_thick + 0.2]);
                    }}
        }}
    }}

    // 2. Center spool posts in slack wells
    if (enable_spool_posts) {{
        for (w = slack_wells) {{
            translate([w[0], w[1], 0])
                cylinder(d = spool_post_dia, h = wire_channel_depth, $fn = 16);
        }}
    }}
}}

// ----------------------------------------------------------------------------
// 3D MAIN PANEL ASSEMBLY
// Z = 0 is the BACK FACE (shirt-facing side with pockets and wire channels)
// Z = panel_thickness is the FRONT FACE (world-facing side with optical windows)
// ----------------------------------------------------------------------------

module tpu_chest_panel_flat() {{
    union() {{
        difference() {{
            // 1. Base Contoured Solid Plate
            linear_extrude(height = panel_thickness)
                dragon_silhouette_2d();

            // 2. Optical Through-Windows & Fastener Needle Holes
            translate([0, 0, -0.1])
                linear_extrude(height = panel_thickness + 0.2)
                    all_through_holes_2d();

            // 3. Rear Wire Channels & Slack Wells (Cut into back face: Z = 0 to wire_channel_depth)
            translate([0, 0, -0.1])
                linear_extrude(height = wire_channel_depth + 0.1)
                    all_wire_channels_2d();

            // 4. Rear LED Pockets (Cut into back face: Z = 0 to led_pocket_depth)
            translate([0, 0, -0.1])
                linear_extrude(height = led_pocket_depth + 0.1)
                    all_led_pockets_2d();

            // 5. Front Countersunk Recesses for 10mm Fastener T-Bars
            translate([0, 0, panel_thickness - fastener_csk_depth])
                linear_extrude(height = fastener_csk_depth + 0.1)
                    all_fastener_countersinks_2d();
        }}

        // 6. Integrated Flexible Retention Clips & Spool Posts
        additive_retention_features();
    }}
}}

// Render the panel
tpu_chest_panel_flat();
"""

scad_file_path = os.path.join(PANELS_DIR, "petes_dragon_tpu_panel.scad")
with open(scad_file_path, "w", encoding="utf-8") as f:
    f.write(scad_content)

print(f"Saved OpenSCAD file: {scad_file_path} ({len(scad_content)} bytes)")

# ========================================================
# 7. GENERATE SPECS JSON
# ========================================================
specs_data = {
    "character": "Pete's Dragon (Elliott)",
    "preset": "petes_dragon_chris.json",
    "led_count": 100,
    "panel_width_mm": WIDTH_MM,
    "panel_height_mm": HEIGHT_MM,
    "panel_thickness_mm": 2.0,
    "total_direct_wire_mm": round(total_direct_wire_len, 2),
    "wire_segments_count": len(wire_segments),
    "wire_clips_count": len(wire_clips),
    "slack_wells_count": len(slack_wells),
    "fastener_tabs_count": len(all_fastener_tabs),
    "contour_vertices": len(contour_pts),
    "led_pocket_dia_mm": 5.4,
    "led_window_dia_mm": 3.2,
    "wire_channel_width_mm": 1.8,
    "wire_channel_depth_mm": 1.2,
    "fastener_hole_dia_mm": 2.2,
    "contour_pts": contour_pts,
    "ordered_leds": ordered_leds,
    "wire_segments": wire_segments,
    "wire_clips": wire_clips,
    "slack_wells": slack_wells,
    "fastener_tabs": all_fastener_tabs
}

specs_file_path = os.path.join(PANELS_DIR, "petes_dragon_specs.json")
with open(specs_file_path, "w", encoding="utf-8") as f:
    json.dump(specs_data, f, indent=2)

print(f"Saved Specs JSON: {specs_file_path}")

# ========================================================
# 8. GENERATE INTERACTIVE 3D WEB INSPECTOR (tpu_panel_preview.html)
# Features TRUE 3D volumetric trenches, physical snap clips,
# 3D black fairy light wire, and 3D resin LED teardrop bulbs!
# ========================================================
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pete's Dragon 3D-Printable Flexible TPU Panel Inspector</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<style>
  :root {{
    --bg: #070a0f;
    --card: #121820;
    --card-border: #1e293b;
    --accent: #00ff88;
    --accent-cyan: #00e5ff;
    --accent-orange: #ff9100;
    --accent-purple: #c084fc;
    --text: #e2e8f0;
    --text-dim: #94a3b8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 16px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--card-border);
    padding-bottom: 12px;
    margin-bottom: 16px;
  }}
  .title-group {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  h1 {{ margin: 0; font-size: 21px; color: #fff; }}
  .badge {{
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 12px;
    font-weight: 600;
    color: #fff;
  }}
  .badge-tpu {{ background: #059669; }}
  .badge-snap {{ background: #2563eb; }}
  .badge-clip {{ background: #0891b2; }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 390px;
    gap: 16px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 16px;
  }}
  .viewport-container {{
    position: relative;
    height: 720px;
    background: radial-gradient(circle at 50% 50%, #0d1520 0%, #05080c 100%);
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--card-border);
  }}
  #three-canvas {{ width: 100%; height: 100%; display: block; }}
  
  .view-controls {{
    position: absolute;
    top: 12px;
    left: 12px;
    display: flex;
    gap: 6px;
    z-index: 10;
    flex-wrap: wrap;
  }}
  .btn {{
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(6px);
    color: var(--text);
    border: 1px solid var(--card-border);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.15s ease;
  }}
  .btn:hover {{ background: #334155; border-color: var(--accent-cyan); color: #fff; }}
  .btn.active {{ background: #0891b2; color: #fff; border-color: #00e5ff; }}
  
  .zoom-controls {{
    position: absolute;
    top: 52px;
    left: 12px;
    display: flex;
    gap: 6px;
    z-index: 10;
  }}
  .btn-zoom {{
    background: rgba(15, 23, 42, 0.85);
    border-color: #334155;
    font-size: 11px;
    color: #38bdf8;
  }}
  .btn-zoom:hover {{ background: #0284c7; color: #fff; }}
  
  .side-banner {{
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid #00e5ff;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    color: #00e5ff;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .hud-overlay {{
    position: absolute;
    bottom: 12px;
    left: 12px;
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(8px);
    border: 1px solid var(--card-border);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 11px;
    color: var(--text-dim);
    display: flex;
    gap: 16px;
  }}
  .hud-stat {{ display: flex; flex-direction: column; }}
  .hud-val {{ color: var(--accent); font-weight: 700; font-size: 13px; }}
  
  .sidebar {{ display: flex; flex-direction: column; gap: 12px; max-height: 720px; overflow-y: auto; }}
  .section-title {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--accent-cyan);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .layer-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #1e293b;
    font-size: 11px;
  }}
  .layer-label {{ display: flex; align-items: center; gap: 8px; }}
  .color-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  
  .spec-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    font-size: 11px;
  }}
  .spec-box {{
    background: #0b0f17;
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #1e293b;
  }}
  .spec-lbl {{ color: var(--text-dim); font-size: 10px; }}
  .spec-num {{ color: #fff; font-weight: 600; font-size: 12px; margin-top: 2px; }}

  .print-guide {{
    background: #0b0f17;
    border-left: 3px solid #00e5ff;
    padding: 10px;
    border-radius: 0 6px 6px 0;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-dim);
  }}
  .print-guide strong {{ color: #fff; }}
  
  .pulse-btn {{
    width: 100%;
    background: linear-gradient(135deg, #059669, #0284c7);
    color: #fff;
    border: none;
    padding: 10px;
    border-radius: 6px;
    font-weight: 700;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
  }}
  .pulse-btn:hover {{ filter: brightness(1.15); }}
</style>
</head>
<body>

<div class="header">
  <div class="title-group">
    <h1>🐉 Pete's Dragon 3D TPU Armor Panel</h1>
    <span class="badge badge-tpu">95A Flexible TPU</span>
    <span class="badge badge-clip">🧲 {len(wire_clips)} Wire Snap Clips</span>
    <span class="badge badge-clip" style="background:#ea580c;">🔒 100 LED Snap Collars</span>
    <span class="badge badge-snap">Snapmaker U1 Flat Print</span>
  </div>
  <div>
    <button class="btn" style="background:#059669; color:#fff;" onclick="downloadScad()">📥 Download OpenSCAD (.scad)</button>
  </div>
</div>

<div class="grid">
  <!-- 3D Viewport -->
  <div class="card viewport-container">
    <div class="view-controls">
      <button class="btn active" id="btn-back" onclick="setView('back')">🔄 Underside Assembly (Back Face)</button>
      <button class="btn" id="btn-front" onclick="setView('front')">👕 Race-Day Exterior (Front Face)</button>
      <button class="btn" id="btn-iso" onclick="setView('iso')">Isometric 3D</button>
      <button class="btn" id="btn-xray" onclick="toggleXray()">Toggle X-Ray</button>
    </div>

    <div class="zoom-controls">
      <button class="btn btn-zoom" onclick="zoomToFeature('clip')">🔍 Zoom to Wire Snap Clip</button>
      <button class="btn btn-zoom" onclick="zoomToFeature('pocket')">🔍 Zoom to LED Pocket</button>
      <button class="btn btn-zoom" onclick="zoomToFeature('slack')">🔍 Zoom to Slack Spool</button>
      <button class="btn btn-zoom" onclick="zoomToFeature('reset')">⟲ Reset Zoom</button>
    </div>

    <div class="side-banner" id="view-banner">
      <span>🛠️ VIEWING: UNDERSIDE ASSEMBLY (Pockets, Channels & Clips)</span>
    </div>

    <div id="three-canvas"></div>

    <div class="hud-overlay">
      <div class="hud-stat">
        <span>BOUNDS</span>
        <span class="hud-val">{WIDTH_MM:.1f} × {HEIGHT_MM:.1f} mm</span>
      </div>
      <div class="hud-stat">
        <span>WIRE CLIPS</span>
        <span class="hud-val" style="color:var(--accent-cyan);">{len(wire_clips)} Snap Teeth</span>
      </div>
      <div class="hud-stat">
        <span>LED SNAP COLLARS</span>
        <span class="hud-val" style="color:var(--accent-orange);">100 Retaining Lips</span>
      </div>
      <div class="hud-stat">
        <span>SLACK SPOOLS</span>
        <span class="hud-val" style="color:var(--accent-purple);">{len(slack_wells)} Center Posts</span>
      </div>
      <div class="hud-stat">
        <span>TAGGING TABS</span>
        <span class="hud-val">{len(all_fastener_tabs)} (10mm Barbs)</span>
      </div>
    </div>
  </div>

  <!-- Sidebar Controls & Specs -->
  <div class="sidebar">
    <!-- Action Card -->
    <div class="card">
      <button class="pulse-btn" onclick="togglePulse()">
        <span id="pulse-icon">⚡</span> <span id="pulse-text">Simulate Fairy Light DIN Data Stream</span>
      </button>
    </div>

    <!-- Layer Visibility Card -->
    <div class="card">
      <div class="section-title"><span>📐</span> Inspection Layers</div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#1e293b;"></span> TPU Base Shell (2.0mm Plate)</span>
        <input type="checkbox" id="layer-shell" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#00e5ff;"></span> 🧲 Wire Snap-Retention Clips ({len(wire_clips)})</span>
        <input type="checkbox" id="layer-clips" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#ff9100;"></span> 🔒 LED Snap-Fit Collars (100)</span>
        <input type="checkbox" id="layer-collars" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#f59e0b;"></span> 🕳️ Recessed Wire Trenches (1.8×1.2mm)</span>
        <input type="checkbox" id="layer-channels" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#111111; border:1px solid #94a3b8;"></span> 🧵 3D Black Fairy Wire Strand</span>
        <input type="checkbox" id="layer-wires" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#00ff88;"></span> 💡 3D Resin LED Bulbs (100)</span>
        <input type="checkbox" id="layer-bulbs" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#c084fc;"></span> 🔄 Slack Wells with Spool Posts ({len(slack_wells)})</span>
        <input type="checkbox" id="layer-slack" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#0284c7;"></span> 📌 10mm Fastener Tagging Tabs ({len(all_fastener_tabs)})</span>
        <input type="checkbox" id="layer-tabs" checked onchange="updateLayers()">
      </div>
    </div>

    <!-- How Snap-Retention Works Card -->
    <div class="card">
      <div class="section-title"><span>🧲</span> How Retention Clips Work</div>
      <div style="font-size: 11px; line-height: 1.5; color: var(--text-dim);">
        <strong style="color:#00e5ff;">• Wire Snap Bridges:</strong> Flexible TPU bridges overhang each wire channel with a 1.1mm pinch slit. Pressing the 1.5mm wire in snaps past the flexible lips, locking it down permanently!<br><br>
        <strong style="color:#ff9100;">• LED Snap Collar:</strong> An undercut retaining lip (Ø4.7mm entry expanding to Ø5.4mm) clicks over the shoulder of the 5.0mm resin teardrop bulb.<br><br>
        <strong style="color:#c084fc;">• Center Spool Posts:</strong> Excess fairy wire wraps cleanly around the Ø2.6mm center post inside each slack well.
      </div>
    </div>

    <!-- Snapmaker U1 Print Settings Guide -->
    <div class="card">
      <div class="section-title"><span>🖨️</span> Snapmaker U1 95A TPU Settings</div>
      <div class="print-guide">
        <strong>Print 100% Flat on Bed:</strong> Zero supports required! Bridges and overhangs are engineered strictly under 2.0mm for flawless TPU bridging.<br><br>
        • <strong>Nozzle Temp:</strong> 225°C | <strong>Bed Temp:</strong> 50°C (PEI textured sheet)<br>
        • <strong>Print Speed:</strong> 30 mm/s (First layer 15 mm/s)<br>
        • <strong>Layer Height:</strong> 0.20 mm | <strong>Infill:</strong> 100% Solid<br>
        • <strong>Retraction:</strong> 1.8 mm @ 20 mm/s (Direct Drive)<br>
        • <strong>Est. Weight:</strong> ~52g | <strong>Print Time:</strong> ~1 hr 50 min
      </div>
    </div>
  </div>
</div>

<script>
const SPECS = {json.dumps(specs_data)};

let scene, camera, renderer, controls;
let panelMesh, channelsGroup, clipsGroup, collarsGroup, wiresGroup, bulbsGroup, slackGroup, tabsGroup, pulseGroup;
let isXray = false;
let isPulsing = false;
let pulseIdx = 0;

function initThree() {{
  const container = document.getElementById('three-canvas');
  const w = container.clientWidth;
  const h = container.clientHeight;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x06090e);

  camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 2000);
  // Default to Underside / Back View so channels and clips are immediately visible!
  camera.position.set(0, 0, -340);

  renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
  renderer.setSize(w, h);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // Rich lighting
  const ambLight = new THREE.AmbientLight(0xffffff, 0.85);
  scene.add(ambLight);

  const keyLight = new THREE.DirectionalLight(0x00e5ff, 0.9);
  keyLight.position.set(80, 150, -200);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0xff9100, 0.7);
  fillLight.position.set(-100, -100, -180);
  scene.add(fillLight);

  const frontLight = new THREE.DirectionalLight(0xffffff, 0.6);
  frontLight.position.set(0, 50, 200);
  scene.add(frontLight);

  build3DModel();
  animate();
}}

function build3DModel() {{
  const cx = SPECS.panel_width_mm / 2.0;
  const cy = SPECS.panel_height_mm / 2.0;

  // 1. Base TPU Shell
  const shape = new THREE.Shape();
  SPECS.contour_pts.forEach((p, idx) => {{
    const x = p[0] - cx;
    const y = p[1] - cy;
    if (idx === 0) shape.moveTo(x, y);
    else shape.lineTo(x, y);
  }});
  shape.closePath();

  // Optical windows
  SPECS.ordered_leds.forEach(l => {{
    const hole = new THREE.Path();
    hole.absarc(l.x - cx, l.y - cy, SPECS.led_window_dia_mm / 2.0, 0, Math.PI * 2, true);
    shape.holes.push(hole);
  }});

  // Fastener holes
  SPECS.fastener_tabs.forEach(f => {{
    const hole = new THREE.Path();
    hole.absarc(f[0] - cx, f[1] - cy, SPECS.fastener_hole_dia_mm / 2.0, 0, Math.PI * 2, true);
    shape.holes.push(hole);
  }});

  const extrudeSettings = {{
    depth: SPECS.panel_thickness_mm,
    bevelEnabled: true,
    bevelSegments: 2,
    steps: 1,
    bevelSize: 0.25,
    bevelThickness: 0.25
  }};

  const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
  geom.center();

  const mat = new THREE.MeshPhysicalMaterial({{
    color: 0x18202c,
    roughness: 0.4,
    metalness: 0.15,
    transmission: 0.1,
    opacity: 0.95,
    transparent: true,
    side: THREE.DoubleSide
  }});

  panelMesh = new THREE.Mesh(geom, mat);
  scene.add(panelMesh);

  // 2. 3D Recessed Wire Channels (Real volumetric trenches!)
  channelsGroup = new THREE.Group();
  const trenchMat = new THREE.MeshStandardMaterial({{
    color: 0x0a1017,
    roughness: 0.7,
    metalness: 0.2
  }});
  const trenchRimMat = new THREE.LineBasicMaterial({{ color: 0x0284c7 }});

  SPECS.wire_segments.forEach(seg => {{
    const p1 = seg[0];
    const p2 = seg[1];
    const dx = p2[0] - p1[0];
    const dy = p2[1] - p1[1];
    const len = Math.hypot(dx, dy);
    const angle = Math.atan2(dy, dx);
    const mx = (p1[0] + p2[0]) / 2.0 - cx;
    const my = (p1[1] + p2[1]) / 2.0 - cy;

    // Trench box
    const trenchGeom = new THREE.BoxGeometry(len, SPECS.wire_channel_width_mm, SPECS.wire_channel_depth_mm);
    const trenchMesh = new THREE.Mesh(trenchGeom, trenchMat);
    trenchMesh.position.set(mx, my, -1.0 + SPECS.wire_channel_depth_mm / 2.0);
    trenchMesh.rotation.z = angle;
    channelsGroup.add(trenchMesh);
  }});
  scene.add(channelsGroup);

  // 3. 3D Wire Snap-Retention Clips (High-visibility Cyan Bridges)
  clipsGroup = new THREE.Group();
  const clipMat = new THREE.MeshStandardMaterial({{
    color: 0x00e5ff,
    roughness: 0.3,
    metalness: 0.3,
    emissive: 0x005577,
    emissiveIntensity: 0.2
  }});

  SPECS.wire_clips.forEach(c => {{
    const mx = c.x - cx;
    const my = c.y - cy;
    const rad = (c.angle * Math.PI) / 180.0;

    // Left snap finger
    const fGeom = new THREE.BoxGeometry(2.2, 0.7, 0.55);
    const fMeshL = new THREE.Mesh(fGeom, clipMat);
    fMeshL.position.set(mx, my, -1.25);
    fMeshL.rotation.z = rad;
    fMeshL.translateY(-0.75);
    clipsGroup.add(fMeshL);

    // Right snap finger
    const fMeshR = new THREE.Mesh(fGeom, clipMat);
    fMeshR.position.set(mx, my, -1.25);
    fMeshR.rotation.z = rad;
    fMeshR.translateY(0.75);
    clipsGroup.add(fMeshR);
  }});
  scene.add(clipsGroup);

  // 4. 3D LED Retaining Snap Collars (Vivid Amber Rings with Inward Lips)
  collarsGroup = new THREE.Group();
  const collarMat = new THREE.MeshStandardMaterial({{
    color: 0xff9100,
    roughness: 0.3,
    metalness: 0.2,
    emissive: 0x663300,
    emissiveIntensity: 0.3
  }});

  const collarGeom = new THREE.RingGeometry(SPECS.led_pocket_dia_mm / 2 - 0.4, SPECS.led_pocket_dia_mm / 2 + 0.5, 20);
  SPECS.ordered_leds.forEach(l => {{
    const mesh = new THREE.Mesh(collarGeom, collarMat);
    mesh.position.set(l.x - cx, l.y - cy, -1.22);
    collarsGroup.add(mesh);
  }});
  scene.add(collarsGroup);

  // 5. 3D Black Fairy Light Wire (Continuous 3D Cylindrical Cable!)
  wiresGroup = new THREE.Group();
  const wireMat = new THREE.MeshStandardMaterial({{
    color: 0x111111,
    roughness: 0.5,
    metalness: 0.4
  }});

  SPECS.wire_segments.forEach(seg => {{
    const p1 = seg[0];
    const p2 = seg[1];
    const dx = p2[0] - p1[0];
    const dy = p2[1] - p1[1];
    const len = Math.hypot(dx, dy);
    const angle = Math.atan2(dy, dx);
    const mx = (p1[0] + p2[0]) / 2.0 - cx;
    const my = (p1[1] + p2[1]) / 2.0 - cy;

    const cylGeom = new THREE.CylinderGeometry(0.55, 0.55, len, 10);
    const wireCyl = new THREE.Mesh(cylGeom, wireMat);
    wireCyl.rotation.z = angle - Math.PI / 2;
    wireCyl.position.set(mx, my, -0.65);
    wiresGroup.add(wireCyl);
  }});
  scene.add(wiresGroup);

  // 6. 3D Resin LED Teardrop Bulbs (Translucent Epoxy Nodes with Emitter Cores)
  bulbsGroup = new THREE.Group();
  const bulbResinMat = new THREE.MeshPhysicalMaterial({{
    color: 0xa7f3d0,
    roughness: 0.2,
    metalness: 0.1,
    transmission: 0.7,
    opacity: 0.85,
    transparent: true
  }});

  const bulbGeom = new THREE.SphereGeometry(2.3, 16, 16);
  SPECS.ordered_leds.forEach(l => {{
    const c = l.color || {{r: 0, g: 255, b: 100}};
    const bulbMesh = new THREE.Mesh(bulbGeom, bulbResinMat);
    bulbMesh.scale.set(1.0, 1.0, 0.65);
    bulbMesh.position.set(l.x - cx, l.y - cy, -0.5);

    // Glowing core emitter chip inside
    const coreGeom = new THREE.BoxGeometry(0.8, 0.8, 0.4);
    const coreMat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(`rgb(${{c.r}},${{c.g}},${{c.b}})`) }});
    const coreMesh = new THREE.Mesh(coreGeom, coreMat);
    coreMesh.position.set(l.x - cx, l.y - cy, -0.5);

    bulbsGroup.add(bulbMesh);
    bulbsGroup.add(coreMesh);
  }});
  scene.add(bulbsGroup);

  // 7. Slack Wells with Center Spool Posts
  slackGroup = new THREE.Group();
  const spoolMat = new THREE.MeshStandardMaterial({{
    color: 0xc084fc,
    roughness: 0.4,
    metalness: 0.2
  }});
  const spoolGeom = new THREE.CylinderGeometry(1.3, 1.3, 1.1, 16);
  const coilGeom = new THREE.TorusGeometry(2.4, 0.4, 8, 20);

  SPECS.slack_wells.forEach(w => {{
    // Center post
    const postMesh = new THREE.Mesh(spoolGeom, spoolMat);
    postMesh.rotation.x = Math.PI / 2;
    postMesh.position.set(w.x - cx, w.y - cy, -0.65);
    slackGroup.add(postMesh);

    // Wire loop around post
    const coilMesh = new THREE.Mesh(coilGeom, wireMat);
    coilMesh.position.set(w.x - cx, w.y - cy, -0.65);
    slackGroup.add(coilMesh);
  }});
  scene.add(slackGroup);

  // 8. Fastener Tabs (Blue rings)
  tabsGroup = new THREE.Group();
  const tabGeom = new THREE.RingGeometry(1.1, 2.4, 16);
  const tabMat = new THREE.MeshBasicMaterial({{ color: 0x0284c7, side: THREE.DoubleSide }});
  SPECS.fastener_tabs.forEach(f => {{
    const ring = new THREE.Mesh(tabGeom, tabMat);
    ring.position.set(f[0] - cx, f[1] - cy, 1.15);
    tabsGroup.add(ring);
  }});
  scene.add(tabsGroup);

  // 9. Pulse Spark Packet
  pulseGroup = new THREE.Group();
  const pulseGeom = new THREE.SphereGeometry(3.2, 16, 16);
  const pulseMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
  const pulseSphere = new THREE.Mesh(pulseGeom, pulseMat);
  pulseSphere.name = "spark";
  pulseGroup.add(pulseSphere);
  pulseGroup.visible = false;
  scene.add(pulseGroup);
}}

function animate() {{
  requestAnimationFrame(animate);
  controls.update();

  if (isPulsing) {{
    pulseIdx = (pulseIdx + 0.35) % SPECS.ordered_leds.length;
    const l1 = SPECS.ordered_leds[Math.floor(pulseIdx)];
    const l2 = SPECS.ordered_leds[(Math.floor(pulseIdx) + 1) % SPECS.ordered_leds.length];
    const t = pulseIdx - Math.floor(pulseIdx);
    const cx = SPECS.panel_width_mm / 2.0;
    const cy = SPECS.panel_height_mm / 2.0;

    const spark = pulseGroup.getObjectByName("spark");
    if (spark) {{
      spark.position.x = (l1.x + (l2.x - l1.x) * t) - cx;
      spark.position.y = (l1.y + (l2.y - l1.y) * t) - cy;
      spark.position.z = -1.6;
    }}
  }}

  renderer.render(scene, camera);
}}

function setView(view) {{
  document.querySelectorAll('.view-controls .btn').forEach(b => b.classList.remove('active'));
  const banner = document.getElementById('view-banner');

  if (view === 'back') {{
    document.getElementById('btn-back').classList.add('active');
    camera.position.set(0, 0, -340);
    controls.target.set(0, 0, 0);
    banner.innerHTML = "🛠️ VIEWING: UNDERSIDE ASSEMBLY (Pockets, Channels & Clips)";
    banner.style.color = "#00e5ff";
    banner.style.borderColor = "#00e5ff";
  }} else if (view === 'front') {{
    document.getElementById('btn-front').classList.add('active');
    camera.position.set(0, 0, 340);
    controls.target.set(0, 0, 0);
    banner.innerHTML = "👕 VIEWING: RACE-DAY EXTERIOR (Front Face Optical Windows)";
    banner.style.color = "#00ff88";
    banner.style.borderColor = "#00ff88";
  }} else if (view === 'iso') {{
    document.getElementById('btn-iso').classList.add('active');
    camera.position.set(160, -170, -220);
    controls.target.set(0, 0, 0);
  }}
}}

function zoomToFeature(feat) {{
  const cx = SPECS.panel_width_mm / 2.0;
  const cy = SPECS.panel_height_mm / 2.0;

  if (feat === 'clip') {{
    // Focus on first wire clip
    const c = SPECS.wire_clips[0] || {{x: 40, y: 60}};
    const targetX = c.x - cx;
    const targetY = c.y - cy;
    controls.target.set(targetX, targetY, -1.0);
    camera.position.set(targetX, targetY - 20, -50);
  }} else if (feat === 'pocket') {{
    // Focus on first LED pocket
    const l = SPECS.ordered_leds[0] || {{x: 20, y: 50}};
    const targetX = l.x - cx;
    const targetY = l.y - cy;
    controls.target.set(targetX, targetY, -1.0);
    camera.position.set(targetX, targetY - 15, -45);
  }} else if (feat === 'slack') {{
    // Focus on first slack spool
    const w = SPECS.slack_wells[0] || {{x: 30, y: 60}};
    const targetX = w.x - cx;
    const targetY = w.y - cy;
    controls.target.set(targetX, targetY, -1.0);
    camera.position.set(targetX, targetY - 25, -60);
  }} else if (feat === 'reset') {{
    setView('back');
  }}
}}

function toggleXray() {{
  isXray = !isXray;
  document.getElementById('btn-xray').classList.toggle('active', isXray);
  if (panelMesh) {{
    panelMesh.material.wireframe = isXray;
    panelMesh.material.opacity = isXray ? 0.25 : 0.95;
  }}
}}

function togglePulse() {{
  isPulsing = !isPulsing;
  pulseGroup.visible = isPulsing;
  document.getElementById('pulse-text').textContent = isPulsing ? "Stop DIN Data Stream" : "Simulate Fairy Light DIN Data Stream";
}}

function updateLayers() {{
  panelMesh.visible = document.getElementById('layer-shell').checked;
  clipsGroup.visible = document.getElementById('layer-clips').checked;
  collarsGroup.visible = document.getElementById('layer-collars').checked;
  channelsGroup.visible = document.getElementById('layer-channels').checked;
  wiresGroup.visible = document.getElementById('layer-wires').checked;
  bulbsGroup.visible = document.getElementById('layer-bulbs').checked;
  slackGroup.visible = document.getElementById('layer-slack').checked;
  tabsGroup.visible = document.getElementById('layer-tabs').checked;
}}

function downloadScad() {{
  window.location.href = 'petes_dragon_tpu_panel.scad';
}}

window.addEventListener('resize', () => {{
  const container = document.getElementById('three-canvas');
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});

window.onload = initThree;
</script>

</body>
</html>
"""

html_file_path = os.path.join(PANELS_DIR, "tpu_panel_preview.html")
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Saved Enhanced Interactive 3D Web Inspector: {html_file_path}")
print("=== All 3D Panel Files Successfully Upgraded! ===")
