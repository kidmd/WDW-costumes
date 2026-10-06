import json, math, time, os, shutil, sys
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
import trimesh
from manifold3d import Manifold, Mesh, OpType
import cv2
from PIL import Image

print("=" * 70)
print("ANTIGRAVITY IMAGINEERING - DUAL FRONT & BACK TPU ARMOR TRAY COMPILER v4")
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
TOTAL_THICK = 6.0           # mm (overall height to top of perimeter rim)
RIM_HEIGHT = 4.0            # mm (outer wall from Z = 2.0 to 6.0)
RIM_WALL_THICK = 2.5        # mm (width of outer perimeter wall)

COLLAR_FLOOR_Z = 1.0        # mm (pocket floor starts at Z = 1.0)
COLLAR_HEIGHT = 3.0         # mm (pocket walls rise 3.0mm, from Z = 1.0 to 4.0)
COLLAR_TOP_Z = 4.0          # mm (leaving exactly 2.0mm space below 6.0mm rim!)
COLLAR_INNER_L = 10.0       # mm (10mm inner length)
COLLAR_INNER_W = 5.0        # mm (5mm inner width)
COLLAR_WALL_THICK = 1.2     # mm (collar wall thickness)
COLLAR_OUTER_L = COLLAR_INNER_L + 2 * COLLAR_WALL_THICK # 12.4mm
COLLAR_OUTER_W = COLLAR_INNER_W + 2 * COLLAR_WALL_THICK # 7.4mm

NOTCH_WIDTH = 4.0           # mm (wire pass-through slot on both 5mm ends)
WINDOW_SQ = 3.0             # mm (3x3mm square optical aperture through 1.0mm front skin)

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
    v = np.ascontiguousarray(tm.vertices, dtype=np.float32)
    f = np.ascontiguousarray(tm.faces, dtype=np.uint32)
    return Manifold(Mesh(vert_properties=v, tri_verts=f))

def compile_plate_variant(variant_name, width_mm, height_mm, raw_leds, artwork_path, window_shape='square'):
    print(f"\n>>> Compiling {variant_name.upper()} Plate ({width_mm}mm x {height_mm}mm, Window Shape: {window_shape.upper()})...")
    v_t0 = time.time()
    num_leds = len(raw_leds)
    leds = [dict(l) for l in raw_leds]

    # 1. Extract Active Silhouette Boundary & Safe Artwork Containment Zone
    active_img = Image.open(artwork_path)
    img_w, img_h = active_img.size
    img_arr = np.array(active_img)

    if img_arr.ndim == 3 and img_arr.shape[2] == 4:
        alpha = img_arr[:, :, 3]
        mask = (alpha > 40).astype(np.uint8)
    else:
        gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY) if img_arr.ndim == 3 else img_arr
        _, mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)

    raw_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if raw_contours:
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

    # 2. LED Collar Horizontal Orientation & PBD Collision Avoidance with Artwork Boundary Clamping
    led_rotations_deg = [0.0] * num_leds
    pts = np.array([[l['x'], l['y']] for l in leds], dtype=np.float64)
    orig_pts = pts.copy()
    req_dist = 7.4 + 0.5 # 7.9 mm center distance

    for iteration in range(60):
        for i in range(num_leds):
            for j in range(i + 1, num_leds):
                dx = pts[j, 0] - pts[i, 0]
                dy = pts[j, 1] - pts[i, 1]
                adx = abs(dx)
                ady = abs(dy)
                seg_dx = max(0.0, adx - 5.0)
                seg_dy = ady
                center_dist = np.hypot(seg_dx, seg_dy)
                
                if center_dist < req_dist:
                    pen = req_dist - center_dist
                    if center_dist < 1e-4:
                        nx, ny = 0.0, 1.0
                    else:
                        nx = (seg_dx / center_dist) * (1.0 if dx >= 0 else -1.0)
                        ny = (seg_dy / center_dist) * (1.0 if dy >= 0 else -1.0)
                    
                    push_x = nx * pen * 0.35
                    push_y = ny * pen * 0.35
                    pts[i] -= [push_x, push_y]
                    pts[j] += [push_x, push_y]

        # Clamp strictly within artwork boundary so LEDs never bleed out into empty space!
        for i in range(num_leds):
            pt = sg.Point(pts[i])
            if not safe_art_boundary.contains(pt):
                nearest = safe_art_boundary.exterior.interpolate(safe_art_boundary.exterior.project(pt))
                pts[i] = [nearest.x, nearest.y]

    max_shift = np.max(np.hypot(pts[:, 0] - orig_pts[:, 0], pts[:, 1] - orig_pts[:, 1]))
    avg_shift = np.mean(np.hypot(pts[:, 0] - orig_pts[:, 0], pts[:, 1] - orig_pts[:, 1]))
    print(f"[{variant_name}] PBD solver: Max shift = {max_shift:.2f}mm, Avg shift = {avg_shift:.2f}mm.")
    for i in range(num_leds):
        leds[i]['x'] = round(float(pts[i, 0]), 2)
        leds[i]['y'] = round(float(pts[i, 1]), 2)

    # 3. Dilate Outer Rim and Generate Armor Plate Polygon
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
    rim_mesh.apply_translation([0, 0, FRONT_THICK_GENERAL]) # Z = 2.0 to 6.0mm

    # 3. 16 Outside Perimeter Mounting Eyelets
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
        pt_next = boundary_line.interpolate(min(total_len, dist_along + 1.0))
        tan = np.array([pt_next.x - pt.x, pt_next.y - pt.y])
        tan_norm = tan / (np.linalg.norm(tan) + 1e-6)
        normal = np.array([-tan_norm[1], tan_norm[0]])
        cand_center = np.array([pt.x, pt.y]) + normal * 1.5
        if smoothed_plate_2d.contains(sg.Point(cand_center)):
            normal = -normal
            cand_center = np.array([pt.x, pt.y]) + normal * 1.5
            
        tab_coords.append([round(float(cand_center[0]), 2), round(float(cand_center[1]), 2)])
        cyl = Manifold.cylinder(TAB_HEIGHT, TAB_OUTER_R, TAB_OUTER_R, 32).translate([cand_center[0], cand_center[1], 4.0])
        hole = Manifold.cylinder(TAB_HEIGHT + 0.4, TAB_INNER_R, TAB_INNER_R, 32).translate([cand_center[0], cand_center[1], 3.8])
        tab_m = cyl - hole
        tab_mesh_data = tab_m.to_mesh()
        tab_solid = trimesh.Trimesh(vertices=tab_mesh_data.vert_properties[:, :3], faces=tab_mesh_data.tri_verts)
        tab_meshes.append(tab_solid)

    # 4. Collars, Recesses & Windows
    outer_collar_2d = make_stadium_polygon(COLLAR_OUTER_L, COLLAR_OUTER_W, sections=16)
    inner_collar_2d = make_stadium_polygon(COLLAR_INNER_L, COLLAR_INNER_W, sections=16)
    collar_ring_2d = sg.Polygon(outer_collar_2d.exterior.coords, [inner_collar_2d.exterior.coords])

    collar_meshes = []
    floor_recess_cutters = []
    square_window_cutters = []

    for i in range(num_leds):
        l = leds[i]
        cx, cy = l['x'], l['y']
        angle_deg = led_rotations_deg[i]
        rad = math.radians(angle_deg)
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])

        # Floor Recess (1.0mm)
        recess = trimesh.creation.extrude_polygon(inner_collar_2d, height=1.1)
        recess.apply_transform(rot)
        recess.apply_translation([cx, cy, FRONT_THICK_LED])
        floor_recess_cutters.append(recess)

        # 3.0mm Collar with 4mm Wire Notches
        c_mesh = trimesh.creation.extrude_polygon(collar_ring_2d, height=COLLAR_HEIGHT)
        notch_r = trimesh.creation.box(extents=[3.5, NOTCH_WIDTH, COLLAR_HEIGHT + 0.2])
        notch_r.apply_translation([COLLAR_OUTER_L / 2.0 - 1.0, 0, COLLAR_HEIGHT / 2.0])
        notch_l = trimesh.creation.box(extents=[3.5, NOTCH_WIDTH, COLLAR_HEIGHT + 0.2])
        notch_l.apply_translation([-COLLAR_OUTER_L / 2.0 + 1.0, 0, COLLAR_HEIGHT / 2.0])
        notched_collar = c_mesh.difference(trimesh.boolean.union([notch_r, notch_l]))
        notched_collar.apply_transform(rot)
        notched_collar.apply_translation([cx, cy, COLLAR_FLOOR_Z])
        collar_meshes.append(notched_collar)

        # 3x3mm Square or Ø 3mm Round Optical Window
        if str(window_shape).lower() in ['round', 'circle']:
            sq_win = trimesh.creation.cylinder(radius=WINDOW_SQ / 2.0, height=FRONT_THICK_LED + 1.0, sections=24)
        else:
            sq_win = trimesh.creation.box(extents=[WINDOW_SQ, WINDOW_SQ, FRONT_THICK_LED + 1.0])
            sq_win.apply_transform(rot)
        sq_win.apply_translation([cx, cy, FRONT_THICK_LED / 2.0])
        square_window_cutters.append(sq_win)

    # 5. Debossed LED Numbers (1 to 100)
    number_positions = []
    number_cutters = []

    for i, l in enumerate(leds):
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
            min_d = min(np.linalg.norm(cand - np.array([ol['x'], ol['y']])) for j, ol in enumerate(leds) if j != i)
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
            num_combined.apply_translation([-tx_mid[0], -tx_mid[1], 1.5])
            num_combined.apply_translation([best_cand[0], best_cand[1], 0.0])
            number_cutters.append(num_combined)

    # 6. Manifold3D Assembly & Boolean Operations
    all_solids = [base_front_mesh, rim_mesh] + tab_meshes + collar_meshes
    solids_m = [to_m(s) for s in all_solids]
    assembled_m = Manifold.batch_boolean(solids_m, OpType.Add)

    all_cutters = floor_recess_cutters + square_window_cutters + number_cutters
    cutters_m = [to_m(c) for c in all_cutters]
    cutters_union_m = Manifold.batch_boolean(cutters_m, OpType.Add)

    final_m = assembled_m - cutters_union_m
    out_m = final_m.to_mesh()

    # Flip Z so FRONT face faces +Z and UNDERSIDE faces -Z
    verts_flipped = out_m.vert_properties[:, :3].copy()
    verts_flipped[:, 2] = TOTAL_THICK - verts_flipped[:, 2]
    faces_flipped = out_m.tri_verts[:, ::-1].copy()
    final_model = trimesh.Trimesh(vertices=verts_flipped, faces=faces_flipped, process=True)

    # Export STL
    stl_filename = f"tpu_panel_{variant_name}.stl"
    stl_path = os.path.join('3d_panels', stl_filename)
    final_model.export(stl_path)

    if variant_name == 'front':
        # Maintain backward compatibility aliases
        shutil.copyfile(stl_path, '3d_panels/tpu_panel.stl')
        shutil.copyfile(stl_path, '3d_panels/petes_dragon_tpu_panel.stl')

    # Export OpenSCAD Parametric Model
    scad_code = f'''// ============================================================================
// 🏰 Main Street Electrical Parade (WDW 10K) - 3D TPU Armor Plate ({variant_name.upper()})
// Dimensions: {panel_w}mm x {panel_h}mm x {TOTAL_THICK}mm
// Sized for Snapmaker U1 & Bambu Lab | Material: 95A TPU
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
    scad_path = os.path.join('3d_panels', scad_filename)
    with open(scad_path, 'w', encoding='utf-8') as f_scad:
        f_scad.write(scad_code)
    if variant_name == 'front':
        shutil.copyfile(scad_path, '3d_panels/petes_dragon_tpu_panel.scad')

    stl_size = os.path.getsize(stl_path)
    stl_bounds = [round(float(x), 2) for x in (final_model.bounds[1] - final_model.bounds[0])]
    stl_center = [round(float(x), 2) for x in ((final_model.bounds[1] + final_model.bounds[0]) / 2.0)]
    print(f"[{variant_name}] SUCCESS! Exported {stl_filename} ({stl_size/1024/1024:.2f} MB) in {time.time()-v_t0:.2f}s")
    print(f"[{variant_name}] Dimensions: {stl_bounds} | Center: {stl_center}")

    return {
        "variant": variant_name,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "panel_width_mm": panel_w,
        "panel_height_mm": panel_h,
        "total_image_width_mm": width_mm,
        "total_image_height_mm": height_mm,
        "ordered_leds": leds,
        "fastener_tabs": tab_coords,
        "number_positions": number_positions,
        "contour_pts": contour_coords,
        "stl_bounds": stl_bounds,
        "stl_center": stl_center,
        "stl_size": stl_size,
        "volume_mm3": round(final_model.volume, 1),
        "is_watertight": final_model.is_watertight
    }

# ---------------------------------------------------------------------------
# MAIN BATCH COMPILATION: FRONT & BACK PLATES
# ---------------------------------------------------------------------------
artwork_file = specs.get('artwork_file', 'active_artwork.png')
artwork_path = os.path.join('3d_panels', artwork_file)
if not os.path.exists(artwork_path):
    artwork_path = 'assets/petes_dragon_transparent.png'

print(f"Using artwork: {artwork_path}")

# Check if specs has structured front/back definitions
front_specs = specs.get('front')
back_specs = specs.get('back')

if not front_specs:
    front_specs = {
        'width_mm': specs.get('width_mm', 185.0),
        'height_mm': specs.get('height_mm', 154.0),
        'ordered_leds': specs.get('ordered_leds', [])
    }

if not back_specs:
    aspect = front_specs['width_mm'] / float(max(1.0, front_specs['height_mm']))
    back_max = 240.0
    if aspect >= 1.0:
        b_w, b_h = back_max, round(back_max / aspect, 2)
    else:
        b_h, b_w = back_max, round(back_max * aspect, 2)
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

window_shape = specs.get('window_shape', 'square')
if '--window-shape' in sys.argv:
    try:
        w_idx = sys.argv.index('--window-shape')
        if w_idx + 1 < len(sys.argv):
            window_shape = sys.argv[w_idx + 1]
    except Exception:
        pass

# 1. Compile Front Plate
front_result = compile_plate_variant(
    'front',
    front_specs['width_mm'],
    front_specs['height_mm'],
    front_specs['ordered_leds'],
    artwork_path,
    window_shape=window_shape
)

# 2. Compile Back Plate
back_result = compile_plate_variant(
    'back',
    back_specs['width_mm'],
    back_specs['height_mm'],
    back_specs['ordered_leds'],
    artwork_path,
    window_shape=window_shape
)

# Update full JSON specifications
specs['window_shape'] = window_shape
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
print(f"Front: {front_result['stl_bounds']} ({front_result['stl_size']/1024/1024:.2f} MB)")
print(f"Back:  {back_result['stl_bounds']} ({back_result['stl_size']/1024/1024:.2f} MB)")
print("=" * 70)
