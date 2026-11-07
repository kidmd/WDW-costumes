import cv2
import numpy as np
from PIL import Image

# Canonical 5 Colors:
# Black:  #141414 -> [20, 20, 20]
# Green:  #22c55e -> [34, 197, 94]
# Red:    #e61919 -> [230, 25, 25]
# Yellow: #facc15 -> [250, 204, 21]
# Blue:   #2563eb -> [37, 99, 235]

C_BLACK  = (20, 20, 20)
C_GREEN  = (34, 197, 94)
C_RED    = (230, 25, 25)
C_YELLOW = (250, 204, 21)
C_BLUE   = (37, 99, 235)

# Load base transparent image
src = cv2.imread('assets/lightningbug_transparent.png', cv2.IMREAD_UNCHANGED)
h, w = src.shape[:2]

# Work in 4x supersampling (approx 1840 x 1744) for ultra-smooth curves
SCALE = 4
H4, W4 = h * SCALE, w * SCALE

src4 = cv2.resize(src, (W4, H4), interpolation=cv2.INTER_LANCZOS4)
fg_mask = src4[:, :, 3] > 100

# Helper to smooth a binary mask into organic cartoon curves
def get_smooth_mask(mask, k_blur=21, thresh=128):
    blurred = cv2.GaussianBlur(mask.astype(np.uint8) * 255, (k_blur, k_blur), 0)
    return (blurred >= thresh)

# Total silhouette smoothing (eliminates all staircasing and jagged steps):
total_fg = get_smooth_mask(fg_mask, k_blur=17, thresh=110)

canvas = np.zeros((H4, W4, 3), dtype=np.uint8)
alpha = np.zeros((H4, W4), dtype=np.uint8)
alpha[total_fg] = 255

# Fill default body with Green
canvas[total_fg] = C_GREEN

# -------------------------------------------------------------
# 1. RED TAIL
# -------------------------------------------------------------
# Tail region: x < 130*SCALE, y > 180*SCALE
tail_box = (np.arange(W4)[None, :] < int(130 * SCALE)) & (np.arange(H4)[:, None] > int(180 * SCALE))
tail_raw = total_fg & tail_box & (src4[:, :, 2] > 130) & (src4[:, :, 1] < 100)
k_tail = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
tail_closed = cv2.morphologyEx(tail_raw.astype(np.uint8), cv2.MORPH_CLOSE, k_tail).astype(bool)
tail_smooth = get_smooth_mask(tail_closed, k_blur=25, thresh=120) & total_fg
canvas[tail_smooth] = C_RED

# -------------------------------------------------------------
# 2. YELLOW TAIL TIP (Lantern Dome)
# -------------------------------------------------------------
# Sits atop tail crest: x in [50..112]*SCALE, y in [135..185]*SCALE
tip_box = (np.arange(W4)[None, :] >= int(50 * SCALE)) & (np.arange(W4)[None, :] <= int(112 * SCALE)) & \
          (np.arange(H4)[:, None] >= int(135 * SCALE)) & (np.arange(H4)[:, None] <= int(185 * SCALE))
tip_raw = total_fg & tip_box & ~tail_smooth
tip_closed = cv2.morphologyEx(tip_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)).astype(bool)
tip_smooth = get_smooth_mask(tip_closed, k_blur=19, thresh=120) & total_fg
canvas[tip_smooth] = C_YELLOW

# -------------------------------------------------------------
# 3. RED CROWN CAP
# -------------------------------------------------------------
# Sits on top of head: x in [165..250]*SCALE, y in [35..110]*SCALE
crown_box = (np.arange(W4)[None, :] >= int(165 * SCALE)) & (np.arange(W4)[None, :] <= int(250 * SCALE)) & \
            (np.arange(H4)[:, None] >= int(35 * SCALE)) & (np.arange(H4)[:, None] <= int(110 * SCALE))
crown_raw = total_fg & crown_box
crown_closed = cv2.morphologyEx(crown_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)).astype(bool)
crown_smooth = get_smooth_mask(crown_closed, k_blur=19, thresh=120) & total_fg
canvas[crown_smooth] = C_RED

# -------------------------------------------------------------
# 4. YELLOW ANTENNAE
# -------------------------------------------------------------
# Radiating rays: x >= 235*SCALE, y <= 95*SCALE
ant_box = (np.arange(W4)[None, :] >= int(235 * SCALE)) & (np.arange(H4)[:, None] <= int(95 * SCALE))
ant_raw = total_fg & ant_box
ant_closed = cv2.morphologyEx(ant_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)).astype(bool)
ant_smooth = get_smooth_mask(ant_closed, k_blur=13, thresh=95) & total_fg
canvas[ant_smooth] = C_YELLOW

# -------------------------------------------------------------
# 5. WING (Blue Interior & Yellow Outer Rim)
# -------------------------------------------------------------
# Wing region: x in [70..175]*SCALE, y in [25..220]*SCALE
wing_box = (np.arange(W4)[None, :] >= int(70 * SCALE)) & (np.arange(W4)[None, :] <= int(175 * SCALE)) & \
           (np.arange(H4)[:, None] >= int(25 * SCALE)) & (np.arange(H4)[:, None] <= int(220 * SCALE)) & \
           ~tail_smooth & ~tip_smooth & ~crown_smooth

wing_full = cv2.morphologyEx(wing_box.astype(np.uint8) & total_fg.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8)).astype(bool)
wing_full_smooth = get_smooth_mask(wing_full, k_blur=21, thresh=120) & total_fg & ~tail_smooth & ~tip_smooth

# Solid Blue interior:
k_rim = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
wing_blue_smooth = cv2.erode(wing_full_smooth.astype(np.uint8), k_rim).astype(bool)
wing_yellow_rim = wing_full_smooth & ~wing_blue_smooth

canvas[wing_yellow_rim] = C_YELLOW
canvas[wing_blue_smooth] = C_BLUE

# -------------------------------------------------------------
# 6. RED OPEN SMILE
# -------------------------------------------------------------
# Mouth region: x in [250..405]*SCALE, y in [180..270]*SCALE
mouth_box = (np.arange(W4)[None, :] >= int(250 * SCALE)) & (np.arange(W4)[None, :] <= int(410 * SCALE)) & \
            (np.arange(H4)[:, None] >= int(180 * SCALE)) & (np.arange(H4)[:, None] <= int(270 * SCALE))
mouth_raw = total_fg & mouth_box & (src4[:, :, 2] > 160) & (src4[:, :, 1] < 100)
mouth_closed = cv2.morphologyEx(mouth_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)).astype(bool)
mouth_smooth = get_smooth_mask(mouth_closed, k_blur=19, thresh=120) & total_fg
canvas[mouth_smooth] = C_RED

# -------------------------------------------------------------
# 7. YELLOW MUZZLE / SNOUT FACET
# -------------------------------------------------------------
# Front snout: x in [355..405]*SCALE, y in [85..215]*SCALE
snout_box = (np.arange(W4)[None, :] >= int(355 * SCALE)) & (np.arange(W4)[None, :] <= int(405 * SCALE)) & \
            (np.arange(H4)[:, None] >= int(85 * SCALE)) & (np.arange(H4)[:, None] <= int(215 * SCALE))
snout_raw = total_fg & snout_box & ~mouth_smooth
snout_closed = cv2.morphologyEx(snout_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8)).astype(bool)
snout_smooth = get_smooth_mask(snout_closed, k_blur=17, thresh=120) & total_fg & ~mouth_smooth
canvas[snout_smooth] = C_YELLOW

# -------------------------------------------------------------
# 8. ALTERNATING YELLOW BELLY BANDS
# -------------------------------------------------------------
# Belly area: x in [120..300]*SCALE, y in [180..375]*SCALE
belly_box = (np.arange(W4)[None, :] >= int(120 * SCALE)) & (np.arange(W4)[None, :] <= int(300 * SCALE)) & \
            (np.arange(H4)[:, None] >= int(180 * SCALE)) & (np.arange(H4)[:, None] <= int(375 * SCALE)) & \
            ~wing_full_smooth & ~tail_smooth & ~mouth_smooth

# Upper Yellow Band (Tier 2):
y_b2 = (np.arange(H4)[:, None] >= int(215 * SCALE)) & (np.arange(H4)[:, None] <= int(260 * SCALE))
b2_mask = total_fg & belly_box & y_b2
b2_smooth = get_smooth_mask(b2_mask, k_blur=25, thresh=120) & total_fg & ~wing_full_smooth & ~tail_smooth & ~mouth_smooth
canvas[b2_smooth] = C_YELLOW

# Lower Yellow Band (Tier 4):
y_b4 = (np.arange(H4)[:, None] >= int(295 * SCALE)) & (np.arange(H4)[:, None] <= int(360 * SCALE)) & (np.arange(W4)[None, :] <= int(280 * SCALE))
b4_mask = total_fg & belly_box & y_b4
b4_smooth = get_smooth_mask(b4_mask, k_blur=25, thresh=120) & total_fg & ~wing_full_smooth & ~tail_smooth & ~mouth_smooth
canvas[b4_smooth] = C_YELLOW

# -------------------------------------------------------------
# 9. BOLD BLACK CARTOON OUTLINES & DETAILS
# -------------------------------------------------------------
def stroke_mask(img, mask, thickness=9, color=C_BLACK):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
    dilated = cv2.dilate(mask.astype(np.uint8), k).astype(bool)
    eroded = cv2.erode(mask.astype(np.uint8), k).astype(bool)
    boundary = dilated & ~eroded & total_fg
    img[boundary] = color

# Outer silhouette contour (bold 11px)
k_outer = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
outer_rim = total_fg & ~cv2.erode(total_fg.astype(np.uint8), k_outer).astype(bool)
canvas[outer_rim] = C_BLACK

# Feature boundaries
stroke_mask(canvas, tail_smooth, thickness=9)
stroke_mask(canvas, tip_smooth, thickness=7)
stroke_mask(canvas, wing_full_smooth, thickness=9)
stroke_mask(canvas, wing_blue_smooth, thickness=7)
stroke_mask(canvas, crown_smooth, thickness=7)
stroke_mask(canvas, ant_smooth, thickness=7)
stroke_mask(canvas, mouth_smooth, thickness=9)
stroke_mask(canvas, snout_smooth, thickness=7)
stroke_mask(canvas, b2_smooth, thickness=7)
stroke_mask(canvas, b4_smooth, thickness=7)

# Accordion stripes on Red Tail (smooth curved rings):
tail_stripes = [
    np.array([(45*SCALE, 210*SCALE), (75*SCALE, 203*SCALE), (105*SCALE, 206*SCALE)], dtype=np.int32),
    np.array([(48*SCALE, 250*SCALE), (80*SCALE, 240*SCALE), (115*SCALE, 245*SCALE)], dtype=np.int32),
    np.array([(55*SCALE, 295*SCALE), (90*SCALE, 285*SCALE), (125*SCALE, 290*SCALE)], dtype=np.int32)
]
for st in tail_stripes:
    cv2.polylines(canvas, [st], isClosed=False, color=C_BLACK, thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)

# Tail tip dome facet lines:
tip_f1 = np.array([(58*SCALE, 160*SCALE), (85*SCALE, 155*SCALE), (108*SCALE, 158*SCALE)], dtype=np.int32)
tip_f2 = np.array([(85*SCALE, 138*SCALE), (85*SCALE, 175*SCALE)], dtype=np.int32)
cv2.polylines(canvas, [tip_f1], isClosed=False, color=C_BLACK, thickness=int(2.0 * SCALE), lineType=cv2.LINE_AA)
cv2.polylines(canvas, [tip_f2], isClosed=False, color=C_BLACK, thickness=int(2.0 * SCALE), lineType=cv2.LINE_AA)

# Crown cap facet lines:
c_line1 = np.array([(185*SCALE, 55*SCALE), (200*SCALE, 105*SCALE)], dtype=np.int32)
c_line2 = np.array([(215*SCALE, 45*SCALE), (225*SCALE, 105*SCALE)], dtype=np.int32)
c_line3 = np.array([(240*SCALE, 60*SCALE), (245*SCALE, 105*SCALE)], dtype=np.int32)
for cl in [c_line1, c_line2, c_line3]:
    cv2.polylines(canvas, [cl], isClosed=False, color=C_BLACK, thickness=int(2.0 * SCALE), lineType=cv2.LINE_AA)

# Wing cartoon swirl loop inside blue wing:
swirl_pts = np.array([
    (100*SCALE, 80*SCALE), (115*SCALE, 65*SCALE), (130*SCALE, 80*SCALE), (135*SCALE, 115*SCALE),
    (125*SCALE, 150*SCALE), (108*SCALE, 165*SCALE), (95*SCALE, 145*SCALE), (105*SCALE, 105*SCALE), (120*SCALE, 100*SCALE)
], dtype=np.int32)
cv2.polylines(canvas, [swirl_pts], isClosed=False, color=C_BLACK, thickness=int(2.5 * SCALE), lineType=cv2.LINE_AA)

# Smile corner dimple:
dimple = np.array([(255*SCALE, 205*SCALE), (262*SCALE, 218*SCALE), (258*SCALE, 230*SCALE)], dtype=np.int32)
cv2.polylines(canvas, [dimple], isClosed=False, color=C_BLACK, thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)

# Cheek contour curve separating green cheek from face:
cheek_curve = np.array([
    (270*SCALE, 175*SCALE), (285*SCALE, 195*SCALE), (300*SCALE, 220*SCALE), (290*SCALE, 260*SCALE)
], dtype=np.int32)
cv2.polylines(canvas, [cheek_curve], isClosed=False, color=C_BLACK, thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)

# Leg separation lines along bottom skirt:
leg_line1 = np.array([(165*SCALE, 335*SCALE), (180*SCALE, 375*SCALE)], dtype=np.int32)
leg_line2 = np.array([(270*SCALE, 335*SCALE), (285*SCALE, 375*SCALE)], dtype=np.int32)
cv2.polylines(canvas, [leg_line1], isClosed=False, color=C_BLACK, thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)
cv2.polylines(canvas, [leg_line2], isClosed=False, color=C_BLACK, thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)

# -------------------------------------------------------------
# 10. CARTOON EYE (Sclera Yellow, Iris Blue, Pupil Black)
# -------------------------------------------------------------
eye_cx = int(312 * SCALE)
eye_cy = int(131 * SCALE)
sclera_rx = int(18 * SCALE)
sclera_ry = int(25 * SCALE)

# Yellow Sclera
cv2.ellipse(canvas, (eye_cx, eye_cy), (sclera_rx, sclera_ry), -15, 0, 360, C_YELLOW, -1, cv2.LINE_AA)
cv2.ellipse(canvas, (eye_cx, eye_cy), (sclera_rx, sclera_ry), -15, 0, 360, C_BLACK, int(2.5 * SCALE), cv2.LINE_AA)

# Blue Iris
iris_r = int(11 * SCALE)
cv2.circle(canvas, (eye_cx + int(2 * SCALE), eye_cy + int(2 * SCALE)), iris_r, C_BLUE, -1, cv2.LINE_AA)
cv2.circle(canvas, (eye_cx + int(2 * SCALE), eye_cy + int(2 * SCALE)), iris_r, C_BLACK, int(1.8 * SCALE), cv2.LINE_AA)

# Black Pupil
pupil_r = int(6.5 * SCALE)
cv2.circle(canvas, (eye_cx + int(3 * SCALE), eye_cy + int(2 * SCALE)), pupil_r, C_BLACK, -1, cv2.LINE_AA)

# Yellow Specular Catchlight
catch_r = int(2.5 * SCALE)
cv2.circle(canvas, (eye_cx + int(1 * SCALE), eye_cy - int(1 * SCALE)), catch_r, C_YELLOW, -1, cv2.LINE_AA)

# Eyelid arch
cv2.ellipse(canvas, (eye_cx, eye_cy - int(4 * SCALE)), (sclera_rx + int(2 * SCALE), sclera_ry), -15, 200, 340, C_BLACK, int(3.0 * SCALE), cv2.LINE_AA)

# -------------------------------------------------------------
# 11. STRICT 5-COLOR ENFORCEMENT & TIGHT CROP
# -------------------------------------------------------------
palette = np.array([C_BLACK, C_GREEN, C_RED, C_YELLOW, C_BLUE], dtype=float)
fg_pixels = canvas[total_fg].astype(float)
dists = np.sum((fg_pixels[:, None, :] - palette[None, :, :]) ** 2, axis=2)
canvas[total_fg] = palette[np.argmin(dists, axis=1)].astype(np.uint8)

# Crop with 40px padding
y_indices, x_indices = np.where(total_fg)
pad = 40
x1 = max(0, x_indices.min() - pad)
y1 = max(0, y_indices.min() - pad)
x2 = min(W4, x_indices.max() + pad + 1)
y2 = min(H4, y_indices.max() + pad + 1)

cropped_rgb = canvas[y1:y2, x1:x2]
cropped_alpha = alpha[y1:y2, x1:x2]

out_bgra = cv2.merge([
    cropped_rgb[:, :, 2],
    cropped_rgb[:, :, 1],
    cropped_rgb[:, :, 0],
    cropped_alpha
])

cv2.imwrite('assets/lightningbug_5color_perfect.png', out_bgra)
print('Successfully generated lightningbug_5color_perfect.png, size:', cropped_rgb.shape)
