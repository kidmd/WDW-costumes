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

# 1. Antennae (Yellow, Part ID 2)
m4 = (lab == 4)
stalk = m4 & (np.arange(h)[:, None] < 65) & (np.arange(w)[None, :] > 310)
part_map[np.isin(lab, [1, 9, 42]) | stalk] = 2

# 2. Hat (Red): 3 symmetrical panels separated by black seam lines
part_map[m4 & (~stalk)] = 3
part_map[lab == 8] = 4
part_map[lab == 11] = 18

# 3. Head & Body base masks
head_facets = [12, 13, 14, 15, 16, 17, 19, 22, 25, 26]
body_facets = [6, 7, 29, 30, 31, 33, 43]
head_or_body = np.isin(lab, head_facets + body_facets + [18])  # include 18 so eye corners are absorbed into head

# Fix 0: Smooth curved neck boundary separating Head (5) and Body (17)
# Fit a smooth curve from y=215 to y=290
# Upper neck starts near (215, 158), passes through (245, 204), (265, 238), (275, 264), (284, 305)
ys_neck = np.array([215, 235, 255, 270, 280, 286])
xs_neck = np.array([158, 189, 220, 252, 280, 305])
p_neck = np.polyfit(ys_neck, xs_neck, 2)

for y in range(h):
    if y < 215:
        # Above neck junction
        mask_row = head_or_body[y]
        part_map[y, mask_row] = 5
    elif y <= 290:
        xc = int(np.round(np.polyval(p_neck, y)))
        cols_body = head_or_body[y] & (np.arange(w) < xc)
        cols_head = head_or_body[y] & (np.arange(w) >= xc)
        part_map[y, cols_body] = 17
        part_map[y, cols_head] = 5
    else:
        # Below y=290, remainder of body/belly is Body (17)
        mask_row = head_or_body[y]
        part_map[y, mask_row] = 17

# Fix 1: Wing (Blue, 9) and Tail Tip Dome (Yellow, 10)
# Tail is BEHIND the wing! The wing has a smooth, uninterrupted outer contour.
# Wing includes facets 2, 3, 5, and all of 10 for y < 140.
# Wing's left boundary is smooth from y=50 to y=215.
# At y=120..140, wing outer contour is at x ~ 61..65.
ys_wcurve = np.array([50, 75, 100, 120, 135, 155, 175, 195, 215])
xs_wcurve = np.array([81, 66, 61, 62, 65, 74, 84, 92, 97])
p_wcurve = np.polyfit(ys_wcurve, xs_wcurve, 3)

wing_mask = np.isin(lab, [2, 3, 5, 10]) & (np.arange(w)[None, :] < 170)
# Enforce smooth left boundary for wing:
for y in range(45, 225):
    xc = int(np.round(np.polyval(p_wcurve, y)))
    # To the left of xc is outside the wing
    wing_mask[y, :xc] = False
    # Inside the wing boundary (up to x=166 where it meets head/body) is wing
    if y <= 215:
        wing_mask[y, xc:min(168, np.max(np.where(np.isin(lab[y], [5, 10]))[0], initial=xc)+1)] = True

wing_mask &= ~((lab == 23) & (np.arange(h)[:, None] >= 182))  # red tail accordion fold below wing
part_map[wing_mask] = 9

# Tail Tip Dome (Yellow, 10): emerges from BEHIND the wing
# Spans y in [141..184], x in [15..95], strictly to the left of wing_mask!
tail_dome = np.isin(lab, [20, 21])
tail_dome |= ((lab == 10) & (np.arange(h)[:, None] >= 140))
tail_dome |= ((lab == 23) & (np.arange(h)[:, None] < 182) & (np.arange(w)[None, :] <= 95))
# Include former white gap/notch:
hole = (np.arange(h)[:, None] >= 165) & (np.arange(h)[:, None] <= 185) & (np.arange(w)[None, :] >= 65) & (np.arange(w)[None, :] <= 95)
tail_dome |= hole
tail_dome &= (~wing_mask)  # strictly behind the wing!

cnts_tip, _ = cv2.findContours(tail_dome.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
if cnts_tip:
    c_tip = max(cnts_tip, key=cv2.contourArea)
    filled_tip = np.zeros_like(tail_dome, dtype=np.uint8)
    cv2.drawContours(filled_tip, [c_tip], -1, 1, -1)
    tail_dome = filled_tip.astype(bool) & (~wing_mask)

part_map[tail_dome] = 10

# Tail Accordion Folds (Red): TWO sections separated by single divider
upper_fold = (lab == 23) & (np.arange(h)[:, None] >= 182) & (~tail_dome) & (~wing_mask)
lower_fold = np.isin(lab, [24, 28])
lower_fold &= ~((np.arange(h)[:, None] >= 200) & (np.arange(h)[:, None] < 228) & (np.arange(w)[None, :] > 75))
upper_fold |= ((lab == 23) & (np.arange(h)[:, None] >= 200) & (np.arange(h)[:, None] < 228) & (np.arange(w)[None, :] > 75))
part_map[upper_fold] = 11
part_map[lower_fold] = 12

# Fix 2: Legs (Green) with smooth outer contour on front leg/foot (Part 16)
part_map[np.isin(lab, [34, 39])] = 14       # back leg
part_map[np.isin(lab, [35, 36, 40])] = 15   # middle leg

front_leg = np.isin(lab, [32, 37, 38])
# Smooth the front leg's outer right contour to eliminate jagged facets and ankle spike
# Ankle spike occurred at y=361 where x jumped from 381 to 406
# Smooth outer boundary:
foot_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
front_leg_smooth = cv2.morphologyEx(front_leg.astype(np.uint8), cv2.MORPH_CLOSE, foot_kernel)
front_leg_smooth = cv2.GaussianBlur(front_leg_smooth.astype(float), (7, 7), 1.5) > 0.4
part_map[front_leg_smooth] = 16

# Fix 3: Eye Sclera (Yellow, 6) and Iris (Blue, 7)
# Old eye polygon corners in lab == 18 are already absorbed into Head (5)
eye_raw = (lab == 18).astype(np.uint8)
cnts_eye, _ = cv2.findContours(eye_raw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c_eye = max(cnts_eye, key=cv2.contourArea)
ellipse_eye = cv2.fitEllipse(c_eye)
mask_eye_round = np.zeros_like(eye_raw)
cv2.ellipse(mask_eye_round, ellipse_eye, 1, -1)
part_map[mask_eye_round == 1] = 6

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

# Fix 4: Smiling Mouth (Red, 8) with smooth upper crescent edge
mouth_raw = (lab == 27).copy()
# Smooth upper boundary of mouth
# Mouth spans x in [272..406]
pts_m = np.argwhere(mouth_raw)
xs_m = np.unique(pts_m[:, 1])
ymins_m = np.array([pts_m[pts_m[:, 1] == x, 0].min() for x in xs_m])
# Fit a smooth curve to upper mouth edge
p_mouth_top = np.polyfit(xs_m, ymins_m, 3)
smooth_mouth = np.zeros_like(mouth_raw)
for x in xs_m:
    y_top = int(np.round(np.polyval(p_mouth_top, x)))
    y_bot = pts_m[pts_m[:, 1] == x, 0].max()
    if y_bot >= y_top:
        smooth_mouth[y_top:y_bot+1, x] = True

# Dilate/close slightly to ensure full thickness
smooth_mouth = cv2.morphologyEx(smooth_mouth.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
part_map[smooth_mouth] = 8

# Foreground bounds & Fix 5: Smooth outer face/cheek silhouette
is_fg = (lab != 0) & (lab != 41)
is_fg |= (mask_eye_round == 1)
is_fg |= hole
is_fg |= front_leg_smooth
is_fg |= smooth_mouth
is_fg |= wing_mask
is_fg |= tail_dome

# Fix 5: Smooth face/cheek outer silhouette along y in [80..200]
# Currently x_max has steps and inward dents. Fit a smooth spherical arc.
ys_face = np.array([80, 95, 110, 130, 150, 170, 190, 205])
xs_face = np.array([359, 363, 378, 391, 400, 406, 407, 406])
p_face = np.polyfit(ys_face, xs_face, 2)
for y in range(80, 206):
    xf = int(np.round(np.polyval(p_face, y)))
    is_fg[y, 340:xf+1] = True
    is_fg[y, xf+1:] = False

part_map[~is_fg] = 0

# Fill any small gaps inside foreground:
unl = is_fg & (part_map == 0)
if unl.any():
    _, (r_idx, c_idx) = distance_transform_edt(~(part_map > 0), return_indices=True)
    part_map[unl] = part_map[r_idx[unl], c_idx[unl]]

# Smooth parts for organic cartoon contours:
part_ids = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18]
smoothed_parts = {}
for pid in part_ids:
    mask = (part_map == pid).astype(np.uint8)
    if pid in [6, 7, 8]:
        smoothed_parts[pid] = mask
    else:
        blur = cv2.GaussianBlur(mask.astype(float), (5, 5), 1.2)
        smoothed = (blur > 0.45).astype(np.uint8)
        smoothed_parts[pid] = smoothed

stack = np.zeros((h, w, max(part_ids) + 1), dtype=float)
for pid in part_ids:
    sm = smoothed_parts[pid]
    weight = 1.5 if pid in [6, 7, 8] else 1.0
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
    3: RED, 4: RED, 8: RED, 11: RED, 12: RED, 18: RED
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

cv2.imwrite('scripts/test_fixes_painted.png', out)

# Verification against reference palette:
pal = np.array([BLACK[:3], GREEN[:3], BLUE[:3], RED[:3], YELLOW[:3]])
fg_pixels = out[clean_fg][:, :3].astype(int)
ok = (np.abs(fg_pixels[:, None, :] - pal[None]).sum(axis=2) == 0).any(axis=1)
print('Palette compliance: %.4f%%' % (100 * ok.mean()))
print('Total foreground pixels:', int(clean_fg.sum()))
print('Total black line pixels:', int(all_lines.sum()))
