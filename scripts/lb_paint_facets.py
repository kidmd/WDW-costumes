"""Generate clean, cartoony 5-color vector-style Lightning Bug graphic.

Style & Geometry Standards:
- Head & Body: Solid Yellow (#facc15 / [250, 204, 21])
- Neck Line: Bold, curved black line separating the spherical head/cheek from the body/torso
- Legs: Solid Green (#22c55e / [34, 197, 94])
- Wing: Solid Blue (#2563eb / [37, 99, 235])
- Hat, Tail Accordion Folds, Mouth: Solid Red (#e61919 / [230, 25, 25])
  * Tail folds: Exactly TWO red sections separated by a SINGLE, extra-bold black dividing line (4x standard thickness)
- Tail Tip Lantern Dome: Solid Yellow (#facc15 / [250, 204, 21]) with zero internal lines and a smooth, elegant cartoon curved boundary meeting the blue wing
- Antennae: Solid Yellow (#facc15 / [250, 204, 21])
- Eye Sclera: Smooth, rounded cartoon oval in Solid Yellow (#facc15 / [250, 204, 21])
- Eye Iris: Smooth, rounded cartoon oval in Solid Blue (#2563eb / [37, 99, 235])
- Outlines: Bold, consistent solid black lines (#141414 / [20, 20, 20])
  separating all color regions, anatomical features, and surrounding the whole character.
"""
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

REF = 'assets/lightningbug_dots_removed_backup.png'
img = cv2.imread(REF, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
bgr = img[:, :, :3].astype(int)
alpha = img[:, :, 3].copy()
lab = np.load('scripts/lb_labels_v3.npy').copy()

# Palette in BGR
BLACK = np.array([20, 20, 20, 255], dtype=np.uint8)
GREEN = np.array([94, 197, 34, 255], dtype=np.uint8)
BLUE = np.array([235, 99, 37, 255], dtype=np.uint8)
RED = np.array([25, 25, 230, 255], dtype=np.uint8)
YELLOW = np.array([21, 204, 250, 255], dtype=np.uint8)

# Semantic part map:
part_map = np.zeros((h, w), dtype=np.uint8)

# 1. Head (Yellow, Part ID 5)
head_facets = [12, 13, 14, 15, 16, 17, 19, 22, 25, 26]
part_map[np.isin(lab, head_facets)] = 5

# 2. Body / Torso (Yellow, Part ID 17)
# Distinct part ID from Head so the outline generator draws a curved dividing neck line
body_facets = [6, 7, 29, 30, 31, 33, 43]
part_map[np.isin(lab, body_facets)] = 17

# 3. Antennae (Yellow, Part ID 2)
part_map[np.isin(lab, [1, 9, 42])] = 2

# 4. Hat (Red): dome and visor
part_map[lab == 4] = 3              # Hat dome
part_map[np.isin(lab, [8, 11])] = 4 # Hat visor/band

# 5. Tail Tip Lantern Dome (Yellow, Part ID 10)
# Clean, unified yellow dome with zero internal dividing lines and zero red/white patches.
# Bounded by a smooth, monotonic cartoon curve along the blue wing edge.
ys_curve = np.arange(130, 185)
poly = [1.00611302e-03, -1.86267239e-01, 8.59393060e+01]
xs_curve = np.polyval(poly, ys_curve).round().astype(int)

tail_dome = np.isin(lab, [20, 21])
tail_dome |= ((lab == 10) & (np.arange(h)[:, None] >= 135))
tail_dome |= ((lab == 23) & (np.arange(h)[:, None] < 182) & (np.arange(w)[None, :] <= 95))
tail_dome |= ((lab == 0) & (np.arange(h)[:, None] >= 155) & (np.arange(h)[:, None] <= 185) & (np.arange(w)[None, :] >= 60) & (np.arange(w)[None, :] <= 95))

# Smooth curve boundary with wing:
for y, xc in zip(ys_curve, xs_curve):
    tail_dome[y, 50:xc] = True
    tail_dome[y, xc:95] = False

cnts_tip, _ = cv2.findContours(tail_dome.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
if cnts_tip:
    c_tip = max(cnts_tip, key=cv2.contourArea)
    filled_tip = np.zeros_like(tail_dome, dtype=np.uint8)
    cv2.drawContours(filled_tip, [c_tip], -1, 1, -1)
    tail_dome = filled_tip.astype(bool)
part_map[tail_dome] = 10

# 6. Wing (Blue, Part ID 9)
wing_mask = np.isin(lab, [2, 3, 5]) | ((lab == 10) & (np.arange(h)[:, None] < 135))
wing_mask &= (~tail_dome)
for y, xc in zip(ys_curve, xs_curve):
    wing_mask[y, xc:110] = True
wing_mask &= ~((lab == 23) & (np.arange(h)[:, None] >= 182))
part_map[wing_mask] = 9

# 7. Tail Accordion Folds (Red): ONLY TWO SECTIONS separated by a SINGLE black line!
# Upper Tail Fold: facet 23 starting at y >= 182 (below the lantern dome and wing)
part_map[(lab == 23) & (np.arange(h)[:, None] >= 182) & (~tail_dome) & (~wing_mask)] = 11
# Lower Tail Fold: facets 24 and 28 merged into a single section
lower_fold = np.isin(lab, [24, 28])
lower_fold &= ~((np.arange(h)[:, None] >= 200) & (np.arange(h)[:, None] < 228) & (np.arange(w)[None, :] > 75))
part_map[(lab == 23) & (np.arange(h)[:, None] >= 200) & (np.arange(h)[:, None] < 228) & (np.arange(w)[None, :] > 75)] = 11
part_map[lower_fold] = 12

# 8. Legs (Green)
part_map[np.isin(lab, [34, 39])] = 14       # back leg
part_map[np.isin(lab, [35, 36, 40])] = 15   # middle leg
part_map[np.isin(lab, [32, 37, 38])] = 16   # front leg

# 9. Eye Sclera (Yellow, Part ID 6) - Smooth, rounded cartoon oval
eye_raw = (lab == 18).astype(np.uint8)
cnts_eye, _ = cv2.findContours(eye_raw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c_eye = max(cnts_eye, key=cv2.contourArea)
ellipse_eye = cv2.fitEllipse(c_eye)
mask_eye_round = np.zeros_like(eye_raw)
cv2.ellipse(mask_eye_round, ellipse_eye, 1, -1)
part_map[mask_eye_round == 1] = 6

# 10. Eye Iris (Blue, Part ID 7) - Smooth, rounded cartoon oval
b_ch, g_ch, r_ch = bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2]
iris_raw = (eye_raw == 1) & (b_ch > r_ch + 15) & (b_ch > 90)
iris_raw = cv2.morphologyEx(iris_raw.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, l2, st, _ = cv2.connectedComponentsWithStats(iris_raw)
if n > 1:
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    iris_raw = (l2 == big).astype(np.uint8)
cnts_iris, _ = cv2.findContours(iris_raw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
if cnts_iris:
    c_iris = max(cnts_iris, key=cv2.contourArea)
    ellipse_iris = cv2.fitEllipse(c_iris)
    mask_iris_round = np.zeros_like(eye_raw)
    cv2.ellipse(mask_iris_round, ellipse_iris, 1, -1)
    mask_iris_round &= (mask_eye_round == 1)
    part_map[mask_iris_round == 1] = 7

# 11. Smiling Mouth (Red, Part ID 8)
part_map[lab == 27] = 8

# Foreground bounds:
is_fg = (lab != 0) & (lab != 41)
leg_spurs = (
    ((np.arange(h)[:, None] == 335) & (np.arange(w)[None, :] >= 392)) |
    ((np.arange(h)[:, None] == 336) & (np.arange(w)[None, :] >= 392)) |
    ((np.arange(h)[:, None] == 337) & (np.arange(w)[None, :] >= 391)) |
    ((np.arange(h)[:, None] == 338) & (np.arange(w)[None, :] >= 391)) |
    ((np.arange(h)[:, None] == 339) & (np.arange(w)[None, :] >= 390))
)
is_fg[leg_spurs] = False
is_fg |= (mask_eye_round == 1)
part_map[~is_fg] = 0

# Fill any small gaps inside foreground:
unl = is_fg & (part_map == 0)
if unl.any():
    _, (r_idx, c_idx) = distance_transform_edt(~(part_map > 0), return_indices=True)
    part_map[unl] = part_map[r_idx[unl], c_idx[unl]]

# Smooth parts for organic cartoon contours:
part_ids = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17]
smoothed_parts = {}
for pid in part_ids:
    mask = (part_map == pid).astype(np.uint8)
    if pid in [6, 7]:
        smoothed_parts[pid] = mask
    else:
        blur = cv2.GaussianBlur(mask.astype(float), (5, 5), 1.2)
        smoothed = (blur > 0.45).astype(np.uint8)
        smoothed_parts[pid] = smoothed

stack = np.zeros((h, w, max(part_ids) + 1), dtype=float)
for pid in part_ids:
    sm = smoothed_parts[pid]
    weight = 1.5 if pid in [6, 7] else 1.0
    dist = cv2.distanceTransform(sm, cv2.DIST_L2, 5) * weight
    stack[:, :, pid] = dist

clean_part_map = np.argmax(stack, axis=2).astype(np.uint8)

# Smooth outer foreground contour:
fg_blur = cv2.GaussianBlur(is_fg.astype(float), (5, 5), 1.0)
clean_fg = fg_blur > 0.45
clean_part_map[~clean_fg] = 0
bg = ~clean_fg

# Color mapping:
PART_COLOR = {
    2: YELLOW, 5: YELLOW, 6: YELLOW, 10: YELLOW, 17: YELLOW,
    14: GREEN, 15: GREEN, 16: GREEN,
    7: BLUE, 9: BLUE,
    3: RED, 4: RED, 8: RED, 11: RED, 12: RED
}

# Outlines:
# 1) Outer silhouette outline
outer_edge = cv2.dilate(bg.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))).astype(bool) & clean_fg

# 2) Standard part boundaries (2x thick)
part_boundary_1x = np.zeros((h, w), dtype=bool)
for pid in part_ids:
    p_mask = (clean_part_map == pid)
    dil = cv2.dilate(p_mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    other = (clean_part_map != pid) & clean_fg
    part_boundary_1x |= (dil & other)

part_boundary_2x = cv2.dilate(part_boundary_1x.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))).astype(bool) & clean_fg

# 3) Special 4x thicker divider line separating the two red tail sections (part 11 and part 12)
fold_boundary_1x = cv2.dilate((clean_part_map == 11).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (clean_part_map == 12)
fold_boundary_4x = cv2.dilate(fold_boundary_1x.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))).astype(bool) & clean_fg

all_lines = outer_edge | part_boundary_2x | fold_boundary_4x

# Paint final image:
out = np.zeros((h, w, 4), dtype=np.uint8)
for pid, col in PART_COLOR.items():
    out[clean_part_map == pid] = col

out[all_lines] = BLACK
out[bg] = [0, 0, 0, 0]

cv2.imwrite('scripts/lb_painted.png', out)

# Verification against reference palette:
pal = np.array([BLACK[:3], GREEN[:3], BLUE[:3], RED[:3], YELLOW[:3]])
fg_pixels = out[clean_fg][:, :3].astype(int)
ok = (np.abs(fg_pixels[:, None, :] - pal[None]).sum(axis=2) == 0).any(axis=1)
print('Palette compliance: %.4f%%' % (100 * ok.mean()))
print('Total foreground pixels:', int(clean_fg.sum()))
print('Total black line pixels:', int(all_lines.sum()))
