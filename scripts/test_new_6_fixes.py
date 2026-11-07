import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter1d

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
m4 = (lab == 4).copy()
stalk = m4 & (np.arange(h)[:, None] < 65) & (np.arange(w)[None, :] > 310)
part_map[np.isin(lab, [1, 9, 42]) | stalk] = 2

# 2. Fix 5: Bottom Contour of Red Cap (Red: 3, 4, 18)
# Fit smooth curve to bottom of cap from x=166 (y=119) up to x=235 (y=85)
xs_cap_fit = np.array([166, 185, 205, 225, 235])
ys_cap_fit = np.array([119, 108, 97, 88, 85])
p_cap_bot = np.polyfit(xs_cap_fit, ys_cap_fit, 2)

cap_mask = np.isin(lab, [4, 8, 11]) & (~stalk)
# Enforce smooth bottom edge on cap:
for x in range(160, 240):
    y_bot = int(np.round(np.polyval(p_cap_bot, x)))
    cap_mask[y_bot+1:, x] = False

# Reassign 3 panels:
part_map[cap_mask & (lab == 4)] = 3
part_map[cap_mask & (lab == 8)] = 4
part_map[cap_mask & (lab == 11)] = 18

# 3. Smiling Mouth (Red, 8) with smooth upper crescent edge
pts_m = np.argwhere(lab == 27)
xs_m = np.arange(272, 407)
xs_fit = np.array([272, 290, 315, 340, 360, 385, 406])
ys_fit = np.array([185, 198, 218, 232, 238, 234, 222])
p_mouth_top = np.polyfit(xs_fit, ys_fit, 3)

ymax_dict = {x: pts_m[pts_m[:, 1] == x, 0].max() for x in np.unique(pts_m[:, 1])}
mouth_mask = np.zeros((h, w), dtype=bool)
for x in xs_m:
    yt = int(np.round(np.polyval(p_mouth_top, x)))
    yb = ymax_dict.get(x, yt + 20)
    mouth_mask[yt:yb+1, x] = True
part_map[mouth_mask] = 8

# 4. Legs (Green) with rounded tops and Fix 2 (back foot bottom smoothing):
m34 = (lab == 34).copy()
m39 = (lab == 39).copy()
m35 = (lab == 35).copy()
m36 = (lab == 36).copy()
m40 = (lab == 40).copy()
front_leg = np.isin(lab, [32, 37, 38]).copy()

# Leg 34 top-right shoulder rounding:
xs_34 = np.arange(80, 110)
p_34 = np.polyfit([80, 95, 108], [292, 293, 308], 2)
for x in xs_34:
    yt = int(np.round(np.polyval(p_34, x)))
    m34[:yt, x] = False

# Fix 2: Back foot bottom smoothing across x in [65..110]:
# Smooth bottom sole of back foot:
pts_34 = np.argwhere(m34 | m39)
xs_sole = np.unique(pts_34[:, 1])
y_soles = np.array([pts_34[pts_34[:, 1] == x, 0].max() for x in xs_sole], dtype=float)
y_soles_smooth = gaussian_filter1d(y_soles, sigma=2.5)
back_foot = m34 | m39
for x, y_s in zip(xs_sole, y_soles_smooth):
    back_foot[int(np.round(y_s))+1:, x] = False

# Leg 35 top dome rounding:
xs_35 = np.arange(138, 187)
for x in xs_35:
    yt = int(np.round(302 + 0.038 * (x - 162.0)**2))
    m35[:yt, x] = False

# Leg 36 top apex rounding:
xs_36 = np.arange(275, 306)
p_36 = np.polyfit([275, 290, 305], [311, 303, 328], 2)
for x in xs_36:
    yt = int(np.round(np.polyval(p_36, x)))
    m36[:yt, x] = False

# Front leg outer silhouette smoothing:
ys_leg = np.arange(280, 385)
xs_outer = []
for y in ys_leg:
    row_pts = np.where(front_leg[y])[0]
    xs_outer.append(row_pts.max() if len(row_pts) > 0 else 380)
xs_outer = np.array(xs_outer, dtype=float)
xs_leg_smooth = gaussian_filter1d(xs_outer, sigma=3.5)

front_leg_smooth = front_leg.copy()
for y, xs in zip(ys_leg, xs_leg_smooth):
    xs_int = int(np.round(xs))
    front_leg_smooth[y, xs_int+1:] = False

all_legs = back_foot | m35 | m36 | m40 | front_leg_smooth

part_map[back_foot] = 14
part_map[m35 | m36 | m40] = 15
part_map[front_leg_smooth] = 16

# 5. Head & Body base masks (strictly excludes mouth, cap, and legs)
head_facets = [12, 13, 14, 15, 16, 17, 19, 22, 25, 26]
body_facets = [6, 7, 29, 30, 31, 33, 43]
head_or_body = np.isin(lab, head_facets + body_facets + [18]) & (~mouth_mask) & (~all_legs) & (~cap_mask)

# Add any pixels below smoothed cap to head:
for x in range(160, 240):
    y_bot = int(np.round(np.polyval(p_cap_bot, x)))
    head_or_body[y_bot+1:y_bot+10, x] = True

# Smooth curved neck boundary separating Head (5) and Body (17)
ys_neck = np.array([215, 235, 255, 270, 280, 286])
xs_neck = np.array([158, 189, 220, 252, 280, 305])
p_neck = np.polyfit(ys_neck, xs_neck, 2)

for y in range(h):
    if y < 215:
        part_map[y, head_or_body[y]] = 5
    elif y <= 290:
        xc = int(np.round(np.polyval(p_neck, y)))
        cols_body = head_or_body[y] & (np.arange(w) < xc)
        cols_head = head_or_body[y] & (np.arange(w) >= xc)
        part_map[y, cols_body] = 17
        part_map[y, cols_head] = 5
    else:
        part_map[y, head_or_body[y]] = 17

# 6. Fix 4: Wing (Blue, 9) with smooth left AND smooth right boundary (x=166 straight vertical seam)
ys_wcurve = np.array([50, 75, 100, 120, 135, 155, 175, 195, 215])
xs_wcurve = np.array([81, 66, 61, 62, 65, 74, 84, 92, 97])
p_wcurve = np.polyfit(ys_wcurve, xs_wcurve, 3)

wing_mask = np.isin(lab, [2, 3, 5, 10]) & (np.arange(w)[None, :] < 170)
for y in range(45, 225):
    xc = int(np.round(np.polyval(p_wcurve, y)))
    wing_mask[y, :xc] = False
    if y <= 215:
        # Fix 4: Perfectly smooth vertical right seam at x=166 from y=135 to 215!
        max_x = 166 if y >= 135 else min(168, np.max(np.where(np.isin(lab[y], [5, 10]))[0], initial=xc)+1)
        wing_mask[y, xc:max_x] = True
        wing_mask[y, max_x:] = False

wing_mask &= ~((lab == 23) & (np.arange(h)[:, None] >= 182))
part_map[wing_mask] = 9

# Tail Tip Dome (Yellow, 10): emerges strictly BEHIND the wing
tail_dome = np.isin(lab, [20, 21])
tail_dome |= ((lab == 10) & (np.arange(h)[:, None] >= 140))
tail_dome |= ((lab == 23) & (np.arange(h)[:, None] < 182) & (np.arange(w)[None, :] <= 95))
hole = (np.arange(h)[:, None] >= 165) & (np.arange(h)[:, None] <= 185) & (np.arange(w)[None, :] >= 65) & (np.arange(w)[None, :] <= 95)
tail_dome |= hole
tail_dome &= (~wing_mask)

cnts_tip, _ = cv2.findContours(tail_dome.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
if cnts_tip:
    c_tip = max(cnts_tip, key=cv2.contourArea)
    filled_tip = np.zeros_like(tail_dome, dtype=np.uint8)
    cv2.drawContours(filled_tip, [c_tip], -1, 1, -1)
    tail_dome = filled_tip.astype(bool) & (~wing_mask)
part_map[tail_dome] = 10

# 7. Tail Accordion Folds (Red): TWO sections separated by single divider
upper_fold = (lab == 23) & (np.arange(h)[:, None] >= 182) & (~tail_dome) & (~wing_mask)
lower_fold = np.isin(lab, [24, 28])
lower_fold &= ~((np.arange(h)[:, None] >= 200) & (np.arange(h)[:, None] < 228) & (np.arange(w)[None, :] > 75))
upper_fold |= ((lab == 23) & (np.arange(h)[:, None] >= 200) & (np.arange(h)[:, None] < 228) & (np.arange(w)[None, :] > 75))

# Fix 0 & 1: Smooth the outer left and bottom-left silhouette of the tail:
# Extract tail left boundary from y=190 to y=355:
tail_all = upper_fold | lower_fold
ys_tail = np.arange(190, 356)
xs_tail_min = []
for y in ys_tail:
    pts_row = np.where(tail_all[y])[0]
    xs_tail_min.append(pts_row.min() if len(pts_row) > 0 else 50)
xs_tail_min = np.array(xs_tail_min, dtype=float)
# Smooth with Gaussian filter:
xs_tail_smooth = gaussian_filter1d(xs_tail_min, sigma=3.0)

for y, xs in zip(ys_tail, xs_tail_smooth):
    xs_int = int(np.round(xs))
    upper_fold[y, :xs_int] = False
    lower_fold[y, :xs_int] = False

part_map[upper_fold] = 11
part_map[lower_fold] = 12

# 8. Eye Sclera (Yellow, 6) & Eye Iris (Blue, 7)
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

# Foreground bounds & Silhouette smoothing
is_fg = (lab != 0) & (lab != 41)
is_fg |= (mask_eye_round == 1)
is_fg |= hole
is_fg |= all_legs
is_fg |= mouth_mask
is_fg |= wing_mask
is_fg |= tail_dome
is_fg |= upper_fold
is_fg |= lower_fold
is_fg |= cap_mask

# Tail left bound (Fix 0 & 1):
for y, xs in zip(ys_tail, xs_tail_smooth):
    xs_int = int(np.round(xs))
    is_fg[y, :xs_int] = False

# Leg outer bound:
for y, xs in zip(ys_leg, xs_leg_smooth):
    xs_int = int(np.round(xs))
    is_fg[y, xs_int+1:] = False

# Fix 3: Smooth the entire bottom baseline across x in [95..385]
xs_base = np.arange(95, 385)
ys_bot = []
for x in xs_base:
    pts_col = np.where(is_fg[:, x])[0]
    ys_bot.append(pts_col.max() if len(pts_col) > 0 else 380)
ys_bot = np.array(ys_bot, dtype=float)
ys_bot_smooth = gaussian_filter1d(ys_bot, sigma=4.5)
for x, yb in zip(xs_base, ys_bot_smooth):
    yb_int = int(np.round(yb))
    is_fg[yb_int+1:, x] = False

# Face/cheek outer silhouette along y in [80..205]
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

cv2.imwrite('scripts/test_new_6_painted.png', out)

# Verification against reference palette:
pal = np.array([BLACK[:3], GREEN[:3], BLUE[:3], RED[:3], YELLOW[:3]])
fg_pixels = out[clean_fg][:, :3].astype(int)
ok = (np.abs(fg_pixels[:, None, :] - pal[None]).sum(axis=2) == 0).any(axis=1)
print('Palette compliance: %.4f%%' % (100 * ok.mean()))
print('Total foreground pixels:', int(clean_fg.sum()))
print('Total black line pixels:', int(all_lines.sum()))
