"""Facet segmentation v2: gap-bridged outlines + watershed on original colors."""
import cv2
import numpy as np
import sys

SRC = 'assets/lightningbug_dots_removed_backup.png'
K = int(sys.argv[1]) if len(sys.argv) > 1 else 9
img = cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
alpha = img[:, :, 3]
fg = alpha > 100
bgr = img[:, :, :3]
mx = bgr.astype(int).max(axis=2)
line = fg & (mx < 80)

# Bridge gaps: union of closings along multiple line orientations
lu = line.astype(np.uint8)
bridged = lu.copy()
for ang in range(0, 180, 15):
    kern = np.zeros((K, K), np.uint8)
    c = K // 2
    dx, dy = np.cos(np.radians(ang)) * c, np.sin(np.radians(ang)) * c
    cv2.line(kern, (int(round(c - dx)), int(round(c - dy))), (int(round(c + dx)), int(round(c + dy))), 1, 1)
    bridged |= cv2.morphologyEx(lu, cv2.MORPH_CLOSE, kern)
bridged = bridged.astype(bool)
barrier = bridged | ~fg

n, lab, st, cen = cv2.connectedComponentsWithStats((~barrier).astype(np.uint8), connectivity=4)
MIN = 30
markers = np.zeros((h, w), np.int32)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] >= MIN:
        markers[lab == i] = i

# Watershed: grow markers into unassigned fg pixels (bridges, tiny bits, line pixels) using original colors
ws_in = cv2.cvtColor(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
ws_in = bgr.copy()
mk = markers.copy()
mk[~fg] = -1  # will be overwritten; use a separate bg marker
BG = n + 5
mk[~fg] = BG
mk = cv2.watershed(ws_in, mk)
mk[~fg] = 0
mk[mk == BG] = 0
# watershed boundary pixels (-1): assign to neighbor majority
neg = mk == -1
if neg.any():
    dil = cv2.dilate(np.where(mk > 0, mk, 0).astype(np.float32), np.ones((3, 3), np.uint8)).astype(np.int32)
    mk[neg] = dil[neg]
np.save('scripts/lb_ws_labels.npy', mk)

ids = sorted(set(np.unique(mk)) - {0})
vis = np.full((h, w, 3), 255, np.uint8)
rng = np.random.default_rng(7)
for i in ids:
    vis[mk == i] = rng.integers(70, 255, 3)
vis[line] = 0
vis = cv2.resize(vis, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
for i in ids:
    ys, xs = np.where(mk == i)
    # label position: point deepest inside region
    m = (mk == i).astype(np.uint8)
    d = cv2.distanceTransform(m, cv2.DIST_L2, 3)
    y, x = np.unravel_index(np.argmax(d), d.shape)
    cv2.putText(vis, str(i), (x * 2 - 8, y * 2 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 2)
    cv2.putText(vis, str(i), (x * 2 - 8, y * 2 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
cv2.imwrite(f'scripts/lb_ws_labels_k{K}.png', vis)
print('K', K, 'regions', len(ids))
for i in ids:
    m = mk == i
    print(i, int(m.sum()), np.median(bgr[m], axis=0).astype(int)[::-1].tolist())
