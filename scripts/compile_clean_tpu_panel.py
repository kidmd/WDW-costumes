import json, math, time, os
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
import trimesh

print("=" * 70)
print("ANTIGRAVITY IMAGINEERING - OPEN CHASSIS TPU CHEST ARMOR TRAY COMPILER v3")
print("=" * 70)
t0 = time.time()

specs_path = '3d_panels/petes_dragon_specs.json'
with open(specs_path) as f:
    specs = json.load(f)

leds = specs['ordered_leds']
num_leds = len(leds)

# ---------------------------------------------------------------------------
# EXACT USER-SPECIFIED DIMENSIONS & CLEARANCES:
# ---------------------------------------------------------------------------
# Front plate: 2.0mm thick generally, but recessed to 1.0mm under LED pockets
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
WINDOW_SQ = 2.0             # mm (2x2mm square optical aperture through 1.0mm front skin)

print(f"Loaded {num_leds} LEDs from specs.")
print(f"Cross-section: 1.0mm LED floor -> 3.0mm pocket walls (Z=1.0 to 4.0mm) -> 2.0mm space to 6.0mm rim.")

# ---------------------------------------------------------------------------
# 1. LED COLLAR ROTATION ORIENTATION
# ---------------------------------------------------------------------------
# In Pete's Dragon Chris preset, all LEDs have 0 deg rotation (horizontal 10x5mm ovals).
# Orienting all collars horizontally (0 deg) prevents criss-crossing/squishing collisions!
led_rotations_deg = [0.0] * num_leds
print("Oriented all 100 LED collars horizontally (0 deg) matching Pete's Dragon Chris preset.")

# ---------------------------------------------------------------------------
# 2. GENERATE CLEAN DRAGON SILHOUETTE BOUNDARY & PERIMETER WALL
# ---------------------------------------------------------------------------
import cv2
from PIL import Image

dragon_img = Image.open('assets/petes_dragon_transparent.png')
img_w, img_h = dragon_img.size
WIDTH_MM = 185.0
aspect = img_w / img_h
HEIGHT_MM = round(WIDTH_MM / aspect, 2)

alpha = np.array(dragon_img)[:, :, 3]
mask = (alpha > 50).astype(np.uint8)
mask_dilated = cv2.dilate(mask, np.ones((17, 17), np.uint8), iterations=2)
contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
main_contour = max(contours, key=cv2.contourArea)
epsilon = 0.0022 * cv2.arcLength(main_contour, True)
approx_contour = cv2.approxPolyDP(main_contour, epsilon, True)

contour_pts = []
for pt in approx_contour:
    cx = round((pt[0][0] / img_w) * WIDTH_MM, 2)
    cy = round((1.0 - pt[0][1] / img_h) * HEIGHT_MM, 2)
    contour_pts.append((cx, cy))

orig_poly = sg.Polygon(contour_pts)
smoothed_plate_2d = orig_poly.buffer(4.0, resolution=16)
smoothed_plate_2d = smoothed_plate_2d.simplify(0.3, preserve_topology=True)

contour_coords = [[round(p[0], 2), round(p[1], 2)] for p in smoothed_plate_2d.exterior.coords]
bounds = smoothed_plate_2d.bounds
panel_w = round(bounds[2] - bounds[0], 2)
panel_h = round(bounds[3] - bounds[1], 2)
print(f"Outer boundary: {panel_w}mm W x {panel_h}mm H | {len(contour_coords)} vertices")

# 1. Base Front Plate: 2.0mm solid continuous front plate (Z = 0 to 2.0mm)
base_front_mesh = trimesh.creation.extrude_polygon(smoothed_plate_2d, height=FRONT_THICK_GENERAL)

# 2. Perimeter Wall Rim: 4.0mm tall outer wall from Z = 2.0 to 6.0mm
inner_plate_2d = smoothed_plate_2d.buffer(-RIM_WALL_THICK, resolution=16)
if inner_plate_2d.geom_type == 'MultiPolygon':
    inner_plate_2d = max(inner_plate_2d.geoms, key=lambda g: g.area)

rim_polygon_2d = sg.Polygon(smoothed_plate_2d.exterior.coords, [inner_plate_2d.exterior.coords])
rim_mesh = trimesh.creation.extrude_polygon(rim_polygon_2d, height=RIM_HEIGHT)
rim_mesh.apply_translation([0, 0, FRONT_THICK_GENERAL]) # Z = 2.0 to 6.0mm
print("Perimeter wall rim generated (4.0mm tall from Z=2.0 to 6.0mm).")

# ---------------------------------------------------------------------------
# 3. BACKSIDE PERIMETER FASTENER TABS (Inside rim wall, Z = 2.0 to 5.0mm)
# ---------------------------------------------------------------------------
boundary_line = smoothed_plate_2d.exterior
total_len = boundary_line.length
num_tabs = 16
tab_meshes = []
tab_coords = []

for k in range(num_tabs):
    dist_along = (k / float(num_tabs)) * total_len
    pt = boundary_line.interpolate(dist_along)
    pt_next = boundary_line.interpolate(min(total_len, dist_along + 1.0))
    tan = np.array([pt_next.x - pt.x, pt_next.y - pt.y])
    tan_norm = tan / (np.linalg.norm(tan) + 1e-6)
    normal = np.array([-tan_norm[1], tan_norm[0]])
    
    tab_center = np.array([pt.x, pt.y]) + normal * 4.0
    if not inner_plate_2d.contains(sg.Point(tab_center)):
        tab_center = np.array([pt.x, pt.y]) - normal * 4.0
        
    tab_coords.append([round(tab_center[0], 2), round(tab_center[1], 2)])
    
    tab_cyl = trimesh.creation.cylinder(radius=3.0, height=3.0, sections=16)
    tab_hole = trimesh.creation.cylinder(radius=1.25, height=3.4, sections=16)
    tab_solid = tab_cyl.difference(tab_hole)
    tab_solid.apply_translation([tab_center[0], tab_center[1], FRONT_THICK_GENERAL + 1.5])
    tab_meshes.append(tab_solid)

print("Generated 16 backside rim fastener ear tabs.")

# ---------------------------------------------------------------------------
# 4. 100 ROTATED OVAL LED COLLARS & 1mm RECESSED CAVITIES
# ---------------------------------------------------------------------------
def make_stadium_polygon(length, width, sections=16):
    r = width / 2.0
    c_len = max(0.0, length - width)
    pts = []
    for a in np.linspace(-np.pi/2, np.pi/2, sections):
        pts.append([c_len/2.0 + r * np.cos(a), r * np.sin(a)])
    for a in np.linspace(np.pi/2, 3*np.pi/2, sections):
        pts.append([-c_len/2.0 + r * np.cos(a), r * np.sin(a)])
    return sg.Polygon(pts)

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
    
    # A. 1.0mm Deep Floor Recess under the LED pocket (recesses Z from 2.0 down to 1.0mm)
    # Inside the 10x5mm inner cavity, so the front plate is 1.0mm thick!
    recess = trimesh.creation.extrude_polygon(inner_collar_2d, height=1.1)
    recess.apply_transform(rot)
    recess.apply_translation([cx, cy, FRONT_THICK_LED]) # Z = 1.0 to 2.1mm
    floor_recess_cutters.append(recess)
    
    # B. 3.0mm Tall Collar Wall rising from Z = 1.0 to Z = 4.0mm
    c_mesh = trimesh.creation.extrude_polygon(collar_ring_2d, height=COLLAR_HEIGHT)
    
    # Cut 4.0mm wide notches on both 5mm ends all the way down to Z = 1.0mm floor
    notch_r = trimesh.creation.box(extents=[3.5, NOTCH_WIDTH, COLLAR_HEIGHT + 0.2])
    notch_r.apply_translation([COLLAR_OUTER_L / 2.0 - 1.0, 0, COLLAR_HEIGHT / 2.0])
    
    notch_l = trimesh.creation.box(extents=[3.5, NOTCH_WIDTH, COLLAR_HEIGHT + 0.2])
    notch_l.apply_translation([-COLLAR_OUTER_L / 2.0 + 1.0, 0, COLLAR_HEIGHT / 2.0])
    
    notched_collar = c_mesh.difference(trimesh.boolean.union([notch_r, notch_l]))
    notched_collar.apply_transform(rot)
    notched_collar.apply_translation([cx, cy, COLLAR_FLOOR_Z]) # Z = 1.0 to 4.0mm!
    collar_meshes.append(notched_collar)
    
    # C. 2.0mm x 2.0mm Square Optical Window through the 1.0mm front skin (Z = -0.5 to 1.5mm)
    sq_win = trimesh.creation.box(extents=[WINDOW_SQ, WINDOW_SQ, FRONT_THICK_LED + 1.0])
    sq_win.apply_transform(rot)
    sq_win.apply_translation([cx, cy, FRONT_THICK_LED / 2.0])
    square_window_cutters.append(sq_win)

print(f"Generated {len(collar_meshes)} notched collars (Z=1.0 to 4.0mm) and {len(floor_recess_cutters)} 1mm recesses.")

# ---------------------------------------------------------------------------
# 5. CLEAR IMPRINTED DEBOSSED LED NUMBERS (1 to 100)
# ---------------------------------------------------------------------------
# Etched 0.6mm deep into the general tray floor (Z = 2.0 down to 1.4mm)
print("Generating clean debossed LED numbers 1 to 100 on interior floor...")
number_positions = []
number_cutters = []

for i, l in enumerate(leds):
    num_str = str(i + 1)
    p = np.array([l['x'], l['y']])
    
    # Collar is horizontal (12.4mm x 7.4mm outer envelope).
    # Search around collar (+Y above, -Y below, +X right, -X left, diagonals) for best clearance:
    best_cand = None
    max_d = -1
    candidates = [
        p + np.array([0.0, 5.5]),   # Above
        p + np.array([0.0, -5.5]),  # Below
        p + np.array([8.0, 0.0]),   # Right
        p + np.array([-8.0, 0.0]),  # Left
        p + np.array([6.5, 4.5]),   # Top-right
        p + np.array([-6.5, 4.5]),  # Top-left
        p + np.array([6.5, -4.5]),  # Bottom-right
        p + np.array([-6.5, -4.5]), # Bottom-left
    ]
    for cand in candidates:
        min_d = min(np.linalg.norm(cand - np.array([ol['x'], ol['y']])) for j, ol in enumerate(leds) if j != i)
        if min_d > max_d:
            max_d = min_d
            best_cand = cand
            
    number_positions.append([round(best_cand[0], 2), round(best_cand[1], 2)])
    
    # Multi-digit text path extraction
    tp = TextPath((0, 0), num_str, size=2.8)
    polys = tp.to_polygons()
    
    sg_polys = [sg.Polygon(p_ring) for p_ring in polys if len(p_ring) >= 3]
    shells = []
    holes = []
    for sp in sg_polys:
        is_hole = False
        for other in sg_polys:
            if other != sp and other.contains(sp):
                is_hole = True
                break
        if is_hole:
            holes.append(sp)
        else:
            shells.append(sp)
            
    digit_meshes = []
    for shell in shells:
        interior_holes = [h.exterior.coords for h in holes if shell.contains(h)]
        final_poly = sg.Polygon(shell.exterior.coords, holes=interior_holes)
        try:
            m = trimesh.creation.extrude_polygon(final_poly, height=0.8)
            digit_meshes.append(m)
        except Exception as e:
            pass
            
    if digit_meshes:
        # Concatenate ALL digits of this number string into a SINGLE combined mesh!
        # Do NOT center digits individually — that was what placed '1' and '0' on top of each other!
        num_combined = trimesh.util.concatenate(digit_meshes)
        tx_mid = (num_combined.bounds[0][:2] + num_combined.bounds[1][:2]) / 2.0
        num_combined.apply_translation([-tx_mid[0], -tx_mid[1], 1.4]) # Z from 1.4 to 2.2mm
        num_combined.apply_translation([best_cand[0], best_cand[1], 0.0])
        number_cutters.append(num_combined)

print(f"Generated {len(number_cutters)} clean multi-digit number glyph cutters.")

# ---------------------------------------------------------------------------
# 6. ASSEMBLE FULL CHASSIS AND PERFORM CSG BOOLEAN OPERATIONS
# ---------------------------------------------------------------------------
print("Assembling solid plate, rim, tabs, and collars...")
all_solids = [base_front_mesh, rim_mesh] + tab_meshes + collar_meshes
assembled_body = trimesh.boolean.union(all_solids)

all_cutters = floor_recess_cutters + square_window_cutters + number_cutters
print(f"Subtracting {len(all_cutters)} floor recesses, windows & number cutters...")
cutter_union = trimesh.boolean.union(all_cutters)

final_model = assembled_body.difference(cutter_union)

# Manifold3D topology validation pass to ensure 100% watertight binary STL
try:
    from manifold3d import Manifold, Mesh
    v_arr = np.ascontiguousarray(final_model.vertices, dtype=np.float32)
    f_arr = np.ascontiguousarray(final_model.faces, dtype=np.uint32)
    m = Manifold(Mesh(vert_properties=v_arr, tri_verts=f_arr))
    out_m = m.to_mesh()
    final_model = trimesh.Trimesh(vertices=out_m.vert_properties[:, :3], faces=out_m.tri_verts)
    print("Manifold3D mesh cleanup pass applied successfully.")
except Exception as e:
    print(f"Manifold3D cleanup pass skipped: {e}")

stl_path = '3d_panels/petes_dragon_tpu_panel.stl'
final_model.export(stl_path)
print("=" * 70)
print(f"SUCCESS! Wrote open chassis STL in {time.time()-t0:.2f}s")
print(f"File size: {os.path.getsize(stl_path)} bytes")
print(f"Watertight: {final_model.is_watertight} | Volume: {final_model.volume:.1f} mm3")
print(f"Dimensions: {final_model.bounds[1] - final_model.bounds[0]}")
print("=" * 70)

# ---------------------------------------------------------------------------
# 7. UPDATE MECHANICAL SPECIFICATIONS JSON
# ---------------------------------------------------------------------------
specs['panel_thickness_mm'] = TOTAL_THICK
specs['front_skin_thickness_general_mm'] = FRONT_THICK_GENERAL
specs['front_skin_thickness_led_mm'] = FRONT_THICK_LED
specs['perimeter_wall_height_mm'] = RIM_HEIGHT
specs['perimeter_wall_thickness_mm'] = RIM_WALL_THICK
specs['collar_floor_z_mm'] = COLLAR_FLOOR_Z
specs['led_collar_height_mm'] = COLLAR_HEIGHT
specs['collar_top_z_mm'] = COLLAR_TOP_Z
specs['table_clearance_space_mm'] = TOTAL_THICK - COLLAR_TOP_Z # Exactly 2.0mm!
specs['led_collar_inner_length_mm'] = COLLAR_INNER_L
specs['led_collar_inner_width_mm'] = COLLAR_INNER_W
specs['led_window_square_mm'] = WINDOW_SQ
specs['notch_width_mm'] = NOTCH_WIDTH
specs['led_rotations_deg'] = [round(a, 1) for a in led_rotations_deg]
specs['fastener_tabs'] = tab_coords
specs['number_positions'] = number_positions
specs['contour_pts'] = contour_coords
specs['panel_width_mm'] = panel_w
specs['panel_height_mm'] = panel_h

with open(specs_path, 'w') as f:
    json.dump(specs, f, indent=2)
print("Updated 3d_panels/petes_dragon_specs.json successfully!")
