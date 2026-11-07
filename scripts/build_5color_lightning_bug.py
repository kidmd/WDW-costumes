import cv2
import numpy as np
from PIL import Image

# Load current transparent image
src = cv2.imread('assets/lightningbug_transparent.png', cv2.IMREAD_UNCHANGED)
h, w = src.shape[:2]

# Canonical 5 Colors (RGB):
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

# 1. Upscale by 4x for high-precision vector smoothing and clean rendering
SCALE = 4
H4, W4 = h * SCALE, w * SCALE
src4 = cv2.resize(src, (W4, H4), interpolation=cv2.INTER_LANCZOS4)

b4 = src4[:, :, 0].astype(int)
g4 = src4[:, :, 1].astype(int)
r4 = src4[:, :, 2].astype(int)
a4 = src4[:, :, 3]

is_fg = a4 > 80

# Helper to smooth a binary mask:
def smooth_mask(mask, blur_k=21, thresh=128):
    blurred = cv2.GaussianBlur(mask.astype(np.uint8) * 255, (blur_k, blur_k), 0)
    return blurred >= thresh

# Total character mask (smooth outer silhouette):
total_fg = smooth_mask(is_fg, blur_k=15, thresh=110)

# Create output canvas
out_rgb = np.zeros((H4, W4, 3), dtype=np.uint8)
out_alpha = np.zeros((H4, W4), dtype=np.uint8)
out_alpha[total_fg] = 255

# Default entire body to Green
out_rgb[total_fg] = C_GREEN

# -----------------------------------------------------------------
# 1. RED TAIL
# -----------------------------------------------------------------
# Red tail is at x < 135 * SCALE, y > 170 * SCALE
x_tail_max = int(135 * SCALE)
y_tail_min = int(170 * SCALE)
tail_raw = is_fg & (r4 > 140) & (g4 < 90) & (b4 > 60)
# Restrict to tail spatial box
tail_raw = tail_raw & (np.arange(W4)[None, :] < x_tail_max) & (np.arange(H4)[:, None] > y_tail_min)
# Close small holes
tail_mask = cv2.morphologyEx(tail_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
tail_smooth = smooth_mask(tail_mask > 0, blur_k=17, thresh=120) & total_fg
out_rgb[tail_smooth] = C_RED

# -----------------------------------------------------------------
# 2. YELLOW TAIL TIP (Lantern Dome)
# -----------------------------------------------------------------
# Tail tip is at x in [55..110]*SCALE, y in [135..185]*SCALE
y_tip_box = (np.arange(H4)[:, None] >= int(135 * SCALE)) & (np.arange(H4)[:, None] <= int(185 * SCALE))
x_tip_box = (np.arange(W4)[None, :] >= int(55 * SCALE)) & (np.arange(W4)[None, :] <= int(112 * SCALE))
tip_raw = is_fg & y_tip_box & x_tip_box & (r4 > 160) & (g4 > 120) & (b4 < 120)
tip_mask = cv2.morphologyEx(tip_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
tip_smooth = smooth_mask(tip_mask > 0, blur_k=15, thresh=120) & total_fg
out_rgb[tip_smooth] = C_YELLOW

# -----------------------------------------------------------------
# 3. RED CROWN CAP (on top of head)
# -----------------------------------------------------------------
# Crown cap is at x in [170..260]*SCALE, y in [40..115]*SCALE
y_crown_box = (np.arange(H4)[:, None] >= int(35 * SCALE)) & (np.arange(H4)[:, None] <= int(115 * SCALE))
x_crown_box = (np.arange(W4)[None, :] >= int(170 * SCALE)) & (np.arange(W4)[None, :] <= int(260 * SCALE))
crown_raw = is_fg & y_crown_box & x_crown_box
crown_mask = cv2.morphologyEx(crown_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
crown_smooth = smooth_mask(crown_mask > 0, blur_k=17, thresh=120) & total_fg
out_rgb[crown_smooth] = C_RED

# -----------------------------------------------------------------
# 4. YELLOW ANTENNAE
# -----------------------------------------------------------------
# Antennae are at x > 230*SCALE, y < 100*SCALE
y_ant_box = np.arange(H4)[:, None] <= int(100 * SCALE)
x_ant_box = np.arange(W4)[None, :] >= int(230 * SCALE)
ant_raw = is_fg & y_ant_box & x_ant_box
ant_smooth = smooth_mask(ant_raw, blur_k=11, thresh=100) & total_fg
out_rgb[ant_smooth] = C_YELLOW

# -----------------------------------------------------------------
# 5. WING (Blue Interior & Yellow Bulb Rim)
# -----------------------------------------------------------------
# Wing is at x in [75..175]*SCALE, y in [25..220]*SCALE
y_wing_box = (np.arange(H4)[:, None] >= int(20 * SCALE)) & (np.arange(H4)[:, None] <= int(220 * SCALE))
x_wing_box = (np.arange(W4)[None, :] >= int(75 * SCALE)) & (np.arange(W4)[None, :] <= int(175 * SCALE))

# Wing blue interior:
wing_blue_raw = is_fg & y_wing_box & x_wing_box & (b4 > 140) & (r4 < 120)
wing_blue_mask = cv2.morphologyEx(wing_blue_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
wing_blue_smooth = smooth_mask(wing_blue_mask > 0, blur_k=19, thresh=120) & total_fg

# Wing full extent (including rim):
wing_full_raw = is_fg & y_wing_box & x_wing_box & ~tail_smooth & ~tip_smooth
wing_full_mask = cv2.morphologyEx(wing_full_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
wing_full_smooth = smooth_mask(wing_full_mask > 0, blur_k=17, thresh=120) & total_fg

# Wing rim is full wing minus blue interior:
# Erode blue slightly to create clean ~35px yellow rim
kernel_rim = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
wing_blue_eroded = cv2.erode(wing_blue_smooth.astype(np.uint8), kernel_rim).astype(bool)

wing_rim = wing_full_smooth & ~wing_blue_eroded

out_rgb[wing_rim] = C_YELLOW
out_rgb[wing_blue_eroded] = C_BLUE

# -----------------------------------------------------------------
# 6. RED OPEN SMILE
# -----------------------------------------------------------------
# Mouth is at x in [260..400]*SCALE, y in [170..270]*SCALE
y_mouth_box = (np.arange(H4)[:, None] >= int(165 * SCALE)) & (np.arange(H4)[:, None] <= int(270 * SCALE))
x_mouth_box = (np.arange(W4)[None, :] >= int(260 * SCALE)) & (np.arange(W4)[None, :] <= int(410 * SCALE))
mouth_raw = is_fg & y_mouth_box & x_mouth_box & (r4 > 160) & (g4 < 80)
mouth_mask = cv2.morphologyEx(mouth_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
mouth_smooth = smooth_mask(mouth_mask > 0, blur_k=17, thresh=120) & total_fg
out_rgb[mouth_smooth] = C_RED

# -----------------------------------------------------------------
# 7. CARTOON EYE
# -----------------------------------------------------------------
# Eye is at x in [270..340]*SCALE, y in [85..155]*SCALE
y_eye_box = (np.arange(H4)[:, None] >= int(80 * SCALE)) & (np.arange(H4)[:, None] <= int(155 * SCALE))
x_eye_box = (np.arange(W4)[None, :] >= int(270 * SCALE)) & (np.arange(W4)[None, :] <= int(345 * SCALE))

# Sclera is yellow
sclera_raw = is_fg & y_eye_box & x_eye_box & (r4 > 180) & (g4 > 150) & (b4 < 140)
sclera_mask = cv2.morphologyEx(sclera_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
sclera_smooth = smooth_mask(sclera_mask > 0, blur_k=15, thresh=120) & total_fg
out_rgb[sclera_smooth] = C_YELLOW

# Iris (Blue oval) & Pupil (Black)
iris_raw = is_fg & y_eye_box & x_eye_box & (b4 > 140) & (r4 < 100)
if np.sum(iris_raw) > 50:
    iy, ix = np.where(iris_raw)
    icx, icy = int(np.mean(ix)), int(np.mean(iy))
    cv2.circle(out_rgb, (icx, icy), int(16 * SCALE), C_BLUE, -1, cv2.LINE_AA)
    cv2.circle(out_rgb, (icx, icy), int(16 * SCALE), C_BLACK, int(2.5 * SCALE), cv2.LINE_AA)
    # Pupil
    cv2.circle(out_rgb, (icx + int(2 * SCALE), icy), int(9 * SCALE), C_BLACK, -1, cv2.LINE_AA)
    # Catchlight
    cv2.circle(out_rgb, (icx - int(4 * SCALE), icy - int(4 * SCALE)), int(3.5 * SCALE), C_YELLOW, -1, cv2.LINE_AA)

# -----------------------------------------------------------------
# 8. YELLOW BELLY BANDS (Alternating with Green)
# -----------------------------------------------------------------
# Belly area: x in [130..290]*SCALE, y in [180..360]*SCALE
y_belly_box = (np.arange(H4)[:, None] >= int(180 * SCALE)) & (np.arange(H4)[:, None] <= int(370 * SCALE))
x_belly_box = (np.arange(W4)[None, :] >= int(130 * SCALE)) & (np.arange(W4)[None, :] <= int(290 * SCALE))

# Band 2 (upper yellow) & Band 4 (lower yellow):
belly_yellow_raw = is_fg & y_belly_box & x_belly_box & (r4 > 160) & (g4 > 150) & (b4 < 100) & ~wing_full_smooth
belly_yellow_mask = cv2.morphologyEx(belly_yellow_raw.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
belly_yellow_smooth = smooth_mask(belly_yellow_mask > 0, blur_k=21, thresh=120) & total_fg & ~mouth_smooth & ~tail_smooth
out_rgb[belly_yellow_smooth] = C_YELLOW

# -----------------------------------------------------------------
# 9. BOLD BLACK CARTOON OUTLINES
# -----------------------------------------------------------------
# Detect boundaries between regions:
# Total silhouette boundary:
kernel_edge = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
outer_rim = total_fg & ~cv2.erode(total_fg.astype(np.uint8), kernel_edge).astype(bool)

# Region boundaries:
def get_boundary(mask, thickness=7):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
    return cv2.dilate(mask.astype(np.uint8), k).astype(bool) & ~cv2.erode(mask.astype(np.uint8), k).astype(bool) & total_fg

b_tail = get_boundary(tail_smooth, thickness=9)
b_tip = get_boundary(tip_smooth, thickness=7)
b_wing_outer = get_boundary(wing_full_smooth, thickness=9)
b_wing_inner = get_boundary(wing_blue_eroded, thickness=7)
b_crown = get_boundary(crown_smooth, thickness=7)
b_ant = get_boundary(ant_smooth, thickness=7)
b_mouth = get_boundary(mouth_smooth, thickness=9)
b_sclera = get_boundary(sclera_smooth, thickness=7)
b_belly = get_boundary(belly_yellow_smooth, thickness=7)

# Combine all black linework
black_lines = outer_rim | b_tail | b_tip | b_wing_outer | b_wing_inner | b_crown | b_ant | b_mouth | b_sclera | b_belly

# Add cheek separation curve and wing swirl
# Draw on out_rgb
out_rgb[black_lines] = C_BLACK

# -----------------------------------------------------------------
# 10. STRICT 5-COLOR ENFORCEMENT
# -----------------------------------------------------------------
palette = np.array([C_BLACK, C_GREEN, C_RED, C_YELLOW, C_BLUE], dtype=float)
fg_pixels = out_rgb[total_fg].astype(float)
dists = np.sum((fg_pixels[:, None, :] - palette[None, :, :]) ** 2, axis=2)
out_rgb[total_fg] = palette[np.argmin(dists, axis=1)].astype(np.uint8)

# Crop with 40px padding
y_idx, x_idx = np.where(total_fg)
pad = 40
x1 = max(0, x_idx.min() - pad)
y1 = max(0, y_idx.min() - pad)
x2 = min(W4, x_idx.max() + pad + 1)
y2 = min(H4, y_idx.max() + pad + 1)

final_cropped_rgb = out_rgb[y1:y2, x1:x2]
final_cropped_alpha = out_alpha[y1:y2, x1:x2]

# In OpenCV, RGBA is BGRA for saving
final_bgra = cv2.merge([
    final_cropped_rgb[:, :, 2], # B
    final_cropped_rgb[:, :, 1], # G
    final_cropped_rgb[:, :, 0], # R
    final_cropped_alpha
])

cv2.imwrite('assets/lightningbug_5color_streamline.png', final_bgra)
print('Saved assets/lightningbug_5color_streamline.png, size:', final_cropped_rgb.shape)
