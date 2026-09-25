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
    sparkleRate: 1.5,
    greenHue: 140, // 100 = lime, 140 = emerald, 165 = seafoam
    brightness: 85,
    glowSize: 20,
    showWiring: false,
    showNumbers: false,
    reflectiveShine: true,
    showBib: true,
    bibYOffset: 0.57,
    bibScale: 1.0
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

// Carriage (No Horses) Artwork
const carriageNoHorsesImg = new Image();
let carriageNoHorsesLoaded = false;
carriageNoHorsesImg.onload = () => {
    carriageNoHorsesLoaded = true;
};
carriageNoHorsesImg.src = 'assets/Carriage_nohorses.png';

// Custom artwork image (if user uploads one or loads one from preset)
let customArtworkImg = null;
let currentGraphicType = 'builtin_dragon'; // 'builtin_dragon', 'cinderellas_coach', 'carriage_nohorses', or 'custom_image'
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
    if (currentGraphicType === 'carriage_nohorses') {
        if (carriageNoHorsesImg && carriageNoHorsesImg.naturalWidth > 0) {
            return carriageNoHorsesImg;
        }
        return carriageNoHorsesImg;
    }
    if (defaultDragonLoaded && defaultDragonImg.complete && defaultDragonImg.naturalWidth > 0) {
        return defaultDragonImg;
    }
    return null;
}

// Compute normalized bounds of the graphic on the athletic shirt
function getGraphicChestBounds() {
    const activeImg = getActiveGraphicImg();
    const maxH = 0.385; // Available vertical height strictly above bib (0.168 to 0.553)
    const maxW = 0.70;  // Maximum chest width between raglan seams
    const topY = 0.168; // Just below crew neck collar dip (0.14)

    let normH = maxH;
    let normW = 0.54;
    let normY = topY;

    if (activeImg && activeImg.naturalWidth > 0 && activeImg.naturalHeight > 0) {
        const aspect = activeImg.naturalWidth / activeImg.naturalHeight;
        if (aspect > 1.3) {
            // Wide landscape graphic (like Cinderella's Coach: aspect ~ 1.789, Carriage ~ 1.835)
            normW = maxW;
            normH = normW / (1.25 * aspect);
            if (normH > maxH) {
                normH = maxH;
                normW = normH * 1.25 * aspect;
            }
            normY = 0.22 + (0.40 - normH) * 0.4;
            if (normY + normH > 0.565) {
                normY = 0.565 - normH;
            }
        } else {
            // Portrait or square graphic (like Pete's Dragon: aspect ~ 0.706)
            // Scale so full height fits strictly in area above bib, keeping exact x/y ratio
            normH = maxH;
            normW = normH * 1.25 * aspect;
            if (normW > maxW) {
                normW = maxW;
                normH = normW / (1.25 * aspect);
            }
            normY = topY;
        }
    } else {
        // Fallback vector Pete's Dragon
        normH = maxH;
        normW = normH * 1.25 * 0.706;
        normY = topY;
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
let multiDragStartNorm = null;
let multiDragInitialPositions = new Map();

// Click-to-Draw Sequential Path State
let isDrawGroupMode = false;
let drawGroupLedIndices = [];
let drawGroupPoints = [];

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

function hexToRgb(hex) {
    if (!hex || typeof hex !== 'string') return null;
    const clean = hex.replace('#', '').trim();
    if (clean.length === 3) {
        return {
            r: parseInt(clean[0] + clean[0], 16),
            g: parseInt(clean[1] + clean[1], 16),
            b: parseInt(clean[2] + clean[2], 16)
        };
    }
    if (clean.length === 6) {
        return {
            r: parseInt(clean.slice(0, 2), 16),
            g: parseInt(clean.slice(2, 4), 16),
            b: parseInt(clean.slice(4, 6), 16)
        };
    }
    return null;
}


// ============================================================================
// PARADE CUE DIRECTOR (Autonomous 90s Float Show Sequence Engine)
// ============================================================================
let sequenceMode = false;           // false = Free-Run pattern, true = 90s Show Sequence
let sequenceLoopDuration = 90.0;    // Loop duration in seconds
let sequenceTime = 0.0;            // Current timeline position in seconds
let sequencePlaying = false;       // Playback state
let sequenceLoop = true;           // Loop back to 0:00
let sequenceCues = [];             // Array of cue objects
let lastTimelineFrameTime = performance.now();

// LEDs array: [{ x, y, color: {r, g, b} }]
let leds = [];

function initDefaultDragonLeds() {
    leds = [
        // Snout & Head (0 - 6)
        { x: 0.463, y: 0.230 }, { x: 0.444, y: 0.236 }, { x: 0.425, y: 0.249 },
        { x: 0.413, y: 0.261 }, { x: 0.425, y: 0.280 }, { x: 0.444, y: 0.292 }, { x: 0.469, y: 0.298 },
        // Neck & Front Leg (7 - 12)
        { x: 0.457, y: 0.323 }, { x: 0.444, y: 0.354 }, { x: 0.432, y: 0.392 },
        { x: 0.419, y: 0.429 }, { x: 0.432, y: 0.447 }, { x: 0.457, y: 0.441 },
        // Belly & Foot (13 - 18)
        { x: 0.475, y: 0.447 }, { x: 0.500, y: 0.454 }, { x: 0.525, y: 0.460 },
        { x: 0.550, y: 0.460 }, { x: 0.568, y: 0.454 }, { x: 0.587, y: 0.441 },
        // Back Leg & Tail Base (19 - 25)
        { x: 0.599, y: 0.460 }, { x: 0.618, y: 0.460 }, { x: 0.637, y: 0.447 },
        { x: 0.649, y: 0.429 }, { x: 0.661, y: 0.416 }, { x: 0.680, y: 0.404 }, { x: 0.699, y: 0.398 },
        // Tail Tip & Curl (26 - 31)
        { x: 0.717, y: 0.385 }, { x: 0.730, y: 0.367 }, { x: 0.724, y: 0.348 },
        { x: 0.705, y: 0.342 }, { x: 0.686, y: 0.354 }, { x: 0.668, y: 0.367 },
        // Upper Back & Wing Tip (32 - 39)
        { x: 0.649, y: 0.348 }, { x: 0.637, y: 0.323 }, { x: 0.643, y: 0.292 },
        { x: 0.655, y: 0.267 }, { x: 0.637, y: 0.261 }, { x: 0.612, y: 0.280 },
        { x: 0.593, y: 0.305 }, { x: 0.575, y: 0.323 },
        // Dragon Horns & Crest (40 - 49)
        { x: 0.556, y: 0.298 }, { x: 0.537, y: 0.280 }, { x: 0.525, y: 0.255 },
        { x: 0.519, y: 0.230 }, { x: 0.512, y: 0.205 }, { x: 0.500, y: 0.187 },
        { x: 0.488, y: 0.199 }, { x: 0.481, y: 0.218 }, { x: 0.475, y: 0.236 }, { x: 0.469, y: 0.230 }
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
// DRAWING ROUTINES: Authentic runDisney 10K Race Bib (#1952) with Chip & Dale
// ============================================================================

// Chip Character Face (Left flank: chocolate chip nose, single center tooth, red headband)
function drawChipFace(cx, centerX, centerY, size) {
    cx.save();
    cx.translate(centerX, centerY);
    const s = size / 50;
    cx.scale(s, s);

    // 1. Ears
    cx.fillStyle = '#6b3410';
    cx.beginPath();
    cx.arc(-14, -18, 9, 0, Math.PI * 2);
    cx.arc(14, -18, 9, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = '#f472b6';
    cx.beginPath();
    cx.arc(-14, -18, 5, 0, Math.PI * 2);
    cx.arc(14, -18, 5, 0, Math.PI * 2);
    cx.fill();

    // 2. Head Base (Dark Chocolate Brown)
    cx.fillStyle = '#78350f';
    cx.beginPath();
    cx.ellipse(0, 0, 20, 18, 0, 0, Math.PI * 2);
    cx.fill();

    // Cheek puffs
    cx.beginPath();
    cx.arc(-13, 6, 10, 0, Math.PI * 2);
    cx.arc(13, 6, 10, 0, Math.PI * 2);
    cx.fill();

    // 3. Cream muzzle / cheeks
    cx.fillStyle = '#fef3c7';
    cx.beginPath();
    cx.ellipse(0, 7, 14, 10, 0, 0, Math.PI * 2);
    cx.fill();
    cx.beginPath();
    cx.arc(-9, 7, 8, 0, Math.PI * 2);
    cx.arc(9, 7, 8, 0, Math.PI * 2);
    cx.fill();

    // 4. Eyes (Dark oval with highlight)
    cx.fillStyle = '#1e1b4b';
    cx.beginPath();
    cx.ellipse(-7, -4, 4, 6, -0.1, 0, Math.PI * 2);
    cx.ellipse(7, -4, 4, 6, 0.1, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = '#ffffff';
    cx.beginPath();
    cx.arc(-8, -6, 1.8, 0, Math.PI * 2);
    cx.arc(6, -6, 1.8, 0, Math.PI * 2);
    cx.fill();

    // 5. Signature "Chocolate Chip" Nose (Small, Black, Shiny)
    cx.fillStyle = '#0f172a';
    cx.beginPath();
    cx.ellipse(0, 3, 4.5, 3.2, 0, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = '#ffffff';
    cx.beginPath();
    cx.arc(-1.2, 2.0, 1.2, 0, Math.PI * 2);
    cx.fill();

    // 6. Smile & Chip's Single Center Buck Tooth
    cx.strokeStyle = '#451a03';
    cx.lineWidth = 1.6;
    cx.beginPath();
    cx.arc(0, 7, 7, 0.15 * Math.PI, 0.85 * Math.PI);
    cx.stroke();

    // Single centered front tooth
    cx.fillStyle = '#ffffff';
    cx.strokeStyle = '#78350f';
    cx.lineWidth = 0.8;
    cx.fillRect(-2, 10.5, 4, 4);
    cx.strokeRect(-2, 10.5, 4, 4);

    // 7. Red Runner's Headband
    cx.fillStyle = '#ef4444';
    cx.beginPath();
    if (cx.roundRect) {
        cx.roundRect(-17, -13, 34, 5, 2.5);
    } else {
        cx.rect(-17, -13, 34, 5);
    }
    cx.fill();
    cx.fillStyle = '#ffffff';
    cx.fillRect(-17, -11.5, 34, 1.5);

    cx.restore();
}

// Dale Character Face (Right flank: big red nose, two separated teeth, messy hair, blue headband)
function drawDaleFace(cx, centerX, centerY, size) {
    cx.save();
    cx.translate(centerX, centerY);
    const s = size / 50;
    cx.scale(s, s);

    // 1. Ears
    cx.fillStyle = '#9a3412';
    cx.beginPath();
    cx.arc(-14, -18, 9, 0, Math.PI * 2);
    cx.arc(14, -18, 9, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = '#f472b6';
    cx.beginPath();
    cx.arc(-14, -18, 5, 0, Math.PI * 2);
    cx.arc(14, -18, 5, 0, Math.PI * 2);
    cx.fill();

    // 2. Head Base (Lighter Reddish/Golden Brown)
    cx.fillStyle = '#c2410c';
    cx.beginPath();
    cx.ellipse(0, 0, 20, 18, 0, 0, Math.PI * 2);
    cx.fill();

    // Cheek puffs
    cx.beginPath();
    cx.arc(-13, 6, 10, 0, Math.PI * 2);
    cx.arc(13, 6, 10, 0, Math.PI * 2);
    cx.fill();

    // 3. Dale's signature messy red hair tuft on top!
    cx.fillStyle = '#9a3412';
    cx.beginPath();
    cx.moveTo(-5, -17);
    cx.quadraticCurveTo(-7, -26, -2, -24);
    cx.quadraticCurveTo(0, -28, 4, -23);
    cx.quadraticCurveTo(6, -26, 7, -17);
    cx.closePath();
    cx.fill();

    // 4. Cream muzzle / cheeks
    cx.fillStyle = '#fef3c7';
    cx.beginPath();
    cx.ellipse(0, 7, 14, 10, 0, 0, Math.PI * 2);
    cx.fill();
    cx.beginPath();
    cx.arc(-9, 7, 8, 0, Math.PI * 2);
    cx.arc(9, 7, 8, 0, Math.PI * 2);
    cx.fill();

    // 5. Playful eyes (Left open, Right cheeky wink)
    cx.fillStyle = '#1e1b4b';
    cx.beginPath();
    cx.ellipse(-7, -4, 4, 6, -0.1, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = '#ffffff';
    cx.beginPath();
    cx.arc(-8, -6, 1.8, 0, Math.PI * 2);
    cx.fill();

    // Right eye wink
    cx.strokeStyle = '#1e1b4b';
    cx.lineWidth = 2.2;
    cx.beginPath();
    cx.arc(7, -3, 4.5, 1.1 * Math.PI, 1.9 * Math.PI);
    cx.stroke();

    // 6. Dale's signature BIG RED NOSE (Oval, Bright Red, Glossy)
    cx.fillStyle = '#dc2626';
    cx.beginPath();
    cx.ellipse(0, 2.5, 7.5, 5.5, 0, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = '#fca5a5';
    cx.beginPath();
    cx.arc(-2.5, 1.0, 2.0, 0, Math.PI * 2);
    cx.fill();

    // 7. Wide Goofy Smile & TWO SEPARATED Buck Teeth
    cx.strokeStyle = '#7c2d12';
    cx.lineWidth = 1.6;
    cx.beginPath();
    cx.arc(0, 7, 8, 0.12 * Math.PI, 0.88 * Math.PI);
    cx.stroke();

    // Two separated buck teeth
    cx.fillStyle = '#ffffff';
    cx.strokeStyle = '#9a3412';
    cx.lineWidth = 0.8;
    cx.fillRect(-5.5, 11, 3.5, 4);
    cx.strokeRect(-5.5, 11, 3.5, 4);
    cx.fillRect(2.0, 11, 3.5, 4);
    cx.strokeRect(2.0, 11, 3.5, 4);

    // 8. Royal Blue Runner's Headband
    cx.fillStyle = '#2563eb';
    cx.beginPath();
    if (cx.roundRect) {
        cx.roundRect(-17, -13, 34, 5, 2.5);
    } else {
        cx.rect(-17, -13, 34, 5);
    }
    cx.fill();
    cx.fillStyle = '#facc15';
    cx.fillRect(-17, -11.5, 34, 1.5);

    cx.restore();
}

// Little Acorn Accent
function drawAcorn(cx, x, y, size) {
    cx.save();
    cx.translate(x, y);
    const s = size / 20;
    cx.scale(s, s);

    // Cap
    cx.fillStyle = '#78350f';
    cx.beginPath();
    cx.arc(0, -2, 7, Math.PI, 0);
    cx.fill();
    // Stem
    cx.strokeStyle = '#451a03';
    cx.lineWidth = 1.8;
    cx.beginPath();
    cx.moveTo(0, -7);
    cx.quadraticCurveTo(2, -11, 4, -10);
    cx.stroke();

    // Body
    cx.fillStyle = '#d97706';
    cx.beginPath();
    cx.moveTo(-6, -2);
    cx.quadraticCurveTo(-6, 7, 0, 11);
    cx.quadraticCurveTo(6, 7, 6, -2);
    cx.closePath();
    cx.fill();

    // Highlight
    cx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    cx.beginPath();
    cx.ellipse(-2, 2, 1.5, 4, -0.3, 0, Math.PI * 2);
    cx.fill();

    cx.restore();
}

function drawRaceBib(cx, s) {
    if (!params.showBib) return;

    cx.save();

    // Authentic runDisney bib dimensions: ~7.5" wide by 8.0" tall
    // Scaled realistically onto athletic running shirt with user scale multiplier
    const scale = (params.bibScale !== undefined ? params.bibScale : 1.0);
    const baseBibW = s.width * 0.375;
    const bibW = baseBibW * scale;
    const bibH = bibW * (8.0 / 7.5); // ~ 1.067 aspect ratio
    const bibX = s.x + (s.width - bibW) / 2;
    const bibY = s.y + s.height * (params.bibYOffset !== undefined ? params.bibYOffset : 0.57);

    // 1. Tyvek Drop Shadow
    cx.shadowColor = 'rgba(0, 0, 0, 0.65)';
    cx.shadowBlur = 14;
    cx.shadowOffsetX = 0;
    cx.shadowOffsetY = 4;

    // 2. Bright Sunshine Yellow Tyvek Card Body with Rounded Corners
    const r = Math.max(4, bibW * 0.028);
    cx.beginPath();
    cx.moveTo(bibX + r, bibY);
    cx.lineTo(bibX + bibW - r, bibY);
    cx.quadraticCurveTo(bibX + bibW, bibY, bibX + bibW, bibY + r);
    cx.lineTo(bibX + bibW, bibY + bibH - r);
    cx.quadraticCurveTo(bibX + bibW, bibY + bibH, bibX + bibW - r, bibY + bibH);
    cx.lineTo(bibX + r, bibY + bibH);
    cx.quadraticCurveTo(bibX, bibY + bibH, bibX, bibY + bibH - r);
    cx.lineTo(bibX, bibY + r);
    cx.quadraticCurveTo(bibX, bibY, bibX + r, bibY);
    cx.closePath();

    // Mostly Yellow Gradient: Lemon Sunshine to Deep Disney Gold
    const tyvekGrad = cx.createLinearGradient(bibX, bibY, bibX, bibY + bibH);
    tyvekGrad.addColorStop(0, '#fef9c3');    // Sunny lemon top
    tyvekGrad.addColorStop(0.35, '#fef08a'); // Warm vibrant sunshine yellow
    tyvekGrad.addColorStop(0.75, '#fde047'); // Rich race yellow
    tyvekGrad.addColorStop(1, '#facc15');    // Golden sunshine yellow
    cx.fillStyle = tyvekGrad;
    cx.fill();

    // Reset shadow for crisp internal graphics
    cx.shadowColor = 'transparent';
    cx.shadowBlur = 0;
    cx.shadowOffsetY = 0;

    // Golden Card Border
    cx.strokeStyle = '#ca8a04';
    cx.lineWidth = 1.8;
    cx.stroke();

    // Background Graphic Accents: Diagonal Runner Speed Stripes & Radiance
    cx.save();
    cx.clip();

    // Subtle yellow speed chevrons across background
    cx.fillStyle = 'rgba(234, 179, 8, 0.16)';
    for (let stripe = -bibH; stripe < bibW + bibH; stripe += bibW * 0.12) {
        cx.beginPath();
        cx.moveTo(bibX + stripe, bibY);
        cx.lineTo(bibX + stripe + bibW * 0.05, bibY);
        cx.lineTo(bibX + stripe + bibW * 0.05 - bibH * 0.35, bibY + bibH);
        cx.lineTo(bibX + stripe - bibH * 0.35, bibY + bibH);
        cx.closePath();
        cx.fill();
    }

    // Side racing accent stripes (Disney Red & Blue trim)
    const stripeW = Math.max(3, bibW * 0.018);
    cx.fillStyle = '#ef4444'; // Red
    cx.fillRect(bibX, bibY, stripeW, bibH);
    cx.fillStyle = '#1e40af'; // Blue
    cx.fillRect(bibX + stripeW, bibY, stripeW, bibH);

    cx.fillStyle = '#ef4444';
    cx.fillRect(bibX + bibW - stripeW, bibY, stripeW, bibH);
    cx.fillStyle = '#1e40af';
    cx.fillRect(bibX + bibW - stripeW * 2, bibY, stripeW, bibH);

    // Center radial athletic highlight behind bib number
    const centerGrad = cx.createRadialGradient(
        bibX + bibW / 2, bibY + bibH * 0.58, 5,
        bibX + bibW / 2, bibY + bibH * 0.58, bibW * 0.45
    );
    centerGrad.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
    centerGrad.addColorStop(0.6, 'rgba(254, 240, 138, 0.30)');
    centerGrad.addColorStop(1, 'rgba(254, 240, 138, 0)');
    cx.fillStyle = centerGrad;
    cx.fillRect(bibX, bibY + bibH * 0.30, bibW, bibH * 0.50);

    cx.restore();

    // 3. Top Header Banner: Royal Disney Navy/Purple Gradient with Gold Trim
    const headerH = bibH * 0.23;
    cx.save();
    cx.beginPath();
    cx.moveTo(bibX + r, bibY);
    cx.lineTo(bibX + bibW - r, bibY);
    cx.quadraticCurveTo(bibX + bibW, bibY, bibX + bibW, bibY + r);
    cx.lineTo(bibX + bibW, bibY + headerH);
    cx.lineTo(bibX, bibY + headerH);
    cx.lineTo(bibX, bibY + r);
    cx.quadraticCurveTo(bibX, bibY, bibX + r, bibY);
    cx.closePath();
    cx.clip();

    const bannerGrad = cx.createLinearGradient(bibX, bibY, bibX + bibW, bibY + headerH);
    bannerGrad.addColorStop(0, '#1e1b4b'); // Deep Royal Navy
    bannerGrad.addColorStop(0.5, '#312e81');
    bannerGrad.addColorStop(1, '#1e1b4b');
    cx.fillStyle = bannerGrad;
    cx.fill();

    // Gold ribbon bottom accent on header
    cx.fillStyle = '#f59e0b';
    cx.fillRect(bibX, bibY + headerH - 2.5, bibW, 2.5);

    // Header Stars & Text
    cx.fillStyle = '#facc15'; // Gold Star
    cx.font = `bold ${Math.max(8, Math.floor(bibW * 0.052))}px sans-serif`;
    cx.textAlign = 'left';
    cx.fillText("★ runDisney", bibX + bibW * 0.06, bibY + headerH * 0.36);

    cx.fillStyle = '#ffffff';
    cx.font = `bold ${Math.max(8, Math.floor(bibW * 0.060))}px sans-serif`;
    cx.fillText("WALT DISNEY WORLD® 10K", bibX + bibW * 0.06, bibY + headerH * 0.68);

    // Official Sub-Title Ribbon
    cx.fillStyle = '#fef08a';
    cx.font = `900 ${Math.max(7, Math.floor(bibW * 0.040))}px sans-serif`;
    cx.fillText("CHIP 'N' DALE 10K", bibX + bibW * 0.06, bibY + headerH * 0.92);

    // Top-Right Corral Badge: "CORRAL A"
    const badgeW = bibW * 0.22;
    const badgeH = headerH * 0.72;
    const badgeX = bibX + bibW - badgeW - bibW * 0.04;
    const badgeY = bibY + (headerH - badgeH) / 2;

    cx.fillStyle = '#0284c7'; // Cyan Corral box
    cx.beginPath();
    if (cx.roundRect) {
        cx.roundRect(badgeX, badgeY, badgeW, badgeH, 4);
    } else {
        cx.rect(badgeX, badgeY, badgeW, badgeH);
    }
    cx.fill();
    cx.strokeStyle = '#ffffff';
    cx.lineWidth = 1;
    cx.stroke();

    cx.fillStyle = '#ffffff';
    cx.textAlign = 'center';
    cx.font = `bold ${Math.max(6, Math.floor(badgeH * 0.32))}px sans-serif`;
    cx.fillText("CORRAL", badgeX + badgeW / 2, badgeY + badgeH * 0.38);
    cx.font = `bold ${Math.max(12, Math.floor(badgeH * 0.58))}px sans-serif`;
    cx.fillText("A", badgeX + badgeW / 2, badgeY + badgeH * 0.88);
    cx.restore();

    // 4. CHIP & DALE CHARACTER GRAPHICS (Flanking the Number)
    const charSize = bibW * 0.22;
    const charY = bibY + bibH * 0.52;

    // Draw Chip on Left Flank
    drawChipFace(cx, bibX + bibW * 0.16, charY, charSize);
    cx.fillStyle = '#78350f';
    cx.textAlign = 'center';
    cx.font = `900 ${Math.max(7, Math.floor(bibW * 0.042))}px sans-serif`;
    cx.fillText("CHIP", bibX + bibW * 0.16, charY + charSize * 0.52);

    // Draw Dale on Right Flank
    drawDaleFace(cx, bibX + bibW * 0.84, charY, charSize);
    cx.fillStyle = '#c2410c';
    cx.textAlign = 'center';
    cx.font = `900 ${Math.max(7, Math.floor(bibW * 0.042))}px sans-serif`;
    cx.fillText("DALE", bibX + bibW * 0.84, charY + charSize * 0.52);

    // 5. Center Bib Number: "1952" with Crisp White Edge
    const numX = bibX + bibW / 2;
    const numY = bibY + bibH * 0.59;
    cx.font = `900 ${Math.max(22, Math.floor(bibW * 0.25))}px Impact, "Arial Black", sans-serif`;
    cx.textAlign = 'center';

    // White outline for athletic pop on yellow card
    cx.strokeStyle = '#ffffff';
    cx.lineWidth = Math.max(3, bibW * 0.024);
    cx.lineJoin = 'round';
    cx.strokeText("1952", numX, numY);

    // Dark Athletic Slate fill
    cx.fillStyle = '#0f172a';
    cx.fillText("1952", numX, numY);

    // Runner Name under number flanked by Acorns
    const subY = bibY + bibH * 0.70;
    cx.fillStyle = '#78350f';
    cx.font = `bold ${Math.max(8, Math.floor(bibW * 0.052))}px sans-serif`;
    cx.fillText("MSEP RUNNER", numX, subY);

    // Acorns flanking MSEP RUNNER
    const acornSize = Math.max(8, bibW * 0.055);
    drawAcorn(cx, numX - bibW * 0.20, subY - bibH * 0.015, acornSize);
    drawAcorn(cx, numX + bibW * 0.20, subY - bibH * 0.015, acornSize);

    // 6. Bottom Section: PhotoPass Barcode & Verification
    const footerY = bibY + bibH * 0.78;

    // Dual racing stripe divider
    cx.fillStyle = '#ef4444';
    cx.fillRect(bibX + bibW * 0.05, footerY, bibW * 0.90, 1.5);
    cx.fillStyle = '#1e40af';
    cx.fillRect(bibX + bibW * 0.05, footerY + 2.5, bibW * 0.90, 1.5);

    // White Tyvek Barcode Window
    const barStartY = footerY + bibH * 0.04;
    const barH = bibH * 0.09;
    const barX0 = bibX + bibW * 0.07;
    const barW = bibW * 0.40;

    cx.fillStyle = '#ffffff';
    cx.fillRect(barX0 - 4, barStartY - 2, barW + 8, barH + 4);
    cx.strokeStyle = '#e2e8f0';
    cx.lineWidth = 0.8;
    cx.strokeRect(barX0 - 4, barStartY - 2, barW + 8, barH + 4);

    // Barcode lines
    cx.fillStyle = '#0f172a';
    for (let b = 0; b < 22; b++) {
        const bw = (b % 3 === 0 || b % 5 === 0) ? 2.5 : 1.2;
        cx.fillRect(barX0 + b * (bibW * 0.017), barStartY, bw, barH);
    }

    // PhotoPass code & text
    cx.fillStyle = '#64748b';
    cx.textAlign = 'right';
    cx.font = `bold ${Math.max(6, Math.floor(bibW * 0.038))}px sans-serif`;
    cx.fillText("Disney PhotoPass®", bibX + bibW * 0.93, barStartY + barH * 0.45);
    cx.font = `bold ${Math.max(6, Math.floor(bibW * 0.036))}px monospace`;
    cx.fillStyle = '#1e293b';
    cx.fillText("DIS-1952-10K", bibX + bibW * 0.93, barStartY + barH * 0.90);

    // 7. FOUR CORNER BIBBOARDS SNAP FASTENERS
    const boardRadius = Math.max(5, bibW * 0.040);
    const cornerInset = boardRadius + 4;
    const corners = [
        { x: bibX + cornerInset, y: bibY + cornerInset },             // Top-Left
        { x: bibX + bibW - cornerInset, y: bibY + cornerInset },      // Top-Right
        { x: bibX + cornerInset, y: bibY + bibH - cornerInset },      // Bottom-Left
        { x: bibX + bibW - cornerInset, y: bibY + bibH - cornerInset }// Bottom-Right
    ];

    corners.forEach((c) => {
        // Outer dark casing
        cx.beginPath();
        cx.arc(c.x, c.y, boardRadius, 0, Math.PI * 2);
        cx.fillStyle = '#0f172a';
        cx.fill();
        // Cyan accent ring
        cx.strokeStyle = '#38bdf8';
        cx.lineWidth = Math.max(1.2, boardRadius * 0.22);
        cx.stroke();

        // Inner dome button
        cx.beginPath();
        cx.arc(c.x, c.y, boardRadius * 0.55, 0, Math.PI * 2);
        cx.fillStyle = '#38bdf8';
        cx.fill();

        // Center glossy highlight
        cx.beginPath();
        cx.arc(c.x, c.y, boardRadius * 0.22, 0, Math.PI * 2);
        cx.fillStyle = '#ffffff';
        cx.fill();
    });

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
// LIGHTING ENGINE (Modular Multi-Layer Pattern & Group Evaluator)
// ============================================================================

function evalGroupEffect(grp, effect, bpm, dir, grpIndex, grpSize, timeMs, c) {
    const grpBeatMs = 60000 / Math.max(20, bpm || 120);
    const grpNormTime = timeMs / grpBeatMs;
    const direction = dir || 1;

    let baseR = c ? c.r : 255;
    let baseG = c ? c.g : 200;
    let baseB = c ? c.b : 50;

    if (grp.colorMode === 'custom' && grp.customColor) {
        baseR = grp.customColor.r;
        baseG = grp.customColor.g;
        baseB = grp.customColor.b;
    }

    let grpIntensity = 1.0;

    switch (effect) {
        case 'off': {
            return { r: 0, g: 0, b: 0, alpha: 0 };
        }
        case 'chase': {
            const head = ((grpNormTime * direction) % grpSize + grpSize) % grpSize;
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
                grpIntensity = 0.14;
            }
            break;
        }
        case 'flash_slow': {
            const phase = (timeMs % (grpBeatMs * 2)) / (grpBeatMs * 2);
            grpIntensity = phase < 0.5 ? 1.0 : 0.08;
            break;
        }
        case 'pulse': {
            const sine = Math.sin(grpNormTime * Math.PI * 2) * 0.5 + 0.5;
            grpIntensity = 0.18 + 0.82 * sine;
            break;
        }
        case 'write_on_off': {
            const totalCycleMs = grpBeatMs * 4;
            const progress = (timeMs % totalCycleMs) / totalCycleMs;
            if (progress < 0.40) {
                const litHead = (progress / 0.40) * grpSize;
                grpIntensity = (direction >= 0 ? (grpIndex <= litHead) : ((grpSize - 1 - grpIndex) <= litHead)) ? 1.0 : 0.05;
            } else if (progress < 0.58) {
                grpIntensity = 1.0;
            } else if (progress < 0.88) {
                const offHead = ((progress - 0.58) / 0.30) * grpSize;
                grpIntensity = (direction >= 0 ? (grpIndex <= offHead) : ((grpSize - 1 - grpIndex) <= offHead)) ? 0.05 : 1.0;
            } else {
                grpIntensity = 0.05;
            }
            break;
        }
        case 'sparkle_storm': {
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
            const step = Math.floor(grpNormTime * 2 * direction) % 3;
            const posInStep = ((grpIndex + step) % 3 + 3) % 3;
            grpIntensity = posInStep === 0 ? 1.0 : 0.12;
            break;
        }
        case 'rainbow_cycle': {
            const hue = ((timeMs * 0.08 * direction + grpIndex * (360 / grpSize)) % 360 + 360) % 360;
            const rgb = hslToRgb(hue / 360, 0.95, 0.52);
            baseR = rgb.r; baseG = rgb.g; baseB = rgb.b;
            grpIntensity = 1.0;
            break;
        }
        case 'fireworks': {
            const ledsPerRay = Math.max(2, grp.fireworkLedsPerRay || (
                (grpSize % 5 === 0) ? (grpSize / 5) :
                (grpSize % 4 === 0) ? (grpSize / 4) :
                (grpSize % 6 === 0) ? (grpSize / 6) :
                (grpSize % 3 === 0) ? (grpSize / 3) : 4
            ));
            const rays = Math.max(1, Math.round(grpSize / ledsPerRay));
            const rayIdx = Math.floor(grpIndex / ledsPerRay);
            const posInRay = grpIndex % ledsPerRay;

            // Serpentine wiring:
            // Even rays (0, 2, 4): center -> tip (step 0 to ledsPerRay - 1)
            // Odd rays (1, 3, 5): tip -> center (step ledsPerRay - 1 down to 0)
            const isSerp = grp.wiringMode !== 'spoke';
            const step = (isSerp && (rayIdx % 2 === 1)) ? (ledsPerRay - 1 - posInRay) : posInRay;

            // Cycle timing based on BPM (faster BPM = more frequent bursts)
            const cycleMs = grpBeatMs * 3.0; // e.g. 1500ms at 120 BPM
            const tau = (timeMs % cycleMs) / cycleMs; // 0.0 to 1.0

            // All rays of a firework group share the exact same uniform color
            let fwR = 255, fwG = 195, fwB = 45; // Golden Amber signature default
            if (grp.fireworkColor && grp.fireworkColor !== 'rainbow') {
                const cRgb = hexToRgb(grp.fireworkColor);
                if (cRgb) { fwR = cRgb.r; fwG = cRgb.g; fwB = cRgb.b; }
            } else if (grp.customColor) {
                fwR = grp.customColor.r; fwG = grp.customColor.g; fwB = grp.customColor.b;
            } else if (grp.colorMode === 'custom' && grp.customColor) {
                fwR = grp.customColor.r; fwG = grp.customColor.g; fwB = grp.customColor.b;
            }
            baseR = fwR;
            baseG = fwG;
            baseB = fwB;

            if (tau < 0.12) {
                // Phase 1: Center ignition flash
                if (step === 0) {
                    const igniteProg = tau / 0.12;
                    grpIntensity = Math.sin(igniteProg * Math.PI);
                    baseR = 255;
                    baseG = Math.min(255, baseG + 160);
                    baseB = Math.min(255, baseB + 180);
                } else {
                    grpIntensity = 0.0; // Completely off until ignited
                }
            } else if (tau < 0.70) {
                // Phase 2: Outward Trail Growth (Wavefront expands from center to tips)
                const expandProg = (tau - 0.12) / 0.58; // 0.0 to 1.0
                const waveHead = expandProg * (ledsPerRay - 1);
                const delta = waveHead - step;

                if (delta >= -0.25) {
                    const headDist = Math.abs(delta);
                    if (headDist < 0.75) {
                        // Bright leading spark head
                        grpIntensity = 1.0;
                        baseR = Math.min(255, baseR + 90);
                        baseG = Math.min(255, baseG + 90);
                        baseB = Math.min(255, baseB + 90);
                    } else if (delta > 0) {
                        // Trailing line growing behind the head
                        const trailDecay = Math.exp(-0.85 * (delta - 0.5));
                        // LEAVE CENTERMOST LEDS ON to create a continuous radiating trail!
                        if (step === 0) {
                            grpIntensity = Math.max(0.68, trailDecay);
                            baseR = Math.min(255, baseR + 35);
                            baseG = Math.min(255, Math.round(baseG * 0.95 + 35));
                        } else {
                            grpIntensity = Math.max(0.20, trailDecay);
                            // Warm ember shift in trailing line
                            baseR = Math.min(255, Math.round(baseR * 1.08));
                            baseG = Math.round(baseG * 0.85);
                            baseB = Math.round(baseB * 0.65);
                        }
                    } else {
                        grpIntensity = 0.0;
                    }
                } else {
                    grpIntensity = 0.0; // Ahead of expanding wavefront: completely off
                }
            } else if (tau < 0.88) {
                // Phase 3: Outer Starburst Twinkle & Crackle at Tips
                const tipProg = (tau - 0.70) / 0.18; // 0.0 to 1.0
                if (step >= ledsPerRay - 2) {
                    const crackle = Math.sin(timeMs * 0.09 + grpIndex * 37.3) > 0.15;
                    if (crackle) {
                        grpIntensity = Math.max(0.25, (1.0 - tipProg * 0.65));
                        baseR = 255;
                        baseG = 250;
                        baseB = 220; // Starlight white sparkle
                    } else {
                        grpIntensity = 0.0;
                    }
                } else if (step === 0) {
                    // LEAVE CENTERMOST LEDS ON as persistent trailing anchor while tips crackle
                    grpIntensity = Math.max(0.35, 0.58 * (1.0 - tipProg));
                    baseR = Math.min(255, baseR + 30);
                    baseG = Math.min(255, Math.round(baseG * 0.9));
                } else {
                    grpIntensity = 0.0; // Burned out inner trail: completely off
                }
            } else {
                // Phase 4: Rest / Burst ended - baseline completely unlit / off
                grpIntensity = 0.0;
            }
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

function evalGlobalPattern(pattern, bpm, index, totalLeds, timeMs, c, hasColor) {
    const beatMs = 60000 / Math.max(20, bpm || params.speedBpm || 120);
    const normTime = timeMs / beatMs;
    const baseH = params.greenHue;

    let r = 0, g = 255, b = 100, brightness = params.brightness / 100;

    switch (pattern) {
        case 'steady_sparkle': {
            if (hasColor) {
                r = c.r; g = c.g; b = c.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
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
        case 'pulse': {
            const breath = 0.35 + 0.65 * (Math.sin(normTime * Math.PI * 2) * 0.5 + 0.5);
            if (hasColor) {
                r = Math.floor(c.r * breath);
                g = Math.floor(c.g * breath);
                b = Math.floor(c.b * breath);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * breath);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            break;
        }
        case 'chase': {
            const head = (normTime * 2) % totalLeds;
            const dist = Math.abs(index - head);
            const fade = Math.max(0, 1 - (dist / 8));
            const intensity = 0.15 + 0.85 * fade;
            if (hasColor) {
                r = Math.floor(c.r * intensity);
                g = Math.floor(c.g * intensity);
                b = Math.floor(c.b * intensity);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * intensity);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            break;
        }
        case 'fireworks': {
            const cycleMs = beatMs * 3.0;
            const tau = (timeMs % cycleMs) / cycleMs;
            const fwGroup = animationGroups.find(g => g.effect === 'fireworks' && g.ledIndices && g.ledIndices.includes(index)) || animationGroups.find(g => g.effect === 'fireworks');
            const ledsPerRay = fwGroup ? (fwGroup.fireworkLedsPerRay || 4) : 4;
            const posInGroup = (fwGroup && fwGroup.ledIndices) ? fwGroup.ledIndices.indexOf(index) : -1;
            const posInRay = (posInGroup >= 0) ? (posInGroup % ledsPerRay) : (index % ledsPerRay);
            const rayIdx = (posInGroup >= 0) ? Math.floor(posInGroup / ledsPerRay) : 0;
            const isSerp = !fwGroup || fwGroup.wiringMode !== 'spoke';
            const step = (isSerp && (rayIdx % 2 === 1)) ? (ledsPerRay - 1 - posInRay) : posInRay;

            // All rays of a firework group share the exact same uniform color
            let fwR = 255, fwG = 195, fwB = 45;
            if (fwGroup && fwGroup.fireworkColor && fwGroup.fireworkColor !== 'rainbow') {
                const cRgb = hexToRgb(fwGroup.fireworkColor);
                if (cRgb) { fwR = cRgb.r; fwG = cRgb.g; fwB = cRgb.b; }
            } else if (fwGroup && fwGroup.customColor) {
                fwR = fwGroup.customColor.r; fwG = fwGroup.customColor.g; fwB = fwGroup.customColor.b;
            }

            if (tau < 0.12) {
                if (step === 0) {
                    r = 255; g = 250; b = 200;
                    brightness = Math.sin((tau / 0.12) * Math.PI);
                } else {
                    brightness = 0.0;
                }
            } else if (tau < 0.70) {
                const expandProg = (tau - 0.12) / 0.58;
                const waveHead = expandProg * (ledsPerRay - 1);
                const delta = waveHead - step;
                if (delta >= -0.25) {
                    if (Math.abs(delta) < 0.75) {
                        r = 255; g = 230; b = 150;
                        brightness = 1.0;
                    } else if (delta > 0) {
                        const decay = Math.exp(-1.15 * (delta - 0.75));
                        r = 255; g = 140; b = 30;
                        brightness = Math.max(0.20, decay);
                    } else {
                        brightness = 0.0;
                    }
                } else {
                    brightness = 0.0;
                }
            } else if (tau < 0.88) {
                if (step >= ledsPerRay - 2) {
                    const crackle = Math.sin(timeMs * 0.09 + index * 37.3) > 0.15;
                    r = 255; g = 255; b = 240;
                    brightness = crackle ? 0.95 : 0.0;
                } else if (step === 0) {
                    r = 255; g = 180; b = 80;
                    brightness = 0.40;
                } else {
                    brightness = 0.0;
                }
            } else {
                brightness = 0.0;
            }
            break;
        }
        default: {
            if (hasColor) {
                r = c.r; g = c.g; b = c.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            break;
        }
    }

    if (sparkles[index] > 0) {
        sparkles[index] = Math.max(0, sparkles[index] - 0.04);
    }
    if ((pattern === 'steady_sparkle' || pattern === 'dragon_sparkle' || pattern === 'color_match') && Math.random() * 1000 < params.sparkleRate) {
        sparkles[index] = 1.0;
    }

    return {
        r: Math.floor(r * brightness),
        g: Math.floor(g * brightness),
        b: Math.floor(b * brightness),
        alpha: brightness
    };
}

function computeLedColor(index, totalLeds, timeMs) {
    const hasColor = (leds[index] && leds[index].color);
    const c = hasColor ? leds[index].color : null;
    const grpEntry = ledGroupMap[index];

    // ========================================================================
    // MODE A: SHOW SEQUENCE PLAYBACK (Parade Cue Director)
    // ========================================================================
    if (sequenceMode) {
        const t = sequenceTime;

        // 1. Evaluate Active Global Cues
        const activeGlobalCues = sequenceCues.filter(q => q.targetType === 'global' && t >= q.startTime && t < (q.startTime + q.duration));

        let baseColor = null;
        if (activeGlobalCues.length === 0) {
            baseColor = evalGlobalPattern(activePattern, params.speedBpm, index, totalLeds, timeMs, c, hasColor);
        } else if (activeGlobalCues.length === 1) {
            const q = activeGlobalCues[0];
            const col = evalGlobalPattern(q.effect, q.speedBpm, index, totalLeds, timeMs, c, hasColor);
            const w = getCueWeight(q, t);
            if (w < 1.0) {
                const restCol = evalGlobalPattern('steady_sparkle', 120, index, totalLeds, timeMs, c, hasColor);
                baseColor = {
                    r: Math.round(restCol.r * (1 - w) + col.r * w),
                    g: Math.round(restCol.g * (1 - w) + col.g * w),
                    b: Math.round(restCol.b * (1 - w) + col.b * w),
                    alpha: restCol.alpha * (1 - w) + col.alpha * w
                };
            } else {
                baseColor = col;
            }
        } else {
            // Crossfade between overlapping active global cues
            let totalW = 0;
            const weights = activeGlobalCues.map(q => {
                const w = getCueWeight(q, t);
                totalW += w;
                return w;
            });
            let blR = 0, blG = 0, blB = 0, blA = 0;
            for (let i = 0; i < activeGlobalCues.length; i++) {
                const q = activeGlobalCues[i];
                const col = evalGlobalPattern(q.effect, q.speedBpm, index, totalLeds, timeMs, c, hasColor);
                const normW = totalW > 0 ? (weights[i] / totalW) : (1 / activeGlobalCues.length);
                blR += col.r * normW;
                blG += col.g * normW;
                blB += col.b * normW;
                blA += col.alpha * normW;
            }
            baseColor = { r: Math.round(blR), g: Math.round(blG), b: Math.round(blB), alpha: blA };
        }

        // 2. Evaluate Active Group Cue Overrides (Scenario B: Multi-Layer)
        if (grpEntry && grpEntry.group) {
            const grp = grpEntry.group;
            const grpId = grp.id;
            const isFirework = grp.effect === 'fireworks' || (grp.id && grp.id.includes('fireworks'));
            const activeGrpCue = sequenceCues.find(q => q.targetType === 'group' && (q.groupId === grpId || q.groupName === grp.name) && t >= q.startTime && t < (q.startTime + q.duration));

            // Determine this group's resting baseline effect
            // Default: 'inherit' (follows overall global baseline) for standard groups; 'off' for fireworks
            const groupBaseline = grp.baselineEffect || (isFirework ? 'off' : 'inherit');

            // Evaluate the group's resting baseline color (when idle / outside active cues)
            let grpBaselineCol;
            if (groupBaseline === 'off') {
                grpBaselineCol = { r: 0, g: 0, b: 0, alpha: 0 };
            } else if (groupBaseline === 'steady_sparkle') {
                grpBaselineCol = evalGlobalPattern('steady_sparkle', 120, index, totalLeds, timeMs, c, hasColor);
            } else if (groupBaseline === 'dim_glow') {
                const baseR = (grp.customColor && grp.colorMode === 'custom') ? grp.customColor.r : (c ? c.r : 255);
                const baseG = (grp.customColor && grp.colorMode === 'custom') ? grp.customColor.g : (c ? c.g : 200);
                const baseB = (grp.customColor && grp.colorMode === 'custom') ? grp.customColor.b : (c ? c.b : 50);
                grpBaselineCol = { r: Math.round(baseR * 0.22), g: Math.round(baseG * 0.22), b: Math.round(baseB * 0.22), alpha: 0.35 };
            } else if (groupBaseline === 'breathe' || groupBaseline === 'pulse_slow') {
                const sine = Math.sin((timeMs / 1000) * Math.PI) * 0.5 + 0.5; // ~30 BPM gentle breath
                const baseR = (grp.customColor && grp.colorMode === 'custom') ? grp.customColor.r : (c ? c.r : 255);
                const baseG = (grp.customColor && grp.colorMode === 'custom') ? grp.customColor.g : (c ? c.g : 200);
                const baseB = (grp.customColor && grp.colorMode === 'custom') ? grp.customColor.b : (c ? c.b : 50);
                const intensity = 0.08 + 0.32 * sine;
                grpBaselineCol = { r: Math.round(baseR * intensity), g: Math.round(baseG * intensity), b: Math.round(baseB * intensity), alpha: intensity };
            } else {
                // 'inherit' or default: follow overall global baseline
                grpBaselineCol = baseColor;
            }

            if (activeGrpCue) {
                // Synchronize animation phase to cue onset time so cue effects explode/trigger precisely on cue!
                const cueTimeMs = Math.max(0, (t - activeGrpCue.startTime) * 1000);
                const grpCol = evalGroupEffect(grp, activeGrpCue.effect, activeGrpCue.speedBpm, activeGrpCue.direction, grpEntry.indexInGroup, grpEntry.groupSize, cueTimeMs, c);
                const w = getCueWeight(activeGrpCue, t);

                // Blend smoothly from group resting baseline into active cue animation
                return {
                    r: Math.round(grpBaselineCol.r * (1 - w) + grpCol.r * w),
                    g: Math.round(grpBaselineCol.g * (1 - w) + grpCol.g * w),
                    b: Math.round(grpBaselineCol.b * (1 - w) + grpCol.b * w),
                    alpha: grpBaselineCol.alpha * (1 - w) + grpCol.alpha * w
                };
            } else {
                // Return configured resting baseline effect when group is idle!
                return grpBaselineCol;
            }
        }

        return baseColor;
    }

    // ========================================================================
    // MODE B: FREE-RUN PARADE PATTERN
    // ========================================================================
    if (grpEntry && grpEntry.group) {
        const grp = grpEntry.group;
        if (grp.effect === 'off') {
            return { r: 0, g: 0, b: 0, alpha: 0 };
        }
        return evalGroupEffect(grp, grp.effect, grp.speedBpm, grp.direction, grpEntry.indexInGroup, grpEntry.groupSize, timeMs, c);
    }

    return evalGlobalPattern(activePattern, params.speedBpm, index, totalLeds, timeMs, c, hasColor);
}

function renderBulb(cx, x, y, col, isHovered, isSelected, index) {
    const isLit = (col.alpha > 0.01) && (col.r > 2 || col.g > 2 || col.b > 2);

    if (isLit) {
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
    } else {
        // Physical unlit LED bead (completely off)
        cx.beginPath();
        cx.arc(x, y, 3.5, 0, Math.PI * 2);
        cx.fillStyle = 'rgba(22, 26, 33, 0.85)';
        cx.fill();
        cx.strokeStyle = 'rgba(75, 82, 95, 0.45)';
        cx.lineWidth = 1;
        cx.stroke();
    }

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
        const grpEntry = ledGroupMap[index];
        let fwTag = '';
        let isFw = false;
        if (grpEntry && grpEntry.group && grpEntry.group.effect === 'fireworks') {
            isFw = true;
            const ledsPerRay = grpEntry.group.fireworkLedsPerRay || 4;
            const ray = Math.floor(grpEntry.indexInGroup / ledsPerRay) + 1;
            const pos = grpEntry.indexInGroup % ledsPerRay;
            const isSerp = grpEntry.group.wiringMode !== 'spoke';
            const step = (isSerp && ((ray - 1) % 2 === 1)) ? (ledsPerRay - 1 - pos) : pos;
            const role = (step === 0) ? 'CTR' : (step === ledsPerRay - 1 ? 'TIP' : `S${step + 1}`);
            fwTag = `R${ray}:${step + 1}${role === 'CTR' ? '•C' : (role === 'TIP' ? '•T' : '')}`;
        }

        const baseLabel = isSelected ? `#${index}` : index;
        const displayLabel = fwTag ? (isSelected ? `#${index} [${fwTag}]` : `${index} [${fwTag}]`) : baseLabel;

        if (index === 0) {
            cx.fillStyle = '#00ff88';
            cx.font = 'bold 10px monospace';
            cx.fillText(`0 (START)${fwTag ? ' ' + fwTag : ''}`, x + 6, y - 6);
        } else if (index === leds.length - 1) {
            cx.fillStyle = '#ff4d6d';
            cx.font = 'bold 10px monospace';
            cx.fillText(`${index} (END)${fwTag ? ' ' + fwTag : ''}`, x + 6, y - 6);
        } else {
            cx.fillStyle = isSelected ? '#00ffff' : (isFw ? '#ffa657' : '#ffffff');
            cx.font = isSelected ? 'bold 11px monospace' : '9px monospace';
            cx.fillText(displayLabel, x + 6, y - 6);
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
    } else if (currentGraphicType === 'carriage_nohorses') {
        shirtTitle = "FLOAT #5: CARRIAGE (NO HORSES)";
    } else if (currentGraphicType === 'custom_image') {
        shirtTitle = "CUSTOM RUNNER DESIGN";
    }
    drawRunningShirt(ctx, s.x, s.y, s.width, s.height, shirtTitle);
    drawPetesDragon(ctx, s);
    drawRaceBib(ctx, s);

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

    // Render Click-to-Draw Guide Lines & Step Indicators on Canvas
    if (isDrawGroupMode && drawGroupPoints.length > 0) {
        ctx.save();
        if (drawGroupPoints.length > 1) {
            ctx.beginPath();
            const pStart = normToCanvas(drawGroupPoints[0]);
            ctx.moveTo(pStart.x, pStart.y);
            for (let p = 1; p < drawGroupPoints.length; p++) {
                const pt = normToCanvas(drawGroupPoints[p]);
                ctx.lineTo(pt.x, pt.y);
            }
            ctx.strokeStyle = '#ffc107';
            ctx.lineWidth = 2.4;
            ctx.setLineDash([6, 4]);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Draw order badges (1, 2, 3...) at each placed point
        for (let p = 0; p < drawGroupPoints.length; p++) {
            const pt = normToCanvas(drawGroupPoints[p]);

            // Outer glowing gold ring
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 11, 0, Math.PI * 2);
            ctx.fillStyle = '#ffc107';
            ctx.fill();
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Sequence order number
            ctx.fillStyle = '#000';
            ctx.font = 'bold 10px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(String(p + 1), pt.x, pt.y);
        }
        ctx.restore();
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
    { num: "01", name: "The Train", tag: "CASEY JR.", color: "#e63946", accent: "Red" },
    { num: "02", name: "Title Drum", tag: "THE DRUM", color: "#ffb703", accent: "Gold" },
    { num: "03", name: "The Turtle", tag: "TURTLE", color: "#2ec4b6", accent: "Teal" },
    { num: "04", name: "The Snail", tag: "SNAIL", color: "#ff007f", accent: "Pink" },
    { num: "05", name: "Cinderella", tag: "COACH", color: "#48cae4", accent: "Cyan" },
    { num: "06", name: "Pete's Dragon", tag: "ELLIOTT", color: "#00ff88", accent: "Green" },
    { num: "07", name: "Flag & Eagle", tag: "HONOR AMERICA", color: "#3a86ff", accent: "Patriotic" }
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

    const inspectorSection = document.getElementById('ledInspectorSection');

    if (totalSelected === 0) {
        if (inspectorSection) {
            inspectorSection.classList.remove('dock-active');
            inspectorSection.classList.add('dock-empty');
        }
        if (emptyPrompt) emptyPrompt.style.display = 'block';
        if (colorControls) colorControls.style.display = 'none';
        if (stepperRow) stepperRow.style.display = 'none';
        if (multiRow) multiRow.style.display = 'none';
        const groupFwRow = document.getElementById('groupFwRadiusRow');
        if (groupFwRow) groupFwRow.style.display = 'none';
        if (badge) {
            badge.textContent = 'None Selected';
            badge.style.background = '#30363d';
            badge.style.color = '#8b949e';
        }
        if (groupBadge) groupBadge.textContent = '0 LEDs Selected';

        // Populate quick group chips when 0 LEDs selected
        const quickPrompt = document.getElementById('inspectorQuickGroupsPrompt');
        const chipsRow = document.getElementById('inspectorGroupChipsRow');
        if (quickPrompt && chipsRow) {
            if (animationGroups && animationGroups.length > 0) {
                quickPrompt.style.display = 'flex';
                chipsRow.innerHTML = '';
                animationGroups.forEach(g => {
                    const chip = document.createElement('span');
                    chip.className = 'inspector-group-chip';
                    const icon = g.effect === 'fireworks' ? '🎆' : (g.effect === 'chase' ? '🎡' : (g.effect === 'sparkle_storm' ? '✨' : '👥'));
                    chip.innerHTML = `${icon} ${g.name} <span style="opacity:0.65;">(${g.ledIndices.length})</span>`;
                    chip.title = `Click to select all ${g.ledIndices.length} LEDs in "${g.name}"`;
                    chip.addEventListener('click', (e) => {
                        e.stopPropagation();
                        selectGroupLeds(g.id);
                    });
                    chipsRow.appendChild(chip);
                });
            } else {
                quickPrompt.style.display = 'none';
                chipsRow.innerHTML = '';
            }
        }

        // Remove active-group highlights on cards
        document.querySelectorAll('.group-card.active-group').forEach(el => el.classList.remove('active-group'));

        // Update Group Creation Hub in tabGroups
        const selEmpty = document.getElementById('creationSelectEmptyText');
        const selActive = document.getElementById('creationSelectActiveText');
        const saveHubBtn = document.getElementById('saveSelectionGroupBtnHub');
        if (selEmpty) selEmpty.style.display = 'block';
        if (selActive) selActive.style.display = 'none';
        if (saveHubBtn) {
            saveHubBtn.innerHTML = '💾 Save Selection as Group';
            saveHubBtn.style.background = 'linear-gradient(135deg, #238636, #2ea043)';
            saveHubBtn.style.borderColor = '#2ea043';
        }

        return;
    }

    if (inspectorSection) {
        inspectorSection.classList.remove('dock-empty');
        inspectorSection.classList.add('dock-active');
    }
    if (emptyPrompt) emptyPrompt.style.display = 'none';
    const quickPrompt = document.getElementById('inspectorQuickGroupsPrompt');
    if (quickPrompt) quickPrompt.style.display = 'none';
    if (colorControls) colorControls.style.display = 'flex';

    if (totalSelected === 1) {
        if (stepperRow) stepperRow.style.display = 'flex';
        if (multiRow) multiRow.style.display = 'none';
        const grpEntry = ledGroupMap[selectedLed];
        if (badge) {
            if (grpEntry && grpEntry.group && grpEntry.group.effect === 'fireworks') {
                const ledsPerRay = grpEntry.group.fireworkLedsPerRay || 4;
                const rays = grpEntry.group.fireworkRays || Math.round(grpEntry.groupSize / ledsPerRay);
                const ray = Math.floor(grpEntry.indexInGroup / ledsPerRay) + 1;
                const pos = grpEntry.indexInGroup % ledsPerRay;
                const isSerp = grpEntry.group.wiringMode !== 'spoke';
                const step = (isSerp && ((ray - 1) % 2 === 1)) ? (ledsPerRay - 1 - pos) : pos;
                const role = (step === 0) ? 'Center Hub' : (step === ledsPerRay - 1 ? 'Outer Tip' : `Trail Step ${step + 1}`);
                badge.textContent = `LED #${selectedLed} (Ray ${ray}/${rays} • ${role})`;
                badge.style.background = '#ff7b72';
                badge.style.color = '#000';
            } else {
                badge.textContent = `LED #${selectedLed}`;
                badge.style.background = '#ffc107';
                badge.style.color = '#000';
            }
        }
        if (groupBadge) groupBadge.textContent = '1 LED Selected';
        if (numInput) {
            numInput.value = selectedLed;
            numInput.max = Math.max(0, leds.length - 1);
        }

        // If this LED belongs to a group, populate group inputs
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
            const baselineSelect = document.getElementById('groupBaselineSelect');
            if (baselineSelect) baselineSelect.value = grp.baselineEffect || (grp.effect === 'fireworks' ? 'off' : 'inherit');
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

    // Show or hide Fireworks Burst Radius slider in Group Inspector
    const groupFwRow = document.getElementById('groupFwRadiusRow');
    if (groupFwRow) {
        let isFw = false;
        let fwGrp = null;

        if (totalSelected === 1 && selectedLed !== null && ledGroupMap[selectedLed]) {
            if (ledGroupMap[selectedLed].group && ledGroupMap[selectedLed].group.effect === 'fireworks') {
                isFw = true;
                fwGrp = ledGroupMap[selectedLed].group;
            }
        } else if (totalSelected > 1) {
            const firstLed = Array.from(selectedLeds)[0];
            const grpEntry = ledGroupMap[firstLed];
            if (grpEntry && grpEntry.group && grpEntry.group.effect === 'fireworks') {
                isFw = true;
                fwGrp = grpEntry.group;
            } else {
                fwGrp = animationGroups.find(g => g.effect === 'fireworks' && g.ledIndices.some(idx => selectedLeds.has(idx)));
                if (fwGrp) isFw = true;
            }
        }

        if (!isFw) {
            const effectSelect = document.getElementById('groupEffectSelect');
            if (effectSelect && effectSelect.value === 'fireworks') {
                isFw = true;
                fwGrp = typeof getActiveFireworksGroup === 'function' ? getActiveFireworksGroup() : null;
            }
        }

        if (isFw) {
            groupFwRow.style.display = 'block';
            if (fwGrp) {
                activeFireworksGroupId = fwGrp.id;
                const rPct = Math.round((fwGrp.burstRadius || 0.13) * 100);
                const gSlider = document.getElementById('groupFwRadiusSlider');
                const gVal = document.getElementById('groupFwRadiusVal');
                if (gSlider) gSlider.value = rPct;
                if (gVal) gVal.textContent = `${rPct}%`;
                if (typeof highlightRadiusPresetButtons === 'function') {
                    highlightRadiusPresetButtons(rPct);
                }
            }
        } else {
            groupFwRow.style.display = 'none';
        }
    }

    const activeRef = (selectedLed !== null && leds[selectedLed]) ? selectedLed : Array.from(selectedLeds)[0];
    if (activeRef !== undefined && leds[activeRef]) {
        let col = leds[activeRef].color;
        if (!col) {
            col = computeLedColor(activeRef, leds.length, performance.now());
            leds[activeRef].color = { r: col.r, g: col.g, b: col.b };
        }
        updateLedInspectorColorInputs(col.r, col.g, col.b);
    }

    // Dynamic Save vs. Update Button text and styling
    const applyBtn = document.getElementById('applyGroupEffectBtn');
    if (applyBtn) {
        const nameInput = document.getElementById('groupNameInput');
        const rawName = (nameInput?.value || '').trim();
        const existingGrp = (rawName ? animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase()) : null) ||
            (selectedLed !== null && ledGroupMap[selectedLed] ? ledGroupMap[selectedLed].group : null);
        if (existingGrp) {
            applyBtn.innerHTML = `💾 Update Group "${existingGrp.name}"`;
            applyBtn.style.background = 'linear-gradient(135deg, #1f6feb, #388bfd)';
            applyBtn.style.borderColor = '#388bfd';
        } else {
            applyBtn.innerHTML = `💾 Save Selection as Group`;
            applyBtn.style.background = 'linear-gradient(135deg, #238636, #2ea043)';
            applyBtn.style.borderColor = '#2ea043';
        }
    }

    // Update Group Creation Hub (in tabGroups)
    const selEmpty = document.getElementById('creationSelectEmptyText');
    const selActive = document.getElementById('creationSelectActiveText');
    const selCount = document.getElementById('creationSelectCountText');
    const selRange = document.getElementById('creationSelectRangeText');
    const saveHubBtn = document.getElementById('saveSelectionGroupBtnHub');

    if (totalSelected >= 2) {
        if (selEmpty) selEmpty.style.display = 'none';
        if (selActive) selActive.style.display = 'flex';
        if (selCount) selCount.textContent = `✨ ${totalSelected} LEDs Selected`;
        if (selRange) selRange.textContent = `Indices: ${formatIndexSummary(Array.from(selectedLeds))}`;

        const nameInput = document.getElementById('groupNameInput');
        const rawName = (nameInput?.value || '').trim();
        const existingGrp = (rawName ? animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase()) : null) ||
            (selectedLed !== null && ledGroupMap[selectedLed] ? ledGroupMap[selectedLed].group : null);

        if (existingGrp) {
            const hubName = document.getElementById('groupNameInputHub');
            const hubEff = document.getElementById('groupEffectSelectHub');
            const hubSpd = document.getElementById('groupSpeedSliderHub');
            const hubSpdVal = document.getElementById('groupSpeedValHub');
            const hubDir = document.getElementById('groupDirectionSelectHub');
            const hubBase = document.getElementById('groupBaselineSelectHub');

            if (hubName && document.activeElement !== hubName) hubName.value = existingGrp.name;
            if (hubEff) hubEff.value = existingGrp.effect;
            if (hubSpd) hubSpd.value = existingGrp.speedBpm;
            if (hubSpdVal) hubSpdVal.textContent = `${existingGrp.speedBpm} BPM`;
            if (hubDir) hubDir.value = String(existingGrp.direction || 1);
            if (hubBase) hubBase.value = existingGrp.baselineEffect || (existingGrp.effect === 'fireworks' ? 'off' : 'inherit');

            if (saveHubBtn) {
                saveHubBtn.innerHTML = `💾 Update Group "${existingGrp.name}"`;
                saveHubBtn.style.background = 'linear-gradient(135deg, #1f6feb, #388bfd)';
                saveHubBtn.style.borderColor = '#388bfd';
            }
        } else {
            if (saveHubBtn) {
                saveHubBtn.innerHTML = `💾 Save Selection as Group`;
                saveHubBtn.style.background = 'linear-gradient(135deg, #238636, #2ea043)';
                saveHubBtn.style.borderColor = '#2ea043';
            }
        }
    } else {
        if (selEmpty) selEmpty.style.display = 'block';
        if (selActive) selActive.style.display = 'none';
        if (saveHubBtn) {
            saveHubBtn.innerHTML = `💾 Save Selection as Group`;
            saveHubBtn.style.background = 'linear-gradient(135deg, #238636, #2ea043)';
            saveHubBtn.style.borderColor = '#2ea043';
        }
    }
}

// ----------------------------------------------------------------------------
// CLICK-TO-DRAW SEQUENTIAL PATH & GROUP CREATION HUB ENGINE
// ----------------------------------------------------------------------------

function switchGroupCreationMode(mode) {
    const targetMode = mode === 'fireworks' ? 'fw' : mode;

    document.getElementById('creationModeSelectBtn')?.classList.toggle('active', targetMode === 'select');
    document.getElementById('creationModeDrawBtn')?.classList.toggle('active', targetMode === 'draw');
    document.getElementById('creationModeFwBtn')?.classList.toggle('active', targetMode === 'fw');

    const panelSelect = document.getElementById('creationPanelSelect');
    const panelDraw = document.getElementById('creationPanelDraw');
    const panelFw = document.getElementById('creationPanelFw');
    const badge = document.getElementById('creationModeBadge');

    if (panelSelect) panelSelect.style.display = targetMode === 'select' ? 'block' : 'none';
    if (panelDraw) panelDraw.style.display = targetMode === 'draw' ? 'block' : 'none';
    if (panelFw) panelFw.style.display = targetMode === 'fw' ? 'block' : 'none';

    if (badge) {
        if (targetMode === 'select') {
            badge.textContent = 'Selection';
            badge.style.background = '#1f6feb';
        } else if (targetMode === 'draw') {
            badge.textContent = 'Click-to-Draw';
            badge.style.background = '#d29922';
        } else if (targetMode === 'fw') {
            badge.textContent = 'Fireworks';
            badge.style.background = '#ff7b72';
        }
    }
}

function getNextAvailableLedIndex() {
    const totalCostumeLeds = (leds && leds.length > 0) ? leds.length : 100;
    const assignedIndices = new Set();
    animationGroups.forEach(g => (g.ledIndices || []).forEach(idx => assignedIndices.add(idx)));
    drawGroupLedIndices.forEach(idx => assignedIndices.add(idx));

    if (drawGroupLedIndices.length > 0) {
        const last = drawGroupLedIndices[drawGroupLedIndices.length - 1];
        if (last + 1 < totalCostumeLeds && !assignedIndices.has(last + 1)) {
            return last + 1;
        }
    }
    for (let i = 0; i < totalCostumeLeds; i++) {
        if (!assignedIndices.has(i)) return i;
    }
    return -1;
}

function handleDrawGroupClick(normX, normY) {
    const targetIdx = getNextAvailableLedIndex();
    if (targetIdx === -1) {
        showToast("⚠️ All 100 costume LEDs are assigned to groups! Free up or delete a group first.", "warning");
        return;
    }

    // Reposition LED to exact click coordinates
    leds[targetIdx].x = parseFloat(normX.toFixed(4));
    leds[targetIdx].y = parseFloat(normY.toFixed(4));

    // Sample color from artwork or keep existing
    const col = sampleColorAtNorm(normX, normY);
    if (col) {
        leds[targetIdx].color = { ...col };
    }

    drawGroupLedIndices.push(targetIdx);
    drawGroupPoints.push({ x: leds[targetIdx].x, y: leds[targetIdx].y });
    selectedLeds.add(targetIdx);
    selectedLed = targetIdx;

    updateDrawGroupUI();
    showToast(`📍 Placed Point ${drawGroupLedIndices.length}: LED #${targetIdx}!`);
}

function updateDrawGroupUI() {
    const count = drawGroupLedIndices.length;
    const bannerBadge = document.getElementById('canvasDrawCountBadge');
    const panelBadge = document.getElementById('drawPlacedCountBadge');
    const statusText = document.getElementById('drawStatusText');
    const finishBtn = document.getElementById('finishDrawBtn');
    const canvasFinishBtn = document.getElementById('canvasFinishDrawBtn');

    const badgeText = `${count} Placed`;
    if (bannerBadge) bannerBadge.textContent = badgeText;
    if (panelBadge) panelBadge.textContent = badgeText;

    if (statusText) {
        if (count === 0) {
            statusText.textContent = '✏️ Drawing... Click on shirt';
        } else {
            const nextIdx = getNextAvailableLedIndex();
            statusText.textContent = `📍 ${count} LEDs placed ${nextIdx !== -1 ? `(next: #${nextIdx})` : ''}`;
        }
    }

    const canFinish = count >= 2;
    if (finishBtn) finishBtn.disabled = !canFinish;
    if (canvasFinishBtn) canvasFinishBtn.disabled = !canFinish;

    updateLedInspectorUI();
}

function startDrawGroupMode() {
    isDrawGroupMode = true;
    if (isBoxSelectMode) {
        isBoxSelectMode = false;
        const boxBtn = document.getElementById('boxSelectBtn');
        if (boxBtn) boxBtn.classList.remove('active');
    }

    drawGroupLedIndices = [];
    drawGroupPoints = [];
    selectedLeds.clear();
    selectedLed = null;

    switchGroupCreationMode('draw');

    const drawBtn = document.getElementById('drawGroupBtn');
    if (drawBtn) drawBtn.classList.add('active');

    const toggleBtn = document.getElementById('toggleDrawModeBtn');
    if (toggleBtn) {
        toggleBtn.textContent = '🛑 Stop Drawing';
        toggleBtn.style.background = 'linear-gradient(135deg, #f85149, #da3633)';
        toggleBtn.style.borderColor = '#f85149';
        toggleBtn.style.color = '#fff';
    }

    const banner = document.getElementById('canvasDrawBanner');
    if (banner) banner.style.display = 'flex';

    canvas.style.cursor = 'crosshair';
    updateDrawGroupUI();
    showToast('✏️ Draw Mode Activated: Click anywhere on shirt to place LEDs!');
}

function stopDrawGroupMode() {
    isDrawGroupMode = false;

    const drawBtn = document.getElementById('drawGroupBtn');
    if (drawBtn) drawBtn.classList.remove('active');

    const toggleBtn = document.getElementById('toggleDrawModeBtn');
    if (toggleBtn) {
        toggleBtn.textContent = '✏️ Start Drawing on Shirt';
        toggleBtn.style.background = 'linear-gradient(135deg, #ffc107, #f0883e)';
        toggleBtn.style.borderColor = '#ffc107';
        toggleBtn.style.color = '#000';
    }

    const banner = document.getElementById('canvasDrawBanner');
    if (banner) banner.style.display = 'none';

    canvas.style.cursor = 'default';
}

function cancelDrawGroup() {
    stopDrawGroupMode();
    drawGroupLedIndices = [];
    drawGroupPoints = [];
    selectedLeds.clear();
    selectedLed = null;
    updateLedInspectorUI();
    showToast('Drawing mode cancelled.');
}

function finishDrawGroup() {
    if (drawGroupLedIndices.length < 2) {
        showToast('⚠️ Please place at least 2 LEDs before saving an animation group!', 'warning');
        return;
    }

    const nameInput = document.getElementById('drawGroupNameInput');
    const effectSelect = document.getElementById('drawGroupEffectSelect');
    const dirSelect = document.getElementById('drawGroupDirectionSelect');
    const speedSlider = document.getElementById('drawGroupSpeedSlider');
    const baselineSelect = document.getElementById('drawGroupBaselineSelect');

    const defaultName = `Drawn Path (${drawGroupLedIndices.length} LEDs)`;
    const rawName = (nameInput?.value || '').trim() || defaultName;
    const effect = effectSelect?.value || 'chase';
    const direction = parseInt(dirSelect?.value || '1', 10);
    const speedBpm = parseInt(speedSlider?.value || '140', 10);
    const baselineEffect = baselineSelect?.value || 'inherit';

    const newGroup = {
        id: 'grp_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
        name: rawName,
        ledIndices: [...drawGroupLedIndices], // in exact sequential order of clicks!
        effect: effect,
        speedBpm: speedBpm,
        direction: direction,
        width: 3,
        colorMode: 'original',
        baselineEffect: baselineEffect
    };

    animationGroups.push(newGroup);
    rebuildLedGroupMap();
    renderActiveGroupsList();

    // Select the new group
    selectGroupLeds(newGroup.id);
    stopDrawGroupMode();
    showToast(`🎉 Saved group "${newGroup.name}" with ${newGroup.ledIndices.length} sequential LEDs!`);

    if (nameInput) nameInput.value = '';
}

// ----------------------------------------------------------------------------
// ANIMATION GROUP MANAGEMENT ROUTINES
// ----------------------------------------------------------------------------
function applyGroupEffectToSelection() {
    if (selectedLeds.size === 0) {
        showToast("⚠️ Please select at least 2 LEDs to create or update an animation group!");
        return;
    }

    const nameInput = document.getElementById('groupNameInputHub')?.value ? document.getElementById('groupNameInputHub') : document.getElementById('groupNameInput');
    const effectSelect = document.getElementById('groupEffectSelectHub')?.value ? document.getElementById('groupEffectSelectHub') : document.getElementById('groupEffectSelect');
    const speedSlider = document.getElementById('groupSpeedSliderHub') || document.getElementById('groupSpeedSlider');
    const dirSelect = document.getElementById('groupDirectionSelectHub') || document.getElementById('groupDirectionSelect');
    const baselineSelect = document.getElementById('groupBaselineSelectHub') || document.getElementById('groupBaselineSelect');

    const rawName = (nameInput?.value || '').trim() || `Zone (${selectedLeds.size} LEDs)`;
    const effect = effectSelect?.value || 'chase';
    const speedBpm = parseInt(speedSlider?.value || '140', 10);
    const direction = parseInt(dirSelect?.value || '1', 10);
    const baselineEffect = baselineSelect?.value || (effect === 'fireworks' ? 'off' : 'inherit');

    const sortedIndices = Array.from(selectedLeds).sort((a, b) => a - b);

    // If an existing group with this exact name exists, update it; otherwise create new
    let targetGroup = animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase());
    const isNew = !targetGroup;

    if (targetGroup) {
        targetGroup.ledIndices = sortedIndices;
        targetGroup.effect = effect;
        targetGroup.speedBpm = speedBpm;
        targetGroup.direction = direction;
        targetGroup.baselineEffect = baselineEffect;
    } else {
        targetGroup = {
            id: 'grp_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
            name: rawName,
            ledIndices: sortedIndices,
            effect: effect,
            speedBpm: speedBpm,
            direction: direction,
            width: 3,
            colorMode: 'original',
            baselineEffect: baselineEffect
        };
        animationGroups.push(targetGroup);
    }

    if (effect === 'fireworks') {
        const count = sortedIndices.length;
        const inferredRays = (count % 5 === 0) ? 5 : ((count % 4 === 0) ? 4 : ((count % 6 === 0) ? 6 : ((count % 3 === 0) ? 3 : 5)));
        targetGroup.fireworkRays = targetGroup.fireworkRays || inferredRays;
        targetGroup.fireworkLedsPerRay = targetGroup.fireworkLedsPerRay || Math.round(count / targetGroup.fireworkRays);
        targetGroup.wiringMode = targetGroup.wiringMode || 'serpentine';
    }

    rebuildLedGroupMap();
    renderActiveGroupsList();
    updateLedInspectorUI();

    if (isNew) {
        showToast(`🎉 Saved new group "${targetGroup.name}" (${sortedIndices.length} LEDs)!`);
    } else {
        showToast(`✅ Updated group "${targetGroup.name}" (${sortedIndices.length} LEDs)!`);
    }
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
    updateLedInspectorUI();
    showToast(`🗑️ Removed group effects from ${removedCount} LEDs.`);
}

function deleteGroup(groupId) {
    const idx = animationGroups.findIndex(g => g.id === groupId);
    if (idx !== -1) {
        const name = animationGroups[idx].name;
        animationGroups.splice(idx, 1);
        rebuildLedGroupMap();
        renderActiveGroupsList();
        updateLedInspectorUI();
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
    const baselineSelect = document.getElementById('groupBaselineSelect');
    if (baselineSelect) baselineSelect.value = grp.baselineEffect || (grp.effect === 'fireworks' ? 'off' : 'inherit');

    updateLedInspectorUI();
    renderActiveGroupsList();
    showToast(`🎯 Selected ${selectedLeds.size} LEDs for group "${grp.name}"!`);
}

function formatIndexSummary(indices) {
    if (!indices || indices.length === 0) return 'None';
    const sorted = [...indices].sort((a, b) => a - b);
    if (sorted.length <= 5) {
        return sorted.map(i => `#${i}`).join(', ');
    }
    let isConsecutive = true;
    for (let i = 1; i < sorted.length; i++) {
        if (sorted[i] !== sorted[i - 1] + 1) {
            isConsecutive = false;
            break;
        }
    }
    if (isConsecutive) {
        return `#${sorted[0]}–#${sorted[sorted.length - 1]} (${sorted.length})`;
    }
    return `#${sorted[0]}..#${sorted[sorted.length - 1]} (${sorted.length} LEDs)`;
}

function renderActiveGroupsList() {
    const container = document.getElementById('activeGroupsList');
    const badge = document.getElementById('activeGroupsCountBadge');
    const tabBadge = document.getElementById('tabGroupsBadge');
    const capBadge = document.getElementById('groupsCapacityBadge');
    const countText = document.getElementById('groupedLedsCountText');
    const groupedBar = document.getElementById('groupedLedsBar');
    const ungroupedBar = document.getElementById('ungroupedLedsBar');
    const groupedPctText = document.getElementById('groupedPctText');
    const ungroupedPctText = document.getElementById('ungroupedPctText');

    const totalCostumeLeds = (leds && leds.length > 0) ? leds.length : 100;
    const assignedSet = new Set();
    animationGroups.forEach(g => {
        (g.ledIndices || []).forEach(idx => {
            if (idx < totalCostumeLeds) assignedSet.add(idx);
        });
    });
    const assignedCount = assignedSet.size;
    const unassignedCount = Math.max(0, totalCostumeLeds - assignedCount);
    const assignedPct = Math.round((assignedCount / totalCostumeLeds) * 100);
    const unassignedPct = 100 - assignedPct;

    if (tabBadge) tabBadge.textContent = animationGroups.length;
    if (badge) badge.textContent = `${animationGroups.length} Groups`;
    if (capBadge) capBadge.textContent = `${assignedCount}/${totalCostumeLeds} LEDs`;
    if (countText) countText.textContent = `${assignedCount} / ${totalCostumeLeds} LEDs (${assignedPct}%) assigned to groups`;
    if (groupedBar) groupedBar.style.width = `${assignedPct}%`;
    if (ungroupedBar) ungroupedBar.style.width = `${unassignedPct}%`;
    if (groupedPctText) groupedPctText.textContent = `${assignedPct}% (${assignedCount} LEDs)`;
    if (ungroupedPctText) ungroupedPctText.textContent = `${unassignedPct}% (${unassignedCount} LEDs)`;

    if (!container) return;
    container.innerHTML = '';

    if (animationGroups.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 22px 14px; background: #0d1117; border-radius: 8px; border: 1px dashed #30363d;">
                <div style="font-size: 26px; margin-bottom: 6px;">👥</div>
                <div style="font-size: 13px; font-weight: 600; color: #c9d1d9;">No Animation Groups Yet</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px; line-height: 1.45;">
                    Select 2 or more LEDs using <strong>⬚ Box Select</strong> or <strong>Shift + Click</strong>, configure animation parameters in the Inspector dock below, and click <strong>💾 Save Selection as Group</strong>.
                </div>
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
        rainbow_cycle: '🌈 Rainbow',
        fireworks: '🎆 Fireworks',
        off: '🌑 Off'
    };

    const effectEmoji = {
        fireworks: '🎆',
        chase: '🎡',
        flash_slow: '💡',
        pulse: '💓',
        write_on_off: '✍️',
        sparkle_storm: '✨',
        marquee: '🎪',
        rainbow_cycle: '🌈',
        off: '🌑'
    };

    const baselineLabels = {
        inherit: '🌐 Global',
        off: '🌑 Off / Unlit',
        steady_sparkle: '✨ Sparkle',
        dim_glow: '💡 Glow',
        breathe: '🌬️ Breathe',
        pulse_slow: '💓 Pulse'
    };

    for (const grp of animationGroups) {
        const card = document.createElement('div');
        card.className = 'group-card';
        card.setAttribute('data-group-id', grp.id);

        const isFullySelected = selectedLeds.size > 0 &&
            grp.ledIndices.length > 0 &&
            grp.ledIndices.every(idx => selectedLeds.has(idx));
        if (isFullySelected) {
            card.classList.add('active-group');
        }

        const icon = effectEmoji[grp.effect] || '💫';
        const label = effectIcons[grp.effect] || grp.effect;
        const currentBaseline = grp.baselineEffect || (grp.effect === 'fireworks' ? 'off' : 'inherit');
        const baselineLabel = baselineLabels[currentBaseline] || '🌐 Global';

        let extraPillHtml = '';
        if (grp.effect === 'fireworks') {
            const rPct = Math.round((grp.burstRadius || 0.13) * 100);
            extraPillHtml = `<span class="group-pill group-pill-burst">🎆 ${grp.fireworkRays || 5} Rays • R: ${rPct}%</span>`;
        }

        card.innerHTML = `
            <div class="group-card-header">
                <div class="group-card-title-wrap">
                    <span class="group-card-icon">${icon}</span>
                    <span class="group-card-name" title="${grp.name}">${grp.name}</span>
                </div>
                <span class="group-card-leds-badge">${grp.ledIndices.length} LEDs</span>
            </div>
            <div class="group-card-badges">
                <span class="group-pill group-pill-effect">${label} @ ${grp.speedBpm} BPM</span>
                ${extraPillHtml}
                <span class="group-pill group-pill-baseline">Idle: ${baselineLabel}</span>
                <span class="group-pill" style="background: #21262d; color: #8b949e; border: 1px solid #30363d;" title="LED indices: ${grp.ledIndices.join(', ')}">LEDs: ${formatIndexSummary(grp.ledIndices)}</span>
            </div>
            <div class="group-card-actions">
                <button type="button" class="action-btn select-grp-btn" style="flex: 1; font-weight: 600;" title="Select and inspect all LEDs in this group">
                    🎯 Select & Edit
                </button>
                <button type="button" class="action-btn del-grp-btn" style="color: #ff7b72;" title="Delete group">
                    🗑️
                </button>
            </div>
        `;

        card.addEventListener('click', (e) => {
            if (e.target.closest('.del-grp-btn')) return;
            selectGroupLeds(grp.id);
        });

        const delBtn = card.querySelector('.del-grp-btn');
        if (delBtn) {
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm(`Delete animation group "${grp.name}"?`)) {
                    deleteGroup(grp.id);
                }
            });
        }

        container.appendChild(card);
    }
}

// ============================================================================
// PARADE CUE DIRECTOR (Autonomous Show Sequence Engine)
// ============================================================================

function formatTimelineTime(sec) {
    const s = Math.max(0, sec);
    const m = Math.floor(s / 60);
    const remS = (s % 60).toFixed(1);
    return `${m < 10 ? '0' : ''}${m}:${parseFloat(remS) < 10 ? '0' : ''}${remS}`;
}

function getCueWeight(cue, t) {
    const start = cue.startTime;
    const end = cue.startTime + cue.duration;
    if (t < start || t >= end) return 0;

    let weight = 1.0;
    const fadeIn = Math.max(0, cue.fadeIn || 0);
    const fadeOut = Math.max(0, cue.fadeOut || 0);

    if (fadeIn > 0 && (t - start) < fadeIn) {
        weight = Math.min(weight, (t - start) / fadeIn);
    }
    if (fadeOut > 0 && (end - t) < fadeOut) {
        weight = Math.min(weight, (end - t) / fadeOut);
    }
    return Math.max(0, Math.min(1, weight));
}

function updateSequenceTimeline(now) {
    const dt = (now - lastTimelineFrameTime) / 1000;
    lastTimelineFrameTime = now;

    if (sequenceMode && sequencePlaying) {
        sequenceTime += dt;
        if (sequenceTime >= sequenceLoopDuration) {
            if (sequenceLoop) {
                sequenceTime = sequenceTime % sequenceLoopDuration;
            } else {
                sequenceTime = sequenceLoopDuration;
                sequencePlaying = false;
                updateTimelinePlayBtn();
            }
        }
        updateTimelineScrubberUI();
    }
}

function updateTimelineScrubberUI() {
    const scrubber = document.getElementById('timelineScrubber');
    const currTimeElem = document.getElementById('timelineCurrentTime');
    const totalTimeElem = document.getElementById('timelineTotalTime');
    const needle = document.getElementById('timelinePlayheadNeedle');
    const layersBadge = document.getElementById('timelineActiveLayersBadge');
    const cuesBadge = document.getElementById('timelineActiveCuesBadge');

    if (scrubber) {
        scrubber.max = sequenceLoopDuration;
        scrubber.value = sequenceTime;
    }
    if (currTimeElem) currTimeElem.textContent = formatTimelineTime(sequenceTime);
    if (totalTimeElem) totalTimeElem.textContent = formatTimelineTime(sequenceLoopDuration);

    // Update Playhead Needle position
    if (needle) {
        const pct = Math.max(0, Math.min(1, sequenceTime / sequenceLoopDuration));
        needle.style.left = `calc(115px + (100% - 115px) * ${pct})`;
    }

    // Update active cue highlights in multi-layer tracks and sidebar cards
    const activeCueNames = [];
    const blocks = document.querySelectorAll('.cue-block');
    blocks.forEach(blk => {
        const id = blk.dataset.cueId;
        const cue = sequenceCues.find(q => q.id === id);
        if (cue && sequenceTime >= cue.startTime && sequenceTime < (cue.startTime + cue.duration)) {
            blk.classList.add('active');
            if (!activeCueNames.includes(cue.name)) activeCueNames.push(cue.name);
        } else {
            blk.classList.remove('active');
        }
    });

    const cards = document.querySelectorAll('.cue-card');
    cards.forEach(card => {
        const id = card.dataset.cueId;
        const cue = sequenceCues.find(q => q.id === id);
        if (cue && sequenceTime >= cue.startTime && sequenceTime < (cue.startTime + cue.duration)) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });

    // Update status badges in timeline transport bar
    if (layersBadge) {
        const rowCount = document.querySelectorAll('.timeline-layer-row').length;
        layersBadge.textContent = `${rowCount} Layer${rowCount !== 1 ? 's' : ''}`;
    }
    if (cuesBadge) {
        if (activeCueNames.length === 0) {
            cuesBadge.textContent = sequenceMode ? 'No Cues Active' : 'Sequence Standby (Free-Run)';
            cuesBadge.style.color = '#8b949e';
        } else {
            cuesBadge.textContent = `Active (${activeCueNames.length}): ${activeCueNames.join(' + ')}`;
            cuesBadge.style.color = '#58a6ff';
        }
    }
}

function updateTimelinePlayBtn() {
    const btn = document.getElementById('timelinePlayBtn');
    if (btn) {
        btn.textContent = sequencePlaying ? '⏸' : '▶';
        btn.title = sequencePlaying ? 'Pause Sequence (Spacebar)' : 'Play Sequence (Spacebar)';
    }
}

function togglePlayPause() {
    sequencePlaying = !sequencePlaying;
    if (sequencePlaying && !sequenceMode) {
        toggleSequenceMode(true);
    }
    lastTimelineFrameTime = performance.now();
    updateTimelinePlayBtn();
    showToast(sequencePlaying ? `▶ Playing show sequence (${formatTimelineTime(sequenceTime)})` : '⏸ Paused show sequence');
}

function stopSequence() {
    sequencePlaying = false;
    sequenceTime = 0.0;
    updateTimelinePlayBtn();
    updateTimelineScrubberUI();
    showToast('⏹ Rewound sequence to 0:00');
}

function toggleSequenceMode(forceState) {
    sequenceMode = (typeof forceState === 'boolean') ? forceState : !sequenceMode;

    const btn1 = document.getElementById('toggleSequenceModeBtn');
    const btn2 = document.getElementById('timelineModeToggle');
    const badge = document.getElementById('cueDirectorBadge');

    if (sequenceMode) {
        if (btn1) {
            btn1.textContent = '⏹ Switch to Free-Run';
            btn1.style.borderColor = '#d29922';
            btn1.style.color = '#f0883e';
        }
        if (btn2) {
            btn2.classList.add('active');
            btn2.textContent = '🎬 Sequence: ON';
        }
        if (badge) {
            badge.textContent = `${sequenceCues.length} Cues (Sequence ON)`;
            badge.style.color = '#3fb950';
        }
        showToast('🎬 Show Sequence mode enabled! Running multi-cue timeline.');
    } else {
        if (btn1) {
            btn1.textContent = '▶ Switch to Show Sequence';
            btn1.style.borderColor = '#58a6ff';
            btn1.style.color = '#58a6ff';
        }
        if (btn2) {
            btn2.classList.remove('active');
            btn2.textContent = '🎬 Sequence: OFF';
        }
        if (badge) {
            badge.textContent = `${sequenceCues.length} Cues (Free-Run)`;
            badge.style.color = 'var(--accent-cyan)';
        }
        showToast('🖱️ Free-Run pattern mode restored.');
    }
}

function renderTimelineLayers() {
    const container = document.getElementById('timelineLayersContainer');
    const marksContainer = document.getElementById('timelineRulerMarks');
    if (!container) return;

    // 1. Render Dynamic Ruler Marks
    if (marksContainer) {
        marksContainer.innerHTML = '';
        const tickCount = 6;
        for (let i = 0; i <= tickCount; i++) {
            const t = (sequenceLoopDuration * i) / tickCount;
            const span = document.createElement('span');
            span.className = 'ruler-tick';
            span.textContent = formatTimelineTime(t);
            marksContainer.appendChild(span);
        }
    }

    container.innerHTML = '';

    if (sequenceCues.length === 0) {
        container.innerHTML = `
            <div style="font-size: 11px; color: var(--text-muted); font-style: italic; padding: 6px 12px; text-align: center; border: 1px dashed #30363d; border-radius: 4px;">
                No cues scheduled. Add cues or pick an example routine in the sidebar.
            </div>
        `;
        updateTimelineScrubberUI();
        return;
    }

    // 2. Identify Distinct Target Layers
    const layerMap = new Map();

    const globalCues = sequenceCues.filter(q => q.targetType === 'global');
    if (globalCues.length > 0 || animationGroups.length === 0) {
        layerMap.set('global', {
            id: 'global',
            name: '🌐 Global Float',
            isGlobal: true,
            cues: globalCues
        });
    }

    // Groups present in cues or active animation groups
    sequenceCues.filter(q => q.targetType === 'group').forEach(q => {
        const key = q.groupId || q.groupName || 'unknown_group';
        if (!layerMap.has(key)) {
            const grp = animationGroups.find(g => g.id === q.groupId);
            layerMap.set(key, {
                id: key,
                name: grp ? `🎡 ${grp.name}` : (q.groupName ? `🎡 ${q.groupName}` : '🎡 Group Layer'),
                isGlobal: false,
                cues: []
            });
        }
        layerMap.get(key).cues.push(q);
    });

    let layerIndex = 0;

    layerMap.forEach((layer) => {
        // Calculate non-colliding sub-lanes for overlapping cues in this layer
        const layerCues = [...layer.cues].sort((a, b) => a.startTime - b.startTime);
        const laneEndTimes = [];

        layerCues.forEach(cue => {
            let placedLane = -1;
            for (let l = 0; l < laneEndTimes.length; l++) {
                if (laneEndTimes[l] <= cue.startTime) {
                    placedLane = l;
                    laneEndTimes[l] = cue.startTime + cue.duration;
                    break;
                }
            }
            if (placedLane === -1) {
                placedLane = laneEndTimes.length;
                laneEndTimes.push(cue.startTime + cue.duration);
            }
            cue._subLane = placedLane;
        });

        const totalSubLanes = Math.max(1, laneEndTimes.length);
        const rowHeight = totalSubLanes * 24;

        const row = document.createElement('div');
        row.className = 'timeline-layer-row';
        row.style.minHeight = `${rowHeight}px`;

        const label = document.createElement('div');
        label.className = 'timeline-layer-label';
        label.title = layer.name;
        label.textContent = layer.name;
        label.style.minHeight = `${rowHeight}px`;

        const track = document.createElement('div');
        track.className = 'timeline-layer-track';
        track.style.minHeight = `${rowHeight}px`;

        // Click track seeking
        track.addEventListener('click', (e) => {
            const rect = track.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const pct = Math.max(0, Math.min(1, clickX / rect.width));
            sequenceTime = pct * sequenceLoopDuration;
            updateTimelineScrubberUI();
        });

        layerCues.forEach(cue => {
            const block = document.createElement('div');
            const colorClass = layer.isGlobal 
                ? 'global-layer' 
                : (layerIndex % 3 === 0 ? 'group-layer' : (layerIndex % 3 === 1 ? 'group-layer-alt' : 'group-layer-green'));
            block.className = `cue-block ${colorClass}`;
            block.dataset.cueId = cue.id;

            const leftPct = (cue.startTime / sequenceLoopDuration) * 100;
            const widthPct = Math.max(1.2, (cue.duration / sequenceLoopDuration) * 100);
            block.style.left = `${leftPct}%`;
            block.style.width = `${widthPct}%`;
            block.style.top = `${cue._subLane * 24 + 2}px`;
            block.title = `${cue.name} (${cue.startTime.toFixed(1)}s - ${(cue.startTime + cue.duration).toFixed(1)}s) [Fade In: ${cue.fadeIn || 0}s, Out: ${cue.fadeOut || 0}s]`;

            if (cue.fadeIn && cue.fadeIn > 0) {
                const inPct = Math.min(40, (cue.fadeIn / cue.duration) * 100);
                const fadeDiv = document.createElement('div');
                fadeDiv.className = 'cue-fade-indicator-in';
                fadeDiv.style.width = `${inPct}%`;
                block.appendChild(fadeDiv);
            }

            const title = document.createElement('span');
            title.className = 'cue-block-title';
            title.textContent = `${cue.name} (${cue.duration.toFixed(0)}s)`;
            block.appendChild(title);

            if (cue.fadeOut && cue.fadeOut > 0) {
                const outPct = Math.min(40, (cue.fadeOut / cue.duration) * 100);
                const fadeDiv = document.createElement('div');
                fadeDiv.className = 'cue-fade-indicator-out';
                fadeDiv.style.width = `${outPct}%`;
                block.appendChild(fadeDiv);
            }

            block.addEventListener('click', (e) => {
                e.stopPropagation();
                sequenceTime = cue.startTime;
                updateTimelineScrubberUI();
                const card = document.querySelector(`.cue-card[data-cue-id="${cue.id}"]`);
                if (card) {
                    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    card.style.outline = '2px solid #58a6ff';
                    setTimeout(() => card.style.outline = 'none', 1000);
                }
            });

            track.appendChild(block);
        });

        row.appendChild(label);
        row.appendChild(track);
        container.appendChild(row);

        layerIndex++;
    });

    updateTimelineScrubberUI();
}

// Retain alias for any existing calls
const renderTimelineCueStrip = renderTimelineLayers;

function renderCuesList() {
    const container = document.getElementById('cuesListContainer');
    const badge = document.getElementById('cueDirectorBadge');
    if (!container) return;

    if (badge) {
        badge.textContent = `${sequenceCues.length} Cues (${sequenceMode ? 'Sequence ON' : 'Free-Run'})`;
    }

    container.innerHTML = '';

    if (sequenceCues.length === 0) {
        container.innerHTML = `
            <div style="font-size: 11px; color: var(--text-muted); font-style: italic; padding: 12px; text-align: center; border: 1px dashed #30363d; border-radius: 6px;">
                No cues added yet. Click <strong>➕ Add Cue</strong> or pick an example routine above to start directing your float!
            </div>
        `;
        renderTimelineCueStrip();
        return;
    }

    // Sort cues by start time
    sequenceCues.sort((a, b) => a.startTime - b.startTime);

    const effectOptions = [
        { id: 'steady_sparkle', label: '✨ Steady Colors + Sparkles' },
        { id: 'color_match', label: '🌈 Color-Matched Breathing Glow' },
        { id: 'chase', label: '🎡 Chase / Wheel Spin' },
        { id: 'pulse', label: '💓 Breathing Glow Pulse' },
        { id: 'flash_slow', label: '💡 Slow Flashing / Blink' },
        { id: 'write_on_off', label: '✍️ Theatrical Write-On/Off' },
        { id: 'sparkle_storm', label: '✨ Sparkle Storm' },
        { id: 'marquee', label: '🎪 Theater Marquee' },
        { id: 'traveling_wave', label: '🌊 Traveling Parade Wave' },
        { id: 'fire_breath', label: '🔥 Snout Fire Breath' },
        { id: 'fireworks', label: '🎆 Fireworks Starburst' }
    ];

    sequenceCues.forEach((cue, idx) => {
        const card = document.createElement('div');
        card.className = 'cue-card';
        card.dataset.cueId = cue.id;

        const endTime = (cue.startTime + cue.duration).toFixed(1);

        card.innerHTML = `
            <div class="cue-card-header">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${cue.targetType === 'global' ? '#58a6ff' : '#ffc107'};"></span>
                    <input type="text" class="cue-name-input" value="${cue.name}" style="background: transparent; border: none; border-bottom: 1px dashed #30363d; color: #fff; font-size: 12px; font-weight: bold; width: 150px; outline: none;">
                </div>
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="font-family: monospace; font-size: 10px; color: var(--accent-cyan);">${cue.startTime.toFixed(1)}s - ${endTime}s</span>
                    <button type="button" class="del-cue-btn" style="background: transparent; border: none; color: #f85149; font-size: 11px; cursor: pointer; padding: 2px;" title="Delete this cue">🗑️</button>
                </div>
            </div>

            <!-- Target Layer & Effect Selection -->
            <div class="cue-card-row">
                <div style="flex: 1.1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Target Layer:</label>
                    <select class="cue-target-select" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px;">
                        <option value="global" ${cue.targetType === 'global' ? 'selected' : ''}>🌐 Global Float</option>
                        ${animationGroups.map(g => `<option value="group:${g.id}" ${cue.targetType === 'group' && cue.groupId === g.id ? 'selected' : ''}>🎡 Group: ${g.name}</option>`).join('')}
                    </select>
                </div>
                <div style="flex: 1.3;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Pattern / Effect:</label>
                    <select class="cue-effect-select" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px;">
                        ${effectOptions.map(e => `<option value="${e.id}" ${cue.effect === e.id ? 'selected' : ''}>${e.label}</option>`).join('')}
                    </select>
                </div>
            </div>

            <!-- Start Time, Duration & BPM -->
            <div class="cue-card-row">
                <div style="flex: 1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Start (s):</label>
                    <input type="number" class="cue-start-input" step="0.5" min="0" max="${sequenceLoopDuration}" value="${cue.startTime}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px; text-align: center;">
                </div>
                <div style="flex: 1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Duration (s):</label>
                    <input type="number" class="cue-dur-input" step="0.5" min="1" max="${sequenceLoopDuration}" value="${cue.duration}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px; text-align: center;">
                </div>
                <div style="flex: 1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">BPM:</label>
                    <input type="number" class="cue-bpm-input" min="30" max="280" value="${cue.speedBpm || 120}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px; text-align: center;">
                </div>
            </div>

            <!-- Crossfade In / Out -->
            <div class="cue-card-row" style="background: rgba(0,0,0,0.25); padding: 4px 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: var(--text-muted);">Crossfade:</span>
                <div style="display: flex; align-items: center; gap: 4px; flex: 1;">
                    <label style="font-size: 10px; color: var(--text-muted);">In:</label>
                    <input type="number" class="cue-fade-in-input" step="0.5" min="0" max="10" value="${cue.fadeIn || 0}" style="width: 44px; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 2px 4px; font-size: 10px; text-align: center;">
                    <span style="font-size: 10px; color: var(--text-muted);">s</span>
                </div>
                <div style="display: flex; align-items: center; gap: 4px; flex: 1;">
                    <label style="font-size: 10px; color: var(--text-muted);">Out:</label>
                    <input type="number" class="cue-fade-out-input" step="0.5" min="0" max="10" value="${cue.fadeOut || 0}" style="width: 44px; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 2px 4px; font-size: 10px; text-align: center;">
                    <span style="font-size: 10px; color: var(--text-muted);">s</span>
                </div>
            </div>
        `;

        // Event listeners for cue inputs
        card.querySelector('.cue-name-input').addEventListener('input', (e) => {
            cue.name = e.target.value.trim() || `Cue #${idx + 1}`;
        });

        card.querySelector('.cue-target-select').addEventListener('change', (e) => {
            const val = e.target.value;
            if (val.startsWith('group:')) {
                cue.targetType = 'group';
                cue.groupId = val.replace('group:', '');
                const grp = animationGroups.find(g => g.id === cue.groupId);
                cue.groupName = grp ? grp.name : '';
            } else {
                cue.targetType = 'global';
                cue.groupId = '';
                cue.groupName = '';
            }
            renderTimelineCueStrip();
        });

        card.querySelector('.cue-effect-select').addEventListener('change', (e) => {
            cue.effect = e.target.value;
        });

        card.querySelector('.cue-start-input').addEventListener('change', (e) => {
            cue.startTime = Math.max(0, parseFloat(e.target.value) || 0);
            renderTimelineCueStrip();
        });

        card.querySelector('.cue-dur-input').addEventListener('change', (e) => {
            cue.duration = Math.max(0.5, parseFloat(e.target.value) || 10);
            renderTimelineCueStrip();
        });

        card.querySelector('.cue-bpm-input').addEventListener('change', (e) => {
            cue.speedBpm = Math.max(20, parseInt(e.target.value) || 120);
        });

        card.querySelector('.cue-fade-in-input').addEventListener('change', (e) => {
            cue.fadeIn = Math.max(0, parseFloat(e.target.value) || 0);
        });

        card.querySelector('.cue-fade-out-input').addEventListener('change', (e) => {
            cue.fadeOut = Math.max(0, parseFloat(e.target.value) || 0);
        });

        card.querySelector('.del-cue-btn').addEventListener('click', () => {
            deleteCue(cue.id);
        });

        container.appendChild(card);
    });

    renderTimelineCueStrip();
    updateTimelineScrubberUI();
}

function addCue(options = {}) {
    const lastCue = sequenceCues.length > 0 ? sequenceCues[sequenceCues.length - 1] : null;
    const defaultStart = lastCue ? Math.min(sequenceLoopDuration - 5, lastCue.startTime + lastCue.duration) : Math.min(sequenceLoopDuration - 10, Math.floor(sequenceTime));

    const newCue = {
        id: 'cue_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
        name: options.name || `Cue #${sequenceCues.length + 1}`,
        startTime: options.startTime !== undefined ? options.startTime : defaultStart,
        duration: options.duration !== undefined ? options.duration : 20.0,
        targetType: options.targetType || 'global',
        groupId: options.groupId || '',
        groupName: options.groupName || '',
        effect: options.effect || 'color_match',
        speedBpm: options.speedBpm || 120,
        fadeIn: options.fadeIn !== undefined ? options.fadeIn : 1.5,
        fadeOut: options.fadeOut !== undefined ? options.fadeOut : 1.5
    };

    sequenceCues.push(newCue);
    renderCuesList();
    showToast(`➕ Added show cue "${newCue.name}"!`);
}

function deleteCue(cueId) {
    const idx = sequenceCues.findIndex(q => q.id === cueId);
    if (idx !== -1) {
        const name = sequenceCues[idx].name;
        sequenceCues.splice(idx, 1);
        renderCuesList();
        showToast(`🗑️ Deleted cue "${name}"`);
    }
}

function loadCinderellaShowTemplate() {
    sequenceLoopDuration = 90.0;
    const loopInput = document.getElementById('sequenceLoopInput');
    if (loopInput) loopInput.value = 90;

    let wheelGrp = animationGroups.find(g => g.name.toLowerCase().includes('wheel'));
    let lanternGrp = animationGroups.find(g => g.name.toLowerCase().includes('lantern'));

    sequenceCues = [
        {
            id: 'cue_cinderella_1',
            name: 'Opening Starlight Sparkle',
            startTime: 0.0,
            duration: 25.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'steady_sparkle',
            speedBpm: 120,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_cinderella_2',
            name: 'Carriage Wheels Spin',
            startTime: 15.0,
            duration: 35.0,
            targetType: wheelGrp ? 'group' : 'global',
            groupId: wheelGrp ? wheelGrp.id : '',
            groupName: wheelGrp ? wheelGrp.name : 'Carriage Wheels',
            effect: 'chase',
            speedBpm: 140,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_cinderella_3',
            name: 'Royal Carriage Breathing Glow',
            startTime: 25.0,
            duration: 40.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'color_match',
            speedBpm: 100,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_cinderella_4',
            name: 'Lanterns Breathing Pulse',
            startTime: 35.0,
            duration: 25.0,
            targetType: lanternGrp ? 'group' : 'global',
            groupId: lanternGrp ? lanternGrp.id : '',
            groupName: lanternGrp ? lanternGrp.name : 'Carriage Lanterns',
            effect: 'pulse',
            speedBpm: 75,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_cinderella_5',
            name: 'Grand Finale Electrical Wave',
            startTime: 60.0,
            duration: 30.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'traveling_wave',
            speedBpm: 130,
            fadeIn: 2.5,
            fadeOut: 2.0
        }
    ];

    renderCuesList();
    toggleSequenceMode(true);
    showToast("🎃 Loaded Cinderella's Coach 90s Parade Show Routine!");
}

function loadDragonShowTemplate() {
    sequenceLoopDuration = 90.0;
    const loopInput = document.getElementById('sequenceLoopInput');
    if (loopInput) loopInput.value = 90;

    let crestGrp = animationGroups.find(g => g.name.toLowerCase().includes('crest') || g.name.toLowerCase().includes('hair'));

    sequenceCues = [
        {
            id: 'cue_dragon_1',
            name: 'Comic Starlight Sparkle',
            startTime: 0.0,
            duration: 30.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'steady_sparkle',
            speedBpm: 120,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_dragon_2',
            name: 'Flame Hair Crest Fire Pulse',
            startTime: 20.0,
            duration: 30.0,
            targetType: crestGrp ? 'group' : 'global',
            groupId: crestGrp ? crestGrp.id : '',
            groupName: crestGrp ? crestGrp.name : 'Flame Crest',
            effect: 'pulse',
            speedBpm: 100,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_dragon_3',
            name: 'Snout Fire-Breathing Pulse',
            startTime: 30.0,
            duration: 35.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'fire_breath',
            speedBpm: 110,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_dragon_4',
            name: 'Broadway Electrical Marquee',
            startTime: 65.0,
            duration: 25.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'marquee',
            speedBpm: 140,
            fadeIn: 2.0,
            fadeOut: 2.0
        }
    ];

    renderCuesList();
    toggleSequenceMode(true);
    showToast("🐉 Loaded Pete's Dragon 90s Parade Show Routine!");
}

// ============================================================================
// PARADE CUE DIRECTOR & MASTER TIMELINE EVENT LISTENERS
// ============================================================================
const timelinePlayBtn = document.getElementById('timelinePlayBtn');
if (timelinePlayBtn) {
    timelinePlayBtn.addEventListener('click', togglePlayPause);
}

const timelineStopBtn = document.getElementById('timelineStopBtn');
if (timelineStopBtn) {
    timelineStopBtn.addEventListener('click', stopSequence);
}

const timelineLoopToggle = document.getElementById('timelineLoopToggle');
if (timelineLoopToggle) {
    timelineLoopToggle.addEventListener('click', () => {
        sequenceLoop = !sequenceLoop;
        timelineLoopToggle.classList.toggle('active', sequenceLoop);
        showToast(sequenceLoop ? "🔁 Sequence loop ON" : "➡️ Sequence play once (no loop)");
    });
}

const timelineModeToggle = document.getElementById('timelineModeToggle');
if (timelineModeToggle) {
    timelineModeToggle.addEventListener('click', () => toggleSequenceMode());
}

const toggleSequenceModeBtn = document.getElementById('toggleSequenceModeBtn');
if (toggleSequenceModeBtn) {
    toggleSequenceModeBtn.addEventListener('click', () => toggleSequenceMode());
}

const timelineScrubber = document.getElementById('timelineScrubber');
if (timelineScrubber) {
    timelineScrubber.addEventListener('input', (e) => {
        sequenceTime = parseFloat(e.target.value) || 0;
        updateTimelineScrubberUI();
    });
}

const sequenceLoopInput = document.getElementById('sequenceLoopInput');
if (sequenceLoopInput) {
    sequenceLoopInput.addEventListener('change', (e) => {
        const val = Math.max(10, parseFloat(e.target.value) || 90);
        sequenceLoopDuration = val;
        e.target.value = val;
        const scrubber = document.getElementById('timelineScrubber');
        if (scrubber) scrubber.max = val;
        updateTimelineScrubberUI();
        renderTimelineCueStrip();
        showToast(`⏱️ Loop duration set to ${val}s`);
    });
}

const addCueBtn = document.getElementById('addCueBtn');
if (addCueBtn) {
    addCueBtn.addEventListener('click', () => addCue());
}

const sequenceTemplateSelect = document.getElementById('sequenceTemplateSelect');
if (sequenceTemplateSelect) {
    sequenceTemplateSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'cinderella_90s') {
            loadCinderellaShowTemplate();
        } else if (val === 'dragon_90s') {
            loadDragonShowTemplate();
        } else if (val === 'clear_cues') {
            sequenceCues = [];
            renderCuesList();
            showToast("🗑️ All sequence cues cleared.");
        }
        e.target.value = '';
    });
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

    if (isDrawGroupMode) {
        if (e.key === 'Enter') {
            e.preventDefault();
            finishDrawGroup();
            return;
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelDrawGroup();
            return;
        }
    }

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
        if (!isPanning && !hasMovedSignificantly && !['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
            togglePlayPause();
        }
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

    // Click-to-Draw Sequential Mode Handler
    if (isDrawGroupMode) {
        const worldX = (mx - panX) / zoomScale;
        const worldY = (my - panY) / zoomScale;
        const norm = canvasToNorm(worldX, worldY);
        const clampX = Math.max(0.08, Math.min(0.92, norm.x));
        const clampY = Math.max(0.08, Math.min(0.92, norm.y));
        handleDrawGroupClick(clampX, clampY);
        return;
    }

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
            // Normal click: select single LED or drag entire multi-selection/firework
            let isGroupDrag = false;
            if (selectedLeds.has(clickedIdx) && selectedLeds.size > 1) {
                isGroupDrag = true;
                selectedLed = clickedIdx;
                updateLedInspectorUI();
            } else {
                // Check if this LED belongs to an active fireworks group
                const fwGroup = animationGroups.find(g => g.effect === 'fireworks' && g.ledIndices && g.ledIndices.includes(clickedIdx));
                if (fwGroup) {
                    isGroupDrag = true;
                    activeFireworksGroupId = fwGroup.id;
                    updateActiveFwDropdown();
                    syncFireworksSliders(fwGroup.centerNormX, fwGroup.centerNormY, fwGroup.burstRadius, fwGroup.fireworkColor);
                    selectedLeds.clear();
                    for (const idx of fwGroup.ledIndices) selectedLeds.add(idx);
                    selectedLed = clickedIdx;
                    updateLedInspectorUI();
                } else {
                    selectLed(clickedIdx, false);
                }
            }

            draggedLed = clickedIdx;
            isDraggingLed = true;
            canvas.classList.add('dragging');

            const worldX = (mx - panX) / zoomScale;
            const worldY = (my - panY) / zoomScale;
            multiDragStartNorm = canvasToNorm(worldX, worldY);
            multiDragInitialPositions.clear();

            if (isGroupDrag) {
                for (const idx of selectedLeds) {
                    if (leds[idx]) {
                        multiDragInitialPositions.set(idx, { x: leds[idx].x, y: leds[idx].y });
                    }
                }
            } else {
                if (leds[clickedIdx]) {
                    multiDragInitialPositions.set(clickedIdx, { x: leds[clickedIdx].x, y: leds[clickedIdx].y });
                }
            }
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

        if (multiDragInitialPositions.size > 1 && multiDragStartNorm) {
            const dx = norm.x - multiDragStartNorm.x;
            const dy = norm.y - multiDragStartNorm.y;

            for (const [idx, initialPos] of multiDragInitialPositions.entries()) {
                if (leds[idx]) {
                    leds[idx].x = Math.max(0.05, Math.min(0.95, parseFloat((initialPos.x + dx).toFixed(4))));
                    leds[idx].y = Math.max(0.05, Math.min(0.95, parseFloat((initialPos.y + dy).toFixed(4))));
                }
            }

            // Sync fireworks group center & sliders if a fireworks group is being dragged
            const fwGroup = animationGroups.find(g => g.effect === 'fireworks' && g.ledIndices && g.ledIndices.includes(draggedLed));
            if (fwGroup) {
                let sumX = 0, sumY = 0;
                for (const idx of fwGroup.ledIndices) {
                    sumX += leds[idx].x;
                    sumY += leds[idx].y;
                }
                fwGroup.centerNormX = parseFloat((sumX / fwGroup.ledIndices.length).toFixed(4));
                fwGroup.centerNormY = parseFloat((sumY / fwGroup.ledIndices.length).toFixed(4));
                activeFireworksGroupId = fwGroup.id;
                syncFireworksSliders(fwGroup.centerNormX, fwGroup.centerNormY, fwGroup.burstRadius, fwGroup.fireworkColor);
                const sel = document.getElementById('activeFwSelect');
                if (sel) sel.value = fwGroup.id;
            }
        } else {
            leds[draggedLed].x = norm.x;
            leds[draggedLed].y = norm.y;
        }

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
    } else if (isDrawGroupMode) {
        canvas.style.cursor = 'crosshair';
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
        multiDragStartNorm = null;
        multiDragInitialPositions.clear();
        canvas.classList.remove('dragging');
    }
});

// ============================================================================
// MAIN ANIMATION LOOP
// ============================================================================
function animate(time) {
    updateSequenceTimeline(time);
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
        },
        sequence: {
            loopDuration: sequenceLoopDuration,
            cues: sequenceCues
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
    } else if (currentGraphicType === 'carriage_nohorses') {
        customArtworkImg = null;
        customArtworkDataUrl = null;
        if (graphicSelect) graphicSelect.value = 'carriage_nohorses';
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
            params.sparkleRate = parseFloat(s.sparkleRate);
            const spk = document.getElementById('sparkleSlider');
            if (spk) spk.value = params.sparkleRate;
            const spkVal = document.getElementById('sparkleVal');
            if (spkVal) spkVal.textContent = `${params.sparkleRate.toFixed(params.sparkleRate < 1 ? 2 : 1)}%`;
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
    const loadedFwGroups = animationGroups.filter(g => g.effect === 'fireworks');
    if (loadedFwGroups.length > 0) {
        activeFireworksGroupId = loadedFwGroups[0].id;
        updateActiveFwDropdown();
        syncFireworksSliders(loadedFwGroups[0].centerNormX, loadedFwGroups[0].centerNormY, loadedFwGroups[0].burstRadius, loadedFwGroups[0].fireworkColor);
    } else {
        activeFireworksGroupId = null;
        updateActiveFwDropdown();
    }

    // 5. Restore Sequence Cues (Parade Cue Director)
    if (profileData.sequence && typeof profileData.sequence === 'object') {
        sequenceLoopDuration = Math.max(10, parseFloat(profileData.sequence.loopDuration) || 90.0);
        sequenceCues = Array.isArray(profileData.sequence.cues) ? profileData.sequence.cues : [];
        const loopInput = document.getElementById('sequenceLoopInput');
        if (loopInput) loopInput.value = sequenceLoopDuration;
        const scrubber = document.getElementById('timelineScrubber');
        if (scrubber) scrubber.max = sequenceLoopDuration;
        renderCuesList();
        renderTimelineCueStrip();
        updateTimelineScrubberUI();
    } else {
        sequenceCues = [];
        renderCuesList();
        renderTimelineCueStrip();
    }

    // 6. Populate profile name input
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
    params.sparkleRate = parseFloat(e.target.value);
    document.getElementById('sparkleVal').textContent = `${params.sparkleRate.toFixed(params.sparkleRate < 1 ? 2 : 1)}%`;
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

const showBibToggle = document.getElementById('showBibToggle');
if (showBibToggle) {
    showBibToggle.addEventListener('change', (e) => {
        params.showBib = e.target.checked;
        const posRow = document.getElementById('bibPositionRow');
        const scaleRow = document.getElementById('bibScaleRow');
        if (posRow) posRow.style.display = e.target.checked ? 'flex' : 'none';
        if (scaleRow) scaleRow.style.display = e.target.checked ? 'flex' : 'none';
    });
}

const bibYSlider = document.getElementById('bibYSlider');
if (bibYSlider) {
    bibYSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        params.bibYOffset = val / 100.0;
        const valBadge = document.getElementById('bibYVal');
        if (valBadge) valBadge.textContent = `${val}%`;
    });
}

const bibScaleSlider = document.getElementById('bibScaleSlider');
if (bibScaleSlider) {
    bibScaleSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        params.bibScale = val / 100.0;
        const valBadge = document.getElementById('bibScaleVal');
        if (valBadge) valBadge.textContent = `${val}%`;
    });
}

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

// Group Creation Hub & Navigation Bindings
document.getElementById('goToGroupsTabBtn')?.addEventListener('click', () => {
    if (typeof switchSidebarTab === 'function') switchSidebarTab('tabGroups');
});

document.getElementById('quickActivateBoxSelectBtn')?.addEventListener('click', () => {
    isBoxSelectMode = true;
    const boxBtn = document.getElementById('boxSelectBtn');
    if (boxBtn) boxBtn.classList.add('active');
    canvas.style.cursor = 'crosshair';
    showToast('⬚ Box Select mode enabled: Drag across LEDs to select');
});

// Mode Selector Tabs (Selection, Click-to-Draw, Fireworks)
document.getElementById('creationModeSelectBtn')?.addEventListener('click', () => switchGroupCreationMode('select'));
document.getElementById('creationModeDrawBtn')?.addEventListener('click', () => switchGroupCreationMode('draw'));
document.getElementById('creationModeFwBtn')?.addEventListener('click', () => switchGroupCreationMode('fw'));

// Hub Panel 1: From Selection Actions & Sliders
document.getElementById('saveSelectionGroupBtnHub')?.addEventListener('click', () => applyGroupEffectToSelection());
document.getElementById('removeGroupEffectBtnHub')?.addEventListener('click', () => removeGroupEffectFromSelection());

const groupSpeedSliderHub = document.getElementById('groupSpeedSliderHub');
const groupSpeedValHub = document.getElementById('groupSpeedValHub');
if (groupSpeedSliderHub) {
    groupSpeedSliderHub.addEventListener('input', (e) => {
        if (groupSpeedValHub) groupSpeedValHub.textContent = `${e.target.value} BPM`;
        const gSlider = document.getElementById('groupSpeedSlider');
        const gVal = document.getElementById('groupSpeedVal');
        if (gSlider) gSlider.value = e.target.value;
        if (gVal) gVal.textContent = `${e.target.value} BPM`;
    });
}

const groupBaselineSelectHub = document.getElementById('groupBaselineSelectHub');
if (groupBaselineSelectHub) {
    groupBaselineSelectHub.addEventListener('change', (e) => {
        const val = e.target.value;
        const gBase = document.getElementById('groupBaselineSelect');
        if (gBase) gBase.value = val;
        const nameInput = document.getElementById('groupNameInputHub') || document.getElementById('groupNameInput');
        const rawName = (nameInput?.value || '').trim();
        let grp = null;
        if (selectedLed !== null && ledGroupMap[selectedLed]) {
            grp = ledGroupMap[selectedLed].group;
        } else if (rawName) {
            grp = animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase());
        }
        if (grp) {
            grp.baselineEffect = val;
            renderActiveGroupsList();
            showToast(`💤 Set resting baseline for "${grp.name}" to: ${val}`);
        }
    });
}

// Hub Panel 2: Click-to-Draw Actions
const drawGroupBtn = document.getElementById('drawGroupBtn');
if (drawGroupBtn) {
    drawGroupBtn.addEventListener('click', () => {
        if (isDrawGroupMode) {
            stopDrawGroupMode();
        } else {
            if (typeof switchSidebarTab === 'function') switchSidebarTab('tabGroups');
            startDrawGroupMode();
        }
    });
}

const toggleDrawModeBtn = document.getElementById('toggleDrawModeBtn');
if (toggleDrawModeBtn) {
    toggleDrawModeBtn.addEventListener('click', () => {
        if (isDrawGroupMode) {
            stopDrawGroupMode();
        } else {
            startDrawGroupMode();
        }
    });
}

document.getElementById('finishDrawBtn')?.addEventListener('click', () => finishDrawGroup());
document.getElementById('canvasFinishDrawBtn')?.addEventListener('click', () => finishDrawGroup());
document.getElementById('cancelDrawBtn')?.addEventListener('click', () => cancelDrawGroup());
document.getElementById('canvasCancelDrawBtn')?.addEventListener('click', () => cancelDrawGroup());

const drawGroupSpeedSlider = document.getElementById('drawGroupSpeedSlider');
const drawGroupSpeedVal = document.getElementById('drawGroupSpeedVal');
if (drawGroupSpeedSlider) {
    drawGroupSpeedSlider.addEventListener('input', (e) => {
        if (drawGroupSpeedVal) drawGroupSpeedVal.textContent = `${e.target.value} BPM`;
    });
}

document.getElementById('selectAllGroupedBtn')?.addEventListener('click', () => {
    const allGroupedIndices = new Set();
    animationGroups.forEach(g => (g.ledIndices || []).forEach(idx => allGroupedIndices.add(idx)));
    if (allGroupedIndices.size === 0) {
        showToast('⚠️ No LEDs are currently assigned to any group.');
        return;
    }
    selectedLeds.clear();
    allGroupedIndices.forEach(idx => { if (idx < leds.length) selectedLeds.add(idx); });
    selectedLed = Array.from(selectedLeds)[0] || null;
    updateLedInspectorUI();
    renderActiveGroupsList();
    showToast(`👥 Selected all ${selectedLeds.size} grouped LEDs across ${animationGroups.length} groups.`);
});

document.getElementById('selectUnassignedBtn')?.addEventListener('click', () => {
    const allGroupedIndices = new Set();
    animationGroups.forEach(g => (g.ledIndices || []).forEach(idx => allGroupedIndices.add(idx)));
    selectedLeds.clear();
    for (let i = 0; i < leds.length; i++) {
        if (!allGroupedIndices.has(i)) {
            selectedLeds.add(i);
        }
    }
    if (selectedLeds.size === 0) {
        showToast('🎉 All 100 LEDs are assigned to animation groups!');
        return;
    }
    selectedLed = Array.from(selectedLeds)[0] || null;
    updateLedInspectorUI();
    renderActiveGroupsList();
    showToast(`⚡ Selected ${selectedLeds.size} unassigned LEDs! Customize effect and save as a group below.`);
});

const groupEffectSelect = document.getElementById('groupEffectSelect');
if (groupEffectSelect) {
    groupEffectSelect.addEventListener('change', (e) => {
        const row = document.getElementById('groupFwRadiusRow');
        if (row) {
            const isFw = e.target.value === 'fireworks';
            row.style.display = isFw ? 'block' : 'none';
            if (isFw) {
                const fwGrp = typeof getActiveFireworksGroup === 'function' ? getActiveFireworksGroup() : null;
                if (fwGrp) {
                    syncFireworksSliders(fwGrp.centerNormX, fwGrp.centerNormY, fwGrp.burstRadius, fwGrp.fireworkColor);
                }
            }
        }
    });
}

const groupSpeedSlider = document.getElementById('groupSpeedSlider');
const groupSpeedVal = document.getElementById('groupSpeedVal');
if (groupSpeedSlider) {
    groupSpeedSlider.addEventListener('input', (e) => {
        if (groupSpeedVal) groupSpeedVal.textContent = `${e.target.value} BPM`;
    });
}

const groupBaselineSelect = document.getElementById('groupBaselineSelect');
if (groupBaselineSelect) {
    groupBaselineSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        const nameInput = document.getElementById('groupNameInput');
        const rawName = (nameInput?.value || '').trim();
        let grp = null;
        if (selectedLed !== null && ledGroupMap[selectedLed]) {
            grp = ledGroupMap[selectedLed].group;
        } else if (rawName) {
            grp = animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase());
        }
        if (grp) {
            grp.baselineEffect = val;
            renderActiveGroupsList();
            const labelMap = {
                inherit: 'Follow Overall Baseline (Default)',
                off: 'Off / Completely Unlit (Pitch Black)',
                steady_sparkle: 'Gentle Starlight Sparkle',
                dim_glow: 'Dim Static Glow',
                breathe: 'Calm Breathing Glow',
                pulse_slow: 'Slow Resting Pulse'
            };
            showToast(`💤 Set resting baseline for "${grp.name}" to: ${labelMap[val] || val}`);
        }
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
    // If user uploaded a custom graphic, selected Cinderella's Coach, or Carriage (No Horses), preserve and boost authentic colors!
    if (currentGraphicType === 'custom_image' || currentGraphicType === 'cinderellas_coach' || currentGraphicType === 'carriage_nohorses') {
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
    } else if (type === 'carriage_nohorses') {
        currentGraphicType = 'carriage_nohorses';
        customArtworkImg = null;
        customArtworkDataUrl = null;
        if (uploadContainer) uploadContainer.style.display = 'none';
        if (resetBtn) resetBtn.style.display = 'block';

        // Load Carriage (No Horses) preset if available from server
        try {
            const res = await fetch('/api/preset/carriage_nohorses.json');
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
                    if (nameIn) nameIn.value = "Carriage (No Horses)";
                    showToast("🎃 Loaded Carriage (No Horses) with 100 color-matched LEDs!");
                    return;
                }
            }
        } catch (e) {
            console.warn("Could not fetch Carriage (No Horses) preset:", e);
        }

        animationGroups = [];
        rebuildLedGroupMap();
        renderActiveGroupsList();
        scatterLedsOnGraphic(100, true);
        showToast("🎃 Switched to Carriage (No Horses)!");
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

// ============================================================================
// FIREWORKS STARBURST GENERATOR & REMAINING LED RE-DISTRIBUTION (100 TOTAL)
// ============================================================================
function sampleRemainingGraphicLeds(targetCount, excludeX = 0, excludeY = 0, excludeRadius = 0) {
    if (targetCount <= 0) return [];

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

    let isLightBg = false;
    let isDarkBg = false;
    if (!hasTransparency) {
        const cornerCoords = [
            [4, 4], [targetW - 5, 4], [4, targetH - 5], [targetW - 5, targetH - 5],
            [Math.floor(targetW / 2), 4], [Math.floor(targetW / 2), targetH - 5]
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

    const gb = getGraphicChestBounds();
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
                isFg = (currentGraphicType === 'builtin_dragon') ? (a > 80 && Math.max(r, g, b) >= 60) : (a > 60);
            } else if (isLightBg) {
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                const satDelta = Math.max(r, g, b) - Math.min(r, g, b);
                isFg = (lum < 225 || satDelta > 25);
            } else {
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                isFg = (lum > 40);
            }

            if (isFg) {
                const relX = x / targetW;
                const relY = y / targetH;
                const normX = gb.normX + relX * gb.normW;
                const normY = gb.normY + relY * gb.normH;

                // Check exclusion distance if specified (0 = use entire graphic)
                if (excludeRadius > 0) {
                    const distToFw = Math.hypot((normX - excludeX) * 1.25, normY - excludeY);
                    if (distToFw >= excludeRadius) {
                        candidates.push({ x, y, r, g, b, normX, normY });
                    }
                } else {
                    candidates.push({ x, y, r, g, b, normX, normY });
                }
            }
        }
    }

    // Fallback if exclusion zone was too large: accept any foreground pixel
    if (candidates.length < targetCount) {
        for (let y = 3; y < targetH - 3; y += step * 2) {
            for (let x = 3; x < targetW - 3; x += step * 2) {
                const idx = (y * targetW + x) * 4;
                const a = data[idx + 3];
                if (a > 40) {
                    const relX = x / targetW;
                    const relY = y / targetH;
                    const normX = gb.normX + relX * gb.normW;
                    const normY = gb.normY + relY * gb.normH;
                    candidates.push({ x, y, r: data[idx], g: data[idx + 1], b: data[idx + 2], normX, normY });
                }
            }
        }
    }

    if (candidates.length === 0) return [];

    // Farthest Point Sampling
    const numCandidates = candidates.length;
    const countToPick = Math.min(targetCount, numCandidates);
    const minDist = new Float32Array(numCandidates).fill(1e9);
    const selected = [];

    let startIdx = Math.floor(numCandidates / 2);
    selected.push(candidates[startIdx]);

    for (let i = 0; i < numCandidates; i++) {
        const dx = candidates[i].normX - candidates[startIdx].normX;
        const dy = candidates[i].normY - candidates[startIdx].normY;
        minDist[i] = dx * dx + dy * dy;
    }

    for (let k = 1; k < countToPick; k++) {
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
            const dx = candidates[i].normX - chosen.normX;
            const dy = candidates[i].normY - chosen.normY;
            const d = dx * dx + dy * dy;
            if (d < minDist[i]) {
                minDist[i] = d;
            }
        }
    }

    const result = [];
    for (let i = 0; i < selected.length; i++) {
        const p = selected[i];
        let col = boostLedVibrancy(p.r, p.g, p.b, (p.normX - gb.normX) / gb.normW, (p.normY - gb.normY) / gb.normH);
        result.push({
            x: Math.max(0.05, Math.min(0.95, parseFloat(p.normX.toFixed(4)))),
            y: Math.max(0.05, Math.min(0.95, parseFloat(p.normY.toFixed(4)))),
            color: col
        });
    }

    return result;
}

let activeFireworksGroupId = null;

function getActiveFireworksGroup() {
    const fwGroups = animationGroups.filter(g => g.effect === 'fireworks');
    if (fwGroups.length === 0) return null;
    if (activeFireworksGroupId) {
        const found = fwGroups.find(g => g.id === activeFireworksGroupId);
        if (found) return found;
    }
    return fwGroups[fwGroups.length - 1]; // Default to most recent
}

function updateActiveFwDropdown() {
    const fwRow = document.getElementById('activeFwRow');
    const select = document.getElementById('activeFwSelect');
    if (!select || !fwRow) return;

    const fwGroups = animationGroups.filter(g => g.effect === 'fireworks');
    if (fwGroups.length <= 1) {
        fwRow.style.display = 'none';
        return;
    }

    fwRow.style.display = 'block';
    select.innerHTML = '';
    fwGroups.forEach((g) => {
        const opt = document.createElement('option');
        opt.value = g.id;
        opt.textContent = `${g.name} (${g.fireworkColor || '#ffb703'})`;
        if (g.id === activeFireworksGroupId) {
            opt.selected = true;
        }
        select.appendChild(opt);
    });
}

function deleteFireworksGroup(groupId) {
    const idx = animationGroups.findIndex(g => g.id === groupId);
    if (idx === -1) return;
    const name = animationGroups[idx].name;
    animationGroups.splice(idx, 1);

    // Remove cues for this fireworks group
    sequenceCues = sequenceCues.filter(q => q.groupId !== groupId);

    const remainingFwGroups = animationGroups.filter(g => g.effect === 'fireworks');
    activeFireworksGroupId = remainingFwGroups.length > 0 ? remainingFwGroups[remainingFwGroups.length - 1].id : null;

    if (remainingFwGroups.length > 0) {
        redistributeRemainingNonFireworkLeds();
    } else {
        // All fireworks removed: re-sample all 100 LEDs across graphic
        scatterLedsOnGraphic(currentGraphicType, 100);
    }

    rebuildLedGroupMap();
    renderActiveGroupsList();
    updateActiveFwDropdown();
    renderCuesList();
    renderTimelineCueStrip();
    updateTimelineScrubberUI();
    showToast(`🗑️ Removed ${name}! Total LEDs: ${leds.length}.`);
}

function generateFireworksCluster(centerNormX = 0.28, centerNormY = 0.22, rays = 5, ledsPerRay = 4, burstRadius = 0.13, redistributeRemaining = true, forceHexColor = null) {
    const existingFwGroups = animationGroups.filter(g => g.effect === 'fireworks');
    const newFwCount = rays * ledsPerRay;

    // Check existing fireworks LED data to preserve their positions
    const existingFwData = existingFwGroups.map(g => ({
        group: g,
        leds: g.ledIndices.map(idx => ({ ...leds[idx] }))
    }));
    const totalExistingFwLeds = existingFwData.reduce((sum, d) => sum + d.leds.length, 0);

    if (totalExistingFwLeds + newFwCount > 80) {
        showToast('⚠️ Maximum fireworks capacity reached (at least 20 LEDs reserved for float artwork)!');
        return;
    }

    const totalAllFwLeds = totalExistingFwLeds + newFwCount;
    const remainingCount = 100 - totalAllFwLeds;

    // Determine single uniform color for this firework: ALL rays of this group share this exact color!
    const FW_PALETTE = ['#ffb703', '#00e5ff', '#ff3366', '#76ff03', '#d500f9', '#ff3d00', '#ffffff'];
    let chosenHex = forceHexColor;
    if (!chosenHex) {
        const colorSelect = document.getElementById('fwColorSelect');
        const colorVal = colorSelect?.value || '#ffb703';
        const customPicker = document.getElementById('fwCustomColorPicker');
        chosenHex = (colorVal === 'custom') ? (customPicker?.value || '#ffb703') :
                    (colorVal === 'rainbow') ? (FW_PALETTE[existingFwGroups.length % FW_PALETTE.length]) : colorVal;
    }
    const chosenRgb = hexToRgb(chosenHex) || { r: 255, g: 195, b: 45 };

    // 1. Generate New Firework LEDs in Serpentine order (ALL rays have chosenRgb!)
    const newFwLeds = [];
    for (let r = 0; r < rays; r++) {
        const theta = -Math.PI / 2 + r * ((2 * Math.PI) / rays);
        for (let p = 0; p < ledsPerRay; p++) {
            const step = (r % 2 === 1) ? (ledsPerRay - 1 - p) : p;
            const normDist = step / Math.max(1, ledsPerRay - 1);
            const rad = 0.025 + normDist * (burstRadius - 0.025);

            const nx = centerNormX + Math.cos(theta) * rad * 0.82;
            const ny = centerNormY + Math.sin(theta) * rad;

            newFwLeds.push({
                x: Math.max(0.08, Math.min(0.92, parseFloat(nx.toFixed(4)))),
                y: Math.max(0.08, Math.min(0.92, parseFloat(ny.toFixed(4)))),
                color: { r: chosenRgb.r, g: chosenRgb.g, b: chosenRgb.b }
            });
        }
    }

    // 2. Generate remaining non-firework LEDs across ENTIRE graphic to guarantee exactly 100 LEDs
    let nonFwLeds = sampleRemainingGraphicLeds(remainingCount, 0, 0, 0);
    if (nonFwLeds.length > remainingCount) {
        nonFwLeds = nonFwLeds.slice(0, remainingCount);
    } else if (nonFwLeds.length < remainingCount) {
        const filler = sampleRemainingGraphicLeds(remainingCount - nonFwLeds.length, 0, 0, 0);
        nonFwLeds = nonFwLeds.concat(filler);
    }
    nonFwLeds = optimizeLedWiringOrder(nonFwLeds, 'bottom-left');

    // 3. Assemble full array: [nonFwLeds, existingFw1, existingFw2, ..., newFwLeds]
    let newLeds = [...nonFwLeds];
    let currentIdx = nonFwLeds.length;

    // Preserve existing fireworks and re-index their ledIndices
    existingFwData.forEach(d => {
        const newIndices = [];
        d.leds.forEach(l => {
            newLeds.push(l);
            newIndices.push(currentIdx++);
        });
        d.group.ledIndices = newIndices;
    });

    // Append new firework LEDs
    const newFwIndices = [];
    newFwLeds.forEach(l => {
        newLeds.push(l);
        newFwIndices.push(currentIdx++);
    });

    leds = newLeds;
    while (sparkles.length < leds.length) sparkles.push(0);

    // 4. Create new Animation Group for this firework
    const fwNum = existingFwGroups.length + 1;
    const fwGroup = {
        id: 'grp_fireworks_' + Date.now(),
        name: `Fireworks #${fwNum} (${rays}R x ${ledsPerRay}L)`,
        ledIndices: newFwIndices,
        effect: 'fireworks',
        speedBpm: 120,
        direction: 1,
        width: 3,
        colorMode: 'custom',
        fireworkColor: chosenHex,
        customColor: chosenRgb,
        fireworkRays: rays,
        fireworkLedsPerRay: ledsPerRay,
        wiringMode: 'serpentine',
        centerNormX: centerNormX,
        centerNormY: centerNormY,
        burstRadius: burstRadius,
        baselineEffect: 'off'
    };
    animationGroups.push(fwGroup);
    activeFireworksGroupId = fwGroup.id;

    rebuildLedGroupMap();
    renderActiveGroupsList();
    updateActiveFwDropdown();
    syncFireworksSliders(centerNormX, centerNormY, burstRadius, chosenHex);

    // Select the newly created firework group on canvas
    selectedLeds.clear();
    for (const idx of newFwIndices) selectedLeds.add(idx);
    selectedLed = newFwIndices[0];
    updateLedInspectorUI();
    updateLedCountUI();

    // Auto-place explosion cues on Master Timeline in Parade Cue Director!
    autoPlaceFireworksCues(fwGroup, false);

    showToast(`🎆 Created ${fwGroup.name} (All Rays ${chosenHex}) at (${Math.round(centerNormX*100)}%, ${Math.round(centerNormY*100)}%)! Total LEDs: ${leds.length}.`);
}

function redistributeRemainingNonFireworkLeds() {
    const fwGroups = animationGroups.filter(g => g.effect === 'fireworks');
    if (fwGroups.length === 0) {
        showToast('⚠️ No active Fireworks group found. Stamp a fireworks cluster first!');
        return;
    }

    // Collect all firework LEDs
    const allFwLeds = [];
    fwGroups.forEach(g => {
        g.ledIndices.forEach(idx => {
            if (leds[idx]) allFwLeds.push({ ...leds[idx] });
        });
    });

    const totalFwCount = allFwLeds.length;
    const remainingCount = 100 - totalFwCount;

    let nonFwLeds = sampleRemainingGraphicLeds(remainingCount, 0, 0, 0);
    if (nonFwLeds.length > remainingCount) nonFwLeds = nonFwLeds.slice(0, remainingCount);
    else if (nonFwLeds.length < remainingCount) {
        nonFwLeds = nonFwLeds.concat(sampleRemainingGraphicLeds(remainingCount - nonFwLeds.length, 0, 0, 0));
    }
    nonFwLeds = optimizeLedWiringOrder(nonFwLeds, 'bottom-left');

    let newLeds = [...nonFwLeds];
    let currentIdx = nonFwLeds.length;

    fwGroups.forEach(g => {
        const newIndices = [];
        const count = g.ledIndices.length;
        for (let i = 0; i < count; i++) {
            newLeds.push(allFwLeds.shift());
            newIndices.push(currentIdx++);
        }
        g.ledIndices = newIndices;
    });

    leds = newLeds;
    while (sparkles.length < leds.length) sparkles.push(0);

    rebuildLedGroupMap();
    renderActiveGroupsList();
    updateActiveFwDropdown();
    updateLedCountUI();
    updateLedInspectorUI();

    showToast(`🔄 Re-distributed non-firework LEDs across the entire graphic (100 total LEDs preserved, ${fwGroups.length} fireworks intact)!`);
}

function updateFireworksLedPositions(fwGroup, cx, cy, radius) {
    if (!fwGroup || !fwGroup.ledIndices || fwGroup.ledIndices.length === 0) return;
    const rays = fwGroup.fireworkRays || 5;
    const ledsPerRay = fwGroup.fireworkLedsPerRay || 4;
    fwGroup.centerNormX = cx;
    fwGroup.centerNormY = cy;
    fwGroup.burstRadius = radius;

    let pIdx = 0;
    for (let r = 0; r < rays; r++) {
        const theta = -Math.PI / 2 + r * ((2 * Math.PI) / rays);
        for (let p = 0; p < ledsPerRay; p++) {
            if (pIdx >= fwGroup.ledIndices.length) break;
            const ledIdx = fwGroup.ledIndices[pIdx++];
            if (!leds[ledIdx]) continue;

            const step = (r % 2 === 1) ? (ledsPerRay - 1 - p) : p;
            const normDist = step / Math.max(1, ledsPerRay - 1);
            const rad = 0.025 + normDist * (radius - 0.025);
            const nx = cx + Math.cos(theta) * rad * 0.82;
            const ny = cy + Math.sin(theta) * rad;

            leds[ledIdx].x = Math.max(0.05, Math.min(0.95, parseFloat(nx.toFixed(4))));
            leds[ledIdx].y = Math.max(0.05, Math.min(0.95, parseFloat(ny.toFixed(4))));
        }
    }
    updateLedInspectorCoords();
}

function highlightRadiusPresetButtons(rPct) {
    const presets = [
        { id: 'fwRadiusSmBtn', grpId: 'groupFwRadiusSmBtn', val: 8 },
        { id: 'fwRadiusMdBtn', grpId: 'groupFwRadiusMdBtn', val: 13 },
        { id: 'fwRadiusLgBtn', grpId: 'groupFwRadiusLgBtn', val: 18 },
        { id: 'fwRadiusXlBtn', grpId: 'groupFwRadiusXlBtn', val: 24 }
    ];

    presets.forEach(p => {
        const btn = document.getElementById(p.id);
        const grpBtn = document.getElementById(p.grpId);
        const isMatch = Math.abs(rPct - p.val) <= 1;
        if (btn) {
            btn.style.color = isMatch ? '#ff7b72' : '';
            btn.style.fontWeight = isMatch ? '700' : 'normal';
            btn.style.borderColor = isMatch ? '#ff7b72' : '';
        }
        if (grpBtn) {
            grpBtn.style.color = isMatch ? '#ff7b72' : '';
            grpBtn.style.fontWeight = isMatch ? '700' : 'normal';
            grpBtn.style.borderColor = isMatch ? '#ff7b72' : '';
        }
    });
}

function setFireworksRadius(radPct) {
    const rad = radPct / 100;
    const fwGroup = getActiveFireworksGroup();
    if (fwGroup) {
        fwGroup.burstRadius = rad;
        const cx = fwGroup.centerNormX || (parseInt(document.getElementById('fwPosXSlider')?.value || '28', 10) / 100);
        const cy = fwGroup.centerNormY || (parseInt(document.getElementById('fwPosYSlider')?.value || '22', 10) / 100);
        updateFireworksLedPositions(fwGroup, cx, cy, rad);
        syncFireworksSliders(cx, cy, rad, fwGroup.fireworkColor);
        showToast(`🔍 Scaled ${fwGroup.name} burst radius to ${radPct}%`);
    } else {
        syncFireworksSliders(undefined, undefined, rad);
    }
}

function syncFireworksSliders(cx, cy, radius, color) {
    const xSlider = document.getElementById('fwPosXSlider');
    const xVal = document.getElementById('fwPosXVal');
    const ySlider = document.getElementById('fwPosYSlider');
    const yVal = document.getElementById('fwPosYVal');
    const rSlider = document.getElementById('fwRadiusSlider');
    const rVal = document.getElementById('fwRadiusVal');
    const groupRSlider = document.getElementById('groupFwRadiusSlider');
    const groupRVal = document.getElementById('groupFwRadiusVal');
    const colorSelect = document.getElementById('fwColorSelect');
    const customPicker = document.getElementById('fwCustomColorPicker');

    if (xSlider && cx !== undefined) {
        const xPct = Math.round(cx * 100);
        xSlider.value = xPct;
        if (xVal) xVal.textContent = `${xPct}%`;
    }
    if (ySlider && cy !== undefined) {
        const yPct = Math.round(cy * 100);
        ySlider.value = yPct;
        if (yVal) yVal.textContent = `${yPct}%`;
    }
    if (radius !== undefined) {
        const rPct = Math.round(radius * 100);
        if (rSlider) rSlider.value = rPct;
        if (rVal) rVal.textContent = `${rPct}%`;
        if (groupRSlider) groupRSlider.value = rPct;
        if (groupRVal) groupRVal.textContent = `${rPct}%`;
        highlightRadiusPresetButtons(rPct);
    }
    if (color && colorSelect) {
        const standardOptions = ['rainbow', '#ffb703', '#00e5ff', '#ff3366', '#76ff03', '#d500f9', '#ff3d00', '#ffffff'];
        if (standardOptions.includes(color)) {
            colorSelect.value = color;
            if (customPicker) customPicker.style.display = 'none';
        } else {
            colorSelect.value = 'custom';
            if (customPicker) {
                customPicker.style.display = 'block';
                customPicker.value = color;
            }
        }
    }
}

function applyFireworksColor(colorVal) {
    const customPicker = document.getElementById('fwCustomColorPicker');
    if (customPicker) {
        customPicker.style.display = (colorVal === 'custom') ? 'block' : 'none';
    }
    const hex = (colorVal === 'custom') ? (customPicker?.value || '#ffb703') : colorVal;
    const chosenRgb = hexToRgb(hex) || { r: 255, g: 195, b: 45 };

    const fwGroup = getActiveFireworksGroup();
    if (fwGroup) {
        fwGroup.fireworkColor = hex;
        fwGroup.colorMode = 'custom';
        fwGroup.customColor = chosenRgb;

        // All rays of this firework group share the exact same uniform color!
        for (const ledIdx of fwGroup.ledIndices) {
            if (leds[ledIdx]) {
                leds[ledIdx].color = { r: chosenRgb.r, g: chosenRgb.g, b: chosenRgb.b };
            }
        }
        updateActiveFwDropdown();
        updateLedInspectorUI();
    }
}

function setFireworksPositionPreset(preset) {
    let cx = 0.28, cy = 0.22;
    if (preset === 'top-right') {
        cx = 0.72; cy = 0.22;
    } else if (preset === 'center') {
        cx = 0.50; cy = 0.34;
    }

    const tlBtn = document.getElementById('fwPosTopLeftBtn');
    const trBtn = document.getElementById('fwPosTopRightBtn');
    const cBtn = document.getElementById('fwPosCenterBtn');
    [tlBtn, trBtn, cBtn].forEach(b => {
        if (b) {
            b.style.color = '';
            b.style.fontWeight = 'normal';
        }
    });
    const activeBtn = preset === 'top-left' ? tlBtn : (preset === 'top-right' ? trBtn : cBtn);
    if (activeBtn) {
        activeBtn.style.color = '#ff7b72';
        activeBtn.style.fontWeight = '600';
    }

    const fwGroup = getActiveFireworksGroup();
    if (fwGroup) {
        const rad = fwGroup.burstRadius || (parseInt(document.getElementById('fwRadiusSlider')?.value || '13', 10) / 100);
        updateFireworksLedPositions(fwGroup, cx, cy, rad);
        syncFireworksSliders(cx, cy, rad, fwGroup.fireworkColor);
    } else {
        syncFireworksSliders(cx, cy);
    }
}

// Fireworks Starburst Generator Event Listeners
const fwPosTopLeftBtn = document.getElementById('fwPosTopLeftBtn');
const fwPosTopRightBtn = document.getElementById('fwPosTopRightBtn');
const fwPosCenterBtn = document.getElementById('fwPosCenterBtn');
const fwPosXSlider = document.getElementById('fwPosXSlider');
const fwPosXVal = document.getElementById('fwPosXVal');
const fwPosYSlider = document.getElementById('fwPosYSlider');
const fwPosYVal = document.getElementById('fwPosYVal');
const fwRadiusSlider = document.getElementById('fwRadiusSlider');
const fwRadiusVal = document.getElementById('fwRadiusVal');
const fwRaysSelect = document.getElementById('fwRaysSelect');
const fwLedsPerRaySelect = document.getElementById('fwLedsPerRaySelect');
const fwLedCountBadge = document.getElementById('fwLedCountBadge');
const fwColorSelect = document.getElementById('fwColorSelect');
const fwCustomColorPicker = document.getElementById('fwCustomColorPicker');
const stampFwBtn = document.getElementById('stampFireworksBtn');
const redistRemBtn = document.getElementById('redistributeRemainingBtn');
const fwAddCueBtn = document.getElementById('fwAddCueBtn');
const activeFwSelect = document.getElementById('activeFwSelect');
const removeActiveFwBtn = document.getElementById('removeActiveFwBtn');

if (activeFwSelect) {
    activeFwSelect.addEventListener('change', (e) => {
        activeFireworksGroupId = e.target.value;
        const fwGroup = getActiveFireworksGroup();
        if (fwGroup) {
            syncFireworksSliders(fwGroup.centerNormX, fwGroup.centerNormY, fwGroup.burstRadius, fwGroup.fireworkColor);
            selectedLeds.clear();
            for (const idx of fwGroup.ledIndices) selectedLeds.add(idx);
            selectedLed = fwGroup.ledIndices[0];
            updateLedInspectorUI();
        }
    });
}

if (removeActiveFwBtn) {
    removeActiveFwBtn.addEventListener('click', () => {
        if (activeFireworksGroupId) {
            deleteFireworksGroup(activeFireworksGroupId);
        }
    });
}

if (fwPosTopLeftBtn) fwPosTopLeftBtn.addEventListener('click', () => setFireworksPositionPreset('top-left'));
if (fwPosTopRightBtn) fwPosTopRightBtn.addEventListener('click', () => setFireworksPositionPreset('top-right'));
if (fwPosCenterBtn) fwPosCenterBtn.addEventListener('click', () => setFireworksPositionPreset('center'));

if (fwColorSelect) {
    fwColorSelect.addEventListener('change', (e) => applyFireworksColor(e.target.value));
}
if (fwCustomColorPicker) {
    fwCustomColorPicker.addEventListener('input', (e) => applyFireworksColor('custom'));
}

if (fwPosXSlider) {
    fwPosXSlider.addEventListener('input', (e) => {
        const cx = parseInt(e.target.value, 10) / 100;
        if (fwPosXVal) fwPosXVal.textContent = `${e.target.value}%`;
        const fwGroup = getActiveFireworksGroup();
        if (fwGroup) {
            const cy = fwGroup.centerNormY || (parseInt(fwPosYSlider?.value || '22', 10) / 100);
            const rad = fwGroup.burstRadius || (parseInt(fwRadiusSlider?.value || '13', 10) / 100);
            updateFireworksLedPositions(fwGroup, cx, cy, rad);
        }
    });
}

if (fwPosYSlider) {
    fwPosYSlider.addEventListener('input', (e) => {
        const cy = parseInt(e.target.value, 10) / 100;
        if (fwPosYVal) fwPosYVal.textContent = `${e.target.value}%`;
        const fwGroup = getActiveFireworksGroup();
        if (fwGroup) {
            const cx = fwGroup.centerNormX || (parseInt(fwPosXSlider?.value || '28', 10) / 100);
            const rad = fwGroup.burstRadius || (parseInt(fwRadiusSlider?.value || '13', 10) / 100);
            updateFireworksLedPositions(fwGroup, cx, cy, rad);
        }
    });
}

if (fwRadiusSlider) {
    fwRadiusSlider.addEventListener('input', (e) => {
        const radPct = parseInt(e.target.value, 10);
        setFireworksRadius(radPct);
    });
}

const groupFwRadiusSlider = document.getElementById('groupFwRadiusSlider');
if (groupFwRadiusSlider) {
    groupFwRadiusSlider.addEventListener('input', (e) => {
        const radPct = parseInt(e.target.value, 10);
        setFireworksRadius(radPct);
    });
}

// Preset button handlers in Fireworks Generator Card
document.getElementById('fwRadiusSmBtn')?.addEventListener('click', () => setFireworksRadius(8));
document.getElementById('fwRadiusMdBtn')?.addEventListener('click', () => setFireworksRadius(13));
document.getElementById('fwRadiusLgBtn')?.addEventListener('click', () => setFireworksRadius(18));
document.getElementById('fwRadiusXlBtn')?.addEventListener('click', () => setFireworksRadius(24));

// Preset button handlers in Group Inspector Card
document.getElementById('groupFwRadiusSmBtn')?.addEventListener('click', () => setFireworksRadius(8));
document.getElementById('groupFwRadiusMdBtn')?.addEventListener('click', () => setFireworksRadius(13));
document.getElementById('groupFwRadiusLgBtn')?.addEventListener('click', () => setFireworksRadius(18));
document.getElementById('groupFwRadiusXlBtn')?.addEventListener('click', () => setFireworksRadius(24));

function updateFwBadge() {
    if (!fwRaysSelect || !fwLedsPerRaySelect || !fwLedCountBadge) return;
    const rays = parseInt(fwRaysSelect.value, 10) || 5;
    const lpr = parseInt(fwLedsPerRaySelect.value, 10) || 4;
    const total = rays * lpr;
    fwLedCountBadge.textContent = `${total} LEDs (${100 - total} Other)`;
}

if (fwRaysSelect) fwRaysSelect.addEventListener('change', updateFwBadge);
if (fwLedsPerRaySelect) fwLedsPerRaySelect.addEventListener('change', updateFwBadge);

function autoPlaceFireworksCues(fwGroup, clearExisting = false) {
    if (!fwGroup) return;

    if (clearExisting) {
        sequenceCues = sequenceCues.filter(q => !(q.effect === 'fireworks' || q.groupId === fwGroup.id || (q.groupName && q.groupName.toLowerCase().includes('fireworks'))));
    }

    const existingFwCues = sequenceCues.filter(q => q.groupId === fwGroup.id);

    if (existingFwCues.length > 0 && !clearExisting) {
        // Update existing cues with latest group name, ID, and speed
        existingFwCues.forEach(q => {
            q.groupId = fwGroup.id;
            q.groupName = fwGroup.name;
            q.effect = 'fireworks';
            q.speedBpm = fwGroup.speedBpm || 120;
        });
    } else {
        // Ensure baseline background cue if timeline has no global cues
        const hasGlobalCue = sequenceCues.some(q => q.targetType === 'global');
        if (!hasGlobalCue) {
            sequenceCues.push({
                id: 'cue_bg_' + Date.now(),
                name: 'Parade Starlight Sparkle (Float)',
                startTime: 0.0,
                duration: sequenceLoopDuration || 90.0,
                targetType: 'global',
                groupId: '',
                groupName: '',
                effect: 'steady_sparkle',
                speedBpm: 120,
                fadeIn: 1.0,
                fadeOut: 1.0
            });
        }

        // Stagger bursts based on which fireworks group this is (+2.5s per firework group)
        const fwGroups = animationGroups.filter(g => g.effect === 'fireworks');
        const fwIdx = Math.max(0, fwGroups.findIndex(g => g.id === fwGroup.id));
        const stagger = fwIdx * 2.5;

        // Generate evenly spaced bursts across sequence loop duration
        const duration = sequenceLoopDuration || 90.0;
        const baseBurstTimes = [];
        if (duration <= 25) {
            baseBurstTimes.push(3.0);
        } else if (duration <= 50) {
            baseBurstTimes.push(4.0, 24.0);
        } else if (duration <= 75) {
            baseBurstTimes.push(5.0, 26.0, 48.0);
        } else {
            // E.g. 90s loop: 4 bursts spaced across the show
            baseBurstTimes.push(6.0, 28.0, 52.0, 74.0);
        }

        baseBurstTimes.forEach((bTime, i) => {
            const burstTime = parseFloat(((bTime + stagger) % Math.max(10, duration - 5)).toFixed(1));
            sequenceCues.push({
                id: `cue_fw_${Date.now()}_${fwGroup.id}_${i}`,
                name: `🎆 ${fwGroup.name} Burst #${i + 1}`,
                startTime: burstTime,
                duration: 4.5,
                targetType: 'group',
                groupId: fwGroup.id,
                groupName: fwGroup.name,
                effect: 'fireworks',
                speedBpm: fwGroup.speedBpm || 120,
                fadeIn: 0.1,
                fadeOut: 0.8
            });
        });

        sequenceCues.sort((a, b) => a.startTime - b.startTime);
    }

    renderCuesList();
    renderTimelineCueStrip();
    updateTimelineScrubberUI();

    if (!sequenceMode) {
        toggleSequenceMode(true);
    }
}

if (stampFwBtn) {
    stampFwBtn.addEventListener('click', () => {
        const rays = parseInt(fwRaysSelect?.value || '5', 10);
        const lpr = parseInt(fwLedsPerRaySelect?.value || '4', 10);
        const radPct = parseInt(fwRadiusSlider?.value || '13', 10);
        const burstRadius = radPct / 100;

        const existingFw = animationGroups.filter(g => g.effect === 'fireworks');
        // Preset offset coordinates so additional fireworks are clearly visible side-by-side above race bib
        const offsetPresets = [
            { x: 0.28, y: 0.22 }, // #1 Top-Left
            { x: 0.58, y: 0.26 }, // #2 Upper-Right offset
            { x: 0.38, y: 0.40 }, // #3 Lower-Mid offset
            { x: 0.72, y: 0.22 }  // #4 Far Top-Right
        ];

        let cx, cy;
        if (existingFw.length === 0) {
            cx = parseInt(fwPosXSlider?.value || '28', 10) / 100;
            cy = parseInt(fwPosYSlider?.value || '22', 10) / 100;
        } else {
            const nextPreset = offsetPresets[existingFw.length % offsetPresets.length];
            cx = nextPreset.x;
            cy = nextPreset.y;
        }

        const FW_PALETTE = ['#ffb703', '#00e5ff', '#ff3366', '#76ff03', '#d500f9', '#ff3d00', '#ffffff'];
        const colorVal = fwColorSelect?.value;
        let colorToUse = null;
        if (existingFw.length > 0) {
            colorToUse = FW_PALETTE[existingFw.length % FW_PALETTE.length];
            if (fwColorSelect) fwColorSelect.value = colorToUse;
        } else {
            colorToUse = (colorVal === 'custom') ? (fwCustomColorPicker?.value || '#ffb703') : (colorVal || '#ffb703');
        }

        generateFireworksCluster(cx, cy, rays, lpr, burstRadius, true, colorToUse);
    });
}

if (redistRemBtn) {
    redistRemBtn.addEventListener('click', () => {
        redistributeRemainingNonFireworkLeds();
    });
}

const fwAutoScheduleBtn = document.getElementById('fwAutoScheduleBtn');
if (fwAutoScheduleBtn) {
    fwAutoScheduleBtn.addEventListener('click', () => {
        let fwGroup = getActiveFireworksGroup();
        if (!fwGroup) {
            stampFwBtn?.click();
            fwGroup = getActiveFireworksGroup();
        }
        if (!fwGroup) return;
        autoPlaceFireworksCues(fwGroup, true);
        showToast(`⚡ Auto-scheduled recurring bursts for ${fwGroup.name} across timeline!`);
    });
}

if (fwAddCueBtn) {
    fwAddCueBtn.addEventListener('click', () => {
        let fwGroup = getActiveFireworksGroup();
        if (!fwGroup) {
            stampFwBtn?.click();
            fwGroup = getActiveFireworksGroup();
        }
        if (!fwGroup) {
            showToast('⚠️ Please stamp a fireworks cluster first!');
            return;
        }

        const startSec = Math.min(sequenceLoopDuration - 4, Math.floor(sequenceTime));
        addCue({
            name: `🎆 ${fwGroup.name} Burst`,
            startTime: startSec,
            duration: 4.5,
            targetType: 'group',
            groupId: fwGroup.id,
            groupName: fwGroup.name,
            effect: 'fireworks',
            speedBpm: fwGroup.speedBpm || 120,
            fadeIn: 0.1,
            fadeOut: 0.8
        });

        if (!sequenceMode) {
            toggleSequenceMode(true);
        } else {
            renderCuesList();
            renderTimelineCueStrip();
            updateTimelineScrubberUI();
        }
        showToast(`🎆 Added ${fwGroup.name} explosion cue at ${startSec.toFixed(1)}s on timeline!`);
    });
}

// Preset Buttons
document.getElementById('presetSelect').addEventListener('change', (e) => {
    loadProfile(e.target.value);
});

// Export complete profile configuration JSON
function exportCurrentProfileJson() {
    const nameInput = document.getElementById('profileNameInput');
    const name = (nameInput?.value || '').trim() || (currentGraphicType === 'cinderellas_coach' ? "Cinderella_Coach" : (currentGraphicType === 'carriage_nohorses' ? "Carriage_nohorses" : "Petes_Dragon"));
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
        },
        sequence: {
            loopDuration: sequenceLoopDuration,
            cues: sequenceCues
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
    const defaultName = currentGraphicType === 'cinderellas_coach' ? "Cinderella's Coach" : (currentGraphicType === 'carriage_nohorses' ? "Carriage (No Horses)" : "Pete's Dragon");
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

    if (sequenceCues.length > 0) {
        const paletteLines = [];
        for (let i = 0; i < leds.length; i++) {
            const c = leds[i].color || { r: 0, g: 255, b: 100 };
            paletteLines.push(`    CRGB(${c.r}, ${c.g}, ${c.b})${i < leds.length - 1 ? ',' : ''} // LED ${i}`);
        }

        const cueCommentLines = sequenceCues.map((q, idx) => 
            `// Cue ${idx + 1}: "${q.name}" [${q.startTime.toFixed(1)}s - ${(q.startTime + q.duration).toFixed(1)}s] -> Layer: ${q.targetType.toUpperCase()}${q.targetType === 'group' ? ` (${q.groupName})` : ''} | Effect: ${q.effect} (${q.speedBpm} BPM)`
        ).join('\n');

        code = `// ============================================================================
// FASTLED AUTONOMOUS SHOW SEQUENCE: ${currentGraphicType.toUpperCase()}
// Loop Duration: ${sequenceLoopDuration}s (${sequenceCues.length} Cues)
// Generated by Parade Cue Director - kidmd/WDW-costumes
// ============================================================================
#define NUM_LEDS ${leds.length}
#define SHOW_LOOP_MS ${(sequenceLoopDuration * 1000).toFixed(0)}

// Artwork Sampled Color Palette (PROGMEM flash storage)
const CRGB PROGMEM ARTWORK_PALETTE[NUM_LEDS] = {
${paletteLines.join('\n')}
};

// --- Show Sequence Cue List ---
${cueCommentLines}

void runAutonomousShowSequence(uint32_t now) {
    uint32_t seqTime = now % SHOW_LOOP_MS;

    // Default base color
    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i].r = pgm_read_byte(&ARTWORK_PALETTE[i].r);
        leds[i].g = pgm_read_byte(&ARTWORK_PALETTE[i].g);
        leds[i].b = pgm_read_byte(&ARTWORK_PALETTE[i].b);
    }

${sequenceCues.map((q, idx) => {
    const startMs = Math.round(q.startTime * 1000);
    const endMs = Math.round((q.startTime + q.duration) * 1000);
    return `    // Cue ${idx + 1}: ${q.name} (${startMs}ms - ${endMs}ms)\n    if (seqTime >= ${startMs} && seqTime < ${endMs}) {\n        // Active effect: ${q.effect} @ ${q.speedBpm} BPM\n    }`;
}).join('\n\n')}

    FastLED.show();
}`;
    } else if (hasAnyColors) {
        const paletteLines = [];
        for (let i = 0; i < leds.length; i++) {
            const c = leds[i].color || { r: 0, g: 255, b: 100 };
            paletteLines.push(`    CRGB(${c.r}, ${c.g}, ${c.b})${i < leds.length - 1 ? ',' : ''} // LED ${i}`);
        }

        const sparkleThreshold = Math.max(1, Math.round(params.sparkleRate * 65.5));

        if (activePattern === 'steady_sparkle') {
            code = `// ============================================================================
// FASTLED ANIMATION: ${currentGraphicType.toUpperCase()} ${leds.length}-LED STEADY COLOR + SPARKLES
// Generated by MSEP Simulator - kidmd/WDW-costumes
// ============================================================================
#define NUM_LEDS ${leds.length}

// Artwork Sampled Color Palette (PROGMEM flash storage)
const CRGB PROGMEM ARTWORK_PALETTE[NUM_LEDS] = {
${paletteLines.join('\n')}
};

void renderCostumeCustom(uint32_t t) {
    for (int i = 0; i < NUM_LEDS; i++) {
        // Steady baseline color (no breathing pulse)
        CRGB baseColor;
        baseColor.r = pgm_read_byte(&ARTWORK_PALETTE[i].r);
        baseColor.g = pgm_read_byte(&ARTWORK_PALETTE[i].g);
        baseColor.b = pgm_read_byte(&ARTWORK_PALETTE[i].b);
        leds[i] = baseColor;

        // Occasional Incandescent Starlight Sparkles (Rate: ${params.sparkleRate.toFixed(2)}%)
        if (random16() < ${sparkleThreshold}) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
}`;
        } else {
            code = `// ============================================================================
// FASTLED ANIMATION: ${currentGraphicType.toUpperCase()} ${leds.length}-LED COLOR-MATCHED COSTUME
// Generated by MSEP Simulator - kidmd/WDW-costumes
// ============================================================================
#define NUM_LEDS ${leds.length}

// Artwork Sampled Color Palette (PROGMEM flash storage)
const CRGB PROGMEM ARTWORK_PALETTE[NUM_LEDS] = {
${paletteLines.join('\n')}
};

void renderCostumeCustom(uint32_t t) {
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

        // Incandescent Starlight Sparkles (Rate: ${params.sparkleRate.toFixed(2)}%)
        if (random16() < ${sparkleThreshold}) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
}`;
        }
    } else {
        code = `// ============================================================================
// FASTLED ANIMATION: ${currentGraphicType.toUpperCase()} FLOAT (GENERATED BY SIMULATOR)
// ============================================================================
#define NUM_LEDS ${leds.length}
void renderCostumeCustom(uint32_t t) {
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

// ============================================================================
// SIDEBAR TASK TABS & TIMELINE COLLAPSE (THOROUGHBRED UI)
// ============================================================================
function switchSidebarTab(targetTabId) {
    const tabBtns = document.querySelectorAll('.sidebar-tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    tabBtns.forEach(btn => {
        const isTarget = btn.getAttribute('data-tab') === targetTabId;
        btn.classList.toggle('active', isTarget);
    });
    tabPanels.forEach(panel => {
        const isTarget = panel.id === targetTabId;
        panel.classList.toggle('active', isTarget);
    });
    try {
        localStorage.setItem('msep_active_sidebar_tab', targetTabId);
    } catch (e) {}
}
window.switchSidebarTab = switchSidebarTab;

function initSidebarTabs() {
    const tabBtns = document.querySelectorAll('.sidebar-tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            if (targetId) switchSidebarTab(targetId);
        });
    });

    let savedTab = 'tabLayout';
    try {
        savedTab = localStorage.getItem('msep_active_sidebar_tab') || 'tabLayout';
    } catch (e) {}

    if (document.getElementById(savedTab)) {
        switchSidebarTab(savedTab);
    }
}

function initTimelineCollapse() {
    const timelineCollapseBtn = document.getElementById('timelineCollapseBtn');
    const timelineBar = document.getElementById('timelineBar');
    if (!timelineCollapseBtn || !timelineBar) return;

    function setTimelineCollapsed(collapsed) {
        timelineBar.classList.toggle('collapsed', collapsed);
        timelineCollapseBtn.textContent = collapsed ? '⤢ Expand' : '⤢ Minimize';
        timelineCollapseBtn.title = collapsed ? 'Expand Timeline Tracks' : 'Collapse Timeline Tracks';
        try {
            localStorage.setItem('msep_timeline_collapsed', collapsed ? 'true' : 'false');
        } catch (e) {}
    }

    timelineCollapseBtn.addEventListener('click', () => {
        const isCollapsed = !timelineBar.classList.contains('collapsed');
        setTimelineCollapsed(isCollapsed);
    });

    let savedCollapsed = false;
    try {
        savedCollapsed = localStorage.getItem('msep_timeline_collapsed') === 'true';
    } catch (e) {}

    if (savedCollapsed) {
        setTimelineCollapsed(true);
    }
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initSidebarTabs();
        initTimelineCollapse();
    });
} else {
    initSidebarTabs();
    initTimelineCollapse();
}

