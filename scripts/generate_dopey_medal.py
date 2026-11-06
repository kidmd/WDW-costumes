#!/usr/bin/env python3
"""
Generate 3D-Printable "DOPEY PHOTOGRAPHER - runDisney 2026" Finisher Medal
for the Main Street Electrical Parade (WDW 10K) Family Team!

Produces:
1. Monolithic Bas-Relief Finisher Medal (`dopey_photographer_medal_relief.stl`)
   - Standard runDisney Finisher Medal size: 90.0 mm wide x 105.0 mm tall (with integrated 38mm ribbon slot) x 6.0 mm thick
   - High-resolution 3D sculpted relief with raised banner, characters, tripod camera, runners, and integrated top ribbon loop
2. Snapmaker U1 4-Color Multi-Material Assembly (`dopey_photographer_medal_multicolor.3mf` & `.zip` bundle)
   - T0 (Extruder 1): Antique Bronze / Gold Main Medal Body & Sculpted Relief
   - T1 (Extruder 2): Dopey Green Enamel Hat (3D sculpted relief inlay)
   - T2 (Extruder 3): Dopey Purple Enamel Robe (3D sculpted relief inlay)
   - T3 (Extruder 4): Dark Bronze / Black Outlines & Recessed Shadow Accents
"""

import os
import re
import time
import uuid
import shutil
import zipfile
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh
from manifold3d import Manifold, Mesh

import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("=" * 72)
print("*** IMAGINEERING MEDAL FOUNDRY - DOPEY PHOTOGRAPHER runDisney 2026 ***")
print("=" * 72)
t0 = time.time()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "3d_panels", "dopey_medal")
os.makedirs(OUT_DIR, exist_ok=True)

UPLOADED_IMG = r"C:/Users/Kiddi/.gemini/antigravity/brain/10fbdacf-3971-4404-8a34-b71fb013f1c7/.user_uploaded/media_1793939888753_1d555805.jpg"
ASSET_BACKUP = os.path.join(BASE_DIR, "assets", "dopey_photographer_medal_2026.jpg")
if os.path.exists(UPLOADED_IMG) and not os.path.exists(ASSET_BACKUP):
    os.makedirs(os.path.dirname(ASSET_BACKUP), exist_ok=True)
    shutil.copyfile(UPLOADED_IMG, ASSET_BACKUP)

img_path = UPLOADED_IMG if os.path.exists(UPLOADED_IMG) else ASSET_BACKUP
img = Image.open(img_path).convert("RGB")
arr = np.array(img)
h, w, _ = arr.shape

# ---------------------------------------------------------------------------
# 1. EXTRACT FOREGROUND MASK & EXACT PHYSICAL SCALING (90.0 mm Diameter)
# ---------------------------------------------------------------------------
is_white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
num_l, labels = cv2.connectedComponents(is_white.astype(np.uint8))
fg_mask = (labels != labels[0, 0])
fg_mask = cv2.morphologyEx(fg_mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0

y_idx, x_idx = np.where(fg_mask)
min_x, max_x = int(x_idx.min()), int(x_idx.max())
min_y, max_y = int(y_idx.min()), int(y_idx.max())
w_px = max_x - min_x + 1
h_px = max_y - min_y + 1

MEDAL_WIDTH_MM = 90.0
scale = MEDAL_WIDTH_MM / float(w_px)
MEDAL_ART_HEIGHT_MM = round(h_px * scale, 2)

print(f"Loaded artwork: {w}x{h} px | Medal foreground: {w_px}x{h_px} px")
print(f"Physical Medal Scale: {MEDAL_WIDTH_MM:.1f} mm W x {MEDAL_ART_HEIGHT_MM:.1f} mm H ({scale:.4f} mm/px)")

# ---------------------------------------------------------------------------
# 2. SEGMENT COLOR REGIONS (GREEN HAT, PURPLE ROBE, DARK ACCENTS)
# ---------------------------------------------------------------------------
hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
R, G, B = arr[:, :, 0].astype(np.float32), arr[:, :, 1].astype(np.float32), arr[:, :, 2].astype(np.float32)

# A. Green Hat Mask
hat_roi = np.zeros((h, w), dtype=bool)
hat_roi[330:580, 500:800] = True
green_raw = fg_mask & hat_roi & (((H >= 35) & (H <= 90) & (S >= 45) & (V >= 25)) | ((G - R > 15) & (G - B > 15)))
num_g, g_labels, g_stats, _ = cv2.connectedComponentsWithStats(green_raw.astype(np.uint8))
clean_green = np.zeros((h, w), dtype=bool)
for i in range(1, num_g):
    if g_stats[i, cv2.CC_STAT_AREA] >= 50:
        clean_green |= (g_labels == i)
clean_green = cv2.morphologyEx(clean_green.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0

# B. Purple Robe Mask (preserving gold sleeve cuff patch, button, and belt buckle)
robe_roi = np.zeros((h, w), dtype=bool)
robe_roi[490:840, 460:760] = True
purple_raw = fg_mask & robe_roi & (((H >= 120) & (H <= 172) & (S >= 35) & (V >= 35)) | ((B - G > 15) & (R - G > 10)))
num_p, p_labels, p_stats, _ = cv2.connectedComponentsWithStats(purple_raw.astype(np.uint8))
clean_purple = np.zeros((h, w), dtype=bool)
for i in range(1, num_p):
    if p_stats[i, cv2.CC_STAT_AREA] >= 80:
        clean_purple |= (p_labels == i)
clean_purple = cv2.morphologyEx(clean_purple.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
is_gold_detail = fg_mask & robe_roi & (H >= 12) & (H <= 32) & (S >= 50) & (V >= 90) & (G > B + 15)
clean_purple = clean_purple & (~is_gold_detail) & (~clean_green)

# C. Dark Bronze / Black Outline & Recessed Crevice Mask
lum = 0.299 * R + 0.587 * G + 0.114 * B
local_mean = cv2.GaussianBlur(lum, (25, 25), 6.0)
# Restrict dark inlay away from outer 1.5mm perimeter rim so the outer medal edge is 100% solid bronze
inner_fg = cv2.erode(fg_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))) > 0
dark_raw = inner_fg & (~clean_green) & (~clean_purple) & ((lum < 55) | ((lum < 78) & (lum < local_mean - 26)))
dark_closed = cv2.morphologyEx(dark_raw.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))) > 0
num_d, d_labels, d_stats, _ = cv2.connectedComponentsWithStats(dark_closed.astype(np.uint8))
clean_dark = np.zeros((h, w), dtype=bool)
for i in range(1, num_d):
    if d_stats[i, cv2.CC_STAT_AREA] >= 65:
        clean_dark |= (d_labels == i)

# ---------------------------------------------------------------------------
# 3. BUILD SCULPTED 3D BAS-RELIEF HEIGHTMAP
# ---------------------------------------------------------------------------
# Normalize luminance in [0, 1]
lum_norm = np.clip(lum / 255.0, 0.0, 1.0)

# Enhance local relief contrast (unsharp mask / local detail boost) so lettering, faces,
# runners, camera bellows, and tripod legs pop with crisp 3D depth
blur_broad = cv2.GaussianBlur(lum_norm, (31, 31), 8.0)
detail_high = lum_norm - blur_broad

relief_01 = np.clip(0.75 * lum_norm + 0.45 * detail_high, 0.0, 1.0)

# Boost Green Hat and Purple Robe so they sit proudly as rounded 3D enamel domes
g_vals = lum_norm[clean_green]
if len(g_vals) > 0:
    g_norm = (g_vals - g_vals.min()) / max(0.05, g_vals.max() - g_vals.min())
    # Distance transform from edge of hat for smooth dome pillowing
    g_dist = cv2.distanceTransform(clean_green.astype(np.uint8), cv2.DIST_L2, 5)
    g_dome = np.clip(g_dist / max(1.0, g_dist.max()), 0.0, 1.0) ** 0.5
    relief_01[clean_green] = np.clip(0.58 + 0.25 * g_norm + 0.14 * g_dome[clean_green], 0.55, 0.96)

p_vals = lum_norm[clean_purple]
if len(p_vals) > 0:
    p_norm = (p_vals - p_vals.min()) / max(0.05, p_vals.max() - p_vals.min())
    p_dist = cv2.distanceTransform(clean_purple.astype(np.uint8), cv2.DIST_L2, 5)
    p_dome = np.clip(p_dist / max(1.0, p_dist.max()), 0.0, 1.0) ** 0.5
    relief_01[clean_purple] = np.clip(0.54 + 0.26 * p_norm + 0.14 * p_dome[clean_purple], 0.50, 0.94)

# Smooth slightly with bilateral filter to eliminate JPEG compression artifacts while keeping edges razor-sharp
relief_smooth = cv2.bilateralFilter(relief_01.astype(np.float32), d=5, sigmaColor=0.08, sigmaSpace=2.5)
relief_smooth = cv2.GaussianBlur(relief_smooth, (3, 3), 0.5)

# Map relief_smooth [0, 1] to physical Z height (mm):
# Base solid medal backing: Z = 0.00 to 3.40 mm (3.40 mm solid structural base)
# Sculpted bas-relief: Z = 3.40 mm (deepest grooves) to 6.00 mm (highest peaks = 2.60 mm relief depth)
BASE_Z_MM = 3.40
RELIEF_DEPTH_MM = 2.60
TOTAL_Z_MM = BASE_Z_MM + RELIEF_DEPTH_MM  # 6.00 mm

# ---------------------------------------------------------------------------
# 4. CONSTRUCT 2D SHAPELY GEOMETRY (SILHOUETTE + INTEGRATED 38MM RIBBON LOOP)
# ---------------------------------------------------------------------------
def mask_to_shapely(mask_img, simplify_tol=0.06, min_area=0.20):
    contours, hierarchy = cv2.findContours(mask_img.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if not contours or hierarchy is None:
        return sg.Polygon()
    hierarchy = hierarchy[0]
    polys = []
    for idx, c in enumerate(contours):
        if hierarchy[idx][3] == -1 and len(c) >= 3:
            shell = [((pt[0][0] - min_x) * scale, (max_y - pt[0][1]) * scale) for pt in c]
            holes = []
            child = hierarchy[idx][2]
            while child != -1:
                if len(contours[child]) >= 3:
                    h_pts = [((pt[0][0] - min_x) * scale, (max_y - pt[0][1]) * scale) for pt in contours[child]]
                    holes.append(h_pts)
                child = hierarchy[child][0]
            p = sg.Polygon(shell, holes).buffer(0)
            if not p.is_empty and p.area >= min_area:
                polys.append(p.simplify(simplify_tol, preserve_topology=True).buffer(0))
    return unary_union(polys) if polys else sg.Polygon()

medal_poly = mask_to_shapely(fg_mask, simplify_tol=0.06, min_area=10.0)

# Design Integrated Top Neck-Ribbon Slot (for standard 38mm / 1.5" runDisney ribbon)
cx_mm = MEDAL_WIDTH_MM / 2.0  # 45.0 mm
top_y = MEDAL_ART_HEIGHT_MM   # ~96.45 mm

# Outer collar lug smoothly merges into the top "DOPEY" scroll banner
# Width = 46.0 mm (X from 22.0 to 68.0 mm), extending up to Y = top_y + 8.5 mm (Total height ~105.0 mm)
loop_outer = sg.box(cx_mm - 19.5, top_y - 8.0, cx_mm + 19.5, top_y + 5.0).buffer(3.5, resolution=32)
# Inner ribbon slot: 38.6 mm wide x 4.2 mm tall stadium slot centered at Y = top_y + 3.4 mm
slot_inner = sg.box(cx_mm - 17.2, top_y + 3.3, cx_mm + 17.2, top_y + 3.5).buffer(2.0, resolution=32)
# Recessed decorative bevel surround around the slot
loop_bevel_ring = loop_outer.buffer(-1.4).difference(slot_inner.buffer(1.4))

full_medal_2d = unary_union([medal_poly, loop_outer]).difference(slot_inner).simplify(0.04, preserve_topology=True).buffer(0)
loop_only_2d = loop_outer.difference(medal_poly).difference(slot_inner)

print(f"2D Silhouette + Ribbon Loop ready: {full_medal_2d.bounds[2]-full_medal_2d.bounds[0]:.2f} mm W x {full_medal_2d.bounds[3]-full_medal_2d.bounds[1]:.2f} mm H")

# ---------------------------------------------------------------------------
# 5. BUILD CLOSED WATERTIGHT HEIGHTFIELD MANIFOLD & BOOLEAN INTERSECT
# ---------------------------------------------------------------------------
# Grid covering X in [-1.5, 91.5] mm, Y in [-1.5, 106.5] mm
grid_w = 560
grid_h = 650
xs = np.linspace(-1.5, 91.5, grid_w, dtype=np.float32)
ys = np.linspace(-1.5, 106.5, grid_h, dtype=np.float32)
XX, YY = np.meshgrid(xs, ys)

px_map = (XX / scale + min_x).astype(np.float32)
py_map = (max_y - YY / scale).astype(np.float32)

grid_relief = cv2.remap(relief_smooth, px_map, py_map, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0.5)
grid_fg = cv2.remap(fg_mask.astype(np.uint8) * 255, px_map, py_map, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) > 127

# Compute Z height across the grid:
# Inside the medal artwork: BASE_Z_MM + RELIEF_DEPTH_MM * grid_relief
# On the top ribbon loop lug (outside medal_poly): sculpted 5.2mm collar bar with a raised 5.6mm border rim around the slot!
ZZ = BASE_Z_MM + RELIEF_DEPTH_MM * grid_relief

# Smoothly blend the ribbon loop height where YY > top_y - 6.0 and not in grid_fg
loop_mask = ~grid_fg
# Distance from slot center (cx_mm, top_y + 3.4) to give the ribbon loop a handsome raised border frame
slot_dx = np.maximum(0.0, np.abs(XX - cx_mm) - 17.2)
slot_dy = np.abs(YY - (top_y + 3.4))
slot_dist = np.hypot(slot_dx, slot_dy)
# Loop bar is 5.3 mm thick, with a 5.7 mm raised rim right around the ribbon slot (2.0 < slot_dist < 3.6)
loop_z = np.where((slot_dist >= 2.0) & (slot_dist <= 3.7), 5.65, 5.15)
ZZ = np.where(loop_mask, loop_z, ZZ).astype(np.float32)

# Build watertight heightfield Manifold
N = grid_h * grid_w
top_v = np.column_stack([XX.ravel(), YY.ravel(), ZZ.ravel()]).astype(np.float32)
bot_v = np.column_stack([XX.ravel(), YY.ravel(), np.zeros(N, dtype=np.float32)]).astype(np.float32)
verts = np.vstack([top_v, bot_v])

idx = np.arange(N, dtype=np.uint32).reshape(grid_h, grid_w)
i00 = idx[:-1, :-1].ravel()
i10 = idx[:-1, 1:].ravel()
i01 = idx[1:, :-1].ravel()
i11 = idx[1:, 1:].ravel()

top_f1 = np.column_stack([i00, i10, i11])
top_f2 = np.column_stack([i00, i11, i01])

b00, b10, b01, b11 = i00 + N, i10 + N, i01 + N, i11 + N
bot_f1 = np.column_stack([b00, b11, b10])
bot_f2 = np.column_stack([b00, b01, b11])

e_bot = idx[0, :]
w_bot1 = np.column_stack([e_bot[:-1] + N, e_bot[1:] + N, e_bot[1:]])
w_bot2 = np.column_stack([e_bot[:-1] + N, e_bot[1:], e_bot[:-1]])

e_top = idx[-1, :]
w_top1 = np.column_stack([e_top[:-1], e_top[1:], e_top[1:] + N])
w_top2 = np.column_stack([e_top[:-1], e_top[1:] + N, e_top[:-1] + N])

e_left = idx[:, 0]
w_left1 = np.column_stack([e_left[:-1], e_left[1:], e_left[1:] + N])
w_left2 = np.column_stack([e_left[:-1], e_left[1:] + N, e_left[:-1] + N])

e_right = idx[:, -1]
w_right1 = np.column_stack([e_right[:-1] + N, e_right[1:] + N, e_right[1:]])
w_right2 = np.column_stack([e_right[:-1] + N, e_right[1:], e_right[:-1]])

faces = np.vstack([
    top_f1, top_f2, bot_f1, bot_f2,
    w_bot1, w_bot2, w_top1, w_top2, w_left1, w_left2, w_right1, w_right2
]).astype(np.uint32)

hf_manifold = Manifold(Mesh(vert_properties=verts, tri_verts=faces))

def shapely_to_manifold(poly, z0, z1):
    if poly is None or poly.is_empty:
        return None
    geoms = poly.geoms if poly.geom_type in ['MultiPolygon', 'GeometryCollection'] else [poly]
    tms = []
    for g in geoms:
        if g.geom_type == 'Polygon' and g.area > 0.05:
            tm = trimesh.creation.extrude_polygon(g, height=(z1 - z0))
            tm.apply_translation([0.0, 0.0, z0])
            tms.append(tm)
    if not tms:
        return None
    combined = trimesh.util.concatenate(tms) if len(tms) > 1 else tms[0]
    v = np.ascontiguousarray(combined.vertices, dtype=np.float32)
    f = np.ascontiguousarray(combined.faces, dtype=np.uint32)
    return Manifold(Mesh(vert_properties=v, tri_verts=f))

def manifold_to_trimesh(m):
    md = m.to_mesh()
    v = md.vert_properties[:, :3].copy()
    f = md.tri_verts.copy()
    return trimesh.Trimesh(vertices=v, faces=f, process=True)

# Extrude outer silhouette prism and intersect with heightfield
sil_prism = shapely_to_manifold(full_medal_2d, 0.0, 10.0)
monolithic_medal_m = hf_manifold ^ sil_prism
monolithic_tm = manifold_to_trimesh(monolithic_medal_m)

mono_stl_path = os.path.join(OUT_DIR, "dopey_photographer_medal_relief.stl")
monolithic_tm.export(mono_stl_path)
print(f"Exported Monolithic Relief Medal: {mono_stl_path}")
print(f"  -> Watertight: {monolithic_tm.is_watertight} | Volume: {monolithic_tm.volume / 1000.0:.2f} cm³ | Triangles: {len(monolithic_tm.faces):,}")

# ---------------------------------------------------------------------------
# 6. BUILD 4-COLOR SNAPMAKER U1 MULTI-MATERIAL PARTS (T0, T1, T2, T3)
# ---------------------------------------------------------------------------
print("\nBuilding 4-Color Snapmaker U1 Multi-Material Components...")

# Color inlay depth: from Z = 3.20 mm up to the exact sculpted 3D relief surface!
# Why Z = 3.20 mm?
# - From Z = 0.00 to 3.20 mm (first 16 layers at 0.20mm), ONLY Toolhead 0 (Antique Bronze) prints!
#   Zero tool changes for the entire structural base and ribbon loop!
# - Above Z = 3.20 mm, the Green Hat, Purple Robe, and Dark Outline inlays extend all the way
#   through the 3D relief surface, giving 100% solid color saturation across every contour!
INLAY_Z0 = 3.20

green_poly_2d = mask_to_shapely(clean_green, simplify_tol=0.05, min_area=0.20).intersection(full_medal_2d)
purple_poly_2d = mask_to_shapely(clean_purple, simplify_tol=0.05, min_area=0.20).difference(green_poly_2d).intersection(full_medal_2d)
dark_poly_2d = mask_to_shapely(clean_dark, simplify_tol=0.07, min_area=0.30).difference(green_poly_2d).difference(purple_poly_2d).intersection(full_medal_2d)

m_green_prism = shapely_to_manifold(green_poly_2d, INLAY_Z0, 10.0)
m_purple_prism = shapely_to_manifold(purple_poly_2d, INLAY_Z0, 10.0)
m_dark_prism = shapely_to_manifold(dark_poly_2d, INLAY_Z0, 10.0)

# Intersect each color prism with the sculpted medal manifold so top surfaces match the 3D relief!
m_green = monolithic_medal_m ^ m_green_prism
m_purple = monolithic_medal_m ^ m_purple_prism
m_dark = monolithic_medal_m ^ m_dark_prism

# Subtract all 3 inlays from the main Bronze body so there is zero mesh overlap in the slicer
m_bronze = monolithic_medal_m - m_green_prism - m_purple_prism - m_dark_prism

tm_bronze = manifold_to_trimesh(m_bronze)
tm_green = manifold_to_trimesh(m_green)
tm_purple = manifold_to_trimesh(m_purple)
tm_dark = manifold_to_trimesh(m_dark)

bronze_stl = os.path.join(OUT_DIR, "dopey_medal_1_bronze_body.stl")
green_stl = os.path.join(OUT_DIR, "dopey_medal_2_green_hat.stl")
purple_stl = os.path.join(OUT_DIR, "dopey_medal_3_purple_robe.stl")
dark_stl = os.path.join(OUT_DIR, "dopey_medal_4_dark_outlines.stl")

tm_bronze.export(bronze_stl)
tm_green.export(green_stl)
tm_purple.export(purple_stl)
tm_dark.export(dark_stl)

print(f"  -> T0 Bronze Body   : {len(tm_bronze.faces):,} tris | Watertight: {tm_bronze.is_watertight} | Vol: {tm_bronze.volume/1000:.2f} cm³")
print(f"  -> T1 Green Hat     : {len(tm_green.faces):,} tris | Watertight: {tm_green.is_watertight} | Vol: {tm_green.volume/1000:.2f} cm³")
print(f"  -> T2 Purple Robe   : {len(tm_purple.faces):,} tris | Watertight: {tm_purple.is_watertight} | Vol: {tm_purple.volume/1000:.2f} cm³")
print(f"  -> T3 Dark Outlines : {len(tm_dark.faces):,} tris | Watertight: {tm_dark.is_watertight} | Vol: {tm_dark.volume/1000:.2f} cm³")

# ---------------------------------------------------------------------------
# 7. EXPORT PRE-ASSEMBLED 4-COLOR 3MF FOR SNAPMAKER ORCA / BAMBU / ORCASLICER
# ---------------------------------------------------------------------------
def export_medal_3mf(scene_items, mf3_path, assembly_name="Dopey_Photographer_Medal_2026"):
    clean_assembly_name = re.sub(r'[^A-Za-z0-9_]', '_', str(assembly_name)).strip('_')
    scene = trimesh.Scene(scene_items)
    scene.export(mf3_path)

    with zipfile.ZipFile(mf3_path, 'r') as zin:
        files_data = {name: zin.read(name) for name in zin.namelist()}

    if '3D/3dmodel.model' in files_data:
        ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
        p_ns = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
        ET.register_namespace('', ns)
        ET.register_namespace('p', p_ns)

        root = ET.fromstring(files_data['3D/3dmodel.model'])
        resources = root.find(f"{{{ns}}}resources")
        build = root.find(f"{{{ns}}}build")
        if resources is not None and build is not None:
            objs = resources.findall(f"{{{ns}}}object")
            if len(objs) > 1:
                max_id = max(int(o.attrib.get('id', 0)) for o in objs)
                parent_id = str(max_id + 1)
                parent_obj = ET.Element(f"{{{ns}}}object", {
                    'id': parent_id,
                    'name': clean_assembly_name,
                    'type': 'model',
                    f"{{{p_ns}}}UUID": str(uuid.uuid4())
                })
                comps = ET.SubElement(parent_obj, f"{{{ns}}}components")
                part_mappings = []
                for o in objs:
                    oid = o.attrib.get('id')
                    raw_oname = o.attrib.get('name', '')
                    clean_oname = re.sub(r'[^A-Za-z0-9_]', '_', raw_oname).strip('_')
                    o.attrib['name'] = clean_oname

                    prefix = clean_oname.split('_')[0]
                    ext_id = prefix if prefix in ('1', '2', '3', '4') else '1'
                    part_mappings.append((oid, clean_oname, ext_id))
                    ET.SubElement(comps, f"{{{ns}}}component", {
                        'objectid': oid,
                        'transform': '1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0',
                        f"{{{p_ns}}}UUID": str(uuid.uuid4())
                    })
                resources.append(parent_obj)
                for item in list(build):
                    build.remove(item)
                ET.SubElement(build, f"{{{ns}}}item", {
                    'objectid': parent_id,
                    'transform': '1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0',
                    f"{{{p_ns}}}UUID": str(uuid.uuid4()),
                    'partnumber': clean_assembly_name
                })
                files_data['3D/3dmodel.model'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

                cfg_root = ET.Element('config')
                plate_elem = ET.SubElement(cfg_root, 'plate')
                ET.SubElement(plate_elem, 'metadata', {'key': 'plater_id', 'value': '1'})
                ET.SubElement(plate_elem, 'metadata', {'key': 'plater_name', 'value': ''})

                obj_elem = ET.SubElement(cfg_root, 'object', {'id': parent_id})
                ET.SubElement(obj_elem, 'metadata', {'key': 'name', 'value': clean_assembly_name})
                for oid, oname, ext_id in part_mappings:
                    part_elem = ET.SubElement(obj_elem, 'part', {'id': oid, 'subtype': 'normal_part'})
                    ET.SubElement(part_elem, 'metadata', {'key': 'name', 'value': oname})
                    ET.SubElement(part_elem, 'metadata', {'key': 'extruder', 'value': ext_id})

                files_data['Metadata/model_settings.config'] = ET.tostring(cfg_root, encoding='utf-8', xml_declaration=True)

                if 'Metadata/slice_info.config' in files_data:
                    del files_data['Metadata/slice_info.config']

                if '[Content_Types].xml' in files_data:
                    ct_xml = files_data['[Content_Types].xml'].decode('utf-8')
                    ct_xml = re.sub(r'<Override PartName="/Metadata/slice_info\.config"[^>]*/>\s*', '', ct_xml)
                    if 'Metadata/model_settings.config' not in ct_xml:
                        ct_insert = '  <Override PartName="/Metadata/model_settings.config" ContentType="application/vnd.ms-package.config+xml"/>\n</Types>'
                        ct_xml = ct_xml.replace('</Types>', ct_insert)
                    files_data['[Content_Types].xml'] = ct_xml.encode('utf-8')

                tmp_3mf = mf3_path + '.tmp'
                with zipfile.ZipFile(tmp_3mf, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for name, content in files_data.items():
                        zout.writestr(name, content)
                if os.path.exists(mf3_path):
                    os.remove(mf3_path)
                shutil.move(tmp_3mf, mf3_path)

scene_parts = {
    "1_Antique_Bronze_Medal_Body": tm_bronze,
    "2_Dopey_Green_Hat": tm_green,
    "3_Dopey_Purple_Robe": tm_purple,
    "4_Dark_Bronze_Outlines": tm_dark
}

mf3_path = os.path.join(OUT_DIR, "dopey_photographer_medal_multicolor.3mf")
export_medal_3mf(scene_parts, mf3_path)
print(f"Exported 4-Color Assembled 3MF: {mf3_path}")

# Bundle into a convenient ZIP archive with README instructions
zip_path = os.path.join(OUT_DIR, "dopey_photographer_medal_bundle.zip")
readme_txt = """========================================================================
DOPEY PHOTOGRAPHER - runDisney 2026 FINISHER MEDAL (3D PRINT BUNDLE)
========================================================================

DIMENSIONS:
- Medal Diameter (Width) : 90.0 mm (3.54 inches)
- Total Height with Loop : 105.0 mm (4.13 inches)
- Total Thickness        : 6.0 mm (3.4mm solid base + 2.6mm sculpted 3D bas-relief)
- Top Ribbon Slot        : 38.6 mm x 4.2 mm (fits standard 1.5" / 38mm runDisney neck ribbons)

INCLUDED FILES:
1. dopey_photographer_medal_relief.stl
   - Single-piece monolithic 3D bas-relief medal.
   - Ideal for printing in Antique Gold / Bronze Silk PLA or Resin.

2. dopey_photographer_medal_multicolor.3mf
   - Pre-assembled 4-toolhead project file for Snapmaker U1 / OrcaSlicer / Bambu Studio.
   - Extruder 1 (T0): Antique Gold / Bronze Silk PLA (Main Medal & Sculpted Relief)
   - Extruder 2 (T1): Green PLA (Dopey's Hat)
   - Extruder 3 (T2): Purple / Lilac PLA (Dopey's Robe)
   - Extruder 4 (T3): Black / Dark Bronze PLA (Recessed Outlines & Lettering Shadows)
   - NOTE: Layers from Z = 0.00mm to 3.20mm print 100% in Extruder 1 (Bronze) with zero tool swaps!

3. Individual Multi-Color STLs (if importing manually as a multi-part object):
   - dopey_medal_1_bronze_body.stl
   - dopey_medal_2_green_hat.stl
   - dopey_medal_3_purple_robe.stl
   - dopey_medal_4_dark_outlines.stl

RECOMMENDED SLICER SETTINGS:
- Layer Height : 0.12 mm or 0.16 mm (for ultra-smooth relief gradation)
- Nozzle       : 0.4 mm (enable Arachne perimeter generator for crisp lettering)
- Infill       : 20% - 25% Gyroid (add extra perimeters/infill if you want hefty metal-like weight!)
- Supports     : NONE REQUIRED (100% flat back at Z = 0.00 mm)
"""

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("README_DOPEY_MEDAL.txt", readme_txt)
    zf.write(mono_stl_path, "dopey_photographer_medal_relief.stl")
    zf.write(mf3_path, "dopey_photographer_medal_multicolor.3mf")
    zf.write(bronze_stl, "dopey_medal_1_bronze_body.stl")
    zf.write(green_stl, "dopey_medal_2_green_hat.stl")
    zf.write(purple_stl, "dopey_medal_3_purple_robe.stl")
    zf.write(dark_stl, "dopey_medal_4_dark_outlines.stl")

print(f"Exported Complete Bundle ZIP: {zip_path} ({os.path.getsize(zip_path)/1024/1024:.2f} MB)")
print(f"Done in {time.time() - t0:.2f}s!")
