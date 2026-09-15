// Main Street Electrical Parade - LED Costume Simulator
// Interactive HTML5 Canvas Engine with Preset Management & Realistic Fleet Proportions

const canvas = document.getElementById('simulatorCanvas');
const ctx = canvas.getContext('2d');

// State
let currentView = 'single'; // 'single' or 'fleet'
let activePattern = 'dragon_sparkle';

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

// Custom artwork image (if user uploads one or loads one from preset)
let customArtworkImg = null;
let currentGraphicType = 'builtin_dragon'; // 'builtin_dragon' or 'custom_image'
let customArtworkDataUrl = null;

// Dragging state
let draggedLed = null;
let hoveredLed = null;
let isDragging = false;

// 50 LEDs coordinates (normalized 0.0 to 1.0 relative to shirt chest area)
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

// Shirt boundaries in Canvas Space (single shirt view)
function getShirtBounds() {
    const w = canvas.width;
    const h = canvas.height;
    const shirtWidth = Math.min(w * 0.70, 560);
    const shirtHeight = shirtWidth * 1.25; // True athletic t-shirt aspect ratio (1 : 1.25)
    return {
        x: (w - shirtWidth) / 2,
        y: Math.max(30, (h - shirtHeight) / 2 - 20),
        width: shirtWidth,
        height: shirtHeight
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

// Sparkle state per LED
const sparkles = new Array(50).fill(0);

// ============================================================================
// DRAWING ROUTINES: Authentic Athletic T-Shirt with Natural Dimensions
// ============================================================================
function drawRunningShirt(cx, x, y, width, height, label = "PETE'S DRAGON") {
    cx.save();

    // Natural proportions check (ensure athletic ratio 1 : 1.25)
    const collarLeftX = x + width * 0.38;
    const collarRightX = x + width * 0.62;
    const collarY = y + height * 0.07;

    cx.beginPath();
    cx.moveTo(collarLeftX, collarY);
    // Crew neck dip
    cx.quadraticCurveTo(x + width * 0.5, y + height * 0.14, collarRightX, collarY);
    // Right shoulder
    cx.lineTo(x + width * 0.82, y + height * 0.14);
    // Right sleeve
    cx.lineTo(x + width * 0.98, y + height * 0.35);
    cx.lineTo(x + width * 0.85, y + height * 0.44);
    // Right armpit
    cx.lineTo(x + width * 0.76, y + height * 0.37);
    // Right torso down to hem
    cx.lineTo(x + width * 0.74, y + height * 0.94);
    // Bottom hem curve
    cx.quadraticCurveTo(x + width * 0.5, y + height * 0.97, x + width * 0.26, y + height * 0.94);
    // Left torso up
    cx.lineTo(x + width * 0.24, y + height * 0.37);
    // Left armpit & sleeve
    cx.lineTo(x + width * 0.15, y + height * 0.44);
    cx.lineTo(x + width * 0.02, y + height * 0.35);
    // Left shoulder
    cx.lineTo(x + width * 0.18, y + height * 0.14);
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
    cx.arc(x + width * 0.5, y + height * 0.08, width * 0.12, 0.2 * Math.PI, 0.8 * Math.PI);
    cx.stroke();

    // Raglan shoulder lines
    cx.beginPath();
    cx.moveTo(collarLeftX, collarY);
    cx.quadraticCurveTo(x + width * 0.30, y + height * 0.24, x + width * 0.24, y + height * 0.37);
    cx.moveTo(collarRightX, collarY);
    cx.quadraticCurveTo(x + width * 0.70, y + height * 0.24, x + width * 0.76, y + height * 0.37);
    cx.strokeStyle = '#282e37';
    cx.stroke();

    // Hem label badge
    if (label) {
        cx.fillStyle = '#6e7681';
        cx.font = `${Math.max(9, Math.floor(width * 0.08))}px sans-serif`;
        cx.textAlign = 'center';
        cx.fillText(label, x + width * 0.5, y + height * 0.91);
    }

    cx.restore();
}

// ============================================================================
// DRAWING ROUTINES: Green Reflective Pete's Dragon Graphic
// ============================================================================
function drawPetesDragon(cx, s) {
    if (customArtworkImg) {
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
    dragonGrad.addColorStop(0.3, `hsl(${baseH + 15}, 100%, 75%)`);
    dragonGrad.addColorStop(0.7, `hsl(${baseH - 10}, 85%, 45%)`);
    dragonGrad.addColorStop(1, `hsl(${baseH - 25}, 90%, 35%)`);

    // Dragon Body Silhouette Path
    cx.beginPath();
    cx.moveTo(s.x + s.width * 0.36, s.y + s.height * 0.33);
    cx.quadraticCurveTo(s.x + s.width * 0.42, s.y + s.height * 0.25, s.x + s.width * 0.49, s.y + s.height * 0.22);
    cx.lineTo(s.x + s.width * 0.52, s.y + s.height * 0.18);
    cx.lineTo(s.x + s.width * 0.53, s.y + s.height * 0.24);
    cx.lineTo(s.x + s.width * 0.56, s.y + s.height * 0.20);
    cx.lineTo(s.x + s.width * 0.57, s.y + s.height * 0.27);
    cx.quadraticCurveTo(s.x + s.width * 0.60, s.y + s.height * 0.35, s.x + s.width * 0.65, s.y + s.height * 0.38);
    cx.lineTo(s.x + s.width * 0.74, s.y + s.height * 0.30);
    cx.quadraticCurveTo(s.x + s.width * 0.71, s.y + s.height * 0.37, s.x + s.width * 0.76, s.y + s.height * 0.35);
    cx.quadraticCurveTo(s.x + s.width * 0.70, s.y + s.height * 0.43, s.x + s.width * 0.67, s.y + s.height * 0.46);
    cx.quadraticCurveTo(s.x + s.width * 0.72, s.y + s.height * 0.52, s.x + s.width * 0.77, s.y + s.height * 0.55);
    cx.quadraticCurveTo(s.x + s.width * 0.88, s.y + s.height * 0.52, s.x + s.width * 0.86, s.y + s.height * 0.45);
    cx.quadraticCurveTo(s.x + s.width * 0.80, s.y + s.height * 0.44, s.x + s.width * 0.78, s.y + s.height * 0.52);
    cx.quadraticCurveTo(s.x + s.width * 0.72, s.y + s.height * 0.63, s.x + s.width * 0.64, s.y + s.height * 0.64);
    cx.quadraticCurveTo(s.x + s.width * 0.52, s.y + s.height * 0.67, s.x + s.width * 0.42, s.y + s.height * 0.63);
    cx.lineTo(s.x + s.width * 0.38, s.y + s.height * 0.63);
    cx.quadraticCurveTo(s.x + s.width * 0.42, s.y + s.height * 0.47, s.x + s.width * 0.38, s.y + s.height * 0.38);
    cx.quadraticCurveTo(s.x + s.width * 0.34, s.y + s.height * 0.36, s.x + s.width * 0.36, s.y + s.height * 0.33);
    cx.closePath();

    cx.fillStyle = dragonGrad;
    cx.fill();

    if (params.reflectiveShine) {
        cx.lineWidth = 2.5;
        cx.strokeStyle = `hsl(${baseH + 20}, 100%, 85%)`;
        cx.stroke();

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
// LIGHTING ENGINE
// ============================================================================
function computeLedColor(index, totalLeds, timeMs) {
    const bpm = params.speedBpm;
    const beatMs = 60000 / bpm;
    const normTime = timeMs / beatMs;
    const baseH = params.greenHue;

    let r = 0, g = 255, b = 100, brightness = params.brightness / 100;

    switch (activePattern) {
        case 'dragon_sparkle': {
            const breath = 0.75 + 0.25 * Math.sin(normTime * 2 + index * 0.15);
            const h = baseH + Math.sin(index * 0.4) * 8;
            const rgb = hslToRgb(h / 360, 0.95, 0.50 * breath);
            r = rgb.r; g = rgb.g; b = rgb.b;

            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                r = r * (1 - sp) + 255 * sp;
                g = g * (1 - sp) + 255 * sp;
                b = b * (1 - sp) + 230 * sp;
                brightness = Math.min(1.0, brightness + sp * 0.5);
            }
            break;
        }
        case 'fire_breath': {
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
            const step = Math.floor(normTime * 3) % 3;
            if ((index + step) % 3 === 0) {
                r = 255; g = 150; b = 30;
                brightness = 0.9;
            } else {
                r = 10; g = 10; b = 10;
                brightness = 0.1;
            }
            break;
        }
        case 'photo_mode': {
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

    if (sparkles[index] > 0) {
        sparkles[index] = Math.max(0, sparkles[index] - 0.04);
    }
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

function renderBulb(cx, x, y, col, isHovered, isSelected, index) {
    const glowRadius = params.glowSize;

    const grad = cx.createRadialGradient(x, y, 1, x, y, glowRadius);
    grad.addColorStop(0, `rgba(${col.r}, ${col.g}, ${col.b}, 0.9)`);
    grad.addColorStop(0.3, `rgba(${col.r}, ${col.g}, ${col.b}, 0.45)`);
    grad.addColorStop(0.7, `rgba(${col.r}, ${col.g}, ${col.b}, 0.12)`);
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

    cx.fillStyle = grad;
    cx.beginPath();
    cx.arc(x, y, glowRadius, 0, Math.PI * 2);
    cx.fill();

    cx.beginPath();
    cx.arc(x, y, 4.5, 0, Math.PI * 2);
    cx.fillStyle = `rgb(${Math.min(255, col.r + 40)}, ${Math.min(255, col.g + 40)}, ${Math.min(255, col.b + 40)})`;
    cx.fill();

    cx.beginPath();
    cx.arc(x, y, 2.0, 0, Math.PI * 2);
    cx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    cx.fill();

    if (isHovered || isSelected) {
        cx.beginPath();
        cx.arc(x, y, 7.5, 0, Math.PI * 2);
        cx.strokeStyle = isSelected ? '#ffc107' : '#00e5ff';
        cx.lineWidth = 2;
        cx.stroke();
    }

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

    ctx.clearRect(0, 0, w, h);

    drawRunningShirt(ctx, s.x, s.y, s.width, s.height, "FLOAT #3: PETE'S DRAGON");
    drawPetesDragon(ctx, s);

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

    for (let i = 0; i < leds.length; i++) {
        const pt = normToCanvas(leds[i]);
        const col = computeLedColor(i, leds.length, timeMs);
        const isHover = (hoveredLed === i);
        const isSel = (draggedLed === i);
        renderBulb(ctx, pt.x, pt.y, col, isHover, isSel, i);
    }
}

// ============================================================================
// 7-SHIRT FLEET PARADE VIEW (NATURAL ATHELTIC PROPORTIONS)
// ============================================================================
const FLEET_ROSTER = [
    { num: "01", name: "Title Drum", tag: "THE DRUM", color: "#ffb703", accent: "Gold" },
    { num: "02", name: "Casey Jr.", tag: "LOCOMOTIVE", color: "#e63946", accent: "Red" },
    { num: "03", name: "Elliott", tag: "PETE'S DRAGON", color: "#00ff88", accent: "Green" },
    { num: "04", name: "Mushroom", tag: "ALICE", color: "#9d4edd", accent: "Purple" },
    { num: "05", name: "Cinderella", tag: "PUMPKIN COACH", color: "#48cae4", accent: "Cyan" },
    { num: "06", name: "Pirate Ship", tag: "PETER PAN", color: "#fb8500", accent: "Orange" },
    { num: "07", name: "Snail Finale", tag: "SPINNING SNAIL", color: "#ff007f", accent: "Pink" }
];

function renderFleetView(timeMs) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const totalFloats = 7;
    // Natural Athletic Proportions:
    // With 820px canvas width, 7 shirts = ~96px wide each, 120px tall (1 : 1.25 ratio!)
    const shirtW = Math.floor(w / 8.2); // ~100px
    const shirtH = Math.floor(shirtW * 1.25); // ~125px (natural athletic dimensions!)
    const shirtY = h * 0.28; // Centered vertically in upper-mid canvas

    // Master Traveling Wave Clock (7-second loop across 7 runners)
    const masterWaveTime = (timeMs % 7000);
    const activeFloatIndex = Math.floor(masterWaveTime / 1000); // 0 to 6
    const waveProgress = (masterWaveTime % 1000) / 1000; // 0.0 to 1.0

    // Header Title & Subtitle
    ctx.fillStyle = '#ffc107';
    ctx.font = 'bold 15px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText("MAIN STREET ELECTRICAL PARADE — 7-RUNNER FLEET LINEUP", w * 0.5, h * 0.09);

    ctx.fillStyle = '#8b949e';
    ctx.font = '12px sans-serif';
    ctx.fillText("Synchronized ESP-NOW Traveling Wave Passing from Runner 1 to Runner 7", w * 0.5, h * 0.13);

    // Draw Parade Course Road Surface
    ctx.fillStyle = '#161b22';
    ctx.fillRect(w * 0.02, shirtY + shirtH + 90, w * 0.96, 40);
    // Yellow Road Dash Line
    ctx.setLineDash([15, 15]);
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w * 0.02, shirtY + shirtH + 110);
    ctx.lineTo(w * 0.98, shirtY + shirtH + 110);
    ctx.stroke();
    ctx.setLineDash([]);

    for (let i = 0; i < totalFloats; i++) {
        const shirtX = (w * 0.03) + i * (shirtW * 1.08);
        const floatData = FLEET_ROSTER[i];
        const isCurrentWaveFloat = (i === activeFloatIndex);

        // 1. Draw Runner Bib Number Above Shirt
        ctx.fillStyle = isCurrentWaveFloat ? '#ffc107' : '#8b949e';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`BIB #${floatData.num}`, shirtX + shirtW * 0.5, shirtY - 14);

        // 2. Draw Natural Proportioned Shirt (1 : 1.25)
        drawRunningShirt(ctx, shirtX, shirtY, shirtW, shirtH, "");

        // 3. Draw Running Shorts & Legs Below Shirt
        const shortsW = shirtW * 0.44;
        const shortsH = shirtW * 0.35;
        const shortsY = shirtY + shirtH * 0.93;

        // Running Shorts (Black)
        ctx.fillStyle = '#0a0d12';
        ctx.fillRect(shirtX + shirtW * 0.28, shortsY, shortsW, shortsH);
        ctx.strokeStyle = '#21262d';
        ctx.strokeRect(shirtX + shirtW * 0.28, shortsY, shortsW, shortsH);

        // Legs
        ctx.fillStyle = '#484f58';
        ctx.fillRect(shirtX + shirtW * 0.32, shortsY + shortsH, 6, 20);
        ctx.fillRect(shirtX + shirtW * 0.58, shortsY + shortsH, 6, 20);

        // Running Shoes
        ctx.fillStyle = floatData.color;
        ctx.fillRect(shirtX + shirtW * 0.29, shortsY + shortsH + 20, 10, 5);
        ctx.fillRect(shirtX + shirtW * 0.57, shortsY + shortsH + 20, 10, 5);

        // 4. Draw Mini LEDs around chest
        const numMiniLeds = 18;
        const chestCX = shirtX + shirtW * 0.5;
        const chestCY = shirtY + shirtH * 0.50;
        const rx = shirtW * 0.26;
        const ry = shirtH * 0.22;

        for (let j = 0; j < numMiniLeds; j++) {
            const angle = (j / numMiniLeds) * Math.PI * 2;
            const lx = chestCX + Math.cos(angle) * rx;
            const ly = chestCY + Math.sin(angle) * ry;

            let r = 20, g = 20, b = 20;

            if (isCurrentWaveFloat) {
                const ledNorm = j / numMiniLeds;
                const dist = Math.abs(ledNorm - waveProgress);
                if (dist < 0.18) {
                    r = 255; g = 255; b = 255; // White hot center
                } else {
                    r = 255; g = 180; b = 40; // Warm trail
                }
            } else {
                r = 15; g = 35; b = 20;
            }

            ctx.beginPath();
            ctx.arc(lx, ly, isCurrentWaveFloat ? 3.5 : 2, 0, Math.PI * 2);
            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.fill();
        }

        // 5. Float Name Tag Below Runner
        ctx.fillStyle = isCurrentWaveFloat ? '#ffffff' : '#8b949e';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(floatData.name, shirtX + shirtW * 0.5, shirtY + shirtH + 68);

        ctx.fillStyle = isCurrentWaveFloat ? '#ffc107' : '#57606a';
        ctx.font = '9px sans-serif';
        ctx.fillText(floatData.tag, shirtX + shirtW * 0.5, shirtY + shirtH + 80);

        // Wave active highlight indicator
        if (isCurrentWaveFloat) {
            ctx.strokeStyle = '#ffc107';
            ctx.lineWidth = 2;
            ctx.strokeRect(shirtX - 4, shirtY - 25, shirtW + 8, shirtH + 115);
        }
    }
}

// ============================================================================
// INTERACTION & HIT DETECTION
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
// MAIN ANIMATION LOOP
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
// PRESET & PROFILE MANAGEMENT (Save Coordinates + Graphic for Quick Loading)
// ============================================================================

// Load preset list from API & localStorage
async function refreshPresetDropdown() {
    const select = document.getElementById('presetSelect');
    select.innerHTML = '<option value="">-- Select Saved Profile --</option>';

    // 1. Fetch from Python backend
    try {
        const res = await fetch('/api/presets');
        if (res.ok) {
            const serverPresets = await res.json();
            serverPresets.forEach(p => {
                const opt = document.createElement('option');
                opt.value = 'server:' + p.filename;
                opt.textContent = `📁 ${p.name}`;
                select.appendChild(opt);
            });
        }
    } catch (err) {
        console.log("Offline mode, checking local storage...");
    }

    // 2. Fetch from localStorage
    const localProfiles = JSON.parse(localStorage.getItem('msep_custom_presets') || '{}');
    Object.keys(localProfiles).forEach(name => {
        const opt = document.createElement('option');
        opt.value = 'local:' + name;
        opt.textContent = `💾 ${name} (Browser)`;
        select.appendChild(opt);
    });
}

// Save Current Profile (LEDs + Graphic + Settings)
async function saveCurrentProfile(name) {
    if (!name || name.trim() === '') {
        alert("Please enter a name for this costume profile!");
        return;
    }
    const cleanName = name.trim();

    const profileData = {
        name: cleanName,
        savedAt: new Date().toISOString(),
        ledCount: leds.length,
        leds: leds,
        graphicType: currentGraphicType,
        customArtworkDataUrl: customArtworkDataUrl,
        settings: {
            pattern: activePattern,
            speedBpm: params.speedBpm,
            sparkleRate: params.sparkleRate,
            greenHue: params.greenHue,
            brightness: params.brightness,
            glowSize: params.glowSize
        }
    };

    // 1. Save to LocalStorage
    const localProfiles = JSON.parse(localStorage.getItem('msep_custom_presets') || '{}');
    localProfiles[cleanName] = profileData;
    localStorage.setItem('msep_custom_presets', JSON.stringify(localProfiles));

    // 2. Save to Python backend
    try {
        const res = await fetch('/api/save_preset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
        });
        if (res.ok) {
            const result = await res.json();
            alert(`Profile "${cleanName}" saved successfully!`);
        }
    } catch (e) {
        alert(`Profile "${cleanName}" saved to browser cache.`);
    }

    refreshPresetDropdown();
}

// Load Selected Profile
async function loadProfile(sourceValue) {
    if (!sourceValue) return;

    let profileData = null;

    if (sourceValue.startsWith('server:')) {
        const filename = sourceValue.replace('server:', '');
        try {
            const res = await fetch(`/api/preset/${encodeURIComponent(filename)}`);
            if (res.ok) {
                profileData = await res.json();
            }
        } catch (e) {
            alert("Failed to load preset from server.");
            return;
        }
    } else if (sourceValue.startsWith('local:')) {
        const name = sourceValue.replace('local:', '');
        const localProfiles = JSON.parse(localStorage.getItem('msep_custom_presets') || '{}');
        profileData = localProfiles[name];
    }

    if (!profileData) return;

    // 1. Restore LEDs
    if (Array.isArray(profileData.leds) && profileData.leds.length > 0) {
        leds = profileData.leds;
    }

    // 2. Restore Graphic
    currentGraphicType = profileData.graphicType || 'builtin_dragon';
    if (profileData.customArtworkDataUrl) {
        customArtworkDataUrl = profileData.customArtworkDataUrl;
        const img = new Image();
        img.onload = () => {
            customArtworkImg = img;
        };
        img.src = customArtworkDataUrl;
    } else {
        customArtworkImg = null;
    }

    // 3. Restore Settings
    if (profileData.settings) {
        const s = profileData.settings;
        if (s.pattern) {
            activePattern = s.pattern;
            document.getElementById('patternSelect').value = s.pattern;
        }
        if (s.speedBpm) {
            params.speedBpm = s.speedBpm;
            document.getElementById('speedSlider').value = s.speedBpm;
            document.getElementById('speedVal').textContent = `${s.speedBpm} BPM`;
        }
        if (s.sparkleRate !== undefined) {
            params.sparkleRate = s.sparkleRate;
            document.getElementById('sparkleSlider').value = s.sparkleRate;
            document.getElementById('sparkleVal').textContent = `${s.sparkleRate}%`;
        }
        if (s.greenHue !== undefined) {
            params.greenHue = s.greenHue;
            document.getElementById('hueSlider').value = s.greenHue;
            document.getElementById('hueVal').textContent = `${s.greenHue}°`;
        }
        if (s.brightness !== undefined) {
            params.brightness = s.brightness;
            document.getElementById('brightnessSlider').value = s.brightness;
            document.getElementById('brightVal').textContent = `${s.brightness}%`;
        }
        if (s.glowSize !== undefined) {
            params.glowSize = s.glowSize;
            document.getElementById('glowSlider').value = s.glowSize;
            document.getElementById('glowVal').textContent = `${s.glowSize}px`;
        }
    }
}

// Initial Preset Load
refreshPresetDropdown();

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

// ============================================================================
// COMPUTER VISION: AUTO-OUTLINE PERIMETER TRACING (50 LEDs)
// ============================================================================
function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function autoOutlineCurrentGraphic(targetCount = 50) {
    const targetW = 320;
    let targetH = 320;

    const offCanvas = document.createElement('canvas');
    const offCtx = offCanvas.getContext('2d');

    if (customArtworkImg && customArtworkImg.complete && customArtworkImg.naturalWidth > 0) {
        targetH = Math.max(100, Math.round(targetW * (customArtworkImg.naturalHeight / customArtworkImg.naturalWidth)));
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        offCtx.drawImage(customArtworkImg, 0, 0, targetW, targetH);
    } else {
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        const fakeBounds = { x: 0, y: 0, width: targetW, height: targetH };
        drawPetesDragon(offCtx, fakeBounds);
    }

    const imgData = offCtx.getImageData(0, 0, targetW, targetH);
    const data = imgData.data;

    // Detect transparency
    let hasTransparency = false;
    for (let i = 3; i < data.length; i += 16) {
        if (data[i] < 200) {
            hasTransparency = true;
            break;
        }
    }

    // Visibility test
    const isFg = (x, y) => {
        if (x < 0 || x >= targetW || y < 0 || y >= targetH) return false;
        const idx = (y * targetW + x) * 4;
        const a = data[idx + 3];
        if (hasTransparency) {
            return a > 40; // Visible pixels on transparent background
        } else {
            const r = data[idx], g = data[idx + 1], b = data[idx + 2];
            const lum = 0.299 * r + 0.587 * g + 0.114 * b;
            return lum > 40;
        }
    };

    // Find starting top-left foreground pixel
    let startX = -1, startY = -1;
    for (let y = 0; y < targetH; y++) {
        for (let x = 0; x < targetW; x++) {
            if (isFg(x, y)) {
                startX = x;
                startY = y;
                break;
            }
        }
        if (startX !== -1) break;
    }

    if (startX === -1) {
        alert("No visible graphic detected! Make sure your image contains visible content.");
        return;
    }

    // Moore-Neighbor Clockwise Boundary Tracing
    const DIRS = [
        { dx: 0, dy: -1 },  // N
        { dx: 1, dy: -1 },  // NE
        { dx: 1, dy: 0 },   // E
        { dx: 1, dy: 1 },   // SE
        { dx: 0, dy: 1 },   // S
        { dx: -1, dy: 1 },  // SW
        { dx: -1, dy: 0 },  // W
        { dx: -1, dy: -1 }  // NW
    ];

    const rawPerimeter = [];
    let currX = startX, currY = startY;
    let backtrackDir = 6;
    const maxSteps = targetW * targetH * 2;
    let stepCount = 0;

    rawPerimeter.push({ x: currX, y: currY });

    while (stepCount++ < maxSteps) {
        let foundNext = false;
        const checkStart = (backtrackDir + 1) % 8;
        for (let i = 0; i < 8; i++) {
            const checkDir = (checkStart + i) % 8;
            const nx = currX + DIRS[checkDir].dx;
            const ny = currY + DIRS[checkDir].dy;

            if (isFg(nx, ny)) {
                currX = nx;
                currY = ny;
                backtrackDir = (checkDir + 4) % 8;
                foundNext = true;
                break;
            }
        }

        if (!foundNext) break;
        if (currX === startX && currY === startY && rawPerimeter.length > 10) {
            break;
        }
        rawPerimeter.push({ x: currX, y: currY });
    }

    if (rawPerimeter.length < targetCount) {
        alert("The detected outline is too small to distribute 50 LEDs.");
        return;
    }

    // Calculate Cumulative Perimeter Distances
    const cumulativeDist = [0];
    let totalLength = 0;
    for (let i = 1; i < rawPerimeter.length; i++) {
        const d = Math.hypot(rawPerimeter[i].x - rawPerimeter[i - 1].x, rawPerimeter[i].y - rawPerimeter[i - 1].y);
        totalLength += d;
        cumulativeDist.push(totalLength);
    }
    const loopCloseDist = Math.hypot(rawPerimeter[0].x - rawPerimeter[rawPerimeter.length - 1].x, rawPerimeter[0].y - rawPerimeter[rawPerimeter.length - 1].y);
    totalLength += loopCloseDist;

    // Resample 50 equidistant points
    const step = totalLength / targetCount;
    const newLeds = [];

    let searchIdx = 0;
    for (let k = 0; k < targetCount; k++) {
        const targetDist = k * step;

        while (searchIdx < cumulativeDist.length - 1 && cumulativeDist[searchIdx + 1] < targetDist) {
            searchIdx++;
        }

        const p1 = rawPerimeter[searchIdx];
        const p2 = rawPerimeter[(searchIdx + 1) % rawPerimeter.length];
        const segStartDist = cumulativeDist[searchIdx];
        const segEndDist = (searchIdx + 1 < cumulativeDist.length) ? cumulativeDist[searchIdx + 1] : totalLength;
        const segLen = segEndDist - segStartDist;

        let px = p1.x, py = p1.y;
        if (segLen > 0.001) {
            const fraction = (targetDist - segStartDist) / segLen;
            px = p1.x + (p2.x - p1.x) * fraction;
            py = p1.y + (p2.y - p1.y) * fraction;
        }

        // Map into normalized shirt chest area (0.175 + 0.65x, 0.20 + 0.55y)
        const normX = 0.175 + (px / targetW) * 0.65;
        const normY = 0.20 + (py / targetH) * 0.55;

        newLeds.push({
            x: Math.max(0.05, Math.min(0.95, parseFloat(normX.toFixed(3)))),
            y: Math.max(0.05, Math.min(0.95, parseFloat(normY.toFixed(3))))
        });
    }

    leds = newLeds;
    showToast("✨ 50 LEDs redistributed along graphic outline!");
}

// Custom Artwork Image Upload
document.getElementById('artworkUpload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            customArtworkDataUrl = event.target.result;
            currentGraphicType = 'custom_image';
            const img = new Image();
            img.onload = () => {
                customArtworkImg = img;
                // Automatically outline the new image!
                autoOutlineCurrentGraphic(50);
            };
            img.src = customArtworkDataUrl;
        };
        reader.readAsDataURL(file);
    }
});

// Auto-Outline Button Click
document.getElementById('autoOutlineBtn').addEventListener('click', () => {
    autoOutlineCurrentGraphic(50);
});


// Preset Buttons
document.getElementById('presetSelect').addEventListener('change', (e) => {
    loadProfile(e.target.value);
});

document.getElementById('saveProfileBtn').addEventListener('click', () => {
    const nameInput = document.getElementById('profileNameInput');
    const name = nameInput.value.trim() || prompt("Enter a name for this profile:", "Pete's Dragon V1");
    if (name) {
        saveCurrentProfile(name);
        nameInput.value = "";
    }
});

// Export JSON file
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
    for (int i = 0; i < NUM_LEDS; i++) {
        // Deep emerald green base with organic breathing pulse
        uint8_t breath = beatsin8(${Math.round(params.speedBpm / 2)}, 180, 255);
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
