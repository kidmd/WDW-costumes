import cv2
import numpy as np
from PIL import Image

# Load original Turtle_clean.png
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)
h, w = arr.shape[:2]

# Define 5 discrete colors:
# Black (outlines/chassis)
COLOR_BLACK  = np.array([17, 22, 29, 255], dtype=np.uint8)
# Yellow (head, neck, shirt, arm)
COLOR_YELLOW = np.array([236, 203, 46, 255], dtype=np.uint8)
# Red (tie, mouth)
COLOR_RED    = np.array([216, 29, 23, 255], dtype=np.uint8)
# Green (shell plates, belly plates, feet)
COLOR_GREEN  = np.array([33, 101, 46, 255], dtype=np.uint8)
# Blue (shell grid/matrix, glasses frames, pupil)
COLOR_BLUE   = np.array([41, 64, 98, 255], dtype=np.uint8)

# 1. Base classification of all non-transparent pixels
alpha = arr[:, :, 3]
a = alpha
fg_mask = alpha > 128
r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# Detect black lines
is_black = fg_mask & (r < 65) & (g < 75) & (b < 85)

# Detect grey glasses frame:
# In head area: y in [260, 750], x in [260, 950]
is_head = np.zeros((h, w), dtype=bool)
is_head[260:750, 260:950] = True
is_grey_frame = is_head & fg_mask & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 40) & (r < 175)

# Use connected components to isolate Component 1 of the glasses frame
num_l, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grey_frame.astype(np.uint8), connectivity=8)
# Find largest component
if num_l > 1:
    largest_l = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    glasses_mask = (labels == largest_l)
else:
    glasses_mask = is_grey_frame

# Detach any pixels touching top edge of head (y < 365)
glasses_mask[:365, :] = False

# Dilate glasses slightly to close any pinholes, then compute thin black outline
kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
glasses_mask = cv2.morphologyEx(glasses_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel_close) > 0

# The user asked: "Make his glasses blue with a thin black outline."
# Outline of glasses: morphological gradient of glasses_mask (width ~ 3px)
kernel_edge = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
glasses_dilated = cv2.dilate(glasses_mask.astype(np.uint8), kernel_edge) > 0
glasses_eroded = cv2.erode(glasses_mask.astype(np.uint8), kernel_edge) > 0
glasses_edge = glasses_dilated & (~glasses_eroded)

# 2. Front of turtle:
# Helper floodfill
fg_nonblack = (fg_mask & (~is_black)).astype(np.uint8) * 255
def get_mask(seed_pt):
    mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = fg_nonblack.copy()
    cv2.floodFill(filled, mask, seed_pt, 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
    return (filled == 128)

mask_20 = get_mask((591, 1164)) # left shirt flap
mask_24 = get_mask((554, 1257)) # left blue notch 1
mask_26 = get_mask((564, 1310)) # left blue notch 2
mask_28 = get_mask((750, 1503)) # green belly plate under tie

# Internal lines between 20, 24, 26 to dissolve into yellow
tie_mask = get_mask((637, 1323))
kernel_tie = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
tie_border = cv2.dilate(tie_mask.astype(np.uint8), kernel_tie) > 0

# Alpha outer border
alpha_mask = (a > 128).astype(np.uint8)
kernel_alpha = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
alpha_erode = cv2.erode(alpha_mask, kernel_alpha) > 0
outer_border = (alpha_mask > 0) & (~alpha_erode)

box_left = np.zeros((h, w), dtype=bool)
box_left[1130:1350, 545:615] = True
internal_left_lines = box_left & is_black & (~outer_border) & (~tie_border)

# 3. Feet: convert lime green to C_GREEN
# Lime green pixels have: r ~ 120-150, g ~ 170-200, b ~ 60-90
is_lime_feet = fg_mask & (g > 140) & (r > 90) & (r < 180) & (b < 110)

# Build result array
result = np.zeros((h, w, 4), dtype=np.uint8)

# Classify all non-transparent pixels into the 5 colors:
for y in range(h):
    for x in range(w):
        if not fg_mask[y, x]:
            continue
        
        # Check glasses
        if glasses_mask[y, x]:
            result[y, x] = COLOR_BLUE
            continue
            
        # Check if in front yellow shirt regions
        if mask_20[y, x] or mask_24[y, x] or mask_26[y, x] or mask_28[y, x] or internal_left_lines[y, x]:
            result[y, x] = COLOR_YELLOW
            continue
            
        # Check if lime feet
        if is_lime_feet[y, x]:
            result[y, x] = COLOR_GREEN
            continue
            
        # General color matching:
        cur_r, cur_g, cur_b = r[y, x], g[y, x], b[y, x]
        
        # Black lines
        if is_black[y, x]:
            result[y, x] = COLOR_BLACK
        # Red tie & mouth
        elif cur_r > 160 and cur_g < 70 and cur_b < 70:
            result[y, x] = COLOR_RED
        # Yellow body, head, neck, shirt
        elif cur_r > 160 and cur_g > 140 and cur_b < 110:
            result[y, x] = COLOR_YELLOW
        # Green shell plates
        elif cur_g > 70 and cur_r < 90 and cur_b < 90:
            result[y, x] = COLOR_GREEN
        # Blue shell ribs, pupil
        elif cur_b > 65 and cur_r < 80:
            result[y, x] = COLOR_BLUE
        else:
            # Distance to the 5 colors
            c_curr = np.array([cur_r, cur_g, cur_b], dtype=float)
            d_black = np.linalg.norm(c_curr - COLOR_BLACK[:3])
            d_yellow = np.linalg.norm(c_curr - COLOR_YELLOW[:3])
            d_red = np.linalg.norm(c_curr - COLOR_RED[:3])
            d_green = np.linalg.norm(c_curr - COLOR_GREEN[:3])
            d_blue = np.linalg.norm(c_curr - COLOR_BLUE[:3])
            dists = [d_black, d_yellow, d_red, d_green, d_blue]
            best = np.argmin(dists)
            if best == 0: result[y, x] = COLOR_BLACK
            elif best == 1: result[y, x] = COLOR_YELLOW
            elif best == 2: result[y, x] = COLOR_RED
            elif best == 3: result[y, x] = COLOR_GREEN
            else: result[y, x] = COLOR_BLUE

# Apply glasses thin black outline:
# Outline is drawn where glasses edge borders non-glasses foreground or background
for y in range(h):
    for x in range(w):
        if glasses_edge[y, x] and fg_mask[y, x]:
            # If at the boundary of glasses_mask
            # Check 3x3 neighborhood: does it have both glasses and non-glasses?
            patch = glasses_mask[max(0, y-1):min(h, y+2), max(0, x-1):min(w, x+2)]
            if np.any(patch) and not np.all(patch):
                result[y, x] = COLOR_BLACK

# Verify exact colors present:
u_colors, counts = np.unique(result[fg_mask], axis=0, return_counts=True)
print("\nUnique foreground colors in result:")
for c, cnt in zip(u_colors, counts):
    hex_code = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"RGBA: {c}, Hex: {hex_code}, Count: {cnt}")

# Save full rendered turtle
Image.fromarray(result).save('scripts/turtle_5color_test.png')

# Save head crop and chest crop for inspection
Image.fromarray(result[260:750, 260:1100]).save('scripts/turtle_head_5color.png')
Image.fromarray(result[700:1750, 400:1000]).save('scripts/turtle_chest_5color.png')

print("All 5-color test images saved successfully!")
