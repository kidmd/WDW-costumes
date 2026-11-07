import os, math
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh

# ==============================================================================
# 🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K)
# ALL-BLACK 16x16 MATRIX TEST PANEL GENERATOR
# Architecture: 176mm Extended Perimeter Flange + Integrated Snap Ears
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

def build_test_panels():
    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Geometric Specifications:
    # -------------------------------------------------------------------------
    CAVITY_SIZE = 160.4        # mm (fits 160x160mm BTF-Lighting matrix with 0.2mm perimeter tolerance)
    FRAME_WALL_WIDTH = 2.0     # mm
    FLOOR_THICKNESS = 1.0      # mm (solid black floor from Z = 0.0 to 1.0mm)
    POCKET_DEPTH = 2.0         # mm (frame wall height above floor, Z = 1.0 to 3.0mm)
    TOTAL_HEIGHT = FLOOR_THICKNESS + POCKET_DEPTH # 3.0 mm
    
    PLATE_BASE_WIDTH = 176.0   # mm (outer straight edge width, provides 5.8mm perimeter flange)
    SNAP_HOLE_DIA = 3.0        # mm (Ø 3.0mm loose clearance for KAM size 20 pin)
    SNAP_HOLE_RADIUS = SNAP_HOLE_DIA / 2.0 # 1.5 mm
    SNAP_EAR_THICKNESS = 2.0   # mm (solid PETG corner tab from Z = 0.0 to 2.0mm)
    
    # Coordinates centered at (0, 0):
    half_cav = CAVITY_SIZE / 2.0         # 80.2 mm
    half_frame = half_cav + FRAME_WALL_WIDTH # 82.2 mm
    half_plate = PLATE_BASE_WIDTH / 2.0  # 88.0 mm
    
    cavity_box = sg.box(-half_cav, -half_cav, half_cav, half_cav)
    frame_outer_box = sg.box(-half_frame, -half_frame, half_frame, half_frame)
    plate_box = sg.box(-half_plate, -half_plate, half_plate, half_plate)
    
    # Wire exit notch: 16mm wide, cuts through bottom frame wall
    wire_notch = sg.box(-8.0, -half_frame - 1.0, 8.0, -half_cav + 0.1)
    
    # 2.0mm Vertical Frame Wall Polygon (Z = 1.0 to 3.0mm):
    frame_wall_2d = frame_outer_box.difference(cavity_box).difference(wire_notch)
    
    # -------------------------------------------------------------------------
    # 176mm Extended Flange + Integrated Snap Ears:
    # -------------------------------------------------------------------------
    # Frame wall corner is at (±82.2, ±82.2).
    # Hole center requires 7.5mm diagonal clearance from frame wall corner:
    diag_clearance = 7.5 # mm
    diag_offset = diag_clearance * math.cos(math.radians(45)) # 5.303 mm
    hole_pos = half_frame + diag_offset # 87.503 mm
    
    corner_signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    hole_pts = []
    hole_cutouts = []
    ear_hulls = []
    ear_reinforce_polys = []
    
    for sx, sy in corner_signs:
        hx, hy = sx * hole_pos, sy * hole_pos
        pt = sg.Point(hx, hy)
        hole_pts.append(pt)
        hole_cutouts.append(pt.buffer(SNAP_HOLE_RADIUS, resolution=32))
        
        # 15mm diameter ear lobe around the hole (radius 7.5mm):
        circle = pt.buffer(7.5, resolution=32)
        ear_reinforce_polys.append(circle)
        
        # Blend smoothly into the straight 176mm flange edges starting 13mm back:
        c_box = sg.box(min(sx * 75.0, sx * half_plate), min(sy * 75.0, sy * half_plate),
                       max(sx * 75.0, sx * half_plate), max(sy * 75.0, sy * half_plate))
        ear_wing = unary_union([circle, c_box]).convex_hull
        ear_hulls.append(ear_wing)
    
    all_ears_union = unary_union(ear_hulls)
    hole_cutouts_union = unary_union(hole_cutouts)
    
    # Monolithic base plate (176mm straight sides + smooth corner wings):
    base_plate_2d = unary_union([plate_box, all_ears_union])
    
    # Floor polygon (Z = 0.0 to 1.0mm): spans full 176mm base plate with snap holes subtracted
    floor_2d = base_plate_2d.difference(hole_cutouts_union)
    
    # Snap ears solid flange (Z = 1.0 to 2.0mm):
    # Thickens the corner snap region outside the 2mm frame wall to 2.0mm total thickness!
    all_reinforce = unary_union(ear_reinforce_polys + ear_hulls)
    ear_flange_2d = all_reinforce.difference(frame_outer_box).difference(hole_cutouts_union)
    
    # -------------------------------------------------------------------------
    # 3D Extrusion & Assembly (Full Panel):
    # -------------------------------------------------------------------------
    # 1. Floor: 0.0 to 1.0mm (spans entire 176mm footprint including 5.8mm perimeter flange)
    m_floor = extrude_shapely(floor_2d, FLOOR_THICKNESS)
    
    # 2. 2.0mm Perimeter Frame Walls: 1.0 to 3.0mm (height 2.0mm)
    m_walls = extrude_shapely(frame_wall_2d, POCKET_DEPTH)
    m_walls.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    # 3. Snap Ears Solid Flange: 1.0 to 2.0mm (height 1.0mm)
    m_ears = extrude_shapely(ear_flange_2d, SNAP_EAR_THICKNESS - FLOOR_THICKNESS)
    m_ears.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    # Combine into monolithic mesh:
    full_panel = trimesh.util.concatenate([m_floor, m_walls, m_ears])
    full_panel.apply_translation([0.0, 0.0, -full_panel.bounds[0][2]])
    
    # Export Full All-Black Test Panel:
    full_stl_path = os.path.join(out_dir, "test_all_black_16x16_panel.stl")
    full_3mf_path = os.path.join(out_dir, "test_all_black_16x16_panel.3mf")
    full_panel.export(full_stl_path)
    full_panel.export(full_3mf_path)
    print(f"Exported: {full_stl_path} | Verts: {len(full_panel.vertices)}, Faces: {len(full_panel.faces)}")
    print(f"  Dimensions: X={full_panel.extents[0]:.1f}mm, Y={full_panel.extents[1]:.1f}mm, Z={full_panel.extents[2]:.1f}mm")
    print(f"  Is watertight: {full_panel.is_watertight}")
    
    # -------------------------------------------------------------------------
    # 12-Minute Quick Corner Snap Coupon (Single Corner Test Piece):
    # -------------------------------------------------------------------------
    # Crop a 50mm x 50mm region around the top-right corner [50, 100] x [50, 100]
    coupon_box = sg.box(50.0, 50.0, 100.0, 100.0)
    
    coupon_floor_2d = floor_2d.intersection(coupon_box)
    coupon_walls_2d = frame_wall_2d.intersection(coupon_box)
    coupon_ears_2d = ear_flange_2d.intersection(coupon_box)
    
    c_floor = extrude_shapely(coupon_floor_2d, FLOOR_THICKNESS)
    c_walls = extrude_shapely(coupon_walls_2d, POCKET_DEPTH)
    c_walls.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    c_ears = extrude_shapely(coupon_ears_2d, SNAP_EAR_THICKNESS - FLOOR_THICKNESS)
    c_ears.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    coupon_mesh = trimesh.util.concatenate([c_floor, c_walls, c_ears])
    coupon_mesh.apply_translation([-coupon_mesh.bounds[0][0], -coupon_mesh.bounds[0][1], -coupon_mesh.bounds[0][2]])
    
    coupon_stl_path = os.path.join(out_dir, "test_corner_snap_coupon.stl")
    coupon_3mf_path = os.path.join(out_dir, "test_corner_snap_coupon.3mf")
    coupon_mesh.export(coupon_stl_path)
    coupon_mesh.export(coupon_3mf_path)
    print(f"Exported: {coupon_stl_path} | Verts: {len(coupon_mesh.vertices)}, Faces: {len(coupon_mesh.faces)}")
    print(f"  Dimensions: X={coupon_mesh.extents[0]:.1f}mm, Y={coupon_mesh.extents[1]:.1f}mm, Z={coupon_mesh.extents[2]:.1f}mm")
    print(f"  Is watertight: {coupon_mesh.is_watertight}")

if __name__ == '__main__':
    build_test_panels()
