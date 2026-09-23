// Main Street Electrical Parade - LED Costume Simulator
// Interactive HTML5 Canvas Engine with Preset Management & Realistic Fleet Proportions

const canvas = document.getElementById('simulatorCanvas');
const ctx = canvas.getContext('2d');

// State
let currentView = 'single'; // 'single' or 'fleet'
let activePattern = 'steady_sparkle'; // 'steady_sparkle', 'color_match', 'dragon_sparkle', etc.

// Control parameters
let params = {
    speedBpm: 120,
    sparkleRate: 40,
    greenHue: 140, // 100 = lime, 140 = emerald, 165 = seafoam
    brightness: 85,
    glowSize: 20,
    showWiring: false,
    showNumbers: false,
    reflectiveShine: true
};

// Default Pete's Dragon Artwork
const defaultDragonImg = new Image();
let defaultDragonLoaded = false;
defaultDragonImg.onload = () => {
    defaultDragonLoaded = true;
    // If starting fresh without saved profile, scatter 100 color-matched LEDs
    if (leds.length === 0 || activePattern === 'steady_sparkle' || activePattern === 'color_match') {
        scatterLedsOnGraphic(100, true);
    }
};
defaultDragonImg.src = 'assets/petes_dragon.png';

// Cinderella's Coach Artwork
const cinderellasCoachImg = new Image();
let cinderellasCoachLoaded = false;
cinderellasCoachImg.onload = () => {
    cinderellasCoachLoaded = true;
};
cinderellasCoachImg.src = 'assets/cinderellas_coach.png';

// Custom artwork image (if user uploads one or loads one from preset)
let customArtworkImg = null;
let currentGraphicType = 'builtin_dragon'; // 'builtin_dragon', 'cinderellas_coach', or 'custom_image'
let customArtworkDataUrl = null;

function getActiveGraphicImg() {
    if (currentGraphicType === 'custom_image' && customArtworkImg && customArtworkImg.complete && customArtworkImg.naturalWidth > 0) {
        return customArtworkImg;
    }
    if (currentGraphicType === 'cinderellas_coach') {
        if (cinderellasCoachImg && cinderellasCoachImg.naturalWidth > 0) {
            return cinderellasCoachImg;
        }
        return cinderellasCoachImg;
    }
    if (defaultDragonLoaded && defaultDragonImg.complete && defaultDragonImg.naturalWidth > 0) {
        return defaultDragonImg;
    }
    return null;
}

// Compute normalized bounds of the graphic on the athletic shirt
function getGraphicChestBounds() {
    const activeImg = getActiveGraphicImg();
    let normH = 0.62;
    let normW = 0.54;
    let normY = 0.18;

    if (activeImg && activeImg.naturalWidth > 0 && activeImg.naturalHeight > 0) {
        const aspect = activeImg.naturalWidth / activeImg.naturalHeight;
        if (aspect > 1.3) {
            // Wide landscape graphic (like Cinderella's Coach: aspect ~ 1.789)
            normW = 0.70;
            normH = normW / (1.25 * aspect);
            normY = 0.22 + (0.40 - normH) * 0.4;
        } else {
            // Portrait or square graphic (like Pete's Dragon: aspect ~ 0.706)
            normH = 0.62;
            normW = normH * 1.25 * aspect;
            if (normW > 0.65) {
                normW = 0.65;
                normH = normW / (1.25 * aspect);
            }
            normY = 0.18;
        }
    }
    const normX = (1.0 - normW) / 2;
    return { normX, normY, normW, normH };
}

// Zoom & Pan state (Smooth interactive navigation)
let zoomScale = 1.0;
let panX = 0;
let panY = 0;
const minZoom = 0.6;
const maxZoom = 5.0;

let isPanning = false;
let panStartX = 0;
let panStartY = 0;
let isSpacePressed = false;
let mouseStartX = 0;
let mouseStartY = 0;
let hasMovedSignificantly = false;

// Selection & Dragging state
let selectedLed = null; // Primary / last selected LED index
let selectedLeds = new Set(); // Multi-selection set of LED indices
let isBoxSelectMode = false; // Toggleable box-select mode
let isBoxSelecting = false;
let boxStartX = 0;
let boxStartY = 0;
let boxCurrentX = 0;
let boxCurrentY = 0;

let draggedLed = null;
let hoveredLed = null;
let isDraggingLed = false;

// Animation Groups & Zones
// Array of { id, name, ledIndices: [idx...], effect: 'chase'|'flash_slow'|..., speedBpm, direction, width, colorMode, customColor }
let animationGroups = [];
let ledGroupMap = {}; // mapping: ledIndex -> { group, indexInGroup, groupSize }

function rebuildLedGroupMap() {
    ledGroupMap = {};
    for (const grp of animationGroups) {
        if (!grp || !Array.isArray(grp.ledIndices)) continue;
        for (let pos = 0; pos < grp.ledIndices.length; pos++) {
            const idx = grp.ledIndices[pos];
            ledGroupMap[idx] = {
                group: grp,
                indexInGroup: pos,
                groupSize: grp.ledIndices.length
            };
        }
    }
}

// LEDs array: [{ x, y, color: {r, g, b} }]
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
    updateLedCountUI();
}

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
let sparkles = new Array(100).fill(0);

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
    const activeImg = getActiveGraphicImg();
    if (activeImg) {
        const gb = getGraphicChestBounds();
        const gx = s.x + gb.normX * s.width;
        const gy = s.y + gb.normY * s.height;
        const gw = gb.normW * s.width;
        const gh = gb.normH * s.height;
        cx.drawImage(activeImg, gx, gy, gw, gh);
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

    // Belly patch (Lime)
    cx.beginPath();
    cx.moveTo(s.x + s.width * 0.44, s.y + s.height * 0.45);
    cx.quadraticCurveTo(s.x + s.width * 0.56, s.y + s.height * 0.46, s.x + s.width * 0.59, s.y + s.height * 0.63);
    cx.quadraticCurveTo(s.x + s.width * 0.48, s.y + s.height * 0.66, s.x + s.width * 0.43, s.y + s.height * 0.62);
    cx.closePath();
    cx.fillStyle = '#a6e22e';
    cx.fill();

    // Wings (Hot Pink)
    cx.beginPath();
    cx.moveTo(s.x + s.width * 0.65, s.y + s.height * 0.38);
    cx.lineTo(s.x + s.width * 0.77, s.y + s.height * 0.30);
    cx.quadraticCurveTo(s.x + s.width * 0.73, s.y + s.height * 0.37, s.x + s.width * 0.79, s.y + s.height * 0.36);
    cx.quadraticCurveTo(s.x + s.width * 0.71, s.y + s.height * 0.44, s.x + s.width * 0.67, s.y + s.height * 0.46);
    cx.closePath();
    cx.fillStyle = '#ff2a8d';
    cx.fill();

    // Hair Tuft on Head (Bright Orange / Coral)
    cx.beginPath();
    cx.moveTo(s.x + s.width * 0.47, s.y + s.height * 0.24);
    cx.lineTo(s.x + s.width * 0.51, s.y + s.height * 0.16);
    cx.lineTo(s.x + s.width * 0.54, s.y + s.height * 0.22);
    cx.lineTo(s.x + s.width * 0.57, s.y + s.height * 0.18);
    cx.lineTo(s.x + s.width * 0.58, s.y + s.height * 0.26);
    cx.closePath();
    cx.fillStyle = '#ff6a00';
    cx.fill();

    if (params.reflectiveShine) {
        cx.lineWidth = 2.5;
        cx.strokeStyle = `hsl(${baseH + 20}, 100%, 85%)`;
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

    const hasColor = (leds[index] && leds[index].color);
    const c = hasColor ? leds[index].color : null;

    // ------------------------------------------------------------------------
    // ANIMATION GROUP / ZONE OVERRIDE
    // If this LED belongs to a custom animation group (e.g. Coach Wheels, Lanterns):
    // ------------------------------------------------------------------------
    const grpEntry = ledGroupMap[index];
    if (grpEntry && grpEntry.group) {
        const grp = grpEntry.group;
        const grpIndex = grpEntry.indexInGroup;
        const grpSize = Math.max(1, grpEntry.groupSize);
        const grpBpm = grp.speedBpm || params.speedBpm || 120;
        const grpBeatMs = 60000 / grpBpm;
        const grpNormTime = timeMs / grpBeatMs;
        const grpDir = grp.direction || 1;

        let baseR = c ? c.r : 255;
        let baseG = c ? c.g : 200;
        let baseB = c ? c.b : 50;

        if (grp.colorMode === 'custom' && grp.customColor) {
            baseR = grp.customColor.r;
            baseG = grp.customColor.g;
            baseB = grp.customColor.b;
        }

        let grpIntensity = 1.0;

        switch (grp.effect) {
            case 'chase': {
                // Spinning wheel chase: traveling lit segment rotating along the group
                const head = ((grpNormTime * grpDir) % grpSize + grpSize) % grpSize;
                const directDist = Math.abs(grpIndex - head);
                const circDist = Math.min(directDist, grpSize - directDist);
                const fadeLen = Math.max(1.8, (grp.width || 2.5));
                if (circDist < fadeLen) {
                    const fade = Math.max(0, 1 - (circDist / fadeLen));
                    grpIntensity = 0.18 + 0.82 * Math.pow(fade, 1.2);
                    if (circDist < 0.85) {
                        baseR = Math.min(255, baseR + 45);
                        baseG = Math.min(255, baseG + 45);
                        baseB = Math.min(255, baseB + 45);
                    }
                } else {
                    grpIntensity = 0.14; // Dim unlit wheel track
                }
                break;
            }
            case 'flash_slow': {
                // Gentle slow blink
                const phase = (timeMs % (grpBeatMs * 2)) / (grpBeatMs * 2);
                grpIntensity = phase < 0.5 ? 1.0 : 0.08;
                break;
            }
            case 'pulse': {
                // Smooth sine-wave breathing glow
                const sine = Math.sin(grpNormTime * Math.PI * 2) * 0.5 + 0.5;
                grpIntensity = 0.18 + 0.82 * sine;
                break;
            }
            case 'write_on_off': {
                // Theatrical / Neon sign progressive write-on and write-off wipe
                const totalCycleMs = grpBeatMs * 4;
                const progress = (timeMs % totalCycleMs) / totalCycleMs;
                if (progress < 0.40) {
                    // Progressive turn-on
                    const litHead = (progress / 0.40) * grpSize;
                    if (grpDir >= 0) {
                        grpIntensity = grpIndex <= litHead ? 1.0 : 0.05;
                    } else {
                        grpIntensity = (grpSize - 1 - grpIndex) <= litHead ? 1.0 : 0.05;
                    }
                } else if (progress < 0.58) {
                    // Hold fully lit
                    grpIntensity = 1.0;
                } else if (progress < 0.88) {
                    // Progressive turn-off
                    const offHead = ((progress - 0.58) / 0.30) * grpSize;
                    if (grpDir >= 0) {
                        grpIntensity = grpIndex <= offHead ? 0.05 : 1.0;
                    } else {
                        grpIntensity = (grpSize - 1 - grpIndex) <= offHead ? 0.05 : 1.0;
                    }
                } else {
                    // Dark pause
                    grpIntensity = 0.05;
                }
                break;
            }
            case 'sparkle_storm': {
                // Rapid shimmering fairy dust / starlight on this group
                const rand = Math.sin(timeMs * 0.05 + grpIndex * 37.1) * 0.5 + 0.5;
                if (rand > 0.65) {
                    grpIntensity = 1.0;
                    baseR = Math.min(255, baseR + 80);
                    baseG = Math.min(255, baseG + 80);
                    baseB = Math.min(255, baseB + 80);
                } else {
                    grpIntensity = 0.25 + 0.35 * rand;
                }
                break;
            }
            case 'marquee': {
                // 3-step running marquee dot chase
                const step = Math.floor(grpNormTime * 2 * grpDir) % 3;
                const posInStep = ((grpIndex + step) % 3 + 3) % 3;
                grpIntensity = posInStep === 0 ? 1.0 : 0.12;
                break;
            }
            case 'rainbow_cycle': {
                // Flowing spectrum
                const hue = ((timeMs * 0.08 * grpDir + grpIndex * (360 / grpSize)) % 360 + 360) % 360;
                const rgb = hslToRgb(hue / 360, 0.95, 0.52);
                baseR = rgb.r;
                baseG = rgb.g;
                baseB = rgb.b;
                grpIntensity = 1.0;
                break;
            }
            default:
                grpIntensity = 1.0;
                break;
        }

        const effBrightness = (params.brightness / 100) * grpIntensity;
        return {
            r: Math.floor(baseR * effBrightness),
            g: Math.floor(baseG * effBrightness),
            b: Math.floor(baseB * effBrightness),
            alpha: effBrightness
        };
    }

    switch (activePattern) {
        case 'steady_sparkle': {
            // Constant steady colors without breathing pulse
            if (hasColor) {
                r = c.r;
                g = c.g;
                b = c.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
                r = rgb.r;
                g = rgb.g;
                b = rgb.b;
            }

            // Occasional bright starlight sparkle
            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                r = Math.round(r * (1 - sp) + 255 * sp);
                g = Math.round(g * (1 - sp) + 255 * sp);
                b = Math.round(b * (1 - sp) + 240 * sp);
                brightness = Math.min(1.0, brightness + sp * 0.4);
            }
            break;
        }
        case 'color_match': {
            if (hasColor) {
                const breath = 0.72 + 0.28 * Math.sin(normTime * 2 + index * 0.18);
                r = Math.floor(c.r * breath);
                g = Math.floor(c.g * breath);
                b = Math.floor(c.b * breath);
            } else {
                const breath = 0.75 + 0.25 * Math.sin(normTime * 2 + index * 0.15);
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * breath);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }

            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                r = Math.round(r * (1 - sp) + 255 * sp);
                g = Math.round(g * (1 - sp) + 255 * sp);
                b = Math.round(b * (1 - sp) + 240 * sp);
                brightness = Math.min(1.0, brightness + sp * 0.4);
            }
            break;
        }
        case 'dragon_sparkle': {
            if (hasColor) {
                const breath = 0.75 + 0.25 * Math.sin(normTime * 2 + index * 0.15);
                r = Math.floor(c.r * breath);
                g = Math.floor(c.g * breath);
                b = Math.floor(c.b * breath);
            } else {
                const breath = 0.75 + 0.25 * Math.sin(normTime * 2 + index * 0.15);
                const h = baseH + Math.sin(index * 0.4) * 8;
                const rgb = hslToRgb(h / 360, 0.95, 0.50 * breath);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }

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
            if (index <= 8) {
                const fire = Math.sin(normTime * 6 + index) * 0.5 + 0.5;
                r = 255;
                g = Math.floor(60 + fire * 100);
                b = 10;
            } else if (hasColor) {
                r = c.r; g = c.g; b = c.b;
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

            if (dist < 4.0) {
                const intensity = Math.max(0, 1 - (dist / 4.0));
                r = 255 * intensity;
                g = 255 * intensity;
                b = Math.floor(220 * intensity);
                brightness = 1.0;
            } else if (hasColor) {
                r = Math.floor(c.r * 0.5);
                g = Math.floor(c.g * 0.5);
                b = Math.floor(c.b * 0.5);
                brightness = 0.4;
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
                if (hasColor) {
                    r = Math.min(255, c.r + 50);
                    g = Math.min(255, c.g + 50);
                    b = Math.min(255, c.b + 50);
                } else {
                    r = 255; g = 150; b = 30;
                }
                brightness = 0.9;
            } else {
                r = 10; g = 10; b = 10;
                brightness = 0.1;
            }
            break;
        }
        case 'photo_mode': {
            if (hasColor) {
                r = c.r; g = c.g; b = c.b;
            } else if (index % 2 === 0) {
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
    if ((activePattern === 'steady_sparkle' || activePattern === 'dragon_sparkle' || activePattern === 'color_match') && Math.random() * 1000 < params.sparkleRate) {
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

    if (isSelected) {
        cx.save();
        // High-visibility cyan outer dashed ring
        cx.beginPath();
        cx.arc(x, y, 11, 0, Math.PI * 2);
        cx.strokeStyle = '#00ffff';
        cx.lineWidth = 2.5;
        cx.setLineDash([4, 3]);
        cx.stroke();

        // Inner solid gold ring
        cx.beginPath();
        cx.arc(x, y, 7.5, 0, Math.PI * 2);
        cx.strokeStyle = '#ffc107';
        cx.lineWidth = 2;
        cx.setLineDash([]);
        cx.stroke();

        // 4 Focus Crosshairs
        const crossLen = 4;
        cx.beginPath();
        cx.moveTo(x - 15, y); cx.lineTo(x - 15 + crossLen, y);
        cx.moveTo(x + 15 - crossLen, y); cx.lineTo(x + 15, y);
        cx.moveTo(x, y - 15); cx.lineTo(x, y - 15 + crossLen);
        cx.moveTo(x, y + 15 - crossLen); cx.lineTo(x, y + 15);
        cx.strokeStyle = '#00ffff';
        cx.lineWidth = 2;
        cx.stroke();
        cx.restore();
    } else if (isHovered) {
        cx.beginPath();
        cx.arc(x, y, 8.5, 0, Math.PI * 2);
        cx.strokeStyle = '#00e5ff';
        cx.lineWidth = 2;
        cx.stroke();
    }

    if (params.showNumbers || isSelected) {
        if (index === 0) {
            cx.fillStyle = '#00ff88';
            cx.font = 'bold 10px monospace';
            cx.fillText('0 (START)', x + 6, y - 6);
        } else if (index === leds.length - 1) {
            cx.fillStyle = '#ff4d6d';
            cx.font = 'bold 10px monospace';
            cx.fillText(`${index} (END)`, x + 6, y - 6);
        } else {
            cx.fillStyle = isSelected ? '#00ffff' : '#ffffff';
            cx.font = isSelected ? 'bold 11px monospace' : '9px monospace';
            cx.fillText(isSelected ? `#${index}` : index, x + 6, y - 6);
        }
    }
}

// ============================================================================
// SINGLE SHIRT VIEW (With Smooth Zoom & Pan Support)
// ============================================================================
function renderSingleShirtView(timeMs) {
    const w = canvas.width;
    const h = canvas.height;
    const s = getShirtBounds();

    ctx.clearRect(0, 0, w, h);

    // Apply interactive Zoom & Pan transform
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoomScale, zoomScale);

    let shirtTitle = "FLOAT #3: PETE'S DRAGON";
    if (currentGraphicType === 'cinderellas_coach') {
        shirtTitle = "FLOAT #5: CINDERELLA'S COACH";
    } else if (currentGraphicType === 'custom_image') {
        shirtTitle = "CUSTOM RUNNER DESIGN";
    }
    drawRunningShirt(ctx, s.x, s.y, s.width, s.height, shirtTitle);
    drawPetesDragon(ctx, s);

    if (params.showWiring && leds.length > 1) {
        ctx.save();
        ctx.beginPath();
        const p0 = normToCanvas(leds[0]);
        ctx.moveTo(p0.x, p0.y);
        for (let i = 1; i < leds.length; i++) {
            const pt = normToCanvas(leds[i]);
            ctx.lineTo(pt.x, pt.y);
        }
        ctx.strokeStyle = 'rgba(255, 193, 7, 0.55)';
        ctx.lineWidth = 1.8;
        ctx.setLineDash([5, 4]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Highlight Start LED 0 (Green indicator ring)
        ctx.beginPath();
        ctx.arc(p0.x, p0.y, 9.5, 0, Math.PI * 2);
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Highlight End LED (Red indicator ring)
        const pEnd = normToCanvas(leds[leds.length - 1]);
        ctx.beginPath();
        ctx.arc(pEnd.x, pEnd.y, 9.5, 0, Math.PI * 2);
        ctx.strokeStyle = '#ff4d6d';
        ctx.lineWidth = 2.5;
        ctx.stroke();
        ctx.restore();
    }

    for (let i = 0; i < leds.length; i++) {
        const pt = normToCanvas(leds[i]);
        const col = computeLedColor(i, leds.length, timeMs);
        const isHover = (hoveredLed === i);
        const isSel = (selectedLed === i || draggedLed === i || selectedLeds.has(i));
        renderBulb(ctx, pt.x, pt.y, col, isHover, isSel, i);
    }

    ctx.restore();

    // Render Marquee Selection Box in Screen Space
    if (isBoxSelecting) {
        const bx = Math.min(boxStartX, boxCurrentX);
        const by = Math.min(boxStartY, boxCurrentY);
        const bw = Math.abs(boxCurrentX - boxStartX);
        const bh = Math.abs(boxCurrentY - boxStartY);

        ctx.save();
        ctx.fillStyle = 'rgba(56, 139, 253, 0.18)';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = '#58a6ff';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 3]);
        ctx.strokeRect(bx, by, bw, bh);
        ctx.restore();
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
// ZOOM & PAN ENGINE
// ============================================================================
function setZoom(newZoom, pivotX = canvas.width / 2, pivotY = canvas.height / 2) {
    const clampedZoom = Math.min(maxZoom, Math.max(minZoom, newZoom));
    if (Math.abs(clampedZoom - zoomScale) < 0.001) return;

    // Keep world coordinate under pivot point invariant
    const worldPivotX = (pivotX - panX) / zoomScale;
    const worldPivotY = (pivotY - panY) / zoomScale;

    zoomScale = clampedZoom;
    panX = pivotX - worldPivotX * zoomScale;
    panY = pivotY - worldPivotY * zoomScale;

    updateZoomUI();
}

function resetZoom() {
    zoomScale = 1.0;
    panX = 0;
    panY = 0;
    updateZoomUI();
}

function updateZoomUI() {
    const badge = document.getElementById('zoomLevelText');
    if (badge) {
        badge.textContent = `${Math.round(zoomScale * 100)}%`;
    }
}

function focusOnLed(index) {
    if (index === null || index < 0 || index >= leds.length) return;
    const pt = normToCanvas(leds[index]);
    zoomScale = Math.max(zoomScale, 2.2);
    panX = (canvas.width / 2) - pt.x * zoomScale;
    panY = (canvas.height / 2) - pt.y * zoomScale;
    updateZoomUI();
}

// ============================================================================
// LED SELECTION & RGB COLOR INSPECTOR
// ============================================================================
function selectLed(index, isMulti = false) {
    if (index === null || index < 0 || index >= leds.length) {
        deselectLed();
        return;
    }

    if (isMulti) {
        if (selectedLeds.has(index)) {
            selectedLeds.delete(index);
            if (selectedLed === index) {
                const arr = Array.from(selectedLeds);
                selectedLed = arr.length > 0 ? arr[arr.length - 1] : null;
            }
        } else {
            selectedLeds.add(index);
            selectedLed = index;
        }
    } else {
        selectedLeds.clear();
        selectedLeds.add(index);
        selectedLed = index;
    }

    updateLedInspectorUI();
}

function deselectLed() {
    selectedLed = null;
    selectedLeds.clear();
    updateLedInspectorUI();
}

function selectNextLed() {
    if (!leds || leds.length === 0) return;
    if (selectedLed === null) {
        selectLed(0);
    } else {
        selectLed((selectedLed + 1) % leds.length);
    }
}

function selectPrevLed() {
    if (!leds || leds.length === 0) return;
    if (selectedLed === null) {
        selectLed(leds.length - 1);
    } else {
        selectLed((selectedLed - 1 + leds.length) % leds.length);
    }
}

function selectAllLeds() {
    if (!leds || leds.length === 0) return;
    selectedLeds.clear();
    for (let i = 0; i < leds.length; i++) {
        selectedLeds.add(i);
    }
    selectedLed = 0;
    updateLedInspectorUI();
    showToast(`✨ Selected all ${leds.length} LEDs!`);
}

function invertLedSelection() {
    if (!leds || leds.length === 0) return;
    const newSel = new Set();
    for (let i = 0; i < leds.length; i++) {
        if (!selectedLeds.has(i)) newSel.add(i);
    }
    selectedLeds = newSel;
    const arr = Array.from(selectedLeds);
    selectedLed = arr.length > 0 ? arr[0] : null;
    updateLedInspectorUI();
    showToast(`🔄 Inverted selection: ${selectedLeds.size} LEDs selected`);
}

function updateLedInspectorCoords() {
    if (selectedLed === null || !leds[selectedLed]) return;
    const coordsEl = document.getElementById('inspectorCoordsText');
    if (coordsEl) {
        if (selectedLeds.size > 1) {
            coordsEl.textContent = `${selectedLeds.size} LEDs in selection`;
        } else {
            coordsEl.textContent = `X: ${(leds[selectedLed].x * 100).toFixed(1)}% | Y: ${(leds[selectedLed].y * 100).toFixed(1)}%`;
        }
    }
}

function setSelectedLedColor(r, g, b) {
    if (selectedLeds.size === 0 && (selectedLed === null || !leds[selectedLed])) return;
    const clampedR = Math.max(0, Math.min(255, Math.round(r)));
    const clampedG = Math.max(0, Math.min(255, Math.round(g)));
    const clampedB = Math.max(0, Math.min(255, Math.round(b)));

    if (selectedLeds.size > 0) {
        for (const idx of selectedLeds) {
            if (leds[idx]) {
                leds[idx].color = { r: clampedR, g: clampedG, b: clampedB };
            }
        }
    } else if (selectedLed !== null && leds[selectedLed]) {
        leds[selectedLed].color = { r: clampedR, g: clampedG, b: clampedB };
    }

    updateLedInspectorColorInputs(clampedR, clampedG, clampedB);

    if (isWifiStreaming) {
        sendLivePixelFrame(performance.now());
    }
}

function updateLedInspectorColorInputs(r, g, b) {
    const toHex = (n) => n.toString(16).padStart(2, '0').toUpperCase();
    const hex = `#${toHex(r)}${toHex(g)}${toHex(b)}`;

    const swatch = document.getElementById('inspectorColorSwatch');
    if (swatch) swatch.style.background = hex;

    const nativePicker = document.getElementById('inspectorNativePicker');
    if (nativePicker) nativePicker.value = hex.toLowerCase();

    const hexText = document.getElementById('inspectorHexText');
    if (hexText) {
        if (selectedLeds.size > 1) {
            hexText.textContent = `${hex} (${selectedLeds.size} LEDs)`;
        } else {
            hexText.textContent = hex;
        }
    }

    const rgbText = document.getElementById('inspectorRgbText');
    if (rgbText) rgbText.textContent = `rgb(${r}, ${g}, ${b})`;

    // Sliders
    const rSlider = document.getElementById('ledRSlider');
    const gSlider = document.getElementById('ledGSlider');
    const bSlider = document.getElementById('ledBSlider');
    if (rSlider) rSlider.value = r;
    if (gSlider) gSlider.value = g;
    if (bSlider) bSlider.value = b;

    // Numbers
    const rNum = document.getElementById('ledRNum');
    const gNum = document.getElementById('ledGNum');
    const bNum = document.getElementById('ledBNum');
    if (rNum) rNum.value = r;
    if (gNum) gNum.value = g;
    if (bNum) bNum.value = b;
}

function updateLedInspectorUI() {
    const emptyPrompt = document.getElementById('inspectorEmptyPrompt');
    const colorControls = document.getElementById('inspectorColorControls');
    const badge = document.getElementById('inspectorLedBadge');
    const numInput = document.getElementById('inspectorLedNumInput');
    const stepperRow = document.getElementById('inspectorStepperRow');
    const multiRow = document.getElementById('inspectorMultiSelectRow');
    const groupBadge = document.getElementById('groupEffectLedCountBadge');

    const totalSelected = selectedLeds.size;

    if (totalSelected === 0) {
        if (emptyPrompt) emptyPrompt.style.display = 'block';
        if (colorControls) colorControls.style.display = 'none';
        if (stepperRow) stepperRow.style.display = 'flex';
        if (multiRow) multiRow.style.display = 'none';
        if (badge) {
            badge.textContent = 'None Selected';
            badge.style.background = '#30363d';
            badge.style.color = '#8b949e';
        }
        if (groupBadge) groupBadge.textContent = '0 LEDs Selected';
        return;
    }

    if (emptyPrompt) emptyPrompt.style.display = 'none';
    if (colorControls) colorControls.style.display = 'flex';

    if (totalSelected === 1) {
        if (stepperRow) stepperRow.style.display = 'flex';
        if (multiRow) multiRow.style.display = 'none';
        if (badge) {
            badge.textContent = `LED #${selectedLed}`;
            badge.style.background = '#ffc107';
            badge.style.color = '#000';
        }
        if (groupBadge) groupBadge.textContent = '1 LED Selected';
        if (numInput) {
            numInput.value = selectedLed;
            numInput.max = Math.max(0, leds.length - 1);
        }

        // If this LED belongs to a group, populate group inputs
        const grpEntry = ledGroupMap[selectedLed];
        if (grpEntry && grpEntry.group) {
            const grp = grpEntry.group;
            const nameInput = document.getElementById('groupNameInput');
            const effectSelect = document.getElementById('groupEffectSelect');
            const speedSlider = document.getElementById('groupSpeedSlider');
            const speedVal = document.getElementById('groupSpeedVal');
            const dirSelect = document.getElementById('groupDirectionSelect');
            if (nameInput) nameInput.value = grp.name;
            if (effectSelect) effectSelect.value = grp.effect;
            if (speedSlider) {
                speedSlider.value = grp.speedBpm;
                if (speedVal) speedVal.textContent = `${grp.speedBpm} BPM`;
            }
            if (dirSelect) dirSelect.value = String(grp.direction || 1);
        }
    } else {
        // Multi-selection (> 1)
        if (stepperRow) stepperRow.style.display = 'none';
        if (multiRow) multiRow.style.display = 'flex';
        if (badge) {
            badge.textContent = `✨ ${totalSelected} LEDs Selected`;
            badge.style.background = '#388bfd';
            badge.style.color = '#ffffff';
        }
        if (groupBadge) groupBadge.textContent = `${totalSelected} LEDs Selected`;
    }

    updateLedInspectorCoords();

    const activeRef = (selectedLed !== null && leds[selectedLed]) ? selectedLed : Array.from(selectedLeds)[0];
    if (activeRef !== undefined && leds[activeRef]) {
        let col = leds[activeRef].color;
        if (!col) {
            col = computeLedColor(activeRef, leds.length, performance.now());
            leds[activeRef].color = { r: col.r, g: col.g, b: col.b };
        }
        updateLedInspectorColorInputs(col.r, col.g, col.b);
    }
}

// ----------------------------------------------------------------------------
// ANIMATION GROUP MANAGEMENT ROUTINES
// ----------------------------------------------------------------------------
function applyGroupEffectToSelection() {
    if (selectedLeds.size === 0) {
        alert("Please select at least 2 LEDs to create or apply an animation group effect!");
        return;
    }

    const nameInput = document.getElementById('groupNameInput');
    const effectSelect = document.getElementById('groupEffectSelect');
    const speedSlider = document.getElementById('groupSpeedSlider');
    const dirSelect = document.getElementById('groupDirectionSelect');

    const rawName = (nameInput?.value || '').trim() || `Zone (${selectedLeds.size} LEDs)`;
    const effect = effectSelect?.value || 'chase';
    const speedBpm = parseInt(speedSlider?.value || '140', 10);
    const direction = parseInt(dirSelect?.value || '1', 10);

    const sortedIndices = Array.from(selectedLeds).sort((a, b) => a - b);

    // If an existing group with this exact name exists, update it; otherwise create new
    let targetGroup = animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase());

    if (targetGroup) {
        targetGroup.ledIndices = sortedIndices;
        targetGroup.effect = effect;
        targetGroup.speedBpm = speedBpm;
        targetGroup.direction = direction;
    } else {
        targetGroup = {
            id: 'grp_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
            name: rawName,
            ledIndices: sortedIndices,
            effect: effect,
            speedBpm: speedBpm,
            direction: direction,
            width: 3,
            colorMode: 'original'
        };
        animationGroups.push(targetGroup);
    }

    rebuildLedGroupMap();
    renderActiveGroupsList();
    showToast(`✨ Applied "${effect.replace('_', ' ')}" to ${sortedIndices.length} LEDs in "${targetGroup.name}"!`);
}

function removeGroupEffectFromSelection() {
    if (selectedLeds.size === 0) return;

    let removedCount = 0;
    for (const idx of selectedLeds) {
        for (let g = animationGroups.length - 1; g >= 0; g--) {
            const grp = animationGroups[g];
            const p = grp.ledIndices.indexOf(idx);
            if (p !== -1) {
                grp.ledIndices.splice(p, 1);
                removedCount++;
                if (grp.ledIndices.length === 0) {
                    animationGroups.splice(g, 1);
                }
            }
        }
    }

    rebuildLedGroupMap();
    renderActiveGroupsList();
    showToast(`🗑️ Removed group effects from ${removedCount} LEDs.`);
}

function deleteGroup(groupId) {
    const idx = animationGroups.findIndex(g => g.id === groupId);
    if (idx !== -1) {
        const name = animationGroups[idx].name;
        animationGroups.splice(idx, 1);
        rebuildLedGroupMap();
        renderActiveGroupsList();
        showToast(`🗑️ Deleted animation group "${name}"`);
    }
}

function selectGroupLeds(groupId) {
    const grp = animationGroups.find(g => g.id === groupId);
    if (!grp) return;

    selectedLeds.clear();
    for (const idx of grp.ledIndices) {
        if (idx < leds.length) selectedLeds.add(idx);
    }
    selectedLed = grp.ledIndices[0] || null;

    const nameInput = document.getElementById('groupNameInput');
    const effectSelect = document.getElementById('groupEffectSelect');
    const speedSlider = document.getElementById('groupSpeedSlider');
    const speedVal = document.getElementById('groupSpeedVal');
    const dirSelect = document.getElementById('groupDirectionSelect');

    if (nameInput) nameInput.value = grp.name;
    if (effectSelect) effectSelect.value = grp.effect;
    if (speedSlider) {
        speedSlider.value = grp.speedBpm;
        if (speedVal) speedVal.textContent = `${grp.speedBpm} BPM`;
    }
    if (dirSelect) dirSelect.value = String(grp.direction || 1);

    updateLedInspectorUI();
    showToast(`🎯 Selected ${selectedLeds.size} LEDs for group "${grp.name}"!`);
}

function renderActiveGroupsList() {
    const container = document.getElementById('activeGroupsList');
    const badge = document.getElementById('activeGroupsCountBadge');
    if (!container) return;

    if (badge) badge.textContent = `${animationGroups.length} Groups`;
    container.innerHTML = '';

    if (animationGroups.length === 0) {
        container.innerHTML = `
            <div style="font-size: 11px; color: var(--text-muted); font-style: italic; padding: 6px; text-align: center;">
                No custom groups created yet. Select LEDs to add an effect!
            </div>
        `;
        return;
    }

    const effectIcons = {
        chase: '🎡 Chase',
        flash_slow: '💡 Blink',
        pulse: '💓 Pulse',
        write_on_off: '✍️ Wipe',
        sparkle_storm: '✨ Sparkle',
        marquee: '🎪 Marquee',
        rainbow_cycle: '🌈 Rainbow'
    };

    for (const grp of animationGroups) {
        const item = document.createElement('div');
        item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 6px 8px; background: #0d1117; border-radius: 6px; border: 1px solid #30363d; font-size: 11px;';

        const label = effectIcons[grp.effect] || grp.effect;

        item.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 2px; overflow: hidden; max-width: 170px;">
                <span style="font-weight: 600; color: #fff; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${grp.name}</span>
                <span style="font-size: 10px; color: var(--accent-cyan);">${label} (${grp.ledIndices.length} LEDs @ ${grp.speedBpm} BPM)</span>
            </div>
            <div style="display: flex; gap: 4px; align-items: center;">
                <button type="button" class="action-btn select-grp-btn" style="padding: 3px 6px; font-size: 10px;" title="Select all LEDs in this group">⌖ Select</button>
                <button type="button" class="action-btn del-grp-btn" style="padding: 3px 6px; font-size: 10px; color: #f85149;" title="Delete group">🗑️</button>
            </div>
        `;

        item.querySelector('.select-grp-btn').addEventListener('click', () => selectGroupLeds(grp.id));
        item.querySelector('.del-grp-btn').addEventListener('click', () => deleteGroup(grp.id));

        container.appendChild(item);
    }
}

// ============================================================================
// INTERACTION & HIT DETECTION (Zoom, Pan, Drag, and Selection)
// ============================================================================

canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault(); // Prevent context menu so right-drag pans seamlessly
});

canvas.addEventListener('wheel', (e) => {
    if (currentView !== 'single') return;
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;

    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    setZoom(zoomScale * zoomFactor, mx, my);
}, { passive: false });

window.addEventListener('keydown', (e) => {
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;

    if (e.code === 'Space') {
        if (!isSpacePressed) {
            isSpacePressed = true;
            canvas.style.cursor = 'grab';
        }
        e.preventDefault();
    } else if ((e.key === 'a' || e.key === 'A') && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        selectAllLeds();
    } else if (e.key === 'ArrowRight' || e.key === ']' || e.key === 'n') {
        selectNextLed();
    } else if (e.key === 'ArrowLeft' || e.key === '[' || e.key === 'p') {
        selectPrevLed();
    } else if (e.key === 'Escape') {
        deselectLed();
    } else if (e.key === '+' || e.key === '=') {
        setZoom(zoomScale * 1.2);
    } else if (e.key === '-' || e.key === '_') {
        setZoom(zoomScale / 1.2);
    } else if (e.key === '0') {
        resetZoom();
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'Space') {
        isSpacePressed = false;
        canvas.style.cursor = hoveredLed !== null ? 'pointer' : 'default';
    }
});

canvas.addEventListener('mousedown', (e) => {
    if (currentView !== 'single') return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;

    mouseStartX = mx;
    mouseStartY = my;
    hasMovedSignificantly = false;

    const isMultiKey = e.shiftKey || e.ctrlKey || e.metaKey;

    // Right-click (2), Middle-click (1), or Space+click -> Pan Canvas
    if (e.button === 2 || e.button === 1 || (e.button === 0 && isSpacePressed)) {
        isPanning = true;
        panStartX = mx - panX;
        panStartY = my - panY;
        canvas.style.cursor = 'grabbing';
        return;
    }

    if (e.button !== 0) return;

    // Left-click: Screen space hit test
    let clickedIdx = -1;
    for (let i = 0; i < leds.length; i++) {
        const pt = normToCanvas(leds[i]);
        const screenX = pt.x * zoomScale + panX;
        const screenY = pt.y * zoomScale + panY;
        const dist = Math.hypot(mx - screenX, my - screenY);
        const hitRadius = Math.max(14, Math.min(28, 14 * zoomScale));
        if (dist <= hitRadius) {
            clickedIdx = i;
            break;
        }
    }

    if (clickedIdx !== -1) {
        if (isMultiKey) {
            // Shift / Ctrl click: toggle LED in multi-selection
            selectLed(clickedIdx, true);
        } else {
            // Normal click: select single LED and allow drag
            draggedLed = clickedIdx;
            isDraggingLed = true;
            selectLed(clickedIdx, false);
            canvas.classList.add('dragging');
        }
    } else {
        // Clicked background
        if (isBoxSelectMode || isMultiKey) {
            isBoxSelecting = true;
            boxStartX = mx;
            boxStartY = my;
            boxCurrentX = mx;
            boxCurrentY = my;
        } else {
            // Prepare to pan if user drags
            isPanning = true;
            panStartX = mx - panX;
            panStartY = my - panY;
        }
    }
});

canvas.addEventListener('mousemove', (e) => {
    if (currentView !== 'single') return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;

    if (Math.hypot(mx - mouseStartX, my - mouseStartY) > 5) {
        hasMovedSignificantly = true;
    }

    if (isBoxSelecting) {
        boxCurrentX = mx;
        boxCurrentY = my;
        return;
    }

    if (isPanning) {
        panX = mx - panStartX;
        panY = my - panStartY;
        canvas.style.cursor = 'grabbing';
        return;
    }

    if (isDraggingLed && draggedLed !== null) {
        const worldX = (mx - panX) / zoomScale;
        const worldY = (my - panY) / zoomScale;
        const norm = canvasToNorm(worldX, worldY);
        leds[draggedLed].x = norm.x;
        leds[draggedLed].y = norm.y;
        updateLedInspectorCoords();
        return;
    }

    // Hover detection
    let found = null;
    for (let i = 0; i < leds.length; i++) {
        const pt = normToCanvas(leds[i]);
        const screenX = pt.x * zoomScale + panX;
        const screenY = pt.y * zoomScale + panY;
        const dist = Math.hypot(mx - screenX, my - screenY);
        const hitRadius = Math.max(14, Math.min(28, 14 * zoomScale));
        if (dist <= hitRadius) {
            found = i;
            break;
        }
    }
    hoveredLed = found;

    if (isSpacePressed) {
        canvas.style.cursor = 'grab';
    } else if (isBoxSelectMode) {
        canvas.style.cursor = 'crosshair';
    } else if (found !== null) {
        canvas.style.cursor = 'pointer';
    } else {
        canvas.style.cursor = 'default';
    }
});

window.addEventListener('mouseup', (e) => {
    if (isBoxSelecting) {
        isBoxSelecting = false;
        const minX = Math.min(boxStartX, boxCurrentX);
        const maxX = Math.max(boxStartX, boxCurrentX);
        const minY = Math.min(boxStartY, boxCurrentY);
        const maxY = Math.max(boxStartY, boxCurrentY);

        if (Math.abs(maxX - minX) > 6 && Math.abs(maxY - minY) > 6) {
            if (!e.shiftKey && !e.ctrlKey && !e.metaKey) {
                selectedLeds.clear();
            }
            let newlyFound = 0;
            for (let i = 0; i < leds.length; i++) {
                const pt = normToCanvas(leds[i]);
                const sx = pt.x * zoomScale + panX;
                const sy = pt.y * zoomScale + panY;
                if (sx >= minX && sx <= maxX && sy >= minY && sy <= maxY) {
                    selectedLeds.add(i);
                    newlyFound++;
                }
            }
            if (selectedLeds.size > 0) {
                const arr = Array.from(selectedLeds);
                selectedLed = arr[arr.length - 1];
                showToast(`✨ Selected ${selectedLeds.size} LEDs in box!`);
            }
            updateLedInspectorUI();
        }
        return;
    }

    if (isPanning) {
        isPanning = false;
        canvas.style.cursor = isSpacePressed ? 'grab' : (hoveredLed !== null ? 'pointer' : 'default');
        // Click on empty canvas without dragging clears selection
        if (!hasMovedSignificantly && draggedLed === null && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
            deselectLed();
        }
    }

    if (isDraggingLed && draggedLed !== null) {
        if (hasMovedSignificantly) {
            if (activePattern === 'color_match' || (leds[draggedLed] && leds[draggedLed].color)) {
                const newCol = sampleColorAtNorm(leds[draggedLed].x, leds[draggedLed].y);
                if (newCol) {
                    leds[draggedLed].color = newCol;
                    updateLedInspectorUI();
                }
            }
        }
        isDraggingLed = false;
        draggedLed = null;
        canvas.classList.remove('dragging');
    }
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
    if (isWifiStreaming) {
        sendLivePixelFrame(time);
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

// Save Current Profile (LEDs + Graphic + Settings + Animation Groups)
async function saveCurrentProfile(name) {
    if (!name || name.trim() === '') {
        showToast("⚠️ Please enter a name for this costume profile!");
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
        animationGroups: animationGroups,
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
            showToast(`💾 Profile "${cleanName}" saved successfully!`);
        }
    } catch (e) {
        showToast(`💾 Profile "${cleanName}" saved to browser cache.`);
    }

    await refreshPresetDropdown();
    const select = document.getElementById('presetSelect');
    if (select) {
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].text.includes(cleanName)) {
                select.selectedIndex = i;
                break;
            }
        }
    }
}

// Apply Profile Data object to simulator
function applyProfileData(profileData) {
    if (!profileData) return;

    // 1. Restore LEDs
    if (Array.isArray(profileData.leds) && profileData.leds.length > 0) {
        leds = profileData.leds;
        while (sparkles.length < leds.length) sparkles.push(0);
        updateLedCountUI();
    }

    // 2. Restore Graphic
    currentGraphicType = profileData.graphicType || 'builtin_dragon';
    const resetBtn = document.getElementById('resetArtworkBtn');
    const graphicSelect = document.getElementById('graphicPresetSelect');
    const uploadContainer = document.getElementById('customUploadContainer');

    if (currentGraphicType === 'cinderellas_coach') {
        customArtworkImg = null;
        customArtworkDataUrl = null;
        if (graphicSelect) graphicSelect.value = 'cinderellas_coach';
        if (uploadContainer) uploadContainer.style.display = 'none';
        if (resetBtn) resetBtn.style.display = 'block';
    } else if (profileData.customArtworkDataUrl) {
        customArtworkDataUrl = profileData.customArtworkDataUrl;
        const img = new Image();
        img.onload = () => {
            customArtworkImg = img;
        };
        img.src = customArtworkDataUrl;
        if (graphicSelect) graphicSelect.value = 'custom_upload';
        if (uploadContainer) uploadContainer.style.display = 'block';
        if (resetBtn) resetBtn.style.display = 'block';
    } else {
        customArtworkImg = null;
        if (graphicSelect) graphicSelect.value = 'builtin_dragon';
        if (uploadContainer) uploadContainer.style.display = 'none';
        if (resetBtn) resetBtn.style.display = 'none';
    }

    // 3. Restore Settings
    if (profileData.settings) {
        const s = profileData.settings;
        if (s.pattern) {
            activePattern = s.pattern;
            const pSel = document.getElementById('patternSelect');
            if (pSel) pSel.value = s.pattern;
        }
        if (s.speedBpm) {
            params.speedBpm = s.speedBpm;
            const spd = document.getElementById('speedSlider');
            if (spd) spd.value = s.speedBpm;
            const spdVal = document.getElementById('speedVal');
            if (spdVal) spdVal.textContent = `${s.speedBpm} BPM`;
        }
        if (s.sparkleRate !== undefined) {
            params.sparkleRate = s.sparkleRate;
            const spk = document.getElementById('sparkleSlider');
            if (spk) spk.value = s.sparkleRate;
            const spkVal = document.getElementById('sparkleVal');
            if (spkVal) spkVal.textContent = `${s.sparkleRate}%`;
        }
        if (s.greenHue !== undefined) {
            params.greenHue = s.greenHue;
            const hue = document.getElementById('hueSlider');
            if (hue) hue.value = s.greenHue;
            const hueVal = document.getElementById('hueVal');
            if (hueVal) hueVal.textContent = `${s.greenHue}°`;
        }
        if (s.brightness !== undefined) {
            params.brightness = s.brightness;
            const brt = document.getElementById('brightnessSlider');
            if (brt) brt.value = s.brightness;
            const brtVal = document.getElementById('brightVal');
            if (brtVal) brtVal.textContent = `${s.brightness}%`;
        }
        if (s.glowSize !== undefined) {
            params.glowSize = s.glowSize;
            const glow = document.getElementById('glowSlider');
            if (glow) glow.value = s.glowSize;
            const glowVal = document.getElementById('glowVal');
            if (glowVal) glowVal.textContent = `${s.glowSize}px`;
        }
    }

    // 4. Restore Animation Groups
    if (Array.isArray(profileData.animationGroups)) {
        animationGroups = profileData.animationGroups;
    } else {
        animationGroups = [];
    }
    rebuildLedGroupMap();
    renderActiveGroupsList();

    // 5. Populate profile name input
    const nameInput = document.getElementById('profileNameInput');
    if (nameInput && profileData.name) {
        nameInput.value = profileData.name;
    }
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
            showToast("⚠️ Failed to load preset from server.");
            return;
        }
    } else if (sourceValue.startsWith('local:')) {
        const name = sourceValue.replace('local:', '');
        const localProfiles = JSON.parse(localStorage.getItem('msep_custom_presets') || '{}');
        profileData = localProfiles[name];
    }

    if (!profileData) return;
    applyProfileData(profileData);
    showToast(`📂 Loaded "${profileData.name || 'Profile'}"`);
}

// Initial Preset Load
refreshPresetDropdown();
rebuildLedGroupMap();
renderActiveGroupsList();

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
    const zt = document.querySelector('.zoom-toolbar');
    if (zt) zt.style.display = 'flex';
});

document.getElementById('fleetViewBtn').addEventListener('click', () => {
    currentView = 'fleet';
    document.getElementById('fleetViewBtn').classList.add('active');
    document.getElementById('singleViewBtn').classList.remove('active');
    const zt = document.querySelector('.zoom-toolbar');
    if (zt) zt.style.display = 'none';
});

// ============================================================================
// COMPUTER VISION & COLOR-MATCHED SAMPLING
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

function updateLedCountUI() {
    const title = document.getElementById('ledCountTitle');
    if (title) {
        title.textContent = `LED Layout (${leds.length} Pixels)`;
    }
    const wiringLabel = document.getElementById('wiringLabel');
    if (wiringLabel) {
        wiringLabel.textContent = `Show Wiring Trace (0 → ${Math.max(0, leds.length - 1)})`;
    }
    const inspectorNumInput = document.getElementById('inspectorLedNumInput');
    if (inspectorNumInput) {
        inspectorNumInput.max = Math.max(0, leds.length - 1);
    }
    if (selectedLed !== null && selectedLed >= leds.length) {
        selectedLed = leds.length > 0 ? leds.length - 1 : null;
        updateLedInspectorUI();
    }
}

// ============================================================================
// BINDINGS FOR ZOOM TOOLBAR & LED INSPECTOR / COLOR TUNER
// ============================================================================
document.getElementById('zoomInBtn')?.addEventListener('click', () => setZoom(zoomScale * 1.3));
document.getElementById('zoomOutBtn')?.addEventListener('click', () => setZoom(zoomScale / 1.3));
document.getElementById('zoomResetBtn')?.addEventListener('click', () => resetZoom());

document.getElementById('prevLedBtn')?.addEventListener('click', () => selectPrevLed());
document.getElementById('nextLedBtn')?.addEventListener('click', () => selectNextLed());
document.getElementById('focusLedBtn')?.addEventListener('click', () => {
    if (selectedLed !== null) focusOnLed(selectedLed);
    else if (leds.length > 0) { selectLed(0); focusOnLed(0); }
});

const inspectorLedNumInput = document.getElementById('inspectorLedNumInput');
if (inspectorLedNumInput) {
    inspectorLedNumInput.addEventListener('change', (e) => {
        const val = parseInt(e.target.value, 10);
        if (!isNaN(val) && val >= 0 && val < leds.length) {
            selectLed(val);
        }
    });
}

document.getElementById('inspectorNativePicker')?.addEventListener('input', (e) => {
    const hex = e.target.value;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    setSelectedLedColor(r, g, b);
});

const bindRgbControl = (sliderId, numId, channel) => {
    const slider = document.getElementById(sliderId);
    const num = document.getElementById(numId);
    if (!slider || !num) return;

    slider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        num.value = val;
        if (selectedLed !== null && leds[selectedLed]) {
            const cur = leds[selectedLed].color || { r: 0, g: 255, b: 100 };
            cur[channel] = val;
            setSelectedLedColor(cur.r, cur.g, cur.b);
        }
    });

    num.addEventListener('input', (e) => {
        let val = parseInt(e.target.value, 10);
        if (isNaN(val)) val = 0;
        val = Math.max(0, Math.min(255, val));
        slider.value = val;
        if (selectedLed !== null && leds[selectedLed]) {
            const cur = leds[selectedLed].color || { r: 0, g: 255, b: 100 };
            cur[channel] = val;
            setSelectedLedColor(cur.r, cur.g, cur.b);
        }
    });
};

bindRgbControl('ledRSlider', 'ledRNum', 'r');
bindRgbControl('ledGSlider', 'ledGNum', 'g');
bindRgbControl('ledBSlider', 'ledBNum', 'b');

document.querySelectorAll('.palette-swatch-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (selectedLed === null) {
            if (leds.length > 0) selectLed(0);
            else return;
        }
        const r = parseInt(btn.getAttribute('data-r'), 10);
        const g = parseInt(btn.getAttribute('data-g'), 10);
        const b = parseInt(btn.getAttribute('data-b'), 10);
        setSelectedLedColor(r, g, b);
        showToast(`🎨 Set LED #${selectedLed} to ${btn.title}!`);
    });
});

document.getElementById('inspectorSampleBtn')?.addEventListener('click', () => {
    if (selectedLed === null || !leds[selectedLed]) return;
    const col = sampleColorAtNorm(leds[selectedLed].x, leds[selectedLed].y);
    if (col) {
        setSelectedLedColor(col.r, col.g, col.b);
        showToast(`🎨 Sampled artwork color for LED #${selectedLed}!`);
    } else {
        showToast(`⚠️ No graphic pixel found directly under LED #${selectedLed}`);
    }
});

document.getElementById('inspectorCopyNextBtn')?.addEventListener('click', () => {
    if (selectedLed === null || !leds[selectedLed] || !leds[selectedLed].color) return;
    const srcCol = { ...leds[selectedLed].color };
    let count = 0;
    for (let i = selectedLed + 1; i <= Math.min(leds.length - 1, selectedLed + 5); i++) {
        leds[i].color = { ...srcCol };
        count++;
    }
    if (count > 0) {
        showToast(`⏩ Copied color to next ${count} LEDs along the wire!`);
        if (isWifiStreaming) sendLivePixelFrame(performance.now());
    }
});

document.getElementById('inspectorDeselectBtn')?.addEventListener('click', () => deselectLed());

// Canvas Toolbar Box Select, Select All, and Clear Bindings
const boxSelectBtn = document.getElementById('boxSelectBtn');
if (boxSelectBtn) {
    boxSelectBtn.addEventListener('click', () => {
        isBoxSelectMode = !isBoxSelectMode;
        boxSelectBtn.classList.toggle('active', isBoxSelectMode);
        canvas.style.cursor = isBoxSelectMode ? 'crosshair' : 'default';
        showToast(isBoxSelectMode ? '⬚ Box Select mode enabled: Drag across LEDs to select' : '🖱️ Normal Pan/Select mode restored');
    });
}

document.getElementById('selectAllBtn')?.addEventListener('click', () => selectAllLeds());
document.getElementById('clearSelectionBtn')?.addEventListener('click', () => deselectLed());

// Inspector Multi-Selection Action Bar Bindings
document.getElementById('inspectorSelectAllBtn')?.addEventListener('click', () => selectAllLeds());
document.getElementById('inspectorInvertBtn')?.addEventListener('click', () => invertLedSelection());
document.getElementById('inspectorClearBtn')?.addEventListener('click', () => deselectLed());

// Group Animation Controls Bindings
document.getElementById('applyGroupEffectBtn')?.addEventListener('click', () => applyGroupEffectToSelection());
document.getElementById('removeGroupEffectBtn')?.addEventListener('click', () => removeGroupEffectFromSelection());

const groupSpeedSlider = document.getElementById('groupSpeedSlider');
const groupSpeedVal = document.getElementById('groupSpeedVal');
if (groupSpeedSlider) {
    groupSpeedSlider.addEventListener('input', (e) => {
        if (groupSpeedVal) groupSpeedVal.textContent = `${e.target.value} BPM`;
    });
}

// ============================================================================
// COLOR SCIENCE & VIBRANCY BOOSTING
// ============================================================================
function rgbToHsl(r, g, b) {
    const rNorm = r / 255.0;
    const gNorm = g / 255.0;
    const bNorm = b / 255.0;
    const max = Math.max(rNorm, gNorm, bNorm);
    const min = Math.min(rNorm, gNorm, bNorm);
    let h = 0, s = 0;
    const l = (max + min) / 2.0;

    if (max !== min) {
        const d = max - min;
        s = l > 0.5 ? d / (2.0 - max - min) : d / (max + min);
        switch (max) {
            case rNorm: h = (gNorm - bNorm) / d + (gNorm < bNorm ? 6 : 0); break;
            case gNorm: h = (bNorm - rNorm) / d + 2; break;
            case bNorm: h = (rNorm - gNorm) / d + 4; break;
        }
        h /= 6.0;
    }
    return { h, s, l };
}

// Boost custom image colors so WS2812Bs pop with true character vibrancy without falling back to dragon green
function boostCustomImageColor(r, g, b) {
    const maxVal = Math.max(r, g, b);
    const minVal = Math.min(r, g, b);
    const delta = maxVal - minVal;

    // 1. Dark pixels (shadows, line art, dark contours):
    // Never leave an LED completely dark or unlit on the costume
    if (maxVal < 45) {
        if (delta >= 10) {
            const { h, s } = rgbToHsl(r, g, b);
            return hslToRgb(h, Math.min(1.0, s * 1.5 + 0.2), 0.28);
        }
        // Neutral black/charcoal -> clean cool starlight night glow
        return { r: 50, g: 52, b: 65 };
    }

    // 2. Whites, Silvers, and Light Neutrals (low saturation, high lightness):
    if (delta < 28 && maxVal > 170) {
        return { r: 255, g: 250, b: 242 };
    }

    // 3. Colored pixels: Boost saturation and normalize lightness for maximum WS2812B punch!
    const { h, s, l } = rgbToHsl(r, g, b);
    const boostedS = Math.min(1.0, Math.max(0.65, s * 1.35 + 0.12));

    let boostedL = 0.50;
    if (l < 0.40) {
        boostedL = 0.38 + (l / 0.40) * 0.12;
    } else if (l > 0.65) {
        boostedL = 0.52 + (l - 0.65) * 0.25;
    } else {
        boostedL = 0.48 + (l - 0.40) * 0.16;
    }
    boostedL = Math.min(0.70, Math.max(0.35, boostedL));

    const result = hslToRgb(h, boostedS, boostedL);

    // Ensure dominant channel reaches punchy brightness for physical LEDs
    const resMax = Math.max(result.r, result.g, result.b);
    if (resMax > 0 && resMax < 255 && boostedS > 0.5) {
        const scale = 255 / resMax;
        const factor = 0.7;
        result.r = Math.min(255, Math.round(result.r * (1 + (scale - 1) * factor)));
        result.g = Math.min(255, Math.round(result.g * (1 + (scale - 1) * factor)));
        result.b = Math.min(255, Math.round(result.b * (1 + (scale - 1) * factor)));
    }

    return result;
}

// Boost vibrancy and saturation of sampled colors so physical WS2812B LEDs shine with true character colors
function boostLedVibrancy(r, g, b, relX, relY) {
    // If user uploaded a custom graphic or selected Cinderella's Coach, preserve and boost authentic colors!
    if (currentGraphicType === 'custom_image' || currentGraphicType === 'cinderellas_coach') {
        return boostCustomImageColor(r, g, b);
    }

    // --- Pete's Dragon Built-in Preset Enhancement ---
    // If pixel is near-black line art, contour, or dark shadow (< 60):
    // Default to vibrant dragon green for the built-in dragon graphic.
    const maxVal = Math.max(r, g, b);
    if (maxVal < 60) {
        return { r: 15, g: 255, b: 35 };
    }

    // Convert to HSV to evaluate dominant hue and saturation
    const rNorm = r / 255.0;
    const gNorm = g / 255.0;
    const bNorm = b / 255.0;
    const max = Math.max(rNorm, gNorm, bNorm);
    const min = Math.min(rNorm, gNorm, bNorm);
    const delta = max - min;

    let hue = 0;
    if (delta > 0.001) {
        if (max === rNorm) {
            hue = ((gNorm - bNorm) / delta) % 6;
        } else if (max === gNorm) {
            hue = (bNorm - rNorm) / delta + 2;
        } else {
            hue = (rNorm - gNorm) / delta + 4;
        }
        hue = Math.round(hue * 60);
        if (hue < 0) hue += 360;
    }

    // 1. Pete's Dragon Hair Crest / Tuft (at the top of the head: relY < 0.12):
    // Produce vivid Disney flame orange hair!
    if (currentGraphicType === 'builtin_dragon' && relY !== undefined && relY < 0.12 && relX > 0.35 && relX < 0.62) {
        return { r: 255, g: 120, b: 0 };
    }

    // 2. Wings / Pink / Magenta / Violet:
    // Electric Disney Hot Pink: equal punch on Red & Blue with minimal green
    if ((hue >= 265 || hue <= 15) && (r > g + 8 || b > g || delta > 0.12)) {
        return { r: 255, g: 25, b: 230 };
    }

    // 3. Orange / Red (Hue 15° to 55°):
    if (hue > 15 && hue < 55 && r > g + 15) {
        return { r: 255, g: 120, b: 0 };
    }

    // 4. Lime Green / Yellow-Green Underbelly (Hue 55° to 95°):
    if (hue >= 55 && hue < 95) {
        const rLed = Math.min(100, Math.max(50, Math.round(r * 0.7)));
        return { r: rLed, g: 255, b: 15 };
    }

    // 5. Cyan / Sky Blue (Hue 175° to 260°):
    if (hue >= 175 && hue < 260) {
        const gLed = Math.min(220, Math.max(80, Math.round(g * 0.9)));
        return { r: 0, g: gLed, b: 255 };
    }

    // 6. Emerald Dragon Green Body (Hue 95° to 175°, or default):
    return {
        r: Math.min(40, Math.max(10, Math.round(r * 0.3))),
        g: 255,
        b: Math.min(60, Math.max(25, Math.round(b * 0.4)))
    };
}

// Sample artwork pixel color at normalized shirt coordinates
function sampleColorAtNorm(normX, normY) {
    const gb = getGraphicChestBounds();
    const relX = (normX - gb.normX) / gb.normW;
    const relY = (normY - gb.normY) / gb.normH;
    if (relX < 0 || relX > 1 || relY < 0 || relY > 1) {
        return null;
    }

    const activeImg = getActiveGraphicImg();
    const targetW = 360;
    let targetH = 360;

    const offCanvas = document.createElement('canvas');
    const offCtx = offCanvas.getContext('2d');

    if (activeImg) {
        targetH = Math.max(120, Math.round(targetW * (activeImg.naturalHeight / activeImg.naturalWidth)));
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        offCtx.drawImage(activeImg, 0, 0, targetW, targetH);
    } else {
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        drawPetesDragon(offCtx, { x: 0, y: 0, width: targetW, height: targetH });
    }

    const px = Math.floor(relX * targetW);
    const py = Math.floor(relY * targetH);
    if (px < 0 || px >= targetW || py < 0 || py >= targetH) return null;

    const p = offCtx.getImageData(px, py, 1, 1).data;
    if (p[3] < 30) return null;

    return boostLedVibrancy(p[0], p[1], p[2], relX, relY);
}

// Resample colors for all current LEDs based on current background graphic
function resampleAllLedColors() {
    if (!leds || leds.length === 0) return;

    const gb = getGraphicChestBounds();
    const activeImg = getActiveGraphicImg();
    const targetW = 360;
    let targetH = 360;

    const offCanvas = document.createElement('canvas');
    const offCtx = offCanvas.getContext('2d');

    if (activeImg) {
        targetH = Math.max(120, Math.round(targetW * (activeImg.naturalHeight / activeImg.naturalWidth)));
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        offCtx.drawImage(activeImg, 0, 0, targetW, targetH);
    } else {
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        drawPetesDragon(offCtx, { x: 0, y: 0, width: targetW, height: targetH });
    }

    const imgData = offCtx.getImageData(0, 0, targetW, targetH).data;
    let count = 0;

    for (let i = 0; i < leds.length; i++) {
        const normX = leds[i].x;
        const normY = leds[i].y;
        const relX = (normX - gb.normX) / gb.normW;
        const relY = (normY - gb.normY) / gb.normH;
        if (relX < 0 || relX > 1 || relY < 0 || relY > 1) continue;

        const px = Math.floor(relX * targetW);
        const py = Math.floor(relY * targetH);
        if (px < 0 || px >= targetW || py < 0 || py >= targetH) continue;

        const pIdx = (py * targetW + px) * 4;
        if (imgData[pIdx + 3] < 30) continue;

        leds[i].color = boostLedVibrancy(imgData[pIdx], imgData[pIdx + 1], imgData[pIdx + 2], relX, relY);
        count++;
    }
    showToast(`🎨 Resampled ${count} LED colors from background graphic!`);
}

// ============================================================================
// CONTINUOUS PHYSICAL WIRING ROUTING (Shortest Path: Nearest-Neighbor + 2-Opt)
// Sorts and renumbers LEDs so LED[i+1] is always immediately adjacent to LED[i].
// Minimizes wire travel, prevents crisscrossing, and makes costume sewing easy!
// ============================================================================
function optimizeLedWiringOrder(points, startCorner = 'bottom-left') {
    if (!points || points.length <= 2) return points;

    const n = points.length;

    // 1. Pick starting LED (e.g. bottom-left near the waist / battery pack)
    let startIdx = 0;
    let bestScore = Infinity;

    for (let i = 0; i < n; i++) {
        let score;
        const p = points[i];
        if (startCorner === 'bottom-left') {
            score = (1.0 - p.y) * 1.5 + p.x;
        } else if (startCorner === 'bottom-center') {
            score = (1.0 - p.y) * 1.5 + Math.abs(p.x - 0.5);
        } else if (startCorner === 'bottom-right') {
            score = (1.0 - p.y) * 1.5 + (1.0 - p.x);
        } else { // top-left
            score = p.y * 1.5 + p.x;
        }
        if (score < bestScore) {
            bestScore = score;
            startIdx = i;
        }
    }

    // 2. Nearest Neighbor Tour Construction
    const unvisited = new Set();
    for (let i = 0; i < n; i++) {
        if (i !== startIdx) unvisited.add(i);
    }

    const path = [startIdx];
    while (unvisited.size > 0) {
        const curr = path[path.length - 1];
        let nearest = -1;
        let minD = Infinity;

        for (const idx of unvisited) {
            const dx = points[curr].x - points[idx].x;
            const dy = points[curr].y - points[idx].y;
            const d = dx * dx + dy * dy;
            if (d < minD) {
                minD = d;
                nearest = idx;
            }
        }

        path.push(nearest);
        unvisited.delete(nearest);
    }

    // Distance helper
    const dist = (a, b) => Math.hypot(points[a].x - points[b].x, points[a].y - points[b].y);

    // 3. 2-Opt Optimization Pass (Untangles crossovers & minimizes total physical wire length)
    let improved = true;
    let iterations = 0;
    while (improved && iterations < 60) {
        improved = false;
        iterations++;
        for (let i = 0; i < n - 2; i++) {
            for (let j = i + 2; j < n; j++) {
                if (j === n - 1) {
                    const dCur = dist(path[i], path[i + 1]);
                    const dNew = dist(path[i], path[j]);
                    if (dNew < dCur - 1e-5) {
                        let left = i + 1, right = j;
                        while (left < right) {
                            const tmp = path[left];
                            path[left] = path[right];
                            path[right] = tmp;
                            left++;
                            right--;
                        }
                        improved = true;
                    }
                } else {
                    const dCur = dist(path[i], path[i + 1]) + dist(path[j], path[j + 1]);
                    const dNew = dist(path[i], path[j]) + dist(path[i + 1], path[j + 1]);
                    if (dNew < dCur - 1e-5) {
                        let left = i + 1, right = j;
                        while (left < right) {
                            const tmp = path[left];
                            path[left] = path[right];
                            path[right] = tmp;
                            left++;
                            right--;
                        }
                        improved = true;
                    }
                }
            }
        }
    }

    return path.map(idx => points[idx]);
}

// SCATTER 100 LEDs (Farthest-Point Sampling inside graphic with pixel color matching)
function scatterLedsOnGraphic(targetCount = 100, colorMatch = true) {
    const targetW = 360;
    let targetH = 360;

    const offCanvas = document.createElement('canvas');
    const offCtx = offCanvas.getContext('2d');
    const activeImg = getActiveGraphicImg();

    if (activeImg) {
        targetH = Math.max(120, Math.round(targetW * (activeImg.naturalHeight / activeImg.naturalWidth)));
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        offCtx.drawImage(activeImg, 0, 0, targetW, targetH);
    } else {
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        drawPetesDragon(offCtx, { x: 0, y: 0, width: targetW, height: targetH });
    }

    const imgData = offCtx.getImageData(0, 0, targetW, targetH);
    const data = imgData.data;

    let hasTransparency = false;
    for (let i = 3; i < data.length; i += 16) {
        if (data[i] < 200) {
            hasTransparency = true;
            break;
        }
    }

    // Detect background type for opaque images by sampling the 4 corners
    let isLightBg = false;
    let isDarkBg = false;
    if (!hasTransparency) {
        const cornerCoords = [
            [4, 4],
            [targetW - 5, 4],
            [4, targetH - 5],
            [targetW - 5, targetH - 5],
            [Math.floor(targetW / 2), 4],
            [Math.floor(targetW / 2), targetH - 5]
        ];
        let lightCorners = 0;
        let darkCorners = 0;
        for (const [cx, cy] of cornerCoords) {
            const cIdx = (cy * targetW + cx) * 4;
            const cLum = 0.299 * data[cIdx] + 0.587 * data[cIdx + 1] + 0.114 * data[cIdx + 2];
            if (cLum > 215) lightCorners++;
            else if (cLum < 45) darkCorners++;
        }
        if (lightCorners >= 3) isLightBg = true;
        else if (darkCorners >= 3) isDarkBg = true;
    }

    const step = 3;
    const candidates = [];
    for (let y = 3; y < targetH - 3; y += step) {
        for (let x = 3; x < targetW - 3; x += step) {
            const idx = (y * targetW + x) * 4;
            const a = data[idx + 3];
            const r = data[idx];
            const g = data[idx + 1];
            const b = data[idx + 2];

            let isFg = false;
            if (hasTransparency) {
                // For Pete's dragon built-in, avoid contour ink lines (< 60)
                if (currentGraphicType === 'builtin_dragon') {
                    isFg = (a > 80 && Math.max(r, g, b) >= 60);
                } else {
                    isFg = (a > 60);
                }
            } else if (isLightBg) {
                // Opaque image on white / light background: foreground is anything non-white
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                const maxC = Math.max(r, g, b);
                const minC = Math.min(r, g, b);
                const satDelta = maxC - minC;
                isFg = (lum < 225 || satDelta > 25);
            } else if (isDarkBg) {
                // Opaque image on dark background: foreground is visible graphic
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                isFg = (lum > 45);
            } else {
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                isFg = (lum > 40);
            }

            if (isFg) {
                candidates.push({ x, y, r, g, b });
            }
        }
    }

    if (candidates.length < targetCount) {
        alert(`Graphic area is too small to distribute ${targetCount} LEDs!`);
        return;
    }

    // Farthest Point Sampling (FPS) for maximal, uniform organic distribution
    const numCandidates = candidates.length;
    const minDist = new Float32Array(numCandidates).fill(1e9);
    const selected = [];

    let startIdx = Math.floor(numCandidates / 2);
    selected.push(candidates[startIdx]);

    for (let i = 0; i < numCandidates; i++) {
        const dx = candidates[i].x - candidates[startIdx].x;
        const dy = candidates[i].y - candidates[startIdx].y;
        minDist[i] = dx * dx + dy * dy;
    }

    for (let k = 1; k < targetCount; k++) {
        let maxD = -1;
        let bestIdx = 0;
        for (let i = 0; i < numCandidates; i++) {
            if (minDist[i] > maxD) {
                maxD = minDist[i];
                bestIdx = i;
            }
        }

        const chosen = candidates[bestIdx];
        selected.push(chosen);

        for (let i = 0; i < numCandidates; i++) {
            const dx = candidates[i].x - chosen.x;
            const dy = candidates[i].y - chosen.y;
            const d = dx * dx + dy * dy;
            if (d < minDist[i]) {
                minDist[i] = d;
            }
        }
    }

    const gb = getGraphicChestBounds();
    const newLeds = [];

    for (let i = 0; i < selected.length; i++) {
        const p = selected[i];
        const relX = p.x / targetW;
        const relY = p.y / targetH;
        const normX = gb.normX + relX * gb.normW;
        const normY = gb.normY + relY * gb.normH;

        let col = { r: p.r, g: p.g, b: p.b };
        if (colorMatch) {
            col = boostLedVibrancy(col.r, col.g, col.b, relX, relY);
        }

        newLeds.push({
            x: Math.max(0.05, Math.min(0.95, parseFloat(normX.toFixed(3)))),
            y: Math.max(0.05, Math.min(0.95, parseFloat(normY.toFixed(3)))),
            color: col
        });
    }

    // Sort & renumber LEDs into a continuous physical wiring path (starts near waist / bottom-left)
    leds = optimizeLedWiringOrder(newLeds, 'bottom-left');
    while (sparkles.length < leds.length) sparkles.push(0);

    activePattern = 'steady_sparkle';
    const patSelect = document.getElementById('patternSelect');
    if (patSelect) patSelect.value = 'steady_sparkle';

    updateLedCountUI();
    showToast(`🌈 ${targetCount} LEDs scattered & ordered along continuous wiring route!`);
}

// OUTLINE 50 LEDs (Moore-Neighbor Clockwise Boundary Tracing)
function autoOutlineCurrentGraphic(targetCount = 50) {
    const targetW = 320;
    let targetH = 320;

    const offCanvas = document.createElement('canvas');
    const offCtx = offCanvas.getContext('2d');
    const activeImg = getActiveGraphicImg();

    if (activeImg) {
        targetH = Math.max(100, Math.round(targetW * (activeImg.naturalHeight / activeImg.naturalWidth)));
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        offCtx.drawImage(activeImg, 0, 0, targetW, targetH);
    } else {
        offCanvas.width = targetW;
        offCanvas.height = targetH;
        const fakeBounds = { x: 0, y: 0, width: targetW, height: targetH };
        drawPetesDragon(offCtx, fakeBounds);
    }

    const imgData = offCtx.getImageData(0, 0, targetW, targetH);
    const data = imgData.data;

    let hasTransparency = false;
    for (let i = 3; i < data.length; i += 16) {
        if (data[i] < 200) {
            hasTransparency = true;
            break;
        }
    }

    let isLightBg = false;
    if (!hasTransparency) {
        const cornerCoords = [[4, 4], [targetW - 5, 4], [4, targetH - 5], [targetW - 5, targetH - 5]];
        let lightCorners = 0;
        for (const [cx, cy] of cornerCoords) {
            const cIdx = (cy * targetW + cx) * 4;
            const cLum = 0.299 * data[cIdx] + 0.587 * data[cIdx + 1] + 0.114 * data[cIdx + 2];
            if (cLum > 215) lightCorners++;
        }
        if (lightCorners >= 3) isLightBg = true;
    }

    const isFg = (x, y) => {
        if (x < 0 || x >= targetW || y < 0 || y >= targetH) return false;
        const idx = (y * targetW + x) * 4;
        const a = data[idx + 3];
        if (hasTransparency) {
            return a > 40;
        } else if (isLightBg) {
            const r = data[idx], g = data[idx + 1], b = data[idx + 2];
            const lum = 0.299 * r + 0.587 * g + 0.114 * b;
            const satDelta = Math.max(r, g, b) - Math.min(r, g, b);
            return (lum < 225 || satDelta > 25);
        } else {
            const r = data[idx], g = data[idx + 1], b = data[idx + 2];
            const lum = 0.299 * r + 0.587 * g + 0.114 * b;
            return lum > 40;
        }
    };

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
        alert("The detected outline is too small to distribute LEDs.");
        return;
    }

    const cumulativeDist = [0];
    let totalLength = 0;
    for (let i = 1; i < rawPerimeter.length; i++) {
        const d = Math.hypot(rawPerimeter[i].x - rawPerimeter[i - 1].x, rawPerimeter[i].y - rawPerimeter[i - 1].y);
        totalLength += d;
        cumulativeDist.push(totalLength);
    }
    const loopCloseDist = Math.hypot(rawPerimeter[0].x - rawPerimeter[rawPerimeter.length - 1].x, rawPerimeter[0].y - rawPerimeter[rawPerimeter.length - 1].y);
    totalLength += loopCloseDist;

    const step = totalLength / targetCount;
    const gb = getGraphicChestBounds();
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

        const normX = gb.normX + (px / targetW) * gb.normW;
        const normY = gb.normY + (py / targetH) * gb.normH;

        // Sample color at perimeter point as well
        const col = sampleColorAtNorm(normX, normY);

        newLeds.push({
            x: Math.max(0.05, Math.min(0.95, parseFloat(normX.toFixed(3)))),
            y: Math.max(0.05, Math.min(0.95, parseFloat(normY.toFixed(3)))),
            color: col || { r: 255, g: 250, b: 242 }
        });
    }

    leds = newLeds;
    while (sparkles.length < leds.length) sparkles.push(0);
    updateLedCountUI();
    showToast(`✨ ${targetCount} LEDs redistributed along graphic outline!`);
}

// Switch costume graphic preset (Pete's Dragon, Cinderella's Coach, or Custom Upload)
async function loadGraphicPreset(type) {
    const uploadContainer = document.getElementById('customUploadContainer');
    const resetBtn = document.getElementById('resetArtworkBtn');
    const graphicSelect = document.getElementById('graphicPresetSelect');
    if (graphicSelect) graphicSelect.value = type;

    if (type === 'cinderellas_coach') {
        currentGraphicType = 'cinderellas_coach';
        customArtworkImg = null;
        customArtworkDataUrl = null;
        if (uploadContainer) uploadContainer.style.display = 'none';
        if (resetBtn) resetBtn.style.display = 'block';

        // Load Cinderella's Coach preset if available from server
        try {
            const res = await fetch('/api/preset/cinderellas_coach.json');
            if (res.ok) {
                const profileData = await res.json();
                if (Array.isArray(profileData.leds) && profileData.leds.length > 0) {
                    leds = profileData.leds;
                    while (sparkles.length < leds.length) sparkles.push(0);
                    if (Array.isArray(profileData.animationGroups)) {
                        animationGroups = profileData.animationGroups;
                    } else {
                        animationGroups = [];
                    }
                    rebuildLedGroupMap();
                    renderActiveGroupsList();
                    updateLedCountUI();
                    const nameIn = document.getElementById('profileNameInput');
                    if (nameIn) nameIn.value = "Cinderella's Coach";
                    showToast("🎃 Loaded Cinderella's Coach with 100 color-matched LEDs!");
                    return;
                }
            }
        } catch (e) {
            console.warn("Could not fetch Cinderella preset:", e);
        }

        animationGroups = [];
        rebuildLedGroupMap();
        renderActiveGroupsList();
        scatterLedsOnGraphic(100, true);
        showToast("🎃 Switched to Cinderella's Coach!");
    } else if (type === 'custom_upload') {
        if (uploadContainer) uploadContainer.style.display = 'block';
        if (resetBtn) resetBtn.style.display = customArtworkImg ? 'block' : 'none';
        if (customArtworkImg) {
            currentGraphicType = 'custom_image';
            scatterLedsOnGraphic(100, true);
        } else {
            const fileInput = document.getElementById('artworkUpload');
            if (fileInput) fileInput.click();
        }
    } else {
        // Default Pete's Dragon
        currentGraphicType = 'builtin_dragon';
        customArtworkImg = null;
        customArtworkDataUrl = null;
        if (uploadContainer) uploadContainer.style.display = 'none';
        if (resetBtn) resetBtn.style.display = 'none';
        const fileInput = document.getElementById('artworkUpload');
        if (fileInput) fileInput.value = '';

        try {
            const res = await fetch('/api/preset/petes_dragon.json');
            if (res.ok) {
                const profileData = await res.json();
                if (Array.isArray(profileData.leds) && profileData.leds.length > 0) {
                    leds = profileData.leds;
                    while (sparkles.length < leds.length) sparkles.push(0);
                    if (Array.isArray(profileData.animationGroups)) {
                        animationGroups = profileData.animationGroups;
                    } else {
                        animationGroups = [];
                    }
                    rebuildLedGroupMap();
                    renderActiveGroupsList();
                    updateLedCountUI();
                    const nameIn = document.getElementById('profileNameInput');
                    if (nameIn) nameIn.value = "Pete's Dragon";
                    showToast("🐉 Loaded Pete's Dragon with 100 color-matched LEDs!");
                    return;
                }
            }
        } catch (e) {
            console.warn("Could not fetch dragon preset:", e);
        }

        animationGroups = [];
        rebuildLedGroupMap();
        renderActiveGroupsList();
        scatterLedsOnGraphic(100, true);
        showToast("🔄 Restored default Pete's Dragon graphic!");
    }
}

// Graphic Preset Dropdown Handler
const graphicPresetSelect = document.getElementById('graphicPresetSelect');
if (graphicPresetSelect) {
    graphicPresetSelect.addEventListener('change', (e) => {
        loadGraphicPreset(e.target.value);
    });
}

// Custom Artwork Image Upload
const artworkUploadInput = document.getElementById('artworkUpload');
if (artworkUploadInput) {
    artworkUploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                customArtworkDataUrl = event.target.result;
                currentGraphicType = 'custom_image';
                const img = new Image();
                img.onload = () => {
                    customArtworkImg = img;
                    const resetBtn = document.getElementById('resetArtworkBtn');
                    if (resetBtn) resetBtn.style.display = 'block';
                    const graphicSelect = document.getElementById('graphicPresetSelect');
                    if (graphicSelect) graphicSelect.value = 'custom_upload';
                    const uploadContainer = document.getElementById('customUploadContainer');
                    if (uploadContainer) uploadContainer.style.display = 'block';
                    // Automatically scatter 100 color-matched LEDs across new artwork!
                    scatterLedsOnGraphic(100, true);
                };
                img.src = customArtworkDataUrl;
            };
            reader.readAsDataURL(file);
        }
    });
}

// Button Click Handlers
const optWiringBtn = document.getElementById('optimizeWiringBtn');
if (optWiringBtn) {
    optWiringBtn.addEventListener('click', () => {
        if (!leds || leds.length <= 2) return;
        leds = optimizeLedWiringOrder(leds, 'bottom-left');
        showToast(`🔌 Renumbered ${leds.length} LEDs along continuous physical wiring route!`);
    });
}

document.getElementById('scatterColorBtn').addEventListener('click', () => {
    scatterLedsOnGraphic(100, true);
});

document.getElementById('quick100Btn').addEventListener('click', () => {
    scatterLedsOnGraphic(100, true);
});

document.getElementById('autoOutlineBtn').addEventListener('click', () => {
    autoOutlineCurrentGraphic(50);
});

document.getElementById('quick50Btn').addEventListener('click', () => {
    autoOutlineCurrentGraphic(50);
});

document.getElementById('resampleColorsBtn').addEventListener('click', () => {
    resampleAllLedColors();
});

const resetArtworkBtn = document.getElementById('resetArtworkBtn');
if (resetArtworkBtn) {
    resetArtworkBtn.addEventListener('click', () => {
        loadGraphicPreset('builtin_dragon');
    });
}

// Preset Buttons
document.getElementById('presetSelect').addEventListener('change', (e) => {
    loadProfile(e.target.value);
});

// Export complete profile configuration JSON
function exportCurrentProfileJson() {
    const nameInput = document.getElementById('profileNameInput');
    const name = (nameInput?.value || '').trim() || (currentGraphicType === 'cinderellas_coach' ? "Cinderella_Coach" : "Petes_Dragon");
    const profileData = {
        name: name,
        savedAt: new Date().toISOString(),
        ledCount: leds.length,
        leds: leds,
        graphicType: currentGraphicType,
        customArtworkDataUrl: customArtworkDataUrl,
        animationGroups: animationGroups,
        settings: {
            pattern: activePattern,
            speedBpm: params.speedBpm,
            sparkleRate: params.sparkleRate,
            greenHue: params.greenHue,
            brightness: params.brightness,
            glowSize: params.glowSize
        }
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(profileData, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    const safeFilename = `${name.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}_profile.json`;
    dlAnchor.setAttribute("download", safeFilename);
    dlAnchor.click();
    showToast(`⬇ Exported ${safeFilename}`);
}

document.getElementById('saveProfileBtn').addEventListener('click', () => {
    const nameInput = document.getElementById('profileNameInput');
    const defaultName = currentGraphicType === 'cinderellas_coach' ? "Cinderella's Coach" : "Pete's Dragon";
    const name = (nameInput?.value || '').trim() || prompt("Enter a name for this profile:", defaultName);
    if (name) {
        if (nameInput) nameInput.value = name;
        saveCurrentProfile(name);
    }
});

// Download & Import Profile Buttons
const downloadProfileBtn = document.getElementById('downloadProfileBtn');
if (downloadProfileBtn) {
    downloadProfileBtn.addEventListener('click', exportCurrentProfileJson);
}

const importProfileBtn = document.getElementById('importProfileBtn');
const importProfileFileInput = document.getElementById('importProfileFileInput');
if (importProfileBtn && importProfileFileInput) {
    importProfileBtn.addEventListener('click', () => importProfileFileInput.click());
    importProfileFileInput.addEventListener('change', (e) => {
        const file = e.target.files && e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (evt) => {
                try {
                    const parsed = JSON.parse(evt.target.result);
                    const profile = Array.isArray(parsed) ? { leds: parsed, name: file.name.replace('.json', '') } : parsed;
                    applyProfileData(profile);
                    showToast(`📂 Imported "${profile.name || file.name}" (${leds.length} LEDs)!`);
                } catch (err) {
                    showToast("⚠️ Failed to parse profile JSON: " + err.message);
                }
            };
            reader.readAsText(file);
        }
        e.target.value = '';
    });
}

// Export JSON file (Section 5)
document.getElementById('saveLayoutBtn').addEventListener('click', () => {
    exportCurrentProfileJson();
});

// Generate FastLED C++ Code
document.getElementById('exportCodeBtn').addEventListener('click', () => {
    const hasAnyColors = leds.some(l => l.color);
    let code = '';

    if (hasAnyColors) {
        const paletteLines = [];
        for (let i = 0; i < leds.length; i++) {
            const c = leds[i].color || { r: 0, g: 255, b: 100 };
            paletteLines.push(`    CRGB(${c.r}, ${c.g}, ${c.b})${i < leds.length - 1 ? ',' : ''} // LED ${i}`);
        }

        if (activePattern === 'steady_sparkle') {
            code = `// ============================================================================
// FASTLED ANIMATION: PETE'S DRAGON ${leds.length}-LED STEADY COLOR + SPARKLES
// Generated by MSEP Simulator - kidmd/WDW-costumes
// ============================================================================
#define NUM_LEDS ${leds.length}

// Artwork Sampled Color Palette (PROGMEM flash storage)
const CRGB PROGMEM ARTWORK_PALETTE[NUM_LEDS] = {
${paletteLines.join('\n')}
};

void renderPetesDragonCustom(uint32_t t) {
    for (int i = 0; i < NUM_LEDS; i++) {
        // Steady baseline color (no breathing pulse)
        CRGB baseColor;
        baseColor.r = pgm_read_byte(&ARTWORK_PALETTE[i].r);
        baseColor.g = pgm_read_byte(&ARTWORK_PALETTE[i].g);
        baseColor.b = pgm_read_byte(&ARTWORK_PALETTE[i].b);
        leds[i] = baseColor;

        // Occasional Incandescent Starlight Sparkles (Probability: ${params.sparkleRate}%)
        if (random8() < ${Math.floor(params.sparkleRate * 0.4)}) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
}`;
        } else {
            code = `// ============================================================================
// FASTLED ANIMATION: PETE'S DRAGON ${leds.length}-LED COLOR-MATCHED COSTUME
// Generated by MSEP Simulator - kidmd/WDW-costumes
// ============================================================================
#define NUM_LEDS ${leds.length}

// Artwork Sampled Color Palette (PROGMEM flash storage)
const CRGB PROGMEM ARTWORK_PALETTE[NUM_LEDS] = {
${paletteLines.join('\n')}
};

void renderPetesDragonCustom(uint32_t t) {
    // Breathing tempo: ${params.speedBpm} BPM
    uint8_t breath = beatsin8(${Math.round(params.speedBpm / 2)}, 160, 255);

    for (int i = 0; i < NUM_LEDS; i++) {
        // Read color from artwork flash palette
        CRGB baseColor;
        baseColor.r = pgm_read_byte(&ARTWORK_PALETTE[i].r);
        baseColor.g = pgm_read_byte(&ARTWORK_PALETTE[i].g);
        baseColor.b = pgm_read_byte(&ARTWORK_PALETTE[i].b);

        // Apply organic breathing
        baseColor.nscale8_video(breath);
        leds[i] = baseColor;

        // Incandescent Starlight Sparkles (Probability: ${params.sparkleRate}%)
        if (random8() < ${Math.floor(params.sparkleRate * 0.4)}) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
}`;
        }
    } else {
        code = `// ============================================================================
// FASTLED ANIMATION: PETE'S DRAGON FLOAT (GENERATED BY SIMULATOR)
// ============================================================================
#define NUM_LEDS ${leds.length}
void renderPetesDragonCustom(uint32_t t) {
    for (int i = 0; i < NUM_LEDS; i++) {
        uint8_t breath = beatsin8(${Math.round(params.speedBpm / 2)}, 180, 255);
        leds[i] = CHSV(${Math.floor(params.greenHue * 255 / 360)}, 240, breath);
        if (random8() < ${Math.floor(params.sparkleRate * 0.4)}) {
            leds[i] = CRGB(255, 255, 230);
        }
    }
}`;
    }

    document.getElementById('codeOutput').textContent = code;
    document.getElementById('codeModal').classList.add('open');
});

document.getElementById('closeModalBtn').addEventListener('click', () => {
    document.getElementById('codeModal').classList.remove('open');
});

document.getElementById('copyCodeBtn').addEventListener('click', () => {
    const codeText = document.getElementById('codeOutput').textContent;
    navigator.clipboard.writeText(codeText).then(() => {
        showToast("📋 FastLED C++ code copied to clipboard!");
    });
});

// ============================================================================
// ESP32 USB SERIAL & ONE-CLICK FIRMWARE FLASHER
// ============================================================================
let detectedSerialPort = null;
let isSerialPortReady = false;
let isFlashingFirmware = false;

async function checkSerialPortStatus() {
    const dot = document.getElementById('serialIndicatorDot');
    const text = document.getElementById('serialStatusText');
    const portBadge = document.getElementById('flashPortBadge');
    
    try {
        const res = await fetch('/api/serial_status');
        if (res.ok) {
            const data = await res.json();
            if (data.connected && data.port) {
                detectedSerialPort = data.port;
                isSerialPortReady = !!data.ready;
                if (data.ready) {
                    if (dot) dot.style.background = '#3fb950';
                    if (text) {
                        text.textContent = `ESP32 on ${data.port} (Ready)`;
                        text.style.color = '#3fb950';
                    }
                } else {
                    if (dot) dot.style.background = '#e3b341';
                    if (text) {
                        text.textContent = `${data.port} Wedged: Please Re-plug USB!`;
                        text.style.color = '#e3b341';
                    }
                }
                if (portBadge) {
                    portBadge.textContent = data.port;
                    portBadge.style.display = 'inline-block';
                }
                return;
            }
        }
    } catch (e) {
        // Backend offline or error
    }

    detectedSerialPort = null;
    if (dot) dot.style.background = '#f85149';
    if (text) {
        text.textContent = 'No ESP32 (Plug into USB)';
        text.style.color = '#8b949e';
    }
    if (portBadge) {
        portBadge.style.display = 'none';
    }
}

const refreshSerialBtn = document.getElementById('refreshSerialBtn');
if (refreshSerialBtn) {
    refreshSerialBtn.addEventListener('click', () => {
        checkSerialPortStatus();
        showToast("🔄 Refreshed USB serial port status");
    });
}

// Initial status check & auto-poll every 6 seconds
checkSerialPortStatus();
setInterval(checkSerialPortStatus, 6000);

// Flash to Connected ESP32 handler
const flashEsp32Btn = document.getElementById('flashEsp32Btn');
const flashModal = document.getElementById('flashModal');
const closeFlashModalBtn = document.getElementById('closeFlashModalBtn');
const flashDoneBtn = document.getElementById('flashDoneBtn');
const flashStatusText = document.getElementById('flashStatusText');
const flashProgressBar = document.getElementById('flashProgressBar');
const flashTerminal = document.getElementById('flashTerminal');
const flashTipText = document.getElementById('flashTipText');

if (flashEsp32Btn) {
    flashEsp32Btn.addEventListener('click', async () => {
        if (isFlashingFirmware) return;

        if (!isSerialPortReady && detectedSerialPort) {
            flashModal.classList.add('open');
            flashStatusText.textContent = `⚠️ USB Port ${detectedSerialPort} Wedged (Windows Error 31)`;
            flashStatusText.style.color = '#f85149';
            flashProgressBar.style.width = '100%';
            flashProgressBar.style.background = '#da3633';
            flashTipText.textContent = 'Please unplug the USB cable, wait 2 seconds, and plug it back in!';
            flashTerminal.textContent = `[PORT ERROR] Windows driver locked ${detectedSerialPort}: "A device attached to the system is not functioning" (Error 31).\n\n` +
                `TO FIX THIS NOW:\n` +
                `1. Unplug the ESP32 USB cable from your computer.\n` +
                `2. Wait 2 seconds.\n` +
                `3. Plug it back into your USB port.\n` +
                `4. Watch the top indicator turn green: "● ESP32 on ${detectedSerialPort} (Ready)".\n` +
                `5. Click Flash again!\n`;
            flashDoneBtn.style.display = 'inline-block';
            return;
        }

        // Open modal and show initial build state
        flashModal.classList.add('open');
        flashStatusText.textContent = `Building costume firmware (${leds.length} LEDs)...`;
        flashStatusText.style.color = 'var(--text-main)';
        flashProgressBar.style.width = '20%';
        flashProgressBar.style.background = '#388bfd';
        flashDoneBtn.style.display = 'none';
        flashTipText.textContent = 'Compiling C++ FastLED code and flashing via USB...';
        
        flashTerminal.textContent = `[SIMULATOR] Preparing firmware for ${leds.length} LEDs...\n` +
            `[SIMULATOR] Active Pattern: ${activePattern}\n` +
            `[SIMULATOR] Speed: ${params.speedBpm} BPM | Sparkle Rate: ${params.sparkleRate}%\n` +
            `[SIMULATOR] Generating include/costume_config.h...\n` +
            `[SIMULATOR] Connecting to ESP32...\n--------------------------------------------------\n`;

        isFlashingFirmware = true;
        flashEsp32Btn.disabled = true;
        flashEsp32Btn.style.opacity = '0.6';

        // Animate progress bar incrementally while waiting
        let progress = 20;
        const progressTimer = setInterval(() => {
            if (progress < 85) {
                progress += 5;
                flashProgressBar.style.width = `${progress}%`;
            }
        }, 600);

        try {
            const payload = {
                numLeds: leds.length,
                pattern: activePattern,
                speedBpm: params.speedBpm,
                sparkleRate: params.sparkleRate,
                greenHue: params.greenHue,
                brightness: params.brightness,
                palette: leds.map(l => l.color || { r: 15, g: 255, b: 35 })
            };

            const response = await fetch('/api/flash_firmware', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            clearInterval(progressTimer);

            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                flashProgressBar.style.width = '100%';
                flashProgressBar.style.background = '#238636';
                flashStatusText.textContent = `🎉 Flash Complete! Running on ${data.port || 'ESP32'}`;
                flashStatusText.style.color = '#3fb950';
                flashTipText.textContent = 'ESP32 restarted and running your costume animation!';
                flashTerminal.textContent += (data.log || '') + '\n\n' +
                    `==================================================\n` +
                    `[SUCCESS] Costume successfully flashed to ESP32 on ${data.port}!\n` +
                    `GPIO 16 is now outputting the ${leds.length}-LED animation.\n` +
                    `==================================================`;
                showToast(`⚡ Flashed successfully to ${data.port}!`);
            } else {
                flashProgressBar.style.width = '100%';
                flashProgressBar.style.background = '#da3633';
                flashStatusText.textContent = `⚠️ Flash Failed: ${data.error || 'Check log'}`;
                flashStatusText.style.color = '#f85149';
                flashTipText.textContent = 'Ensure ESP32 is plugged in and hold BOOT button if needed.';
                flashTerminal.textContent += (data.log || '') + '\n\n' +
                    `--------------------------------------------------\n` +
                    `[ERROR] ${data.error || 'Upload failed'}\n` +
                    `Tip: Check USB cable or hold BOOT button on the ESP32 while connecting.`;
            }
        } catch (err) {
            clearInterval(progressTimer);
            flashProgressBar.style.width = '100%';
            flashProgressBar.style.background = '#da3633';
            flashStatusText.textContent = `⚠️ Error: ${err.message}`;
            flashStatusText.style.color = '#f85149';
            flashTerminal.textContent += `\n[CLIENT ERROR] ${err.message}\nMake sure simulator.py is running.`;
        } finally {
            isFlashingFirmware = false;
            flashEsp32Btn.disabled = false;
            flashEsp32Btn.style.opacity = '1';
            flashDoneBtn.style.display = 'block';
            flashTerminal.scrollTop = flashTerminal.scrollHeight;
            checkSerialPortStatus();
        }
    });
}

if (closeFlashModalBtn) {
    closeFlashModalBtn.addEventListener('click', () => {
        flashModal.classList.remove('open');
    });
}

if (flashDoneBtn) {
    flashDoneBtn.addEventListener('click', () => {
        flashModal.classList.remove('open');
    });
}

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

// ============================================================================
// WI-FI LIVE STREAM ENGINE & RECEIVER FLASHER
// ============================================================================
let isWifiStreaming = false;
let wifiTargetIp = '255.255.255.255';
let lastWifiStreamTime = 0;
let isSendingFrame = false;
let streamPacketCounter = 0;

const toggleWifiStreamBtn = document.getElementById('toggleWifiStreamBtn');
const wifiStreamDot = document.getElementById('wifiStreamDot');
const wifiStreamStatusText = document.getElementById('wifiStreamStatusText');
const wifiSettingsBtn = document.getElementById('wifiSettingsBtn');
const wifiModal = document.getElementById('wifiModal');
const closeWifiModalBtn = document.getElementById('closeWifiModalBtn');
const wifiSsidInput = document.getElementById('wifiSsidInput');
const wifiPasswordInput = document.getElementById('wifiPasswordInput');
const wifiTargetIpInput = document.getElementById('wifiTargetIpInput');
const saveWifiBtn = document.getElementById('saveWifiBtn');
const flashReceiverBtn = document.getElementById('flashReceiverBtn');

async function sendLivePixelFrame(timeMs) {
    if (!isWifiStreaming || isSendingFrame) return;
    if (timeMs - lastWifiStreamTime < 33) return; // 30 FPS throttle (~33ms)
    lastWifiStreamTime = timeMs;
    isSendingFrame = true;

    try {
        const pixelPayload = [];
        const total = leds.length;
        for (let i = 0; i < total; i++) {
            const col = computeLedColor(i, total, timeMs);
            pixelPayload.push({
                r: Math.max(0, Math.min(255, col.r)),
                g: Math.max(0, Math.min(255, col.g)),
                b: Math.max(0, Math.min(255, col.b))
            });
        }

        const res = await fetch('/api/stream_pixels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                targetIp: wifiTargetIp,
                pixels: pixelPayload
            })
        });
        const data = await res.json();
        if (data && data.success) {
            streamPacketCounter++;
            if (streamPacketCounter % 30 === 0 && wifiStreamStatusText) {
                wifiStreamStatusText.textContent = `Streaming (${total} LEDs @ 30 FPS)`;
            }
        }
    } catch (err) {
        console.warn("[WIFI STREAM] Packet send error:", err);
    } finally {
        isSendingFrame = false;
    }
}

async function loadWifiSettings() {
    try {
        const res = await fetch('/api/wifi_config');
        if (res.ok) {
            const data = await res.json();
            if (wifiSsidInput && data.ssid) wifiSsidInput.value = data.ssid;
            if (wifiPasswordInput && data.password) wifiPasswordInput.value = data.password;
            if (wifiTargetIpInput && data.targetIp) {
                wifiTargetIpInput.value = data.targetIp;
                wifiTargetIp = data.targetIp;
            }
        }
    } catch (e) {
        console.warn("[WIFI] Could not load Wi-Fi config:", e);
    }
}
loadWifiSettings();

if (toggleWifiStreamBtn) {
    toggleWifiStreamBtn.addEventListener('click', () => {
        isWifiStreaming = !isWifiStreaming;
        if (isWifiStreaming) {
            toggleWifiStreamBtn.textContent = '⏹ Stop Live Wi-Fi Stream';
            toggleWifiStreamBtn.style.background = 'linear-gradient(135deg, #da3633, #f85149)';
            if (wifiStreamDot) {
                wifiStreamDot.style.background = '#2ea043';
                wifiStreamDot.style.boxShadow = '0 0 8px #2ea043';
            }
            if (wifiStreamStatusText) {
                wifiStreamStatusText.textContent = `Streaming (${leds.length} LEDs @ 30 FPS)`;
                wifiStreamStatusText.style.color = '#3fb950';
            }
            showToast('📡 Wi-Fi live stream started! Updating LEDs in real time.');
        } else {
            toggleWifiStreamBtn.textContent = '▶ Start Live Wi-Fi Stream';
            toggleWifiStreamBtn.style.background = 'linear-gradient(135deg, #1f6feb, #388bfd)';
            if (wifiStreamDot) {
                wifiStreamDot.style.background = '#8b949e';
                wifiStreamDot.style.boxShadow = 'none';
            }
            if (wifiStreamStatusText) {
                wifiStreamStatusText.textContent = 'Standby (Off)';
                wifiStreamStatusText.style.color = 'var(--text-muted)';
            }
            showToast('⏹ Live Wi-Fi stream stopped.');
        }
    });
}

window.openWifiModal = function() {
    loadWifiSettings();
    const modal = document.getElementById('wifiModal') || wifiModal;
    if (modal) modal.classList.add('open');
};

window.closeWifiModal = function() {
    const modal = document.getElementById('wifiModal') || wifiModal;
    if (modal) modal.classList.remove('open');
};

if (wifiSettingsBtn) {
    wifiSettingsBtn.addEventListener('click', window.openWifiModal);
}

if (closeWifiModalBtn) {
    closeWifiModalBtn.addEventListener('click', window.closeWifiModal);
}

if (saveWifiBtn) {
    saveWifiBtn.addEventListener('click', async () => {
        const ssid = wifiSsidInput.value.trim();
        const password = wifiPasswordInput.value.trim();
        const targetIp = (wifiTargetIpInput.value.trim()) || '255.255.255.255';
        wifiTargetIp = targetIp;

        try {
            const res = await fetch('/api/save_wifi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ssid, password, targetIp })
            });
            const data = await res.json();
            if (data.success) {
                showToast('💾 Wi-Fi settings saved!');
                if (wifiModal) wifiModal.classList.remove('open');
            } else {
                showToast('⚠️ Failed to save Wi-Fi settings');
            }
        } catch (e) {
            showToast('⚠️ Error saving Wi-Fi settings: ' + e.message);
        }
    });
}

if (flashReceiverBtn) {
    flashReceiverBtn.addEventListener('click', async () => {
        const ssid = wifiSsidInput.value.trim();
        const password = wifiPasswordInput.value.trim();
        const targetIp = (wifiTargetIpInput.value.trim()) || '255.255.255.255';
        wifiTargetIp = targetIp;

        await fetch('/api/save_wifi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ssid, password, targetIp })
        });

        if (wifiModal) wifiModal.classList.remove('open');
        if (flashModal) flashModal.classList.add('open');

        flashStatusText.textContent = 'Building Wi-Fi Receiver Firmware...';
        flashStatusText.style.color = 'var(--text-main)';
        flashProgressBar.style.width = '20%';
        flashProgressBar.style.background = '#388bfd';
        flashDoneBtn.style.display = 'none';
        flashTipText.textContent = 'Flashing one-time Wi-Fi Receiver to ESP32...';

        flashTerminal.textContent = `[SIMULATOR] Preparing Wi-Fi Receiver firmware...\n` +
            `[SIMULATOR] Protocol: High-Speed UDP Pixel Stream (Port 4210)\n` +
            `[SIMULATOR] Target Network: ${ssid || 'MSEP-Costume-AP (Fallback)'}\n` +
            `[SIMULATOR] Connecting to ESP32 over USB...\n--------------------------------------------------\n`;

        let progress = 20;
        const progressTimer = setInterval(() => {
            progress = Math.min(progress + 4, 90);
            flashProgressBar.style.width = progress + '%';
        }, 800);

        try {
            const res = await fetch('/api/flash_wifi_receiver', { method: 'POST' });
            clearInterval(progressTimer);
            const data = await res.json();

            if (data.success) {
                flashProgressBar.style.width = '100%';
                flashProgressBar.style.background = '#238636';
                flashStatusText.textContent = `🎉 Wi-Fi Receiver Flashed to ${data.port || 'ESP32'}!`;
                flashStatusText.style.color = '#3fb950';
                flashTipText.textContent = 'Now unplug USB and connect ESP32 to a 5V wall charger!';
                flashTerminal.textContent += (data.log || '') + '\n\n' +
                    `==================================================\n` +
                    `[SUCCESS] Wi-Fi Receiver active on ${data.port}!\n` +
                    `1. Unplug USB cable from the ESP32.\n` +
                    `2. Plug ESP32 into your 5V/2A wall charger or battery pack.\n` +
                    `3. Click "▶ Start Live Wi-Fi Stream" to test in real time!\n` +
                    `==================================================`;
                showToast(`⚡ Receiver flashed successfully to ${data.port}!`);
            } else {
                flashProgressBar.style.width = '100%';
                flashProgressBar.style.background = '#da3633';
                flashStatusText.textContent = `⚠️ Flash Failed: ${data.error || 'Check log'}`;
                flashStatusText.style.color = '#f85149';
                flashTipText.textContent = 'Ensure ESP32 is plugged in via USB and click flash again.';
                flashTerminal.textContent += (data.log || '') + '\n\n' +
                    `--------------------------------------------------\n` +
                    `[ERROR] ${data.error || 'Upload failed'}\n`;
            }
        } catch (err) {
            clearInterval(progressTimer);
            flashProgressBar.style.width = '100%';
            flashProgressBar.style.background = '#da3633';
            flashStatusText.textContent = `⚠️ Error: ${err.message}`;
            flashStatusText.style.color = '#f85149';
            flashTerminal.textContent += `\n[CLIENT ERROR] ${err.message}\n`;
        } finally {
            flashDoneBtn.style.display = 'block';
            flashTerminal.scrollTop = flashTerminal.scrollHeight;
            checkSerialPortStatus();
        }
    });
}
