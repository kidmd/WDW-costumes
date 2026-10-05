import json, math, time, os
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
import trimesh

print("=" * 70)
print("ANTIGRAVITY IMAGINEERING - OPEN CHASSIS TPU CHEST ARMOR TRAY COMPILER")
print("=" * 70)
t0 = time.time()

specs_path = '3d_panels/petes_dragon_specs.json'
with open(specs_path) as f:
    specs = json.load(f)

leds = specs['ordered_leds']
num_leds = len(leds)

# Dimensions per user specification
FRONT_THICK = 2.0        # mm (solid front plate from Z = 0 to 2.0)
RIM_HEIGHT = 4.0         # mm (perimeter wall from Z = 2.0 to 6.0)
TOTAL_THICK = 6.0        # mm (FRONT_THICK + RIM_HEIGHT)
RIM_WALL_THICK = 2.5     # mm (width of outer perimeter wall)

COLLAR_HEIGHT = 3.0      # mm (socket walls from Z = 2.0 to 5.0)
COLLAR_INNER_L = 10.0    # mm (10mm inner length)
COLLAR_INNER_W = 5.0     # mm (5mm inner width)
COLLAR_WALL_THICK = 1.2  # mm (outer dimensions: 12.4 x 7.4mm)
COLLAR_OUTER_L = COLLAR_INNER_L + 2 * COLLAR_WALL_THICK # 12.4mm
COLLAR_OUTER_W = COLLAR_INNER_W + 2 * COLLAR_WALL_THICK # 7.4mm

NOTCH_WIDTH = 4.0        # mm (wire pass-through slot on both 5mm ends)
WINDOW_SQ = 2.0          # mm (2x2mm square optical aperture through front)

print(f"Loaded {num_leds} LEDs from specs.")

# ---------------------------------------------------------------------------
# 1. COMPUTE SEQUENTIAL PATH TANGENT ROTATION FOR EACH LED
# ---------------------------------------------------------------------------
# theta_i points from LED i to LED i+1
led_rotations_deg = []
for i in range(num_leds):
    p_curr = np.array([leds[i]['x'], leds[i]['y']])
    if i < num_leds - 1:
        p_next = np.array([leds[i+1]['x'], leds[i+1]['y']])
        diff = p_next - p_curr
    else:
        p_prev = np.array([leds[i-1]['x'], leds[i-1]['y']])
        diff = p_curr - p_prev
    angle_rad = math.atan2(diff[1], diff[0])
    led_rotations_deg.append(math.degrees(angle_rad))

print("Computed tangent rotation angles for all 100 LEDs.")

# ---------------------------------------------------------------------------
# 2. GENERATE CONTINUOUS SMOOTH OUTER BOUNDARY & PERIMETER WALL
# ---------------------------------------------------------------------------
orig_contour = sg.Polygon(specs['contour_pts'])
led_pts = [sg.Point(l['x'], l['y']) for l in leds]
wire_lines = [sg.LineString([s[0], s[1]]) for s in specs['wire_segments']]

led_pads = [p.buffer(10.5, resolution=16) for p in led_pts]
wire_pads = [w.buffer(7.0, resolution=16) for w in wire_lines]

combined_area = unary_union([orig_contour.buffer(6.0, resolution=16)] + led_pads + wire_pads)
solid_plate_2d = sg.Polygon(combined_area.exterior.coords)

# Smooth with morphological dilation/erosion with high resolution
smoothed_plate_2d = solid_plate_2d.buffer(3.5, resolution=16).buffer(-3.5, resolution=16)
smoothed_plate_2d = smoothed_plate_2d.simplify(0.4, preserve_topology=True)

contour_coords = [[round(p[0], 2), round(p[1], 2)] for p in smoothed_plate_2d.exterior.coords]
bounds = smoothed_plate_2d.bounds
panel_w = round(bounds[2] - bounds[0], 2)
panel_h = round(bounds[3] - bounds[1], 2)
print(f"Outer boundary: {panel_w}mm W x {panel_h}mm H | {len(contour_coords)} vertices")

# 1. Base Plate: 2.0mm solid continuous front skin (Z = 0 to 2.0mm)
base_front_mesh = trimesh.creation.extrude_polygon(smoothed_plate_2d, height=FRONT_THICK)
# Positioned from Z = 0 to 2.0mm

# 2. Perimeter Wall Rim: 4.0mm tall outer wall from Z = 2.0 to 6.0mm
# Inset the inner border by RIM_WALL_THICK (2.5mm)
inner_plate_2d = smoothed_plate_2d.buffer(-RIM_WALL_THICK, resolution=16)
if inner_plate_2d.geom_type == 'MultiPolygon':
    inner_plate_2d = max(inner_plate_2d.geoms, key=lambda g: g.area)

rim_polygon_2d = sg.Polygon(smoothed_plate_2d.exterior.coords, [inner_plate_2d.exterior.coords])
rim_mesh = trimesh.creation.extrude_polygon(rim_polygon_2d, height=RIM_HEIGHT)
rim_mesh.apply_translation([0, 0, FRONT_THICK]) # Z = 2.0 to 6.0mm
print("Perimeter wall rim generated (4.0mm tall from Z=2.0 to 6.0mm).")

# ---------------------------------------------------------------------------
# 3. BACKSIDE PERIMETER FASTENER TABS (Connected to inside of edge wall)
# ---------------------------------------------------------------------------
# 16 eyelet ear tabs connected to the inside of the rim wall on the back side (Z = 2.0 to 5.0mm)
# Front face remains 100% solid and puncture-free!
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
    
    # Inset by 4.0mm from outer perimeter (sitting right against inside rim wall)
    tab_center = np.array([pt.x, pt.y]) + normal * 4.0
    if not inner_plate_2d.contains(sg.Point(tab_center)):
        tab_center = np.array([pt.x, pt.y]) - normal * 4.0
        
    tab_coords.append([round(tab_center[0], 2), round(tab_center[1], 2)])
    
    # Solid cylinder tab: OD = 6.0mm, height = 3.0mm (Z = 2.0 to 5.0mm)
    tab_cyl = trimesh.creation.cylinder(radius=3.0, height=3.0, sections=16)
    # Eyelet hole: ID = 2.5mm through the tab (Z = 1.9 to 5.1mm)
    tab_hole = trimesh.creation.cylinder(radius=1.25, height=3.4, sections=16)
    tab_solid = tab_cyl.difference(tab_hole)
    tab_solid.apply_translation([tab_center[0], tab_center[1], FRONT_THICK + 1.5])
    tab_meshes.append(tab_solid)

print("Generated 16 backside rim fastener ear tabs.")

# ---------------------------------------------------------------------------
# 4. 100 OVAL LED COLLARS WITH WIRE NOTCHES & 2x2mm WINDOWS
# ---------------------------------------------------------------------------
# Helper function to generate stadium/oval polygon
def make_stadium_polygon(length, width, sections=16):
    r = width / 2.0
    c_len = max(0.0, length - width)
    pts = []
    # Right semi-circle
    for a in np.linspace(-np.pi/2, np.pi/2, sections):
        pts.append([c_len/2.0 + r * np.cos(a), r * np.sin(a)])
    # Left semi-circle
    for a in np.linspace(np.pi/2, 3*np.pi/2, sections):
        pts.append([-c_len/2.0 + r * np.cos(a), r * np.sin(a)])
    return sg.Polygon(pts)

outer_collar_2d = make_stadium_polygon(COLLAR_OUTER_L, COLLAR_OUTER_W, sections=16)
inner_collar_2d = make_stadium_polygon(COLLAR_INNER_L, COLLAR_INNER_W, sections=16)
collar_ring_2d = sg.Polygon(outer_collar_2d.exterior.coords, [inner_collar_2d.exterior.coords])

collar_meshes = []
square_window_cutters = []

for i in range(num_leds):
    l = leds[i]
    cx, cy = l['x'], l['y']
    angle_deg = led_rotations_deg[i]
    rad = math.radians(angle_deg)
    
    # 1. Extrude collar ring (Z = 2.0 to 5.0mm, height = 3.0mm)
    c_mesh = trimesh.creation.extrude_polygon(collar_ring_2d, height=COLLAR_HEIGHT)
    
    # 2. Cut 4.0mm wide wire notches on both 5mm ends down to the floor (Z = 2.0 to 5.0)
    # Notch length 3.5mm, width 4.0mm, height 3.2mm at both ends along X axis
    notch_r = trimesh.creation.box(extents=[3.5, NOTCH_WIDTH, COLLAR_HEIGHT + 0.2])
    notch_r.apply_translation([COLLAR_OUTER_L / 2.0 - 1.0, 0, COLLAR_HEIGHT / 2.0])
    
    notch_l = trimesh.creation.box(extents=[3.5, NOTCH_WIDTH, COLLAR_HEIGHT + 0.2])
    notch_l.apply_translation([-COLLAR_OUTER_L / 2.0 + 1.0, 0, COLLAR_HEIGHT / 2.0])
    
    notched_collar = c_mesh.difference(trimesh.boolean.union([notch_r, notch_l]))
    
    # Rotate collar by path tangent angle
    rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
    notched_collar.apply_transform(rot)
    notched_collar.apply_translation([cx, cy, FRONT_THICK]) # Z = 2.0 to 5.0mm
    collar_meshes.append(notched_collar)
    
    # 3. 2.0mm x 2.0mm square optical window through the 2.0mm front face (Z = -0.5 to 2.5mm)
    sq_win = trimesh.creation.box(extents=[WINDOW_SQ, WINDOW_SQ, FRONT_THICK + 1.0])
    sq_win.apply_transform(rot) # Align with bulb orientation
    sq_win.apply_translation([cx, cy, FRONT_THICK / 2.0])
    square_window_cutters.append(sq_win)

print(f"Generated {len(collar_meshes)} notched oval collars and {len(square_window_cutters)} square windows.")

# ---------------------------------------------------------------------------
# 5. CLEAR IMPRINTED DEBOSSED LED NUMBERS (1 to 100)
# ---------------------------------------------------------------------------
# Etched 0.6mm deep into the inner floor (from Z = 2.0 down to 1.4mm)
print("Generating clean debossed LED numbers 1 to 100 on interior floor...")
number_positions = []
number_cutters = []

for i, l in enumerate(leds):
    num_str = str(i + 1)
    p = np.array([l['x'], l['y']])
    
    # Find best direction perpendicular to LED orientation with maximum clearance
    best_cand = None
    max_d = -1
    angle_rad = math.radians(led_rotations_deg[i])
    # Perpendicular angles
    for perp_offset in [np.pi/2, -np.pi/2, np.pi/4, -np.pi/4, 3*np.pi/4, -3*np.pi/4]:
        cand_angle = angle_rad + perp_offset
        cand = p + np.array([np.cos(cand_angle), np.sin(cand_angle)]) * 6.5
        min_d = min(np.linalg.norm(cand - np.array([ol['x'], ol['y']])) for j, ol in enumerate(leds) if j != i)
        if min_d > max_d:
            max_d = min_d
            best_cand = cand
            
    number_positions.append([round(best_cand[0], 2), round(best_cand[1], 2)])
    
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
            
    for shell in shells:
        interior_holes = [h.exterior.coords for h in holes if shell.contains(h)]
        final_poly = sg.Polygon(shell.exterior.coords, holes=interior_holes)
        try:
            # Extrude 0.8mm thick, translate to cut 0.6mm into the floor at Z = 2.0mm
            # Z range: 1.4mm to 2.2mm
            m = trimesh.creation.extrude_polygon(final_poly, height=0.8)
            tx_mid = (m.bounds[0][:2] + m.bounds[1][:2]) / 2.0
            m.apply_translation([-tx_mid[0], -tx_mid[1], 0])
            m.apply_translation([best_cand[0], best_cand[1], 1.4]) # Z from 1.4 to 2.2mm
            number_cutters.append(m)
        except Exception as e:
            pass

print(f"Generated {len(number_cutters)} number glyph cutters.")

# ---------------------------------------------------------------------------
# 6. ASSEMBLE FULL CHASSIS AND PERFORM CSG DIFFERENCE
# ---------------------------------------------------------------------------
print("Assembling solid plate, rim, tabs, and collars...")
# Union solid components: base front plate + perimeter rim + tabs + collars
all_solids = [base_front_mesh, rim_mesh] + tab_meshes + collar_meshes
assembled_body = trimesh.boolean.union(all_solids)

# Subtract 2x2mm square windows and floor debossed numbers
all_cutters = square_window_cutters + number_cutters
print(f"Subtracting {len(all_cutters)} window & number cutters...")
cutter_union = trimesh.boolean.union(all_cutters)

final_model = assembled_body.difference(cutter_union)

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
specs['front_skin_thickness_mm'] = FRONT_THICK
specs['perimeter_wall_height_mm'] = RIM_HEIGHT
specs['perimeter_wall_thickness_mm'] = RIM_WALL_THICK
specs['led_collar_height_mm'] = COLLAR_HEIGHT
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

# Remove obsolete channel/slack well keys
specs.pop('expansion_wells', None)
specs.pop('wire_channels', None)

with open(specs_path, 'w') as f:
    json.dump(specs, f, indent=2)
print("Updated 3d_panels/petes_dragon_specs.json successfully!")
