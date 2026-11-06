#!/usr/bin/env python3
"""
Engrave Custom 1-Piece Nameplate onto the Flat Back of the Dopey Photographer Medal.

Text:
- Line 1: Tom Reinsvold
- Line 2: 1st in Age Group
- Line 3: 48.6 photos / mile

Features:
- Micro-debossed: 0.40 mm depth (universal: exactly 2 layers @ 0.20mm, 3 layers @ 0.12mm, or 5 layers @ 0.08mm).
- True 5-pointed vector stars (★ ★ ★) drawn geometrically to replace unrenderable Unicode glyphs.
- Properly mirrored across X=45.0mm so when the medal is turned over, it reads naturally left-to-right!
- Updates both the Single-Color STL and the 4-Color 3MF project so both show the authentic back engraving!
"""

import os
import sys
import time
import shutil
import zipfile
import re
import uuid
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import shapely.geometry as sg
from shapely.ops import unary_union
from shapely.affinity import scale as shp_scale
import trimesh
from manifold3d import Manifold, Mesh

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("=" * 72)
print("*** ENGRAVING DOPEY PHOTOGRAPHER MEDAL (CUSTOM BACK - TRUE STARS) ***")
print("=" * 72)
t0 = time.time()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDAL_DIR = os.path.join(BASE_DIR, "3d_panels", "dopey_medal")
MONO_STL = os.path.join(MEDAL_DIR, "dopey_photographer_medal_relief.stl")
ENGRAVED_STL = os.path.join(MEDAL_DIR, "dopey_photographer_medal_engraved_back.stl")
BRONZE_STL = os.path.join(MEDAL_DIR, "dopey_medal_1_bronze_body.stl")
GREEN_STL = os.path.join(MEDAL_DIR, "dopey_medal_2_green_hat.stl")
PURPLE_STL = os.path.join(MEDAL_DIR, "dopey_medal_3_purple_robe.stl")
DARK_STL = os.path.join(MEDAL_DIR, "dopey_medal_4_dark_outlines.stl")
MF3_PATH = os.path.join(MEDAL_DIR, "dopey_photographer_medal_multicolor.3mf")

if not os.path.exists(MONO_STL):
    raise FileNotFoundError(f"Missing base STL: {MONO_STL}")

# 1. Rasterize High-Resolution Back Text
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

cx_px = 45.0 * SCALE_PX
def mm_to_py(y_mm):
    return (105.0 - y_mm) * SCALE_PX

# Draw 3 text lines
lines_to_draw = [
    ("Tom Reinsvold", font_name, 56.5),
    ("1st in Age Group", font_sub, 46.5),
    ("48.6 photos / mile", font_sub, 36.5),
]

for text, font, y_mm in lines_to_draw:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px = cx_px - tw / 2.0 - bbox[0]
    py = mm_to_py(y_mm) - th / 2.0 - bbox[1]
    draw.text((px, py), text, fill=255, font=font)

# Add decorative circular framing ring on back:
center_y_px = mm_to_py(46.0)
r_out_px = 42.0 * SCALE_PX
draw.ellipse([cx_px - r_out_px, center_y_px - r_out_px, cx_px + r_out_px, center_y_px + r_out_px], outline=255, width=int(1.2 * SCALE_PX))

# 2. Extract 2D Text & Ring Contours to Shapely
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

text_and_ring_2d = unary_union(polys).simplify(0.035, preserve_topology=True).buffer(0.06)

# Generate True Geometric 5-Point Vector Stars in 3D Millimeter Space
# (Every star has its top point pointing strictly straight UP (+Y) with zero tilt!)
def make_clean_upright_star(center_x, center_y, r_out, r_in=None):
    if r_in is None:
        r_in = r_out * 0.382
    pts = []
    for i in range(10):
        r = r_out if (i % 2 == 0) else r_in
        angle = np.radians(90.0 - i * 36.0) # i=0 is angle +90 deg (strictly pointing straight UP!)
        pts.append((round(center_x + r * np.cos(angle), 4), round(center_y + r * np.sin(angle), 4)))
    return sg.Polygon(pts)

clean_stars = [
    # Top Star Triplet (above Name, Y = 66.5 mm)
    make_clean_upright_star(45.0, 66.5, 3.6),  # Center star
    make_clean_upright_star(34.0, 66.5, 2.6),  # Left star
    make_clean_upright_star(56.0, 66.5, 2.6),  # Right star
    # Bottom Star Triplet (below 48.6 photos/mile, Y = 26.5 mm)
    make_clean_upright_star(45.0, 26.5, 3.6),  # Center star
    make_clean_upright_star(34.0, 26.5, 2.6),  # Left star
    make_clean_upright_star(56.0, 26.5, 2.6),  # Right star
]

back_art_2d = unary_union([text_and_ring_2d] + clean_stars).buffer(0)

# 3. CRITICAL: Mirror horizontally across X = 45.0 mm so it reads left-to-right when viewed from the back!
mirrored_art_2d = shp_scale(back_art_2d, xfact=-1.0, yfact=1.0, origin=(45.0, 46.0)).buffer(0)
print(f"Extracted back engraving geometry: {len(mirrored_art_2d.geoms) if hasattr(mirrored_art_2d, 'geoms') else 1} parts (with true 5-pointed stars)")

# 4. Extrude text cutter prism: Z = -0.05 mm to Z = 0.40 mm
DEBOSS_DEPTH_MM = 0.40  # Exactly 0.40 mm (compatible with 0.08, 0.12, 0.16, 0.20 mm layer heights!)
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

# 5. Boolean Difference for Monolithic Relief Medal
print("Debossing custom back onto monolithic medal...")
base_tm = trimesh.load(MONO_STL)
v_b = np.ascontiguousarray(base_tm.vertices, dtype=np.float32)
f_b = np.ascontiguousarray(base_tm.faces, dtype=np.uint32)
base_manifold = Manifold(Mesh(vert_properties=v_b, tri_verts=f_b))

engraved_manifold = base_manifold - text_manifold
md = engraved_manifold.to_mesh()
engraved_tm = trimesh.Trimesh(vertices=md.vert_properties[:, :3].copy(), faces=md.tri_verts.copy(), process=True)

engraved_tm.export(ENGRAVED_STL)
print(f"Exported Monolithic Engraved Medal: {ENGRAVED_STL} (Watertight: {engraved_tm.is_watertight})")

# 6. Also Deboss Back into 4-Color Bronze Chassis & Update 3MF!
if os.path.exists(BRONZE_STL):
    print("Debossing custom back onto 4-Color Bronze Body...")
    bronze_raw = trimesh.load(BRONZE_STL)
    v_br = np.ascontiguousarray(bronze_raw.vertices, dtype=np.float32)
    f_br = np.ascontiguousarray(bronze_raw.faces, dtype=np.uint32)
    bronze_manifold = Manifold(Mesh(vert_properties=v_br, tri_verts=f_br))
    
    engraved_bronze_manifold = bronze_manifold - text_manifold
    md_br = engraved_bronze_manifold.to_mesh()
    engraved_bronze_tm = trimesh.Trimesh(vertices=md_br.vert_properties[:, :3].copy(), faces=md_br.tri_verts.copy(), process=True)
    engraved_bronze_tm.export(BRONZE_STL)
    print(f"Updated 4-Color Bronze Body STL: {BRONZE_STL}")

    # Re-export 4-Color 3MF
    if os.path.exists(GREEN_STL) and os.path.exists(PURPLE_STL) and os.path.exists(DARK_STL):
        tm_green = trimesh.load(GREEN_STL)
        tm_purple = trimesh.load(PURPLE_STL)
        tm_dark = trimesh.load(DARK_STL)

        scene_parts = {
            "1_Antique_Bronze_Medal_Body": engraved_bronze_tm,
            "2_Dopey_Green_Hat": tm_green,
            "3_Dopey_Purple_Robe": tm_purple,
            "4_Dark_Bronze_Outlines": tm_dark
        }
        
        # 3MF Export Helper
        clean_assembly_name = "Dopey_Photographer_Medal_2026"
        scene = trimesh.Scene(scene_parts)
        scene.export(MF3_PATH)

        with zipfile.ZipFile(MF3_PATH, 'r') as zin:
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

                    tmp_3mf = MF3_PATH + '.tmp'
                    with zipfile.ZipFile(tmp_3mf, 'w', zipfile.ZIP_DEFLATED) as zout:
                        for name, content in files_data.items():
                            zout.writestr(name, content)
                    if os.path.exists(MF3_PATH):
                        os.remove(MF3_PATH)
                    shutil.move(tmp_3mf, MF3_PATH)
        print(f"Re-exported 4-Color 3MF with Engraved Back: {MF3_PATH}")

# 7. Update Bundle ZIP Archive
zip_path = os.path.join(MEDAL_DIR, "dopey_photographer_medal_bundle.zip")
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(ENGRAVED_STL, "dopey_photographer_medal_engraved_back.stl")
        zf.write(MONO_STL, "dopey_photographer_medal_relief.stl")
        zf.write(MF3_PATH, "dopey_photographer_medal_multicolor.3mf")
        zf.write(BRONZE_STL, "dopey_medal_1_bronze_body.stl")
        zf.write(GREEN_STL, "dopey_medal_2_green_hat.stl")
        zf.write(PURPLE_STL, "dopey_medal_3_purple_robe.stl")
        zf.write(DARK_STL, "dopey_medal_4_dark_outlines.stl")
    print(f"Refreshed complete bundle ZIP: {zip_path}")

print(f"All models compiled in {time.time() - t0:.2f}s!")
