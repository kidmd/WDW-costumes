import os, math
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh

# ==============================================================================
# 🏰 MAIN STREET ELECTRICAL PARADE (WDW 10K)
# 16x16 MATRIX TEST PANEL - ALL-BLACK 0.6mm DEEP RECESSED TAB STANDARD
# Features:
#  - 100% Flat Front Face against PEI Bed (Zero Bridging / Zero Supports)
#  - 176mm Extended Perimeter Flange (5.8mm horizontal border)
#  - 3.0mm Flush Back Rim (Corner tabs flush with 2mm frame wall)
#  - Ø 14.0mm x 2.4mm Deep Recessed Pocket on the BACK (Felt Side)
#  - 0.6mm Solid PETG Floor under Snap Cap (Gives +0.4mm More Pin Protrusion)
#  - Ø 3.2mm Through-Holes for Snag-Free Pin Insertion
#  - 16mm Bottom Wire Exit Notch for JST Matrix Power / Data Harness
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

def export_3mf_with_100_infill(mesh, mf3_path, obj_name="MSEP_Solid_Panel"):
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

def build_recessed_back_panels(floor_thick=0.60):
    out_dir = '3d_panels'
    os.makedirs(out_dir, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Geometric Specifications:
    # -------------------------------------------------------------------------
    CAVITY_SIZE = 160.4          # mm (fits 160x160mm BTF-Lighting matrix with 0.2mm tolerance)
    FRAME_WALL_WIDTH = 2.0       # mm
    PLATE_BASE_WIDTH = 176.0     # mm (5.8mm perimeter flange around frame walls)
    
    FLOOR_THICKNESS = floor_thick # mm (0.60mm solid black floor, 3 layers @ 0.20mm)
    TOTAL_HEIGHT = 3.00          # mm (top rim flush)
    WALL_HEIGHT = TOTAL_HEIGHT - FLOOR_THICKNESS # 2.40 mm
    
    SNAP_THROUGH_HOLE_DIA = 3.2  # mm (Ø 3.2mm snag-free clearance for KAM size 20 pin)
    SNAP_HOLE_RADIUS = SNAP_THROUGH_HOLE_DIA / 2.0 # 1.6 mm
    
    RECESSED_POCKET_DIA = 14.0   # mm (Ø 14.0mm well for KAM snap socket & plier die)
    RECESSED_POCKET_RADIUS = RECESSED_POCKET_DIA / 2.0 # 7.0 mm
    
    half_cav = CAVITY_SIZE / 2.0             # 80.2 mm
    half_frame = half_cav + FRAME_WALL_WIDTH # 82.2 mm
    half_plate = PLATE_BASE_WIDTH / 2.0      # 88.0 mm
    
    cavity_box = sg.box(-half_cav, -half_cav, half_cav, half_cav)
    frame_outer_box = sg.box(-half_frame, -half_frame, half_frame, half_frame)
    plate_box = sg.box(-half_plate, -half_plate, half_plate, half_plate)
    
    # Wire notch: 16mm wide, cuts bottom frame wall
    wire_notch = sg.box(-8.0, -half_frame - 1.0, 8.0, -half_cav + 0.1)
    
    # Frame wall polygon (Z = FLOOR_THICKNESS to 3.0mm):
    frame_wall_2d = frame_outer_box.difference(cavity_box).difference(wire_notch)
    
    # Corner Snap Wings (4 Corners):
    diag_clearance = 7.5
    diag_offset = diag_clearance * math.cos(math.radians(45)) # 5.303 mm
    hole_pos = half_frame + diag_offset # 87.503 mm
    
    corner_signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    hole_cutouts = []
    pocket_cutouts = []
    ear_hulls = []
    
    for sx, sy in corner_signs:
        hx, hy = sx * hole_pos, sy * hole_pos
        pt = sg.Point(hx, hy)
        hole_cutouts.append(pt.buffer(SNAP_HOLE_RADIUS, resolution=64))
        pocket_cutouts.append(pt.buffer(RECESSED_POCKET_RADIUS, resolution=64))
        
        circle = pt.buffer(7.5, resolution=64)
        c_box = sg.box(min(sx * 75.0, sx * half_plate), min(sy * 75.0, sy * half_plate),
                       max(sx * 75.0, sx * half_plate), max(sy * 75.0, sy * half_plate))
        ear_wing = unary_union([circle, c_box]).convex_hull
        ear_hulls.append(ear_wing)
    
    all_ears_union = unary_union(ear_hulls)
    hole_cutouts_union = unary_union(hole_cutouts)
    pocket_cutouts_union = unary_union(pocket_cutouts)
    
    base_plate_2d = unary_union([plate_box, all_ears_union])
    
    # Floor polygon (Z = 0.0 to FLOOR_THICKNESS):
    floor_2d = base_plate_2d.difference(hole_cutouts_union)
    
    # Upper Ear Rim (Z = FLOOR_THICKNESS to 3.0mm):
    ear_rim_2d = all_ears_union.difference(frame_outer_box).difference(pocket_cutouts_union)
    
    m_floor = extrude_shapely(floor_2d, FLOOR_THICKNESS)
    m_walls = extrude_shapely(frame_wall_2d, WALL_HEIGHT)
    m_walls.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    m_ear_rim = extrude_shapely(ear_rim_2d, WALL_HEIGHT)
    m_ear_rim.apply_translation([0.0, 0.0, FLOOR_THICKNESS])
    
    full_panel = trimesh.util.concatenate([m_floor, m_walls, m_ear_rim])
    full_panel.apply_translation([0.0, 0.0, -full_panel.bounds[0][2]])
    
    targets = [
        ("test_all_black_16x16_panel_recessed_0.6mm", "MSEP_16x16_Panel_0.6mm_Recessed"),
        ("test_all_black_16x16_panel_recessed_back", "MSEP_16x16_Panel_Recessed_Back")
    ]
    
    for base_name, label in targets:
        stl_path = os.path.join(out_dir, f"{base_name}.stl")
        mf3_path = os.path.join(out_dir, f"{base_name}.3mf")
        full_panel.export(stl_path)
        export_3mf_with_100_infill(full_panel, mf3_path, label)
        print(f"Exported: {stl_path} | Watertight: {full_panel.is_watertight}")
        print(f"  Bounds: X={full_panel.extents[0]:.2f}mm, Y={full_panel.extents[1]:.2f}mm, Z={full_panel.extents[2]:.2f}mm")
        print(f"  Floor: {FLOOR_THICKNESS:.2f}mm | Recess Depth: {WALL_HEIGHT:.2f}mm")

if __name__ == '__main__':
    build_recessed_back_panels(floor_thick=0.60)
