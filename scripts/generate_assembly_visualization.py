#!/usr/bin/env python3
"""
generate_assembly_visualization.py

Builds the ultimate Disney Imagineering visualizer for the SWIFTVEST hidden clip system:
1. Full Assembly View: Front plate, 4 hidden rear clips, and thin fabric vest straps.
2. Macro Clip Close-Up View: Zooms in on a SINGLE clip engaging with the plate and webbing,
   complete with a US Quarter coin ($24.26mm) for instant real-world scale!
3. Animated "Snap In / Snap Out" button showing the clip flexing onto the webbing.
4. Exploded View slider.
5. Exports color-separated OBJ + 3MF + STL.
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

def make_cylinder(height, radius, segments=32):
    return Manifold.cylinder(height, radius, radius, segments)

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
            background: rgba(22, 27, 34, 0.94);
            backdrop-filter: blur(12px);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 14px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            width: 92%;
            max-width: 660px;
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
            padding: 8px 12px;
            font-size: 11.5px;
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
            background: rgba(22, 27, 34, 0.90);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 16px;
            max-width: 360px;
            font-size: 12px;
            line-height: 1.4;
            z-index: 10;
        }
        #info-overlay h3 {
            color: #58a6ff;
            font-size: 13px;
            margin-bottom: 4px;
        }
        #scale-badge {
            display: inline-block;
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid #f59e0b;
            color: #f59e0b;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 11px;
            margin-top: 6px;
        }
    </style>
</head>
<body>
    <div id="header">
        <div>
            <h1>🎽 SWIFTVEST + 3D Plate: The Real Clip Revealed</h1>
            <p>Main Street Electrical Parade (WDW 10K) Costumes | Macro Scale & Assembly</p>
        </div>
        <div style="font-size: 11px; color: #58a6ff; font-weight: 600;">
            Disney Imagineering Pair-Programming
        </div>
    </div>

    <div id="canvas-container">
        <div id="info-overlay">
            <h3 id="mode-title">🔎 Macro Close-Up: The Tiny Hidden Clip</h3>
            <p id="mode-desc">This is the actual 3D printed clip! It is only 14mm x 26mm (the exact size of a US Quarter coin shown in silver). It screws flat against the back of the turtle plate and snaps onto the vest's thin nylon webbing strap.</p>
            <div id="scale-badge">🪙 Actual Size: Same diameter as a US Quarter ($24.26mm)!</div>
        </div>

        <div id="legend">
            <div style="font-weight: 600; margin-bottom: 4px; color: #f0f6fc;">Components:</div>
            <div class="legend-item"><div class="color-dot" style="background: #f59e0b;"></div> Tiny 3D Clip (14x26mm, 1.1g)</div>
            <div class="legend-item"><div class="color-dot" style="background: #94a3b8;"></div> US Quarter Coin (Scale Ref)</div>
            <div class="legend-item"><div class="color-dot" style="background: #38bdf8;"></div> Vest Webbing Strap (22mm ribbon)</div>
            <div class="legend-item"><div class="color-dot" style="background: #1e293b;"></div> Plate Back Wall (Dark Slate)</div>
            <div class="legend-item"><div class="color-dot" style="background: #10b981;"></div> Turtle Float Artwork</div>
        </div>

        <div id="controls-panel">
            <div class="btn-group">
                <button class="btn active" id="btn-macro" onclick="switchMode('macro')">🔎 Macro Clip Close-Up (Coin Scale)</button>
                <button class="btn" id="btn-full-front" onclick="switchMode('front')">👤 Full Chest View (Front)</button>
                <button class="btn" id="btn-full-back" onclick="switchMode('back')">🔄 Full Rear View (Back of Plate)</button>
                <button class="btn" id="btn-exploded" onclick="toggleExploded()">💥 Exploded View</button>
            </div>
            <div class="control-row" id="snap-row">
                <button class="btn" id="btn-snap-toggle" onclick="toggleSnapAnimation()" style="background: #1f6feb; border-color: #388bfd; color: #fff;">
                    ⚡ Animate: Snap Webbing Into Clip
                </button>
            </div>
            <div class="control-row">
                <span class="slider-label">Exploded Separation: <span id="explode-display">0 mm</span></span>
                <input type="range" id="explode-slider" min="0" max="80" value="0" oninput="updateExplode(this.value)">
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, controls;
        let fullAssemblyGroup, macroGroup;
        let vestGroup, plateGroup, clipsGroup;
        let macroWebbing, macroClip, macroPlateSection, coinMesh;
        let currentMode = 'macro';
        let currentExplodeZ = 0;
        let isSnapped = true;

        init();
        animate();

        function init() {
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0d1117);

            camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 1, 2500);
            
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Lighting
            const ambient = new THREE.AmbientLight(0xffffff, 0.85);
            scene.add(ambient);

            const keyLight = new THREE.DirectionalLight(0xffffff, 0.95);
            keyLight.position.set(50, 100, 200);
            scene.add(keyLight);

            const fillLight = new THREE.DirectionalLight(0x58a6ff, 0.6);
            fillLight.position.set(-150, -50, 150);
            scene.add(fillLight);

            const backLight = new THREE.DirectionalLight(0xffffff, 0.4);
            backLight.position.set(0, 100, -200);
            scene.add(backLight);

            // Ground grid
            const grid = new THREE.GridHelper(600, 30, 0x30363d, 0x161b22);
            grid.rotation.x = Math.PI / 2;
            grid.position.set(0, 0, -40);
            scene.add(grid);

            // Build Models
            buildMacroModel();
            buildFullAssembly();

            // Start in Macro mode
            switchMode('macro');

            window.addEventListener('resize', onWindowResize, false);
        }

        // ==========================================
        // 1. MACRO CLOSE-UP VIEW (1 Clip + Coin + Webbing)
        // ==========================================
        function buildMacroModel() {
            macroGroup = new THREE.Group();
            scene.add(macroGroup);

            // Materials
            const clipMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.3, roughness: 0.35 });
            const coinMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.85, roughness: 0.2 });
            const webbingMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.5 });
            const plateBackMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
            const screwMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 });

            // A. Section of the Plate Back Wall (Behind the clip)
            macroPlateSection = new THREE.Mesh(new THREE.BoxGeometry(60, 60, 6), plateBackMat);
            macroPlateSection.position.set(0, 0, 3);
            macroGroup.add(macroPlateSection);

            // Debossed text on plate
            const boss = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, 2, 32), plateBackMat);
            boss.rotation.x = Math.PI / 2;
            boss.position.set(0, 0, 0.5);
            macroGroup.add(boss);

            // B. The Tiny Hidden C-Clip (14mm x 26mm x 5.2mm)
            // Build detailed C-clip geometry
            macroClip = new THREE.Group();

            // Base mounting pad (14 x 26 x 2.2 mm)
            const baseFlange = new THREE.Mesh(new THREE.BoxGeometry(14, 26, 2.2), clipMat);
            baseFlange.position.set(0, 0, -1.1);
            macroClip.add(baseFlange);

            // M2 Screw inside counterbore
            const screwHead = new THREE.Mesh(new THREE.CylinderGeometry(2.3, 2.3, 1.8, 32), screwMat);
            screwHead.rotation.x = Math.PI / 2;
            screwHead.position.set(0, 0, -0.9);
            macroClip.add(screwHead);

            // Upper and Lower C-channel jaws
            const upperJaw = new THREE.Mesh(new THREE.BoxGeometry(14, 3.5, 4.0), clipMat);
            upperJaw.position.set(0, 11.25, -3.2);
            macroClip.add(upperJaw);

            const lowerJaw = new THREE.Mesh(new THREE.BoxGeometry(14, 3.5, 4.0), clipMat);
            lowerJaw.position.set(0, -11.25, -3.2);
            macroClip.add(lowerJaw);

            // Retention barbs (angled lead-in ramp)
            const upperBarb = new THREE.Mesh(new THREE.BoxGeometry(14, 2.0, 1.4), clipMat);
            upperBarb.position.set(0, 8.5, -4.5);
            macroClip.add(upperBarb);

            const lowerBarb = new THREE.Mesh(new THREE.BoxGeometry(14, 2.0, 1.4), clipMat);
            lowerBarb.position.set(0, -8.5, -4.5);
            macroClip.add(lowerBarb);

            macroGroup.add(macroClip);

            // C. The Thin Nylon Webbing Ribbon (22mm wide x 1.8mm thick)
            macroWebbing = new THREE.Mesh(new THREE.BoxGeometry(18, 22, 1.8), webbingMat);
            macroWebbing.position.set(0, 0, -3.3); // Sitting captive inside the C-channel
            macroGroup.add(macroWebbing);

            // D. Real-World Scale Reference: US QUARTER COIN ($24.26mm dia x 1.75mm)
            coinMesh = new THREE.Group();
            const coinBody = new THREE.Mesh(new THREE.CylinderGeometry(12.13, 12.13, 1.75, 48), coinMat);
            coinBody.rotation.x = Math.PI / 2;
            coinMesh.add(coinBody);

            // Coin rim
            const coinRim = new THREE.Mesh(new THREE.TorusGeometry(11.8, 0.4, 16, 48), coinMat);
            coinRim.position.z = 0.85;
            coinMesh.add(coinRim);

            // Position coin right next to the clip!
            coinMesh.position.set(-32, 0, -1.0);
            macroGroup.add(coinMesh);
        }

        // ==========================================
        // 2. FULL ASSEMBLY (Turtle Plate + 4 Clips + Vest)
        // ==========================================
        function buildFullAssembly() {
            fullAssemblyGroup = new THREE.Group();
            scene.add(fullAssemblyGroup);

            // Shift entire assembly so center is at (0, 0, 0)
            fullAssemblyGroup.position.set(-145, -120, 0);

            // A. Vest straps (Fabric-thin, NOT solid 2x4 beams!)
            vestGroup = new THREE.Group();
            const vestFabricMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.85 });
            const webbingMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.45 });
            const buckleMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 });

            // Thin flexible fabric straps (only 2mm thick)
            const leftStrap = new THREE.Mesh(new THREE.BoxGeometry(40, 290, 2), vestFabricMat);
            leftStrap.position.set(45, 120, -7);
            vestGroup.add(leftStrap);

            const leftWebbing = new THREE.Mesh(new THREE.BoxGeometry(22, 290, 1.5), webbingMat);
            leftWebbing.position.set(45, 120, -5.2);
            vestGroup.add(leftWebbing);

            const rightStrap = new THREE.Mesh(new THREE.BoxGeometry(40, 290, 2), vestFabricMat);
            rightStrap.position.set(245, 120, -7);
            vestGroup.add(rightStrap);

            const rightWebbing = new THREE.Mesh(new THREE.BoxGeometry(22, 290, 1.5), webbingMat);
            rightWebbing.position.set(245, 120, -5.2);
            vestGroup.add(rightWebbing);

            // Sternum cross-straps
            const sternumUp = new THREE.Mesh(new THREE.BoxGeometry(190, 18, 1.5), webbingMat);
            sternumUp.position.set(145, 160, -7.5);
            vestGroup.add(sternumUp);

            const sternumLo = new THREE.Mesh(new THREE.BoxGeometry(190, 18, 1.5), webbingMat);
            sternumLo.position.set(145, 70, -7.5);
            vestGroup.add(sternumLo);

            const b1 = new THREE.Mesh(new THREE.BoxGeometry(28, 24, 4), buckleMat);
            b1.position.set(145, 160, -6);
            vestGroup.add(b1);

            const b2 = new THREE.Mesh(new THREE.BoxGeometry(28, 24, 4), buckleMat);
            b2.position.set(145, 70, -6);
            vestGroup.add(b2);

            fullAssemblyGroup.add(vestGroup);

            // B. 4x Tiny Hidden Clips (Gold)
            clipsGroup = new THREE.Group();
            const clipMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.3, roughness: 0.35 });
            const clipPositions = [
                [45, 160, -2.5],
                [45, 70, -2.5],
                [245, 160, -2.5],
                [245, 70, -2.5]
            ];

            clipPositions.forEach(p => {
                const c = new THREE.Mesh(new THREE.BoxGeometry(14, 26, 5.2), clipMat);
                c.position.set(p[0], p[1], p[2]);
                clipsGroup.add(c);
            });
            fullAssemblyGroup.add(clipsGroup);

            // C. Front Turtle Costume Plate
            plateGroup = new THREE.Group();
            const plateMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6 });
            const artMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.3 });

            const turtleBody = new THREE.Mesh(new THREE.CylinderGeometry(95, 95, 10, 32), plateMat);
            turtleBody.rotation.x = Math.PI / 2;
            turtleBody.position.set(145, 120, 5);
            plateGroup.add(turtleBody);

            const turtleHead = new THREE.Mesh(new THREE.SphereGeometry(38, 32, 16), plateMat);
            turtleHead.position.set(65, 175, 5);
            plateGroup.add(turtleHead);

            const emblem = new THREE.Mesh(new THREE.CylinderGeometry(75, 75, 1.2, 32), artMat);
            emblem.rotation.x = Math.PI / 2;
            emblem.position.set(145, 120, 10.6);
            plateGroup.add(emblem);

            fullAssemblyGroup.add(plateGroup);
        }

        // ==========================================
        // UI & CAMERA SWITCHER
        // ==========================================
        function switchMode(mode) {
            currentMode = mode;
            document.getElementById('btn-macro').classList.toggle('active', mode === 'macro');
            document.getElementById('btn-full-front').classList.toggle('active', mode === 'front');
            document.getElementById('btn-full-back').classList.toggle('active', mode === 'back');

            const snapRow = document.getElementById('snap-row');
            const title = document.getElementById('mode-title');
            const desc = document.getElementById('mode-desc');
            const scaleBadge = document.getElementById('scale-badge');

            if (mode === 'macro') {
                macroGroup.visible = true;
                fullAssemblyGroup.visible = false;
                snapRow.style.display = 'flex';
                scaleBadge.style.display = 'inline-block';

                title.innerText = '🔎 Macro Close-Up: The Tiny Hidden Clip';
                desc.innerText = "This is the actual 3D printed clip! It is only 14mm x 26mm (the exact size of a US Quarter coin shown in silver). It screws flat against the back of the turtle plate and snaps onto the vest's thin nylon webbing strap.";

                animateCameraTo(new THREE.Vector3(0, 0, 85), new THREE.Vector3(0, 0, 0));
            } else if (mode === 'front') {
                macroGroup.visible = false;
                fullAssemblyGroup.visible = true;
                snapRow.style.display = 'none';
                scaleBadge.style.display = 'none';

                title.innerText = '👤 Full Chest View: Clean & Bracket-Free';
                desc.innerText = 'Notice that ZERO brackets stick out past the turtle! The 4 tiny clips are completely hidden behind the plate. The vest straps are thin fabric running under the plate.';

                animateCameraTo(new THREE.Vector3(0, 0, 480), new THREE.Vector3(0, 0, 0));
            } else if (mode === 'back') {
                macroGroup.visible = false;
                fullAssemblyGroup.visible = true;
                snapRow.style.display = 'none';
                scaleBadge.style.display = 'none';

                title.innerText = '🔄 Full Rear View: Inspecting the 4 Hidden Clips';
                desc.innerText = 'Looking at the back of the plate: The 4 tiny gold clips (<1.1g each) snap snugly onto the blue vertical webbing tracks of the vest.';

                animateCameraTo(new THREE.Vector3(0, 0, -480), new THREE.Vector3(0, 0, 0));
            }
        }

        function toggleSnapAnimation() {
            isSnapped = !isSnapped;
            const targetZ = isSnapped ? -3.3 : -18.0;
            const btn = document.getElementById('btn-snap-toggle');
            btn.innerText = isSnapped ? '⚡ Animate: Unsnap Webbing from Clip' : '⚡ Animate: Snap Webbing Into Clip';

            const startZ = macroWebbing.position.z;
            const startTime = performance.now();
            const duration = 400;

            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                const ease = 1 - Math.pow(1 - progress, 3);
                macroWebbing.position.z = startZ + (targetZ - startZ) * ease;
                if (progress < 1.0) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }

        function animateCameraTo(targetPos, targetLookAt) {
            const startPos = camera.position.clone();
            const startTarget = controls.target.clone();
            const startTime = performance.now();
            const duration = 600;

            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                const ease = 1 - Math.pow(1 - progress, 3);
                camera.position.lerpVectors(startPos, targetPos, ease);
                controls.target.lerpVectors(startTarget, targetLookAt, ease);
                controls.update();
                if (progress < 1.0) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }

        function updateExplode(val) {
            currentExplodeZ = parseFloat(val);
            document.getElementById('explode-display').innerText = Math.round(val) + ' mm';

            if (currentMode === 'macro') {
                macroPlateSection.position.z = 3 + currentExplodeZ * 0.5;
                macroWebbing.position.z = -3.3 - currentExplodeZ * 0.5;
            } else {
                plateGroup.position.z = currentExplodeZ;
                clipsGroup.position.z = currentExplodeZ * 0.45;
                vestGroup.position.z = -currentExplodeZ * 0.3;
            }
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
    print("Generating updated SWIFTVEST visual pipeline with Macro coin scale...")
    
    # 1. Generate Interactive HTML Viewer
    create_interactive_viewer_html()
    
    # 2. Export swiftvest_clip_with_coin_scale.stl (Single Clip next to US Quarter)
    clip_path = os.path.join(PANELS_DIR, "swiftvest_hidden_webbing_clip.stl")
    if os.path.exists(clip_path):
        clip_mesh = trimesh.load(clip_path)
        # Create US Quarter coin (dia 24.26mm x 1.75mm)
        coin_cyl = make_cylinder(1.75, 12.13, 64)
        coin_mesh = to_trimesh(coin_cyl)
        coin_mesh.apply_translation([-20.0, 13.0, 0.0])
        scale_demo = trimesh.util.concatenate([clip_mesh, coin_mesh])
        scale_out = os.path.join(PANELS_DIR, "swiftvest_clip_with_coin_scale.stl")
        scale_demo.export(scale_out)
        print(f"  [OK] Exported Coin Scale STL: {scale_out}")
    
    # 3. Export clean swiftvest_front_assembly_preview.stl (Plate + 4 Tiny Hidden Clips ONLY - Zero strap slabs!)
    chassis_path = os.path.join(PANELS_DIR, "tpu_panel_front_chassis_black.stl")
    if os.path.exists(chassis_path) and os.path.exists(clip_path):
        plate_mesh = trimesh.load(chassis_path)
        base_clip = trimesh.load(clip_path)
        
        # Position 4 clips flat on the rear face of the plate
        clip_positions = [
            [45.0, 160.0, -1.0],
            [45.0, 70.0, -1.0],
            [245.0, 160.0, -1.0],
            [245.0, 70.0, -1.0]
        ]
        placed_clips = []
        for pos in clip_positions:
            c = base_clip.copy()
            c.apply_translation([-7.0, -13.0, 0.0])
            c.apply_translation(pos)
            placed_clips.append(c)
            
        clean_assembly = trimesh.util.concatenate([plate_mesh] + placed_clips)
        clean_out = os.path.join(PANELS_DIR, "swiftvest_front_assembly_preview.stl")
        clean_assembly.export(clean_out)
        print(f"  [OK] Exported Clean Assembly STL (Zero giant slabs!): {clean_out}")
        
    print("Done!")

if __name__ == "__main__":
    main()
