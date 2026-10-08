import cv2
import numpy as np
from PIL import Image

# Read original snail2.png
img = cv2.imread('assets/snail2.png')
h, w, _ = img.shape
cx, cy = 153.5, 156.5

# 5 Discrete Colors for 3D Printing (RGBA)
C_TRANS = np.array([0, 0, 0, 0], dtype=np.uint8)
C_BLACK = np.array([17, 22, 29, 255], dtype=np.uint8)
C_GOLD  = np.array([250, 204, 21, 255], dtype=np.uint8)
C_RED   = np.array([239, 68, 68, 255], dtype=np.uint8)
C_BLUE  = np.array([37, 99, 235, 255], dtype=np.uint8)
C_GREEN = np.array([16, 185, 129, 255], dtype=np.uint8)

# Initialize blank transparent image
out = np.zeros((h, w, 4), dtype=np.uint8)

# ---------------------------------------------------------
# 1. ANTENNAE & HEAD
# ---------------------------------------------------------
# Left Antenna stalk
left_ant_pts = [
    [43, 119], [39, 112], [37, 106], [40, 100], [45, 99], [49, 102],
    [45, 104], [41, 105], [41, 110], [44, 118]
]
# Right Antenna stalk
right_ant_pts = [
    [47, 118], [45, 111], [46, 104], [52, 99], [59, 101], [64, 106],
    [59, 107], [53, 104], [49, 107], [50, 117]
]

# Diamond Eye on cheek
eye_diamond_pts = [
    [40, 128], [44, 134], [40, 140], [36, 134]
]

# Snail Head and Body Polygon (Red)
body_poly_pts = [
    # Top of head where antennae attach
    [42, 119], [51, 118],
    # Back of neck down to hood junction
    [53, 128], [58, 142], [64, 156], [67, 169],
    # Hood under-junction to foot
    [78, 178], [94, 189], [112, 202], [126, 212],
    # Foot base (flat along bottom ground)
    [121, 217], [105, 218], [85, 216], [70, 210], [56, 198],
    # Front chest / neck
    [48, 182], [41, 168], [36, 154],
    # Front of face / cheek
    [31, 145], [28, 135], [32, 126], [42, 119]
]

# ---------------------------------------------------------
# 2. SHELL POLYGON & FEATURES
# ---------------------------------------------------------
shell_rim_pts = [
    # Hood junction with neck
    [67, 169], [68, 155], [71, 142], [77, 129], [86, 117], [97, 107], 
    [110, 100], [123, 95], [136, 93], [149, 95], [163, 101], [175, 110], 
    [184, 122], [189, 136], [192, 154], [189, 172], [185, 188], [178, 202], 
    [168, 214], [154, 223], [138, 220], [126, 212],
    # Hood under-junction
    [112, 202], [94, 189], [78, 178], [67, 169]
]

# Outer boundary of shell for rim drawing:
shell_outer_rim_pts = [
    [67, 169], [68, 155], [71, 142], [77, 129], [86, 117], [97, 107], 
    [110, 100], [123, 95], [136, 93], [149, 95], [163, 101], [175, 110], 
    [184, 122], [189, 136], [192, 154], [189, 172], [185, 188], [178, 202], 
    [168, 214], [154, 223], [138, 220], [126, 212]
]

# Continuous Smooth Spiral Nodes inside the shell:
spiral_nodes = [
    # Starts at bottom right junction with outer rim:
    [178, 202],
    [166, 206],
    [152, 208],
    [136, 203],
    [118, 194],
    [104, 180],
    [93, 164],
    [88, 148],
    [91, 132],
    [100, 118],
    [114, 108],
    [132, 104],
    [150, 106],
    [164, 114],
    [174, 128],
    [178, 144],
    [174, 158],
    [165, 168],
    [153, 171],
    [143, 166],
    [141, 156],
    [146, 150],
    [153, 152],
    [156, 158]
]

# Create masks
mask_body = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(mask_body, [np.array(body_poly_pts, dtype=np.int32)], 255)

mask_eye = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(mask_eye, [np.array(eye_diamond_pts, dtype=np.int32)], 255)

mask_ant = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(mask_ant, [np.array(left_ant_pts, dtype=np.int32)], 255)
cv2.fillPoly(mask_ant, [np.array(right_ant_pts, dtype=np.int32)], 255)

mask_shell = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(mask_shell, [np.array(shell_rim_pts, dtype=np.int32)], 255)

# Outer Gold Rim Track (3.5px width) along perimeter
mask_rim = np.zeros((h, w), dtype=np.uint8)
cv2.polylines(mask_rim, [np.array(shell_outer_rim_pts, dtype=np.int32)], isClosed=False, color=255, thickness=4)
# Also bottom junction of hood
cv2.polylines(mask_rim, [np.array([[126, 212], [112, 202], [94, 189], [78, 178], [67, 169]], dtype=np.int32)], isClosed=False, color=255, thickness=3)
mask_rim = mask_rim & mask_shell

# Spiral Track (3.5px width)
mask_spiral = np.zeros((h, w), dtype=np.uint8)
spline_pts = []
for i in range(len(spiral_nodes) - 1):
    p0 = spiral_nodes[i]
    p1 = spiral_nodes[i+1]
    for t in np.linspace(0, 1, 8, endpoint=False):
        spline_pts.append([int(round((1-t)*p0[0] + t*p1[0])), int(round((1-t)*p0[1] + t*p1[1]))])
spline_pts.append(spiral_nodes[-1])
cv2.polylines(mask_spiral, [np.array(spline_pts, dtype=np.int32)], isClosed=False, color=255, thickness=4)
# Center curl filled cap
cv2.circle(mask_spiral, (int(round(cx)), int(round(cy))), 6, 255, -1)
mask_spiral = mask_spiral & mask_shell

# Combined Shell Gold
mask_shell_gold = mask_rim | mask_spiral

# ---------------------------------------------------------
# 3. RADIAL STRIPES SECTORS
# ---------------------------------------------------------
mask_stripes = (mask_shell > 0) & (mask_shell_gold == 0)

yy, xx = np.mgrid[:h, :w]
theta_offset = 5.0 # deg
angles_deg = (np.arctan2(yy - cy, xx - cx) * 180.0 / np.pi - theta_offset) % 360.0
sector_idx = (angles_deg / 11.25).astype(int) % 32

# Alternating sequence:
# 0 -> Green, 1 -> Black, 2 -> Blue, 3 -> Black
color_cycle = (sector_idx + 2) % 4

# ---------------------------------------------------------
# 4. COMPOSE FINAL 5-COLOR IMAGE
# ---------------------------------------------------------
# 1. Red Body (exclude eye and antennae)
out[(mask_body > 0) & (mask_eye == 0) & (mask_ant == 0)] = C_RED

# 2. Gold Eye & Antennae
out[mask_eye > 0] = C_GOLD
out[mask_ant > 0] = C_GOLD

# 3. Shell Stripes (Alternating Green, Black, Blue, Black)
for y in range(h):
    for x in range(w):
        if mask_stripes[y, x]:
            c = color_cycle[y, x]
            if c == 0:
                out[y, x] = C_GREEN
            elif c == 1 or c == 3:
                out[y, x] = C_BLACK
            elif c == 2:
                out[y, x] = C_BLUE

# 4. Gold Rim & Spiral
out[mask_shell_gold > 0] = C_GOLD

# Save output
Image.fromarray(out).save('assets/snail2.png')
print("Successfully generated assets/snail2.png")
