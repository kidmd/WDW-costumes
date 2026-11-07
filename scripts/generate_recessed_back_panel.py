import os, math
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh

# ==============================================================================
# 🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K)
# 16x16 MATRIX TEST PANEL - RECESSED BACK (FELT SIDE) COUNTERBORE v3
# Features:
#  - 100% Flat Front Face against PEI Bed (Zero Bridging / Zero Supports)
#  - 176mm Extended Perimeter Flange (5.8mm horizontal border)
#  - 3.0mm Flush Back Rim (Corner tabs flush with 2mm frame wall)
#  - Ø 13.0mm x 1.2mm Deep Recessed Pocket on the BACK (Felt Side)
#  - 1.8mm Solid PETG Floor under Snap Cap (Ideal for 6.2mm Prongs)
# ==============================================================================

def extrude_shapely(shape, height):
    """Extrude any 2D shapely geometry (Polygon or MultiPolygon) into a watertight Trimesh."""
    if shape is None or shape.is_empty:
        return None
    geoms = shape.geoms if shape.geom_type in ['MultiPolygon', 'GeometryCollection'] else [shape]
    meshes = []
    for g in geoms:
        if g.geom_type == 'Polygon' and g.area > 0.05:
            try:
                m = trimesh.creation.extrude_polygon(g, height=height)
                if m and len(m.faces) > 0:
                    meshes.append(m)
            except Exception as e:
                print(f"Extrusion error on sub-polygon: {e}")
    if not meshes:
        return None
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.util.concatenate(meshes)

def build_recessed_back_panels():
    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Geometric Specifications:
    # -------------------------------------------------------------------------
    CAVITY_SIZE = 160.4        # mm (fits 160x160mm BTF-Lighting matrix with 0.2mm tolerance)
    FRAME_WALL_WIDTH = 2.0     # mm
    PLATE_BASE_WIDTH = 176.0   # mm (5.8mm perimeter flange around frame walls)
    
    FLOOR_THICKNESS = 1.0      # mm (Z = 0.0 to 1.0mm)
    SUB_FLOOR_Z = 1.8          # mm (height where snap pocket floor sits)
    TOTAL_HEIGHT = 3.0         # mm (top rim of frame wall and corner tabs)
    
    SNAP_THROUGH_HOLE_DIA = 3.0 # mm (Ø 3.0mm loose clearance for KAM size 20 pin)
    SNAP_HOLE_RADIUS = SNAP_THROUGH_HOLE_DIA / 2.0 # 1.5 mm
    
    RECESSED_POCKET_DIA = 13.0 # mm (Ø 13.0mm well on back for snap socket / felt nest)
    RECESSED_POCKET_RADIUS = RECESSED_POCKET_DIA / 2.0 # 6.5 mm
    
    # Coordinates centered at (0, 0):
    half_cav = CAVITY_SIZE / 2.0         # 80.2 mm
    half_frame = half_cav + FRAME_WALL_WIDTH # 82.2 mm
    half_plate = PLATE_BASE_WIDTH / 2.0  # 88.0 mm
    
    cavity_box = sg.box(-half_cav, -half_cav, half_cav, half_cav)
    frame_outer_box = sg.box(-half_frame, -half_frame, half_frame, half_frame)
    plate_box = sg.box(-half_plate, -half_plate, half_plate, half_plate)
    
    # Wire notch: 16mm wide, cuts bottom frame wall
    wire_notch = sg.box(-8.0, -half_frame - 1.0, 8.0, -half_cav + 0.1)
    
    # Frame wall polygon (Z = 1.0 to 3.0mm):
    frame_wall_2d = frame_outer_box.difference(cavity_box).difference(wire_notch)
    
    # -------------------------------------------------------------------------
    # Integrated Corner Snap Wings:
    # -------------------------------------------------------------------------
    diag_clearance = 7.5 # mm diagonal clearance from frame wall corner (82.2, 82.2)
    diag_offset = diag_clearance * math.cos(math.radians(45)) # 5.303 mm
    hole_pos = half_frame + diag_offset # 87.503 mm
    
    corner_signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    hole_cutouts = []
    pocket_cutouts = []
    ear_hulls = []
    
    for sx, sy in corner_signs:
        hx, hy = sx * hole_pos, sy * hole_pos
        pt = sg.Point(hx, hy)
        hole_cutouts.append(pt.buffer(SNAP_HOLE_RADIUS, resolution=32))
        pocket_cutouts.append(pt.buffer(RECESSED_POCKET_RADIUS, resolution=32))
        
        # 15mm diameter ear lobe around the hole (radius 7.5mm)
        circle = pt.buffer(7.5, resolution=32)
        
        # Blend smoothly into the straight 176mm flange edges starting 13mm back:
        c_box = sg.box(min(sx * 75.0, sx * half_plate), min(sy * 75.0, sy * half_plate),
                       max(sx * 75.0, sx * half_plate), max(sy * 75.0, sy * half_plate))
        ear_wing = unary_union([circle, c_box]).convex_hull
        ear_hulls.append(ear_wing)
    
    all_ears_union = unary_union(ear_hulls)
    hole_cutouts_union = unary_union(hole_cutouts)
    pocket_cutouts_union = unary_union(pocket_cutouts)
    
    # Base plate perimeter:
    base_plate_2d = unary_union([plate_box, all_ears_union])
    
    # -------------------------------------------------------------------------
    # Layer Slicing Geometry (Face-Down: Z=0 is Bed, Z=3 is Back/Felt Side):
    # -------------------------------------------------------------------------
    # 1. Base Floor (Z = 0.0 to 1.0mm, thickness 1.0mm):
    #    Spans full 176mm plate with 3.0mm through-holes. 100% FLAT against bed!
    floor_2d = base_plate_2d.difference(hole_cutouts_union)
    
    # 2. Lower Flange & Lower Frame Wall (Z = 1.0 to 1.8mm, thickness 0.8mm):
    #    Solid PETG under the pocket floor.
    ear_lower_2d = all_ears_union.difference(frame_outer_box).difference(hole_cutouts_union)
    
    # 3. Upper Ear Rim (Z = 1.8 to 3.0mm, thickness 1.2mm):
    #    Forms the 3.0mm tall outer rim of the corner tab, leaving the Ø13mm pocket open!
    ear_upper_rim_2d = all_ears_union.difference(frame_outer_box).difference(pocket_cutouts_union)
    
    # -------------------------------------------------------------------------
    # 3D Extrusion (Full Panel):
    # -------------------------------------------------------------------------
    # Floor: 0.0 to 1.0mm
    m_floor = extrude_shapely(floor_2d, 1.0)
    
    # Frame Wall: 1.0 to 3.0mm (height 2.0mm)
    m_walls = extrude_shapely(frame_wall_2d, 2.0)
    m_walls.apply_translation([0.0, 0.0, 1.0])
    
    # Ear Lower Solid (Z = 1.0 to 1.8mm, height 0.8mm)
    m_ear_lower = extrude_shapely(ear_lower_2d, 0.8)
    m_ear_lower.apply_translation([0.0, 0.0, 1.0])
    
    # Ear Upper Rim (Z = 1.8 to 3.0mm, height 1.2mm)
    m_ear_upper = extrude_shapely(ear_upper_rim_2d, 1.2)
    m_ear_upper.apply_translation([0.0, 0.0, 1.8])
    
    full_panel = trimesh.util.concatenate([m_floor, m_walls, m_ear_lower, m_ear_upper])
    full_panel.apply_translation([0.0, 0.0, -full_panel.bounds[0][2]])
    
    # Export Full Panel with Recessed Back:
    stl_path = os.path.join(out_dir, "test_all_black_16x16_panel_recessed_back.stl")
    mf3_path = os.path.join(out_dir, "test_all_black_16x16_panel_recessed_back.3mf")
    full_panel.export(stl_path)
    full_panel.export(mf3_path)
    print(f"Exported: {stl_path} | Verts: {len(full_panel.vertices)}, Faces: {len(full_panel.faces)}")
    print(f"  Dimensions: X={full_panel.extents[0]:.1f}mm, Y={full_panel.extents[1]:.1f}mm, Z={full_panel.extents[2]:.1f}mm")
    print(f"  Is watertight: {full_panel.is_watertight}")
    
    # -------------------------------------------------------------------------
    # 12-Minute Quick Corner Snap Coupon (Single Corner Test Piece):
    # -------------------------------------------------------------------------
    coupon_box = sg.box(50.0, 50.0, 100.0, 100.0)
    
    c_floor = extrude_shapely(floor_2d.intersection(coupon_box), 1.0)
    c_walls = extrude_shapely(frame_wall_2d.intersection(coupon_box), 2.0)
    c_walls.apply_translation([0.0, 0.0, 1.0])
    c_ear_lower = extrude_shapely(ear_lower_2d.intersection(coupon_box), 0.8)
    c_ear_lower.apply_translation([0.0, 0.0, 1.0])
    c_ear_upper = extrude_shapely(ear_upper_rim_2d.intersection(coupon_box), 1.2)
    c_ear_upper.apply_translation([0.0, 0.0, 1.8])
    
    coupon_mesh = trimesh.util.concatenate([c_floor, c_walls, c_ear_lower, c_ear_upper])
    coupon_mesh.apply_translation([-coupon_mesh.bounds[0][0], -coupon_mesh.bounds[0][1], -coupon_mesh.bounds[0][2]])
    
    coupon_stl = os.path.join(out_dir, "test_corner_snap_coupon_recessed_back.stl")
    coupon_3mf = os.path.join(out_dir, "test_corner_snap_coupon_recessed_back.3mf")
    coupon_mesh.export(coupon_stl)
    coupon_mesh.export(coupon_3mf)
    print(f"Exported: {coupon_stl} | Verts: {len(coupon_mesh.vertices)}, Faces: {len(coupon_mesh.faces)}")
    print(f"  Dimensions: X={coupon_mesh.extents[0]:.1f}mm, Y={coupon_mesh.extents[1]:.1f}mm, Z={coupon_mesh.extents[2]:.1f}mm")
    print(f"  Is watertight: {coupon_mesh.is_watertight}")

if __name__ == '__main__':
    build_recessed_back_panels()
