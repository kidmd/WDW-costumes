import cv2
import numpy as np
from PIL import Image

# 1. Load original
orig_img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(orig_img)
h, w = arr.shape[:2]

alpha = arr[:, :, 3]
fg = alpha > 128
r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# Exact 5-color palette
C_BLACK  = np.array([17, 22, 29, 255], dtype=np.uint8)
C_YELLOW = np.array([236, 203, 46, 255], dtype=np.uint8)
C_RED    = np.array([216, 29, 23, 255], dtype=np.uint8)
C_GREEN  = np.array([33, 101, 46, 255], dtype=np.uint8)
C_BLUE   = np.array([41, 64, 98, 255], dtype=np.uint8)

# 2. Black linework detection
# Dark pixels in original
is_dark = fg & (r < 70) & (g < 75) & (b < 85)

# 3. Red regions (mouth & tie)
# Flood fill or color threshold
is_red = fg & (r > 130) & (g < 60) & (b < 60)
k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
is_red = cv2.morphologyEx(is_red.astype(np.uint8), cv2.MORPH_CLOSE, k3) > 0

# 4. Glasses detection & smoothing
is_head = np.zeros((h, w), dtype=bool)
is_head[260:750, 260:920] = True
is_grey_frame = is_head & fg & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 40) & (r < 175)

num_l, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grey_frame.astype(np.uint8), connectivity=8)
largest_l = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
glasses_raw = (labels == largest_l)
glasses_raw[:365, :] = False

k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
glasses_clean = cv2.morphologyEx(glasses_raw.astype(np.uint8), cv2.MORPH_CLOSE, k5) > 0

# Smooth bridge
bridge_box = np.zeros((h, w), dtype=np.uint8)
bridge_box[520:570, 470:520] = 1
bridge_patch = cv2.morphologyEx((glasses_clean & bridge_box).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
glasses_clean[520:570, 470:520] = bridge_patch[520:570, 470:520]

# Thin black outline around glasses (2-3px)
glasses_dilated = cv2.dilate(glasses_clean.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
glasses_outline = glasses_dilated & (~glasses_clean) & fg

# 5. Front shirt regions:
# Region helper
fg_nonblack = (fg & (~is_dark) & (~is_red) & (~glasses_clean)).astype(np.uint8) * 255
def get_mask(seed_pt):
    mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = fg_nonblack.copy()
    cv2.floodFill(filled, mask, seed_pt, 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
    return (filled == 128)

mask_20 = get_mask((591, 1164)) # left shirt flap
mask_24 = get_mask((554, 1257)) # left blue notch 1
mask_26 = get_mask((564, 1310)) # left blue notch 2
mask_28 = get_mask((750, 1503)) # green belly plate under tie
mask_23 = get_mask((710, 1281)) # right shirt strip
mask_21 = get_mask((828, 1335)) # right yellow strip/arm

# Left interior black lines
tie_dilated = cv2.dilate(is_red.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
alpha_erode = cv2.erode((fg).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
outer_border = fg & (~alpha_erode)

box_left = np.zeros((h, w), dtype=bool)
box_left[1130:1350, 540:620] = True
internal_left_lines = box_left & is_dark & (~outer_border) & (~tie_dilated)

streak_mask = np.zeros((h, w), dtype=bool)
streak_mask[1080:1180, 715:745] = True
green_streak = streak_mask & (g > 60) & (r < 70)

front_shirt_mask = mask_20 | mask_24 | mask_26 | mask_28 | mask_23 | mask_21 | internal_left_lines | green_streak

# 6. Feet (convert lime green to green)
is_lime_feet = fg & (g > 130) & (r > 80) & (r < 185) & (b < 115)

# 7. Shell plates (green) vs shell ribs (blue)
# Green plates in shell: y in [350, 1600], x > 800
# High green ratio
is_shell_green = fg & (g > 70) & (g > r * 1.1) & (g > b * 1.1) & (np.arange(w)[None, :] > 800) & (~front_shirt_mask)

# 8. Pupil in right eye:
# Center around x=660, y=600
is_pupil = fg & is_head & (b > 65) & (r < 65) & (g < 80) & (~glasses_clean) & (~glasses_outline)

# 9. Assembly
out = np.zeros((h, w, 4), dtype=np.uint8)

# Priority layer 1: Background is transparent (0,0,0,0)
# Priority layer 2: General foreground default (Yellow for head/body, Green for shell plates, Blue for shell ribs)
# Fast vectorized classification:
# Shell ribs:
is_shell = fg & (~front_shirt_mask) & (~is_head) & (np.arange(w)[None, :] >= 780)
# Start with default assignments:
out[fg] = C_YELLOW # Head, neck, shirt default to yellow

# Shell grid defaults to Blue
out[is_shell] = C_BLUE

# Shell green plates
out[is_shell_green] = C_GREEN

# Feet to Green
out[is_lime_feet] = C_GREEN

# Front shirt explicitly Yellow
out[front_shirt_mask] = C_YELLOW

# Glasses frame Blue
out[glasses_clean] = C_BLUE

# Pupil Blue
out[is_pupil] = C_BLUE

# Red mouth and tie
out[is_red] = C_RED

# Black linework on top
out[is_dark] = C_BLACK
out[glasses_outline] = C_BLACK

# Ensure the tie has clean black outline and no yellow halo:
# Tie outline from original:
tie_edge = cv2.dilate(is_red.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))) > 0
tie_outer_edge = tie_edge & (~is_red) & fg
# Where tie borders non-tie, ensure black outline
out[tie_outer_edge & is_dark] = C_BLACK

# Verify 100% strictly 5 foreground colors
u_colors, counts = np.unique(out[fg], axis=0, return_counts=True)
print("Unique foreground colors:")
for c, cnt in zip(u_colors, counts):
    hex_code = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"RGBA: {c}, Hex: {hex_code}, Count: {cnt}")

assert len(u_colors) == 5, f"Expected 5 colors, got {len(u_colors)}"

# Save final result
out_img = Image.fromarray(out)
out_img.save('scripts/Turtle_clean_final.png')
print("Successfully generated scripts/Turtle_clean_final.png")
