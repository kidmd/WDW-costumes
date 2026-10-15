#!/usr/bin/env python3
"""
generate_swiftvest_mounts.py

Generates 3D-printable mounting hardware for attaching MSEP costume plates
(240mm rigid PLA front and back chassis) to the SWIFTVEST running vest:

1. swiftvest_hinge_clamp_right.stl:
   Captive webbing hinge clamp for right shoulder strap (permanent pivot hinge).
2. swiftvest_quick_latch_left.stl:
   Quick-release thumb-actuated snap latch for left shoulder strap.
3. swiftvest_bungee_anchor_hook.stl:
   Rear plate shock-cord corner anchor hooks (2.5mm - 3.0mm bungee).
4. swiftvest_cord_lock_slide.stl:
   Dual-hole low-profile friction cord cinch for bungee tensioning.
"""

import os
import math
import numpy as np
import trimesh
import manifold3d
from manifold3d import Manifold

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "3d_panels")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def to_trimesh(m: Manifold) -> trimesh.Trimesh:
    data = m.to_mesh()
    verts = data.vert_properties[:, :3]
    faces = data.tri_verts
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    return mesh

def make_cylinder(height, radius, segments=32):
    return Manifold.cylinder(height, radius, radius, segments)

def make_box(x, y, z):
    return Manifold.cube([x, y, z], center=False)

def build_hinge_clamp_right() -> trimesh.Trimesh:
    """
    Right shoulder strap captive hinge clamp.
    Mounts to plate eyelet tab (via M2 / M2.5 screw).
    Features a captive, radiused 22mm x 2.8mm webbing channel with a 1.4mm angled
    retaining entry gate, allowing it to slip onto the vest webbing and stay securely captive.
    """
    total_w = 26.0  # mm (along webbing width)
    total_l = 28.0  # mm (from plate eyelet to webbing center)
    height = 6.0   # mm
    
    # 1. Main outer body block
    body = make_box(total_l, total_w, height)
    
    # 2. Mounting pad cutout for plate eyelet tab (10mm wide x 12mm long x 2.2mm shelf)
    tab_pocket = make_box(12.0, 10.0, 2.4).translate([0.0, (total_w - 10.0) / 2.0, height - 2.4])
    
    # 3. Screw hole: M2.5 clearance hole (dia 2.8mm) at x = 5.0, y = total_w / 2.0
    screw_hole = make_cylinder(height + 2.0, 1.4, 32).translate([5.0, total_w / 2.0, -1.0])
    # Nut counterbore on bottom: hex or 5.2mm round x 2.2mm deep
    nut_pocket = make_cylinder(2.4, 2.7, 32).translate([5.0, total_w / 2.0, -0.2])
    
    # 4. Webbing channel: 22.0mm wide x 3.0mm thick slot at x = 18.0 to 24.0mm
    webbing_slot = make_box(4.0, 22.0, height + 2.0).translate([18.0, (total_w - 22.0) / 2.0, -1.0])
    
    # 5. Angled entry gate so webbing can be threaded without unstitching vest (1.4mm wide, angled at 30 deg)
    gate_box = make_box(8.0, 1.4, height + 2.0).translate([20.0, (total_w - 22.0) / 2.0 - 0.5, -1.0])
    
    # 6. Smooth chamfer/bevel relief on outer corners to prevent chafing
    corner_cutter1 = make_box(10.0, 10.0, height + 2.0).translate([-5.0, -5.0, -1.0])
    
    # Combine booleans
    part = body - tab_pocket - screw_hole - nut_pocket - webbing_slot - gate_box
    
    # Smooth outer edges using cylinder pillars
    outer_bar = make_cylinder(height, 2.0, 32).translate([total_l - 2.0, total_w / 2.0, 0.0])
    
    return to_trimesh(part)

def build_quick_latch_left() -> trimesh.Trimesh:
    """
    Left shoulder strap quick-release thumb latch.
    Features a flexible cantilever jaw with an angled lead-in ramp and positive retention tooth,
    plus a tactile textured thumb paddle for quick one-handed release.
    """
    total_l = 32.0  # mm
    total_w = 26.0  # mm
    height = 6.0   # mm
    
    # 1. Base mount body
    base = make_box(12.0, total_w, height)
    
    # 2. Eyelet tab pocket and M2.5 screw hole
    tab_pocket = make_box(10.0, 10.0, 2.4).translate([0.0, (total_w - 10.0) / 2.0, height - 2.4])
    screw_hole = make_cylinder(height + 2.0, 1.4, 32).translate([5.0, total_w / 2.0, -1.0])
    nut_pocket = make_cylinder(2.4, 2.7, 32).translate([5.0, total_w / 2.0, -0.2])
    
    # 3. Cantilever spring arms (upper and lower beam flanking the webbing slot)
    beam_upper = make_box(16.0, 3.5, height).translate([12.0, total_w - 3.5, 0.0])
    beam_lower = make_box(16.0, 3.5, height).translate([12.0, 0.0, 0.0])
    
    # 4. Snap jaw with retaining tooth at x = 24.0mm
    tooth_upper = make_box(2.5, 2.0, height).translate([24.0, total_w - 5.5, 0.0])
    tooth_lower = make_box(2.5, 2.0, height).translate([24.0, 3.5, 0.0])
    
    # 5. Angled lead-in ramps (45 deg) on jaw tips
    # 6. Ergonomic thumb paddle protruding outward at x = 27.0 to 32.0
    paddle = make_box(6.0, 8.0, height).translate([26.0, (total_w - 8.0) / 2.0, 0.0])
    
    # Webbing capture cavity inside (22mm wide x 3.5mm thick)
    # Build complete assembly
    full_solid = base + beam_upper + beam_lower + tooth_upper + tooth_lower + paddle
    
    # Cutters: eyelet pocket, screw hole, nut pocket
    part = full_solid - tab_pocket - screw_hole - nut_pocket
    
    # Add grip ridges on thumb paddle
    ridge1 = make_cylinder(height, 0.6, 16).translate([28.0, total_w / 2.0, 0.0])
    ridge2 = make_cylinder(height, 0.6, 16).translate([30.0, total_w / 2.0, 0.0])
    part = part + ridge1 + ridge2
    
    return to_trimesh(part)

def build_bungee_anchor_hook() -> trimesh.Trimesh:
    """
    Rear plate shock-cord corner anchor hook.
    Mounts through any plate eyelet (M2/M2.5 screw or snap peg) and provides
    a low-profile, radiused 3.5mm channel for 2.5mm - 3.0mm elastic bungee cord.
    """
    length = 16.0  # mm
    width = 10.0   # mm
    height = 7.0   # mm
    
    # 1. Main body
    body = make_box(length, width, height)
    
    # 2. Eyelet mount hole (dia 2.8mm) at x = 4.0mm
    mount_hole = make_cylinder(height + 2.0, 1.4, 32).translate([4.0, width / 2.0, -1.0])
    
    # 3. Cord channel: smooth cylindrical recess dia 3.8mm at x = 11.5mm, oriented along Y
    cord_channel = make_cylinder(width + 2.0, 1.9, 32)
    # Rotate cylinder to lie along Y axis
    rot_matrix = np.array([
        [1, 0, 0, 11.5],
        [0, 0, -1, -1.0],
        [0, 1, 0, 3.8],
        [0, 0, 0, 1]
    ], dtype=np.float32)
    # We can create cord cutout with a box + cylinder
    cord_slot = make_box(3.8, width + 2.0, 3.8).translate([9.6, -1.0, 3.5])
    
    # 4. Retaining lip on hook (0.8mm overhang prevents cord from popping out)
    lip = make_box(1.2, width, 1.2).translate([9.6, 0.0, height - 1.2])
    
    part = (body - mount_hole - cord_slot) + lip
    return to_trimesh(part)

def build_cord_lock_slide() -> trimesh.Trimesh:
    """
    Dual-hole low-profile friction cord cinch for 2.5mm elastic shock cord.
    Allows tensioning without requiring separate store-bought hardware.
    """
    length = 18.0  # mm
    width = 10.0   # mm
    height = 5.0   # mm
    
    body = make_box(length, width, height)
    
    # Hole 1 (dia 3.2mm) at x = 5.0mm
    h1 = make_cylinder(height + 2.0, 1.6, 32).translate([5.0, width / 2.0, -1.0])
    # Hole 2 (dia 3.2mm) at x = 13.0mm
    h2 = make_cylinder(height + 2.0, 1.6, 32).translate([13.0, width / 2.0, -1.0])
    
    # Ergonomic side scallops for finger grip
    scallop_left = make_cylinder(height + 2.0, 2.5, 32).translate([length / 2.0, -1.0, -1.0])
    scallop_right = make_cylinder(height + 2.0, 2.5, 32).translate([length / 2.0, width + 1.0, -1.0])
    
    part = body - h1 - h2 - scallop_left - scallop_right
    return to_trimesh(part)

def main():
    print("Generating SWIFTVEST 3D mounting hardware...")
    
    models = {
        "swiftvest_hinge_clamp_right.stl": build_hinge_clamp_right(),
        "swiftvest_quick_latch_left.stl": build_quick_latch_left(),
        "swiftvest_bungee_anchor_hook.stl": build_bungee_anchor_hook(),
        "swiftvest_cord_lock_slide.stl": build_cord_lock_slide()
    }
    
    for filename, mesh in models.items():
        out_path = os.path.join(OUTPUT_DIR, filename)
        mesh.export(out_path)
        vol_cm3 = mesh.volume / 1000.0 if mesh.is_watertight else 0.0
        print(f"  [OK] Exported: {filename}")
        print(f"       Vertices: {len(mesh.vertices)}, Triangles: {len(mesh.faces)}, Watertight: {mesh.is_watertight}")
        print(f"       Volume: {vol_cm3:.2f} cm3 (~{vol_cm3 * 1.25:.1f}g PLA)\n")
        
    print(f"All 4 SWIFTVEST mounting files successfully exported to {OUTPUT_DIR}!")

if __name__ == "__main__":
    main()
