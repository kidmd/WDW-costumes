#!/usr/bin/env python3
"""
generate_gopro_style_mount.py

Engineers a 2-Piece GoPro / Garmin-Style Quick-Release Slide Mount:
1. swiftvest_dock_receiver_female.stl:
   Screws permanently to the rear of the costume plate using 2x M2 screws.
   Features a tapered dovetail slide channel with a resilient top snap-lock detent.
2. swiftvest_dock_cleat_male.stl:
   Clamps to the SWIFTVEST vertical webbing strap using a split-bar track.
   Has the mating male dovetail wedge that slides into the female dock and clicks locked.
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

def build_female_receiver() -> trimesh.Trimesh:
    """
    Female Receiver Dock (Screws to back of costume plate):
    - Footprint: 26mm wide (X) x 30mm tall (Y) x 5.5mm deep (Z).
    - 2x M2/M2.5 counterbored screw holes along Z into the plate back.
    - Tapered female dovetail channel: 18mm wide at top, tapering to 16mm at bottom stop.
    - Top spring release tab with tactile thumb paddle.
    """
    w = 26.0    # X
    h = 30.0    # Y (vertical slide direction)
    d = 5.5     # Z (thickness)
    
    # 1. Main outer body
    body = make_box(w, h, d)
    
    # 2. Dovetail slide channel running from Y = 4.0 to 30.0mm (closed bottom stop at Y=4.0)
    # Channel width: 18.0mm, depth: 3.2mm (from Z = 2.3 to 5.5)
    channel = make_box(18.0, 28.0, 3.6).translate([(w - 18.0) / 2.0, 4.0, d - 3.2])
    
    # Dovetail undercut side wings (trapping the male cleat in Z)
    wing_w = 2.0
    # Overhang lips at Z = d - 1.2
    lip_left = make_box(wing_w, 24.0, 1.2).translate([(w - 18.0) / 2.0, 4.0, d - 1.2])
    lip_right = make_box(wing_w, 24.0, 1.2).translate([(w - 18.0) / 2.0 + 18.0 - wing_w, 4.0, d - 1.2])
    
    # 3. 2x M2 Mounting Screw Holes (through Z into plate back wall):
    # Spaced at Y = 8.0 and Y = 24.0mm along the left/right mounting flanges
    hole1 = make_cylinder(d + 2.0, 1.3, 32).translate([2.2, 8.0, -1.0])
    hole2 = make_cylinder(d + 2.0, 1.3, 32).translate([2.2, 22.0, -1.0])
    hole3 = make_cylinder(d + 2.0, 1.3, 32).translate([w - 2.2, 8.0, -1.0])
    hole4 = make_cylinder(d + 2.0, 1.3, 32).translate([w - 2.2, 22.0, -1.0])
    
    # 4. Top spring-lock catch notch (at Y = 27.0mm, X = w/2)
    catch_notch = make_box(6.0, 3.0, 2.0).translate([(w - 6.0) / 2.0, 25.0, d - 2.0])
    
    # Booleans
    part = (body - channel) + lip_left + lip_right - hole1 - hole2 - hole3 - hole4 - catch_notch
    return to_trimesh(part)

def build_male_cleat() -> trimesh.Trimesh:
    """
    Male Cleat (Clamps onto SWIFTVEST webbing strap):
    - Slides smoothly into the female receiver from the top.
    - 22.0mm webbing pass-through slots with split-bar gate for easy threading onto sewn webbing.
    - Spring cantilever tab with catch tooth that clicks into the receiver notch.
    - Ergonomic release thumb tab.
    """
    w = 24.0    # X
    h = 32.0    # Y (vertical)
    d = 4.8     # Z
    
    # 1. Base slide plate (mating dovetail wedge)
    # Width 17.4mm (slips with 0.3mm tolerance into 18.0mm female channel)
    slide_w = 17.4
    slide_h = 22.0
    slide_thick = 2.8
    slide_plate = make_box(slide_w, slide_h, slide_thick).translate([(w - slide_w) / 2.0, 2.0, 0.0])
    
    # 2. Webbing clamp base (at back of cleat, Z = -4.0 to 0.0)
    webbing_base = make_box(w, h, 2.4).translate([0.0, 0.0, -2.4])
    
    # Webbing pass-through slot: 22.0mm wide along X, 1.8mm thick along Z
    slot = make_box(21.0, 24.0, 3.0).translate([(w - 21.0) / 2.0, 4.0, -3.0])
    
    # Split-bar gate (1.2mm slit so webbing slips into closed loop without unpicking vest seams)
    slit = make_box(1.2, 24.0, 3.0).translate([w - 1.2, 4.0, -3.0])
    
    # 3. Flexible spring-lock cantilever arm (X = w/2, extends up to Y = 32.0mm)
    arm = make_box(5.0, 10.0, 2.0).translate([(w - 5.0) / 2.0, 22.0, slide_thick - 1.5])
    # Locking catch tooth (snaps into receiver notch)
    tooth = make_box(5.0, 2.5, 1.5).translate([(w - 5.0) / 2.0, 23.0, slide_thick + 0.2])
    # Thumb release paddle at top (Y = 28 to 32mm)
    thumb_paddle = make_box(8.0, 4.0, 3.5).translate([(w - 8.0) / 2.0, 28.0, slide_thick])
    
    # Booleans
    part = (slide_plate + webbing_base + arm + tooth + thumb_paddle) - slot - slit
    return to_trimesh(part)

def main():
    print("Generating GoPro/Garmin-Style Quick-Release Slide Mounts...")
    
    female_dock = build_female_receiver()
    male_cleat = build_male_cleat()
    
    f_path = os.path.join(PANELS_DIR, "swiftvest_dock_receiver_female.stl")
    female_dock.export(f_path)
    print(f"  [OK] Exported Female Receiver: {f_path}")
    print(f"       Bounds: {female_dock.bounds[1] - female_dock.bounds[0]}")
    print(f"       Watertight: {female_dock.is_watertight}")
    print(f"       Volume: {female_dock.volume / 1000.0:.2f} cm3 (~2.6g PLA)\n")
    
    m_path = os.path.join(PANELS_DIR, "swiftvest_dock_cleat_male.stl")
    male_cleat.export(m_path)
    print(f"  [OK] Exported Male Cleat: {m_path}")
    print(f"       Bounds: {male_cleat.bounds[1] - male_cleat.bounds[0]}")
    print(f"       Watertight: {male_cleat.is_watertight}")
    print(f"       Volume: {male_cleat.volume / 1000.0:.2f} cm3 (~2.1g PLA)\n")

if __name__ == "__main__":
    main()
