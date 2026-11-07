"""Segment lightning bug facets using black outlines; render numbered label map."""
import cv2
import numpy as np

SRC = 'assets/lightningbug_dots_removed_backup.png'
img = cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
alpha = img[:, :, 3]
fg = alpha > 100
bgr = img[:, :, :3].astype(int)
mx = bgr.max(axis=2)

# Outline pixels: dark
line = fg & (mx < 80)

# Close small gaps in outlines for labeling only
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
line_closed = cv2.morphologyEx(line.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool)
# Also treat the fg border as a barrier
barrier = line_closed | ~fg

regions = (~barrier).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(regions, connectivity=4)

# Drop tiny regions (merge later into neighbors)
MIN = 40
keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= MIN]

# Render numbered map
vis = np.full((h, w, 3), 255, np.uint8)
rng = np.random.default_rng(3)
for i in keep:
    vis[lab == i] = rng.integers(60, 255, 3)
vis[line] = 0
vis = cv2.resize(vis, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
for i in keep:
    cx, cy = cen[i]
    cv2.putText(vis, str(i), (int(cx * 2) - 8, int(cy * 2) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)
    cv2.putText(vis, str(i), (int(cx * 2) - 8, int(cy * 2) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
cv2.imwrite('scripts/lb_facet_labels.png', vis)
np.save('scripts/lb_labels.npy', lab)
print('regions kept:', len(keep))
for i in keep:
    m = lab == i
    print(i, st[i, cv2.CC_STAT_AREA], tuple(int(v) for v in cen[i]), np.median(bgr[m], axis=0).astype(int)[::-1])
