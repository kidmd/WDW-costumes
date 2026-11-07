import cv2
import numpy as np
from PIL import Image

orig_img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(orig_img)
h, w = arr.shape[:2]

alpha = arr[:, :, 3]
fg = alpha > 128
r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# Exact 5 colors
C_BLACK  = np.array([17, 22, 29, 255], dtype=np.uint8)
C_YELLOW = np.array([236, 203, 46, 255], dtype=np.uint8)
C_RED    = np.array([216, 29, 23, 255], dtype=np.uint8)
C_GREEN  = np.array([33, 101, 46, 255], dtype=np.uint8)
C_BLUE   = np.array([41, 64, 98, 255], dtype=np.uint8)

# 1. Base classification into the natural color families:
# In the original image:
# Red family (tie & mouth): high R, low G, low B
is_red_family = fg & (r > 60) & (r.astype(int) > g.astype(int) * 1.5) & (r.astype(int) > b.astype(int) * 1.5)

# Blue family (shell grid, eye pupil): high B relative to R & G, or dark navy
is_blue_family = fg & (b > 50) & (b.astype(int) >= r.astype(int)) & (b.astype(int) >= g.astype(int) - 10) & (~is_red_family)

# Green family (shell plates, belly plates, feet): high G relative to R & B
is_green_family = fg & (g > 50) & (g.astype(int) > r.astype(int)) & (g.astype(int) > b.astype(int) - 5) & (~is_red_family) & (~is_blue_family)

# Yellow family (head, neck, shirt): high R and G, low B
is_yellow_family = fg & (~is_red_family) & (~is_blue_family) & (~is_green_family)

# Glasses frame detection (grey in head region)
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

# Thin black outline around glasses
glasses_dilated = cv2.dilate(glasses_clean.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
glasses_outline = glasses_dilated & (~glasses_clean) & fg

# Front yellow shirt:
# Detect the regions in front
fg_nonblack = (fg & (r > 60) & (g > 60) & (~glasses_clean)).astype(np.uint8) * 255
def get_mask(seed_pt):
    mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = fg_nonblack.copy()
    cv2.floodFill(filled, mask, seed_pt, 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
    return (filled == 128)

mask_20 = get_mask((591, 1164))
mask_24 = get_mask((554, 1257))
mask_26 = get_mask((564, 1310))
mask_28 = get_mask((750, 1503))
mask_23 = get_mask((710, 1281))
mask_21 = get_mask((828, 1335))

# Internal divider lines on left
box_left = np.zeros((h, w), dtype=bool)
box_left[1130:1350, 540:620] = True
is_dark = fg & (r < 65) & (g < 70) & (b < 80)
tie_dilated = cv2.dilate(is_red_family.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
alpha_erode = cv2.erode(fg.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
outer_border = fg & (~alpha_erode)
internal_left_lines = box_left & is_dark & (~outer_border) & (~tie_dilated)

streak_mask = np.zeros((h, w), dtype=bool)
streak_mask[1080:1180, 715:745] = True
green_streak = streak_mask & (g > 60) & (r < 70)

front_shirt_mask = mask_20 | mask_24 | mask_26 | mask_28 | mask_23 | mask_21 | internal_left_lines | green_streak

# Assemble final array
out = np.zeros((h, w, 4), dtype=np.uint8)

# 1. Yellow family
# If brightness < 80, it's black outline. Else yellow.
is_yellow_fill = is_yellow_family & ((r.astype(int) + g.astype(int)) >= 150)
is_yellow_line = is_yellow_family & (~is_yellow_fill)
out[is_yellow_fill] = C_YELLOW
out[is_yellow_line] = C_BLACK

# 2. Red family (tie & mouth)
# If brightness < 90, it's black outline. Else red.
is_red_fill = is_red_family & (r >= 110)
is_red_line = is_red_family & (~is_red_fill)
out[is_red_fill] = C_RED
out[is_red_line] = C_BLACK

# 3. Green family (shell plates & feet)
# If brightness < 70, it's black outline. Else green.
is_green_fill = is_green_family & (g >= 70)
is_green_line = is_green_family & (~is_green_fill)
out[is_green_fill] = C_GREEN
out[is_green_line] = C_BLACK

# 4. Blue family (shell ribs & pupil)
# If brightness < 60, it's black outline. Else blue.
is_blue_fill = is_blue_family & (b >= 60)
is_blue_line = is_blue_family & (~is_blue_fill)
out[is_blue_fill] = C_BLUE
out[is_blue_line] = C_BLACK

# 5. Overrides:
# Feet (all feet converted to Green)
is_feet = fg & (np.arange(h)[:, None] >= 1540) & (
    (np.arange(w)[None, :] <= 660) | 
    ((np.arange(w)[None, :] >= 1000) & (np.arange(w)[None, :] <= 1350)) |
    (np.arange(w)[None, :] >= 1700)
) & (is_green_fill | is_yellow_fill | (g > 100))
out[is_feet] = C_GREEN

# Front shirt is solid Yellow
out[front_shirt_mask] = C_YELLOW

# Glasses frame is solid Blue
out[glasses_clean] = C_BLUE

# Glasses outline is Black
out[glasses_outline] = C_BLACK

# Verify exact colors present:
u_colors, counts = np.unique(out[fg], axis=0, return_counts=True)
print("\nFinal Unique Colors:")
for c, cnt in zip(u_colors, counts):
    hex_code = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"RGBA: {c}, Hex: {hex_code}, Count: {cnt}")

assert len(u_colors) == 5, f"Expected 5 colors, got {len(u_colors)}"

# Save final image
Image.fromarray(out).save('scripts/Turtle_clean_perfect.png')
print("Successfully generated Turtle_clean_perfect.png!")
