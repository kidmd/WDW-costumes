import os
import sys
import numpy as np
import trimesh
import manifold3d as m3d
from manifold3d import Manifold

os.makedirs("3d_panels/wire_clips", exist_ok=True)

# ==============================================================================
# PARAMETRIC CONSTANTS FOR RIGID PLA / PETG WIRE CLIPS
# Resized for standard ~3.2mm fairy light wiring (calibrated with test comb)
# ==============================================================================
WIRE_DIAMETER = 3.20     # Calibrated wire OD (mm)
CAVITY_RADIUS = 1.65     # Inner pocket radius (3.30mm dia for smooth wire glide without pinch)
WALL_THICKNESS = 1.35    # Flex cantilever spring wall thickness (~3-4 perimeters on 0.4mm nozzle)
FLOOR_THICKNESS = 1.20   # Bottom chassis thickness resting flat against shirt/build plate
NECK_OPENING = 2.35      # Snap constriction mouth width (gives positive snap click without stress-whitening)
CLIP_LENGTH = 8.00       # Extrusion length along wire path (mm)


def to_flat_trimesh(profile: m3d.CrossSection, length: float = CLIP_LENGTH) -> trimesh.Trimesh:
    """Extrudes a 2D profile along Z and rotates +90 deg around X so the flat base sits at Z=0 and mouths point UP."""
    m = profile.extrude(length)
    raw = m.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)
    # Rotate +90 deg around X so base (Y=0) lies flat on build plate at Z=0, mouth (Y>0) points UP (+Z)
    rot = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
    mesh.apply_transform(rot)
    # Center bounds in X and align to Y=0, Z=0
    bounds = mesh.bounds
    mesh.apply_translation([
        -bounds[0][0] - (bounds[1][0] - bounds[0][0]) / 2.0,
        -bounds[0][1],
        -bounds[0][2]
    ])
    return mesh


def export_trimesh(mesh: trimesh.Trimesh, filename: str):
    mesh.export(filename)
    ext = mesh.bounds[1] - mesh.bounds[0]
    print(f"Exported: {filename} ({len(mesh.faces)} faces, {ext[0]:.2f}W x {ext[1]:.2f}L x {ext[2]:.2f}H mm, {mesh.volume:.1f} mm³)")


# ==============================================================================
# 1. 2-STRAND FLAT PARALLEL CLIP (3.2mm)
# Holds 2 strands side-by-side, ultra low-profile (flush against chest/shirt)
# ==============================================================================
def create_clip_2strand_flat(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    spacing = 2 * r_cav + WALL_THICKNESS
    w_total = 2 * (spacing / 2.0 + r_cav + WALL_THICKNESS)
    y_cen = FLOOR_THICKNESS + r_cav
    h_total = y_cen + r_cav + 0.70

    pts_body = [
        [-w_total / 2.0, 0.0],
        [-w_total / 2.0, h_total - 0.8],
        [-w_total / 2.0 + 0.8, h_total],
        [w_total / 2.0 - 0.8, h_total],
        [w_total / 2.0, h_total - 0.8],
        [w_total / 2.0, 0.0]
    ]
    body = m3d.CrossSection.hull_points(pts_body)

    cuts = []
    for xc in [-spacing / 2.0, spacing / 2.0]:
        circ = m3d.CrossSection.circle(r_cav, 32).translate([xc, y_cen])
        y_neck = y_cen + 1.05
        hw_neck = NECK_OPENING / 2.0
        hw_top = hw_neck + (h_total - y_neck) * 1.1
        pts_entry = [
            [xc - hw_neck, y_cen],
            [xc - hw_neck, y_neck],
            [xc - hw_top, h_total + 0.2],
            [xc + hw_top, h_total + 0.2],
            [xc + hw_neck, y_neck],
            [xc + hw_neck, y_cen]
        ]
        slot = m3d.CrossSection.hull_points(pts_entry)
        cuts.append(circ + slot)

    profile = body - (cuts[0] + cuts[1])
    return to_flat_trimesh(profile, length)


# ==============================================================================
# 2. 3-STRAND FLAT PARALLEL CLIP (3.2mm)
# Holds 3 strands side-by-side in individual snap bays (for flat folds / accordions)
# ==============================================================================
def create_clip_3strand_flat(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    spacing = 2 * r_cav + WALL_THICKNESS
    w_total = 2 * (spacing + r_cav + WALL_THICKNESS)
    y_cen = FLOOR_THICKNESS + r_cav
    h_total = y_cen + r_cav + 0.70

    pts_body = [
        [-w_total / 2.0, 0.0],
        [-w_total / 2.0, h_total - 0.8],
        [-w_total / 2.0 + 0.8, h_total],
        [w_total / 2.0 - 0.8, h_total],
        [w_total / 2.0, h_total - 0.8],
        [w_total / 2.0, 0.0]
    ]
    body = m3d.CrossSection.hull_points(pts_body)

    cuts = []
    for xc in [-spacing, 0.0, spacing]:
        circ = m3d.CrossSection.circle(r_cav, 32).translate([xc, y_cen])
        y_neck = y_cen + 1.05
        hw_neck = NECK_OPENING / 2.0
        hw_top = hw_neck + (h_total - y_neck) * 1.1
        pts_entry = [
            [xc - hw_neck, y_cen],
            [xc - hw_neck, y_neck],
            [xc - hw_top, h_total + 0.2],
            [xc + hw_top, h_total + 0.2],
            [xc + hw_neck, y_neck],
            [xc + hw_neck, y_cen]
        ]
        slot = m3d.CrossSection.hull_points(pts_entry)
        cuts.append(circ + slot)

    profile = body - (cuts[0] + cuts[1] + cuts[2])
    return to_flat_trimesh(profile, length)


# ==============================================================================
# 3. 2-STRAND STACKED VERTICAL CLIP (3.2mm)
# Holds 2 strands stacked vertically over-under. Narrowest lateral footprint (6.0mm)!
# ==============================================================================
def create_clip_2strand_stacked(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    y1 = FLOOR_THICKNESS + r_cav
    y2 = y1 + 2 * r_cav + 0.20
    y_waist = (y1 + y2) / 2.0
    y_neck = y2 + 1.05
    h_total = y2 + r_cav + 0.80
    w_total = 2 * (r_cav + WALL_THICKNESS)

    pts_body = [
        [-w_total / 2.0, 0.0],
        [-w_total / 2.0, h_total - 0.8],
        [-w_total / 2.0 + 0.8, h_total],
        [w_total / 2.0 - 0.8, h_total],
        [w_total / 2.0, h_total - 0.8],
        [w_total / 2.0, 0.0]
    ]
    body = m3d.CrossSection.hull_points(pts_body)

    c1 = m3d.CrossSection.circle(r_cav, 32).translate([0, y1])
    c2 = m3d.CrossSection.circle(r_cav, 32).translate([0, y2])
    waist = m3d.CrossSection.square([2.40, y2 - y1], center=True).translate([0, y_waist])

    hw_neck = NECK_OPENING / 2.0
    hw_top = hw_neck + (h_total - y_neck) * 1.1
    pts_top = [
        [-hw_neck, y2],
        [-hw_neck, y_neck],
        [-hw_top, h_total + 0.2],
        [hw_top, h_total + 0.2],
        [hw_neck, y_neck],
        [hw_neck, y2]
    ]
    top_slot = m3d.CrossSection.hull_points(pts_top)

    profile = body - (c1 + c2 + waist + top_slot)
    return to_flat_trimesh(profile, length)


# ==============================================================================
# 4. 3-STRAND PYRAMID BUNDLE CLIP (3.2mm)
# Holds 3 strands in a compact triangular cluster (2 bottom, 1 top locked)
# ==============================================================================
def create_clip_3strand_bundle(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    x1, y1 = -1.85, FLOOR_THICKNESS + r_cav
    x2, y2 = 1.85, FLOOR_THICKNESS + r_cav
    x3, y3 = 0.0, y1 + 2.85
    h_total = y3 + r_cav + 0.90
    w_bot = 2 * (1.85 + r_cav + WALL_THICKNESS)
    w_top = 2 * (r_cav + WALL_THICKNESS)

    pts_body = [
        [-w_bot / 2.0, 0.0],
        [-w_bot / 2.0, y1 + 0.6],
        [-w_top / 2.0, h_total - 0.8],
        [-w_top / 2.0 + 0.8, h_total],
        [w_top / 2.0 - 0.8, h_total],
        [w_top / 2.0, h_total - 0.8],
        [w_bot / 2.0, y1 + 0.6],
        [w_bot / 2.0, 0.0]
    ]
    body = m3d.CrossSection.hull_points(pts_body)

    c1 = m3d.CrossSection.circle(r_cav, 32).translate([x1, y1])
    c2 = m3d.CrossSection.circle(r_cav, 32).translate([x2, y2])
    c3 = m3d.CrossSection.circle(r_cav, 32).translate([x3, y3])
    throat = m3d.CrossSection.square([NECK_OPENING, y3 - y1], center=True).translate([0, (y1 + y3) / 2.0])

    y_neck = y3 + 1.05
    hw_neck = NECK_OPENING / 2.0
    hw_top = hw_neck + (h_total - y_neck) * 1.1
    pts_top = [
        [-hw_neck, y3],
        [-hw_neck, y_neck],
        [-hw_top, h_total + 0.2],
        [hw_top, h_total + 0.2],
        [hw_neck, y_neck],
        [hw_neck, y3]
    ]
    top_slot = m3d.CrossSection.hull_points(pts_top)
    divider = m3d.CrossSection.circle(0.50, 16).translate([0, FLOOR_THICKNESS + 0.35])

    cutout = (c1 + c2 + c3 + throat + top_slot) - divider
    profile = body - cutout
    return to_flat_trimesh(profile, length)


# ==============================================================================
# 5. PRESERVED 2-STRAND PYRAMID CRADLE (v1 Geometry for 2 Wires)
# User tested and verified: cradles 2 wires snugly in the lower lobes!
# ==============================================================================
def create_clip_2strand_pyramid_cradle(length=CLIP_LENGTH) -> trimesh.Trimesh:
    # Exact v1 parameters
    wire_d = 2.30
    r_cav = 1.20
    wall = 1.25
    floor = 1.10
    neck_w = 1.65

    x1, y1 = -1.35, floor + r_cav
    x2, y2 = 1.35, floor + r_cav
    x3, y3 = 0.0, y1 + 2.05
    h_total = y3 + r_cav + 0.80
    w_bot = 2 * (1.35 + r_cav + wall)
    w_top = 2 * (r_cav + wall)

    pts_body = [
        [-w_bot / 2.0, 0.0],
        [-w_bot / 2.0, y1 + 0.5],
        [-w_top / 2.0, h_total - 0.6],
        [-w_top / 2.0 + 0.6, h_total],
        [w_top / 2.0 - 0.6, h_total],
        [w_top / 2.0, h_total - 0.6],
        [w_bot / 2.0, y1 + 0.5],
        [w_bot / 2.0, 0.0]
    ]
    body = m3d.CrossSection.hull_points(pts_body)

    c1 = m3d.CrossSection.circle(r_cav, 32).translate([x1, y1])
    c2 = m3d.CrossSection.circle(r_cav, 32).translate([x2, y2])
    c3 = m3d.CrossSection.circle(r_cav, 32).translate([x3, y3])
    throat = m3d.CrossSection.square([neck_w, y3 - y1], center=True).translate([0, (y1 + y3) / 2.0])

    y_neck = y3 + 0.85
    hw_neck = neck_w / 2.0
    hw_top = hw_neck + (h_total - y_neck) * 1.1
    pts_top = [
        [-hw_neck, y3],
        [-hw_neck, y_neck],
        [-hw_top, h_total + 0.2],
        [hw_top, h_total + 0.2],
        [hw_neck, y_neck],
        [hw_neck, y3]
    ]
    top_slot = m3d.CrossSection.hull_points(pts_top)
    divider = m3d.CrossSection.circle(0.40, 16).translate([0, floor + 0.25])

    cutout = (c1 + c2 + c3 + throat + top_slot) - divider
    profile = body - cutout
    return to_flat_trimesh(profile, length)


# ==============================================================================
# 6. 90-DEGREE SINGLE-WIRE CORNER ELBOW BRACKETS (3.2mm)
# Holds 1 wire around a gentle 90° bend (5mm inner bend radius)
# ==============================================================================
def create_single_wire_channel_profile(r_inner=4.0, r_outer=10.0, height=5.0):
    """Creates a radial cross-section for revolving around Y-axis."""
    sq = m3d.CrossSection.square([r_outer - r_inner, height], center=False).translate([r_inner, 0.0])
    r_cen = (r_inner + r_outer) / 2.0  # 7.0mm
    y_cen = FLOOR_THICKNESS + CAVITY_RADIUS
    c = m3d.CrossSection.circle(CAVITY_RADIUS, 32).translate([r_cen, y_cen])
    y_neck = y_cen + 1.05
    hw_neck = NECK_OPENING / 2.0
    hw_top = hw_neck + (height - y_neck) * 1.1
    pts_top = [
        [r_cen - hw_neck, y_cen],
        [r_cen - hw_neck, y_neck],
        [r_cen - hw_top, height + 0.2],
        [r_cen + hw_top, height + 0.2],
        [r_cen + hw_neck, y_neck],
        [r_cen + hw_neck, y_cen]
    ]
    slot = m3d.CrossSection.hull_points(pts_top)
    return sq - (c + slot)


def create_corner_90_single(leg_len=2.5) -> trimesh.Trimesh:
    """90-degree curved elbow bracket for single wire (floating)."""
    r_in = 4.0
    r_out = 10.0
    h = 5.0
    prof = create_single_wire_channel_profile(r_in, r_out, h)
    
    # 90-degree curved elbow
    bend = prof.revolve(circular_segments=48, revolve_degrees=90.0)
    mesh_bend = trimesh.Trimesh(vertices=bend.to_mesh().vert_properties, faces=bend.to_mesh().tri_verts)

    # Leg 1 extending along -Y
    raw1 = prof.extrude(leg_len).to_mesh()
    mesh_leg1 = trimesh.Trimesh(vertices=raw1.vert_properties, faces=raw1.tri_verts)
    rot1 = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
    mesh_leg1.apply_transform(rot1)

    # Leg 2 extending along -X (swap X and Y, invert faces)
    mesh_leg2 = mesh_leg1.copy()
    v = mesh_leg2.vertices.copy()
    mesh_leg2.vertices[:, 0] = v[:, 1]
    mesh_leg2.vertices[:, 1] = v[:, 0]
    mesh_leg2.faces = mesh_leg2.faces[:, [0, 2, 1]]

    full = trimesh.boolean.union([mesh_bend, mesh_leg1, mesh_leg2], engine='manifold')
    # Center bounds in XY and place Z at 0
    full.apply_translation([
        -full.bounds[0][0] - (full.bounds[1][0] - full.bounds[0][0]) / 2.0,
        -full.bounds[0][1] - (full.bounds[1][1] - full.bounds[0][1]) / 2.0,
        -full.bounds[0][2]
    ])
    return full


def create_corner_90_sewable(leg_len=2.5) -> trimesh.Trimesh:
    """90-degree curved elbow bracket with corner stitching eyelet tabs."""
    elbow = create_corner_90_single(leg_len)
    
    # Add 2 flat sewing tabs on the outer corner flank
    # Tab 1: near leg 1 outer flank
    # Tab 2: near leg 2 outer flank
    bounds = elbow.bounds
    tab_r_out = 2.6
    tab_r_in = 0.95  # 1.9mm hole for needle/safety-pin
    tab_thick = 1.20
    
    tab_cs = m3d.CrossSection.circle(tab_r_out, 24) - m3d.CrossSection.circle(tab_r_in, 24)
    m_tab = tab_cs.extrude(tab_thick)
    raw_tab = m_tab.to_mesh()
    mesh_tab1 = trimesh.Trimesh(vertices=raw_tab.vert_properties, faces=raw_tab.tri_verts)
    
    # Position tab 1 at outer flank of leg 1
    mesh_tab1.apply_translation([bounds[1][0] - 0.5, bounds[0][1] + 2.0, 0.0])
    
    # Tab 2 at outer flank of leg 2
    mesh_tab2 = trimesh.Trimesh(vertices=raw_tab.vert_properties, faces=raw_tab.tri_verts)
    mesh_tab2.apply_translation([bounds[0][0] + 2.0, bounds[1][1] - 0.5, 0.0])
    
    combined = trimesh.boolean.union([elbow, mesh_tab1, mesh_tab2], engine='manifold')
    combined.apply_translation([
        -combined.bounds[0][0] - (combined.bounds[1][0] - combined.bounds[0][0]) / 2.0,
        -combined.bounds[0][1] - (combined.bounds[1][1] - combined.bounds[0][1]) / 2.0,
        -combined.bounds[0][2]
    ])
    return combined


# ==============================================================================
# 7. TEST GAUGE COMB (3-MINUTE QUICK PRINT)
# 5 stepped test slots (2.6, 2.8, 3.0, 3.2, 3.4 mm) to find the perfect snap fit
# ==============================================================================
def create_test_gauge_comb(length: float = 6.00) -> trimesh.Trimesh:
    diameters = [2.6, 2.8, 3.0, 3.2, 3.4]
    slot_spacing = 7.0
    w_total = (len(diameters) - 1) * slot_spacing + 2 * (1.75 + 1.30) + 2.0
    h_total = 5.3
    floor = 1.2

    body = m3d.CrossSection.square([w_total, h_total], center=False).translate([-w_total / 2.0, 0.0])

    cuts = []
    x_start = - (len(diameters) - 1) * slot_spacing / 2.0
    for i, d in enumerate(diameters):
        xc = x_start + i * slot_spacing
        r_cav = d / 2.0 + 0.05
        neck_w = d * 0.73
        y_cen = floor + r_cav
        c = m3d.CrossSection.circle(r_cav, 32).translate([xc, y_cen])
        y_neck = y_cen + (d * 0.32)
        hw_n = neck_w / 2.0
        hw_t = hw_n + (h_total - y_neck) * 1.1
        s = m3d.CrossSection.hull_points([
            [xc - hw_n, y_cen], [xc - hw_n, y_neck], [xc - hw_t, h_total + 0.2],
            [xc + hw_t, h_total + 0.2], [xc + hw_n, y_neck], [xc + hw_n, y_cen]
        ])
        cuts.append(c + s)

    cut_all = cuts[0]
    for c in cuts[1:]:
        cut_all = cut_all + c

    profile = body - cut_all
    mesh = to_flat_trimesh(profile, length)
    return mesh


# ==============================================================================
# 8. MULTI-PACK RUNNER PRINT BED
# 4x of each straight clip + 4x 2-strand cradle + 2x floating corner + 2x sewable corner + test comb
# ==============================================================================
def create_runner_multipack() -> trimesh.Trimesh:
    c2_flat = create_clip_2strand_flat()
    c3_flat = create_clip_3strand_flat()
    c2_stack = create_clip_2strand_stacked()
    c3_bund = create_clip_3strand_bundle()
    c2_cradle = create_clip_2strand_pyramid_cradle()
    c90_single = create_corner_90_single()
    c90_sew = create_corner_90_sewable()
    comb = create_test_gauge_comb()

    # Straight 4x rows
    straight_models = [c2_flat, c3_flat, c2_stack, c3_bund, c2_cradle]
    row_y = [0.0, 14.0, 28.0, 42.0, 56.0]
    col_x_offsets = [
        [-25.5, -8.5, 8.5, 25.5],  # 2-strand flat (10.1mm wide)
        [-31.5, -10.5, 10.5, 31.5],# 3-strand flat (14.5mm wide)
        [-22.5, -7.5, 7.5, 22.5],  # 2-strand stacked (5.7mm wide)
        [-25.5, -8.5, 8.5, 25.5],  # 3-strand bundle (9.2mm wide)
        [-24.0, -8.0, 8.0, 24.0]   # 2-strand pyramid cradle (7.6mm wide)
    ]

    pack_parts = []
    for r_idx, (model, y_pos) in enumerate(zip(straight_models, row_y)):
        for x_pos in col_x_offsets[r_idx]:
            inst = model.copy()
            inst.apply_translation([x_pos, y_pos, 0.0])
            pack_parts.append(inst)

    # Row 5 (Y=72): 2x Floating 90 Corner + 2x Sewable 90 Corner
    corner_models = [c90_single, c90_single, c90_sew, c90_sew]
    corner_xs = [-26.0, -9.0, 9.0, 26.0]
    for m, x in zip(corner_models, corner_xs):
        inst = m.copy()
        inst.apply_translation([x, 72.0, 0.0])
        pack_parts.append(inst)

    # Row 6 (Y=88): 1x Test Gauge Comb centered
    comb_inst = comb.copy()
    comb_inst.apply_translation([0.0, 88.0, 0.0])
    pack_parts.append(comb_inst)

    combined = trimesh.util.concatenate(pack_parts)
    # Ensure entire bed array is centered in XY and resting at Z=0
    bounds = combined.bounds
    combined.apply_translation([
        -bounds[0][0] - (bounds[1][0] - bounds[0][0]) / 2.0,
        -bounds[0][1],
        -bounds[0][2]
    ])
    return combined


# ==============================================================================
# LEGACY HARDWARE CLIPS
# ==============================================================================
def export_legacy_mesh(m: Manifold, filename: str):
    raw = m.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)
    mesh.export(filename)
    print(f"Exported (Legacy): {filename} ({len(mesh.faces)} faces, {mesh.volume:.1f} mm³)")

def create_plate_rim_clip():
    body = Manifold.cube([14.0, 10.0, 8.5])
    slot = Manifold.cube([14.2, 5.85, 7.0]).translate([-0.1, 1.6, 0.0])
    wire_groove = Manifold.cylinder(14.2, 1.3, 1.3, 24).rotate([0, 90, 0]).translate([-0.1, 9.2, 4.25])
    wire_entry = Manifold.cube([14.2, 1.8, 1.8]).translate([-0.1, 8.8, 3.35])
    return body - slot - wire_groove - wire_entry

def create_fabric_snap_top():
    base = Manifold.cylinder(2.2, 8.0, 8.0, 36)
    wire_cut = Manifold.cube([16.5, 2.5, 2.0]).translate([-8.25, -1.25, 0.8])
    pin_stem = Manifold.cylinder(3.2, 2.0, 2.0, 24).translate([0, 0, -3.2])
    pin_barb = Manifold.cylinder(1.2, 2.4, 2.0, 24).translate([0, 0, -3.2])
    pin_relief = Manifold.cube([0.8, 5.0, 3.5]).translate([-0.4, -2.5, -3.4])
    pin = (pin_stem + pin_barb) - pin_relief
    return (base - wire_cut) + pin

def create_fabric_snap_back():
    base = Manifold.cylinder(2.0, 8.0, 8.0, 36)
    chamfer = Manifold.cylinder(0.8, 8.0, 7.2, 36).translate([0, 0, 1.2])
    disc = base + chamfer
    hole = Manifold.cylinder(2.5, 2.1, 2.1, 24).translate([0, 0, -0.2])
    counterbore = Manifold.cylinder(1.0, 2.5, 2.5, 24).translate([0, 0, -0.1])
    return disc - hole - counterbore

def create_shoulder_saddle_clip():
    body = Manifold.cube([24.0, 12.0, 3.6])
    wire_chan = Manifold.cylinder(24.2, 1.3, 1.3, 24).rotate([0, 90, 0]).translate([-0.1, 6.0, 2.2])
    wire_neck = Manifold.cube([24.2, 1.8, 1.8]).translate([-0.1, 5.1, 2.0])
    slot1 = Manifold.cube([2.4, 8.0, 4.0]).translate([3.0, 2.0, -0.2])
    slot2 = Manifold.cube([2.4, 8.0, 4.0]).translate([18.6, 2.0, -0.2])
    return body - wire_chan - wire_neck - slot1 - slot2


# ==============================================================================
# MAIN COMPILATION ENTRYPOINT
# ==============================================================================
if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("[Imagineering] Compiling 3.2mm Fairy Light Clips, 90° Elbows & Pyramid Cradle...")

    # Primary 3.2mm straight fold clips
    export_trimesh(create_clip_2strand_flat(), "3d_panels/wire_clips/clip_2strand_flat.stl")
    export_trimesh(create_clip_3strand_flat(), "3d_panels/wire_clips/clip_3strand_flat.stl")
    export_trimesh(create_clip_2strand_stacked(), "3d_panels/wire_clips/clip_2strand_stacked.stl")
    export_trimesh(create_clip_3strand_bundle(), "3d_panels/wire_clips/clip_3strand_bundle.stl")

    # Preserved 2-strand pyramid cradle (v1 fit)
    export_trimesh(create_clip_2strand_pyramid_cradle(), "3d_panels/wire_clips/clip_2strand_pyramid_cradle.stl")

    # Single-wire 90-degree corner brackets
    export_trimesh(create_corner_90_single(), "3d_panels/wire_clips/clip_corner_90_single.stl")
    export_trimesh(create_corner_90_sewable(), "3d_panels/wire_clips/clip_corner_90_sewable.stl")

    # Quick 3-Minute Test Gauge Comb
    export_trimesh(create_test_gauge_comb(), "3d_panels/wire_clips/wire_gauge_test_comb.stl")

    # Comprehensive Runner Multi-Pack (25 pieces total)
    export_trimesh(create_runner_multipack(), "3d_panels/wire_clips/wire_clips_runner_pack.stl")

    # Legacy Clips
    export_legacy_mesh(create_plate_rim_clip(), "3d_panels/wire_clips/clip_plate_rim.stl")
    export_legacy_mesh(create_fabric_snap_top(), "3d_panels/wire_clips/clip_fabric_snap_top.stl")
    export_legacy_mesh(create_fabric_snap_back(), "3d_panels/wire_clips/clip_fabric_snap_back.stl")
    export_legacy_mesh(create_shoulder_saddle_clip(), "3d_panels/wire_clips/clip_shoulder_saddle.stl")

    print("[Done] All 3.2mm clips, 90° elbows, and multi-pack compiled and exported successfully!")
