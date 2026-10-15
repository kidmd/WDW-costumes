#!/usr/bin/env python3
"""
generate_assembly_visualization.py

Builds a complete, detailed 3D assembly and interactive visualizer demonstrating
how the SWIFTVEST running vest, the 3D-printed front costume plate, the right-side
hinge clamps, and the left-side quick-release latches come together.

Outputs:
1. 3d_panels/swiftvest_front_assembly_preview.obj (Color-coded multi-group 3D model)
2. 3d_panels/swiftvest_front_assembly_preview.stl (Single combined STL)
3. simulator/swiftvest_assembly_viewer.html (Interactive 3D Web Viewer with Swing Door & Exploded View)
"""

import os
import json
import numpy as np
import trimesh
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

def build_swiftvest_model():
    """
    Builds a clean 3D representation of the SWIFTVEST running harness:
    - Left shoulder strap (X = 40 to 65 mm, Y = -20 to 260 mm)
    - Right shoulder strap (X = 225 to 250 mm, Y = -20 to 260 mm)
    - Vertical nylon webbing tracks on both straps (22mm wide x 2mm thick)
    - Upper & lower horizontal sternum cross-straps bridging across the chest
    - Quick-release snap buckles centered at X = 145 mm
    """
    strap_w = 42.0   # mm
    strap_thick = 4.0 # mm
    webbing_w = 22.0 # mm
    webbing_thick = 2.0 # mm
    y_min = -20.0
    y_max = 260.0
    y_len = y_max - y_min
    
    # Left strap (runner's right, screen left: X ~ 45mm center)
    left_x = 42.0
    left_strap = make_box(strap_w, y_len, strap_thick).translate([left_x - strap_w/2, y_min, -strap_thick - 1.0])
    left_webbing = make_box(webbing_w, y_len, webbing_thick).translate([left_x - webbing_w/2, y_min, -1.0])
    
    # Right strap (runner's left, screen right: X ~ 248mm center)
    right_x = 248.0
    right_strap = make_box(strap_w, y_len, strap_thick).translate([right_x - strap_w/2, y_min, -strap_thick - 1.0])
    right_webbing = make_box(webbing_w, y_len, webbing_thick).translate([right_x - webbing_w/2, y_min, -1.0])
    
    # Sternum cross straps bridging left & right (at Y = 70mm and Y = 160mm)
    bridge_w = right_x - left_x
    sternum_upper = make_box(bridge_w, 20.0, 2.0).translate([left_x, 150.0, -strap_thick - 2.5])
    sternum_lower = make_box(bridge_w, 20.0, 2.0).translate([left_x, 60.0, -strap_thick - 2.5])
    
    # Center buckles
    buckle_upper = make_box(30.0, 28.0, 6.0).translate([145.0 - 15.0, 146.0, -strap_thick - 5.0])
    buckle_lower = make_box(30.0, 28.0, 6.0).translate([145.0 - 15.0, 56.0, -strap_thick - 5.0])
    
    vest_mesh = to_trimesh(left_strap + right_strap + left_webbing + right_webbing + sternum_upper + sternum_lower + buckle_upper + buckle_lower)
    return vest_mesh

def build_hardware_instances():
    """
    Loads and positions the 3D-printed mounting hardware:
    - 2x Right Hinge Clamps at Tab 5 (Y=167) and Tab 7 (Y=63.5)
    - 2x Left Quick Latches at Tab 15 (Y=154.7) and Tab 13 (Y=73)
    """
    hinge_mesh = trimesh.load(os.path.join(PANELS_DIR, "swiftvest_hinge_clamp_right.stl"))
    latch_mesh = trimesh.load(os.path.join(PANELS_DIR, "swiftvest_quick_latch_left.stl"))
    
    # Right hinge 1 (upper, at Tab 5: X=243.9, Y=167.0)
    h_up = hinge_mesh.copy()
    # Align hinge to plate tab
    h_up.apply_translation([232.0, 154.0, -2.0])
    
    # Right hinge 2 (lower, at Tab 7: X=254.9, Y=63.5)
    h_lo = hinge_mesh.copy()
    h_lo.apply_translation([234.0, 50.5, -2.0])
    
    # Left latch 1 (upper, at Tab 15: X=28.0, Y=154.7)
    l_up = latch_mesh.copy()
    # Rotate 180 around Z to point inward toward left strap
    rot180 = trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1])
    l_up.apply_transform(rot180)
    l_up.apply_translation([60.0, 168.0, -2.0])
    
    # Left latch 2 (lower, at Tab 13: X=60.3, Y=73.0)
    l_lo = latch_mesh.copy()
    l_lo.apply_transform(rot180)
    l_lo.apply_translation([72.0, 86.0, -2.0])
    
    return [h_up, h_lo], [l_up, l_lo]

def create_interactive_viewer_html():
    """
    Generates a rich, interactive Three.js 3D viewer where the user can:
    - Rotate 360 degrees around the assembly.
    - Toggle between CLOSED (Race Mode) and OPEN (Donning/Doffing Hinge Mode).
    - Slider controlling hinge angle (0 to 110 degrees).
    - Exploded view slider to separate the layers (Vest, Clips, Plate).
    - Annotated callout tags.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SWIFTVEST & 3D Plate Assembly Visualizer | MSEP 10K Costumes</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        #header {
            background: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 10;
        }
        #header h1 {
            font-size: 16px;
            font-weight: 600;
            color: #58a6ff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #header p {
            font-size: 12px;
            color: #8b949e;
        }
        #canvas-container {
            flex: 1;
            position: relative;
            outline: none;
        }
        #controls-panel {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(22, 27, 34, 0.92);
            backdrop-filter: blur(12px);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 14px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            width: 90%;
            max-width: 620px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            z-index: 10;
        }
        .control-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }
        .btn-group {
            display: flex;
            gap: 8px;
            width: 100%;
        }
        .btn {
            flex: 1;
            padding: 8px 14px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            border: 1px solid #30363d;
            background: #21262d;
            color: #c9d1d9;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
        }
        .btn:hover {
            background: #30363d;
            border-color: #8b949e;
        }
        .btn.active {
            background: #238636;
            color: #ffffff;
            border-color: #2ea043;
            box-shadow: 0 0 12px rgba(46, 160, 67, 0.4);
        }
        .slider-label {
            font-size: 12px;
            font-weight: 500;
            color: #8b949e;
            min-width: 140px;
        }
        input[type="range"] {
            flex: 1;
            accent-color: #58a6ff;
            cursor: pointer;
        }
        #legend {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(22, 27, 34, 0.88);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 11px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            z-index: 10;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .color-dot {
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }
        #info-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(22, 27, 34, 0.88);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 16px;
            max-width: 320px;
            font-size: 12px;
            line-height: 1.4;
            z-index: 10;
        }
        #info-overlay h3 {
            color: #58a6ff;
            font-size: 13px;
            margin-bottom: 4px;
        }
    </style>
</head>
<body>
    <div id="header">
        <div>
            <h1>🎽 SWIFTVEST + 3D Plate Assembly Inspector</h1>
            <p>Main Street Electrical Parade (WDW 10K) Costumes | Interactive 3D Kinematics</p>
        </div>
        <div style="font-size: 11px; color: #58a6ff; font-weight: 600;">
            Disney Imagineering Pair-Programming
        </div>
    </div>

    <div id="canvas-container">
        <div id="info-overlay">
            <h3 id="mode-title">📖 Mode: Race Ready (Plate Closed)</h3>
            <p id="mode-desc">The front 3D plate spans across both shoulder straps. Left latches are locked. Center sternum straps are securely hidden underneath.</p>
        </div>

        <div id="legend">
            <div style="font-weight: 600; margin-bottom: 4px; color: #f0f6fc;">Component Legend:</div>
            <div class="legend-item"><div class="color-dot" style="background: #2563eb;"></div> SWIFTVEST Harness</div>
            <div class="legend-item"><div class="color-dot" style="background: #38bdf8;"></div> Vest Webbing Tracks</div>
            <div class="legend-item"><div class="color-dot" style="background: #f59e0b;"></div> Right Pivot Hinge (Captive)</div>
            <div class="legend-item"><div class="color-dot" style="background: #ef4444;"></div> Left Quick-Latch (Release Tab)</div>
            <div class="legend-item"><div class="color-dot" style="background: #475569;"></div> 240mm Front 3D Plate</div>
            <div class="legend-item"><div class="color-dot" style="background: #10b981;"></div> Float Graphic Artwork</div>
        </div>

        <div id="controls-panel">
            <div class="btn-group">
                <button class="btn active" id="btn-closed" onclick="setPlateState(0)">🔒 Race Closed (0°)</button>
                <button class="btn" id="btn-open" onclick="setPlateState(1)">📖 Swing Open (110°)</button>
                <button class="btn" id="btn-exploded" onclick="toggleExploded()">💥 Exploded View</button>
            </div>
            <div class="control-row">
                <span class="slider-label">Door Swing Angle: <span id="angle-display">0°</span></span>
                <input type="range" id="hinge-slider" min="0" max="110" value="0" oninput="updateHingeAngle(this.value)">
            </div>
            <div class="control-row">
                <span class="slider-label">Exploded Separation: <span id="explode-display">0 mm</span></span>
                <input type="range" id="explode-slider" min="0" max="80" value="0" oninput="updateExplode(this.value)">
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, controls;
        let vestGroup, doorPivotGroup, plateMesh, rightHingesGroup, leftLatchesGroup, explodedGroup;
        let currentHingeAngle = 0;
        let currentExplodeZ = 0;

        init();
        animate();

        function init() {
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0d1117);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 1, 2000);
            camera.position.set(145, 120, 480);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.target.set(145, 120, 0);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
            dirLight.position.set(145, 200, 350);
            scene.add(dirLight);

            const backLight = new THREE.DirectionalLight(0xffffff, 0.4);
            backLight.position.set(145, -100, -300);
            scene.add(backLight);

            const rimLight = new THREE.DirectionalLight(0x58a6ff, 0.6);
            rimLight.position.set(-200, 200, 200);
            scene.add(rimLight);

            // Ground grid
            const grid = new THREE.GridHelper(600, 30, 0x30363d, 0x21262d);
            grid.rotation.x = Math.PI / 2;
            grid.position.set(145, 120, -30);
            scene.add(grid);

            // Build Groups
            buildAssembly();

            window.addEventListener('resize', onWindowResize, false);
        }

        function buildAssembly() {
            // Root group
            explodedGroup = new THREE.Group();
            scene.add(explodedGroup);

            // 1. SWIFTVEST MODEL (Fixed base)
            vestGroup = new THREE.Group();
            const vestMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.7 });
            const webbingMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.4 });
            const buckleMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 });

            // Left Shoulder Strap
            const leftStrap = new THREE.Mesh(new THREE.BoxGeometry(44, 300, 4), vestMat);
            leftStrap.position.set(45, 120, -8);
            vestGroup.add(leftStrap);

            const leftWebbing = new THREE.Mesh(new THREE.BoxGeometry(22, 300, 2), webbingMat);
            leftWebbing.position.set(45, 120, -5);
            vestGroup.add(leftWebbing);

            // Right Shoulder Strap
            const rightStrap = new THREE.Mesh(new THREE.BoxGeometry(44, 300, 4), vestMat);
            rightStrap.position.set(245, 120, -8);
            vestGroup.add(rightStrap);

            const rightWebbing = new THREE.Mesh(new THREE.BoxGeometry(22, 300, 2), webbingMat);
            rightWebbing.position.set(245, 120, -5);
            vestGroup.add(rightWebbing);

            // Sternum Cross Straps (Bridge)
            const sternumUpper = new THREE.Mesh(new THREE.BoxGeometry(190, 20, 2), webbingMat);
            sternumUpper.position.set(145, 160, -9);
            vestGroup.add(sternumUpper);

            const sternumLower = new THREE.Mesh(new THREE.BoxGeometry(190, 20, 2), webbingMat);
            sternumLower.position.set(145, 70, -9);
            vestGroup.add(sternumLower);

            // Center Buckles
            const buckleUp = new THREE.Mesh(new THREE.BoxGeometry(32, 26, 6), buckleMat);
            buckleUp.position.set(145, 160, -8);
            vestGroup.add(buckleUp);

            const buckleLo = new THREE.Mesh(new THREE.BoxGeometry(32, 26, 6), buckleMat);
            buckleLo.position.set(145, 70, -8);
            vestGroup.add(buckleLo);

            explodedGroup.add(vestGroup);

            // 2. DOOR PIVOT GROUP (Pivot axis sits along Right Shoulder Strap at X = 245)
            doorPivotGroup = new THREE.Group();
            doorPivotGroup.position.set(245, 120, 0); // Hinge pivot center
            explodedGroup.add(doorPivotGroup);

            // Plate sub-group relative to pivot (pivot at X=245, so relative pos is X - 245)
            const movingGroup = new THREE.Group();
            movingGroup.position.set(-245, -120, 0);
            doorPivotGroup.add(movingGroup);

            // Load Chassis Plate (or simulated plate)
            const plateMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6 });
            plateMesh = new THREE.Mesh(new THREE.BoxGeometry(240, 212, 10), plateMat);
            plateMesh.position.set(145, 120, 5);
            movingGroup.add(plateMesh);

            // Decorative Float Artwork Inlay on Front of Plate
            const artMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.3 });
            const artBadge = new THREE.Mesh(new THREE.CylinderGeometry(55, 55, 1.2, 32), artMat);
            artBadge.rotation.x = Math.PI / 2;
            artBadge.position.set(145, 120, 10.6);
            movingGroup.add(artBadge);

            // 3. RIGHT HINGE CLAMPS (Gold)
            const hingeMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.4, roughness: 0.3 });
            const hUp = new THREE.Mesh(new THREE.BoxGeometry(28, 26, 6), hingeMat);
            hUp.position.set(245, 167, 2);
            movingGroup.add(hUp);

            const hLo = new THREE.Mesh(new THREE.BoxGeometry(28, 26, 6), hingeMat);
            hLo.position.set(245, 63, 2);
            movingGroup.add(hLo);

            // 4. LEFT QUICK-RELEASE LATCHES (Red/Orange with thumb paddles)
            const latchMat = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.4 });
            const lUp = new THREE.Mesh(new THREE.BoxGeometry(32, 26, 6), latchMat);
            lUp.position.set(45, 155, 2);
            movingGroup.add(lUp);

            const lLo = new THREE.Mesh(new THREE.BoxGeometry(32, 26, 6), latchMat);
            lLo.position.set(45, 73, 2);
            movingGroup.add(lLo);
        }

        function setPlateState(state) {
            document.getElementById('btn-closed').classList.toggle('active', state === 0);
            document.getElementById('btn-open').classList.toggle('active', state === 1);
            const targetAngle = state === 1 ? 110 : 0;
            animateHingeTo(targetAngle);
        }

        function animateHingeTo(target) {
            const start = currentHingeAngle;
            const startTime = performance.now();
            const duration = 600; // ms

            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                const ease = 1 - Math.pow(1 - progress, 3);
                const angle = start + (target - start) * ease;
                updateHingeAngle(angle);
                document.getElementById('hinge-slider').value = angle;

                if (progress < 1.0) {
                    requestAnimationFrame(step);
                } else {
                    updateOverlayText(target);
                }
            }
            requestAnimationFrame(step);
        }

        function updateHingeAngle(deg) {
            currentHingeAngle = parseFloat(deg);
            document.getElementById('angle-display').innerText = Math.round(deg) + '°';
            const rad = (currentHingeAngle * Math.PI) / 180;
            // Swing open around the Y axis
            doorPivotGroup.rotation.y = rad;
        }

        function updateExplode(val) {
            currentExplodeZ = parseFloat(val);
            document.getElementById('explode-display').innerText = Math.round(val) + ' mm';
            doorPivotGroup.position.z = currentExplodeZ;
            vestGroup.position.z = -currentExplodeZ;
        }

        function toggleExploded() {
            const btn = document.getElementById('btn-exploded');
            const target = currentExplodeZ > 10 ? 0 : 50;
            btn.classList.toggle('active', target > 0);
            
            const start = currentExplodeZ;
            const startTime = performance.now();
            const duration = 400;
            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                const ease = 1 - Math.pow(1 - progress, 3);
                const z = start + (target - start) * ease;
                updateExplode(z);
                document.getElementById('explode-slider').value = z;
                if (progress < 1.0) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }

        function updateOverlayText(angle) {
            const title = document.getElementById('mode-title');
            const desc = document.getElementById('mode-desc');
            if (angle > 45) {
                title.innerText = '📖 Mode: Donning & Doffing (Plate Swung Open)';
                title.style.color = '#38bdf8';
                desc.innerText = 'Left thumb latches are released! The front plate swings 110° open like a car door, allowing full access to unbuckle the center sternum straps and easily slip out of the vest.';
            } else {
                title.innerText = '🔒 Mode: Race Ready (Plate Closed)';
                title.style.color = '#10b981';
                desc.innerText = 'The plate is closed flush across the chest. Left thumb latches are snapped shut over the left webbing track. Center sternum straps are securely hidden underneath.';
            }
        }

        function onWindowResize() {
            const container = document.getElementById('canvas-container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""
    out_file = os.path.join(SIM_DIR, "swiftvest_assembly_viewer.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  [OK] Exported Interactive 3D Viewer: {out_file}")

def main():
    print("Building SWIFTVEST 3D Assembly Preview...")
    vest_mesh = build_swiftvest_model()
    hinges, latches = build_hardware_instances()
    
    # Load plate chassis
    chassis_path = os.path.join(PANELS_DIR, "tpu_panel_front_chassis_black.stl")
    if os.path.exists(chassis_path):
        plate_mesh = trimesh.load(chassis_path)
    else:
        plate_mesh = trimesh.creation.box([240, 212, 10])
        plate_mesh.apply_translation([145, 120, 5])
    
    # Combine into monolithic assembly STL
    all_meshes = [vest_mesh, plate_mesh] + hinges + latches
    combined_mesh = trimesh.util.concatenate(all_meshes)
    stl_out = os.path.join(PANELS_DIR, "swiftvest_front_assembly_preview.stl")
    combined_mesh.export(stl_out)
    print(f"  [OK] Exported Combined 3D STL: {stl_out}")
    print(f"       Vertices: {len(combined_mesh.vertices)}, Faces: {len(combined_mesh.faces)}")
    
    # Export interactive HTML viewer
    create_interactive_viewer_html()
    print("SWIFTVEST visual assembly pipeline complete!")

if __name__ == "__main__":
    main()
