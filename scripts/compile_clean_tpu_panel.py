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
TOTAL_THICK = 9.0           # mm (overall height to top of perimeter rim)
RIM_HEIGHT = 7.0            # mm (outer wall from Z = 2.0 to 9.0)
RIM_WALL_THICK = 2.5        # mm (width of outer perimeter wall)

COLLAR_FLOOR_Z = 1.0        # mm (pocket floor starts at Z = 1.0)
COLLAR_HEIGHT = 3.0         # mm (pocket walls rise 3.0mm, from Z = 1.0 to 4.0)
COLLAR_TOP_Z = 4.0          # mm (leaving exactly 5.0mm space below 9.0mm rim!)
COLLAR_INNER_L = 10.0       # mm (10mm inner length)
COLLAR_INNER_W = 5.0        # mm (5mm inner width)
COLLAR_WALL_THICK = 1.2     # mm (collar wall thickness)
COLLAR_OUTER_L = COLLAR_INNER_L + 2 * COLLAR_WALL_THICK # 12.4mm
COLLAR_OUTER_W = COLLAR_INNER_W + 2 * COLLAR_WALL_THICK # 7.4mm

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
    return trimesh.Trimesh(vertices=v, faces=f, process=True)

def flip_z_trimesh(tm):
    if tm is None or len(tm.faces) == 0:
        return None
    v = tm.vertices.copy()
    v[:, 2] = TOTAL_THICK - v[:, 2]
    f = tm.faces[:, ::-1].copy()
    return trimesh.Trimesh(vertices=v, faces=f, process=True)

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

def compile_plate_variant(variant_name, width_mm, height_mm, raw_leds, artwork_path, window_shape='square', clip_grooves=False, top_nubs=False):
    print(f"\n>>> Compiling {variant_name.upper()} Plate ({width_mm}mm x {height_mm}mm, {len(raw_leds)} LEDs, Window Shape: {window_shape.upper()}, Clip Grooves: {'ON' if clip_grooves else 'OFF'}, Top Nubs: {'ON' if top_nubs else 'OFF'})...")
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

    if corners_opaque and corners_black:
        mask = ((rgb.max(axis=2) > 20) & (alpha > 40)).astype(np.uint8)
    else:
        mask = (alpha > 40).astype(np.uint8)

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

    # 2. LED Collar Orientation & Collision Avoidance
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

        for i in range(num_leds):
            pt = sg.Point(pts[i])
            if not safe_art_boundary.contains(pt):
                nearest = safe_art_boundary.exterior.interpolate(safe_art_boundary.exterior.project(pt))
                pts[i] = [nearest.x, nearest.y]

    max_shift = np.max(np.hypot(pts[:, 0] - orig_pts[:, 0], pts[:, 1] - orig_pts[:, 1])) if num_leds > 0 else 0.0
    avg_shift = np.mean(np.hypot(pts[:, 0] - orig_pts[:, 0], pts[:, 1] - orig_pts[:, 1])) if num_leds > 0 else 0.0
    print(f"[{variant_name}] PBD solver ({num_leds} LEDs): Max shift = {max_shift:.2f}mm, Avg shift = {avg_shift:.2f}mm.")
    for i in range(num_leds):
        leds[i]['x'] = round(float(pts[i, 0]), 2)
        leds[i]['y'] = round(float(pts[i, 1]), 2)

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

    # 4. 16 Outside Perimeter Mounting Eyelets
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

    # 4b. Bottom-Center Wire Entry/Exit Notch & Internal Strain Relief Anchor (Option B)
    cx_mid = (bounds[0] + bounds[2]) / 2.0
    bottom_pts = [p for p in contour_coords if abs(p[0] - cx_mid) < 25.0]
    if bottom_pts:
        lowest_pt = min(bottom_pts, key=lambda p: p[1])
        wire_portal_x = lowest_pt[0]
        wire_portal_y = lowest_pt[1]
    else:
        wire_portal_x = cx_mid
        wire_portal_y = bounds[1]

    # Parting-line wire exit notch at top of outer rim wall (Z = 6.0 to 9.2mm in pre-flip space)
    # Flips to Z = 0.0 to 3.0mm in exported STL (right at the parting line where outer wall meets lid!)
    PORTAL_NOTCH_W = 5.5   # mm wide
    PORTAL_NOTCH_H = 3.0   # mm tall
    wire_portal_cutter = trimesh.creation.box(extents=[PORTAL_NOTCH_W, RIM_WALL_THICK + 4.0, PORTAL_NOTCH_H + 0.4])
    wire_portal_cutter.apply_translation([wire_portal_x, wire_portal_y, TOTAL_THICK - PORTAL_NOTCH_H / 2.0 + 0.2])

    # Internal floor zip-tie strain relief bridge (no holes piercing front artwork face!)
    # Bridge: 7.0mm wide (X, across wire) x 5.0mm long (Y, along wire) x 2.8mm tall (Z = 2.0 to 4.8mm)
    # Under-Tunnel (Perpendicular to wire): cuts left-to-right (along X) under bridge:
    #   10.0mm long in X (clears both sides) x 3.0mm wide in Y (for 2.5mm zip-tie) x 1.4mm tall in Z (Z = 2.0 to 3.4mm)
    # Wire Saddle: shallow 0.6mm concave cradle on top of bridge along Y (aligned with wire path from U-notch):
    #   4.5mm wide in X x 7.0mm long in Y x 0.8mm tall in Z (recessing 0.6mm into top, Z = 4.2 to 4.9mm)
    bridge_y = wire_portal_y + RIM_WALL_THICK + 5.0
    BRIDGE_X_W = 7.0
    BRIDGE_Y_L = 5.0
    BRIDGE_Z_H = 2.8
    bridge_solid_tm = trimesh.creation.box(extents=[BRIDGE_X_W, BRIDGE_Y_L, BRIDGE_Z_H])
    bridge_solid_tm.apply_translation([wire_portal_x, bridge_y, FRONT_THICK_GENERAL + BRIDGE_Z_H / 2.0])

    tunnel_cutter_tm = trimesh.creation.box(extents=[BRIDGE_X_W + 4.0, 3.0, 1.4 + 0.4])
    tunnel_cutter_tm.apply_translation([wire_portal_x, bridge_y, FRONT_THICK_GENERAL + 0.70 - 0.2])

    saddle_cutter_tm = trimesh.creation.box(extents=[4.5, BRIDGE_Y_L + 2.0, 0.8])
    saddle_cutter_tm.apply_translation([wire_portal_x, bridge_y, FRONT_THICK_GENERAL + BRIDGE_Z_H - 0.3])

    internal_bridge_m = to_m(bridge_solid_tm) - to_m(tunnel_cutter_tm) - to_m(saddle_cutter_tm)

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

        # 3x3mm Square or Ø 3mm Round Optical Window
        if str(window_shape).lower() in ['round', 'circle']:
            sq_win = trimesh.creation.cylinder(radius=WINDOW_SQ / 2.0, height=FRONT_THICK_LED + 1.0, sections=24)
            win_2d = sg.Point(cx, cy).buffer(WINDOW_SQ / 2.0, resolution=16)
        else:
            sq_win = trimesh.creation.box(extents=[WINDOW_SQ, WINDOW_SQ, FRONT_THICK_LED + 1.0])
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

    if raw_stl_colors and isinstance(raw_stl_colors, dict):
        stl_colors = raw_stl_colors
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
            'black': { 'name': 'Chassis & Shell Background', 'hex': '#11161d', 'targetRgb': [17, 22, 29], 'role': 'chassis' },
            'red': { 'name': 'Head, Neck & Foot', 'hex': '#ef4444', 'targetRgb': [239, 68, 68], 'role': 'inlay', 'filename': 'color_red.stl' },
            'gold': { 'name': 'Antennae, Spiral & Edge', 'hex': '#facc15', 'targetRgb': [250, 204, 21], 'role': 'inlay', 'filename': 'color_gold.stl' },
            'green': { 'name': 'Green Radial Stripes', 'hex': '#10b981', 'targetRgb': [16, 185, 129], 'role': 'inlay', 'filename': 'color_green.stl' },
            'blue': { 'name': 'Blue Radial Stripes', 'hex': '#2563eb', 'targetRgb': [37, 99, 235], 'role': 'inlay', 'filename': 'color_blue.stl' }
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

    # 7b. Perimeter Screw Boss Locations (6 to 8 perimeter positions avoiding LEDs and wire portal)
    NUM_SCREWS = 8
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
    screw_coords = []
    
    for i in range(NUM_SCREWS):
        nominal_d = (i / float(NUM_SCREWS)) * total_inner_len
        best_pt = None
        best_clearance = -1
        # Search along boundary arc +/- 12mm for maximum clearance from LEDs & wire portal
        for delta in np.linspace(-12.0, 12.0, 17):
            cur_d = (nominal_d + delta) % total_inner_len
            cand_p = inner_boundary.interpolate(cur_d)
            dist_portal = np.linalg.norm([cand_p.x - wire_portal_x, cand_p.y - wire_portal_y])
            if dist_portal < 14.0:
                continue
            min_led = min(np.linalg.norm([cand_p.x - l['x'], cand_p.y - l['y']]) for l in leds) if leds else 20.0
            if min_led > best_clearance:
                best_clearance = min_led
                best_pt = cand_p
                
        if best_pt is None:
            best_pt = inner_boundary.interpolate(nominal_d)
        screw_coords.append([round(float(best_pt.x), 2), round(float(best_pt.y), 2)])

    tray_boss_solids = []
    pilot_hole_cutters = []
    for sp in screw_coords:
        # 5.0mm diameter pillar rising from Z = 2.0 to 9.0mm fused to inner rim wall
        boss_cyl = make_clean_cylinder(RIM_HEIGHT, SCREW_BOSS_R, 32).translate([sp[0], sp[1], FRONT_THICK_GENERAL])
        tray_boss_solids.append(boss_cyl)
        # 1.6mm diameter pilot hole from top of rim down 5.5mm (Z = 9.0 down to 3.5mm)
        pilot_cyl = make_clean_cylinder(PILOT_HOLE_DEPTH + 0.2, PILOT_HOLE_R, 32).translate([sp[0], sp[1], TOTAL_THICK - PILOT_HOLE_DEPTH])
        pilot_hole_cutters.append(pilot_cyl)

    chassis_solids = [base_with_pockets_m, to_m(rim_mesh), internal_bridge_m] + [to_m(t) for t in tab_meshes] + [to_m(c) for c in collar_meshes] + tray_boss_solids
    chassis_assembled_m = Manifold.batch_boolean(chassis_solids, OpType.Add)

    # Cutters: floor recesses, square/round optical windows, debossed numbers, wire portal notch, and M2 pilot holes (no front face holes!)
    all_cutters = floor_recess_cutters + square_window_cutters + number_cutters + [wire_portal_cutter]
    cutters_m = [to_m(c) for c in all_cutters] + pilot_hole_cutters
    cutters_union_m = Manifold.batch_boolean(cutters_m, OpType.Add)

    final_chassis_m = chassis_assembled_m - cutters_union_m
    final_chassis_tm = flip_z_manifold(final_chassis_m)

    # Monolithic single-color black STL (legacy compatible, without color pockets subtracted)
    monolithic_solids = [base_m, to_m(rim_mesh), internal_bridge_m] + [to_m(t) for t in tab_meshes] + [to_m(c) for c in collar_meshes] + tray_boss_solids
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

    # Cutout over wire portal so outgoing wires are never pinched
    portal_relief_m = Manifold.cube([14.0, RIM_WALL_THICK + 8.0, RIDGE_HEIGHT + 0.6], True).translate([wire_portal_x, wire_portal_y, LID_THICK + RIDGE_HEIGHT / 2.0])

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
    lid_cutters_m = Manifold.batch_boolean([portal_relief_m] + boss_relief_m + screw_holes_m + screw_cbore_m, OpType.Add)
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
    specs['stl_colors'] = stl_colors

    if variant_name == 'front':
        shutil.copyfile(mono_path, os.path.join(out_dir, 'tpu_panel.stl'))
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

    readme_content = f"""🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K) - 3D TPU ARMOR PLATE
BAMBU LAB X1-CARBON / AMS MULTI-COLOR PRINTING GUIDE

PLATE VARIANT: {variant_name.upper()} ({specs.get('float_name', 'MSEP Float')})
======================================================================
PHYSICAL SIZE: {panel_w} mm W x {panel_h} mm H (Target Width: {width_mm} mm / ~{round(width_mm/25.4, 1)} in)
ACTIVE LEDS: {num_leds} LEDs with 3x3mm open optical apertures

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
        "ordered_leds": leds,
        "led_count": len(leds),
        "fastener_tabs": tab_coords,
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
    window_shape=window_shape,
    clip_grooves=INCLUDE_CLIP_GROOVES,
    top_nubs=INCLUDE_TOP_NUBS
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
    top_nubs=INCLUDE_TOP_NUBS
)

# Update full JSON specifications
specs['window_shape'] = window_shape
specs['include_led_numbers'] = INCLUDE_LED_NUMBERS
specs['include_clip_grooves'] = INCLUDE_CLIP_GROOVES
specs['include_top_nubs'] = INCLUDE_TOP_NUBS
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
