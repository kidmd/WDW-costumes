import os, math
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh

# ==============================================================================
# 🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K)
# ALL-BLACK 16x16 MATRIX TEST PANEL GENERATOR (SOLID CORNER WINGS v2)
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
    # Geometric Parameters:
    # -------------------------------------------------------------------------
    CAVITY_SIZE = 160.4        # mm (fits 160x160mm BTF-Lighting matrix with 0.2mm side tolerance)
    FRAME_WALL_WIDTH = 2.0     # mm
    FLOOR_THICKNESS = 1.0      # mm (solid black floor from Z = 0.0 to 1.0mm)
    POCKET_DEPTH = 2.0         # mm (frame wall height above floor, Z = 1.0 to 3.0mm)
    TOTAL_HEIGHT = FLOOR_THICKNESS + POCKET_DEPTH # 3.0 mm
    
    SNAP_HOLE_DIA = 3.0        # mm (Ø 3.0mm loose clearance for KAM size 20 pin)
    SNAP_HOLE_RADIUS = SNAP_HOLE_DIA / 2.0 # 1.5 mm
    SNAP_EAR_THICKNESS = 2.0   # mm (solid PETG corner tab from Z = 0.0 to 2.0mm)
    
    # Inner cavity bounds (centered at 0, 0):
    half_cav = CAVITY_SIZE / 2.0 # 80.2 mm
    cavity_box = sg.box(-half_cav, -half_cav, half_cav, half_cav)
    
    # Outer frame wall bounds:
    half_frame = half_cav + FRAME_WALL_WIDTH # 82.2 mm
    frame_outer_box = sg.box(-half_frame, -half_frame, half_frame, half_frame)
    
    # Wire exit notch: 16mm wide, cuts through bottom frame wall
    wire_notch = sg.box(-8.0, -half_frame - 1.0, 8.0, -half_cav + 0.1)
    
    # Frame wall polygon (Z = 1.0 to 3.0mm):
    frame_wall_2d = frame_outer_box.difference(cavity_box).difference(wire_notch)
    
    # -------------------------------------------------------------------------
    # Solid Corner Snap Wings Design (Wide Tangent Gusset):
    # -------------------------------------------------------------------------
    # Outer frame wall corner is at (±82.2, ±82.2).
    # To clear a 12.2mm snap cap (radius 6.1mm) and 14mm plier die (radius 7.0mm),
    # the hole center is stepped outward along the diagonal by 8.0mm.
    diag_step = 8.0
    hole_offset = half_frame + diag_step * math.cos(math.radians(45)) # 82.2 + 5.657 = 87.857 mm
    
    corner_signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    ear_hulls = []
    hole_cutouts = []
    
    # We bridge the corner lobes into the straight edges starting from 14mm back (X, Y = 68.0mm)
    # using a convex hull. This creates a solid 20mm+ wide tangent wing at every corner!
    for sx, sy in corner_signs:
        hx, hy = sx * hole_offset, sy * hole_offset
        pt = sg.Point(hx, hy)
        hole_cutouts.append(pt.buffer(SNAP_HOLE_RADIUS, resolution=32))
        
        # 16mm circular ear around the hole
        circle = pt.buffer(8.0, resolution=32)
        
        # Sub-box of the plate corner extending 14mm along each straight edge
        c_box = sg.box(min(sx * 68.0, sx * half_frame), min(sy * 68.0, sy * half_frame),
                       max(sx * 68.0, sx * half_frame), max(sy * 68.0, sy * half_frame))
        
        # Convex hull blends the straight wall seamlessly into the ear circle:
        wing_hull = unary_union([circle, c_box]).convex_hull
        ear_hulls.append(wing_hull)
    
    all_ears_union = unary_union(ear_hulls)
    hole_cutouts_union = unary_union(hole_cutouts)
    
    # Monolithic base plate perimeter:
    base_plate_2d = unary_union([frame_outer_box, all_ears_union])
    
    # Floor polygon (Z = 0.0 to 1.0mm): spans full base plate with snap holes subtracted
    floor_2d = base_plate_2d.difference(hole_cutouts_union)
    
    # Snap ears solid flange (Z = 1.0 to 2.0mm):
    # Thickens the entire corner wing outside the 2.0mm frame wall to 2.0mm total thickness!
    ear_flange_2d = all_ears_union.difference(frame_outer_box).difference(hole_cutouts_union)
    
    # -------------------------------------------------------------------------
    # 3D Extrusion & Assembly (Full Panel):
    # -------------------------------------------------------------------------
    # 1. Floor: 0.0 to 1.0mm
    m_floor = extrude_shapely(floor_2d, FLOOR_THICKNESS)
    
    # 2. Frame Walls: 1.0 to 3.0mm (height 2.0mm)
    m_walls = extrude_shapely(frame_wall_2d, POCKET_DEPTH)
    m_walls.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    # 3. Snap Wings Solid Flange: 1.0 to 2.0mm (height 1.0mm)
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
