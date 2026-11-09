import os, math
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh

# ==============================================================================
# 🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K)
# DEEPER RECESSED SNAP TAB TEST COUPON GENERATOR (0.6mm & 0.4mm FLOORS)
# Solves: Gives +0.4mm to +0.6mm more pin protrusion for massive mushroom heads
# ==============================================================================

def extrude_shapely(shape, height):
    """Extrude any 2D shapely geometry into a watertight Trimesh."""
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

def make_coupon(floor_thick, total_height=3.0):
    """Builds a corner test coupon with a specific floor thickness and recess depth."""
    CAVITY_SIZE = 160.4
    FRAME_WALL_WIDTH = 2.0
    PLATE_BASE_WIDTH = 176.0
    
    SNAP_HOLE_RADIUS = 3.2 / 2.0  # 1.6 mm
    RECESSED_POCKET_RADIUS = 14.0 / 2.0 # 7.0 mm
    
    half_cav = CAVITY_SIZE / 2.0             # 80.2 mm
    half_frame = half_cav + FRAME_WALL_WIDTH # 82.2 mm
    half_plate = PLATE_BASE_WIDTH / 2.0      # 88.0 mm
    
    cavity_box = sg.box(-half_cav, -half_cav, half_cav, half_cav)
    frame_outer_box = sg.box(-half_frame, -half_frame, half_frame, half_frame)
    plate_box = sg.box(-half_plate, -half_plate, half_plate, half_plate)
    
    frame_wall_2d = frame_outer_box.difference(cavity_box)
    
    diag_clearance = 7.5
    diag_offset = diag_clearance * math.cos(math.radians(45)) # 5.303 mm
    hx = half_frame + diag_offset # 87.503 mm
    hy = half_frame + diag_offset # 87.503 mm
    hole_pt = sg.Point(hx, hy)
    
    hole_cutout = hole_pt.buffer(SNAP_HOLE_RADIUS, resolution=64)
    pocket_cutout = hole_pt.buffer(RECESSED_POCKET_RADIUS, resolution=64)
    
    ear_circle = hole_pt.buffer(7.5, resolution=64)
    c_box = sg.box(75.0, 75.0, half_plate, half_plate)
    ear_wing = unary_union([ear_circle, c_box]).convex_hull
    
    base_plate_2d = unary_union([plate_box, ear_wing])
    coupon_box = sg.box(50.0, 50.0, 100.0, 100.0)
    
    coupon_floor_2d = base_plate_2d.difference(hole_cutout).intersection(coupon_box)
    coupon_wall_2d = frame_wall_2d.intersection(coupon_box)
    ear_rim_2d = ear_wing.difference(frame_outer_box).difference(pocket_cutout).intersection(coupon_box)
    
    wall_height = total_height - floor_thick
    
    m_floor = extrude_shapely(coupon_floor_2d, floor_thick)
    m_wall = extrude_shapely(coupon_wall_2d, wall_height)
    m_wall.apply_translation([0.0, 0.0, floor_thick])
    m_rim = extrude_shapely(ear_rim_2d, wall_height)
    m_rim.apply_translation([0.0, 0.0, floor_thick])
    
    mesh = trimesh.util.concatenate([m_floor, m_wall, m_rim])
    mesh.apply_translation([-mesh.bounds[0][0], -mesh.bounds[0][1], -mesh.bounds[0][2]])
    return mesh

def main():
    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. 0.6mm floor (recess depth 2.4mm, 3 layers @ 0.2mm) - +0.4mm extra pin length!
    c_06 = make_coupon(0.60)
    stl_06 = os.path.join(out_dir, "test_coupon_0.6mm_recessed_tab.stl")
    mf3_06 = os.path.join(out_dir, "test_coupon_0.6mm_recessed_tab.3mf")
    c_06.export(stl_06)
    export_3mf_with_100_infill(c_06, mf3_06, "MSEP_Coupon_0.6mm_Recessed")
    print(f"Exported: {stl_06} | Watertight: {c_06.is_watertight}")
    
    # 2. 0.4mm floor (recess depth 2.6mm, 2 layers @ 0.2mm) - +0.6mm extra pin length!
    c_04 = make_coupon(0.40)
    stl_04 = os.path.join(out_dir, "test_coupon_0.4mm_recessed_tab.stl")
    mf3_04 = os.path.join(out_dir, "test_coupon_0.4mm_recessed_tab.3mf")
    c_04.export(stl_04)
    export_3mf_with_100_infill(c_04, mf3_04, "MSEP_Coupon_0.4mm_Recessed")
    print(f"Exported: {stl_04} | Watertight: {c_04.is_watertight}")
    
    # 3. Combo Plate: Both side-by-side with 15mm gap (single ~12 min print)
    c_06_copy = c_06.copy()
    c_04_copy = c_04.copy()
    shift_x = c_06_copy.extents[0] + 15.0
    c_04_copy.apply_translation([shift_x, 0.0, 0.0])
    
    combo = trimesh.util.concatenate([c_06_copy, c_04_copy])
    combo.apply_translation([-combo.bounds[0][0], -combo.bounds[0][1], -combo.bounds[0][2]])
    stl_combo = os.path.join(out_dir, "test_coupon_deep_recess_combo.stl")
    mf3_combo = os.path.join(out_dir, "test_coupon_deep_recess_combo.3mf")
    combo.export(stl_combo)
    export_3mf_with_100_infill(combo, mf3_combo, "MSEP_Coupons_Deep_Recess_Combo")
    print(f"Exported: {stl_combo} | Watertight: {combo.is_watertight}")

if __name__ == '__main__':
    main()
