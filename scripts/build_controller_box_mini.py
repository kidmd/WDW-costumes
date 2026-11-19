"""
Parametric 3D CAD Generator — WDW 10K MSEP ULTRA-MINI No-WAGO Zero-Solder Controller Box.

Smallest possible zero-solder enclosure for the 38-pin ESP32 Screw Terminal Breakout (B0DYD168RC):
  - Outer Dimensions: 72.0 x 98.5 x 23.5 mm (4.0mm thinner than V6, ~35% smaller than 5-port WAGO!)
  - Zero WAGOs: USB-C Red (+5V) & LED Red (+5V) twist together directly into the breakout's 5V
    screw terminal; USB-C Black & LED Black twist into one GND screw terminal; Button 1 & 2
    grounds use the breakout board's other two spare GND screw terminals!
  - -Y Main Bay: 63 x 78 mm 38-pin Screw Terminal Breakout (B0DYD168RC) + 2.5mm side wire channels
    (pre-wire the 5 screw terminals outside the box, then drop the board straight in!) + ESP USB-C cutout.
  - +Y Mini-Bay (16.1mm deep): Centered M12 panel-mount USB-C (B0CXLZBD2V, Ø 12.3mm),
    offset LED cable U-notch (X = +11.5mm), and 2x APIELE PBS-33B 12mm waterproof buttons
    (B09V2KZZ8W) in the lid at X = ±23.0mm, Y = +39.4mm.
  - Tool-Free Snap-Fit Lid: Prints flat upside-down with zero supports!
"""

from __future__ import annotations

import json
from pathlib import Path
import zipfile

import cv2
import manifold3d as m3d
import numpy as np
import trimesh


CFG = {
    # Ultra-mini outer envelope: 72.0 x 98.5 x 23.5 mm!
    "outer_w": 72.0,          # X width: 63.4mm breakout + 2x 2.5mm wire channels + 2x 1.8mm walls
    "outer_l": 98.5,          # Y length: 78.4mm breakout + 16.1mm +Y mini-bay + walls
    "base_h": 21.3,           # Z height of base tub (19.7mm inner height clears ESP32 + PBS-33B + M12 nut!)
    "lid_h": 2.2,             # Z thickness of flat snap-fit lid (total assembled height = 23.5mm!)
    "wall": 1.8,              # Perimeter wall thickness (4 perimeters w/ 0.4mm nozzle)
    "floor": 1.6,             # Bottom floor thickness
    "corner_r": 3.5,          # Smooth FlipBelt-friendly rounded corners

    # Snap-fit lid lip & compliant hook latches (zero screws!)
    "lip_h": 1.6,             # Inner registration lip height
    "lip_clearance": 0.25,    # XY gap between lid lip and inner wall
    "snap_overhang": 0.65,    # Snap bead protrusion into wall groove
    "snap_w": 9.0,            # Width of each snap-hook tab
    "snap_z_from_top": 3.2,   # Groove center below base rim
    "snap_ys": [-26.0, 14.0], # 4 latches (2 on -X wall, 2 on +X wall)

    # Zone A (-Y Bay): 63 x 78 mm 38-Pin ESP32 Screw Terminal Breakout Board (B0DYD168RC)
    "brk_w": 63.4,            # 63.0mm PCB + 0.4mm fit tolerance
    "brk_l": 78.4,            # 78.0mm PCB + 0.4mm fit tolerance
    "brk_standoff_h": 1.6,    # Floor rail height clearing underside solder pins
    "brk_pcb_h": 1.6,         # Breakout PCB thickness
    "esp_usb_w": 13.5,        # ESP32 onboard USB-C reflash cutout width (-Y wall)
    "esp_usb_h": 7.4,         # Cutout height
    "esp_usb_z_center": 15.8, # Aligned with plugged-in 38-pin ESP32 USB-C port

    # Zone B (+Y Mini-Bay): M12 Panel-Mount USB-C (B0CXLZBD2V) + LED U-Notch
    "usbc_hole_d": 12.3,      # Ø 12.0mm M12 panel-mount USB-C + 0.3mm FDM tolerance
    "usbc_x": 0.0,            # Centered on +Y wall
    "usbc_z_center": 11.5,    # Centered in the 19.7mm inner height (clears floor & lid!)
    "led_exit_x": 11.5,       # Cleanly between USB-C (X=0) and Button 2 (X=+23.0)
    "wire_notch_w": 5.0,      # 3-wire LED cable U-notch width
    "wire_notch_h": 3.2,      # U-notch depth from top rim

    # Zone C (Lid Top Face): 2x APIELE PBS-33B 12mm Waterproof Buttons (B09V2KZZ8W)
    "btn_hole_d": 12.3,       # Ø 12.0mm threaded PBS-33B + 0.3mm FDM tolerance
    "btn1_x": -23.0,          # Button 1 (1 SHOW - GPIO 4)
    "btn2_x": 23.0,           # Button 2 (2 PHOTO - GPIO 33)
    "btn_y": 39.4,            # Centered in the 16.1mm +Y mini-bay (clears breakout PCB & +Y wall!)
}


def rounded_rect_cs(w: float, l: float, r: float, segments: int = 32) -> m3d.CrossSection:
    r = min(r, w / 2.0 - 0.01, l / 2.0 - 0.01)
    hw, hl = w / 2.0 - r, l / 2.0 - r
    pts = []
    for cx, cy, start_deg in [
        (hw, hl, 0),
        (-hw, hl, 90),
        (-hw, -hl, 180),
        (hw, -hl, 270),
    ]:
        for i in range(segments // 4 + 1):
            ang = np.deg2rad(start_deg + i * 90.0 / (segments // 4))
            pts.append([cx + r * np.cos(ang), cy + r * np.sin(ang)])
    return m3d.CrossSection([pts])


def rot_x_90(m: m3d.Manifold) -> m3d.Manifold:
    return m.transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0]], dtype=np.float64))


def rot_x_180(m: m3d.Manifold) -> m3d.Manifold:
    return m.transform(np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0]], dtype=np.float64))


def rot_z_180(m: m3d.Manifold) -> m3d.Manifold:
    return m.transform(np.array([[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0]], dtype=np.float64))


def make_cylinder(height: float, radius: float, circular_segments: int = 40, center: bool = False) -> m3d.Manifold:
    cyl = m3d.CrossSection.circle(radius, circular_segments).extrude(height)
    if center:
        cyl = cyl.translate([0, 0, -height / 2.0])
    return cyl


def make_cylinder_y(radius: float, length: float, segments: int = 48) -> m3d.Manifold:
    return rot_x_90(make_cylinder(length, radius, circular_segments=segments, center=True))


def rounded_slot_y_cutout(w: float, h: float, depth: float) -> m3d.Manifold:
    r = min(w, h) / 2.0 * 0.45
    cs = rounded_rect_cs(w, h, r, segments=24)
    return rot_x_90(cs.extrude(depth, n_divisions=1).translate([0, 0, -depth / 2.0]))


def build_text_cs(text: str, target_h: float) -> m3d.CrossSection:
    canvas = np.zeros((180, 720), dtype=np.uint8)
    cv2.putText(canvas, text, (16, 135), cv2.FONT_HERSHEY_SIMPLEX, 3.6, 255, 14, cv2.LINE_AA)
    binary = (canvas > 128).astype(np.uint8)
    cnts, _ = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    for cnt in cnts:
        if cv2.contourArea(cnt) < 15:
            continue
        approx = cv2.approxPolyDP(cnt, 0.8, True).reshape(-1, 2)
        if len(approx) >= 3:
            polys.append([[float(x), float(-y)] for x, y in approx])
    cs = m3d.CrossSection(polys, m3d.FillRule.EvenOdd)
    min_x, min_y, max_x, max_y = cs.bounds()
    scale = target_h / max(max_y - min_y, 1e-3)
    cx, cy = (min_x + max_x) / 2.0, (min_y + max_y) / 2.0
    return cs.translate([-cx, -cy]).scale([scale, scale])


def build_wall_label_neg_y(text: str, target_h: float, depth: float) -> m3d.Manifold:
    return rot_x_90(build_text_cs(text, target_h).extrude(depth))


def build_wall_label_pos_y(text: str, target_h: float, depth: float) -> m3d.Manifold:
    return rot_z_180(rot_x_90(build_text_cs(text, target_h).extrude(depth)))


def build_base(c: dict) -> tuple[m3d.Manifold, dict]:
    ow, ol, bh = c["outer_w"], c["outer_l"], c["base_h"]
    wall, floor, cr = c["wall"], c["floor"], c["corner_r"]
    iw, il = ow - 2 * wall, ol - 2 * wall

    outer_cs = rounded_rect_cs(ow, ol, cr, 48)
    inner_cs = outer_cs.offset(-wall)
    outer = outer_cs.extrude(bh)
    cavity = inner_cs.extrude(bh - floor + 1.0).translate([0, 0, floor])
    base = outer - cavity

    # Zone A (-Y Bay): 63 x 78 mm Breakout Board standoffs + corner locating bumps
    brk_w, brk_l = c["brk_w"], c["brk_l"]
    brk_y_min = -il / 2.0 + 0.4
    brk_y_max = brk_y_min + brk_l
    brk_cy = (brk_y_min + brk_y_max) / 2.0
    st_h = c["brk_standoff_h"]

    rail_w, rail_l = 2.8, brk_l - 8.0
    rail_x_off = brk_w / 2.0 - 3.5
    rails = [
        m3d.Manifold.cube([rail_w, rail_l, st_h], center=True).translate([-rail_x_off, brk_cy, floor + st_h / 2.0]),
        m3d.Manifold.cube([rail_w, rail_l, st_h], center=True).translate([rail_x_off, brk_cy, floor + st_h / 2.0]),
    ]

    # Low-profile corner stops (1.2mm thick so 2.5mm side wire channels stay open!)
    stop_h = st_h + 1.8
    corner_stops = []
    for sx in (-1.0, 1.0):
        for sy_pos in (brk_y_min + 5.0, brk_y_max - 5.0):
            corner_stops.append(
                m3d.Manifold.cube([1.2, 6.0, stop_h], center=True).translate(
                    [sx * (brk_w / 2.0 + 0.6), sy_pos, floor + stop_h / 2.0]
                )
            )

    # Short center backstop rib between Breakout PCB and +Y mini-bay (clears both PBS-33B buttons!)
    div_y = brk_y_max + 0.7
    backstop = m3d.Manifold.cube([22.0, 1.4, 3.6], center=True).translate(
        [0.0, div_y, floor + 3.6 / 2.0]
    )

    base = base + m3d.Manifold.compose(rails + corner_stops + [backstop])

    # Cutouts & Labels
    lbl_depth = 0.5
    esp_usb_cut = rounded_slot_y_cutout(c["esp_usb_w"], c["esp_usb_h"], wall + 6.0).translate(
        [0.0, -ol / 2.0 + wall / 2.0, c["esp_usb_z_center"]]
    )
    lbl_esp = build_wall_label_neg_y("ESP", 3.6, lbl_depth + 0.5).translate(
        [0.0, -ol / 2.0 + lbl_depth, 7.2]
    )

    usbc_cut = make_cylinder_y(c["usbc_hole_d"] / 2.0, wall + 6.0, 48).translate(
        [c["usbc_x"], ol / 2.0 - wall / 2.0, c["usbc_z_center"]]
    )

    led_x = c["led_exit_x"]
    nw, nh = c["wire_notch_w"], c["wire_notch_h"]
    led_notch = m3d.Manifold.cube([nw, wall + 6.0, nh + 2.0], center=True).translate(
        [led_x, ol / 2.0 - wall / 2.0, bh - nh / 2.0 + 1.0]
    )
    lbl_led = build_wall_label_pos_y("LED", 3.0, lbl_depth + 0.5).translate(
        [led_x, ol / 2.0 - lbl_depth, 12.0]
    )

    # 4 Snap-fit grooves on ±X walls
    snap_z = bh - c["snap_z_from_top"]
    snap_grooves = []
    for sy in c["snap_ys"]:
        snap_grooves.append(
            m3d.Manifold.cube([2.0, c["snap_w"] + 0.8, 1.6], center=True).translate(
                [-iw / 2.0 - 0.25, sy, snap_z]
            )
        )
        snap_grooves.append(
            m3d.Manifold.cube([2.0, c["snap_w"] + 0.8, 1.6], center=True).translate(
                [iw / 2.0 + 0.25, sy, snap_z]
            )
        )

    base = base - m3d.Manifold.compose(
        snap_grooves + [esp_usb_cut, lbl_esp, usbc_cut, led_notch, lbl_led]
    )

    meta = {
        "brk_center": [0.0, brk_cy],
        "usbc_x": c["usbc_x"],
        "led_exit_x": led_x,
    }
    return base, meta


def build_lid(c: dict, meta: dict) -> m3d.Manifold:
    ow, ol, lh = c["outer_w"], c["outer_l"], c["lid_h"]
    wall, cr = c["wall"], c["corner_r"]
    iw, il = ow - 2 * wall, ol - 2 * wall

    outer_cs = rounded_rect_cs(ow, ol, cr, 48)
    lid = outer_cs.extrude(lh)

    clr = c["lip_clearance"]
    lip_outer = outer_cs.offset(-wall - clr).extrude(c["lip_h"])
    lip_inner = outer_cs.offset(-wall - clr - 1.3).extrude(c["lip_h"] + 1.0)
    lip = (lip_outer - lip_inner).translate([0, 0, -c["lip_h"]])

    # Trim inner lip along +Y wall so M12 USB-C nut, LED notch, and PBS-33B nuts have 100% clearance
    trim_pos_y = m3d.Manifold.cube([iw - 4.0, 6.0, c["lip_h"] + 2.0], center=True).translate(
        [0.0, il / 2.0 - 1.0, -c["lip_h"] / 2.0]
    )
    lid = lid + (lip - trim_pos_y)

    # 4 Compliant Snap-Hook Latches (1.3mm slim arms fit cleanly inside 2.5mm wire channels!)
    hook_drop = c["snap_z_from_top"] + 1.3
    hooks = []
    for side in (-1, 1):
        x_edge = side * (iw / 2.0 - clr)
        for sy in c["snap_ys"]:
            sw = c["snap_w"]
            arm = m3d.Manifold.cube([1.3, sw, hook_drop], center=True).translate(
                [x_edge - side * 0.65, sy, -hook_drop / 2.0]
            )
            pts = [[0.0, -1.0], [side * c["snap_overhang"], 0.0], [0.0, 0.9]]
            if side < 0:
                pts.reverse()
            bead = rot_x_90(m3d.CrossSection([pts]).extrude(sw)).translate(
                [x_edge - side * 0.08, sy + sw / 2.0, -c["snap_z_from_top"]]
            )
            hooks.append(arm + bead)
    lid = lid + m3d.Manifold.compose(hooks)

    # 2x Ø 12.3mm PBS-33B Button Holes (X = ±23.0mm, Y = +39.4mm)
    btn_r = c["btn_hole_d"] / 2.0
    btn1_hole = make_cylinder(lh + 4.0, btn_r, 48).translate([c["btn1_x"], c["btn_y"], -2.0])
    btn2_hole = make_cylinder(lh + 4.0, btn_r, 48).translate([c["btn2_x"], c["btn_y"], -2.0])

    engrave_d = 0.5
    lbl_b1 = build_text_cs("1 SHOW", 3.8).extrude(engrave_d + 0.4).translate(
        [c["btn1_x"] + 1.5, c["btn_y"] - 12.6, lh - engrave_d]
    )
    lbl_b2 = build_text_cs("2 PHOTO", 3.8).extrude(engrave_d + 0.4).translate(
        [c["btn2_x"] - 1.5, c["btn_y"] - 12.6, lh - engrave_d]
    )
    lbl_title = build_text_cs("WDW 10K MINI", 4.8).extrude(engrave_d + 0.4).translate(
        [0.0, -16.0, lh - engrave_d]
    )

    return lid - m3d.Manifold.compose([btn1_hole, btn2_hole, lbl_b1, lbl_b2, lbl_title])


def manifold_to_trimesh(m: m3d.Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    verts = np.asarray(mesh.vert_properties[:, :3], dtype=np.float64)
    faces = np.asarray(mesh.tri_verts, dtype=np.int64)
    return trimesh.Trimesh(vertices=verts, faces=faces, process=False)


def export_plate_3mf(out_path: Path, base_tm: trimesh.Trimesh, lid_tm: trimesh.Trimesh) -> None:
    def mesh_xml(obj_id: int, name: str, tm: trimesh.Trimesh) -> str:
        verts = "\n".join(
            f'          <vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}" />'
            for v in tm.vertices
        )
        tris = "\n".join(
            f'          <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}" />'
            for f in tm.faces
        )
        return (
            f'    <object id="{obj_id}" name="{name}" type="model">\n'
            f'      <mesh>\n'
            f'        <vertices>\n{verts}\n        </vertices>\n'
            f'        <triangles>\n{tris}\n        </triangles>\n'
            f'      </mesh>\n'
            f'    </object>'
        )

    objs = "\n".join([
        mesh_xml(1, "mini_box_base", base_tm),
        mesh_xml(2, "mini_box_lid", lid_tm),
    ])
    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '  <resources>\n'
        f'{objs}\n'
        '  </resources>\n'
        '  <build>\n'
        '    <item objectid="1" transform="1 0 0 0 1 0 0 0 1 -41 0 0" />\n'
        '    <item objectid="2" transform="1 0 0 0 1 0 0 0 1 41 0 0" />\n'
        '  </build>\n'
        '</model>\n'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/contenttypes">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />\n'
        '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />\n'
        '</Types>\n'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2015/02/3dmodel" />\n'
        '</Relationships>\n'
    )
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("3D/3dmodel.model", model_xml)


def write_preview_html(
    out_dir: Path,
    base_tm: trimesh.Trimesh,
    lid_assy_tm: trimesh.Trimesh,
    cfg: dict,
    meta: dict,
) -> Path:
    def mesh_to_json(tm: trimesh.Trimesh) -> dict:
        return {
            "vertices": np.round(tm.vertices, 3).flatten().tolist(),
            "faces": tm.faces.flatten().tolist(),
        }

    data = {
        "base": mesh_to_json(base_tm),
        "lid": mesh_to_json(lid_assy_tm),
        "cfg": cfg,
        "meta": meta,
    }
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>WDW 10K ULTRA-MINI No-WAGO ESP32 Box (72 × 98.5 × 23.5 mm)</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }}
    body {{ background: #0f172a; color: #e2e8f0; overflow: hidden; }}
    #hud {{
      position: fixed; top: 14px; left: 14px; z-index: 10;
      background: rgba(15, 23, 42, 0.9); border: 1px solid #334155;
      border-radius: 12px; padding: 14px 16px; max-width: 410px; backdrop-filter: blur(8px);
    }}
    h1 {{ font-size: 15px; color: #facc15; margin-bottom: 6px; }}
    p {{ font-size: 12px; line-height: 1.45; color: #cbd5e1; margin-bottom: 8px; }}
    .btns {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    button {{
      background: #1e293b; color: #f8fafc; border: 1px solid #475569;
      border-radius: 7px; padding: 6px 10px; font-size: 12px; cursor: pointer;
    }}
    button:hover {{ background: #334155; }}
  </style>
  <script type="importmap">
    {{ "imports": {{
      "three": "https://unpkg.com/three@0.164.1/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.164.1/examples/jsm/"
    }} }}
  </script>
</head>
<body>
  <div id="hud">
    <h1>WDW 10K ULTRA-MINI No-WAGO Box</h1>
    <p>
      <b>Outer:</b> <b>{cfg['outer_w']} × {cfg['outer_l']} × {cfg['base_h'] + cfg['lid_h']} mm</b> (4.0 mm thinner than V6!)<br/>
      <b>Zero WAGOs:</b> Twist USB-C + LED power wires directly into the breakout's 5V &amp; GND screw terminals.<br/>
      <b>+Y Mini-Bay:</b> Centered M12 USB-C (B0CXLZBD2V) + 2× PBS-33B 12mm buttons (X = ±23 mm) + LED notch.
    </p>
    <div class="btns">
      <button id="toggleLid">Explode Lid</button>
      <button id="toggleLidVis">Hide/Show Lid</button>
      <button id="toggleElec">Hide/Show Parts</button>
      <button id="resetCam">Reset View</button>
    </div>
  </div>
  <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

    const DATA = {json.dumps(data)};
    const cfg = DATA.cfg;
    const meta = DATA.meta;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);
    const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.5, 1000);
    camera.position.set(95, -115, 90);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 11);
    controls.update();

    scene.add(new THREE.AmbientLight(0xffffff, 0.75));
    const dl1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dl1.position.set(90, -110, 150);
    scene.add(dl1);
    const dl2 = new THREE.DirectionalLight(0x93c5fd, 0.45);
    dl2.position.set(-100, 100, 80);
    scene.add(dl2);

    const grid = new THREE.GridHelper(200, 20, 0x334155, 0x1e293b);
    grid.rotation.x = Math.PI / 2;
    scene.add(grid);

    function makeMesh(obj, color, opacity = 1.0) {{
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(obj.vertices, 3));
      geo.setIndex(obj.faces);
      geo.computeVertexNormals();
      const mat = new THREE.MeshStandardMaterial({{
        color, roughness: 0.45, metalness: 0.08,
        transparent: opacity < 1.0, opacity
      }});
      return new THREE.Mesh(geo, mat);
    }}

    const baseMesh = makeMesh(DATA.base, 0x334155);
    const lidMesh = makeMesh(DATA.lid, 0x475569, 0.85);
    lidMesh.position.z = cfg.base_h;
    scene.add(baseMesh, lidMesh);

    // Mockup internal hardware
    const elec = new THREE.Group();
    const brkZ = cfg.floor + cfg.brk_standoff_h;
    const brk = new THREE.Mesh(
      new THREE.BoxGeometry(63.0, 78.0, 1.6),
      new THREE.MeshStandardMaterial({{ color: 0x16a34a }})
    );
    brk.position.set(meta.brk_center[0], meta.brk_center[1], brkZ + 0.8);
    elec.add(brk);

    const esp = new THREE.Mesh(
      new THREE.BoxGeometry(28.0, 54.5, 5.1),
      new THREE.MeshStandardMaterial({{ color: 0x0284c7 }})
    );
    esp.position.set(meta.brk_center[0], meta.brk_center[1] - 8.0, brkZ + 1.6 + 8.5 + 2.55);
    elec.add(esp);

    // M12 Panel-Mount USB-C barrel (B0CXLZBD2V)
    const usbc = new THREE.Mesh(
      new THREE.CylinderGeometry(6.0, 6.0, 12.0, 24),
      new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.6, roughness: 0.3 }})
    );
    usbc.position.set(cfg.usbc_x, cfg.outer_l / 2.0 - 5.0, cfg.usbc_z_center);
    elec.add(usbc);

    // 2x PBS-33B 12mm Waterproof Buttons
    for (const [bx, col] of [[cfg.btn1_x, 0xef4444], [cfg.btn2_x, 0x3b82f6]]) {{
      const body = new THREE.Mesh(
        new THREE.CylinderGeometry(6.0, 6.0, 18.5, 24),
        new THREE.MeshStandardMaterial({{ color: col }})
      );
      body.rotation.x = Math.PI / 2;
      body.position.set(bx, cfg.btn_y, cfg.base_h + cfg.lid_h - 9.25);
      const cap = new THREE.Mesh(
        new THREE.CylinderGeometry(8.75, 8.75, 3.0, 24),
        new THREE.MeshStandardMaterial({{ color: col }})
      );
      cap.rotation.x = Math.PI / 2;
      cap.position.set(bx, cfg.btn_y, cfg.base_h + cfg.lid_h + 1.5);
      elec.add(body, cap);
    }}
    scene.add(elec);

    let exploded = false;
    document.getElementById('toggleLid').onclick = () => {{
      exploded = !exploded;
      lidMesh.position.z = cfg.base_h + (exploded ? 20 : 0);
    }};
    document.getElementById('toggleLidVis').onclick = () => {{ lidMesh.visible = !lidMesh.visible; }};
    document.getElementById('toggleElec').onclick = () => {{ elec.visible = !elec.visible; }};
    document.getElementById('resetCam').onclick = () => {{
      camera.position.set(95, -115, 90);
      controls.target.set(0, 0, 11);
    }};

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }});
    function animate() {{ requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }}
    animate();
  </script>
</body>
</html>
"""
    preview_path = out_dir / "mini_controller_box_preview.html"
    preview_path.write_text(html, encoding="utf-8")
    return preview_path


def main() -> None:
    out_dir = Path("3d_panels/controller_box_mini")
    out_dir.mkdir(parents=True, exist_ok=True)

    base_m, meta = build_base(CFG)
    lid_m = build_lid(CFG, meta)

    base_tm = manifold_to_trimesh(base_m)
    lid_assy_tm = manifold_to_trimesh(lid_m)
    lid_print_tm = manifold_to_trimesh(rot_x_180(lid_m).translate([0, 0, CFG["lid_h"]]))

    base_stl = out_dir / "mini_controller_box_base.stl"
    lid_stl = out_dir / "mini_controller_box_lid.stl"
    plate_3mf = out_dir / "mini_controller_box_plate.3mf"

    base_tm.export(base_stl)
    lid_print_tm.export(lid_stl)
    export_plate_3mf(plate_3mf, base_tm, lid_print_tm)
    preview_path = write_preview_html(out_dir, base_tm, lid_assy_tm, CFG, meta)

    assert base_tm.is_watertight, "Mini Base mesh is NOT watertight!"
    assert lid_print_tm.is_watertight, "Mini Lid mesh is NOT watertight!"
    assert abs(base_tm.bounds[0][2]) < 1e-4
    assert abs(lid_print_tm.bounds[0][2]) < 1e-4

    bv, lv = base_tm.volume / 1000.0, lid_print_tm.volume / 1000.0
    print(f"MINI Base watertight: {base_tm.is_watertight} | Z_min: {base_tm.bounds[0][2]:.4f} | Bounds: {np.round(base_tm.extents, 2)}")
    print(f"MINI Lid  watertight: {lid_print_tm.is_watertight} | Z_min: {lid_print_tm.bounds[0][2]:.4f} | Bounds: {np.round(lid_print_tm.extents, 2)}")
    print(f"Volume: Base {bv:.2f} cm3 + Lid {lv:.2f} cm3 = {bv+lv:.2f} cm3 (~{(bv+lv)*1.27*0.88:.1f}g PETG)")
    print(f"Base STL : {base_stl} ({base_stl.stat().st_size / 1024:.1f} KB)")
    print(f"Lid STL  : {lid_stl} ({lid_stl.stat().st_size / 1024:.1f} KB)")
    print(f"3MF Plate: {plate_3mf} ({plate_3mf.stat().st_size / 1024:.1f} KB)")
    print(f"Preview  : {preview_path}")


if __name__ == "__main__":
    main()
