import os
import sys
import numpy as np
import trimesh
import manifold3d as m3d
from manifold3d import Manifold

os.makedirs("3d_panels/wire_clips", exist_ok=True)

# ==============================================================================
# PARAMETRIC CONSTANTS FOR RIGID PLA / PETG WIRE CLIPS
# ==============================================================================
# Target wire: Standard insulated fairy light wire (~2.0mm to 2.5mm OD)
WIRE_DIAMETER = 2.30     # Nominal wire OD (mm)
CAVITY_RADIUS = WIRE_DIAMETER / 2.0 + 0.05  # 1.20mm radius (2.40mm dia for smooth glide without pinching)
WALL_THICKNESS = 1.25    # Flex cantilever spring wall thickness (~3 perimeters on 0.4mm nozzle)
FLOOR_THICKNESS = 1.10   # Bottom chassis thickness resting flat against shirt
NECK_OPENING = 1.65      # Snap constriction mouth width (gives positive snap without stress-whitening)
CLIP_LENGTH = 8.00       # Extrusion length along wire path (mm)


def to_flat_trimesh(profile: m3d.CrossSection, length: float = CLIP_LENGTH) -> trimesh.Trimesh:
    """Extrudes a 2D profile along Z and rotates so the flat base sits at Z=0 for printing."""
    m = profile.extrude(length)
    raw = m.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties, faces=raw.tri_verts)
    # Rotate 90 deg around X so base (Y=0) lies flat on build plate at Z=0
    rot = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
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
# 1. 2-STRAND FLAT PARALLEL CLIP
# Holds 2 strands side-by-side, ultra low-profile (flush against chest/shirt)
# ==============================================================================
def create_clip_2strand_flat(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    spacing = 2 * r_cav + WALL_THICKNESS
    w_total = 2 * (spacing / 2.0 + r_cav + WALL_THICKNESS)
    y_cen = FLOOR_THICKNESS + r_cav
    h_total = y_cen + r_cav + 0.65

    # Chamfered outer envelope (flat bottom at Y=0)
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
        y_neck = y_cen + 0.85
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
# 2. 3-STRAND FLAT PARALLEL CLIP
# Holds 3 strands side-by-side in individual snap bays (for flat folds / accordions)
# ==============================================================================
def create_clip_3strand_flat(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    spacing = 2 * r_cav + WALL_THICKNESS
    w_total = 2 * (spacing + r_cav + WALL_THICKNESS)
    y_cen = FLOOR_THICKNESS + r_cav
    h_total = y_cen + r_cav + 0.65

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
        y_neck = y_cen + 0.85
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
# 3. 2-STRAND STACKED VERTICAL CLIP
# Holds 2 strands stacked vertically over-under. Narrowest lateral footprint (4.9mm)!
# ==============================================================================
def create_clip_2strand_stacked(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    y1 = FLOOR_THICKNESS + r_cav
    y2 = y1 + 2 * r_cav + 0.15
    y_waist = (y1 + y2) / 2.0
    y_neck = y2 + 0.85
    h_total = y2 + r_cav + 0.70
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
    waist = m3d.CrossSection.square([1.70, y2 - y1], center=True).translate([0, y_waist])

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
# 4. 3-STRAND PYRAMID BUNDLE CLIP
# Holds 3 strands in a compact triangular cluster (2 bottom, 1 top locked)
# ==============================================================================
def create_clip_3strand_bundle(wire_d=WIRE_DIAMETER, length=CLIP_LENGTH) -> trimesh.Trimesh:
    r_cav = wire_d / 2.0 + 0.05
    x1, y1 = -1.35, FLOOR_THICKNESS + r_cav
    x2, y2 = 1.35, FLOOR_THICKNESS + r_cav
    x3, y3 = 0.0, y1 + 2.05
    h_total = y3 + r_cav + 0.80
    w_bot = 2 * (1.35 + r_cav + WALL_THICKNESS)
    w_top = 2 * (r_cav + WALL_THICKNESS)

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
    throat = m3d.CrossSection.square([NECK_OPENING, y3 - y1], center=True).translate([0, (y1 + y3) / 2.0])

    y_neck = y3 + 0.85
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
    divider = m3d.CrossSection.circle(0.40, 16).translate([0, FLOOR_THICKNESS + 0.25])

    cutout = (c1 + c2 + c3 + throat + top_slot) - divider
    profile = body - cutout
    return to_flat_trimesh(profile, length)


# ==============================================================================
# 5. MULTI-PACK RUNNER PRINT BED (16 CLIPS TOTAL)
# 4x of each model arranged on a clean ~55x50mm print bed layout
# ==============================================================================
def create_runner_multipack() -> trimesh.Trimesh:
    c2_flat = create_clip_2strand_flat()
    c3_flat = create_clip_3strand_flat()
    c2_stack = create_clip_2strand_stacked()
    c3_bund = create_clip_3strand_bundle()

    models = [c2_flat, c3_flat, c2_stack, c3_bund]
    row_y = [0.0, 13.0, 26.0, 39.0]
    col_x_offsets = [
        [-21.0, -7.0, 7.0, 21.0],  # 2-strand flat (8.5mm wide)
        [-24.0, -8.0, 8.0, 24.0],  # 3-strand flat (12.2mm wide)
        [-18.0, -6.0, 6.0, 18.0],  # 2-strand stacked (4.9mm wide)
        [-21.0, -7.0, 7.0, 21.0]   # 3-strand bundle (7.6mm wide)
    ]

    pack_parts = []
    for r_idx, (model, y_pos) in enumerate(zip(models, row_y)):
        for x_pos in col_x_offsets[r_idx]:
            inst = model.copy()
            inst.apply_translation([x_pos, y_pos, 0.0])
            pack_parts.append(inst)

    combined = trimesh.util.concatenate(pack_parts)
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
    print("[Imagineering] Compiling WDW 10K Fairy Light Wire Fold Management Clips...")

    # 4 New Fold Clips
    export_trimesh(create_clip_2strand_flat(), "3d_panels/wire_clips/clip_2strand_flat.stl")
    export_trimesh(create_clip_3strand_flat(), "3d_panels/wire_clips/clip_3strand_flat.stl")
    export_trimesh(create_clip_2strand_stacked(), "3d_panels/wire_clips/clip_2strand_stacked.stl")
    export_trimesh(create_clip_3strand_bundle(), "3d_panels/wire_clips/clip_3strand_bundle.stl")

    # Runner Multi-Pack (16 clips ready for single-plate 3D print)
    export_trimesh(create_runner_multipack(), "3d_panels/wire_clips/wire_clips_runner_pack.stl")

    # Legacy Clips
    export_legacy_mesh(create_plate_rim_clip(), "3d_panels/wire_clips/clip_plate_rim.stl")
    export_legacy_mesh(create_fabric_snap_top(), "3d_panels/wire_clips/clip_fabric_snap_top.stl")
    export_legacy_mesh(create_fabric_snap_back(), "3d_panels/wire_clips/clip_fabric_snap_back.stl")
    export_legacy_mesh(create_shoulder_saddle_clip(), "3d_panels/wire_clips/clip_shoulder_saddle.stl")

    print("[Done] All wire management clips compiled and exported successfully!")
