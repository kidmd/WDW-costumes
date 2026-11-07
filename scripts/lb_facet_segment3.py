"""Facet segmentation v3: intersect fine (K13) and coarse (K29) gap-bridged partitions, then watershed."""
import cv2
import numpy as np

SRC = 'assets/lightningbug_dots_removed_backup.png'
img = cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
fg = img[:, :, 3] > 100
bgr = img[:, :, :3]
mx = bgr.astype(int).max(axis=2)
line_orig = fg & (mx < 80)
# Manual gap bridges (labeling barriers only; never drawn into the artwork)
BRIDGES = [((166, 168), (166, 192)),   # wing right edge gap
           ((336, 73), (355, 87))]     # lower antenna base
_b = np.zeros((h, w), np.uint8)
for p, q in BRIDGES:
    cv2.line(_b, p, q, 1, 2)
line = line_orig | (_b.astype(bool) & fg)


def bridged_labels(K):
    lu = line.astype(np.uint8)
    br = lu.copy()
    c = K // 2
    for ang in range(0, 180, 15):
        kern = np.zeros((K, K), np.uint8)
        dx, dy = np.cos(np.radians(ang)) * c, np.sin(np.radians(ang)) * c
        cv2.line(kern, (int(round(c - dx)), int(round(c - dy))), (int(round(c + dx)), int(round(c + dy))), 1, 1)
        br |= cv2.morphologyEx(lu, cv2.MORPH_CLOSE, kern)
    barrier = br.astype(bool) | ~fg
    _, lab = cv2.connectedComponents((~barrier).astype(np.uint8), connectivity=4)
    return lab


fine = bridged_labels(13)
coarse = bridged_labels(29)

pair = fine.astype(np.int64) * 100000 + coarse
pair[fine == 0] = 0
markers = np.zeros((h, w), np.int32)
nid = 1
MINP = 120
for f in np.unique(fine):
    if f == 0:
        continue
    fm = fine == f
    if fm.sum() < 30:
        continue
    subs = [(c, int((fm & (coarse == c)).sum())) for c in np.unique(coarse[fm]) if c != 0]
    big = [c for c, a in subs if a >= MINP]
    if len(big) <= 1:
        markers[fm] = nid
        nid += 1
    else:
        for c in big:
            m = (fm & (coarse == c)).astype(np.uint8)
            n2, l2, st2, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
            for j in range(1, n2):
                if st2[j, cv2.CC_STAT_AREA] >= MINP:
                    markers[l2 == j] = nid
                    nid += 1

# Rescue thin facets (e.g. lower antenna) erased by the heavy closing: use light closing K=5
light = bridged_labels(5)
for l in np.unique(light):
    if l == 0:
        continue
    lm = light == l
    a = lm.sum()
    if a >= 100 and (markers[lm] > 0).sum() < 0.2 * a:
        markers[lm & (markers == 0)] = nid
        nid += 1
BG = nid + 1
mk = markers.copy()
mk[~fg] = BG
mk = cv2.watershed(bgr.copy(), mk)
mk[(mk == BG) | ~fg] = 0
neg = mk == -1
for _ in range(3):
    if not neg.any():
        break
    dil = cv2.dilate(np.where(mk > 0, mk, 0).astype(np.float32), np.ones((3, 3), np.uint8)).astype(np.int32)
    mk[neg] = dil[neg]
    neg = mk == -1
mk[mk < 0] = 0
np.save('scripts/lb_labels_v3.npy', mk)

ids = sorted(set(np.unique(mk)) - {0})
vis = np.full((h, w, 3), 255, np.uint8)
rng = np.random.default_rng(11)
for i in ids:
    vis[mk == i] = rng.integers(70, 255, 3)
vis[line] = 0
S = 2
vis = cv2.resize(vis, None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
for i in ids:
    m = (mk == i).astype(np.uint8)
    d = cv2.distanceTransform(m, cv2.DIST_L2, 3)
    y, x = np.unravel_index(np.argmax(d), d.shape)
    cv2.putText(vis, str(i), (x * S - 7, y * S + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 2)
    cv2.putText(vis, str(i), (x * S - 7, y * S + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
cv2.imwrite('scripts/lb_labels_v3.png', vis)
print('regions', len(ids))
for i in ids:
    m = mk == i
    print(i, int(m.sum()), np.median(bgr[m], axis=0).astype(int)[::-1].tolist())
