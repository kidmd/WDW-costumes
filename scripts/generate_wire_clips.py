import os
import sys
import numpy as np
import trimesh
import manifold3d as m3d
from manifold3d import Manifold

os.makedirs("3d_panels/wire_clips", exist_ok=True)

# ==============================================================================
# PARAMETRIC CONSTANTS FOR RIGID PLA / PETG WIRE CLIPS & SNAP-ON CAPS
# Resized for standard ~3.2mm fairy light wiring (calibrated with test comb)
# ==============================================================================
WIRE_DIAMETER = 3.20     # Calibrated wire OD (mm)
CAVITY_RADIUS = 1.65     # Inner pocket radius (3.30mm dia for smooth wire glide without pinch)
WALL_THICKNESS = 1.35    # Flex cantilever spring wall thickness (~3-4 perimeters on 0.4mm nozzle)
FLOOR_THICKNESS = 1.20   # Bottom chassis thickness resting flat against shirt/build plate
NECK_OPENING = 2.35      # Snap constriction mouth width (gives positive snap click without stress-whitening)
CLIP_LENGTH = 8.00       # Extrusion length along wire path (mm)

# Retention bead parameters for snap-on race-day caps
BEAD_DEPTH = 0.35        # Outward retention bead protrusion (mm)
BEAD_HEIGHT = 0.60       # Bead vertical span (mm)
CAP_ROOF_T = 1.00        # Cap solid top roof thickness (mm)
CAP_LEG_T = 1.10         # Cap spring retention skirt thickness (mm)
CAP_TOLERANCE = 0.12     # Clearance gap between clip flank and cap inner wall for smooth snap


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
    y_bead = h_total - 1.20

    pts_body = [
        [-w_total / 2.0, 0.0],
        [-w_total / 2.0, y_bead - BEAD_HEIGHT / 2.0],
        [-w_total / 2.0 - BEAD_DEPTH, y_bead],
        [-w_total / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [-w_total / 2.0, h_total - 0.8],
        [-w_total / 2.0 + 0.8, h_total],
        [w_total / 2.0 - 0.8, h_total],
        [w_total / 2.0, h_total - 0.8],
        [w_total / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [w_total / 2.0 + BEAD_DEPTH, y_bead],
        [w_total / 2.0, y_bead - BEAD_HEIGHT / 2.0],
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
    y_bead = h_total - 1.20

    pts_body = [
        [-w_total / 2.0, 0.0],
        [-w_total / 2.0, y_bead - BEAD_HEIGHT / 2.0],
        [-w_total / 2.0 - BEAD_DEPTH, y_bead],
        [-w_total / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [-w_total / 2.0, h_total - 0.8],
        [-w_total / 2.0 + 0.8, h_total],
        [w_total / 2.0 - 0.8, h_total],
        [w_total / 2.0, h_total - 0.8],
        [w_total / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [w_total / 2.0 + BEAD_DEPTH, y_bead],
        [w_total / 2.0, y_bead - BEAD_HEIGHT / 2.0],
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
    y_bead = h_total - 1.20

    pts_body = [
        [-w_total / 2.0, 0.0],
        [-w_total / 2.0, y_bead - BEAD_HEIGHT / 2.0],
        [-w_total / 2.0 - BEAD_DEPTH, y_bead],
        [-w_total / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [-w_total / 2.0, h_total - 0.8],
        [-w_total / 2.0 + 0.8, h_total],
        [w_total / 2.0 - 0.8, h_total],
        [w_total / 2.0, h_total - 0.8],
        [w_total / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [w_total / 2.0 + BEAD_DEPTH, y_bead],
        [w_total / 2.0, y_bead - BEAD_HEIGHT / 2.0],
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
    y_bead = h_total - 1.20

    pts_body = [
        [-w_bot / 2.0, 0.0],
        [-w_bot / 2.0, y1 + 0.6],
        [-w_top / 2.0, y_bead - BEAD_HEIGHT / 2.0],
        [-w_top / 2.0 - BEAD_DEPTH, y_bead],
        [-w_top / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [-w_top / 2.0, h_total - 0.8],
        [-w_top / 2.0 + 0.8, h_total],
        [w_top / 2.0 - 0.8, h_total],
        [w_top / 2.0, h_total - 0.8],
        [w_top / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [w_top / 2.0 + BEAD_DEPTH, y_bead],
        [w_top / 2.0, y_bead - BEAD_HEIGHT / 2.0],
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
    y_bead = h_total - 1.20

    pts_body = [
        [-w_bot / 2.0, 0.0],
        [-w_bot / 2.0, y1 + 0.5],
        [-w_top / 2.0, y_bead - BEAD_HEIGHT / 2.0],
        [-w_top / 2.0 - BEAD_DEPTH, y_bead],
        [-w_top / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [-w_top / 2.0, h_total - 0.6],
        [-w_top / 2.0 + 0.6, h_total],
        [w_top / 2.0 - 0.6, h_total],
        [w_top / 2.0, h_total - 0.6],
        [w_top / 2.0, y_bead + BEAD_HEIGHT / 2.0],
        [w_top / 2.0 + BEAD_DEPTH, y_bead],
        [w_top / 2.0, y_bead - BEAD_HEIGHT / 2.0],
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
# 6. 90-DEGREE CORNER ELBOW BRACKETS FOR 3-STRAND RIBBON ON EDGE
# Holds 3-strand flat fairy light ribbon oriented vertically on-edge (stacked)
# Bends across thin ~1.2mm axis (easy way) - zero copper strain or kinking!
# ==============================================================================
def create_vertical_ribbon_channel_profile(
    r_inner=5.0,
    slot_w=1.65,
    slot_h=3.60,
    floor_t=1.20,
    wall_t=1.40,
    neck_w=1.00,
    lead_in_w=2.40,
    h_total=5.60
):
    """
    Creates a radial cross-section for a 3-strand flat ribbon wire oriented VERTICALLY on-edge
    with pronounced cantilever snap-fit lips, undercut retention shelf, and exterior cap snap beads.
    - Inner cavity width: 1.65 mm (smooth glide for ~1.2mm ribbon)
    - Constriction throat: 1.00 mm (positive snap retention lips over top strand)
    - Undercut shelf: 0.325 mm inward cantilever overhang per side (locks wire down)
    - Lead-in funnel: 45° widening to 2.40 mm for easy wire insertion
    - Exterior retention beads: 0.35 mm bead on inner and outer walls for snap-on cap lock
    """
    r_slot_cen = r_inner + wall_t + slot_w / 2.0   # 7.225 mm
    r_outer = r_inner + 2 * wall_t + slot_w        # 9.45 mm
    y_bead = h_total - 1.20

    pts_body = [
        [r_inner, 0.0],
        [r_outer, 0.0],
        [r_outer, y_bead - BEAD_HEIGHT / 2.0],
        [r_outer + BEAD_DEPTH, y_bead],
        [r_outer, y_bead + BEAD_HEIGHT / 2.0],
        [r_outer, h_total - 0.5],
        [r_outer - 0.5, h_total],
        [r_inner + 0.5, h_total],
        [r_inner, h_total - 0.5],
        [r_inner, y_bead + BEAD_HEIGHT / 2.0],
        [r_inner - BEAD_DEPTH, y_bead],
        [r_inner, y_bead - BEAD_HEIGHT / 2.0]
    ]
    body = m3d.CrossSection.hull_points(pts_body)

    y_cav_top = floor_t + slot_h          # 4.80 mm
    y_shelf = y_cav_top - 0.25            # 4.55 mm

    # Monolithic cutout polygon with cantilever overhang lips
    pts_cutout = [
        [r_slot_cen - lead_in_w / 2.0, h_total + 0.2],
        [r_slot_cen - neck_w / 2.0, y_cav_top],
        [r_slot_cen - slot_w / 2.0, y_shelf],
        [r_slot_cen - slot_w / 2.0, floor_t],
        [r_slot_cen + slot_w / 2.0, floor_t],
        [r_slot_cen + slot_w / 2.0, y_shelf],
        [r_slot_cen + neck_w / 2.0, y_cav_top],
        [r_slot_cen + lead_in_w / 2.0, h_total + 0.2]
    ]

    cs_cutout = m3d.CrossSection([pts_cutout])
    return body - cs_cutout


def create_corner_90_single() -> trimesh.Trimesh:
    """90-degree pure curved elbow bracket for 3-strand ribbon on edge (floating, zero tangential artifacts)."""
    r_in = 5.0
    prof = create_vertical_ribbon_channel_profile(r_inner=r_in)

    # 360-degree revolve intersected with quadrant bounding box to eliminate partial-revolve diagonal artifacts
    rev360 = prof.revolve(circular_segments=64, revolve_degrees=360.0)
    quad_box = m3d.Manifold.cube([20.0, 20.0, 10.0], center=False).translate([0.0, 0.0, -2.0])
    corner_single = rev360 ^ quad_box

    raw = corner_single.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)

    # Center bounds in XY and place Z at 0
    bounds = mesh.bounds
    mesh.apply_translation([
        -bounds[0][0] - (bounds[1][0] - bounds[0][0]) / 2.0,
        -bounds[0][1] - (bounds[1][1] - bounds[0][1]) / 2.0,
        -bounds[0][2]
    ])
    return mesh


def create_corner_90_sewable() -> trimesh.Trimesh:
    """90-degree pure curved elbow bracket for 3-strand ribbon on edge with clear, unobstructed corner eyelets."""
    r_in = 5.0
    prof = create_vertical_ribbon_channel_profile(r_inner=r_in)

    # 360-degree revolve intersected with quadrant bounding box
    rev360 = prof.revolve(circular_segments=64, revolve_degrees=360.0)
    quad_box = m3d.Manifold.cube([20.0, 20.0, 10.0], center=False).translate([0.0, 0.0, -2.0])
    corner_single = rev360 ^ quad_box

    # 2 flat sewing tabs positioned with holes completely clear of the outer 9.45mm channel wall
    # Center holes at X=11.2, Y=2.0 and X=2.0, Y=11.2 (clearance > 0.75mm from wall)
    tab_cs = m3d.CrossSection.circle(2.5, 24) - m3d.CrossSection.circle(1.0, 24)
    tab1 = tab_cs.extrude(1.2).translate([11.2, 2.0, 0.0])
    tab2 = tab_cs.extrude(1.2).translate([2.0, 11.2, 0.0])

    combined = corner_single + tab1 + tab2
    raw = combined.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)

    bounds = mesh.bounds
    mesh.apply_translation([
        -bounds[0][0] - (bounds[1][0] - bounds[0][0]) / 2.0,
        -bounds[0][1] - (bounds[1][1] - bounds[0][1]) / 2.0,
        -bounds[0][2]
    ])
    return mesh


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


def ensure_ccw(pts):
    """Ensures a 2D polygon has counter-clockwise (positive) winding order for Manifold3D."""
    area = 0.0
    n = len(pts)
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        area += (p1[0] * p2[1] - p2[0] * p1[1])
    if area < 0:
        return pts[::-1]
    return pts


# ==============================================================================
# 9. SNAP-ON RACE-DAY SECURITY CAPS (ROOFS)
# Positive-locking armored hoods that snap over clips to lock wires down for 10K
# Pre-oriented flat on roof at Z=0 for support-free printing!
# ==============================================================================
def create_cap_for_straight_clip(clip_top_width: float, clip_height: float, length: float = CLIP_LENGTH, skirt_depth: float = 2.20) -> trimesh.Trimesh:
    """
    Creates a snap-on cap / hood that clips over the top of a straight clip.
    - Roof thickness: 1.00 mm
    - Leg / Skirt thickness: 1.10 mm
    - Skirt reach: 2.20 mm down from top
    - Snap undercut bead: 0.35 mm catch bead on the inside of the skirt legs
    - Print orientation: Flat on roof at Z=0, legs point UP (+Z), zero supports needed!
    """
    inner_w = clip_top_width + 2 * CAP_TOLERANCE
    outer_w = inner_w + 2 * CAP_LEG_T

    y_clip_top = clip_height
    y_cap_top = y_clip_top + CAP_ROOF_T
    y_leg_bot = y_clip_top - skirt_depth
    y_bead = y_clip_top - 1.20

    pts_outer = [
        [-outer_w / 2.0, y_leg_bot],
        [-outer_w / 2.0, y_cap_top - 0.5],
        [-outer_w / 2.0 + 0.5, y_cap_top],
        [outer_w / 2.0 - 0.5, y_cap_top],
        [outer_w / 2.0, y_cap_top - 0.5],
        [outer_w / 2.0, y_leg_bot]
    ]
    cap_outer = m3d.CrossSection.hull_points(pts_outer)

    pts_cutout = [
        [-inner_w / 2.0 + BEAD_DEPTH, y_leg_bot - 0.1],
        [-inner_w / 2.0 + BEAD_DEPTH, y_bead - BEAD_HEIGHT / 2.0],
        [-inner_w / 2.0, y_bead],
        [-inner_w / 2.0, y_clip_top],
        [inner_w / 2.0, y_clip_top],
        [inner_w / 2.0, y_bead],
        [inner_w / 2.0 - BEAD_DEPTH, y_bead - BEAD_HEIGHT / 2.0],
        [inner_w / 2.0 - BEAD_DEPTH, y_leg_bot - 0.1]
    ]
    cap_cutout = m3d.CrossSection([ensure_ccw(pts_cutout)])
    cap_cs = cap_outer - cap_cutout

    m = cap_cs.extrude(length)
    raw = m.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)

    # Rotate -90 deg around X so roof (max Y) sits flat at Z=0 and legs point UP (+Z)
    rot = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
    mesh.apply_transform(rot)
    bounds = mesh.bounds
    mesh.apply_translation([
        -bounds[0][0] - (bounds[1][0] - bounds[0][0]) / 2.0,
        -bounds[0][1] - (bounds[1][1] - bounds[0][1]) / 2.0,
        -bounds[0][2]
    ])
    return mesh


def create_cap_corner_90(r_inner: float = 5.00, r_outer: float = 9.45, h_clip: float = 5.60) -> trimesh.Trimesh:
    """
    Creates a 90-degree curved snap-on hood for the 90° corner elbows.
    Locks over both inner and outer channel walls with dual curved snap skirts.
    Fits both floating and sewable 90° elbows identically!
    Pre-oriented flat on roof at Z=0 for support-free printing.
    """
    r_cap_in = r_inner - CAP_TOLERANCE - CAP_LEG_T
    r_cap_out = r_outer + CAP_TOLERANCE + CAP_LEG_T
    y_cap_top = h_clip + CAP_ROOF_T
    y_bead = h_clip - 1.20
    y_leg_bot = y_bead - BEAD_HEIGHT / 2.0 - 0.30

    pts_cap_outer = [
        [r_cap_in, y_leg_bot],
        [r_cap_in, y_cap_top - 0.5],
        [r_cap_in + 0.5, y_cap_top],
        [r_cap_out - 0.5, y_cap_top],
        [r_cap_out, y_cap_top - 0.5],
        [r_cap_out, y_leg_bot]
    ]
    cap_outer = m3d.CrossSection.hull_points(pts_cap_outer)

    r_clip_inner_face = r_inner - CAP_TOLERANCE
    r_clip_outer_face = r_outer + CAP_TOLERANCE

    pts_cap_cutout = [
        [r_clip_inner_face - BEAD_DEPTH, y_leg_bot - 0.1],
        [r_clip_inner_face - BEAD_DEPTH, y_bead - BEAD_HEIGHT / 2.0],
        [r_clip_inner_face, y_bead],
        [r_clip_inner_face, h_clip],
        [r_clip_outer_face, h_clip],
        [r_clip_outer_face, y_bead],
        [r_clip_outer_face + BEAD_DEPTH, y_bead - BEAD_HEIGHT / 2.0],
        [r_clip_outer_face + BEAD_DEPTH, y_leg_bot - 0.1]
    ]
    cap_cutout = m3d.CrossSection([ensure_ccw(pts_cap_cutout)])
    cap_cs = cap_outer - cap_cutout

    # Full 360 revolve and quadrant cube crop (Rule 7)
    rev360 = cap_cs.revolve(64, 360.0)
    quad_box = m3d.Manifold.cube([20.0, 20.0, 10.0], center=False).translate([0.0, 0.0, -2.0])
    corner_cap = rev360 ^ quad_box

    raw = corner_cap.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)

    # Rotate 180 deg around X so roof (max Y) sits flat at Z=0 and skirts point UP (+Z)
    rot = trimesh.transformations.rotation_matrix(np.radians(180), [1, 0, 0])
    mesh.apply_transform(rot)
    bounds = mesh.bounds
    mesh.apply_translation([
        -bounds[0][0] - (bounds[1][0] - bounds[0][0]) / 2.0,
        -bounds[0][1] - (bounds[1][1] - bounds[0][1]) / 2.0,
        -bounds[0][2]
    ])
    return mesh


def create_caps_multipack() -> trimesh.Trimesh:
    """
    Comprehensive 24-Piece Race-Day Security Caps Companion Plate:
    4x of each straight cap (20 straight caps) + 4x 90° corner caps (4 corner caps) = 24 caps!
    Pre-oriented flat on bed at Z=0, zero supports, ~12 min print time in PLA!
    """
    cap_c2_flat = create_cap_for_straight_clip(10.65, 5.01)
    cap_c3_flat = create_cap_for_straight_clip(15.30, 5.01)
    cap_c2_stack = create_cap_for_straight_clip(6.00, 8.55)
    cap_c3_bund = create_cap_for_straight_clip(6.00, 7.93)
    cap_c2_crad = create_cap_for_straight_clip(4.90, 6.27)
    cap_c90 = create_cap_corner_90()

    straight_caps = [cap_c2_flat, cap_c3_flat, cap_c2_stack, cap_c3_bund, cap_c2_crad]
    row_y = [0.0, 13.0, 26.0, 39.0, 52.0]
    col_x_offsets = [
        [-27.0, -9.0, 9.0, 27.0],   # c2_flat (13.1mm wide)
        [-33.0, -11.0, 11.0, 33.0], # c3_flat (17.7mm wide)
        [-22.5, -7.5, 7.5, 22.5],   # c2_stack (8.4mm wide)
        [-22.5, -7.5, 7.5, 22.5],   # c3_bundle (8.4mm wide)
        [-21.0, -7.0, 7.0, 21.0]    # c2_cradle (7.3mm wide)
    ]

    parts = []
    for r_idx, (model, y_pos) in enumerate(zip(straight_caps, row_y)):
        for x_pos in col_x_offsets[r_idx]:
            inst = model.copy()
            inst.apply_translation([x_pos, y_pos, 0.0])
            parts.append(inst)

    # Row 6 (Y=66): 4x 90 corner caps (10.65mm wide)
    corner_xs = [-24.0, -8.0, 8.0, 24.0]
    for x in corner_xs:
        inst = cap_c90.copy()
        inst.apply_translation([x, 66.0, 0.0])
        parts.append(inst)

    combined = trimesh.util.concatenate(parts)
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

    # Snap-On Race-Day Security Caps (Roofs)
    export_trimesh(create_cap_for_straight_clip(10.65, 5.01), "3d_panels/wire_clips/cap_2strand_flat.stl")
    export_trimesh(create_cap_for_straight_clip(15.30, 5.01), "3d_panels/wire_clips/cap_3strand_flat.stl")
    export_trimesh(create_cap_for_straight_clip(6.00, 8.55), "3d_panels/wire_clips/cap_2strand_stacked.stl")
    export_trimesh(create_cap_for_straight_clip(6.00, 7.93), "3d_panels/wire_clips/cap_3strand_bundle.stl")
    export_trimesh(create_cap_for_straight_clip(4.90, 6.27), "3d_panels/wire_clips/cap_2strand_pyramid_cradle.stl")
    export_trimesh(create_cap_corner_90(), "3d_panels/wire_clips/cap_corner_90.stl")

    # Comprehensive Runner Multi-Pack (25 pieces total: clips + test comb)
    export_trimesh(create_runner_multipack(), "3d_panels/wire_clips/wire_clips_runner_pack.stl")

    # 24-Piece Race-Day Caps Pack (Matching companion plate)
    export_trimesh(create_caps_multipack(), "3d_panels/wire_clips/wire_clips_caps_pack.stl")

    # Legacy Clips
    export_legacy_mesh(create_plate_rim_clip(), "3d_panels/wire_clips/clip_plate_rim.stl")
    export_legacy_mesh(create_fabric_snap_top(), "3d_panels/wire_clips/clip_fabric_snap_top.stl")
    export_legacy_mesh(create_fabric_snap_back(), "3d_panels/wire_clips/clip_fabric_snap_back.stl")
    export_legacy_mesh(create_shoulder_saddle_clip(), "3d_panels/wire_clips/clip_shoulder_saddle.stl")

    print("[Done] All 3.2mm clips, 90° elbows, and multi-pack compiled and exported successfully!")
