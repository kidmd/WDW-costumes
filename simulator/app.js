// Main Street Electrical Parade - LED Costume Simulator
// Interactive HTML5 Canvas Engine with Preset Management & Realistic Fleet Proportions

const canvas = document.getElementById('simulatorCanvas');
const ctx = canvas.getContext('2d');

// State
let currentView = 'single'; // 'single' or 'fleet'
const savedActiveSlot = localStorage.getItem('msep_active_single_shirt_slot');
let activeSingleShirtRunnerSlot = (savedActiveSlot !== null && !isNaN(parseInt(savedActiveSlot, 10)) && parseInt(savedActiveSlot, 10) >= 0 && parseInt(savedActiveSlot, 10) <= 6)
    ? parseInt(savedActiveSlot, 10)
    : 0; // Default to Float 1: The Train (Casey Jr.)
let isSingleShirtDirty = false; // True when unsaved modifications exist in single shirt editor
let lastSingleShirtTab = 'tabLayout'; // Tracks active single-shirt tab prior to entering Fleet view
let activePattern = 'steady_sparkle'; // 'steady_sparkle', 'color_match', 'dragon_sparkle', etc.

// Global Fleet Radar & Attendance Wave State
let rapidRollCallActive = false;
let rapidRollCallStartTime = 0;
let isCorralStandbyActive = false;
let isPhotoModeActive = false;

const DEFAULT_FLEET_RADAR = [
    { id: 1, name: "The Train", role: "LEADER", tag: "CASEY JR.", color: "#ff5e3a", icon: "🚂", status: "ONLINE", rssi: -44, voltage: 5.14, batteryPct: 99, lastSeenSec: 0.2 },
    { id: 2, name: "Title Drum", role: "FOLLOWER", tag: "THE DRUM", color: "#f1e05a", icon: "🥁", status: "ONLINE", rssi: -52, voltage: 5.10, batteryPct: 97, lastSeenSec: 0.5 },
    { id: 3, name: "The Turtle", role: "FOLLOWER", tag: "TURTLE", color: "#2ec4b6", icon: "🐢", status: "ONLINE", rssi: -58, voltage: 5.12, batteryPct: 98, lastSeenSec: 1.1 },
    { id: 4, name: "The Snail", role: "FOLLOWER", tag: "SNAIL", color: "#ff007f", icon: "🐌", status: "ONLINE", rssi: -61, voltage: 5.08, batteryPct: 95, lastSeenSec: 1.4 },
    { id: 5, name: "Cinderella", role: "FOLLOWER", tag: "COACH", color: "#05d9e8", icon: "🩵", status: "ONLINE", rssi: -63, voltage: 5.11, batteryPct: 96, lastSeenSec: 0.8 },
    { id: 6, name: "Pete's Dragon", role: "FOLLOWER", tag: "ELLIOTT", color: "#39ff14", icon: "🐉", status: "ONLINE", rssi: -55, voltage: 5.15, batteryPct: 99, lastSeenSec: 0.4 },
    { id: 7, name: "Flag & Eagle", role: "CO-LEADER", tag: "PATRIOTIC", color: "#388bfd", icon: "🦅", status: "ONLINE", rssi: -69, voltage: 5.09, batteryPct: 94, lastSeenSec: 2.1 }
];

// Dynamic live single shirt editor preset helper
function getLiveSingleShirtPresetData() {
    return {
        name: (document.getElementById('profileNameInput')?.value || '').trim() || `Runner #${(activeSingleShirtRunnerSlot ?? 5) + 1} (Live Edit)`,
        ledCount: leds.length,
        leds: leds,
        graphicType: currentGraphicType,
        customArtworkDataUrl: customArtworkDataUrl,
        animationGroups: animationGroups,
        settings: { ...params, pattern: activePattern },
        sequence: { loopDuration: sequenceLoopDuration, cues: sequenceCues }
    };
}

function markSingleShirtDirty() {
    isSingleShirtDirty = true;
    if (currentView === 'fleet') {
        renderFleetCards();
    }
}

// Control parameters
let params = {
    speedBpm: 48,
    sparkleRate: 1.5,
    sparkleStyle: 'incandescent', // 'incandescent', 'diamond', 'gold'
    ambientColorMode: 'artwork',   // 'artwork', 'float_theme', 'vintage_warm', 'custom'
    ambientCustomColor: '#ffb703',
    direction: 1,                 // 1 = forward, -1 = reverse
    greenHue: 140, // 100 = lime, 140 = emerald, 165 = seafoam (procedural fallback)
    brightness: 85,
    glowSize: 20,
    showWiring: false,
    showWireTension: false,
    showPillSlots: false,
    showTpuWindows: false,
    tpuWindowShape: 'square', // 'square' (3x3mm) or 'round' (Ø 3mm)
    showSymmetryAxis: false,
    liveSymmetryDrag: false,
    showNumbers: false,
    reflectiveShine: true,
    showBib: true,
    bibYOffset: 0.57,
    bibScale: 1.0
};

try {
    const savedShape = localStorage.getItem('msep_tpu_window_shape');
    if (savedShape === 'round' || savedShape === 'square') {
        params.tpuWindowShape = savedShape;
    }
} catch (e) {}

// Default Pete's Dragon Artwork
const defaultDragonImg = new Image();
let defaultDragonLoaded = false;
defaultDragonImg.onload = () => {
    defaultDragonLoaded = true;
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

// Spinning Turtle Artwork (High-res transparent PNG)
const spinningTurtleImg = new Image();
let spinningTurtleLoaded = false;
spinningTurtleImg.onload = () => {
    spinningTurtleLoaded = true;
};
spinningTurtleImg.src = 'assets/Turtle_clean.png';

// Spinning Snail Artwork (High-res transparent PNG)
const spinningSnailImg = new Image();
let spinningSnailLoaded = false;
spinningSnailImg.onload = () => {
    spinningSnailLoaded = true;
};
spinningSnailImg.src = 'assets/spinning_snail.png';

// Custom artwork image (if user uploads one or loads one from preset)
let customArtworkImg = null;
let currentGraphicType = 'builtin_dragon'; // 'builtin_dragon', 'cinderellas_coach', 'carriage_nohorses', 'casey_jr_train', 'title_drum', 'spinning_turtle', 'spinning_snail', 'honor_america_eagle', or 'custom_image'
let customArtworkDataUrl = null;

// Cricut SVG Float Artwork Suite for 7-Runner Lineup
const floatArtworkImgs = {
    'casey_jr_train': new Image(),
    'title_drum': new Image(),
    'spinning_turtle': spinningTurtleImg,
    'spinning_snail': spinningSnailImg,
    'cinderella_coach': new Image(),
    'cinderellas_coach': new Image(),
    'petes_dragon': new Image(),
    'builtin_dragon': new Image(),
    'honor_america_eagle': new Image()
};
floatArtworkImgs['casey_jr_train'].src = 'assets/cricut_svg/casey_jr_train.svg';
floatArtworkImgs['title_drum'].src = 'assets/cricut_svg/title_drum.svg';
floatArtworkImgs['spinning_turtle'].src = 'assets/Turtle_clean.png';
floatArtworkImgs['spinning_snail'].src = 'assets/spinning_snail.png';
floatArtworkImgs['cinderella_coach'].src = 'assets/cricut_svg/cinderella_coach.svg';
floatArtworkImgs['cinderellas_coach'].src = 'assets/cricut_svg/cinderella_coach.svg';
floatArtworkImgs['petes_dragon'].src = 'assets/cricut_svg/petes_dragon.svg';
floatArtworkImgs['builtin_dragon'].src = 'assets/cricut_svg/petes_dragon.svg';
floatArtworkImgs['honor_america_eagle'].src = 'assets/cricut_svg/honor_america_eagle.svg';

function getGraphicImgForType(gType) {
    if (!gType) return defaultDragonImg;
    if (gType === 'custom_image' && customArtworkImg && customArtworkImg.complete && customArtworkImg.naturalWidth > 0) {
        return customArtworkImg;
    }
    if (gType === 'spinning_turtle') {
        if (spinningTurtleImg && spinningTurtleImg.naturalWidth > 0) return spinningTurtleImg;
        return floatArtworkImgs['spinning_turtle'];
    }
    if (gType === 'spinning_snail') {
        if (spinningSnailImg && spinningSnailImg.naturalWidth > 0) return spinningSnailImg;
        return floatArtworkImgs['spinning_snail'];
    }
    if (gType === 'cinderellas_coach' || gType === 'cinderella_coach') {
        if (cinderellasCoachImg && cinderellasCoachImg.naturalWidth > 0) return cinderellasCoachImg;
        return floatArtworkImgs['cinderella_coach'];
    }
    if (gType === 'carriage_nohorses') {
        if (carriageNoHorsesImg && carriageNoHorsesImg.naturalWidth > 0) return carriageNoHorsesImg;
    }
    if (gType === 'builtin_dragon' || gType === 'petes_dragon') {
        if (defaultDragonLoaded && defaultDragonImg.complete && defaultDragonImg.naturalWidth > 0) return defaultDragonImg;
        return floatArtworkImgs['petes_dragon'];
    }
    if (floatArtworkImgs[gType]) {
        return floatArtworkImgs[gType];
    }
    return null;
}

function getActiveGraphicImg() {
    return getGraphicImgForType(currentGraphicType);
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
let liveSymmetryPartners = new Map();

// Click-to-Draw Sequential Path State
let isDrawGroupMode = false;
let drawGroupLedIndices = [];
let drawGroupPoints = [];
let preDrawLedBackup = null;

// Animation Groups & Zones
// Array of { id, name, ledIndices: [idx...], effect: 'chase'|'flash_slow'|..., speedBpm, direction, width, colorMode, customColor }
let animationGroups = [];
let ledGroupMap = {}; // mapping: ledIndex -> { group, indexInGroup, groupSize }
let selectedGroupId = null; // Track currently selected/editing animation group ID

// Global Animation Group Clipboard State (with localStorage persistence)
let copiedGroupClipboard = null;

function saveGroupClipboardToStorage() {
    if (!copiedGroupClipboard) {
        try { localStorage.removeItem('msep_copied_group'); } catch (e) {}
    } else {
        try { localStorage.setItem('msep_copied_group', JSON.stringify(copiedGroupClipboard)); } catch (e) {}
    }
    updatePasteButtonState();
}

function loadGroupClipboardFromStorage() {
    try {
        const raw = localStorage.getItem('msep_copied_group');
        if (raw) {
            copiedGroupClipboard = JSON.parse(raw);
        }
    } catch (e) {}
    updatePasteButtonState();
}

function updatePasteButtonState() {
    const pasteHeaderBtn = document.getElementById('pasteGroupHeaderBtn');
    const inspectorPasteBtn = document.getElementById('inspectorPasteGroupBtn');
    const hasGroup = !!copiedGroupClipboard && Array.isArray(copiedGroupClipboard.relPositions) && copiedGroupClipboard.relPositions.length > 0;

    [pasteHeaderBtn, inspectorPasteBtn].forEach(btn => {
        if (btn) {
            btn.disabled = !hasGroup;
            btn.style.opacity = hasGroup ? '1.0' : '0.45';
            btn.style.cursor = hasGroup ? 'pointer' : 'not-allowed';
        }
    });
}

function rebuildLedGroupMap() {
    ledGroupMap = {};
    for (const grp of animationGroups) {
        if (!grp) continue;
        const arr = Array.isArray(grp.ledIndices) ? grp.ledIndices : (Array.isArray(grp.indices) ? grp.indices : []);
        grp.ledIndices = arr;
        grp.indices = arr;
        const grpSize = arr.length;
        if (grpSize === 0) continue;

        let gMinX = Infinity, gMaxX = -Infinity, gMinY = Infinity, gMaxY = -Infinity;
        let gSumX = 0, gSumY = 0;
        for (let pos = 0; pos < grpSize; pos++) {
            const idx = arr[pos];
            const p = leds[idx] || { x: 0.5, y: 0.5 };
            const x = (typeof p.x === 'number') ? p.x : 0.5;
            const y = (typeof p.y === 'number') ? p.y : 0.5;
            gSumX += x; gSumY += y;
            if (x < gMinX) gMinX = x;
            if (x > gMaxX) gMaxX = x;
            if (y < gMinY) gMinY = y;
            if (y > gMaxY) gMaxY = y;
        }
        const gCx = gSumX / grpSize;
        const gCy = gSumY / grpSize;
        const gSpanX = Math.max(0.001, gMaxX - gMinX);
        const gSpanY = Math.max(0.001, gMaxY - gMinY);

        let gMaxR = 0.001;
        const gRadii = new Float32Array(grpSize);
        for (let pos = 0; pos < grpSize; pos++) {
            const idx = arr[pos];
            const p = leds[idx] || { x: 0.5, y: 0.5 };
            const r = Math.hypot((p.x || 0.5) - gCx, (p.y || 0.5) - gCy);
            gRadii[pos] = r;
            if (r > gMaxR) gMaxR = r;
        }

        const orderYDesc = Array.from({ length: grpSize }, (_, i) => i);
        orderYDesc.sort((a, b) => {
            const pA = leds[arr[a]] || { y: 0.5, x: 0.5 };
            const pB = leds[arr[b]] || { y: 0.5, x: 0.5 };
            if (Math.abs(pB.y - pA.y) > 0.0001) return pB.y - pA.y;
            return (pA.x || 0.5) - (pB.x || 0.5);
        });
        const grpRankYBottomUp = new Int32Array(grpSize);
        const grpRankYTopDown = new Int32Array(grpSize);
        for (let r = 0; r < grpSize; r++) {
            const pIdx = orderYDesc[r];
            grpRankYBottomUp[pIdx] = r;
            grpRankYTopDown[pIdx] = (grpSize - 1) - r;
        }

        for (let pos = 0; pos < grpSize; pos++) {
            const idx = arr[pos];
            const p = leds[idx] || { x: 0.5, y: 0.5 };
            ledGroupMap[idx] = {
                group: grp,
                indexInGroup: pos,
                groupSize: grpSize,
                normX: ((p.x || 0.5) - gMinX) / gSpanX,
                normY: ((p.y || 0.5) - gMinY) / gSpanY,
                normRadius: gRadii[pos] / gMaxR,
                rankYBottomUp: grpRankYBottomUp[pos],
                rankYTopDown: grpRankYTopDown[pos]
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
let sequenceMode = true;           // Master timeline engine: always active and looping
let sequenceLoopDuration = 90.0;    // Loop duration in seconds
let sequenceTime = 0.0;            // Current timeline position in seconds
let sequencePlaying = false;       // Playback state
let sequenceLoop = true;           // Loop back to 0:00
let sequenceCues = [];             // Array of cue objects
let lastTimelineFrameTime = performance.now();

// Feature 10: Hover-Scrubbing & Grid Snap State
let gridSnapInterval = 0.5;        // Default: 0.5s grid snapping (0 = off)
let isHoverScrubbing = false;      // True when hovering over timeline ruler/tracks
let hoverScrubTime = 0.0;          // Microsecond timestamp under cursor during hover-scrub

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

// ============================================================================
// UNIVERSAL UNDO / REDO HISTORY ENGINE (Ctrl+Z / Ctrl+Y)
// ============================================================================
const MAX_UNDO_HISTORY = 50;
let undoStack = [];
let redoStack = [];
let isApplyingHistory = false;
let preDragStateSnapshot = null;

function captureEditorSnapshot(actionName = 'Edit') {
    return {
        action: actionName,
        timestamp: Date.now(),
        leds: JSON.parse(JSON.stringify(leds)),
        animationGroups: JSON.parse(JSON.stringify(animationGroups)),
        selectedLeds: Array.from(selectedLeds),
        selectedLed: selectedLed,
        selectedGroupId: selectedGroupId,
        graphicType: typeof currentGraphicType !== 'undefined' ? currentGraphicType : 'builtin_dragon',
        customArtworkDataUrl: typeof customArtworkDataUrl !== 'undefined' ? customArtworkDataUrl : null
    };
}

function recordHistory(actionName = 'Edit') {
    if (isApplyingHistory) return;
    const snapshot = captureEditorSnapshot(actionName);
    undoStack.push(snapshot);
    if (undoStack.length > MAX_UNDO_HISTORY) {
        undoStack.shift();
    }
    redoStack = [];
    updateUndoRedoUI();
}

function restoreEditorSnapshot(snapshot) {
    if (!snapshot) return;
    isApplyingHistory = true;
    try {
        // 1. Restore LEDs
        if (Array.isArray(snapshot.leds)) {
            leds = JSON.parse(JSON.stringify(snapshot.leds));
            if (typeof sparkles !== 'undefined' && Array.isArray(sparkles)) {
                while (sparkles.length < leds.length) sparkles.push(0);
            }
            if (typeof updateLedCountUI === 'function') updateLedCountUI();
        }

        // 2. Restore Animation Groups
        if (Array.isArray(snapshot.animationGroups)) {
            animationGroups = JSON.parse(JSON.stringify(snapshot.animationGroups)).map(g => {
                const arr = Array.isArray(g.ledIndices) ? g.ledIndices : (Array.isArray(g.indices) ? g.indices : []);
                return {
                    ...g,
                    ledIndices: arr,
                    indices: arr
                };
            });
        } else {
            animationGroups = [];
        }
        if (typeof rebuildLedGroupMap === 'function') rebuildLedGroupMap();
        if (typeof renderActiveGroupsList === 'function') renderActiveGroupsList();

        // 3. Restore graphic type if changed
        if (snapshot.graphicType && snapshot.graphicType !== currentGraphicType) {
            currentGraphicType = snapshot.graphicType;
            customArtworkDataUrl = snapshot.customArtworkDataUrl || null;
            const graphicSelect = document.getElementById('graphicPresetSelect');
            if (graphicSelect) {
                graphicSelect.value = currentGraphicType;
            }
        }

        // 4. Restore Selection
        selectedLeds.clear();
        if (Array.isArray(snapshot.selectedLeds)) {
            for (const idx of snapshot.selectedLeds) {
                if (idx < leds.length) selectedLeds.add(idx);
            }
        }
        selectedLed = (snapshot.selectedLed !== null && snapshot.selectedLed !== undefined && snapshot.selectedLed < leds.length) ? snapshot.selectedLed : (selectedLeds.size > 0 ? Array.from(selectedLeds)[0] : null);
        selectedGroupId = snapshot.selectedGroupId || null;

        if (selectedGroupId && typeof populateGroupForm === 'function') {
            const grp = animationGroups.find(g => g.id === selectedGroupId);
            if (grp) populateGroupForm(grp);
        }

        if (typeof updateLedInspectorUI === 'function') updateLedInspectorUI();
        if (typeof markSingleShirtDirty === 'function') markSingleShirtDirty();
        if (typeof updatePasteButtonState === 'function') updatePasteButtonState();
    } finally {
        isApplyingHistory = false;
    }
}

function undo() {
    if (undoStack.length === 0) {
        showToast("ℹ️ Nothing to undo");
        return;
    }
    const currentAction = undoStack[undoStack.length - 1].action || 'Action';
    const currentState = captureEditorSnapshot(currentAction);
    redoStack.push(currentState);

    const prevState = undoStack.pop();
    restoreEditorSnapshot(prevState);
    updateUndoRedoUI();
    showToast(`↩️ Undid: ${prevState.action || 'action'}`);
}

function redo() {
    if (redoStack.length === 0) {
        showToast("ℹ️ Nothing to redo");
        return;
    }
    const nextAction = redoStack[redoStack.length - 1].action || 'Action';
    const currentState = captureEditorSnapshot(nextAction);
    undoStack.push(currentState);

    const nextState = redoStack.pop();
    restoreEditorSnapshot(nextState);
    updateUndoRedoUI();
    showToast(`↪️ Redid: ${nextState.action || 'action'}`);
}

function clearHistoryStacks() {
    undoStack = [];
    redoStack = [];
    preDragStateSnapshot = null;
    updateUndoRedoUI();
}

function updateUndoRedoUI() {
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');

    if (undoBtn) {
        const canUndo = undoStack.length > 0;
        undoBtn.disabled = !canUndo;
        if (canUndo) {
            const nextUndoAction = undoStack[undoStack.length - 1].action || 'action';
            undoBtn.title = `Undo: ${nextUndoAction} (Ctrl+Z / Cmd+Z)`;
            undoBtn.style.opacity = '1';
        } else {
            undoBtn.title = `Undo (Ctrl+Z / Cmd+Z) - No actions to undo`;
            undoBtn.style.opacity = '0.35';
        }
    }

    if (redoBtn) {
        const canRedo = redoStack.length > 0;
        redoBtn.disabled = !canRedo;
        if (canRedo) {
            const nextRedoAction = redoStack[redoStack.length - 1].action || 'action';
            redoBtn.title = `Redo: ${nextRedoAction} (Ctrl+Y / Cmd+Shift+Z)`;
            redoBtn.style.opacity = '1';
        } else {
            redoBtn.title = `Redo (Ctrl+Y / Cmd+Shift+Z) - No actions to redo`;
            redoBtn.style.opacity = '0.35';
        }
    }
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

    // Authentic runDisney bib dimensions: 8.0" wide by 7.0" high (relative to 18" x 24" shirt model)
    // Scaled realistically onto athletic running shirt with user scale multiplier
    const scale = (params.bibScale !== undefined ? params.bibScale : 1.0);
    const baseBibW = s.width * (8.0 / 18.0); // 8.0" wide on 18.0" wide shirt (~0.4444 * s.width)
    const bibW = baseBibW * scale;
    const bibH = bibW * (7.0 / 8.0); // 7.0" high for 8.0" wide (0.875 aspect ratio)
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
    if (activeImg && (activeImg.complete || activeImg.naturalWidth > 0)) {
        const gb = getGraphicChestBounds();
        const gx = s.x + gb.normX * s.width;
        const gy = s.y + gb.normY * s.height;
        const gw = gb.normW * s.width;
        const gh = gb.normH * s.height;
        try {
            cx.drawImage(activeImg, gx, gy, gw, gh);
            return;
        } catch (e) {}
    }

    // Only render metallic green silhouette if graphic is actually Pete's Dragon
    if (currentGraphicType !== 'builtin_dragon' && currentGraphicType !== 'petes_dragon') {
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
// 2D SPATIAL METRICS ENGINE (Physics-Aware Lighting & Contoured Sweep Architecture)
// Calculates continuous spatial coordinates, centroid, bounds, and sorted spatial ranks
// so animations (Progressive Fill, Wave, Ripple, Scanner, Rainbow) map to physical fabric
// geometry rather than electrical wiring strand sequence.
// ============================================================================
let cachedSpatialMetrics = null;
let spatialMetricsLedsRef = null;

function recomputeSpatialMetrics(targetLeds = leds) {
    if (!targetLeds || targetLeds.length === 0) {
        cachedSpatialMetrics = {
            count: 0,
            centroid: { x: 0.5, y: 0.5 },
            minX: 0, maxX: 1, minY: 0, maxY: 1,
            spanX: 1, spanY: 1, maxRadius: 1,
            normX: [], normY: [], normYBottomUp: [], normRadius: [],
            rankYBottomUp: [], rankYTopDown: [], rankXLeftRight: [], rankXRightLeft: [], rankRadius: []
        };
        spatialMetricsLedsRef = targetLeds;
        return cachedSpatialMetrics;
    }

    const n = targetLeds.length;
    let sumX = 0, sumY = 0;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

    for (let i = 0; i < n; i++) {
        const p = targetLeds[i] || { x: 0.5, y: 0.5 };
        const x = (typeof p.x === 'number') ? p.x : 0.5;
        const y = (typeof p.y === 'number') ? p.y : 0.5;
        sumX += x;
        sumY += y;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
    }

    const cx = sumX / n;
    const cy = sumY / n;
    const spanX = Math.max(0.001, maxX - minX);
    const spanY = Math.max(0.001, maxY - minY);

    // Compute radii from centroid
    let maxR = 0.001;
    const radii = new Float32Array(n);
    for (let i = 0; i < n; i++) {
        const p = targetLeds[i] || { x: 0.5, y: 0.5 };
        const dx = ((typeof p.x === 'number' ? p.x : 0.5) - cx);
        const dy = ((typeof p.y === 'number' ? p.y : 0.5) - cy);
        const r = Math.hypot(dx, dy);
        radii[i] = r;
        if (r > maxR) maxR = r;
    }

    // Normalized coordinates
    const normX = new Float32Array(n);
    const normY = new Float32Array(n);
    const normYBottomUp = new Float32Array(n);
    const normRadius = new Float32Array(n);

    for (let i = 0; i < n; i++) {
        const p = targetLeds[i] || { x: 0.5, y: 0.5 };
        const px = (typeof p.x === 'number') ? p.x : 0.5;
        const py = (typeof p.y === 'number') ? p.y : 0.5;
        normX[i] = Math.max(0, Math.min(1, (px - minX) / spanX));
        normY[i] = Math.max(0, Math.min(1, (py - minY) / spanY)); // 0 top, 1 bottom
        normYBottomUp[i] = 1.0 - normY[i];                         // 0 bottom, 1 top
        normRadius[i] = Math.max(0, Math.min(1, radii[i] / maxR));
    }

    // Sorted ranks:
    // 1. Bottom-up: Highest y is 0 (bottom-most on shirt), lowest y is n-1 (top-most near neck)
    const indicesByYDesc = Array.from({ length: n }, (_, i) => i);
    indicesByYDesc.sort((a, b) => {
        const pA = targetLeds[a] || { y: 0.5, x: 0.5 };
        const pB = targetLeds[b] || { y: 0.5, x: 0.5 };
        const yA = typeof pA.y === 'number' ? pA.y : 0.5;
        const yB = typeof pB.y === 'number' ? pB.y : 0.5;
        if (Math.abs(yB - yA) > 0.0001) return yB - yA;
        const xA = typeof pA.x === 'number' ? pA.x : 0.5;
        const xB = typeof pB.x === 'number' ? pB.x : 0.5;
        return xA - xB;
    });
    const rankYBottomUp = new Int32Array(n);
    const rankYTopDown = new Int32Array(n);
    for (let r = 0; r < n; r++) {
        const idx = indicesByYDesc[r];
        rankYBottomUp[idx] = r;
        rankYTopDown[idx] = (n - 1) - r;
    }

    // 2. Left-to-Right: Lowest x is 0, highest x is n-1
    const indicesByXAsc = Array.from({ length: n }, (_, i) => i);
    indicesByXAsc.sort((a, b) => {
        const pA = targetLeds[a] || { x: 0.5, y: 0.5 };
        const pB = targetLeds[b] || { x: 0.5, y: 0.5 };
        const xA = typeof pA.x === 'number' ? pA.x : 0.5;
        const xB = typeof pB.x === 'number' ? pB.x : 0.5;
        if (Math.abs(xA - xB) > 0.0001) return xA - xB;
        const yA = typeof pA.y === 'number' ? pA.y : 0.5;
        const yB = typeof pB.y === 'number' ? pB.y : 0.5;
        return yA - yB;
    });
    const rankXLeftRight = new Int32Array(n);
    const rankXRightLeft = new Int32Array(n);
    for (let r = 0; r < n; r++) {
        const idx = indicesByXAsc[r];
        rankXLeftRight[idx] = r;
        rankXRightLeft[idx] = (n - 1) - r;
    }

    // 3. Radial: Center outward
    const indicesByRadius = Array.from({ length: n }, (_, i) => i);
    indicesByRadius.sort((a, b) => radii[a] - radii[b]);
    const rankRadius = new Int32Array(n);
    for (let r = 0; r < n; r++) {
        rankRadius[indicesByRadius[r]] = r;
    }

    cachedSpatialMetrics = {
        count: n,
        centroid: { x: cx, y: cy },
        minX, maxX, minY, maxY,
        spanX, spanY, maxRadius: maxR,
        normX, normY, normYBottomUp, normRadius,
        rankYBottomUp, rankYTopDown,
        rankXLeftRight, rankXRightLeft,
        rankRadius
    };
    spatialMetricsLedsRef = targetLeds;
    return cachedSpatialMetrics;
}

function getSpatialMetrics() {
    if (cachedSpatialMetrics && spatialMetricsLedsRef === leds && cachedSpatialMetrics.count === leds.length) {
        return cachedSpatialMetrics;
    }
    return recomputeSpatialMetrics(leds);
}

function evalGroupEffect(grp, effect, bpm, dir, grpIndex, grpSize, timeMs, c) {
    let effectiveBpm = bpm;
    if (!effectiveBpm) {
        if (grp && grp.syncWithGroupId) {
            const parentGrp = animationGroups.find(g => g.id === grp.syncWithGroupId);
            if (parentGrp && parentGrp.speedBpm) effectiveBpm = parentGrp.speedBpm;
        }
        if (!effectiveBpm) effectiveBpm = (grp && grp.speedBpm) ? grp.speedBpm : 120;
    }
    const grpBeatMs = 60000 / Math.max(20, effectiveBpm);
    const phaseOffsetDeg = (grp && grp.phaseOffsetDeg !== undefined) ? grp.phaseOffsetDeg : 0;
    const phaseOffsetMs = (phaseOffsetDeg / 360.0) * grpBeatMs;
    const effectiveTimeMs = timeMs + phaseOffsetMs;
    const grpNormTime = effectiveTimeMs / grpBeatMs;
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
    const actualLedIndex = (grp && grp.ledIndices && grp.ledIndices[grpIndex] !== undefined) ? grp.ledIndices[grpIndex] : grpIndex;
    const grpEntry = ledGroupMap[actualLedIndex];

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
            const phase = (effectiveTimeMs % (grpBeatMs * 2)) / (grpBeatMs * 2);
            grpIntensity = phase < 0.5 ? 1.0 : 0.08;
            break;
        }
        case 'steady_sparkle': {
            if (sparkles[grpIndex] > 0) {
                const sp = sparkles[grpIndex];
                baseR = Math.round(baseR * (1 - sp) + 255 * sp);
                baseG = Math.round(baseG * (1 - sp) + 255 * sp);
                baseB = Math.round(baseB * (1 - sp) + 240 * sp);
                grpIntensity = Math.min(1.0, 0.85 + sp * 0.4);
            } else {
                grpIntensity = 0.85;
            }
            break;
        }
        case 'color_match':
        case 'breathe':
        case 'pulse_slow':
        case 'pulse': {
            const sine = Math.sin(grpNormTime * Math.PI * 2) * 0.5 + 0.5;
            grpIntensity = 0.18 + 0.82 * sine;
            break;
        }
        case 'comet': {
            const grpCometMs = Math.max(600, grpBeatMs * 1.2);
            const head = (((effectiveTimeMs / grpCometMs) * direction * grpSize) % grpSize + grpSize) % grpSize;
            const tailLen = Math.max(3, Math.min(grpSize * 0.75, 12));
            let dist = (direction >= 0) ? (head - grpIndex) : (grpIndex - head);
            if (dist < 0) dist += grpSize;
            if (dist < tailLen) {
                const fade = Math.exp(-dist * (2.8 / tailLen));
                grpIntensity = 0.08 + 0.92 * fade;
                if (dist < 1.0) {
                    baseR = Math.min(255, baseR + 90);
                    baseG = Math.min(255, baseG + 90);
                    baseB = Math.min(255, baseB + 90);
                }
            } else {
                grpIntensity = 0.08;
            }
            break;
        }
        case 'scanner': {
            const cycle = (effectiveTimeMs / grpBeatMs) % 2.0;
            const pos = cycle <= 1.0 ? cycle : (2.0 - cycle);
            const ledX = (grpEntry && grpEntry.normX !== undefined)
                ? (direction >= 0 ? grpEntry.normX : (1.0 - grpEntry.normX))
                : (grpIndex / Math.max(1, grpSize - 1));
            const dist = Math.abs(ledX - pos);
            const sigma = Math.max(0.12, 1.2 / Math.max(2, grpSize));
            const wake = Math.exp(-(dist * dist) / (2 * sigma * sigma));
            grpIntensity = 0.10 + 0.90 * wake;
            if (dist < 0.10) {
                baseR = Math.min(255, baseR + 80);
                baseG = Math.min(255, baseG + 80);
                baseB = Math.min(255, baseB + 80);
            }
            break;
        }
        case 'write_on_off': {
            const totalCycleMs = grpBeatMs * 4;
            const progress = (effectiveTimeMs % totalCycleMs) / totalCycleMs;
            const effRank = (direction >= 0 ? grpIndex : ((grpSize - 1) - grpIndex));
            if (progress < 0.40) {
                const litHead = (progress / 0.40) * grpSize;
                grpIntensity = (effRank <= litHead) ? 1.0 : 0.05;
            } else if (progress < 0.58) {
                grpIntensity = 1.0;
            } else if (progress < 0.88) {
                const offHead = ((progress - 0.58) / 0.30) * grpSize;
                grpIntensity = (effRank <= offHead) ? 0.05 : 1.0;
            } else {
                grpIntensity = 0.05;
            }
            break;
        }
        case 'sparkle_storm': {
            const rand = Math.sin(grpNormTime * 12.0 + grpIndex * 37.1) * 0.5 + 0.5;
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
            const effRank = (direction >= 0 ? grpIndex : ((grpSize - 1) - grpIndex));
            const step = Math.floor(grpNormTime * 2 * direction) % 3;
            const posInStep = ((effRank + step) % 3 + 3) % 3;
            grpIntensity = posInStep === 0 ? 1.0 : 0.12;
            break;
        }
        case 'rainbow_cycle': {
            const spatialPos = (grpEntry && grpEntry.normX !== undefined)
                ? (grpEntry.normX * 0.7 + grpEntry.normY * 0.3)
                : (grpIndex / Math.max(1, grpSize));
            const hue = ((effectiveTimeMs * 0.08 * direction + spatialPos * 360) % 360 + 360) % 360;
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
            const tau = (effectiveTimeMs % cycleMs) / cycleMs; // 0.0 to 1.0

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
        case 'color_wipe': {
            const totalCycleMs = grpBeatMs * 4;
            const progress = (effectiveTimeMs % totalCycleMs) / totalCycleMs;
            const effRank = (direction >= 0 ? grpIndex : ((grpSize - 1) - grpIndex));
            if (progress < 0.40) {
                const litHead = (progress / 0.40) * grpSize;
                grpIntensity = (effRank <= litHead) ? 1.0 : 0.05;
            } else if (progress < 0.58) {
                grpIntensity = 1.0;
            } else if (progress < 0.88) {
                const offHead = ((progress - 0.58) / 0.30) * grpSize;
                grpIntensity = (effRank <= offHead) ? 0.05 : 1.0;
            } else {
                grpIntensity = 0.05;
            }
            break;
        }
        case 'pixie_dust': {
            const drift = Math.sin(grpNormTime * Math.PI * 0.5 + grpIndex * 0.25) * 0.22 + 0.78;
            const twinkle = Math.sin(grpNormTime * 6.0 + grpIndex * 37.17) * 0.5 + 0.5;
            if (twinkle > 0.82) {
                const twFactor = Math.pow((twinkle - 0.82) / 0.18, 1.5);
                grpIntensity = Math.min(1.0, 0.65 * drift + 0.35 * twFactor);
                baseR = Math.min(255, baseR + Math.round(110 * twFactor));
                baseG = Math.min(255, baseG + Math.round(110 * twFactor));
                baseB = Math.min(255, baseB + Math.round(110 * twFactor));
            } else {
                grpIntensity = 0.55 * drift;
            }
            break;
        }
        case 'filament_glow': {
            const warmDrift = Math.sin(grpNormTime * 2.5 + grpIndex * 13.7) * 0.09 +
                              Math.sin(grpNormTime * 6.0 + grpIndex * 31.9) * 0.05;
            grpIntensity = 0.80 + warmDrift;
            baseR = Math.min(255, Math.round(baseR * 1.08 + 15));
            baseG = Math.round(baseG * 0.94 + 5);
            baseB = Math.round(baseB * 0.70);
            break;
        }
        case 'candle_flicker': {
            const slowDraft = Math.sin(grpNormTime * 1.2 + grpIndex * 5.1) * 0.12;
            const flameWaver = Math.sin(grpNormTime * 4.5 + grpIndex * 17.3) * 0.09 +
                               Math.sin(grpNormTime * 9.8 + grpIndex * 37.7) * 0.05;
            grpIntensity = Math.max(0.40, Math.min(1.0, 0.78 + slowDraft + flameWaver));
            baseR = 255;
            baseG = Math.min(255, Math.max(110, Math.round(baseG * 0.85 + 40)));
            baseB = Math.min(120, Math.round(baseB * 0.35));
            break;
        }
        case 'tidal_ripple': {
            const normDist = (grpEntry && grpEntry.normRadius !== undefined)
                ? grpEntry.normRadius
                : (Math.abs(grpIndex - (grpSize - 1) / 2) / Math.max(1, (grpSize - 1) / 2));
            const wavePhase = (grpNormTime * direction) - (normDist * 2.5);
            const wave = Math.sin(wavePhase * Math.PI) * 0.5 + 0.5;
            grpIntensity = 0.15 + 0.85 * Math.pow(wave, 1.8);
            break;
        }
        case 'piston_chug': {
            const strokeProgress = (grpNormTime * 2) % 1.0;
            const strokeIdx = Math.floor(grpNormTime * 2) % 4;
            if (strokeIdx === 0 || strokeIdx === 2) {
                const decay = Math.exp(-strokeProgress * 4.5);
                grpIntensity = 0.15 + 0.85 * decay;
                if (strokeProgress < 0.25) {
                    baseR = Math.min(255, baseR + 70);
                    baseG = Math.min(255, baseG + 70);
                    baseB = Math.min(255, baseB + 70);
                }
            } else {
                grpIntensity = 0.15 + 0.20 * Math.sin(strokeProgress * Math.PI);
            }
            break;
        }
        case 'photo_mode': {
            grpIntensity = 1.0;
            break;
        }
        case 'flashlight': {
            const t = grpNormTime * 1.2;
            const wanderX = 0.50 + 0.38 * (Math.sin(t * 1.1 * direction) * 0.70 + Math.sin(t * 2.3) * 0.30);
            const wanderY = 0.50 + 0.38 * (Math.cos(t * 0.8) * 0.70 + Math.sin(t * 1.9 * direction) * 0.30);
            const ledX = (grpEntry && grpEntry.normX !== undefined) ? grpEntry.normX : (grpIndex / Math.max(1, grpSize - 1));
            const ledY = (grpEntry && grpEntry.normY !== undefined) ? grpEntry.normY : 0.5;
            const dx = ledX - wanderX;
            const dy = ledY - wanderY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const sigma = Math.max(0.14, 1.6 / Math.max(2, grpSize));
            const beam = Math.exp(-(dist * dist) / (2 * sigma * sigma));
            grpIntensity = 0.08 + 0.92 * beam;
            if (dist < 0.09) {
                baseR = Math.min(255, baseR + 100);
                baseG = Math.min(255, baseG + 100);
                baseB = Math.min(255, baseB + 100);
            }
            break;
        }
        case 'mouse_scamper': {
            const scamperMs = Math.max(700, grpBeatMs * 1.5);
            const tCurr = (effectiveTimeMs / scamperMs) * 2.0;

            const headX = 0.50 + 0.38 * (Math.sin(tCurr * 1.1 * direction) * 0.70 + Math.sin(tCurr * 2.3) * 0.30);
            const headY = 0.50 + 0.38 * (Math.cos(tCurr * 0.8) * 0.70 + Math.sin(tCurr * 1.9 * direction) * 0.30);

            const ledX = (grpEntry && grpEntry.normX !== undefined) ? grpEntry.normX : (grpIndex / Math.max(1, grpSize - 1));
            const ledY = (grpEntry && grpEntry.normY !== undefined) ? grpEntry.normY : 0.5;

            const dHead = Math.hypot(ledX - headX, ledY - headY);

            let maxTailFade = 0.0;
            const historySteps = 24;
            const historySpanT = 1.6; // Extended long trailing path
            const captureRadius = 0.075; // Focused narrow tube

            for (let s = 1; s <= historySteps; s++) {
                const frac = s / historySteps;
                const tPast = tCurr - (frac * historySpanT * direction);
                const pastX = 0.50 + 0.38 * (Math.sin(tPast * 1.1 * direction) * 0.70 + Math.sin(tPast * 2.3) * 0.30);
                const pastY = 0.50 + 0.38 * (Math.cos(tPast * 0.8) * 0.70 + Math.sin(tPast * 1.9 * direction) * 0.30);
                const dPast = Math.hypot(ledX - pastX, ledY - pastY);
                if (dPast < captureRadius) {
                    const tubeFalloff = 1.0 - (dPast / captureRadius);
                    const ageFalloff = 1.0 - (frac * 0.80); // Smooth gradual falloff along the tail
                    const cand = tubeFalloff * ageFalloff;
                    if (cand > maxTailFade) maxTailFade = cand;
                }
            }

            if (dHead < 0.055) {
                // Single focused bright head point
                const headIntensity = 1.0 - (dHead / 0.055);
                grpIntensity = 1.0;
                baseR = Math.min(255, baseR + Math.round(150 * headIntensity));
                baseG = Math.min(255, baseG + Math.round(150 * headIntensity));
                baseB = Math.min(255, baseB + Math.round(150 * headIntensity));
            } else if (maxTailFade > 0.02) {
                grpIntensity = 0.08 + 0.92 * maxTailFade;
            } else {
                grpIntensity = 0.08;
            }
            break;
        }
        case 'dim_glow': {
            grpIntensity = 0.22;
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

function getSparkleRgb(style) {
    if (style === 'diamond') return { r: 255, g: 255, b: 255 };
    if (style === 'gold') return { r: 255, g: 215, b: 40 };
    return { r: 255, g: 240, b: 200 }; // default: warm 2700K incandescent filament
}

function evalGlobalPattern(pattern, bpm, index, totalLeds, timeMs, c, hasColor, isGroupOverride = false, directionOverride = null) {
    const beatMs = 60000 / Math.max(20, bpm || params.speedBpm || 120);
    const normTime = timeMs / beatMs;
    const baseH = params.greenHue || 140;
    const dir = (directionOverride !== null && directionOverride !== undefined)
        ? ((directionOverride === -1 || directionOverride === '-1' || directionOverride === 'reverse') ? -1 : 1)
        : (params.direction || 1);

    let effC = c;
    let effHasColor = hasColor;
    if (!isGroupOverride && params.ambientColorMode && params.ambientColorMode !== 'artwork') {
        if (params.ambientColorMode === 'float_theme') {
            const floatIdx = (typeof activeSingleShirtRunnerSlot === 'number' && activeSingleShirtRunnerSlot >= 0) ? activeSingleShirtRunnerSlot : 0;
            const floatObj = (DEFAULT_FLEET_RADAR && DEFAULT_FLEET_RADAR[floatIdx]) ? DEFAULT_FLEET_RADAR[floatIdx] : null;
            effC = (floatObj && floatObj.color && typeof hexToRgb === 'function') ? (hexToRgb(floatObj.color) || { r: 56, g: 139, b: 253 }) : { r: 56, g: 139, b: 253 };
            effHasColor = true;
        } else if (params.ambientColorMode === 'vintage_warm') {
            effC = { r: 255, g: 210, b: 120 };
            effHasColor = true;
        } else if (params.ambientColorMode === 'custom') {
            effC = (typeof hexToRgb === 'function') ? (hexToRgb(params.ambientCustomColor || '#ffb703') || { r: 255, g: 183, b: 3 }) : { r: 255, g: 183, b: 3 };
            effHasColor = true;
        }
    }

    const spkCol = getSparkleRgb(params.sparkleStyle);
    let r = 0, g = 255, b = 100, brightness = params.brightness / 100;

    switch (pattern) {
        case 'steady_sparkle': {
            if (effHasColor) {
                r = effC.r; g = effC.g; b = effC.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                r = Math.round(r * (1 - sp) + spkCol.r * sp);
                g = Math.round(g * (1 - sp) + spkCol.g * sp);
                b = Math.round(b * (1 - sp) + spkCol.b * sp);
                brightness = Math.min(1.0, brightness + sp * 0.4);
            }
            break;
        }
        case 'color_match': {
            if (effHasColor) {
                const breath = 0.72 + 0.28 * Math.sin(normTime * Math.PI + index * 0.15);
                r = Math.floor(effC.r * breath);
                g = Math.floor(effC.g * breath);
                b = Math.floor(effC.b * breath);
            } else {
                const breath = 0.75 + 0.25 * Math.sin(normTime * Math.PI + index * 0.12);
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * breath);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                r = Math.round(r * (1 - sp) + spkCol.r * sp);
                g = Math.round(g * (1 - sp) + spkCol.g * sp);
                b = Math.round(b * (1 - sp) + spkCol.b * sp);
                brightness = Math.min(1.0, brightness + sp * 0.4);
            }
            break;
        }
        case 'dragon_sparkle': {
            if (effHasColor) {
                const breath = 0.75 + 0.25 * Math.sin(normTime * Math.PI + index * 0.15);
                r = Math.floor(effC.r * breath);
                g = Math.floor(effC.g * breath);
                b = Math.floor(effC.b * breath);
            } else {
                const breath = 0.75 + 0.25 * Math.sin(normTime * Math.PI + index * 0.15);
                const h = baseH + Math.sin(index * 0.4) * 8;
                const rgb = hslToRgb(h / 360, 0.95, 0.50 * breath);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (sparkles[index] > 0) {
                const sp = sparkles[index];
                r = Math.round(r * (1 - sp) + spkCol.r * sp);
                g = Math.round(g * (1 - sp) + spkCol.g * sp);
                b = Math.round(b * (1 - sp) + spkCol.b * sp);
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
            } else if (effHasColor) {
                r = effC.r; g = effC.g; b = effC.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.85, 0.45);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            break;
        }
        case 'traveling_wave': {
            const sm = getSpatialMetrics();
            const wavePeriodMs = Math.max(1200, beatMs * 3.0);
            const waveCycle = (timeMs % wavePeriodMs) / wavePeriodMs;
            const headX = (dir === -1) ? (1.0 - waveCycle) : waveCycle;
            const ledX = (sm && sm.normX && sm.normX[index] !== undefined) ? sm.normX[index] : (index / Math.max(1, totalLeds));
            const waveWidth = 0.14;
            const dist = Math.abs(ledX - headX);
            if (dist < waveWidth) {
                const intensity = Math.max(0, 1.0 - (dist / waveWidth));
                r = 255 * intensity;
                g = 255 * intensity;
                b = Math.floor(220 * intensity);
                brightness = 1.0;
            } else if (effHasColor) {
                r = Math.floor(effC.r * 0.4);
                g = Math.floor(effC.g * 0.4);
                b = Math.floor(effC.b * 0.4);
                brightness = 0.35;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.9, 0.25);
                r = rgb.r; g = rgb.g; b = rgb.b;
                brightness = 0.30;
            }
            break;
        }
        case 'marquee': {
            const sm = getSpatialMetrics();
            const effRank = (sm && sm.rankYBottomUp && sm.rankYBottomUp[index] !== undefined) ? sm.rankYBottomUp[index] : index;
            const step = Math.floor(normTime * 3) % 3;
            const effStep = (dir === -1) ? (3 - step) % 3 : step;
            if ((effRank + effStep) % 3 === 0) {
                if (effHasColor) {
                    r = Math.min(255, effC.r + 50);
                    g = Math.min(255, effC.g + 50);
                    b = Math.min(255, effC.b + 50);
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
            if (effHasColor) {
                r = effC.r; g = effC.g; b = effC.b;
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
            const breath = 0.35 + 0.65 * (Math.sin(normTime * Math.PI) * 0.5 + 0.5);
            if (effHasColor) {
                r = Math.floor(effC.r * breath);
                g = Math.floor(effC.g * breath);
                b = Math.floor(effC.b * breath);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * breath);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            break;
        }
        case 'chase': {
            const sm = getSpatialMetrics();
            const effRank = (sm && sm.rankYBottomUp && sm.rankYBottomUp[index] !== undefined)
                ? (dir === -1 ? sm.rankYTopDown[index] : sm.rankYBottomUp[index])
                : ((dir === -1) ? (totalLeds - 1 - index) : index);
            const head = (normTime * 0.6) % totalLeds;
            const dist = Math.abs(effRank - head);
            const fade = Math.max(0, 1 - (dist / 8));
            const intensity = 0.15 + 0.85 * fade;
            if (effHasColor) {
                r = Math.floor(effC.r * intensity);
                g = Math.floor(effC.g * intensity);
                b = Math.floor(effC.b * intensity);
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
        case 'flash_slow': {
            const phase = (timeMs % (beatMs * 2)) / (beatMs * 2);
            if (hasColor) {
                r = c.r; g = c.g; b = c.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            brightness = phase < 0.5 ? 1.0 : 0.05;
            break;
        }
        case 'write_on_off': {
            const totalCycleMs = beatMs * 4;
            const progress = (timeMs % totalCycleMs) / totalCycleMs;
            const sm = getSpatialMetrics();
            const effRank = (sm && sm.rankYBottomUp && sm.rankYBottomUp[index] !== undefined)
                ? (dir === -1 ? sm.rankYTopDown[index] : sm.rankYBottomUp[index])
                : ((dir === -1) ? (totalLeds - 1 - index) : index);
            if (hasColor) {
                r = c.r; g = c.g; b = c.b;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (progress < 0.40) {
                const litHead = (progress / 0.40) * totalLeds;
                brightness = effRank <= litHead ? 1.0 : 0.05;
            } else if (progress < 0.58) {
                brightness = 1.0;
            } else if (progress < 0.88) {
                const offHead = ((progress - 0.58) / 0.30) * totalLeds;
                brightness = effRank <= offHead ? 0.05 : 1.0;
            } else {
                brightness = 0.05;
            }
            break;
        }
        case 'sparkle_storm': {
            const rand = Math.sin(normTime * 12.0 + index * 37.1) * 0.5 + 0.5;
            if (rand > 0.65) {
                r = 255; g = 255; b = 240;
                brightness = 1.0;
            } else if (effHasColor) {
                r = effC.r; g = effC.g; b = effC.b;
                brightness = 0.15;
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.35);
                r = rgb.r; g = rgb.g; b = rgb.b;
                brightness = 0.15;
            }
            break;
        }
        case 'rainbow_cycle': {
            const sm = getSpatialMetrics();
            const spatialPos = (sm && sm.normX && sm.normX[index] !== undefined)
                ? (sm.normX[index] * 0.7 + sm.normY[index] * 0.3)
                : (index / Math.max(1, totalLeds));
            const hueCycleMs = Math.max(2500, beatMs * 8.0);
            const hue = (((timeMs / hueCycleMs) * 360 * dir + spatialPos * 360) % 360 + 360) % 360;
            const rgb = hslToRgb(hue / 360, 0.95, 0.52);
            r = rgb.r; g = rgb.g; b = rgb.b;
            brightness = 1.0;
            break;
        }
        case 'comet': {
            const sm = getSpatialMetrics();
            const effRank = (sm && sm.rankYBottomUp && sm.rankYBottomUp[index] !== undefined)
                ? (dir === -1 ? sm.rankYTopDown[index] : sm.rankYBottomUp[index])
                : ((dir === -1) ? (totalLeds - 1 - index) : index);
            const cometPassMs = Math.max(900, beatMs * 1.5);
            const head = (((timeMs / cometPassMs) * totalLeds) % totalLeds + totalLeds) % totalLeds;
            const tailLen = Math.max(12, totalLeds * 0.22);
            let dist = head - effRank;
            if (dist < 0) dist += totalLeds;
            if (dist < tailLen) {
                const fade = Math.exp(-dist * (2.8 / tailLen));
                const effIntensity = 0.08 + 0.92 * fade;
                if (effHasColor) {
                    r = Math.floor(effC.r * effIntensity);
                    g = Math.floor(effC.g * effIntensity);
                    b = Math.floor(effC.b * effIntensity);
                } else {
                    const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * effIntensity);
                    r = rgb.r; g = rgb.g; b = rgb.b;
                }
                if (dist < 1.2) {
                    r = Math.min(255, r + 110);
                    g = Math.min(255, g + 110);
                    b = Math.min(255, b + 110);
                }
                brightness = 1.0;
            } else {
                if (effHasColor) {
                    r = Math.floor(effC.r * 0.08); g = Math.floor(effC.g * 0.08); b = Math.floor(effC.b * 0.08);
                } else {
                    r = 15; g = 15; b = 15;
                }
                brightness = 0.2;
            }
            break;
        }
        case 'scanner': {
            const sm = getSpatialMetrics();
            const cycle = (normTime / 2.0) % 2.0;
            let headX = cycle <= 1.0 ? cycle : (2.0 - cycle);
            if (dir === -1) headX = 1.0 - headX;
            const ledX = (sm && sm.normX && sm.normX[index] !== undefined)
                ? sm.normX[index]
                : (index / Math.max(1, totalLeds - 1));
            const dist = Math.abs(ledX - headX);
            const sigma = 0.09;
            const wake = Math.exp(-(dist * dist) / (2 * sigma * sigma));
            const effIntensity = 0.10 + 0.90 * wake;
            if (effHasColor) {
                r = Math.floor(effC.r * effIntensity);
                g = Math.floor(effC.g * effIntensity);
                b = Math.floor(effC.b * effIntensity);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * effIntensity);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (dist < 0.05) {
                r = Math.min(255, r + 80);
                g = Math.min(255, g + 80);
                b = Math.min(255, b + 80);
            }
            brightness = 1.0;
            break;
        }
        case 'color_wipe': {
            const totalCycleMs = beatMs * 4;
            const progress = (timeMs % totalCycleMs) / totalCycleMs;
            const sm = getSpatialMetrics();
            const effRank = (sm && sm.rankYBottomUp && sm.rankYBottomUp[index] !== undefined)
                ? (dir === -1 ? sm.rankYTopDown[index] : sm.rankYBottomUp[index])
                : ((dir === -1) ? (totalLeds - 1 - index) : index);
            let lit = false;
            if (progress < 0.40) {
                lit = effRank <= (progress / 0.40) * totalLeds;
            } else if (progress < 0.58) {
                lit = true;
            } else if (progress < 0.88) {
                lit = effRank > ((progress - 0.58) / 0.30) * totalLeds;
            } else {
                lit = false;
            }
            const eff = lit ? 1.0 : 0.06;
            if (effHasColor) {
                r = Math.floor(effC.r * eff); g = Math.floor(effC.g * eff); b = Math.floor(effC.b * eff);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * eff);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            brightness = lit ? 1.0 : 0.15;
            break;
        }
        case 'pixie_dust': {
            const drift = Math.sin(normTime * Math.PI * 0.5 + index * 0.18) * 0.22 + 0.78;
            const twinkle = Math.sin(normTime * 6.0 + index * 37.17) * 0.5 + 0.5;
            if (effHasColor) {
                r = Math.floor(effC.r * drift); g = Math.floor(effC.g * drift); b = Math.floor(effC.b * drift);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * drift);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (twinkle > 0.82) {
                const twFactor = Math.pow((twinkle - 0.82) / 0.18, 1.5);
                r = Math.min(255, r + Math.round(spkCol.r * 0.7 * twFactor));
                g = Math.min(255, g + Math.round(spkCol.g * 0.7 * twFactor));
                b = Math.min(255, b + Math.round(spkCol.b * 0.7 * twFactor));
                brightness = Math.min(1.0, 0.65 * drift + 0.35 * twFactor);
            } else {
                brightness = 0.55 * drift;
            }
            break;
        }
        case 'filament_glow': {
            const warmDrift = Math.sin(normTime * 2.5 + index * 13.7) * 0.09 +
                              Math.sin(normTime * 6.0 + index * 31.9) * 0.05;
            const eff = 0.80 + warmDrift;
            if (effHasColor) {
                r = Math.min(255, Math.floor((effC.r * 1.08 + 15) * eff));
                g = Math.floor((effC.g * 0.94 + 5) * eff);
                b = Math.floor((effC.b * 0.70) * eff);
            } else {
                r = Math.floor(255 * eff);
                g = Math.floor(180 * eff);
                b = Math.floor(45 * eff);
            }
            brightness = 0.85;
            break;
        }
        case 'candle_flicker': {
            const slowDraft = Math.sin(normTime * 1.2 + index * 5.1) * 0.12;
            const flameWaver = Math.sin(normTime * 4.5 + index * 17.3) * 0.09 +
                               Math.sin(normTime * 9.8 + index * 37.7) * 0.05;
            const eff = Math.max(0.40, Math.min(1.0, 0.78 + slowDraft + flameWaver));
            if (effHasColor) {
                r = Math.min(255, Math.floor(255 * eff));
                g = Math.min(255, Math.floor(Math.max(110, effC.g * 0.85 + 40) * eff));
                b = Math.min(120, Math.floor(effC.b * 0.35 * eff));
            } else {
                r = Math.floor(255 * eff);
                g = Math.floor(150 * eff);
                b = Math.floor(30 * eff);
            }
            brightness = 0.9;
            break;
        }
        case 'tidal_ripple': {
            const sm = getSpatialMetrics();
            const normDist = (sm && sm.normRadius && sm.normRadius[index] !== undefined)
                ? sm.normRadius[index]
                : (Math.abs(index - (totalLeds - 1) / 2) / Math.max(1, (totalLeds - 1) / 2));
            const wavePhase = (normTime * 0.75 * dir) - (normDist * 2.2);
            const wave = Math.sin(wavePhase * Math.PI) * 0.5 + 0.5;
            const eff = 0.15 + 0.85 * Math.pow(wave, 1.8);
            if (effHasColor) {
                r = Math.floor(effC.r * eff); g = Math.floor(effC.g * eff); b = Math.floor(effC.b * eff);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * eff);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            brightness = eff;
            break;
        }
        case 'piston_chug': {
            const strokeProgress = (normTime * 1.0) % 1.0;
            const strokeIdx = Math.floor(normTime * 1.0) % 4;
            let eff = 0.15;
            let punch = false;
            if (strokeIdx === 0 || strokeIdx === 2) {
                eff = 0.15 + 0.85 * Math.exp(-strokeProgress * 4.5);
                if (strokeProgress < 0.25) punch = true;
            } else {
                eff = 0.15 + 0.20 * Math.sin(strokeProgress * Math.PI);
            }
            if (effHasColor) {
                r = Math.floor(effC.r * eff); g = Math.floor(effC.g * eff); b = Math.floor(effC.b * eff);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * eff);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (punch) {
                r = Math.min(255, r + 70); g = Math.min(255, g + 70); b = Math.min(255, b + 70);
            }
            brightness = eff;
            break;
        }
        case 'flashlight': {
            const sm = getSpatialMetrics();
            const t = normTime * 1.2;
            const wanderX = 0.50 + 0.38 * (Math.sin(t * 1.1 * dir) * 0.70 + Math.sin(t * 2.3) * 0.30);
            const wanderY = 0.50 + 0.38 * (Math.cos(t * 0.8) * 0.70 + Math.sin(t * 1.9 * dir) * 0.30);
            const ledX = (sm && sm.normX && sm.normX[index] !== undefined) ? sm.normX[index] : (index / Math.max(1, totalLeds));
            const ledY = (sm && sm.normY && sm.normY[index] !== undefined) ? sm.normY[index] : 0.5;
            const dx = ledX - wanderX;
            const dy = ledY - wanderY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const sigma = 0.14;
            const beam = Math.exp(-(dist * dist) / (2 * sigma * sigma));
            const effIntensity = 0.08 + 0.92 * beam;
            if (effHasColor) {
                r = Math.floor(effC.r * effIntensity);
                g = Math.floor(effC.g * effIntensity);
                b = Math.floor(effC.b * effIntensity);
            } else {
                const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * effIntensity);
                r = rgb.r; g = rgb.g; b = rgb.b;
            }
            if (dist < 0.08) {
                r = Math.min(255, r + 110);
                g = Math.min(255, g + 110);
                b = Math.min(255, b + 110);
                brightness = 1.0;
            } else {
                brightness = Math.max(0.15, beam);
            }
            break;
        }
        case 'mouse_scamper': {
            const sm = getSpatialMetrics();
            const scamperPassMs = Math.max(700, beatMs * 1.5);
            const tCurr = (timeMs / scamperPassMs) * 2.0;

            // Current 2D position of mouse head
            const headX = 0.50 + 0.38 * (Math.sin(tCurr * 1.1 * dir) * 0.70 + Math.sin(tCurr * 2.3) * 0.30);
            const headY = 0.50 + 0.38 * (Math.cos(tCurr * 0.8) * 0.70 + Math.sin(tCurr * 1.9 * dir) * 0.30);

            // This LED's physical 2D location on the shirt
            const ledX = (sm && sm.normX && sm.normX[index] !== undefined) ? sm.normX[index] : (index / Math.max(1, totalLeds));
            const ledY = (sm && sm.normY && sm.normY[index] !== undefined) ? sm.normY[index] : 0.5;

            // Distance to current head
            const dHead = Math.hypot(ledX - headX, ledY - headY);

            // Sample the historical path behind the head with a long graceful tail
            let maxTailFade = 0.0;
            const historySteps = 24;
            const historySpanT = 1.6; // Extended long trailing path
            const captureRadius = 0.075; // Focused narrow tube

            for (let s = 1; s <= historySteps; s++) {
                const frac = s / historySteps;
                const tPast = tCurr - (frac * historySpanT * dir);
                const pastX = 0.50 + 0.38 * (Math.sin(tPast * 1.1 * dir) * 0.70 + Math.sin(tPast * 2.3) * 0.30);
                const pastY = 0.50 + 0.38 * (Math.cos(tPast * 0.8) * 0.70 + Math.sin(tPast * 1.9 * dir) * 0.30);
                const dPast = Math.hypot(ledX - pastX, ledY - pastY);
                if (dPast < captureRadius) {
                    const tubeFalloff = 1.0 - (dPast / captureRadius);
                    const ageFalloff = 1.0 - (frac * 0.80); // Smooth gradual falloff along the tail
                    const cand = tubeFalloff * ageFalloff;
                    if (cand > maxTailFade) maxTailFade = cand;
                }
            }

            if (dHead < 0.055) {
                // Leading bright dot (single sharp spark)
                const headIntensity = 1.0 - (dHead / 0.055);
                if (effHasColor) {
                    r = effC.r; g = effC.g; b = effC.b;
                } else {
                    const rgb = hslToRgb(baseH / 360, 0.95, 0.50);
                    r = rgb.r; g = rgb.g; b = rgb.b;
                }
                r = Math.min(255, r + Math.round(150 * headIntensity));
                g = Math.min(255, g + Math.round(150 * headIntensity));
                b = Math.min(255, b + Math.round(150 * headIntensity));
                brightness = 1.0;
            } else if (maxTailFade > 0.02) {
                // Directional trail of where it has been
                const effIntensity = 0.08 + 0.92 * maxTailFade;
                if (effHasColor) {
                    r = Math.floor(effC.r * effIntensity);
                    g = Math.floor(effC.g * effIntensity);
                    b = Math.floor(effC.b * effIntensity);
                } else {
                    const rgb = hslToRgb(baseH / 360, 0.95, 0.50 * effIntensity);
                    r = rgb.r; g = rgb.g; b = rgb.b;
                }
                brightness = Math.min(1.0, 0.20 + 0.80 * maxTailFade);
            } else {
                // Outside the trail: clean resting baseline
                if (effHasColor) {
                    r = Math.floor(effC.r * 0.08); g = Math.floor(effC.g * 0.08); b = Math.floor(effC.b * 0.08);
                } else {
                    r = 15; g = 15; b = 15;
                }
                brightness = 0.15;
            }
            break;
        }
        case 'off': {
            return { r: 0, g: 0, b: 0, alpha: 0 };
        }
        default: {
            if (effHasColor) {
                r = effC.r; g = effC.g; b = effC.b;
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
    if (isCorralStandbyActive) {
        const floatIdx = (activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) ? activeSingleShirtRunnerSlot : 5;
        const floatObj = (DEFAULT_FLEET_RADAR && DEFAULT_FLEET_RADAR[floatIdx]) ? DEFAULT_FLEET_RADAR[floatIdx] : (DEFAULT_FLEET_RADAR ? DEFAULT_FLEET_RADAR[0] : null);
        const baseColor = (floatObj && floatObj.color && typeof hexToRgb === 'function') ? (hexToRgb(floatObj.color) || { r: 56, g: 139, b: 253 }) : { r: 56, g: 139, b: 253 };
        
        // Visible deep midnight base glow (28% float color) - distinctly visible on black jersey
        const dimR = Math.max(25, Math.round(baseColor.r * 0.28));
        const dimG = Math.max(25, Math.round(baseColor.g * 0.28));
        const dimB = Math.max(25, Math.round(baseColor.b * 0.28));
        
        // Calm, sparse starlight twinkle: slow ~5s period, spatially scattered
        const wave = Math.sin((timeMs * 0.0012) + (index * 1.9));
        let r = dimR;
        let g = dimG;
        let b = dimB;
        let alpha = 0.55;

        // Subtle shimmer on only ~5% of LEDs at any moment, gently dimmed
        if (wave > 0.88) {
            const blendFactor = (wave - 0.88) / 0.12; // 0.0 to 1.0 gentle swell
            r = Math.min(255, Math.round(dimR + 45 * blendFactor));
            g = Math.min(255, Math.round(dimG + 38 * blendFactor));
            b = Math.min(255, Math.round(dimB + 20 * blendFactor));
            alpha = 0.55 + (0.15 * blendFactor);
        }

        return { r, g, b, alpha };
    }

    if (isPhotoModeActive) {
        if (leds[index] && leds[index].color) {
            return {
                r: Math.round(leds[index].color.r),
                g: Math.round(leds[index].color.g),
                b: Math.round(leds[index].color.b),
                alpha: 1.0
            };
        }
        const floatIdx = (activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) ? activeSingleShirtRunnerSlot : 5;
        const floatObj = (DEFAULT_FLEET_RADAR && DEFAULT_FLEET_RADAR[floatIdx]) ? DEFAULT_FLEET_RADAR[floatIdx] : (DEFAULT_FLEET_RADAR ? DEFAULT_FLEET_RADAR[0] : null);
        const heroColor = (floatObj && floatObj.color && typeof hexToRgb === 'function') ? (hexToRgb(floatObj.color) || { r: 56, g: 139, b: 253 }) : { r: 56, g: 139, b: 253 };
        return { r: heroColor.r, g: heroColor.g, b: heroColor.b, alpha: 1.0 };
    }

    if (rapidRollCallActive) {
        const elapsed = timeMs - rapidRollCallStartTime;
        if (elapsed >= 0 && elapsed < 4000) {
            const runnerIndex = activeSingleShirtRunnerSlot || 0;
            if (elapsed < 3500) {
                const activeSlot = Math.floor(elapsed / 500);
                if (runnerIndex === activeSlot) {
                    const radarFloat = DEFAULT_FLEET_RADAR[runnerIndex];
                    const col = hexToRgb(radarFloat ? radarFloat.color : '#ffffff');
                    return { r: col.r, g: col.g, b: col.b, alpha: 1.0 };
                } else {
                    return { r: 0, g: 0, b: 0, alpha: 0.0 };
                }
            } else {
                const finaleMs = elapsed - 3500;
                if ((finaleMs < 200) || (finaleMs >= 300 && finaleMs < 500)) {
                    return { r: 0, g: 255, b: 80, alpha: 1.0 };
                } else {
                    return { r: 0, g: 0, b: 0, alpha: 0.0 };
                }
            }
        }
    }

    const hasColor = (leds[index] && leds[index].color);
    const c = hasColor ? leds[index].color : null;
    const grpEntry = ledGroupMap[index];

    // ========================================================================
    // MODE A: SHOW SEQUENCE PLAYBACK (Parade Cue Director)
    // ========================================================================
    if (sequenceMode) {
        const t = (isHoverScrubbing && !sequencePlaying) ? hoverScrubTime : sequenceTime;
        const effectiveTimeMs = (isHoverScrubbing && !sequencePlaying) ? (hoverScrubTime * 1000) : timeMs;

        // 1. Evaluate Active Global Cues
        const activeGlobalCues = sequenceCues.filter(q => q.targetType === 'global' && t >= q.startTime && t < (q.startTime + q.duration));

        let baseColor = null;
        if (activeGlobalCues.length === 0) {
            baseColor = evalGlobalPattern(activePattern, params.speedBpm, index, totalLeds, effectiveTimeMs, c, hasColor);
        } else if (activeGlobalCues.length === 1) {
            const q = activeGlobalCues[0];
            const col = evalGlobalPattern(q.effect, q.speedBpm, index, totalLeds, effectiveTimeMs, c, hasColor, false, q.direction);
            const w = getCueWeight(q, t);
            if (w < 1.0) {
                const restCol = evalGlobalPattern('steady_sparkle', 120, index, totalLeds, effectiveTimeMs, c, hasColor);
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
                const col = evalGlobalPattern(q.effect, q.speedBpm, index, totalLeds, effectiveTimeMs, c, hasColor, false, q.direction);
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
            } else if (groupBaseline === 'inherit' || !groupBaseline) {
                if (grp.colorMode === 'custom' && grp.customColor) {
                    grpBaselineCol = evalGlobalPattern(activePattern, params.speedBpm, index, totalLeds, timeMs, grp.customColor, true, true);
                } else {
                    grpBaselineCol = baseColor;
                }
            } else {
                grpBaselineCol = evalGroupEffect(grp, groupBaseline, grp.speedBpm || params.speedBpm, grp.direction || 1, grpEntry.indexInGroup, grpEntry.groupSize, timeMs, c);
            }

            if (activeGrpCue) {
                // Synchronize animation phase to cue onset time so cue effects explode/trigger precisely on cue!
                const cueTimeMs = Math.max(0, (t - activeGrpCue.startTime) * 1000);
                const cueDir = (activeGrpCue.direction !== undefined) ? activeGrpCue.direction : (grp.direction || 1);
                const grpCol = evalGroupEffect(grp, activeGrpCue.effect, activeGrpCue.speedBpm, cueDir, grpEntry.indexInGroup, grpEntry.groupSize, cueTimeMs, c);
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
        const baseline = grp.baselineEffect || grp.baseline || 'inherit';
        if (baseline === 'off' || grp.effect === 'off') {
            return { r: 0, g: 0, b: 0, alpha: 0 };
        }
        if (baseline !== 'inherit') {
            return evalGroupEffect(grp, baseline, grp.speedBpm || params.speedBpm, grp.direction || 1, grpEntry.indexInGroup, grpEntry.groupSize, timeMs, c);
        }
        if (grp.effect && grp.effect !== 'off' && grp.effect !== 'inherit') {
            return evalGroupEffect(grp, grp.effect, grp.speedBpm || params.speedBpm, grp.direction || 1, grpEntry.indexInGroup, grpEntry.groupSize, timeMs, c);
        }
        const effectiveColor = (grp.colorMode === 'custom' && grp.customColor) ? grp.customColor : c;
        return evalGlobalPattern(activePattern, params.speedBpm, index, totalLeds, timeMs, effectiveColor, hasColor || (grp.colorMode === 'custom'), grp.colorMode === 'custom');
    }

    return evalGlobalPattern(activePattern, params.speedBpm, index, totalLeds, timeMs, c, hasColor);
}


// Calculate tangent angle of the continuous wiring path at LED index i
function getLedTangentAngle(index, ledsList) {
    const list = ledsList || leds;
    if (!list || list.length === 0) return 0;
    if (list.length === 1) return 0;

    const curr = normToCanvas(list[index]);
    let prev = (index > 0) ? normToCanvas(list[index - 1]) : curr;
    let next = (index < list.length - 1) ? normToCanvas(list[index + 1]) : curr;

    if (index === 0) {
        return Math.atan2(next.y - curr.y, next.x - curr.x);
    }
    if (index === list.length - 1) {
        return Math.atan2(curr.y - prev.y, curr.x - prev.x);
    }
    // Interior points: smooth chord tangent (next - prev)
    return Math.atan2(next.y - prev.y, next.x - prev.x);
}


// ============================================================================
// 🎨 CRICUT HTV MULTI-LAYER SVG EXPORT SUITE WITH 6×3mm PILL SLOTS
// ============================================================================

const CRICUT_FLOAT_CONFIG = {
    'petes_dragon': {
        floatId: 6,
        name: "Pete's Dragon (Elliott)",
        role: "FOLLOWER",
        tag: "FAN FAVORITE",
        svgFile: "petes_dragon.svg",
        layers: [
            { id: "Layer_1_Green_Vinyl", name: "Emerald Body & Legs", hex: "#00cc66", r: 0, g: 204, b: 102 },
            { id: "Layer_2_Pink_Vinyl", name: "Pink Crest, Wings & Spines", hex: "#ff007f", r: 255, g: 25, b: 230 }
        ]
    },
    'builtin_dragon': {
        floatId: 6,
        name: "Pete's Dragon (Elliott)",
        role: "FOLLOWER",
        tag: "FAN FAVORITE",
        svgFile: "petes_dragon.svg",
        layers: [
            { id: "Layer_1_Green_Vinyl", name: "Emerald Body & Legs", hex: "#00cc66", r: 0, g: 204, b: 102 },
            { id: "Layer_2_Pink_Vinyl", name: "Pink Crest, Wings & Spines", hex: "#ff007f", r: 255, g: 25, b: 230 }
        ]
    },
    'casey_jr_train': {
        floatId: 1,
        name: "Casey Jr. Locomotive",
        role: "LEADER",
        tag: "PARADE ENGINE",
        svgFile: "casey_jr_train.svg",
        layers: [
            { id: "Layer_1_Red_Vinyl", name: "Crimson Boiler & Cab", hex: "#e63946", r: 230, g: 57, b: 70 },
            { id: "Layer_2_Cyan_Vinyl", name: "Cyan Roof & Trim", hex: "#48cae4", r: 72, g: 202, b: 228 },
            { id: "Layer_3_Gold_Vinyl", name: "Gold Cowcatcher & Wheels", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_4_White_Vinyl", name: "White Headlight & Steam", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'title_drum': {
        floatId: 2,
        name: "The Title Drum",
        role: "FOLLOWER",
        tag: "MARQUEE",
        svgFile: "title_drum.svg",
        layers: [
            { id: "Layer_1_Blue_Vinyl", name: "Navy Drum Backdrop", hex: "#1d3557", r: 29, g: 53, b: 87 },
            { id: "Layer_2_Gold_Vinyl", name: "Gold Marquee Rim", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_3_Cyan_Vinyl", name: "Cyan Banners", hex: "#48cae4", r: 72, g: 202, b: 228 },
            { id: "Layer_4_White_Vinyl", name: "White Bulbs & Text", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'spinning_turtle': {
        floatId: 3,
        name: "The Spinning Turtle",
        role: "FOLLOWER",
        tag: "SPINNING",
        svgFile: "spinning_turtle.svg",
        layers: [
            { id: "Layer_1_Green_Vinyl", name: "Teal Turtle Body", hex: "#2ec4b6", r: 46, g: 196, b: 182 },
            { id: "Layer_2_Red_Vinyl", name: "Red Bow Tie", hex: "#e63946", r: 230, g: 57, b: 70 },
            { id: "Layer_3_Yellow_Vinyl", name: "Yellow Shell & Glasses", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_4_White_Vinyl", name: "White Shell Bulbs", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'spinning_snail': {
        floatId: 4,
        name: "The Spinning Snail",
        role: "FOLLOWER",
        tag: "SPINNING",
        svgFile: "spinning_snail.svg",
        layers: [
            { id: "Layer_1_Yellow_Vinyl", name: "Golden Shell Spiral", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_2_Pink_Vinyl", name: "Pink Snail Body", hex: "#ff007f", r: 255, g: 0, b: 127 },
            { id: "Layer_3_Cyan_Vinyl", name: "Cyan Stalks & Shell Accents", hex: "#48cae4", r: 72, g: 202, b: 228 },
            { id: "Layer_4_White_Vinyl", name: "White Eyes & Accents", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'cinderella_coach': {
        floatId: 5,
        name: "Cinderella's Coach",
        role: "FOLLOWER",
        tag: "FAIRY TALE",
        svgFile: "cinderella_coach.svg",
        layers: [
            { id: "Layer_1_Cyan_Vinyl", name: "Cyan Pumpkin Drapes", hex: "#48cae4", r: 72, g: 202, b: 228 },
            { id: "Layer_2_Gold_Vinyl", name: "Gold Filigree & Wheels", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_3_White_Vinyl", name: "White Fairy Sparkles", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'cinderellas_coach': {
        floatId: 5,
        name: "Cinderella's Coach",
        role: "FOLLOWER",
        tag: "FAIRY TALE",
        svgFile: "cinderella_coach.svg",
        layers: [
            { id: "Layer_1_Cyan_Vinyl", name: "Cyan Pumpkin Drapes", hex: "#48cae4", r: 72, g: 202, b: 228 },
            { id: "Layer_2_Gold_Vinyl", name: "Gold Filigree & Wheels", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_3_White_Vinyl", name: "White Fairy Sparkles", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'carriage_nohorses': {
        floatId: 5,
        name: "Carriage (No Horses)",
        role: "FOLLOWER",
        tag: "FAIRY TALE",
        svgFile: "cinderella_coach.svg",
        layers: [
            { id: "Layer_1_Cyan_Vinyl", name: "Cyan Pumpkin Drapes", hex: "#48cae4", r: 72, g: 202, b: 228 },
            { id: "Layer_2_Gold_Vinyl", name: "Gold Filigree & Wheels", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_3_White_Vinyl", name: "White Fairy Sparkles", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    },
    'honor_america_eagle': {
        floatId: 7,
        name: "To Honor America",
        role: "FOLLOWER",
        tag: "FINALE",
        svgFile: "honor_america_eagle.svg",
        layers: [
            { id: "Layer_1_Blue_Vinyl", name: "Navy Starfield & Wings", hex: "#1d3557", r: 29, g: 53, b: 87 },
            { id: "Layer_2_Red_Vinyl", name: "Crimson Flag Stripes", hex: "#e63946", r: 230, g: 57, b: 70 },
            { id: "Layer_3_Gold_Vinyl", name: "Gold Eagle Beak & Trim", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_4_White_Vinyl", name: "Crisp White Stars & Head", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    }
};

function getSvgViewBoxDimensions(rawSvgText) {
    if (!rawSvgText) return { width: 800, height: 600 };
    const match = rawSvgText.match(/viewBox=["']\s*0\s+0\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*["']/);
    if (match) {
        return { width: parseFloat(match[1]), height: parseFloat(match[2]) };
    }
    return { width: 800, height: 600 };
}

function generateRegistrationCrosshairsSvg(svgW = 800, svgH = 600) {
    const pad = Math.min(25, svgW * 0.05);
    const x1 = pad, y1 = pad;
    const x2 = svgW - pad, y2 = pad;
    const x3 = pad, y3 = svgH - pad;
    const x4 = svgW - pad, y4 = svgH - pad;
    const arm = Math.max(8, svgW * 0.015);
    const r = Math.max(4, svgW * 0.008);

    return `  <!-- HTV Heat Press Registration Marks (4 Corners for Multi-Color Vinyl Layering) -->
  <g id="Layer_0_Registration_Crosshairs" stroke="#888888" stroke-width="1.5" fill="none">
    <!-- Top-Left Crosshair -->
    <path d="M ${x1 - arm} ${y1} L ${x1 + arm} ${y1} M ${x1} ${y1 - arm} L ${x1} ${y1 + arm}" />
    <circle cx="${x1}" cy="${y1}" r="${r}" />
    <!-- Top-Right Crosshair -->
    <path d="M ${x2 - arm} ${y2} L ${x2 + arm} ${y2} M ${x2} ${y2 - arm} L ${x2} ${y2 + arm}" />
    <circle cx="${x2}" cy="${y2}" r="${r}" />
    <!-- Bottom-Left Crosshair -->
    <path d="M ${x3 - arm} ${y3} L ${x3 + arm} ${y3} M ${x3} ${y3 - arm} L ${x3} ${y3 + arm}" />
    <circle cx="${x3}" cy="${y3}" r="${r}" />
    <!-- Bottom-Right Crosshair -->
    <path d="M ${x4 - arm} ${y4} L ${x4 + arm} ${y4} M ${x4} ${y4 - arm} L ${x4} ${y4 + arm}" />
    <circle cx="${x4}" cy="${y4}" r="${r}" />
  </g>\n`;
}

async function fetchMasterSvgText(filename) {
    const urls = [
        `assets/cricut_svg/${filename}`,
        `/assets/cricut_svg/${filename}`,
        `simulator/assets/cricut_svg/${filename}`
    ];
    for (const url of urls) {
        try {
            const res = await fetch(url);
            if (res.ok) {
                const text = await res.text();
                if (text && text.includes('<svg')) return text;
            }
        } catch (e) {}
    }
    return null;
}

function calculateLedCutoutData(layers, rawSvgText) {
    const gb = getGraphicChestBounds();
    const { width: svgW, height: svgH } = getSvgViewBoxDimensions(rawSvgText);

    // Physical garment width = 18.0 inches (457.2 mm)
    const garmentWidthMm = 457.2;
    const graphicWidthMm = Math.max(10, gb.normW * garmentWidthMm);
    const unitsPerMm = svgW / graphicWidthMm;

    // 6.0mm x 3.0mm pill slot scaled to SVG coordinate system
    const pillW = parseFloat((6.0 * unitsPerMm).toFixed(1));
    const pillH = parseFloat((3.0 * unitsPerMm).toFixed(1));
    const halfW = parseFloat((pillW / 2).toFixed(1));
    const halfH = parseFloat((pillH / 2).toFixed(1));
    const rx = parseFloat((pillH / 2).toFixed(1));

    let allCutoutsXml = '';
    const layerCutouts = {};
    const layerLedCounts = {};
    layers.forEach(l => {
        layerCutouts[l.id] = '';
        layerLedCounts[l.id] = 0;
    });

    const isPeteDragon = (currentGraphicType === 'builtin_dragon' || currentGraphicType === 'petes_dragon');

    for (let i = 0; i < leds.length; i++) {
        const l = leds[i];
        const relX = (l.x - gb.normX) / gb.normW;
        const relY = (l.y - gb.normY) / gb.normH;
        if (relX < -0.05 || relX > 1.05 || relY < -0.05 || relY > 1.05) continue;

        const svgX = (relX * svgW).toFixed(1);
        const svgY = (relY * svgH).toFixed(1);
        const angleDeg = (getLedTangentAngle(i, leds) * 180 / Math.PI).toFixed(1);

        let bestLayer = layers[0];

        if (isPeteDragon) {
            // Pete's Dragon: Green LEDs ALWAYS map to Layer 1 Green Vinyl
            const isGreenLed = (l.color && l.color.g > l.color.r && l.color.g > l.color.b) || (l.color && l.color.g > 140 && l.color.r < 100);
            if (isGreenLed) {
                bestLayer = layers.find(lay => lay.id === 'Layer_1_Green_Vinyl') || layers[0];
            } else if ((l.color && l.color.r > 190 && l.color.b > 170 && l.color.g < 120) ||
                (relY < 0.16 && relX > 0.25 && relX < 0.75) ||
                (relY >= 0.58 && relX >= 0.65) ||
                (relY >= 0.20 && relY <= 0.58 && ((relX >= 0.20 && relX <= 0.45) || (relX >= 0.58 && relX <= 0.94)))) {
                bestLayer = layers.find(lay => lay.id === 'Layer_2_Pink_Vinyl') || layers[1];
            } else {
                bestLayer = layers.find(lay => lay.id === 'Layer_1_Green_Vinyl') || layers[0];
            }
        } else {
            // General Euclidean distance in RGB color space
            let minD = 1e9;
            for (const lay of layers) {
                const dr = l.color.r - lay.r;
                const dg = l.color.g - lay.g;
                const db = l.color.b - lay.b;
                const d = dr * dr + dg * dg + db * db;
                if (d < minD) {
                    minD = d;
                    bestLayer = lay;
                }
            }
        }

        layerLedCounts[bestLayer.id] = (layerLedCounts[bestLayer.id] || 0) + 1;

        const rectXml = `    <rect x="-${halfW}" y="-${halfH}" width="${pillW}" height="${pillH}" rx="${rx}" transform="translate(${svgX}, ${svgY}) rotate(${angleDeg})" fill="#000000" stroke="${bestLayer.hex}" stroke-width="1.2" class="cricut-led-slot" data-led="${i}" data-layer="${bestLayer.id}" />\n`;
        allCutoutsXml += rectXml;
        if (layerCutouts[bestLayer.id] !== undefined) {
            layerCutouts[bestLayer.id] += rectXml;
        }
    }

    return { allCutoutsXml, layerCutouts, layerLedCounts, svgW, svgH };
}

function downloadSvgBlob(svgContent, filename) {
    const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const dlAnchor = document.createElement('a');
    dlAnchor.href = URL.createObjectURL(blob);
    dlAnchor.download = filename;
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    document.body.removeChild(dlAnchor);
}

function generateSingleMatSvg(rawSvgText, targetLayer, cutoutsForLayer, svgW = 800, svgH = 600) {
    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(rawSvgText, "image/svg+xml");
        const svgEl = doc.querySelector('svg');
        if (!svgEl) return null;

        // Strip clipart image reference if cutting pure vinyl mat
        const clipart = svgEl.querySelector('#Layer_0_Clipart_Artwork');
        if (clipart) clipart.remove();

        // Strip other color vinyl layers
        const allGroups = Array.from(svgEl.querySelectorAll('g[id^="Layer_"]'));
        for (const g of allGroups) {
            if (g.id !== targetLayer.id) {
                g.remove();
            }
        }

        // Append 4-Corner Registration Crosshairs
        const regParser = new DOMParser();
        const regDoc = regParser.parseFromString(`<svg xmlns="http://www.w3.org/2000/svg">${generateRegistrationCrosshairsSvg(svgW, svgH)}</svg>`, "image/svg+xml");
        const regGroup = regDoc.querySelector('#Layer_0_Registration_Crosshairs');
        if (regGroup) {
            svgEl.appendChild(doc.importNode(regGroup, true));
        }

        // Append this mat's cutouts
        const cutsParser = new DOMParser();
        const cutsXml = `<g id="Layer_Cutouts_${targetLayer.id}" stroke="${targetLayer.hex}" fill="#000000" stroke-width="1.2">\n${cutoutsForLayer}\n</g>`;
        const cutsDoc = cutsParser.parseFromString(`<svg xmlns="http://www.w3.org/2000/svg">${cutsXml}</svg>`, "image/svg+xml");
        const cutsGroup = cutsDoc.querySelector(`#Layer_Cutouts_${targetLayer.id}`);
        if (cutsGroup) {
            svgEl.appendChild(doc.importNode(cutsGroup, true));
        }

        return new XMLSerializer().serializeToString(doc);
    } catch (e) {
        console.error("Error creating single mat SVG:", e);
        return null;
    }
}

// Global cached state for open Cricut export dialog
let currentCricutExportPackage = null;

// Opens the Cricut HTV Multi-Layer Cut File Exporter Modal
async function exportCricutSvgWithPillSlots() {
    try {
        const modal = document.getElementById('cricutExportModal');
        if (!modal) {
            showToast("⚠️ Cricut export modal element not found.");
            return;
        }

        const floatKey = currentGraphicType || 'builtin_dragon';
        const floatConfig = CRICUT_FLOAT_CONFIG[floatKey] || CRICUT_FLOAT_CONFIG['petes_dragon'];
        const svgBaseName = floatConfig.svgFile.replace('.svg', '');

        // Fetch master vector artwork
        let rawSvgText = await fetchMasterSvgText(floatConfig.svgFile);
        if (!rawSvgText) {
            showToast("⚠️ Loading artwork SVG... Using fallback template.");
            rawSvgText = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 850" width="100%" height="100%">\n<g id="Layer_1_Base_Vinyl" fill="#00cc66"></g>\n</svg>`;
        }

        // Calculate 100 pill cutouts & assign to layers based on actual SVG viewBox
        const cutoutsData = calculateLedCutoutData(floatConfig.layers, rawSvgText);

        // Store package in cache
        currentCricutExportPackage = {
            floatConfig,
            svgBaseName,
            rawSvgText,
            cutoutsData
        };

        // Render Float Info in Modal Header
        const infoEl = document.getElementById('cricutExportFloatInfo');
        if (infoEl) {
            infoEl.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">🐲</span>
                    <div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <strong style="font-size: 13px; color: #fff;">${floatConfig.name}</strong>
                            <span style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: rgba(0, 255, 136, 0.2); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.4); font-weight: 700;">FLOAT ${floatConfig.floatId}</span>
                        </div>
                        <span style="font-size: 11px; color: #8b949e;">${leds.length} LEDs • 6×3mm Tangent Pill Slots (${cutoutsData.svgW}×${cutoutsData.svgH} Canvas Match) • ${floatConfig.layers.length} Color Vinyl Mats</span>
                    </div>
                </div>
            `;
        }

        // Render Mat-by-Mat Cards
        const gridEl = document.getElementById('cricutMatListGrid');
        if (gridEl) {
            gridEl.innerHTML = floatConfig.layers.map((layer, idx) => {
                const count = cutoutsData.layerLedCounts[layer.id] || 0;
                return `
                    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 8px 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="width: 12px; height: 12px; border-radius: 3px; background: ${layer.hex}; display: inline-block; border: 1px solid rgba(255,255,255,0.2);"></span>
                            <div>
                                <div style="font-size: 11.5px; font-weight: 600; color: #e6edf3;">Mat ${idx + 1}: ${layer.name}</div>
                                <div style="font-size: 10px; color: #8b949e;">${count} LED cutouts</div>
                            </div>
                        </div>
                        <button type="button" class="action-btn download-single-mat-btn" data-layer-id="${layer.id}" style="padding: 4px 8px; font-size: 10.5px;">
                            ⬇️ SVG
                        </button>
                    </div>
                `;
            }).join('');

            // Bind single mat download buttons
            gridEl.querySelectorAll('.download-single-mat-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const layerId = e.currentTarget.getAttribute('data-layer-id');
                    const targetLayer = floatConfig.layers.find(l => l.id === layerId);
                    if (!targetLayer) return;

                    const matSvg = generateSingleMatSvg(rawSvgText, targetLayer, cutoutsData.layerCutouts[targetLayer.id] || '', cutoutsData.svgW, cutoutsData.svgH);
                    if (matSvg) {
                        const filename = `${svgBaseName}_mat_${targetLayer.id.toLowerCase().replace('layer_', '')}.svg`;
                        downloadSvgBlob(matSvg, filename);
                        showToast(`✂️ Downloaded ${filename}`);
                    }
                });
            });
        }

        // Show Modal
        modal.style.display = 'flex';

    } catch (err) {
        console.error("Error opening Cricut export dialog:", err);
        showToast("⚠️ Could not open Cricut export dialog: " + err.message);
    }
}

function closeCricutExportModal() {
    const modal = document.getElementById('cricutExportModal');
    if (modal) modal.style.display = 'none';
}

// Master All-in-One Download Handler
document.getElementById('downloadMasterCricutSvgBtn')?.addEventListener('click', () => {
    if (!currentCricutExportPackage) return;
    const { floatConfig, svgBaseName, rawSvgText, cutoutsData } = currentCricutExportPackage;

    const regMarks = generateRegistrationCrosshairsSvg(cutoutsData.svgW, cutoutsData.svgH);
    const cutoutsGroup = `  <!-- LAYER: 6x3mm LED PILL SLOT CUTOUTS (Tangent-Aligned for Wire Ribbon) -->
  <g id="Layer_LED_Pill_Slots_6x3mm">
${cutoutsData.allCutoutsXml}  </g>\n`;

    let masterSvg = rawSvgText;
    if (masterSvg.includes('</svg>')) {
        masterSvg = masterSvg.replace('</svg>', `${regMarks}\n${cutoutsGroup}</svg>`);
    } else {
        masterSvg = `${masterSvg}\n${regMarks}\n${cutoutsGroup}\n</svg>`;
    }

    const filename = `${svgBaseName}_cricut_full_artwork_with_6x3mm_slots.svg`;
    downloadSvgBlob(masterSvg, filename);
    showToast(`🌟 Downloaded Master Multi-Layer Cricut Cut SVG: ${filename}`);
});

// Download All Mats Handler
document.getElementById('downloadAllMatsZipBtn')?.addEventListener('click', async () => {
    if (!currentCricutExportPackage) return;
    const { floatConfig, svgBaseName, rawSvgText, cutoutsData } = currentCricutExportPackage;

    for (let i = 0; i < floatConfig.layers.length; i++) {
        const targetLayer = floatConfig.layers[i];
        const matSvg = generateSingleMatSvg(rawSvgText, targetLayer, cutoutsData.layerCutouts[targetLayer.id] || '', cutoutsData.svgW, cutoutsData.svgH);
        if (matSvg) {
            const filename = `${svgBaseName}_mat_${i + 1}_${targetLayer.id.toLowerCase().replace('layer_', '')}.svg`;
            downloadSvgBlob(matSvg, filename);
            await new Promise(r => setTimeout(r, 160)); // Stagger downloads cleanly
        }
    }
    showToast(`📦 Downloaded all ${floatConfig.layers.length} color mat cut files!`);
});

// Download Holes-Only Cut Layer Handler
document.getElementById('downloadHolesOnlySvgBtn')?.addEventListener('click', () => {
    if (!currentCricutExportPackage) return;
    const { svgBaseName, cutoutsData } = currentCricutExportPackage;
    const regMarks = generateRegistrationCrosshairsSvg(cutoutsData.svgW, cutoutsData.svgH);

    const holesSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${cutoutsData.svgW} ${cutoutsData.svgH}" width="100%" height="100%">
  <!-- Main Street Electrical Parade - Standalone 6x3mm LED Pill Slot Cut Layer -->
  <!-- Generated for: ${svgBaseName.toUpperCase()} | 100 LEDs Tangent-Aligned -->
  <defs>
    <style>
      .cricut-led-slot { fill: #000000; stroke: #ff0055; stroke-width: 1.2; }
    </style>
  </defs>

${regMarks}
  <g id="Layer_LED_Pill_Slots_6x3mm">
${cutoutsData.allCutoutsXml}  </g>
</svg>`;

    const filename = `${svgBaseName}_cricut_6x3mm_slots_only.svg`;
    downloadSvgBlob(holesSvg, filename);
    showToast(`🕳️ Downloaded ${filename} (${leds.length} Pill Slots)!`);
});

document.getElementById('closeCricutExportModalBtn')?.addEventListener('click', closeCricutExportModal);
document.getElementById('closeCricutExportModalBottomBtn')?.addEventListener('click', closeCricutExportModal);


function renderBulb(cx, x, y, col, isHovered, isSelected, index) {
    if (!col) return;
    const isLit = (col.alpha > 0.01) && (col.r > 2 || col.g > 2 || col.b > 2);
    const bulbAlpha = (col.alpha !== undefined) ? Math.max(0.35, Math.min(1.0, col.alpha)) : 1.0;

    if (params.showTpuWindows) {
        // Physical scale: 18.0 inch wide garment (457.2 mm)
        const s = getShirtBounds();
        const ppm = s.width / 457.2;

        const outerW = Math.max(14, 12.4 * ppm); // 12.4mm outer collar length
        const outerH = Math.max(8, 7.4 * ppm);   // 7.4mm outer collar width
        const innerW = Math.max(11, 10.0 * ppm); // 10.0mm inner pocket length
        const innerH = Math.max(5.5, 5.0 * ppm); // 5.0mm inner pocket width
        const winSq = Math.max(4.5, 3.0 * ppm);  // 3.0mm square optical aperture

        cx.save();
        cx.translate(x, y);

        // 1. Subtle 12.4x7.4mm Outer Collar Outline (Zero-Overlap Footprint)
        cx.beginPath();
        if (typeof cx.roundRect === 'function') {
            cx.roundRect(-outerW / 2, -outerH / 2, outerW, outerH, outerH / 2);
        } else {
            cx.rect(-outerW / 2, -outerH / 2, outerW, outerH);
        }
        cx.fillStyle = 'rgba(11, 15, 23, 0.45)';
        cx.fill();
        cx.strokeStyle = (isHovered || isSelected) ? 'rgba(0, 255, 136, 0.90)' : 'rgba(0, 255, 136, 0.28)';
        cx.lineWidth = (isHovered || isSelected) ? 1.5 : 0.8;
        cx.stroke();

        // 2. 10x5mm Inner Pocket Socket Boundary
        cx.beginPath();
        if (typeof cx.roundRect === 'function') {
            cx.roundRect(-innerW / 2, -innerH / 2, innerW, innerH, innerH / 2);
        } else {
            cx.rect(-innerW / 2, -innerH / 2, innerW, innerH);
        }
        cx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        cx.lineWidth = 0.6;
        cx.stroke();

        // 3. 4mm Wire Pass-Through Notches on ends
        cx.strokeStyle = 'rgba(56, 189, 248, 0.40)';
        cx.lineWidth = 1.0;
        cx.beginPath();
        cx.moveTo(-outerW / 2, 0); cx.lineTo(-innerW / 2, 0);
        cx.moveTo(innerW / 2, 0); cx.lineTo(outerW / 2, 0);
        cx.stroke();

        // 4. Glow Bloom through Aperture
        if (isLit) {
            const glowR = params.glowSize;
            const grad = cx.createRadialGradient(0, 0, 1, 0, 0, glowR);
            grad.addColorStop(0, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.85 * bulbAlpha})`);
            grad.addColorStop(0.35, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.45 * bulbAlpha})`);
            grad.addColorStop(0.75, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.12 * bulbAlpha})`);
            grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

            cx.fillStyle = grad;
            cx.beginPath();
            cx.arc(0, 0, glowR, 0, Math.PI * 2);
            cx.fill();
        }

        // 5. Centered 3mm Square or Ø 3mm Round Optical Window Aperture
        const isRound = (params.tpuWindowShape === 'round' || params.tpuWindowShape === 'circle');
        cx.beginPath();
        if (isRound) {
            cx.arc(0, 0, winSq / 2, 0, Math.PI * 2);
        } else {
            cx.rect(-winSq / 2, -winSq / 2, winSq, winSq);
        }

        if (isLit) {
            cx.fillStyle = `rgba(${Math.min(255, col.r + 35)}, ${Math.min(255, col.g + 35)}, ${Math.min(255, col.b + 35)}, ${Math.max(0.85, bulbAlpha)})`;
            cx.fill();
            cx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
            cx.lineWidth = 0.8;
            cx.stroke();

            // Inner white bright emission core
            cx.fillStyle = `rgba(255, 255, 255, ${0.95 * bulbAlpha})`;
            if (isRound) {
                cx.beginPath();
                cx.arc(0, 0, winSq * 0.25, 0, Math.PI * 2);
                cx.fill();
            } else {
                cx.fillRect(-winSq * 0.25, -winSq * 0.25, winSq * 0.5, winSq * 0.5);
            }
        } else {
            cx.fillStyle = '#080c14';
            cx.fill();
            cx.strokeStyle = 'rgba(75, 85, 100, 0.65)';
            cx.lineWidth = 0.8;
            cx.stroke();
            // Tiny unlit resin core
            cx.fillStyle = 'rgba(30, 36, 48, 0.9)';
            if (isRound) {
                cx.beginPath();
                cx.arc(0, 0, winSq * 0.25, 0, Math.PI * 2);
                cx.fill();
            } else {
                cx.fillRect(-winSq * 0.25, -winSq * 0.25, winSq * 0.5, winSq * 0.5);
            }
        }

        cx.restore();
    } else if (params.showPillSlots) {
        // Physical scale: 18.0 inch wide garment (457.2 mm)
        const s = getShirtBounds();
        const ppm = s.width / 457.2;
        const slotW = Math.max(12, 6.0 * ppm); // 6mm slot width
        const slotH = Math.max(6, 3.0 * ppm);  // 3mm slot height
        const ledW = Math.max(8, 4.0 * ppm);   // 4mm pebble LED width
        const ledH = Math.max(5.5, 3.0 * ppm); // 3mm pebble LED height
        const angle = getLedTangentAngle(index, leds);

        cx.save();
        cx.translate(x, y);
        cx.rotate(angle);

        // 1. Vinyl Cutout Hole (6mm x 3mm Pill Capsule)
        // Shows dark pinnie mesh fabric underneath where vinyl was cut away
        cx.beginPath();
        if (typeof cx.roundRect === 'function') {
            cx.roundRect(-slotW / 2, -slotH / 2, slotW, slotH, slotH / 2);
        } else {
            cx.ellipse(0, 0, slotW / 2, slotH / 2, 0, 0, Math.PI * 2);
        }
        cx.fillStyle = '#0a0d12'; // Dark pinnie mesh fabric backing
        cx.fill();
        cx.strokeStyle = 'rgba(255, 255, 255, 0.40)'; // Clean laser/blade cut vinyl edge
        cx.lineWidth = 1.0;
        cx.stroke();

        // 2. Visible mesh weave eyelet perforations inside the cutout
        const eyeletSpacing = slotW * 0.28;
        cx.fillStyle = '#040608';
        cx.beginPath();
        cx.arc(-eyeletSpacing, 0, slotH * 0.26, 0, Math.PI * 2);
        cx.arc(eyeletSpacing, 0, slotH * 0.26, 0, Math.PI * 2);
        cx.fill();

        // 3. Flat 3-conductor ribbon wire entering/exiting through mesh eyelets
        cx.strokeStyle = 'rgba(180, 185, 195, 0.45)';
        cx.lineWidth = Math.max(1.2, 1.0 * ppm);
        cx.beginPath();
        cx.moveTo(-slotW / 2, 0); cx.lineTo(-ledW / 2, 0);
        cx.moveTo(ledW / 2, 0); cx.lineTo(slotW / 2, 0);
        cx.stroke();

        // 4. Glow Bloom (Elliptical radiating from the lens)
        if (isLit) {
            const glowR = params.glowSize;
            const grad = cx.createRadialGradient(0, 0, 1, 0, 0, glowR);
            grad.addColorStop(0, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.85 * bulbAlpha})`);
            grad.addColorStop(0.35, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.45 * bulbAlpha})`);
            grad.addColorStop(0.75, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.12 * bulbAlpha})`);
            grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

            cx.fillStyle = grad;
            cx.beginPath();
            cx.ellipse(0, 0, glowR * 1.15, glowR * 0.90, 0, 0, Math.PI * 2);
            cx.fill();
        }

        // 5. 4mm x 3mm Clear Epoxy Resin Pebble Capsule
        cx.beginPath();
        if (typeof cx.roundRect === 'function') {
            cx.roundRect(-ledW / 2, -ledH / 2, ledW, ledH, ledH / 2);
        } else {
            cx.ellipse(0, 0, ledW / 2, ledH / 2, 0, 0, Math.PI * 2);
        }

        if (isLit) {
            cx.fillStyle = `rgba(${Math.min(255, col.r + 35)}, ${Math.min(255, col.g + 35)}, ${Math.min(255, col.b + 35)}, ${Math.max(0.85, bulbAlpha)})`;
            cx.fill();
            cx.strokeStyle = 'rgba(255, 255, 255, 0.75)';
            cx.lineWidth = 0.8;
            cx.stroke();

            // Inner intense white emission core
            cx.beginPath();
            cx.ellipse(0, 0, ledW * 0.35, ledH * 0.35, 0, 0, Math.PI * 2);
            cx.fillStyle = `rgba(255, 255, 255, ${0.95 * bulbAlpha})`;
            cx.fill();
        } else {
            cx.fillStyle = 'rgba(25, 30, 38, 0.90)';
            cx.fill();
            cx.strokeStyle = 'rgba(75, 82, 95, 0.6)';
            cx.lineWidth = 0.8;
            cx.stroke();

            // Unlit silicone micro-die chip center
            cx.fillStyle = 'rgba(160, 140, 90, 0.7)';
            cx.fillRect(-ledW * 0.15, -ledH * 0.15, ledW * 0.3, ledH * 0.3);
        }

        // 6. Resin dome top specular gloss highlight
        cx.beginPath();
        cx.ellipse(-ledW * 0.15, -ledH * 0.22, ledW * 0.25, ledH * 0.12, -0.1, 0, Math.PI * 2);
        cx.fillStyle = 'rgba(255, 255, 255, 0.65)';
        cx.fill();

        cx.restore();
    } else {
        // Standard Circular Light Bulb
        if (isLit) {
            const glowRadius = params.glowSize;
            const grad = cx.createRadialGradient(x, y, 1, x, y, glowRadius);
            grad.addColorStop(0, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.85 * bulbAlpha})`);
            grad.addColorStop(0.3, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.45 * bulbAlpha})`);
            grad.addColorStop(0.7, `rgba(${col.r}, ${col.g}, ${col.b}, ${0.12 * bulbAlpha})`);
            grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

            cx.fillStyle = grad;
            cx.beginPath();
            cx.arc(x, y, glowRadius, 0, Math.PI * 2);
            cx.fill();

            cx.beginPath();
            cx.arc(x, y, 4.5, 0, Math.PI * 2);
            cx.fillStyle = `rgba(${Math.min(255, col.r + 35)}, ${Math.min(255, col.g + 35)}, ${Math.min(255, col.b + 35)}, ${Math.max(0.7, bulbAlpha)})`;
            cx.fill();

            cx.beginPath();
            cx.arc(x, y, 2.0, 0, Math.PI * 2);
            cx.fillStyle = `rgba(255, 255, 255, ${0.9 * bulbAlpha})`;
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

    const FLOAT_TITLES = {
        'casey_jr_train': "FLOAT #1: CASEY JR. LOCOMOTIVE",
        'title_drum': "FLOAT #2: ELECTRICAL PARADE DRUM",
        'spinning_turtle': "FLOAT #3: THE SPINNING TURTLE",
        'spinning_snail': "FLOAT #4: THE SPINNING SNAIL",
        'cinderellas_coach': "FLOAT #5: CINDERELLA'S COACH",
        'cinderella_coach': "FLOAT #5: CINDERELLA'S COACH",
        'carriage_nohorses': "FLOAT #5: CARRIAGE (NO HORSES)",
        'builtin_dragon': "FLOAT #6: PETE'S DRAGON (ELLIOTT)",
        'petes_dragon': "FLOAT #6: PETE'S DRAGON (ELLIOTT)",
        'honor_america_eagle': "FLOAT #7: TO HONOR AMERICA (EAGLE)",
        'custom_image': "CUSTOM RUNNER DESIGN"
    };
    let shirtTitle = FLOAT_TITLES[currentGraphicType] || "MAIN STREET ELECTRICAL PARADE";
    drawRunningShirt(ctx, s.x, s.y, s.width, s.height, shirtTitle);
    drawPetesDragon(ctx, s);
    drawRaceBib(ctx, s);

    // Bilateral Symmetry Centerline Guide (x = 50%)
    if (params.showSymmetryAxis) {
        ctx.save();
        const topPt = normToCanvas({ x: 0.5, y: 0.08 });
        const botPt = normToCanvas({ x: 0.5, y: 0.92 });
        
        // Vertical dashed symmetry axis
        ctx.beginPath();
        ctx.moveTo(topPt.x, topPt.y);
        ctx.lineTo(botPt.x, botPt.y);
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.85)';
        ctx.lineWidth = 2.0;
        ctx.setLineDash([8, 6]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Top Axis Label Badge
        ctx.fillStyle = 'rgba(168, 85, 247, 0.95)';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText('🪞 50% Symmetry Axis', topPt.x, topPt.y - 6);
        
        // Small arrows on axis
        ctx.beginPath();
        ctx.moveTo(topPt.x - 4, topPt.y);
        ctx.lineTo(topPt.x, topPt.y - 5);
        ctx.lineTo(topPt.x + 4, topPt.y);
        ctx.moveTo(botPt.x - 4, botPt.y);
        ctx.lineTo(botPt.x, botPt.y + 5);
        ctx.lineTo(botPt.x + 4, botPt.y);
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.9)';
        ctx.lineWidth = 2.0;
        ctx.stroke();

        ctx.restore();
    }

    // Wire Tension Heatmap or Standard Wiring Trace
    if ((params.showWireTension || params.showWiring) && leds.length > 1) {
        ctx.save();
        const SHIRT_PHYSICAL_WIDTH_CM = 18.0 * 2.54;
        const SHIRT_PHYSICAL_HEIGHT_CM = 24.0 * 2.54;

        const singleSelIdx = (selectedLeds && selectedLeds.size === 1)
            ? Array.from(selectedLeds)[0]
            : (selectedLed !== null && (!selectedLeds || selectedLeds.size <= 1) ? selectedLed : null);

        if (params.showWireTension) {
            // Draw each segment with tension-coded color & thickness
            for (let i = 0; i < leds.length - 1; i++) {
                // If a single LED is selected, isolate and only render incoming (i === singleSelIdx - 1) and outgoing (i === singleSelIdx) wires
                if (singleSelIdx !== null && i !== singleSelIdx - 1 && i !== singleSelIdx) {
                    continue;
                }

                const p1 = normToCanvas(leds[i]);
                const p2 = normToCanvas(leds[i + 1]);
                const dxCm = (leds[i + 1].x - leds[i].x) * SHIRT_PHYSICAL_WIDTH_CM;
                const dyCm = (leds[i + 1].y - leds[i].y) * SHIRT_PHYSICAL_HEIGHT_CM;
                const distCm = Math.hypot(dxCm, dyCm);

                let strokeCol = 'rgba(0, 255, 136, 0.85)'; // Green optimal slack (4.5cm - 8.5cm)
                let lineW = 2.2;
                let isAlert = false;

                if (distCm > 9.2) {
                    strokeCol = 'rgba(255, 51, 102, 0.95)'; // Red alert (>9.2cm taut)
                    lineW = 3.6;
                    isAlert = true;
                } else if (distCm > 8.5) {
                    strokeCol = 'rgba(255, 193, 7, 0.85)'; // Yellow snug (8.5cm - 9.2cm)
                    lineW = 2.6;
                } else if (distCm < 4.5) {
                    strokeCol = 'rgba(56, 189, 248, 0.85)'; // Blue fold warning (<4.5cm excessive slack)
                    lineW = 1.8;
                }

                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.strokeStyle = strokeCol;
                ctx.lineWidth = lineW;
                if (!isAlert) {
                    ctx.setLineDash([5, 4]);
                } else {
                    ctx.setLineDash([]);
                }
                ctx.stroke();
                ctx.setLineDash([]);

                // If over-stretched alert or hovered or selected or zoomed, render distance label at segment midpoint
                const isHoverSegment = (hoveredLed === i || hoveredLed === i + 1);
                const isSelectedSegment = (singleSelIdx !== null && (singleSelIdx === i || singleSelIdx === i + 1)) || (selectedLed === i || selectedLed === i + 1);
                if (isAlert || isHoverSegment || isSelectedSegment || zoomScale > 1.4) {
                    const midX = (p1.x + p2.x) / 2;
                    const midY = (p1.y + p2.y) / 2;

                    ctx.save();
                    ctx.fillStyle = isAlert ? 'rgba(255, 51, 102, 0.9)' : 'rgba(13, 17, 23, 0.85)';
                    ctx.strokeStyle = isAlert ? '#fff' : strokeCol;
                    ctx.lineWidth = 1;
                    const tagTxt = `${distCm.toFixed(1)} cm`;
                    ctx.font = 'bold 9px monospace';
                    const tw = ctx.measureText(tagTxt).width;
                    ctx.fillRect(midX - tw / 2 - 3, midY - 6, tw + 6, 12);
                    ctx.strokeRect(midX - tw / 2 - 3, midY - 6, tw + 6, 12);
                    ctx.fillStyle = isAlert ? '#fff' : '#e6edf3';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(tagTxt, midX, midY);
                    ctx.restore();
                }

                // Alert glowing ring at the over-tension joint
                if (isAlert) {
                    ctx.beginPath();
                    ctx.arc(p2.x, p2.y, 8 + Math.sin(timeMs * 0.008) * 2, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(255, 51, 102, 0.8)';
                    ctx.lineWidth = 2.0;
                    ctx.stroke();
                }
            }
        } else {
            // Standard gold dashed wiring trace
            ctx.beginPath();
            if (singleSelIdx !== null) {
                // If a single LED is selected, only draw incoming and outgoing wires
                if (singleSelIdx > 0) {
                    const pInFrom = normToCanvas(leds[singleSelIdx - 1]);
                    const pInTo = normToCanvas(leds[singleSelIdx]);
                    ctx.moveTo(pInFrom.x, pInFrom.y);
                    ctx.lineTo(pInTo.x, pInTo.y);
                }
                if (singleSelIdx < leds.length - 1) {
                    const pOutFrom = normToCanvas(leds[singleSelIdx]);
                    const pOutTo = normToCanvas(leds[singleSelIdx + 1]);
                    ctx.moveTo(pOutFrom.x, pOutFrom.y);
                    ctx.lineTo(pOutTo.x, pOutTo.y);
                }
            } else {
                const p0 = normToCanvas(leds[0]);
                ctx.moveTo(p0.x, p0.y);
                for (let i = 1; i < leds.length; i++) {
                    const pt = normToCanvas(leds[i]);
                    ctx.lineTo(pt.x, pt.y);
                }
            }
            ctx.strokeStyle = 'rgba(255, 193, 7, 0.55)';
            ctx.lineWidth = 1.8;
            ctx.setLineDash([5, 4]);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Highlight Start LED 0 (Green indicator ring) and End LED (Red indicator ring)
        if (singleSelIdx === null || singleSelIdx === 0) {
            const p0 = normToCanvas(leds[0]);
            ctx.beginPath();
            ctx.arc(p0.x, p0.y, 9.5, 0, Math.PI * 2);
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }

        if (singleSelIdx === null || singleSelIdx === leds.length - 1) {
            const pEnd = normToCanvas(leds[leds.length - 1]);
            ctx.beginPath();
            ctx.arc(pEnd.x, pEnd.y, 9.5, 0, Math.PI * 2);
            ctx.strokeStyle = '#ff4d6d';
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }
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
// 7-SHIRT FLEET PARADE VIEW & PRESET MANAGER (NATURAL ATHLETIC PROPORTIONS)
// ============================================================================
const DEFAULT_FLEET_ROSTER = [
    { slot: 0, num: "01", icon: "🚂", fullName: "The Train (Casey Jr.)", name: "The Train", tag: "CASEY JR.", color: "#e63946", accent: "Red", role: "👑 Fleet Leader (Broadcast)", preset: "server:casey_jr_train.json", defaultGraphic: "casey_jr_train" },
    { slot: 1, num: "02", icon: "🥁", fullName: "Electrical Parade Drum", name: "Title Drum", tag: "THE DRUM", color: "#ffb703", accent: "Gold", role: "📡 Follower Float", preset: "server:title_drum.json", defaultGraphic: "title_drum" },
    { slot: 2, num: "03", icon: "🐢", fullName: "The Spinning Turtle", name: "The Turtle", tag: "TURTLE", color: "#2ec4b6", accent: "Teal", role: "📡 Follower Float", preset: "server:spinning_turtle.json", defaultGraphic: "spinning_turtle" },
    { slot: 3, num: "04", icon: "🐌", fullName: "The Spinning Snail", name: "The Snail", tag: "SNAIL", color: "#ff007f", accent: "Pink", role: "📡 Follower Float", preset: "server:spinning_snail.json", defaultGraphic: "spinning_snail" },
    { slot: 4, num: "05", icon: "🩵", fullName: "Cinderella's Coach", name: "Cinderella", tag: "COACH", color: "#48cae4", accent: "Cyan", role: "📡 Follower Float", preset: "server:cinderellas_coach_both_wheel.json", defaultGraphic: "cinderella_coach" },
    { slot: 5, num: "06", icon: "🐉", fullName: "Pete's Dragon (Elliott)", name: "Pete's Dragon", tag: "ELLIOTT", color: "#00ff88", accent: "Green", role: "📡 Follower Float", preset: "server:petes_dragon.json", defaultGraphic: "builtin_dragon" },
    { slot: 6, num: "07", icon: "🦅", fullName: "To Honor America", name: "Flag & Eagle", tag: "HONOR AMERICA", color: "#3a86ff", accent: "Patriotic", role: "📡 Follower Float", preset: "server:honor_america_eagle.json", defaultGraphic: "honor_america_eagle" }
];

let fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
let fleetSyncMode = 'parade_20s'; // 'parade_20s' (default), 'wave', 'free', or 'show'
let fleetWaveCycleDurationMs = 7000; // 7.0s default
let fleetHoveredRunner = -1;
let fleetSelectedRunner = -1;
const fleetPresetCache = {};

const fleetPresetPromises = {};

// Asynchronously load and cache preset data for a runner
async function getPresetDataForRunner(runner) {
    if (!runner) return null;
    const key = runner.preset;
    if (!key) return null;
    if (fleetPresetCache[key]) return fleetPresetCache[key];
    if (fleetPresetPromises[key]) return await fleetPresetPromises[key];

    fleetPresetPromises[key] = (async () => {
        if (key.startsWith('server:')) {
            const filename = key.replace('server:', '');
            try {
                const res = await fetch(`/api/preset/${encodeURIComponent(filename)}`);
                if (res.ok) {
                    const data = await res.json();
                    fleetPresetCache[key] = data;
                    return data;
                }
            } catch (e) {
                console.warn("Could not fetch server preset", filename, e);
            }
        } else if (key.startsWith('local:')) {
            const name = key.replace('local:', '');
            try {
                const localProfiles = JSON.parse(localStorage.getItem('msep_custom_presets') || '{}');
                if (localProfiles[name]) {
                    fleetPresetCache[key] = localProfiles[name];
                    return localProfiles[name];
                }
            } catch (e) {}
        } else if (key === 'current_editor') {
            return {
                name: "Current Editor Preset",
                ledCount: leds.length,
                leds: leds,
                graphicType: currentGraphicType,
                customArtworkDataUrl: customArtworkDataUrl,
                animationGroups: animationGroups,
                settings: { ...params, pattern: activePattern },
                sequence: { loopDuration: sequenceLoopDuration, cues: sequenceCues }
            };
        }
        return null;
    })();

    return await fleetPresetPromises[key];
}

// Standard Disney palette colors for the 20-second parade routine wave
const FLEET_WAVE_STANDARD_COLORS = [
    { name: "Belle Gold", r: 255, g: 193, b: 7, hex: "#ffc107" },
    { name: "Alice Cyan", r: 0, g: 240, b: 255, hex: "#00f0ff" },
    { name: "Coral Rose", r: 255, g: 60, b: 120, hex: "#ff3c78" },
    { name: "Electric Pink", r: 255, g: 25, b: 230, hex: "#ff19e6" },
    { name: "Electric Lime", r: 85, g: 255, b: 16, hex: "#55ff10" },
    { name: "Cinderella Blue", r: 0, g: 119, b: 255, hex: "#0077ff" },
    { name: "Cheshire Violet", r: 175, g: 37, b: 255, hex: "#af25ff" },
    { name: "Deep Indigo", r: 75, g: 35, b: 190, hex: "#4b23be" },
    { name: "Flame Orange", r: 255, g: 120, b: 0, hex: "#ff7800" },
    { name: "Starlight White", r: 255, g: 250, b: 242, hex: "#fffaf2" },
    { name: "Dragon Green", r: 0, g: 255, b: 35, hex: "#00ff23" },
    { name: "Mickey Red", r: 255, g: 13, b: 26, hex: "#ff0d1a" }
];

// Returns the active standard color for the current 20-second cycle.
// Guaranteed to stay identical during forward wave (1s-2s), backward wave (2s-3s), 5s pulse (3s-8s),
// and sparkle storm (8s-10s) within that cycle, and cycles to a new random standard color on the next
// 20-second cycle without consecutive repeats.
function getFleetRoutineWaveColor(timeMs) {
    const cycle = Math.floor(Math.max(0, timeMs) / 20000);
    const count = FLEET_WAVE_STANDARD_COLORS.length;
    // Step 5 is coprime to 12 (gcd=1), cycling all 12 colors without immediate repeats
    const idx = (cycle * 5) % count;
    return FLEET_WAVE_STANDARD_COLORS[idx];
}

// ============================================================================
// 7-SHIRT FLEET SHOW CREATOR ENGINE & 14-BLOCK CHOREOGRAPHY DEFINITIONS
// ============================================================================
const FLEET_BLOCK_DEFS = {
    'wave_forward': {
        name: "Forward Wave (1 ➔ 7)",
        icon: "🌊",
        category: "waves",
        defaultDuration: 1.5,
        defaultParams: { colorMode: "cycle_random", trailLengthShirts: 2.0, incandescentCrest: true }
    },
    'wave_reverse': {
        name: "Reverse Wave (7 ➔ 1)",
        icon: "🌊",
        category: "waves",
        defaultDuration: 1.5,
        defaultParams: { colorMode: "match_previous", trailLengthShirts: 2.0, incandescentCrest: true }
    },
    'fleet_pulse': {
        name: "All-Fleet Majestic Breath",
        icon: "💓",
        category: "sync",
        defaultDuration: 5.0,
        defaultParams: { colorMode: "match_previous", pulseSpeedBpm: 36, minBrightness: 0.28, peakFlare: true }
    },
    'sparkle_storm': {
        name: "Starlight Sparkle Storm",
        icon: "✨",
        category: "sync",
        defaultDuration: 3.0,
        defaultParams: { sparkleColorMix: "wave_and_white", density: 0.75 }
    },
    'center_burst': {
        name: "Center-Outward Energy Burst",
        icon: "🎆",
        category: "waves",
        defaultDuration: 2.0,
        defaultParams: { colorMode: "cycle_random", peakFlare: true }
    },
    'converge_center': {
        name: "Converge Inward (1 & 7 ➔ 4)",
        icon: "🎯",
        category: "waves",
        defaultDuration: 2.0,
        defaultParams: { colorMode: "cycle_random", peakFlare: true }
    },
    'wig_wag': {
        name: "Odd/Even Marquee Wig-Wag",
        icon: "🎪",
        category: "theatrical",
        defaultDuration: 2.5,
        defaultParams: { speedBpm: 120, colorA: "Belle Gold", colorB: "Alice Cyan" }
    },
    'baton_chase': {
        name: "Baton Leapfrog Chase",
        icon: "🏃",
        category: "waves",
        defaultDuration: 3.0,
        defaultParams: { direction: "1_to_7", colorMode: "cycle_random" }
    },
    'ping_pong_wave': {
        name: "Ping-Pong Double Bounce",
        icon: "🏓",
        category: "waves",
        defaultDuration: 3.0,
        defaultParams: { bounces: 2, colorMode: "cycle_random" }
    },
    'color_wash_chase': {
        name: "Color Wash Progressive Fill",
        icon: "🎨",
        category: "sync",
        defaultDuration: 3.5,
        defaultParams: { colorMode: "cycle_random" }
    },
    'rainbow_sweep': {
        name: "Rainbow Fleet Sweep",
        icon: "🌈",
        category: "sync",
        defaultDuration: 4.0,
        defaultParams: { speedBpm: 120 }
    },
    'strobe_all': {
        name: "Grand Finale Strobe",
        icon: "⚡",
        category: "theatrical",
        defaultDuration: 2.0,
        defaultParams: { speedBpm: 240, color: "Starlight White" }
    },
    'shimmer_drift': {
        name: "Shimmer & Twinkle Drift",
        icon: "🌌",
        category: "sync",
        defaultDuration: 4.0,
        defaultParams: { colorMode: "match_previous" }
    },
    'grand_finale': {
        name: "Carnival Finale Crescendo",
        icon: "🎆",
        category: "theatrical",
        defaultDuration: 5.0,
        defaultParams: { speedBpm: 150, strobeClimax: true }
    },
    'blackout': {
        name: "Theatrical Blackout (Off)",
        icon: "🌑",
        category: "theatrical",
        defaultDuration: 1.0,
        defaultParams: {}
    },
    'color_collision': {
        name: "Dual Collision & Shockwave",
        icon: "💥",
        category: "waves",
        defaultDuration: 3.0,
        defaultParams: { colorMode: "cycle_random" }
    },
    'cross_dissolve_chase': {
        name: "Silky Cascade Dissolve",
        icon: "🌊✨",
        category: "sync",
        defaultDuration: 3.5,
        defaultParams: { colorMode: "cycle_random" }
    },
    'ripple_echo': {
        name: "Mirror Pair Echo (Butterfly)",
        icon: "🦋",
        category: "theatrical",
        defaultDuration: 2.5,
        defaultParams: { colorMode: "cycle_random" }
    },
    'sparkle_cascade': {
        name: "Fairy Dust Waterfall",
        icon: "🪄",
        category: "waves",
        defaultDuration: 3.0,
        defaultParams: { colorMode: "cycle_random" }
    }
};

// Active Fleet Show Choreography State
let activeFleetShow = null;
let fleetShowActive = false; // True only while one-shot 30s routine is playing
let fleetShowElapsedSec = 0.0;
let fleetShowLastTimestamp = 0;
let lastFleetTriggerTime = 0; // For 300ms software debounce
let fleetShowCycleIndex = 0;
let activeFleetShowLastColor = null;

// Resolve dynamic color for a fleet block (palette cycle, match previous, or named Disney color)
function getActiveFleetColor(colorMode, blockIndex) {
    if (!colorMode || colorMode === 'cycle_random' || colorMode === 'palette_cycle') {
        const count = FLEET_WAVE_STANDARD_COLORS.length;
        const idx = ((fleetShowCycleIndex + (blockIndex || 0)) * 5) % count;
        const col = FLEET_WAVE_STANDARD_COLORS[idx];
        activeFleetShowLastColor = col;
        return col;
    }
    if (colorMode === 'match_previous' && activeFleetShowLastColor) {
        return activeFleetShowLastColor;
    }
    const matched = FLEET_WAVE_STANDARD_COLORS.find(c => c.name.toLowerCase() === String(colorMode).toLowerCase());
    if (matched) {
        activeFleetShowLastColor = matched;
        return matched;
    }
    const defCol = FLEET_WAVE_STANDARD_COLORS[0];
    activeFleetShowLastColor = defCol;
    return defCol;
}

// Find the block active at a specific timestamp in the fleet routine
function getActiveFleetBlock(elapsedSec) {
    if (!activeFleetShow || !Array.isArray(activeFleetShow.blocks) || activeFleetShow.blocks.length === 0) return null;
    const t = Math.max(0, elapsedSec);
    for (let i = 0; i < activeFleetShow.blocks.length; i++) {
        const b = activeFleetShow.blocks[i];
        const start = b.startTime !== undefined ? b.startTime : 0;
        const dur = b.duration || 1.0;
        if (t >= start && t < (start + dur)) {
            return { block: b, index: i, start, dur, localT: t - start };
        }
    }
    const last = activeFleetShow.blocks[activeFleetShow.blocks.length - 1];
    return { block: last, index: activeFleetShow.blocks.length - 1, start: last.startTime || 0, dur: last.duration || 1.0, localT: last.duration || 1.0 };
}

// Helper: Convert HSL to RGB
function hslToRgb(h, s, l) {
    s /= 100;
    l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    return {
        r: Math.round(255 * f(0)),
        g: Math.round(255 * f(8)),
        b: Math.round(255 * f(4))
    };
}

// Evaluate LED color for a runner during active 30s fleet show
function evalActiveFleetShowColor(runnerIndex, runner, presetData, ledIndex, totalLeds, timeMs, elapsedSec) {
    const activeInfo = getActiveFleetBlock(elapsedSec);
    if (!activeInfo) return { r: 0, g: 0, b: 0, alpha: 0.0 };

    const block = activeInfo.block;
    const bType = block.type || 'wave_forward';
    const dur = Math.max(0.1, block.duration || 1.0);
    const localT = Math.min(dur, Math.max(0, activeInfo.localT));
    const localP = localT / dur; // 0.0 to 1.0
    const params = block.params || {};

    const waveColor = getActiveFleetColor(params.colorMode || 'cycle_random', activeInfo.index);
    const ledsArr = (presetData && presetData.leds) ? presetData.leds : [];
    const led = ledsArr[ledIndex] || {};
    const ledNormX = (typeof led.x === 'number') ? led.x : (ledIndex / Math.max(1, totalLeds));
    const globalPos = runnerIndex + ledNormX;

    // 1. BLACKOUT
    if (bType === 'blackout') {
        return { r: 0, g: 0, b: 0, alpha: 0.0 };
    }

    // 2. FORWARD WAVE (1 ➔ 7)
    if (bType === 'wave_forward') {
        const sweepPos = -0.3 + localP * 7.6;
        const delta = sweepPos - globalPos;
        const trailLen = params.trailLengthShirts || 2.0;

        if (delta < -0.35) {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        } else if (delta < 0.0) {
            const fRise = (delta + 0.35) / 0.35;
            return { r: Math.round(waveColor.r * fRise * 0.9), g: Math.round(waveColor.g * fRise * 0.9), b: Math.round(waveColor.b * fRise * 0.9), alpha: fRise };
        } else if (delta < 0.25) {
            const crestMix = delta / 0.25;
            const coreR = Math.min(255, Math.round(255 * (1.0 - 0.2 * crestMix) + waveColor.r * (0.2 * crestMix)));
            const coreG = Math.min(255, Math.round(255 * (1.0 - 0.2 * crestMix) + waveColor.g * (0.2 * crestMix)));
            const coreB = Math.min(255, Math.round(255 * (1.0 - 0.2 * crestMix) + waveColor.r * (0.2 * crestMix)));
            return { r: coreR, g: coreG, b: coreB, alpha: 1.0 };
        } else if (delta < (0.25 + trailLen)) {
            const trailFraction = (delta - 0.25) / trailLen;
            const decay = Math.pow(Math.max(0, 1.0 - trailFraction), 1.35);
            return { r: Math.round(waveColor.r * decay), g: Math.round(waveColor.g * decay), b: Math.round(waveColor.b * decay), alpha: Math.max(0.0, decay * 0.95) };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 3. REVERSE WAVE (7 ➔ 1)
    if (bType === 'wave_reverse') {
        const sweepPos = 7.3 - localP * 7.6;
        const delta = globalPos - sweepPos;
        const trailLen = params.trailLengthShirts || 2.0;

        if (delta < -0.35) {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        } else if (delta < 0.0) {
            const fRise = (delta + 0.35) / 0.35;
            return { r: Math.round(waveColor.r * fRise * 0.9), g: Math.round(waveColor.g * fRise * 0.9), b: Math.round(waveColor.b * fRise * 0.9), alpha: fRise };
        } else if (delta < 0.25) {
            const crestMix = delta / 0.25;
            const coreR = Math.min(255, Math.round(255 * (1.0 - 0.2 * crestMix) + waveColor.r * (0.2 * crestMix)));
            const coreG = Math.min(255, Math.round(255 * (1.0 - 0.2 * crestMix) + waveColor.r * (0.2 * crestMix)));
            const coreB = Math.min(255, Math.round(255 * (1.0 - 0.2 * crestMix) + waveColor.r * (0.2 * crestMix)));
            return { r: coreR, g: coreG, b: coreB, alpha: 1.0 };
        } else if (delta < (0.25 + trailLen)) {
            const trailFraction = (delta - 0.25) / trailLen;
            const decay = Math.pow(Math.max(0, 1.0 - trailFraction), 1.35);
            return { r: Math.round(waveColor.r * decay), g: Math.round(waveColor.g * decay), b: Math.round(waveColor.b * decay), alpha: Math.max(0.0, decay * 0.95) };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 4. ALL-FLEET MAJESTIC BREATH PULSE
    if (bType === 'fleet_pulse') {
        const cycles = 3.0;
        const breath = 0.5 + 0.5 * Math.sin(localP * Math.PI * 2.0 * cycles - Math.PI * 0.5);
        const minBright = params.minBrightness || 0.28;
        const intensity = minBright + (1.0 - minBright) * breath;
        const boost = (breath > 0.82) ? Math.round((breath - 0.82) / 0.18 * 60) : 0;
        return {
            r: Math.min(255, Math.round(waveColor.r * intensity + boost)),
            g: Math.min(255, Math.round(waveColor.g * intensity + boost)),
            b: Math.min(255, Math.round(waveColor.b * intensity + boost)),
            alpha: Math.max(0.35, intensity)
        };
    }

    // 5. STARLIGHT SPARKLE STORM
    if (bType === 'sparkle_storm') {
        const frameBucket = Math.floor(timeMs / 45);
        const hash = Math.sin(runnerIndex * 43.17 + ledIndex * 93.31 + frameBucket * 19.73) * 43758.5453;
        const rnd = hash - Math.floor(hash);

        if (rnd > 0.72) {
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        } else if (rnd > 0.40) {
            return { r: waveColor.r, g: waveColor.g, b: waveColor.b, alpha: 0.98 };
        } else if (rnd > 0.18) {
            return {
                r: Math.min(255, Math.round(waveColor.r * 0.55 + 255 * 0.45)),
                g: Math.min(255, Math.round(waveColor.g * 0.55 + 255 * 0.45)),
                b: Math.min(255, Math.round(waveColor.b * 0.55 + 255 * 0.45)),
                alpha: 0.88
            };
        } else {
            const shim = 0.22 + 0.32 * Math.sin((timeMs * 0.015) + ledIndex * 0.8 + runnerIndex * 1.5);
            return { r: Math.round(waveColor.r * shim), g: Math.round(waveColor.g * shim), b: Math.round(waveColor.b * shim), alpha: Math.max(0.18, shim) };
        }
    }

    // 6. CENTER-OUTWARD ENERGY BURST (Float 4 ➔ 1 & 7)
    if (bType === 'center_burst') {
        const distFromCenter = Math.abs(runnerIndex - 3.0) + (ledNormX - 0.5) * 0.5;
        const blastRadius = localP * 4.2;
        const delta = blastRadius - distFromCenter;

        if (delta < -0.3) {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        } else if (delta < 0.2) {
            // White-hot shockwave front
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        } else if (delta < 1.6) {
            const fade = 1.0 - (delta - 0.2) / 1.4;
            return { r: Math.round(waveColor.r * fade), g: Math.round(waveColor.g * fade), b: Math.round(waveColor.b * fade), alpha: fade * 0.9 };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 7. CONVERGE INWARD (Floats 1 & 7 ➔ Float 4)
    if (bType === 'converge_center') {
        const distInward = (runnerIndex <= 3) ? (runnerIndex + ledNormX) : (6.0 - runnerIndex + (1.0 - ledNormX));
        const waveFront = localP * 3.8;
        const delta = Math.abs(waveFront - distInward);

        if (localP > 0.88 && runnerIndex === 3) {
            // Central collision flash!
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        }
        if (delta < 0.3) {
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        } else if (delta < 1.4) {
            const f = 1.0 - (delta - 0.3) / 1.1;
            return { r: Math.round(waveColor.r * f), g: Math.round(waveColor.g * f), b: Math.round(waveColor.b * f), alpha: f * 0.85 };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 8. ODD/EVEN MARQUEE WIG-WAG
    if (bType === 'wig_wag') {
        const bpm = params.speedBpm || 120;
        const beat = Math.floor(localT * (bpm / 60) * 2) % 2;
        const isOdd = (runnerIndex % 2 === 1);
        const activeGroup = (beat === 1) ? isOdd : !isOdd;

        if (activeGroup) {
            return { r: waveColor.r, g: waveColor.g, b: waveColor.b, alpha: 1.0 };
        } else {
            // Opposite floats soft accent or unlit
            const dimCol = FLEET_WAVE_STANDARD_COLORS[(activeInfo.index + 3) % FLEET_WAVE_STANDARD_COLORS.length];
            return { r: Math.round(dimCol.r * 0.15), g: Math.round(dimCol.g * 0.15), b: Math.round(dimCol.b * 0.15), alpha: 0.2 };
        }
    }

    // 9. BATON LEAPFROG CHASE
    if (bType === 'baton_chase') {
        const activeFloat = Math.min(6, Math.floor(localP * 7.0));
        if (runnerIndex === activeFloat) {
            const spin = Math.sin((timeMs * 0.02) + ledIndex * 0.6) > 0.3 ? 1.0 : 0.4;
            return { r: Math.min(255, Math.round(waveColor.r * spin + 60)), g: Math.min(255, Math.round(waveColor.g * spin + 60)), b: Math.min(255, Math.round(waveColor.b * spin + 60)), alpha: 1.0 };
        } else {
            const resting = 0.15 + 0.12 * Math.sin(timeMs * 0.005 + ledIndex);
            return { r: Math.round(waveColor.r * resting), g: Math.round(waveColor.g * resting), b: Math.round(waveColor.b * resting), alpha: resting };
        }
    }

    // 10. PING-PONG DOUBLE BOUNCE
    if (bType === 'ping_pong_wave') {
        const bouncePhase = (localP * 4.0) % 2.0; // 2 complete round-trips
        const sweepPos = (bouncePhase < 1.0) ? (bouncePhase * 7.0) : (7.0 - (bouncePhase - 1.0) * 7.0);
        const delta = Math.abs(sweepPos - globalPos);

        if (delta < 0.25) {
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        } else if (delta < 1.5) {
            const dec = Math.pow(1.0 - (delta - 0.25) / 1.25, 1.4);
            return { r: Math.round(waveColor.r * dec), g: Math.round(waveColor.g * dec), b: Math.round(waveColor.b * dec), alpha: dec };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 11. COLOR WASH PROGRESSIVE FILL
    if (bType === 'color_wash_chase') {
        const threshold = localP * 7.5;
        if (runnerIndex < Math.floor(threshold)) {
            // Already ignited: glowing steadily
            const shim = 0.75 + 0.25 * Math.sin(timeMs * 0.006 + ledIndex * 0.4);
            return { r: Math.round(waveColor.r * shim), g: Math.round(waveColor.g * shim), b: Math.round(waveColor.b * shim), alpha: 0.9 };
        } else if (runnerIndex === Math.floor(threshold)) {
            // Currently igniting: brilliant white flare
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 12. RAINBOW FLEET SWEEP
    if (bType === 'rainbow_sweep') {
        const hue = Math.floor((localP * 720) + (runnerIndex * 51) + (ledIndex * 2.2)) % 360;
        const rgb = hslToRgb(hue, 100, 52);
        return { r: rgb.r, g: rgb.g, b: rgb.b, alpha: 0.98 };
    }

    // 13. GRAND FINALE STROBE
    if (bType === 'strobe_all') {
        const flash = Math.sin(localT * Math.PI * 26.0) > 0.0;
        if (flash) {
            return { r: 255, g: 255, b: 255, alpha: 1.0 };
        } else {
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 14. SHIMMER & TWINKLE DRIFT
    if (bType === 'shimmer_drift') {
        const wave = 0.5 + 0.5 * Math.sin(localP * Math.PI * 4.0 + runnerIndex * 0.9 + ledIndex * 0.2);
        const spk = Math.sin(timeMs * 0.015 + runnerIndex * 13.7 + ledIndex * 31.3) > 0.85 ? 1.0 : wave;
        return { r: Math.round(waveColor.r * spk), g: Math.round(waveColor.g * spk), b: Math.round(waveColor.b * spk), alpha: Math.max(0.2, spk) };
    }

    // 15. CARNIVAL FINALE CRESCENDO
    if (bType === 'grand_finale') {
        if (localP < 0.6) {
            const p = localP / 0.6;
            const sweep = (Math.sin(p * Math.PI * 6.0) * 0.5 + 0.5) * 7.0;
            const delta = Math.abs(sweep - globalPos);
            const intensity = 0.4 + 0.6 * p;
            if (delta < 0.4) {
                return { r: 255, g: 255, b: 255, alpha: 1.0 };
            } else {
                return { r: Math.round(waveColor.r * intensity), g: Math.round(waveColor.g * intensity), b: Math.round(waveColor.b * intensity), alpha: intensity };
            }
        } else {
            // Climax strobe & sparkle explosion
            const flash = Math.sin(localT * Math.PI * 30.0) > 0.2;
            if (flash) {
                return { r: 255, g: 255, b: 255, alpha: 1.0 };
            } else {
                return { r: waveColor.r, g: waveColor.g, b: waveColor.b, alpha: 0.9 };
            }
        }
    }

    // 16. DUAL COLLISION & SHOCKWAVE (1 & 7 ➔ 4 ➔ 1 & 7)
    if (bType === 'color_collision') {
        if (localP < 0.45) {
            const inP = localP / 0.45;
            const headL = inP * 3.0;
            const headR = 6.0 - (inP * 3.0);
            const distL = Math.abs(globalPos - headL);
            const distR = Math.abs(globalPos - headR);
            const minDist = Math.min(distL, distR);
            if (minDist <= 1.4) {
                const intensity = 1.0 - (minDist / 1.4);
                const col = (distL < distR) ? waveColor : { r: 255, g: 60, b: 180 };
                return { r: Math.round(col.r * intensity), g: Math.round(col.g * intensity), b: Math.round(col.b * intensity), alpha: intensity };
            }
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        } else if (localP < 0.60) {
            // Impact supernova explosion at Float 4 (Peter Pan)
            if (runnerIndex === 3) {
                return { r: 255, g: 255, b: 255, alpha: 1.0 };
            } else {
                return { r: Math.round(waveColor.r * 0.15), g: Math.round(waveColor.g * 0.15), b: Math.round(waveColor.b * 0.15), alpha: 0.2 };
            }
        } else {
            // Rebound shockwave
            const shockP = (localP - 0.60) / 0.40;
            const shockRadius = shockP * 3.2;
            const distFromCenter = Math.abs(runnerIndex - 3.0);
            const ringDist = Math.abs(distFromCenter - shockRadius);
            if (ringDist <= 1.2) {
                const intensity = 1.0 - (ringDist / 1.2);
                return { r: Math.min(255, Math.round(waveColor.r * intensity + 80)), g: Math.min(255, Math.round(waveColor.g * intensity + 80)), b: Math.round(waveColor.b * intensity), alpha: intensity };
            }
            return { r: 0, g: 0, b: 0, alpha: 0.0 };
        }
    }

    // 17. SILKY CASCADE DISSOLVE (1 ➔ 7)
    if (bType === 'cross_dissolve_chase') {
        const runnerOffset = runnerIndex / 7.0;
        const localRunnerP = Math.min(1.0, Math.max(0.0, (localP - runnerOffset * 0.5) / 0.5));
        const blendAmt = 0.5 * (1.0 - Math.cos(localRunnerP * Math.PI));
        const colA = waveColor;
        const colB = { r: 0, g: 220, b: 255 }; // Enchanted Blue
        return {
            r: Math.round(colA.r * (1.0 - blendAmt) + colB.r * blendAmt),
            g: Math.round(colA.g * (1.0 - blendAmt) + colB.g * blendAmt),
            b: Math.round(colA.b * (1.0 - blendAmt) + colB.b * blendAmt),
            alpha: 0.95
        };
    }

    // 18. MIRROR PAIR ECHO (BUTTERFLY RIPPLE)
    if (bType === 'ripple_echo') {
        const subPhase = Math.floor(localP * 4.0) % 4; // 0: 4, 1: 3&5, 2: 2&6, 3: 1&7
        const subP = (localP * 4.0) % 1.0;
        const pulse = Math.sin(subP * Math.PI);
        let isActivePair = false;
        if (subPhase === 0 && runnerIndex === 3) isActivePair = true;
        else if (subPhase === 1 && (runnerIndex === 2 || runnerIndex === 4)) isActivePair = true;
        else if (subPhase === 2 && (runnerIndex === 1 || runnerIndex === 5)) isActivePair = true;
        else if (subPhase === 3 && (runnerIndex === 0 || runnerIndex === 6)) isActivePair = true;

        if (isActivePair) {
            return { r: Math.round(waveColor.r * pulse), g: Math.round(waveColor.g * pulse), b: Math.round(waveColor.b * pulse), alpha: pulse };
        } else {
            return { r: Math.round(waveColor.r * 0.12), g: Math.round(waveColor.g * 0.12), b: Math.round(waveColor.b * 0.12), alpha: 0.15 };
        }
    }

    // 19. FAIRY DUST WATERFALL CASCADE
    if (bType === 'sparkle_cascade') {
        const center = localP * 6.0;
        const dist = Math.abs(runnerIndex - center);
        if (dist <= 1.5) {
            const intensity = 1.0 - (dist / 1.5);
            const isSparkle = Math.random() < (0.45 * intensity);
            if (isSparkle) {
                return { r: 255, g: 255, b: 255, alpha: 1.0 };
            } else {
                return { r: Math.min(255, Math.round(waveColor.r * intensity + 40)), g: Math.min(255, Math.round(waveColor.g * intensity + 40)), b: Math.round(waveColor.b * intensity), alpha: Math.max(0.3, intensity) };
            }
        }
        return { r: Math.round(waveColor.r * 0.12), g: Math.round(waveColor.g * 0.12), b: Math.round(waveColor.b * 0.12), alpha: 0.15 };
    }

    return { r: 0, g: 0, b: 0, alpha: 0.0 };
}

// Compute dynamic color for an individual LED on one of the 7 runners
function computeRunnerLedColor(runnerIndex, runner, presetData, ledIndex, totalLeds, timeMs, waveProgress, isCurrentWave) {
    const isLivePreview = (runnerIndex === activeSingleShirtRunnerSlot) || (runner && runner.preset === 'current_editor');
    const effectiveData = isLivePreview ? getLiveSingleShirtPresetData() : presetData;
    const ledsArr = (effectiveData && effectiveData.leds) ? effectiveData.leds : [];
    const led = ledsArr[ledIndex] || {};
    const hasColor = !!led.color;
    const c = hasColor ? led.color : { r: 255, g: 255, b: 255 };

    // 0. Radar Identify Flash Strobe (3 rapid color flashes)
    if (radarIdentifyFlashes[runnerIndex]) {
        const flash = radarIdentifyFlashes[runnerIndex];
        const elapsed = timeMs - flash.startTime;
        if (elapsed >= 0 && elapsed <= flash.duration) {
            const cycle = Math.floor(elapsed / 120);
            if (cycle % 2 === 0) {
                return { r: flash.color.r, g: flash.color.g, b: flash.color.b, alpha: 1.0 };
            } else {
                return { r: 0, g: 0, b: 0, alpha: 0.0 };
            }
        } else if (elapsed > flash.duration) {
            delete radarIdentifyFlashes[runnerIndex];
        }
    }

    // 0B. Rapid Attendance Roll Call (4.0s wave: 500ms per float 1..7, then 500ms unison double emerald green flash)
    if (rapidRollCallActive) {
        const elapsed = timeMs - rapidRollCallStartTime;
        if (elapsed >= 0 && elapsed < 4000) {
            if (elapsed < 3500) {
                const activeSlot = Math.floor(elapsed / 500); // 0..6
                if (runnerIndex === activeSlot) {
                    const radarFloat = DEFAULT_FLEET_RADAR[runnerIndex];
                    const col = hexToRgb(radarFloat ? radarFloat.color : '#ffffff');
                    return { r: col.r, g: col.g, b: col.b, alpha: 1.0 };
                } else {
                    return { r: 0, g: 0, b: 0, alpha: 0.0 };
                }
            } else {
                // Finale (3500ms - 4000ms): Double emerald green flash across ALL 7 floats!
                const finaleMs = elapsed - 3500;
                if ((finaleMs < 200) || (finaleMs >= 300 && finaleMs < 500)) {
                    return { r: 0, g: 255, b: 80, alpha: 1.0 };
                } else {
                    return { r: 0, g: 0, b: 0, alpha: 0.0 };
                }
            }
        } else if (elapsed >= 4000) {
            rapidRollCallActive = false;
        }
    }

    // 0C. Corral Standby Mode (12% Dim Twinkle <120mA)
    if (isCorralStandbyActive) {
        const floatObj = (DEFAULT_FLEET_RADAR && DEFAULT_FLEET_RADAR[runnerIndex]) ? DEFAULT_FLEET_RADAR[runnerIndex] : (DEFAULT_FLEET_RADAR ? DEFAULT_FLEET_RADAR[0] : null);
        const baseColor = (floatObj && floatObj.color && typeof hexToRgb === 'function') ? (hexToRgb(floatObj.color) || { r: 56, g: 139, b: 253 }) : { r: 56, g: 139, b: 253 };
        
        const dimR = Math.max(25, Math.round(baseColor.r * 0.28));
        const dimG = Math.max(25, Math.round(baseColor.g * 0.28));
        const dimB = Math.max(25, Math.round(baseColor.b * 0.28));
        
        // Calm, sparse starlight twinkle: slow ~5s period, spatially scattered
        const wave = Math.sin((timeMs * 0.0012) + (ledIndex * 1.9) + (runnerIndex * 2.3));
        let r = dimR;
        let g = dimG;
        let b = dimB;
        let alpha = 0.55;

        if (wave > 0.88) {
            const blendFactor = (wave - 0.88) / 0.12;
            r = Math.min(255, Math.round(dimR + 45 * blendFactor));
            g = Math.min(255, Math.round(dimG + 38 * blendFactor));
            b = Math.min(255, Math.round(dimB + 20 * blendFactor));
            alpha = 0.55 + (0.15 * blendFactor);
        }

        return { r, g, b, alpha };
    }

    // 0D. Castle Photo Mode (Solid, 100% steady, zero-flicker full graphic background colors across all 200 LEDs)
    if (isPhotoModeActive) {
        if (hasColor && c) {
            return { r: Math.round(c.r), g: Math.round(c.g), b: Math.round(c.b), alpha: 1.0 };
        }
        const floatObj = (DEFAULT_FLEET_RADAR && DEFAULT_FLEET_RADAR[runnerIndex]) ? DEFAULT_FLEET_RADAR[runnerIndex] : (DEFAULT_FLEET_RADAR ? DEFAULT_FLEET_RADAR[0] : null);
        const heroColor = (floatObj && floatObj.color && typeof hexToRgb === 'function') ? (hexToRgb(floatObj.color) || { r: 56, g: 139, b: 253 }) : { r: 56, g: 139, b: 253 };
        return { r: heroColor.r, g: heroColor.g, b: heroColor.b, alpha: 1.0 };
    }

    // 1. If 30-Second Fleet Show is Active: Evaluate Choreographed Block
    if (fleetShowActive) {
        return evalActiveFleetShowColor(runnerIndex, runner, effectiveData, ledIndex, totalLeds, timeMs, fleetShowElapsedSec);
    }

    // 2. BASELINE MODE: Evaluate Float's Individual Preset Programs and Animation Groups
    const pattern = (effectiveData && effectiveData.settings && effectiveData.settings.pattern) || 'steady_sparkle';
    const bpm = (effectiveData && effectiveData.settings && effectiveData.settings.speedBpm) || 120;
    const groups = (effectiveData && effectiveData.animationGroups) || [];
    for (const grp of groups) {
        const grpIndices = Array.isArray(grp.indices) ? grp.indices : (Array.isArray(grp.ledIndices) ? grp.ledIndices : []);
        if (grpIndices.includes(ledIndex)) {
            const idxInGrp = grpIndices.indexOf(ledIndex);
            return evalGroupEffect(grp, grp.effect, grp.speedBpm || bpm, grp.direction || 1, idxInGrp, grpIndices.length, timeMs, c);
        }
    }
    return evalGlobalPattern(pattern, bpm, ledIndex, totalLeds, timeMs, c, hasColor);
}

// ============================================================================
// FLEET SHOW TRIGGER & 300MS SOFTWARE DEBOUNCE CONTROLLER
// ============================================================================
function triggerFleetShowToggle() {
    const now = performance.now();
    if (now - lastFleetTriggerTime < 300) {
        console.log("Fleet show trigger debounced (<300ms)");
        return;
    }
    lastFleetTriggerTime = now;

    if (fleetShowActive) {
        stopFleetShow();
        showToast("⏹ Stopped Fleet Show early — reverted to baseline individual float programs");
    } else {
        startFleetShow();
        showToast(`👑 Activated 30s Fleet Show: "${activeFleetShow?.name || 'Grand Parade'}"`);
    }
}

function startFleetShow() {
    fleetShowActive = true;
    fleetShowElapsedSec = 0.0;
    fleetShowLastTimestamp = performance.now();
    fleetShowCycleIndex++;
    updateFleetShowUI();
    updateTimelinePlayBtn();
    if (typeof baroqueSynth !== 'undefined') {
        baroqueSynth.onFleetShowStart();
    }
}

function stopFleetShow() {
    fleetShowActive = false;
    fleetShowElapsedSec = 0.0;
    updateFleetShowUI();
    updateTimelinePlayBtn();
    if (typeof baroqueSynth !== 'undefined') {
        baroqueSynth.onFleetShowStop();
    }
}

// Keep 30-Second Fleet Show Timeline and UI Synchronized
function updateFleetShowTimeline(timeMs) {
    if (!fleetShowActive) {
        fleetShowLastTimestamp = timeMs;
        return;
    }
    if (!fleetShowLastTimestamp) fleetShowLastTimestamp = timeMs;
    const deltaSec = Math.max(0, (timeMs - fleetShowLastTimestamp) / 1000.0);
    fleetShowLastTimestamp = timeMs;

    const totalDur = (activeFleetShow && activeFleetShow.loopDuration) || 30.0;
    fleetShowElapsedSec += deltaSec;

    if (fleetShowElapsedSec >= totalDur) {
        // Complete one-shot show and return to baseline!
        stopFleetShow();
        showToast("🏁 30s Fleet Show completed! Returned to individual float programs.");
        return;
    }

    updateFleetShowUI();
}

// Update DOM elements reflecting fleet show progress and state
function updateFleetShowUI() {
    const actBtn = document.getElementById('fleetShowActivateBtn');
    const statusTitle = document.getElementById('fleetShowStatusTitle');
    const timeBadge = document.getElementById('fleetShowTimeProgressBadge');
    const activeBlockText = document.getElementById('fleetShowActiveBlockText');
    const colorBadge = document.getElementById('fleetRoutineColorBadge');
    const durationBadge = document.getElementById('fleetShowDurationBadge');

    const totalDur = (activeFleetShow && activeFleetShow.loopDuration) || 30.0;
    if (durationBadge) durationBadge.textContent = `${totalDur.toFixed(1)}s Total`;

    const activeInfo = getActiveFleetBlock(fleetShowElapsedSec);
    const activeBlock = activeInfo ? activeInfo.block : null;
    const waveColor = getActiveFleetColor(activeBlock?.params?.colorMode, activeInfo?.index);

    if (colorBadge && waveColor) {
        colorBadge.textContent = waveColor.name;
        colorBadge.style.background = waveColor.hex;
        const isDark = (waveColor.r * 0.299 + waveColor.g * 0.587 + waveColor.b * 0.114) < 140;
        colorBadge.style.color = isDark ? '#ffffff' : '#000000';
    }

    if (actBtn) {
        if (fleetShowActive) {
            actBtn.classList.add('playing');
            actBtn.textContent = `⏹ Stop Fleet Show (${fleetShowElapsedSec.toFixed(1)}s / ${totalDur.toFixed(1)}s)`;
        } else {
            actBtn.classList.remove('playing');
            actBtn.textContent = `👑 Activate ${totalDur.toFixed(0)}s Fleet Show`;
        }
    }

    if (statusTitle) {
        if (fleetShowActive) {
            statusTitle.textContent = `👑 SHOW ACTIVE: ${activeBlock ? activeBlock.name : 'Grand Routine'}`;
        } else {
            statusTitle.textContent = `⚡ Baseline Mode: Individual Presets`;
        }
    }

    if (timeBadge) {
        if (fleetShowActive) {
            timeBadge.textContent = `${fleetShowElapsedSec.toFixed(1)}s / ${totalDur.toFixed(1)}s`;
        } else {
            timeBadge.textContent = 'Idle';
        }
    }

    if (activeBlockText) {
        if (fleetShowActive && activeBlock) {
            activeBlockText.textContent = `Block #${activeInfo.index + 1}: ${activeBlock.name} (${activeBlock.startTime.toFixed(1)}s – ${(activeBlock.startTime + activeBlock.duration).toFixed(1)}s)`;
        } else {
            activeBlockText.textContent = `Ready. Press Activate to play ${totalDur.toFixed(0)}s routine once across all 7 shirts.`;
        }
    }

    // Highlight active card in stack editor
    const stackContainer = document.getElementById('fleetBlocksStackContainer');
    if (stackContainer) {
        stackContainer.querySelectorAll('.fleet-block-card').forEach((card, idx) => {
            card.classList.toggle('active-block', fleetShowActive && activeInfo && activeInfo.index === idx);
        });
    }

    // Highlight active block in Master Timeline track
    const timelineBlocks = document.querySelectorAll('.timeline-layer-track .cue-block[data-fleet-block-idx]');
    timelineBlocks.forEach(blk => {
        const idx = parseInt(blk.getAttribute('data-fleet-block-idx'));
        blk.classList.toggle('active', fleetShowActive && activeInfo && activeInfo.index === idx);
    });

    // Keep Master Timeline scrubber & transport synchronized if in Fleet View
    if (currentView === 'fleet') {
        updateTimelineScrubberUI();
        updateTimelinePlayBtn();
    }
}


// Draw Authentic Mini runDisney 10K Race Bib on miniature shirt
function drawMiniRaceBib(cx, x, y, width, height, bibNumber) {
    cx.save();
    // Yellow Tyvek Bib Paper
    cx.fillStyle = '#fbc02d';
    cx.fillRect(x, y, width, height);
    cx.strokeStyle = '#e65100';
    cx.lineWidth = 1;
    cx.strokeRect(x, y, width, height);

    // runDisney Top Stripe (Dark Navy)
    cx.fillStyle = '#0d1b2a';
    cx.fillRect(x, y, width, height * 0.28);

    // 10K Logo in top stripe
    cx.fillStyle = '#ffc107';
    cx.font = `bold ${Math.max(7, Math.floor(height * 0.22))}px sans-serif`;
    cx.textAlign = 'center';
    cx.textBaseline = 'middle';
    cx.fillText("runDisney 10K", x + width * 0.5, y + height * 0.14);

    // Bib Number in center
    cx.fillStyle = '#111111';
    cx.font = `bold ${Math.max(9, Math.floor(height * 0.40))}px monospace`;
    cx.textAlign = 'center';
    cx.textBaseline = 'middle';
    cx.fillText(bibNumber || "1952", x + width * 0.5, y + height * 0.62);

    // 4 Corner BibBoards Snap Fasteners
    const clampR = Math.max(1.5, width * 0.035);
    const cornerInset = width * 0.08;
    const corners = [
        { cx: x + cornerInset, cy: y + cornerInset },
        { cx: x + width - cornerInset, cy: y + cornerInset },
        { cx: x + cornerInset, cy: y + height - cornerInset },
        { cx: x + width - cornerInset, cy: y + height - cornerInset }
    ];
    cx.fillStyle = '#38bdf8';
    corners.forEach(c => {
        cx.beginPath();
        cx.arc(c.cx, c.cy, clampR, 0, Math.PI * 2);
        cx.fill();
    });

    cx.restore();
}

// ============================================================================
// ATHLETIC RUNNER FIGURE RENDERER (FULL BODY: HEAD, VISOR, ARMS, SHORTS, TONED LEGS, SNEAKERS)
// ============================================================================
function drawAthleticRunnerBase(ctx, shirtX, shirtY, shirtW, shirtH, floatData) {
    const shirtCX = shirtX + shirtW * 0.5;
    const skinTone = '#d4a373'; // Natural warm athletic runner skin tone

    // 1. Runner Neck (emerging naturally from collar)
    ctx.fillStyle = skinTone;
    ctx.fillRect(shirtCX - shirtW * 0.09, shirtY - 12, shirtW * 0.18, 22);

    // 2. Athletic Runner Head Silhouette (clean athletic silhouette, no visors)
    ctx.beginPath();
    ctx.ellipse(shirtCX, shirtY - 20, shirtW * 0.13, shirtW * 0.15, 0, 0, Math.PI * 2);
    ctx.fillStyle = skinTone;
    ctx.fill();

    // Clean athletic hair contour
    ctx.beginPath();
    ctx.arc(shirtCX, shirtY - 20, shirtW * 0.132, Math.PI * 1.05, Math.PI * 1.95, false);
    ctx.quadraticCurveTo(shirtCX, shirtY - 24, shirtCX - shirtW * 0.12, shirtY - 19);
    ctx.fillStyle = '#1e293b';
    ctx.fill();

    // 3. Athletic Running Arms (Mid-Stride Posture)
    // Left Arm (Forward pump)
    ctx.beginPath();
    ctx.moveTo(shirtX + shirtW * 0.12, shirtY + shirtH * 0.32);
    ctx.quadraticCurveTo(shirtX - 4, shirtY + shirtH * 0.48, shirtX + shirtW * 0.04, shirtY + shirtH * 0.62);
    ctx.lineWidth = 6.5;
    ctx.lineCap = 'round';
    ctx.strokeStyle = skinTone;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(shirtX + shirtW * 0.04, shirtY + shirtH * 0.63, 4, 0, Math.PI * 2);
    ctx.fillStyle = skinTone;
    ctx.fill();

    // Right Arm (Back stride)
    ctx.beginPath();
    ctx.moveTo(shirtX + shirtW * 0.88, shirtY + shirtH * 0.32);
    ctx.quadraticCurveTo(shirtX + shirtW + 4, shirtY + shirtH * 0.46, shirtX + shirtW * 0.94, shirtY + shirtH * 0.64);
    ctx.lineWidth = 6.5;
    ctx.lineCap = 'round';
    ctx.strokeStyle = skinTone;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(shirtX + shirtW * 0.94, shirtY + shirtH * 0.65, 4, 0, Math.PI * 2);
    ctx.fillStyle = skinTone;
    ctx.fill();
}

function drawSneaker(ctx, x, y, width, height, accentColor) {
    // Sneaker Upper Body
    ctx.beginPath();
    ctx.moveTo(x, y + height - 4);
    ctx.lineTo(x, y + 3);
    ctx.quadraticCurveTo(x + width * 0.5, y - 2, x + width, y + height - 4);
    ctx.lineTo(x + width, y + height);
    ctx.lineTo(x, y + height);
    ctx.closePath();
    ctx.fillStyle = accentColor || '#ffc107';
    ctx.fill();

    // White Cushioned Midsole (Performance Foam)
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x - 1, y + height - 4, width + 2, 3);

    // Durable Black Outsole Tread
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(x - 1, y + height - 1.5, width + 2, 1.5);

    // Laces Accent
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + width * 0.35, y + 2);
    ctx.lineTo(x + width * 0.65, y + 2);
    ctx.moveTo(x + width * 0.40, y + 4);
    ctx.lineTo(x + width * 0.60, y + 4);
    ctx.stroke();
}

function drawAthleticRunnerLowerBody(ctx, shirtX, shirtY, shirtW, shirtH, floatData, groundY) {
    const shirtCX = shirtX + shirtW * 0.5;
    const skinTone = '#d4a373'; // Natural warm athletic runner skin tone (always clearly visible!)
    const skinKnee = '#bf8556';
    const shortsTopY = shirtY + shirtH * 0.88;
    const shortsH = Math.round(shirtH * 0.30);
    const shortsBottomY = shortsTopY + shortsH;

    // 1. Athletic Running Shorts (Technical Black with Float Signature Racing Stripe)
    const legLeftShortX = shirtX + shirtW * 0.21;
    const legShortW = shirtW * 0.28;
    const legRightShortX = shirtX + shirtW * 0.51;

    // Left Short Leg
    ctx.fillStyle = '#161b22';
    ctx.fillRect(legLeftShortX, shortsTopY, legShortW, shortsH);
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 1;
    ctx.strokeRect(legLeftShortX, shortsTopY, legShortW, shortsH);
    // Outer racing stripe (Left)
    ctx.fillStyle = floatData.color || '#ffc107';
    ctx.fillRect(legLeftShortX, shortsTopY, 2.5, shortsH);

    // Right Short Leg
    ctx.fillStyle = '#161b22';
    ctx.fillRect(legRightShortX, shortsTopY, legShortW, shortsH);
    ctx.strokeRect(legRightShortX, shortsTopY, legShortW, shortsH);
    // Outer racing stripe (Right)
    ctx.fillStyle = floatData.color || '#ffc107';
    ctx.fillRect(legRightShortX + legShortW - 2.5, shortsTopY, 2.5, shortsH);

    // Inseam Crease
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(shirtCX - 1.5, shortsTopY + 8, 3, shortsH - 8);

    // 2. Athletic Runner Legs (Toned Thighs, Knees, Calves)
    const leftLegCX = legLeftShortX + legShortW * 0.5;
    const rightLegCX = legRightShortX + legShortW * 0.5;
    const kneeY = shortsBottomY + 16;
    const sockTopY = groundY - 18;

    // --- Left Leg ---
    // Thigh
    ctx.fillStyle = skinTone;
    ctx.beginPath();
    ctx.moveTo(leftLegCX - 6, shortsBottomY);
    ctx.lineTo(leftLegCX + 6, shortsBottomY);
    ctx.lineTo(leftLegCX + 5.5, kneeY);
    ctx.lineTo(leftLegCX - 5.5, kneeY);
    ctx.closePath();
    ctx.fill();

    // Knee cap subtle contour
    ctx.fillStyle = skinKnee;
    ctx.beginPath();
    ctx.arc(leftLegCX, kneeY, 3.8, 0, Math.PI * 2);
    ctx.fill();

    // Athletic Muscular Calf (curving outward, tapering to ankle)
    ctx.fillStyle = skinTone;
    ctx.beginPath();
    ctx.moveTo(leftLegCX - 5.5, kneeY);
    ctx.quadraticCurveTo(leftLegCX - 7.5, (kneeY + sockTopY) * 0.5, leftLegCX - 4.5, sockTopY);
    ctx.lineTo(leftLegCX + 4.5, sockTopY);
    ctx.quadraticCurveTo(leftLegCX + 6.5, (kneeY + sockTopY) * 0.5, leftLegCX + 5.5, kneeY);
    ctx.closePath();
    ctx.fill();

    // --- Right Leg ---
    // Thigh
    ctx.beginPath();
    ctx.moveTo(rightLegCX - 6, shortsBottomY);
    ctx.lineTo(rightLegCX + 6, shortsBottomY);
    ctx.lineTo(rightLegCX + 5.5, kneeY);
    ctx.lineTo(rightLegCX - 5.5, kneeY);
    ctx.closePath();
    ctx.fill();

    // Knee cap
    ctx.fillStyle = skinKnee;
    ctx.beginPath();
    ctx.arc(rightLegCX, kneeY, 3.8, 0, Math.PI * 2);
    ctx.fill();

    // Calf
    ctx.fillStyle = skinTone;
    ctx.beginPath();
    ctx.moveTo(rightLegCX - 5.5, kneeY);
    ctx.quadraticCurveTo(rightLegCX - 6.5, (kneeY + sockTopY) * 0.5, rightLegCX - 4.5, sockTopY);
    ctx.lineTo(rightLegCX + 4.5, sockTopY);
    ctx.quadraticCurveTo(rightLegCX + 7.5, (kneeY + sockTopY) * 0.5, rightLegCX + 5.5, kneeY);
    ctx.closePath();
    ctx.fill();

    // 3. Athletic Running Socks (White Quarter Socks with Float Accent Ring)
    const sockH = 8;
    const sockW = 10;
    // Left Sock
    ctx.fillStyle = '#f0f6fc';
    ctx.fillRect(leftLegCX - sockW * 0.5, sockTopY, sockW, sockH);
    ctx.fillStyle = floatData.color || '#ffc107';
    ctx.fillRect(leftLegCX - sockW * 0.5, sockTopY, sockW, 2);

    // Right Sock
    ctx.fillStyle = '#f0f6fc';
    ctx.fillRect(rightLegCX - sockW * 0.5, sockTopY, sockW, sockH);
    ctx.fillStyle = floatData.color || '#ffc107';
    ctx.fillRect(rightLegCX - sockW * 0.5, sockTopY, sockW, 2);

    // 4. Runner Drop Shadows on Asphalt Road
    ctx.beginPath();
    ctx.ellipse(leftLegCX - 1, groundY + 1, 12, 3.5, 0, 0, Math.PI * 2);
    ctx.ellipse(rightLegCX + 1, groundY + 1, 12, 3.5, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
    ctx.fill();

    // 5. Performance Running Sneakers (Shoes) firmly on the road
    const shoeW = 20;
    const shoeH = 10;
    const shoeY = groundY - shoeH;

    // Left Sneaker
    drawSneaker(ctx, leftLegCX - shoeW * 0.55, shoeY, shoeW, shoeH, floatData.color);
    // Right Sneaker
    drawSneaker(ctx, rightLegCX - shoeW * 0.45, shoeY, shoeW, shoeH, floatData.color);
}

function renderFleetView(timeMs) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const totalFloats = 7;
    const marginX = w * 0.025;
    const usableW = w - marginX * 2;
    const slotW = usableW / totalFloats;
    const shirtW = Math.floor(slotW * 0.88); // ~100px
    const shirtH = Math.floor(shirtW * 1.25); // ~125px (natural athletic dimensions!)
    const shirtY = h * 0.25; // Centered vertically in upper-mid canvas

    // Coordinate ground line & road surface
    const groundY = shirtY + shirtH + 74;
    const roadY = groundY - 2;

    // 4-Second Rapid Attendance Roll Call Evaluation
    const isRollCallActive = rapidRollCallActive && (timeMs - rapidRollCallStartTime >= 0) && (timeMs - rapidRollCallStartTime < 4000);
    const rollCallElapsed = isRollCallActive ? (timeMs - rapidRollCallStartTime) : 0;
    const rollCallSlot = isRollCallActive ? Math.floor(rollCallElapsed / 500) : -1;
    const isRollCallFinale = isRollCallActive && (rollCallElapsed >= 3500);

    // Fleet View Header & Mode Subtitle
    const totalDur = (activeFleetShow && activeFleetShow.loopDuration) || 30.0;
    const activeInfo = fleetShowActive ? getActiveFleetBlock(fleetShowElapsedSec) : null;
    const activeBlock = activeInfo ? activeInfo.block : null;
    const waveColor = activeBlock ? getActiveFleetColor(activeBlock.params?.colorMode, activeInfo.index) : FLEET_WAVE_STANDARD_COLORS[0];

    ctx.textAlign = 'center';

    if (isRollCallActive) {
        // Roll Call Header
        ctx.fillStyle = '#00ff88';
        ctx.font = 'bold 16px sans-serif';
        ctx.fillText("MAIN STREET ELECTRICAL PARADE — ⚡ 4-SECOND RAPID ATTENDANCE WAVE", w * 0.5, h * 0.08);

        let rollCallText = "";
        if (isRollCallFinale) {
            rollCallText = "🟢 ALL 7 BROTHERS LINKED & READY FOR THE 10K START GUN! (Unison Emerald Flash)";
            ctx.fillStyle = '#39ff14';
        } else {
            const reportingFloat = fleetRunners[rollCallSlot] || DEFAULT_FLEET_ROSTER[rollCallSlot];
            rollCallText = `⚡ Float ${rollCallSlot + 1} (${reportingFloat.name}): Reporting In! (${((3500 - rollCallElapsed)/1000).toFixed(1)}s remaining)`;
            ctx.fillStyle = reportingFloat.color || '#ffc107';
        }
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText(rollCallText, w * 0.5, h * 0.12);

        // Progress bar for the 4-second rapid roll call
        const progW = Math.min(500, w * 0.45);
        const progH = 4;
        const progX = (w - progW) / 2;
        const progY = h * 0.142;
        ctx.fillStyle = '#21262d';
        ctx.fillRect(progX, progY, progW, progH);
        ctx.fillStyle = isRollCallFinale ? '#39ff14' : (fleetRunners[rollCallSlot]?.color || '#00e5ff');
        ctx.fillRect(progX, progY, progW * Math.min(1.0, rollCallElapsed / 4000), progH);
    } else if (fleetShowActive) {
        ctx.fillStyle = '#ffc107';
        ctx.font = 'bold 16px sans-serif';
        ctx.fillText("MAIN STREET ELECTRICAL PARADE — 👑 FLEET SHOW ACTIVE", w * 0.5, h * 0.08);
        const blockName = activeBlock ? activeBlock.name : 'Grand Parade';
        const modeText = `👑 Block #${(activeInfo ? activeInfo.index + 1 : 1)}: ${blockName} [${waveColor.name}] (${fleetShowElapsedSec.toFixed(1)}s / ${totalDur.toFixed(1)}s) — Press [Stop] or [F] to exit early`;
        ctx.fillStyle = '#f0f6fc';
        ctx.font = '12px sans-serif';
        ctx.fillText(modeText, w * 0.5, h * 0.12);

        // Sleek canvas progress bar under header
        const progW = Math.min(500, w * 0.45);
        const progH = 4;
        const progX = (w - progW) / 2;
        const progY = h * 0.142;
        ctx.fillStyle = '#21262d';
        ctx.fillRect(progX, progY, progW, progH);
        ctx.fillStyle = waveColor.hex || '#ffc107';
        ctx.fillRect(progX, progY, progW * Math.min(1.0, fleetShowElapsedSec / totalDur), progH);
    } else {
        ctx.fillStyle = '#ffc107';
        ctx.font = 'bold 16px sans-serif';
        ctx.fillText("MAIN STREET ELECTRICAL PARADE — 7-RUNNER FLEET LINEUP", w * 0.5, h * 0.08);
        let modeText = "⚡ Baseline Mode: Individual Float Programs Running (Press [👑 Activate 30s Fleet Show] or [Space/F] to launch)";
        if (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && activeSingleShirtRunnerSlot < 7) {
            const runnerName = fleetRunners[activeSingleShirtRunnerSlot]?.name || `Runner #${activeSingleShirtRunnerSlot + 1}`;
            if (isSingleShirtDirty) {
                modeText = `⚡ Baseline Mode • ✏️ Previewing Unsaved Live Edit on Float ${activeSingleShirtRunnerSlot + 1} (${runnerName})`;
            } else {
                modeText = `⚡ Baseline Mode • ✨ Live Editor Previewing Float ${activeSingleShirtRunnerSlot + 1} (${runnerName})`;
            }
        }
        ctx.fillStyle = (isSingleShirtDirty && activeSingleShirtRunnerSlot !== null) ? '#f0883e' : '#8b949e';
        ctx.font = '12px sans-serif';
        ctx.fillText(modeText, w * 0.5, h * 0.12);
    }

    // Draw Parade Course Road Surface (Sneakers planted directly on pavement!)
    ctx.fillStyle = '#161b22';
    ctx.fillRect(w * 0.015, roadY, w * 0.97, 45);
    // Yellow Road Dash Centerline
    ctx.setLineDash([16, 16]);
    ctx.strokeStyle = '#f1e05a';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(w * 0.015, roadY + 22);
    ctx.lineTo(w * 0.985, roadY + 22);
    ctx.stroke();
    ctx.setLineDash([]);

    for (let i = 0; i < totalFloats; i++) {
        try {
            const shirtX = marginX + i * slotW + (slotW - shirtW) / 2;
            const shirtCX = shirtX + shirtW * 0.5;
            const floatData = fleetRunners[i] || DEFAULT_FLEET_ROSTER[i];

            let isCurrentWaveFloat = false;
            if (fleetShowActive && activeBlock) {
                const bType = activeBlock.type;
                const dur = Math.max(0.1, activeBlock.duration || 1.0);
                const localP = (activeInfo ? activeInfo.localT : 0) / dur;
                if (bType === 'wave_forward') {
                    isCurrentWaveFloat = Math.abs((-0.3 + localP * 7.6) - i) < 0.9;
                } else if (bType === 'wave_reverse') {
                    isCurrentWaveFloat = Math.abs((7.3 - localP * 7.6) - i) < 0.9;
                } else if (bType === 'baton_chase') {
                    isCurrentWaveFloat = (i === Math.min(6, Math.floor(localP * 7.0)));
                } else if (bType === 'fleet_pulse' || bType === 'sparkle_storm' || bType === 'strobe_all' || bType === 'grand_finale') {
                    isCurrentWaveFloat = true;
                }
            }

            // Rapid Attendance Wave reporting state
            const isRollCallReporting = isRollCallActive && (i === rollCallSlot || isRollCallFinale);
            if (isRollCallReporting) {
                isCurrentWaveFloat = true;
            }

            const isHovered = (fleetHoveredRunner === i);
            const isSelected = (fleetSelectedRunner === i);

            // Retrieve preset data (use live single-shirt editor data if this runner is currently active in editor)
            const isLivePreview = (i === activeSingleShirtRunnerSlot) || (floatData.preset === 'current_editor');
            const pData = isLivePreview ? getLiveSingleShirtPresetData() : (fleetPresetCache[floatData.preset] || null);

            // 1. Draw Runner Bib Number Badge & Preview Badge Above Shirt
            const activeBibCol = isRollCallReporting ? (isRollCallFinale ? '#00ff88' : floatData.color) : (fleetShowActive ? (waveColor.hex || '#ffc107') : '#ffc107');
            ctx.fillStyle = isCurrentWaveFloat ? activeBibCol : (isSelected ? '#58a6ff' : '#8b949e');
            ctx.font = 'bold 11px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(`BIB #${floatData.num}`, shirtCX, shirtY - 14);

            if (isLivePreview) {
                ctx.fillStyle = isSingleShirtDirty ? '#f0883e' : '#58a6ff';
                ctx.font = 'bold 9px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(isSingleShirtDirty ? '✏️ UNSAVED LIVE PREVIEW' : '✨ LIVE PREVIEW', shirtCX, shirtY - 26);
            }

            // 2. Draw Athletic Runner Base (Head, Running Cap, Neck & Arms behind shirt)
            drawAthleticRunnerBase(ctx, shirtX, shirtY, shirtW, shirtH, floatData);

            // 3. Draw Natural Proportioned Athletic Shirt (1 : 1.25)
            drawRunningShirt(ctx, shirtX, shirtY, shirtW, shirtH, "");

            // 4. Draw Float Graphic Artwork strictly in chest zone above bib
            const chestW = shirtW * 0.56;
            const chestH = shirtH * 0.385;
            const chestTop = shirtY + shirtH * 0.168;
            const chestLeft = shirtX + (shirtW - chestW) * 0.5;

            const graphicType = (pData && pData.graphicType) ? pData.graphicType : floatData.defaultGraphic;
            const gImg = getGraphicImgForType(graphicType);

            if (gImg && gImg.complete && gImg.naturalWidth > 0) {
                ctx.drawImage(gImg, chestLeft, chestTop, chestW, chestH);
            } else if (graphicType === 'builtin_dragon' || graphicType === 'petes_dragon') {
                // Scaled silhouette fallback
                const dummyBounds = { x: shirtX, y: shirtY, width: shirtW, height: shirtH };
                drawPetesDragon(ctx, dummyBounds);
            }

            // 5. Draw Mini runDisney Race Bib on lower torso
            const bibW = shirtW * (8.0 / 18.0);
            const bibH = bibW * (7.0 / 8.0);
            const bibX = shirtX + (shirtW - bibW) * 0.5;
            const bibY = shirtY + shirtH * 0.57;
            drawMiniRaceBib(ctx, bibX, bibY, bibW, bibH, floatData.num);

            // 6. Draw Real 100-LED Configuration
            const ledsArr = (pData && Array.isArray(pData.leds) && pData.leds.length > 0) ? pData.leds : null;
            if (ledsArr) {
                for (let j = 0; j < ledsArr.length; j++) {
                    const led = ledsArr[j];
                    const lx = shirtX + led.x * shirtW;
                    const ly = shirtY + led.y * shirtH;
                    const col = computeRunnerLedColor(i, floatData, pData, j, ledsArr.length, timeMs, 0, isCurrentWaveFloat);

                    if (col.alpha > 0.02 && (col.r > 0 || col.g > 0 || col.b > 0)) {
                        // Bulb outer halo glow
                        if (isCurrentWaveFloat || fleetShowActive) {
                            ctx.beginPath();
                            ctx.arc(lx, ly, 4.4, 0, Math.PI * 2);
                            ctx.fillStyle = `rgba(${col.r}, ${col.g}, ${col.b}, 0.32)`;
                            ctx.fill();
                        }

                        // Core bulb dot
                        ctx.beginPath();
                        ctx.arc(lx, ly, (isCurrentWaveFloat || fleetShowActive) ? 2.6 : 1.8, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(${col.r}, ${col.g}, ${col.b}, ${col.alpha || 1})`;
                        ctx.fill();
                    } else {
                        // Unlit / black bulb
                        ctx.beginPath();
                        ctx.arc(lx, ly, 1.2, 0, Math.PI * 2);
                        ctx.fillStyle = 'rgba(20, 25, 32, 0.45)';
                        ctx.fill();
                    }
                }
            } else {
                // Graceful fallback: 18 mini LEDs while preset loads
                const numMiniLeds = 18;
                const chestCX = shirtX + shirtW * 0.5;
                const chestCY = shirtY + shirtH * 0.44;
                const rx = shirtW * 0.26;
                const ry = shirtH * 0.20;

                for (let j = 0; j < numMiniLeds; j++) {
                    const angle = (j / numMiniLeds) * Math.PI * 2;
                    const lx = chestCX + Math.cos(angle) * rx;
                    const ly = chestCY + Math.sin(angle) * ry;
                    const col = computeRunnerLedColor(i, floatData, null, j, numMiniLeds, timeMs, 0, isCurrentWaveFloat);

                    if (col.alpha > 0.02 && (col.r > 0 || col.g > 0 || col.b > 0)) {
                        ctx.beginPath();
                        ctx.arc(lx, ly, (isCurrentWaveFloat || fleetShowActive) ? 3.4 : 2.2, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(${col.r}, ${col.g}, ${col.b}, ${col.alpha || 1})`;
                        ctx.fill();
                    } else {
                        ctx.beginPath();
                        ctx.arc(lx, ly, 1.2, 0, Math.PI * 2);
                        ctx.fillStyle = 'rgba(20, 25, 32, 0.45)';
                        ctx.fill();
                    }
                }
            }

            // 7. Draw Athletic Runner Lower Body (Shorts, Toned Legs, Socks, Running Shoes, Shadows)
            drawAthleticRunnerLowerBody(ctx, shirtX, shirtY, shirtW, shirtH, floatData, groundY);

            // 8. Float Name Tag & Character Description Below Runner on Road
            ctx.fillStyle = isCurrentWaveFloat ? '#ffffff' : (isSelected ? '#58a6ff' : '#c9d1d9');
            ctx.font = 'bold 10px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(floatData.name, shirtCX, roadY + 28);

            ctx.fillStyle = isCurrentWaveFloat ? activeBibCol : (isSelected ? '#ffc107' : '#8b949e');
            ctx.font = '9px sans-serif';
            ctx.fillText(floatData.tag, shirtCX, roadY + 39);

            // 9. Highlight Frame (Hovered or Selected only)
            if (isSelected) {
                ctx.save();
                ctx.strokeStyle = '#388bfd';
                ctx.lineWidth = 2;
                ctx.shadowColor = '#388bfd';
                ctx.shadowBlur = 8;
                ctx.strokeRect(shirtX - 8, shirtY - 34, shirtW + 16, groundY - shirtY + 80);
                ctx.restore();
            } else if (isHovered) {
                ctx.save();
                ctx.strokeStyle = 'rgba(88, 166, 255, 0.6)';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(shirtX - 8, shirtY - 34, shirtW + 16, groundY - shirtY + 80);
                ctx.restore();
            }
        } catch (err) {
            console.error(`Error rendering float runner ${i}:`, err);
        }
    }
}

// ============================================================================
// FLEET LINEUP MANAGEMENT & SIDEBAR UI CONTROLS
// ============================================================================

let isRenderingFleetCards = false;

async function renderFleetCards() {
    const container = document.getElementById('fleetRunnersContainer');
    if (!container) return;
    if (isRenderingFleetCards) return;
    isRenderingFleetCards = true;

    try {
        // Fetch list of available server and local presets
        let serverPresets = [];
        try {
            const res = await fetch('/api/presets');
            if (res.ok) serverPresets = await res.json();
        } catch (e) {}

        const localProfiles = JSON.parse(localStorage.getItem('msep_custom_presets') || '{}');

        container.innerHTML = '';

        for (let i = 0; i < fleetRunners.length; i++) {
            const runner = fleetRunners[i];
            const card = document.createElement('div');
            card.className = `fleet-runner-card ${fleetSelectedRunner === i ? 'selected-runner' : ''}`;
            card.setAttribute('data-slot', i);

            // Preload preset data if not cached
            const isLivePreview = (i === activeSingleShirtRunnerSlot) || (runner.preset === 'current_editor');
            const pData = isLivePreview ? getLiveSingleShirtPresetData() : (await getPresetDataForRunner(runner));

            const ledCount = (pData && pData.leds) ? pData.leds.length : 100;
            const patternName = (pData && pData.settings && pData.settings.pattern) ? pData.settings.pattern.replace(/_/g, ' ') : 'Sparkle';
            const graphicName = (pData && pData.graphicType) ? pData.graphicType.replace(/_/g, ' ') : runner.name;

            let statusBadgeHtml = '';
            let labelExtraHtml = '';
            if (isLivePreview) {
                if (isSingleShirtDirty) {
                    statusBadgeHtml = `<span class="fleet-pill" style="background: rgba(240, 136, 62, 0.25); color: #f0883e; border: 1px solid rgba(240, 136, 62, 0.4);">✏️ Unsaved Live Edit</span>`;
                    labelExtraHtml = `<span style="font-size: 10px; color: #f0883e; margin-left: 6px; font-weight: 600;">✏️ Previewing Unsaved Edit</span>`;
                } else {
                    statusBadgeHtml = `<span class="fleet-pill" style="background: rgba(56, 139, 253, 0.25); color: #58a6ff; border: 1px solid rgba(56, 139, 253, 0.4);">✨ Live Editor Active</span>`;
                    labelExtraHtml = `<span style="font-size: 10px; color: #58a6ff; margin-left: 6px; font-weight: 600;">✨ Previewing Live Editor</span>`;
                }
            }

            // Build Card HTML
            card.innerHTML = `
                <div class="fleet-card-header">
                    <span class="fleet-bib-badge" style="background: ${runner.color}22; color: ${runner.color}; border: 1px solid ${runner.color}66;">
                        BIB #${runner.num}
                    </span>
                    <span class="fleet-runner-title" title="${runner.name} (${runner.tag})">
                        ${runner.slot + 1}. ${runner.name}
                    </span>
                    <span style="font-size: 10px; color: ${runner.color}; font-weight: 700;">${runner.tag}</span>
                </div>

                <div>
                    <label style="font-size: 10px; color: var(--text-muted); display: block; margin-bottom: 2px;">Assigned Costume Preset:${labelExtraHtml}</label>
                    <select class="fleet-preset-select" data-slot="${i}">
                        <optgroup label="Official Server Presets">
                            ${serverPresets.map(p => `
                                <option value="server:${p.filename}" ${runner.preset === ('server:' + p.filename) ? 'selected' : ''}>
                                    📁 ${p.name}
                                </option>
                            `).join('')}
                        </optgroup>
                        ${Object.keys(localProfiles).length > 0 ? `
                            <optgroup label="Browser Saved Profiles">
                                ${Object.keys(localProfiles).map(name => `
                                    <option value="local:${name}" ${runner.preset === ('local:' + name) ? 'selected' : ''}>
                                        💾 ${name}
                                    </option>
                                `).join('')}
                            </optgroup>
                        ` : ''}
                        <optgroup label="Editor Session">
                            <option value="current_editor" ${runner.preset === 'current_editor' ? 'selected' : ''}>
                                ✨ Currently Active Editor Design
                            </option>
                        </optgroup>
                    </select>
                </div>

                <div class="fleet-pills-row">
                    ${statusBadgeHtml}
                    <span class="fleet-pill">💡 ${ledCount} LEDs</span>
                    <span class="fleet-pill">🎨 ${graphicName}</span>
                    <span class="fleet-pill">✨ ${patternName}</span>
                </div>

                <div class="fleet-actions-row">
                    <button type="button" class="action-btn fleet-edit-single-btn" data-slot="${i}" style="flex: 1.2; font-weight: 600; color: #58a6ff; border-color: rgba(56, 139, 253, 0.4);" title="Load into Single Shirt visualizer to tweak LEDs, colors, and groups">
                        ✏️ Edit in Single View
                    </button>
                    <button type="button" class="action-btn fleet-copy-active-btn" data-slot="${i}" style="flex: 1;" title="Assign current single-shirt editor design to this runner">
                        📥 Assign Editor
                    </button>
                </div>
            `;

            // Card click & dblclick handlers
            card.addEventListener('click', (e) => {
                if (e.target.closest('button') || e.target.closest('select')) return;
                fleetSelectedRunner = i;
                container.querySelectorAll('.fleet-runner-card').forEach((c, idx) => {
                    c.classList.toggle('selected-runner', idx === i);
                });
            });

            card.addEventListener('dblclick', async (e) => {
                if (e.target.closest('button') || e.target.closest('select')) return;
                await editRunnerInSingleView(i);
            });

            container.appendChild(card);
        }

        // Attach event listeners
        container.querySelectorAll('.fleet-preset-select').forEach(sel => {
            sel.addEventListener('change', async () => {
                const slot = parseInt(sel.getAttribute('data-slot'));
                fleetRunners[slot].preset = sel.value;
                delete fleetPresetCache[sel.value];
                await getPresetDataForRunner(fleetRunners[slot]);
                saveFleetLineupToStorage();
                renderFleetCards();
                showToast(`Assigned preset to Runner #${fleetRunners[slot].num}!`);
            });
        });

        container.querySelectorAll('.fleet-edit-single-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const slot = parseInt(btn.getAttribute('data-slot'));
                await editRunnerInSingleView(slot);
            });
        });

        container.querySelectorAll('.fleet-copy-active-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const slot = parseInt(btn.getAttribute('data-slot'));
                assignCurrentEditorToRunner(slot);
            });
        });
    } finally {
        isRenderingFleetCards = false;
    }
}

// Interactive Modal: Confirm saving or discarding unsaved single-shirt edits before switching
function confirmUnsavedEditsModal(prevRunner, targetRunner) {
    return new Promise((resolve) => {
        const modal = document.getElementById('unsavedChangesModal');
        if (!modal) {
            // Fallback prompt/confirm if modal DOM element is not present
            const defName = prevRunner ? `${prevRunner.name} Custom` : "My Costume Profile";
            const askSave = confirm(`You have unsaved edits on ${prevRunner ? `Runner #${prevRunner.num} (${prevRunner.name})` : 'current costume'}.\n\nWould you like to SAVE these edits as a profile before switching?\n\n• OK = Save profile with a name\n• Cancel = Choose whether to discard`);
            if (askSave) {
                const name = prompt("Enter a profile name to save your edits:", defName);
                if (name && name.trim()) {
                    resolve({ action: 'save', name: name.trim() });
                } else {
                    resolve({ action: 'cancel' });
                }
            } else {
                const discard = confirm(`Discard unsaved edits and proceed to switch?`);
                resolve({ action: discard ? 'discard' : 'cancel' });
            }
            return;
        }

        const titleEl = document.getElementById('unsavedModalTitle');
        const descEl = document.getElementById('unsavedModalDesc');
        const nameInput = document.getElementById('unsavedModalProfileNameInput');
        const hintEl = document.getElementById('unsavedModalGraphicHint');
        const saveBtn = document.getElementById('unsavedModalSaveBtn');
        const discardBtn = document.getElementById('unsavedModalDiscardBtn');
        const cancelBtn = document.getElementById('unsavedModalCancelBtn');
        const closeBtn = document.getElementById('closeUnsavedModalBtn');

        const prevName = prevRunner ? `Runner #${prevRunner.num} (${prevRunner.name})` : 'Current Single Shirt';
        const targetName = targetRunner ? (targetRunner.num ? `Runner #${targetRunner.num} (${targetRunner.name})` : (targetRunner.name || 'New Profile')) : 'Another Costume';

        if (titleEl) {
            titleEl.textContent = `Unsaved Edits on ${prevRunner ? prevRunner.name : 'Costume'}`;
        }
        if (descEl) {
            descEl.innerHTML = `You have modified <strong>${prevName}</strong> with unsaved layout or pattern changes.<br>Would you like to save these edits as a named costume profile before switching to <strong>${targetName}</strong>?`;
        }

        // Determine a sensible default name for the profile
        const layoutInputVal = (document.getElementById('profileNameInput')?.value || '').trim();
        let defaultName = layoutInputVal;
        if (!defaultName) {
            if (prevRunner) {
                defaultName = `${prevRunner.name} Custom`;
            } else if (currentGraphicType === 'cinderellas_coach') {
                defaultName = "Cinderella's Coach Custom";
            } else if (currentGraphicType === 'carriage_nohorses') {
                defaultName = "Carriage (No Horses) Custom";
            } else {
                defaultName = "Pete's Dragon Custom";
            }
        }
        if (nameInput) {
            nameInput.value = defaultName;
            nameInput.style.borderColor = '#388bfd';
        }
        if (hintEl) {
            hintEl.textContent = `${leds.length} LEDs • ${(currentGraphicType || 'dragon').replace(/_/g, ' ')}`;
        }

        let isResolved = false;

        const cleanup = () => {
            modal.classList.remove('open');
            saveBtn?.removeEventListener('click', onSave);
            discardBtn?.removeEventListener('click', onDiscard);
            cancelBtn?.removeEventListener('click', onCancel);
            closeBtn?.removeEventListener('click', onCancel);
            modal.removeEventListener('click', onBackdrop);
            document.removeEventListener('keydown', onKeyDown);
        };

        const onSave = () => {
            if (isResolved) return;
            const entered = (nameInput?.value || '').trim();
            if (!entered) {
                if (nameInput) {
                    nameInput.focus();
                    nameInput.style.borderColor = '#f85149';
                }
                showToast("⚠️ Please enter a profile name to save.");
                return;
            }
            isResolved = true;
            cleanup();
            resolve({ action: 'save', name: entered });
        };

        const onDiscard = () => {
            if (isResolved) return;
            isResolved = true;
            cleanup();
            resolve({ action: 'discard' });
        };

        const onCancel = () => {
            if (isResolved) return;
            isResolved = true;
            cleanup();
            resolve({ action: 'cancel' });
        };

        const onBackdrop = (e) => {
            if (e.target === modal) {
                onCancel();
            }
        };

        const onKeyDown = (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                onCancel();
            } else if (e.key === 'Enter' && e.target === nameInput) {
                e.preventDefault();
                onSave();
            }
        };

        saveBtn?.addEventListener('click', onSave);
        discardBtn?.addEventListener('click', onDiscard);
        cancelBtn?.addEventListener('click', onCancel);
        closeBtn?.addEventListener('click', onCancel);
        modal.addEventListener('click', onBackdrop);
        document.addEventListener('keydown', onKeyDown);

        modal.classList.add('open');
        setTimeout(() => {
            if (nameInput) {
                nameInput.select();
                nameInput.focus();
            }
        }, 50);
    });
}

// ============================================================================
// SINGLE SHIRT ACTIVE FLOAT DISPLAY & QUICK SELECTOR
// ============================================================================
function updateActiveFloatUI(slot) {
    if (slot === null || slot === undefined || isNaN(slot) || slot < 0 || slot >= DEFAULT_FLEET_ROSTER.length) {
        slot = (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && activeSingleShirtRunnerSlot < DEFAULT_FLEET_ROSTER.length) ? activeSingleShirtRunnerSlot : 5;
    }
    const info = (fleetRunners && fleetRunners[slot]) ? fleetRunners[slot] : DEFAULT_FLEET_ROSTER[slot];
    if (!info) return;

    const icon = info.icon || (['🚂','🥁','🐢','🐌','🩵','🐉','🦅'][slot] || '👕');
    const fullName = info.fullName || `${info.name} (${info.tag || 'Float ' + (slot+1)})`;
    const role = info.role || (slot === 0 ? '👑 Fleet Leader (Broadcast)' : '📡 Follower Float');
    const color = info.color || '#38bdf8';
    const num = info.num || `0${slot + 1}`;

    // 1. Update slot indicator text in section title
    const slotIndicator = document.getElementById('activeFloatSlotIndicator');
    if (slotIndicator) {
        slotIndicator.textContent = `FLOAT ${slot + 1} OF 7`;
        slotIndicator.style.color = color;
    }

    // 2. Update active float banner
    const banner = document.getElementById('activeFloatBanner');
    if (banner) {
        banner.style.borderColor = `${color}88`;
        banner.style.boxShadow = `0 2px 10px rgba(0, 0, 0, 0.4), 0 0 14px ${color}22`;
        banner.style.background = `linear-gradient(135deg, ${color}15 0%, rgba(13, 17, 23, 0.85) 100%)`;
        banner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; min-width: 0;">
                <div style="font-size: 26px; line-height: 1; filter: drop-shadow(0 0 6px ${color}88);">${icon}</div>
                <div style="min-width: 0;">
                    <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                        <span style="font-size: 10px; font-weight: 800; background: ${color}33; color: ${color}; border: 1px solid ${color}88; padding: 1px 6px; border-radius: 4px; letter-spacing: 0.5px;">FLOAT ${num}</span>
                        <span style="font-size: 13px; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${fullName}</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                        <span style="background: ${color}22; color: ${color}; border: 1px solid ${color}55; padding: 0 5px; border-radius: 3px; font-size: 9px; font-weight: 600;">${role}</span>
                        <span>Lineup Tag: <strong style="color: ${color};">${info.tag || ''}</strong></span>
                    </div>
                </div>
            </div>
            <div style="text-align: right; flex-shrink: 0; margin-left: 8px;">
                <span style="font-size: 9px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block;">Accent</span>
                <span style="font-size: 11px; font-weight: 700; color: ${color};">${info.accent || ''}</span>
            </div>
        `;
    }

    // 3. Update 7-button selector states (buttons 1 to 7)
    const numBtns = document.querySelectorAll('#floatSelectorGrid .float-num-btn');
    numBtns.forEach((btn) => {
        const btnSlot = parseInt(btn.getAttribute('data-slot'), 10);
        if (btnSlot === slot) {
            btn.classList.add('active');
            btn.style.setProperty('--float-accent', color);
            btn.style.setProperty('--float-accent-bg', `${color}33`);
            btn.style.setProperty('--float-accent-glow', `${color}66`);
        } else {
            btn.classList.remove('active');
            btn.style.removeProperty('--float-accent');
            btn.style.removeProperty('--float-accent-bg');
            btn.style.removeProperty('--float-accent-glow');
        }
    });

    // 4. Update Graphic Preset Dropdown selection (if not custom upload)
    const graphicSelect = document.getElementById('graphicPresetSelect');
    if (graphicSelect && currentGraphicType !== 'custom_image') {
        const defaultMap = {
            0: 'casey_jr_train',
            1: 'title_drum',
            2: 'spinning_turtle',
            3: 'spinning_snail',
            4: 'cinderellas_coach',
            5: 'builtin_dragon',
            6: 'honor_america_eagle'
        };
        const targetVal = defaultMap[slot];
        if (targetVal) {
            graphicSelect.value = targetVal;
        }
    }

    // 5. Update Single Shirt top nav tab button text
    const singleBtn = document.getElementById('singleViewBtn');
    if (singleBtn) {
        singleBtn.innerHTML = `<span>👕</span> Single Shirt (#${slot + 1} ${info.name})`;
        singleBtn.title = `Currently editing Float #${slot + 1}: ${fullName}`;
    }

    // 6. Update Canvas Watermark badge
    const watermark = document.getElementById('canvasFloatWatermark');
    if (watermark) {
        if (currentView === 'single') {
            watermark.style.display = 'flex';
            watermark.innerHTML = `${icon} <span style="color: #fff; font-weight: 500;">Float ${slot + 1}:</span> <span style="color: ${color}; font-weight: 700;">${fullName}</span>`;
            watermark.style.borderColor = `${color}88`;
            watermark.style.boxShadow = `0 4px 14px rgba(0, 0, 0, 0.6), 0 0 10px ${color}44`;
        } else {
            watermark.style.display = 'none';
        }
    }

    // 7. Update Show Tab Active Float Badge
    const directorBadge = document.getElementById('directorActiveFloatBadge');
    if (directorBadge) {
        directorBadge.textContent = `Float #${slot + 1}: ${info.name}`;
        directorBadge.style.color = color;
        directorBadge.style.borderColor = `${color}88`;
        directorBadge.style.background = `${color}22`;
    }

    // 8. Update Deploy Tab Flasher Hub (Single Unified Flashing Station)
    updateDeployFlasherUI(slot);
}

// ============================================================================
// DEPLOY TAB UNIFIED FLASHER STATION (WYSIWYG CANVAS TARGET)
// ============================================================================
function updateDeployFlasherUI(slot) {
    if (slot === null || slot === undefined || isNaN(slot) || slot < 0 || slot >= DEFAULT_FLEET_ROSTER.length) {
        slot = (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && activeSingleShirtRunnerSlot < DEFAULT_FLEET_ROSTER.length) ? activeSingleShirtRunnerSlot : 0;
    }
    const info = (fleetRunners && fleetRunners[slot]) ? fleetRunners[slot] : DEFAULT_FLEET_ROSTER[slot];
    if (!info) return;

    const icon = info.icon || (['🚂','🥁','🐢','🐌','🩵','🐉','🦅'][slot] || '👕');
    const color = info.color || '#38bdf8';
    const num = info.num || `0${slot + 1}`;
    const isLeader = (slot === 0);

    const activeIconEl = document.getElementById('deployActiveIcon');
    const activeTitleEl = document.getElementById('deployActiveTitle');
    const activeSubtitleEl = document.getElementById('deployActiveSubtitle');
    const activeRolePillEl = document.getElementById('deployActiveRolePill');
    const flashBtnTextEl = document.getElementById('flashEsp32BtnText');

    if (activeIconEl) activeIconEl.textContent = icon;
    if (activeTitleEl) activeTitleEl.textContent = `Float ${slot + 1}: ${info.name}`;
    if (activeSubtitleEl) {
        activeSubtitleEl.textContent = `${info.tag || 'FLOAT ' + num} · ${isLeader ? 'Pulls parade & broadcasts ESP-NOW master sync' : 'Follower Float (Synchronized)'}`;
    }
    if (activeRolePillEl) {
        if (isLeader) {
            activeRolePillEl.textContent = '👑 LEADER';
            activeRolePillEl.style.background = 'rgba(248,81,73,0.2)';
            activeRolePillEl.style.color = '#ff7b72';
            activeRolePillEl.style.border = '1px solid rgba(248,81,73,0.4)';
        } else {
            activeRolePillEl.textContent = '📡 FOLLOWER';
            activeRolePillEl.style.background = 'rgba(56,139,253,0.15)';
            activeRolePillEl.style.color = '#58a6ff';
            activeRolePillEl.style.border = '1px solid rgba(56,139,253,0.3)';
        }
    }

    if (flashBtnTextEl) {
        flashBtnTextEl.textContent = `⚡ Flash Float ${slot + 1}: ${info.name} to ESP32 (USB)`;
    }

    renderDeployFloatSwitchGrid(slot);
}

function renderDeployFloatSwitchGrid(currentActiveSlot) {
    const grid = document.getElementById('deployFloatSwitchGrid');
    if (!grid) return;
    grid.innerHTML = '';

    const DEFAULT_ICONS = ['🚂', '🥁', '🐢', '🐌', '🩵', '🐉', '🦅'];

    for (let i = 0; i < DEFAULT_FLEET_ROSTER.length; i++) {
        const item = (fleetRunners && fleetRunners[i]) ? fleetRunners[i] : DEFAULT_FLEET_ROSTER[i];
        const defaultDef = DEFAULT_FLEET_ROSTER[i];
        const icon = (item && item.icon) || DEFAULT_ICONS[i] || '👕';
        const name = (item && item.name) || (defaultDef && defaultDef.name) || `Float ${i + 1}`;
        const color = (item && item.color) || (defaultDef && defaultDef.color) || '#388bfd';
        const isSelected = (i === currentActiveSlot);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `float-num-btn ${isSelected ? 'active' : ''}`;
        btn.style.width = '100%';
        btn.style.minWidth = '0';
        btn.style.padding = '5px 2px';
        btn.style.boxSizing = 'border-box';
        btn.style.cursor = 'pointer';
        btn.title = `Switch canvas to Float ${i + 1}: ${name}`;

        if (isSelected) {
            btn.style.setProperty('--float-accent', color);
            btn.style.setProperty('--float-accent-bg', `${color}33`);
            btn.style.setProperty('--float-accent-glow', `${color}66`);
            btn.style.borderColor = color;
            btn.style.boxShadow = `0 0 8px ${color}55`;
        } else {
            btn.style.removeProperty('--float-accent');
            btn.style.removeProperty('--float-accent-bg');
            btn.style.removeProperty('--float-accent-glow');
        }

        btn.innerHTML = `
            <span style="font-size: 16px; line-height: 1.1; display: block;">${icon}</span>
            <span style="font-size: 10px; font-weight: 800; line-height: 1; margin-top: 1px;">#${i + 1}</span>
            <span class="float-dot" style="--float-dot-color: ${color}; width: 5px; height: 5px; margin-top: 1px;"></span>
        `;

        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (i === activeSingleShirtRunnerSlot) {
                showToast(`Already viewing Float #${i + 1}: ${name}`);
                return;
            }
            await editRunnerInSingleView(i);
            updateActiveFloatUI(activeSingleShirtRunnerSlot);
        });

        grid.appendChild(btn);
    }
}

// Initialize Single Shirt 7-Button Float Switcher and Controls
function initSingleShirtFloatSelector() {
    const numBtns = document.querySelectorAll('#floatSelectorGrid .float-num-btn');
    numBtns.forEach((btn) => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const targetSlot = parseInt(btn.getAttribute('data-slot'), 10);
            if (isNaN(targetSlot)) return;
            await editRunnerInSingleView(targetSlot);
            updateActiveFloatUI(activeSingleShirtRunnerSlot);
        });
    });

    // Initial update of active float UI
    updateActiveFloatUI(activeSingleShirtRunnerSlot);
}

// 1-Click Load Runner Preset into Single Shirt Editor
async function editRunnerInSingleView(slot) {
    try {
        const runner = fleetRunners[slot];
        if (!runner) return false;

        // If fleet show is active, stop it before switching to single view
        if (fleetShowActive) {
            stopFleetShow();
        }

        // If user is already editing this runner slot, simply return to the single view
        // without reloading and wiping out their active live in-memory edits!
        if (slot === activeSingleShirtRunnerSlot) {
            currentView = 'single';
            document.getElementById('singleViewBtn')?.classList.add('active');
            document.getElementById('fleetViewBtn')?.classList.remove('active');
            const zt = document.querySelector('.zoom-toolbar');
            if (zt) zt.style.display = 'flex';
            resetZoom();
            switchSidebarTab(lastSingleShirtTab || 'tabLayout');
            updateActiveFloatUI(slot);
            showToast(`✏️ Returned to active single-shirt editor for Runner #${runner.num} (${runner.name})`);
            return true;
        }

        // Switching to a DIFFERENT runner:
        // If there are unsaved edits on the current runner slot, ask user to save, discard, or cancel!
        if (isSingleShirtDirty && activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && fleetRunners[activeSingleShirtRunnerSlot]) {
            const prevRunner = fleetRunners[activeSingleShirtRunnerSlot];
            const modalResult = await confirmUnsavedEditsModal(prevRunner, runner);

            if (modalResult.action === 'cancel') {
                updateActiveFloatUI(activeSingleShirtRunnerSlot);
                return false; // Stay where we are!
            } else if (modalResult.action === 'save') {
                await saveCurrentProfile(modalResult.name);
                showToast(`💾 Saved Runner #${prevRunner.num} edits as "${modalResult.name}"!`);
            } else if (modalResult.action === 'discard') {
                isSingleShirtDirty = false;
            }
        }

        // Record new active single shirt slot and reset dirty state
        activeSingleShirtRunnerSlot = slot;
        try {
            localStorage.setItem('msep_active_single_shirt_slot', slot.toString());
        } catch (e) {
            console.warn("Could not save active slot to localStorage:", e);
        }
        isSingleShirtDirty = false;

        // Switch view to Single Shirt FIRST before loading preset data
        currentView = 'single';
        document.getElementById('singleViewBtn')?.classList.add('active');
        document.getElementById('fleetViewBtn')?.classList.remove('active');
        const zt = document.querySelector('.zoom-toolbar');
        if (zt) zt.style.display = 'flex';
        resetZoom();

        let pData = await getPresetDataForRunner(runner);
        if (!pData) {
            // Fallback profile if server unavailable
            pData = {
                name: `${runner.name} Costume`,
                floatName: `Float ${runner.slot + 1} - ${runner.name}`,
                ledCount: 100,
                leds: [],
                graphicType: runner.defaultGraphic || 'builtin_dragon',
                settings: { pattern: 'steady_sparkle', speedBpm: 120, sparkleRate: 1.5, greenHue: 140, brightness: 80, glowSize: 22 },
                animationGroups: [],
                sequence: { loopDuration: 90.0, cues: [] }
            };
        }

        // Apply preset to main editor (now runs with currentView === 'single' so individual timeline loads)
        applyProfileData(pData);
        clearHistoryStacks();

        // If preset has no leds, generate 100 on graphic
        if (!leds || leds.length === 0) {
            scatterLedsOnGraphic(100, true);
        }

        // Switch sidebar back to last used single-shirt tab
        switchSidebarTab(lastSingleShirtTab || 'tabLayout');

        // Synchronize Quick-Load Profile dropdown in tabLayout
        const pSel = document.getElementById('presetSelect');
        if (pSel && runner.preset) {
            pSel.value = runner.preset;
        }

        updateActiveFloatUI(slot);
        showToast(`✏️ Loaded Float #${runner.num} (${runner.name}) into Single Shirt Editor`);
        return true;
    } catch (err) {
        console.error("Error editing runner in single view:", err);
        showToast(`⚠️ Error loading runner into editor: ${err.message}`);
        updateActiveFloatUI(activeSingleShirtRunnerSlot);
        return false;
    }
}

// Copy Current Single-Shirt Editor State to a Specific Runner
function assignCurrentEditorToRunner(slot) {
    const runner = fleetRunners[slot];
    if (!runner) return;

    const editorData = {
        name: `${runner.name} (Custom)`,
        floatName: `Float ${runner.slot + 1} - ${runner.name}`,
        savedAt: new Date().toISOString(),
        ledCount: leds.length,
        leds: JSON.parse(JSON.stringify(leds)),
        graphicType: currentGraphicType,
        customArtworkDataUrl: customArtworkDataUrl,
        animationGroups: JSON.parse(JSON.stringify(animationGroups)),
        settings: {
            pattern: activePattern,
            direction: params.direction || 1,
            speedBpm: params.speedBpm,
            sparkleRate: params.sparkleRate,
            sparkleStyle: params.sparkleStyle || 'incandescent',
            ambientColorMode: params.ambientColorMode || 'artwork',
            ambientCustomColor: params.ambientCustomColor || '#ffb703',
            greenHue: params.greenHue,
            brightness: params.brightness,
            glowSize: params.glowSize
        },
        sequence: {
            loopDuration: sequenceLoopDuration,
            cues: JSON.parse(JSON.stringify(sequenceCues))
        }
    };

    const cacheKey = `custom_slot_${slot}_${Date.now()}`;
    fleetPresetCache[cacheKey] = editorData;
    runner.preset = cacheKey;

    saveFleetLineupToStorage();
    renderFleetCards();
    showToast(`📋 Copied current single-shirt editor design to Runner #${runner.num}!`);
}

// Assign Current Single-Shirt Editor State to All 7 Runners
function assignCurrentEditorToAllRunners() {
    for (let slot = 0; slot < fleetRunners.length; slot++) {
        const runner = fleetRunners[slot];
        const editorData = {
            name: `${runner.name} (Unified Fleet)`,
            floatName: `Float ${runner.slot + 1} - ${runner.name}`,
            savedAt: new Date().toISOString(),
            ledCount: leds.length,
            leds: JSON.parse(JSON.stringify(leds)),
            graphicType: currentGraphicType,
            customArtworkDataUrl: customArtworkDataUrl,
            animationGroups: JSON.parse(JSON.stringify(animationGroups)),
            settings: {
                pattern: activePattern,
                direction: params.direction || 1,
                speedBpm: params.speedBpm,
                sparkleRate: params.sparkleRate,
                sparkleStyle: params.sparkleStyle || 'incandescent',
                ambientColorMode: params.ambientColorMode || 'artwork',
                ambientCustomColor: params.ambientCustomColor || '#ffb703',
                greenHue: params.greenHue,
                brightness: params.brightness,
                glowSize: params.glowSize
            },
            sequence: {
                loopDuration: sequenceLoopDuration,
                cues: JSON.parse(JSON.stringify(sequenceCues))
            }
        };
        const cacheKey = `custom_slot_${slot}_${Date.now()}`;
        fleetPresetCache[cacheKey] = editorData;
        runner.preset = cacheKey;
    }
    saveFleetLineupToStorage();
    renderFleetCards();
    showToast(`📋 Assigned current editor design to all 7 runners!`);
}

// Reset Lineup to Official Parade Roster Defaults
function resetFleetLineupDefaults() {
    fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
    saveFleetLineupToStorage();
    fleetRunners.forEach(r => getPresetDataForRunner(r));
    renderFleetCards();
    showToast("🔁 Restored official 7-float Electrical Parade lineup defaults!");
}

// ============================================================================
// FLEET SHOW CREATOR UI & CHOREOGRAPHY STACK EDITOR
// ============================================================================

// Render the choreography block cards inside the Fleet Show Creator stack
function renderFleetBlocksEditor() {
    const container = document.getElementById('fleetBlocksStackContainer');
    const countText = document.getElementById('fleetBlockCountText');
    const durationBadge = document.getElementById('fleetShowDurationBadge');
    if (!container || !activeFleetShow) return;

    const blocks = activeFleetShow.blocks || [];
    if (countText) countText.textContent = `${blocks.length} Blocks`;
    if (durationBadge) durationBadge.textContent = `${(activeFleetShow.loopDuration || 30.0).toFixed(1)}s Total`;

    container.innerHTML = '';

    blocks.forEach((block, idx) => {
        const def = FLEET_BLOCK_DEFS[block.type] || { icon: "✨", name: block.name || "Block" };
        const card = document.createElement('div');
        const isCurrentActive = fleetShowActive && getActiveFleetBlock(fleetShowElapsedSec)?.index === idx;
        card.className = `fleet-block-card ${isCurrentActive ? 'active-block' : ''}`;
        card.setAttribute('data-index', idx);

        const startTime = block.startTime || 0;
        const endTime = startTime + (block.duration || 1.0);
        const colorMode = block.params?.colorMode || 'cycle_random';

        card.innerHTML = `
            <div class="fleet-block-header">
                <span class="fleet-block-title">
                    <span>${def.icon}</span>
                    <span>${idx + 1}. ${block.name || def.name}</span>
                </span>
                <span class="fleet-block-time-badge">${startTime.toFixed(1)}s – ${endTime.toFixed(1)}s (${(block.duration || 1.0).toFixed(1)}s)</span>
            </div>
            <div class="fleet-block-controls">
                <div>
                    <label style="font-size: 9.5px; color: var(--text-muted); display: block; margin-bottom: 2px;">Duration (sec):</label>
                    <input type="number" class="fleet-block-dur-input" data-index="${idx}" min="0.1" max="30.0" step="0.1" value="${(block.duration || 1.0).toFixed(1)}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 3px 6px; font-size: 11px;">
                </div>
                <div>
                    <label style="font-size: 9.5px; color: var(--text-muted); display: block; margin-bottom: 2px;">Color Dynamic:</label>
                    <select class="fleet-block-color-select" data-index="${idx}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 3px 4px; font-size: 10.5px;">
                        <option value="cycle_random" ${colorMode === 'cycle_random' ? 'selected' : ''}>🎨 Disney Palette Cycle</option>
                        <option value="match_previous" ${colorMode === 'match_previous' ? 'selected' : ''}>🔗 Match Previous</option>
                        ${FLEET_WAVE_STANDARD_COLORS.map(c => `
                            <option value="${c.name}" ${colorMode === c.name ? 'selected' : ''}>🟡 ${c.name}</option>
                        `).join('')}
                    </select>
                </div>
            </div>
            <div class="fleet-block-btn-row">
                <button type="button" class="fleet-block-mini-btn btn-move-up" data-index="${idx}" title="Move Up (Earlier)" ${idx === 0 ? 'disabled style="opacity:0.4"' : ''}>▲</button>
                <button type="button" class="fleet-block-mini-btn btn-move-down" data-index="${idx}" title="Move Down (Later)" ${idx === blocks.length - 1 ? 'disabled style="opacity:0.4"' : ''}>▼</button>
                <button type="button" class="fleet-block-mini-btn btn-duplicate" data-index="${idx}" title="Duplicate this block">📋</button>
                <button type="button" class="fleet-block-mini-btn danger btn-delete" data-index="${idx}" title="Delete block">🗑️</button>
            </div>
        `;

        container.appendChild(card);
    });
}

// Recalculate block start times and total loop duration
function recalculateFleetBlockStartTimes() {
    if (!activeFleetShow || !Array.isArray(activeFleetShow.blocks)) return;
    let t = 0.0;
    activeFleetShow.blocks.forEach(b => {
        b.startTime = Math.round(t * 100) / 100;
        t += (b.duration || 1.0);
    });
    activeFleetShow.loopDuration = Math.round(t * 100) / 100;
}

// Proportionally adjust block durations to total exactly 30.0 seconds
function snapFleetShowTo30s() {
    if (!activeFleetShow || !Array.isArray(activeFleetShow.blocks) || activeFleetShow.blocks.length === 0) return;
    recalculateFleetBlockStartTimes();
    const currentDur = activeFleetShow.loopDuration;
    if (currentDur <= 0.01) return;

    const scale = 30.0 / currentDur;
    activeFleetShow.blocks.forEach(b => {
        b.duration = Math.max(0.1, Math.round(b.duration * scale * 10) / 10);
    });
    recalculateFleetBlockStartTimes();
    renderFleetBlocksEditor();
    updateFleetShowUI();
    if (currentView === 'fleet') renderTimelineLayers();
    showToast(`⏱️ Adjusted all blocks to total exactly 30.0s!`);
}

// Add a new choreography block to the active fleet show
function addFleetBlock(type) {
    if (!activeFleetShow) return;
    const def = FLEET_BLOCK_DEFS[type] || FLEET_BLOCK_DEFS['wave_forward'];
    const newBlock = {
        id: `blk_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
        name: def.name,
        type: type,
        startTime: activeFleetShow.loopDuration || 0.0,
        duration: def.defaultDuration || 1.5,
        params: JSON.parse(JSON.stringify(def.defaultParams || {}))
    };
    activeFleetShow.blocks.push(newBlock);
    recalculateFleetBlockStartTimes();
    renderFleetBlocksEditor();
    updateFleetShowUI();
    if (currentView === 'fleet') renderTimelineLayers();
    showToast(`➕ Added "${def.name}" block to Fleet Show!`);
}

// Remove a block from active fleet show
function removeFleetBlock(index) {
    if (!activeFleetShow || !activeFleetShow.blocks[index]) return;
    const name = activeFleetShow.blocks[index].name;
    activeFleetShow.blocks.splice(index, 1);
    recalculateFleetBlockStartTimes();
    renderFleetBlocksEditor();
    updateFleetShowUI();
    if (currentView === 'fleet') renderTimelineLayers();
    showToast(`🗑️ Removed block "${name}"`);
}

// Move a block earlier or later in sequence
function moveFleetBlock(index, delta) {
    if (!activeFleetShow) return;
    const targetIdx = index + delta;
    if (targetIdx < 0 || targetIdx >= activeFleetShow.blocks.length) return;
    const item = activeFleetShow.blocks.splice(index, 1)[0];
    activeFleetShow.blocks.splice(targetIdx, 0, item);
    recalculateFleetBlockStartTimes();
    renderFleetBlocksEditor();
    updateFleetShowUI();
    if (currentView === 'fleet') renderTimelineLayers();
}

// Duplicate a block
function duplicateFleetBlock(index) {
    if (!activeFleetShow || !activeFleetShow.blocks[index]) return;
    const orig = activeFleetShow.blocks[index];
    const clone = JSON.parse(JSON.stringify(orig));
    clone.id = `blk_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;
    clone.name = `${orig.name} (Copy)`;
    activeFleetShow.blocks.splice(index + 1, 0, clone);
    recalculateFleetBlockStartTimes();
    renderFleetBlocksEditor();
    updateFleetShowUI();
    if (currentView === 'fleet') renderTimelineLayers();
    showToast(`📋 Duplicated block "${orig.name}"!`);
}

// Save active fleet show to server and browser storage
async function saveActiveFleetShow() {
    if (!activeFleetShow) return;
    recalculateFleetBlockStartTimes();
    activeFleetShow.updatedAt = new Date().toISOString();

    const filename = activeFleetShow.id.endsWith('.json') ? activeFleetShow.id : `${activeFleetShow.id}.json`;

    // Save to localStorage
    try {
        localStorage.setItem(`msep_fleet_show_${activeFleetShow.id}`, JSON.stringify(activeFleetShow));
        localStorage.setItem('msep_active_fleet_show_id', filename);
    } catch (e) {}

    // Save to server
    try {
        const res = await fetch('/api/save_fleet_show', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(activeFleetShow)
        });
        if (res.ok) {
            showToast(`💾 Saved Fleet Show "${activeFleetShow.name}" to server!`);
            await refreshFleetShowsDropdown();
            return;
        }
    } catch (e) {
        console.warn("Could not save fleet show to server:", e);
    }
    showToast(`💾 Saved Fleet Show "${activeFleetShow.name}" to browser storage!`);
}

// Load a fleet show from server or browser storage
async function loadFleetShow(filename) {
    if (!filename) return;
    try {
        const res = await fetch(`/api/fleet_show/${encodeURIComponent(filename)}`);
        if (res.ok) {
            const data = await res.json();
            activeFleetShow = data;
            recalculateFleetBlockStartTimes();
            renderFleetBlocksEditor();
            updateFleetShowUI();
            if (currentView === 'fleet') renderTimelineLayers();
            try { localStorage.setItem('msep_active_fleet_show_id', filename); } catch (e) {}
            showToast(`👑 Loaded Fleet Show: "${activeFleetShow.name}" (${activeFleetShow.loopDuration.toFixed(1)}s)`);
            return;
        }
    } catch (e) {}

    try {
        const raw = localStorage.getItem(`msep_fleet_show_${filename.replace('.json', '')}`);
        if (raw) {
            activeFleetShow = JSON.parse(raw);
            recalculateFleetBlockStartTimes();
            renderFleetBlocksEditor();
            updateFleetShowUI();
            if (currentView === 'fleet') renderTimelineLayers();
            showToast(`👑 Loaded Fleet Show: "${activeFleetShow.name}" from local storage`);
            return;
        }
    } catch (e) {}
}

// Refresh Fleet Shows Dropdown with server and local options
async function refreshFleetShowsDropdown() {
    const sel = document.getElementById('fleetShowSelect');
    if (!sel) return;

    let serverShows = [];
    try {
        const res = await fetch('/api/fleet_shows');
        if (res.ok) serverShows = await res.json();
    } catch (e) {}

    const localShows = [];
    try {
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            if (k && k.startsWith('msep_fleet_show_')) {
                try {
                    const parsed = JSON.parse(localStorage.getItem(k));
                    if (parsed && parsed.id) localShows.push(parsed);
                } catch (e) {}
            }
        }
    } catch (e) {}

    const currentVal = activeFleetShow ? (activeFleetShow.id.endsWith('.json') ? activeFleetShow.id : `${activeFleetShow.id}.json`) : 'default_30s_grand_parade.json';

    sel.innerHTML = `
        <optgroup label="Official Fleet Shows">
            ${serverShows.map(s => `
                <option value="${s.filename}" ${s.filename === currentVal ? 'selected' : ''}>
                    👑 ${s.name} (${s.loopDuration || 30}s)
                </option>
            `).join('')}
        </optgroup>
        ${localShows.length > 0 ? `
            <optgroup label="Custom Saved Shows">
                ${localShows.map(s => `
                    <option value="${s.id}.json" ${(`${s.id}.json` === currentVal) ? 'selected' : ''}>
                        💾 ${s.name} (${s.loopDuration || 30}s)
                    </option>
                `).join('')}
            </optgroup>
        ` : ''}
    `;
}

// Create a new blank fleet show routine
function createNewFleetShow() {
    const showId = `fleet_show_${Date.now()}`;
    activeFleetShow = {
        id: showId,
        name: "Custom 30s Fleet Routine",
        description: "Custom user-designed synchronized 7-shirt fleet sequence",
        version: "1.0",
        loopDuration: 30.0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        blocks: [
            { id: "blk_1", name: "Dramatic Blackout", type: "blackout", startTime: 0.0, duration: 1.0, params: {} },
            { id: "blk_2", name: "Forward Wave (1➔7)", type: "wave_forward", startTime: 1.0, duration: 2.0, params: { colorMode: "cycle_random", trailLengthShirts: 2.0 } },
            { id: "blk_3", name: "All-Fleet Pulse", type: "fleet_pulse", startTime: 3.0, duration: 5.0, params: { colorMode: "match_previous" } },
            { id: "blk_4", name: "Reverse Wave (7➔1)", type: "wave_reverse", startTime: 8.0, duration: 2.0, params: { colorMode: "match_previous", trailLengthShirts: 2.0 } },
            { id: "blk_5", name: "Starlight Sparkle Storm", type: "sparkle_storm", startTime: 10.0, duration: 4.0, params: { sparkleColorMix: "wave_and_white" } },
            { id: "blk_6", name: "Carnival Finale", type: "grand_finale", startTime: 14.0, duration: 5.0, params: {} }
        ]
    };
    recalculateFleetBlockStartTimes();
    snapFleetShowTo30s();
    renderFleetBlocksEditor();
    updateFleetShowUI();
    if (currentView === 'fleet') renderTimelineLayers();
    showToast(`✨ Created new Fleet Show! Customize blocks or Snap to 30s.`);
}

// Generate C++ FastLED code for the active Fleet Choreography Show
function generateFleetRoutineCpp(fleetShow) {
    if (!fleetShow) fleetShow = activeFleetShow;
    const blocks = (fleetShow && fleetShow.blocks) ? fleetShow.blocks : [];
    const totalSec = fleetShow?.loopDuration || 30.0;
    const totalMs = Math.round(totalSec * 1000);
    const showName = fleetShow?.name || "Custom Fleet Show";

    let cpp = `// Auto-Generated FastLED Fleet Choreography Routine
// Show Name: ${showName}
// Total Duration: ${totalSec.toFixed(1)}s (${totalMs} ms)
// Generated by Main Street Electrical Parade Simulator

void render30sFleetRoutine(uint32_t elapsedMs) {
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB routineColor = STANDARD_FLEET_COLORS[fleetRoutineCycle % 7];
`;

    if (blocks.length === 0) {
        cpp += `
    // No choreography blocks configured: default blackout
    fill_solid(leds, FRONT_LEDS, CRGB::Black);
`;
    } else {
        blocks.forEach((block, idx) => {
            const startMs = Math.round((block.startTime || 0) * 1000);
            const durMs = Math.max(100, Math.round((block.duration || 1.0) * 1000));
            const endMs = startMs + durMs;
            const bType = block.type || 'wave_forward';
            const colorMode = block.params?.colorMode || 'cycle_random';

            // Resolve C++ color expression
            let colorExpr = 'routineColor';
            if (colorMode === 'cycle_random') {
                colorExpr = `STANDARD_FLEET_COLORS[(fleetRoutineCycle + ${idx}) % 7]`;
            } else if (colorMode === 'match_previous') {
                colorExpr = 'routineColor';
            } else if (colorMode === 'Electric Gold') {
                colorExpr = 'CRGB(255, 195, 20)';
            } else if (colorMode === 'Electric Lime') {
                colorExpr = 'CRGB(40, 255, 40)';
            } else if (colorMode === 'Parade Teal') {
                colorExpr = 'CRGB(40, 220, 200)';
            } else if (colorMode === "Pete's Dragon Green") {
                colorExpr = 'CRGB(20, 255, 110)';
            } else if (colorMode === 'Parade Ruby Red') {
                colorExpr = 'CRGB(240, 50, 50)';
            } else if (colorMode === 'Magic Violet') {
                colorExpr = 'CRGB(170, 60, 255)';
            } else if (colorMode === 'Citrus Orange') {
                colorExpr = 'CRGB(255, 130, 20)';
            } else if (colorMode === 'Electric Cyan') {
                colorExpr = 'CRGB(50, 180, 240)';
            } else if (colorMode === 'Hot Pink') {
                colorExpr = 'CRGB(255, 20, 140)';
            } else if (colorMode === 'Bright White') {
                colorExpr = 'CRGB(255, 255, 255)';
            }

            const prefix = (idx === 0) ? '    if' : '    else if';

            if (bType === 'blackout') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Blackout'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }`;
            } else if (bType === 'wave_forward') {
                const trail = (block.params?.trailLengthShirts || 2.0).toFixed(1);
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Forward Wave (1->7)'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float waveProgress = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float headPos = waveProgress * 6.0f;
        float dist = fabs((float)floatIdx - headPos);
        float trailLength = ${trail}f;

        if (dist <= trailLength) {
            float intensity = 1.0f - (dist / trailLength);
            CRGB col = ${colorExpr};
            col.nscale8_video((uint8_t)(intensity * 255));
            if (dist < 0.45f) {
                col = blend(col, CRGB(255, 245, 220), (uint8_t)((1.0f - (dist / 0.45f)) * 230));
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'wave_reverse') {
                const trail = (block.params?.trailLengthShirts || 2.0).toFixed(1);
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Reverse Wave (7->1)'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float waveProgress = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float headPos = 6.0f - (waveProgress * 6.0f);
        float dist = fabs((float)floatIdx - headPos);
        float trailLength = ${trail}f;

        if (dist <= trailLength) {
            float intensity = 1.0f - (dist / trailLength);
            CRGB col = ${colorExpr};
            col.nscale8_video((uint8_t)(intensity * 255));
            if (dist < 0.45f) {
                col = blend(col, CRGB(255, 245, 220), (uint8_t)((1.0f - (dist / 0.45f)) * 230));
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'fleet_pulse') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'All-Fleet Pulse'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        uint8_t breath = beatsin8(36, 70, 255, fleetRoutineStartTime + ${startMs});
        CRGB col = ${colorExpr};
        col.nscale8_video(breath);
        if (breath > 240) {
            col = blend(col, CRGB(255, 255, 230), map(breath, 240, 255, 0, 180));
        }
        fill_solid(leds, FRONT_LEDS, col);
    }`;
            } else if (bType === 'sparkle_storm') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Starlight Sparkle Storm'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        CRGB dimBase = ${colorExpr};
        dimBase.nscale8_video(35);
        fill_solid(leds, FRONT_LEDS, dimBase);
        for (int i = 0; i < FRONT_LEDS; i++) {
            if (random16(1000) < 140) {
                leds[i] = (random8(2) == 0) ? ${colorExpr} : CRGB(255, 255, 240);
            }
        }
    }`;
            } else if (bType === 'center_burst') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Center-Outward Energy Burst'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float burstProgress = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float burstRadius = burstProgress * 3.5f;
        float distFromCenter = fabs((float)floatIdx - 3.0f);
        float ringDist = fabs(distFromCenter - burstRadius);

        if (ringDist < 1.2f) {
            float intensity = 1.0f - (ringDist / 1.2f);
            CRGB col = ${colorExpr};
            col.nscale8_video((uint8_t)(intensity * 255));
            if (ringDist < 0.35f) {
                col = blend(col, CRGB(255, 255, 240), 220);
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'converge_center') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Inward Converging Wave'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float targetDist = p * 3.5f;
        float distInward = (floatIdx <= 3) ? (float)floatIdx : (6.0f - (float)floatIdx);
        float delta = fabs(targetDist - distInward);

        if (delta < 1.2f) {
            float intensity = 1.0f - (delta / 1.2f);
            CRGB col = ${colorExpr};
            col.nscale8_video((uint8_t)(intensity * 255));
            if (p > 0.85f && floatIdx == 3) {
                col = blend(col, CRGB(255, 255, 255), 230);
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'wig_wag') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Odd/Even Marquee Wig-Wag'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        uint8_t phase = ((elapsedMs - ${startMs}) / 250) % 2;
        bool isOddFloat = (myFloatNumber % 2 != 0);
        if ((phase == 0 && isOddFloat) || (phase == 1 && !isOddFloat)) {
            fill_solid(leds, FRONT_LEDS, ${colorExpr});
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'baton_chase') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Baton Leapfrog Chase'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        uint8_t activeRunner = ((elapsedMs - ${startMs}) / 428) % 7;
        if (floatIdx == activeRunner) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 245, 220));
        } else {
            CRGB dimBase = FLEET_ROSTER_INFO[floatIdx].color;
            dimBase.nscale8_video(40);
            fill_solid(leds, FRONT_LEDS, dimBase);
        }
    }`;
            } else if (bType === 'ping_pong_wave') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Ping-Pong Double Bounce'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float bounceCycle = fmod((float)(elapsedMs - ${startMs}) / (${durMs}.0f / 2.0f), 2.0f);
        float headPos = (bounceCycle < 1.0f) ? (bounceCycle * 6.0f) : ((2.0f - bounceCycle) * 6.0f);
        float dist = fabs((float)floatIdx - headPos);

        if (dist <= 1.8f) {
            float intensity = 1.0f - (dist / 1.8f);
            CRGB col = ${colorExpr};
            col.nscale8_video((uint8_t)(intensity * 255));
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'color_wash_chase') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Color Wash Progressive Fill'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float threshold = p * 7.5f;
        if ((float)floatIdx < floorf(threshold)) {
            fill_solid(leds, FRONT_LEDS, ${colorExpr});
        } else if (fabs((float)floatIdx - floorf(threshold)) < 0.5f) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 255, 255));
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }`;
            } else if (bType === 'rainbow_sweep') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Rainbow Fleet Sweep'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        uint8_t hue = (uint8_t)(p * 255.0f + floatIdx * 36);
        fill_solid(leds, FRONT_LEDS, CHSV(hue, 220, 255));
    }`;
            } else if (bType === 'strobe_all') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'All-Fleet Strobe'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        bool flash = ((elapsedMs / 50) % 2 == 0);
        fill_solid(leds, FRONT_LEDS, flash ? CRGB(255, 255, 255) : CRGB::Black);
    }`;
            } else if (bType === 'shimmer_drift') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Shimmer & Twinkle Drift'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        uint8_t shimmer = beatsin8(45, 60, 220, fleetRoutineStartTime + ${startMs} + floatIdx * 300);
        CRGB col = ${colorExpr};
        col.nscale8_video(shimmer);
        fill_solid(leds, FRONT_LEDS, col);
        for (int i = 0; i < FRONT_LEDS; i++) {
            if (random16(1000) < 60) leds[i] = CRGB(255, 255, 240);
        }
    }`;
            } else if (bType === 'grand_finale') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Carnival Finale Crescendo'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        uint8_t hue = (uint8_t)(elapsedMs * 3 / 10 + floatIdx * 36);
        fill_solid(leds, FRONT_LEDS, CHSV(hue, 220, 255));
        if (p >= 0.65f && ((elapsedMs / 70) % 2 == 0)) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 255, 255));
        }
    }`;
            } else if (bType === 'color_collision') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Dual Collision & Shockwave'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        if (p < 0.45f) {
            float inP = p / 0.45f;
            float headL = inP * 3.0f;
            float headR = 6.0f - (inP * 3.0f);
            float distL = fabs((float)floatIdx - headL);
            float distR = fabs((float)floatIdx - headR);
            float minDist = fminf(distL, distR);
            if (minDist <= 1.4f) {
                float intensity = 1.0f - (minDist / 1.4f);
                CRGB col = (distL < distR) ? ${colorExpr} : CRGB(255, 60, 180);
                col.nscale8_video((uint8_t)(intensity * 255));
                fill_solid(leds, FRONT_LEDS, col);
            } else {
                fill_solid(leds, FRONT_LEDS, CRGB::Black);
            }
        } else if (p < 0.60f) {
            // Impact supernova flash at Float 4 (Peter Pan)
            if (floatIdx == 3) {
                fill_solid(leds, FRONT_LEDS, CRGB(255, 255, 255));
            } else {
                CRGB dimCol = ${colorExpr};
                dimCol.nscale8_video(30);
                fill_solid(leds, FRONT_LEDS, dimCol);
            }
        } else {
            // Rebound shockwave radiating back out
            float shockP = (p - 0.60f) / 0.40f;
            float shockRadius = shockP * 3.2f;
            float distFromCenter = fabs((float)floatIdx - 3.0f);
            float ringDist = fabs(distFromCenter - shockRadius);
            if (ringDist <= 1.2f) {
                float intensity = 1.0f - (ringDist / 1.2f);
                CRGB col = blend(${colorExpr}, CRGB(255, 240, 180), 120);
                col.nscale8_video((uint8_t)(intensity * 255));
                fill_solid(leds, FRONT_LEDS, col);
            } else {
                fill_solid(leds, FRONT_LEDS, CRGB::Black);
            }
        }
    }`;
            } else if (bType === 'cross_dissolve_chase') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Silky Cascade Dissolve'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float runnerOffset = (float)floatIdx / 7.0f;
        float localRunnerP = fminf(1.0f, fmaxf(0.0f, (p - runnerOffset * 0.5f) / 0.5f));
        uint8_t blendAmt = (uint8_t)(0.5f * (1.0f - cosf(localRunnerP * 3.14159f)) * 255);
        CRGB colA = ${colorExpr};
        CRGB colB = CRGB(0, 220, 255);
        CRGB finalCol = blend(colA, colB, blendAmt);
        fill_solid(leds, FRONT_LEDS, finalCol);
    }`;
            } else if (bType === 'ripple_echo') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Mirror Pair Echo (Butterfly Ripple)'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        int subPhase = (int)(p * 4.0f) % 4;
        float subP = fmodf(p * 4.0f, 1.0f);
        uint8_t pulse = (uint8_t)(sinf(subP * 3.14159f) * 255);
        bool isActivePair = false;
        if (subPhase == 0 && floatIdx == 3) isActivePair = true;
        else if (subPhase == 1 && (floatIdx == 2 || floatIdx == 4)) isActivePair = true;
        else if (subPhase == 2 && (floatIdx == 1 || floatIdx == 5)) isActivePair = true;
        else if (subPhase == 3 && (floatIdx == 0 || floatIdx == 6)) isActivePair = true;

        if (isActivePair) {
            CRGB col = ${colorExpr};
            col.nscale8_video(pulse);
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            CRGB dimCol = ${colorExpr};
            dimCol.nscale8_video(25);
            fill_solid(leds, FRONT_LEDS, dimCol);
        }
    }`;
            } else if (bType === 'sparkle_cascade') {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Fairy Dust Waterfall Cascade'} (${(startMs/1000).toFixed(1)}s - ${(endMs/1000).toFixed(1)}s)
        float p = (float)(elapsedMs - ${startMs}) / ${durMs}.0f;
        float center = p * 6.0f;
        float dist = fabs((float)floatIdx - center);
        CRGB baseCol = ${colorExpr};
        baseCol.nscale8_video(30);
        fill_solid(leds, FRONT_LEDS, baseCol);
        if (dist <= 1.5f) {
            float intensity = 1.0f - (dist / 1.5f);
            uint8_t sparkleCount = (uint8_t)(intensity * 25.0f);
            for (int s = 0; s < sparkleCount; s++) {
                uint8_t rndPix = random8(FRONT_LEDS);
                leds[rndPix] = (random8(100) < 60) ? CRGB(255, 255, 255) : blend(baseCol, CRGB(255, 215, 0), 160);
            }
        }
    }`;
            } else {
                cpp += `\n${prefix} (elapsedMs < ${endMs}) {
        // Block ${idx + 1}: ${block.name || 'Custom Effect'}
        fill_solid(leds, FRONT_LEDS, ${colorExpr});
    }`;
            }
        });

        cpp += `
    else {
        // Routine completed: blackout curtain
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }`;
    }

    cpp += `

    // Duplicate front 100 LEDs to back 100 LEDs for full 200-LED costume!
    duplicateFrontToBack();

    // Clear any extra LEDs beyond strand count
    for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = CRGB::Black;
    }

    // Status LED blink cadence during fleet routine
    digitalWrite(STATUS_LED_PIN, ((elapsedMs / 200) % 2 == 0) ? HIGH : LOW);

    FastLED.show();
    delay(15);
}`;

    return cpp;
}

// Display Generated FastLED C++ Code in Code Export Modal
function viewFleetShowCpp() {
    if (!activeFleetShow) return;
    const code = generateFleetRoutineCpp(activeFleetShow);
    const codeOutput = document.getElementById('codeOutput');
    const codeModal = document.getElementById('codeModal');
    const modalHeaderTitle = codeModal?.querySelector('.modal-header h3');

    if (modalHeaderTitle) {
        modalHeaderTitle.textContent = `FastLED Fleet Routine (${activeFleetShow.name || 'Custom Show'})`;
    }
    if (codeOutput) {
        codeOutput.textContent = code;
    }
    if (codeModal) {
        codeModal.classList.add('open');
    }
}

// Export Active Fleet Choreography Directly into C++ Firmware and Test Compile
async function applyFleetShowToFirmware() {
    if (!activeFleetShow) return;
    const btn = document.getElementById('fleetApplyFirmwareBtn');
    const origText = btn ? btn.textContent : '⚡ Apply to Firmware';
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Compiling...';
    }

    try {
        const cppCode = generateFleetRoutineCpp(activeFleetShow);
        showToast("⚡ Updating firmware & testing compilation with PlatformIO...");

        const res = await fetch('/api/export_fleet_routine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cppCode: cppCode,
                loopDuration: activeFleetShow.loopDuration || 30.0,
                showName: activeFleetShow.name || "Custom Fleet Show",
                verifyCompile: true
            })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || `HTTP ${res.status}`);
        }

        const data = await res.json();
        if (data.success) {
            if (data.compileResult && data.compileResult.tested) {
                if (data.compileResult.success) {
                    showToast(`✅ Firmware updated & verified! (${(data.loopDuration).toFixed(1)}s routine compiled cleanly)`);
                } else {
                    showToast(`⚠️ Firmware files updated, but compile check had warnings. See terminal.`);
                    console.warn("PlatformIO compile output:", data.compileResult.output);
                }
            } else {
                showToast(`💾 Exported "${data.showName}" (${(data.loopDuration).toFixed(1)}s) to firmware!`);
            }
        } else {
            throw new Error(data.error || "Failed to update firmware");
        }
    } catch (err) {
        console.error("Error exporting fleet routine to firmware:", err);
        showToast(`❌ Firmware export error: ${err.message}`);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = origText;
        }
    }
}

// Persist Lineup Configuration to LocalStorage and Backend
function saveFleetLineupToStorage() {
    try {
        localStorage.setItem('msep_fleet_lineup', JSON.stringify(fleetRunners));
        localStorage.setItem('msep_fleet_sync_mode', fleetSyncMode);
        localStorage.setItem('msep_fleet_wave_duration', String(fleetWaveCycleDurationMs));
    } catch (e) {}

    try {
        fetch('/api/save_fleet_config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fleetRunners)
        }).catch(() => {});
    } catch (e) {}
}

// Load Lineup Configuration from Storage on Startup
async function loadFleetLineupFromStorage() {
    try {
        // One-time cleanup of legacy pre-cleanup browser presets
        if (!localStorage.getItem('msep_presets_cleanup_v1_done')) {
            localStorage.removeItem('msep_custom_presets');
            localStorage.setItem('msep_presets_cleanup_v1_done', 'true');
        }
        const savedLineup = localStorage.getItem('msep_fleet_lineup');
        if (savedLineup) {
            const parsed = JSON.parse(savedLineup);
            if (Array.isArray(parsed) && parsed.length === 7) {
                fleetRunners = parsed.map((item, idx) => ({ ...DEFAULT_FLEET_ROSTER[idx], ...item }));
            } else {
                fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
            }
        } else {
            try {
                const res = await fetch('/api/fleet_config');
                if (res.ok) {
                    const serverConfig = await res.json();
                    if (Array.isArray(serverConfig) && serverConfig.length === 7) {
                        fleetRunners = serverConfig.map((item, idx) => ({ ...DEFAULT_FLEET_ROSTER[idx], ...item }));
                    } else {
                        fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
                    }
                } else {
                    fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
                }
            } catch (e) {
                fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
            }
        }
    } catch (e) {
        fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
    }

    if (!Array.isArray(fleetRunners) || fleetRunners.length !== 7) {
        fleetRunners = JSON.parse(JSON.stringify(DEFAULT_FLEET_ROSTER));
    } else {
        // Ensure every slot has complete default properties (icon, name, role, color, etc.)
        fleetRunners = fleetRunners.map((item, idx) => ({ ...DEFAULT_FLEET_ROSTER[idx], ...item }));
    }

    // Ensure slot 4 (Cinderella/Coach) always defaults to cinderellas_coach_both_wheel.json
    if (fleetRunners[4] && (fleetRunners[4].preset === 'server:cinderellas_coach.json' || fleetRunners[4].preset === 'server:carriage_nohorses.json' || !fleetRunners[4].preset || fleetRunners[4].preset.includes('cinderellas_coach') || fleetRunners[4].preset.includes('carriage_nohorses'))) {
        fleetRunners[4].preset = 'server:cinderellas_coach_both_wheel.json';
        fleetRunners[4].defaultGraphic = 'cinderella_coach';
    }

    // Preload all runner presets into cache in parallel
    try {
        await Promise.all(fleetRunners.map(r => getPresetDataForRunner(r)));
    } catch (e) {
        console.warn("Error preloading fleet presets:", e);
    }
}

// Initialize Fleet Lineup Manager controls and event listeners
function initFleetManager() {
    const activateBtn = document.getElementById('fleetShowActivateBtn');
    const showSelect = document.getElementById('fleetShowSelect');
    const saveShowBtn = document.getElementById('fleetSaveShowBtn');
    const newShowBtn = document.getElementById('fleetNewShowBtn');
    const snap30Btn = document.getElementById('fleetSnap30Btn');
    const addBlockBtn = document.getElementById('fleetAddBlockBtn');
    const addBlockTypeSelect = document.getElementById('fleetAddBlockTypeSelect');
    const stackContainer = document.getElementById('fleetBlocksStackContainer');
    const assignAllBtn = document.getElementById('fleetAssignAllCurrentBtn');
    const resetBtn = document.getElementById('fleetResetDefaultsBtn');
    const saveBtn = document.getElementById('fleetSaveConfigBtn');
    const runnersContainer = document.getElementById('fleetRunnersContainer');

    // 1. One-Shot Fleet Show Activation / Early Stop Trigger with 300ms software debounce
    if (activateBtn) {
        activateBtn.addEventListener('click', (e) => {
            e.preventDefault();
            triggerFleetShowToggle();
        });
    }

    // 2. Global Hotkey: 'F' triggers or stops Fleet Show early
    window.addEventListener('keydown', (e) => {
        const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
        if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select') return;
        if (e.key === 'f' || e.key === 'F') {
            e.preventDefault();
            triggerFleetShowToggle();
        }
    });

    // 3. Show Selector, Save, New, Snap Buttons
    if (showSelect) {
        showSelect.addEventListener('change', (e) => {
            loadFleetShow(e.target.value);
        });
    }
    if (saveShowBtn) saveShowBtn.addEventListener('click', saveActiveFleetShow);
    if (newShowBtn) newShowBtn.addEventListener('click', createNewFleetShow);
    if (snap30Btn) snap30Btn.addEventListener('click', snapFleetShowTo30s);

    const viewCppBtn = document.getElementById('fleetViewCppBtn');
    if (viewCppBtn) viewCppBtn.addEventListener('click', viewFleetShowCpp);

    const applyFirmwareBtn = document.getElementById('fleetApplyFirmwareBtn');
    if (applyFirmwareBtn) applyFirmwareBtn.addEventListener('click', applyFleetShowToFirmware);

    const goToFlasherBtn = document.getElementById('goToFlasherBtn');
    if (goToFlasherBtn) {
        goToFlasherBtn.addEventListener('click', () => {
            switchSidebarTab('tabHardware');
            document.getElementById('deployFlasherSection')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            showToast(`⚡ Switched to Deploy Flasher for Float #${activeSingleShirtRunnerSlot + 1}`);
        });
    }

    if (addBlockBtn && addBlockTypeSelect) {
        addBlockBtn.addEventListener('click', () => {
            addFleetBlock(addBlockTypeSelect.value);
        });
    }

    // 4. Event Delegation on Blocks Stack Container (Duration, ColorMode, Up, Down, Copy, Delete)
    if (stackContainer) {
        stackContainer.addEventListener('input', (e) => {
            const durInput = e.target.closest('.fleet-block-dur-input');
            if (durInput && activeFleetShow) {
                const idx = parseInt(durInput.getAttribute('data-index'));
                const val = parseFloat(durInput.value);
                if (!isNaN(val) && val > 0 && activeFleetShow.blocks[idx]) {
                    activeFleetShow.blocks[idx].duration = val;
                    recalculateFleetBlockStartTimes();
                    renderFleetBlocksEditor();
                    updateFleetShowUI();
                    if (currentView === 'fleet') renderTimelineLayers();
                }
            }
        });

        stackContainer.addEventListener('change', (e) => {
            const colSelect = e.target.closest('.fleet-block-color-select');
            if (colSelect && activeFleetShow) {
                const idx = parseInt(colSelect.getAttribute('data-index'));
                if (activeFleetShow.blocks[idx]) {
                    if (!activeFleetShow.blocks[idx].params) activeFleetShow.blocks[idx].params = {};
                    activeFleetShow.blocks[idx].params.colorMode = colSelect.value;
                    updateFleetShowUI();
                }
            }
        });

        stackContainer.addEventListener('click', (e) => {
            const btnMoveUp = e.target.closest('.btn-move-up');
            if (btnMoveUp) {
                const idx = parseInt(btnMoveUp.getAttribute('data-index'));
                moveFleetBlock(idx, -1);
                return;
            }
            const btnMoveDown = e.target.closest('.btn-move-down');
            if (btnMoveDown) {
                const idx = parseInt(btnMoveDown.getAttribute('data-index'));
                moveFleetBlock(idx, 1);
                return;
            }
            const btnDup = e.target.closest('.btn-duplicate');
            if (btnDup) {
                const idx = parseInt(btnDup.getAttribute('data-index'));
                duplicateFleetBlock(idx);
                return;
            }
            const btnDel = e.target.closest('.btn-delete');
            if (btnDel) {
                const idx = parseInt(btnDel.getAttribute('data-index'));
                removeFleetBlock(idx);
                return;
            }
        });
    }

    // 5. Lineup Toolbar Actions
    if (assignAllBtn) assignAllBtn.addEventListener('click', assignCurrentEditorToAllRunners);
    if (resetBtn) resetBtn.addEventListener('click', resetFleetLineupDefaults);
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            saveFleetLineupToStorage();
            showToast("💾 Saved 7-Runner Fleet Lineup configuration!");
        });
    }

    // 6. Robust Event Delegation on 7-Runner Cards Container (Fixes Edit in Single View)
    if (runnersContainer) {
        runnersContainer.addEventListener('click', async (e) => {
            const editBtn = e.target.closest('.fleet-edit-single-btn');
            if (editBtn) {
                e.preventDefault();
                e.stopPropagation();
                const slot = parseInt(editBtn.getAttribute('data-slot'));
                await editRunnerInSingleView(slot);
                return;
            }

            const copyBtn = e.target.closest('.fleet-copy-active-btn');
            if (copyBtn) {
                e.preventDefault();
                e.stopPropagation();
                const slot = parseInt(copyBtn.getAttribute('data-slot'));
                assignCurrentEditorToRunner(slot);
                return;
            }
        });
    }

    // 7. Load default fleet show and lineup
    loadFleetLineupFromStorage().then(() => {
        renderFleetCards();
    });

    refreshFleetShowsDropdown().then(() => {
        const savedShow = localStorage.getItem('msep_active_fleet_show_id') || 'default_30s_grand_parade.json';
        loadFleetShow(savedShow);
    });
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
    selectedGroupId = null;
    resetGroupFormToDefaults();
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

    // If an animation group is selected, update the group's custom color & mode so animations illuminate in this color!
    if (selectedGroupId) {
        const activeGrp = animationGroups.find(g => g.id === selectedGroupId);
        if (activeGrp) {
            activeGrp.colorMode = 'custom';
            activeGrp.customColor = { r: clampedR, g: clampedG, b: clampedB };
            const toHex = (n) => n.toString(16).padStart(2, '0').toUpperCase();
            const hex = `#${toHex(clampedR)}${toHex(clampedG)}${toHex(clampedB)}`;
            if (activeGrp.effect === 'fireworks') {
                activeGrp.fireworkColor = hex;
                const fwSel = document.getElementById('fwColorSelect');
                if (fwSel) {
                    const match = Array.from(fwSel.options).some(o => o.value.toLowerCase() === hex.toLowerCase());
                    fwSel.value = match ? hex.toLowerCase() : 'custom';
                    const customPicker = document.getElementById('fwCustomColorPicker');
                    if (customPicker) {
                        customPicker.value = hex;
                        customPicker.style.display = match ? 'none' : 'block';
                    }
                }
            }
        }
    }

    updateLedInspectorColorInputs(clampedR, clampedG, clampedB);
    updateLedInspectorUI();
    markSingleShirtDirty();

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

function populateGroupForm(grp) {
    if (!grp) return;
    selectedGroupId = grp.id;

    const nameHub = document.getElementById('groupNameInputHub');
    const nameDoc = document.getElementById('groupNameInput');
    const effHub = document.getElementById('groupEffectSelectHub');
    const effDoc = document.getElementById('groupEffectSelect');
    const spdHub = document.getElementById('groupSpeedSliderHub');
    const spdDoc = document.getElementById('groupSpeedSlider');
    const spdValHub = document.getElementById('groupSpeedValHub');
    const spdValDoc = document.getElementById('groupSpeedVal');
    const dirHub = document.getElementById('groupDirectionSelectHub');
    const dirDoc = document.getElementById('groupDirectionSelect');
    const baseHub = document.getElementById('groupBaselineSelectHub');
    const baseDoc = document.getElementById('groupBaselineSelect');
    const phaseHub = document.getElementById('groupPhaseSliderHub');
    const phaseValHub = document.getElementById('groupPhaseValHub');
    const syncSelectHub = document.getElementById('groupSyncWithSelectHub');

    const nameVal = grp.name || '';
    const effVal = grp.effect || 'chase';
    const spdVal = grp.speedBpm || 140;
    const dirVal = String(grp.direction || 1);
    const baseVal = grp.baselineEffect || (effVal === 'fireworks' ? 'off' : 'inherit');
    const phaseVal = (grp.phaseOffsetDeg !== undefined) ? grp.phaseOffsetDeg : 0;

    if (nameHub) nameHub.value = nameVal;
    if (nameDoc) nameDoc.value = nameVal;
    if (effHub) effHub.value = effVal;
    if (effDoc) effDoc.value = effVal;
    if (spdHub) spdHub.value = spdVal;
    if (spdDoc) spdDoc.value = spdVal;
    if (spdValHub) spdValHub.textContent = `${spdVal} BPM`;
    if (spdValDoc) spdValDoc.textContent = `${spdVal} BPM`;
    if (dirHub) dirHub.value = dirVal;
    if (dirDoc) dirDoc.value = dirVal;
    if (baseHub) baseHub.value = baseVal;
    if (baseDoc) baseDoc.value = baseVal;

    if (phaseHub) phaseHub.value = phaseVal;
    if (phaseValHub) {
        let phaseLabel = `${phaseVal}°`;
        if (phaseVal === 0) phaseLabel += ' (Synced)';
        else if (phaseVal === 90) phaseLabel += ' (Quarter)';
        else if (phaseVal === 180) phaseLabel += ' (Anti-Phase)';
        else if (phaseVal === 270) phaseLabel += ' (3/4 Phase)';
        phaseValHub.textContent = phaseLabel;
    }

    if (syncSelectHub) {
        syncSelectHub.innerHTML = '<option value="">None (Independent Speed)</option>';
        for (const other of animationGroups) {
            if (other.id !== grp.id) {
                const opt = document.createElement('option');
                opt.value = other.id;
                opt.textContent = `🔗 ${other.name} (${other.speedBpm} BPM)`;
                syncSelectHub.appendChild(opt);
            }
        }
        syncSelectHub.value = grp.syncWithGroupId || '';
    }

    // Toggle Fireworks Burst Radius row if firework
    const fwRow = document.getElementById('groupFwRadiusRow');
    if (fwRow) {
        const isFw = effVal === 'fireworks';
        fwRow.style.display = isFw ? 'block' : 'none';
        if (isFw) {
            const rPct = Math.round((grp.burstRadius || 0.13) * 100);
            const gSlider = document.getElementById('groupFwRadiusSlider');
            const gVal = document.getElementById('groupFwRadiusVal');
            if (gSlider) gSlider.value = rPct;
            if (gVal) gVal.textContent = `${rPct}%`;
        }
    }

    const saveHubBtn = document.getElementById('saveSelectionGroupBtnHub');
    const applyBtn = document.getElementById('applyGroupEffectBtn');
    const updateText = `💾 Update Group "${nameVal}"`;
    const updateBg = 'linear-gradient(135deg, #1f6feb, #388bfd)';
    const updateBorder = '#388bfd';
    if (saveHubBtn) {
        saveHubBtn.innerHTML = updateText;
        saveHubBtn.style.background = updateBg;
        saveHubBtn.style.borderColor = updateBorder;
    }
    if (applyBtn) {
        applyBtn.innerHTML = updateText;
        applyBtn.style.background = updateBg;
        applyBtn.style.borderColor = updateBorder;
    }
}

function resetGroupFormToDefaults() {
    selectedGroupId = null;
    const nameHub = document.getElementById('groupNameInputHub');
    const nameDoc = document.getElementById('groupNameInput');
    const effHub = document.getElementById('groupEffectSelectHub');
    const effDoc = document.getElementById('groupEffectSelect');
    const spdHub = document.getElementById('groupSpeedSliderHub');
    const spdDoc = document.getElementById('groupSpeedSlider');
    const spdValHub = document.getElementById('groupSpeedValHub');
    const spdValDoc = document.getElementById('groupSpeedVal');
    const dirHub = document.getElementById('groupDirectionSelectHub');
    const dirDoc = document.getElementById('groupDirectionSelect');
    const baseHub = document.getElementById('groupBaselineSelectHub');
    const baseDoc = document.getElementById('groupBaselineSelect');
    const phaseHub = document.getElementById('groupPhaseSliderHub');
    const phaseValHub = document.getElementById('groupPhaseValHub');
    const syncSelectHub = document.getElementById('groupSyncWithSelectHub');

    if (nameHub) nameHub.value = '';
    if (nameDoc) nameDoc.value = '';
    if (effHub) effHub.value = 'chase';
    if (effDoc) effDoc.value = 'chase';
    if (spdHub) spdHub.value = 140;
    if (spdDoc) spdDoc.value = 140;
    if (spdValHub) spdValHub.textContent = '140 BPM';
    if (spdValDoc) spdValDoc.textContent = '140 BPM';
    if (dirHub) dirHub.value = '1';
    if (dirDoc) dirDoc.value = '1';
    if (baseHub) baseHub.value = 'inherit';
    if (baseDoc) baseDoc.value = 'inherit';
    if (phaseHub) phaseHub.value = 0;
    if (phaseValHub) phaseValHub.textContent = '0° (Synced)';
    if (syncSelectHub) {
        syncSelectHub.innerHTML = '<option value="">None (Independent Speed)</option>';
        for (const other of animationGroups) {
            const opt = document.createElement('option');
            opt.value = other.id;
            opt.textContent = `🔗 ${other.name} (${other.speedBpm} BPM)`;
            syncSelectHub.appendChild(opt);
        }
        syncSelectHub.value = '';
    }

    const fwRow = document.getElementById('groupFwRadiusRow');
    if (fwRow) fwRow.style.display = 'none';

    const saveHubBtn = document.getElementById('saveSelectionGroupBtnHub');
    const applyBtn = document.getElementById('applyGroupEffectBtn');
    const saveText = `💾 Save Selection as Group`;
    const saveBg = 'linear-gradient(135deg, #238636, #2ea043)';
    const saveBorder = '#2ea043';
    if (saveHubBtn) {
        saveHubBtn.innerHTML = saveText;
        saveHubBtn.style.background = saveBg;
        saveHubBtn.style.borderColor = saveBorder;
    }
    if (applyBtn) {
        applyBtn.innerHTML = saveText;
        applyBtn.style.background = saveBg;
        applyBtn.style.borderColor = saveBorder;
    }
}

function updateLedInspectorUI() {
    const emptyPrompt = document.getElementById('inspectorEmptyPrompt');
    const colorControls = document.getElementById('inspectorColorControls');
    const badge = document.getElementById('inspectorLedBadge');
    const numInput = document.getElementById('inspectorLedNumInput');
    const stepperRow = document.getElementById('inspectorStepperRow');
    const multiRow = document.getElementById('inspectorMultiSelectRow');
    const groupBadge = document.getElementById('groupEffectLedCountBadge');
    const inspectorSection = document.getElementById('ledInspectorSection');

    // While drawing a sequential path on shirt, keep the docked inspector completely collapsed/standby
    if (isDrawGroupMode) {
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
        const quickPrompt = document.getElementById('inspectorQuickGroupsPrompt');
        if (quickPrompt) quickPrompt.style.display = 'none';
        return;
    }

    const totalSelected = selectedLeds.size;

    if (totalSelected === 0) {
        selectedGroupId = null;
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

        // If this LED belongs to a group, populate group inputs if not already editing this group
        if (grpEntry && grpEntry.group && selectedGroupId !== grpEntry.group.id) {
            populateGroupForm(grpEntry.group);
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
            const effectSelect = document.getElementById('groupEffectSelectHub') || document.getElementById('groupEffectSelect');
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

    // Update Group Creation Hub in tabGroups & Action Buttons
    const selEmpty = document.getElementById('creationSelectEmptyText');
    const selActive = document.getElementById('creationSelectActiveText');
    const selCount = document.getElementById('creationSelectCountText');
    const selRange = document.getElementById('creationSelectRangeText');
    const saveHubBtn = document.getElementById('saveSelectionGroupBtnHub');
    const applyBtn = document.getElementById('applyGroupEffectBtn');

    let activeGrp = null;
    if (selectedGroupId) {
        activeGrp = animationGroups.find(g => g.id === selectedGroupId);
    } else {
        const nameInput = document.getElementById('groupNameInputHub') || document.getElementById('groupNameInput');
        const rawName = (nameInput?.value || '').trim();
        if (rawName) {
            activeGrp = animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase());
        }
    }

    if (totalSelected >= 2) {
        if (selEmpty) selEmpty.style.display = 'none';
        if (selActive) selActive.style.display = 'flex';
        if (selCount) selCount.textContent = `✨ ${totalSelected} LEDs Selected`;
        if (selRange) selRange.textContent = `Indices: ${formatIndexSummary(Array.from(selectedLeds))}`;

        const btnText = activeGrp ? `💾 Update Group "${activeGrp.name}"` : `💾 Save Selection as Group`;
        const btnBg = activeGrp ? 'linear-gradient(135deg, #1f6feb, #388bfd)' : 'linear-gradient(135deg, #238636, #2ea043)';
        const btnBorder = activeGrp ? '#388bfd' : '#2ea043';

        if (saveHubBtn) {
            saveHubBtn.innerHTML = btnText;
            saveHubBtn.style.background = btnBg;
            saveHubBtn.style.borderColor = btnBorder;
        }
        if (applyBtn) {
            applyBtn.innerHTML = btnText;
            applyBtn.style.background = btnBg;
            applyBtn.style.borderColor = btnBorder;
        }
    } else {
        if (selEmpty) selEmpty.style.display = 'block';
        if (selActive) selActive.style.display = 'none';
        const defaultText = activeGrp ? `💾 Update Group "${activeGrp.name}"` : `💾 Save Selection as Group`;
        const defaultBg = activeGrp ? 'linear-gradient(135deg, #1f6feb, #388bfd)' : 'linear-gradient(135deg, #238636, #2ea043)';
        const defaultBorder = activeGrp ? '#388bfd' : '#2ea043';
        if (saveHubBtn) {
            saveHubBtn.innerHTML = defaultText;
            saveHubBtn.style.background = defaultBg;
            saveHubBtn.style.borderColor = defaultBorder;
        }
        if (applyBtn) {
            applyBtn.innerHTML = defaultText;
            applyBtn.style.background = defaultBg;
            applyBtn.style.borderColor = defaultBorder;
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
    // Note: Do NOT add to selectedLeds or set selectedLed while drawing
    // so the docked inspector stays closed and does not distract the user!

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
}

function startDrawGroupMode() {
    isDrawGroupMode = true;
    if (isBoxSelectMode) {
        isBoxSelectMode = false;
        const boxBtn = document.getElementById('boxSelectBtn');
        if (boxBtn) boxBtn.classList.remove('active');
    }

    // Save pre-draw positions of LEDs so cancellation can cleanly restore them
    preDrawLedBackup = leds.map(l => ({ x: l.x, y: l.y, color: { ...l.color } }));

    drawGroupLedIndices = [];
    drawGroupPoints = [];
    selectedLeds.clear();
    selectedLed = null;
    selectedGroupId = null;

    // Explicitly collapse the docked inspector so it stays out of the way
    const inspectorSection = document.getElementById('ledInspectorSection');
    if (inspectorSection) {
        inspectorSection.classList.remove('dock-active');
        inspectorSection.classList.add('dock-empty');
    }

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
    if (preDrawLedBackup && preDrawLedBackup.length === leds.length) {
        for (let i = 0; i < leds.length; i++) {
            leds[i].x = preDrawLedBackup[i].x;
            leds[i].y = preDrawLedBackup[i].y;
            leds[i].color = { ...preDrawLedBackup[i].color };
        }
    }
    preDrawLedBackup = null;
    drawGroupLedIndices = [];
    drawGroupPoints = [];
    selectedLeds.clear();
    selectedLed = null;
    selectedGroupId = null;
    updateLedInspectorUI();
    showToast('Drawing mode cancelled. Previous LED positions restored.');
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

    if (preDrawLedBackup) {
        const preDrawSnapshot = {
            action: `Draw Group "${rawName}"`,
            timestamp: Date.now(),
            leds: JSON.parse(JSON.stringify(preDrawLedBackup)),
            animationGroups: JSON.parse(JSON.stringify(animationGroups)),
            selectedLeds: [],
            selectedLed: null,
            selectedGroupId: null,
            graphicType: typeof currentGraphicType !== 'undefined' ? currentGraphicType : 'builtin_dragon',
            customArtworkDataUrl: typeof customArtworkDataUrl !== 'undefined' ? customArtworkDataUrl : null
        };
        undoStack.push(preDrawSnapshot);
        if (undoStack.length > MAX_UNDO_HISTORY) undoStack.shift();
        redoStack = [];
        updateUndoRedoUI();
    }

    preDrawLedBackup = null;
    animationGroups.push(newGroup);

    // Check if auto-rearranging remaining LEDs is enabled
    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }

    stopDrawGroupMode();
    selectGroupLeds(newGroup.id);
    markSingleShirtDirty();

    if (autoRearrange) {
        showToast(`🎉 Saved group "${newGroup.name}" (${newGroup.ledIndices.length} LEDs) & filled graphic with remaining LEDs!`);
    } else {
        showToast(`🎉 Saved group "${newGroup.name}" with ${newGroup.ledIndices.length} sequential LEDs!`);
    }

    if (nameInput) nameInput.value = '';
}

// ----------------------------------------------------------------------------
// ANIMATION GROUP MANAGEMENT ROUTINES
// ----------------------------------------------------------------------------
function applyGroupEffectToSelection() {
    let targetGroup = null;
    if (selectedGroupId) {
        targetGroup = animationGroups.find(g => g.id === selectedGroupId);
    }

    if (!targetGroup && selectedLeds.size < 2) {
        showToast("⚠️ Please select at least 2 LEDs to create or update an animation group!", "warning");
        return;
    }

    const nameInput = document.getElementById('groupNameInputHub') || document.getElementById('groupNameInput');
    const effectSelect = document.getElementById('groupEffectSelectHub') || document.getElementById('groupEffectSelect');
    const speedSlider = document.getElementById('groupSpeedSliderHub') || document.getElementById('groupSpeedSlider');
    const dirSelect = document.getElementById('groupDirectionSelectHub') || document.getElementById('groupDirectionSelect');
    const baselineSelect = document.getElementById('groupBaselineSelectHub') || document.getElementById('groupBaselineSelect');
    const phaseSlider = document.getElementById('groupPhaseSliderHub');
    const syncSelect = document.getElementById('groupSyncWithSelectHub');

    const rawName = (nameInput?.value || '').trim() || (targetGroup ? targetGroup.name : `Zone (${selectedLeds.size} LEDs)`);
    const effect = effectSelect?.value || 'chase';
    const speedBpm = parseInt(speedSlider?.value || '140', 10);
    const direction = parseInt(dirSelect?.value || '1', 10);
    const baselineEffect = baselineSelect?.value || (effect === 'fireworks' ? 'off' : 'inherit');
    const phaseOffsetDeg = parseInt(phaseSlider?.value || '0', 10);
    const syncWithGroupId = syncSelect?.value || null;

    if (!targetGroup && rawName) {
        targetGroup = animationGroups.find(g => g.name.toLowerCase() === rawName.toLowerCase());
    }

    const isNew = !targetGroup;

    recordHistory(isNew ? `Create Group "${rawName}"` : `Update Group "${rawName}"`);

    if (targetGroup) {
        targetGroup.name = rawName;
        targetGroup.effect = effect;
        targetGroup.speedBpm = speedBpm;
        targetGroup.direction = direction;
        targetGroup.baselineEffect = baselineEffect;
        targetGroup.phaseOffsetDeg = phaseOffsetDeg;
        targetGroup.syncWithGroupId = syncWithGroupId;
        if (selectedLeds.size >= 2) {
            targetGroup.ledIndices = Array.from(selectedLeds).sort((a, b) => a - b);
        }
        selectedGroupId = targetGroup.id;
    } else {
        const sortedIndices = Array.from(selectedLeds).sort((a, b) => a - b);
        targetGroup = {
            id: 'grp_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
            name: rawName,
            ledIndices: sortedIndices,
            effect: effect,
            speedBpm: speedBpm,
            direction: direction,
            phaseOffsetDeg: phaseOffsetDeg,
            syncWithGroupId: syncWithGroupId,
            width: 3,
            colorMode: 'original',
            baselineEffect: baselineEffect
        };
        animationGroups.push(targetGroup);
        selectedGroupId = targetGroup.id;
    }

    if (effect === 'fireworks') {
        const count = targetGroup.ledIndices.length;
        const inferredRays = (count % 5 === 0) ? 5 : ((count % 4 === 0) ? 4 : ((count % 6 === 0) ? 6 : ((count % 3 === 0) ? 3 : 5)));
        targetGroup.fireworkRays = targetGroup.fireworkRays || inferredRays;
        targetGroup.fireworkLedsPerRay = targetGroup.fireworkLedsPerRay || Math.round(count / targetGroup.fireworkRays);
        targetGroup.wiringMode = targetGroup.wiringMode || 'serpentine';
    }

    rebuildLedGroupMap();
    renderActiveGroupsList();
    populateGroupForm(targetGroup);
    markSingleShirtDirty();

    if (isNew) {
        showToast(`🎉 Saved new group "${targetGroup.name}" (${targetGroup.ledIndices.length} LEDs)!`);
    } else {
        showToast(`✅ Saved changes for group "${targetGroup.name}"!`);
    }
}

function removeGroupEffectFromSelection() {
    if (selectedLeds.size === 0) return;

    recordHistory('Remove Group Effects');

    let removedCount = 0;
    for (const idx of selectedLeds) {
        for (let g = animationGroups.length - 1; g >= 0; g--) {
            const grp = animationGroups[g];
            const p = grp.ledIndices.indexOf(idx);
            if (p !== -1) {
                grp.ledIndices.splice(p, 1);
                removedCount++;
                if (grp.ledIndices.length === 0) {
                    if (selectedGroupId === grp.id) resetGroupFormToDefaults();
                    animationGroups.splice(g, 1);
                }
            }
        }
    }

    rebuildLedGroupMap();
    renderActiveGroupsList();
    updateLedInspectorUI();
    markSingleShirtDirty();
    showToast(`🗑️ Removed group effects from ${removedCount} LEDs.`);
}

function deleteGroup(groupId) {
    const idx = animationGroups.findIndex(g => g.id === groupId);
    if (idx !== -1) {
        const name = animationGroups[idx].name;
        recordHistory(`Delete Group "${name}"`);
        animationGroups.splice(idx, 1);
        if (selectedGroupId === groupId) {
            resetGroupFormToDefaults();
        }
        rebuildLedGroupMap();
        renderActiveGroupsList();
        updateLedInspectorUI();
        markSingleShirtDirty();
        showToast(`🗑️ Deleted animation group "${name}"`);
    }
}

function selectGroupLeds(groupId) {
    const grp = animationGroups.find(g => g.id === groupId);
    if (!grp) return;

    const arr = Array.isArray(grp.ledIndices) ? grp.ledIndices : (Array.isArray(grp.indices) ? grp.indices : []);
    grp.ledIndices = arr;
    grp.indices = arr;

    selectedGroupId = grp.id;

    selectedLeds.clear();
    for (const idx of arr) {
        if (idx < leds.length) selectedLeds.add(idx);
    }
    selectedLed = arr[0] || null;

    // Switch Hub mode to 'select' so From Selection panel is visible
    switchGroupCreationMode('select');

    // Populate all form fields in both Hub and docked inspector
    populateGroupForm(grp);

    updateLedInspectorUI();
    renderActiveGroupsList();
    showToast(`🎯 Selected & Editing group "${grp.name}" (${selectedLeds.size} LEDs)!`);
}

// ----------------------------------------------------------------------------
// GROUP TRANSFORMATIONS & CLIPBOARD ROUTINES
// ----------------------------------------------------------------------------

function sampleColorAtNormCoord(normX, normY) {
    if (!leds || leds.length === 0) return { r: 255, g: 255, b: 255 };

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

    const relX = Math.max(0, Math.min(1, (normX - gb.normX) / gb.normW));
    const relY = Math.max(0, Math.min(1, (normY - gb.normY) / gb.normH));

    const px = Math.floor(relX * targetW);
    const py = Math.floor(relY * targetH);
    if (px < 0 || px >= targetW || py < 0 || py >= targetH) return { r: 255, g: 255, b: 255 };

    const p = offCtx.getImageData(px, py, 1, 1).data;
    let col = { r: p[0], g: p[1], b: p[2] };
    if (p[3] < 30) {
        col = { r: 255, g: 255, b: 255 };
    }
    if (typeof boostLedVibrancy === 'function') {
        col = boostLedVibrancy(col.r, col.g, col.b, relX, relY);
    }
    return col;
}

function copyGroup(groupId) {
    const targetId = groupId || selectedGroupId;
    const grp = animationGroups.find(g => g.id === targetId);
    if (!grp || !grp.ledIndices || grp.ledIndices.length === 0) {
        showToast('⚠️ Please select an animation group to copy!', 'warning');
        return;
    }

    const normPositions = grp.ledIndices.map(idx => {
        const l = leds[idx] || { x: 0.5, y: 0.35 };
        return {
            x: l.x,
            y: l.y
        };
    });

    copiedGroupClipboard = {
        name: grp.name,
        effect: grp.effect,
        speedBpm: grp.speedBpm,
        direction: grp.direction,
        width: grp.width,
        colorMode: grp.colorMode,
        baselineEffect: grp.baselineEffect,
        fireworkRays: grp.fireworkRays,
        fireworkLedsPerRay: grp.fireworkLedsPerRay,
        burstRadius: grp.burstRadius,
        wiringMode: grp.wiringMode,
        normPositions: normPositions,
        relPositions: normPositions,
        sourceSlot: activeSingleShirtRunnerSlot
    };

    saveGroupClipboardToStorage();
    showToast(`📋 Copied animation group "${grp.name}" (${normPositions.length} LEDs) to clipboard!`);
}

function pasteGroup() {
    if (!copiedGroupClipboard || (!Array.isArray(copiedGroupClipboard.normPositions) && !Array.isArray(copiedGroupClipboard.relPositions))) {
        loadGroupClipboardFromStorage();
    }
    const positionsList = (copiedGroupClipboard && Array.isArray(copiedGroupClipboard.normPositions))
        ? copiedGroupClipboard.normPositions
        : (copiedGroupClipboard ? copiedGroupClipboard.relPositions : null);

    if (!copiedGroupClipboard || !Array.isArray(positionsList) || positionsList.length === 0) {
        showToast('⚠️ Clipboard is empty! Copy an animation group first.', 'warning');
        return;
    }

    const totalLeds = leds ? leds.length : 100;
    const assignedSet = new Set();
    animationGroups.forEach(g => {
        (g.ledIndices || []).forEach(idx => {
            if (idx < totalLeds) assignedSet.add(idx);
        });
    });

    const unassignedIndices = [];
    for (let i = 0; i < totalLeds; i++) {
        if (!assignedSet.has(i)) unassignedIndices.push(i);
    }

    const reqCount = positionsList.length;
    if (unassignedIndices.length < reqCount) {
        showToast(`⚠️ Target shirt only has ${unassignedIndices.length} unused LEDs available, but copied group requires ${reqCount} LEDs. Please delete or reduce existing groups first.`, 'warning');
        return;
    }

    recordHistory(`Paste Group "${copiedGroupClipboard.name}"`);

    const allocatedIndices = unassignedIndices.slice(0, reqCount);
    const gb = getGraphicChestBounds();
    const isSameShirt = (copiedGroupClipboard.sourceSlot === activeSingleShirtRunnerSlot);
    const offsetX = isSameShirt ? 0.03 : 0.0;
    const offsetY = isSameShirt ? 0.03 : 0.0;

    for (let i = 0; i < reqCount; i++) {
        const ledIdx = allocatedIndices[i];
        const pos = positionsList[i];

        let rawX = (pos.x !== undefined) ? pos.x : (gb.normX + pos.relX * gb.normW);
        let rawY = (pos.y !== undefined) ? pos.y : (gb.normY + pos.relY * gb.normH);

        const normX = Math.max(0.04, Math.min(0.96, rawX + offsetX));
        const normY = Math.max(0.04, Math.min(0.96, rawY + offsetY));

        leds[ledIdx].x = parseFloat(normX.toFixed(4));
        leds[ledIdx].y = parseFloat(normY.toFixed(4));
        leds[ledIdx].color = sampleColorAtNormCoord(normX, normY);
    }

    const pastedName = isSameShirt ? `${copiedGroupClipboard.name} (Copy)` : copiedGroupClipboard.name;

    const newGroup = {
        id: 'grp_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
        name: pastedName,
        ledIndices: [...allocatedIndices],
        effect: copiedGroupClipboard.effect || 'chase',
        speedBpm: copiedGroupClipboard.speedBpm || 140,
        direction: copiedGroupClipboard.direction || 1,
        width: copiedGroupClipboard.width || 3,
        colorMode: copiedGroupClipboard.colorMode || 'original',
        baselineEffect: copiedGroupClipboard.baselineEffect || 'inherit',
        fireworkRays: copiedGroupClipboard.fireworkRays,
        fireworkLedsPerRay: copiedGroupClipboard.fireworkLedsPerRay,
        burstRadius: copiedGroupClipboard.burstRadius,
        wiringMode: copiedGroupClipboard.wiringMode
    };

    animationGroups.push(newGroup);

    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }

    selectGroupLeds(newGroup.id);
    markSingleShirtDirty();
    showToast(`🎉 Pasted group "${newGroup.name}" (${reqCount} LEDs) from unused pool!`);
}

function getGroupCentroid(grp) {
    if (!grp || !grp.ledIndices || grp.ledIndices.length === 0) return null;
    let sumX = 0, sumY = 0;
    let validCount = 0;
    grp.ledIndices.forEach(idx => {
        if (leds[idx]) {
            sumX += leds[idx].x;
            sumY += leds[idx].y;
            validCount++;
        }
    });
    if (validCount === 0) return null;
    return { cx: sumX / validCount, cy: sumY / validCount };
}

function applyRigidGroupTransform(grp, transformFn) {
    if (!grp || !grp.ledIndices || !grp.ledIndices.length) return false;
    const c = getGroupCentroid(grp);
    if (!c) return false;

    for (let i = 0; i < grp.ledIndices.length; i++) {
        const idx = grp.ledIndices[i];
        if (!leds[idx]) continue;
        const off = transformFn(leds[idx].x - c.cx, leds[idx].y - c.cy, c);
        const nx = Math.max(0.01, Math.min(0.99, parseFloat((c.cx + off.rx).toFixed(4))));
        const ny = Math.max(0.01, Math.min(0.99, parseFloat((c.cy + off.ry).toFixed(4))));

        leds[idx].x = nx;
        leds[idx].y = ny;
        leds[idx].color = sampleColorAtNormCoord(nx, ny);
    }
    return true;
}

function rotateGroup(groupId, angleDegrees = 90) {
    const targetId = groupId || selectedGroupId;
    const grp = animationGroups.find(g => g.id === targetId);
    if (!grp || !grp.ledIndices.length) {
        showToast('⚠️ Select an animation group to rotate!', 'warning');
        return;
    }

    recordHistory(`Rotate "${grp.name}" ${angleDegrees}°`);

    const rad = (angleDegrees * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);

    applyRigidGroupTransform(grp, (dx, dy) => {
        const dxc = dx;
        const dyc = dy * 1.25;

        const rxc = dxc * cos - dyc * sin;
        const ryc = dxc * sin + dyc * cos;

        return {
            rx: rxc,
            ry: ryc / 1.25
        };
    });

    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }
    updateLedInspectorUI();
    markSingleShirtDirty();
    showToast(`🔄 Rotated "${grp.name}" by ${angleDegrees}°!`);
}

function flipGroupHorizontal(groupId) {
    const targetId = groupId || selectedGroupId;
    const grp = animationGroups.find(g => g.id === targetId);
    if (!grp || !grp.ledIndices.length) {
        showToast('⚠️ Select an animation group to flip!', 'warning');
        return;
    }

    recordHistory(`Flip "${grp.name}" Horizontally`);

    applyRigidGroupTransform(grp, (dx, dy) => ({
        rx: -dx,
        ry: dy
    }));

    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }
    updateLedInspectorUI();
    markSingleShirtDirty();
    showToast(`↔️ Flipped "${grp.name}" horizontally!`);
}

function flipGroupVertical(groupId) {
    const targetId = groupId || selectedGroupId;
    const grp = animationGroups.find(g => g.id === targetId);
    if (!grp || !grp.ledIndices.length) {
        showToast('⚠️ Select an animation group to flip!', 'warning');
        return;
    }

    recordHistory(`Flip "${grp.name}" Vertically`);

    applyRigidGroupTransform(grp, (dx, dy) => ({
        rx: dx,
        ry: -dy
    }));

    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }
    updateLedInspectorUI();
    markSingleShirtDirty();
    showToast(`↕️ Flipped "${grp.name}" vertically!`);
}

function scaleGroup(groupId, scaleFactor = 1.10) {
    const targetId = groupId || selectedGroupId;
    const grp = animationGroups.find(g => g.id === targetId);
    if (!grp || !grp.ledIndices.length) {
        showToast('⚠️ Select an animation group to scale!', 'warning');
        return;
    }

    recordHistory(`Scale Spacing "${grp.name}" (${Math.round(scaleFactor * 100)}%)`);

    applyRigidGroupTransform(grp, (dx, dy) => ({
        rx: dx * scaleFactor,
        ry: dy * scaleFactor
    }));

    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }
    updateLedInspectorUI();
    markSingleShirtDirty();
    showToast(`🔍 Scaled LED spacing for "${grp.name}" (${Math.round(scaleFactor * 100)}%)!`);
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
        const arr = Array.isArray(g.ledIndices) ? g.ledIndices : (Array.isArray(g.indices) ? g.indices : []);
        g.ledIndices = arr;
        g.indices = arr;
        arr.forEach(idx => {
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

    const fxUngroupedBadge = document.getElementById('fxUngroupedCountBadge');
    if (fxUngroupedBadge) {
        fxUngroupedBadge.textContent = `${unassignedCount} of ${totalCostumeLeds} LEDs (${unassignedPct}% Baseline)`;
    }

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
        const arr = Array.isArray(grp.ledIndices) ? grp.ledIndices : (Array.isArray(grp.indices) ? grp.indices : []);
        grp.ledIndices = arr;
        grp.indices = arr;

        const card = document.createElement('div');
        card.className = 'group-card';
        card.setAttribute('data-group-id', grp.id);

        const isFullySelected = selectedLeds.size > 0 &&
            arr.length > 0 &&
            arr.every(idx => selectedLeds.has(idx));
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

        let phasePillHtml = '';
        if (grp.syncWithGroupId) {
            const parentGrp = animationGroups.find(g => g.id === grp.syncWithGroupId);
            const pName = parentGrp ? parentGrp.name : 'Master';
            const deg = grp.phaseOffsetDeg || 0;
            phasePillHtml = `<span class="group-pill" style="background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid rgba(88, 166, 255, 0.4);" title="Synced to ${pName}">🔗 ${pName} (+${deg}°)</span>`;
        } else if (grp.phaseOffsetDeg && grp.phaseOffsetDeg > 0) {
            let pDesc = `${grp.phaseOffsetDeg}°`;
            if (grp.phaseOffsetDeg === 180) pDesc += ' Anti';
            else if (grp.phaseOffsetDeg === 90) pDesc += ' Quad';
            phasePillHtml = `<span class="group-pill" style="background: rgba(163, 113, 247, 0.15); color: #d2a8ff; border: 1px solid rgba(163, 113, 247, 0.4);">🔄 Phase: ${pDesc}</span>`;
        }

        card.innerHTML = `
            <div class="group-card-header">
                <div class="group-card-title-wrap">
                    <span class="group-card-icon">${icon}</span>
                    <span class="group-card-name" title="${grp.name}">${grp.name}</span>
                </div>
                <span class="group-card-leds-badge">${arr.length} LEDs</span>
            </div>
            <div class="group-card-badges">
                <span class="group-pill group-pill-effect">${label} @ ${grp.speedBpm} BPM</span>
                ${extraPillHtml}
                ${phasePillHtml}
                <span class="group-pill group-pill-baseline">Idle: ${baselineLabel}</span>
                <span class="group-pill" style="background: #21262d; color: #8b949e; border: 1px solid #30363d;" title="LED indices: ${arr.join(', ')}">LEDs: ${formatIndexSummary(arr)}</span>
            </div>
            <div class="group-card-actions" style="display: flex; gap: 4px; flex-wrap: wrap;">
                <button type="button" class="action-btn select-grp-btn" style="flex: 1.2; font-weight: 600;" title="Select and inspect all LEDs in this group">
                    🎯 Select
                </button>
                <button type="button" class="action-btn copy-card-grp-btn" style="font-weight: 600; color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);" title="Copy group to clipboard (Ctrl+C / Cmd+C)">
                    📋 Copy
                </button>
                <button type="button" class="action-btn rotate-card-grp-btn" style="font-weight: 600;" title="Rotate group 90° Clockwise">
                    🔄 90°
                </button>
                <button type="button" class="action-btn add-cue-grp-btn" style="font-weight: 600; color: #58a6ff; border-color: rgba(56, 139, 253, 0.4);" title="Add a Show Cue for this group to the Master Timeline">
                    ➕ Cue
                </button>
                <button type="button" class="action-btn del-grp-btn" style="color: #ff7b72;" title="Delete group">
                    🗑️
                </button>
            </div>
        `;

        card.addEventListener('click', (e) => {
            if (e.target.closest('.del-grp-btn') || e.target.closest('.add-cue-grp-btn') || e.target.closest('.copy-card-grp-btn') || e.target.closest('.rotate-card-grp-btn')) return;
            selectGroupLeds(grp.id);
        });

        const copyCardBtn = card.querySelector('.copy-card-grp-btn');
        if (copyCardBtn) {
            copyCardBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                copyGroup(grp.id);
            });
        }

        const rotateCardBtn = card.querySelector('.rotate-card-grp-btn');
        if (rotateCardBtn) {
            rotateCardBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                rotateGroup(grp.id, 90);
            });
        }

        const addCueBtn = card.querySelector('.add-cue-grp-btn');
        if (addCueBtn) {
            addCueBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                addCue({
                    targetType: 'group',
                    groupId: grp.id,
                    groupName: grp.name,
                    effect: grp.effect || 'chase',
                    speedBpm: grp.speedBpm || 140
                });
                if (typeof switchSidebarTab === 'function') {
                    switchSidebarTab('tabDirector');
                }
            });
        }

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
        if (currentView === 'single') {
            updateTimelineScrubberUI();
        }
    }
}

function updateTimelineScrubberUI() {
    const scrubber = document.getElementById('timelineScrubber');
    const currTimeElem = document.getElementById('timelineCurrentTime');
    const totalTimeElem = document.getElementById('timelineTotalTime');
    const needle = document.getElementById('timelinePlayheadNeedle');
    const layersBadge = document.getElementById('timelineActiveLayersBadge');
    const cuesBadge = document.getElementById('timelineActiveCuesBadge');
    const modeBtn = document.getElementById('timelineModeToggle');
    const loopBtn = document.getElementById('timelineLoopToggle');
    const labelCol = document.querySelector('.timeline-track-label-col span');

    if (currentView === 'fleet') {
        const totalDur = (activeFleetShow && activeFleetShow.loopDuration) || 30.0;
        if (scrubber) {
            scrubber.max = totalDur;
            scrubber.value = fleetShowElapsedSec;
        }
        if (currTimeElem) currTimeElem.textContent = `${fleetShowElapsedSec.toFixed(1)}s`;
        if (totalTimeElem) totalTimeElem.textContent = `${totalDur.toFixed(1)}s`;
        if (needle) {
            const pct = Math.max(0, Math.min(1, fleetShowElapsedSec / totalDur));
            needle.style.left = `calc(115px + (100% - 115px) * ${pct})`;
        }
        if (labelCol) labelCol.textContent = 'FLEET SHOW';
        if (layersBadge) {
            const blockCount = (activeFleetShow && activeFleetShow.blocks) ? activeFleetShow.blocks.length : 0;
            layersBadge.textContent = `👑 Fleet Show (${totalDur.toFixed(0)}s)`;
        }
        if (cuesBadge) {
            const activeInfo = getActiveFleetBlock(fleetShowElapsedSec);
            const activeBlock = activeInfo ? activeInfo.block : null;
            if (fleetShowActive && activeBlock) {
                cuesBadge.textContent = `Block #${activeInfo.index + 1}: ${activeBlock.name} (${activeBlock.startTime.toFixed(1)}s – ${(activeBlock.startTime + activeBlock.duration).toFixed(1)}s)`;
                cuesBadge.style.color = '#ffc107';
            } else {
                cuesBadge.textContent = `Ready (${totalDur.toFixed(0)}s Standby)`;
                cuesBadge.style.color = '#8b949e';
            }
        }
        if (modeBtn) {
            modeBtn.style.display = '';
            modeBtn.textContent = fleetShowActive ? '👑 Fleet Show: ON' : '⚡ Baseline: ON';
            modeBtn.title = 'Click to activate or stop 30s synchronized fleet choreography';
            modeBtn.classList.toggle('active', fleetShowActive);
        }
        if (loopBtn) {
            loopBtn.style.display = 'none';
        }
        return;
    }

    // Single Shirt View:
    if (labelCol) labelCol.textContent = 'TIMELINE';
    if (loopBtn) {
        loopBtn.style.display = '';
        loopBtn.classList.toggle('active', sequenceLoop);
    }
    if (modeBtn) {
        modeBtn.style.display = 'none';
    }
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
            cuesBadge.textContent = sequenceCues.length === 0 ? 'Ambient Program (No Cues)' : 'Ambient Fallback (Between Cues)';
            cuesBadge.style.color = '#3fb950';
        } else {
            cuesBadge.textContent = `Active (${activeCueNames.length}): ${activeCueNames.join(' + ')}`;
            cuesBadge.style.color = '#58a6ff';
        }
    }
}

function updateTimelinePlayBtn() {
    const btn = document.getElementById('timelinePlayBtn');
    if (!btn) return;

    if (currentView === 'fleet') {
        btn.textContent = fleetShowActive ? '⏸' : '👑';
        btn.title = fleetShowActive ? 'Stop Fleet Show (Spacebar)' : 'Activate Fleet Show (Spacebar)';
    } else {
        btn.textContent = sequencePlaying ? '⏸' : '▶';
        btn.title = sequencePlaying ? 'Pause Sequence (Spacebar)' : 'Play Sequence (Spacebar)';
    }
}

function togglePlayPause() {
    sequencePlaying = !sequencePlaying;
    sequenceMode = true;
    lastTimelineFrameTime = performance.now();
    updateTimelinePlayBtn();
    showToast(sequencePlaying ? `▶ Playing master timeline (${formatTimelineTime(sequenceTime)})` : '⏸ Paused master timeline');
}

function stopSequence() {
    sequencePlaying = false;
    sequenceTime = 0.0;
    updateTimelinePlayBtn();
    updateTimelineScrubberUI();
    showToast('⏹ Rewound sequence to 0:00');
}

function toggleSequenceMode(forceState) {
    sequenceMode = true;
    const badge = document.getElementById('cueDirectorBadge');
    if (badge) {
        badge.textContent = sequenceCues.length === 0 ? '0 Cues (Ambient Fallback)' : `${sequenceCues.length} Cue${sequenceCues.length !== 1 ? 's' : ''}`;
        badge.style.color = sequenceCues.length === 0 ? 'var(--accent-cyan)' : '#3fb950';
    }
}

// ============================================================================
// INTERACTIVE FLEET SHOW TIMELINE ENGINE (DRAG-TO-STRETCH, TRIM & REORDER)
// ============================================================================
let selectedFleetBlockIdx = null;
let activeTimelineDrag = null;

function getFleetBlockDirectionBadge(bType) {
    switch (bType) {
        case 'wave_forward': return '1 ➔ 7';
        case 'wave_reverse': return '7 ➔ 1';
        case 'center_burst': return '4 ➔ 1&7';
        case 'converge_center': return '1&7 ➔ 4';
        case 'baton_chase': return '1 ➔ 7';
        case 'ping_pong_wave': return '1 ⇆ 7';
        case 'color_collision': return '1&7 ➔ 4 ➔ 1&7';
        case 'cross_dissolve_chase': return '1 ➔ 7';
        case 'ripple_echo': return '4 ➔ 1&7';
        case 'sparkle_cascade': return '1 ➔ 7';
        case 'wig_wag': return '1,3,5,7 ⇄ 2,4,6';
        case 'fleet_pulse': return 'All 7';
        case 'sparkle_storm': return '✨ All';
        case 'color_wash_chase': return '1 ➔ 7';
        case 'rainbow_sweep': return '🌈 360°';
        case 'strobe_all': return '⚡ All';
        case 'grand_finale': return '🎆 Finale';
        case 'shimmer_drift': return '🌌 Drift';
        case 'blackout': return '🌑 Off';
        default: return '';
    }
}

function getFleetBlockCategoryClass(bType) {
    if (bType === 'blackout') return 'fleet-block-cat-blackout';
    const def = FLEET_BLOCK_DEFS[bType];
    const cat = def?.category || 'waves';
    if (cat === 'waves') return 'fleet-block-cat-waves';
    if (cat === 'sync') return 'fleet-block-cat-sync';
    if (cat === 'theatrical') return 'fleet-block-cat-theatrical';
    return 'fleet-block-cat-waves';
}

function highlightSidebarFleetBlockCard(idx) {
    document.querySelectorAll('.fleet-block-card').forEach(c => c.style.outline = 'none');
    const card = document.querySelector(`.fleet-block-card[data-index="${idx}"]`);
    if (card) {
        card.style.outline = '2px solid #58a6ff';
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Global mousemove & mouseup listeners for drag-to-stretch and reorder
window.addEventListener('mousemove', (e) => {
    if (!activeTimelineDrag) return;
    const { type, blockIdx, startClientX, initialDuration, initialPrevDuration, trackRect, totalDur } = activeTimelineDrag;
    const blocks = activeFleetShow?.blocks;
    if (!blocks || !blocks[blockIdx]) return;
    const blk = blocks[blockIdx];
    const pixelsPerSec = trackRect.width / totalDur;
    const deltaX = e.clientX - startClientX;
    const deltaSec = deltaX / pixelsPerSec;
    if (Math.abs(deltaX) > 3) activeTimelineDrag.hasMoved = true;

    const tooltip = document.getElementById('timelineFloatingTooltip');

    if (type === 'resize-right') {
        const newDuration = Math.max(0.2, Math.round((initialDuration + deltaSec) * 10) / 10);
        blk.duration = newDuration;
        recalculateFleetBlockStartTimes();

        if (tooltip) {
            tooltip.style.display = 'block';
            tooltip.style.left = `${e.clientX}px`;
            tooltip.style.top = `${e.clientY - 12}px`;
            tooltip.innerHTML = `⏱️ <strong>${blk.name}</strong>: ${newDuration.toFixed(1)}s (Ends at ${(blk.startTime + newDuration).toFixed(1)}s)`;
        }
        renderFleetShowTimelineLayers();
    } else if (type === 'resize-left') {
        if (blockIdx > 0) {
            const prevBlk = blocks[blockIdx - 1];
            const totalPairDur = initialPrevDuration + initialDuration;
            const newPrevDur = Math.max(0.2, Math.min(totalPairDur - 0.2, Math.round((initialPrevDuration + deltaSec) * 10) / 10));
            const newDur = Math.round((totalPairDur - newPrevDur) * 10) / 10;
            prevBlk.duration = newPrevDur;
            blk.duration = newDur;
            recalculateFleetBlockStartTimes();

            if (tooltip) {
                tooltip.style.display = 'block';
                tooltip.style.left = `${e.clientX}px`;
                tooltip.style.top = `${e.clientY - 12}px`;
                tooltip.innerHTML = `⏱️ <strong>Trim:</strong> ${prevBlk.name} (${newPrevDur.toFixed(1)}s) ➔ ${blk.name} (${newDur.toFixed(1)}s)`;
            }
            renderFleetShowTimelineLayers();
        }
    } else if (type === 'move') {
        const cursorTime = Math.max(0, Math.min(totalDur, (e.clientX - trackRect.left) / pixelsPerSec));
        let targetIdx = blocks.length - 1;
        for (let i = 0; i < blocks.length; i++) {
            const b = blocks[i];
            const mid = b.startTime + (b.duration / 2.0);
            if (cursorTime < mid) {
                targetIdx = i;
                break;
            }
        }
        activeTimelineDrag.targetIdx = targetIdx;

        if (tooltip) {
            tooltip.style.display = 'block';
            tooltip.style.left = `${e.clientX}px`;
            tooltip.style.top = `${e.clientY - 12}px`;
            tooltip.innerHTML = `🔀 Move <strong>${blk.name}</strong> to position #${targetIdx + 1} of ${blocks.length}`;
        }

        let dropIndicator = document.getElementById('fleetTimelineDropIndicator');
        const track = document.querySelector('.timeline-layer-track');
        if (track) {
            if (!dropIndicator) {
                dropIndicator = document.createElement('div');
                dropIndicator.id = 'fleetTimelineDropIndicator';
                dropIndicator.className = 'fleet-timeline-drop-indicator';
                track.appendChild(dropIndicator);
            }
            const targetBlock = blocks[targetIdx];
            const targetLeftPct = ((targetBlock?.startTime || 0) / totalDur) * 100;
            dropIndicator.style.left = `${targetLeftPct}%`;
            dropIndicator.style.display = 'block';
        }
        renderFleetShowTimelineLayers();
    }
});

window.addEventListener('mouseup', () => {
    if (!activeTimelineDrag) return;
    const { type, blockIdx, hasMoved, targetIdx } = activeTimelineDrag;
    const blocks = activeFleetShow?.blocks;
    const blk = blocks && blocks[blockIdx];

    const tooltip = document.getElementById('timelineFloatingTooltip');
    if (tooltip) tooltip.style.display = 'none';

    const dropIndicator = document.getElementById('fleetTimelineDropIndicator');
    if (dropIndicator) dropIndicator.remove();

    if (type === 'move' && hasMoved && typeof targetIdx === 'number' && targetIdx !== blockIdx) {
        const [moved] = activeFleetShow.blocks.splice(blockIdx, 1);
        activeFleetShow.blocks.splice(targetIdx, 0, moved);
        recalculateFleetBlockStartTimes();
        selectedFleetBlockIdx = targetIdx;
        showToast(`🔀 Reordered "${moved.name}" to position #${targetIdx + 1}`);
    } else if (type === 'resize-right' || type === 'resize-left') {
        if (blk) showToast(`⏱️ Updated "${blk.name}" duration to ${blk.duration.toFixed(1)}s`);
    } else if (type === 'move' && !hasMoved && blk) {
        selectedFleetBlockIdx = blockIdx;
        fleetShowElapsedSec = blk.startTime;
        updateFleetShowUI();
        highlightSidebarFleetBlockCard(blockIdx);
    }

    activeTimelineDrag = null;
    renderFleetBlocksEditor();
    updateFleetShowUI();
    renderFleetShowTimelineLayers();
});

// Render 7-Shirt Fleet Show choreography blocks along the master timeline
function renderFleetShowTimelineLayers() {
    const container = document.getElementById('timelineLayersContainer');
    const marksContainer = document.getElementById('timelineRulerMarks');
    const labelCol = document.querySelector('.timeline-track-label-col span');
    if (!container) return;

    if (labelCol) labelCol.textContent = 'FLEET SHOW';

    if (!activeFleetShow) {
        container.innerHTML = `
            <div style="font-size: 11px; color: var(--text-muted); font-style: italic; padding: 6px 12px; text-align: center; border: 1px dashed #30363d; border-radius: 4px;">
                Loading Fleet Show Choreography...
            </div>
        `;
        updateTimelineScrubberUI();
        return;
    }

    const totalDur = activeFleetShow.loopDuration || 30.0;

    // 1. Render Dynamic Ruler Marks
    if (marksContainer) {
        marksContainer.innerHTML = '';
        const tickCount = 6;
        for (let i = 0; i <= tickCount; i++) {
            const t = (totalDur * i) / tickCount;
            const span = document.createElement('span');
            span.className = 'ruler-tick';
            span.textContent = `${t.toFixed(1)}s`;
            marksContainer.appendChild(span);
        }
    }

    container.innerHTML = '';

    const blocks = activeFleetShow.blocks || [];
    if (blocks.length === 0) {
        container.innerHTML = `
            <div style="font-size: 11px; color: var(--text-muted); font-style: italic; padding: 6px 12px; text-align: center; border: 1px dashed #30363d; border-radius: 4px;">
                No fleet choreography blocks scheduled. Use the Fleet tab to add blocks.
            </div>
        `;
        updateTimelineScrubberUI();
        return;
    }

    // 2. Render Choreography Track Row
    const row = document.createElement('div');
    row.className = 'timeline-layer-row';
    row.style.minHeight = '32px';

    const label = document.createElement('div');
    label.className = 'timeline-layer-label';
    label.style.minHeight = '32px';
    label.style.display = 'flex';
    label.style.alignItems = 'center';
    label.style.justifyContent = 'space-between';
    label.innerHTML = `
        <span class="timeline-layer-name" title="7-Shirt Synchronized Fleet Show Choreography" style="font-weight: 600; color: #ffc107; font-size: 11px;">👑 Fleet Show</span>
        <span class="timeline-layer-badge" style="background: rgba(255, 193, 7, 0.2); color: #ffc107; font-size: 9px; padding: 1px 4px; border-radius: 8px;">${blocks.length}</span>
    `;

    const track = document.createElement('div');
    track.className = 'timeline-layer-track';
    track.style.minHeight = '32px';

    track.addEventListener('click', (e) => {
        if (activeTimelineDrag && activeTimelineDrag.hasMoved) return;
        const rect = track.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const pct = Math.max(0, Math.min(1, clickX / rect.width));
        fleetShowElapsedSec = pct * totalDur;
        updateFleetShowUI();
    });

    const activeInfo = getActiveFleetBlock(fleetShowElapsedSec);

    blocks.forEach((blk, idx) => {
        const def = FLEET_BLOCK_DEFS[blk.type] || { icon: "✨", name: blk.name };
        const leftPct = ((blk.startTime || 0) / totalDur) * 100;
        const widthPct = Math.max(1.8, ((blk.duration || 1.0) / totalDur) * 100);
        const catClass = getFleetBlockCategoryClass(blk.type);
        const dirBadge = getFleetBlockDirectionBadge(blk.type);

        const blockElem = document.createElement('div');
        blockElem.className = `fleet-timeline-block ${catClass}`;
        blockElem.setAttribute('data-fleet-block-idx', idx);

        if (fleetShowActive && activeInfo && activeInfo.index === idx) {
            blockElem.classList.add('active');
        }
        if (selectedFleetBlockIdx === idx) {
            blockElem.classList.add('selected');
        }
        if (activeTimelineDrag && activeTimelineDrag.blockIdx === idx && activeTimelineDrag.type === 'move' && activeTimelineDrag.hasMoved) {
            blockElem.classList.add('dragging');
        }

        blockElem.style.left = `${leftPct}%`;
        blockElem.style.width = `${widthPct}%`;

        const showDir = widthPct > 5.5 && dirBadge;
        const showDur = widthPct > 4.0;
        blockElem.innerHTML = `
            <div style="display: flex; align-items: center; gap: 4px; overflow: hidden; pointer-events: none;">
                <span style="font-size: 10.5px; flex: none;">${def.icon}</span>
                <span style="font-size: 10px; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${blk.name || def.name}</span>
                ${showDir ? `<span style="font-size: 8.5px; background: rgba(0,0,0,0.35); color: #7ee787; padding: 1px 4px; border-radius: 3px; font-family: monospace; font-weight: bold; flex: none;">${dirBadge}</span>` : ''}
            </div>
            ${showDur ? `<span style="font-size: 9px; font-family: monospace; color: rgba(255,255,255,0.85); background: rgba(0,0,0,0.3); padding: 1px 4px; border-radius: 3px; flex: none; pointer-events: none;">${blk.duration.toFixed(1)}s</span>` : ''}
        `;

        // Left Resize Handle (rolling trim)
        if (idx > 0) {
            const leftHandle = document.createElement('div');
            leftHandle.className = 'fleet-block-resize-handle left';
            leftHandle.title = "Drag to trim transition with previous block";
            leftHandle.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                const trackRect = track.getBoundingClientRect();
                activeTimelineDrag = {
                    type: 'resize-left',
                    blockIdx: idx,
                    startClientX: e.clientX,
                    initialDuration: blk.duration,
                    initialPrevDuration: blocks[idx - 1].duration,
                    trackRect: trackRect,
                    totalDur: totalDur,
                    hasMoved: false
                };
            });
            blockElem.appendChild(leftHandle);
        }

        // Right Resize Handle (stretch / shrink duration)
        const rightHandle = document.createElement('div');
        rightHandle.className = 'fleet-block-resize-handle right';
        rightHandle.title = "Drag to stretch or shrink duration";
        rightHandle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            const trackRect = track.getBoundingClientRect();
            activeTimelineDrag = {
                type: 'resize-right',
                blockIdx: idx,
                startClientX: e.clientX,
                initialDuration: blk.duration,
                trackRect: trackRect,
                totalDur: totalDur,
                hasMoved: false
            };
        });
        blockElem.appendChild(rightHandle);

        // Block Body Dragging
        blockElem.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('fleet-block-resize-handle')) return;
            e.stopPropagation();
            const trackRect = track.getBoundingClientRect();
            activeTimelineDrag = {
                type: 'move',
                blockIdx: idx,
                startClientX: e.clientX,
                initialDuration: blk.duration,
                trackRect: trackRect,
                totalDur: totalDur,
                hasMoved: false
            };
        });

        // Tooltip hover
        blockElem.addEventListener('mouseenter', (e) => {
            if (activeTimelineDrag) return;
            const tooltip = document.getElementById('timelineFloatingTooltip');
            if (tooltip) {
                tooltip.style.display = 'block';
                tooltip.style.left = `${e.clientX}px`;
                tooltip.style.top = `${e.clientY - 12}px`;
                const endSec = ((blk.startTime || 0) + (blk.duration || 1.0)).toFixed(1);
                tooltip.innerHTML = `<strong>${def.icon} ${blk.name}</strong> (${(blk.startTime || 0).toFixed(1)}s – ${endSec}s)<br><span style="font-size: 9.5px; color: var(--text-muted);">↔️ Drag edges to stretch • Drag body to reorder</span>`;
            }
        });

        blockElem.addEventListener('mousemove', (e) => {
            if (activeTimelineDrag) return;
            const tooltip = document.getElementById('timelineFloatingTooltip');
            if (tooltip && tooltip.style.display === 'block') {
                tooltip.style.left = `${e.clientX}px`;
                tooltip.style.top = `${e.clientY - 12}px`;
            }
        });

        blockElem.addEventListener('mouseleave', () => {
            if (activeTimelineDrag) return;
            const tooltip = document.getElementById('timelineFloatingTooltip');
            if (tooltip) tooltip.style.display = 'none';
        });

        track.appendChild(blockElem);
    });

    row.appendChild(label);
    row.appendChild(track);
    container.appendChild(row);

    updateTimelineScrubberUI();
}

function syncCueCardInputs(cue) {
    if (!cue) return;
    const card = document.querySelector(`.cue-card[data-cue-id="${cue.id}"]`);
    if (!card) return;
    const startInput = card.querySelector('.cue-start-input');
    const durInput = card.querySelector('.cue-dur-input');
    const timeSpan = card.querySelector('.cue-card-header span[style*="monospace"]');
    if (startInput) startInput.value = cue.startTime.toFixed(1);
    if (durInput) durInput.value = cue.duration.toFixed(1);
    if (timeSpan) {
        const endVal = (cue.startTime + cue.duration).toFixed(1);
        timeSpan.textContent = `${cue.startTime.toFixed(1)}s - ${endVal}s`;
    }
}

function renderTimelineLayers() {
    const container = document.getElementById('timelineLayersContainer');
    const marksContainer = document.getElementById('timelineRulerMarks');
    const labelCol = document.querySelector('.timeline-track-label-col span');
    if (!container) return;

    if (currentView === 'fleet') {
        renderFleetShowTimelineLayers();
        return;
    }

    if (labelCol) labelCol.textContent = 'FLOAT SHOW';

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
            block.title = `${cue.name} (${cue.startTime.toFixed(1)}s - ${(cue.startTime + cue.duration).toFixed(1)}s)`;

            // Left Resize / Trim Handle (drag to trim start time)
            const leftHandle = document.createElement('div');
            leftHandle.className = 'cue-resize-handle handle-left';
            leftHandle.title = 'Drag left/right to trim clip start time';
            block.appendChild(leftHandle);

            if (cue.fadeIn && cue.fadeIn > 0) {
                const inPct = Math.min(40, (cue.fadeIn / cue.duration) * 100);
                const fadeDiv = document.createElement('div');
                fadeDiv.className = 'cue-fade-indicator-in';
                fadeDiv.style.width = `${inPct}%`;
                block.appendChild(fadeDiv);
            }

            const title = document.createElement('span');
            title.className = 'cue-block-title';
            title.textContent = `${cue.name} (${cue.duration.toFixed(1)}s)`;
            block.appendChild(title);

            if (cue.fadeOut && cue.fadeOut > 0) {
                const outPct = Math.min(40, (cue.fadeOut / cue.duration) * 100);
                const fadeDiv = document.createElement('div');
                fadeDiv.className = 'cue-fade-indicator-out';
                fadeDiv.style.width = `${outPct}%`;
                block.appendChild(fadeDiv);
            }

            // Right Resize / Trim Handle (drag to trim duration / end time)
            const rightHandle = document.createElement('div');
            rightHandle.className = 'cue-resize-handle handle-right';
            rightHandle.title = 'Drag left/right to trim clip duration';
            block.appendChild(rightHandle);

            // Reusable floating timeline tooltip
            let timelineTooltip = document.getElementById('timelineDragTooltip');
            if (!timelineTooltip) {
                timelineTooltip = document.createElement('div');
                timelineTooltip.id = 'timelineDragTooltip';
                timelineTooltip.className = 'timeline-drag-tooltip';
                timelineTooltip.style.display = 'none';
                document.body.appendChild(timelineTooltip);
            }

            // 1. LEFT HANDLE: Trim start time
            leftHandle.addEventListener('pointerdown', (e) => {
                e.stopPropagation();
                e.preventDefault();
                leftHandle.setPointerCapture(e.pointerId);

                const startX = e.clientX;
                const origStart = cue.startTime;
                const origDur = cue.duration;
                const origEnd = origStart + origDur;
                const trackRect = track.getBoundingClientRect();
                const secPerPx = sequenceLoopDuration / (trackRect.width || 1);

                block.classList.add('dragging-resize');
                leftHandle.classList.add('dragging');
                timelineTooltip.style.display = 'block';

                const onPointerMove = (ev) => {
                    const dx = ev.clientX - startX;
                    const deltaSec = dx * secPerPx;
                    let newStart = origStart + deltaSec;
                    if (gridSnapInterval > 0) {
                        newStart = Math.round(newStart / gridSnapInterval) * gridSnapInterval;
                    } else {
                        newStart = Math.round(newStart * 10) / 10;
                    }
                    newStart = Math.max(0, Math.min(origEnd - 0.5, newStart));
                    const newDur = Math.round((origEnd - newStart) * 10) / 10;

                    cue.startTime = newStart;
                    cue.duration = newDur;

                    block.style.left = `${(newStart / sequenceLoopDuration) * 100}%`;
                    block.style.width = `${Math.max(1.0, (newDur / sequenceLoopDuration) * 100)}%`;
                    title.textContent = `${cue.name} (${newDur.toFixed(1)}s)`;

                    timelineTooltip.textContent = `◀ Trim Start: ${newStart.toFixed(1)}s | End: ${origEnd.toFixed(1)}s (Dur: ${newDur.toFixed(1)}s)`;
                    timelineTooltip.style.left = `${ev.clientX}px`;
                    timelineTooltip.style.top = `${trackRect.top - 14}px`;
                };

                const onPointerUp = (ev) => {
                    leftHandle.removeEventListener('pointermove', onPointerMove);
                    leftHandle.removeEventListener('pointerup', onPointerUp);
                    leftHandle.removeEventListener('pointercancel', onPointerUp);
                    block.classList.remove('dragging-resize');
                    leftHandle.classList.remove('dragging');
                    timelineTooltip.style.display = 'none';

                    syncCueCardInputs(cue);
                    isSingleShirtDirty = true;
                    renderTimelineLayers();
                };

                leftHandle.addEventListener('pointermove', onPointerMove);
                leftHandle.addEventListener('pointerup', onPointerUp);
                leftHandle.addEventListener('pointercancel', onPointerUp);
            });

            // 2. RIGHT HANDLE: Trim duration / end time
            rightHandle.addEventListener('pointerdown', (e) => {
                e.stopPropagation();
                e.preventDefault();
                rightHandle.setPointerCapture(e.pointerId);

                const startX = e.clientX;
                const origStart = cue.startTime;
                const origDur = cue.duration;
                const origEnd = origStart + origDur;
                const trackRect = track.getBoundingClientRect();
                const secPerPx = sequenceLoopDuration / (trackRect.width || 1);

                block.classList.add('dragging-resize');
                rightHandle.classList.add('dragging');
                timelineTooltip.style.display = 'block';

                const onPointerMove = (ev) => {
                    const dx = ev.clientX - startX;
                    const deltaSec = dx * secPerPx;
                    let newEnd = origEnd + deltaSec;
                    if (gridSnapInterval > 0) {
                        newEnd = Math.round(newEnd / gridSnapInterval) * gridSnapInterval;
                    } else {
                        newEnd = Math.round(newEnd * 10) / 10;
                    }
                    newEnd = Math.max(origStart + (gridSnapInterval > 0 ? gridSnapInterval : 0.5), Math.min(sequenceLoopDuration, newEnd));
                    const newDur = Math.round((newEnd - origStart) * 10) / 10;

                    cue.duration = newDur;

                    block.style.width = `${Math.max(1.0, (newDur / sequenceLoopDuration) * 100)}%`;
                    title.textContent = `${cue.name} (${newDur.toFixed(1)}s)`;

                    timelineTooltip.textContent = `▶ Trim End: ${newEnd.toFixed(1)}s | Start: ${origStart.toFixed(1)}s (Dur: ${newDur.toFixed(1)}s)`;
                    timelineTooltip.style.left = `${ev.clientX}px`;
                    timelineTooltip.style.top = `${trackRect.top - 14}px`;
                };

                const onPointerUp = (ev) => {
                    rightHandle.removeEventListener('pointermove', onPointerMove);
                    rightHandle.removeEventListener('pointerup', onPointerUp);
                    rightHandle.removeEventListener('pointercancel', onPointerUp);
                    block.classList.remove('dragging-resize');
                    rightHandle.classList.remove('dragging');
                    timelineTooltip.style.display = 'none';

                    syncCueCardInputs(cue);
                    isSingleShirtDirty = true;
                    renderTimelineLayers();
                };

                rightHandle.addEventListener('pointermove', onPointerMove);
                rightHandle.addEventListener('pointerup', onPointerUp);
                rightHandle.addEventListener('pointercancel', onPointerUp);
            });

            // 3. BLOCK BODY: Move / Slip Clip on Timeline or Click to Seek
            block.addEventListener('pointerdown', (e) => {
                if (e.target === leftHandle || e.target === rightHandle) return;
                e.stopPropagation();
                e.preventDefault();
                block.setPointerCapture(e.pointerId);

                const startX = e.clientX;
                const origStart = cue.startTime;
                const dur = cue.duration;
                const trackRect = track.getBoundingClientRect();
                const secPerPx = sequenceLoopDuration / (trackRect.width || 1);
                let hasDragged = false;

                const onPointerMove = (ev) => {
                    const dx = ev.clientX - startX;
                    if (!hasDragged && Math.abs(dx) >= 4) {
                        hasDragged = true;
                        block.classList.add('dragging-move');
                        timelineTooltip.style.display = 'block';
                    }

                    if (hasDragged) {
                        const deltaSec = dx * secPerPx;
                        let newStart = origStart + deltaSec;
                        if (gridSnapInterval > 0) {
                            newStart = Math.round(newStart / gridSnapInterval) * gridSnapInterval;
                        } else {
                            newStart = Math.round(newStart * 10) / 10;
                        }
                        newStart = Math.max(0, Math.min(sequenceLoopDuration - dur, newStart));
                        const newEnd = Math.round((newStart + dur) * 10) / 10;

                        cue.startTime = newStart;

                        block.style.left = `${(newStart / sequenceLoopDuration) * 100}%`;

                        timelineTooltip.textContent = `↔ Move: ${newStart.toFixed(1)}s – ${newEnd.toFixed(1)}s (${dur.toFixed(1)}s)`;
                        timelineTooltip.style.left = `${ev.clientX}px`;
                        timelineTooltip.style.top = `${trackRect.top - 14}px`;
                    }
                };

                const onPointerUp = (ev) => {
                    block.removeEventListener('pointermove', onPointerMove);
                    block.removeEventListener('pointerup', onPointerUp);
                    block.removeEventListener('pointercancel', onPointerUp);

                    if (hasDragged) {
                        block.classList.remove('dragging-move');
                        timelineTooltip.style.display = 'none';

                        syncCueCardInputs(cue);
                        isSingleShirtDirty = true;
                        renderTimelineLayers();
                    } else {
                        // Click without drag -> seek playhead and highlight cue card
                        sequenceTime = cue.startTime;
                        updateTimelineScrubberUI();
                        const card = document.querySelector(`.cue-card[data-cue-id="${cue.id}"]`);
                        if (card) {
                            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            card.style.outline = '2px solid #58a6ff';
                            setTimeout(() => card.style.outline = 'none', 1000);
                        }
                    }
                };

                block.addEventListener('pointermove', onPointerMove);
                block.addEventListener('pointerup', onPointerUp);
                block.addEventListener('pointercancel', onPointerUp);
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
        badge.textContent = sequenceCues.length === 0 ? '0 Cues (Ambient Fallback)' : `${sequenceCues.length} Cue${sequenceCues.length !== 1 ? 's' : ''}`;
        badge.style.color = sequenceCues.length === 0 ? 'var(--accent-cyan)' : '#3fb950';
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
        { id: 'color_match', label: '🌬️ Slo-Glo Breath' },
        { id: 'comet', label: '☄️ Meteor / Comet Trail' },
        { id: 'scanner', label: '🛸 Larson Scanner' },
        { id: 'color_wipe', label: '✍️ Color Wipe / Progressive Fill' },
        { id: 'pixie_dust', label: '💫 Pixie Dust Drift' },
        { id: 'filament_glow', label: '⚡ Vintage 1972 Filament' },
        { id: 'candle_flicker', label: '🕯️ Candle / Lantern Flame' },
        { id: 'tidal_ripple', label: '🌊 Tidal Ripple' },
        { id: 'piston_chug', label: '🚂 Locomotive Piston Chug' },
        { id: 'marquee', label: '🎪 Classic Marquee Chase' },
        { id: 'fireworks', label: '🎆 Fireworks Starburst' },
        { id: 'rainbow_cycle', label: '🌈 Rainbow Color Wave' },
        { id: 'photo_mode', label: '📸 Castle Photo Mode (Solid)' },
        { id: 'chase', label: '🎡 Chase / Wheel Spin' },
        { id: 'flash_slow', label: '💡 Slow Flashing / Blink' },
        { id: 'sparkle_storm', label: '✨ Sparkle Storm' },
        { id: 'write_on_off', label: '✍️ Theatrical Write-On/Off' },
        { id: 'traveling_wave', label: '🌊 Traveling Parade Wave' },
        { id: 'fire_breath', label: '🔥 Snout Fire Breath' },
        { id: 'off', label: '🌑 Off / Completely Unlit' }
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

            <!-- Target Layer, Effect & Direction Selection -->
            <div class="cue-card-row">
                <div style="flex: 1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Target Layer:</label>
                    <select class="cue-target-select" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px;">
                        <option value="global" ${cue.targetType === 'global' ? 'selected' : ''}>🌐 Global Float</option>
                        ${animationGroups.map(g => `<option value="group:${g.id}" ${cue.targetType === 'group' && cue.groupId === g.id ? 'selected' : ''}>🎡 Group: ${g.name}</option>`).join('')}
                    </select>
                </div>
                <div style="flex: 1.2;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Pattern / Effect:</label>
                    <select class="cue-effect-select" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px;">
                        ${effectOptions.map(e => `<option value="${e.id}" ${cue.effect === e.id ? 'selected' : ''}>${e.label}</option>`).join('')}
                    </select>
                </div>
                <div style="flex: 0.8;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Direction:</label>
                    <select class="cue-direction-select" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px;">
                        <option value="1" ${(cue.direction === 1 || cue.direction === '1' || !cue.direction || cue.direction === 'forward') ? 'selected' : ''}>➡️ Fwd</option>
                        <option value="-1" ${(cue.direction === -1 || cue.direction === '-1' || cue.direction === 'reverse') ? 'selected' : ''}>⬅️ Rev</option>
                    </select>
                </div>
            </div>

            <!-- Start Time, Duration & BPM with Quick Chips -->
            <div class="cue-card-row">
                <div style="flex: 0.9;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Start (s):</label>
                    <input type="number" class="cue-start-input" step="0.5" min="0" max="${sequenceLoopDuration}" value="${cue.startTime}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px; text-align: center;">
                </div>
                <div style="flex: 1.1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">Dur (s):</label>
                    <input type="number" class="cue-dur-input" step="0.5" min="1" max="${sequenceLoopDuration}" value="${cue.duration}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px; text-align: center;">
                    <div style="display: flex; gap: 2px; margin-top: 2px;">
                        <button type="button" class="action-btn cue-dur-chip" data-dur="5" style="flex: 1; font-size: 8px; padding: 1px 0;" title="5s">5s</button>
                        <button type="button" class="action-btn cue-dur-chip" data-dur="10" style="flex: 1; font-size: 8px; padding: 1px 0;" title="10s">10s</button>
                        <button type="button" class="action-btn cue-dur-chip" data-dur="15" style="flex: 1; font-size: 8px; padding: 1px 0;" title="15s">15s</button>
                        <button type="button" class="action-btn cue-dur-chip" data-dur="30" style="flex: 1; font-size: 8px; padding: 1px 0;" title="30s">30s</button>
                    </div>
                </div>
                <div style="flex: 1.1;">
                    <label style="font-size: 10px; color: var(--text-muted); display: block;">BPM:</label>
                    <input type="number" class="cue-bpm-input" min="30" max="280" value="${cue.speedBpm || 120}" style="width: 100%; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 4px; font-size: 11px; text-align: center;">
                    <div style="display: flex; gap: 2px; margin-top: 2px;">
                        <button type="button" class="action-btn cue-bpm-chip" data-bpm="90" style="flex: 1; font-size: 8px; padding: 1px 0;" title="90 BPM">90</button>
                        <button type="button" class="action-btn cue-bpm-chip" data-bpm="120" style="flex: 1; font-size: 8px; padding: 1px 0;" title="120 BPM">120</button>
                        <button type="button" class="action-btn cue-bpm-chip" data-bpm="144" style="flex: 1; font-size: 8px; padding: 1px 0; font-weight: 600; color: var(--accent-gold);" title="144 BPM">144</button>
                        <button type="button" class="action-btn cue-bpm-chip" data-bpm="180" style="flex: 1; font-size: 8px; padding: 1px 0;" title="180 BPM">180</button>
                    </div>
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
                if (grp) {
                    // Carry over the animation effect that was selected when the group was created!
                    if (grp.effect) {
                        cue.effect = grp.effect;
                        const effSelect = card.querySelector('.cue-effect-select');
                        if (effSelect) effSelect.value = grp.effect;
                    }
                    if (grp.speedBpm) {
                        cue.speedBpm = grp.speedBpm;
                        const bpmInput = card.querySelector('.cue-bpm-input');
                        if (bpmInput) bpmInput.value = grp.speedBpm;
                    }
                    if (grp.direction !== undefined) {
                        cue.direction = grp.direction;
                        const dirSelect = card.querySelector('.cue-direction-select');
                        if (dirSelect) dirSelect.value = grp.direction;
                    }
                    // If cue has default name, update to reflect group name
                    if (cue.name.startsWith('Cue #') || cue.name.endsWith(' Routine')) {
                        cue.name = `${grp.name} Routine`;
                        const nameInput = card.querySelector('.cue-name-input');
                        if (nameInput) nameInput.value = cue.name;
                    }
                }
            } else {
                cue.targetType = 'global';
                cue.groupId = '';
                cue.groupName = '';
            }
            renderTimelineCueStrip();
        });

        card.querySelector('.cue-effect-select').addEventListener('change', (e) => {
            cue.effect = e.target.value;
            renderTimelineCueStrip();
        });

        card.querySelector('.cue-direction-select').addEventListener('change', (e) => {
            cue.direction = parseInt(e.target.value, 10);
            markSingleShirtDirty();
        });

        card.querySelector('.cue-start-input').addEventListener('change', (e) => {
            cue.startTime = Math.max(0, parseFloat(e.target.value) || 0);
            renderTimelineCueStrip();
        });

        card.querySelector('.cue-dur-input').addEventListener('change', (e) => {
            cue.duration = Math.max(0.5, parseFloat(e.target.value) || 10);
            renderTimelineCueStrip();
        });

        card.querySelectorAll('.cue-dur-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                const val = parseFloat(btn.dataset.dur);
                cue.duration = val;
                const durInput = card.querySelector('.cue-dur-input');
                if (durInput) durInput.value = val;
                renderTimelineCueStrip();
                updateTimelineScrubberUI();
                markSingleShirtDirty();
            });
        });

        card.querySelector('.cue-bpm-input').addEventListener('change', (e) => {
            cue.speedBpm = Math.max(20, parseInt(e.target.value) || 120);
        });

        card.querySelectorAll('.cue-bpm-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                const val = parseInt(btn.dataset.bpm, 10);
                cue.speedBpm = val;
                const bpmInput = card.querySelector('.cue-bpm-input');
                if (bpmInput) bpmInput.value = val;
                markSingleShirtDirty();
            });
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

    let targetType = options.targetType;
    let groupId = options.groupId;
    let groupName = options.groupName;
    let effect = options.effect;
    let speedBpm = options.speedBpm;
    let direction = options.direction;

    // If options didn't specify target, but an animation group is currently selected in the UI:
    if (!targetType && !groupId && selectedGroupId) {
        const selGrp = animationGroups.find(g => g.id === selectedGroupId);
        if (selGrp) {
            targetType = 'group';
            groupId = selGrp.id;
            groupName = selGrp.name;
        }
    }

    if (!targetType) targetType = 'global';
    if (!groupId) groupId = '';
    if (!groupName) groupName = '';

    // If cue targets a group, carry over the effect that was selected when the group was created!
    if (targetType === 'group' && groupId) {
        const grp = animationGroups.find(g => g.id === groupId);
        if (grp) {
            if (!groupName) groupName = grp.name;
            if (!effect) effect = grp.effect || 'chase';
            if (!speedBpm) speedBpm = grp.speedBpm || 140;
            if (direction === undefined && grp.direction !== undefined) direction = grp.direction;
        }
    }

    if (!effect) effect = 'color_match';
    if (!speedBpm) speedBpm = 120;
    if (direction === undefined) direction = 1;

    const defaultName = (targetType === 'group' && groupName)
        ? `${groupName} Routine`
        : `Cue #${sequenceCues.length + 1}`;

    const newCue = {
        id: 'cue_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
        name: options.name || defaultName,
        startTime: options.startTime !== undefined ? options.startTime : defaultStart,
        duration: options.duration !== undefined ? options.duration : 20.0,
        targetType: targetType,
        groupId: groupId,
        groupName: groupName,
        effect: effect,
        direction: direction,
        speedBpm: speedBpm,
        fadeIn: options.fadeIn !== undefined ? options.fadeIn : 1.5,
        fadeOut: options.fadeOut !== undefined ? options.fadeOut : 1.5
    };

    sequenceCues.push(newCue);
    renderCuesList();
    markSingleShirtDirty();
    showToast(`➕ Added show cue "${newCue.name}" (${newCue.effect})!`);
}

function deleteCue(cueId) {
    const idx = sequenceCues.findIndex(q => q.id === cueId);
    if (idx !== -1) {
        const name = sequenceCues[idx].name;
        sequenceCues.splice(idx, 1);
        renderCuesList();
        markSingleShirtDirty();
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

function load90sTheatricalShowTemplate() {
    sequenceLoopDuration = 90.0;
    const loopInput = document.getElementById('sequenceLoopInput');
    if (loopInput) loopInput.value = 90;

    sequenceCues = [
        {
            id: 'cue_90s_1',
            name: 'Phase 1: Sampled Starlight Sparkle',
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
            id: 'cue_90s_2',
            name: 'Phase 2: Theatrical Breathing Glow',
            startTime: 30.0,
            duration: 30.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'breathe',
            speedBpm: 60,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_90s_3',
            name: 'Phase 3: Dynamic Traveling Chase Beam',
            startTime: 60.0,
            duration: 15.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'chase',
            speedBpm: 140,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_90s_4',
            name: 'Phase 4: Solo Electrical Parade Wave',
            startTime: 75.0,
            duration: 15.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'traveling_wave',
            speedBpm: 120,
            fadeIn: 1.5,
            fadeOut: 1.5
        }
    ];

    renderCuesList();
    toggleSequenceMode(true);
    showToast("🎭 Loaded 90-Second Classic Theatrical Showcase!");
}

function loadCaseyLocomotiveShowTemplate() {
    sequenceLoopDuration = 90.0;
    const loopInput = document.getElementById('sequenceLoopInput');
    if (loopInput) loopInput.value = 90;

    let wheelGrp = animationGroups.find(g => g.name.toLowerCase().includes('wheel') || g.name.toLowerCase().includes('piston'));

    sequenceCues = [
        {
            id: 'cue_casey_1',
            name: 'Opening Steam & Sparkle',
            startTime: 0.0,
            duration: 25.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'steady_sparkle',
            direction: 1,
            speedBpm: 120,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_casey_2',
            name: 'Piston Chug Acceleration',
            startTime: 20.0,
            duration: 30.0,
            targetType: wheelGrp ? 'group' : 'global',
            groupId: wheelGrp ? wheelGrp.id : '',
            groupName: wheelGrp ? wheelGrp.name : 'Locomotive Pistons',
            effect: 'piston_chug',
            direction: 1,
            speedBpm: 144,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_casey_3',
            name: 'Full Head of Steam Comet Sweep',
            startTime: 45.0,
            duration: 30.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'comet',
            direction: 1,
            speedBpm: 180,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_casey_4',
            name: 'Casey Jr. Circus Marquee Finale',
            startTime: 70.0,
            duration: 20.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'marquee',
            direction: 1,
            speedBpm: 144,
            fadeIn: 1.5,
            fadeOut: 2.0
        }
    ];

    renderCuesList();
    toggleSequenceMode(true);
    showToast("🚂 Loaded Casey Jr. 90s Locomotive Parade Routine!");
}

function loadTurtleSnailShowTemplate() {
    sequenceLoopDuration = 90.0;
    const loopInput = document.getElementById('sequenceLoopInput');
    if (loopInput) loopInput.value = 90;

    let shellGrp = animationGroups.find(g => g.name.toLowerCase().includes('shell') || g.name.toLowerCase().includes('spiral') || g.name.toLowerCase().includes('wheel'));

    sequenceCues = [
        {
            id: 'cue_turtle_1',
            name: 'Enchanted Garden Pixie Dust',
            startTime: 0.0,
            duration: 30.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'pixie_dust',
            direction: 1,
            speedBpm: 90,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_turtle_2',
            name: 'Rotating Shell Spin',
            startTime: 25.0,
            duration: 35.0,
            targetType: shellGrp ? 'group' : 'global',
            groupId: shellGrp ? shellGrp.id : '',
            groupName: shellGrp ? shellGrp.name : 'Turtle Shell',
            effect: 'chase',
            direction: 1,
            speedBpm: 120,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_turtle_3',
            name: 'Tidal Ripple Expansion',
            startTime: 55.0,
            duration: 25.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'tidal_ripple',
            direction: 1,
            speedBpm: 120,
            fadeIn: 2.0,
            fadeOut: 1.5
        },
        {
            id: 'cue_turtle_4',
            name: 'Rainbow Shell Spiral Finale',
            startTime: 75.0,
            duration: 15.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'rainbow_cycle',
            direction: 1,
            speedBpm: 144,
            fadeIn: 1.5,
            fadeOut: 2.0
        }
    ];

    renderCuesList();
    toggleSequenceMode(true);
    showToast("🐢 Loaded Turtle & Snail 90s Parade Routine!");
}

function loadPatrioticFinaleShowTemplate() {
    sequenceLoopDuration = 90.0;
    const loopInput = document.getElementById('sequenceLoopInput');
    if (loopInput) loopInput.value = 90;

    let fwGrp = animationGroups.find(g => g.name.toLowerCase().includes('firework') || g.name.toLowerCase().includes('burst') || g.name.toLowerCase().includes('star'));

    sequenceCues = [
        {
            id: 'cue_patriotic_1',
            name: 'Red White & Blue Starlight',
            startTime: 0.0,
            duration: 25.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'steady_sparkle',
            direction: 1,
            speedBpm: 120,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_patriotic_2',
            name: 'Main Street Parade Wave',
            startTime: 20.0,
            duration: 30.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'traveling_wave',
            direction: 1,
            speedBpm: 144,
            fadeIn: 1.5,
            fadeOut: 1.5
        },
        {
            id: 'cue_patriotic_3',
            name: 'Grand Starburst Fireworks',
            startTime: 45.0,
            duration: 30.0,
            targetType: fwGrp ? 'group' : 'global',
            groupId: fwGrp ? fwGrp.id : '',
            groupName: fwGrp ? fwGrp.name : 'Grand Starburst',
            effect: 'fireworks',
            direction: 1,
            speedBpm: 140,
            fadeIn: 2.0,
            fadeOut: 2.0
        },
        {
            id: 'cue_patriotic_4',
            name: 'Golden Age 1972 Theater Marquee',
            startTime: 70.0,
            duration: 20.0,
            targetType: 'global',
            groupId: '',
            groupName: '',
            effect: 'marquee',
            direction: 1,
            speedBpm: 180,
            fadeIn: 1.5,
            fadeOut: 2.0
        }
    ];

    renderCuesList();
    toggleSequenceMode(true);
    showToast("🎆 Loaded America Grand Finale 90s Parade Routine!");
}

// ============================================================================
// PARADE CUE DIRECTOR & MASTER TIMELINE EVENT LISTENERS
// ============================================================================
const timelinePlayBtn = document.getElementById('timelinePlayBtn');
if (timelinePlayBtn) {
    timelinePlayBtn.addEventListener('click', () => {
        if (currentView === 'fleet') {
            triggerFleetShowToggle();
        } else {
            togglePlayPause();
        }
    });
}

const timelineStopBtn = document.getElementById('timelineStopBtn');
if (timelineStopBtn) {
    timelineStopBtn.addEventListener('click', () => {
        if (currentView === 'fleet') {
            stopFleetShow();
            showToast('⏹ Stopped Fleet Show and rewound to 0.0s');
        } else {
            stopSequence();
        }
    });
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
    timelineModeToggle.addEventListener('click', () => {
        if (currentView === 'fleet') {
            triggerFleetShowToggle();
        } else {
            toggleSequenceMode();
        }
    });
}

const toggleSequenceModeBtn = document.getElementById('toggleSequenceModeBtn');
if (toggleSequenceModeBtn) {
    toggleSequenceModeBtn.addEventListener('click', () => toggleSequenceMode());
}

const timelineScrubber = document.getElementById('timelineScrubber');
if (timelineScrubber) {
    timelineScrubber.addEventListener('input', (e) => {
        if (currentView === 'fleet' && activeFleetShow) {
            fleetShowElapsedSec = parseFloat(e.target.value) || 0;
            updateFleetShowUI();
        } else {
            sequenceTime = parseFloat(e.target.value) || 0;
            updateTimelineScrubberUI();
        }
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

// ============================================================================
// FEATURE 10: CUE QUANTIZATION & TIMELINE HOVER-SCRUBBING ENGINE
// ============================================================================
function quantizeCue(cue, interval) {
    if (!interval || interval <= 0) return;
    const newStart = Math.round(cue.startTime / interval) * interval;
    const newDur = Math.max(interval, Math.round(cue.duration / interval) * interval);
    cue.startTime = Math.max(0, Math.min(sequenceLoopDuration - newDur, Math.round(newStart * 10) / 10));
    cue.duration = Math.round(newDur * 10) / 10;
}

function quantizeAllCues(interval = gridSnapInterval) {
    if (sequenceCues.length === 0) {
        showToast("⚠️ No cues on timeline to quantize!");
        return;
    }
    const quantInterval = (interval && interval > 0) ? interval : 0.5;
    pushUndoState("Quantize All Cues");
    sequenceCues.forEach(q => quantizeCue(q, quantInterval));
    renderTimelineLayers();
    renderCueCards();
    isSingleShirtDirty = true;
    showToast(`🎯 Quantized ${sequenceCues.length} cue${sequenceCues.length !== 1 ? 's' : ''} to ${quantInterval}s grid!`);
}

const timelineGridSnapSelect = document.getElementById('timelineGridSnapSelect');
if (timelineGridSnapSelect) {
    timelineGridSnapSelect.addEventListener('change', (e) => {
        gridSnapInterval = parseFloat(e.target.value) || 0;
        showToast(gridSnapInterval > 0 ? `🎯 Grid Snap set to ${gridSnapInterval}s` : "🎯 Grid Snap OFF");
    });
}

const timelineQuantizeBtn = document.getElementById('timelineQuantizeBtn');
if (timelineQuantizeBtn) {
    timelineQuantizeBtn.addEventListener('click', () => {
        quantizeAllCues(gridSnapInterval > 0 ? gridSnapInterval : 0.5);
    });
}

function initTimelineHoverScrub() {
    const rulerWrapper = document.getElementById('timelineRulerWrapper');
    const layersWrapper = document.getElementById('timelineLayersWrapper');
    const ghostNeedle = document.getElementById('timelineGhostNeedle');
    const tooltip = document.getElementById('timelineFloatingTooltip');

    if (!rulerWrapper || !layersWrapper) return;

    function handleTimelineHover(e) {
        if (sequencePlaying) {
            if (ghostNeedle) ghostNeedle.style.display = 'none';
            if (tooltip) tooltip.style.display = 'none';
            isHoverScrubbing = false;
            return;
        }

        const rect = layersWrapper.getBoundingClientRect();
        const labelColWidth = 115;
        const mouseX = e.clientX - rect.left - labelColWidth;
        const trackWidth = rect.width - labelColWidth;

        if (mouseX < 0 || mouseX > trackWidth || trackWidth <= 0) {
            if (ghostNeedle) ghostNeedle.style.display = 'none';
            if (tooltip) tooltip.style.display = 'none';
            isHoverScrubbing = false;
            return;
        }

        const pct = mouseX / trackWidth;
        const hoverSec = Math.max(0, Math.min(sequenceLoopDuration, pct * sequenceLoopDuration));
        
        isHoverScrubbing = true;
        hoverScrubTime = hoverSec;

        // Position Ghost Needle
        if (ghostNeedle) {
            ghostNeedle.style.display = 'block';
            ghostNeedle.style.left = `${labelColWidth + mouseX}px`;
        }

        // Find active cues at hover timestamp
        const activeCues = sequenceCues.filter(q => hoverSec >= q.startTime && hoverSec < (q.startTime + q.duration));
        const cueText = activeCues.length > 0 ? activeCues.map(c => c.name).join(', ') : 'Ambient Fallback';

        // Position Floating Tooltip
        if (tooltip) {
            tooltip.style.display = 'block';
            tooltip.style.left = `${e.clientX}px`;
            tooltip.style.top = `${rect.top - 10}px`;
            tooltip.innerHTML = `⏱️ <strong>${hoverSec.toFixed(1)}s</strong> <span style="color:#8b949e">| ${cueText}</span>`;
        }

        // Trigger real-time canvas redraw for hover preview
        if (typeof requestAnimationFrame === 'function') {
            requestAnimationFrame(() => {
                if (typeof drawCanvas === 'function') drawCanvas();
            });
        }
    }

    function handleTimelineLeave() {
        isHoverScrubbing = false;
        if (ghostNeedle) ghostNeedle.style.display = 'none';
        if (tooltip) tooltip.style.display = 'none';
        if (typeof drawCanvas === 'function') drawCanvas();
    }

    [rulerWrapper, layersWrapper].forEach(container => {
        container.addEventListener('mousemove', handleTimelineHover);
        container.addEventListener('mouseleave', handleTimelineLeave);
    });
}

const sequenceTemplateSelect = document.getElementById('sequenceTemplateSelect');
if (sequenceTemplateSelect) {
    sequenceTemplateSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'cinderella_90s') {
            loadCinderellaShowTemplate();
        } else if (val === 'dragon_90s') {
            loadDragonShowTemplate();
        } else if (val === 'casey_locomotive_90s') {
            loadCaseyLocomotiveShowTemplate();
        } else if (val === 'turtle_snail_spin_90s') {
            loadTurtleSnailShowTemplate();
        } else if (val === 'patriotic_grand_finale_90s') {
            loadPatrioticFinaleShowTemplate();
        } else if (val === 'classic_90s' || val === 'autonomous_90s') {
            load90sTheatricalShowTemplate();
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
    } else if ((e.key === 'z' || e.key === 'Z') && (e.ctrlKey || e.metaKey) && !e.shiftKey) {
        e.preventDefault();
        undo();
    } else if (((e.key === 'y' || e.key === 'Y') && (e.ctrlKey || e.metaKey)) || ((e.key === 'z' || e.key === 'Z') && (e.ctrlKey || e.metaKey) && e.shiftKey)) {
        e.preventDefault();
        redo();
    } else if ((e.key === 'c' || e.key === 'C') && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        copyGroup();
    } else if ((e.key === 'v' || e.key === 'V') && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        pasteGroup();
    } else if ((e.key === 'r' || e.key === 'R') && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        rotateGroup(null, 90);
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
            if (currentView === 'fleet') {
                triggerFleetShowToggle();
            } else {
                togglePlayPause();
            }
        }
        isSpacePressed = false;
        canvas.style.cursor = hoveredLed !== null ? 'pointer' : 'default';
    }
});

canvas.addEventListener('mousedown', (e) => {
    if (currentView === 'fleet') {
        if (fleetHoveredRunner !== -1) {
            fleetSelectedRunner = fleetHoveredRunner;
            document.querySelectorAll('.fleet-runner-card').forEach(c => c.classList.remove('selected-runner'));
            const card = document.querySelector(`.fleet-runner-card[data-slot="${fleetHoveredRunner}"]`);
            if (card) {
                card.classList.add('selected-runner');
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
        return;
    }
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

    // Click-to-Place Stamp Mode Handler
    if (isClickCanvasToPlaceActive) {
        const worldX = (mx - panX) / zoomScale;
        const worldY = (my - panY) / zoomScale;
        const norm = canvasToNorm(worldX, worldY);
        const clampX = Math.max(0.08, Math.min(0.92, norm.x));
        const clampY = Math.max(0.08, Math.min(0.92, norm.y));
        stampSelectedShape(clampX, clampY);
        isClickCanvasToPlaceActive = false;
        const clickBtn = document.getElementById('stampClickCanvasBtn');
        if (clickBtn) {
            clickBtn.classList.remove('active');
            clickBtn.textContent = '🎯 Click Canvas to Place';
        }
        canvas.style.cursor = 'default';
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
            // Normal click: select single LED or drag entire animation group / multi-selection
            let isGroupDrag = false;
            
            // Priority A: Already part of active multi-selection
            if (selectedLeds.has(clickedIdx) && selectedLeds.size > 1) {
                isGroupDrag = true;
                selectedLed = clickedIdx;
                updateLedInspectorUI();
            } else {
                // Priority B: Check if LED belongs to an animation group
                const grpEntry = ledGroupMap[clickedIdx];
                const grp = grpEntry ? grpEntry.group : animationGroups.find(g => g.ledIndices && g.ledIndices.includes(clickedIdx));
                if (grp && Array.isArray(grp.ledIndices) && grp.ledIndices.length > 1) {
                    isGroupDrag = true;
                    selectedGroupId = grp.id;
                    selectedLeds.clear();
                    for (const idx of grp.ledIndices) {
                        if (idx < leds.length) selectedLeds.add(idx);
                    }
                    selectedLed = clickedIdx;
                    populateGroupForm(grp);

                    if (grp.effect === 'fireworks') {
                        activeFireworksGroupId = grp.id;
                        updateActiveFwDropdown();
                        syncFireworksSliders(grp.centerNormX, grp.centerNormY, grp.burstRadius, grp.fireworkColor);
                    }

                    updateLedInspectorUI();
                    renderActiveGroupsList();
                } else {
                    // Priority C: Single LED
                    selectLed(clickedIdx, false);
                }
            }

            draggedLed = clickedIdx;
            isDraggingLed = true;
            canvas.classList.add('dragging');

            // Capture pre-drag state for Undo/Redo
            if (isGroupDrag || selectedLeds.size > 1) {
                const grpEntry = ledGroupMap[clickedIdx];
                const grp = grpEntry ? grpEntry.group : animationGroups.find(g => g.ledIndices && g.ledIndices.includes(clickedIdx));
                const grpName = grp ? grp.name : 'Group';
                preDragStateSnapshot = captureEditorSnapshot(`Move Group "${grpName}"`);
            } else {
                preDragStateSnapshot = captureEditorSnapshot(`Move LED #${clickedIdx + 1}`);
            }

            const worldX = (mx - panX) / zoomScale;
            const worldY = (my - panY) / zoomScale;
            multiDragStartNorm = canvasToNorm(worldX, worldY);
            multiDragInitialPositions.clear();

            if (isGroupDrag || selectedLeds.size > 1) {
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

            // Find symmetrical partners if Live Symmetry Drag is active
            liveSymmetryPartners.clear();
            if (params.liveSymmetryDrag) {
                for (const [dragIdx, initPos] of multiDragInitialPositions.entries()) {
                    const targetX = 1.0 - initPos.x;
                    const targetY = initPos.y;
                    let bestPartner = -1;
                    let bestDist = 0.045; // max tolerance
                    for (let j = 0; j < leds.length; j++) {
                        if (j === dragIdx || multiDragInitialPositions.has(j) || liveSymmetryPartners.has(j)) continue;
                        const d = Math.hypot(leds[j].x - targetX, leds[j].y - targetY);
                        if (d < bestDist) {
                            bestDist = d;
                            bestPartner = j;
                        }
                    }
                    if (bestPartner !== -1 && leds[bestPartner]) {
                        liveSymmetryPartners.set(bestPartner, { x: leds[bestPartner].x, y: leds[bestPartner].y });
                    }
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

// ---------------------------------------------------------------------------
// ZERO-OVERLAP TPU COLLAR CLEARANCE & PBD RELAXATION
// 10x5mm inner socket, 12.4x7.4mm outer collar stadium (5.0mm horizontal segment).
// Required center distance >= 7.9mm (0.5mm clear wall gap between any two collars).
// Physical garment scale: 18.0 inch garment = 457.2mm -> 1.0mm = 1.0 / 457.2 normalized units.
// ---------------------------------------------------------------------------
function clampLedNoCollarOverlap(targetX, targetY, movingIndex, ledsArray) {
    const mmToNorm = 1.0 / 457.2;
    const segLen = 5.0 * mmToNorm;
    const reqDist = 7.9 * mmToNorm;
    let x = targetX;
    let y = targetY;

    for (let iter = 0; iter < 4; iter++) {
        for (let j = 0; j < ledsArray.length; j++) {
            if (j === movingIndex) continue;
            const ox = ledsArray[j].x;
            const oy = ledsArray[j].y;
            const dx = x - ox;
            const dy = y - oy;
            const adx = Math.abs(dx);
            const ady = Math.abs(dy);
            const segDx = Math.max(0, adx - segLen);
            const segDy = ady;
            const dist = Math.hypot(segDx, segDy);

            if (dist < reqDist) {
                const pen = reqDist - dist;
                let nx, ny;
                if (dist < 1e-5) {
                    nx = 0.0;
                    ny = 1.0;
                } else {
                    nx = (segDx / dist) * (dx >= 0 ? 1.0 : -1.0);
                    ny = (segDy / dist) * (dy >= 0 ? 1.0 : -1.0);
                }
                x += nx * pen;
                y += ny * pen;
            }
        }
    }
    return {
        x: Math.max(0.05, Math.min(0.95, parseFloat(x.toFixed(4)))),
        y: Math.max(0.05, Math.min(0.95, parseFloat(y.toFixed(4))))
    };
}

function relaxLedCollarOverlaps(ledsList, iterations = 35) {
    if (!ledsList || ledsList.length < 2) return;
    const mmToNorm = 1.0 / 457.2;
    const segLen = 5.0 * mmToNorm;
    const reqDist = 7.9 * mmToNorm;
    const n = ledsList.length;
    const gb = typeof getGraphicChestBounds === 'function' ? getGraphicChestBounds() : { normX: 0.1, normY: 0.1, normW: 0.8, normH: 0.8 };

    for (let iter = 0; iter < iterations; iter++) {
        for (let i = 0; i < n; i++) {
            for (let j = i + 1; j < n; j++) {
                const dx = ledsList[j].x - ledsList[i].x;
                const dy = ledsList[j].y - ledsList[i].y;
                const adx = Math.abs(dx);
                const ady = Math.abs(dy);
                const segDx = Math.max(0, adx - segLen);
                const segDy = ady;
                const dist = Math.hypot(segDx, segDy);

                if (dist < reqDist) {
                    const pen = reqDist - dist;
                    let nx, ny;
                    if (dist < 1e-5) {
                        nx = 0.0;
                        ny = 1.0;
                    } else {
                        nx = (segDx / dist) * (dx >= 0 ? 1.0 : -1.0);
                        ny = (segDy / dist) * (dy >= 0 ? 1.0 : -1.0);
                    }
                    const pushX = nx * pen * 0.5;
                    const pushY = ny * pen * 0.5;
                    ledsList[i].x -= pushX;
                    ledsList[i].y -= pushY;
                    ledsList[j].x += pushX;
                    ledsList[j].y += pushY;
                }
            }
        }
        for (let i = 0; i < n; i++) {
            ledsList[i].x = Math.max(gb.normX, Math.min(gb.normX + gb.normW, parseFloat(ledsList[i].x.toFixed(4))));
            ledsList[i].y = Math.max(gb.normY, Math.min(gb.normY + gb.normH, parseFloat(ledsList[i].y.toFixed(4))));
        }
    }
}

canvas.addEventListener('mousemove', (e) => {
    if (currentView === 'fleet') {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const mx = (e.clientX - rect.left) * scaleX;
        const my = (e.clientY - rect.top) * scaleY;

        const w = canvas.width;
        const h = canvas.height;
        const marginX = w * 0.025;
        const usableW = w - marginX * 2;
        const slotW = usableW / 7;
        const shirtW = Math.floor(slotW * 0.88);
        const shirtH = Math.floor(shirtW * 1.25);
        const shirtY = h * 0.25;

        let hitRunner = -1;
        for (let i = 0; i < 7; i++) {
            const rx = marginX + i * slotW + (slotW - shirtW) / 2;
            if (mx >= rx - 4 && mx <= rx + shirtW + 4 && my >= shirtY - 26 && my <= shirtY + shirtH + 115) {
                hitRunner = i;
                break;
            }
        }
        fleetHoveredRunner = hitRunner;
        canvas.style.cursor = (hitRunner !== -1) ? 'pointer' : 'default';
        return;
    }
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

        if (multiDragStartNorm) {
            const dx = norm.x - multiDragStartNorm.x;
            const dy = norm.y - multiDragStartNorm.y;

            for (const [idx, initialPos] of multiDragInitialPositions.entries()) {
                if (leds[idx]) {
                    leds[idx].x = Math.max(0.05, Math.min(0.95, parseFloat((initialPos.x + dx).toFixed(4))));
                    leds[idx].y = Math.max(0.05, Math.min(0.95, parseFloat((initialPos.y + dy).toFixed(4))));
                }
            }

            // Sync symmetrical partner movement (dx is inverted across centerline)
            if (params.liveSymmetryDrag && liveSymmetryPartners.size > 0) {
                for (const [pIdx, pInit] of liveSymmetryPartners.entries()) {
                    if (leds[pIdx]) {
                        leds[pIdx].x = Math.max(0.05, Math.min(0.95, parseFloat((pInit.x - dx).toFixed(4))));
                        leds[pIdx].y = Math.max(0.05, Math.min(0.95, parseFloat((pInit.y + dy).toFixed(4))));
                    }
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
            const clamped = clampLedNoCollarOverlap(norm.x, norm.y, draggedLed, leds);
            leds[draggedLed].x = clamped.x;
            leds[draggedLed].y = clamped.y;
        }

        updateLedInspectorCoords();
        if (params.showWireTension || params.showWiring) {
            updateWireTensionUI();
        }
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
            for (const [idx] of multiDragInitialPositions.entries()) {
                if (leds[idx] && typeof sampleColorAtNormCoord === 'function') {
                    const newCol = sampleColorAtNormCoord(leds[idx].x, leds[idx].y);
                    if (newCol) leds[idx].color = newCol;
                }
            }
            if (params.liveSymmetryDrag && liveSymmetryPartners.size > 0) {
                for (const [pIdx] of liveSymmetryPartners.entries()) {
                    if (leds[pIdx] && typeof sampleColorAtNormCoord === 'function') {
                        const newCol = sampleColorAtNormCoord(leds[pIdx].x, leds[pIdx].y);
                        if (newCol) leds[pIdx].color = newCol;
                    }
                }
            }
            updateLedInspectorUI();
            if (params.showWireTension || params.showWiring) {
                updateWireTensionUI();
            }
            markSingleShirtDirty();
            if (preDragStateSnapshot) {
                undoStack.push(preDragStateSnapshot);
                if (undoStack.length > MAX_UNDO_HISTORY) undoStack.shift();
                redoStack = [];
                updateUndoRedoUI();
                preDragStateSnapshot = null;
            }
        } else {
            preDragStateSnapshot = null;
        }
        isDraggingLed = false;
        draggedLed = null;
        multiDragStartNorm = null;
        multiDragInitialPositions.clear();
        liveSymmetryPartners.clear();
        canvas.classList.remove('dragging');
    }
});

canvas.addEventListener('dblclick', (e) => {
    if (currentView === 'fleet' && fleetHoveredRunner !== -1) {
        editRunnerInSingleView(fleetHoveredRunner);
    }
});

// ============================================================================
// MAIN ANIMATION LOOP
// ============================================================================
function animate(time) {
    updateSequenceTimeline(time);
    updateFleetShowTimeline(time);
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
            direction: params.direction || 1,
            speedBpm: params.speedBpm,
            sparkleRate: params.sparkleRate,
            sparkleStyle: params.sparkleStyle || 'incandescent',
            ambientColorMode: params.ambientColorMode || 'artwork',
            ambientCustomColor: params.ambientCustomColor || '#ffb703',
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

    // Cache local profile data and assign to active runner card slot
    fleetPresetCache['local:' + cleanName] = profileData;
    if (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && fleetRunners[activeSingleShirtRunnerSlot]) {
        fleetRunners[activeSingleShirtRunnerSlot].preset = 'local:' + cleanName;
        saveFleetLineupToStorage();
    }
    isSingleShirtDirty = false;

    // 2. Save to Python backend
    try {
        const res = await fetch('/api/save_preset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
        });
        if (res.ok) {
            const result = await res.json();
            if (result && result.filename) {
                fleetPresetCache['server:' + result.filename] = profileData;
                if (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && fleetRunners[activeSingleShirtRunnerSlot]) {
                    fleetRunners[activeSingleShirtRunnerSlot].preset = 'server:' + result.filename;
                    saveFleetLineupToStorage();
                }
            }
            showToast(`💾 Profile "${cleanName}" saved successfully to disk and browser!`);
        }
    } catch (e) {
        showToast(`💾 Profile "${cleanName}" saved to browser cache.`);
    }

    await refreshPresetDropdown();
    renderFleetCards();
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

    if (currentGraphicType === 'custom_image' || profileData.customArtworkDataUrl) {
        currentGraphicType = 'custom_image';
        customArtworkDataUrl = profileData.customArtworkDataUrl || null;
        if (customArtworkDataUrl) {
            const img = new Image();
            img.onload = () => {
                customArtworkImg = img;
            };
            img.src = customArtworkDataUrl;
        }
        if (graphicSelect) graphicSelect.value = 'custom_upload';
        if (uploadContainer) uploadContainer.style.display = 'block';
        if (resetBtn) resetBtn.style.display = 'block';
    } else {
        customArtworkImg = null;
        customArtworkDataUrl = null;
        if (uploadContainer) uploadContainer.style.display = 'none';
        if (resetBtn) resetBtn.style.display = (currentGraphicType === 'builtin_dragon' || currentGraphicType === 'petes_dragon') ? 'none' : 'block';
        if (graphicSelect) {
            let matched = false;
            for (let opt of graphicSelect.options) {
                if (opt.value === currentGraphicType) {
                    graphicSelect.value = currentGraphicType;
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                if (currentGraphicType === 'cinderella_coach') graphicSelect.value = 'cinderellas_coach';
                else if (currentGraphicType === 'petes_dragon') graphicSelect.value = 'builtin_dragon';
            }
        }
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
        if (s.direction !== undefined) {
            params.direction = parseInt(s.direction) || 1;
            const dirSel = document.getElementById('ambientDirectionSelect');
            if (dirSel) dirSel.value = params.direction.toString();
        }
        if (s.sparkleStyle !== undefined) {
            params.sparkleStyle = s.sparkleStyle;
            const spkStyleSel = document.getElementById('sparkleStyleSelect');
            if (spkStyleSel) spkStyleSel.value = s.sparkleStyle;
        }
        if (s.ambientColorMode !== undefined) {
            params.ambientColorMode = s.ambientColorMode;
            const modeSel = document.getElementById('ambientColorModeSelect');
            if (modeSel) modeSel.value = s.ambientColorMode;
            const customRow = document.getElementById('ambientCustomColorRow');
            if (customRow) customRow.style.display = (s.ambientColorMode === 'custom') ? 'flex' : 'none';
        }
        if (s.ambientCustomColor !== undefined) {
            params.ambientCustomColor = s.ambientCustomColor;
            const picker = document.getElementById('ambientCustomColorPicker');
            if (picker) picker.value = s.ambientCustomColor;
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
        animationGroups = profileData.animationGroups.map(g => {
            const arr = Array.isArray(g.ledIndices) ? g.ledIndices : (Array.isArray(g.indices) ? g.indices : []);
            return {
                ...g,
                ledIndices: arr,
                indices: arr
            };
        });
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
    isSingleShirtDirty = false;
    if (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && fleetRunners[activeSingleShirtRunnerSlot]) {
        fleetRunners[activeSingleShirtRunnerSlot].preset = sourceValue;
        saveFleetLineupToStorage();
        renderFleetCards();
    }
    showToast(`📂 Loaded "${profileData.name || 'Profile'}"`);
}

// Initial Preset Load: Cleanly load active runner's official preset without marking dirty
refreshPresetDropdown().then(() => {
    const startupRunner = (fleetRunners && fleetRunners[activeSingleShirtRunnerSlot])
        ? fleetRunners[activeSingleShirtRunnerSlot]
        : (DEFAULT_FLEET_ROSTER[activeSingleShirtRunnerSlot] || DEFAULT_FLEET_ROSTER[0]);
    const targetPreset = startupRunner.preset || 'server:casey_jr_train.json';

    loadProfile(targetPreset).then(() => {
        isSingleShirtDirty = false;
        const pSel = document.getElementById('presetSelect');
        if (pSel) pSel.value = targetPreset;
        updateActiveFloatUI(activeSingleShirtRunnerSlot);
    }).catch(() => {
        if (leds.length === 0) {
            initDefaultDragonLeds();
        }
        isSingleShirtDirty = false;
        updateActiveFloatUI(activeSingleShirtRunnerSlot);
    });
});
rebuildLedGroupMap();
renderActiveGroupsList();

// ============================================================================
// UI CONTROLS BINDING
// ============================================================================
document.getElementById('patternSelect').addEventListener('change', (e) => {
    activePattern = e.target.value;
    markSingleShirtDirty();
});

document.getElementById('ambientDirectionSelect')?.addEventListener('change', (e) => {
    params.direction = parseInt(e.target.value) || 1;
    markSingleShirtDirty();
});

document.getElementById('speedSlider').addEventListener('input', (e) => {
    params.speedBpm = parseInt(e.target.value);
    document.getElementById('speedVal').textContent = `${params.speedBpm} BPM`;
    markSingleShirtDirty();
});

document.querySelectorAll('.tempo-chip').forEach(btn => {
    btn.addEventListener('click', () => {
        const bpm = parseInt(btn.dataset.bpm);
        if (!isNaN(bpm)) {
            params.speedBpm = bpm;
            const slider = document.getElementById('speedSlider');
            if (slider) slider.value = bpm;
            const val = document.getElementById('speedVal');
            if (val) val.textContent = `${bpm} BPM`;
            markSingleShirtDirty();
        }
    });
});

document.getElementById('sparkleSlider').addEventListener('input', (e) => {
    params.sparkleRate = parseFloat(e.target.value);
    document.getElementById('sparkleVal').textContent = `${params.sparkleRate.toFixed(params.sparkleRate < 1 ? 2 : 1)}%`;
    markSingleShirtDirty();
});

document.querySelectorAll('.sparkle-chip').forEach(btn => {
    btn.addEventListener('click', () => {
        const rate = parseFloat(btn.dataset.rate);
        if (!isNaN(rate)) {
            params.sparkleRate = rate;
            const slider = document.getElementById('sparkleSlider');
            if (slider) slider.value = rate;
            const val = document.getElementById('sparkleVal');
            if (val) val.textContent = `${rate.toFixed(rate < 1 ? 2 : 1)}%`;
            markSingleShirtDirty();
        }
    });
});

document.getElementById('sparkleStyleSelect')?.addEventListener('change', (e) => {
    params.sparkleStyle = e.target.value;
    markSingleShirtDirty();
});

document.getElementById('ambientColorModeSelect')?.addEventListener('change', (e) => {
    params.ambientColorMode = e.target.value;
    const row = document.getElementById('ambientCustomColorRow');
    if (row) {
        row.style.display = (params.ambientColorMode === 'custom') ? 'flex' : 'none';
    }
    markSingleShirtDirty();
});

document.getElementById('ambientCustomColorPicker')?.addEventListener('input', (e) => {
    params.ambientCustomColor = e.target.value;
    markSingleShirtDirty();
});

document.getElementById('hueSlider')?.addEventListener('input', (e) => {
    params.greenHue = parseInt(e.target.value);
    const hv = document.getElementById('hueVal');
    if (hv) hv.textContent = `${params.greenHue}°`;
    markSingleShirtDirty();
});

document.getElementById('brightnessSlider').addEventListener('input', (e) => {
    params.brightness = parseInt(e.target.value);
    document.getElementById('brightVal').textContent = `${params.brightness}%`;
    markSingleShirtDirty();
});

document.getElementById('glowSlider').addEventListener('input', (e) => {
    params.glowSize = parseInt(e.target.value);
    document.getElementById('glowVal').textContent = `${params.glowSize}px`;
    markSingleShirtDirty();
});

document.getElementById('showWiringToggle').addEventListener('change', (e) => {
    params.showWiring = e.target.checked;
    updateWireTensionUI();
    markSingleShirtDirty();
});

document.getElementById('showPillSlotsToggle')?.addEventListener('change', (e) => {
    params.showPillSlots = e.target.checked;
    try { localStorage.setItem('msep_show_pill_slots', params.showPillSlots ? 'true' : 'false'); } catch (err) {}
    markSingleShirtDirty();
});

document.getElementById('showTpuWindowsToggle')?.addEventListener('change', (e) => {
    params.showTpuWindows = e.target.checked;
    try { localStorage.setItem('msep_show_tpu_windows', params.showTpuWindows ? 'true' : 'false'); } catch (err) {}
    markSingleShirtDirty();
});

document.getElementById('exportCricutSvgBtn')?.addEventListener('click', () => {
    exportCricutSvgWithPillSlots();
});

document.getElementById('showWireTensionToggle')?.addEventListener('change', (e) => {
    params.showWireTension = e.target.checked;
    updateWireTensionUI();
    markSingleShirtDirty();
});

document.getElementById('inspectMaxSpanBtn')?.addEventListener('click', () => {
    const metrics = calculateWireTensionMetrics();
    if (metrics.segments.length === 0) return;
    selectedLeds.clear();
    selectedLeds.add(metrics.maxSpanFrom);
    selectedLeds.add(metrics.maxSpanTo);
    selectedLed = metrics.maxSpanTo;
    updateLedInspectorUI();
    focusOnLed(metrics.maxSpanFrom);
    showToast(`🔍 Longest wire span: #${metrics.maxSpanFrom} → #${metrics.maxSpanTo} (${metrics.maxSpanCm.toFixed(1)} cm)`);
    markSingleShirtDirty();
});

document.getElementById('showSymmetryAxisToggle')?.addEventListener('change', (e) => {
    params.showSymmetryAxis = e.target.checked;
    markSingleShirtDirty();
});

document.getElementById('liveSymmetryDragToggle')?.addEventListener('change', (e) => {
    params.liveSymmetryDrag = e.target.checked;
});

document.getElementById('mirrorLeftToRightBtn')?.addEventListener('click', () => {
    mirrorLeftToRight();
});

document.getElementById('mirrorRightToLeftBtn')?.addEventListener('click', () => {
    mirrorRightToLeft();
});

document.getElementById('showNumbersToggle').addEventListener('change', (e) => {
    params.showNumbers = e.target.checked;
    markSingleShirtDirty();
});

const showBibToggle = document.getElementById('showBibToggle');
if (showBibToggle) {
    showBibToggle.addEventListener('change', (e) => {
        params.showBib = e.target.checked;
        const posRow = document.getElementById('bibPositionRow');
        const scaleRow = document.getElementById('bibScaleRow');
        if (posRow) posRow.style.display = e.target.checked ? 'flex' : 'none';
        if (scaleRow) scaleRow.style.display = e.target.checked ? 'flex' : 'none';
        markSingleShirtDirty();
    });
}

const bibYSlider = document.getElementById('bibYSlider');
if (bibYSlider) {
    bibYSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        params.bibYOffset = val / 100.0;
        const valBadge = document.getElementById('bibYVal');
        if (valBadge) valBadge.textContent = `${val}%`;
        markSingleShirtDirty();
    });
}

const bibScaleSlider = document.getElementById('bibScaleSlider');
if (bibScaleSlider) {
    bibScaleSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        params.bibScale = val / 100.0;
        const valBadge = document.getElementById('bibScaleVal');
        if (valBadge) valBadge.textContent = `${val}%`;
        markSingleShirtDirty();
    });
}

document.getElementById('resetLedsBtn').addEventListener('click', () => {
    recordHistory('Reset Layout');
    initDefaultDragonLeds();
    markSingleShirtDirty();
});

// View Toggle
document.getElementById('singleViewBtn').addEventListener('click', () => {
    currentView = 'single';
    document.getElementById('singleViewBtn').classList.add('active');
    document.getElementById('fleetViewBtn').classList.remove('active');
    const zt = document.querySelector('.zoom-toolbar');
    if (zt) zt.style.display = 'flex';
    updateActiveFloatUI(activeSingleShirtRunnerSlot);
    const activeTab = document.querySelector('.sidebar-tab-btn.active')?.getAttribute('data-tab');
    if (activeTab === 'tabFleet') {
        switchSidebarTab('tabLayout');
    } else {
        renderTimelineLayers();
        updateTimelinePlayBtn();
        updateTimelineScrubberUI();
    }
});

document.getElementById('fleetViewBtn').addEventListener('click', () => {
    currentView = 'fleet';
    document.getElementById('fleetViewBtn').classList.add('active');
    document.getElementById('singleViewBtn').classList.remove('active');
    const zt = document.querySelector('.zoom-toolbar');
    if (zt) zt.style.display = 'none';
    updateActiveFloatUI(activeSingleShirtRunnerSlot);
    switchSidebarTab('tabFleet');
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

// ============================================================================
// FEATURE 2: WIRE TENSION & PHYSICAL SPACING ENGINE
// ============================================================================
const SHIRT_PHYSICAL_WIDTH_CM = 18.0 * 2.54;
const SHIRT_PHYSICAL_HEIGHT_CM = 24.0 * 2.54;

function calculateWireTensionMetrics() {
    if (!leds || leds.length < 2) {
        return {
            totalLengthCm: 0,
            avgPitchCm: 0,
            maxSpanCm: 0,
            maxSpanFrom: 0,
            maxSpanTo: 0,
            overStretchedCount: 0,
            snugCount: 0,
            optimalCount: 0,
            foldingCount: 0,
            segments: []
        };
    }
    let totalLen = 0;
    let maxSpan = 0;
    let maxFrom = 0;
    let maxTo = 0;
    let overCount = 0;
    let snugCount = 0;
    let optimalCount = 0;
    let foldingCount = 0;
    const segments = [];

    // Calibrated for 10.0cm physical wire pitch:
    // Excessive fold: < 4.5 cm (leaves > 5.5cm excess slack requiring folding)
    // Optimal Sweet Spot: 4.5 cm to 8.5 cm (gentle curve, zero folds)
    // Snug: 8.5 cm to 9.2 cm (minimal slack)
    // Over-stretched Alert: > 9.2 cm (risks pulling or breaking 10.0cm wire)
    for (let i = 0; i < leds.length - 1; i++) {
        const p1 = leds[i];
        const p2 = leds[i + 1];
        const dx = (p2.x - p1.x) * SHIRT_PHYSICAL_WIDTH_CM;
        const dy = (p2.y - p1.y) * SHIRT_PHYSICAL_HEIGHT_CM;
        const dist = Math.hypot(dx, dy);
        totalLen += dist;
        if (dist > maxSpan) {
            maxSpan = dist;
            maxFrom = i;
            maxTo = i + 1;
        }

        let status = 'optimal';
        if (dist > 9.2) {
            status = 'alert';
            overCount++;
        } else if (dist > 8.5) {
            status = 'snug';
            snugCount++;
        } else if (dist < 4.5) {
            status = 'folding';
            foldingCount++;
        } else {
            status = 'optimal';
            optimalCount++;
        }
        segments.push({
            from: i,
            to: i + 1,
            distCm: dist,
            status: status
        });
    }

    return {
        totalLengthCm: totalLen,
        avgPitchCm: totalLen / (leds.length - 1),
        maxSpanCm: maxSpan,
        maxSpanFrom: maxFrom,
        maxSpanTo: maxTo,
        overStretchedCount: overCount,
        snugCount: snugCount,
        optimalCount: optimalCount,
        foldingCount: foldingCount,
        segments: segments
    };
}

function updateWireTensionUI() {
    const card = document.getElementById('wireTensionMetricsCard');
    if (!card) return;
    if (params.showWireTension || params.showWiring) {
        card.style.display = 'block';
    } else {
        card.style.display = 'none';
        return;
    }

    const metrics = calculateWireTensionMetrics();
    const totalLengthVal = document.getElementById('tensionTotalLengthVal');
    if (totalLengthVal) {
        const m = (metrics.totalLengthCm / 100.0).toFixed(2);
        totalLengthVal.textContent = `${metrics.totalLengthCm.toFixed(1)} cm (${m} m)`;
    }

    const avgPitchVal = document.getElementById('tensionAvgPitchVal');
    if (avgPitchVal) {
        avgPitchVal.textContent = `${metrics.avgPitchCm.toFixed(1)} cm`;
    }

    const maxSpanVal = document.getElementById('tensionMaxSpanVal');
    if (maxSpanVal) {
        maxSpanVal.textContent = `${metrics.maxSpanCm.toFixed(1)} cm (#${metrics.maxSpanFrom} → #${metrics.maxSpanTo})`;
    }

    const statusBadge = document.getElementById('tensionStatusBadge');
    if (statusBadge) {
        if (metrics.overStretchedCount > 0) {
            statusBadge.style.background = 'rgba(255, 51, 102, 0.2)';
            statusBadge.style.color = '#ff4d6d';
            statusBadge.style.borderColor = 'rgba(255, 51, 102, 0.5)';
            statusBadge.textContent = `⚠️ ${metrics.overStretchedCount} Taut (>9.2 cm)`;
        } else if (metrics.foldingCount > 10) {
            statusBadge.style.background = 'rgba(56, 189, 248, 0.15)';
            statusBadge.style.color = '#38bdf8';
            statusBadge.style.borderColor = 'rgba(56, 189, 248, 0.4)';
            statusBadge.textContent = `🔵 ${metrics.foldingCount} Fold (<4.5 cm)`;
        } else if (metrics.snugCount > 0) {
            statusBadge.style.background = 'rgba(255, 193, 7, 0.15)';
            statusBadge.style.color = '#ffb703';
            statusBadge.style.borderColor = 'rgba(255, 193, 7, 0.4)';
            statusBadge.textContent = `🟡 ${metrics.snugCount} Snug (8.5–9.2 cm)`;
        } else {
            statusBadge.style.background = 'rgba(0, 255, 136, 0.15)';
            statusBadge.style.color = '#00ff88';
            statusBadge.style.borderColor = 'rgba(0, 255, 136, 0.4)';
            statusBadge.textContent = `🟢 ${metrics.optimalCount} Optimal (10cm Slack)`;
        }
    }
}

// ============================================================================
// FEATURE 3: BILATERAL SYMMETRY & MIRRORING ENGINE
// ============================================================================
function mirrorLeftToRight() {
    if (!leds || leds.length === 0) return;
    recordHistory('Mirror Left to Right');

    const leftLeds = [];
    const centerLeds = [];

    for (let i = 0; i < leds.length; i++) {
        const l = leds[i];
        if (Math.abs(l.x - 0.50) <= 0.015) {
            centerLeds.push({ ...l, x: 0.50, origIdx: i });
        } else if (l.x < 0.50) {
            leftLeds.push({ ...l, origIdx: i });
        }
    }

    if (leftLeds.length === 0 && centerLeds.length === 0) {
        showToast('⚠️ No LEDs found on left half (x < 50%) to mirror');
        return;
    }

    // Sort left LEDs by Y (top to bottom), then X (left to right) for clean snake order
    leftLeds.sort((a, b) => a.y - b.y || a.x - b.x);

    const newLeds = [];
    // Add center LEDs first (up to remaining count)
    for (const cl of centerLeds) {
        if (newLeds.length < 100) {
            let col = { ...cl.color };
            if (typeof sampleColorAtNormCoord === 'function') {
                const sampled = sampleColorAtNormCoord(0.50, cl.y);
                if (sampled) col = sampled;
            }
            newLeds.push({ x: 0.50, y: cl.y, color: col });
        }
    }

    const availableSlots = 100 - newLeds.length;
    const maxPairs = Math.floor(availableSlots / 2);
    const pairsToTake = Math.min(leftLeds.length, maxPairs);

    for (let i = 0; i < pairsToTake; i++) {
        const left = leftLeds[i];
        const rightX = parseFloat((1.0 - left.x).toFixed(4));
        let leftCol = { ...left.color };
        let rightCol = { ...left.color };
        if (typeof sampleColorAtNormCoord === 'function') {
            const sampledL = sampleColorAtNormCoord(left.x, left.y);
            if (sampledL) leftCol = sampledL;
            const sampledR = sampleColorAtNormCoord(rightX, left.y);
            if (sampledR) rightCol = sampledR;
        }
        newLeds.push({ x: left.x, y: left.y, color: leftCol });
        newLeds.push({ x: rightX, y: left.y, color: rightCol });
    }

    leds = newLeds;
    if (typeof sparkles !== 'undefined' && Array.isArray(sparkles)) {
        while (sparkles.length < leds.length) sparkles.push(0);
    }

    updateLedCountUI();
    rebuildLedGroupMap();
    markSingleShirtDirty();
    showToast(`🪞 Mirrored Left to Right: ${leds.length} symmetrical LEDs created!`);
}

function mirrorRightToLeft() {
    if (!leds || leds.length === 0) return;
    recordHistory('Mirror Right to Left');

    const rightLeds = [];
    const centerLeds = [];

    for (let i = 0; i < leds.length; i++) {
        const l = leds[i];
        if (Math.abs(l.x - 0.50) <= 0.015) {
            centerLeds.push({ ...l, x: 0.50, origIdx: i });
        } else if (l.x > 0.50) {
            rightLeds.push({ ...l, origIdx: i });
        }
    }

    if (rightLeds.length === 0 && centerLeds.length === 0) {
        showToast('⚠️ No LEDs found on right half (x > 50%) to mirror');
        return;
    }

    // Sort right LEDs by Y (top to bottom), then X (right to left)
    rightLeds.sort((a, b) => a.y - b.y || b.x - a.x);

    const newLeds = [];
    for (const cl of centerLeds) {
        if (newLeds.length < 100) {
            let col = { ...cl.color };
            if (typeof sampleColorAtNormCoord === 'function') {
                const sampled = sampleColorAtNormCoord(0.50, cl.y);
                if (sampled) col = sampled;
            }
            newLeds.push({ x: 0.50, y: cl.y, color: col });
        }
    }

    const availableSlots = 100 - newLeds.length;
    const maxPairs = Math.floor(availableSlots / 2);
    const pairsToTake = Math.min(rightLeds.length, maxPairs);

    for (let i = 0; i < pairsToTake; i++) {
        const right = rightLeds[i];
        const leftX = parseFloat((1.0 - right.x).toFixed(4));
        let leftCol = { ...right.color };
        let rightCol = { ...right.color };
        if (typeof sampleColorAtNormCoord === 'function') {
            const sampledL = sampleColorAtNormCoord(leftX, right.y);
            if (sampledL) leftCol = sampledL;
            const sampledR = sampleColorAtNormCoord(right.x, right.y);
            if (sampledR) rightCol = sampledR;
        }
        newLeds.push({ x: leftX, y: right.y, color: leftCol });
        newLeds.push({ x: right.x, y: right.y, color: rightCol });
    }

    leds = newLeds;
    if (typeof sparkles !== 'undefined' && Array.isArray(sparkles)) {
        while (sparkles.length < leds.length) sparkles.push(0);
    }

    updateLedCountUI();
    rebuildLedGroupMap();
    markSingleShirtDirty();
    showToast(`🪞 Mirrored Right to Left: ${leds.length} symmetrical LEDs created!`);
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
    updateWireTensionUI();
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
        if (selectedLeds.size === 0 && selectedLed === null) {
            if (leds.length > 0) selectLed(0);
            else return;
        }
        const r = parseInt(btn.getAttribute('data-r'), 10);
        const g = parseInt(btn.getAttribute('data-g'), 10);
        const b = parseInt(btn.getAttribute('data-b'), 10);
        setSelectedLedColor(r, g, b);

        const activeGrp = selectedGroupId ? animationGroups.find(g => g.id === selectedGroupId) : null;
        if (selectedLeds.size > 1) {
            const label = activeGrp ? `group "${activeGrp.name}"` : `${selectedLeds.size} LEDs`;
            showToast(`🎨 Set ${selectedLeds.size} LEDs in ${label} to ${btn.title}!`);
        } else {
            showToast(`🎨 Set LED #${selectedLed} to ${btn.title}!`);
        }
    });
});

document.getElementById('resetGroupArtworkColorBtnHub')?.addEventListener('click', () => {
    if (selectedLeds.size === 0 && (selectedLed === null || !leds[selectedLed])) {
        showToast("⚠️ Select a group or LEDs to restore artwork colors.", "warning");
        return;
    }
    const targetIndices = selectedLeds.size > 0 ? Array.from(selectedLeds) : [selectedLed];
    let restored = 0;
    targetIndices.forEach(idx => {
        if (leds[idx]) {
            const col = sampleColorAtNorm(leds[idx].x, leds[idx].y) || { r: 255, g: 255, b: 255 };
            leds[idx].color = col;
            restored++;
        }
    });

    if (selectedGroupId) {
        const activeGrp = animationGroups.find(g => g.id === selectedGroupId);
        if (activeGrp) {
            activeGrp.colorMode = 'original';
            activeGrp.customColor = null;
        }
    }

    const ref = selectedLed !== null ? selectedLed : targetIndices[0];
    if (leds[ref]?.color) {
        updateLedInspectorColorInputs(leds[ref].color.r, leds[ref].color.g, leds[ref].color.b);
    }
    updateLedInspectorUI();
    showToast(`🎨 Restored original artwork colors for ${restored} LEDs!`);
});

function applyGroupCustomColor(hex) {
    if (!hex) return;
    const rgb = hexToRgb(hex);
    if (!rgb) return;
    if (selectedLeds.size === 0 && (selectedLed === null || !leds[selectedLed])) {
        if (leds.length > 0) selectLed(0);
        else return;
    }
    setSelectedLedColor(rgb.r, rgb.g, rgb.b);
    if (selectedGroupId) {
        const activeGrp = animationGroups.find(g => g.id === selectedGroupId);
        if (activeGrp) {
            activeGrp.colorMode = 'custom';
            activeGrp.customColor = rgb;
        }
    }
    const label = selectedGroupId ? `group` : `${selectedLeds.size || 1} LEDs`;
    showToast(`🎨 Applied custom color ${hex.toUpperCase()} to ${label}`);
}

const grpCustomPickerHub = document.getElementById('groupCustomColorPickerHub');
if (grpCustomPickerHub) {
    grpCustomPickerHub.addEventListener('input', (e) => {
        const hex = e.target.value;
        const lbl = document.getElementById('groupCustomColorHexLabelHub');
        if (lbl) lbl.textContent = hex.toUpperCase();
    });
    grpCustomPickerHub.addEventListener('change', (e) => {
        applyGroupCustomColor(e.target.value);
    });
}

const grpCustomPickerInspector = document.getElementById('groupCustomColorPickerInspector');
if (grpCustomPickerInspector) {
    grpCustomPickerInspector.addEventListener('input', (e) => {
        const hex = e.target.value;
        const lbl = document.getElementById('groupCustomColorHexLabelInspector');
        if (lbl) lbl.textContent = hex.toUpperCase();
    });
    grpCustomPickerInspector.addEventListener('change', (e) => {
        applyGroupCustomColor(e.target.value);
    });
}

document.getElementById('resetGroupArtworkColorBtnInspector')?.addEventListener('click', () => {
    document.getElementById('resetGroupArtworkColorBtnHub')?.click();
});

// Group Tempo Quick Chips Listeners (Tab 3 Hub, Draw Mode & Inspector)
document.querySelectorAll('.grp-tempo-chip').forEach(btn => {
    btn.addEventListener('click', () => {
        const bpm = parseInt(btn.dataset.bpm, 10);
        const slider = document.getElementById('groupSpeedSliderHub');
        const badge = document.getElementById('groupSpeedValHub');
        if (slider) slider.value = bpm;
        if (badge) badge.textContent = `${bpm} BPM`;
        if (selectedGroupId) {
            const grp = animationGroups.find(g => g.id === selectedGroupId);
            if (grp) grp.speedBpm = bpm;
        }
        markSingleShirtDirty();
        showToast(`⚡ Set group speed to ${bpm} BPM`);
    });
});

document.querySelectorAll('.draw-grp-tempo-chip').forEach(btn => {
    btn.addEventListener('click', () => {
        const bpm = parseInt(btn.dataset.bpm, 10);
        const slider = document.getElementById('drawGroupSpeedSlider');
        const badge = document.getElementById('drawGroupSpeedVal');
        if (slider) slider.value = bpm;
        if (badge) badge.textContent = `${bpm} BPM`;
        markSingleShirtDirty();
        showToast(`⚡ Set drawn group speed to ${bpm} BPM`);
    });
});

document.querySelectorAll('.grp-tempo-chip-inspector').forEach(btn => {
    btn.addEventListener('click', () => {
        const bpm = parseInt(btn.dataset.bpm, 10);
        const slider = document.getElementById('groupSpeedSlider');
        const badge = document.getElementById('groupSpeedVal');
        if (slider) slider.value = bpm;
        if (badge) badge.textContent = `${bpm} BPM`;
        if (selectedGroupId) {
            const grp = animationGroups.find(g => g.id === selectedGroupId);
            if (grp) grp.speedBpm = bpm;
        }
        markSingleShirtDirty();
        showToast(`⚡ Set group tempo to ${bpm} BPM`);
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
document.getElementById('undoBtn')?.addEventListener('click', () => undo());
document.getElementById('redoBtn')?.addEventListener('click', () => redo());

// Inspector Multi-Selection Action Bar Bindings
document.getElementById('inspectorSelectAllBtn')?.addEventListener('click', () => selectAllLeds());
document.getElementById('inspectorInvertBtn')?.addEventListener('click', () => invertLedSelection());
document.getElementById('inspectorClearBtn')?.addEventListener('click', () => deselectLed());

// Group Animation Controls Bindings
document.getElementById('applyGroupEffectBtn')?.addEventListener('click', () => applyGroupEffectToSelection());
document.getElementById('removeGroupEffectBtn')?.addEventListener('click', () => removeGroupEffectFromSelection());

// Group Spatial Transformations & Clipboard Bindings
document.getElementById('pasteGroupHeaderBtn')?.addEventListener('click', () => pasteGroup());
document.getElementById('inspectorCopyGroupBtn')?.addEventListener('click', () => copyGroup());
document.getElementById('inspectorPasteGroupBtn')?.addEventListener('click', () => pasteGroup());
document.getElementById('inspectorRotate90Btn')?.addEventListener('click', () => rotateGroup(null, 90));
document.getElementById('inspectorFlipHBtn')?.addEventListener('click', () => flipGroupHorizontal());
document.getElementById('inspectorFlipVBtn')?.addEventListener('click', () => flipGroupVertical());
document.getElementById('inspectorScaleDownBtn')?.addEventListener('click', () => {
    scaleGroup(null, 0.90);
    const slider = document.getElementById('inspectorScaleSlider');
    const val = document.getElementById('inspectorScaleVal');
    if (slider) slider.value = 90;
    if (val) val.textContent = '90%';
});
document.getElementById('inspectorScaleUpBtn')?.addEventListener('click', () => {
    scaleGroup(null, 1.10);
    const slider = document.getElementById('inspectorScaleSlider');
    const val = document.getElementById('inspectorScaleVal');
    if (slider) slider.value = 110;
    if (val) val.textContent = '110%';
});

const inspectorScaleSlider = document.getElementById('inspectorScaleSlider');
let prevScaleVal = 100;
inspectorScaleSlider?.addEventListener('input', (e) => {
    const curVal = parseInt(e.target.value, 10);
    const valBadge = document.getElementById('inspectorScaleVal');
    if (valBadge) valBadge.textContent = `${curVal}%`;
});
inspectorScaleSlider?.addEventListener('change', (e) => {
    const curVal = parseInt(e.target.value, 10);
    const factor = curVal / prevScaleVal;
    scaleGroup(null, factor);
    prevScaleVal = curVal;
});

// Load persistent group clipboard state on startup
loadGroupClipboardFromStorage();

// Group Creation Hub & Navigation Bindings
document.getElementById('goToGroupsTabBtn')?.addEventListener('click', () => {
    if (typeof switchSidebarTab === 'function') switchSidebarTab('tabGroups');
});

document.getElementById('directorGoToFleetBtn')?.addEventListener('click', () => {
    if (typeof switchSidebarTab === 'function') switchSidebarTab('tabFleet');
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

// Bidirectional Group Form Synchronization (Hub <-> Docked Inspector)
const nameHub = document.getElementById('groupNameInputHub');
const nameDoc = document.getElementById('groupNameInput');
const syncGroupName = (val) => {
    if (nameHub && nameHub.value !== val) nameHub.value = val;
    if (nameDoc && nameDoc.value !== val) nameDoc.value = val;
    const saveHubBtn = document.getElementById('saveSelectionGroupBtnHub');
    const applyBtn = document.getElementById('applyGroupEffectBtn');
    const btnText = selectedGroupId ? `💾 Update Group "${val.trim() || 'Group'}"` : `💾 Save Selection as Group`;
    if (saveHubBtn) saveHubBtn.innerHTML = btnText;
    if (applyBtn) applyBtn.innerHTML = btnText;
};
nameHub?.addEventListener('input', (e) => syncGroupName(e.target.value));
nameDoc?.addEventListener('input', (e) => syncGroupName(e.target.value));

const effHub = document.getElementById('groupEffectSelectHub');
const effDoc = document.getElementById('groupEffectSelect');
const syncGroupEffect = (val) => {
    if (effHub && effHub.value !== val) effHub.value = val;
    if (effDoc && effDoc.value !== val) effDoc.value = val;
    const row = document.getElementById('groupFwRadiusRow');
    if (row) {
        const isFw = val === 'fireworks';
        row.style.display = isFw ? 'block' : 'none';
        if (isFw) {
            const fwGrp = typeof getActiveFireworksGroup === 'function' ? getActiveFireworksGroup() : null;
            if (fwGrp) syncFireworksSliders(fwGrp.centerNormX, fwGrp.centerNormY, fwGrp.burstRadius, fwGrp.fireworkColor);
        }
    }
};
effHub?.addEventListener('change', (e) => syncGroupEffect(e.target.value));
effDoc?.addEventListener('change', (e) => syncGroupEffect(e.target.value));

const spdHub = document.getElementById('groupSpeedSliderHub');
const spdDoc = document.getElementById('groupSpeedSlider');
const spdValHub = document.getElementById('groupSpeedValHub');
const spdValDoc = document.getElementById('groupSpeedVal');
const syncGroupSpeed = (val) => {
    if (spdHub && spdHub.value !== String(val)) spdHub.value = val;
    if (spdDoc && spdDoc.value !== String(val)) spdDoc.value = val;
    if (spdValHub) spdValHub.textContent = `${val} BPM`;
    if (spdValDoc) spdValDoc.textContent = `${val} BPM`;
};
spdHub?.addEventListener('input', (e) => syncGroupSpeed(e.target.value));
spdDoc?.addEventListener('input', (e) => syncGroupSpeed(e.target.value));

const dirHub = document.getElementById('groupDirectionSelectHub');
const dirDoc = document.getElementById('groupDirectionSelect');
const syncGroupDir = (val) => {
    if (dirHub && dirHub.value !== String(val)) dirHub.value = val;
    if (dirDoc && dirDoc.value !== String(val)) dirDoc.value = val;
};
dirHub?.addEventListener('change', (e) => syncGroupDir(e.target.value));
dirDoc?.addEventListener('change', (e) => syncGroupDir(e.target.value));

const baseHub = document.getElementById('groupBaselineSelectHub');
const baseDoc = document.getElementById('groupBaselineSelect');
const syncGroupBaseline = (val) => {
    if (baseHub && baseHub.value !== val) baseHub.value = val;
    if (baseDoc && baseDoc.value !== val) baseDoc.value = val;
};
baseHub?.addEventListener('change', (e) => syncGroupBaseline(e.target.value));
baseDoc?.addEventListener('change', (e) => syncGroupBaseline(e.target.value));

// Phase Offset & Sync Synchronization (Feature 8)
const phaseHub = document.getElementById('groupPhaseSliderHub');
const phaseValHub = document.getElementById('groupPhaseValHub');
const syncPhaseVal = (val) => {
    const num = parseInt(val, 10);
    if (phaseHub && phaseHub.value !== String(num)) phaseHub.value = num;
    if (phaseValHub) {
        let label = `${num}°`;
        if (num === 0) label += ' (Synced)';
        else if (num === 90) label += ' (Quarter)';
        else if (num === 180) label += ' (Anti-Phase)';
        else if (num === 270) label += ' (3/4 Phase)';
        phaseValHub.textContent = label;
    }
    if (selectedGroupId) {
        const grp = animationGroups.find(g => g.id === selectedGroupId);
        if (grp) {
            grp.phaseOffsetDeg = num;
            renderActiveGroupsList();
            markSingleShirtDirty();
        }
    }
};
phaseHub?.addEventListener('input', (e) => syncPhaseVal(e.target.value));

document.querySelectorAll('.grp-phase-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const deg = parseInt(btn.getAttribute('data-deg') || '0', 10);
        syncPhaseVal(deg);
    });
});

const syncSelectHub = document.getElementById('groupSyncWithSelectHub');
syncSelectHub?.addEventListener('change', (e) => {
    const masterId = e.target.value || null;
    if (selectedGroupId) {
        const grp = animationGroups.find(g => g.id === selectedGroupId);
        if (grp) {
            grp.syncWithGroupId = masterId;
            renderActiveGroupsList();
            markSingleShirtDirty();
            if (masterId) {
                const parent = animationGroups.find(g => g.id === masterId);
                if (parent) showToast(`🔗 Linked "${grp.name}" tempo to "${parent.name}"!`);
            }
        }
    }
});

function autoStaggerPhaseAcrossGroups() {
    if (!animationGroups || animationGroups.length === 0) {
        showToast('⚠️ No animation groups to stagger. Create groups first!');
        return;
    }
    if (animationGroups.length === 1) {
        animationGroups[0].phaseOffsetDeg = 0;
        showToast('ℹ️ 1 group: Phase set to 0° (In-Phase)');
        renderActiveGroupsList();
        if (selectedGroupId === animationGroups[0].id) {
            populateGroupForm(animationGroups[0]);
        }
        markSingleShirtDirty();
        return;
    }

    recordHistory('Auto-Stagger Group Phases');

    const step = Math.round(360 / animationGroups.length);
    animationGroups.forEach((grp, idx) => {
        grp.phaseOffsetDeg = (idx * step) % 360;
    });

    renderActiveGroupsList();
    if (selectedGroupId) {
        const sel = animationGroups.find(g => g.id === selectedGroupId);
        if (sel) populateGroupForm(sel);
    }
    markSingleShirtDirty();
    showToast(`🔀 Auto-staggered ${animationGroups.length} groups evenly (${step}° step: 0°, ${step}°...)!`);
}

document.getElementById('autoStaggerPhaseBtn')?.addEventListener('click', () => autoStaggerPhaseAcrossGroups());

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

const drawRearrangeCb = document.getElementById('drawAutoRearrangeCheckbox');
const canvasRearrangeCb = document.getElementById('canvasDrawAutoRearrangeCheckbox');
drawRearrangeCb?.addEventListener('change', (e) => {
    if (canvasRearrangeCb) canvasRearrangeCb.checked = e.target.checked;
});
canvasRearrangeCb?.addEventListener('change', (e) => {
    if (drawRearrangeCb) drawRearrangeCb.checked = e.target.checked;
});

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
    // If user uploaded a custom graphic, selected Cinderella's Coach, Carriage (No Horses), Spinning Turtle, or Spinning Snail, preserve and boost authentic colors!
    if (currentGraphicType === 'custom_image' || currentGraphicType === 'cinderellas_coach' || currentGraphicType === 'carriage_nohorses' || currentGraphicType === 'spinning_turtle' || currentGraphicType === 'spinning_snail') {
        return boostCustomImageColor(r, g, b);
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

    const maxVal = Math.max(r, g, b);
    const isPeteDragon = (currentGraphicType === 'builtin_dragon' || currentGraphicType === 'petes_dragon');
    const DISNEY_DRAGON_PINK = { r: 255, g: 25, b: 230 }; // #ff19e6 / FastLED CRGB(255, 25, 230)

    // --- RULE 1: Any Green Pixel (Light, Medium, or Dark) MUST ALWAYS Resolve to Vibrant Dragon Green ---
    // A green pixel (dominant green channel or hue in yellow-green to cyan-green 55°-180°) must NEVER sample as pink!
    const isGreenPixel = (g > r && g > b) || (hue >= 55 && hue <= 180);
    if (isGreenPixel) {
        // Dark contour / scale shadow on green body (< 60):
        if (maxVal < 60) {
            return { r: 15, g: 255, b: 35 };
        }
        // Lime Green / Yellow-Green Underbelly (Hue 55° to 95°):
        if (hue >= 55 && hue < 95) {
            const rLed = Math.min(100, Math.max(50, Math.round(r * 0.7)));
            return { r: rLed, g: 255, b: 15 };
        }
        // Emerald Dragon Green Body (Hue 95° to 180°, or standard dragon green scale):
        return {
            r: Math.min(40, Math.max(10, Math.round(r * 0.3))),
            g: 255,
            b: Math.min(60, Math.max(25, Math.round(b * 0.4)))
        };
    }

    // --- RULE 2: Pete's Dragon Authentic Disney Pink Features (Hair Crest, Wings, Dorsal Plates & Tail Spines) ---
    // Only non-green pixels reach this section!
    if (isPeteDragon) {
        // Genuinely pink/magenta hue (hue in 255°-360° or 0°-45°) with dominant red or blue over green
        const isPinkHue = (hue >= 255 || hue <= 45) && (r > g || b > g || delta > 0.08);

        // 1. Wild jagged hair crest on head (top)
        if (relY !== undefined && relY < 0.16 && relX > 0.25 && relX < 0.75 && (r > g || b > g || isPinkHue)) {
            return DISNEY_DRAGON_PINK;
        }

        // 2. Cute little dragon wings (upper chest/back left & right flanks)
        if (relY !== undefined && relY >= 0.20 && relY <= 0.58 &&
            ((relX >= 0.20 && relX <= 0.45) || (relX >= 0.58 && relX <= 0.94)) && isPinkHue) {
            return DISNEY_DRAGON_PINK;
        }

        // 3. Spines on the tail (running down back into sweeping tail)
        if (relY !== undefined && relY >= 0.58 && relX >= 0.65 && isPinkHue) {
            return DISNEY_DRAGON_PINK;
        }

        // 4. Dorsal spine spikes along upper back curve
        if (relY !== undefined && relY >= 0.18 && relY <= 0.65 && relX >= 0.55 && relX <= 0.88 && isPinkHue) {
            return DISNEY_DRAGON_PINK;
        }
    }

    // 5. General Wings / Pink / Magenta / Violet Hue:
    // Electric Disney Hot Pink: equal punch on Red & Blue with minimal green
    if ((hue >= 260 || hue <= 25) && (r > g + 4 || b > g)) {
        return DISNEY_DRAGON_PINK;
    }

    // --- Pete's Dragon Dark Line Art / Shadow Enhancement ---
    // If pixel is near-black contour or dark shadow (< 60):
    if (maxVal < 60) {
        if (r > g || b > g) {
            return DISNEY_DRAGON_PINK;
        }
        return { r: 15, g: 255, b: 35 };
    }

    // 6. Orange / Red (Hue 15° to 55°):
    if (hue > 15 && hue < 55 && r > g + 15) {
        return { r: 255, g: 120, b: 0 };
    }

    // 7. Lime Green / Yellow-Green Underbelly (Hue 55° to 95°):
    if (hue >= 55 && hue < 95) {
        const rLed = Math.min(100, Math.max(50, Math.round(r * 0.7)));
        return { r: rLed, g: 255, b: 15 };
    }

    // 8. Cyan / Sky Blue (Hue 175° to 260°):
    if (hue >= 175 && hue < 260) {
        const gLed = Math.min(220, Math.max(80, Math.round(g * 0.9)));
        return { r: 0, g: gLed, b: 255 };
    }

    // 9. Emerald Dragon Green Body Fallback:
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
// CONTINUOUS PHYSICAL WIRING ROUTING (Slack-Targeted for 10cm Physical Wire Pitch)
// Sorts and renumbers LEDs so consecutive hops (LED[i] -> LED[i+1]) maintain the ideal
// ~6.0cm to 8.0cm span on the garment, leaving gentle ~2-4cm natural slack (ZERO folding)!
// ============================================================================
function optimizeLedWiringOrder(points, startCorner = 'bottom-left') {
    if (!points || points.length <= 2) return points;

    const n = points.length;

    // Physical garment scale (18.0" wide x 24.0" high converted to cm)
    const W_CM = 18.0 * 2.54; // 45.72 cm
    const H_CM = 24.0 * 2.54; // 60.96 cm
    const TARGET_CM = 6.8;    // Ideal 10cm wire span on shirt (~3.2cm gentle slack)
    const MAX_CM = 9.2;       // Maximum reach limit for 10cm physical wire
    const MIN_CM = 4.5;       // Folding penalty threshold (<4.5cm requires >5.5cm fold)

    // Distance helper in physical centimeters
    const distCm = (pA, pB) => {
        const dx = (pA.x - pB.x) * W_CM;
        const dy = (pA.y - pB.y) * H_CM;
        return Math.hypot(dx, dy);
    };

    // Cost function for a wire segment:
    // Heavily penalizes unreachable segments (>9.2cm) and excessive wire folding (<4.5cm).
    // Rewards sweet spot spans (4.5cm - 8.5cm, ~1.8" - 3.3") where wire hangs naturally with zero folds.
    const edgeCost = (d) => {
        if (d > MAX_CM) {
            return 1000.0 + (d - MAX_CM) * 50.0;
        } else if (d < MIN_CM) {
            return (MIN_CM - d) * (MIN_CM - d) * 4.0 + Math.abs(d - TARGET_CM);
        } else if (d > 8.5) {
            return (d - 8.5) * 3.0 + Math.abs(d - TARGET_CM);
        } else {
            return Math.abs(d - TARGET_CM);
        }
    };

    // 1. Pick starting LED (e.g. bottom-left near the waist / battery pack)
    let startIdx = 0;
    let bestScore = -Infinity;

    for (let i = 0; i < n; i++) {
        let score;
        const p = points[i];
        if (startCorner === 'bottom-left') {
            score = p.y * 1.5 - p.x;
        } else if (startCorner === 'bottom-center') {
            score = p.y * 1.5 - Math.abs(p.x - 0.5);
        } else if (startCorner === 'bottom-right') {
            score = p.y * 1.5 - (1.0 - p.x);
        } else { // top-left
            score = -p.y * 1.5 - p.x;
        }
        if (score > bestScore) {
            bestScore = score;
            startIdx = i;
        }
    }

    // 2. Slack-Targeted Tour Construction
    const unvisited = new Set();
    for (let i = 0; i < n; i++) {
        if (i !== startIdx) unvisited.add(i);
    }

    const path = [startIdx];
    while (unvisited.size > 0) {
        const curr = path[path.length - 1];
        let bestCand = -1;
        let bestC = Infinity;

        for (const idx of unvisited) {
            const d = distCm(points[curr], points[idx]);
            const c = edgeCost(d);
            if (c < bestC) {
                bestC = c;
                bestCand = idx;
            }
        }

        path.push(bestCand);
        unvisited.delete(bestCand);
    }

    // 3. Slack-Targeted 2-Opt Optimization Pass (eliminates folds & overstretched segments)
    let improved = true;
    let iterations = 0;
    while (improved && iterations < 50) {
        improved = false;
        iterations++;
        for (let i = 0; i < n - 2; i++) {
            for (let j = i + 2; j < n; j++) {
                const pI = points[path[i]];
                const pI1 = points[path[i + 1]];
                const pJ = points[path[j]];
                const pJ1 = (j < n - 1) ? points[path[j + 1]] : null;

                const cCur = edgeCost(distCm(pI, pI1)) + (pJ1 ? edgeCost(distCm(pJ, pJ1)) : 0);
                const cNew = edgeCost(distCm(pI, pJ)) + (pJ1 ? edgeCost(distCm(pI1, pJ1)) : 0);

                if (cNew < cCur - 1e-4) {
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

    return path.map(idx => points[idx]);
}

// ============================================================================
// REARRANGE REMAINING (NON-GROUPED) LEDs TO FILL GRAPHIC SPACE
// ============================================================================
// Uses Farthest-Point Sampling with existing grouped LEDs as fixed distance anchors
// so remaining LEDs evenly fill open spaces of the graphic without moving any groups.
function rearrangeRemainingLedsOnGraphic(showNotification = true) {
    if (!leds || leds.length === 0) return;

    if (showNotification) {
        recordHistory('Rearrange Remaining LEDs');
    }

    // 1. Identify all grouped LEDs vs unassigned LEDs
    const allGroupedIndices = new Set();
    animationGroups.forEach(g => {
        (g.ledIndices || []).forEach(idx => {
            if (idx >= 0 && idx < leds.length) {
                allGroupedIndices.add(idx);
            }
        });
    });

    const unassignedIndices = [];
    for (let i = 0; i < leds.length; i++) {
        if (!allGroupedIndices.has(i)) {
            unassignedIndices.push(i);
        }
    }

    if (unassignedIndices.length === 0) {
        if (showNotification) {
            showToast('🎉 All 100 LEDs are assigned to animation groups! No remaining LEDs to rearrange.', 'info');
        }
        return;
    }

    // 2. Prepare offscreen canvas to sample current character graphic
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
                if (currentGraphicType === 'builtin_dragon') {
                    isFg = (a > 80 && Math.max(r, g, b) >= 60);
                } else {
                    isFg = (a > 60);
                }
            } else if (isLightBg) {
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                const maxC = Math.max(r, g, b);
                const minC = Math.min(r, g, b);
                const satDelta = maxC - minC;
                isFg = (lum < 225 || satDelta > 25);
            } else if (isDarkBg) {
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

    const targetCount = unassignedIndices.length;
    if (candidates.length < targetCount) {
        showToast(`Graphic area is too small to distribute ${targetCount} LEDs!`, 'warning');
        return;
    }

    const gb = getGraphicChestBounds();
    const numCandidates = candidates.length;
    const minDist = new Float32Array(numCandidates);

    // 3. Anchor distances to existing grouped LEDs so remaining LEDs don't overlap with them
    if (allGroupedIndices.size > 0) {
        const groupedPixels = [];
        allGroupedIndices.forEach(idx => {
            const l = leds[idx];
            if (l) {
                const relX = (l.x - gb.normX) / gb.normW;
                const relY = (l.y - gb.normY) / gb.normH;
                groupedPixels.push({ px: relX * targetW, py: relY * targetH });
            }
        });

        for (let i = 0; i < numCandidates; i++) {
            let dMin = 1e9;
            const cx = candidates[i].x;
            const cy = candidates[i].y;
            for (let g = 0; g < groupedPixels.length; g++) {
                const dx = cx - groupedPixels[g].px;
                const dy = cy - groupedPixels[g].py;
                const d = dx * dx + dy * dy;
                if (d < dMin) dMin = d;
            }
            minDist[i] = dMin;
        }
    } else {
        const startIdx = Math.floor(numCandidates / 2);
        for (let i = 0; i < numCandidates; i++) {
            const dx = candidates[i].x - candidates[startIdx].x;
            const dy = candidates[i].y - candidates[startIdx].y;
            minDist[i] = dx * dx + dy * dy;
        }
    }

    // 4. Farthest Point Sampling to choose positions for all remaining LEDs
    const selected = [];
    for (let k = 0; k < targetCount; k++) {
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

    // 5. Convert selected pixel positions to normalized coordinates & color match
    const newPoints = [];
    for (let i = 0; i < selected.length; i++) {
        const p = selected[i];
        const relX = p.x / targetW;
        const relY = p.y / targetH;
        const normX = gb.normX + relX * gb.normW;
        const normY = gb.normY + relY * gb.normH;

        let col = { r: p.r, g: p.g, b: p.b };
        if (typeof boostLedVibrancy === 'function') {
            col = boostLedVibrancy(col.r, col.g, col.b, relX, relY);
        }

        newPoints.push({
            x: Math.max(0.05, Math.min(0.95, parseFloat(normX.toFixed(3)))),
            y: Math.max(0.05, Math.min(0.95, parseFloat(normY.toFixed(3)))),
            color: col
        });
    }

    // 5b. Relax any pocket collisions to ensure zero collar overlap
    relaxLedCollarOverlaps(newPoints, 35);

    // 6. Order the unassigned points along a continuous physical snake path
    const sortedPoints = optimizeLedWiringOrder(newPoints, 'bottom-left');

    // 7. Assign new coordinates and colors to unassigned LEDs
    for (let i = 0; i < unassignedIndices.length; i++) {
        const ledIdx = unassignedIndices[i];
        leds[ledIdx].x = sortedPoints[i].x;
        leds[ledIdx].y = sortedPoints[i].y;
        leds[ledIdx].color = sortedPoints[i].color;
    }

    while (sparkles.length < leds.length) sparkles.push(0);

    rebuildLedGroupMap();
    renderActiveGroupsList();
    updateLedInspectorUI();
    updateLedCountUI();
    markSingleShirtDirty();

    if (showNotification) {
        showToast(`✨ Evenly rearranged ${targetCount} remaining LEDs across the graphic!`);
    }
}

// SCATTER 100 LEDs (Farthest-Point Sampling inside graphic with pixel color matching)
function scatterLedsOnGraphic(targetCount = 100, colorMatch = true, markDirty = true) {
    if (markDirty) {
        recordHistory('Scatter LEDs on Graphic');
    }

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

    // Relax any pocket collisions to ensure zero collar overlap in 3D STL
    relaxLedCollarOverlaps(newLeds, 40);

    // Sort & renumber LEDs into a continuous physical wiring path (starts near waist / bottom-left)
    leds = optimizeLedWiringOrder(newLeds, 'bottom-left');
    while (sparkles.length < leds.length) sparkles.push(0);

    activePattern = 'steady_sparkle';
    const patSelect = document.getElementById('patternSelect');
    if (patSelect) patSelect.value = 'steady_sparkle';

    updateLedCountUI();
    if (markDirty) {
        markSingleShirtDirty();
        showToast(`🌈 ${targetCount} LEDs scattered & ordered along continuous wiring route!`);
    }
}

// OUTLINE 50 LEDs (Moore-Neighbor Clockwise Boundary Tracing)
function autoOutlineCurrentGraphic(targetCount = 50, markDirty = true) {
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
    if (markDirty) {
        markSingleShirtDirty();
        showToast(`✨ ${targetCount} LEDs redistributed along graphic outline!`);
    }
}

// Switch costume graphic preset (Pete's Dragon, Casey Jr., Cinderella's Coach, etc.)
async function loadGraphicPreset(type) {
    const uploadContainer = document.getElementById('customUploadContainer');
    const resetBtn = document.getElementById('resetArtworkBtn');
    const graphicSelect = document.getElementById('graphicPresetSelect');
    if (graphicSelect) graphicSelect.value = type;

    if (type === 'custom_upload') {
        if (uploadContainer) uploadContainer.style.display = 'block';
        if (resetBtn) resetBtn.style.display = customArtworkImg ? 'block' : 'none';
        if (customArtworkImg) {
            currentGraphicType = 'custom_image';
            scatterLedsOnGraphic(100, true);
        } else {
            const fileInput = document.getElementById('artworkUpload');
            if (fileInput) fileInput.click();
        }
        return;
    }

    currentGraphicType = type;
    customArtworkImg = null;
    customArtworkDataUrl = null;
    if (uploadContainer) uploadContainer.style.display = 'none';
    if (resetBtn) resetBtn.style.display = (type === 'builtin_dragon' || type === 'petes_dragon') ? 'none' : 'block';

    const presetFileMap = {
        'casey_jr_train': 'casey_jr_train.json',
        'title_drum': 'title_drum.json',
        'spinning_turtle': 'spinning_turtle.json',
        'spinning_snail': 'spinning_snail.json',
        'cinderellas_coach': 'cinderellas_coach_both_wheel.json',
        'cinderella_coach': 'cinderellas_coach_both_wheel.json',
        'carriage_nohorses': 'cinderellas_coach_both_wheel.json',
        'builtin_dragon': 'petes_dragon.json',
        'petes_dragon': 'petes_dragon.json',
        'honor_america_eagle': 'honor_america_eagle.json'
    };

    const presetFile = presetFileMap[type];
    if (presetFile) {
        try {
            const res = await fetch(`/api/preset/${presetFile}`);
            if (res.ok) {
                const profileData = await res.json();
                applyProfileData(profileData);
                isSingleShirtDirty = false;
                if (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && fleetRunners[activeSingleShirtRunnerSlot]) {
                    fleetRunners[activeSingleShirtRunnerSlot].preset = `server:${presetFile}`;
                    saveFleetLineupToStorage();
                    renderFleetCards();
                }
                const pSel = document.getElementById('presetSelect');
                if (pSel) pSel.value = `server:${presetFile}`;
                showToast(`✨ Loaded ${profileData.name || type} preset!`);
                return;
            }
        } catch (e) {
            console.warn("Could not fetch preset for", type, e);
        }
    }

    // Fallback if preset file not fetched or custom
    animationGroups = [];
    rebuildLedGroupMap();
    renderActiveGroupsList();
    scatterLedsOnGraphic(100, true);
    showToast(`🎨 Switched graphic to ${type.replace(/_/g, ' ')}!`);
}

// Graphic Preset Dropdown Handler
const graphicPresetSelect = document.getElementById('graphicPresetSelect');
if (graphicPresetSelect) {
    graphicPresetSelect.addEventListener('change', async (e) => {
        const val = e.target.value;
        if (val === 'custom_upload') {
            await loadGraphicPreset(val);
            return;
        }
        const floatToSlot = {
            'casey_jr_train': 0,
            'title_drum': 1,
            'spinning_turtle': 2,
            'spinning_snail': 3,
            'cinderellas_coach': 4,
            'cinderella_coach': 4,
            'carriage_nohorses': 4,
            'builtin_dragon': 5,
            'petes_dragon': 5,
            'honor_america_eagle': 6
        };
        const targetSlot = floatToSlot[val];
        if (targetSlot !== undefined && targetSlot !== activeSingleShirtRunnerSlot) {
            await editRunnerInSingleView(targetSlot);
            updateActiveFloatUI(activeSingleShirtRunnerSlot);
        } else {
            await loadGraphicPreset(val);
            updateActiveFloatUI(activeSingleShirtRunnerSlot);
        }
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
        markSingleShirtDirty();
        showToast(`🔌 Renumbered ${leds.length} LEDs along continuous physical wiring route!`);
    });
}

document.getElementById('scatterColorBtn')?.addEventListener('click', () => {
    scatterLedsOnGraphic(100, true);
});

document.getElementById('quick100Btn')?.addEventListener('click', () => {
    scatterLedsOnGraphic(100, true);
});

document.getElementById('autoOutlineBtn')?.addEventListener('click', () => {
    autoOutlineCurrentGraphic(50);
});

document.getElementById('quick50Btn')?.addEventListener('click', () => {
    autoOutlineCurrentGraphic(50);
});

document.getElementById('resampleColorsBtn')?.addEventListener('click', () => {
    resampleAllLedColors();
});

const resetArtworkBtn = document.getElementById('resetArtworkBtn');
if (resetArtworkBtn) {
    resetArtworkBtn.addEventListener('click', () => {
        const defaultMap = {
            0: 'casey_jr_train',
            1: 'title_drum',
            2: 'spinning_turtle',
            3: 'spinning_snail',
            4: 'cinderellas_coach',
            5: 'builtin_dragon',
            6: 'honor_america_eagle'
        };
        const defaultKey = defaultMap[activeSingleShirtRunnerSlot] || 'builtin_dragon';
        loadGraphicPreset(defaultKey);
    });
}

const rearrangeRemainingBtn = document.getElementById('rearrangeRemainingLedsBtn');
if (rearrangeRemainingBtn) {
    rearrangeRemainingBtn.addEventListener('click', () => {
        rearrangeRemainingLedsOnGraphic(true);
    });
}

const rearrangeRemainingBtn2 = document.getElementById('rearrangeRemainingLedsBtn2');
if (rearrangeRemainingBtn2) {
    rearrangeRemainingBtn2.addEventListener('click', () => {
        rearrangeRemainingLedsOnGraphic(true);
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
    recordHistory(`Delete Fireworks "${name}"`);
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
    markSingleShirtDirty();
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
    markSingleShirtDirty();

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

// ============================================================================
// PARAMETRIC SHAPE GENERATORS & SHAPE STAMP LIBRARY ENGINE
// ============================================================================
let currentSelectedStampShape = 'fireworks';
let isClickCanvasToPlaceActive = false;

function generateCirclePoints(cx, cy, radius, count, arcDegrees = 360, rotationDeg = 0) {
    const pts = [];
    const arcRad = (arcDegrees * Math.PI) / 180;
    const rotRad = (rotationDeg * Math.PI) / 180;
    const isClosed = (arcDegrees >= 360);
    const denom = isClosed ? count : Math.max(1, count - 1);

    for (let i = 0; i < count; i++) {
        const t = i / denom;
        const theta = rotRad - Math.PI / 2 + t * arcRad;
        const rx = radius * Math.cos(theta);
        const ry = (radius * Math.sin(theta)) / 1.25;
        pts.push({ x: cx + rx, y: cy + ry });
    }
    return pts;
}

function generateArchPoints(cx, cy, spanW, heightH, count, isInverted = false) {
    const pts = [];
    const mult = isInverted ? 1 : -1;
    for (let i = 0; i < count; i++) {
        const t = count > 1 ? i / (count - 1) : 0.5;
        const u = 2 * t - 1;
        const rx = u * (spanW / 2);
        const ry = mult * (1 - u * u) * (heightH / 1.25);
        pts.push({ x: cx + rx, y: cy + ry });
    }
    return pts;
}

function generateWavePoints(cx, cy, lengthL, amplitudeA, cycles, count, isVertical = false) {
    const pts = [];
    for (let i = 0; i < count; i++) {
        const t = count > 1 ? i / (count - 1) : 0.5;
        const offsetPrimary = (t - 0.5) * lengthL;
        const offsetSine = Math.sin(2 * Math.PI * cycles * t) * (amplitudeA / 1.25);
        if (isVertical) {
            pts.push({ x: cx + offsetSine, y: cy + offsetPrimary });
        } else {
            pts.push({ x: cx + offsetPrimary, y: cy + offsetSine });
        }
    }
    return pts;
}

function generateStarPoints(cx, cy, outerR, innerR, points = 5, totalCount = 10) {
    const vertices = [];
    const numVerts = points * 2;
    for (let i = 0; i < numVerts; i++) {
        const theta = -Math.PI / 2 + i * (Math.PI / points);
        const r = (i % 2 === 0) ? outerR : innerR;
        vertices.push({
            x: cx + r * Math.cos(theta),
            y: cy + (r * Math.sin(theta)) / 1.25
        });
    }

    const pts = [];
    const totalSegs = vertices.length;
    for (let i = 0; i < totalCount; i++) {
        const t = (i / totalCount) * totalSegs;
        const segIdx = Math.floor(t) % totalSegs;
        const nextIdx = (segIdx + 1) % totalSegs;
        const segT = t - Math.floor(t);
        const v1 = vertices[segIdx];
        const v2 = vertices[nextIdx];
        pts.push({
            x: v1.x + (v2.x - v1.x) * segT,
            y: v1.y + (v2.y - v1.y) * segT
        });
    }
    return pts;
}

function generateLinePoints(cx, cy, lengthL, angleDeg = 0, count = 8) {
    const pts = [];
    const rad = (angleDeg * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    for (let i = 0; i < count; i++) {
        const t = count > 1 ? i / (count - 1) : 0.5;
        const dist = (t - 0.5) * lengthL;
        const rx = dist * cos;
        const ry = (dist * sin) / 1.25;
        pts.push({ x: cx + rx, y: cy + ry });
    }
    return pts;
}

function stampSelectedShape(customCx = null, customCy = null) {
    if (currentSelectedStampShape === 'fireworks') {
        const rays = parseInt(document.getElementById('fwRaysSelect')?.value || '5', 10);
        const lpr = parseInt(document.getElementById('fwLedsPerRaySelect')?.value || '4', 10);
        const radPct = parseInt(document.getElementById('fwRadiusSlider')?.value || '13', 10);
        const burstRadius = radPct / 100;

        let cx = customCx !== null ? customCx : (parseInt(document.getElementById('fwPosXSlider')?.value || '28', 10) / 100);
        let cy = customCy !== null ? customCy : (parseInt(document.getElementById('fwPosYSlider')?.value || '22', 10) / 100);

        const colorVal = document.getElementById('fwColorSelect')?.value;
        const customPicker = document.getElementById('fwCustomColorPicker');
        const colorToUse = (colorVal === 'custom') ? (customPicker?.value || '#ffb703') : (colorVal || '#ffb703');

        recordHistory('Stamp Fireworks Starburst');
        generateFireworksCluster(cx, cy, rays, lpr, burstRadius, true, colorToUse);
        return;
    }

    let cx = customCx !== null ? customCx : (parseInt(document.getElementById('fwPosXSlider')?.value || '50', 10) / 100);
    let cy = customCy !== null ? customCy : (parseInt(document.getElementById('fwPosYSlider')?.value || '35', 10) / 100);
    const radPct = parseInt(document.getElementById('fwRadiusSlider')?.value || '13', 10);
    const sizeScale = radPct / 100;

    let pts = [];
    let shapeName = 'Shape';
    let reqCount = 10;

    if (currentSelectedStampShape === 'circle') {
        reqCount = parseInt(document.getElementById('stampCircleCount')?.value || '12', 10);
        const arc = parseInt(document.getElementById('stampCircleArc')?.value || '360', 10);
        shapeName = `Circle Wheel (${reqCount} LEDs)`;
        pts = generateCirclePoints(cx, cy, sizeScale, reqCount, arc);
    } else if (currentSelectedStampShape === 'arch') {
        reqCount = parseInt(document.getElementById('stampArchCount')?.value || '10', 10);
        const dir = document.getElementById('stampArchDir')?.value || 'up';
        shapeName = `Arch Canopy (${reqCount} LEDs)`;
        pts = generateArchPoints(cx, cy, sizeScale * 2.2, sizeScale * 1.2, reqCount, dir === 'down');
    } else if (currentSelectedStampShape === 'wave') {
        reqCount = parseInt(document.getElementById('stampWaveCount')?.value || '12', 10);
        const cycles = parseInt(document.getElementById('stampWaveCycles')?.value || '2', 10);
        shapeName = `Serpentine Wave (${reqCount} LEDs)`;
        pts = generateWavePoints(cx, cy, sizeScale * 2.5, sizeScale * 0.8, cycles, reqCount);
    } else if (currentSelectedStampShape === 'star') {
        reqCount = parseInt(document.getElementById('stampStarCount')?.value || '10', 10);
        const numPoints = parseInt(document.getElementById('stampStarPoints')?.value || '5', 10);
        shapeName = `${numPoints}-Point Star (${reqCount} LEDs)`;
        pts = generateStarPoints(cx, cy, sizeScale * 1.2, sizeScale * 0.5, numPoints, reqCount);
    } else if (currentSelectedStampShape === 'line') {
        reqCount = parseInt(document.getElementById('stampLineCount')?.value || '8', 10);
        const angle = parseInt(document.getElementById('stampLineAngle')?.value || '0', 10);
        shapeName = `Straight Line (${reqCount} LEDs)`;
        pts = generateLinePoints(cx, cy, sizeScale * 2.5, angle, reqCount);
    }

    if (!pts || pts.length === 0) return;

    const totalLeds = leds ? leds.length : 100;
    const assignedSet = new Set();
    animationGroups.forEach(g => {
        (g.ledIndices || []).forEach(idx => {
            if (idx < totalLeds) assignedSet.add(idx);
        });
    });

    const unassignedIndices = [];
    for (let i = 0; i < totalLeds; i++) {
        if (!assignedSet.has(i)) unassignedIndices.push(i);
    }

    if (unassignedIndices.length < pts.length) {
        showToast(`⚠️ Target shirt only has ${unassignedIndices.length} unused LEDs available, but stamp requires ${pts.length} LEDs!`, 'warning');
        return;
    }

    recordHistory(`Stamp ${shapeName}`);

    const allocatedIndices = unassignedIndices.slice(0, pts.length);
    for (let i = 0; i < pts.length; i++) {
        const ledIdx = allocatedIndices[i];
        const p = pts[i];
        const nx = Math.max(0.04, Math.min(0.96, parseFloat(p.x.toFixed(4))));
        const ny = Math.max(0.04, Math.min(0.96, parseFloat(p.y.toFixed(4))));
        leds[ledIdx].x = nx;
        leds[ledIdx].y = ny;
        if (typeof sampleColorAtNormCoord === 'function') {
            leds[ledIdx].color = sampleColorAtNormCoord(nx, ny);
        }
    }

    const newGroup = {
        id: 'grp_stamp_' + Date.now(),
        name: shapeName,
        ledIndices: [...allocatedIndices],
        effect: 'chase',
        speedBpm: 140,
        direction: 1,
        width: 3,
        colorMode: 'original',
        baselineEffect: 'inherit'
    };

    animationGroups.push(newGroup);

    const autoRearrange = document.getElementById('drawAutoRearrangeCheckbox')?.checked ?? true;
    if (autoRearrange) {
        rearrangeRemainingLedsOnGraphic(false);
    } else {
        rebuildLedGroupMap();
        renderActiveGroupsList();
    }

    selectGroupLeds(newGroup.id);
    markSingleShirtDirty();
    showToast(`🎉 Stamped ${newGroup.name} onto shirt!`);
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
        if (currentSelectedStampShape && currentSelectedStampShape !== 'fireworks') {
            stampSelectedShape();
            return;
        }

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

// Shape Type Picker Event Listeners
document.querySelectorAll('.stamp-type-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const shape = e.currentTarget.getAttribute('data-shape');
        currentSelectedStampShape = shape;
        document.querySelectorAll('.stamp-type-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');

        const paramsBox = document.getElementById('shapeParamsBox');
        const headerTitle = document.getElementById('stampHeaderTitle');
        document.querySelectorAll('.shape-control-sub').forEach(el => el.style.display = 'none');

        if (shape === 'fireworks') {
            if (paramsBox) paramsBox.style.display = 'none';
            if (headerTitle) headerTitle.textContent = '🎆 360° Fireworks Starburst';
        } else {
            if (paramsBox) paramsBox.style.display = 'block';
            if (shape === 'circle') {
                const sub = document.getElementById('shapeCircleControls');
                if (sub) sub.style.display = 'block';
                if (headerTitle) headerTitle.textContent = '⭕ Circle / Wheel Ring';
            } else if (shape === 'arch') {
                const sub = document.getElementById('shapeArchControls');
                if (sub) sub.style.display = 'block';
                if (headerTitle) headerTitle.textContent = '🌈 Arch / Roof Canopy';
            } else if (shape === 'wave') {
                const sub = document.getElementById('shapeWaveControls');
                if (sub) sub.style.display = 'block';
                if (headerTitle) headerTitle.textContent = '🌊 Wave / Serpentine Puff';
            } else if (shape === 'star') {
                const sub = document.getElementById('shapeStarControls');
                if (sub) sub.style.display = 'block';
                if (headerTitle) headerTitle.textContent = '⭐ Star / Sparkle Burst';
            } else if (shape === 'line') {
                const sub = document.getElementById('shapeLineControls');
                if (sub) sub.style.display = 'block';
                if (headerTitle) headerTitle.textContent = '▬ Straight Line / Border Bar';
            }
        }
    });
});

const clickCanvasBtn = document.getElementById('stampClickCanvasBtn');
if (clickCanvasBtn) {
    clickCanvasBtn.addEventListener('click', () => {
        isClickCanvasToPlaceActive = !isClickCanvasToPlaceActive;
        clickCanvasBtn.classList.toggle('active', isClickCanvasToPlaceActive);
        if (isClickCanvasToPlaceActive) {
            clickCanvasBtn.textContent = '🎯 Click on Shirt Canvas now...';
            canvas.style.cursor = 'crosshair';
            showToast('🎯 Click anywhere on the shirt canvas to place stamp center!');
        } else {
            clickCanvasBtn.textContent = '🎯 Click Canvas to Place';
            canvas.style.cursor = 'default';
        }
    });
}

// Preset Buttons
document.getElementById('presetSelect').addEventListener('change', async (e) => {
    const nextVal = e.target.value;
    if (isSingleShirtDirty && activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && fleetRunners[activeSingleShirtRunnerSlot]) {
        const prevRunner = fleetRunners[activeSingleShirtRunnerSlot];
        const selectedOptText = e.target.options[e.target.selectedIndex]?.text?.trim() || nextVal;
        const modalResult = await confirmUnsavedEditsModal(prevRunner, { name: selectedOptText });

        if (modalResult.action === 'cancel') {
            e.target.value = fleetRunners[activeSingleShirtRunnerSlot].preset || '';
            return;
        } else if (modalResult.action === 'save') {
            await saveCurrentProfile(modalResult.name);
            showToast(`💾 Saved Runner #${prevRunner.num} edits as "${modalResult.name}"!`);
        } else if (modalResult.action === 'discard') {
            isSingleShirtDirty = false;
        }
    }
    await loadProfile(nextVal);
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
            direction: params.direction || 1,
            speedBpm: params.speedBpm,
            sparkleRate: params.sparkleRate,
            sparkleStyle: params.sparkleStyle || 'incandescent',
            ambientColorMode: params.ambientColorMode || 'artwork',
            ambientCustomColor: params.ambientCustomColor || '#ffb703',
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

// Fleet Flasher Metadata Roster
const FLEET_FLASHER_ROSTER = [
    { id: 1, name: "The Train", role: "LEADER", tag: "CASEY JR.", icon: "🚂", color: "#ff5e3a", desc: "Pulls the parade & broadcasts ESP-NOW master sync clock. Tapping BOOT triggers the fleet show!" },
    { id: 2, name: "The Title Drum", role: "FOLLOWER", tag: "THE DRUM", icon: "🥁", color: "#f1e05a", desc: "Follows Casey Jr. with warm golden amber sparkles and traveling waves." },
    { id: 3, name: "Cinderella's Coach", role: "FOLLOWER", tag: "CINDERELLA", icon: "🩵", color: "#05d9e8", desc: "Pumpkin coach enchanted blue glow with rotating wheel chase patterns." },
    { id: 4, name: "Peter Pan's Ship", role: "FOLLOWER", tag: "PETER PAN", icon: "🏴‍☠️", color: "#00ff66", desc: "Captain Hook's galleon sailing with emerald pixie dust shimmers." },
    { id: 5, name: "Dumbo the Elephant", role: "FOLLOWER", tag: "DUMBO", icon: "🐘", color: "#ff70a6", desc: "Circus pink and gold starbursts with high-flying ear wave pulses." },
    { id: 6, name: "Pete's Dragon", role: "FOLLOWER", tag: "ELLIOTT", icon: "🐉", color: "#39ff14", desc: "Bright green dragon scales, violet spine accents, and fire-breath sweeps!" },
    { id: 7, name: "To Honor America", role: "FOLLOWER", tag: "FLAG & EAGLE", icon: "🦅", color: "#388bfd", desc: "Grand Finale Stars & Stripes patriotic waves, strobes, and fireworks." },
    { id: 0, name: "Generic / Auto Board", role: "GENERIC", tag: "HOTEL BOOT SELECT", icon: "🎲", color: "#bc8cff", desc: "Universal costume firmware. Remembers previous float ID or defaults to Float 2." }
];

let selectedFleetFlashFloatId = 1;

// Unified USB Flasher supporting both standalone layout and dedicated float identities
async function triggerUsbFirmwareFlash(floatId = 0) {
    if (isFlashingFirmware) return;

    // Auto-resolve floatId from active shirt runner slot if generic 0 was passed
    let effectiveFloatId = floatId;
    if (effectiveFloatId <= 0 && activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) {
        effectiveFloatId = activeSingleShirtRunnerSlot + 1; // e.g., slot 5 = Float 6 (Pete's Dragon)
    }
    if (effectiveFloatId <= 0) effectiveFloatId = 6; // Default to Float 6 (Pete's Dragon)

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

    const floatMeta = FLEET_FLASHER_ROSTER.find(f => f.id === effectiveFloatId) || FLEET_FLASHER_ROSTER[5];
    const floatLabel = `Float ${effectiveFloatId}: ${floatMeta.name}`;

    // Open main flash progress modal
    flashModal.classList.add('open');
    flashStatusText.textContent = `Building & Flashing ${floatLabel}...`;
    flashStatusText.style.color = 'var(--text-main)';
    flashProgressBar.style.width = '20%';
    flashProgressBar.style.background = '#388bfd';
    flashDoneBtn.style.display = 'none';
    flashTipText.textContent = `Baking ${floatLabel} (${floatMeta.role}) into ESP32 NVS flash over USB...`;

    flashTerminal.textContent = `[SIMULATOR] Preparing firmware for 200 LEDs (100 Front + 100 Back)...\n` +
        `[SIMULATOR] Assigned Float Role: ${floatLabel} (${floatMeta.role})\n` +
        `[SIMULATOR] Active Pattern: Unified Master Timeline (${sequenceCues.length} cues, fallback: ambient)\n` +
        `[SIMULATOR] Generating include/float_config.h (COMPILED_FLOAT_ID=${effectiveFloatId})...\n` +
        `[SIMULATOR] Connecting to ESP32...\n--------------------------------------------------\n`;

    isFlashingFirmware = true;
    if (flashEsp32Btn) {
        flashEsp32Btn.disabled = true;
        flashEsp32Btn.style.opacity = '0.6';
    }

    let progress = 20;
    const progressTimer = setInterval(() => {
        if (progress < 85) {
            progress += 5;
            flashProgressBar.style.width = `${progress}%`;
        }
    }, 600);

    try {
        const payload = {
            numLeds: leds.length || 100,
            floatId: effectiveFloatId,
            pattern: 'autonomous_90s',
            ambientPattern: activePattern,   // User's selected ambient mode (steady_sparkle, photo_mode, breathing_glow, etc.)
            ambientDirection: params.direction || 1,
            sparkleStyle: params.sparkleStyle || 'incandescent',
            ambientColorMode: params.ambientColorMode || 'artwork',
            ambientCustomColor: params.ambientCustomColor || '#ffb703',
            speedBpm: params.speedBpm,
            sparkleRate: params.sparkleRate,
            greenHue: params.greenHue,
            brightness: params.brightness,
            palette: leds.map(l => l.color || { r: 15, g: 255, b: 35 }),
            coords: leds.map(l => ({ x: (typeof l.x === 'number' ? l.x : 0.5), y: (typeof l.y === 'number' ? l.y : 0.5) })),
            sequenceCues: sequenceCues || [],
            sequenceLoopDuration: sequenceLoopDuration || 90.0
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
            flashStatusText.textContent = `🎉 Flash Complete! Flashed as ${floatLabel} on ${data.port || 'ESP32'}`;
            flashStatusText.style.color = '#3fb950';
            flashTipText.textContent = `ESP32 rebooted and running as ${floatLabel}!`;
            flashTerminal.textContent += (data.log || '') + '\n\n' +
                `==================================================\n` +
                `[SUCCESS] Flashed successfully as ${floatLabel} to ESP32 on ${data.port}!\n` +
                `The ESP32 has saved Float ID ${floatId} into NVS flash memory.\n` +
                `Outputting 200 LEDs on GPIO 16 (FastLED 2.0A power limiter active).\n` +
                `==================================================`;
            showToast(`⚡ Flashed ${floatLabel} to ${data.port}!`);
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
        if (flashEsp32Btn) {
            flashEsp32Btn.disabled = false;
            flashEsp32Btn.style.opacity = '1';
        }
        flashDoneBtn.style.display = 'block';
        flashTerminal.scrollTop = flashTerminal.scrollHeight;
        checkSerialPortStatus();
    }
}
window.triggerUsbFirmwareFlash = triggerUsbFirmwareFlash;

if (flashEsp32Btn) {
    flashEsp32Btn.addEventListener('click', () => {
        // WYSIWYG Flashing: Always flash whatever float is currently active on canvas!
        const floatId = (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot >= 0 && activeSingleShirtRunnerSlot <= 6)
            ? (activeSingleShirtRunnerSlot + 1)
            : 1;
        triggerUsbFirmwareFlash(floatId);
    });
}

const rebuildFleetBinariesBtn = document.getElementById('rebuildFleetBinariesBtn');
if (rebuildFleetBinariesBtn) {
    rebuildFleetBinariesBtn.addEventListener('click', async () => {
        rebuildFleetBinariesBtn.disabled = true;
        rebuildFleetBinariesBtn.textContent = '⏳ Building...';
        showToast('🔨 Building ROM binaries for all 7 floats in background...');

        try {
            const resp = await fetch('/api/build_fleet_binaries', { method: 'POST' });
            if (!resp.ok) {
                throw new Error(`Server returned HTTP ${resp.status}`);
            }
            const data = await resp.json();
            if (data.success) {
                showToast('✅ Fleet ROM rebuild initiated! Files syncing to firmware folder.');
            } else {
                showToast('❌ Rebuild failed: ' + (data.error || 'Unknown error'));
            }
        } catch (e) {
            showToast('⚠️ Rebuild trigger error: ' + e.message);
        } finally {
            setTimeout(() => {
                rebuildFleetBinariesBtn.disabled = false;
                rebuildFleetBinariesBtn.textContent = '🔨 Rebuild ROMs';
            }, 3000);
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
// RACE-DAY BATTERY LIFE & POWER BUDGET CALCULATOR (200 LEDS / FASTLED 2.0A LIMIT)
// ============================================================================
const FLOAT_POWER_PROFILES = [
    { id: 1, name: "The Train", tag: "CASEY JR.", color: "#ff5e3a", baseMa: 750, showPeakMa: 1120 },
    { id: 2, name: "Title Drum", tag: "THE DRUM", color: "#f1e05a", baseMa: 620, showPeakMa: 1050 },
    { id: 3, name: "The Turtle", tag: "TURTLE", color: "#2ec4b6", baseMa: 660, showPeakMa: 1080 },
    { id: 4, name: "The Snail", tag: "SNAIL", color: "#ff007f", baseMa: 670, showPeakMa: 1090 },
    { id: 5, name: "Cinderella", tag: "COACH", color: "#05d9e8", baseMa: 700, showPeakMa: 1100 },
    { id: 6, name: "Pete's Dragon", tag: "ELLIOTT", color: "#39ff14", baseMa: 720, showPeakMa: 1150 },
    { id: 7, name: "Flag & Eagle", tag: "PATRIOTIC", color: "#388bfd", baseMa: 780, showPeakMa: 1180 }
];

let isPowerBreakdownOpen = false;

function updatePowerBudgetCalculations() {
    const bankSelect = document.getElementById('powerBankSizeSelect');
    const durationRange = document.getElementById('raceDurationRange');
    const freqSelect = document.getElementById('showFrequencySelect');

    const ratedCapacity_mAh = parseInt(bankSelect?.value || '10000', 10);
    const raceDurationMin = parseInt(durationRange?.value || '90', 10);
    const showCadenceMin = parseInt(freqSelect?.value || '4', 10);

    // Save preferences
    try {
        localStorage.setItem('msep_power_bank_size', ratedCapacity_mAh);
        localStorage.setItem('msep_race_duration', raceDurationMin);
        localStorage.setItem('msep_show_frequency', showCadenceMin);
    } catch (e) {}

    // 5V Usable mAh after DC-DC boost conversion (~70% of nominal 3.7V capacity)
    const usable5vMah = Math.round(ratedCapacity_mAh * 0.70);
    const whRating = (ratedCapacity_mAh * 3.7 / 1000).toFixed(1);

    const powerBankWhLabel = document.getElementById('powerBankWhLabel');
    if (powerBankWhLabel) {
        powerBankWhLabel.textContent = `${whRating} Wh (~${usable5vMah.toLocaleString()} mAh @ 5V)`;
    }

    const raceDurationLabel = document.getElementById('raceDurationLabel');
    if (raceDurationLabel) {
        raceDurationLabel.textContent = `${raceDurationMin} min (${(raceDurationMin / 60).toFixed(1)} hrs)`;
    }

    const corralWaitRange = document.getElementById('corralWaitRange');
    const corralWaitMin = corralWaitRange ? parseInt(corralWaitRange.value, 10) : 60;
    const corralWaitLabel = document.getElementById('corralWaitLabel');
    if (corralWaitLabel) {
        corralWaitLabel.textContent = `${corralWaitMin} min (<120mA)`;
    }

    // Number of 30-second shows
    let numShows = 0;
    if (showCadenceMin > 0) {
        numShows = Math.floor(raceDurationMin / showCadenceMin);
    }
    const showMinTotal = (numShows * 0.5).toFixed(1);

    const showCountLabel = document.getElementById('showCountLabel');
    if (showCountLabel) {
        showCountLabel.textContent = (showCadenceMin > 0) 
            ? `${numShows} Shows (~${showMinTotal} min)` 
            : `0 Shows (Baseline Only)`;
    }

    const tShowMin = numShows * 0.5;
    const tBaseMin = Math.max(0, raceDurationMin - tShowMin);
    const tStandbyMin = corralWaitMin;
    const totalTimeMin = raceDurationMin + tStandbyMin;

    // Calculate Fleet Average (including Standby @ 110 mA)
    const fleetAvgBase = FLOAT_POWER_PROFILES.reduce((s, f) => s + f.baseMa, 0) / FLOAT_POWER_PROFILES.length;
    const fleetAvgShow = FLOAT_POWER_PROFILES.reduce((s, f) => s + f.showPeakMa, 0) / FLOAT_POWER_PROFILES.length;
    const fleetStandbyMa = 110;

    const totalFleetMah = Math.round(
        (fleetStandbyMa * (tStandbyMin / 60)) +
        (fleetAvgBase * (tBaseMin / 60)) +
        (fleetAvgShow * (tShowMin / 60))
    );

    const fleetAvgCurrent = Math.round(totalFleetMah / (totalTimeMin / 60));
    const fleetUsedMah = totalFleetMah;
    const fleetRemainMah = Math.max(0, usable5vMah - fleetUsedMah);
    const fleetRemainPct = Math.max(0, Math.min(100, Math.round((fleetRemainMah / usable5vMah) * 100)));
    const fleetTotalHours = (usable5vMah / fleetAvgCurrent).toFixed(1);

    // Update Result Cards
    const batteryRemainingPct = document.getElementById('batteryRemainingPct');
    const batteryRemainingSubtext = document.getElementById('batteryRemainingSubtext');
    const batteryTotalHours = document.getElementById('batteryTotalHours');
    const batteryTotalHoursSubtext = document.getElementById('batteryTotalHoursSubtext');
    const batteryProgressBar = document.getElementById('batteryProgressBar');
    const batteryUsedVsTotalText = document.getElementById('batteryUsedVsTotalText');

    let pctColor = '#3fb950';
    let gradient = 'linear-gradient(90deg, #2ea043, #3fb950)';
    let subtext = '🟢 High Buffer (Safe to Run)';

    if (fleetRemainPct < 15) {
        pctColor = '#f85149';
        gradient = 'linear-gradient(90deg, #cf222e, #f85149)';
        subtext = '🔴 Critical Danger (Upgrade Battery Pack!)';
    } else if (fleetRemainPct < 35) {
        pctColor = '#ffc107';
        gradient = 'linear-gradient(90deg, #d29922, #e3b341)';
        subtext = '🟠 Moderate Buffer (Sufficient for 10K)';
    } else if (fleetRemainPct < 55) {
        pctColor = '#58a6ff';
        gradient = 'linear-gradient(90deg, #1f6feb, #58a6ff)';
        subtext = '🟡 Good Buffer (Safe for 10K)';
    }

    if (batteryRemainingPct) {
        batteryRemainingPct.textContent = `${fleetRemainPct}%`;
        batteryRemainingPct.style.color = pctColor;
    }
    if (batteryRemainingSubtext) {
        batteryRemainingSubtext.textContent = subtext;
    }
    if (batteryTotalHours) {
        batteryTotalHours.textContent = `${fleetTotalHours} hrs`;
    }
    if (batteryTotalHoursSubtext) {
        batteryTotalHoursSubtext.textContent = `To 0% Empty (${fleetAvgCurrent} mA avg)`;
    }
    if (batteryProgressBar) {
        batteryProgressBar.style.width = `${fleetRemainPct}%`;
        batteryProgressBar.style.background = gradient;
    }
    if (batteryUsedVsTotalText) {
        batteryUsedVsTotalText.textContent = `Used: ${fleetUsedMah.toLocaleString()} / ${usable5vMah.toLocaleString()} mAh (5V)`;
    }

    // Populate Float Breakdown Table
    const tableBody = document.getElementById('powerBreakdownTableBody');
    if (tableBody) {
        let rowsHtml = '';
        FLOAT_POWER_PROFILES.forEach(f => {
            const avgCurrent = Math.round(((f.baseMa * tBaseMin) + (f.showPeakMa * tShowMin)) / raceDurationMin);
            const used = Math.round(avgCurrent * (raceDurationMin / 60));
            const remainMah = Math.max(0, usable5vMah - used);
            const remainPct = Math.max(0, Math.min(100, Math.round((remainMah / usable5vMah) * 100)));
            const floatTotalH = (usable5vMah / avgCurrent).toFixed(1);

            let rowColor = '#3fb950';
            if (remainPct < 15) rowColor = '#f85149';
            else if (remainPct < 35) rowColor = '#ffc107';
            else if (remainPct < 55) rowColor = '#58a6ff';

            rowsHtml += `
                <tr style="border-bottom: 1px solid #21262d;">
                    <td style="padding: 5px 2px; display: flex; align-items: center; gap: 5px;">
                        <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: ${f.color};"></span>
                        <span style="font-weight: 600; color: #fff;">${f.name}</span>
                        <span style="color: var(--text-muted); font-size: 9px;">(${f.tag})</span>
                    </td>
                    <td style="padding: 5px 2px; text-align: right; font-family: monospace; color: #8b949e;">${f.baseMa} mA</td>
                    <td style="padding: 5px 2px; text-align: right; font-family: monospace; color: #ffc107;">${f.showPeakMa} mA</td>
                    <td style="padding: 5px 2px; text-align: right; font-family: monospace; font-weight: 700; color: ${rowColor};">${remainPct}% <span style="font-weight: normal; color: var(--text-muted); font-size: 9px;">(${floatTotalH}h)</span></td>
                </tr>
            `;
        });

        // Add Fleet Average Summary Row
        rowsHtml += `
            <tr style="border-top: 1px solid #30363d; background: rgba(56, 139, 253, 0.08); font-weight: 600;">
                <td style="padding: 6px 2px; color: #58a6ff;">⚡ Fleet Average</td>
                <td style="padding: 6px 2px; text-align: right; font-family: monospace; color: #58a6ff;">${Math.round(fleetAvgBase)} mA</td>
                <td style="padding: 6px 2px; text-align: right; font-family: monospace; color: #ffc107;">${Math.round(fleetAvgShow)} mA</td>
                <td style="padding: 6px 2px; text-align: right; font-family: monospace; font-weight: 700; color: ${pctColor};">${fleetRemainPct}% <span style="font-weight: normal; color: #58a6ff; font-size: 9px;">(${fleetTotalHours}h)</span></td>
            </tr>
        `;
        tableBody.innerHTML = rowsHtml;
    }
}
window.updatePowerBudgetCalculations = updatePowerBudgetCalculations;

function initPowerBudgetCalculator() {
    const bankSelect = document.getElementById('powerBankSizeSelect');
    const durationRange = document.getElementById('raceDurationRange');
    const freqSelect = document.getElementById('showFrequencySelect');
    const breakdownToggle = document.getElementById('powerBreakdownToggle');
    const breakdownContent = document.getElementById('powerBreakdownContent');
    const breakdownToggleIcon = document.getElementById('powerBreakdownToggleIcon');
    const jumpBtn = document.getElementById('fleetJumpToBatteryBtn');

    const corralWaitRange = document.getElementById('corralWaitRange');
    const toggleCorralStandbyBtn = document.getElementById('toggleCorralStandbyBtn');
    const wakeCorralStandbyBtn = document.getElementById('wakeCorralStandbyBtn');

    // Restore saved settings
    try {
        const savedSize = localStorage.getItem('msep_power_bank_size');
        if (savedSize && bankSelect) bankSelect.value = savedSize;
        const savedDuration = localStorage.getItem('msep_race_duration');
        if (savedDuration && durationRange) durationRange.value = savedDuration;
        const savedFreq = localStorage.getItem('msep_show_frequency');
        if (savedFreq && freqSelect) freqSelect.value = savedFreq;
        const savedCorral = localStorage.getItem('msep_corral_wait');
        if (savedCorral && corralWaitRange) corralWaitRange.value = savedCorral;
    } catch (e) {}

    bankSelect?.addEventListener('change', updatePowerBudgetCalculations);
    durationRange?.addEventListener('input', updatePowerBudgetCalculations);
    freqSelect?.addEventListener('change', updatePowerBudgetCalculations);
    corralWaitRange?.addEventListener('input', (e) => {
        try { localStorage.setItem('msep_corral_wait', e.target.value); } catch (err) {}
        updatePowerBudgetCalculations();
    });

    function setStandbyUIState(active) {
        isCorralStandbyActive = active;
        if (active && isPhotoModeActive) {
            setPhotoModeUIState(false);
        }
        const pill = document.getElementById('standbyStatusPill');
        if (pill) {
            pill.textContent = active ? '🌙 STANDBY ACTIVE (<120mA)' : 'OFF (Full Parade)';
            pill.style.background = active ? 'rgba(31, 111, 235, 0.25)' : 'rgba(139, 148, 158, 0.2)';
            pill.style.color = active ? '#58a6ff' : '#8b949e';
            pill.style.borderColor = active ? 'rgba(56, 139, 253, 0.5)' : 'rgba(139, 148, 158, 0.4)';
        }
        if (toggleCorralStandbyBtn) {
            toggleCorralStandbyBtn.textContent = active ? '☀️ Wake to Active Parade' : '🌙 Enter Standby Mode';
        }
    }
    window.setStandbyUIState = setStandbyUIState;
    setStandbyUIState(isCorralStandbyActive);

    toggleCorralStandbyBtn?.addEventListener('click', () => {
        setStandbyUIState(!isCorralStandbyActive);
        showToast(isCorralStandbyActive ? '🌙 Entered Corral Standby Mode (12% Dim Twinkle <120mA)!' : '☀️ Woke Fleet to Active Parade Mode!');
    });

    wakeCorralStandbyBtn?.addEventListener('click', () => {
        setStandbyUIState(false);
        showToast('☀️ Leader Woke Entire Fleet to Active Parade Mode!');
    });

    // ========================================================================
    // 📸 CASTLE PHOTO MODE & DUAL HARDWARE BUTTON SIMULATOR
    // ========================================================================
    const photoModeToggleBtn = document.getElementById('photoModeToggleBtn');
    const simButton1TapBtn = document.getElementById('simButton1TapBtn');
    const simButton1DoubleBtn = document.getElementById('simButton1DoubleBtn');
    const simButton1HoldBtn = document.getElementById('simButton1HoldBtn');
    const simButton2TapBtn = document.getElementById('simButton2TapBtn');
    const simButton2HoldBtn = document.getElementById('simButton2HoldBtn');

    function setPhotoModeUIState(active) {
        isPhotoModeActive = active;
        if (photoModeToggleBtn) {
            photoModeToggleBtn.textContent = active ? '📸 Photo Mode: ON' : '📸 Photo Mode: OFF';
            photoModeToggleBtn.style.background = active ? 'rgba(240, 136, 62, 0.25)' : 'transparent';
        }
        if (simButton2TapBtn) {
            simButton2TapBtn.style.background = active ? 'rgba(240, 136, 62, 0.3)' : 'transparent';
        }
    }
    window.setPhotoModeUIState = setPhotoModeUIState;

    photoModeToggleBtn?.addEventListener('click', () => {
        if (isCorralStandbyActive) {
            setStandbyUIState(false);
        }
        setPhotoModeUIState(!isPhotoModeActive);
        showToast(isPhotoModeActive ? '📸 Castle Photo Mode ENGAGED (Solid Steady Glow)!' : '📸 Castle Photo Mode Disengaged.');
    });

    // Sim Button 1: Single Tap (Show / Wake)
    simButton1TapBtn?.addEventListener('click', () => {
        const activeFloatId = (activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) ? (activeSingleShirtRunnerSlot + 1) : 6;
        const isLeader = (activeFloatId === 1 || activeFloatId === 7);

        if (isCorralStandbyActive) {
            setStandbyUIState(false);
            if (isLeader) {
                showToast(`☀️ Button 1: Leader (Float ${activeFloatId}) woke fleet into Solo Show Mode (tap again for 30s fleet show)!`);
            } else {
                showToast(`☀️ Button 1: Follower (Float ${activeFloatId}) woke locally to Solo Show Mode (no fleet show)!`);
            }
        } else if (isLeader) {
            if (fleetShowActive) {
                stopFleetShow();
                showToast(`⏹ Button 1: Leader (Float ${activeFloatId}) stopped fleet show early.`);
            } else {
                startFleetShow();
                showToast(`👑 Button 1: Leader (Float ${activeFloatId}) started 30s fleet show routine!`);
            }
        } else {
            showToast(`🔘 Button 1: Follower (Float ${activeFloatId}) ignored while awake.`);
        }
    });

    // Sim Button 1: Double Tap (Rapid Roll Call Wave)
    simButton1DoubleBtn?.addEventListener('click', () => {
        const activeFloatId = (activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) ? (activeSingleShirtRunnerSlot + 1) : 6;
        const isLeader = (activeFloatId === 1 || activeFloatId === 7);
        if (isLeader) {
            triggerRapidRollCall();
            showToast(`⚡ Button 1 Double-Tap: Leader (Float ${activeFloatId}) launched 4s Rapid Attendance Wave!`);
        } else {
            showToast(`💡 Button 1 Double-Tap: Follower (Float ${activeFloatId}) ignored (Roll call wave reserved for Leader).`);
        }
    });

    // Sim Button 1: 5s Hold (Float ID Configuration Mode)
    simButton1HoldBtn?.addEventListener('click', () => {
        showToast('⏳ Button 1: 5s Long Hold -> Entered Float ID Configuration Mode (1➔7)! Tap to cycle float role.');
    });

    // Sim Button 2: Single Tap (Castle Photo Mode)
    simButton2TapBtn?.addEventListener('click', () => {
        const activeFloatId = (activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) ? (activeSingleShirtRunnerSlot + 1) : 6;
        const isLeader = (activeFloatId === 1 || activeFloatId === 7);
        if (isCorralStandbyActive) {
            setStandbyUIState(false);
            setPhotoModeUIState(true);
            if (isLeader) {
                showToast(`📸 Button 2: Leader (Float ${activeFloatId}) woke fleet directly into Castle Photo Mode!`);
            } else {
                showToast(`📸 Button 2: Follower (Float ${activeFloatId}) woke locally into Castle Photo Mode!`);
            }
            return;
        }
        setPhotoModeUIState(!isPhotoModeActive);
        if (isLeader) {
            showToast(isPhotoModeActive ? `📸 Button 2: Leader (Float ${activeFloatId}) engaged Castle Photo Mode across ENTIRE FLEET!` : `📸 Button 2: Leader (Float ${activeFloatId}) disengaged Castle Photo Mode for fleet.`);
        } else {
            showToast(isPhotoModeActive ? `📸 Button 2: Follower (Float ${activeFloatId}) engaged Castle Photo Mode (local only)!` : `📸 Button 2: Follower (Float ${activeFloatId}) disengaged Castle Photo Mode (local only).`);
        }
    });

    // Sim Button 2: 3s Hold (Standby Sleep Mode)
    simButton2HoldBtn?.addEventListener('click', () => {
        const activeFloatId = (activeSingleShirtRunnerSlot !== undefined && activeSingleShirtRunnerSlot !== null) ? (activeSingleShirtRunnerSlot + 1) : 6;
        const isLeader = (activeFloatId === 1 || activeFloatId === 7);
        if (isPhotoModeActive) {
            setPhotoModeUIState(false);
        }
        setStandbyUIState(true);
        if (isLeader) {
            showToast(`🌙 Button 2: 3s Hold -> Leader (Float ${activeFloatId}) put ENTIRE FLEET into Corral Standby Mode (stays in Standby)!`);
        } else {
            showToast(`🌙 Button 2: 3s Hold -> Follower (Float ${activeFloatId}) entered Corral Standby Mode locally (stays in Standby). Click Button 2 again to enter Photo Mode.`);
        }
    });

    if (breakdownToggle && breakdownContent && breakdownToggleIcon) {
        breakdownToggle.addEventListener('click', () => {
            isPowerBreakdownOpen = !isPowerBreakdownOpen;
            breakdownContent.style.display = isPowerBreakdownOpen ? 'block' : 'none';
            breakdownToggleIcon.textContent = isPowerBreakdownOpen ? '▲ Hide' : '▼ Show';
        });
    }

    if (jumpBtn) {
        jumpBtn.addEventListener('click', () => {
            switchSidebarTab('tabHardware');
            setTimeout(() => {
                const sec = document.getElementById('powerBudgetSection');
                if (sec) {
                    sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    sec.style.transition = 'box-shadow 0.3s ease';
                    sec.style.boxShadow = '0 0 15px rgba(63, 185, 80, 0.6)';
                    setTimeout(() => { sec.style.boxShadow = 'none'; }, 1500);
                }
            }, 100);
        });
    }

    updatePowerBudgetCalculations();
}
window.initPowerBudgetCalculator = initPowerBudgetCalculator;

// ============================================================================
// PRE-RACE CORRAL ROLL CALL & ESP-NOW FLEET RADAR
// ============================================================================
const radarIdentifyFlashes = {};

// DEFAULT_FLEET_RADAR is declared at top of app.js
let fleetRadarFloats = JSON.parse(JSON.stringify(DEFAULT_FLEET_RADAR));
let fleetRadarScenario = 'perfect';

function renderFleetRadarGrid() {
    const grid = document.getElementById('fleetRadarGrid');
    if (!grid) return;

    let onlineCount = 0;
    let offlineCount = 0;
    let conflictCount = 0;

    grid.innerHTML = '';

    fleetRadarFloats.forEach(f => {
        const isOnline = f.status === 'ONLINE';
        const isConflict = f.status === 'CONFLICT';
        const isWeak = (f.rssi <= -82 && isOnline);

        if (isConflict) conflictCount++;
        else if (isOnline) onlineCount++;
        else offlineCount++;

        // Status badge styling
        let statusText = '🟢 READY';
        let statusBadgeStyle = 'background: rgba(46, 160, 67, 0.2); color: #3fb950; border: 1px solid rgba(46, 160, 67, 0.4);';
        if (isConflict) {
            statusText = '⚠️ CONFLICT';
            statusBadgeStyle = 'background: rgba(248, 81, 73, 0.2); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.5); font-weight: 700;';
        } else if (!isOnline) {
            statusText = '🔴 OFFLINE';
            statusBadgeStyle = 'background: rgba(139, 148, 158, 0.2); color: #8b949e; border: 1px solid rgba(139, 148, 158, 0.4);';
        } else if (isWeak) {
            statusText = '🟡 WEAK LINK';
            statusBadgeStyle = 'background: rgba(210, 153, 34, 0.2); color: #e3b341; border: 1px solid rgba(210, 153, 34, 0.4);';
        }

        // RSSI Signal Bars (4 pips)
        let signalBars = '●○○○';
        let signalColor = '#f85149';
        if (!isOnline) {
            signalBars = '○○○○';
            signalColor = '#484f58';
        } else if (f.rssi > -55) {
            signalBars = '●●●●';
            signalColor = '#3fb950';
        } else if (f.rssi > -70) {
            signalBars = '●●●○';
            signalColor = '#58a6ff';
        } else if (f.rssi > -82) {
            signalBars = '●●○○';
            signalColor = '#d29922';
        }

        const roleBadge = f.role === 'LEADER'
            ? `<span style="font-size: 8.5px; background: rgba(248,81,73,0.25); color: #ff7b72; padding: 1px 5px; border-radius: 3px; font-weight: 700; border: 1px solid rgba(248,81,73,0.4);">👑 LEADER</span>`
            : `<span style="font-size: 8.5px; background: rgba(56,139,253,0.15); color: #79c0ff; padding: 1px 5px; border-radius: 3px; font-weight: 600;">📡 FOLLOWER</span>`;

        const card = document.createElement('div');
        card.id = `radarCard_${f.id}`;
        card.style.background = '#0d1117';
        card.style.border = `1px solid ${isConflict ? '#f85149' : (isOnline ? '#30363d' : '#21262d')}`;
        card.style.borderRadius = '6px';
        card.style.padding = '8px 10px';
        card.style.display = 'flex';
        card.style.alignItems = 'center';
        card.style.justifyContent = 'space-between';
        card.style.gap = '8px';
        card.style.transition = 'all 0.2s ease';

        const lastSeenText = isOnline 
            ? (f.lastSeenSec < 1 ? 'Just now' : `${f.lastSeenSec.toFixed(1)}s ago`) 
            : 'No response';

        card.innerHTML = `
            <!-- Left Info -->
            <div style="display: flex; align-items: center; gap: 8px; flex: 1.2; min-width: 0;">
                <span style="font-size: 16px; line-height: 1;">${f.icon || '✨'}</span>
                <div style="overflow: hidden;">
                    <div style="display: flex; align-items: center; gap: 5px; margin-bottom: 2px;">
                        <span style="font-size: 10px; font-weight: 700; color: #8b949e; font-family: monospace;">#0${f.id}</span>
                        <span style="font-size: 11px; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${f.name}</span>
                        ${roleBadge}
                    </div>
                    <div style="font-size: 9.5px; color: var(--text-muted); display: flex; gap: 6px;">
                        <span>${f.tag}</span>
                        <span>•</span>
                        <span style="color: ${isOnline ? '#8b949e' : '#484f58'};">${lastSeenText}</span>
                    </div>
                </div>
            </div>

            <!-- Middle Telemetry (Signal & Voltage) -->
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px; flex: 1; text-align: right;">
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="font-size: 9px; font-family: monospace; color: ${signalColor};">${signalBars}</span>
                    <span style="font-size: 10px; font-family: monospace; color: ${signalColor}; font-weight: 600;">${isOnline ? f.rssi + ' dBm' : 'NO LINK'}</span>
                </div>
                <div style="font-size: 9.5px; color: #8b949e; font-family: monospace;">
                    🔋 ${isOnline ? `${f.voltage.toFixed(2)}V (${f.batteryPct}%)` : '--'}
                </div>
            </div>

            <!-- Right Status & Identify Action -->
            <div style="display: flex; align-items: center; gap: 6px; flex: none;">
                <span style="font-size: 9.5px; padding: 2px 6px; border-radius: 4px; font-weight: 600; white-space: nowrap; ${statusBadgeStyle}">
                    ${statusText}
                </span>
                <button type="button" class="action-btn radar-identify-btn" data-float-id="${f.id}" style="font-size: 10px; padding: 4px 8px; border-color: ${f.color}; color: #fff; background: rgba(255,255,255,0.06); white-space: nowrap;" title="Trigger 3-flash identify pulse on this costume">
                    ✨ Identify
                </button>
            </div>
        `;

        grid.appendChild(card);
    });

    // Wire Identify buttons
    grid.querySelectorAll('.radar-identify-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const fid = parseInt(btn.getAttribute('data-float-id'), 10);
            if (fid) triggerIdentifyFloat(fid);
        });
    });

    // Update Header Status Banner
    const statusPill = document.getElementById('fleetRadarStatusPill');
    const activeText = document.getElementById('fleetRadarActiveCountText');
    if (conflictCount > 0) {
        if (statusPill) {
            statusPill.textContent = `🔴 ${conflictCount} CONFLICT`;
            statusPill.style.background = 'rgba(248, 81, 73, 0.25)';
            statusPill.style.color = '#f85149';
            statusPill.style.borderColor = 'rgba(248, 81, 73, 0.5)';
        }
        if (activeText) {
            activeText.textContent = `⚠️ CONFLICT: Duplicate Float Detected! Check runner configurations`;
            activeText.style.color = '#f85149';
        }
    } else if (offlineCount > 0) {
        if (statusPill) {
            statusPill.textContent = `🟡 ${onlineCount}/7 READY`;
            statusPill.style.background = 'rgba(210, 153, 34, 0.25)';
            statusPill.style.color = '#e3b341';
            statusPill.style.borderColor = 'rgba(210, 153, 34, 0.5)';
        }
        if (activeText) {
            activeText.textContent = `${onlineCount} Online · ${offlineCount} Missing / Offline · 0 Conflict`;
            activeText.style.color = '#e3b341';
        }
    } else {
        if (statusPill) {
            statusPill.textContent = `🟢 7/7 READY`;
            statusPill.style.background = 'rgba(46, 160, 67, 0.25)';
            statusPill.style.color = '#3fb950';
            statusPill.style.borderColor = 'rgba(46, 160, 67, 0.5)';
        }
        if (activeText) {
            activeText.textContent = `7 Online · 0 Offline · 0 Conflict (Ready for Start Gun!)`;
            activeText.style.color = '#3fb950';
        }
    }
}
window.renderFleetRadarGrid = renderFleetRadarGrid;

function hexToRgb(hex) {
    if (!hex) return { r: 255, g: 255, b: 255 };
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
    const num = parseInt(hex, 16);
    return {
        r: (num >> 16) & 255,
        g: (num >> 8) & 255,
        b: num & 255
    };
}

async function triggerIdentifyFloat(floatId) {
    const floatObj = fleetRadarFloats.find(f => f.id === floatId) || DEFAULT_FLEET_RADAR[floatId - 1];
    if (!floatObj) return;

    // Trigger canvas strobe on runnerIndex (floatId - 1)
    const runnerIdx = floatId - 1;
    const nowTime = performance.now();
    radarIdentifyFlashes[runnerIdx] = {
        startTime: nowTime,
        duration: 720, // 3 full cycles of 240ms (120ms ON, 120ms OFF)
        color: hexToRgb(floatObj.color)
    };

    // Animate radar card
    const card = document.getElementById(`radarCard_${floatId}`);
    if (card) {
        card.style.transition = 'box-shadow 0.2s ease, border-color 0.2s ease';
        card.style.boxShadow = `0 0 16px ${floatObj.color}`;
        card.style.borderColor = floatObj.color;
        setTimeout(() => {
            card.style.boxShadow = 'none';
            card.style.borderColor = (floatObj.status === 'CONFLICT') ? '#f85149' : (floatObj.status === 'ONLINE' ? '#30363d' : '#21262d');
        }, 800);
    }

    showToast(`✨ Pinging Float ${floatId} (${floatObj.name}) - Flashing 3x!`);

    // Broadcast UDP/API command
    try {
        await fetch('/api/fleet_radar/identify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targetFloatId: floatId, targetIp: wifiTargetIp || '255.255.255.255' })
        });
    } catch (e) {
        console.warn("API identify call skipped:", e);
    }
}
window.triggerIdentifyFloat = triggerIdentifyFloat;

async function triggerIdentifyAllFloats() {
    showToast(`✨ Flashing full 7-float lineup in sequence (1 ➔ 7)!`);
    for (let fid = 1; fid <= 7; fid++) {
        setTimeout(() => {
            triggerIdentifyFloat(fid);
        }, (fid - 1) * 200);
    }
}
window.triggerIdentifyAllFloats = triggerIdentifyAllFloats;

async function scanFleetRadar() {
    const scanBtn = document.getElementById('fleetRadarScanBtn');
    if (scanBtn) {
        scanBtn.disabled = true;
        scanBtn.innerHTML = `🔄 Scanning Corral...`;
        scanBtn.style.opacity = '0.7';
    }

    try {
        await fetch('/api/fleet_radar/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targetIp: wifiTargetIp || '255.255.255.255' })
        });
    } catch (e) {}

    setTimeout(() => {
        applyRadarScenario(fleetRadarScenario);
        if (scanBtn) {
            scanBtn.disabled = false;
            scanBtn.innerHTML = `📡 Scan Corral / Ping Fleet`;
            scanBtn.style.opacity = '1';
        }
        showToast(`📡 Corral Roll Call Scan complete: ${fleetRadarFloats.filter(f => f.status === 'ONLINE').length}/7 Floats Ready!`);
    }, 600);
}
window.scanFleetRadar = scanFleetRadar;

function applyRadarScenario(scenario) {
    fleetRadarScenario = scenario;
    fleetRadarFloats = JSON.parse(JSON.stringify(DEFAULT_FLEET_RADAR));

    if (scenario === 'missing_4') {
        const f4 = fleetRadarFloats.find(f => f.id === 4);
        if (f4) {
            f4.status = 'OFFLINE';
            f4.rssi = -99;
            f4.lastSeenSec = 720; // 12 mins ago
        }
    } else if (scenario === 'conflict_6') {
        const f6 = fleetRadarFloats.find(f => f.id === 6);
        if (f6) {
            f6.status = 'CONFLICT';
            f6.tag = 'CONFLICT (2 BOARDS)';
        }
    } else if (scenario === 'weak_7') {
        const f7 = fleetRadarFloats.find(f => f.id === 7);
        if (f7) {
            f7.rssi = -88;
            f7.lastSeenSec = 3.8;
        }
    }

    renderFleetRadarGrid();
}
window.applyRadarScenario = applyRadarScenario;

let isFleetRadarExpanded = false;

function setFleetRadarExpanded(expand) {
    isFleetRadarExpanded = expand;
    const content = document.getElementById('fleetRadarContent');
    const toggleBtn = document.getElementById('fleetRadarToggleBtn');
    const hint = document.getElementById('fleetRadarCollapsedHint');
    const section = document.getElementById('fleetRadarSection');

    if (content) content.style.display = expand ? 'block' : 'none';
    if (toggleBtn) {
        toggleBtn.innerHTML = expand ? '▲ Minimize' : '▼ Open Checks';
        toggleBtn.style.color = expand ? '#ff7b72' : '#58a6ff';
        toggleBtn.style.borderColor = expand ? '#f85149' : '#388bfd';
    }
    if (hint) hint.style.display = expand ? 'none' : 'block';
    if (section) {
        section.style.borderColor = expand ? '#388bfd' : '#1f6feb';
    }
}
window.setFleetRadarExpanded = setFleetRadarExpanded;

function openFleetRadar(andScroll = true) {
    setFleetRadarExpanded(true);
    const section = document.getElementById('fleetRadarSection');
    if (section && andScroll) {
        section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        section.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
        section.style.boxShadow = '0 0 16px rgba(56, 139, 253, 0.4)';
        setTimeout(() => {
            if (section) section.style.boxShadow = 'none';
        }, 1200);
    }
}
window.openFleetRadar = openFleetRadar;

async function triggerRapidRollCall() {
    openFleetRadar(false);
    const rollCallBtn = document.getElementById('fleetRadarRapidRollCallBtn');
    if (rapidRollCallActive) return;

    // Ensure we are viewing Fleet View so all 7 runners are immediately visible!
    if (currentView !== 'fleet') {
        currentView = 'fleet';
        document.getElementById('fleetViewBtn')?.classList.add('active');
        document.getElementById('singleViewBtn')?.classList.remove('active');
    }

    rapidRollCallActive = true;
    rapidRollCallStartTime = performance.now();

    if (rollCallBtn) {
        rollCallBtn.style.pointerEvents = 'none';
        rollCallBtn.innerHTML = `⚡ Attendance Wave Active (4s)...`;
        rollCallBtn.style.opacity = '0.85';
    }

    showToast(`⚡ 4-Second Rapid Attendance Roll Call wave activated! (Simulating BOOT Double-Tap)`);

    // Card glow animations matching each float's 500ms slot
    for (let slot = 0; slot < 7; slot++) {
        const floatId = slot + 1;
        const floatObj = fleetRadarFloats.find(f => f.id === floatId) || DEFAULT_FLEET_RADAR[slot];
        setTimeout(() => {
            if (!rapidRollCallActive) return;
            const card = document.getElementById(`radarCard_${floatId}`);
            if (card && floatObj) {
                card.style.transition = 'box-shadow 0.2s ease, border-color 0.2s ease';
                card.style.boxShadow = `0 0 18px ${floatObj.color}`;
                card.style.borderColor = floatObj.color;
                setTimeout(() => {
                    card.style.boxShadow = 'none';
                    card.style.borderColor = (floatObj.status === 'CONFLICT') ? '#f85149' : (floatObj.status === 'ONLINE' ? '#30363d' : '#21262d');
                }, 480);
            }
        }, slot * 500);
    }

    // Finale slot: 3500ms - 4000ms unison emerald green glow across all 7 cards
    setTimeout(() => {
        if (!rapidRollCallActive) return;
        for (let fid = 1; fid <= 7; fid++) {
            const card = document.getElementById(`radarCard_${fid}`);
            if (card) {
                card.style.transition = 'box-shadow 0.15s ease, border-color 0.15s ease';
                card.style.boxShadow = `0 0 16px #39ff14`;
                card.style.borderColor = '#39ff14';
                setTimeout(() => {
                    card.style.boxShadow = 'none';
                    const fObj = fleetRadarFloats.find(f => f.id === fid) || DEFAULT_FLEET_RADAR[fid - 1];
                    card.style.borderColor = (fObj && fObj.status === 'CONFLICT') ? '#f85149' : ((fObj && fObj.status === 'ONLINE') ? '#30363d' : '#21262d');
                }, 480);
            }
        }
    }, 3500);

    // Reset button after 4000ms
    setTimeout(() => {
        rapidRollCallActive = false;
        if (rollCallBtn) {
            rollCallBtn.style.pointerEvents = 'auto';
            rollCallBtn.innerHTML = `⚡ 4s Rapid Attendance Wave <span style="font-size: 9.5px; opacity: 0.85; font-weight: normal; margin-left: 2px;">(Simulate BOOT Double-Tap)</span>`;
            rollCallBtn.style.opacity = '1';
        }
    }, 4000);

    // Broadcast UDP/API command to hardware
    try {
        await fetch('/api/fleet_radar/trigger_roll_call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targetIp: wifiTargetIp || '255.255.255.255' })
        });
    } catch (e) {
        console.warn("API roll call call skipped:", e);
    }
}
window.triggerRapidRollCall = triggerRapidRollCall;

function initFleetRadar() {
    const scanBtn = document.getElementById('fleetRadarScanBtn');
    const identifyAllBtn = document.getElementById('fleetRadarIdentifyAllBtn');
    const rapidRollCallBtn = document.getElementById('fleetRadarRapidRollCallBtn');
    const scenarioSelect = document.getElementById('fleetRadarScenarioSelect');
    const toggleHeader = document.getElementById('fleetRadarToggleHeader');
    const toggleBtn = document.getElementById('fleetRadarToggleBtn');
    const jumpBtn = document.getElementById('fleetJumpToRadarBtn');
    const jumpTopBtn = document.getElementById('fleetJumpToRadarTopBtn');

    toggleHeader?.addEventListener('click', (e) => {
        // Toggle if user clicks anywhere in header except if clicking button itself (handled below)
        if (e.target !== toggleBtn && !toggleBtn?.contains(e.target)) {
            setFleetRadarExpanded(!isFleetRadarExpanded);
        }
    });

    toggleBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        setFleetRadarExpanded(!isFleetRadarExpanded);
    });

    jumpBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        openFleetRadar(true);
    });

    jumpTopBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        openFleetRadar(true);
    });

    scanBtn?.addEventListener('click', scanFleetRadar);
    identifyAllBtn?.addEventListener('click', triggerIdentifyAllFloats);

    // Support both single click and double-tap / double-click
    function onRollCallTrigger(e) {
        if (e) e.preventDefault();
        triggerRapidRollCall();
    }
    rapidRollCallBtn?.addEventListener('click', onRollCallTrigger);
    rapidRollCallBtn?.addEventListener('dblclick', onRollCallTrigger);

    scenarioSelect?.addEventListener('change', (e) => {
        applyRadarScenario(e.target.value);
    });

    renderFleetRadarGrid();
}
window.initFleetRadar = initFleetRadar;

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

const fleetWifiStreamBtn = document.getElementById('fleetWifiStreamBtn');
const fleetWifiStreamDot = document.getElementById('fleetWifiStreamDot');
const fleetWifiStreamStatusBadge = document.getElementById('fleetWifiStreamStatusBadge');

function updateWifiStreamStatusUI(isFleetMode) {
    if (!isWifiStreaming) return;
    if (isFleetMode) {
        if (fleetShowActive) {
            if (wifiStreamStatusText) {
                wifiStreamStatusText.textContent = `⚡ Fleet Show (7 Floats / 700 LEDs @ 30 FPS)`;
                wifiStreamStatusText.style.color = '#ffc107';
            }
            if (fleetWifiStreamStatusBadge) {
                fleetWifiStreamStatusBadge.textContent = '⚡ Streaming Show (30 FPS)';
                fleetWifiStreamStatusBadge.style.color = '#ffc107';
            }
        } else {
            if (wifiStreamStatusText) {
                wifiStreamStatusText.textContent = `📡 7-Float Fleet Lineup (700 LEDs @ 30 FPS)`;
                wifiStreamStatusText.style.color = '#3fb950';
            }
            if (fleetWifiStreamStatusBadge) {
                fleetWifiStreamStatusBadge.textContent = '📡 Streaming Lineup (30 FPS)';
                fleetWifiStreamStatusBadge.style.color = '#3fb950';
            }
        }
    } else {
        const count = Math.min(100, leds.length);
        if (wifiStreamStatusText) {
            wifiStreamStatusText.textContent = `Streaming Single Costume (${count} LEDs @ 30 FPS)`;
            wifiStreamStatusText.style.color = '#58a6ff';
        }
        if (fleetWifiStreamStatusBadge) {
            fleetWifiStreamStatusBadge.textContent = 'Single Shirt Stream';
            fleetWifiStreamStatusBadge.style.color = '#58a6ff';
        }
    }
}

async function sendLivePixelFrame(timeMs) {
    if (!isWifiStreaming || isSendingFrame) return;
    if (timeMs - lastWifiStreamTime < 33) return; // 30 FPS throttle (~33ms)
    lastWifiStreamTime = timeMs;
    isSendingFrame = true;

    try {
        let payload = null;
        const isFleetMode = (currentView === 'fleet') || fleetShowActive;

        if (isFleetMode) {
            // MULTI-FLOAT BROADCAST: Stream all 7 floats with addressed Opcode 0x02
            const fleetFrames = [];
            const totalFloats = 7;
            for (let i = 0; i < totalFloats; i++) {
                const floatData = fleetRunners[i] || DEFAULT_FLEET_ROSTER[i];
                const isLivePreview = (i === activeSingleShirtRunnerSlot) || (floatData && floatData.preset === 'current_editor');
                const pData = isLivePreview ? getLiveSingleShirtPresetData() : (fleetPresetCache[floatData.preset] || null);
                const ledsArr = (pData && Array.isArray(pData.leds) && pData.leds.length > 0) ? pData.leds : leds;
                const count = Math.min(100, (ledsArr && ledsArr.length > 0) ? ledsArr.length : 100);
                const flatRgb = [];

                for (let j = 0; j < count; j++) {
                    const col = computeRunnerLedColor(i, floatData, pData, j, count, timeMs, 0, false);
                    flatRgb.push(
                        Math.max(0, Math.min(255, Math.round(col.r || 0))),
                        Math.max(0, Math.min(255, Math.round(col.g || 0))),
                        Math.max(0, Math.min(255, Math.round(col.b || 0)))
                    );
                }
                fleetFrames.push({
                    floatId: i + 1, // 1 to 7
                    pixels: flatRgb
                });
            }

            payload = {
                targetIp: wifiTargetIp,
                fleetFrames: fleetFrames
            };
        } else {
            // SINGLE COSTUME BROADCAST: Stream active single shirt (Opcode 0x01 universal)
            const count = Math.min(100, leds.length);
            const flatRgb = [];
            for (let i = 0; i < count; i++) {
                const col = computeLedColor(i, count, timeMs);
                flatRgb.push(
                    Math.max(0, Math.min(255, Math.round(col.r || 0))),
                    Math.max(0, Math.min(255, Math.round(col.g || 0))),
                    Math.max(0, Math.min(255, Math.round(col.b || 0)))
                );
            }

            payload = {
                targetIp: wifiTargetIp,
                pixels: flatRgb
            };
        }

        const res = await fetch('/api/stream_pixels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data && data.success) {
            streamPacketCounter++;
            if (streamPacketCounter % 15 === 0) {
                updateWifiStreamStatusUI(isFleetMode);
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

function setWifiStreamingState(active) {
    isWifiStreaming = active;
    const fleetBtn = document.getElementById('fleetWifiStreamBtn');
    const fleetDot = document.getElementById('fleetWifiStreamDot');

    if (isWifiStreaming) {
        if (toggleWifiStreamBtn) {
            toggleWifiStreamBtn.textContent = '⏹ Stop Live Wi-Fi Stream';
            toggleWifiStreamBtn.style.background = 'linear-gradient(135deg, #da3633, #f85149)';
        }
        if (fleetBtn) {
            fleetBtn.innerHTML = '⏹ Stop Stream';
            fleetBtn.style.background = 'linear-gradient(135deg, #da3633, #f85149)';
            fleetBtn.style.borderColor = '#f85149';
            fleetBtn.style.color = '#fff';
        }
        if (wifiStreamDot) {
            wifiStreamDot.style.background = '#2ea043';
            wifiStreamDot.style.boxShadow = '0 0 8px #2ea043';
        }
        if (fleetDot) {
            fleetDot.style.background = '#2ea043';
            fleetDot.style.boxShadow = '0 0 8px #2ea043';
        }
        updateWifiStreamStatusUI((currentView === 'fleet') || fleetShowActive);
        showToast('📡 Wi-Fi live stream started! Updating LEDs in real time.');
    } else {
        if (toggleWifiStreamBtn) {
            toggleWifiStreamBtn.textContent = '▶ Start Live Wi-Fi Stream';
            toggleWifiStreamBtn.style.background = 'linear-gradient(135deg, #1f6feb, #388bfd)';
        }
        if (fleetBtn) {
            fleetBtn.innerHTML = '📡 Wi-Fi Stream';
            fleetBtn.style.background = '#161b22';
            fleetBtn.style.borderColor = '#30363d';
            fleetBtn.style.color = 'var(--text-main)';
        }
        if (wifiStreamDot) {
            wifiStreamDot.style.background = '#8b949e';
            wifiStreamDot.style.boxShadow = 'none';
        }
        if (fleetDot) {
            fleetDot.style.background = '#8b949e';
            fleetDot.style.boxShadow = 'none';
        }
        if (wifiStreamStatusText) {
            wifiStreamStatusText.textContent = 'Standby (Off)';
            wifiStreamStatusText.style.color = 'var(--text-muted)';
        }
        if (fleetWifiStreamStatusBadge) {
            fleetWifiStreamStatusBadge.textContent = 'Wi-Fi: Standby (Off)';
            fleetWifiStreamStatusBadge.style.color = 'var(--text-muted)';
        }
        showToast('⏹ Live Wi-Fi stream stopped.');
    }
}

if (toggleWifiStreamBtn) {
    toggleWifiStreamBtn.addEventListener('click', () => {
        setWifiStreamingState(!isWifiStreaming);
    });
}

if (fleetWifiStreamBtn) {
    fleetWifiStreamBtn.addEventListener('click', () => {
        setWifiStreamingState(!isWifiStreaming);
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
    if (targetTabId !== 'tabFleet') {
        lastSingleShirtTab = targetTabId;
    }
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

    // Auto-synchronize Canvas View
    if (targetTabId === 'tabFleet') {
        currentView = 'fleet';
        document.getElementById('fleetViewBtn')?.classList.add('active');
        document.getElementById('singleViewBtn')?.classList.remove('active');
        const zt = document.querySelector('.zoom-toolbar');
        if (zt) zt.style.display = 'none';
        renderFleetCards();
    } else {
        currentView = 'single';
        document.getElementById('singleViewBtn')?.classList.add('active');
        document.getElementById('fleetViewBtn')?.classList.remove('active');
        const zt = document.querySelector('.zoom-toolbar');
        if (zt) zt.style.display = 'flex';
        updateActiveFloatUI(activeSingleShirtRunnerSlot);
    }

    // Master Timeline Synchronization: Individual shirt show vs Fleet show
    renderTimelineLayers();
    updateTimelinePlayBtn();
    updateTimelineScrubberUI();
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


// ============================================================================
// MASTER FLEET PARADE BUNDLE EXPORT & IMPORT ENGINE
// ============================================================================

let pendingImportBundleData = null;

// Export all 7 costume designs, LED coordinates, zone groups, standalone cues, and 30s fleet choreography to a single master JSON file
async function exportMasterFleetBundleJson() {
    try {
        // 1. Sync current single-shirt editor state to active runner slot in memory
        if (activeSingleShirtRunnerSlot !== null && activeSingleShirtRunnerSlot >= 0 && activeSingleShirtRunnerSlot < fleetRunners.length) {
            const currentSlot = activeSingleShirtRunnerSlot;
            const currentRunner = fleetRunners[currentSlot];
            const currentEditorState = {
                name: currentRunner.name || `Float ${currentSlot + 1}`,
                floatName: `Float ${currentSlot + 1} - ${currentRunner.name}`,
                savedAt: new Date().toISOString(),
                ledCount: leds.length,
                leds: JSON.parse(JSON.stringify(leds)),
                graphicType: currentGraphicType,
                customArtworkDataUrl: customArtworkDataUrl,
                animationGroups: JSON.parse(JSON.stringify(animationGroups)),
                settings: {
                    pattern: activePattern,
                    direction: params.direction || 1,
                    speedBpm: params.speedBpm,
                    sparkleRate: params.sparkleRate,
                    sparkleStyle: params.sparkleStyle || 'incandescent',
                    ambientColorMode: params.ambientColorMode || 'artwork',
                    ambientCustomColor: params.ambientCustomColor || '#ffb703',
                    greenHue: params.greenHue,
                    brightness: params.brightness,
                    glowSize: params.glowSize
                },
                sequence: {
                    loopDuration: sequenceLoopDuration,
                    cues: JSON.parse(JSON.stringify(sequenceCues))
                }
            };
            const cacheKey = `custom_slot_${currentSlot}_${Date.now()}`;
            fleetPresetCache[cacheKey] = currentEditorState;
            currentRunner.preset = cacheKey;
        }

        // 2. Resolve complete preset data for all 7 floats
        const floatsExport = {};
        for (let i = 0; i < fleetRunners.length; i++) {
            const runner = fleetRunners[i];
            const presetData = await getPresetDataForRunner(runner) || {};
            
            floatsExport[String(i + 1)] = {
                slot: i,
                num: runner.num || String(i + 1).padStart(2, '0'),
                name: runner.name || DEFAULT_FLEET_ROSTER[i].name,
                fullName: runner.fullName || DEFAULT_FLEET_ROSTER[i].fullName,
                icon: runner.icon || DEFAULT_FLEET_ROSTER[i].icon,
                color: runner.color || DEFAULT_FLEET_ROSTER[i].color,
                role: runner.role || DEFAULT_FLEET_ROSTER[i].role,
                graphicType: presetData.graphicType || runner.defaultGraphic || DEFAULT_FLEET_ROSTER[i].defaultGraphic,
                customArtworkDataUrl: presetData.customArtworkDataUrl || null,
                ledCount: (presetData.leds && presetData.leds.length) || (presetData.ledCount || 100),
                leds: presetData.leds || [],
                animationGroups: presetData.animationGroups || [],
                settings: presetData.settings || {
                    pattern: 'steady_sparkle',
                    speedBpm: 120,
                    sparkleRate: 5,
                    greenHue: 140,
                    brightness: 255,
                    glowSize: 18
                },
                sequence: presetData.sequence || {
                    loopDuration: 90.0,
                    cues: []
                }
            };
        }

        // 3. Assemble the Master Bundle
        const masterBundle = {
            project: "Main Street Electrical Parade (WDW 10K)",
            bundleType: "MasterFleetParadeSuite",
            version: "1.0",
            exportTimestamp: new Date().toISOString(),
            paradeName: "Main Street Electrical Parade 10K Fleet Show",
            totalFloats: fleetRunners.length,
            fleetChoreography: {
                showDuration: (activeFleetShow && activeFleetShow.loopDuration) || 30.0,
                name: (activeFleetShow && activeFleetShow.name) || "30s Grand Electrical Parade Show",
                blocks: (activeFleetShow && activeFleetShow.blocks) ? JSON.parse(JSON.stringify(activeFleetShow.blocks)) : []
            },
            floats: floatsExport
        };

        // 4. Download file
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(masterBundle, null, 2));
        const dlAnchor = document.createElement('a');
        dlAnchor.setAttribute("href", dataStr);
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const filename = `msep_fleet_parade_master_${timestamp}.json`;
        dlAnchor.setAttribute("download", filename);
        document.body.appendChild(dlAnchor);
        dlAnchor.click();
        document.body.removeChild(dlAnchor);

        showToast(`📦 Exported complete 7-Float Parade Suite (${filename})!`);
    } catch (err) {
        console.error("Error exporting master fleet bundle:", err);
        showToast("⚠️ Failed to export master fleet bundle: " + err.message);
    }
}

// Open and populate the Import Master Fleet Bundle Confirmation Modal
function openFleetBundleImportModal(bundleData, fileName) {
    if (!bundleData || (!bundleData.floats && !bundleData.runners && !Array.isArray(bundleData))) {
        showToast("⚠️ Invalid master fleet bundle JSON structure!");
        return;
    }

    pendingImportBundleData = bundleData;

    const modal = document.getElementById('fleetBundleImportModal');
    const metaBox = document.getElementById('importBundleMetadataBox');
    const floatsList = document.getElementById('importBundleFloatsList');
    const choreoToggle = document.getElementById('importBundleChoreographyToggle');
    const choreoBlockCountSpan = document.getElementById('importBundleChoreoBlockCount');

    if (!modal || !metaBox || !floatsList) return;

    // Normalizing floats object
    let floatsMap = bundleData.floats || {};
    if (Array.isArray(bundleData)) {
        floatsMap = {};
        bundleData.forEach((item, idx) => {
            floatsMap[String(idx + 1)] = item;
        });
    } else if (bundleData.runners && typeof bundleData.runners === 'object') {
        floatsMap = bundleData.runners;
    }

    const paradeTitle = bundleData.paradeName || bundleData.name || fileName || "MSEP Fleet Suite";
    const exportTime = bundleData.exportTimestamp ? new Date(bundleData.exportTimestamp).toLocaleString() : "Unknown date";
    const numFloatsInFile = Object.keys(floatsMap).length;
    const choreoBlocks = (bundleData.fleetChoreography && bundleData.fleetChoreography.blocks) ? bundleData.fleetChoreography.blocks : [];

    // 1. Populate metadata summary
    metaBox.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <strong style="color: #58a6ff; font-size: 12px;">${paradeTitle}</strong>
            <span style="font-size: 10px; background: #21262d; color: #ffc107; padding: 2px 6px; border-radius: 4px;">${numFloatsInFile} Floats Included</span>
        </div>
        <div style="color: #8b949e; font-size: 10.5px;">
            <div>📅 Exported: <strong>${exportTime}</strong></div>
            <div>👑 30s Choreography: <strong>${choreoBlocks.length} Blocks</strong> (${(bundleData.fleetChoreography?.showDuration || 30.0).toFixed(1)}s loop)</div>
        </div>
    `;

    if (choreoBlockCountSpan) {
        choreoBlockCountSpan.textContent = `${choreoBlocks.length} Blocks`;
    }
    if (choreoToggle) {
        choreoToggle.checked = choreoBlocks.length > 0;
        choreoToggle.disabled = choreoBlocks.length === 0;
    }

    // 2. Populate float selection list
    floatsList.innerHTML = '';
    for (let slot = 0; slot < 7; slot++) {
        const floatNum = String(slot + 1);
        const floatData = floatsMap[floatNum] || floatsMap[slot] || null;
        const defaultInfo = DEFAULT_FLEET_ROSTER[slot];
        
        const card = document.createElement('div');
        card.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 7px 10px;
            background: #0d1117;
            border: 1px solid ${floatData ? '#30363d' : 'rgba(255,255,255,0.05)'};
            border-radius: 6px;
            font-size: 11px;
            opacity: ${floatData ? '1.0' : '0.5'};
        `;

        const ledCount = floatData ? (floatData.leds ? floatData.leds.length : (floatData.ledCount || 100)) : 0;
        const groupsCount = floatData && floatData.animationGroups ? floatData.animationGroups.length : 0;
        const cuesCount = floatData && floatData.sequence && floatData.sequence.cues ? floatData.sequence.cues.length : 0;

        card.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <input type="checkbox" class="import-float-checkbox" data-slot="${slot}" data-key="${floatNum}" ${floatData ? 'checked' : 'disabled'} style="accent-color: #388bfd; width: 14px; height: 14px; cursor: pointer;">
                <span style="font-size: 16px;">${floatData?.icon || defaultInfo.icon}</span>
                <div>
                    <div style="font-weight: 600; color: #fff;">
                        Float ${slot + 1}: ${floatData?.name || defaultInfo.name}
                    </div>
                    <div style="font-size: 10px; color: var(--text-muted);">
                        ${floatData ? `${ledCount} LEDs · ${groupsCount} Groups · ${cuesCount} Standalone Cues` : 'Not included in bundle file'}
                    </div>
                </div>
            </div>
            <span style="font-size: 10px; color: ${defaultInfo.color}; font-weight: 700; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;">
                ${defaultInfo.tag}
            </span>
        `;

        floatsList.appendChild(card);
    }

    modal.style.display = 'flex';
}

// Apply selected floats and choreography from imported master bundle
async function applyMasterFleetBundle(bundleData) {
    if (!bundleData) return;

    try {
        pushUndoState("Import Master Fleet Parade Bundle");

        let floatsMap = bundleData.floats || {};
        if (Array.isArray(bundleData)) {
            floatsMap = {};
            bundleData.forEach((item, idx) => {
                floatsMap[String(idx + 1)] = item;
            });
        } else if (bundleData.runners && typeof bundleData.runners === 'object') {
            floatsMap = bundleData.runners;
        }

        const checkboxes = document.querySelectorAll('.import-float-checkbox:checked');
        let importedCount = 0;

        for (const cb of checkboxes) {
            const slot = parseInt(cb.getAttribute('data-slot'));
            const key = cb.getAttribute('data-key');
            const floatData = floatsMap[key] || floatsMap[slot];
            if (!floatData || slot < 0 || slot >= fleetRunners.length) continue;

            const runner = fleetRunners[slot];
            const cacheKey = `imported_bundle_slot_${slot}_${Date.now()}`;

            const normalizedPreset = {
                name: floatData.name || runner.name,
                floatName: `Float ${slot + 1} - ${floatData.name || runner.name}`,
                savedAt: floatData.savedAt || new Date().toISOString(),
                ledCount: (floatData.leds && floatData.leds.length) || floatData.ledCount || 100,
                leds: floatData.leds || [],
                graphicType: floatData.graphicType || runner.defaultGraphic || DEFAULT_FLEET_ROSTER[slot].defaultGraphic,
                customArtworkDataUrl: floatData.customArtworkDataUrl || null,
                animationGroups: floatData.animationGroups || [],
                settings: floatData.settings || {
                    pattern: 'steady_sparkle',
                    speedBpm: 120,
                    sparkleRate: 5,
                    greenHue: 140,
                    brightness: 255,
                    glowSize: 18
                },
                sequence: floatData.sequence || {
                    loopDuration: 90.0,
                    cues: []
                }
            };

            fleetPresetCache[cacheKey] = normalizedPreset;
            runner.preset = cacheKey;

            // If this float is currently active in the Single Shirt editor, update editor in place
            if (activeSingleShirtRunnerSlot === slot) {
                applyProfileData(normalizedPreset);
            }

            importedCount++;
        }

        // 2. Import 30s Choreography if toggled
        const choreoToggle = document.getElementById('importBundleChoreographyToggle');
        if (choreoToggle && choreoToggle.checked && bundleData.fleetChoreography && Array.isArray(bundleData.fleetChoreography.blocks)) {
            if (!activeFleetShow) {
                activeFleetShow = {
                    id: 'imported_master_parade.json',
                    name: bundleData.fleetChoreography.name || 'Imported 30s Master Parade',
                    loopDuration: bundleData.fleetChoreography.showDuration || 30.0,
                    blocks: []
                };
            }
            activeFleetShow.blocks = JSON.parse(JSON.stringify(bundleData.fleetChoreography.blocks));
            activeFleetShow.loopDuration = bundleData.fleetChoreography.showDuration || 30.0;
            recalculateFleetBlockStartTimes();
            renderFleetBlocksEditor();
        }

        // 3. Save lineup and update UI
        saveFleetLineupToStorage();
        renderFleetCards();
        renderActiveGroupsList();
        renderTimelineCues();

        const modal = document.getElementById('fleetBundleImportModal');
        if (modal) modal.style.display = 'none';

        showToast(`🎉 Applied ${importedCount} Floats from Master Fleet Parade Bundle!`);
    } catch (err) {
        console.error("Error applying master fleet bundle:", err);
        showToast("⚠️ Error applying bundle: " + err.message);
    }
}

// Bind Master Fleet Parade Bundle event listeners
function initMasterFleetBundleControls() {
    const fleetExportBtn = document.getElementById('fleetExportBundleBtn');
    const layoutExportAllBtn = document.getElementById('layoutExportAllFleetBtn');
    const fleetImportBtn = document.getElementById('fleetImportBundleBtn');
    const fleetImportFileInput = document.getElementById('fleetImportBundleFileInput');
    const modal = document.getElementById('fleetBundleImportModal');
    const closeModalBtn = document.getElementById('closeFleetBundleModalBtn');
    const cancelModalBtn = document.getElementById('cancelFleetBundleModalBtn');
    const confirmApplyBtn = document.getElementById('confirmFleetBundleApplyBtn');
    const selectAllBtn = document.getElementById('importBundleSelectAllBtn');
    const deselectAllBtn = document.getElementById('importBundleDeselectAllBtn');

    if (fleetExportBtn) fleetExportBtn.addEventListener('click', exportMasterFleetBundleJson);
    if (layoutExportAllBtn) layoutExportAllBtn.addEventListener('click', exportMasterFleetBundleJson);

    if (fleetImportBtn && fleetImportFileInput) {
        fleetImportBtn.addEventListener('click', () => fleetImportFileInput.click());
        fleetImportFileInput.addEventListener('change', (e) => {
            const file = e.target.files && e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    try {
                        const parsed = JSON.parse(evt.target.result);
                        openFleetBundleImportModal(parsed, file.name);
                    } catch (err) {
                        showToast("⚠️ Failed to parse JSON file: " + err.message);
                    }
                };
                reader.readAsText(file);
            }
            e.target.value = '';
        });
    }

    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    }
    if (cancelModalBtn && modal) {
        cancelModalBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            document.querySelectorAll('.import-float-checkbox:not(:disabled)').forEach(cb => { cb.checked = true; });
        });
    }
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => {
            document.querySelectorAll('.import-float-checkbox:not(:disabled)').forEach(cb => { cb.checked = false; });
        });
    }

    if (confirmApplyBtn) {
        confirmApplyBtn.addEventListener('click', () => {
            if (pendingImportBundleData) {
                applyMasterFleetBundle(pendingImportBundleData);
            }
        });
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

// ============================================================================
// 🎵 WEB AUDIO API: BAROQUE HOEDOWN PARADE SYNTHESIZER
// ============================================================================
class BaroqueHoedownSynth {
    constructor() {
        this.ctx = null;
        this.isPlaying = false;
        this.musicEnabled = false;
        this.timer = null;
        this.stepIndex = 0;
        this.tempoBpm = 130;
    }

    initAudioContext() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                this.ctx = new AudioCtx();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleMusic() {
        this.initAudioContext();
        this.musicEnabled = !this.musicEnabled;
        this.updateButtonUI();

        if (this.musicEnabled) {
            this.start();
            showToast("🎵 Baroque Hoedown synthesizer activated!");
        } else {
            this.stop();
            showToast("🔇 Music muted");
        }
    }

    updateButtonUI() {
        const btn = document.getElementById('audioToggleBtn');
        if (!btn) return;
        if (this.musicEnabled) {
            btn.textContent = '🎵 Music: ON';
            btn.style.borderColor = '#39c5bb';
            btn.style.color = '#39c5bb';
            btn.style.background = 'rgba(57, 197, 187, 0.15)';
        } else {
            btn.textContent = '🎵 Music: OFF';
            btn.style.borderColor = '#bc8cff';
            btn.style.color = '#bc8cff';
            btn.style.background = 'transparent';
        }
    }

    getScore() {
        const D3 = 146.83, E3 = 164.81, Fs3 = 185.00, G3 = 196.00, A3 = 220.00, B3 = 246.94, Cs4 = 277.18;
        const D4 = 293.66, E4 = 329.63, Fs4 = 369.99, G4 = 392.00, A4 = 440.00, B4 = 493.88, Cs5 = 554.37;
        const D5 = 587.33, E5 = 659.25, Fs5 = 739.99, G5 = 783.99, A5 = 880.00, B5 = 987.77, Cs6 = 1108.73, D6 = 1174.66, E6 = 1318.51, Fs6 = 1479.98;

        return [
            // Measure 1
            { lead: D5, bass: D3 }, { lead: 0, bass: 0 },
            { lead: Fs5, bass: A3 }, { lead: 0, bass: 0 },
            { lead: A5, bass: D3 }, { lead: 0, bass: 0 },
            { lead: D6, bass: A3 }, { lead: 0, bass: 0 },
            { lead: Cs6, bass: D3 }, { lead: B5, bass: 0 },
            { lead: A5, bass: A3 }, { lead: G5, bass: 0 },
            { lead: Fs5, bass: D3 }, { lead: E5, bass: A3 },
            { lead: D5, bass: D3 }, { lead: D5, bass: 0 },

            // Measure 2
            { lead: E5, bass: A3 }, { lead: 0, bass: 0 },
            { lead: Fs5, bass: Cs4 }, { lead: 0, bass: 0 },
            { lead: G5, bass: A3 }, { lead: 0, bass: 0 },
            { lead: B5, bass: Cs4 }, { lead: 0, bass: 0 },
            { lead: A5, bass: A3 }, { lead: G5, bass: 0 },
            { lead: Fs5, bass: Cs4 }, { lead: E5, bass: 0 },
            { lead: D5, bass: D3 }, { lead: 0, bass: 0 },
            { lead: 0, bass: A3 }, { lead: 0, bass: 0 },

            // Measure 3
            { lead: Fs5, bass: D3 }, { lead: A5, bass: 0 },
            { lead: D6, bass: A3 }, { lead: Fs5, bass: 0 },
            { lead: A5, bass: D3 }, { lead: D6, bass: 0 },
            { lead: Fs6, bass: A3 }, { lead: 0, bass: 0 },
            { lead: E6, bass: G3 }, { lead: D6, bass: 0 },
            { lead: Cs6, bass: A3 }, { lead: B5, bass: 0 },
            { lead: A5, bass: A3 }, { lead: A5, bass: 0 },
            { lead: 0, bass: 0 }, { lead: 0, bass: 0 },

            // Measure 4 (Theme Turnaround)
            { lead: G5, bass: G3 }, { lead: 0, bass: 0 },
            { lead: B5, bass: D4 }, { lead: 0, bass: 0 },
            { lead: A5, bass: A3 }, { lead: 0, bass: 0 },
            { lead: Cs6, bass: E4 }, { lead: 0, bass: 0 },
            { lead: D6, bass: D3 }, { lead: 0, bass: 0 },
            { lead: Fs5, bass: A3 }, { lead: 0, bass: 0 },
            { lead: D5, bass: D3 }, { lead: 0, bass: 0 },
            { lead: 0, bass: 0 }, { lead: 0, bass: 0 }
        ];
    }

    playNote(leadFreq, bassFreq, durSec) {
        if (!this.ctx) return;
        const now = this.ctx.currentTime;

        // Lead synth (Vintage Moog Square with Lowpass filter pluck)
        if (leadFreq > 0) {
            const osc = this.ctx.createOscillator();
            const filter = this.ctx.createBiquadFilter();
            const gain = this.ctx.createGain();

            osc.type = 'square';
            osc.frequency.setValueAtTime(leadFreq, now);

            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(3200, now);
            filter.frequency.exponentialRampToValueAtTime(400, now + durSec * 0.9);
            filter.Q.setValueAtTime(3.5, now);

            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + durSec * 0.95);

            osc.connect(filter);
            filter.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + durSec);
        }

        // Bass synth (Warm punchy triangle)
        if (bassFreq > 0) {
            const bOsc = this.ctx.createOscillator();
            const bFilter = this.ctx.createBiquadFilter();
            const bGain = this.ctx.createGain();

            bOsc.type = 'triangle';
            bOsc.frequency.setValueAtTime(bassFreq, now);

            bFilter.type = 'lowpass';
            bFilter.frequency.setValueAtTime(450, now);

            bGain.gain.setValueAtTime(0.22, now);
            bGain.gain.exponentialRampToValueAtTime(0.001, now + durSec * 0.85);

            bOsc.connect(bFilter);
            bFilter.connect(bGain);
            bGain.connect(this.ctx.destination);

            bOsc.start(now);
            bOsc.stop(now + durSec);
        }
    }

    start() {
        this.initAudioContext();
        if (this.isPlaying) return;
        this.isPlaying = true;
        this.stepIndex = 0;

        const score = this.getScore();
        const stepTimeSec = (60.0 / this.tempoBpm) / 4.0; // 16th note timing

        this.timer = setInterval(() => {
            if (!this.isPlaying) return;
            const step = score[this.stepIndex % score.length];
            this.playNote(step.lead, step.bass, stepTimeSec);
            this.stepIndex++;
        }, stepTimeSec * 1000);
    }

    stop() {
        this.isPlaying = false;
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        this.stepIndex = 0;
    }

    onFleetShowStart() {
        if (this.musicEnabled) {
            this.start();
        }
    }

    onFleetShowStop() {
        if (!this.musicEnabled) {
            this.stop();
        }
    }
}

const baroqueSynth = new BaroqueHoedownSynth();

function initBaroqueSynth() {
    const btn = document.getElementById('audioToggleBtn');
    if (btn) {
        btn.addEventListener('click', () => {
            baroqueSynth.toggleMusic();
        });
    }
}

// ===========================================================================
// 3D TPU ARMOR PANEL VIEWER & STL COMPILATION CONTROLLER
// ===========================================================================
let tpuScene = null;
let tpuCamera = null;
let tpuRenderer = null;
let tpuControls = null;
let tpuStlMesh = null;
let tpuGraphicMesh = null;
let tpuLedsGroup = null;
let tpuLedMaterials = [];
let tpuBaseColors = [];
let tpuLedMode = 'on'; // 'off', 'on', 'animate'
let tpuAnimClock = 0;
let tpuAnimFrameId = null;
let tpuIsOpen = false;

const TPU_IMG_WIDTH_MM = 185.0;
const TPU_IMG_HEIGHT_MM = 222.09;
const TPU_STL_CENTER_X = 87.846;
const TPU_STL_CENTER_Y = 108.536;
const TPU_STL_CENTER_Z = 3.0;

function initTpuArmorPanel() {
    const openBtn = document.getElementById('openTpuPreviewModalBtn');
    const closeBtn = document.getElementById('closeTpuPreviewModalBtn');
    const closeBottomBtn = document.getElementById('closeTpuPreviewModalBottomBtn');
    const compileBtn = document.getElementById('compileTpuStlBtn');
    const modal = document.getElementById('tpuPreviewModal');

    if (openBtn) openBtn.addEventListener('click', openTpuPreviewModal);
    if (closeBtn) closeBtn.addEventListener('click', closeTpuPreviewModal);
    if (closeBottomBtn) closeBottomBtn.addEventListener('click', closeTpuPreviewModal);

    // Modal background click to close
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeTpuPreviewModal();
        });
    }

    // Camera view buttons
    document.getElementById('tpuModalViewFrontBtn')?.addEventListener('click', () => setTpuModalView('front'));
    document.getElementById('tpuModalViewBackBtn')?.addEventListener('click', () => setTpuModalView('back'));
    document.getElementById('tpuModalViewIsoBtn')?.addEventListener('click', () => setTpuModalView('iso'));

    // LED simulation modes
    document.getElementById('tpuModalLedOffBtn')?.addEventListener('click', () => setTpuModalLedMode('off'));
    document.getElementById('tpuModalLedStaticBtn')?.addEventListener('click', () => setTpuModalLedMode('on'));
    document.getElementById('tpuModalLedAnimBtn')?.addEventListener('click', () => setTpuModalLedMode('animate'));

    // Opacity sliders
    document.getElementById('tpuModalGraphicOpSlider')?.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        document.getElementById('tpuModalGraphicOpVal').textContent = `${val}%`;
        if (tpuGraphicMesh && tpuGraphicMesh.material) {
            tpuGraphicMesh.material.opacity = val / 100.0;
            tpuGraphicMesh.visible = val > 0;
        }
    });

    document.getElementById('tpuModalPlateOpSlider')?.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        document.getElementById('tpuModalPlateOpVal').textContent = `${val}%`;
        if (tpuStlMesh && tpuStlMesh.material) {
            tpuStlMesh.material.opacity = val / 100.0;
            tpuStlMesh.material.transparent = val < 100;
        }
    });

    // Recompile STL button
    if (compileBtn) {
        compileBtn.addEventListener('click', handleRecompileTpuStl);
    }

    // Initialize hole shape button styling
    setTpuWindowShape(params.tpuWindowShape || 'square');
}
window.initTpuArmorPanel = initTpuArmorPanel;
window.openTpuPreviewModal = openTpuPreviewModal;
window.closeTpuPreviewModal = closeTpuPreviewModal;
window.handleRecompileTpuStl = handleRecompileTpuStl;

function getActiveFloatName() {
    if (typeof activeSingleShirtRunnerSlot !== 'undefined' && activeSingleShirtRunnerSlot !== null && typeof fleetRunners !== 'undefined' && fleetRunners[activeSingleShirtRunnerSlot]) {
        return fleetRunners[activeSingleShirtRunnerSlot].name || fleetRunners[activeSingleShirtRunnerSlot].fullName || "Parade Float";
    }
    const nameMap = {
        'casey_jr_train': "Casey Jr. Circus Train",
        'title_drum': "MSEP Title Drum",
        'spinning_turtle': "The Spinning Turtle",
        'spinning_snail': "The Spinning Snail",
        'cinderellas_coach': "Cinderella's Coach",
        'cinderella_coach': "Cinderella's Coach",
        'carriage_nohorses': "Cinderella's Carriage",
        'builtin_dragon': "Pete's Dragon",
        'petes_dragon': "Pete's Dragon",
        'honor_america_eagle': "Honor America Eagle",
        'custom_image': "Custom Artwork"
    };
    return nameMap[currentGraphicType] || "Parade Float";
}
window.getActiveFloatName = getActiveFloatName;

// Fingerprint of everything that shapes the STL (artwork silhouette, LED layout, chest bounds, window shape).
// Stored in tpu_panel_specs.json so the Preview button can detect a stale STL compiled for another graphic or hole geometry.
function computeTpuLayoutSignature() {
    const activeImg = getActiveGraphicImg();
    const src = (activeImg && activeImg.src) ? activeImg.src : 'none';
    const gb = getGraphicChestBounds() || {};
    const winShape = params.tpuWindowShape || 'square';
    let h = 5381;
    const mix = (str) => {
        const step = Math.max(1, Math.floor(str.length / 4096)); // sample long data URLs
        for (let i = 0; i < str.length; i += step) h = ((h * 33) ^ str.charCodeAt(i)) >>> 0;
        h = ((h * 33) ^ str.length) >>> 0;
    };
    mix(String(currentGraphicType));
    mix(src);
    mix(String(winShape));
    mix([gb.normX, gb.normY, gb.normW, gb.normH].map(v => Number(v || 0).toFixed(4)).join(','));
    mix((leds || []).map(l => `${Number(l.x).toFixed(4)},${Number(l.y).toFixed(4)}`).join(';'));
    return `${currentGraphicType}-${winShape}-${h.toString(16)}`;
}
window.computeTpuLayoutSignature = computeTpuLayoutSignature;

function setTpuWindowShape(shape) {
    if (shape !== 'round' && shape !== 'square') shape = 'square';
    params.tpuWindowShape = shape;
    try { localStorage.setItem('msep_tpu_window_shape', shape); } catch (e) {}

    // Update Layout tab buttons styling
    const sqBtn = document.getElementById('tpuShapeSquareBtn');
    const rdBtn = document.getElementById('tpuShapeRoundBtn');
    if (sqBtn && rdBtn) {
        if (shape === 'square') {
            sqBtn.style.background = '#00ff88';
            sqBtn.style.color = '#000';
            sqBtn.style.fontWeight = '700';
            rdBtn.style.background = 'transparent';
            rdBtn.style.color = '#8b949e';
            rdBtn.style.fontWeight = '600';
        } else {
            rdBtn.style.background = '#00ff88';
            rdBtn.style.color = '#000';
            rdBtn.style.fontWeight = '700';
            sqBtn.style.background = 'transparent';
            sqBtn.style.color = '#8b949e';
            sqBtn.style.fontWeight = '600';
        }
    }

    // Update 3D modal shape buttons styling
    const modalSqBtn = document.getElementById('tpuModalShapeSquareBtn');
    const modalRdBtn = document.getElementById('tpuModalShapeRoundBtn');
    if (modalSqBtn && modalRdBtn) {
        if (shape === 'square') {
            modalSqBtn.style.background = '#00ff88';
            modalSqBtn.style.color = '#000';
            modalRdBtn.style.background = 'transparent';
            modalRdBtn.style.color = 'rgba(0,0,0,0.7)';
        } else {
            modalRdBtn.style.background = '#00ff88';
            modalRdBtn.style.color = '#000';
            modalSqBtn.style.background = 'transparent';
            modalSqBtn.style.color = 'rgba(0,0,0,0.7)';
        }
    }

    // Update modal subtitle
    const sub = document.getElementById('tpuModalSubtitle');
    if (sub) {
        const shapeText = (shape === 'round') ? 'Ø 3mm Round Windows' : '3×3mm Square Windows';
        sub.textContent = `95A TPU Open-Chassis Tray • ${shapeText} • Zero Overlap Pockets`;
    }

    markSingleShirtDirty();

    // Redraw 2D canvas preview
    if (typeof draw === 'function') draw();

    // If modal is open, trigger auto-recompile / reload to match chosen shape
    if (tpuIsOpen) {
        openTpuPreviewModal();
    }
}
window.setTpuWindowShape = setTpuWindowShape;

async function handleRecompileTpuStl(opts) {
    const skipOpen = !!(opts && opts.skipOpen === true);
    const statusEl = document.getElementById('tpuCompileStatus');
    const compileBtn = document.getElementById('compileTpuStlBtn');
    if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.style.color = '#58a6ff';
        statusEl.textContent = '⚙️ Compiling watertight 95A TPU STL for active float...';
    }
    if (compileBtn) compileBtn.disabled = true;

    try {
        const activeImg = getActiveGraphicImg();
        const gb = getGraphicChestBounds();
        let artworkDataUrl = null;

        if (activeImg && activeImg.naturalWidth > 0 && activeImg.naturalHeight > 0) {
            const off = document.createElement('canvas');
            const targetW = 1024;
            const targetH = Math.max(100, Math.round(targetW * (activeImg.naturalHeight / activeImg.naturalWidth)));
            off.width = targetW;
            off.height = targetH;
            const octx = off.getContext('2d');
            octx.drawImage(activeImg, 0, 0, targetW, targetH);
            artworkDataUrl = off.toDataURL('image/png');
        }

        const slot = (typeof activeSingleShirtRunnerSlot !== 'undefined' && activeSingleShirtRunnerSlot !== null) ? activeSingleShirtRunnerSlot : 5;
        const floatName = getActiveFloatName();

        const payload = {
            leds: leds || [],
            floatIndex: slot,
            floatName: floatName,
            graphicType: currentGraphicType,
            windowShape: params.tpuWindowShape || 'square',
            bounds: gb,
            artworkDataUrl: artworkDataUrl,
            layoutSignature: computeTpuLayoutSignature()
        };

        const resp = await fetch('/api/generate_tpu_stl', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();

        if (data.success) {
            if (statusEl) {
                statusEl.style.color = '#00ff88';
                statusEl.textContent = `✅ Compiled ${data.float_name || floatName} STL (${(data.stl_size / 1024 / 1024).toFixed(2)} MB)!`;
            }
            showToast(`✨ ${data.float_name || floatName} 3D TPU Armor Plate STL compiled!`);
            if (!skipOpen) openTpuPreviewModal();
            return true;
        } else {
            throw new Error(data.error || 'Compilation failed');
        }
    } catch (err) {
        if (statusEl) {
            statusEl.style.color = '#ff4d6d';
            statusEl.textContent = `❌ Compilation error: ${err.message}`;
        }
        showToast(`Compilation failed: ${err.message}`, 'error');
        return false;
    } finally {
        if (compileBtn) compileBtn.disabled = false;
    }
}

let tpuAutoCompileInFlight = false;

async function openTpuPreviewModal() {
    console.log("[TPU Preview] Opening 3D Armor Panel modal...");
    const modal = document.getElementById('tpuPreviewModal');
    if (!modal) {
        console.error("[TPU Preview] Element #tpuPreviewModal not found in DOM");
        return;
    }
    modal.style.display = 'flex';
    tpuIsOpen = true;

    const container = document.getElementById('tpuModalCanvasContainer');
    if (!container) return;

    if (!tpuRenderer) {
        setupTpuThreeScene(container);
    } else {
        onTpuWindowResize();
    }
    setTimeout(onTpuWindowResize, 60);

    // Stale-STL guard: if the compiled panel was built for a different graphic or LED layout,
    // recompile first so the plate silhouette matches the artwork shown on the canvas.
    if (!tpuAutoCompileInFlight) {
        let compiledSig = null;
        try {
            const r = await fetch('/3d_panels/tpu_panel_specs.json?t=' + Date.now());
            if (r.ok) compiledSig = (await r.json()).layout_signature || null;
        } catch (e) {}

        if (compiledSig !== computeTpuLayoutSignature()) {
            const loaderOverlay = document.getElementById('tpuModalLoading');
            if (loaderOverlay) {
                loaderOverlay.style.display = 'flex';
                loaderOverlay.innerHTML = `
                    <div class="spinner" style="width: 32px; height: 32px; border: 3px solid rgba(0, 255, 136, 0.2); border-top-color: #00ff88; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                    <span>Active graphic changed — compiling fresh Front &amp; Back STLs for this artwork...</span>
                `;
            }
            tpuAutoCompileInFlight = true;
            try {
                await handleRecompileTpuStl({ skipOpen: true });
            } finally {
                tpuAutoCompileInFlight = false;
            }
        }
    }

    if (tpuIsOpen) loadTpuModalData();
}

function closeTpuPreviewModal() {
    const modal = document.getElementById('tpuPreviewModal');
    if (modal) modal.style.display = 'none';
    tpuIsOpen = false;
    if (tpuAnimFrameId) {
        cancelAnimationFrame(tpuAnimFrameId);
        tpuAnimFrameId = null;
    }
}

function setupTpuThreeScene(container) {
    if (typeof THREE === 'undefined') {
        console.warn("[TPU Preview] Three.js not yet loaded from CDN");
        const loaderOverlay = document.getElementById('tpuModalLoading');
        if (loaderOverlay) {
            loaderOverlay.innerHTML = `
                <div style="color:#ffb703; text-align:center; padding:20px;">
                    <p style="font-size:14px; font-weight:700;">WebGL 3D engine is initializing...</p>
                    <p style="font-size:12px; color:#c9d1d9; margin-top:8px;">You can also view the full model in a dedicated tab:</p>
                    <a href="/3d_panels/tpu_panel_preview.html" target="_blank" class="action-btn primary" style="display:inline-block; margin-top:10px; text-decoration:none; padding:8px 16px;">↗️ Open Standalone 3D Viewer</a>
                </div>
            `;
        }
        return;
    }

    const w = container.clientWidth || 800;
    const h = container.clientHeight || 550;

    tpuScene = new THREE.Scene();
    tpuScene.background = new THREE.Color(0x070a0f);

    tpuCamera = new THREE.PerspectiveCamera(40, w / h, 1.0, 3000);
    tpuCamera.position.set(0, 0, 320);

    tpuRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, logarithmicDepthBuffer: true });
    tpuRenderer.setSize(w, h);
    tpuRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    tpuRenderer.toneMapping = THREE.ACESFilmicToneMapping;
    tpuRenderer.toneMappingExposure = 1.1;
    container.innerHTML = '';
    container.appendChild(tpuRenderer.domElement);

    if (THREE.OrbitControls) {
        tpuControls = new THREE.OrbitControls(tpuCamera, tpuRenderer.domElement);
        tpuControls.enableDamping = true;
        tpuControls.dampingFactor = 0.05;
        tpuControls.maxDistance = 800;
        tpuControls.minDistance = 60;
    }

    // Studio Lighting
    const ambLight = new THREE.AmbientLight(0xffffff, 0.75);
    tpuScene.add(ambLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 0.85);
    keyLight.position.set(80, 120, 200);
    tpuScene.add(keyLight);

    const backLight = new THREE.DirectionalLight(0x38bdf8, 0.7);
    backLight.position.set(-100, -100, -200);
    tpuScene.add(backLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
    fillLight.position.set(0, -150, 100);
    tpuScene.add(fillLight);

    window.addEventListener('resize', onTpuWindowResize);
}

function onTpuWindowResize() {
    const container = document.getElementById('tpuModalCanvasContainer');
    if (!container || !tpuRenderer || !tpuCamera) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w <= 0 || h <= 0) return;
    tpuCamera.aspect = w / h;
    tpuCamera.updateProjectionMatrix();
    tpuRenderer.setSize(w, h);
}

let tpuActiveVariant = 'front'; // 'front' or 'back'

function switchTpuModalVariant(variant) {
    if (variant !== 'front' && variant !== 'back') variant = 'front';
    tpuActiveVariant = variant;

    // Update button styling
    const fBtn = document.getElementById('tpuModalSelectFrontBtn');
    const bBtn = document.getElementById('tpuModalSelectBackBtn');
    if (fBtn && bBtn) {
        if (variant === 'front') {
            fBtn.style.background = '#000';
            fBtn.style.color = '#00ff88';
            bBtn.style.background = 'transparent';
            bBtn.style.color = 'rgba(0,0,0,0.7)';
        } else {
            bBtn.style.background = '#000';
            bBtn.style.color = '#00ff88';
            fBtn.style.background = 'transparent';
            fBtn.style.color = 'rgba(0,0,0,0.7)';
        }
    }
    loadTpuModalData();
}
window.switchTpuModalVariant = switchTpuModalVariant;

function downloadBothTpuStls() {
    const a1 = document.createElement('a');
    a1.href = '/3d_panels/tpu_panel_front.stl';
    a1.download = 'tpu_panel_front.stl';
    document.body.appendChild(a1);
    a1.click();
    document.body.removeChild(a1);

    setTimeout(() => {
        const a2 = document.createElement('a');
        a2.href = '/3d_panels/tpu_panel_back.stl';
        a2.download = 'tpu_panel_back.stl';
        document.body.appendChild(a2);
        a2.click();
        document.body.removeChild(a2);
        showToast('📦 Downloading both Front & Back TPU STLs!');
    }, 400);
}
window.downloadBothTpuStls = downloadBothTpuStls;

let tpuLoadRequestId = 0;

function clearTpuSceneModel() {
    if (!tpuScene) return;
    const toRemove = [];
    tpuScene.traverse((child) => {
        // Collect all meshes and non-scene groups (exclude lights)
        if (child.isMesh || (child.isGroup && child !== tpuScene)) {
            toRemove.push(child);
        }
    });
    toRemove.forEach((obj) => {
        if (obj.parent) obj.parent.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
            if (Array.isArray(obj.material)) {
                obj.material.forEach((m) => {
                    if (m.map) m.map.dispose();
                    m.dispose();
                });
            } else {
                if (obj.material.map) obj.material.map.dispose();
                obj.material.dispose();
            }
        }
    });
    tpuStlMesh = null;
    tpuGraphicMesh = null;
    tpuLedsGroup = null;
    tpuLedMaterials = [];
    tpuBaseColors = [];
}

async function loadTpuModalData() {
    const reqId = ++tpuLoadRequestId;
    const loaderOverlay = document.getElementById('tpuModalLoading');
    if (loaderOverlay) {
        loaderOverlay.style.display = 'flex';
        loaderOverlay.innerHTML = `
            <div class="spinner" style="width: 32px; height: 32px; border: 3px solid rgba(0, 255, 136, 0.2); border-top-color: #00ff88; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
            <span>Loading ${tpuActiveVariant === 'back' ? 'Back (240mm)' : 'Front (185mm)'} STL & Shaders...</span>
        `;
    }

    try {
        let specs = null;
        try {
            const specsResp = await fetch('/3d_panels/tpu_panel_specs.json?t=' + Date.now());
            if (specsResp.ok) specs = await specsResp.json();
        } catch (e) {}

        if (!specs) {
            const fallbackResp = await fetch('/3d_panels/petes_dragon_specs.json?t=' + Date.now());
            specs = await fallbackResp.json();
        }

        if (reqId !== tpuLoadRequestId) return; // Superceded by newer request

        const variantData = (specs[tpuActiveVariant]) ? specs[tpuActiveVariant] : specs;
        const floatName = specs.float_name || getActiveFloatName();
        const variantTitle = (tpuActiveVariant === 'back') ? "Back Torso Plate" : "Front Chest Plate";

        const modalTitle = document.querySelector('#tpuPreviewModal h3');
        if (modalTitle) {
            modalTitle.textContent = `${floatName} 3D Flexible TPU Armor Panel • ${variantTitle}`;
        }

        const effectiveShape = specs.window_shape || params.tpuWindowShape || 'square';
        const modalSub = document.getElementById('tpuModalSubtitle');
        if (modalSub) {
            const shapeText = (effectiveShape === 'round' || effectiveShape === 'circle') ? 'Ø 3mm Round Windows' : '3×3mm Square Windows';
            modalSub.textContent = `95A TPU Open-Chassis Tray • ${shapeText} • Zero Overlap Pockets`;
        }

        // Sync modal shape buttons
        const mSqBtn = document.getElementById('tpuModalShapeSquareBtn');
        const mRdBtn = document.getElementById('tpuModalShapeRoundBtn');
        if (mSqBtn && mRdBtn) {
            const isRound = (effectiveShape === 'round' || effectiveShape === 'circle');
            if (isRound) {
                mRdBtn.style.background = '#00ff88';
                mRdBtn.style.color = '#000';
                mSqBtn.style.background = 'transparent';
                mSqBtn.style.color = 'rgba(0,0,0,0.7)';
            } else {
                mSqBtn.style.background = '#00ff88';
                mSqBtn.style.color = '#000';
                mRdBtn.style.background = 'transparent';
                mRdBtn.style.color = 'rgba(0,0,0,0.7)';
            }
        }

        // Update dimensions badge & bed clearance text
        const dimText = document.getElementById('tpuModalDimText');
        const weightText = document.getElementById('tpuModalWeightText');
        const snapClearance = document.getElementById('tpuModalSnapmakerClearance');
        const bambuClearance = document.getElementById('tpuModalBambuClearance');

        if (variantData.stl_bounds) {
            const b = variantData.stl_bounds;
            if (dimText) dimText.textContent = `${b[0]} × ${b[1]} × ${b[2]} mm`;
            const estWeight = Math.round((variantData.volume_mm3 || (b[0] * b[1] * 1.5)) * 0.00115);
            if (weightText) weightText.textContent = `~${estWeight} g`;
        } else if (dimText) {
            dimText.textContent = (tpuActiveVariant === 'back') ? '198.1 × 176.1 × 6.0 mm' : '157.0 × 139.8 × 6.0 mm';
        }

        if (snapClearance && bambuClearance) {
            if (tpuActiveVariant === 'back') {
                snapClearance.textContent = 'Snapmaker U1 (270×270mm): ~15mm margin ✓';
                bambuClearance.textContent = 'Bambu Lab (250×250mm safe): ~5mm margin ✓';
            } else {
                snapClearance.textContent = 'Snapmaker U1 (270×270mm): ~50mm margin ✓';
                bambuClearance.textContent = 'Bambu Lab (250×250mm safe): ~42mm margin ✓';
            }
        }

        let stlCenter = new THREE.Vector3(87.8, 108.5, 3.0);

        // Always clean up any existing meshes before instantiating new ones!
        clearTpuSceneModel();

        if (THREE.STLLoader) {
            const stlLoader = new THREE.STLLoader();
            const stlFile = (tpuActiveVariant === 'back') ? 'tpu_panel_back.stl' : 'tpu_panel_front.stl';
            let stlUrl = `/3d_panels/${stlFile}?t=` + Date.now();
            const geom = await new Promise((resolve, reject) => {
                stlLoader.load(stlUrl, resolve, undefined, () => {
                    // Fallback to legacy single-panel if needed
                    stlLoader.load('/3d_panels/tpu_panel.stl?t=' + Date.now(), resolve, undefined, reject);
                });
            });
            if (reqId !== tpuLoadRequestId) return; // Superceded by newer request

            geom.computeVertexNormals();
            geom.computeBoundingBox();
            stlCenter = geom.boundingBox.getCenter(new THREE.Vector3());

            const stlMat = new THREE.MeshStandardMaterial({
                color: (tpuActiveVariant === 'back') ? 0x142033 : 0x1a2230,
                roughness: 0.55,
                metalness: 0.15,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.95,
                depthWrite: true,
                polygonOffset: true,
                polygonOffsetFactor: 1.0,
                polygonOffsetUnits: 1.0
            });

            tpuStlMesh = new THREE.Mesh(geom, stlMat);
            tpuStlMesh.renderOrder = 0;
            tpuStlMesh.position.set(-stlCenter.x, -stlCenter.y, -stlCenter.z);
            tpuScene.add(tpuStlMesh);
        }

        await createTpuGraphicCutoutMesh(variantData, stlCenter);
        if (reqId !== tpuLoadRequestId) return; // Superceded by newer request

        createTpuLedPixels(variantData, stlCenter);

        if (loaderOverlay) loaderOverlay.style.display = 'none';

        startTpuAnimateLoop();
    } catch (err) {
        console.error("TPU Modal loading error:", err);
        if (loaderOverlay) {
            loaderOverlay.innerHTML = `<div style="color:#ef4444; font-weight:700;">Error Loading 3D Preview: ${err.message}</div>`;
        }
    }
}

async function createTpuGraphicCutoutMesh(specs, stlCenter) {
    if (tpuGraphicMesh && tpuScene) {
        tpuScene.remove(tpuGraphicMesh);
        if (tpuGraphicMesh.geometry) tpuGraphicMesh.geometry.dispose();
        if (tpuGraphicMesh.material) {
            if (tpuGraphicMesh.material.map) tpuGraphicMesh.material.map.dispose();
            tpuGraphicMesh.material.dispose();
        }
        tpuGraphicMesh = null;
    }

    const activeImg = getActiveGraphicImg();
    let img = new Image();
    img.crossOrigin = "anonymous";

    if (activeImg && activeImg.src) {
        img.src = activeImg.src;
    } else {
        img.src = '/3d_panels/active_artwork.png?t=' + Date.now();
    }

    await new Promise((resolve) => {
        if (img.complete && img.naturalWidth > 0) return resolve();
        img.onload = resolve;
        img.onerror = () => {
            img.onload = resolve;
            img.src = '/assets/petes_dragon_transparent.png';
        };
    });

    const imgW = img.naturalWidth || img.width || 1024;
    const imgH = img.naturalHeight || img.height || 1024;

    const canvas = document.createElement('canvas');
    canvas.width = imgW;
    canvas.height = imgH;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, imgW, imgH);

    ctx.globalCompositeOperation = 'destination-out';
    const totalW_mm = specs.total_image_width_mm || specs.width_mm || 185.0;
    const totalH_mm = specs.total_image_height_mm || specs.height_mm || (Math.round((totalW_mm / (imgW / imgH)) * 100) / 100);

    const hwPx = (1.5 / totalW_mm) * imgW;
    const hhPx = (1.5 / totalH_mm) * imgH;

    const winShape = specs.window_shape || params.tpuWindowShape || 'square';
    const isRound = (winShape === 'round' || winShape === 'circle');

    const ledsList = specs.ordered_leds || [];
    ledsList.forEach(l => {
        const px = (l.x / totalW_mm) * imgW;
        const py = (1.0 - (l.y / totalH_mm)) * imgH;
        if (isRound) {
            ctx.beginPath();
            ctx.arc(px, py, hwPx, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.fillRect(px - hwPx, py - hhPx, hwPx * 2, hhPx * 2);
        }
    });

    ctx.globalCompositeOperation = 'source-over';

    const tex = new THREE.CanvasTexture(canvas);
    tex.anisotropy = 4;

    const artGeom = new THREE.PlaneGeometry(totalW_mm, totalH_mm);
    const artMat = new THREE.MeshBasicMaterial({
        map: tex,
        transparent: true,
        opacity: 1.0,
        side: THREE.DoubleSide,
        depthWrite: false,
        depthTest: true,
        polygonOffset: true,
        polygonOffsetFactor: -1.0,
        polygonOffsetUnits: -2.0
    });

    tpuGraphicMesh = new THREE.Mesh(artGeom, artMat);
    tpuGraphicMesh.renderOrder = 2; // Always render on top of STL plate
    tpuGraphicMesh.position.set(
        (totalW_mm / 2.0) - stlCenter.x,
        (totalH_mm / 2.0) - stlCenter.y,
        stlCenter.z + 0.35 // Clean 0.35mm physical lift above the TPU front skin
    );
    tpuScene.add(tpuGraphicMesh);
}

function createTpuLedPixels(specs, stlCenter) {
    if (tpuLedsGroup) tpuScene.remove(tpuLedsGroup);
    tpuLedsGroup = new THREE.Group();
    tpuLedsGroup.renderOrder = 3; // Render on top of aperture cutouts
    tpuLedMaterials = [];
    tpuBaseColors = [];

    const winShape = specs.window_shape || params.tpuWindowShape || 'square';
    const isRound = (winShape === 'round' || winShape === 'circle');

    const ledsList = specs.ordered_leds || [];
    const pixelGeom = isRound ? new THREE.CircleGeometry(1.4, 24) : new THREE.PlaneGeometry(2.8, 2.8);

    ledsList.forEach((l, idx) => {
        const c = l.color || { r: 0, g: 255, b: 100 };
        const col = new THREE.Color(c.r / 255, c.g / 255, c.b / 255);
        tpuBaseColors.push(col);

        const mat = new THREE.MeshBasicMaterial({
            color: col.clone(),
            side: THREE.DoubleSide,
            depthWrite: false,
            depthTest: true,
            polygonOffset: true,
            polygonOffsetFactor: -2.0,
            polygonOffsetUnits: -4.0
        });
        tpuLedMaterials.push(mat);

        const pixelMesh = new THREE.Mesh(pixelGeom, mat);
        pixelMesh.renderOrder = 3;
        pixelMesh.position.set(
            l.x - stlCenter.x,
            l.y - stlCenter.y,
            stlCenter.z + 0.20 // Positioned cleanly inside the 3x3mm optical window
        );
        tpuLedsGroup.add(pixelMesh);
    });

    tpuScene.add(tpuLedsGroup);
}

function startTpuAnimateLoop() {
    if (tpuAnimFrameId) cancelAnimationFrame(tpuAnimFrameId);

    function loop() {
        if (!tpuIsOpen) return;
        tpuAnimFrameId = requestAnimationFrame(loop);
        if (tpuControls) tpuControls.update();

        if (tpuLedMode === 'animate' && tpuLedsGroup) {
            tpuAnimClock += 0.035;
            const num = tpuLedMaterials.length;
            for (let i = 0; i < num; i++) {
                const wave = (Math.sin(tpuAnimClock * 4 - i * 0.15) + 1.0) / 2.0;
                const sparkle = (Math.sin(tpuAnimClock * 9 + i * 3.7) > 0.85) ? 1.5 : 1.0;
                const factor = (0.2 + 0.8 * wave) * sparkle;
                const base = tpuBaseColors[i];
                tpuLedMaterials[i].color.setRGB(
                    Math.min(1.0, base.r * factor),
                    Math.min(1.0, base.g * factor),
                    Math.min(1.0, base.b * factor)
                );
            }
        }

        if (tpuRenderer && tpuScene && tpuCamera) {
            tpuRenderer.render(tpuScene, tpuCamera);
        }
    }
    loop();
}

function setTpuModalView(view) {
    if (!tpuCamera || !tpuControls) return;
    document.querySelectorAll('#tpuModalViewFrontBtn, #tpuModalViewBackBtn, #tpuModalViewIsoBtn').forEach(b => {
        b.style.borderColor = 'var(--border-color)';
        b.style.color = 'var(--text-main)';
    });

    if (view === 'front') {
        const btn = document.getElementById('tpuModalViewFrontBtn');
        if (btn) { btn.style.borderColor = '#00ff88'; btn.style.color = '#00ff88'; }
        tpuCamera.position.set(0, 0, 320);
        tpuControls.target.set(0, 0, 0);
    } else if (view === 'back') {
        const btn = document.getElementById('tpuModalViewBackBtn');
        if (btn) { btn.style.borderColor = '#00ff88'; btn.style.color = '#00ff88'; }
        tpuCamera.position.set(0, 0, -320);
        tpuControls.target.set(0, 0, 0);
    } else if (view === 'iso') {
        const btn = document.getElementById('tpuModalViewIsoBtn');
        if (btn) { btn.style.borderColor = '#00ff88'; btn.style.color = '#00ff88'; }
        tpuCamera.position.set(160, -140, 220);
        tpuControls.target.set(0, 0, 0);
    }
}

function setTpuModalLedMode(mode) {
    tpuLedMode = mode;
    document.querySelectorAll('#tpuModalLedOffBtn, #tpuModalLedStaticBtn, #tpuModalLedAnimBtn').forEach(b => {
        b.style.borderColor = 'var(--border-color)';
        b.style.color = 'var(--text-main)';
    });

    if (mode === 'off') {
        const b = document.getElementById('tpuModalLedOffBtn');
        if (b) { b.style.borderColor = '#8b949e'; b.style.color = '#8b949e'; }
        if (tpuLedsGroup) tpuLedsGroup.visible = false;
    } else if (mode === 'on') {
        const b = document.getElementById('tpuModalLedStaticBtn');
        if (b) { b.style.borderColor = '#00ff88'; b.style.color = '#00ff88'; }
        if (tpuLedsGroup) tpuLedsGroup.visible = true;
        for (let i = 0; i < tpuLedMaterials.length; i++) {
            tpuLedMaterials[i].color.copy(tpuBaseColors[i]);
        }
    } else if (mode === 'animate') {
        const b = document.getElementById('tpuModalLedAnimBtn');
        if (b) { b.style.borderColor = '#ffb703'; b.style.color = '#ffb703'; }
        if (tpuLedsGroup) tpuLedsGroup.visible = true;
    }
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initSidebarTabs();
        initTimelineCollapse();
        initTimelineHoverScrub();
        initSingleShirtFloatSelector();
        initFleetManager();
        initPowerBudgetCalculator();
        initFleetRadar();
        initMasterFleetBundleControls();
        initBaroqueSynth();
        initTpuArmorPanel();
        updateUndoRedoUI();
    });
} else {
    initSidebarTabs();
    initTimelineCollapse();
    initTimelineHoverScrub();
    initSingleShirtFloatSelector();
    initFleetManager();
    initPowerBudgetCalculator();
    initFleetRadar();
    initMasterFleetBundleControls();
    initBaroqueSynth();
    initTpuArmorPanel();
    updateUndoRedoUI();
}


