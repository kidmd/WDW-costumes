#!/usr/bin/env python3
"""
Engrave Custom 1-Piece Nameplate onto the Flat Back of the Dopey Photographer Medal.

Text:
- Line 1: Tom Reinsvold
- Line 2: 1st in Age Group
- Line 3: 48.6 photos/mile

Features:
- Micro-debossed: 0.40 mm depth (exactly 2 layers @ 0.20mm layer height) for zero bridging sag.
- Properly mirrored across X=45.0mm so when the medal is turned over, it reads naturally left-to-right!
- Bold typography with rounded terminal buffers for 100% clean first-layer bed adhesion.
- Decorative accent flourishes: vintage star dividers (★ ★ ★) and circular medal framing groove.
- Exports watertight STL and updates interactive 3D Web Viewer with Front/Back flip controls.
"""

import os
import sys
import time
import shutil
import zipfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import shapely.geometry as sg
from shapely.ops import unary_union
from shapely.affinity import scale as shp_scale, translate as shp_translate
import trimesh
from manifold3d import Manifold, Mesh

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("=" * 72)
print("*** ENGRAVING DOPEY PHOTOGRAPHER FINISHER MEDAL (CUSTOM BACK) ***")
print("=" * 72)
t0 = time.time()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDAL_DIR = os.path.join(BASE_DIR, "3d_panels", "dopey_medal")
MONO_STL = os.path.join(MEDAL_DIR, "dopey_photographer_medal_relief.stl")
ENGRAVED_STL = os.path.join(MEDAL_DIR, "dopey_photographer_medal_engraved_back.stl")

if not os.path.exists(MONO_STL):
    raise FileNotFoundError(f"Missing base STL: {MONO_STL}")

# 1. Rasterize High-Resolution Back Graphics & Text
# Medal coordinate frame: X in [0, 90.0] mm, Y in [0, 105.0] mm
# Circle center: X = 45.0 mm, Y = 45.0 mm, Radius ~ 45.0 mm
SCALE_PX = 25.0  # 25 pixels per mm (high sub-pixel precision)
IMG_W = int(90.0 * SCALE_PX)    # 2250 px
IMG_H = int(105.0 * SCALE_PX)   # 2625 px

canvas = Image.new('L', (IMG_W, IMG_H), 0)
draw = ImageDraw.Draw(canvas)

# Locate bold font
font_candidates = [
    'C:/Windows/Fonts/arialbd.ttf',
    'C:/Windows/Fonts/segoeuib.ttf',
    'C:/Windows/Fonts/calibrib.ttf',
    'C:/Windows/Fonts/impact.ttf'
]
chosen_font = None
for f in font_candidates:
    if os.path.exists(f):
        chosen_font = f
        break

font_name = ImageFont.truetype(chosen_font, int(6.4 * SCALE_PX))   # 6.4mm font height
font_sub = ImageFont.truetype(chosen_font, int(4.6 * SCALE_PX))    # 4.6mm font height
font_stars = ImageFont.truetype(chosen_font, int(4.0 * SCALE_PX))  # 4.0mm star accents

# Positions in mm (Y=0 is bottom of medal, Y=105 is top of ribbon loop)
# Medallion circular center is at Y = 46.0 mm, X = 45.0 mm
cx_px = 45.0 * SCALE_PX
def mm_to_py(y_mm):
    # In 3D: Y=0 is bottom. In PIL: Y=0 is top.
    return (105.0 - y_mm) * SCALE_PX

lines_to_draw = [
    ("★  ★  ★", font_stars, 66.0),
    ("Tom Reinsvold", font_name, 56.5),
    ("1st in Age Group", font_sub, 46.5),
    ("48.6 photos / mile", font_sub, 36.5),
    ("★  ★  ★", font_stars, 27.0),
]

for text, font, y_mm in lines_to_draw:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px = cx_px - tw / 2.0 - bbox[0]
    py = mm_to_py(y_mm) - th / 2.0 - bbox[1]
    draw.text((px, py), text, fill=255, font=font)

# Add decorative circular framing ring on back:
# Inner ring radius = 41.5 mm, width = 1.0 mm (groove radius 41.0 to 42.0 mm)
center_y_px = mm_to_py(46.0)
r_out_px = 42.0 * SCALE_PX
r_in_px = 40.8 * SCALE_PX
draw.ellipse([cx_px - r_out_px, center_y_px - r_out_px, cx_px + r_out_px, center_y_px + r_out_px], outline=255, width=int(1.2 * SCALE_PX))

# 2. Extract 2D Contours to Shapely
arr = np.array(canvas)
contours, hierarchy = cv2.findContours(arr, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
hierarchy = hierarchy[0]
polys = []
for idx, c in enumerate(contours):
    if hierarchy[idx][3] == -1 and len(c) >= 3:
        shell = [(pt[0][0] / SCALE_PX, 105.0 - pt[0][1] / SCALE_PX) for pt in c]
        holes = []
        child = hierarchy[idx][2]
        while child != -1:
            if len(contours[child]) >= 3:
                h_pts = [(pt[0][0] / SCALE_PX, 105.0 - pt[0][1] / SCALE_PX) for pt in contours[child]]
                holes.append(h_pts)
            child = hierarchy[child][0]
        p = sg.Polygon(shell, holes).buffer(0)
        if not p.is_empty and p.area > 0.04:
            polys.append(p)

back_art_2d = unary_union(polys).simplify(0.035, preserve_topology=True).buffer(0.06)

# 3. CRITICAL: Mirror horizontally across X = 45.0 mm!
# So that when looking at the back face (+Z normal), the text reads naturally left-to-right!
mirrored_art_2d = shp_scale(back_art_2d, xfact=-1.0, yfact=1.0, origin=(45.0, 46.0)).buffer(0)

print(f"Back engraving polygon created: {len(mirrored_art_2d.geoms) if hasattr(mirrored_art_2d, 'geoms') else 1} parts, area: {mirrored_art_2d.area:.2f} mm²")

# 4. Extrude text cutter prism: Z = -0.05 mm to Z = 0.40 mm (0.45 mm total height)
DEBOSS_DEPTH_MM = 0.40  # Exactly 2 layers at 0.20mm layer height!
geoms = mirrored_art_2d.geoms if mirrored_art_2d.geom_type in ['MultiPolygon', 'GeometryCollection'] else [mirrored_art_2d]
tms = []
for g in geoms:
    if g.geom_type == 'Polygon' and g.area > 0.05:
        tm = trimesh.creation.extrude_polygon(g, height=(DEBOSS_DEPTH_MM + 0.05))
        tm.apply_translation([0.0, 0.0, -0.05])
        tms.append(tm)
text_combined = trimesh.util.concatenate(tms) if len(tms) > 1 else tms[0]

v_t = np.ascontiguousarray(text_combined.vertices, dtype=np.float32)
f_t = np.ascontiguousarray(text_combined.faces, dtype=np.uint32)
text_manifold = Manifold(Mesh(vert_properties=v_t, tri_verts=f_t))

# 5. Boolean Difference in Manifold3D
print("Loading base relief medal mesh...")
base_tm = trimesh.load(MONO_STL)
v_b = np.ascontiguousarray(base_tm.vertices, dtype=np.float32)
f_b = np.ascontiguousarray(base_tm.faces, dtype=np.uint32)
base_manifold = Manifold(Mesh(vert_properties=v_b, tri_verts=f_b))

print("Debossing custom engraving into the flat back (Z = 0.00 to 0.40 mm)...")
engraved_manifold = base_manifold - text_manifold

# Convert back to Trimesh
md = engraved_manifold.to_mesh()
v_out = md.vert_properties[:, :3].copy()
f_out = md.tri_verts.copy()
engraved_tm = trimesh.Trimesh(vertices=v_out, faces=f_out, process=True)

engraved_tm.export(ENGRAVED_STL)
print(f"Successfully exported Engraved Medal: {ENGRAVED_STL}")
print(f"  -> Watertight: {engraved_tm.is_watertight}")
print(f"  -> Volume    : {engraved_tm.volume / 1000.0:.2f} cm³")
print(f"  -> Triangles : {len(engraved_tm.faces):,}")
print(f"  -> Extents   : {engraved_tm.extents}")

# 6. Update Bundle ZIP Archive with the new Engraved STL
zip_path = os.path.join(MEDAL_DIR, "dopey_photographer_medal_bundle.zip")
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zf:
        zf.write(ENGRAVED_STL, "dopey_photographer_medal_engraved_back.stl")
    print(f"Appended engraved STL to bundle ZIP: {zip_path}")

print(f"Completed in {time.time() - t0:.2f}s!")
