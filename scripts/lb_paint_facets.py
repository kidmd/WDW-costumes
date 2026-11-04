"""Paint each lightning bug facet a flat palette color without changing any outline or facet shape.

Inputs:
  assets/lightningbug_dots_removed_backup.png  (reference; never modified)
  scripts/lb_labels_v3.npy                     (facet labels from lb_facet_segment3.py)
"""
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

REF = 'assets/lightningbug_dots_removed_backup.png'
img = cv2.imread(REF, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
alpha = img[:, :, 3].copy()
bgr = img[:, :, :3].astype(int)
fg = alpha > 100
anyfg = alpha > 0
line = fg & (bgr.max(axis=2) < 80)          # identical outline definition used for segmentation
lab = np.load('scripts/lb_labels_v3.npy').copy()

# BGR palette
BLACK = (20, 20, 20)
GREEN = (94, 197, 34)
RED = (25, 25, 230)
YELLOW = (21, 204, 250)
BLUE = (235, 99, 37)

# Region 10 = wing left-edge strip + the two tiny tail-tip top facets: split by row
TIP_TOP = 1000
lab[(lab == 10) & (np.arange(h)[:, None] >= 136)] = TIP_TOP

COLOR = {}
for i in [12, 13, 14, 15, 16, 17, 19, 22, 25, 26,      # head / face / neck / jaw / brow (12: above eye)
          6, 7, 29, 30, 31, 33, 43]:                   # body (7: area between legs)
    COLOR[i] = GREEN
for i in [2, 3, 5, 10,                                 # wing
          32, 34, 35, 36, 37, 38, 39, 40]:            # legs
    COLOR[i] = BLUE
for i in [4, 8, 11,                                    # hat
          23, 24, 28,                                  # tail
          27]:                                         # mouth
    COLOR[i] = RED
for i in [1, 9, 41, 42,                                # antennae
          20, 21, TIP_TOP,                             # tail tip lantern
          18]:                                         # eye sclera
    COLOR[i] = YELLOW

ids = set(np.unique(lab)) - {0}
missing = ids - set(COLOR)
assert not missing, f'unassigned facets: {sorted(missing)}'

# Fill any unlabeled foreground pixel with nearest labeled pixel
unl = anyfg & (lab == 0)
if unl.any():
    _, (r_idx, c_idx) = distance_transform_edt(lab == 0, return_indices=True)
    lab[unl] = lab[r_idx[unl], c_idx[unl]]

out = np.zeros((h, w, 3), np.uint8)
for i, c in COLOR.items():
    out[lab == i] = c

# Iris: blue blob inside the eye facet (no outline) -> keep its exact shape, paint blue
eye = lab == 18
b, g, r = bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2]
iris = eye & (b > r + 15) & (b > 90)
iris = cv2.morphologyEx(iris.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, l2, st, _ = cv2.connectedComponentsWithStats(iris)
if n > 1:
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    iris = (l2 == big).astype(np.uint8)
    cnts, _ = cv2.findContours(iris, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(iris)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    iris = filled.astype(bool) & eye
    out[iris] = BLUE
    print('iris px:', int(iris.sum()))

# Recolor the yellow spur above the eye socket to Green (user request)
is_yellow = (out[:, :, 0] == YELLOW[0]) & (out[:, :, 1] == YELLOW[1]) & (out[:, :, 2] == YELLOW[2])
eye_spur = is_yellow & (
    ((np.arange(h)[:, None] >= 84) & (np.arange(h)[:, None] <= 90) & (np.arange(w)[None, :] >= 274) & (np.arange(w)[None, :] <= 281)) |
    ((np.arange(h)[:, None] == 91) & (np.arange(w)[None, :] >= 274) & (np.arange(w)[None, :] <= 276))
)
out[eye_spur] = GREEN
print('eye spur px recolored to green:', int(eye_spur.sum()))

# Outlines: exact same pixels, pure black
out[line] = BLACK

# Make the interior solid opaque (fix the partial transparency in the dome)
alpha[anyfg] = 255

res = cv2.merge([out[:, :, 0], out[:, :, 1], out[:, :, 2], alpha])
cv2.imwrite('scripts/lb_painted.png', res)

# Verification against reference
assert np.array_equal(line, fg & (res[:, :, :3].max(axis=2) < 80)), 'outline pixels changed!'
pal = np.array([BLACK, GREEN, RED, YELLOW, BLUE])
fgpix = res[anyfg][:, :3].astype(int)
ok = (np.abs(fgpix[:, None, :] - pal[None]).sum(axis=2) == 0).any(axis=1)
print('palette compliance: %.4f%%' % (100 * ok.mean()))
print('facets painted:', len(ids))
print('Total foreground pixels:', int(anyfg.sum()))
