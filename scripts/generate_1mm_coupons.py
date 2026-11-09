import os, math
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh

# ==============================================================================
# 🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K)
# 1.0mm SNAP TAB TEST COUPON GENERATOR
# Coupons:
#  1. test_coupon_1mm_flat_tab (Flat 1.0mm ear, zero recess, maximum plier clearance)
#  2. test_coupon_1mm_recessed_tab (1.0mm floor inside Ø14.0mm counterbore pocket)
#  3. test_coupon_1mm_combo_both (Both side-by-side on single plate)
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

def export_3mf_with_100_infill(mesh, mf3_path, obj_name="MSEP_Coupon"):
    """Exports trimesh as 3MF and injects slicer metadata for 100% solid infill and 5 wall loops."""
    import zipfile, xml.etree.ElementTree as ET
    
    mesh.export(mf3_path)
    try:
        with zipfile.ZipFile(mf3_path, 'r') as zin:
            files_data = {name: zin.read(name) for name in zin.namelist()}
        
        ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
        root = ET.fromstring(files_data['3D/3dmodel.model'])
        resources = root.find(f"{{{ns}}}resources")
        objs = resources.findall(f"{{{ns}}}object") if resources is not None else []
        obj_id = objs[0].attrib.get('id', '1') if objs else '1'
        
        cfg_root = ET.Element('config')
        plate_elem = ET.SubElement(cfg_root, 'plate')
        ET.SubElement(plate_elem, 'metadata', {'key': 'plater_id', 'value': '1'})
        
        obj_elem = ET.SubElement(cfg_root, 'object', {'id': obj_id})
        ET.SubElement(obj_elem, 'metadata', {'key': 'name', 'value': obj_name})
        ET.SubElement(obj_elem, 'metadata', {'key': 'sparse_infill_density', 'value': '100%'})
        ET.SubElement(obj_elem, 'metadata', {'key': 'wall_loops', 'value': '5'})
        ET.SubElement(obj_elem, 'metadata', {'key': 'bottom_shell_layers', 'value': '15'})
        ET.SubElement(obj_elem, 'metadata', {'key': 'top_shell_layers', 'value': '15'})
        
        part_elem = ET.SubElement(obj_elem, 'part', {'id': obj_id, 'subtype': 'normal_part'})
        ET.SubElement(part_elem, 'metadata', {'key': 'name', 'value': obj_name})
        ET.SubElement(part_elem, 'metadata', {'key': 'sparse_infill_density', 'value': '100%'})
        ET.SubElement(part_elem, 'metadata', {'key': 'wall_loops', 'value': '5'})
        ET.SubElement(part_elem, 'metadata', {'key': 'bottom_shell_layers', 'value': '15'})
        ET.SubElement(part_elem, 'metadata', {'key': 'top_shell_layers', 'value': '15'})
        
        files_data['Metadata/model_settings.config'] = ET.tostring(cfg_root, encoding='utf-8', xml_declaration=True)
        
        if '[Content_Types].xml' in files_data:
            ct_xml = files_data['[Content_Types].xml'].decode('utf-8')
            if 'Metadata/model_settings.config' not in ct_xml:
                ct_insert = '<Override PartName="/Metadata/model_settings.config" ContentType="application/vnd.ms-package.config+xml"/>\n</Types>'
                ct_xml = ct_xml.replace('</Types>', ct_insert)
                files_data['[Content_Types].xml'] = ct_xml.encode('utf-8')
                
        tmp_path = mf3_path + '.tmp'
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for name, content in files_data.items():
                zout.writestr(name, content)
        os.replace(tmp_path, mf3_path)
    except Exception as e:
        print(f"Metadata injection warning on {mf3_path}: {e}")

def create_coupons():
    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Geometric Specifications:
    # -------------------------------------------------------------------------
    CAVITY_SIZE = 160.4          # mm
    FRAME_WALL_WIDTH = 2.0       # mm
    PLATE_BASE_WIDTH = 176.0     # mm
    FLOOR_THICKNESS = 1.0        # mm (Z = 0.0 to 1.0mm)
    WALL_HEIGHT = 2.0            # mm (Z = 1.0 to 3.0mm, total height = 3.0mm)
    
    SNAP_HOLE_DIA = 3.2          # mm (Ø 3.2mm clean clearance for KAM size 20 pin)
    SNAP_HOLE_RADIUS = SNAP_HOLE_DIA / 2.0
    
    RECESSED_POCKET_DIA = 14.0   # mm (Ø 14.0mm generous pocket for snap socket & plier die)
    RECESSED_POCKET_RADIUS = RECESSED_POCKET_DIA / 2.0
    
    half_cav = CAVITY_SIZE / 2.0         # 80.2 mm
    half_frame = half_cav + FRAME_WALL_WIDTH # 82.2 mm
    half_plate = PLATE_BASE_WIDTH / 2.0  # 88.0 mm
    
    cavity_box = sg.box(-half_cav, -half_cav, half_cav, half_cav)
    frame_outer_box = sg.box(-half_frame, -half_frame, half_frame, half_frame)
    plate_box = sg.box(-half_plate, -half_plate, half_plate, half_plate)
    
    # Frame wall polygon (Z = 1.0 to 3.0mm)
    frame_wall_2d = frame_outer_box.difference(cavity_box)
    
    # Top-right corner (sx=1, sy=1):
    diag_clearance = 7.5
    diag_offset = diag_clearance * math.cos(math.radians(45)) # 5.303 mm
    hx = half_frame + diag_offset # 87.503 mm
    hy = half_frame + diag_offset # 87.503 mm
    hole_pt = sg.Point(hx, hy)
    
    hole_cutout = hole_pt.buffer(SNAP_HOLE_RADIUS, resolution=64)
    pocket_cutout = hole_pt.buffer(RECESSED_POCKET_RADIUS, resolution=64)
    
    # Ear lobe (15mm diameter circle around hole center):
    ear_circle = hole_pt.buffer(7.5, resolution=64)
    c_box = sg.box(75.0, 75.0, half_plate, half_plate)
    ear_wing = unary_union([ear_circle, c_box]).convex_hull
    
    # Base perimeter
    base_plate_2d = unary_union([plate_box, ear_wing])
    
    # Crop box for coupon: [50, 100] x [50, 100]
    coupon_box = sg.box(50.0, 50.0, 100.0, 100.0)
    
    # Coupon 2D components:
    # 1. Base floor (Z = 0.0 to 1.0mm) with through-hole
    coupon_floor_2d = base_plate_2d.difference(hole_cutout).intersection(coupon_box)
    
    # 2. Frame wall (Z = 1.0 to 3.0mm)
    coupon_wall_2d = frame_wall_2d.intersection(coupon_box)
    
    # 3. Recessed upper rim (Z = 1.0 to 3.0mm, only outside frame wall and outside pocket)
    ear_rim_2d = ear_wing.difference(frame_outer_box).difference(pocket_cutout).intersection(coupon_box)
    
    # -------------------------------------------------------------------------
    # BUILD COUPON 1: Flat 1.0mm Tab (No Recess)
    # -------------------------------------------------------------------------
    # Extrude floor (0 to 1.0mm) and frame wall (1.0 to 3.0mm). Tab is strictly 1.0mm!
    m1_floor = extrude_shapely(coupon_floor_2d, FLOOR_THICKNESS)
    m1_wall = extrude_shapely(coupon_wall_2d, WALL_HEIGHT)
    m1_wall.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    coupon_flat = trimesh.util.concatenate([m1_floor, m1_wall])
    # Zero origin at (0, 0, 0):
    coupon_flat.apply_translation([-coupon_flat.bounds[0][0], -coupon_flat.bounds[0][1], -coupon_flat.bounds[0][2]])
    
    # -------------------------------------------------------------------------
    # BUILD COUPON 2: 1.0mm Tab with Recessed Pocket
    # -------------------------------------------------------------------------
    # Floor: 0 to 1.0mm (with hole)
    # Frame wall: 1.0 to 3.0mm
    # Ear rim: 1.0 to 3.0mm (leaves Ø14mm pocket open with 1.0mm floor at bottom)
    m2_floor = extrude_shapely(coupon_floor_2d, FLOOR_THICKNESS)
    m2_wall = extrude_shapely(coupon_wall_2d, WALL_HEIGHT)
    m2_wall.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    m2_rim = extrude_shapely(ear_rim_2d, WALL_HEIGHT)
    m2_rim.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    coupon_recessed = trimesh.util.concatenate([m2_floor, m2_wall, m2_rim])
    coupon_recessed.apply_translation([-coupon_recessed.bounds[0][0], -coupon_recessed.bounds[0][1], -coupon_recessed.bounds[0][2]])
    
    # -------------------------------------------------------------------------
    # BUILD COMBO PLATE: Both Side-by-Side
    # -------------------------------------------------------------------------
    c_flat_copy = coupon_flat.copy()
    c_rec_copy = coupon_recessed.copy()
    # Offset recessed coupon along X by width + 15mm gap:
    shift_x = c_flat_copy.extents[0] + 15.0
    c_rec_copy.apply_translation([shift_x, 0.0, 0.0])
    
    combo_mesh = trimesh.util.concatenate([c_flat_copy, c_rec_copy])
    combo_mesh.apply_translation([-combo_mesh.bounds[0][0], -combo_mesh.bounds[0][1], -combo_mesh.bounds[0][2]])
    
    # -------------------------------------------------------------------------
    # Export all files:
    # -------------------------------------------------------------------------
    files_to_export = [
        ("test_coupon_1mm_flat_tab", coupon_flat, "MSEP_Coupon_1mm_Flat"),
        ("test_coupon_1mm_recessed_tab", coupon_recessed, "MSEP_Coupon_1mm_Recessed"),
        ("test_coupon_1mm_combo_both", combo_mesh, "MSEP_Coupons_1mm_Combo")
    ]
    
    for base_name, mesh, label in files_to_export:
        stl_path = os.path.join(out_dir, f"{base_name}.stl")
        mf3_path = os.path.join(out_dir, f"{base_name}.3mf")
        mesh.export(stl_path)
        export_3mf_with_100_infill(mesh, mf3_path, label)
        print(f"Exported {base_name}:")
        print(f"  Bounds: X={mesh.extents[0]:.2f}mm, Y={mesh.extents[1]:.2f}mm, Z={mesh.extents[2]:.2f}mm")
        print(f"  Watertight: {mesh.is_watertight}")
        print(f"  Faces: {len(mesh.faces)}, Vertices: {len(mesh.vertices)}")

if __name__ == '__main__':
    create_coupons()
