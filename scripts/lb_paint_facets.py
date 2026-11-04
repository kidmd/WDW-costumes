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

# Region 10 = wing left-edge strip (entirely part of the BLUE wing)
COLOR = {}
for i in [12, 13, 14, 15, 16, 17, 19, 22, 25, 26,      # head / face / neck / jaw / brow (12: above eye)
          6, 7, 29, 30, 31, 33, 43]:                   # body (7: area between legs)
    COLOR[i] = GREEN
for i in [2, 3, 5, 10,                                 # wing (Facet 10 is 100% BLUE)
          32, 34, 35, 36, 37, 38, 39, 40]:            # legs
    COLOR[i] = BLUE
for i in [4, 8, 11,                                    # hat
          23, 24, 28,                                  # tail
          27]:                                         # mouth
    COLOR[i] = RED
for i in [1, 9, 42,                                    # antennae (41 is transparent gap)
          20, 21,                                      # tail tip lantern
          18]:                                         # eye sclera
    COLOR[i] = YELLOW

ids = set(np.unique(lab)) - {0, 41}
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

# Recolor the red triangle in the tail (with the white splotch) to Yellow (user request)
# Bounded by: [161:184, 61:96]
att1 = cv2.imread(r'C:\Users\Kiddi\.gemini\antigravity\brain\73963054-0e68-43d0-9a1f-4e7be7ecffb2\.system_generated\logs\media\step_984_media_1.png', cv2.IMREAD_UNCHANGED)
tri_in_att1 = ((att1[:, :, 3] == 0) | ((att1[:, :, 2] > 180) & (att1[:, :, 0] < 50))) & (att1[:, :, 1] < 100)
tri_full = np.zeros((h, w), dtype=bool)
tri_full[161:184, 61:96] = tri_in_att1
tri_full &= (~line)
out[tri_full] = YELLOW
print('tail triangle px recolored to yellow:', int(tri_full.sum()))

# Recolor the tip of the tail lantern dome to Yellow (user request)
# Bounded by: [130:152, 45:65]
tip_blue = (out[:, :, 0] == BLUE[0]) & (out[:, :, 1] == BLUE[1]) & (out[:, :, 2] == BLUE[2]) & (
    (np.arange(h)[:, None] >= 130) & (np.arange(h)[:, None] <= 152) &
    (np.arange(w)[None, :] >= 45) & (np.arange(w)[None, :] <= 65)
)
out[tip_blue] = YELLOW
print('tail tip px recolored to yellow:', int(tip_blue.sum()))

# Antenna 9 top border line against the transparent gap (facet 41):
f9 = lab == 9
f41 = lab == 41
dil41 = cv2.dilate(f41.astype(np.uint8), np.ones((3, 3), np.uint8))
border_9 = dil41.astype(bool) & f9
cnts, _ = cv2.findContours(f9.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
vis_c = np.zeros_like(f9, dtype=np.uint8)
cv2.drawContours(vis_c, cnts, -1, 1, 1)
line_extra = vis_c.astype(bool) & border_9

# Draw solid, black, easy to see outlines around the whole bug and between colors:
# Map each pixel to its primary color (Green=2, Blue=3, Red=4, Yellow=5)
color_field = np.zeros((h, w), dtype=np.uint8)
color_field[(out[:, :, 0] == GREEN[0]) & (out[:, :, 1] == GREEN[1]) & (out[:, :, 2] == GREEN[2])] = 2
color_field[(out[:, :, 0] == BLUE[0]) & (out[:, :, 1] == BLUE[1]) & (out[:, :, 2] == BLUE[2])] = 3
color_field[(out[:, :, 0] == RED[0]) & (out[:, :, 1] == RED[1]) & (out[:, :, 2] == RED[2])] = 4
color_field[(out[:, :, 0] == YELLOW[0]) & (out[:, :, 1] == YELLOW[1]) & (out[:, :, 2] == YELLOW[2])] = 5

is_fg = ((lab != 0) & (lab != 41)) | tri_full | line | line_extra
bg = ~is_fg

# Outer boundary around the whole bug:
outer_edge = cv2.dilate(bg.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & is_fg

# Color-to-color boundaries:
has_color = color_field > 0
_, (r_idx, c_idx) = distance_transform_edt(~has_color, return_indices=True)
full_color = color_field[r_idx, c_idx]

color_boundary = np.zeros((h, w), dtype=bool)
for c in [2, 3, 4, 5]:
    c_mask = (full_color == c) & is_fg
    dil = cv2.dilate(c_mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    other = (full_color != c) & is_fg
    color_boundary |= (dil & other)

# Full line set: all existing lines + outer silhouette outline + color boundaries
full_line = line | line_extra | outer_edge | color_boundary

# Outlines: pure black
out[full_line] = BLACK

# Alpha channel:
final_alpha = np.zeros((h, w), np.uint8)
foreground = is_fg
final_alpha[foreground] = 255

res = cv2.merge([out[:, :, 0], out[:, :, 1], out[:, :, 2], final_alpha])
cv2.imwrite('scripts/lb_painted.png', res)

# Verification against reference
pal = np.array([BLACK, GREEN, RED, YELLOW, BLUE])
fgpix = res[foreground][:, :3].astype(int)
ok = (np.abs(fgpix[:, None, :] - pal[None]).sum(axis=2) == 0).any(axis=1)
print('palette compliance: %.4f%%' % (100 * ok.mean()))
print('facets painted:', len(ids))
print('Total foreground pixels:', int(foreground.sum()))
print('Transparent pixels in facet 41:', int((lab == 41).sum()))
