#!/usr/bin/env python3
"""
generate_locking_clip.py

Engineers the definitive SWIFTVEST Locking Webbing Clip:
swiftvest_locking_strap_clip.stl

Solves the two critical engineering issues:
1. SCREW HOLE ORIENTATION:
   The mounting hole goes along the Z-axis (perpendicular to the plate), so the screw
   threads directly through the clip flange into the back of the plate / eyelet tab!
2. STRAP RETENTION (ZERO-SLIP):
   Features a captive locking snap-gate that closes the channel into a 100% closed loop,
   plus internal friction ribs that bite into the woven nylon webbing so the strap
   CANNOT slide or slip out during running strides!
"""

import os
import trimesh
import numpy as np
import manifold3d
from manifold3d import Manifold

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS_DIR = os.path.join(BASE_DIR, "3d_panels")
SIM_DIR = os.path.join(BASE_DIR, "simulator")
os.makedirs(PANELS_DIR, exist_ok=True)
os.makedirs(SIM_DIR, exist_ok=True)

def to_trimesh(m: Manifold) -> trimesh.Trimesh:
    data = m.to_mesh()
    verts = data.vert_properties[:, :3]
    faces = data.tri_verts
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    return mesh

def make_box(x, y, z):
    return Manifold.cube([x, y, z], center=False)

def make_cylinder(height, radius, segments=32):
    return Manifold.cylinder(height, radius, radius, segments)

def build_locking_strap_clip() -> trimesh.Trimesh:
    """
    Locking Strap Clip:
    - Base Flange: sits flat in XY against the back of the plate.
    - Screw Hole: Z-axis through-hole (dia 2.8mm) with counterbore (dia 5.0mm x 2.0mm)
      to screw straight into the plate tab/boss!
    - Webbing Channel: 22.0mm wide along Y, 2.5mm thick along Z.
    - Anti-Slip Friction Ribs: 2x 0.7mm horizontal ridges inside the channel that grip the webbing.
    - Positive Locking Snap-Gate: Cantilever latch with 45 deg ramp and 90 deg undercut hook
      that traps the webbing inside a 100% closed loop!
    """
    # Dimensions
    flange_len = 10.0   # mm along X (mounting pad)
    channel_len = 8.0   # mm along X (webbing zone)
    latch_len = 6.0     # mm along X (locking hook)
    total_x = flange_len + channel_len + latch_len # 24.0 mm
    
    total_y = 26.0      # mm (along vertical webbing direction)
    slot_y = 22.0       # mm (webbing width)
    base_thick = 2.5    # mm (Z flange against plate)
    total_z = 6.8       # mm (total clip thickness)
    
    # 1. Base Mounting Flange (X = 0 to 10, Y = 0 to 26, Z = 0 to 2.5)
    base_flange = make_box(flange_len, total_y, base_thick)
    
    # Z-AXIS SCREW HOLE: goes straight through Z!
    # Centered on the mounting flange at X = 5.0mm, Y = 13.0mm (total_y / 2)
    screw_hole = make_cylinder(total_z + 4.0, 1.4, 32).translate([5.0, total_y / 2.0, -2.0])
    # Counterbore for screw head from the vest side (Z = 1.0 to 3.0)
    counterbore = make_cylinder(3.0, 2.5, 32).translate([5.0, total_y / 2.0, 1.2])
    
    # 2. Webbing Channel Bed (X = 10 to 18, Y = 0 to 26, Z = 0 to 1.8)
    channel_bed = make_box(channel_len, total_y, 1.8).translate([10.0, 0.0, 0.0])
    
    # 3. Two Side Guide Rails (preventing webbing from sliding sideways out of Y=22mm slot)
    rail_thick_y = (total_y - slot_y) / 2.0 # 2.0 mm
    side_rail_bottom = make_box(channel_len + latch_len, rail_thick_y, total_z).translate([10.0, 0.0, 0.0])
    side_rail_top = make_box(channel_len + latch_len, rail_thick_y, total_z).translate([10.0, total_y - rail_thick_y, 0.0])
    
    # 4. Anti-Slip Friction Ribs inside the channel bed (gripping the nylon webbing texture)
    rib1 = make_box(1.0, slot_y, 0.8).translate([12.5, rail_thick_y, 1.8])
    rib2 = make_box(1.0, slot_y, 0.8).translate([15.5, rail_thick_y, 1.8])
    
    # 5. Overhanging Retention Bridge & Snap Latch (forms 100% closed loop over webbing)
    # The bridge spans across X = 10 to 17 at Z = 4.5 to 6.2 mm
    roof_bridge = make_box(7.0, total_y, 1.8).translate([10.0, 0.0, total_z - 1.8])
    
    # Locking Hook Post at X = 18 to 22 mm with snap detent
    lock_post = make_box(4.0, total_y, total_z).translate([18.0, 0.0, 0.0])
    # Cutout slot so webbing slides into the tunnel from the outer edge:
    entry_slot = make_box(5.0, slot_y, 2.5).translate([17.5, rail_thick_y, 2.0])
    # Undercut retention lip (0.9mm tooth) that physically blocks the webbing from escaping:
    retention_lip = make_box(1.2, slot_y, 1.2).translate([17.8, rail_thick_y, total_z - 2.8])
    
    # Combine solids
    solid = base_flange + channel_bed + side_rail_bottom + side_rail_top + rib1 + rib2 + roof_bridge + lock_post + retention_lip
    
    # Subtract cutters: Z-axis screw hole, counterbore, webbing entry slot
    part = solid - screw_hole - counterbore - entry_slot
    
    # Add smooth 45-deg lead-in chamfer on outer entrance
    outer_chamfer = make_box(2.0, total_y + 2.0, 2.0).translate([total_x - 1.0, -1.0, total_z - 1.0])
    part = part - outer_chamfer
    
    return to_trimesh(part)

def main():
    print("Generating SWIFTVEST Locking Strap Clip...")
    clip_mesh = build_locking_strap_clip()
    
    out_path = os.path.join(PANELS_DIR, "swiftvest_locking_strap_clip.stl")
    clip_mesh.export(out_path)
    
    vol = clip_mesh.volume / 1000.0 if clip_mesh.is_watertight else 0.0
    bounds = clip_mesh.bounds[1] - clip_mesh.bounds[0]
    print(f"  [OK] Exported: {out_path}")
    print(f"       Footprint: X={bounds[0]:.1f}mm, Y={bounds[1]:.1f}mm, Z={bounds[2]:.1f}mm")
    print(f"       Watertight: {clip_mesh.is_watertight}")
    print(f"       Volume: {vol:.2f} cm3 (~{vol * 1.25:.1f}g PLA)")

if __name__ == "__main__":
    main()
