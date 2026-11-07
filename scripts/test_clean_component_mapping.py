import cv2
import numpy as np

# Load transparent image
img = cv2.imread('assets/lightningbug_transparent.png', cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]

a = img[:, :, 3]
fg_mask = a > 100
r = img[:, :, 2].astype(int)
g = img[:, :, 1].astype(int)
b = img[:, :, 0].astype(int)

# Detect outlines in 1x
is_black = fg_mask & (r < 75) & (g < 75) & (b < 75)
k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
is_black_closed = cv2.dilate(is_black.astype(np.uint8), k3).astype(bool)

non_black = (fg_mask & ~is_black_closed).astype(np.uint8) * 255
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(non_black, connectivity=4)

# Color masks in 1x:
m_red = np.zeros((h, w), dtype=bool)
m_yellow = np.zeros((h, w), dtype=bool)
m_blue = np.zeros((h, w), dtype=bool)
m_green = np.zeros((h, w), dtype=bool)

# Specific Label Assignments:
# Tail:
m_red[labels == 80] = True

# Tail Tip Dome:
m_yellow[labels == 69] = True
m_yellow[labels == 71] = True

# Crown Cap:
m_red[labels == 19] = True

# Antennae:
m_yellow[labels == 2] = True
m_yellow[labels == 7] = True

# Mouth:
m_red[labels == 88] = True

# Belly Yellow Bands:
m_yellow[labels == 96] = True
m_yellow[labels == 87] = True
m_yellow[labels == 123] = True

# Front Snout / Muzzle Facet (Warm yellow face highlight):
m_yellow[labels == 74] = True

# Wing:
wing_raw = (labels == 8) | (labels == 33)
k_wclose = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
wing_closed = cv2.morphologyEx(wing_raw.astype(np.uint8), cv2.MORPH_CLOSE, k_wclose)
cnts, _ = cv2.findContours(wing_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c_wing = max(cnts, key=cv2.contourArea)

wing_solid = np.zeros((h, w), dtype=np.uint8)
cv2.drawContours(wing_solid, [c_wing], -1, 255, -1)
wing_solid_mask = (wing_solid > 0) & fg_mask & ~m_red & ~m_yellow

# Erode wing by 6px for yellow outer frame vs blue interior:
k_rim = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
wing_blue = cv2.erode(wing_solid, k_rim) > 0
wing_yellow = wing_solid_mask & ~wing_blue

m_yellow[wing_yellow] = True
m_blue[wing_blue] = True

# All other non-black cells are Green:
assigned = m_red | m_yellow | m_blue
m_green[fg_mask & ~assigned] = True

# -------------------------------------------------------------
# 4x Supersampling & Gentle Vector Curve Smoothing
# -------------------------------------------------------------
SCALE = 4
H4, W4 = h * SCALE, w * SCALE

def up_and_smooth(mask, k_blur=15, thresh=0.5):
    up = cv2.resize(mask.astype(np.float32), (W4, H4), interpolation=cv2.INTER_LINEAR)
    blurred = cv2.GaussianBlur(up, (k_blur, k_blur), 0)
    return blurred >= thresh

up_fg = cv2.resize(fg_mask.astype(np.float32), (W4, H4), interpolation=cv2.INTER_LINEAR)
total_fg_smooth = cv2.GaussianBlur(up_fg, (17, 17), 0) >= 0.45

# Smooth each class field gently so corners round naturally into flowing cartoon curves
p_green = cv2.GaussianBlur(cv2.resize(m_green.astype(np.float32), (W4, H4)), (19, 19), 0)
p_red = cv2.GaussianBlur(cv2.resize(m_red.astype(np.float32), (W4, H4)), (19, 19), 0)
p_yellow = cv2.GaussianBlur(cv2.resize(m_yellow.astype(np.float32), (W4, H4)), (19, 19), 0)
p_blue = cv2.GaussianBlur(cv2.resize(m_blue.astype(np.float32), (W4, H4)), (19, 19), 0)

# Prob stack
prob_stack = np.stack([p_green, p_red, p_yellow, p_blue], axis=2)
class_map = np.argmax(prob_stack, axis=2) # 0: Green, 1: Red, 2: Yellow, 3: Blue

# Canonical Colors
C_BLACK  = np.array([20, 20, 20], dtype=np.uint8)
C_GREEN  = np.array([34, 197, 94], dtype=np.uint8)
C_RED    = np.array([230, 25, 25], dtype=np.uint8)
C_YELLOW = np.array([250, 204, 21], dtype=np.uint8)
C_BLUE   = np.array([37, 99, 235], dtype=np.uint8)

color_lut = np.array([C_GREEN, C_RED, C_YELLOW, C_BLUE], dtype=np.uint8)
out_rgb = color_lut[class_map]

# -------------------------------------------------------------
# Bold Black Cartoon Outlines
# -------------------------------------------------------------
grad_x = np.abs(class_map[:, 1:] - class_map[:, :-1]) > 0
grad_y = np.abs(class_map[1:, :] - class_map[:-1, :]) > 0

is_boundary = np.zeros((H4, W4), dtype=bool)
is_boundary[:, 1:] |= grad_x
is_boundary[1:, :] |= grad_y

k_out = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
outer_rim = total_fg_smooth & ~cv2.erode(total_fg_smooth.astype(np.uint8), k_out).astype(bool)

k_stroke = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
bold_lines = cv2.dilate(is_boundary.astype(np.uint8), k_stroke).astype(bool) & total_fg_smooth
all_black = bold_lines | outer_rim

out_rgb[all_black] = C_BLACK

# -------------------------------------------------------------
# Cartoon Eye
# -------------------------------------------------------------
eye_cx = int(312 * SCALE)
eye_cy = int(131 * SCALE)
sclera_rx = int(18 * SCALE)
sclera_ry = int(25 * SCALE)

cv2.ellipse(out_rgb, (eye_cx, eye_cy), (sclera_rx, sclera_ry), -15, 0, 360, tuple(int(x) for x in C_YELLOW), -1, cv2.LINE_AA)
cv2.ellipse(out_rgb, (eye_cx, eye_cy), (sclera_rx, sclera_ry), -15, 0, 360, tuple(int(x) for x in C_BLACK), int(2.5 * SCALE), cv2.LINE_AA)

# Iris
iris_r = int(11 * SCALE)
cv2.circle(out_rgb, (eye_cx + int(2 * SCALE), eye_cy + int(2 * SCALE)), iris_r, tuple(int(x) for x in C_BLUE), -1, cv2.LINE_AA)
cv2.circle(out_rgb, (eye_cx + int(2 * SCALE), eye_cy + int(2 * SCALE)), iris_r, tuple(int(x) for x in C_BLACK), int(1.8 * SCALE), cv2.LINE_AA)

# Pupil
pupil_r = int(6.5 * SCALE)
cv2.circle(out_rgb, (eye_cx + int(3 * SCALE), eye_cy + int(2 * SCALE)), pupil_r, tuple(int(x) for x in C_BLACK), -1, cv2.LINE_AA)

# Catchlight
catch_r = int(2.5 * SCALE)
cv2.circle(out_rgb, (eye_cx + int(1 * SCALE), eye_cy - int(1 * SCALE)), catch_r, tuple(int(x) for x in C_YELLOW), -1, cv2.LINE_AA)

# Eyelid arch
cv2.ellipse(out_rgb, (eye_cx, eye_cy - int(4 * SCALE)), (sclera_rx + int(2 * SCALE), sclera_ry), -15, 200, 340, tuple(int(x) for x in C_BLACK), int(3.0 * SCALE), cv2.LINE_AA)

# -------------------------------------------------------------
# Cartoon Details: Tail Accordion Rings & Wing Swirl
# -------------------------------------------------------------
tail_stripes = [
    np.array([(45*SCALE, 210*SCALE), (75*SCALE, 203*SCALE), (105*SCALE, 206*SCALE)], dtype=np.int32),
    np.array([(48*SCALE, 250*SCALE), (80*SCALE, 240*SCALE), (115*SCALE, 245*SCALE)], dtype=np.int32),
    np.array([(55*SCALE, 295*SCALE), (90*SCALE, 285*SCALE), (125*SCALE, 290*SCALE)], dtype=np.int32)
]
for st in tail_stripes:
    cv2.polylines(out_rgb, [st], isClosed=False, color=tuple(int(x) for x in C_BLACK), thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)

# Wing cartoon swirl loop inside blue wing:
swirl_pts = np.array([
    (100*SCALE, 80*SCALE), (115*SCALE, 65*SCALE), (130*SCALE, 80*SCALE), (135*SCALE, 115*SCALE),
    (125*SCALE, 150*SCALE), (108*SCALE, 165*SCALE), (95*SCALE, 145*SCALE), (105*SCALE, 105*SCALE), (120*SCALE, 100*SCALE)
], dtype=np.int32)
cv2.polylines(out_rgb, [swirl_pts], isClosed=False, color=tuple(int(x) for x in C_BLACK), thickness=int(2.5 * SCALE), lineType=cv2.LINE_AA)

# Crown lines on Red Cap:
cv2.line(out_rgb, (185*SCALE, 55*SCALE), (200*SCALE, 105*SCALE), tuple(int(x) for x in C_BLACK), int(2.0 * SCALE), cv2.LINE_AA)
cv2.line(out_rgb, (215*SCALE, 45*SCALE), (225*SCALE, 105*SCALE), tuple(int(x) for x in C_BLACK), int(2.0 * SCALE), cv2.LINE_AA)

# Dimple at corner of mouth:
dimple = np.array([(255*SCALE, 205*SCALE), (262*SCALE, 218*SCALE), (258*SCALE, 230*SCALE)], dtype=np.int32)
cv2.polylines(out_rgb, [dimple], isClosed=False, color=tuple(int(x) for x in C_BLACK), thickness=int(2.2 * SCALE), lineType=cv2.LINE_AA)

# -------------------------------------------------------------
# Strict 5-Color Enforcement & Cropping
# -------------------------------------------------------------
palette = np.array([C_BLACK, C_GREEN, C_RED, C_YELLOW, C_BLUE], dtype=float)
fg_pix = out_rgb[total_fg_smooth].astype(float)
dists = np.sum((fg_pix[:, None, :] - palette[None, :, :]) ** 2, axis=2)
out_rgb[total_fg_smooth] = palette[np.argmin(dists, axis=1)].astype(np.uint8)

alpha = np.zeros((H4, W4), dtype=np.uint8)
alpha[total_fg_smooth] = 255

y_indices, x_indices = np.where(total_fg_smooth)
pad = 40
x1 = max(0, x_indices.min() - pad)
y1 = max(0, y_indices.min() - pad)
x2 = min(W4, x_indices.max() + pad + 1)
y2 = min(H4, y_indices.max() + pad + 1)

cropped_rgb = out_rgb[y1:y2, x1:x2]
cropped_alpha = alpha[y1:y2, x1:x2]

out_bgra = cv2.merge([
    cropped_rgb[:, :, 2],
    cropped_rgb[:, :, 1],
    cropped_rgb[:, :, 0],
    cropped_alpha
])

cv2.imwrite('assets/lightningbug_clean_streamline.png', out_bgra)
print('Successfully saved assets/lightningbug_clean_streamline.png, size:', cropped_rgb.shape)
