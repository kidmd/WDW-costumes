import os
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCKUP_DIR = os.path.join(BASE_DIR, "3d_panels", "mockups")
os.makedirs(MOCKUP_DIR, exist_ok=True)

print("=" * 60)
print("ANTIGRAVITY IMAGINEERING - 3D PRINTABLE PCB MOCKUP GENERATOR")
print("Simulating Exact 1:1 PCB Thickness (2.5mm) and Weight (124g PLA)")
print("=" * 60)

# Helper function to create a rounded rectangle cross section
def rounded_rectangle_cs(width, height, radius=2.0, segments=16):
    r = min(radius, width / 2.0, height / 2.0)
    w_inner = width - 2 * r
    h_inner = height - 2 * r
    
    # Base box + 4 corner circles
    cs = CrossSection.square([w_inner, height], center=False).translate([r, 0])
    cs = cs + CrossSection.square([width, h_inner], center=False).translate([0, r])
    
    c_bl = CrossSection.circle(r, segments).translate([r, r])
    c_br = CrossSection.circle(r, segments).translate([width - r, r])
    c_tl = CrossSection.circle(r, segments).translate([r, height - r])
    c_tr = CrossSection.circle(r, segments).translate([width - r, height - r])
    
    return cs + c_bl + c_br + c_tl + c_tr

# ---------------------------------------------------------------------------
# 1. Generate Monolithic 200mm x 200mm x 2.5mm Mockup
# ---------------------------------------------------------------------------
print("\n[1/2] Generating Monolithic 200mm x 200mm Mockup...")
cs_200 = rounded_rectangle_cs(200.0, 200.0, radius=2.5, segments=24)

# 4 Corner M3 Holes (Ø3.2mm)
m3_200_coords = [(6.0, 6.0), (194.0, 6.0), (6.0, 194.0), (194.0, 194.0)]
for hx, hy in m3_200_coords:
    hole = CrossSection.circle(1.6, 24).translate([hx, hy])
    cs_200 = cs_200 - hole

# 12 Perimeter Sewing Eyelets (Ø2.0mm)
sew_200_coords = [
    (50.0, 5.0), (100.0, 5.0), (150.0, 5.0),
    (75.0, 195.0), (100.0, 195.0), (125.0, 195.0),
    (5.0, 50.0), (5.0, 100.0), (5.0, 150.0),
    (195.0, 50.0), (195.0, 100.0), (195.0, 150.0),
]
for sx, sy in sew_200_coords:
    hole = CrossSection.circle(1.0, 16).translate([sx, sy])
    cs_200 = cs_200 - hole

# Solder Pin Holes (2.54mm pitch, Ø1.2mm) & Strain Relief (Ø2.2mm)
pin_200_coords = [
    # IN header
    (27.46, 192.0), (30.00, 192.0), (32.54, 192.0),
    # OUT header
    (167.46, 192.0), (170.00, 192.0), (172.54, 192.0),
]
for px, py in pin_200_coords:
    hole = CrossSection.circle(0.6, 16).translate([px, py])
    cs_200 = cs_200 - hole

strain_200_coords = [(26.0, 186.5), (34.0, 186.5), (166.0, 186.5), (174.0, 186.5)]
for sx, sy in strain_200_coords:
    hole = CrossSection.circle(1.1, 16).translate([sx, sy])
    cs_200 = cs_200 - hole

# Extrude to exact 2.50mm thickness
m_200 = Manifold.extrude(cs_200, 2.50)
mesh_200 = m_200.to_mesh()
tm_200 = trimesh.Trimesh(vertices=mesh_200.vert_properties, faces=mesh_200.tri_verts)

stl_200_path = os.path.join(MOCKUP_DIR, "mockup_monolithic_200x200.stl")
tm_200.export(stl_200_path)

vol_200_cm3 = tm_200.volume / 1000.0
weight_200_pla = vol_200_cm3 * 1.24  # PLA density = 1.24 g/cm3

print(f"  -> Exported: {stl_200_path}")
print(f"  -> Watertight: {tm_200.is_watertight}")
print(f"  -> Dimensions: 200.0 x 200.0 x 2.50 mm")
print(f"  -> Volume: {vol_200_cm3:.2f} cm³")
print(f"  -> Simulated Weight @ 100% Infill: {weight_200_pla:.1f} grams ({weight_200_pla/28.3495:.2f} oz)")
print(f"  -> Real Loaded FR-4 PCB Weight: ~126.5 grams (Match: {weight_200_pla/126.5*100:.1f}%)")

# ---------------------------------------------------------------------------
# 2. Generate Modular 100mm x 100mm x 2.5mm Tile Mockup
# ---------------------------------------------------------------------------
print("\n[2/2] Generating Modular 100mm x 100mm Tile Mockup...")
cs_100 = rounded_rectangle_cs(100.0, 100.0, radius=2.0, segments=24)

# 4 Corner M3 Holes (Ø3.2mm)
m3_100_coords = [(4.0, 3.5), (96.0, 3.5), (4.0, 96.5), (96.0, 96.5)]
for hx, hy in m3_100_coords:
    hole = CrossSection.circle(1.6, 24).translate([hx, hy])
    cs_100 = cs_100 - hole

# 4 Dedicated Fabric Sewing Eyelets (Ø2.0mm)
sew_100_coords = [(10.0, 3.5), (90.0, 3.5), (10.0, 96.5), (90.0, 96.5)]
for sx, sy in sew_100_coords:
    hole = CrossSection.circle(1.0, 16).translate([sx, sy])
    cs_100 = cs_100 - hole

# Extrude to exact 2.50mm thickness
m_100 = Manifold.extrude(cs_100, 2.50)
mesh_100 = m_100.to_mesh()
tm_100 = trimesh.Trimesh(vertices=mesh_100.vert_properties, faces=mesh_100.tri_verts)

stl_100_path = os.path.join(MOCKUP_DIR, "mockup_modular_100x100.stl")
tm_100.export(stl_100_path)

vol_100_cm3 = tm_100.volume / 1000.0
weight_100_pla = vol_100_cm3 * 1.24

print(f"  -> Exported: {stl_100_path}")
print(f"  -> Watertight: {tm_100.is_watertight}")
print(f"  -> Dimensions: 100.0 x 100.0 x 2.50 mm")
print(f"  -> Volume: {vol_100_cm3:.2f} cm³")
print(f"  -> Simulated Weight per Tile @ 100% Infill: {weight_100_pla:.1f} grams ({weight_100_pla/28.3495:.2f} oz)")
print(f"  -> Set of 4 Tiles (Chest Array): {weight_100_pla * 4:.1f} grams ({weight_100_pla * 4/28.3495:.2f} oz)")

# ---------------------------------------------------------------------------
# 3. Generate Interactive 3D WebGL Inspector
# ---------------------------------------------------------------------------
html_path = os.path.join(MOCKUP_DIR, "mockups_preview.html")
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>3D Printed PCB Mockup Visualizer</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; text-align: center; }}
h1 {{ color: #38bdf8; margin-bottom: 5px; }}
p {{ color: #94a3b8; margin-top: 0; }}
.btn {{ background: #3b82f6; color: white; border: none; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; margin: 4px; }}
.btn:hover {{ background: #2563eb; }}
.btn.active {{ background: #10b981; }}
#viewport {{ width: 700px; height: 500px; margin: 20px auto; background: #020617; border: 2px solid #334155; border-radius: 8px; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
.stat-box {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
.stat {{ background: #1e293b; padding: 10px 18px; border-radius: 8px; border: 1px solid #334155; }}
.stat-val {{ font-size: 1.4em; font-weight: bold; color: #38bdf8; }}
.stat-lbl {{ font-size: 0.8em; color: #94a3b8; }}
.card {{ max-width: 700px; margin: 20px auto; background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; text-align: left; }}
.badge {{ background: #059669; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
</head>
<body>
<h1>3D Printable PCB Test Mockups</h1>
<p>Disney Imagineering MSEP Wearable Evaluation • Exact 1:1 Thickness & Weight Mules</p>

<div>
  <button id="btn200" class="btn active" onclick="loadModel('200')">Monolithic 200x200mm Plate</button>
  <button id="btn100" class="btn" onclick="loadModel('100')">Modular 100x100mm Tile (Print 4)</button>
</div>

<div id="viewport"></div>

<div class="stat-box">
  <div class="stat"><div class="stat-val" id="dispDim">200 x 200 x 2.5 mm</div><div class="stat-lbl">Dimensions</div></div>
  <div class="stat"><div class="stat-val" id="dispWeight">{weight_200_pla:.1f} g ({weight_200_pla/28.3495:.2f} oz)</div><div class="stat-lbl">Simulated Weight (100% Infill)</div></div>
  <div class="stat"><div class="stat-val" id="dispMatch">~126.5 g</div><div class="stat-lbl">Real Loaded PCB Weight</div></div>
  <div class="stat"><div class="stat-val">100%</div><div class="stat-lbl">Slicer Infill Required</div></div>
</div>

<div class="card">
  <h3>🖨️ Slicer Instructions for Accurate Weight:</h3>
  <ul>
    <li><strong>Material:</strong> Standard PLA (Any color you have).</li>
    <li><strong>Infill Density:</strong> <span class="badge">100%</span> (or set Top/Bottom Shell Layers to 99). <em>Do not use 15% infill or it will be 75% too light!</em></li>
    <li><strong>Layer Height:</strong> 0.20mm or 0.28mm (fast print).</li>
    <li><strong>Print Time:</strong> ~45 min for 100mm tile; ~1.5 hours for 200mm plate.</li>
    <li><strong>Testing:</strong> Pin or slip into your running shirt, test breathing expansion, and jog for 5 minutes!</li>
  </ul>
</div>

<script>
let scene, camera, renderer, controls, currentMesh;
const loader = new THREE.STLLoader();
const container = document.getElementById('viewport');

function init() {{
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020617);
  
  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 1, 1000);
  camera.position.set(0, -180, 220);
  
  renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);
  
  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);
  
  const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight1.position.set(100, 100, 200);
  scene.add(dirLight1);
  
  const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.5);
  dirLight2.position.set(-100, -100, -100);
  scene.add(dirLight2);
  
  const grid = new THREE.GridHelper(300, 30, 0x334155, 0x1e293b);
  grid.rotation.x = Math.PI / 2;
  scene.add(grid);
  
  loadModel('200');
  animate();
}}

function loadModel(type) {{
  if (currentMesh) scene.remove(currentMesh);
  
  const btn200 = document.getElementById('btn200');
  const btn100 = document.getElementById('btn100');
  const file = type === '200' ? 'mockup_monolithic_200x200.stl' : 'mockup_modular_100x100.stl';
  
  if (type === '200') {{
    btn200.classList.add('active');
    btn100.classList.remove('active');
    document.getElementById('dispDim').innerText = '200 x 200 x 2.5 mm';
    document.getElementById('dispWeight').innerText = '{weight_200_pla:.1f} g ({weight_200_pla/28.3495:.2f} oz)';
    document.getElementById('dispMatch').innerText = '~126.5 g';
  }} else {{
    btn100.classList.add('active');
    btn200.classList.remove('active');
    document.getElementById('dispDim').innerText = '100 x 100 x 2.5 mm (x4)';
    document.getElementById('dispWeight').innerText = '{weight_100_pla:.1f} g / tile ({weight_100_pla*4:.1f} g array)';
    document.getElementById('dispMatch').innerText = '~126.5 g total';
  }}
  
  loader.load(file, function(geometry) {{
    geometry.center();
    const material = new THREE.MeshPhongMaterial({{
      color: type === '200' ? 0x059669 : 0x0284c7,
      specular: 0x333333,
      shininess: 30
    }});
    currentMesh = new THREE.Mesh(geometry, material);
    scene.add(currentMesh);
  }});
}}

function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});

init();
</script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\nGenerated 3D Web Inspector: {html_path}")
print("ALL MOCKUP STLS SUCCESSFULLY COMPILED!")
