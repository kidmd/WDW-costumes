"""
Parametric 3D CAD Generator — WDW 10K MSEP SHORT & THICK Narrow-Breakout Box + Side-by-Side Comparison.

Builds the shorter, thicker no-WAGO enclosure (77.0 x 84.0 x 35.0 mm — 17.5mm shorter than the
flat 101.5mm box, 8.5mm taller) by mounting:
  - Both 12mm APIELE PBS-33B buttons (B09V2KZZ8W) in the lid directly ABOVE the left (-X) green
    screw-terminal strip (X = -24.5 mm, Y = +22.0 & 0.0 mm; clears the 14.3mm-tall screw terminals
    by 2.2mm and stays 3.0mm clear of the center ESP32!).
  - M12 panel-mount USB-C (B0CXLZBD2V, Ø 12.3 mm) on the +Y wall above the right (+X) green
    screw-terminal strip (X = +22.0 mm, Z = 24.0 mm — clears terminals, ESP32, and lid!).
  - LED cable U-notch centered at top rim of +Y wall (X = 0.0 mm, 9mm above ESP32).
  - Exact 77.5 x 63.25 mm narrow 38-pin terminal adapter (B0GX93HZZZ) in a snug 78.0 x 63.6 mm cradle.

Also generates `short_vs_flat_preview.html` placing BOTH the Flat (77 x 101.5 x 26.5 mm) and
Short (77 x 84.0 x 35.0 mm) boxes side-by-side in the same Three.js scene for instant visual comparison!
"""

from __future__ import annotations

import json
from pathlib import Path
import zipfile

import cv2
import manifold3d as m3d
import numpy as np
import trimesh

import build_controller_box_narrow as flat_mod


CFG = {
    # Short & Thick outer envelope: 77.0 x 84.0 x 35.0 mm (17.5mm shorter, 8.5mm taller!)
    "outer_w": 77.0,          # Same proven 63.6mm cradle + 2x 4.5mm wire channels + 2x 2.2mm walls
    "outer_l": 84.0,          # Just wraps the 78.0mm breakout cradle + 2x 2.2mm walls + 1.6mm clearance!
    "base_h": 32.0,           # 30.0mm inner cavity clears 14.3mm green screw terminals + 15.5mm PBS-33B below lid!
    "lid_h": 3.0,             # Flat snap-fit lid (total assembled height = 35.0mm)
    "wall": 2.2,              # Perimeter wall thickness
    "floor": 2.0,             # Bottom floor thickness
    "corner_r": 4.0,          # Smooth FlipBelt-friendly rounded corners

    # Proven snap-fit lid lip & 4 compliant hook latches (zero screws!)
    "lip_h": 1.8,
    "lip_clearance": 0.25,
    "snap_overhang": 0.75,
    "snap_w": 10.0,
    "snap_z_from_top": 3.6,
    "snap_ys": [-22.0, 22.0],

    # Zone A: Exact measured 77.5 x 63.25 mm Narrow 38-Pin Breakout Board (B0GX93HZZZ)
    "brk_w": 63.6,            # 63.25mm measured + 0.35mm proven snug tab fit
    "brk_l": 78.0,            # 77.50mm measured + 0.50mm snug fit
    "brk_standoff_h": 2.2,    # Proven floor rails clearing underside solder pins
    "esp_usb_w": 13.5,        # ESP32 onboard USB-C reflash cutout (-Y wall)
    "esp_usb_h": 7.6,
    "esp_usb_z_center": 17.5,

    # Zone B (+Y Wall, Upper Deck above right screw terminals): M12 USB-C + Centered LED U-Notch
    "usbc_hole_d": 12.3,      # Ø 12.0mm M12 USB-C + 0.3mm FDM tolerance
    "usbc_x": 22.0,           # Right (+X) side above screw terminals (clears center ESP32 X=-14..+14!)
    "usbc_z_center": 24.0,    # Nut (Z=16.5..31.5) clears 14.3mm green screw terminals & lid!
    "led_exit_x": 0.0,        # Centered at top rim of +Y wall (Z=28.5..32.0, 9mm above ESP32!)
    "wire_notch_w": 5.5,
    "wire_notch_h": 3.5,

    # Zone C (Lid Top Face, Left / -X Side above left screw terminals): 2x PBS-33B 12mm Buttons
    "btn_hole_d": 12.3,       # Ø 12.0mm PBS-33B + 0.3mm FDM tolerance
    "btn_x": -24.5,           # Over left screw terminals (nut X=-32..-17 clears ESP32 X=-14 & -X wall -36.3!)
    "btn1_y": 21.0,           # Button 1 (1 SHOW - GPIO 4)
    "btn2_y": -1.0,           # Button 2 (2 PHOTO - GPIO 33), 22.0mm pitch (4.5mm gap between 17.5mm bezels!)
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

    # Breakout board centered cleanly in Y (78.0mm inside 79.6mm inner length -> 0.8mm clearance per end)
    brk_w, brk_l = c["brk_w"], c["brk_l"]
    brk_cy = 0.0
    brk_y_min = brk_cy - brk_l / 2.0
    brk_y_max = brk_cy + brk_l / 2.0
    st_h = c["brk_standoff_h"]

    rail_w, rail_l = 3.0, brk_l - 8.0
    rail_x_off = brk_w / 2.0 - 3.5
    rails = [
        m3d.Manifold.cube([rail_w, rail_l, st_h], center=True).translate([-rail_x_off, brk_cy, floor + st_h / 2.0]),
        m3d.Manifold.cube([rail_w, rail_l, st_h], center=True).translate([rail_x_off, brk_cy, floor + st_h / 2.0]),
    ]

    stop_h = st_h + 2.2
    corner_stops = []
    for sx in (-1.0, 1.0):
        for sy_pos in (brk_y_min + 5.0, brk_y_max - 5.0):
            corner_stops.append(
                m3d.Manifold.cube([1.6, 8.0, stop_h], center=True).translate(
                    [sx * (brk_w / 2.0 + 0.8), sy_pos, floor + stop_h / 2.0]
                )
            )

    base = base + m3d.Manifold.compose(rails + corner_stops)

    # Cutouts & Labels
    lbl_depth = 0.6
    esp_usb_cut = rounded_slot_y_cutout(c["esp_usb_w"], c["esp_usb_h"], wall + 6.0).translate(
        [0.0, -ol / 2.0 + wall / 2.0, c["esp_usb_z_center"]]
    )
    lbl_esp = build_wall_label_neg_y("ESP", 3.8, lbl_depth + 0.5).translate(
        [0.0, -ol / 2.0 + lbl_depth, 8.2]
    )

    # +Y Wall: M12 USB-C over right screw terminals + LED U-Notch centered at top rim
    usbc_cut = make_cylinder_y(c["usbc_hole_d"] / 2.0, wall + 6.0, 48).translate(
        [c["usbc_x"], ol / 2.0 - wall / 2.0, c["usbc_z_center"]]
    )
    lbl_pwr = build_wall_label_pos_y("PWR", 3.4, lbl_depth + 0.5).translate(
        [c["usbc_x"], ol / 2.0 - lbl_depth, 11.5]
    )

    led_x = c["led_exit_x"]
    nw, nh = c["wire_notch_w"], c["wire_notch_h"]
    led_notch = m3d.Manifold.cube([nw, wall + 6.0, nh + 2.0], center=True).translate(
        [led_x, ol / 2.0 - wall / 2.0, bh - nh / 2.0 + 1.0]
    )
    lbl_led = build_wall_label_pos_y("LED", 3.4, lbl_depth + 0.5).translate(
        [led_x, ol / 2.0 - lbl_depth, 21.5]
    )

    snap_z = bh - c["snap_z_from_top"]
    snap_grooves = []
    for sy in c["snap_ys"]:
        snap_grooves.append(
            m3d.Manifold.cube([2.4, c["snap_w"] + 0.8, 1.8], center=True).translate(
                [-iw / 2.0 - 0.3, sy, snap_z]
            )
        )
        snap_grooves.append(
            m3d.Manifold.cube([2.4, c["snap_w"] + 0.8, 1.8], center=True).translate(
                [iw / 2.0 + 0.3, sy, snap_z]
            )
        )

    base = base - m3d.Manifold.compose(
        snap_grooves + [esp_usb_cut, lbl_esp, usbc_cut, lbl_pwr, led_notch, lbl_led]
    )

    meta = {"brk_center": [0.0, brk_cy], "usbc_x": c["usbc_x"], "led_exit_x": led_x}
    return base, meta


def build_lid(c: dict, meta: dict) -> m3d.Manifold:
    ow, ol, lh = c["outer_w"], c["outer_l"], c["lid_h"]
    wall, cr = c["wall"], c["corner_r"]
    iw, il = ow - 2 * wall, ol - 2 * wall

    outer_cs = rounded_rect_cs(ow, ol, cr, 48)
    lid = outer_cs.extrude(lh)

    clr = c["lip_clearance"]
    lip_outer = outer_cs.offset(-wall - clr).extrude(c["lip_h"])
    lip_inner = outer_cs.offset(-wall - clr - 1.6).extrude(c["lip_h"] + 1.0)
    lip = (lip_outer - lip_inner).translate([0, 0, -c["lip_h"]])

    trim_usbc = m3d.Manifold.cube([18.0, 6.0, c["lip_h"] + 2.0], center=True).translate(
        [meta["usbc_x"], il / 2.0 - 1.0, -c["lip_h"] / 2.0]
    )
    trim_led = m3d.Manifold.cube([c["wire_notch_w"] + 1.6, 6.0, c["lip_h"] + 2.0], center=True).translate(
        [meta["led_exit_x"], il / 2.0 - 1.0, -c["lip_h"] / 2.0]
    )
    lid = lid + (lip - trim_usbc - trim_led)

    hook_drop = c["snap_z_from_top"] + 1.5
    hooks = []
    for side in (-1, 1):
        x_edge = side * (iw / 2.0 - clr)
        for sy in c["snap_ys"]:
            sw = c["snap_w"]
            arm = m3d.Manifold.cube([1.6, sw, hook_drop], center=True).translate(
                [x_edge - side * 0.8, sy, -hook_drop / 2.0]
            )
            pts = [[0.0, -1.2], [side * c["snap_overhang"], 0.0], [0.0, 1.0]]
            if side < 0:
                pts.reverse()
            bead = rot_x_90(m3d.CrossSection([pts]).extrude(sw)).translate(
                [x_edge - side * 0.1, sy + sw / 2.0, -c["snap_z_from_top"]]
            )
            hooks.append(arm + bead)
    lid = lid + m3d.Manifold.compose(hooks)

    # 2x Ø 12.3mm PBS-33B Button Holes lined up along the LEFT (-X) side above the green screw terminals!
    btn_r = c["btn_hole_d"] / 2.0
    btn1_hole = make_cylinder(lh + 4.0, btn_r, 48).translate([c["btn_x"], c["btn1_y"], -2.0])
    btn2_hole = make_cylinder(lh + 4.0, btn_r, 48).translate([c["btn_x"], c["btn2_y"], -2.0])

    engrave_d = 0.6
    lbl_b1 = build_text_cs("1 SHOW", 3.8).extrude(engrave_d + 0.4).translate(
        [c["btn_x"] + 22.0, c["btn1_y"], lh - engrave_d]
    )
    lbl_b2 = build_text_cs("2 PHOTO", 3.8).extrude(engrave_d + 0.4).translate(
        [c["btn_x"] + 23.0, c["btn2_y"], lh - engrave_d]
    )
    lbl_title = build_text_cs("WDW 10K SHORT", 4.6).extrude(engrave_d + 0.4).translate(
        [4.0, -25.0, lh - engrave_d]
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
        mesh_xml(1, "short_box_base", base_tm),
        mesh_xml(2, "short_box_lid", lid_tm),
    ])
    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '  <resources>\n'
        f'{objs}\n'
        '  </resources>\n'
        '  <build>\n'
        '    <item objectid="1" transform="1 0 0 0 1 0 0 0 1 -44 0 0" />\n'
        '    <item objectid="2" transform="1 0 0 0 1 0 0 0 1 44 0 0" />\n'
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


def write_comparison_html(
    out_dir: Path,
    flat_base_tm: trimesh.Trimesh,
    flat_lid_tm: trimesh.Trimesh,
    flat_cfg: dict,
    flat_meta: dict,
    short_base_tm: trimesh.Trimesh,
    short_lid_tm: trimesh.Trimesh,
    short_cfg: dict,
    short_meta: dict,
) -> Path:
    def m2j(tm: trimesh.Trimesh) -> dict:
        return {
            "vertices": np.round(tm.vertices, 3).flatten().tolist(),
            "faces": tm.faces.flatten().tolist(),
        }

    data = {
        "flat": {"base": m2j(flat_base_tm), "lid": m2j(flat_lid_tm), "cfg": flat_cfg, "meta": flat_meta},
        "short": {"base": m2j(short_base_tm), "lid": m2j(short_lid_tm), "cfg": short_cfg, "meta": short_meta},
    }
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Side-by-Side Comparison: Flat (26.5mm) vs. Short (35.0mm)</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }}
    body {{ background: #0f172a; color: #e2e8f0; overflow: hidden; }}
    #hud {{
      position: fixed; top: 14px; left: 14px; z-index: 10;
      background: rgba(15, 23, 42, 0.92); border: 1px solid #334155;
      border-radius: 12px; padding: 14px 16px; max-width: 450px; backdrop-filter: blur(8px);
    }}
    h1 {{ font-size: 15px; color: #38bdf8; margin-bottom: 6px; }}
    p {{ font-size: 12px; line-height: 1.45; color: #cbd5e1; margin-bottom: 8px; }}
    .tag-l {{ color: #38bdf8; font-weight: 700; }}
    .tag-r {{ color: #fbbf24; font-weight: 700; }}
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
    <h1>Side-by-Side: Flat vs. Short &amp; Thick (No-WAGO)</h1>
    <p>
      <span class="tag-l">LEFT — Flat Box:</span> <b>77.0 × 101.5 × 26.5 mm</b> (8.5 mm flatter!)<br/>
      <span class="tag-r">RIGHT — Short Box:</span> <b>77.0 × 84.0 × 35.0 mm</b> (17.5 mm shorter! Buttons &amp; USB-C sit above the green screw terminals.)
    </p>
    <div class="btns">
      <button id="toggleLid">Explode Lids</button>
      <button id="toggleLidVis">Hide/Show Lids</button>
      <button id="toggleElec">Hide/Show Parts</button>
      <button id="resetCam">Reset View</button>
    </div>
  </div>
  <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

    const DATA = {json.dumps(data)};

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);
    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.5, 1200);
    camera.position.set(0, -185, 130);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 16);
    controls.update();

    scene.add(new THREE.AmbientLight(0xffffff, 0.78));
    const dl1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dl1.position.set(110, -130, 170);
    scene.add(dl1);
    const dl2 = new THREE.DirectionalLight(0x93c5fd, 0.45);
    dl2.position.set(-120, 110, 90);
    scene.add(dl2);

    const grid = new THREE.GridHelper(280, 28, 0x334155, 0x1e293b);
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

    function makeLabel(text, bg) {{
      const cv = document.createElement('canvas');
      cv.width = 460; cv.height = 96;
      const ctx = cv.getContext('2d');
      ctx.fillStyle = bg;
      ctx.beginPath(); ctx.roundRect(4, 4, 452, 88, 16); ctx.fill();
      ctx.strokeStyle = '#e2e8f0'; ctx.lineWidth = 3; ctx.stroke();
      ctx.fillStyle = '#ffffff'; ctx.font = 'bold 30px system-ui, sans-serif';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(text, 230, 49);
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: new THREE.CanvasTexture(cv), transparent: true }}));
      sp.scale.set(56, 11.7, 1);
      return sp;
    }}

    const OFFSET_X = 52;
    const lids = [];
    const elecGroups = [];

    // ---- LEFT: FLAT BOX (77 x 101.5 x 26.5 mm) ----
    const gFlat = new THREE.Group();
    gFlat.position.x = -OFFSET_X;
    const fCfg = DATA.flat.cfg, fMeta = DATA.flat.meta;
    const fBase = makeMesh(DATA.flat.base, 0x334155);
    const fLid = makeMesh(DATA.flat.lid, 0x475569, 0.86);
    fLid.position.z = fCfg.base_h;
    lids.push({{ mesh: fLid, baseZ: fCfg.base_h }});
    gFlat.add(fBase, fLid);

    const fElec = new THREE.Group();
    const fBrkZ = fCfg.floor + fCfg.brk_standoff_h;
    const fBrk = new THREE.Mesh(new THREE.BoxGeometry(63.25, 77.5, 1.6), new THREE.MeshStandardMaterial({{ color: 0x16a34a }}));
    fBrk.position.set(0, fMeta.brk_center[1], fBrkZ + 0.8);
    const fEsp = new THREE.Mesh(new THREE.BoxGeometry(28.0, 54.5, 5.1), new THREE.MeshStandardMaterial({{ color: 0x0284c7 }}));
    fEsp.position.set(0, fMeta.brk_center[1] - 8.0, fBrkZ + 1.6 + 8.5 + 2.55);
    const fUsb = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.0, 12.0, 24), new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.6, roughness: 0.3 }}));
    fUsb.position.set(fCfg.usbc_x, fCfg.outer_l / 2.0 - 5.0, fCfg.usbc_z_center);
    fElec.add(fBrk, fEsp, fUsb);
    for (const [bx, col] of [[fCfg.btn1_x, 0xef4444], [fCfg.btn2_x, 0x3b82f6]]) {{
      const body = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.0, 18.5, 24), new THREE.MeshStandardMaterial({{ color: col }}));
      body.rotation.x = Math.PI / 2;
      body.position.set(bx, fCfg.btn_y, fCfg.base_h + fCfg.lid_h - 9.25);
      const cap = new THREE.Mesh(new THREE.CylinderGeometry(8.75, 8.75, 3.0, 24), new THREE.MeshStandardMaterial({{ color: col }}));
      cap.rotation.x = Math.PI / 2;
      cap.position.set(bx, fCfg.btn_y, fCfg.base_h + fCfg.lid_h + 1.5);
      fElec.add(body, cap);
    }}
    gFlat.add(fElec);
    elecGroups.push(fElec);
    const lblL = makeLabel('FLAT: 77 × 101.5 × 26.5 mm', 'rgba(2, 132, 199, 0.9)');
    lblL.position.set(-OFFSET_X, -66, 12);
    scene.add(gFlat, lblL);

    // ---- RIGHT: SHORT & THICK BOX (77 x 84.0 x 35.0 mm) ----
    const gShort = new THREE.Group();
    gShort.position.x = OFFSET_X;
    const sCfg = DATA.short.cfg, sMeta = DATA.short.meta;
    const sBase = makeMesh(DATA.short.base, 0x334155);
    const sLid = makeMesh(DATA.short.lid, 0x475569, 0.86);
    sLid.position.z = sCfg.base_h;
    lids.push({{ mesh: sLid, baseZ: sCfg.base_h }});
    gShort.add(sBase, sLid);

    const sElec = new THREE.Group();
    const sBrkZ = sCfg.floor + sCfg.brk_standoff_h;
    const sBrk = new THREE.Mesh(new THREE.BoxGeometry(63.25, 77.5, 1.6), new THREE.MeshStandardMaterial({{ color: 0x16a34a }}));
    sBrk.position.set(0, 0, sBrkZ + 0.8);
    // Green screw terminal blocks along left & right edges (8.5mm tall)
    for (const tx of [-25.0, 25.0]) {{
      const term = new THREE.Mesh(new THREE.BoxGeometry(8.0, 68.0, 8.5), new THREE.MeshStandardMaterial({{ color: 0x22c55e }}));
      term.position.set(tx, 0, sBrkZ + 1.6 + 4.25);
      sElec.add(term);
    }}
    const sEsp = new THREE.Mesh(new THREE.BoxGeometry(28.0, 54.5, 5.1), new THREE.MeshStandardMaterial({{ color: 0x0284c7 }}));
    sEsp.position.set(0, -8.0, sBrkZ + 1.6 + 8.5 + 2.55);
    const sUsb = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.0, 12.0, 24), new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.6, roughness: 0.3 }}));
    sUsb.position.set(sCfg.usbc_x, sCfg.outer_l / 2.0 - 5.0, sCfg.usbc_z_center);
    sElec.add(sBrk, sEsp, sUsb);
    for (const [by, col] of [[sCfg.btn1_y, 0xef4444], [sCfg.btn2_y, 0x3b82f6]]) {{
      const body = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.0, 18.5, 24), new THREE.MeshStandardMaterial({{ color: col }}));
      body.rotation.x = Math.PI / 2;
      body.position.set(sCfg.btn_x, by, sCfg.base_h + sCfg.lid_h - 9.25);
      const cap = new THREE.Mesh(new THREE.CylinderGeometry(8.75, 8.75, 3.0, 24), new THREE.MeshStandardMaterial({{ color: col }}));
      cap.rotation.x = Math.PI / 2;
      cap.position.set(sCfg.btn_x, by, sCfg.base_h + sCfg.lid_h + 1.5);
      sElec.add(body, cap);
    }}
    gShort.add(sElec);
    elecGroups.push(sElec);
    const lblR = makeLabel('SHORT: 77 × 84.0 × 35.0 mm', 'rgba(217, 119, 6, 0.92)');
    lblR.position.set(OFFSET_X, -66, 12);
    scene.add(gShort, lblR);

    let exploded = false;
    document.getElementById('toggleLid').onclick = () => {{
      exploded = !exploded;
      for (const item of lids) item.mesh.position.z = item.baseZ + (exploded ? 22 : 0);
    }};
    document.getElementById('toggleLidVis').onclick = () => {{
      for (const item of lids) item.mesh.visible = !item.mesh.visible;
    }};
    document.getElementById('toggleElec').onclick = () => {{
      for (const g of elecGroups) g.visible = !g.visible;
    }};
    document.getElementById('resetCam').onclick = () => {{
      camera.position.set(0, -185, 130);
      controls.target.set(0, 0, 16);
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
    preview_path = out_dir / "short_vs_flat_preview.html"
    preview_path.write_text(html, encoding="utf-8")
    return preview_path


def main() -> None:
    out_dir = Path("3d_panels/controller_box_short")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build Short & Thick box
    short_base_m, short_meta = build_base(CFG)
    short_lid_m = build_lid(CFG, short_meta)
    short_base_tm = manifold_to_trimesh(short_base_m)
    short_lid_assy_tm = manifold_to_trimesh(short_lid_m)
    short_lid_print_tm = manifold_to_trimesh(rot_x_180(short_lid_m).translate([0, 0, CFG["lid_h"]]))

    base_stl = out_dir / "short_box_base.stl"
    lid_stl = out_dir / "short_box_lid.stl"
    plate_3mf = out_dir / "short_box_plate.3mf"
    short_base_tm.export(base_stl)
    short_lid_print_tm.export(lid_stl)
    export_plate_3mf(plate_3mf, short_base_tm, short_lid_print_tm)

    # Also build Flat box in memory for side-by-side HTML comparison!
    flat_base_m, flat_meta = flat_mod.build_base(flat_mod.CFG)
    flat_lid_m = flat_mod.build_lid(flat_mod.CFG, flat_meta)
    flat_base_tm = manifold_to_trimesh(flat_base_m)
    flat_lid_assy_tm = manifold_to_trimesh(flat_lid_m)

    preview_path = write_comparison_html(
        out_dir,
        flat_base_tm, flat_lid_assy_tm, flat_mod.CFG, flat_meta,
        short_base_tm, short_lid_assy_tm, CFG, short_meta,
    )

    assert short_base_tm.is_watertight, "Short Base mesh is NOT watertight!"
    assert short_lid_print_tm.is_watertight, "Short Lid mesh is NOT watertight!"
    assert abs(short_base_tm.bounds[0][2]) < 1e-4
    assert abs(short_lid_print_tm.bounds[0][2]) < 1e-4

    bv, lv = short_base_tm.volume / 1000.0, short_lid_print_tm.volume / 1000.0
    print(f"SHORT Base watertight: {short_base_tm.is_watertight} | Z_min: {short_base_tm.bounds[0][2]:.4f} | Bounds: {np.round(short_base_tm.extents, 2)}")
    print(f"SHORT Lid  watertight: {short_lid_print_tm.is_watertight} | Z_min: {short_lid_print_tm.bounds[0][2]:.4f} | Bounds: {np.round(short_lid_print_tm.extents, 2)}")
    print(f"Volume: Base {bv:.2f} cm3 + Lid {lv:.2f} cm3 = {bv+lv:.2f} cm3 (~{(bv+lv)*1.27*0.88:.1f}g PETG)")
    print(f"Base STL : {base_stl} ({base_stl.stat().st_size / 1024:.1f} KB)")
    print(f"Lid STL  : {lid_stl} ({lid_stl.stat().st_size / 1024:.1f} KB)")
    print(f"3MF Plate: {plate_3mf} ({plate_3mf.stat().st_size / 1024:.1f} KB)")
    print(f"Preview  : {preview_path}")


if __name__ == "__main__":
    main()
