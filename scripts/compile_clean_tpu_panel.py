import json, math, time, os
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
import trimesh

print("=" * 70)
print("ANTIGRAVITY IMAGINEERING - CLEAN 3D TPU CHEST PANEL COMPILER v2")
print("=" * 70)
t0 = time.time()

specs_path = '3d_panels/petes_dragon_specs.json'
with open(specs_path) as f:
    specs = json.load(f)

leds = specs['ordered_leds']
num_leds = len(leds)
PANEL_THICK = 5.5 # mm

print(f"Loaded {num_leds} LEDs from specs.")

# 1. GENERATE CLEAN, CONTINUOUS SOLID PLATE BOUNDARY
orig_contour = sg.Polygon(specs['contour_pts'])
led_pts = [sg.Point(l['x'], l['y']) for l in leds]
wire_lines = [sg.LineString([s[0], s[1]]) for s in specs['wire_segments']]

led_pads = [p.buffer(9.5, resolution=16) for p in led_pts]
wire_pads = [w.buffer(6.5, resolution=16) for w in wire_lines]

# Union contour with pads
combined_area = unary_union([orig_contour.buffer(6.0, resolution=16)] + led_pads + wire_pads)
solid_plate_2d = sg.Polygon(combined_area.exterior.coords)

# Smooth with morphological dilation/erosion with high resolution
smoothed_plate_2d = solid_plate_2d.buffer(3.5, resolution=16).buffer(-3.5, resolution=16)
smoothed_plate_2d = smoothed_plate_2d.simplify(0.4, preserve_topology=True)

contour_coords = [[round(p[0], 2), round(p[1], 2)] for p in smoothed_plate_2d.exterior.coords]
bounds = smoothed_plate_2d.bounds
panel_w = round(bounds[2] - bounds[0], 2)
panel_h = round(bounds[3] - bounds[1], 2)
print(f"Plate boundary: {panel_w}mm W x {panel_h}mm H | {len(contour_coords)} vertices")

# Extrude solid base plate (Z = 0 to 5.5mm)
base_mesh = trimesh.creation.extrude_polygon(smoothed_plate_2d, height=PANEL_THICK)

def make_oval(length, width, height, sections=16):
    radius = width / 2.0
    cyl_len = length - width
    if cyl_len <= 0.05:
        return trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    cyl1 = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    cyl1.apply_translation([-cyl_len/2.0, 0, 0])
    cyl2 = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    cyl2.apply_translation([cyl_len/2.0, 0, 0])
    box = trimesh.creation.box(extents=[cyl_len, width, height])
    return trimesh.boolean.union([cyl1, cyl2, box])

cutters = []

# 2. FRONT OPTICAL APERTURES (Through plate from Z=0 to Z=5.5)
# Oval 5.6mm x 3.2mm centered at each LED
for l in leds:
    win = make_oval(5.6, 3.2, PANEL_THICK + 2.0, sections=12)
    win.apply_translation([l['x'], l['y'], PANEL_THICK / 2.0])
    cutters.append(win)

# 3. REAR LED BULB POCKETS (10.5mm x 5.5mm x 2.8mm deep from back face Z=0)
for l in leds:
    pocket = make_oval(10.5, 5.5, 3.0, sections=16) # depth 3.0mm, extends from Z=-0.2 to 2.8
    pocket.apply_translation([l['x'], l['y'], 1.3])
    cutters.append(pocket)

# 4. ON-EDGE SLACK EXPANSION WELLS (dia 7.5mm x 4.5mm deep from back face Z=0)
expansion_wells = []
for i in range(len(leds)):
    l = leds[i]
    p_curr = np.array([l['x'], l['y']])
    if i < len(leds) - 1:
        p_next = np.array([leds[i+1]['x'], leds[i+1]['y']])
        diff = p_next - p_curr
        dist = np.linalg.norm(diff)
        u_dir = diff / dist if dist > 0.1 else np.array([1.0, 0.0])
    else:
        u_dir = np.array([1.0, 0.0])
    
    well_center = p_curr + u_dir * 4.2
    expansion_wells.append([round(well_center[0], 2), round(well_center[1], 2)])
    
    well = trimesh.creation.cylinder(radius=3.5, height=4.7, sections=16)
    well.apply_translation([well_center[0], well_center[1], 2.15]) # Z from -0.2 to 4.5
    cutters.append(well)
    
    # Wire notch
    slot_mid = p_curr + u_dir * 2.1
    angle = math.atan2(u_dir[1], u_dir[0])
    slot = trimesh.creation.box(extents=[4.5, 4.4, 4.7])
    rot = trimesh.transformations.rotation_matrix(angle, [0, 0, 1])
    slot.apply_transform(rot)
    slot.apply_translation([slot_mid[0], slot_mid[1], 2.15])
    cutters.append(slot)

# 5. CLEAR IMPRINTED DEBOSSED LED NUMBERS (1 to 100)
# Engraved 0.8mm deep into back face: cutter extends from Z = -0.2 to Z = 0.8mm!
print("Generating clean debossed LED numbers 1 to 100 (size 3.0mm, depth 0.8mm)...")
number_positions = []
for i, l in enumerate(leds):
    num_str = str(i + 1)
    p = np.array([l['x'], l['y']])
    
    best_cand = None
    max_d = -1
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = np.radians(angle)
        cand = p + np.array([np.cos(rad), np.sin(rad)]) * 6.5
        min_d = min(np.linalg.norm(cand - np.array([ol['x'], ol['y']])) for j, ol in enumerate(leds) if j != i)
        if min_d > max_d:
            max_d = min_d
            best_cand = cand
            
    number_positions.append([round(best_cand[0], 2), round(best_cand[1], 2)])
    
    tp = TextPath((0, 0), num_str, size=3.0)
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
            # Extrude 1.0mm thick, translate so it extends from Z = -0.2 to Z = 0.8
            m = trimesh.creation.extrude_polygon(final_poly, height=1.0)
            tx_mid = (m.bounds[0][:2] + m.bounds[1][:2]) / 2.0
            m.apply_translation([-tx_mid[0], -tx_mid[1], 0])
            m.apply_translation([best_cand[0], best_cand[1], 0.3]) # Z from -0.2 to 0.8!
            cutters.append(m)
        except Exception as e:
            pass

# 6. PERIMETER FASTENER EYELETS (16 along smooth boundary)
print("Generating 16 perimeter fastener eyelets...")
boundary_line = smoothed_plate_2d.exterior
total_len = boundary_line.length
num_tabs = 16
tab_coords = []
for k in range(num_tabs):
    dist_along = (k / float(num_tabs)) * total_len
    pt = boundary_line.interpolate(dist_along)
    pt_next = boundary_line.interpolate(min(total_len, dist_along + 1.0))
    tan = np.array([pt_next.x - pt.x, pt_next.y - pt.y])
    tan_norm = tan / (np.linalg.norm(tan) + 1e-6)
    normal = np.array([-tan_norm[1], tan_norm[0]])
    inset_pt = np.array([pt.x, pt.y]) + normal * 4.2
    if not smoothed_plate_2d.contains(sg.Point(inset_pt)):
        inset_pt = np.array([pt.x, pt.y]) - normal * 4.2
    
    tab_coords.append([round(inset_pt[0], 2), round(inset_pt[1], 2)])
    
    # 2.5mm through hole
    eyelet = trimesh.creation.cylinder(radius=1.25, height=PANEL_THICK + 2.0, sections=12)
    eyelet.apply_translation([inset_pt[0], inset_pt[1], PANEL_THICK / 2.0])
    cutters.append(eyelet)
    
    # 5.0mm countersink recess (1.0mm deep from front face Z=5.5)
    csk = trimesh.creation.cylinder(radius=2.5, height=1.2, sections=12)
    csk.apply_translation([inset_pt[0], inset_pt[1], PANEL_THICK - 0.5])
    cutters.append(csk)

# 7. PERFORM SOLID BOOLEAN CSG DIFFERENCE
print(f"Total cutters compiled: {len(cutters)}. Performing manifold CSG difference...")
cutter_union = trimesh.boolean.union(cutters)
final_model = base_mesh.difference(cutter_union)

stl_path = '3d_panels/petes_dragon_tpu_panel.stl'
final_model.export(stl_path)
print(f"Mesh compilation complete!")
print(f"Wrote {stl_path}: {os.path.getsize(stl_path)} bytes")
print(f"Watertight: {final_model.is_watertight} | Volume: {final_model.volume:.1f} mm3")
print(f"Dimensions: {final_model.bounds[1] - final_model.bounds[0]}")

# 8. UPDATE SPECS JSON FILE
specs['contour_pts'] = contour_coords
specs['panel_width_mm'] = panel_w
specs['panel_height_mm'] = panel_h
specs['fastener_tabs'] = tab_coords
specs['number_positions'] = number_positions
specs['expansion_wells'] = expansion_wells

with open(specs_path, 'w') as f:
    json.dump(specs, f, indent=2)
print("Updated 3d_panels/petes_dragon_specs.json successfully!")

print(f"All operations finished in {time.time()-t0:.2f}s!")
