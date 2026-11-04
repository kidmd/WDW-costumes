"""Generate clean, cartoony 5-color vector-style Lightning Bug graphic.

Style & Geometry Standards:
- Head & Body: Solid Yellow (#facc15 / [250, 204, 21])
- Legs: Solid Green (#22c55e / [34, 197, 94])
- Wing: Solid Blue (#2563eb / [37, 99, 235])
- Hat, Tail Accordion Folds, Mouth: Solid Red (#e61919 / [230, 25, 25])
- Tail Tip Lantern Dome, Antennae, Eye Sclera: Solid Yellow (#facc15 / [250, 204, 21])
- Eye Iris: Solid Blue (#2563eb / [37, 99, 235])
- Outlines: Bold, consistent solid black lines (#141414 / [20, 20, 20])
  separating all color regions, anatomical features, and surrounding the whole character.
- Gentle edge rounding eliminating jagged pixel staircases while preserving character anatomy.
"""
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

REF = 'assets/lightningbug_dots_removed_backup.png'
img = cv2.imread(REF, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
bgr = img[:, :, :3].astype(int)
alpha = img[:, :, 3].copy()
fg = alpha > 100
line = fg & (bgr.max(axis=2) < 80)
lab = np.load('scripts/lb_labels_v3.npy').copy()

# Palette in BGR
BLACK = np.array([20, 20, 20, 255], dtype=np.uint8)
GREEN = np.array([94, 197, 34, 255], dtype=np.uint8)
BLUE = np.array([235, 99, 37, 255], dtype=np.uint8)
RED = np.array([25, 25, 230, 255], dtype=np.uint8)
YELLOW = np.array([21, 204, 250, 255], dtype=np.uint8)

# Semantic part map:
part_map = np.zeros((h, w), dtype=np.uint8)

# Head & Body (Yellow)
head_body_facets = [12, 13, 14, 15, 16, 17, 19, 22, 25, 26, 6, 7, 29, 30, 31, 33, 43]
part_map[np.isin(lab, head_body_facets)] = 5

# Antennae (Yellow)
part_map[np.isin(lab, [1, 9, 42])] = 2

# Hat (Red): dome and visor
part_map[lab == 4] = 3   # Hat dome
part_map[np.isin(lab, [8, 11])] = 4 # Hat visor/band

# Tail folds (Red)
part_map[lab == 28] = 11 # Fold 1
part_map[lab == 24] = 12 # Fold 2
part_map[lab == 23] = 13 # Fold 3

# Tail tip lantern dome (Yellow)
att1_prev = cv2.imread(r'C:\Users\Kiddi\.gemini\antigravity\brain\73963054-0e68-43d0-9a1f-4e7be7ecffb2\.system_generated\logs\media\step_984_media_1.png', cv2.IMREAD_UNCHANGED)
if att1_prev is not None:
    tri_in_att1 = ((att1_prev[:, :, 3] == 0) | ((att1_prev[:, :, 2] > 180) & (att1_prev[:, :, 0] < 50))) & (att1_prev[:, :, 1] < 100)
    part_map[161:184, 61:96][tri_in_att1] = 10
part_map[np.isin(lab, [20, 21])] = 10
part_map[130:152, 45:65][(lab[130:152, 45:65] == 10) | (lab[130:152, 45:65] == 0)] = 10

# Wing (Blue)
part_map[np.isin(lab, [2, 3, 5, 10])] = 9

# Legs (Green)
part_map[np.isin(lab, [34, 39])] = 14       # back leg
part_map[np.isin(lab, [35, 36, 40])] = 15   # middle leg
part_map[np.isin(lab, [32, 37, 38])] = 16   # front leg

# Eye sclera (Yellow)
part_map[lab == 18] = 6

# Eye iris (Blue)
eye = lab == 18
b_ch, g_ch, r_ch = bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2]
iris = eye & (b_ch > r_ch + 15) & (b_ch > 90)
iris = cv2.morphologyEx(iris.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, l2, st, _ = cv2.connectedComponentsWithStats(iris)
if n > 1:
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    iris = (l2 == big).astype(np.uint8)
    cnts, _ = cv2.findContours(iris, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(iris)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    iris = filled.astype(bool) & eye
part_map[iris] = 7

# Smiling Mouth (Red)
part_map[lab == 27] = 8

# Foreground bounds:
is_fg = (lab != 0) & (lab != 41)
# Clean leg spur:
leg_spurs = (
    ((np.arange(h)[:, None] == 335) & (np.arange(w)[None, :] >= 392)) |
    ((np.arange(h)[:, None] == 336) & (np.arange(w)[None, :] >= 392)) |
    ((np.arange(h)[:, None] == 337) & (np.arange(w)[None, :] >= 391)) |
    ((np.arange(h)[:, None] == 338) & (np.arange(w)[None, :] >= 391)) |
    ((np.arange(h)[:, None] == 339) & (np.arange(w)[None, :] >= 390))
)
is_fg[leg_spurs] = False
part_map[~is_fg] = 0

# Fill any small gaps inside foreground:
unl = is_fg & (part_map == 0)
if unl.any():
    _, (r_idx, c_idx) = distance_transform_edt(~(part_map > 0), return_indices=True)
    part_map[unl] = part_map[r_idx[unl], c_idx[unl]]

# Smooth each part mask slightly to round sharp edges and remove jagged staircases:
smoothed_parts = {}
for pid in range(2, 17):
    mask = (part_map == pid).astype(np.uint8)
    blur = cv2.GaussianBlur(mask.astype(float), (5, 5), 1.2)
    smoothed = (blur > 0.45).astype(np.uint8)
    smoothed_parts[pid] = smoothed

stack = np.zeros((h, w, 17), dtype=float)
for pid, sm in smoothed_parts.items():
    dist = cv2.distanceTransform(sm, cv2.DIST_L2, 5)
    stack[:, :, pid] = dist

clean_part_map = np.argmax(stack, axis=2).astype(np.uint8)

# Smooth outer foreground contour slightly:
fg_blur = cv2.GaussianBlur(is_fg.astype(float), (5, 5), 1.0)
clean_fg = fg_blur > 0.45
clean_part_map[~clean_fg] = 0

bg = ~clean_fg

# Color mapping:
PART_COLOR = {
    2: YELLOW, 5: YELLOW, 6: YELLOW, 10: YELLOW,
    14: GREEN, 15: GREEN, 16: GREEN,
    7: BLUE, 9: BLUE,
    3: RED, 4: RED, 8: RED, 11: RED, 12: RED, 13: RED
}

# Outlines: consistent 2x thick black lines
# 1) Outer silhouette outline
outer_edge = cv2.dilate(bg.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))).astype(bool) & clean_fg

# 2) Part boundaries
part_boundary_1x = np.zeros((h, w), dtype=bool)
for pid in range(2, 17):
    p_mask = (clean_part_map == pid)
    dil = cv2.dilate(p_mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    other = (clean_part_map != pid) & clean_fg
    part_boundary_1x |= (dil & other)

part_boundary_2x = cv2.dilate(part_boundary_1x.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))).astype(bool) & clean_fg

all_lines = outer_edge | part_boundary_2x

# Paint image:
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
