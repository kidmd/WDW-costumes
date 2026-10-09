// ============================================================================
// STRICT LED CLEARANCE ENGINE (no 2.5mm wire-corridor / collar-collision warnings)
// Loaded before app.js. Works in true millimetres. Uses a symmetric pair test
// (A's wire openings vs B's collar AND B's wire openings vs A's collar), the 10mm
// strain-relief keep-out, silhouette-aware snapping, and a nearest-valid-spot search
// for any LED that physics relaxation could not free.
// Depends at call time on app.js globals: params, getGraphicChestBounds,
// selectedPlateWidthMm, getTpuBridgeLocationsNorm, getTpuWellRotationAngle,
// distSegmentToSegment, boostLedVibrancy.
// ============================================================================
var lastSampledLedPool = null;

function ledMmFrame() {
    const gb = (typeof getGraphicChestBounds === 'function') ? getGraphicChestBounds() : { normX: 0.1, normY: 0.168, normW: 0.8, normH: 0.385 };
    const plateW = (typeof selectedPlateWidthMm !== 'undefined' && selectedPlateWidthMm > 0) ? selectedPlateWidthMm : 203.2;
    const normW = (gb && gb.normW > 0) ? gb.normW : 0.8;
    // Norm units are isotropic in mm (mmToNormX === mmToNormY elsewhere in app.js)
    return { gb, mm2n: normW / plateW };
}

// True if collars A and B collide, or either one's 2.5mm wire corridor is blocked by the other.
function ledPairViolatesMm(ax, ay, ra, bx, by, rb, margin) {
    const dx = bx - ax, dy = by - ay;
    if (dx > 24 || dx < -24 || dy > 24 || dy < -24) return false;
    const uax = Math.cos(ra), uay = Math.sin(ra);
    const ubx = Math.cos(rb), uby = Math.sin(rb);
    const a1x = ax - 2.5 * uax, a1y = ay - 2.5 * uay, a2x = ax + 2.5 * uax, a2y = ay + 2.5 * uay;
    const b1x = bx - 2.5 * ubx, b1y = by - 2.5 * uby, b2x = bx + 2.5 * ubx, b2y = by + 2.5 * uby;
    if (distSegmentToSegment(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y) < 8.65 + margin) return true;
    const oc = 4.3 + margin;
    if (distSegmentToSegment(ax + 6.8 * uax, ay + 6.8 * uay, ax + 9.3 * uax, ay + 9.3 * uay, b1x, b1y, b2x, b2y) < oc) return true;
    if (distSegmentToSegment(ax - 6.8 * uax, ay - 6.8 * uay, ax - 9.3 * uax, ay - 9.3 * uay, b1x, b1y, b2x, b2y) < oc) return true;
    if (distSegmentToSegment(bx + 6.8 * ubx, by + 6.8 * uby, bx + 9.3 * ubx, by + 9.3 * uby, a1x, a1y, a2x, a2y) < oc) return true;
    if (distSegmentToSegment(bx - 6.8 * ubx, by - 6.8 * uby, bx - 9.3 * ubx, by - 9.3 * uby, a1x, a1y, a2x, a2y) < oc) return true;
    return false;
}

// Snap pool of valid on-artwork positions (norm coords; optional r,g,b,relX,relY for recoloring).
function makeLedPool(pts, cellNormX, cellNormY) {
    return { pts: pts, tolNorm: Math.hypot(cellNormX, cellNormY) * 1.6 };
}

// Clearance-aware Farthest Point Sampling: spreads LEDs evenly like FPS but never picks a
// spot that would warn against an already placed LED / anchor / strain relief bridge.
// Tries 1.0mm spare margin, then 0.3mm, then plain FPS only if the plate is truly full.
function selectClearanceAwareFpsIndices(candNorm, count, anchorsNorm) {
    const n = candNorm.length;
    const want = Math.min(count, n);
    if (want <= 0) return [];
    const mm2n = ledMmFrame().mm2n;
    const cx = new Float64Array(n), cy = new Float64Array(n);
    for (let i = 0; i < n; i++) { cx[i] = candNorm[i].x / mm2n; cy[i] = candNorm[i].y / mm2n; }

    const br = getTpuBridgeLocationsNorm();
    const bridges = [br.entrance, br.exit].map(b => ({ x: b.x / mm2n, y: b.y / mm2n }));

    const minD = new Float64Array(n).fill(1e18);
    const placedX = [], placedY = [];
    (anchorsNorm || []).forEach(a => {
        const ax = a.x / mm2n, ay = a.y / mm2n;
        placedX.push(ax); placedY.push(ay);
        for (let i = 0; i < n; i++) {
            const d = (cx[i] - ax) * (cx[i] - ax) + (cy[i] - ay) * (cy[i] - ay);
            if (d < minD[i]) minD[i] = d;
        }
    });

    const margins = [1.0, 0.3, null];
    let lvl = 0;
    const blocked = new Uint8Array(n);
    const used = new Uint8Array(n);
    const rebuild = () => {
        const mg = margins[lvl];
        for (let i = 0; i < n; i++) {
            blocked[i] = 0;
            if (mg === null) continue;
            for (let b = 0; b < bridges.length; b++) {
                if (Math.hypot(cx[i] - bridges[b].x, cy[i] - bridges[b].y) < 10.3) { blocked[i] = 1; break; }
            }
            if (blocked[i]) continue;
            for (let p = 0; p < placedX.length; p++) {
                if (ledPairViolatesMm(cx[i], cy[i], 0, placedX[p], placedY[p], 0, mg)) { blocked[i] = 1; break; }
            }
        }
    };
    rebuild();

    const selected = [];
    while (selected.length < want) {
        let best = -1;
        for (;;) {
            if (placedX.length === 0) {
                // First LED: start near the middle of the artwork
                for (let off = 0; off < n && best < 0; off++) {
                    const c1 = Math.floor(n / 2) + off, c2 = Math.floor(n / 2) - off;
                    if (c1 < n && !blocked[c1] && !used[c1]) best = c1;
                    else if (c2 >= 0 && !blocked[c2] && !used[c2]) best = c2;
                }
            } else {
                let bestD = -1;
                for (let i = 0; i < n; i++) {
                    if (!blocked[i] && !used[i] && minD[i] > bestD) { bestD = minD[i]; best = i; }
                }
            }
            if (best >= 0 || lvl >= margins.length - 1) break;
            lvl++;
            rebuild();
        }
        if (best < 0) break;
        used[best] = 1;
        selected.push(best);
        placedX.push(cx[best]); placedY.push(cy[best]);
        const mg = margins[lvl];
        for (let i = 0; i < n; i++) {
            const d = (cx[i] - cx[best]) * (cx[i] - cx[best]) + (cy[i] - cy[best]) * (cy[i] - cy[best]);
            if (d < minD[i]) minD[i] = d;
            if (mg !== null && !blocked[i] && ledPairViolatesMm(cx[i], cy[i], 0, cx[best], cy[best], 0, mg)) blocked[i] = 1;
        }
    }
    return selected;
}

// Resolve every wire-corridor / collar-collision / bridge warning it possibly can.
// ledsList: movable LED objects ({x,y} in norm space). Returns number of LEDs still warning (0 = perfect).
// opts: { fixedExtra:[led...], movable:Set(indexes), assumeHorizontal, iterations, margin, recolor }
function resolveLedClearance(ledsList, pool, opts) {
    opts = opts || {};
    if (!ledsList || ledsList.length === 0) return 0;
    const frame = ledMmFrame();
    const gb = frame.gb, mm2n = frame.mm2n;
    const margin = (opts.margin !== undefined) ? opts.margin : 0.6;
    const iterations = opts.iterations || 160;
    const all = ledsList.concat(opts.fixedExtra || []);
    const m = ledsList.length;
    const N = all.length;

    const movable = new Uint8Array(N);
    for (let i = 0; i < m; i++) movable[i] = (!opts.movable || opts.movable.has(i)) ? 1 : 0;

    const px = new Float64Array(N), py = new Float64Array(N), rot = new Float64Array(N);
    for (let i = 0; i < N; i++) { px[i] = all[i].x / mm2n; py[i] = all[i].y / mm2n; }

    const storePos = () => {
        for (let i = 0; i < m; i++) {
            if (!movable[i]) continue;
            all[i].x = parseFloat((px[i] * mm2n).toFixed(4));
            all[i].y = parseFloat((py[i] * mm2n).toFixed(4));
        }
    };
    const refreshRot = () => {
        storePos();
        for (let i = 0; i < N; i++) {
            if (opts.assumeHorizontal && !all[i].is_custom_rotation) rot[i] = 0;
            else rot[i] = (typeof getTpuWellRotationAngle === 'function') ? getTpuWellRotationAngle(i, all) : 0;
        }
    };

    const br = getTpuBridgeLocationsNorm();
    const bridges = [br.entrance, br.exit].map(b => ({ x: b.x / mm2n, y: b.y / mm2n }));
    const minX = gb.normX / mm2n, maxX = (gb.normX + gb.normW) / mm2n;
    const minY = gb.normY / mm2n, maxY = (gb.normY + gb.normH) / mm2n;

    const violatesAny = (i, mg) => {
        for (let j = 0; j < N; j++) {
            if (j === i) continue;
            if (ledPairViolatesMm(px[i], py[i], rot[i], px[j], py[j], rot[j], mg)) return true;
        }
        for (let b = 0; b < bridges.length; b++) {
            if (Math.hypot(px[i] - bridges[b].x, py[i] - bridges[b].y) < 10.0 + Math.max(0.05, mg * 0.5)) return true;
        }
        return false;
    };
    const violators = (mg) => {
        const out = [];
        for (let i = 0; i < m; i++) if (movable[i] && violatesAny(i, mg)) out.push(i);
        return out;
    };

    const dxA = new Float64Array(N), dyA = new Float64Array(N);
    const relax = () => {
        const oc = 4.3 + margin, sc = 8.65 + margin;
        for (let iter = 0; iter < iterations; iter++) {
            dxA.fill(0); dyA.fill(0);
            let viol = 0;
            for (let i = 0; i < N; i++) {
                const uix = Math.cos(rot[i]), uiy = Math.sin(rot[i]);
                for (let j = i + 1; j < N; j++) {
                    if (!movable[i] && !movable[j]) continue;
                    const ddx = px[j] - px[i], ddy = py[j] - py[i];
                    if (ddx > 24 || ddx < -24 || ddy > 24 || ddy < -24) continue;
                    if (!ledPairViolatesMm(px[i], py[i], rot[i], px[j], py[j], rot[j], margin)) continue;
                    viol++;
                    const ujx = Math.cos(rot[j]), ujy = Math.sin(rot[j]);
                    const wi = movable[i] ? (movable[j] ? 0.5 : 1) : 0;
                    const wj = movable[j] ? (movable[i] ? 0.5 : 1) : 0;
                    const cd = Math.hypot(ddx, ddy);
                    const nx = cd > 1e-4 ? ddx / cd : Math.cos(i * 2.39996);
                    const ny = cd > 1e-4 ? ddy / cd : Math.sin(i * 2.39996);

                    const a1x = px[i] - 2.5 * uix, a1y = py[i] - 2.5 * uiy, a2x = px[i] + 2.5 * uix, a2y = py[i] + 2.5 * uiy;
                    const b1x = px[j] - 2.5 * ujx, b1y = py[j] - 2.5 * ujy, b2x = px[j] + 2.5 * ujx, b2y = py[j] + 2.5 * ujy;
                    const sd = distSegmentToSegment(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y);
                    if (sd < sc) {
                        const pen = sc - sd + 0.2;
                        dxA[i] -= nx * pen * wi; dyA[i] -= ny * pen * wi;
                        dxA[j] += nx * pen * wj; dyA[j] += ny * pen * wj;
                    }
                    // Wire openings: [owner, sign along owner's axis, owner axis, other led, other's spine]
                    const checks = [
                        [i, +1, uix, uiy, j, b1x, b1y, b2x, b2y],
                        [i, -1, uix, uiy, j, b1x, b1y, b2x, b2y],
                        [j, +1, ujx, ujy, i, a1x, a1y, a2x, a2y],
                        [j, -1, ujx, ujy, i, a1x, a1y, a2x, a2y]
                    ];
                    for (let c = 0; c < checks.length; c++) {
                        const ck = checks[c];
                        const o = ck[0], sg = ck[1], ox = ck[2], oy = ck[3], other = ck[4];
                        const d = distSegmentToSegment(
                            px[o] + sg * 6.8 * ox, py[o] + sg * 6.8 * oy,
                            px[o] + sg * 9.3 * ox, py[o] + sg * 9.3 * oy,
                            ck[5], ck[6], ck[7], ck[8]);
                        if (d >= oc) continue;
                        const pen = oc - d + 0.2;
                        const wo = (o === i) ? wi : wj, wt = (o === i) ? wj : wi;
                        const lat = (o === i) ? 1 : -1; // n points i -> j; lateral push separates owner from intruder
                        // Owner backs away from its opening; the intruder is pushed past it. Plus a lateral push.
                        dxA[o] -= sg * ox * pen * 0.6 * wo; dyA[o] -= sg * oy * pen * 0.6 * wo;
                        dxA[other] += sg * ox * pen * 0.6 * wt; dyA[other] += sg * oy * pen * 0.6 * wt;
                        dxA[o] -= lat * nx * pen * 0.4 * wo; dyA[o] -= lat * ny * pen * 0.4 * wo;
                        dxA[other] += lat * nx * pen * 0.4 * wt; dyA[other] += lat * ny * pen * 0.4 * wt;
                    }
                }
            }
            for (let i = 0; i < m; i++) {
                if (!movable[i]) continue;
                for (let b = 0; b < bridges.length; b++) {
                    const bx = px[i] - bridges[b].x, by = py[i] - bridges[b].y;
                    const dist = Math.hypot(bx, by);
                    const need = 10.0 + Math.max(0.05, margin * 0.5);
                    if (dist < need) {
                        viol++;
                        const ux = dist > 1e-4 ? bx / dist : 1, uy = dist > 1e-4 ? by / dist : 0;
                        dxA[i] += ux * (need - dist + 0.2); dyA[i] += uy * (need - dist + 0.2);
                    }
                }
            }
            if (viol === 0) break;
            for (let i = 0; i < m; i++) {
                if (!movable[i]) continue;
                px[i] = Math.max(minX, Math.min(maxX, px[i] + dxA[i] * 0.7));
                py[i] = Math.max(minY, Math.min(maxY, py[i] + dyA[i] * 0.7));
            }
            if (!opts.assumeHorizontal && params.tpuWellOrientation !== 'horizontal' && iter % 10 === 9) refreshRot();
        }
    };

    const ptsMm = (pool && pool.pts) ? pool.pts.map(p => ({ x: p.x / mm2n, y: p.y / mm2n, src: p })) : null;
    const tolMm = pool ? pool.tolNorm / mm2n : 0;

    // Pull any LED that drifted off the artwork back onto the nearest valid on-artwork spot.
    const snapToArtwork = () => {
        if (!ptsMm || ptsMm.length === 0) return;
        for (let i = 0; i < m; i++) {
            if (!movable[i]) continue;
            let bd = 1e18, bk = -1;
            for (let k = 0; k < ptsMm.length; k++) {
                const d = (ptsMm[k].x - px[i]) * (ptsMm[k].x - px[i]) + (ptsMm[k].y - py[i]) * (ptsMm[k].y - py[i]);
                if (d < bd) { bd = d; bk = k; }
            }
            if (bk >= 0 && Math.sqrt(bd) > tolMm) { px[i] = ptsMm[bk].x; py[i] = ptsMm[bk].y; }
        }
    };

    // Move LED i to the nearest on-artwork spot that triggers no warning for itself or any neighbor.
    const searchFreeSpot = (i, mg) => {
        if (!ptsMm || ptsMm.length === 0) return false;
        const ox = px[i], oy = py[i];
        const radii = [14, 28, 56, 1e9];
        let prev = -1;
        for (let r = 0; r < radii.length; r++) {
            const R2 = radii[r] * radii[r], P2 = prev * prev;
            const ring = [];
            for (let k = 0; k < ptsMm.length; k++) {
                const d = (ptsMm[k].x - ox) * (ptsMm[k].x - ox) + (ptsMm[k].y - oy) * (ptsMm[k].y - oy);
                if (d <= R2 && d > P2) ring.push({ k: k, d: d });
            }
            ring.sort((a, b) => a.d - b.d);
            const lim = Math.min(ring.length, 4000);
            for (let t = 0; t < lim; t++) {
                px[i] = ptsMm[ring[t].k].x; py[i] = ptsMm[ring[t].k].y;
                if (!violatesAny(i, mg)) {
                    const src = ptsMm[ring[t].k].src;
                    if (opts.recolor !== false && src && src.r !== undefined && typeof boostLedVibrancy === 'function') {
                        all[i].color = boostLedVibrancy(src.r, src.g, src.b, src.relX, src.relY);
                    }
                    return true;
                }
            }
            prev = radii[r];
        }
        px[i] = ox; py[i] = oy;
        return false;
    };

    refreshRot();
    for (let round = 0; round < 3; round++) {
        relax();
        snapToArtwork();
        refreshRot();
        const bad = violators(margin);
        if (bad.length === 0) break;
        bad.forEach(i => { if (!searchFreeSpot(i, margin)) searchFreeSpot(i, 0.1); });
        refreshRot();
        if (violators(margin).length === 0) break;
    }
    storePos();
    refreshRot();
    return violators(0).length;
}

// Drop-in replacement for the legacy collar relaxation (used by older call sites).
function relaxLedCollarOverlaps(ledsList, iterations, pool) {
    return resolveLedClearance(ledsList, pool || null, { iterations: Math.max(iterations || 0, 120), assumeHorizontal: true, recolor: false });
}
