// Main Street Electrical Parade - LED Costume Simulator
// Interactive HTML5 Canvas Engine

const canvas = document.getElementById('simulatorCanvas');
const ctx = canvas.getContext('2d');

// State
let currentView = 'single'; // 'single' or 'fleet'
let activePattern = 'dragon_sparkle'; // 'dragon_sparkle', 'fire_breath', 'traveling_wave', 'marquee', 'photo_mode'

// Control parameters
let params = {
    speedBpm: 120,
    sparkleRate: 40,
    greenHue: 140, // 100 = lime, 140 = emerald, 165 = seafoam
    brightness: 80,
    glowSize: 22,
    showWiring: false,
    showNumbers: false,
    reflectiveShine: true
};

// Custom artwork image (if user uploads one)
let customArtworkImg = null;

// Dragging state
let draggedLed = null;
let hoveredLed = null;
let isDragging = false;

// 50 LEDs coordinates (normalized 0.0 to 1.0 relative to shirt chest area)
// Tracing Pete's Dragon outline: Horns -> Snout -> Spine/Wings -> Belly -> Tail
let leds = [];

function initDefaultDragonLeds() {
    leds = [
        // Snout & Head (0 - 6)
        { x: 0.44, y: 0.28 }, { x: 0.41, y: 0.29 }, { x: 0.38, y: 0.31 },
        { x: 0.36, y: 0.33 }, { x: 0.38, y: 0.36 }, { x: 0.41, y: 0.38 }, { x: 0.45, y: 0.39 },
        // Neck & Front Leg (7 - 12)
        { x: 0.43, y: 0.43 }, { x: 0.41, y: 0.48 }, { x: 0.39, y: 0.54 },
        { x: 0.37, y: 0.60 }, { x: 0.39, y: 0.63 }, { x: 0.43, y: 0.62 },
        // Belly & Foot (13 - 18)
        { x: 0.46, y: 0.63 }, { x: 0.50, y: 0.64 }, { x: 0.54, y: 0.65 },
        { x: 0.58, y: 0.65 }, { x: 0.61, y: 0.64 }, { x: 0.64, y: 0.62 },
        // Back Leg & Tail Base (19 - 25)
        { x: 0.66, y: 0.65 }, { x: 0.69, y: 0.65 }, { x: 0.72, y: 0.63 },
        { x: 0.74, y: 0.60 }, { x: 0.76, y: 0.58 }, { x: 0.79, y: 0.56 }, { x: 0.82, y: 0.55 },
        // Tail Tip & Curl (26 - 31)
        { x: 0.85, y: 0.53 }, { x: 0.87, y: 0.50 }, { x: 0.86, y: 0.47 },
        { x: 0.83, y: 0.46 }, { x: 0.80, y: 0.48 }, { x: 0.77, y: 0.50 },
        // Upper Back & Wing Tip (32 - 39)
        { x: 0.74, y: 0.47 }, { x: 0.72, y: 0.43 }, { x: 0.73, y: 0.38 },
        { x: 0.75, y: 0.34 }, { x: 0.72, y: 0.33 }, { x: 0.68, y: 0.36 },
        { x: 0.65, y: 0.40 }, { x: 0.62, y: 0.43 },
        // Dragon Horns & Crest (40 - 49)
        { x: 0.59, y: 0.39 }, { x: 0.56, y: 0.36 }, { x: 0.54, y: 0.32 },
        { x: 0.53, y: 0.28 }, { x: 0.52, y: 0.24 }, { x: 0.50, y: 0.21 },
        { x: 0.48, y: 0.23 }, { x: 0.47, y: 0.26 }, { x: 0.46, y: 0.29 }, { x: 0.45, y: 0.28 }
    ];
}

initDefaultDragonLeds();

// Shirt boundaries in Canvas Space
function getShirtBounds() {
    const w = canvas.width;
    const h = canvas.height;
    return {
        x: w * 0.15,
        y: h * 0.08,
        width: w * 0.70,
        height: h * 0.84
    };
}

// Convert normalized (0..1) to canvas pixels
function normToCanvas(pt) {
    const s = getShirtBounds();
    return {
        x: s.x + pt.x * s.width,
        y: s.y + pt.y * s.height
    };
}

// Convert canvas pixels to normalized
function canvasToNorm(x, y) {
    const s = getShirtBounds();
    return {
        x: Math.max(0, Math.min(1, (x - s.x) / s.width)),
        y: Math.max(0, Math.min(1, (y - s.y) / s.height))
    };
}

// Sparkle state per LED (intensity and decay)
const sparkles = new Array(50).fill(0);

// ============================================================================
// DRAWING ROUTINES: Black Tech Running Shirt
// ============================================================================
function drawRunningShirt(cx, x, y, width, height, label = "PETE'S DRAGON") {
    cx.save();

    // Shirt Body Silhouette
    cx.beginPath();
    // Collar center
    const collarLeftX = x + width * 0.40;
    const collarRightX = x + width * 0.60;
    const collarY = y + height * 0.06;

    cx.moveTo(collarLeftX, collarY);
    // Crew neck dip
    cx.quadraticCurveTo(x + width * 0.5, y + height * 0.11, collarRightX, collarY);
    // Right shoulder
    cx.lineTo(x + width * 0.82, y + height * 0.12);
    // Right sleeve
    cx.lineTo(x + width * 0.98, y + height * 0.32);
    cx.lineTo(x + width * 0.86, y + height * 0.40);
    // Right armpit
    cx.lineTo(x + width * 0.78, y + height * 0.34);
    // Right torso down to hem
    cx.lineTo(x + width * 0.76, y + height * 0.95);
    // Bottom hem curve
    cx.quadraticCurveTo(x + width * 0.5, y + height * 0.98, x + width * 0.24, y + height * 0.95);
    // Left torso up
    cx.lineTo(x + width * 0.22, y + height * 0.34);
    // Left armpit & sleeve
    cx.lineTo(x + width * 0.14, y + height * 0.40);
    cx.lineTo(x + width * 0.02, y + height * 0.32);
    // Left shoulder
    cx.lineTo(x + width * 0.18, y + height * 0.12);
    cx.closePath();

    // Matte Black Tech Fabric Gradient
    const fabricGrad = cx.createLinearGradient(x, y, x + width, y + height);
    fabricGrad.addColorStop(0, '#1c1f24');
    fabricGrad.addColorStop(0.5, '#121418');
    fabricGrad.addColorStop(1, '#0b0d10');
    cx.fillStyle = fabricGrad;
    cx.fill();

    // Fabric subtle rim highlight
    cx.lineWidth = 2;
    cx.strokeStyle = '#2d333b';
    cx.stroke();

    // Athletic Seams & Collar Trim
    cx.beginPath();
    cx.strokeStyle = '#38404a';
    cx.lineWidth = 1.5;
    // Collar ribbing
    cx.arc(x + width * 0.5, y + height * 0.07, width * 0.12, 0.2 * Math.PI, 0.8 * Math.PI);
    cx.stroke();

    // Raglan athletic shoulder seam lines
    cx.beginPath();
    cx.moveTo(collarLeftX, collarY);
    cx.quadraticCurveTo(x + width * 0.30, y + height * 0.22, x + width * 0.22, y + height * 0.34);
    cx.moveTo(collarRightX, collarY);
    cx.quadraticCurveTo(x + width * 0.70, y + height * 0.22, x + width * 0.78, y + height * 0.34);
    cx.strokeStyle = '#282e37';
    cx.stroke();

    // Subtle runDisney-style chest tag
    cx.fillStyle = '#444d56';
    cx.font = '10px sans-serif';
    cx.textAlign = 'center';
    cx.fillText(label, x + width * 0.5, y + height * 0.92);

    cx.restore();
}

// ============================================================================
// DRAWING ROUTINES: Green Reflective Pete's Dragon Graphic
// ============================================================================
function drawPetesDragon(cx, s) {
    if (customArtworkImg) {
        // Draw user uploaded image
        const imgW = s.width * 0.65;
        const imgH = s.height * 0.55;
        cx.drawImage(customArtworkImg, s.x + s.width * 0.175, s.y + s.height * 0.20, imgW, imgH);
        return;
    }

    cx.save();

    // Metallic Green Reflective Material Gradient
    const dragonGrad = cx.createLinearGradient(s.x, s.y, s.x + s.width, s.y + s.height);
    const baseH = params.greenHue;
    dragonGrad.addColorStop(0, `hsl(${baseH}, 90%, 55%)`);
    dragonGrad.addColorStop(0.3, `hsl(${baseH + 15}, 100%, 75%)`); // Specular metallic sheen
    dragonGrad.addColorStop(0.7, `hsl(${baseH - 10}, 85%, 45%)`);
    dragonGrad.addColorStop(1, `hsl(${baseH - 25}, 90%, 35%)`);

    // Dragon Body Silhouette Path
    cx.beginPath();
    // Start at dragon nose/snout
    cx.moveTo(s.x + s.width * 0.36, s.y + s.height * 0.33);
    // Head crest & horns
    cx.quadraticCurveTo(s.x + s.width * 0.42, s.y + s.height * 0.25, s.x + s.width * 0.49, s.y + s.height * 0.22);
    // Horn spike 1
    cx.lineTo(s.x + s.width * 0.52, s.y + s.height * 0.18);
    cx.lineTo(s.x + s.width * 0.53, s.y + s.height * 0.24);
    // Horn spike 2
    cx.lineTo(s.x + s.width * 0.56, s.y + s.height * 0.20);
    cx.lineTo(s.x + s.width * 0.57, s.y + s.height * 0.27);
    // Neck down to back
    cx.quadraticCurveTo(s.x + s.width * 0.60, s.y + s.height * 0.35, s.x + s.width * 0.65, s.y + s.height * 0.38);
    // Wings
    cx.lineTo(s.x + s.width * 0.74, s.y + s.height * 0.30); // Wing tip 1
    cx.quadraticCurveTo(s.x + s.width * 0.71, s.y + s.height * 0.37, s.x + s.width * 0.76, s.y + s.height * 0.35); // Wing tip 2
    cx.quadraticCurveTo(s.x + s.width * 0.70, s.y + s.height * 0.43, s.x + s.width * 0.67, s.y + s.height * 0.46);
    // Lower back & spine ridges
    cx.quadraticCurveTo(s.x + s.width * 0.72, s.y + s.height * 0.52, s.x + s.width * 0.77, s.y + s.height * 0.55);
    // Tail curl
    cx.quadraticCurveTo(s.x + s.width * 0.88, s.y + s.height * 0.52, s.x + s.width * 0.86, s.y + s.height * 0.45);
    cx.quadraticCurveTo(s.x + s.width * 0.80, s.y + s.height * 0.44, s.x + s.width * 0.78, s.y + s.height * 0.52);
    // Bottom of tail & back leg
    cx.quadraticCurveTo(s.x + s.width * 0.72, s.y + s.height * 0.63, s.x + s.width * 0.64, s.y + s.height * 0.64);
    // Belly curve
    cx.quadraticCurveTo(s.x + s.width * 0.52, s.y + s.height * 0.67, s.x + s.width * 0.42, s.y + s.height * 0.63);
    // Front foot
    cx.lineTo(s.x + s.width * 0.38, s.y + s.height * 0.63);
    // Chest up to chin
    cx.quadraticCurveTo(s.x + s.width * 0.42, s.y + s.height * 0.47, s.x + s.width * 0.38, s.y + s.height * 0.38);
    // Chin & snout
    cx.quadraticCurveTo(s.x + s.width * 0.34, s.y + s.height * 0.36, s.x + s.width * 0.36, s.y + s.height * 0.33);
    cx.closePath();

    // Fill with metallic gradient
    cx.fillStyle = dragonGrad;
    cx.fill();

    // Reflective Vinyl High-Gloss Bevel
    if (params.reflectiveShine) {
        cx.lineWidth = 2.5;
        cx.strokeStyle = `hsl(${baseH + 20}, 100%, 85%)`;
        cx.stroke();

        // Iridescent interior accents (wings & belly plates)
        cx.beginPath();
        cx.moveTo(s.x + s.width * 0.45, s.y + s.height * 0.46);
        cx.quadraticCurveTo(s.x + s.width * 0.53, s.y + s.height * 0.52, s.x + s.width * 0.61, s.y + s.height * 0.48);
        cx.strokeStyle = `rgba(255, 255, 255, 0.4)`;
        cx.lineWidth = 2;
        cx.stroke();
    }

    cx.restore();
}

// ============================================================================
// LIGHTING ENGINE: Colors, Sparkles, and Halos
// ============================================================================
function computeLedColor(index, totalLeds, timeMs) {
    const bpm = params.speedBpm;
    const beatMs = 60000 / bpm;
    const normTime = timeMs / beatMs;
    const baseH = params.greenHue;

    let r = 0, g = 255, b = 100, brightness = params.brightness / 100;

    switch (activePattern) {
        case 'dragon_sparkle': {
            // Predominantly green with breathing glow
            const breath = 0.75 + 0.25 * Math.sin(normTime * 2 + index * 0.15);
            // HSL to RGB approximation for emerald/lime green
            const h = baseH + Math.sin(index * 0.4) * 8;
            const rgb = hslToRgb(h / 360, 0.95, 0.50 * breath);
            r = rgb.r; g = rgb.g; b = rgb.b;

            // Sparkle logic
            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                // Blend toward dazzling incandescent white
                r = r * (1 - sp) + 255 * sp;
                g = g * (1 - sp) + 255 * sp;
                b = b * (1 - sp) + 230 * sp;
                brightness = Math.min(1.0, brightness + sp * 0.5);
            }
            break;
        }
        case 'fire_breath': {
            // Snout LEDs (0-6) breathe fiery orange/red, body is green
            if (index <= 6) {
                const fire = Math.sin(normTime * 6 + index) * 0.5 + 0.5;
                r = 255;
                g = Math.floor(60 + fire * 100);
                b = 10;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.85, 0.45);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            break;
        }
        case 'traveling_wave': {
            // Wave head sweeping 0 to 49
            const waveCycle = (timeMs % 2000) / 2000;
            const head = waveCycle * totalLeds;
            const dist = Math.abs(index - head);

            if (dist < 3.5) {
                const intensity = Math.max(0, 1 - (dist / 3.5));
                r = 255 * intensity;
                g = 255 * intensity;
                b = Math.floor(200 * intensity);
                brightness = 1.0;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.9, 0.25);
                r = rgb.r; g = rgb.g; b = rgb.b;
                brightness = 0.35;
            }
            break;
        }
        case 'marquee': {
            // Classic 1-in-3 incandescent chase
            const step = Math.floor(normTime * 3) % 3;
            if ((index + step) % 3 === 0) {
                r = 255; g = 150; b = 30; // Incandescent Amber Gold
                brightness = 0.9;
            } else {
                r = 10; g = 10; b = 10;
                brightness = 0.1;
            }
            break;
        }
        case 'photo_mode': {
            // Solid high-visibility green and marquee gold
            if (index % 2 === 0) {
                const rgb = hslToRgb(baseH / 360, 1.0, 0.55);
                r = rgb.r; g = rgb.g; b = rgb.b;
            } else {
                r = 255; g = 180; b = 50;
            }
            brightness = 1.0;
            break;
        }
    }

    // Decay sparkle
    if (sparkles[index] > 0) {
        sparkles[index] = Math.max(0, sparkles[index] - 0.04);
    }
    // Trigger new sparkles randomly based on slider
    if (activePattern === 'dragon_sparkle' && Math.random() * 1000 < params.sparkleRate) {
        sparkles[index] = 1.0;
    }

    return {
        r: Math.floor(r * brightness),
        g: Math.floor(g * brightness),
        b: Math.floor(b * brightness),
        alpha: brightness
    };
}

// Draw a single blooming LED
function renderBulb(cx, x, y, col, isHovered, isSelected, index) {
    const glowRadius = params.glowSize;

    // 1. Soft Outer Bloom Halo
    const grad = cx.createRadialGradient(x, y, 1, x, y, glowRadius);
    grad.addColorStop(0, `rgba(${col.r}, ${col.g}, ${col.b}, 0.9)`);
    grad.addColorStop(0.3, `rgba(${col.r}, ${col.g}, ${col.b}, 0.45)`);
    grad.addColorStop(0.7, `rgba(${col.r}, ${col.g}, ${col.b}, 0.12)`);
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

    cx.fillStyle = grad;
    cx.beginPath();
    cx.arc(x, y, glowRadius, 0, Math.PI * 2);
    cx.fill();

    // 2. Physical Glass Bead / Lens
    cx.beginPath();
    cx.arc(x, y, 4.5, 0, Math.PI * 2);
    cx.fillStyle = `rgb(${Math.min(255, col.r + 40)}, ${Math.min(255, col.g + 40)}, ${Math.min(255, col.b + 40)})`;
    cx.fill();

    // 3. Hot White Filament Center
    cx.beginPath();
    cx.arc(x, y, 2.0, 0, Math.PI * 2);
    cx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    cx.fill();

    // Selection / Hover rings
    if (isHovered || isSelected) {
        cx.beginPath();
        cx.arc(x, y, 7.5, 0, Math.PI * 2);
        cx.strokeStyle = isSelected ? '#ffc107' : '#00e5ff';
        cx.lineWidth = 2;
        cx.stroke();
    }

    // Optional LED numbering
    if (params.showNumbers) {
        cx.fillStyle = '#ffffff';
        cx.font = '9px monospace';
        cx.fillText(index, x + 6, y - 6);
    }
}

// ============================================================================
// SINGLE SHIRT VIEW
// ============================================================================
function renderSingleShirtView(timeMs) {
    const w = canvas.width;
    const h = canvas.height;
    const s = getShirtBounds();

    // Clear background
    ctx.clearRect(0, 0, w, h);

    // 1. Draw Black Running Shirt
    drawRunningShirt(ctx, s.x, s.y, s.width, s.height, "FLOAT #3: PETE'S DRAGON");

    // 2. Draw Pete's Dragon Graphic
    drawPetesDragon(ctx, s);

    // 3. Draw Wiring Path (if enabled)
    if (params.showWiring && leds.length > 1) {
        ctx.beginPath();
        const p0 = normToCanvas(leds[0]);
        ctx.moveTo(p0.x, p0.y);
        for (let i = 1; i < leds.length; i++) {
            const pt = normToCanvas(leds[i]);
            ctx.lineTo(pt.x, pt.y);
        }
        ctx.strokeStyle = 'rgba(255, 193, 7, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
    }

    // 4. Draw 50 Blooming LEDs
    for (let i = 0; i < leds.length; i++) {
        const pt = normToCanvas(leds[i]);
        const col = computeLedColor(i, leds.length, timeMs);
        const isHover = (hoveredLed === i);
        const isSel = (draggedLed === i);
        renderBulb(ctx, pt.x, pt.y, col, isHover, isSel, i);
    }
}

// ============================================================================
// 7-SHIRT FLEET PARADE VIEW
// ============================================================================
const FLEET_ROSTER = [
    { num: 1, name: "Title Drum", color: "#ffb703" },
    { num: 2, name: "Casey Jr", color: "#e63946" },
    { num: 3, name: "Elliott", color: "#00ff88" },
    { num: 4, name: "Mushroom", color: "#9d4edd" },
    { num: 5, name: "Cinderella", color: "#48cae4" },
    { num: 6, name: "Pirate Ship", color: "#fb8500" },
    { num: 7, name: "Snail Finale", color: "#ff007f" }
];

function renderFleetView(timeMs) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const totalFloats = 7;
    const shirtW = w / 7.6;
    const shirtH = h * 0.70;
    const shirtY = h * 0.15;

    // Master Traveling Wave Clock (7-second loop across 7 runners)
    const masterWaveTime = (timeMs % 7000);
    const activeFloatIndex = Math.floor(masterWaveTime / 1000); // 0 to 6
    const waveProgress = (masterWaveTime % 1000) / 1000; // 0.0 to 1.0

    for (let i = 0; i < totalFloats; i++) {
        const shirtX = (w * 0.03) + i * (shirtW * 1.05);
        const floatData = FLEET_ROSTER[i];

        // Draw Mini Shirt
        drawRunningShirt(ctx, shirtX, shirtY, shirtW, shirtH, `#${floatData.num} ${floatData.name}`);

        // Draw Mini LEDs around chest
        const numMiniLeds = 20;
        const chestCX = shirtX + shirtW * 0.5;
        const chestCY = shirtY + shirtH * 0.5;
        const rx = shirtW * 0.28;
        const ry = shirtH * 0.22;

        const isCurrentWaveFloat = (i === activeFloatIndex);

        for (let j = 0; j < numMiniLeds; j++) {
            const angle = (j / numMiniLeds) * Math.PI * 2;
            const lx = chestCX + Math.cos(angle) * rx;
            const ly = chestCY + Math.sin(angle) * ry;

            let r = 30, g = 30, b = 30;

            if (isCurrentWaveFloat) {
                // Wave is actively sweeping this float!
                const ledNorm = j / numMiniLeds;
                const dist = Math.abs(ledNorm - waveProgress);
                if (dist < 0.2) {
                    r = 255; g = 255; b = 255; // White hot wave center
                } else {
                    r = 255; g = 180; b = 40;
                }
            } else {
                // Soft idle color
                r = 15; g = 35; b = 20;
            }

            // Draw mini bulb
            ctx.beginPath();
            ctx.arc(lx, ly, isCurrentWaveFloat ? 3.5 : 2, 0, Math.PI * 2);
            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.fill();
        }
    }

    // Title banner
    ctx.fillStyle = '#ffc107';
    ctx.font = '14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText("MAIN STREET ELECTRICAL PARADE — 7-RUNNER SYNCHRONIZED FLEET", w * 0.5, h * 0.08);
}

// ============================================================================
// INTERACTION & HIT DETECTION (Dragging LEDs)
// ============================================================================
canvas.addEventListener('mousedown', (e) => {
    if (currentView !== 'single') return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    for (let i = 0; i < leds.length; i++) {
        const pt = normToCanvas(leds[i]);
        const dist = Math.hypot(mx - pt.x, my - pt.y);
        if (dist <= 14) {
            draggedLed = i;
            isDragging = true;
            canvas.classList.add('dragging');
            break;
        }
    }
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    if (isDragging && draggedLed !== null) {
        const norm = canvasToNorm(mx, my);
        leds[draggedLed].x = norm.x;
        leds[draggedLed].y = norm.y;
    } else {
        // Hover detection
        let found = null;
        for (let i = 0; i < leds.length; i++) {
            const pt = normToCanvas(leds[i]);
            const dist = Math.hypot(mx - pt.x, my - pt.y);
            if (dist <= 14) {
                found = i;
                break;
            }
        }
        hoveredLed = found;
        canvas.style.cursor = found !== null ? 'pointer' : 'default';
    }
});

window.addEventListener('mouseup', () => {
    isDragging = false;
    draggedLed = null;
    canvas.classList.remove('dragging');
});

// ============================================================================
// MAIN LOOP
// ============================================================================
function animate(time) {
    if (currentView === 'single') {
        renderSingleShirtView(time);
    } else {
        renderFleetView(time);
    }
    requestAnimationFrame(animate);
}

requestAnimationFrame(animate);

// ============================================================================
// UI CONTROLS BINDING
// ============================================================================
document.getElementById('patternSelect').addEventListener('change', (e) => {
    activePattern = e.target.value;
});

document.getElementById('speedSlider').addEventListener('input', (e) => {
    params.speedBpm = parseInt(e.target.value);
    document.getElementById('speedVal').textContent = `${params.speedBpm} BPM`;
});

document.getElementById('sparkleSlider').addEventListener('input', (e) => {
    params.sparkleRate = parseInt(e.target.value);
    document.getElementById('sparkleVal').textContent = `${params.sparkleRate}%`;
});

document.getElementById('hueSlider').addEventListener('input', (e) => {
    params.greenHue = parseInt(e.target.value);
    document.getElementById('hueVal').textContent = `${params.greenHue}°`;
});

document.getElementById('brightnessSlider').addEventListener('input', (e) => {
    params.brightness = parseInt(e.target.value);
    document.getElementById('brightVal').textContent = `${params.brightness}%`;
});

document.getElementById('glowSlider').addEventListener('input', (e) => {
    params.glowSize = parseInt(e.target.value);
    document.getElementById('glowVal').textContent = `${params.glowSize}px`;
});

document.getElementById('showWiringToggle').addEventListener('change', (e) => {
    params.showWiring = e.target.checked;
});

document.getElementById('showNumbersToggle').addEventListener('change', (e) => {
    params.showNumbers = e.target.checked;
});

document.getElementById('resetLedsBtn').addEventListener('click', () => {
    initDefaultDragonLeds();
});

// View Toggle
document.getElementById('singleViewBtn').addEventListener('click', () => {
    currentView = 'single';
    document.getElementById('singleViewBtn').classList.add('active');
    document.getElementById('fleetViewBtn').classList.remove('active');
});

document.getElementById('fleetViewBtn').addEventListener('click', () => {
    currentView = 'fleet';
    document.getElementById('fleetViewBtn').classList.add('active');
    document.getElementById('singleViewBtn').classList.remove('active');
});

// Custom Artwork Image Upload
document.getElementById('artworkUpload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                customArtworkImg = img;
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// Save / Export Coordinates to JSON
document.getElementById('saveLayoutBtn').addEventListener('click', () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(leds, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", "petes_dragon_led_coords.json");
    dlAnchor.click();
});

// Generate FastLED C++ Code
document.getElementById('exportCodeBtn').addEventListener('click', () => {
    const code = `// ============================================================================
// FASTLED ANIMATION: PETE'S DRAGON FLOAT (GENERATED BY SIMULATOR)
// ============================================================================
void renderPetesDragonCustom(uint32_t t) {
    // Base Green Hue: ${params.greenHue}° | Tempo: ${params.speedBpm} BPM
    uint32_t beat = (t * ${params.speedBpm}) / 60000;
    
    for (int i = 0; i < NUM_LEDS; i++) {
        // Deep emerald green base with organic breathing pulse
        uint8_t breath = beatsin8(${params.speedBpm / 2}, 180, 255);
        leds[i] = CHSV(${Math.floor(params.greenHue * 255 / 360)}, 240, breath);
        
        // Starlight Sparkles (Probability: ${params.sparkleRate}%)
        if (random8() < ${Math.floor(params.sparkleRate * 0.4)}) {
            leds[i] = CRGB(255, 255, 230); // Incandescent starlight flash
        }
    }
}`;

    document.getElementById('codeOutput').textContent = code;
    document.getElementById('codeModal').classList.add('open');
});

document.getElementById('closeModalBtn').addEventListener('click', () => {
    document.getElementById('codeModal').classList.remove('open');
});

document.getElementById('copyCodeBtn').addEventListener('click', () => {
    const codeText = document.getElementById('codeOutput').textContent;
    navigator.clipboard.writeText(codeText).then(() => {
        alert("FastLED C++ code copied to clipboard!");
    });
});

// Utility: HSL to RGB
function hslToRgb(h, s, l) {
    let r, g, b;
    if (s === 0) {
        r = g = b = l;
    } else {
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1/6) return p + (q - p) * 6 * t;
            if (t < 1/2) return q;
            if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        };
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        r = hue2rgb(p, q, h + 1/3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1/3);
    }
    return {
        r: Math.round(r * 255),
        g: Math.round(g * 255),
        b: Math.round(b * 255)
    };
}
