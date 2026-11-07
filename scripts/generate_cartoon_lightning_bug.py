import numpy as np
import cv2
from scipy.interpolate import splprep, splev
from PIL import Image, ImageDraw

W, H = 2400, 2280

# Canonical 5 Colors:
C_BLACK  = (20, 20, 20, 255)      # #141414
C_GREEN  = (34, 197, 94, 255)     # #22c55e
C_RED    = (230, 25, 25, 255)     # #e61919
C_YELLOW = (250, 204, 21, 255)    # #facc15
C_BLUE   = (37, 99, 235, 255)     # #2563eb
C_CLEAR  = (0, 0, 0, 0)

canvas = np.zeros((H, W, 4), dtype=np.uint8)

def smooth_curve(pts, num_pts=300, closed=True, s=0, k=3):
    pts = np.array(pts, dtype=float)
    if closed:
        pts = np.vstack([pts, pts[0]])
    deg = min(k, len(pts) - 1)
    tck, u = splprep([pts[:, 0], pts[:, 1]], s=s, per=closed, k=deg)
    u_new = np.linspace(0, 1, num_pts)
    x_new, y_new = splev(u_new, tck)
    return np.column_stack([x_new, y_new]).astype(np.int32)

def draw_filled_poly(img, pts, color):
    cv2.fillPoly(img, [pts], color)

def draw_outline(img, pts, color=C_BLACK, thickness=16, closed=True):
    cv2.polylines(img, [pts], isClosed=closed, color=color, thickness=thickness, lineType=cv2.LINE_AA)

# -------------------------------------------------------------
# 1. RED CURLED TAIL (Background layer, behind wing)
# -------------------------------------------------------------
# Tail curls up from lower back, loops up and forward
tail_outer_pts = [
    (380, 1850), (320, 1650), (250, 1400), (220, 1150),
    (240, 900), (320, 720), (450, 650), (600, 680),
    (700, 800), (680, 980), (580, 1100), (480, 1180),
    (420, 1300), (420, 1500), (500, 1700), (580, 1820)
]
tail_smooth = smooth_curve(tail_outer_pts, num_pts=400, closed=True, s=200)
draw_filled_poly(canvas, tail_smooth, C_RED)

# Red tail black stripes (accordion rings like parade float)
stripe1 = smooth_curve([(230, 1250), (330, 1220), (430, 1240)], num_pts=100, closed=False, s=50)
stripe2 = smooth_curve([(240, 1050), (350, 1000), (500, 1050)], num_pts=100, closed=False, s=50)
stripe3 = smooth_curve([(290, 850), (400, 810), (580, 880)], num_pts=100, closed=False, s=50)
for st in [stripe1, stripe2, stripe3]:
    draw_outline(canvas, st, C_BLACK, thickness=16, closed=False)

draw_outline(canvas, tail_smooth, C_BLACK, thickness=18, closed=True)

# -------------------------------------------------------------
# 2. YELLOW TAIL TIP (Lantern Dome)
# -------------------------------------------------------------
# Perched at top crest of tail (x ~ 450..650, y ~ 530..680), directly next to wing
tip_pts = [
    (450, 650), (430, 560), (480, 480), (550, 450), (620, 480), (660, 560), (640, 650), (550, 670)
]
tip_smooth = smooth_curve(tip_pts, num_pts=200, closed=True, s=50)
draw_filled_poly(canvas, tip_smooth, C_YELLOW)

# Tip internal facet / bulb ring lines
tip_line1 = smooth_curve([(435, 560), (550, 550), (655, 560)], num_pts=80, closed=False)
tip_line2 = np.array([(550, 450), (550, 670)], dtype=np.int32)
draw_outline(canvas, tip_line1, C_BLACK, thickness=12, closed=False)
draw_outline(canvas, tip_line2, C_BLACK, thickness=12, closed=False)
draw_outline(canvas, tip_smooth, C_BLACK, thickness=16, closed=True)

# -------------------------------------------------------------
# 3. WING (Sits in front of red tail, next to yellow tip)
# -------------------------------------------------------------
# Outer Yellow Rim:
wing_rim_outer_pts = [
    (670, 620), (580, 420), (540, 240), (580, 130), (680, 70),
    (810, 120), (950, 280), (1020, 550), (1050, 850), (1020, 1100),
    (920, 1250), (800, 1150), (740, 950), (700, 780)
]
# Adjust wing outer contour so left edge cleanly overlaps red tail down to body
wing_outer_pts = [
    (680, 580), (600, 400), (550, 230), (600, 120), (710, 60),
    (830, 110), (960, 280), (1030, 550), (1060, 850), (1010, 1080),
    (920, 1220), (810, 1100), (750, 950), (700, 750)
]
wing_outer_smooth = smooth_curve(wing_outer_pts, num_pts=350, closed=True, s=150)
draw_filled_poly(canvas, wing_outer_smooth, C_YELLOW)

# Blue Wing Interior (Inset from yellow rim by ~50px):
wing_inner_pts = [
    (730, 570), (660, 400), (620, 260), (660, 170), (730, 130),
    (820, 170), (920, 310), (970, 540), (990, 820), (950, 1020),
    (870, 1120), (800, 1020), (770, 880), (740, 720)
]
wing_inner_smooth = smooth_curve(wing_inner_pts, num_pts=350, closed=True, s=120)
draw_filled_poly(canvas, wing_inner_smooth, C_BLUE)

# Cartoon Swirl Graphic inside blue wing (Classic parade wire motif)
swirl_pts = [
    (780, 320), (840, 270), (890, 340), (890, 480), (830, 600),
    (760, 680), (710, 620), (710, 480), (760, 380), (830, 370), (850, 430)
]
swirl_smooth = smooth_curve(swirl_pts, num_pts=200, closed=False, s=100)
draw_outline(canvas, swirl_smooth, C_BLACK, thickness=14, closed=False)

draw_outline(canvas, wing_inner_smooth, C_BLACK, thickness=14, closed=True)
draw_outline(canvas, wing_outer_smooth, C_BLACK, thickness=18, closed=True)

# -------------------------------------------------------------
# 4. MAIN BODY & BELLY (Alternating Yellow & Green Bands)
# -------------------------------------------------------------
# The body spans from x ~ 580 to x ~ 1800, y ~ 600 to 2050
# Let's define the alternating horizontal bands:
# Band 1 (Top / Upper back): Green
# Band 2 (Upper-mid belly): Yellow
# Band 3 (Center belly): Green
# Band 4 (Lower belly): Yellow
# Band 5 (Lower skirt / feet): Green

# Body right border / head junction: x ~ 1500..1650, y ~ 650..1700
# Body left border (wing / tail junction): x ~ 580..850, y ~ 1200..1900

# Let's create the full body outer shape first, then divide into bands
body_pts = [
    (880, 650), (1200, 550), (1500, 650), (1680, 900), (1750, 1200),
    (1780, 1500), (1750, 1800), (1650, 1980), (1450, 2080), (1150, 2120),
    (850, 2050), (650, 1950), (600, 1800), (620, 1550), (700, 1350),
    (800, 1150), (850, 900)
]
body_smooth = smooth_curve(body_pts, num_pts=500, closed=True, s=250)

# Fill entire body base with Green
draw_filled_poly(canvas, body_smooth, C_GREEN)

# Band 2 (Upper-mid yellow band):
b2_pts = [
    (720, 1100), (1000, 1020), (1350, 1050), (1680, 1150),
    (1720, 1350), (1350, 1250), (1000, 1220), (680, 1300)
]
b2_smooth = smooth_curve(b2_pts, num_pts=300, closed=True, s=100)
draw_filled_poly(canvas, b2_smooth, C_YELLOW)
draw_outline(canvas, b2_smooth, C_BLACK, thickness=14, closed=True)

# Band 4 (Lower yellow band):
b4_pts = [
    (640, 1550), (950, 1480), (1300, 1500), (1750, 1580),
    (1740, 1780), (1300, 1700), (950, 1680), (620, 1750)
]
b4_smooth = smooth_curve(b4_pts, num_pts=300, closed=True, s=100)
draw_filled_poly(canvas, b4_smooth, C_YELLOW)
draw_outline(canvas, b4_smooth, C_BLACK, thickness=14, closed=True)

# Segmented green legs / feet along bottom:
# Front foot:
foot_front_pts = [
    (1400, 1850), (1600, 1800), (1780, 1820), (1950, 1950), (1880, 2080), (1650, 2080), (1450, 2000)
]
foot_front = smooth_curve(foot_front_pts, num_pts=200, closed=True, s=80)
draw_filled_poly(canvas, foot_front, C_GREEN)
draw_outline(canvas, foot_front, C_BLACK, thickness=16, closed=True)

# Mid foot:
foot_mid_pts = [
    (980, 1880), (1200, 1850), (1350, 1900), (1400, 2080), (1150, 2120), (950, 2060)
]
foot_mid = smooth_curve(foot_mid_pts, num_pts=200, closed=True, s=80)
draw_filled_poly(canvas, foot_mid, C_GREEN)
draw_outline(canvas, foot_mid, C_BLACK, thickness=16, closed=True)

# Rear foot:
foot_rear_pts = [
    (650, 1880), (850, 1850), (920, 1980), (880, 2080), (680, 2040), (600, 1950)
]
foot_rear = smooth_curve(foot_rear_pts, num_pts=200, closed=True, s=80)
draw_filled_poly(canvas, foot_rear, C_GREEN)
draw_outline(canvas, foot_rear, C_BLACK, thickness=16, closed=True)

# Outer body contour outline:
draw_outline(canvas, body_smooth, C_BLACK, thickness=18, closed=True)

# -------------------------------------------------------------
# 5. GIANT FRIENDLY HEAD & FACE (Green)
# -------------------------------------------------------------
head_pts = [
    (1450, 520), (1650, 400), (1850, 420), (2050, 550), (2180, 750),
    (2220, 1020), (2180, 1280), (2050, 1450), (1850, 1550), (1650, 1580),
    (1480, 1420), (1380, 1180), (1350, 900), (1380, 680)
]
head_smooth = smooth_curve(head_pts, num_pts=400, closed=True, s=200)
draw_filled_poly(canvas, head_smooth, C_GREEN)

# Cheerful Open Smile (Vibrant Red with bold black outlines & smile creases)
mouth_pts = [
    (1550, 1150), (1750, 1220), (1980, 1180), (2120, 1020),
    (2180, 1120), (2080, 1300), (1880, 1400), (1650, 1360), (1520, 1240)
]
mouth_smooth = smooth_curve(mouth_pts, num_pts=250, closed=True, s=80)
draw_filled_poly(canvas, mouth_smooth, C_RED)
draw_outline(canvas, mouth_smooth, C_BLACK, thickness=16, closed=True)

# Smile corner dimple lines
dimple = smooth_curve([(1510, 1190), (1540, 1220), (1520, 1270)], num_pts=50, closed=False)
draw_outline(canvas, dimple, C_BLACK, thickness=14, closed=False)

# Big Expressive Cartoon Eye
# Sclera (Electric Yellow):
eye_sclera_pts = [
    (1680, 720), (1800, 620), (1920, 660), (1980, 780), (1950, 920), (1820, 980), (1700, 920), (1650, 820)
]
eye_sclera = smooth_curve(eye_sclera_pts, num_pts=200, closed=True, s=50)
draw_filled_poly(canvas, eye_sclera, C_YELLOW)
draw_outline(canvas, eye_sclera, C_BLACK, thickness=14, closed=True)

# Iris (Parade Blue):
cv2.circle(canvas, (1840, 800), 75, C_BLUE, -1, cv2.LINE_AA)
cv2.circle(canvas, (1840, 800), 75, C_BLACK, 10, cv2.LINE_AA)

# Pupil (Black):
cv2.circle(canvas, (1850, 800), 45, C_BLACK, -1, cv2.LINE_AA)

# Specular Catchlight (Yellow):
cv2.circle(canvas, (1830, 775), 18, C_YELLOW, -1, cv2.LINE_AA)

# Eyelid / Brow Arch (Black outline):
brow_pts = [(1650, 680), (1780, 570), (1950, 610), (2020, 700)]
brow = smooth_curve(brow_pts, num_pts=80, closed=False, s=30)
draw_outline(canvas, brow, C_BLACK, thickness=16, closed=False)

# Cheek contour & head outer outline
draw_outline(canvas, head_smooth, C_BLACK, thickness=18, closed=True)

# -------------------------------------------------------------
# 6. RED CROWN CAP & RADIATING YELLOW ANTENNAE
# -------------------------------------------------------------
# Red Crown Cap on top of head (x ~ 1520..1950, y ~ 260..450):
crown_pts = [
    (1520, 430), (1620, 310), (1750, 260), (1880, 310), (1960, 420),
    (1850, 420), (1750, 400), (1650, 420)
]
crown_smooth = smooth_curve(crown_pts, num_pts=250, closed=True, s=60)
draw_filled_poly(canvas, crown_smooth, C_RED)

# Crown facet lines
c_line1 = smooth_curve([(1620, 310), (1650, 420)], num_pts=50, closed=False)
c_line2 = smooth_curve([(1750, 260), (1750, 400)], num_pts=50, closed=False)
c_line3 = smooth_curve([(1880, 310), (1850, 420)], num_pts=50, closed=False)
for cl in [c_line1, c_line2, c_line3]:
    draw_outline(canvas, cl, C_BLACK, thickness=12, closed=False)

draw_outline(canvas, crown_smooth, C_BLACK, thickness=16, closed=True)

# Radiating Yellow Antennae (3 playful curved rays shooting up-right from crown):
# Antenna 1 (Front):
ant1_pts = [
    (1880, 310), (1980, 220), (2100, 170), (2240, 160),
    (2260, 195), (2130, 215), (2000, 270), (1910, 340)
]
ant1 = smooth_curve(ant1_pts, num_pts=200, closed=True, s=50)
draw_filled_poly(canvas, ant1, C_YELLOW)
draw_outline(canvas, ant1, C_BLACK, thickness=14, closed=True)

# Antenna 2 (Middle):
ant2_pts = [
    (1780, 270), (1880, 170), (2000, 100), (2150, 80),
    (2165, 115), (2020, 140), (1900, 220), (1820, 300)
]
ant2 = smooth_curve(ant2_pts, num_pts=200, closed=True, s=50)
draw_filled_poly(canvas, ant2, C_YELLOW)
draw_outline(canvas, ant2, C_BLACK, thickness=14, closed=True)

# Antenna 3 (Rear):
ant3_pts = [
    (1680, 290), (1770, 180), (1880, 100), (2020, 70),
    (2035, 105), (1900, 140), (1790, 230), (1720, 310)
]
ant3 = smooth_curve(ant3_pts, num_pts=200, closed=True, s=50)
draw_filled_poly(canvas, ant3, C_YELLOW)
draw_outline(canvas, ant3, C_BLACK, thickness=14, closed=True)

# -------------------------------------------------------------
# 7. STRICT 5-COLOR ENFORCEMENT & CROPPING
# -------------------------------------------------------------
# Re-quantize any non-transparent pixel to strictly one of the 5 canonical palette colors
palette = np.array([
    [20, 20, 20],      # Black
    [34, 197, 94],     # Green
    [230, 25, 25],     # Red
    [250, 204, 21],    # Yellow
    [37, 99, 235]      # Blue
], dtype=float)

alpha_mask = canvas[:, :, 3] > 60
rgb_pixels = canvas[:, :, :3][alpha_mask].astype(float)

# Find nearest palette color for every foreground pixel
dists = np.sum((rgb_pixels[:, None, :] - palette[None, :, :]) ** 2, axis=2)
nearest_idx = np.argmin(dists, axis=1)

quantized_rgb = palette[nearest_idx].astype(np.uint8)
canvas[:, :, :3][alpha_mask] = quantized_rgb
canvas[:, :, 3][alpha_mask] = 255
canvas[:, :, 3][~alpha_mask] = 0

# Crop with 50px padding
y_indices, x_indices = np.where(canvas[:, :, 3] == 255)
pad = 50
x1 = max(0, x_indices.min() - pad)
y1 = max(0, y_indices.min() - pad)
x2 = min(W, x_indices.max() + pad + 1)
y2 = min(H, y_indices.max() + pad + 1)

cropped = canvas[y1:y2, x1:x2]
out_img = Image.fromarray(cropped)
out_img.save('assets/lightningbug_cartoon_test.png')
print('Successfully generated lightningbug_cartoon_test.png, size:', out_img.size)
