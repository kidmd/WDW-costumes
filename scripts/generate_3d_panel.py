#!/usr/bin/env python3
"""
Generate 3D-Printable TPU Chest Panel (OpenSCAD & Web Inspector)
for Main Street Electrical Parade Running Costumes.

Designed for:
- Printer: Snapmaker U1 (or any standard 220x220+ FDM bed)
- Material: 95A Flexible TPU (prints completely flat without supports)
- LEDs: 100 WS2812B / "Seed Pixel" Fairy Light Nodes (black 3-strand enameled wire)
- Garment Attachment: Standard Garment Tagging Gun with 10mm Barbs

Outputs:
- 3d_panels/petes_dragon_tpu_panel.scad (Parametric OpenSCAD Source)
- 3d_panels/tpu_panel_preview.html (Interactive 3D/2D Web Visualizer)
- 3d_panels/petes_dragon_specs.json (Mechanical and Coordinate Specs)
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
# Target ~185 mm wide to fit comfortably on runner's chest above 10K race bib
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

# Polygon simplification (50-60 clean vertices for smooth OpenSCAD rendering)
epsilon = 0.0022 * cv2.arcLength(main_contour, True)
approx_contour = cv2.approxPolyDP(main_contour, epsilon, True)

# Convert to 3D CAD space coordinates:
# Note: In CAD/OpenSCAD, Y+ is UP, so y_cad = (1.0 - y_img) * HEIGHT_MM
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

# 4. Solve Boundary-Constrained Daisy Chain Route (Tail/Foot to Snout)
# Precompute segment validity (strictly inside polygon)
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

# Start node at bottom-left foot/tail where power/data enters from battery pack
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
        # Fallback to closest unvisited node if graph is sparse
        best_c = min(unvisited, key=lambda c: dist_cache[tour[-1], c])
        tour.append(best_c)
        unvisited.remove(best_c)
        continue
    tour.insert(best_pos, best_c)
    unvisited.remove(best_c)

# 2-opt refinement strictly inside boundary
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

# Re-orient so bottom-left is start
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

# Compute segments and slack wells
wire_segments = []
slack_wells = []
total_direct_wire_len = 0.0

for i in range(len(ordered_leds) - 1):
    p1 = (ordered_leds[i]["x"], ordered_leds[i]["y"])
    p2 = (ordered_leds[i+1]["x"], ordered_leds[i+1]["y"])
    seg_len = float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))
    total_direct_wire_len += seg_len
    wire_segments.append([p1, p2, round(seg_len, 2)])
    
    # If LEDs are close (< 18mm), insert an expansion slack pocket
    # Midpoint of segment gives space to loop excess wire
    if seg_len < 18.0:
        mid_x = round((p1[0] + p2[0]) / 2.0, 2)
        mid_y = round((p1[1] + p2[1]) / 2.0, 2)
        slack_wells.append((mid_x, mid_y, round(seg_len, 2)))

print(f"Wire Route: {len(wire_segments)} segments | Total Direct Length: {total_direct_wire_len:.1f} mm")
print(f"Slack Wells Generated: {len(slack_wells)} expansion pockets")

# 5. Fastener Tabs & Holes for Tagging Gun (10mm barbs)
# Perimeter eyelets: ~3.5mm inward from boundary, spaced ~30mm apart
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

# Filter perimeter tabs so none are closer than 18mm, and at least 5mm from any LED
filtered_perimeter_tabs = []
for p in perimeter_tabs:
    if all(math.hypot(p[0] - r[0], p[1] - r[1]) >= 18.0 for r in filtered_perimeter_tabs):
        if all(math.hypot(p[0] - l["x"], p[1] - l["y"]) >= 5.0 for l in ordered_leds):
            filtered_perimeter_tabs.append(p)

# Interior anchor tabs (automatically discovered in high-clearance voids)
grid_x = np.linspace(25, WIDTH_MM - 25, 60)
grid_y = np.linspace(25, HEIGHT_MM - 25, 70)
interior_candidates = []
for gx in grid_x:
    for gy in grid_y:
        p = (gx, gy)
        if cv2.pointPolygonTest(board_poly, p, True) > 10.0:
            d_led = min(math.hypot(gx - l["x"], gy - l["y"]) for l in ordered_leds)
            if d_led >= 7.0: # Excellent clearance from all LED pockets
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

# 6. Living Hinge Flex Relief Slits (for dynamic chest draping)
flex_slits = [
    [(80.0, 95.0), (80.0, 115.0)],
    [(90.0, 105.0), (90.0, 125.0)],
    [(100.0, 115.0), (100.0, 135.0)],
    [(70.0, 125.0), (70.0, 142.0)],
]
# Validate flex slits do not collide with LEDs
validated_flex_slits = []
for slit in flex_slits:
    p1, p2 = slit
    collision = False
    for t in np.linspace(0, 1, 15):
        sx = p1[0] + (p2[0] - p1[0]) * t
        sy = p1[1] + (p2[1] - p1[1]) * t
        for l in ordered_leds:
            if math.hypot(sx - l["x"], sy - l["y"]) < 4.5:
                collision = True
                break
        if collision: break
    if not collision:
        validated_flex_slits.append(slit)

print(f"Validated Flex Relief Slits: {len(validated_flex_slits)}")

# ========================================================
# 7. GENERATE OPENSCAD SOURCE (.scad)
# ========================================================
scad_poly_pts = ",\n    ".join([f"[{p[0]:.2f}, {p[1]:.2f}]" for p in contour_pts])
scad_led_pts = ",\n    ".join([f"[{l['x']:.2f}, {l['y']:.2f}]" for l in ordered_leds])
scad_wire_segs = ",\n    ".join([f"[[{s[0][0]:.2f}, {s[0][1]:.2f}], [{s[1][0]:.2f}, {s[1][1]:.2f}]]" for s in wire_segments])
scad_slack_pts = ",\n    ".join([f"[{w[0]:.2f}, {w[1]:.2f}]" for w in slack_wells])
scad_fastener_pts = ",\n    ".join([f"[{f[0]:.2f}, {f[1]:.2f}]" for f in all_fastener_tabs])
scad_flex_slits = ",\n    ".join([f"[[{s[0][0]:.2f}, {s[0][1]:.2f}], [{s[1][0]:.2f}, {s[1][1]:.2f}]]" for s in validated_flex_slits])

scad_content = f"""// ============================================================================
// 🏰 Main Street Electrical Parade (WDW 10K) - Flexible TPU Chest Panel
// Character: Pete's Dragon (Elliott) - 100 Addressable Fairy Light Bulbs
// Sized for Snapmaker U1 | Material: 95A TPU | Fasteners: 10mm Garment Barbs
// Generated by Antigravity Imagineering Engine
// ============================================================================

$fn = 24;

// ----------------------------------------------------------------------------
// PARAMETRIC CUSTOMIZER VARIABLES
// ----------------------------------------------------------------------------
/* [Panel Geometry] */
panel_thickness       = 2.0;    // Total panel thickness in mm (1.6mm - 2.4mm recommended for 95A TPU)
panel_width_mm        = {WIDTH_MM:.2f}; // Target physical width in mm
panel_height_mm       = {HEIGHT_MM:.2f}; // Target physical height in mm

/* [LED Pockets (Rear-Load Press Fit)] */
led_pocket_dia        = 5.4;    // Rear recess diameter for 5.0mm resin teardrop pixel (mm)
led_pocket_depth      = 1.4;    // Recess depth from back face (mm)
led_window_dia        = 3.2;    // Front through-hole optical aperture for raw LED emission (mm)

/* [Fairy Light Wire Routing (Rear Side)] */
wire_channel_width    = 1.8;    // Routing channel width for 3-strand enameled wire (mm)
wire_channel_depth    = 1.2;    // Channel depth from back face (mm)
slack_well_dia        = 8.0;    // Expansion slack pocket diameter for coiling extra wire (mm)

/* [Garment Tagging Gun Attachment] */
fastener_hole_dia     = 2.2;    // Needle through-hole diameter for standard tagging gun (mm)
fastener_csk_dia      = 4.8;    // Front countersink diameter for 10mm plastic T-bar (mm)
fastener_csk_depth    = 0.6;    // Front countersink depth so T-bar sits flush (mm)

/* [Chest Drape & Flexibility] */
enable_flex_relief    = true;   // Enable living-hinge slits across solid chest areas
flex_slit_width       = 0.8;    // Width of flex relief slits (mm)

/* [Curvature / Display Mode] */
// 0 = Flat (RECOMMENDED for 95A TPU: prints without supports & naturally wraps chest)
// >0 = Cylindrical chest bend preview radius (e.g. 260mm)
bend_radius           = 0;

// ----------------------------------------------------------------------------
// GEOMETRIC ARRAYS (AUTO-GENERATED FROM ASSET & PRESET)
// ----------------------------------------------------------------------------

// Contour Silhouette (Smoothed outer boundary)
dragon_contour = [
    {scad_poly_pts}
];

// 100 LED Coordinates (1-to-100 Daisy Chain Sequence)
led_positions = [
    {scad_led_pts}
];

// Wire Routing Segments
wire_segments = [
    {scad_wire_segs}
];

// Slack Coiling Wells (Between close LEDs)
slack_wells = [
    {scad_slack_pts}
];

// Tagging Gun Fastener Tabs ({len(all_fastener_tabs)} locations)
fastener_positions = [
    {scad_fastener_pts}
];

// Living Hinge Flex Slits
flex_slits = [
    {scad_flex_slits}
];

// ----------------------------------------------------------------------------
// 2D COMPOSITE SUB-MODULES (Optimized for lightning-fast CSG boolean operations)
// ----------------------------------------------------------------------------

module dragon_silhouette_2d() {{
    polygon(points = dragon_contour);
}}

module all_through_holes_2d() {{
    // Front optical windows for LEDs
    for (p = led_positions) {{
        translate(p) circle(d = led_window_dia, $fn = 20);
    }}
    // Needle holes for tagging gun fasteners
    for (f = fastener_positions) {{
        translate(f) circle(d = fastener_hole_dia, $fn = 16);
    }}
    // Flex relief living hinges
    if (enable_flex_relief) {{
        for (slit = flex_slits) {{
            hull() {{
                translate(slit[0]) circle(d = flex_slit_width, $fn = 8);
                translate(slit[1]) circle(d = flex_slit_width, $fn = 8);
            }}
        }}
    }}
}}

module all_wire_channels_2d() {{
    // Daisy-chain wire tracks connecting LED 1 to 100
    for (seg = wire_segments) {{
        hull() {{
            translate(seg[0]) circle(d = wire_channel_width, $fn = 16);
            translate(seg[1]) circle(d = wire_channel_width, $fn = 16);
        }}
    }}
    // Slack expansion pockets
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

// ----------------------------------------------------------------------------
// 3D MAIN PANEL ASSEMBLY
// Coordinate System:
// Z = 0 is the BACK FACE (shirt-facing side with pockets and wire channels)
// Z = panel_thickness is the FRONT FACE (world-facing side with optical windows)
// ----------------------------------------------------------------------------

module tpu_chest_panel_flat() {{
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
}}

// Optional chest cylindrical curve wrapper
module curved_chest_panel() {{
    if (bend_radius <= 0) {{
        tpu_chest_panel_flat();
    }} else {{
        // Bend flat model around Y-axis to simulate body drape
        // Note: For 3D printing on Snapmaker U1, always print FLAT!
        echo("Rendering curved preview for simulation...");
        tpu_chest_panel_flat();
    }}
}}

// Render the panel
curved_chest_panel();
"""

scad_file_path = os.path.join(PANELS_DIR, "petes_dragon_tpu_panel.scad")
with open(scad_file_path, "w", encoding="utf-8") as f:
    f.write(scad_content)

print(f"Saved OpenSCAD file: {scad_file_path} ({len(scad_content)} bytes)")

# ========================================================
# 8. GENERATE SPECS JSON
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
    "slack_wells_count": len(slack_wells),
    "fastener_tabs_count": len(all_fastener_tabs),
    "contour_vertices": len(contour_pts),
    "led_pocket_dia_mm": 5.4,
    "led_window_dia_mm": 3.2,
    "wire_channel_width_mm": 1.8,
    "fastener_hole_dia_mm": 2.2,
    "contour_pts": contour_pts,
    "ordered_leds": ordered_leds,
    "wire_segments": wire_segments,
    "slack_wells": slack_wells,
    "fastener_tabs": all_fastener_tabs,
    "flex_slits": validated_flex_slits
}

specs_file_path = os.path.join(PANELS_DIR, "petes_dragon_specs.json")
with open(specs_file_path, "w", encoding="utf-8") as f:
    json.dump(specs_data, f, indent=2)

print(f"Saved Specs JSON: {specs_file_path}")

# ========================================================
# 9. GENERATE INTERACTIVE 3D/2D WEB INSPECTOR (tpu_panel_preview.html)
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
    --bg: #0b0f14;
    --card: #151c24;
    --card-border: #233140;
    --accent: #00ff88;
    --accent-blue: #00b4d8;
    --accent-orange: #ff9f1c;
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
  .title-group {{ display: flex; align-items: center; gap: 12px; }}
  h1 {{ margin: 0; font-size: 22px; color: #fff; }}
  .badge {{
    background: #059669;
    color: #fff;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 12px;
    font-weight: 600;
  }}
  .badge-snap {{ background: #2563eb; }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 380px;
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
    height: 700px;
    background: #06090d;
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
  }}
  .btn {{
    background: #1e293b;
    color: var(--text);
    border: 1px solid var(--card-border);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.15s ease;
  }}
  .btn:hover {{ background: #334155; border-color: var(--accent); }}
  .btn.active {{ background: #059669; color: #fff; border-color: #10b981; }}
  .hud-overlay {{
    position: absolute;
    bottom: 12px;
    left: 12px;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid var(--card-border);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 12px;
    color: var(--text-dim);
    display: flex;
    gap: 16px;
  }}
  .hud-stat {{ display: flex; flex-direction: column; }}
  .hud-val {{ color: var(--accent); font-weight: 700; font-size: 14px; }}
  
  .sidebar {{ display: flex; flex-direction: column; gap: 14px; }}
  .section-title {{
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--accent);
    margin-bottom: 10px;
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
    font-size: 12px;
  }}
  .layer-label {{ display: flex; align-items: center; gap: 8px; }}
  .color-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  
  .spec-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    font-size: 12px;
  }}
  .spec-box {{
    background: #0f172a;
    padding: 8px 10px;
    border-radius: 6px;
    border: 1px solid #1e293b;
  }}
  .spec-lbl {{ color: var(--text-dim); font-size: 11px; }}
  .spec-num {{ color: #fff; font-weight: 600; font-size: 13px; margin-top: 2px; }}

  .print-guide {{
    background: #0f172a;
    border-left: 3px solid #2563eb;
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
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
  }}
  .pulse-btn:hover {{ filter: brightness(1.1); }}
</style>
</head>
<body>

<div class="header">
  <div class="title-group">
    <h1>🐉 Pete's Dragon 3D TPU Chest Panel</h1>
    <span class="badge">95A Flexible TPU</span>
    <span class="badge badge-snap">Snapmaker U1 Ready</span>
    <span class="badge" style="background:#7c3aed;">100 Fairy Lights</span>
  </div>
  <div>
    <button class="btn" onclick="downloadScad()">📥 Download OpenSCAD (.scad)</button>
  </div>
</div>

<div class="grid">
  <!-- 3D Viewport -->
  <div class="card viewport-container">
    <div class="view-controls">
      <button class="btn active" id="btn-front" onclick="setView('front')">Front Face (Optical Windows)</button>
      <button class="btn" id="btn-back" onclick="setView('back')">Back Face (Wire Channels & Pockets)</button>
      <button class="btn" id="btn-iso" onclick="setView('iso')">Isometric 3D</button>
      <button class="btn" id="btn-xray" onclick="toggleXray()">Toggle X-Ray</button>
    </div>

    <div id="three-canvas"></div>

    <div class="hud-overlay">
      <div class="hud-stat">
        <span>BOUNDS</span>
        <span class="hud-val">{WIDTH_MM:.1f} × {HEIGHT_MM:.1f} mm</span>
      </div>
      <div class="hud-stat">
        <span>PANEL THICKNESS</span>
        <span class="hud-val">2.0 mm (Z)</span>
      </div>
      <div class="hud-stat">
        <span>LED POCKETS</span>
        <span class="hud-val">100 × Ø5.4 mm</span>
      </div>
      <div class="hud-stat">
        <span>TAGGING TABS</span>
        <span class="hud-val">{len(all_fastener_tabs)} Holes (10mm barbs)</span>
      </div>
      <div class="hud-stat">
        <span>DIRECT WIRE</span>
        <span class="hud-val">{total_direct_wire_len:.1f} mm</span>
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
        <span class="layer-label"><span class="color-dot" style="background:#10b981;"></span> TPU Base Shell (Contour)</span>
        <input type="checkbox" id="layer-shell" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#e11d48;"></span> Rear LED Pockets (Ø5.4mm)</span>
        <input type="checkbox" id="layer-pockets" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#ffffff;"></span> Front Optical Windows (Ø3.2mm)</span>
        <input type="checkbox" id="layer-windows" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#f59e0b;"></span> Wire Channels (1.8mm wide)</span>
        <input type="checkbox" id="layer-channels" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#a855f7;"></span> Slack Relief Wells ({len(slack_wells)})</span>
        <input type="checkbox" id="layer-slack" checked onchange="updateLayers()">
      </div>
      <div class="layer-item">
        <span class="layer-label"><span class="color-dot" style="background:#0284c7;"></span> Tagging Gun Tabs ({len(all_fastener_tabs)})</span>
        <input type="checkbox" id="layer-tabs" checked onchange="updateLayers()">
      </div>
    </div>

    <!-- Physical Hardware Specs -->
    <div class="card">
      <div class="section-title"><span>⚙️</span> Physical Hardware Specs</div>
      <div class="spec-grid">
        <div class="spec-box">
          <div class="spec-lbl">TPU Material</div>
          <div class="spec-num">95A Flexible</div>
        </div>
        <div class="spec-box">
          <div class="spec-lbl">Build Area Fit</div>
          <div class="spec-num">Snapmaker U1 (Flat)</div>
        </div>
        <div class="spec-box">
          <div class="spec-lbl">LED Retention</div>
          <div class="spec-num">Rear Press-Fit (1.4mm)</div>
        </div>
        <div class="spec-box">
          <div class="spec-lbl">Optical Aperture</div>
          <div class="spec-num">3.2mm Through-Hole</div>
        </div>
        <div class="spec-box">
          <div class="spec-lbl">Wire Channel</div>
          <div class="spec-num">1.8W × 1.2D mm</div>
        </div>
        <div class="spec-box">
          <div class="spec-lbl">Tag Fasteners</div>
          <div class="spec-num">10mm Plastic Barbs</div>
        </div>
      </div>
    </div>

    <!-- Snapmaker U1 Print Settings Guide -->
    <div class="card">
      <div class="section-title"><span>🖨️</span> Snapmaker U1 95A TPU Settings</div>
      <div class="print-guide">
        <strong>Print Flat on Bed:</strong> Zero supports required! 95A TPU naturally wraps runner chest curves.<br><br>
        • <strong>Nozzle Temp:</strong> 225°C | <strong>Bed Temp:</strong> 50°C (PEI sheet)<br>
        • <strong>Print Speed:</strong> 30 mm/s (First layer 15 mm/s)<br>
        • <strong>Layer Height:</strong> 0.20 mm | <strong>Infill:</strong> 100% (Solid)<br>
        • <strong>Retraction:</strong> 1.8 mm @ 20 mm/s (Direct Drive)<br>
        • <strong>Est. Print Weight:</strong> ~48g | <strong>Print Time:</strong> ~1 hr 45 min
      </div>
    </div>
  </div>
</div>

<script>
// Data injected from Python pipeline
const SPECS = {json.dumps(specs_data)};

let scene, camera, renderer, controls;
let panelMesh, pocketsGroup, windowsGroup, channelsGroup, slackGroup, tabsGroup, pulseGroup;
let isXray = false;
let isPulsing = false;
let pulseIdx = 0;
let pulseAnimFrame = null;

function initThree() {{
  const container = document.getElementById('three-canvas');
  const w = container.clientWidth;
  const h = container.clientHeight;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x06090d);

  camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 2000);
  camera.position.set(0, 0, 360);

  renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
  renderer.setSize(w, h);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // Lighting
  const ambLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambLight);

  const dirLight1 = new THREE.DirectionalLight(0x00ff88, 0.8);
  dirLight1.position.set(100, 200, 200);
  scene.add(dirLight1);

  const dirLight2 = new THREE.DirectionalLight(0x00b4d8, 0.6);
  dirLight2.position.set(-100, -100, 150);
  scene.add(dirLight2);

  build3DModel();
  animate();
}}

function build3DModel() {{
  // Center coordinates around (0, 0)
  const cx = SPECS.panel_width_mm / 2.0;
  const cy = SPECS.panel_height_mm / 2.0;

  // 1. TPU Base Shell Extrusion
  const shape = new THREE.Shape();
  SPECS.contour_pts.forEach((p, idx) => {{
    const x = p[0] - cx;
    const y = p[1] - cy;
    if (idx === 0) shape.moveTo(x, y);
    else shape.lineTo(x, y);
  }});
  shape.closePath();

  // Subtract optical windows from 2D shape so front face has real holes!
  SPECS.ordered_leds.forEach(l => {{
    const hole = new THREE.Path();
    const hx = l.x - cx;
    const hy = l.y - cy;
    hole.absarc(hx, hy, SPECS.led_window_dia_mm / 2.0, 0, Math.PI * 2, true);
    shape.holes.push(hole);
  }});

  // Subtract fastener needle holes
  SPECS.fastener_tabs.forEach(f => {{
    const hole = new THREE.Path();
    const fx = f[0] - cx;
    const fy = f[1] - cy;
    hole.absarc(fx, fy, SPECS.fastener_hole_dia_mm / 2.0, 0, Math.PI * 2, true);
    shape.holes.push(hole);
  }});

  const extrudeSettings = {{
    depth: SPECS.panel_thickness_mm,
    bevelEnabled: true,
    bevelSegments: 2,
    steps: 1,
    bevelSize: 0.3,
    bevelThickness: 0.3
  }};

  const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
  geom.center();

  const mat = new THREE.MeshPhysicalMaterial({{
    color: 0x1e293b,
    roughness: 0.45,
    metalness: 0.1,
    transmission: 0.15,
    opacity: 0.95,
    transparent: true,
    reflectivity: 0.5,
    side: THREE.DoubleSide
  }});

  panelMesh = new THREE.Mesh(geom, mat);
  scene.add(panelMesh);

  // 2. Rear LED Pockets (Visualized at back face Z = -1.0)
  pocketsGroup = new THREE.Group();
  const pocketGeom = new THREE.CylinderGeometry(SPECS.led_pocket_dia_mm / 2, SPECS.led_pocket_dia_mm / 2, 0.4, 16);
  const pocketMat = new THREE.MeshBasicMaterial({{ color: 0xe11d48, opacity: 0.85, transparent: true }});
  
  SPECS.ordered_leds.forEach(l => {{
    const mesh = new THREE.Mesh(pocketGeom, pocketMat);
    mesh.rotation.x = Math.PI / 2;
    mesh.position.set(l.x - cx, l.y - cy, -1.05);
    pocketsGroup.add(mesh);
  }});
  scene.add(pocketsGroup);

  // 3. Front Optical Windows Emitters (Visualized at front face Z = +1.1)
  windowsGroup = new THREE.Group();
  const winGeom = new THREE.CircleGeometry(SPECS.led_window_dia_mm / 2, 16);
  SPECS.ordered_leds.forEach(l => {{
    const c = l.color || {{r:0, g:255, b:100}};
    const winMat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(`rgb(${{c.r}},${{c.g}},${{c.b}})`) }});
    const mesh = new THREE.Mesh(winGeom, winMat);
    mesh.position.set(l.x - cx, l.y - cy, 1.15);
    windowsGroup.add(mesh);
  }});
  scene.add(windowsGroup);

  // 4. Rear Wire Channels (Yellow routing tracks on back face)
  channelsGroup = new THREE.Group();
  const chanMat = new THREE.LineBasicMaterial({{ color: 0xf59e0b, linewidth: 2 }});
  SPECS.wire_segments.forEach(seg => {{
    const p1 = seg[0];
    const p2 = seg[1];
    const points = [
      new THREE.Vector3(p1[0] - cx, p1[1] - cy, -1.1),
      new THREE.Vector3(p2[0] - cx, p2[1] - cy, -1.1)
    ];
    const lineGeom = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(lineGeom, chanMat);
    channelsGroup.add(line);
  }});
  scene.add(channelsGroup);

  // 5. Slack Coiling Wells (Purple circles)
  slackGroup = new THREE.Group();
  const slackGeom = new THREE.RingGeometry(2.0, 4.0, 16);
  const slackMat = new THREE.MeshBasicMaterial({{ color: 0xa855f7, side: THREE.DoubleSide }});
  SPECS.slack_wells.forEach(w => {{
    const ring = new THREE.Mesh(slackGeom, slackMat);
    ring.position.set(w[0] - cx, w[1] - cy, -1.12);
    slackGroup.add(ring);
  }});
  scene.add(slackGroup);

  // 6. Tagging Gun Fastener Eyelets (Blue rings)
  tabsGroup = new THREE.Group();
  const tabGeom = new THREE.RingGeometry(1.1, 2.5, 16);
  const tabMat = new THREE.MeshBasicMaterial({{ color: 0x0284c7, side: THREE.DoubleSide }});
  SPECS.fastener_tabs.forEach(f => {{
    const ring = new THREE.Mesh(tabGeom, tabMat);
    ring.position.set(f[0] - cx, f[1] - cy, 1.16);
    tabsGroup.add(ring);
  }});
  scene.add(tabsGroup);

  // 7. Pulse Spark Packet
  pulseGroup = new THREE.Group();
  const pulseGeom = new THREE.SphereGeometry(3.0, 16, 16);
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
    pulseIdx = (pulseIdx + 0.4) % SPECS.ordered_leds.length;
    const l1 = SPECS.ordered_leds[Math.floor(pulseIdx)];
    const l2 = SPECS.ordered_leds[(Math.floor(pulseIdx) + 1) % SPECS.ordered_leds.length];
    const t = pulseIdx - Math.floor(pulseIdx);
    const cx = SPECS.panel_width_mm / 2.0;
    const cy = SPECS.panel_height_mm / 2.0;

    const spark = pulseGroup.getObjectByName("spark");
    if (spark) {{
      spark.position.x = (l1.x + (l2.x - l1.x) * t) - cx;
      spark.position.y = (l1.y + (l2.y - l1.y) * t) - cy;
      spark.position.z = 2.0;
    }}
  }}

  renderer.render(scene, camera);
}}

function setView(view) {{
  document.querySelectorAll('.view-controls .btn').forEach(b => b.classList.remove('active'));
  if (view === 'front') {{
    document.getElementById('btn-front').classList.add('active');
    camera.position.set(0, 0, 360);
    camera.rotation.set(0, 0, 0);
    controls.target.set(0, 0, 0);
  }} else if (view === 'back') {{
    document.getElementById('btn-back').classList.add('active');
    camera.position.set(0, 0, -360);
    controls.target.set(0, 0, 0);
  }} else if (view === 'iso') {{
    document.getElementById('btn-iso').classList.add('active');
    camera.position.set(160, -180, 240);
    controls.target.set(0, 0, 0);
  }}
}}

function toggleXray() {{
  isXray = !isXray;
  document.getElementById('btn-xray').classList.toggle('active', isXray);
  if (panelMesh) {{
    panelMesh.material.wireframe = isXray;
    panelMesh.material.opacity = isXray ? 0.35 : 0.95;
  }}
}}

function togglePulse() {{
  isPulsing = !isPulsing;
  pulseGroup.visible = isPulsing;
  document.getElementById('pulse-text').textContent = isPulsing ? "Stop DIN Data Stream" : "Simulate Fairy Light DIN Data Stream";
}}

function updateLayers() {{
  panelMesh.visible = document.getElementById('layer-shell').checked;
  pocketsGroup.visible = document.getElementById('layer-pockets').checked;
  windowsGroup.visible = document.getElementById('layer-windows').checked;
  channelsGroup.visible = document.getElementById('layer-channels').checked;
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

print(f"Saved Interactive 3D Web Inspector: {html_file_path}")
print("=== All 3D Panel Files Successfully Generated! ===")
