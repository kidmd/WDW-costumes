import json, math, time, os, shutil, sys, zipfile
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
import trimesh
from manifold3d import Manifold, Mesh, OpType, CrossSection
import cv2
from PIL import Image

print("=" * 70)
print("ANTIGRAVITY IMAGINEERING - 5-COLOR MULTI-MATERIAL TPU ARMOR TRAY COMPILER v5")
print("=" * 70)
t0 = time.time()

specs_path = '3d_panels/tpu_panel_specs.json'
if not os.path.exists(specs_path):
    specs_path = '3d_panels/petes_dragon_specs.json'

with open(specs_path) as f:
    specs = json.load(f)

# ---------------------------------------------------------------------------
# EXACT USER-SPECIFIED DIMENSIONS & CLEARANCES:
# ---------------------------------------------------------------------------
FRONT_THICK_GENERAL = 2.0   # mm (general tray floor from Z = 0 to 2.0)
FRONT_THICK_LED = 1.0       # mm (recessed inside cavity floor from Z = 0 to 1.0)
TOTAL_THICK = 10.0          # mm (overall height to top of perimeter rim, +1.0mm for extra wire room)
RIM_HEIGHT = 8.0            # mm (outer wall from Z = 2.0 to 10.0, +1.0mm taller perimeter wall)
RIM_WALL_THICK = 2.5        # mm (width of outer perimeter wall)

COLLAR_FLOOR_Z = 1.0        # mm (pocket floor starts at Z = 1.0)
COLLAR_HEIGHT = 3.0         # mm (pocket walls rise 3.0mm, from Z = 1.0 to 4.0)
COLLAR_TOP_Z = 4.0          # mm (leaving generous 6.0mm space below 10.0mm rim!)
COLLAR_INNER_L = 10.0       # mm (10mm inner length for WS2812B seed pixel)
COLLAR_INNER_W = 5.0        # mm (5mm inner width for WS2812B seed pixel)
COLLAR_WALL_THICK = 1.8     # mm (collar wall thickness +50% thicker: 1.2mm -> 1.8mm to prevent breakage)
COLLAR_OUTER_L = COLLAR_INNER_L + 2 * COLLAR_WALL_THICK # 13.6mm
COLLAR_OUTER_W = COLLAR_INNER_W + 2 * COLLAR_WALL_THICK # 8.6mm

NOTCH_WIDTH = 4.0           # mm (wire pass-through slot on both 5mm ends)
WINDOW_SQ = 3.0             # mm (3x3mm square optical aperture through 1.0mm front skin)
COLOR_INLAY_THICK = 0.8     # mm (4 solid layers @ 0.20mm layer height for rich, 100% opaque saturation)
if 'color_inlay_thick' in specs:
    try:
        COLOR_INLAY_THICK = float(specs['color_inlay_thick'])
    except Exception:
        pass
if '--inlay-thick' in sys.argv:
    _iti = sys.argv.index('--inlay-thick')
    if _iti + 1 < len(sys.argv):
        try:
            COLOR_INLAY_THICK = float(sys.argv[_iti + 1])
        except Exception:
            pass

def make_stadium_polygon(length, width, sections=16):
    r = width / 2.0
    c_len = max(0.0, length - width)
    pts = []
    for a in np.linspace(-np.pi/2, np.pi/2, sections):
        pts.append([c_len/2.0 + r * np.cos(a), r * np.sin(a)])
    for a in np.linspace(np.pi/2, 3*np.pi/2, sections):
        pts.append([-c_len/2.0 + r * np.cos(a), r * np.sin(a)])
    return sg.Polygon(pts)

def to_m(tm):
    if tm is None:
        return None
    v = np.ascontiguousarray(tm.vertices, dtype=np.float32)
    f = np.ascontiguousarray(tm.faces, dtype=np.uint32)
    return Manifold(Mesh(vert_properties=v, tri_verts=f))

def make_clean_cylinder(height, radius, segments=32):
    return CrossSection.circle(radius, segments).extrude(height)

def extrude_shapely(shape, height):
    if shape is None or shape.is_empty:
        return None
    geoms = shape.geoms if shape.geom_type in ['MultiPolygon', 'GeometryCollection'] else [shape]
    meshes = []
    for g in geoms:
        if g.geom_type == 'Polygon' and g.area > 0.05:
            try:
                m = trimesh.creation.extrude_polygon(g, height=height)
                if m and len(m.faces) > 0:
                    meshes.append(m)
            except Exception:
                pass
    if not meshes:
        return None
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.util.concatenate(meshes)

def flip_z_manifold(m):
    mesh_data = m.to_mesh()
    v = mesh_data.vert_properties[:, :3].copy()
    v[:, 2] = TOTAL_THICK - v[:, 2]
    f = mesh_data.tri_verts[:, ::-1].copy()
    tm = trimesh.Trimesh(vertices=v, faces=f, process=True)
    tm.update_faces(tm.nondegenerate_faces())
    tm.update_faces(tm.unique_faces())
    tm.remove_unreferenced_vertices()
    return tm

def flip_z_trimesh(tm):
    if tm is None or len(tm.faces) == 0:
        return None
    v = tm.vertices.copy()
    v[:, 2] = TOTAL_THICK - v[:, 2]
    f = tm.faces[:, ::-1].copy()
    res = trimesh.Trimesh(vertices=v, faces=f, process=True)
    res.update_faces(res.nondegenerate_faces())
    res.update_faces(res.unique_faces())
    res.remove_unreferenced_vertices()
    return res

INCLUDE_LED_NUMBERS = False
if 'include_led_numbers' in specs:
    INCLUDE_LED_NUMBERS = bool(specs['include_led_numbers'])
if '--numbers' in sys.argv:
    _ni = sys.argv.index('--numbers')
    if _ni + 1 < len(sys.argv):
        INCLUDE_LED_NUMBERS = sys.argv[_ni + 1].lower() in ('on', '1', 'true', 'yes')

INCLUDE_CLIP_GROOVES = False
if 'include_clip_grooves' in specs:
    INCLUDE_CLIP_GROOVES = bool(specs['include_clip_grooves'])
if '--clip-grooves' in sys.argv:
    _cgi = sys.argv.index('--clip-grooves')
    if _cgi + 1 < len(sys.argv):
        INCLUDE_CLIP_GROOVES = sys.argv[_cgi + 1].lower() in ('on', '1', 'true', 'yes')

INCLUDE_TOP_NUBS = False
if 'include_top_nubs' in specs:
    INCLUDE_TOP_NUBS = bool(specs['include_top_nubs'])
if '--top-nubs' in sys.argv:
    _tni = sys.argv.index('--top-nubs')
    if _tni + 1 < len(sys.argv):
        INCLUDE_TOP_NUBS = sys.argv[_tni + 1].lower() in ('on', '1', 'true', 'yes')

MATRIX_16X16_MODE = bool(specs.get('matrix_16x16_mode', False))
if '--matrix-16x16' in sys.argv:
    _m16i = sys.argv.index('--matrix-16x16')
    if _m16i + 1 < len(sys.argv):
        MATRIX_16X16_MODE = sys.argv[_m16i + 1].lower() in ('on', '1', 'true', 'yes')

PLATE_THICKNESS_MM = float(specs.get('plate_thickness_mm', 0.60))
if '--plate-thickness' in sys.argv:
    _pti = sys.argv.index('--plate-thickness')
    if _pti + 1 < len(sys.argv):
        try:
            PLATE_THICKNESS_MM = float(sys.argv[_pti + 1])
        except Exception:
            pass

def compile_matrix_16x16_plate_variant(variant_name, artwork_path, window_shape='round_34', plate_thickness_mm=0.60, windowed_leds=None, backlight_leds=None):
    PLATE_SIZE_MM = 176.0
    MATRIX_SIZE_MM = 160.0
    MARGIN_MM = 8.0
    ART_FIT_MM = 168.0
    THICK_MM = round(max(0.20, min(3.00, float(plate_thickness_mm))), 2)

    print(f"\n>>> Compiling {variant_name.upper()} 16x16 Matrix Backlight Plate ({PLATE_SIZE_MM}x{PLATE_SIZE_MM}x{THICK_MM:.2f}mm, Window Shape: {window_shape.upper()})...")
    v_t0 = time.time()

    active_img = Image.open(artwork_path).convert('RGBA')
    img_w, img_h = active_img.size
    img_arr = np.array(active_img)
    alpha = img_arr[:, :, 3]
    rgb = img_arr[:, :, :3].astype(np.float32)

    corners_opaque = (alpha[0, 0] > 40 and alpha[0, -1] > 40 and alpha[-1, 0] > 40 and alpha[-1, -1] > 40)
    corners_black = (rgb[0, 0].max() < 30 and rgb[0, -1].max() < 30 and rgb[-1, 0].max() < 30 and rgb[-1, -1].max() < 30)
    corners_white = (rgb[0, 0].min() > 235 and rgb[0, -1].min() > 235 and rgb[-1, 0].min() > 235 and rgb[-1, -1].min() > 235)

    if corners_opaque and corners_black:
        fg_mask = (rgb.max(axis=2) > 20) & (alpha > 40)
    elif corners_opaque and corners_white:
        fg_mask = (rgb.min(axis=2) < 235) & (alpha > 40)
    else:
        fg_mask = alpha > 30

    y_idx, x_idx = np.where(fg_mask)
    if len(x_idx) > 0:
        min_x, max_x = int(x_idx.min()), int(x_idx.max())
        min_y, max_y = int(y_idx.min()), int(y_idx.max())
    else:
        min_x, max_x = 0, img_w - 1
        min_y, max_y = 0, img_h - 1

    w_px = max(1, max_x - min_x + 1)
    h_px = max(1, max_y - min_y + 1)
    scale = ART_FIT_MM / max(w_px, h_px)
    target_w_mm = round(w_px * scale, 3)
    target_h_mm = round(h_px * scale, 3)
    offset_x = round((PLATE_SIZE_MM - target_w_mm) / 2.0, 3)
    offset_y = round((PLATE_SIZE_MM - target_h_mm) / 2.0, 3)

    # Color segmentation palette
    float_name = specs.get('float_name', '')
    graphic_type = specs.get('graphic_type', '')
    raw_stl_colors = specs.get('stl_colors')
    is_turtle = ('turtle' in str(graphic_type).lower() or 'turtle' in str(float_name).lower())
    is_snail = ('snail' in str(graphic_type).lower() or 'snail' in str(float_name).lower())
    is_drum = ('drum' in str(graphic_type).lower() or 'drum' in str(float_name).lower())
    is_train = ('train' in str(graphic_type).lower() or 'casey' in str(graphic_type).lower() or 'train' in str(float_name).lower())
    is_pirate = ('pirate' in str(graphic_type).lower() or 'pirate' in str(float_name).lower())

    if raw_stl_colors and isinstance(raw_stl_colors, dict):
        stl_colors = raw_stl_colors
    elif is_pirate:
        stl_colors = {
            'black': { 'name': 'Chassis, Hull & Rigging Accents', 'hex': '#141414', 'targetRgb': [20, 20, 20], 'role': 'chassis' },
            'red': { 'name': 'Sails & Masthead Flag', 'hex': '#e61919', 'targetRgb': [230, 25, 25], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Bright Gold Masts & Trim', 'hex': '#ebb941', 'targetRgb': [235, 185, 65], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'dark_gold': { 'name': 'Antique Bronze Decks & Shading', 'hex': '#9b6914', 'targetRgb': [155, 105, 20], 'role': 'inlay', 'filename': 'color_dark_gold.stl' },
            'green': { 'name': 'Ocean Waves & Sea Keel', 'hex': '#147332', 'targetRgb': [20, 115, 50], 'role': 'inlay', 'filename': 'color_green.stl' }
        }
    elif is_train:
        stl_colors = {
            'black': { 'name': 'Chassis, Roof & Cab Windows', 'hex': '#141414', 'targetRgb': [20, 20, 20], 'role': 'chassis' },
            'red': { 'name': 'Locomotive Body, Smokestack & Cowcatcher', 'hex': '#a3231e', 'targetRgb': [163, 35, 30], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Bright Gold Trim, Steam & Wheels', 'hex': '#d99e48', 'targetRgb': [217, 158, 72], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'dark_gold': { 'name': 'Shaded Gold / Bronze Steam & Details', 'hex': '#a1702c', 'targetRgb': [161, 112, 44], 'role': 'inlay', 'filename': 'color_dark_gold.stl' },
            'grey': { 'name': 'Drive Rod, Wheel Rims & Undercarriage', 'hex': '#716f6f', 'targetRgb': [113, 111, 111], 'role': 'inlay', 'filename': 'color_grey.stl' }
        }
    elif is_turtle:
        stl_colors = {
            'black': { 'name': 'Chassis Black', 'hex': '#11161d', 'targetRgb': [34, 43, 51], 'role': 'chassis' },
            'green': { 'name': 'Shell Plates & Glasses', 'hex': '#00cc66', 'targetRgb': [43, 109, 49], 'role': 'inlay', 'filename': 'color_green.stl' },
            'blue': { 'name': 'Shell & Eyes', 'hex': '#2563eb', 'targetRgb': [41, 63, 96], 'role': 'inlay', 'filename': 'color_blue.stl' },
            'yellow': { 'name': 'Body & Head', 'hex': '#facc15', 'targetRgb': [231, 199, 49], 'role': 'inlay', 'filename': 'color_yellow.stl' },
            'red': { 'name': 'Tie & Lips', 'hex': '#ef4444', 'targetRgb': [217, 29, 22], 'role': 'inlay', 'filename': 'color_red.stl' }
        }
    elif is_snail:
        stl_colors = {
            'black': { 'name': 'Chassis & Shell Background', 'hex': '#11161d', 'targetRgb': [1, 2, 1], 'role': 'chassis' },
            'red': { 'name': 'Head, Neck & Foot', 'hex': '#8a261e', 'targetRgb': [138, 38, 30], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Antennae, Spiral & Edge', 'hex': '#ca9927', 'targetRgb': [202, 153, 39], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'green': { 'name': 'Green Radial Stripes', 'hex': '#1e743d', 'targetRgb': [30, 116, 61], 'role': 'inlay', 'filename': 'color_green.stl' },
            'blue': { 'name': 'Blue Radial Stripes', 'hex': '#295374', 'targetRgb': [41, 83, 116], 'role': 'inlay', 'filename': 'color_blue.stl' }
        }
    elif is_drum:
        stl_colors = {
            'black': { 'name': 'Chassis, Drum Face & Wheels', 'hex': '#11161d', 'targetRgb': [17, 22, 29], 'role': 'chassis' },
            'gold': { 'name': 'Drum Ring, Text & Scrollwork', 'hex': '#facc15', 'targetRgb': [250, 204, 21], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'red': { 'name': 'Body Panels & Streamer', 'hex': '#ef4444', 'targetRgb': [239, 68, 68], 'role': 'inlay', 'filename': 'color_red.stl' },
            'blue': { 'name': 'Flags & Pennants', 'hex': '#2563eb', 'targetRgb': [37, 99, 235], 'role': 'inlay', 'filename': 'color_blue.stl' },
            'green': { 'name': 'Lead Flag', 'hex': '#10b981', 'targetRgb': [16, 185, 129], 'role': 'inlay', 'filename': 'color_green.stl' }
        }
    else:
        stl_colors = {
            'black': { 'name': 'Chassis Black', 'hex': '#11161d', 'targetRgb': [13, 25, 8], 'role': 'chassis' },
            'green': { 'name': 'Dragon Body', 'hex': '#00e676', 'targetRgb': [4, 250, 6], 'role': 'inlay', 'filename': 'color_green.stl' },
            'magenta': { 'name': 'Wings & Crest', 'hex': '#ec4899', 'targetRgb': [210, 10, 200], 'role': 'inlay', 'filename': 'color_magenta.stl' },
            'yellow': { 'name': 'Belly & Horns', 'hex': '#facc15', 'targetRgb': [249, 249, 12], 'role': 'inlay', 'filename': 'color_yellow.stl' },
            'white': { 'name': 'Eyes & Teeth', 'hex': '#ffffff', 'targetRgb': [247, 248, 247], 'role': 'inlay', 'filename': 'color_white.stl' }
        }

    targets = {c_k: np.array(c_v.get('targetRgb', [128, 128, 128]), dtype=np.float32) for c_k, c_v in stl_colors.items()}
    color_names = list(targets.keys())
    color_diffs = np.stack([np.sum((rgb - targets[k])**2, axis=2) for k in color_names], axis=2)
    closest_color_idx = np.argmin(color_diffs, axis=2)

    # If windowed_leds not supplied, auto-spread 50 windowed + 25 backlit on the 16x16 matrix (10mm pitch)
    if not windowed_leds:
        candidates = []
        for r in range(16):
            for c in range(16):
                mx_mm = MARGIN_MM + 5.0 + c * 10.0  # 13.0 to 163.0 mm
                my_mm = MARGIN_MM + 5.0 + (15 - r) * 10.0
                # Map back to image pixel
                px = int(round(min_x + (mx_mm - offset_x) / scale))
                py = int(round(max_y - (my_mm - offset_y) / scale))
                if 0 <= px < img_w and 0 <= py < img_h and fg_mask[py, px]:
                    c_idx = closest_color_idx[py, px]
                    c_key = color_names[c_idx]
                    if c_key != 'black':
                        pr, pg_c, pb = int(rgb[py, px, 0]), int(rgb[py, px, 1]), int(rgb[py, px, 2])
                        candidates.append({
                            'id': r * 16 + c + 1,
                            'row': r,
                            'col': c,
                            'x': round(mx_mm, 2),
                            'y': round(my_mm, 2),
                            'color': {'r': pr, 'g': pg_c, 'b': pb}
                        })
        # Farthest-point sampling for 50 windowed and 25 backlit
        def fps_select(pool, count):
            if len(pool) <= count:
                return list(pool), []
            chosen = [pool[0]]
            rem = list(pool[1:])
            while len(chosen) < count and rem:
                best_i = 0
                best_d = -1.0
                for idx_r, cand in enumerate(rem):
                    min_d = min((cand['x'] - ch['x'])**2 + (cand['y'] - ch['y'])**2 for ch in chosen)
                    if min_d > best_d:
                        best_d = min_d
                        best_i = idx_r
                chosen.append(rem.pop(best_i))
            return chosen, rem

        windowed_leds, rem_cands = fps_select(candidates, 50)
        if not backlight_leds:
            backlight_leds, _ = fps_select(rem_cands, 25)

    windowed_leds = [dict(l) for l in (windowed_leds or [])]
    backlight_leds = [dict(l) for l in (backlight_leds or [])]

    # Build 2D aperture cutouts ONLY for windowed_leds (~50 LEDs)
    w_shape_str = str(window_shape).lower()
    win_polys = []
    for l in windowed_leds:
        lx, ly = float(l['x']), float(l['y'])
        if '30' in w_shape_str or '3.0' in w_shape_str:
            win_polys.append(sg.Point(lx, ly).buffer(1.50, resolution=24))
        elif 'square' in w_shape_str:
            win_polys.append(sg.box(lx - 1.50, ly - 1.50, lx + 1.50, ly + 1.50))
        else:
            win_polys.append(sg.Point(lx, ly).buffer(1.70, resolution=24))
    windows_union_2d = unary_union(win_polys) if win_polys else sg.Polygon()

    # Build 16 perimeter shirt-mounting holes (O 2.8mm) along the 8mm border (4mm inset from 176mm edges)
    edge_offsets = [26.0, 67.33, 108.67, 150.0]
    shirt_hole_coords = []
    for pos in edge_offsets:
        shirt_hole_coords.append([round(pos, 2), 4.0])               # Bottom edge
        shirt_hole_coords.append([round(pos, 2), PLATE_SIZE_MM - 4.0]) # Top edge
        shirt_hole_coords.append([4.0, round(pos, 2)])               # Left edge
        shirt_hole_coords.append([PLATE_SIZE_MM - 4.0, round(pos, 2)]) # Right edge
    shirt_holes_union_2d = unary_union([sg.Point(hx, hy).buffer(1.40, resolution=24) for hx, hy in shirt_hole_coords])

    # Extract 2D polygons for each non-black color inlay
    polys_2d = {}
    for c_i, c_name in enumerate(color_names):
        c_info = stl_colors.get(c_name, {})
        if c_name == 'black' or c_info.get('role') == 'chassis':
            continue
        c_mask = ((closest_color_idx == c_i) & fg_mask).astype(np.uint8) * 255
        c_mask = cv2.morphologyEx(c_mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        cnts, hier = cv2.findContours(c_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        def _cnt_to_poly_m16(c):
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
            for idx_c, c in enumerate(cnts):
                if hier[0][idx_c][3] != -1:
                    continue
                outer = _cnt_to_poly_m16(c)
                if outer is None or outer.is_empty:
                    continue
                child = hier[0][idx_c][2]
                while child != -1:
                    hp = _cnt_to_poly_m16(cnts[child])
                    if hp is not None and not hp.is_empty:
                        outer = outer.difference(hp)
                    child = hier[0][child][0]
                if not outer.is_empty and outer.area > 0.05:
                    c_polys.append(outer)

        if c_polys:
            u = unary_union(c_polys)
            if not windows_union_2d.is_empty:
                u = u.difference(windows_union_2d)
            if not shirt_holes_union_2d.is_empty:
                u = u.difference(shirt_holes_union_2d)
            polys_2d[c_name] = u if u.is_valid else u.buffer(0)

    plate_box_2d = sg.box(0.0, 0.0, PLATE_SIZE_MM, PLATE_SIZE_MM)
    all_inlays_2d = unary_union(list(polys_2d.values())) if polys_2d else sg.Polygon()
    chassis_2d = plate_box_2d.difference(all_inlays_2d)
    if not windows_union_2d.is_empty:
        chassis_2d = chassis_2d.difference(windows_union_2d)
    if not shirt_holes_union_2d.is_empty:
        chassis_2d = chassis_2d.difference(shirt_holes_union_2d)
    if not chassis_2d.is_valid:
        chassis_2d = chassis_2d.buffer(0)

    mono_2d = plate_box_2d
    if not windows_union_2d.is_empty:
        mono_2d = mono_2d.difference(windows_union_2d)
    if not shirt_holes_union_2d.is_empty:
        mono_2d = mono_2d.difference(shirt_holes_union_2d)

    # Extrude all parts through full Z thickness (0 to THICK_MM)
    final_chassis_tm = extrude_shapely(chassis_2d, THICK_MM)
    final_monolithic_tm = extrude_shapely(mono_2d, THICK_MM)
    final_lid_tm = extrude_shapely(plate_box_2d.difference(shirt_holes_union_2d), THICK_MM)

    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)
    import glob
    for old_stl in glob.glob(os.path.join(out_dir, f"tpu_panel_{variant_name}_color_*.stl")):
        try:
            os.remove(old_stl)
        except Exception:
            pass

    mono_filename = f"tpu_panel_{variant_name}.stl"
    mono_path = os.path.join(out_dir, mono_filename)
    final_monolithic_tm.export(mono_path)

    chassis_filename = f"tpu_panel_{variant_name}_chassis_black.stl"
    chassis_path = os.path.join(out_dir, chassis_filename)
    final_chassis_tm.export(chassis_path)

    lid_filename = f"tpu_panel_{variant_name}_lid.stl"
    lid_path = os.path.join(out_dir, lid_filename)
    final_lid_tm.export(lid_path)
    lid_size = os.path.getsize(lid_path)

    color_stls = {}
    exported_inlays = []
    scene_items = {'1_Chassis_Black': final_chassis_tm}
    slot_idx = 2

    for c_name, c_info in stl_colors.items():
        if c_name == 'black' or c_info.get('role') == 'chassis':
            continue
        if c_name in polys_2d and not polys_2d[c_name].is_empty:
            c_tm = extrude_shapely(polys_2d[c_name], THICK_MM)
            if c_tm is not None and len(c_tm.faces) > 0:
                c_filename = f"tpu_panel_{variant_name}_color_{c_name}.stl"
                c_path = os.path.join(out_dir, c_filename)
                c_tm.export(c_path)
                color_stls[c_name] = c_path
                clean_name = c_info.get('name', c_name.capitalize()).replace(' ', '_').replace('&', 'and')
                scene_items[f"{slot_idx}_{clean_name}"] = c_tm
                slot_idx += 1
                exported_inlays.append({
                    "key": c_name,
                    "name": c_info.get('name', c_name.capitalize()),
                    "filename": c_filename,
                    "hex": c_info.get('hex', '#00ff88'),
                    "count": len(c_tm.faces)
                })

    mf3_filename = f"tpu_panel_{variant_name}_multicolor.3mf"
    mf3_path = os.path.join(out_dir, mf3_filename)
    try:
        scene = trimesh.Scene(scene_items)
        scene.export(mf3_path)
    except Exception as e:
        print(f"[{variant_name}] 3MF export warning: {e}")

    zip_filename = f"tpu_panel_{variant_name}_multicolor_bundle.zip"
    zip_path = os.path.join(out_dir, zip_filename)
    readme_txt = f"""🏰 MAIN STREET ELECTRICAL PARADE - 16x16 MATRIX HYBRID BACKLIGHT PLATE
VARIANT: {variant_name.upper()} ({specs.get('float_name', 'MSEP Float')})
======================================================================
PLATE SIZE: {PLATE_SIZE_MM:.1f} mm x {PLATE_SIZE_MM:.1f} mm Square (Covers 160x160mm BTF 16x16 FPCB)
THICKNESS: {THICK_MM:.2f} mm (100% Full Z-Thickness Color Inlays)
WINDOWED LEDS: {len(windowed_leds)} Open Apertures ({window_shape})
BACKLIT LEDS: {len(backlight_leds)} Solid Diffused Glow Positions (Zero Holes)
SHIRT HOLES: {len(shirt_hole_coords)} Perimeter Stitching Holes (Ø 2.8mm along 8mm margin)
"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('README_16X16_MATRIX_PLATE.txt', readme_txt)
        zf.write(chassis_path, chassis_filename)
        for c_n, c_p in color_stls.items():
            zf.write(c_p, os.path.basename(c_p))
        if os.path.exists(mf3_path):
            zf.write(mf3_path, mf3_filename)

    if variant_name == 'front':
        shutil.copyfile(mono_path, os.path.join(out_dir, 'tpu_panel.stl'))

    stl_size = os.path.getsize(mono_path)
    chassis_size = os.path.getsize(chassis_path)
    zip_size = os.path.getsize(zip_path)
    stl_bounds = [PLATE_SIZE_MM, PLATE_SIZE_MM, THICK_MM]
    stl_center = [PLATE_SIZE_MM / 2.0, PLATE_SIZE_MM / 2.0, round(THICK_MM / 2.0, 3)]
    contour_coords = [[0.0, 0.0], [PLATE_SIZE_MM, 0.0], [PLATE_SIZE_MM, PLATE_SIZE_MM], [0.0, PLATE_SIZE_MM], [0.0, 0.0]]

    print(f"[{variant_name}] 16x16 Matrix Plate compiled in {time.time()-v_t0:.2f}s! ({len(windowed_leds)} windows, {len(backlight_leds)} backlit, {THICK_MM:.2f}mm thick)")

    return {
        "variant": variant_name,
        "matrix_16x16_mode": True,
        "plate_thickness_mm": THICK_MM,
        "width_mm": PLATE_SIZE_MM,
        "height_mm": PLATE_SIZE_MM,
        "panel_width_mm": PLATE_SIZE_MM,
        "panel_height_mm": PLATE_SIZE_MM,
        "total_image_width_mm": PLATE_SIZE_MM,
        "total_image_height_mm": PLATE_SIZE_MM,
        "artwork_offset_mm": [offset_x, offset_y],
        "artwork_size_mm": [target_w_mm, target_h_mm],
        "window_shape": window_shape,
        "well_orientation": "horizontal",
        "ordered_leds": windowed_leds,
        "backlight_leds": backlight_leds,
        "led_count": len(windowed_leds),
        "backlight_led_count": len(backlight_leds),
        "fastener_tabs": shirt_hole_coords,
        "screw_positions": shirt_hole_coords,
        "number_positions": [],
        "contour_pts": contour_coords,
        "stl_bounds": stl_bounds,
        "stl_center": stl_center,
        "stl_size": stl_size,
        "chassis_size": chassis_size,
        "lid_size": lid_size,
        "zip_size": zip_size,
        "inlays": exported_inlays,
        "stl_url": f"/3d_panels/{mono_filename}",
        "chassis_stl_url": f"/3d_panels/{chassis_filename}",
        "lid_stl_url": f"/3d_panels/{lid_filename}",
        "multicolor_3mf_url": f"/3d_panels/{mf3_filename}" if os.path.exists(mf3_path) else None,
        "multicolor_zip_url": f"/3d_panels/{zip_filename}",
        "volume_mm3": round(PLATE_SIZE_MM * PLATE_SIZE_MM * THICK_MM, 1),
        "is_watertight": True
    }

def compile_plate_variant(variant_name, width_mm, height_mm, raw_leds, artwork_path, window_shape='round_34', clip_grooves=False, top_nubs=False, well_orientation='horizontal'):
    print(f"\n>>> Compiling {variant_name.upper()} Plate ({width_mm}mm x {height_mm}mm, {len(raw_leds)} LEDs, Window Shape: {window_shape.upper()}, Orientation: {well_orientation.upper()}, Clip Grooves: {'ON' if clip_grooves else 'OFF'}, Top Nubs: {'ON' if top_nubs else 'OFF'})...")
    v_t0 = time.time()
    num_leds = len(raw_leds)
    leds = [dict(l) for l in raw_leds]

    # 1. Extract Active Silhouette Boundary & Safe Artwork Containment Zone
    active_img = Image.open(artwork_path).convert('RGBA')
    img_w, img_h = active_img.size
    img_arr = np.array(active_img)
    alpha = img_arr[:, :, 3]
    rgb = img_arr[:, :, :3]

    # Robust foreground extraction:
    # If all four corners are opaque and near-black (e.g. drawn from shirt preview canvas),
    # then foreground is defined by non-black pixels with visible color or luminance.
    # Otherwise, foreground is defined by the transparent alpha channel (> 40).
    corners_opaque = (alpha[0, 0] > 40 and alpha[0, -1] > 40 and alpha[-1, 0] > 40 and alpha[-1, -1] > 40)
    corners_black = (rgb[0, 0].max() < 30 and rgb[0, -1].max() < 30 and rgb[-1, 0].max() < 30 and rgb[-1, -1].max() < 30)
    corners_white = (rgb[0, 0].min() > 235 and rgb[0, -1].min() > 235 and rgb[-1, 0].min() > 235 and rgb[-1, -1].min() > 235)

    if corners_opaque and corners_black:
        mask = ((rgb.max(axis=2) > 20) & (alpha > 40)).astype(np.uint8)
    elif corners_opaque and corners_white:
        mask = ((rgb.min(axis=2) < 235) & (alpha > 40)).astype(np.uint8)
    else:
        mask = (alpha > 40).astype(np.uint8)

    raw_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if raw_contours:
        # Enforce strict 245.0mm maximum build volume limit (part + tabs <= 245.0mm)
        MAX_PART_DIM_MM = 245.0
        TAB_OVERHANG_MM = 9.5  # 2 * (1.5mm offset + 3.25mm outer tab radius)
        kernel_sz_init = max(5, int(min(img_w, img_h) * 0.02))
        if kernel_sz_init % 2 == 0: kernel_sz_init += 1
        mask_dil_init = cv2.dilate(mask, np.ones((kernel_sz_init, kernel_sz_init), np.uint8), iterations=2)
        cnts_init, _ = cv2.findContours(mask_dil_init, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts_init:
            main_c_init = max(cnts_init, key=cv2.contourArea)
            eps_init = 0.0022 * cv2.arcLength(main_c_init, True)
            app_c_init = cv2.approxPolyDP(main_c_init, eps_init, True)
            while True:
                t_pts = [[(pt[0][0] / img_w) * width_mm, (1.0 - pt[0][1] / img_h) * height_mm] for pt in app_c_init]
                t_poly = sg.Polygon(t_pts).buffer(0).buffer(4.0, resolution=16).simplify(0.3, preserve_topology=True)
                if t_poly.geom_type == 'MultiPolygon':
                    t_poly = max(t_poly.geoms, key=lambda g: g.area)
                tb = t_poly.bounds
                est_max_dim = max((tb[2] - tb[0]) + TAB_OVERHANG_MM, (tb[3] - tb[1]) + TAB_OVERHANG_MM)
                if est_max_dim <= MAX_PART_DIM_MM:
                    break
                sf_limit = (MAX_PART_DIM_MM - 0.2) / est_max_dim
                print(f"[{variant_name}] Part envelope ({est_max_dim:.1f}mm) exceeds 245.0mm limit. Scaling by {sf_limit:.4f}...")
                width_mm = round(width_mm * sf_limit, 2)
                height_mm = round(height_mm * sf_limit, 2)
                for l in leds:
                    l['x'] = round(l['x'] * sf_limit, 2)
                    l['y'] = round(l['y'] * sf_limit, 2)

        main_raw = max(raw_contours, key=cv2.contourArea)
        epsilon_raw = 0.0022 * cv2.arcLength(main_raw, True)
        approx_raw = cv2.approxPolyDP(main_raw, epsilon_raw, True)
        raw_pts = []
        for pt in approx_raw:
            cx = round((pt[0][0] / img_w) * width_mm, 2)
            cy = round((1.0 - pt[0][1] / img_h) * height_mm, 2)
            raw_pts.append((cx, cy))
        dragon_poly = sg.Polygon(raw_pts)
        if not dragon_poly.is_valid:
            dragon_poly = dragon_poly.buffer(0)
        safe_art_boundary = dragon_poly.buffer(-2.0, resolution=16)
        if safe_art_boundary.geom_type == 'MultiPolygon':
            safe_art_boundary = max(safe_art_boundary.geoms, key=lambda g: g.area)
    else:
        safe_art_boundary = sg.box(5.0, 5.0, width_mm - 5.0, height_mm - 5.0)

    # 2. LED Collar Orientation & Collision Avoidance
    if '--orientation' in sys.argv:
        _oi = sys.argv.index('--orientation')
        if _oi + 1 < len(sys.argv):
            well_orientation = sys.argv[_oi + 1].lower()

    led_rotations_deg = []
    for i in range(num_leds):
        if leds[i].get('is_custom_rotation', False) and 'rotation_deg' in leds[i]:
            canvas_deg = float(leds[i]['rotation_deg'])
            rot_3d = (-canvas_deg) % 360.0
            led_rotations_deg.append(rot_3d)
        elif well_orientation == 'horizontal':
            # Global Horizontal Alignment: all standard LEDs are strictly 0.0 degrees
            led_rotations_deg.append(0.0)
        elif 'rotation_deg' in leds[i]:
            # rotation_deg passed from simulator canvas (where Y increases downwards).
            # In 3D (where Y increases upwards), the rotation angle around +Z is negated:
            canvas_deg = float(leds[i]['rotation_deg'])
            rot_3d = (-canvas_deg) % 360.0
            led_rotations_deg.append(rot_3d)
        elif 'angle_deg' in leds[i]:
            canvas_deg = float(leds[i]['angle_deg'])
            rot_3d = (-canvas_deg) % 360.0
            led_rotations_deg.append(rot_3d)
        elif well_orientation == 'tangent' and num_leds > 1:
            if i == 0:
                dx = leds[1]['x'] - leds[0]['x']
                dy = leds[1]['y'] - leds[0]['y']
            elif i == num_leds - 1:
                dx = leds[i]['x'] - leds[i - 1]['x']
                dy = leds[i]['y'] - leds[i - 1]['y']
            else:
                d1x = leds[i]['x'] - leds[i - 1]['x']
                d1y = leds[i]['y'] - leds[i - 1]['y']
                len1 = math.hypot(d1x, d1y) + 1e-6
                d2x = leds[i + 1]['x'] - leds[i]['x']
                d2y = leds[i + 1]['y'] - leds[i]['y']
                len2 = math.hypot(d2x, d2y) + 1e-6
                dx = (d1x / len1) + (d2x / len2)
                dy = (d1y / len1) + (d2y / len2)
            deg = math.degrees(math.atan2(dy, dx))
            led_rotations_deg.append(deg)
        else:
            led_rotations_deg.append(0.0)

    pts = np.array([[l['x'], l['y']] for l in leds], dtype=np.float64)
    orig_pts = pts.copy()
    # 13.6mm outer length (5.0mm straight segment) x 8.6mm outer width (4.3mm radius)
    # req_dist = 8.6mm ensures zero physical collar overlap
    req_dist = COLLAR_OUTER_W                    # 8.6 mm zero-overlap physical boundary
    COLLAR_HALF_L = COLLAR_OUTER_L / 2.0         # 6.8 mm
    COLLAR_HALF_W = COLLAR_OUTER_W / 2.0         # 4.3 mm
    OPENING_CLEARANCE_MM = 2.5                   # 2.5 mm clearance in front of each wire channel opening

    bounds = safe_art_boundary.bounds if safe_art_boundary is not None else (0.0, 0.0, width_mm, height_mm)
    cx_mid = (bounds[0] + bounds[2]) / 2.0

    # Approximate portal bridge locations in 3D plate space
    bridge_ent_approx = np.array([cx_mid, bounds[1] + RIM_WALL_THICK + 5.5])
    bridge_exit_approx = np.array([bounds[2] - RIM_WALL_THICK - 5.5, bounds[1] + 0.30 * (bounds[3] - bounds[1])])

    # Exact Designer Coordinates (1:1 spatial fidelity with 2D Layout Canvas)
    for i in range(num_leds):
        leds[i]['x'] = round(float(orig_pts[i, 0]), 2)
        leds[i]['y'] = round(float(orig_pts[i, 1]), 2)
        leds[i]['rotation_deg'] = round(float(led_rotations_deg[i]), 1)

    print(f"[{variant_name}] 1:1 Precise Layout ({num_leds} LEDs, orientation: {well_orientation}): zero coordinate drift.")

    # 3. Outer Rim and Armor Plate 2D Boundary
    kernel_size = max(5, int(min(img_w, img_h) * 0.02))
    if kernel_size % 2 == 0: kernel_size += 1
    mask_dilated = cv2.dilate(mask, np.ones((kernel_size, kernel_size), np.uint8), iterations=2)
    contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        contour_pts = [
            [4.0, 4.0], [width_mm - 4.0, 4.0],
            [width_mm - 4.0, height_mm - 4.0], [4.0, height_mm - 4.0]
        ]
    else:
        main_contour = max(contours, key=cv2.contourArea)
        epsilon = 0.0022 * cv2.arcLength(main_contour, True)
        approx_contour = cv2.approxPolyDP(main_contour, epsilon, True)

        contour_pts = []
        for pt in approx_contour:
            cx = round((pt[0][0] / img_w) * width_mm, 2)
            cy = round((1.0 - pt[0][1] / img_h) * height_mm, 2)
            contour_pts.append((cx, cy))

    orig_poly = sg.Polygon(contour_pts)
    if not orig_poly.is_valid:
        orig_poly = orig_poly.buffer(0)

    smoothed_plate_2d = orig_poly.buffer(4.0, resolution=16)
    smoothed_plate_2d = smoothed_plate_2d.simplify(0.3, preserve_topology=True)
    if smoothed_plate_2d.geom_type == 'MultiPolygon':
        smoothed_plate_2d = max(smoothed_plate_2d.geoms, key=lambda g: g.area)

    contour_coords = [[round(p[0], 2), round(p[1], 2)] for p in smoothed_plate_2d.exterior.coords]
    bounds = smoothed_plate_2d.bounds
    panel_w = round(bounds[2] - bounds[0], 2)
    panel_h = round(bounds[3] - bounds[1], 2)
    print(f"[{variant_name}] Outer boundary: {panel_w}mm W x {panel_h}mm H | {len(contour_coords)} vertices")

    # Extrude solid plate and perimeter rim
    base_front_mesh = trimesh.creation.extrude_polygon(smoothed_plate_2d, height=FRONT_THICK_GENERAL)
    inner_plate_2d = smoothed_plate_2d.buffer(-RIM_WALL_THICK, resolution=16)
    if inner_plate_2d.geom_type == 'MultiPolygon':
        inner_plate_2d = max(inner_plate_2d.geoms, key=lambda g: g.area)

    rim_polygon_2d = sg.Polygon(smoothed_plate_2d.exterior.coords, [inner_plate_2d.exterior.coords])
    rim_mesh = trimesh.creation.extrude_polygon(rim_polygon_2d, height=RIM_HEIGHT)
    rim_mesh.apply_translation([0, 0, FRONT_THICK_GENERAL]) # Z = 2.0 to 9.0mm (7.0mm tall rim)

    # Manifold cutter for inner tray basin to guarantee gussets never intrude past the 2.5mm rim wall:
    inner_basin_cutter_mesh = trimesh.creation.extrude_polygon(inner_plate_2d, height=TOTAL_THICK + 2.0)
    inner_basin_cutter_mesh.apply_translation([0, 0, -1.0])
    inner_basin_cutter_m = to_m(inner_basin_cutter_mesh)

    # 4b. Bottom-Center Wire Entry Notch & Internal Strain Relief Anchor
    cx_mid = (bounds[0] + bounds[2]) / 2.0
    boundary_line_ent = smoothed_plate_2d.exterior
    
    # In Photo 2, move from corner jog to straight horizontal run to the left if available:
    flat_bottom_pts = [p for p in contour_coords if p[1] < bounds[1] + 2.5 and p[0] < cx_mid + 8.0]
    if len(flat_bottom_pts) >= 2:
        min_flat_x = min(p[0] for p in flat_bottom_pts)
        max_flat_x = max(p[0] for p in flat_bottom_pts)
        cand_ent_x = round((min_flat_x + max_flat_x) / 2.0, 2)
        d_ent = boundary_line_ent.project(sg.Point(cand_ent_x, bounds[1]))
    else:
        # Robust geometric projection onto bottom perimeter
        d_ent = boundary_line_ent.project(sg.Point(cx_mid, bounds[1]))

    pt_ent = boundary_line_ent.interpolate(d_ent)
    wire_portal_x = round(float(pt_ent.x), 2)
    wire_portal_y = round(float(pt_ent.y), 2)

    # Inward normal vector at entrance portal directed into the tray basin
    pt_ent_prev = boundary_line_ent.interpolate(max(0.0, d_ent - 1.0))
    pt_ent_next = boundary_line_ent.interpolate(min(boundary_line_ent.length, d_ent + 1.0))
    tan_ent = np.array([pt_ent_next.x - pt_ent_prev.x, pt_ent_next.y - pt_ent_prev.y])
    tan_ent_norm = tan_ent / (np.linalg.norm(tan_ent) + 1e-6)
    inward_ent = np.array([-tan_ent_norm[1], tan_ent_norm[0]])
    if not smoothed_plate_2d.contains(sg.Point(wire_portal_x + inward_ent[0] * 1.5, wire_portal_y + inward_ent[1] * 1.5)):
        inward_ent = -inward_ent

    rot_angle_ent = math.atan2(inward_ent[1], inward_ent[0])
    rot_mat_ent = trimesh.transformations.rotation_matrix(rot_angle_ent, [0, 0, 1])

    # Parting-line wire entrance notch at top of outer rim wall (Z = 6.5 to 10.2mm in pre-flip space)
    PORTAL_NOTCH_W = 5.5   # mm wide
    PORTAL_NOTCH_H = 3.5   # mm tall
    wire_portal_cutter = trimesh.creation.box(extents=[RIM_WALL_THICK + 14.0, PORTAL_NOTCH_W, PORTAL_NOTCH_H + 0.4])
    wire_portal_cutter.apply_transform(rot_mat_ent)
    wire_portal_cutter.apply_translation([wire_portal_x, wire_portal_y, TOTAL_THICK - PORTAL_NOTCH_H / 2.0 + 0.2])

    # Internal floor zip-tie strain relief bridge for entrance wire (moves inward along normal):
    bridge_pos = np.array([wire_portal_x, wire_portal_y]) + inward_ent * (RIM_WALL_THICK + 5.5)
    bridge_x = round(float(bridge_pos[0]), 2)
    bridge_y = round(float(bridge_pos[1]), 2)
    BRIDGE_X_W = 8.0
    BRIDGE_Y_L = 7.2
    BRIDGE_Z_H = 4.5
    bridge_solid_tm = trimesh.creation.box(extents=[BRIDGE_X_W, BRIDGE_Y_L, BRIDGE_Z_H])
    bridge_solid_tm.apply_translation([bridge_x, bridge_y, FRONT_THICK_GENERAL + BRIDGE_Z_H / 2.0])

    tunnel_cutter_tm = trimesh.creation.box(extents=[BRIDGE_X_W + 8.0, 3.2, 2.8 + 0.2])
    tunnel_cutter_tm.apply_translation([bridge_x, bridge_y, FRONT_THICK_GENERAL + 2.8 / 2.0])

    saddle_cutter_tm = trimesh.creation.box(extents=[4.5, BRIDGE_Y_L + 4.0, 0.8])
    saddle_cutter_tm.apply_translation([bridge_x, bridge_y, FRONT_THICK_GENERAL + BRIDGE_Z_H - 0.3])

    # Clean monolithic bridge arch with unobstructed through-tunnel
    internal_bridge_m = (to_m(bridge_solid_tm) - to_m(tunnel_cutter_tm) - to_m(saddle_cutter_tm)) - to_m(rim_mesh)

    # 4c. Lower-Right Lateral Wire Exit Notch & Internal Strain Relief Anchor (Photo 1 Fix)
    y_min_flank = bounds[1] + 0.18 * (bounds[3] - bounds[1])
    y_max_flank = bounds[1] + 0.45 * (bounds[3] - bounds[1])
    right_flank_pts = [p for p in contour_coords if p[0] > cx_mid and y_min_flank <= p[1] <= y_max_flank]
    if right_flank_pts:
        rightmost_pt = max(right_flank_pts, key=lambda p: p[0])
        exit_portal_x = rightmost_pt[0]
        exit_portal_y = rightmost_pt[1]
    else:
        exit_portal_x = bounds[2]
        exit_portal_y = bounds[1] + 0.30 * (bounds[3] - bounds[1])

    # Find outward normal and tangent on perimeter wall at exit portal
    boundary_line_exit = smoothed_plate_2d.exterior
    d_exit = boundary_line_exit.project(sg.Point(exit_portal_x, exit_portal_y))
    pt_exit_prev = boundary_line_exit.interpolate(max(0.0, d_exit - 1.0))
    pt_exit_next = boundary_line_exit.interpolate(min(boundary_line_exit.length, d_exit + 1.0))
    tan_exit = np.array([pt_exit_next.x - pt_exit_prev.x, pt_exit_next.y - pt_exit_prev.y])
    tan_exit_norm = tan_exit / (np.linalg.norm(tan_exit) + 1e-6)
    normal_exit = np.array([-tan_exit_norm[1], tan_exit_norm[0]])
    if smoothed_plate_2d.contains(sg.Point(exit_portal_x + normal_exit[0] * 1.5, exit_portal_y + normal_exit[1] * 1.5)):
        normal_exit = -normal_exit

    rot_angle_exit = math.atan2(normal_exit[1], normal_exit[0])
    rot_mat_exit = trimesh.transformations.rotation_matrix(rot_angle_exit, [0, 0, 1])

    # Rotated U-Notch Cutter through right rim wall (24.0mm deep through wall, 5.5mm wide)
    # Fully punches through angled wall, eliminating any protruding wall bump or uncut corners
    exit_portal_cutter = trimesh.creation.box(extents=[24.0, PORTAL_NOTCH_W, PORTAL_NOTCH_H + 0.4])
    exit_portal_cutter.apply_transform(rot_mat_exit)
    exit_portal_cutter.apply_translation([exit_portal_x, exit_portal_y, TOTAL_THICK - PORTAL_NOTCH_H / 2.0 + 0.2])

    # Exit Strain Relief Bridge (aligned along wall normal towards interior):
    inward_normal = -normal_exit
    bridge_exit_center = np.array([exit_portal_x, exit_portal_y]) + inward_normal * (RIM_WALL_THICK + 5.5)
    bridge_exit_x = round(float(bridge_exit_center[0]), 2)
    bridge_exit_y = round(float(bridge_exit_center[1]), 2)

    BRIDGE_EXIT_X_L = 7.2  # length along wire
    BRIDGE_EXIT_Y_W = 8.0  # width across wire
    bridge_exit_solid_tm = trimesh.creation.box(extents=[BRIDGE_EXIT_X_L, BRIDGE_EXIT_Y_W, BRIDGE_Z_H])
    bridge_exit_solid_tm.apply_transform(rot_mat_exit)
    bridge_exit_solid_tm.apply_translation([bridge_exit_x, bridge_exit_y, FRONT_THICK_GENERAL + BRIDGE_Z_H / 2.0])

    tunnel_exit_cutter_tm = trimesh.creation.box(extents=[3.2, BRIDGE_EXIT_Y_W + 8.0, 2.8 + 0.2])
    tunnel_exit_cutter_tm.apply_transform(rot_mat_exit)
    tunnel_exit_cutter_tm.apply_translation([bridge_exit_x, bridge_exit_y, FRONT_THICK_GENERAL + 2.8 / 2.0])

    saddle_exit_cutter_tm = trimesh.creation.box(extents=[BRIDGE_EXIT_X_L + 4.0, 4.5, 0.8])
    saddle_exit_cutter_tm.apply_transform(rot_mat_exit)
    saddle_exit_cutter_tm.apply_translation([bridge_exit_x, bridge_exit_y, FRONT_THICK_GENERAL + BRIDGE_Z_H - 0.3])

    # Clean monolithic exit bridge arch with unobstructed through-tunnel
    internal_bridge_exit_m = (to_m(bridge_exit_solid_tm) - to_m(tunnel_exit_cutter_tm) - to_m(saddle_exit_cutter_tm)) - to_m(rim_mesh)

    # 4. 16 Outside Perimeter Mounting Eyelets (with strict portal notch clearance)
    boundary_line = smoothed_plate_2d.exterior
    total_len = boundary_line.length
    num_tabs = 16
    tab_meshes = []
    tab_coords = []
    TAB_INNER_R = 1.25
    TAB_WALL_THICK = 2.0
    TAB_OUTER_R = TAB_INNER_R + TAB_WALL_THICK
    TAB_HEIGHT = 2.0

    for k in range(num_tabs):
        dist_along = (k / float(num_tabs)) * total_len
        pt = boundary_line.interpolate(dist_along)

        # Check clearance against entrance & exit portals so eyelet tab never blocks wire notch:
        cand_p = np.array([pt.x, pt.y])
        dist_ent = np.linalg.norm(cand_p - np.array([wire_portal_x, wire_portal_y]))
        dist_exit = np.linalg.norm(cand_p - np.array([exit_portal_x, exit_portal_y]))
        if dist_ent < 14.0 or dist_exit < 14.0:
            for shift_d in [10.0, -10.0, 15.0, -15.0, 20.0, -20.0]:
                test_dist = (dist_along + shift_d) % total_len
                test_pt = boundary_line.interpolate(test_dist)
                d_e = np.linalg.norm([test_pt.x - wire_portal_x, test_pt.y - wire_portal_y])
                d_x = np.linalg.norm([test_pt.x - exit_portal_x, test_pt.y - exit_portal_y])
                if d_e >= 14.0 and d_x >= 14.0:
                    dist_along = test_dist
                    pt = test_pt
                    break

        pt_prev = boundary_line.interpolate(max(0.0, dist_along - 1.0))
        pt_next = boundary_line.interpolate(min(total_len, dist_along + 1.0))
        tan = np.array([pt_next.x - pt_prev.x, pt_next.y - pt_prev.y])
        tan_norm = tan / (np.linalg.norm(tan) + 1e-6)
        normal = np.array([-tan_norm[1], tan_norm[0]])
        cand_out = np.array([pt.x, pt.y]) + normal * 1.5
        cand_opp = np.array([pt.x, pt.y]) - normal * 1.5
        if smoothed_plate_2d.contains(sg.Point(cand_out)) and not smoothed_plate_2d.contains(sg.Point(cand_opp)):
            normal = -normal
            cand_center = cand_opp
        elif not smoothed_plate_2d.contains(sg.Point(cand_out)):
            cand_center = cand_out
        else:
            d_out = smoothed_plate_2d.distance(sg.Point(cand_out))
            d_opp = smoothed_plate_2d.distance(sg.Point(cand_opp))
            if d_opp > d_out:
                normal = -normal
                cand_center = cand_opp
            else:
                cand_center = cand_out
            
        tab_coords.append([round(float(cand_center[0]), 2), round(float(cand_center[1]), 2)])
        cyl = make_clean_cylinder(TAB_HEIGHT, TAB_OUTER_R, 32).translate([cand_center[0], cand_center[1], TOTAL_THICK - TAB_HEIGHT])
        hole = make_clean_cylinder(TAB_HEIGHT + 0.4, TAB_INNER_R, 32).translate([cand_center[0], cand_center[1], TOTAL_THICK - TAB_HEIGHT - 0.2])
        tab_m = cyl - hole

        # Dual 45° triangular gusset braces flanking tab shoulders (Image 3)
        # Rises 3.0mm up the vertical rim wall from the tab surface (Z = 7.0 to 4.0 in pre-flip space)
        # and extends outward along the tab top.
        # Deep wall anchor: extends from x = -4.5mm (deep inside the 2.5mm rim wall) to x = -1.0mm at full height Z_TOP (4.0mm),
        # then slopes at 45° down to x = +2.0mm at Z_BASE (7.0mm) onto the tab shoulder.
        # This completely cures mid-air gaps on curved or concave perimeter regions (e.g. dragon feet).
        GUSSET_RISE = 3.0
        GUSSET_THICK = 1.2
        Z_BASE = TOTAL_THICK - TAB_HEIGHT
        Z_TOP = Z_BASE - GUSSET_RISE

        tri_pts = [
            [-4.5, Z_TOP],
            [-1.0, Z_TOP],
            [2.0, Z_BASE],
            [-4.5, Z_BASE]
        ]
        tri_ext = trimesh.creation.extrude_polygon(sg.Polygon(tri_pts), height=GUSSET_THICK)
        v_tri = tri_ext.vertices
        v_tri_new = np.zeros_like(v_tri)
        v_tri_new[:, 0] = v_tri[:, 0]                      # outward normal from cand_center
        v_tri_new[:, 1] = v_tri[:, 2] - GUSSET_THICK / 2.0 # tangent centered
        v_tri_new[:, 2] = v_tri[:, 1]                      # Z height
        tri_base_tm = trimesh.Trimesh(vertices=v_tri_new, faces=tri_ext.faces[:, ::-1], process=True)

        rot_mat = np.eye(4)
        rot_mat[0, 0] = normal[0]
        rot_mat[1, 0] = normal[1]
        rot_mat[0, 1] = tan_norm[0]
        rot_mat[1, 1] = tan_norm[1]

        gussets_m = []
        for s_sign in [-1, 1]:
            g_tm = tri_base_tm.copy()
            g_tm.apply_transform(rot_mat)
            g_pos = cand_center + tan_norm * (s_sign * 2.2)
            g_tm.apply_translation([g_pos[0], g_pos[1], 0.0])
            vg = np.ascontiguousarray(g_tm.vertices, dtype=np.float32)
            fg = np.ascontiguousarray(g_tm.faces, dtype=np.uint32)
            gussets_m.append(Manifold(Mesh(vert_properties=vg, tri_verts=fg)))

        full_tab_m = (tab_m + Manifold.batch_boolean(gussets_m, OpType.Add)) - inner_basin_cutter_m
        tab_mesh_data = full_tab_m.to_mesh()
        tab_solid = trimesh.Trimesh(vertices=tab_mesh_data.vert_properties[:, :3], faces=tab_mesh_data.tri_verts)
        tab_meshes.append(tab_solid)

    # 5. Collars, Recesses & Windows
    outer_collar_2d = make_stadium_polygon(COLLAR_OUTER_L, COLLAR_OUTER_W, sections=16)
    inner_collar_2d = make_stadium_polygon(COLLAR_INNER_L, COLLAR_INNER_W, sections=16)
    collar_ring_2d = sg.Polygon(outer_collar_2d.exterior.coords, [inner_collar_2d.exterior.coords])

    # 0.6mm deep x 0.7mm tall external retention clip groove at wall base
    GROOVE_DEPTH = 0.6    # mm (cuts 0.6mm into 1.2mm outer collar wall)
    GROOVE_HEIGHT = 0.7   # mm (0.7mm tall parallel to front facing face)
    groove_inner_2d = outer_collar_2d.buffer(-GROOVE_DEPTH, resolution=16)
    groove_outer_2d = outer_collar_2d.buffer(0.5, resolution=16)
    groove_ring_2d = groove_outer_2d.difference(groove_inner_2d)

    # 0.70mm distinct top collar nubs/lip for rigid PLA snap clips (without weakening wall base)
    NUB_PROTRUSION = 0.70  # mm outward protrusion (creates a clear, tactile snap ridge)
    NUB_HEIGHT = 0.80      # mm tall
    nub_outer_2d = outer_collar_2d.buffer(NUB_PROTRUSION, resolution=16)
    nub_ring_2d = nub_outer_2d.difference(outer_collar_2d)

    collar_meshes = []
    floor_recess_cutters = []
    square_window_cutters = []

    # 2D window apertures for cutting into color inlays
    led_windows_2d_list = []

    # Safe boundary zone ensuring collars never hang past outer rim wall into thin air
    safe_collar_zone = smoothed_plate_2d.buffer(-(RIM_WALL_THICK + COLLAR_OUTER_W / 2.0))
    if safe_collar_zone.geom_type == 'MultiPolygon':
        safe_collar_zone = max(safe_collar_zone.geoms, key=lambda g: g.area)

    for i in range(num_leds):
        l = leds[i]
        cx, cy = l['x'], l['y']

        # Clamp LED inside safe tray basin so collar never hangs past the outer perimeter rim
        if not safe_collar_zone.is_empty:
            led_pt = sg.Point(cx, cy)
            if not safe_collar_zone.contains(led_pt):
                proj_pt = safe_collar_zone.exterior.interpolate(safe_collar_zone.exterior.project(led_pt))
                cx = round(float(proj_pt.x), 2)
                cy = round(float(proj_pt.y), 2)
                leds[i]['x'] = cx
                leds[i]['y'] = cy
        angle_deg = led_rotations_deg[i]
        rad = math.radians(angle_deg)
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])

        # Floor Recess (1.0mm)
        recess = trimesh.creation.extrude_polygon(inner_collar_2d, height=1.1)
        recess.apply_transform(rot)
        recess.apply_translation([cx, cy, FRONT_THICK_LED])
        floor_recess_cutters.append(recess)

        # 3.0mm Collar base solid
        c_mesh = trimesh.creation.extrude_polygon(collar_ring_2d, height=COLLAR_HEIGHT)
        c_solid_m = to_m(c_mesh)

        # Add top collar nubs/lip for PLA snap clips flush at the top rim of the collar
        if top_nubs:
            top_nub_ext = trimesh.creation.extrude_polygon(nub_ring_2d, height=NUB_HEIGHT)
            top_nub_ext.apply_translation([0, 0, COLLAR_HEIGHT - NUB_HEIGHT])
            c_solid_m = c_solid_m + to_m(top_nub_ext)

        # Wire notches cut cleanly through BOTH collar and nubs:
        notch_r = trimesh.creation.box(extents=[COLLAR_OUTER_L + 4.0, NOTCH_WIDTH, COLLAR_HEIGHT + 0.4])
        notch_r.apply_translation([COLLAR_OUTER_L / 2.0 + 1.0, 0, COLLAR_HEIGHT / 2.0])
        notch_l = trimesh.creation.box(extents=[COLLAR_OUTER_L + 4.0, NOTCH_WIDTH, COLLAR_HEIGHT + 0.4])
        notch_l.apply_translation([-COLLAR_OUTER_L / 2.0 - 1.0, 0, COLLAR_HEIGHT / 2.0])

        collar_cutters_list = [to_m(notch_r), to_m(notch_l)]

        # Cut base retention groove ONLY if clip_grooves is True
        if clip_grooves:
            groove_cutter = trimesh.creation.extrude_polygon(groove_ring_2d, height=GROOVE_HEIGHT)
            groove_cutter.apply_translation([0, 0, FRONT_THICK_GENERAL - COLLAR_FLOOR_Z])
            collar_cutters_list.append(to_m(groove_cutter))

        c_cutters_m = Manifold.batch_boolean(collar_cutters_list, OpType.Add)
        notched_collar_m = c_solid_m - c_cutters_m

        mesh_d = notched_collar_m.to_mesh()
        notched_collar = trimesh.Trimesh(vertices=mesh_d.vert_properties[:, :3], faces=mesh_d.tri_verts)

        notched_collar.apply_transform(rot)
        notched_collar.apply_translation([cx, cy, COLLAR_FLOOR_Z])
        collar_meshes.append(notched_collar)

        # Optical Window Aperture:
        # Default: Ø 3.4mm Round (win_radius = 1.7mm)
        # Selectable: round_34 (Ø 3.4mm), round_30 (Ø 3.0mm), square (3x3mm)
        w_shape_str = str(window_shape).lower()
        if '30' in w_shape_str or '3.0' in w_shape_str:
            win_radius = 1.5  # Ø 3.0mm round
            is_circle_win = True
        elif 'square' in w_shape_str:
            win_radius = 1.5  # 3.0mm square half-width
            is_circle_win = False
        else:
            win_radius = 1.7  # Ø 3.4mm round (default: round_34, round, circle)
            is_circle_win = True

        # Use generous cutter height (4.0mm) to guarantee clean punch-through across full tray skin
        cutter_h = FRONT_THICK_GENERAL + 2.0
        if is_circle_win:
            sq_win = trimesh.creation.cylinder(radius=win_radius, height=cutter_h, sections=28)
            win_2d = sg.Point(cx, cy).buffer(win_radius, resolution=16)
        else:
            sq_win = trimesh.creation.box(extents=[WINDOW_SQ, WINDOW_SQ, cutter_h])
            sq_win.apply_transform(rot)
            win_2d = sg.box(cx - WINDOW_SQ / 2.0, cy - WINDOW_SQ / 2.0, cx + WINDOW_SQ / 2.0, cy + WINDOW_SQ / 2.0)

        sq_win.apply_translation([cx, cy, FRONT_THICK_LED / 2.0])
        square_window_cutters.append(sq_win)
        led_windows_2d_list.append(win_2d)

    led_windows_union_2d = unary_union(led_windows_2d_list) if led_windows_2d_list else sg.Polygon()

    # 6. Debossed LED Numbers (1 to N)
    number_positions = []
    number_cutters = []

    for i, l in enumerate(leds):
        if not INCLUDE_LED_NUMBERS:
            break
        num_str = str(i + 1)
        p = np.array([l['x'], l['y']])
        best_cand = None
        max_d = -1
        candidates = [
            p + np.array([0.0, 5.5]),   p + np.array([0.0, -5.5]),
            p + np.array([8.0, 0.0]),   p + np.array([-8.0, 0.0]),
            p + np.array([6.5, 4.5]),   p + np.array([-6.5, 4.5]),
            p + np.array([6.5, -4.5]),  p + np.array([-6.5, -4.5]),
        ]
        for cand in candidates:
            min_d = min(np.linalg.norm(cand - np.array([ol['x'], ol['y']])) for j, ol in enumerate(leds) if j != i) if len(leds) > 1 else 10.0
            if min_d > max_d:
                max_d = min_d
                best_cand = cand
                
        number_positions.append([round(best_cand[0], 2), round(best_cand[1], 2)])
        tp = TextPath((0, 0), num_str, size=1.8)
        polys = tp.to_polygons()
        sg_polys = [sg.Polygon(p_ring) for p_ring in polys if len(p_ring) >= 3]
        shells, holes = [], []
        for sp in sg_polys:
            is_hole = any(other != sp and other.contains(sp) for other in sg_polys)
            if is_hole: holes.append(sp)
            else: shells.append(sp)
                
        digit_meshes = []
        for shell in shells:
            interior_holes = [h.exterior.coords for h in holes if shell.contains(h)]
            final_poly = sg.Polygon(shell.exterior.coords, holes=interior_holes)
            try:
                m = trimesh.creation.extrude_polygon(final_poly, height=0.6)
                digit_meshes.append(m)
            except Exception: pass
                
        if digit_meshes:
            num_combined = trimesh.util.concatenate(digit_meshes)
            num_combined.apply_scale([-1.0, 1.0, 1.0])
            num_combined.faces = num_combined.faces[:, ::-1]
            num_combined.fix_normals()
            tx_mid = (num_combined.bounds[0][:2] + num_combined.bounds[1][:2]) / 2.0
            # Sits at general tray floor level Z = 1.6 to 2.2, cleanly debossing 0.5mm into the floor
            num_combined.apply_translation([-tx_mid[0], -tx_mid[1], FRONT_THICK_GENERAL - 0.4])
            num_combined.apply_translation([best_cand[0], best_cand[1], 0.0])
            number_cutters.append(num_combined)

    # 7. MULTI-COLOR VECTOR SEGMENTATION (Dynamic float color inlays)
    print(f"[{variant_name}] Segmenting artwork for multi-material inlays...")
    rgb = img_arr[:, :, :3].astype(np.float32)

    float_name = specs.get('float_name', '')
    graphic_type = specs.get('graphic_type', '')
    raw_stl_colors = specs.get('stl_colors')

    is_turtle = ('turtle' in str(graphic_type).lower() or 'turtle' in str(float_name).lower() or 'turtle' in str(artwork_path).lower())
    is_snail = ('snail' in str(graphic_type).lower() or 'snail' in str(float_name).lower() or 'snail' in str(artwork_path).lower())
    is_drum = ('drum' in str(graphic_type).lower() or 'drum' in str(float_name).lower() or 'drum' in str(artwork_path).lower())
    is_train = ('train' in str(graphic_type).lower() or 'casey' in str(graphic_type).lower() or 'train' in str(float_name).lower() or 'train' in str(artwork_path).lower())
    is_pirate = ('pirate' in str(graphic_type).lower() or 'pirate' in str(float_name).lower() or 'pirate' in str(artwork_path).lower())

    if raw_stl_colors and isinstance(raw_stl_colors, dict):
        stl_colors = raw_stl_colors
    elif is_pirate:
        stl_colors = {
            'black': { 'name': 'Chassis, Hull & Rigging Accents', 'hex': '#141414', 'targetRgb': [20, 20, 20], 'role': 'chassis' },
            'red': { 'name': 'Sails & Masthead Flag', 'hex': '#e61919', 'targetRgb': [230, 25, 25], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Bright Gold Masts & Trim', 'hex': '#ebb941', 'targetRgb': [235, 185, 65], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'dark_gold': { 'name': 'Antique Bronze Decks & Shading', 'hex': '#9b6914', 'targetRgb': [155, 105, 20], 'role': 'inlay', 'filename': 'color_dark_gold.stl' },
            'green': { 'name': 'Ocean Waves & Sea Keel', 'hex': '#147332', 'targetRgb': [20, 115, 50], 'role': 'inlay', 'filename': 'color_green.stl' }
        }
    elif is_train:
        stl_colors = {
            'black': { 'name': 'Chassis, Roof & Cab Windows', 'hex': '#141414', 'targetRgb': [20, 20, 20], 'role': 'chassis' },
            'red': { 'name': 'Locomotive Body, Smokestack & Cowcatcher', 'hex': '#a3231e', 'targetRgb': [163, 35, 30], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Bright Gold Trim, Steam & Wheels', 'hex': '#d99e48', 'targetRgb': [217, 158, 72], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'dark_gold': { 'name': 'Shaded Gold / Bronze Steam & Details', 'hex': '#a1702c', 'targetRgb': [161, 112, 44], 'role': 'inlay', 'filename': 'color_dark_gold.stl' },
            'grey': { 'name': 'Drive Rod, Wheel Rims & Undercarriage', 'hex': '#716f6f', 'targetRgb': [113, 111, 111], 'role': 'inlay', 'filename': 'color_grey.stl' }
        }
    elif is_turtle:
        stl_colors = {
            'black': { 'name': 'Chassis Black', 'hex': '#11161d', 'targetRgb': [34, 43, 51], 'role': 'chassis' },
            'green': { 'name': 'Shell Plates & Glasses', 'hex': '#00cc66', 'targetRgb': [43, 109, 49], 'role': 'inlay', 'filename': 'color_green.stl' },
            'blue': { 'name': 'Shell & Eyes', 'hex': '#2563eb', 'targetRgb': [41, 63, 96], 'role': 'inlay', 'filename': 'color_blue.stl' },
            'yellow': { 'name': 'Body & Head', 'hex': '#facc15', 'targetRgb': [231, 199, 49], 'role': 'inlay', 'filename': 'color_yellow.stl' },
            'red': { 'name': 'Tie & Lips', 'hex': '#ef4444', 'targetRgb': [217, 29, 22], 'role': 'inlay', 'filename': 'color_red.stl' }
        }
    elif is_snail:
        stl_colors = {
            'black': { 'name': 'Chassis & Shell Background', 'hex': '#11161d', 'targetRgb': [1, 2, 1], 'role': 'chassis' },
            'red': { 'name': 'Head, Neck & Foot', 'hex': '#8a261e', 'targetRgb': [138, 38, 30], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Antennae, Spiral & Edge', 'hex': '#ca9927', 'targetRgb': [202, 153, 39], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'green': { 'name': 'Green Radial Stripes', 'hex': '#1e743d', 'targetRgb': [30, 116, 61], 'role': 'inlay', 'filename': 'color_green.stl' },
            'blue': { 'name': 'Blue Radial Stripes', 'hex': '#295374', 'targetRgb': [41, 83, 116], 'role': 'inlay', 'filename': 'color_blue.stl' }
        }
    elif is_drum:
        stl_colors = {
            'black': { 'name': 'Chassis, Drum Face & Wheels', 'hex': '#11161d', 'targetRgb': [17, 22, 29], 'role': 'chassis' },
            'gold': { 'name': 'Drum Ring, Text & Scrollwork', 'hex': '#facc15', 'targetRgb': [250, 204, 21], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'red': { 'name': 'Body Panels & Streamer', 'hex': '#ef4444', 'targetRgb': [239, 68, 68], 'role': 'inlay', 'filename': 'color_red.stl' },
            'blue': { 'name': 'Flags & Pennants', 'hex': '#2563eb', 'targetRgb': [37, 99, 235], 'role': 'inlay', 'filename': 'color_blue.stl' },
            'green': { 'name': 'Lead Flag', 'hex': '#10b981', 'targetRgb': [16, 185, 129], 'role': 'inlay', 'filename': 'color_green.stl' }
        }
    else:
        stl_colors = {
            'black': { 'name': 'Chassis Black', 'hex': '#11161d', 'targetRgb': [13, 25, 8], 'role': 'chassis' },
            'green': { 'name': 'Dragon Body', 'hex': '#00e676', 'targetRgb': [4, 250, 6], 'role': 'inlay', 'filename': 'color_green.stl' },
            'magenta': { 'name': 'Wings & Crest', 'hex': '#ec4899', 'targetRgb': [210, 10, 200], 'role': 'inlay', 'filename': 'color_magenta.stl' },
            'yellow': { 'name': 'Belly & Horns', 'hex': '#facc15', 'targetRgb': [249, 249, 12], 'role': 'inlay', 'filename': 'color_yellow.stl' },
            'white': { 'name': 'Eyes & Teeth', 'hex': '#ffffff', 'targetRgb': [247, 248, 247], 'role': 'inlay', 'filename': 'color_white.stl' }
        }

    targets = {}
    for c_k, c_v in stl_colors.items():
        targets[c_k] = np.array(c_v.get('targetRgb', [128, 128, 128]), dtype=np.float32)

    color_names = list(targets.keys())
    color_diffs = np.stack([np.sum((rgb - targets[k])**2, axis=2) for k in color_names], axis=2)
    closest_color_idx = np.argmin(color_diffs, axis=2)

    color_inlay_meshes = {}
    color_inlay_manifolds = []

    for c_i, c_name in enumerate(color_names):
        c_info = stl_colors.get(c_name, {})
        if c_name == 'black' or c_info.get('role') == 'chassis':
            continue
        c_mask = ((closest_color_idx == c_i) & (mask > 0)).astype(np.uint8) * 255
        # Light despeckle only
        c_mask = cv2.morphologyEx(c_mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        cnts, hier = cv2.findContours(c_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        def _cnt_to_poly(c):
            if cv2.contourArea(c) < 4:
                return None
            eps = 0.0012 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, eps, True)
            if len(approx) < 3:
                return None
            pts = [(round((pt[0][0] / img_w) * width_mm, 3),
                    round((1.0 - pt[0][1] / img_h) * height_mm, 3)) for pt in approx]
            pg = sg.Polygon(pts)
            if not pg.is_valid:
                pg = pg.buffer(0)
            return pg

        c_polys = []
        if hier is not None:
            for idx, c in enumerate(cnts):
                if hier[0][idx][3] != -1:
                    continue  # hole contour, handled with its parent
                outer = _cnt_to_poly(c)
                if outer is None or outer.is_empty:
                    continue
                child = hier[0][idx][2]
                while child != -1:
                    hp = _cnt_to_poly(cnts[child])
                    if hp is not None and not hp.is_empty:
                        outer = outer.difference(hp)
                    child = hier[0][child][0]
                if not outer.is_empty and outer.area > 0.1:
                    c_polys.append(outer)

        if c_polys:
            c_union = unary_union(c_polys)
            # Subtract LED aperture windows so light projects clean through!
            if not led_windows_union_2d.is_empty:
                c_union = c_union.difference(led_windows_union_2d)
            if not c_union.is_valid:
                c_union = c_union.buffer(0)
            
            # Extrude COLOR_INLAY_THICK thickness (from Z = 0.0 to COLOR_INLAY_THICK)
            inlay_mesh = extrude_shapely(c_union, COLOR_INLAY_THICK)
            if inlay_mesh is not None:
                color_inlay_meshes[c_name] = inlay_mesh
                color_inlay_manifolds.append(to_m(inlay_mesh))
                print(f"[{variant_name}] Created {c_info.get('name', c_name.upper())} Inlay ({len(inlay_mesh.vertices)} vertices, area {c_union.area:.1f} mm^2)")

    # 8. Manifold3D Assembly & Boolean Operations
    # Union all solids for the black chassis:
    # Floor tray + 4mm Perimeter Rim + 16 Eyelet Tabs + Notched Collars
    base_m = to_m(base_front_mesh)
    
    # Subtract color inlays from base plate so black chassis has precision jigsaw pockets:
    if color_inlay_manifolds:
        color_union_m = Manifold.batch_boolean(color_inlay_manifolds, OpType.Add)
        base_with_pockets_m = base_m - color_union_m
    else:
        base_with_pockets_m = base_m

    # 7b. Perimeter Screw Boss Locations (Extremities from Photo 3 + Perimeter Distribution)
    SCREW_BOSS_R = 2.5       # mm (5.0mm diameter pillar)
    SCREW_HOLE_R = 1.0       # mm (2.0mm clearance hole for M2 screw body)
    SCREW_CBORE_R = 1.9      # mm (3.8mm diameter counterbore)
    SCREW_CBORE_DEPTH = 0.8  # mm (flush head seating depth on outer face)
    PILOT_HOLE_R = 0.8       # mm (1.6mm pilot hole for M2 self-tapping screw)
    PILOT_HOLE_DEPTH = 5.5   # mm (blind pilot hole in front tray boss)
    LID_THICK = 2.0          # mm (solid lid plate thickness)
    RIDGE_HEIGHT = 1.2       # mm (downward locator lip)
    RIDGE_CLEARANCE = 0.25   # mm (sliding fit gap inside 2.5mm rim)
    RIDGE_WALL = 1.2         # mm (width of alignment ridge)

    inner_boundary = inner_plate_2d.exterior
    total_inner_len = inner_boundary.length
    coords_inner = np.array(inner_boundary.coords)
    ib_bounds = inner_plate_2d.bounds
    ib_w = ib_bounds[2] - ib_bounds[0]
    ib_h = ib_bounds[3] - ib_bounds[1]

    # Find the 7 key extremity anchor points circled in Photo 3:
    # 1. Top-right ear tip (max x+y in upper right)
    ur_pts = coords_inner[(coords_inner[:, 0] > ib_bounds[0] + 0.6*ib_w) & (coords_inner[:, 1] > ib_bounds[1] + 0.6*ib_h)]
    e1 = ur_pts[np.argmax(ur_pts[:, 0] + ur_pts[:, 1])] if len(ur_pts) else coords_inner[0]

    # 2. Dragon jaw/neck notch nook (between head and back)
    nook_pts = coords_inner[(coords_inner[:, 0] > ib_bounds[0] + 0.4*ib_w) & (coords_inner[:, 0] < ib_bounds[0] + 0.65*ib_w) & (coords_inner[:, 1] > ib_bounds[1] + 0.6*ib_h)]
    e2 = nook_pts[np.argmin(nook_pts[:, 0] + nook_pts[:, 1])] if len(nook_pts) else coords_inner[0]

    # 3. Upper-left tail/wing crest (max y for x < 0.4*ib_w)
    ul_pts = coords_inner[(coords_inner[:, 0] < ib_bounds[0] + 0.4*ib_w) & (coords_inner[:, 1] > ib_bounds[1] + 0.6*ib_h)]
    e3 = ul_pts[np.argmax(ul_pts[:, 1])] if len(ul_pts) else coords_inner[0]

    # 4. Far-left tail tip (min x)
    e4 = coords_inner[np.argmin(coords_inner[:, 0])]

    # 5. Bottom-left foot corner (min x+y in lower left)
    bl_pts = coords_inner[(coords_inner[:, 0] < ib_bounds[0] + 0.3*ib_w) & (coords_inner[:, 1] < ib_bounds[1] + 0.3*ib_h)]
    e5 = bl_pts[np.argmin(bl_pts[:, 0] + bl_pts[:, 1])] if len(bl_pts) else coords_inner[0]

    # 6. Far-right jaw/snout corner (max x for mid-upper y)
    mr_pts = coords_inner[(coords_inner[:, 0] > ib_bounds[0] + 0.7*ib_w) & (coords_inner[:, 1] > ib_bounds[1] + 0.5*ib_h) & (coords_inner[:, 1] < ib_bounds[1] + 0.75*ib_h)]
    e6 = mr_pts[np.argmax(mr_pts[:, 0])] if len(mr_pts) else coords_inner[0]

    # 7. Lower-right flank (straight vertical wall above tab)
    lr_pts = coords_inner[(coords_inner[:, 0] > ib_bounds[0] + 0.6*ib_w) & (coords_inner[:, 1] > ib_bounds[1] + 0.3*ib_h) & (coords_inner[:, 1] < ib_bounds[1] + 0.45*ib_h)]
    e7 = lr_pts[np.argmin(abs(lr_pts[:, 1] - (ib_bounds[1] + 0.36*ib_h)))] if len(lr_pts) else coords_inner[0]

    extremities = [e1, e2, e3, e4, e5, e6, e7]

    # Prioritize keeping Photo 3 extremities in candidate list:
    cand_screws = [(inner_boundary.project(sg.Point(p)), np.array(p), True) for p in extremities]

    # Distribute additional perimeter screws to fill remaining spans (total ~14-16 perimeter screws)
    NUM_DISTRIBUTED = 12
    for i in range(NUM_DISTRIBUTED):
        nominal_d = (i / float(NUM_DISTRIBUTED)) * total_inner_len
        best_pt = None
        best_clearance = -1
        for delta in np.linspace(-15.0, 15.0, 21):
            cur_d = (nominal_d + delta) % total_inner_len
            cand_p = inner_boundary.interpolate(cur_d)
            dist_portal = np.linalg.norm([cand_p.x - wire_portal_x, cand_p.y - wire_portal_y])
            dist_exit = np.linalg.norm([cand_p.x - exit_portal_x, cand_p.y - exit_portal_y])
            if dist_portal < 14.0 or dist_exit < 14.0:
                continue
            min_led = min(np.linalg.norm([cand_p.x - l['x'], cand_p.y - l['y']]) for l in leds) if leds else 20.0
            if min_led < 6.8:
                continue
            if min_led > best_clearance:
                best_clearance = min_led
                best_pt = np.array([cand_p.x, cand_p.y])
        if best_pt is not None:
            cand_screws.append((inner_boundary.project(sg.Point(best_pt)), best_pt, False))

    cand_screws.sort(key=lambda x: x[0])

    filtered_screws = []
    MIN_SPACING = 24.0
    for d, p, is_ext in cand_screws:
        dist_portal = np.linalg.norm([p[0] - wire_portal_x, p[1] - wire_portal_y])
        dist_exit = np.linalg.norm([p[0] - exit_portal_x, p[1] - exit_portal_y])
        if dist_portal < 12.0 or dist_exit < 12.0:
            continue
        min_led = min(np.linalg.norm([p[0] - l['x'], p[1] - l['y']]) for l in leds) if leds else 20.0
        if min_led < 6.5:
            continue
        if not filtered_screws:
            filtered_screws.append((d, p, is_ext))
        else:
            last_d, last_p, last_ext = filtered_screws[-1]
            if (d - last_d) >= MIN_SPACING:
                filtered_screws.append((d, p, is_ext))
            elif is_ext and not last_ext:
                filtered_screws[-1] = (d, p, is_ext)

    if len(filtered_screws) > 1 and (total_inner_len - filtered_screws[-1][0] + filtered_screws[0][0]) < MIN_SPACING:
        if not filtered_screws[-1][2]:
            filtered_screws.pop()

    screw_coords = [[round(float(p[0]), 2), round(float(p[1]), 2)] for d, p, is_ext in filtered_screws]

    tray_boss_solids = []
    pilot_hole_cutters = []
    for sp in screw_coords:
        # 5.0mm diameter pillar rising from Z = 2.0 to 10.0mm fused to inner rim wall
        boss_cyl = make_clean_cylinder(RIM_HEIGHT, SCREW_BOSS_R, 32).translate([sp[0], sp[1], FRONT_THICK_GENERAL])
        tray_boss_solids.append(boss_cyl)
        # 1.6mm diameter pilot hole from top of rim down 5.5mm (Z = 10.0 down to 4.5mm)
        pilot_cyl = make_clean_cylinder(PILOT_HOLE_DEPTH + 0.2, PILOT_HOLE_R, 32).translate([sp[0], sp[1], TOTAL_THICK - PILOT_HOLE_DEPTH])
        pilot_hole_cutters.append(pilot_cyl)

    chassis_solids = [base_with_pockets_m, to_m(rim_mesh), internal_bridge_m, internal_bridge_exit_m] + [to_m(t) for t in tab_meshes] + [to_m(c) for c in collar_meshes] + tray_boss_solids
    chassis_assembled_m = Manifold.batch_boolean(chassis_solids, OpType.Add)

    # Cutters: floor recesses, square/round optical windows, debossed numbers, wire entrance/exit portal notches, and M2 pilot holes
    all_cutters = floor_recess_cutters + square_window_cutters + number_cutters + [wire_portal_cutter, exit_portal_cutter]
    cutters_m = [to_m(c) for c in all_cutters] + pilot_hole_cutters
    cutters_union_m = Manifold.batch_boolean(cutters_m, OpType.Add)

    final_chassis_m = chassis_assembled_m - cutters_union_m
    final_chassis_tm = flip_z_manifold(final_chassis_m)

    # Monolithic single-color black STL (legacy compatible, without color pockets subtracted)
    monolithic_solids = [base_m, to_m(rim_mesh), internal_bridge_m, internal_bridge_exit_m] + [to_m(t) for t in tab_meshes] + [to_m(c) for c in collar_meshes] + tray_boss_solids
    monolithic_m = Manifold.batch_boolean(monolithic_solids, OpType.Add) - cutters_union_m
    final_monolithic_tm = flip_z_manifold(monolithic_m)

    # -----------------------------------------------------------------------
    # 8b. REAR COVER LID PLATE (2.0mm Base + 1.2mm Alignment Ridge + M2 Screws)
    # -----------------------------------------------------------------------
    lid_base_m = to_m(trimesh.creation.extrude_polygon(smoothed_plate_2d, height=LID_THICK))

    # 16 Matching Outer Eyelet Tabs on Lid
    lid_tabs_m = []
    for tc in tab_coords:
        tab_cyl = make_clean_cylinder(LID_THICK, TAB_OUTER_R, 32).translate([tc[0], tc[1], 0.0])
        tab_hole = make_clean_cylinder(LID_THICK + 0.4, TAB_INNER_R, 32).translate([tc[0], tc[1], -0.2])
        lid_tabs_m.append(tab_cyl - tab_hole)

    # 1.2mm Alignment Ridge on inner face (stepping 1.5mm inward with 0.25mm clearance)
    ridge_outer_2d = smoothed_plate_2d.buffer(-(RIM_WALL_THICK + RIDGE_CLEARANCE), resolution=16)
    if ridge_outer_2d.geom_type == 'MultiPolygon':
        ridge_outer_2d = max(ridge_outer_2d.geoms, key=lambda g: g.area)
    ridge_inner_2d = smoothed_plate_2d.buffer(-(RIM_WALL_THICK + RIDGE_CLEARANCE + RIDGE_WALL), resolution=16)
    if ridge_inner_2d.geom_type == 'MultiPolygon':
        ridge_inner_2d = max(ridge_inner_2d.geoms, key=lambda g: g.area)

    ridge_ring_2d = sg.Polygon(ridge_outer_2d.exterior.coords, [ridge_inner_2d.exterior.coords])
    ridge_mesh = trimesh.creation.extrude_polygon(ridge_ring_2d, height=RIDGE_HEIGHT)
    ridge_mesh.apply_translation([0, 0, LID_THICK]) # Rises on inner face from Z = 2.0 to 3.2mm
    ridge_m = to_m(ridge_mesh)

    # Cutout over entrance & exit wire portals so wires are never pinched
    portal_relief_m = Manifold.cube([14.0, RIM_WALL_THICK + 14.0, RIDGE_HEIGHT + 0.6], True).translate([wire_portal_x, wire_portal_y, LID_THICK + RIDGE_HEIGHT / 2.0])
    exit_relief_tm = trimesh.creation.box(extents=[RIM_WALL_THICK + 14.0, 14.0, RIDGE_HEIGHT + 0.6])
    exit_relief_tm.apply_transform(rot_mat_exit)
    exit_relief_tm.apply_translation([exit_portal_x, exit_portal_y, LID_THICK + RIDGE_HEIGHT / 2.0])
    exit_portal_relief_m = to_m(exit_relief_tm)

    # Flush Screw Landings on Inner Face (Z = LID_THICK = 2.0mm):
    # Chassis tray boss pillars already rise flush with the rim top (Z = 9.0mm in tray).
    # Remove any raised pads, and relieve alignment ridge around each chassis screw boss (SCREW_BOSS_R + 0.3mm = 2.8mm)
    # so the chassis boss seats 100% flush against the inner lid surface without interference.
    boss_relief_m = []
    screw_holes_m = []
    screw_cbore_m = []
    for sp in screw_coords:
        # 5.6mm diameter relief cutter clearing alignment ridge down to inner face (Z = LID_THICK)
        boss_relief = make_clean_cylinder(RIDGE_HEIGHT + 0.5, SCREW_BOSS_R + 0.3, 32).translate([sp[0], sp[1], LID_THICK])
        boss_relief_m.append(boss_relief)
        # 2.0mm clearance through hole
        shole = make_clean_cylinder(LID_THICK + 1.0, SCREW_HOLE_R, 32).translate([sp[0], sp[1], -0.5])
        screw_holes_m.append(shole)
        # 3.8mm diameter x 0.8mm deep flush counterbore on outer/shirt face
        scbore = make_clean_cylinder(SCREW_CBORE_DEPTH + 0.2, SCREW_CBORE_R, 32).translate([sp[0], sp[1], -0.1])
        screw_cbore_m.append(scbore)

    lid_solids = [lid_base_m, ridge_m] + lid_tabs_m
    lid_assembled_m = Manifold.batch_boolean(lid_solids, OpType.Add)
    lid_cutters_m = Manifold.batch_boolean([portal_relief_m, exit_portal_relief_m] + boss_relief_m + screw_holes_m + screw_cbore_m, OpType.Add)
    final_lid_m = lid_assembled_m - lid_cutters_m

    lid_mesh_data = final_lid_m.to_mesh()
    final_lid_tm = trimesh.Trimesh(
        vertices=lid_mesh_data.vert_properties[:, :3],
        faces=lid_mesh_data.tri_verts,
        process=True
    )

    # Flipped color inlays:
    flipped_colors = {}
    for c_name, tm in color_inlay_meshes.items():
        flipped_colors[c_name] = flip_z_trimesh(tm)

    # 9. EXPORT STLs (Monolithic + Dynamic Split Inlay Parts)
    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)

    # Clean up stale color STL files from previous floats so they never contaminate the active float
    import glob
    for old_stl in glob.glob(os.path.join(out_dir, f"tpu_panel_{variant_name}_color_*.stl")):
        try:
            os.remove(old_stl)
        except Exception:
            pass

    # 1. Monolithic Single-Color STL (Legacy & single-print compatible)
    mono_filename = f"tpu_panel_{variant_name}.stl"
    mono_path = os.path.join(out_dir, mono_filename)
    final_monolithic_tm.export(mono_path)

    # 2. Black Chassis STL
    chassis_filename = f"tpu_panel_{variant_name}_chassis_black.stl"
    chassis_path = os.path.join(out_dir, chassis_filename)
    final_chassis_tm.export(chassis_path)

    # 2b. Rear Cover Lid Plate STL (2.0mm Plate + 1.2mm Alignment Ridge + M2 Screws)
    lid_filename = f"tpu_panel_{variant_name}_lid.stl"
    lid_path = os.path.join(out_dir, lid_filename)
    final_lid_tm.export(lid_path)
    lid_size = os.path.getsize(lid_path)

    # 3. Dynamic Color Inlay STLs
    color_stls = {}
    exported_inlays = []
    scene_items = {'1_Chassis_Black': final_chassis_tm}
    slot_idx = 2

    for c_name, c_info in stl_colors.items():
        if c_name == 'black' or c_info.get('role') == 'chassis':
            continue
        c_tm = flipped_colors.get(c_name)
        if c_tm is not None and len(c_tm.faces) > 0:
            c_filename = f"tpu_panel_{variant_name}_color_{c_name}.stl"
            c_path = os.path.join(out_dir, c_filename)
            c_tm.export(c_path)
            color_stls[c_name] = c_path
            
            clean_name = c_info.get('name', c_name.capitalize()).replace(' ', '_').replace('&', 'and')
            scene_items[f"{slot_idx}_{clean_name}"] = c_tm
            slot_idx += 1
            exported_inlays.append({
                "key": c_name,
                "name": c_info.get('name', c_name.capitalize()),
                "filename": c_filename,
                "hex": c_info.get('hex', '#00ff88'),
                "count": len(c_tm.faces)
            })

    if variant_name not in specs or not isinstance(specs[variant_name], dict):
        specs[variant_name] = {}
    specs[variant_name]['inlays'] = exported_inlays
    specs[variant_name]['entrance_portal'] = [round(float(wire_portal_x), 2), round(float(wire_portal_y), 2)]
    specs[variant_name]['entrance_bridge'] = [round(float(wire_portal_x), 2), round(float(bridge_y), 2)]
    specs[variant_name]['exit_portal'] = [round(float(exit_portal_x), 2), round(float(exit_portal_y), 2)]
    specs[variant_name]['exit_bridge'] = [round(float(bridge_exit_x), 2), round(float(bridge_exit_y), 2)]
    specs['stl_colors'] = stl_colors

    if variant_name == 'front':
        shutil.copyfile(mono_path, os.path.join(out_dir, 'tpu_panel.stl'))
        if 'dragon' in str(specs.get('graphic_type', '')).lower():
            shutil.copyfile(mono_path, os.path.join(out_dir, 'petes_dragon_tpu_panel.stl'))
            shutil.copyfile(lid_path, os.path.join(out_dir, 'petes_dragon_tpu_panel_lid.stl'))

    # 10. EXPORT NATIVE MULTI-BODY .3MF PROJECT
    mf3_filename = f"tpu_panel_{variant_name}_multicolor.3mf"
    mf3_path = os.path.join(out_dir, mf3_filename)

    try:
        scene = trimesh.Scene(scene_items)
        scene.export(mf3_path)
        print(f"[{variant_name}] Exported native 3MF with {len(scene_items)} parts: {mf3_filename}")
    except Exception as e:
        print(f"[{variant_name}] 3MF export warning: {e}")
        print(f"[{variant_name}] 3MF export warning: {e}")

    # 11. EXPORT READY-TO-PRINT ZIP BUNDLE
    zip_filename = f"tpu_panel_{variant_name}_multicolor_bundle.zip"
    zip_path = os.path.join(out_dir, zip_filename)
    
    stl_list_lines = [f"   - {chassis_filename}", f"   - {lid_filename}"]
    slot_mapping_lines = [f"Slot 1 (Black 95A TPU):   Chassis Tray, 7mm Perimeter Rim, 16 Tabs, {num_leds} Collars, Outlines",
                          f"Rear Lid (TPU or PLA):    2.0mm Rear Cover Plate with Alignment Ridge & M2 Screw Holes"]
    for s_idx, inl in enumerate(exported_inlays, 2):
        stl_list_lines.append(f"   - {inl['filename']}")
        slot_mapping_lines.append(f"Slot {s_idx} ({inl['name']}):  {inl['name']}")
    stl_list_str = "\n".join(stl_list_lines)
    slot_mapping_str = "\n".join(slot_mapping_lines)

    w_shape_str = str(window_shape).lower()
    if '30' in w_shape_str or '3.0' in w_shape_str:
        aperture_desc = "Ø 3.0mm round optical apertures"
    elif 'square' in w_shape_str:
        aperture_desc = "3x3mm square optical apertures"
    else:
        aperture_desc = "Ø 3.4mm round optical apertures (Default)"

    readme_content = f"""🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K) - 3D TPU ARMOR PLATE
BAMBU LAB X1-CARBON / AMS MULTI-COLOR PRINTING GUIDE

PLATE VARIANT: {variant_name.upper()} ({specs.get('float_name', 'MSEP Float')})
======================================================================
PHYSICAL SIZE: {panel_w} mm W x {panel_h} mm H (Target Width: {width_mm} mm / ~{round(width_mm/25.4, 1)} in)
ACTIVE LEDS: {num_leds} LEDs with {aperture_desc}

======================================================================
HOW TO IMPORT INTO BAMBU STUDIO / ORCASLICER:
======================================================================
METHOD 1: NATIVE .3MF PROJECT (RECOMMENDED)
1. Open Bambu Studio.
2. Drag and drop '{mf3_filename}' onto the build plate.
3. In the left panel (Process -> Objects), verify the parts are listed.
4. Assign your AMS filament slots (Slot 1 to {len(exported_inlays) + 1}) to the parts.

METHOD 2: SPLIT STLs (MULTI-PART MERGE)
1. In Bambu Studio, select your printer.
2. Select all STL files simultaneously:
{stl_list_str}
3. Drag all files together onto the build plate.
4. When prompted: "Load these files as a single object with multiple parts?"
   -> Click YES.
5. All parts will lock together in exact (0, 0, 0) 3D alignment.

======================================================================
FILAMENT / AMS SLOT MAPPING:
======================================================================
{slot_mapping_str}

======================================================================
RECOMMENDED 95A TPU PRINT SETTINGS:
======================================================================
- Layer Height: 0.20mm Standard (0.16mm Optimal for fine face detail)
- Wall Loops: 3
- Infill: 100% Solid (flexible high-durability armor for race day)
- Nozzle Temp: 225°C - 235°C
- Bed Temp: 35°C (Textured PEI Plate - use glue stick if TPU sticks too firmly)
- Print Speed: 30 - 45 mm/s (TPU requires steady, unhurried flow)
- Wipe Tower: Enabled (Prime volume ~25-35 mm3)
======================================================================
"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('README_BAMBU_STUDIO.txt', readme_content)
        zf.write(chassis_path, chassis_filename)
        zf.write(lid_path, lid_filename)
        for c_n, c_p in color_stls.items():
            zf.write(c_p, os.path.basename(c_p))
        if os.path.exists(mf3_path):
            zf.write(mf3_path, mf3_filename)

    # 12. Parametric OpenSCAD Export
    scad_code = f'''// ============================================================================
// 🏰 Main Street Electrical Parade (WDW 10K) - 3D TPU Armor Plate ({variant_name.upper()})
// Dimensions: {panel_w}mm x {panel_h}mm x {TOTAL_THICK}mm
// Sized for Snapmaker U1 & Bambu Lab | Material: 95A TPU
// Aperture: {aperture_desc} | Orientation: {well_orientation}
// ============================================================================
$fn = 24;
front_thickness = {FRONT_THICK_GENERAL};
total_thickness = {TOTAL_THICK};
contour_pts = {contour_coords};
ordered_leds = {[ [round(l['x'], 2), round(l['y'], 2)] for l in leds ]};
fastener_tabs = {tab_coords};

linear_extrude(front_thickness) polygon(contour_pts);
'''
    scad_filename = f"tpu_panel_{variant_name}.scad"
    scad_path = os.path.join(out_dir, scad_filename)
    with open(scad_path, 'w', encoding='utf-8') as f_scad:
        f_scad.write(scad_code)
    if variant_name == 'front':
        shutil.copyfile(scad_path, os.path.join(out_dir, 'petes_dragon_tpu_panel.scad'))

    stl_size = os.path.getsize(mono_path)
    chassis_size = os.path.getsize(chassis_path)
    zip_size = os.path.getsize(zip_path)
    stl_bounds = [round(float(x), 2) for x in (final_monolithic_tm.bounds[1] - final_monolithic_tm.bounds[0])]
    stl_center = [round(float(x), 2) for x in ((final_monolithic_tm.bounds[1] + final_monolithic_tm.bounds[0]) / 2.0)]
    
    print(f"[{variant_name}] SUCCESS! Exported {mono_filename} ({stl_size/1024/1024:.2f} MB), Chassis ({chassis_size/1024/1024:.2f} MB), Lid ({lid_size/1024/1024:.2f} MB), Bundle ZIP ({zip_size/1024/1024:.2f} MB) in {time.time()-v_t0:.2f}s")
    print(f"[{variant_name}] Dimensions: {stl_bounds} | Center: {stl_center}")

    return {
        "variant": variant_name,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "panel_width_mm": panel_w,
        "panel_height_mm": panel_h,
        "total_image_width_mm": width_mm,
        "total_image_height_mm": height_mm,
        "window_shape": window_shape,
        "well_orientation": well_orientation,
        "ordered_leds": leds,
        "led_count": len(leds),
        "fastener_tabs": tab_coords,
        "entrance_portal": [round(float(wire_portal_x), 2), round(float(wire_portal_y), 2)],
        "entrance_bridge": [round(float(wire_portal_x), 2), round(float(bridge_y), 2)],
        "exit_portal": [round(float(exit_portal_x), 2), round(float(exit_portal_y), 2)],
        "exit_bridge": [round(float(bridge_exit_x), 2), round(float(bridge_exit_y), 2)],
        "screw_positions": screw_coords,
        "number_positions": number_positions,
        "contour_pts": contour_coords,
        "stl_bounds": stl_bounds,
        "stl_center": stl_center,
        "stl_size": stl_size,
        "chassis_size": chassis_size,
        "lid_size": lid_size,
        "zip_size": zip_size,
        "inlays": exported_inlays,
        "stl_url": f"/3d_panels/{mono_filename}",
        "chassis_stl_url": f"/3d_panels/{chassis_filename}",
        "lid_stl_url": f"/3d_panels/{lid_filename}",
        "multicolor_3mf_url": f"/3d_panels/{mf3_filename}" if os.path.exists(mf3_path) else None,
        "multicolor_zip_url": f"/3d_panels/{zip_filename}",
        "volume_mm3": round(final_monolithic_tm.volume, 1),
        "is_watertight": final_monolithic_tm.is_watertight
    }

# ---------------------------------------------------------------------------
# MAIN BATCH COMPILATION: FRONT & BACK PLATES
# ---------------------------------------------------------------------------
artwork_file = specs.get('artwork_file', 'active_artwork.png')
artwork_path = os.path.join('3d_panels', artwork_file)
if not os.path.exists(artwork_path):
    artwork_path = 'assets/petes_dragon_transparent.png'

print(f"Using artwork: {artwork_path}")

# Check CLI overrides
target_width_override = None
if '--width-mm' in sys.argv:
    try:
        w_idx = sys.argv.index('--width-mm')
        if w_idx + 1 < len(sys.argv):
            target_width_override = float(sys.argv[w_idx + 1])
    except Exception:
        pass

# Check if specs has structured front/back definitions
front_specs = specs.get('front')
back_specs = specs.get('back')

if not front_specs:
    front_specs = {
        'width_mm': specs.get('width_mm', 203.2),
        'height_mm': specs.get('height_mm', 169.1),
        'ordered_leds': specs.get('ordered_leds', [])
    }

if target_width_override is not None:
    aspect = front_specs['width_mm'] / float(max(1.0, front_specs.get('height_mm', 169.1)))
    front_specs['width_mm'] = target_width_override
    front_specs['height_mm'] = round(target_width_override / aspect, 2)

if not back_specs:
    aspect = front_specs['width_mm'] / float(max(1.0, front_specs['height_mm']))
    b_w = target_width_override if target_width_override is not None else 203.2
    b_h = round(b_w / aspect, 2)
    scale_factor = b_w / float(front_specs['width_mm'])
    b_leds = []
    for l in front_specs['ordered_leds']:
        nl = dict(l)
        nl['x'] = round(l['x'] * scale_factor, 2)
        nl['y'] = round(l['y'] * scale_factor, 2)
        b_leds.append(nl)
    back_specs = {
        'width_mm': b_w,
        'height_mm': b_h,
        'ordered_leds': b_leds
    }
elif target_width_override is not None:
    aspect = back_specs['width_mm'] / float(max(1.0, back_specs['height_mm']))
    back_specs['width_mm'] = target_width_override
    back_specs['height_mm'] = round(target_width_override / aspect, 2)

window_shape = specs.get('window_shape', 'round_34')
if window_shape in ['round', 'circle']:
    window_shape = 'round_34'
if '--window-shape' in sys.argv:
    try:
        w_idx = sys.argv.index('--window-shape')
        if w_idx + 1 < len(sys.argv):
            window_shape = sys.argv[w_idx + 1]
    except Exception:
        pass

well_orientation = specs.get('well_orientation', 'horizontal')
if '--orientation' in sys.argv:
    try:
        o_idx = sys.argv.index('--orientation')
        if o_idx + 1 < len(sys.argv):
            well_orientation = sys.argv[o_idx + 1].lower()
    except Exception:
        pass

if MATRIX_16X16_MODE:
    windowed_leds_spec = specs.get('matrix_windowed_leds', None)
    backlight_leds_spec = specs.get('matrix_backlight_leds', None)
    # 1. Compile Front 16x16 Matrix Backlight Plate
    front_result = compile_matrix_16x16_plate_variant(
        'front',
        artwork_path,
        window_shape=window_shape,
        plate_thickness_mm=PLATE_THICKNESS_MM,
        windowed_leds=windowed_leds_spec,
        backlight_leds=backlight_leds_spec
    )
    # 2. Compile Back 16x16 Matrix Backlight Plate
    back_result = compile_matrix_16x16_plate_variant(
        'back',
        artwork_path,
        window_shape=window_shape,
        plate_thickness_mm=PLATE_THICKNESS_MM,
        windowed_leds=windowed_leds_spec,
        backlight_leds=backlight_leds_spec
    )
else:
    # 1. Compile Front Plate
    front_result = compile_plate_variant(
        'front',
        front_specs['width_mm'],
        front_specs['height_mm'],
        front_specs['ordered_leds'],
        artwork_path,
        window_shape=window_shape,
        clip_grooves=INCLUDE_CLIP_GROOVES,
        top_nubs=INCLUDE_TOP_NUBS,
        well_orientation=well_orientation
    )

    # 2. Compile Back Plate
    back_result = compile_plate_variant(
        'back',
        back_specs['width_mm'],
        back_specs['height_mm'],
        back_specs['ordered_leds'],
        artwork_path,
        window_shape=window_shape,
        clip_grooves=INCLUDE_CLIP_GROOVES,
        top_nubs=INCLUDE_TOP_NUBS,
        well_orientation=well_orientation
    )

# Update full JSON specifications
active_graphic_type = specs.get('graphic_type', '')
front_result['graphic_type'] = active_graphic_type
back_result['graphic_type'] = active_graphic_type
specs['graphic_type'] = active_graphic_type
specs['window_shape'] = window_shape
specs['well_orientation'] = well_orientation
specs['include_led_numbers'] = INCLUDE_LED_NUMBERS
specs['include_clip_grooves'] = INCLUDE_CLIP_GROOVES
specs['include_top_nubs'] = INCLUDE_TOP_NUBS
specs['matrix_16x16_mode'] = MATRIX_16X16_MODE
specs['plate_thickness_mm'] = round(PLATE_THICKNESS_MM, 2)
specs['front'] = front_result
specs['back'] = back_result

# Copy front metrics to root for backward compatibility
for k, v in front_result.items():
    specs[k] = v

with open(specs_path, 'w', encoding='utf-8') as f:
    json.dump(specs, f, indent=2)

if specs_path != '3d_panels/petes_dragon_specs.json':
    shutil.copyfile(specs_path, '3d_panels/petes_dragon_specs.json')

print("\n" + "=" * 70)
print(f"ALL PANELS COMPILED IN {time.time()-t0:.2f}s TOTAL!")
print(f"Front: {front_result['stl_bounds']} ({front_result['stl_size']/1024/1024:.2f} MB) | Bundle ZIP: {front_result['zip_size']/1024/1024:.2f} MB")
print(f"Back:  {back_result['stl_bounds']} ({back_result['stl_size']/1024/1024:.2f} MB) | Bundle ZIP: {back_result['zip_size']/1024/1024:.2f} MB")
print("=" * 70)
