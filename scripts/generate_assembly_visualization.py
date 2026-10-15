#!/usr/bin/env python3
"""
generate_assembly_visualization.py

Builds the ultimate Disney Imagineering visualizer for the SWIFTVEST mounting system:
1. GoPro / Garmin-Style 2-Piece Slide Dock (Female Receiver on plate + Male Cleat on webbing)
   with animated "Slide Down & Click Lock" and "Thumb Release" simulation!
2. Macro Close-Up View of the single-piece locking clip with Z-axis screw.
3. Full Chest View & Rear View of the complete costume.
4. Exports STL files for all components.
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
    <title>SWIFTVEST Mounting Systems 3D Inspector | MSEP 10K Costumes</title>
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
            max-width: 720px;
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
            background: rgba(22, 27, 34, 0.92);
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 14px 18px;
            max-width: 420px;
            font-size: 12px;
            line-height: 1.45;
            z-index: 10;
        }
        #info-overlay h3 {
            color: #58a6ff;
            font-size: 13.5px;
            margin-bottom: 6px;
        }
        .feature-tag {
            display: inline-block;
            background: rgba(46, 160, 67, 0.15);
            border: 1px solid #2ea043;
            color: #3fb950;
            padding: 2px 7px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 10.5px;
            margin-top: 6px;
            margin-right: 4px;
        }
    </style>
</head>
<body>
    <div id="header">
        <div>
            <h1>🎽 SWIFTVEST: 2-Piece GoPro-Style Slide Dock</h1>
            <p>Main Street Electrical Parade (WDW 10K) Costumes | Zero-Friction Assembly</p>
        </div>
        <div style="font-size: 11px; color: #58a6ff; font-weight: 600;">
            Disney Imagineering Pair-Programming
        </div>
    </div>

    <div id="canvas-container">
        <div id="info-overlay">
            <h3 id="mode-title">🎥 2-Piece GoPro-Style Quick-Release Slide Dock</h3>
            <p id="mode-desc">
                <strong>1. Female Receiver (Gold):</strong> Screws permanently to the back of the plate in your workshop with 4x M2 screws. Screws are 100% accessible with no strap in the way!<br><br>
                <strong>2. Male Cleat (Orange):</strong> Clamps onto the vest webbing strap with full two-handed access.<br><br>
                <strong>3. Race Morning:</strong> Hold plate to chest, slide down: <strong>"SLIDE... CLICK!"</strong> Dovetail locks in all 3 axes with zero bounce.
            </p>
            <div>
                <span class="feature-tag">✔ 100% Accessible Screws</span>
                <span class="feature-tag">✔ Zero Webbing Wrestling</span>
                <span class="feature-tag">✔ 1-Second Slide &amp; Click</span>
            </div>
        </div>

        <div id="legend">
            <div style="font-weight: 600; margin-bottom: 4px; color: #f0f6fc;">Components:</div>
            <div class="legend-item"><div class="color-dot" style="background: #f59e0b;"></div> Female Dock (Screws to Plate)</div>
            <div class="legend-item"><div class="color-dot" style="background: #ea580c;"></div> Male Cleat (Clamps to Webbing)</div>
            <div class="legend-item"><div class="color-dot" style="background: #e2e8f0;"></div> 4x M2 Screws (Z-Axis Direct)</div>
            <div class="legend-item"><div class="color-dot" style="background: #38bdf8;"></div> Vest Webbing Strap (22mm)</div>
            <div class="legend-item"><div class="color-dot" style="background: #1e293b;"></div> Plate Back Wall</div>
        </div>

        <div id="controls-panel">
            <div class="btn-group">
                <button class="btn active" id="btn-gopro" onclick="switchMode('gopro')">🎥 GoPro Slide Dock (2-Piece)</button>
                <button class="btn" id="btn-full-front" onclick="switchMode('front')">👤 Full Chest View (Front)</button>
                <button class="btn" id="btn-full-back" onclick="switchMode('back')">🔄 Full Rear View (Back of Plate)</button>
                <button class="btn" id="btn-exploded" onclick="toggleExploded()">💥 Exploded View</button>
            </div>
            <div class="control-row" id="slide-action-row">
                <button class="btn" id="btn-slide-toggle" onclick="toggleSlideAnimation()" style="background: #1f6feb; border-color: #388bfd; color: #fff;">
                    ⚡ Animate: Slide Plate Down &amp; Click Lock
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
        let goproGroup, fullAssemblyGroup;
        let femaleDockGroup, maleCleatGroup, goproWebbing, goproPlateSection;
        let vestGroup, plateGroup, clipsGroup;
        let currentMode = 'gopro';
        let currentExplodeZ = 0;
        let isDockLocked = true;

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
            keyLight.position.set(60, 100, 220);
            scene.add(keyLight);

            const fillLight = new THREE.DirectionalLight(0x58a6ff, 0.6);
            fillLight.position.set(-150, -50, 150);
            scene.add(fillLight);

            const backLight = new THREE.DirectionalLight(0xffffff, 0.45);
            backLight.position.set(0, 100, -220);
            scene.add(backLight);

            // Ground grid
            const grid = new THREE.GridHelper(600, 30, 0x30363d, 0x161b22);
            grid.rotation.x = Math.PI / 2;
            grid.position.set(0, 0, -40);
            scene.add(grid);

            // Build Models
            buildGoProModel();
            buildFullAssembly();

            // Start in GoPro mode
            switchMode('gopro');

            window.addEventListener('resize', onWindowResize, false);
        }

        // ==========================================
        // 1. GOPRO 2-PIECE SLIDE DOCK MODEL
        // ==========================================
        function buildGoProModel() {
            goproGroup = new THREE.Group();
            scene.add(goproGroup);

            const femaleMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.35, roughness: 0.35 });
            const maleMat = new THREE.MeshStandardMaterial({ color: 0xea580c, metalness: 0.35, roughness: 0.35 });
            const webbingMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.5 });
            const plateBackMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
            const screwMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, metalness: 0.9, roughness: 0.15 });

            // A. Section of Plate Back Wall (At Z = +6.0)
            goproPlateSection = new THREE.Group();
            const wall = new THREE.Mesh(new THREE.BoxGeometry(75, 75, 6), plateBackMat);
            wall.position.set(0, 0, 7.0);
            goproPlateSection.add(wall);
            goproGroup.add(goproPlateSection);

            // B. Female Receiver Dock (Screws to Plate Back)
            femaleDockGroup = new THREE.Group();
            
            // Base plate with dovetail channel (26mm wide x 30mm tall x 5.5mm deep)
            const dockBase = new THREE.Mesh(new THREE.BoxGeometry(26, 30, 3.0), femaleMat);
            dockBase.position.set(0, 0, 2.5);
            femaleDockGroup.add(dockBase);

            // Left & Right Dovetail Overhang Lips (trapping male cleat)
            const lipLeft = new THREE.Mesh(new THREE.BoxGeometry(3.5, 26, 2.5), femaleMat);
            lipLeft.position.set(-11.25, 0, 4.0);
            femaleDockGroup.add(lipLeft);

            const lipRight = new THREE.Mesh(new THREE.BoxGeometry(3.5, 26, 2.5), femaleMat);
            lipRight.position.set(11.25, 0, 4.0);
            femaleDockGroup.add(lipRight);

            // Bottom Stop (stops cleat from sliding through bottom)
            const botStop = new THREE.Mesh(new THREE.BoxGeometry(26, 3.5, 3.5), femaleMat);
            botStop.position.set(0, -13.25, 3.5);
            femaleDockGroup.add(botStop);

            // 4x M2 Screws in corners (completely accessible around the perimeter!)
            const screwPositions = [
                [-10.5, 11, 4.2],
                [10.5, 11, 4.2],
                [-10.5, -11, 4.2],
                [10.5, -11, 4.2]
            ];
            screwPositions.forEach(p => {
                const s = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 4.5, 32), screwMat);
                s.rotation.x = Math.PI / 2;
                s.position.set(p[0], p[1], p[2]);
                femaleDockGroup.add(s);
            });

            goproGroup.add(femaleDockGroup);

            // C. Male Cleat (Clamps onto Vest Webbing)
            maleCleatGroup = new THREE.Group();

            // Sliding Wedge Block (fits inside female channel)
            const wedge = new THREE.Mesh(new THREE.BoxGeometry(18, 24, 2.8), maleMat);
            wedge.position.set(0, 0, 1.4);
            maleCleatGroup.add(wedge);

            // Webbing Base Plate (behind wedge, Z = -3 to 0)
            const wBase = new THREE.Mesh(new THREE.BoxGeometry(24, 30, 2.4), maleMat);
            wBase.position.set(0, 0, -1.2);
            maleCleatGroup.add(wBase);

            // Top Spring Release Cantilever Arm with Thumb Tab
            const springArm = new THREE.Mesh(new THREE.BoxGeometry(6, 12, 2.2), maleMat);
            springArm.position.set(0, 16, 2.0);
            maleCleatGroup.add(springArm);

            const thumbTab = new THREE.Mesh(new THREE.BoxGeometry(10, 4.5, 3.5), maleMat);
            thumbTab.position.set(0, 21, 3.0);
            maleCleatGroup.add(thumbTab);

            // Locking tooth (engages with female dock)
            const lockTooth = new THREE.Mesh(new THREE.BoxGeometry(6, 3, 1.8), maleMat);
            lockTooth.position.set(0, 12, 3.2);
            maleCleatGroup.add(lockTooth);

            goproGroup.add(maleCleatGroup);

            // D. Vest Webbing (22mm wide running vertically along Y through male cleat)
            goproWebbing = new THREE.Mesh(new THREE.BoxGeometry(22, 60, 1.8), webbingMat);
            goproWebbing.position.set(0, 0, -2.2);
            goproGroup.add(goproWebbing);
        }

        // ==========================================
        // 2. FULL ASSEMBLY (Turtle Plate + 4 Clips + Vest)
        // ==========================================
        function buildFullAssembly() {
            fullAssemblyGroup = new THREE.Group();
            scene.add(fullAssemblyGroup);

            fullAssemblyGroup.position.set(-145, -120, 0);

            vestGroup = new THREE.Group();
            const vestFabricMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.85 });
            const webbingMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.45 });
            const buckleMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 });

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

            clipsGroup = new THREE.Group();
            const clipMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.35, roughness: 0.35 });
            const clipPositions = [
                [45, 160, -2.5],
                [45, 70, -2.5],
                [245, 160, -2.5],
                [245, 70, -2.5]
            ];

            clipPositions.forEach(p => {
                const c = new THREE.Mesh(new THREE.BoxGeometry(14, 26, 5.5), clipMat);
                c.position.set(p[0], p[1], p[2]);
                clipsGroup.add(c);
            });
            fullAssemblyGroup.add(clipsGroup);

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
            document.getElementById('btn-gopro').classList.toggle('active', mode === 'gopro');
            document.getElementById('btn-full-front').classList.toggle('active', mode === 'front');
            document.getElementById('btn-full-back').classList.toggle('active', mode === 'back');

            const slideRow = document.getElementById('slide-action-row');
            const title = document.getElementById('mode-title');
            const desc = document.getElementById('mode-desc');

            if (mode === 'gopro') {
                goproGroup.visible = true;
                fullAssemblyGroup.visible = false;
                slideRow.style.display = 'flex';

                title.innerText = '🎥 2-Piece GoPro-Style Quick-Release Slide Dock';
                desc.innerHTML = '<strong>1. Female Receiver (Gold):</strong> Screws permanently to the back of the plate in your workshop with 4x M2 screws. Screws are 100% accessible with no strap in the way!<br><br><strong>2. Male Cleat (Orange):</strong> Clamps onto the vest webbing strap with full two-handed access.<br><br><strong>3. Race Morning:</strong> Hold plate to chest, slide down: <strong>"SLIDE... CLICK!"</strong> Dovetail locks in all 3 axes with zero bounce.';

                animateCameraTo(new THREE.Vector3(0, 0, 95), new THREE.Vector3(0, 0, 0));
            } else if (mode === 'front') {
                goproGroup.visible = false;
                fullAssemblyGroup.visible = true;
                slideRow.style.display = 'none';

                title.innerText = '👤 Full Chest View: Clean & Bracket-Free';
                desc.innerText = 'Notice that ZERO brackets stick out past the turtle! The 4 tiny docks are completely hidden behind the plate. The vest straps are thin fabric running under the plate.';

                animateCameraTo(new THREE.Vector3(0, 0, 480), new THREE.Vector3(0, 0, 0));
            } else if (mode === 'back') {
                goproGroup.visible = false;
                fullAssemblyGroup.visible = true;
                slideRow.style.display = 'none';

                title.innerText = '🔄 Full Rear View: Inspecting the 4 Hidden Docks';
                desc.innerText = 'Looking at the back of the plate: The 4 tiny docks (<2.5g each) slide onto the vest straps and lock tightly.';

                animateCameraTo(new THREE.Vector3(0, 0, -480), new THREE.Vector3(0, 0, 0));
            }
        }

        function toggleSlideAnimation() {
            isDockLocked = !isDockLocked;
            const targetY = isDockLocked ? 0.0 : 45.0;
            const btn = document.getElementById('btn-slide-toggle');
            btn.innerText = isDockLocked ? '⚡ Animate: Release Thumb Tab & Slide Plate Up' : '⚡ Animate: Slide Plate Down & Click Lock';

            const startY = femaleDockGroup.position.y;
            const startTime = performance.now();
            const duration = 500;

            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                const ease = 1 - Math.pow(1 - progress, 3);
                const curY = startY + (targetY - startY) * ease;
                femaleDockGroup.position.y = curY;
                goproPlateSection.position.y = curY;
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

            if (currentMode === 'gopro') {
                goproPlateSection.position.z = 7.0 + currentExplodeZ * 0.5;
                femaleDockGroup.position.z = currentExplodeZ * 0.4;
                maleCleatGroup.position.z = -currentExplodeZ * 0.2;
                goproWebbing.position.z = -2.2 - currentExplodeZ * 0.5;
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
    print("Generating updated SWIFTVEST GoPro-style visual pipeline...")
    create_interactive_viewer_html()
    
    import generate_gopro_style_mount
    generate_gopro_style_mount.main()
    
    print("Done!")

if __name__ == "__main__":
    main()
