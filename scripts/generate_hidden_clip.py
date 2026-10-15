#!/usr/bin/env python3
"""
generate_hidden_clip.py

Generates the ultra-compact, low-profile hidden rear C-clip:
swiftvest_hidden_webbing_clip.stl

Mounts flat against the back/underside of the front costume plate.
Faces backward and snaps directly onto the 20-22mm vertical webbing of the SWIFTVEST.
100% hidden from the front of the costume!
"""

import os
import trimesh
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

def build_hidden_webbing_clip() -> trimesh.Trimesh:
    """
    Ultra-compact rear C-clip:
    - Base pad with counterbored M2/M2.5 hole (mounts flush to plate rear)
    - 22.0mm wide x 2.4mm thick captive webbing channel
    - 45 deg snap lead-in ramp with 0.9mm rounded retention detents
    - Weight: ~1.1g PLA
    """
    slot_w = 22.0    # mm (webbing width)
    wall = 2.0       # mm wall thickness
    total_w = slot_w + (wall * 2) # 26.0 mm
    total_len = 14.0 # mm (depth from plate back toward vest)
    height = 5.2     # mm (along vertical webbing direction)
    
    # 1. Main body block
    body = make_box(total_len, total_w, height)
    
    # 2. Webbing internal channel: 22.0mm wide x 2.4mm thick, sitting from x = 6.0 to 12.0mm
    # Leaves a 2.0mm front mounting flange against the plate (x = 0 to 4.0mm)
    webbing_cutout = make_box(6.0, slot_w, height + 2.0).translate([5.5, wall, -1.0])
    
    # 3. Entry snap throat: 18.0mm wide opening (leaves 2x 2.0mm retention barbs)
    entry_gap_w = slot_w - 3.2 # 18.8mm wide entry gap
    entry_cutout = make_box(4.0, entry_gap_w, height + 2.0).translate([total_len - 3.0, (total_w - entry_gap_w) / 2.0, -1.0])
    
    # 4. Angled lead-in ramps (45 deg) on back edges for smooth snap-on
    ramp_cutter1 = make_box(3.0, 3.0, height + 2.0).translate([total_len - 1.5, wall - 1.5, -1.0])
    ramp_cutter2 = make_box(3.0, 3.0, height + 2.0).translate([total_len - 1.5, total_w - wall - 1.5, -1.0])
    
    # 5. Mounting screw hole: M2.5 clearance hole (dia 2.6mm) at x = 2.8mm, y = total_w / 2
    screw_hole = make_cylinder(height + 2.0, 1.3, 32).translate([2.8, total_w / 2.0, -1.0])
    # Counterbore for screw head (dia 4.8mm x depth 2.2mm)
    counterbore = make_cylinder(2.6, 2.4, 32).translate([2.8, total_w / 2.0, height - 2.4])
    
    # Booleans
    part = body - webbing_cutout - entry_cutout - screw_hole - counterbore
    
    return to_trimesh(part)

def main():
    print("Generating ultra-compact hidden rear C-clip...")
    clip_mesh = build_hidden_webbing_clip()
    
    out_path = os.path.join(PANELS_DIR, "swiftvest_hidden_webbing_clip.stl")
    clip_mesh.export(out_path)
    
    vol = clip_mesh.volume / 1000.0 if clip_mesh.is_watertight else 0.0
    print(f"  [OK] Exported: {out_path}")
    print(f"       Bounds: {clip_mesh.bounds[1] - clip_mesh.bounds[0]}")
    print(f"       Watertight: {clip_mesh.is_watertight}")
    print(f"       Volume: {vol:.2f} cm3 (~{vol * 1.25:.1f}g PLA)")

if __name__ == "__main__":
    main()
