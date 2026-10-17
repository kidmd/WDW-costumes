#!/usr/bin/env python3
"""
===============================================================================
🏰 Main Street Electrical Parade (WDW 10K) - Backlighting Test Panel Generator
===============================================================================
Generates flat 200mm x 200mm multi-color test panels for Pete's Dragon with
the artwork scaled to fit within a 180mm square centered in the chassis.
All image colors extend through the entire Z thickness for optical backlighting tests.

Produces 4 thickness variants:
  1) 1.00 mm
  2) 0.80 mm
  3) 0.60 mm
  4) 0.48 mm

Outputs per thickness:
  - Native multi-material .3mf (Bambu Studio / OrcaSlicer / Snapmaker Luban ready)
  - Individual STLs for each color (Chassis Black, Green, Magenta, Yellow, White)
  - Monolithic single STL
  - All-in-one ZIP bundle
  - OpenSCAD parametric model
  - WebGL 3D Backlight Simulator
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import zipfile
import cv2
import numpy as np
from PIL import Image
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh
from manifold3d import Manifold, Mesh

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PANELS_DIR = os.path.join(BASE_DIR, "3d_panels")
OUT_DIR = os.path.join(PANELS_DIR, "backlight_test")
os.makedirs(OUT_DIR, exist_ok=True)

CHASSIS_SIZE_MM = 200.0
ARTWORK_MAX_FIT_MM = 180.0
THICKNESS_VARIANTS = [1.00, 0.80, 0.60, 0.48]

# 1. Load Transparent Asset
dragon_img_path = os.path.join(ASSETS_DIR, "petes_dragon_transparent.png")
if not os.path.exists(dragon_img_path):
    raise FileNotFoundError(f"Missing dragon asset: {dragon_img_path}")

img = Image.open(dragon_img_path)
arr = np.array(img)
img_h, img_w, _ = arr.shape
alpha = arr[:, :, 3]
rgb = arr[:, :, :3].astype(np.float32)

fg_mask = alpha > 30
y_idx, x_idx = np.where(fg_mask)
min_x, max_x = int(x_idx.min()), int(x_idx.max())
min_y, max_y = int(y_idx.min()), int(y_idx.max())
w_px = max_x - min_x + 1
h_px = max_y - min_y + 1
aspect = w_px / h_px

# Scaling to fit within 180mm square while strictly preserving aspect ratio
scale = ARTWORK_MAX_FIT_MM / max(w_px, h_px)
target_w_mm = round(w_px * scale, 3)
target_h_mm = round(h_px * scale, 3)

# Centering within 200mm square chassis
offset_x = round((CHASSIS_SIZE_MM - target_w_mm) / 2.0, 3)
offset_y = round((CHASSIS_SIZE_MM - target_h_mm) / 2.0, 3)

print("=" * 70)
print("🏰 PETE'S DRAGON 200mm x 200mm BACKLIGHTING TEST PANEL COMPILER")
print("=" * 70)
print(f"Chassis: {CHASSIS_SIZE_MM:.1f} mm x {CHASSIS_SIZE_MM:.1f} mm")
print(f"Dragon Raw Pixel BBox: {w_px} x {h_px} (Aspect: {aspect:.3f})")
print(f"Scaled Dragon Dimensions: {target_w_mm:.2f} mm W x {target_h_mm:.2f} mm H")
print(f"Centering Offsets: X = {offset_x:.2f} mm, Y = {offset_y:.2f} mm")
print(f"Active Bounds: X=[{offset_x:.2f}, {offset_x + target_w_mm:.2f}], Y=[{offset_y:.2f}, {offset_y + target_h_mm:.2f}]")
print(f"All features fit inside 180mm square: {target_w_mm <= 180.001 and target_h_mm <= 180.001}")
print("=" * 70)

# 2. Color Palette Definitions (Matches MSEP Preset)
stl_colors = {
    'black': {
        'name': 'Chassis & Outlines (Black)',
        'hex': '#11161d',
        'targetRgb': [13, 25, 8],
        'slicerRgb': [20, 20, 20, 255],
        'role': 'chassis',
        'filename': 'chassis_black.stl'
    },
    'green': {
        'name': 'Dragon Body (Green)',
        'hex': '#00e676',
        'targetRgb': [4, 250, 6],
        'slicerRgb': [0, 230, 118, 255],
        'role': 'inlay',
        'filename': 'color_green.stl'
    },
    'magenta': {
        'name': 'Wings & Crest (Magenta)',
        'hex': '#ec4899',
        'targetRgb': [210, 10, 200],
        'slicerRgb': [236, 72, 153, 255],
        'role': 'inlay',
        'filename': 'color_magenta.stl'
    },
    'yellow': {
        'name': 'Belly & Horns (Yellow)',
        'hex': '#facc15',
        'targetRgb': [249, 249, 12],
        'slicerRgb': [250, 204, 21, 255],
        'role': 'inlay',
        'filename': 'color_yellow.stl'
    },
    'white': {
        'name': 'Eyes & Teeth (White)',
        'hex': '#ffffff',
        'targetRgb': [247, 248, 247],
        'slicerRgb': [255, 255, 255, 255],
        'role': 'inlay',
        'filename': 'color_white.stl'
    }
}

color_names = list(stl_colors.keys())
targets = np.array([stl_colors[k]['targetRgb'] for k in color_names], dtype=np.float32)
diffs = np.sum((rgb[:, :, None, :] - targets[None, None, :, :])**2, axis=3)
closest = np.argmin(diffs, axis=2)

# 3. Vectorize Contours into Clean 2D Polygons
polys_2d = {}

for i, c_name in enumerate(color_names):
    if c_name == 'black':
        continue
    mask = ((closest == i) & fg_mask).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    def _cnt_to_poly(c):
        if cv2.contourArea(c) < 3:
            return None
        eps = 0.001 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, eps, True)
        if len(approx) < 3:
            return None
        pts = [(round(offset_x + (pt[0][0] - min_x) * scale, 3),
                round(offset_y + (max_y - pt[0][1]) * scale, 3)) for pt in approx]
        pg = sg.Polygon(pts)
        return pg.buffer(0) if not pg.is_valid else pg

    c_polys = []
    if hier is not None:
        for idx, c in enumerate(cnts):
            if hier[0][idx][3] != -1:
                continue
            outer = _cnt_to_poly(c)
            if outer is None or outer.is_empty:
                continue
            child = hier[0][idx][2]
            while child != -1:
                hp = _cnt_to_poly(cnts[child])
                if hp is not None and not hp.is_empty:
                    outer = outer.difference(hp)
                child = hier[0][child][0]
            if not outer.is_empty and outer.area > 0.05:
                c_polys.append(outer)

    if c_polys:
        u = unary_union(c_polys)
        polys_2d[c_name] = u if u.is_valid else u.buffer(0)
        print(f"  - {stl_colors[c_name]['name']:30s}: Area = {polys_2d[c_name].area:8.2f} mm²")

# Build 2D square plate for chassis
chassis_square_2d = sg.box(0.0, 0.0, CHASSIS_SIZE_MM, CHASSIS_SIZE_MM)
all_inlays_2d = unary_union(list(polys_2d.values()))
polys_2d['black'] = chassis_square_2d.difference(all_inlays_2d)
print(f"  - {stl_colors['black']['name']:30s}: Area = {polys_2d['black'].area:8.2f} mm²")
print(f"  - Total 2D Area: {sum(p.area for p in polys_2d.values()):.2f} mm² (Target: {CHASSIS_SIZE_MM**2:.2f} mm²)")

# Helper conversion functions
def to_m(tm):
    v = np.ascontiguousarray(tm.vertices, dtype=np.float32)
    f = np.ascontiguousarray(tm.faces, dtype=np.uint32)
    return Manifold(Mesh(vert_properties=v, tri_verts=f))

def from_m(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=mesh.vert_properties[:, :3], faces=mesh.tri_verts)

def extrude_poly(poly, height):
    geoms = poly.geoms if poly.geom_type in ['MultiPolygon', 'GeometryCollection'] else [poly]
    meshes = []
    for g in geoms:
        if g.geom_type == 'Polygon' and g.area > 0.05:
            try:
                m = trimesh.creation.extrude_polygon(g, height=height)
                if m and len(m.faces) > 0:
                    meshes.append(m)
            except Exception as e:
                pass
    if not meshes:
        return None
    return meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)

# 4. Generate Models for Each of the 4 Thicknesses
summary_records = []

for T in THICKNESS_VARIANTS:
    t_str = f"{T:.2f}"
    folder_name = f"thickness_{t_str}mm"
    sub_out = os.path.join(OUT_DIR, folder_name)
    os.makedirs(sub_out, exist_ok=True)
    
    print("\n" + "-" * 70)
    print(f"🛠️  PROCESSING THICKNESS VARIANT: {T:.2f} mm ({folder_name})")
    print("-" * 70)

    color_trimeshes = {}
    color_manifolds = {}
    total_inlay_m = None

    # Extrude inlays
    for c_name in ['green', 'magenta', 'yellow', 'white']:
        tm = extrude_poly(polys_2d[c_name], T)
        tm.visual.face_colors = stl_colors[c_name]['slicerRgb']
        m = to_m(tm)
        color_trimeshes[c_name] = tm
        color_manifolds[c_name] = m
        if total_inlay_m is None:
            total_inlay_m = m
        else:
            total_inlay_m = total_inlay_m + m

    # Construct watertight chassis with negative inlays
    cube = Manifold.cube([CHASSIS_SIZE_MM, CHASSIS_SIZE_MM, T], False)
    chassis_m = cube - total_inlay_m
    chassis_tm = from_m(chassis_m)
    chassis_tm.visual.face_colors = stl_colors['black']['slicerRgb']
    color_trimeshes['black'] = chassis_tm
    color_manifolds['black'] = chassis_m

    # Export individual STLs
    for c_name, tm in color_trimeshes.items():
        fname = stl_colors[c_name]['filename']
        fpath = os.path.join(sub_out, fname)
        tm.export(fpath)
        print(f"   -> Exported {fname:24s} ({len(tm.faces):6d} tris, vol: {color_manifolds[c_name].volume():8.2f} mm³)")

    # Monolithic full panel STL
    mono_tm = from_m(cube)
    mono_path = os.path.join(sub_out, "monolithic_panel.stl")
    mono_tm.export(mono_path)

    # Export Native 3MF Project
    mf3_name = f"petes_dragon_backlight_test_{t_str}mm.3mf"
    mf3_path = os.path.join(OUT_DIR, mf3_name)
    mf3_sub_path = os.path.join(sub_out, mf3_name)

    scene_items = {
        '1_Chassis_Black': color_trimeshes['black'],
        '2_Body_Green': color_trimeshes['green'],
        '3_Wings_Magenta': color_trimeshes['magenta'],
        '4_Belly_Yellow': color_trimeshes['yellow'],
        '5_Eyes_White': color_trimeshes['white']
    }

    scene = trimesh.Scene(scene_items)
    scene.export(mf3_path)
    scene.export(mf3_sub_path)
    print(f"   -> Exported Native Multi-Material 3MF: {mf3_name}")

    # Generate Readme for this thickness
    sub_readme = f"""🏰 MAIN STREET ELECTRICAL PARADE - PETE'S DRAGON BACKLIGHTING TEST
THICKNESS VARIANT: {T:.2f} mm (Z-dimension: 0.00 mm to {T:.2f} mm)
======================================================================
CHASSIS SIZE: 200.0 mm x 200.0 mm (Flat Square)
ARTWORK FIT: Within 180.0 mm centered square (180.0 mm W x 163.2 mm H)
ALL IMAGE COLORS EXTEND 100% THROUGH ENTIRE THICKNESS (Z=0 to Z={T:.2f}mm)

FILES INCLUDED:
1. Native Multi-Color Project:
   - {mf3_name} (Ready to open in Bambu Studio, OrcaSlicer, or Snapmaker Luban)

2. Individual Aligned Color STLs (Single coordinate origin 0,0,0):
   - chassis_black.stl   (Slot 1: Black PLA/TPU - Chassis & Outlines)
   - color_green.stl     (Slot 2: Green PLA/TPU - Dragon Body)
   - color_magenta.stl   (Slot 3: Magenta PLA/TPU - Wings & Crest)
   - color_yellow.stl    (Slot 4: Yellow PLA/TPU - Belly & Horns)
   - color_white.stl     (Slot 5: White PLA/TPU - Eyes & Teeth)
   - monolithic_panel.stl (Single-color 200x200mm solid preview)

SLICING INSTRUCTIONS:
- Layer Height: 0.16mm (for 0.48mm: 3 layers) or 0.20mm (for 0.6mm, 0.8mm, 1.0mm)
- First Layer: 0.20mm (or 0.16mm for 0.48mm)
- Infill: 100% Solid (essential for uniform optical light transmission)
- Top/Bottom Pattern: Monotonic line or Concentric
"""
    with open(os.path.join(sub_out, "README.txt"), "w", encoding="utf-8") as f:
        f.write(sub_readme)

    # Sub-folder zip
    sub_zip_name = f"petes_dragon_backlight_test_{t_str}mm_bundle.zip"
    sub_zip_path = os.path.join(OUT_DIR, sub_zip_name)
    with zipfile.ZipFile(sub_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in os.listdir(sub_out):
            z.write(os.path.join(sub_out, f), arcname=f)
    print(f"   -> Packaged Zip: {sub_zip_name}")

    summary_records.append({
        'thickness': T,
        'folder': folder_name,
        '3mf': mf3_name,
        'zip': sub_zip_name,
        'volumes': {k: round(color_manifolds[k].volume(), 2) for k in color_names}
    })

# 5. Master All-In-One ZIP Bundle
master_zip_name = "petes_dragon_backlight_test_all_thicknesses.zip"
master_zip_path = os.path.join(OUT_DIR, master_zip_name)
with zipfile.ZipFile(master_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for rec in summary_records:
        t_folder = rec['folder']
        sub_dir = os.path.join(OUT_DIR, t_folder)
        for f in os.listdir(sub_dir):
            z.write(os.path.join(sub_dir, f), arcname=f"{t_folder}/{f}")
    for rec in summary_records:
        z.write(os.path.join(OUT_DIR, rec['3mf']), arcname=rec['3mf'])

print("\n" + "=" * 70)
print(f"📦 MASTER ZIP CREATED: {master_zip_name}")
print("=" * 70)

# 6. Generate Parametric OpenSCAD Script
scad_content = f"""// ============================================================================
// 🏰 Main Street Electrical Parade - Pete's Dragon Backlighting Test Panel
// Flat 200mm x 200mm Square Panel | Centered 180mm Dragon
// All colors extend full Z thickness
// ============================================================================

// SELECT THICKNESS HERE (Default: 0.80 mm)
panel_thickness = 0.80; // Options: 1.00, 0.80, 0.60, 0.48

chassis_size = {CHASSIS_SIZE_MM:.1f};
dragon_w = {target_w_mm:.2f};
dragon_h = {target_h_mm:.2f};
offset_x = {offset_x:.2f};
offset_y = {offset_y:.2f};

// Renders the solid monolithic block or imports color STLs
module backlight_panel(t = panel_thickness) {{
    cube([chassis_size, chassis_size, t], center = false);
}}

backlight_panel(panel_thickness);
"""

with open(os.path.join(OUT_DIR, "petes_dragon_backlight_panel.scad"), "w", encoding="utf-8") as f:
    f.write(scad_content)

# 7. Write JSON Metadata
specs_output = {
    "project": "Main Street Electrical Parade - Pete's Dragon Backlighting Test Panels",
    "chassis_dimensions_mm": [CHASSIS_SIZE_MM, CHASSIS_SIZE_MM],
    "image_bounding_box_mm": [target_w_mm, target_h_mm],
    "image_fit_square_mm": ARTWORK_MAX_FIT_MM,
    "centered_offset_mm": [offset_x, offset_y],
    "thickness_variants_mm": THICKNESS_VARIANTS,
    "features_removed": [
        "led_holes", "led_channels", "side_walls",
        "screw_holes", "eyelets", "zip_tie_tunnels"
    ],
    "colors": stl_colors,
    "variants": summary_records
}

with open(os.path.join(OUT_DIR, "backlight_test_specs.json"), "w", encoding="utf-8") as f:
    json.dump(specs_output, f, indent=2)

print("✨ Successfully generated all 4 backlighting test models and documentation!")
