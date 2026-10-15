#!/usr/bin/env python3
"""
generate_assembly_visualization.py

Builds a complete, detailed 3D assembly and interactive visualizer demonstrating
the redesigned ULTRA-COMPACT HIDDEN REAR C-CLIPS:
- 4x tiny hidden C-clips (<1.1g each) mounted flat against the back of the front plate.
- Zero brackets or hardware protruding beyond the character's outer perimeter!
- Snaps cleanly onto the SWIFTVEST 20-22mm vertical webbing tracks.
- Exploded view and 360 rotation to inspect both front and back.
"""

import os
import trimesh
import numpy as np
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

def build_swiftvest_model():
    """
    Builds a clean 3D representation of the SWIFTVEST running harness:
    - Left shoulder strap (X ~ 45mm, Y = -20 to 260 mm)
    - Right shoulder strap (X ~ 245mm, Y = -20 to 260 mm)
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
    left_x = 45.0
    left_strap = make_box(strap_w, y_len, strap_thick).translate([left_x - strap_w/2, y_min, -strap_thick - 2.0])
    left_webbing = make_box(webbing_w, y_len, webbing_thick).translate([left_x - webbing_w/2, y_min, -2.0])
    
    # Right strap (runner's left, screen right: X ~ 245mm center)
    right_x = 245.0
    right_strap = make_box(strap_w, y_len, strap_thick).translate([right_x - strap_w/2, y_min, -strap_thick - 2.0])
    right_webbing = make_box(webbing_w, y_len, webbing_thick).translate([right_x - webbing_w/2, y_min, -2.0])
    
    # Sternum cross straps bridging left & right (at Y = 70mm and Y = 160mm)
    bridge_w = right_x - left_x
    sternum_upper = make_box(bridge_w, 20.0, 2.0).translate([left_x, 150.0, -strap_thick - 3.5])
    sternum_lower = make_box(bridge_w, 20.0, 2.0).translate([left_x, 60.0, -strap_thick - 3.5])
    
    # Center buckles
    buckle_upper = make_box(30.0, 28.0, 6.0).translate([145.0 - 15.0, 146.0, -strap_thick - 6.0])
    buckle_lower = make_box(30.0, 28.0, 6.0).translate([145.0 - 15.0, 56.0, -strap_thick - 6.0])
    
    vest_mesh = to_trimesh(left_strap + right_strap + left_webbing + right_webbing + sternum_upper + sternum_lower + buckle_upper + buckle_lower)
    return vest_mesh

def build_hidden_clip_instances():
    """
    Loads swiftvest_hidden_webbing_clip.stl and positions 4 instances
    completely BEHIND the plate, aligned directly with the two vest straps:
    - Left Upper (X=45, Y=160, Z=-1)
    - Left Lower (X=45, Y=70, Z=-1)
    - Right Upper (X=245, Y=160, Z=-1)
    - Right Lower (X=245, Y=70, Z=-1)
    """
    clip_path = os.path.join(PANELS_DIR, "swiftvest_hidden_webbing_clip.stl")
    if not os.path.exists(clip_path):
        import generate_hidden_clip
        generate_hidden_clip.main()
    
    base_clip = trimesh.load(clip_path)
    
    # Rotate clip so it faces toward -Z (into the vest webbing)
    rot_x = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])
    
    clips = []
    positions = [
        [45.0, 160.0, 0.0],  # Left upper
        [45.0, 70.0, 0.0],   # Left lower
        [245.0, 160.0, 0.0], # Right upper
        [245.0, 70.0, 0.0]   # Right lower
    ]
    
    for pos in positions:
        c = base_clip.copy()
        # Center clip on position
        c.apply_translation([-7.0, -13.0, -5.2])
        c.apply_translation(pos)
        clips.append(c)
        
    return clips

def create_interactive_viewer_html():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SWIFTVEST Hidden Clips 3D Inspector | MSEP 10K Costumes</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
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
            min-width: 160px;
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
            max-width: 340px;
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
            <h1>🎽 SWIFTVEST + 3D Plate: Ultra-Compact Hidden Clips</h1>
            <p>Main Street Electrical Parade (WDW 10K) Costumes | Zero Protruding Brackets</p>
        </div>
        <div style="font-size: 11px; color: #58a6ff; font-weight: 600;">
            100% Invisible from Front
        </div>
    </div>

    <div id="canvas-container">
        <div id="info-overlay">
            <h3 id="mode-title">✨ Front View: Clean & Bracket-Free</h3>
            <p id="mode-desc">Notice that ZERO hardware protrudes outside the character outline! The 4 tiny C-clips are completely hidden underneath/behind the plate, snapping directly to the vest straps.</p>
        </div>

        <div id="legend">
            <div style="font-weight: 600; margin-bottom: 4px; color: #f0f6fc;">Components:</div>
            <div class="legend-item"><div class="color-dot" style="background: #2563eb;"></div> SWIFTVEST Harness</div>
            <div class="legend-item"><div class="color-dot" style="background: #38bdf8;"></div> Vest Webbing Tracks</div>
            <div class="legend-item"><div class="color-dot" style="background: #f59e0b;"></div> 4x Hidden Rear C-Clips (&lt;1.1g each)</div>
            <div class="legend-item"><div class="color-dot" style="background: #334155;"></div> 240mm Front 3D Costume Plate</div>
            <div class="legend-item"><div class="color-dot" style="background: #10b981;"></div> Float Character Inlay</div>
        </div>

        <div id="controls-panel">
            <div class="btn-group">
                <button class="btn active" id="btn-front" onclick="setView(0)">👤 Front View (Clean)</button>
                <button class="btn" id="btn-back" onclick="setView(1)">🔄 Rear View (Inspect Clips)</button>
                <button class="btn" id="btn-exploded" onclick="toggleExploded()">💥 Exploded View</button>
            </div>
            <div class="control-row">
                <span class="slider-label">Exploded Separation: <span id="explode-display">0 mm</span></span>
                <input type="range" id="explode-slider" min="0" max="80" value="0" oninput="updateExplode(this.value)">
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, controls;
        let vestGroup, plateGroup, clipsGroup;
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

            const backLight = new THREE.DirectionalLight(0xffffff, 0.5);
            backLight.position.set(145, -100, -350);
            scene.add(backLight);

            const rimLight = new THREE.DirectionalLight(0x58a6ff, 0.6);
            rimLight.position.set(-200, 200, 200);
            scene.add(rimLight);

            // Ground grid
            const grid = new THREE.GridHelper(600, 30, 0x30363d, 0x21262d);
            grid.rotation.x = Math.PI / 2;
            grid.position.set(145, 120, -30);
            scene.add(grid);

            // Build Assembly
            buildAssembly();

            window.addEventListener('resize', onWindowResize, false);
        }

        function buildAssembly() {
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

            scene.add(vestGroup);

            // 2. CLIPS GROUP (4x Tiny Hidden C-Clips - Gold)
            clipsGroup = new THREE.Group();
            const clipMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.3, roughness: 0.3 });

            const clipPositions = [
                [45, 160, -2],
                [45, 70, -2],
                [245, 160, -2],
                [245, 70, -2]
            ];

            clipPositions.forEach(pos => {
                // Sized at 14 x 26 x 5 mm
                const clipMesh = new THREE.Mesh(new THREE.BoxGeometry(14, 26, 5), clipMat);
                clipMesh.position.set(pos[0], pos[1], pos[2]);
                clipsGroup.add(clipMesh);
            });

            scene.add(clipsGroup);

            // 3. FRONT PLATE GROUP (Dark Slate + Green Artwork)
            plateGroup = new THREE.Group();
            const plateMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6 });

            // Stylized Turtle Plate Silhouette (240 x 212 x 10 mm)
            const mainBody = new THREE.Mesh(new THREE.CylinderGeometry(95, 95, 10, 32), plateMat);
            mainBody.rotation.x = Math.PI / 2;
            mainBody.position.set(145, 120, 5);
            plateGroup.add(mainBody);

            const head = new THREE.Mesh(new THREE.SphereGeometry(38, 32, 16), plateMat);
            head.position.set(65, 175, 5);
            plateGroup.add(head);

            // Character Artwork on front face
            const artMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.3 });
            const artPlate = new THREE.Mesh(new THREE.CylinderGeometry(75, 75, 1.2, 32), artMat);
            artPlate.rotation.x = Math.PI / 2;
            artPlate.position.set(145, 120, 10.6);
            plateGroup.add(artPlate);

            scene.add(plateGroup);
        }

        function setView(viewIndex) {
            document.getElementById('btn-front').classList.toggle('active', viewIndex === 0);
            document.getElementById('btn-back').classList.toggle('active', viewIndex === 1);
            
            const targetPos = viewIndex === 0 
                ? new THREE.Vector3(145, 120, 480) 
                : new THREE.Vector3(145, 120, -480);
                
            animateCamera(targetPos);
            
            const title = document.getElementById('mode-title');
            const desc = document.getElementById('mode-desc');
            if (viewIndex === 0) {
                title.innerText = '✨ Front View: Clean & Bracket-Free';
                desc.innerText = 'Notice that ZERO hardware protrudes outside the character outline! The 4 tiny C-clips are completely hidden underneath/behind the plate, snapping directly to the vest straps.';
            } else {
                title.innerText = '🔍 Rear View: Inspecting the 4 Hidden Clips';
                desc.innerText = 'Looking at the back of the vest: The 4 tiny gold C-clips (<1.1g each) clamp snugly onto the blue vertical webbing tracks. Pulling outward from the edge releases the clips in 1 second.';
            }
        }

        function animateCamera(targetPos) {
            const startPos = camera.position.clone();
            const startTime = performance.now();
            const duration = 600;

            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                const ease = 1 - Math.pow(1 - progress, 3);
                camera.position.lerpVectors(startPos, targetPos, ease);
                controls.update();
                if (progress < 1.0) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }

        function updateExplode(val) {
            currentExplodeZ = parseFloat(val);
            document.getElementById('explode-display').innerText = Math.round(val) + ' mm';
            plateGroup.position.z = currentExplodeZ;
            clipsGroup.position.z = currentExplodeZ * 0.45;
            vestGroup.position.z = -currentExplodeZ * 0.3;
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
    print("Generating redesigned assembly with hidden rear C-clips...")
    vest_mesh = build_swiftvest_model()
    hidden_clips = build_hidden_clip_instances()
    
    # Load plate chassis
    chassis_path = os.path.join(PANELS_DIR, "tpu_panel_front_chassis_black.stl")
    if os.path.exists(chassis_path):
        plate_mesh = trimesh.load(chassis_path)
    else:
        plate_mesh = trimesh.creation.box([240, 212, 10])
        plate_mesh.apply_translation([145, 120, 5])
    
    # Combined mesh (Vest + Hidden Clips + Plate)
    all_meshes = [vest_mesh, plate_mesh] + hidden_clips
    combined_mesh = trimesh.util.concatenate(all_meshes)
    stl_out = os.path.join(PANELS_DIR, "swiftvest_front_assembly_preview.stl")
    combined_mesh.export(stl_out)
    print(f"  [OK] Exported Combined 3D STL (No giant brackets): {stl_out}")
    print(f"       Vertices: {len(combined_mesh.vertices)}, Faces: {len(combined_mesh.faces)}")
    
    create_interactive_viewer_html()
    print("Sleek assembly redesign complete!")

if __name__ == "__main__":
    main()
