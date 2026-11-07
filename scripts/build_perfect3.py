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
COLOR_BLACK  = np.array([17, 22, 29, 255], dtype=np.uint8)
COLOR_YELLOW = np.array([236, 203, 46, 255], dtype=np.uint8)
COLOR_RED    = np.array([216, 29, 23, 255], dtype=np.uint8)
COLOR_GREEN  = np.array([33, 101, 46, 255], dtype=np.uint8)
COLOR_BLUE   = np.array([41, 64, 98, 255], dtype=np.uint8)

# Linework: dark pixels
# If r < 75, g < 80, b < 90, it's black
is_black = fg & (r < 75) & (g < 80) & (b < 90)

# Red regions: mouth & tie
# Red has R noticeably higher than G and B
is_red_core = fg & (r > 120) & (g < 65) & (b < 65)
# Dilate red core to fill all anti-aliased edges right up to the black outline
k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
is_red_dilated = cv2.dilate(is_red_core.astype(np.uint8), k3) > 0
# Any pixel in dilated red that is NOT black outline is pure RED
is_red = fg & is_red_dilated & (~is_black)

# Glasses
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

# Front shirt regions
fg_nonblack = (fg & (~is_black) & (~is_red) & (~glasses_clean)).astype(np.uint8) * 255
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

# Internal black lines between 20, 24, 26
tie_dilated = cv2.dilate(is_red.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
alpha_erode = cv2.erode(fg.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
outer_border = fg & (~alpha_erode)
box_left = np.zeros((h, w), dtype=bool)
box_left[1130:1350, 540:620] = True
internal_left_lines = box_left & is_black & (~outer_border) & (~tie_dilated)

streak_mask = np.zeros((h, w), dtype=bool)
streak_mask[1080:1180, 715:745] = True
green_streak = streak_mask & (g > 60) & (r < 70)

front_shirt_mask = mask_20 | mask_24 | mask_26 | mask_28 | mask_23 | mask_21 | internal_left_lines | green_streak

# Feet to Green
is_lime_feet = fg & (g > 130) & (r > 80) & (r < 185) & (b < 115)

# Shell original colors
is_orig_blue = fg & (b > 60) & (r < 80) & (g < 90) & (~front_shirt_mask)
is_orig_green = fg & (g > 65) & (r < 90) & (b < 90) & (~front_shirt_mask)

# Pupil
is_pupil = fg & is_head & (b > 65) & (r < 65) & (g < 80) & (~glasses_clean) & (~glasses_outline)

# Assembly
out = np.zeros((h, w, 4), dtype=np.uint8)

# Default to yellow
out[fg] = COLOR_YELLOW

# Shell
out[is_orig_blue] = COLOR_BLUE
out[is_orig_green] = COLOR_GREEN

# Feet
out[is_lime_feet] = COLOR_GREEN

# Front shirt
out[front_shirt_mask] = COLOR_YELLOW

# Glasses
out[glasses_clean] = COLOR_BLUE
out[is_pupil] = COLOR_BLUE

# Red mouth and tie
out[is_red] = COLOR_RED

# Black outlines
out[is_black] = COLOR_BLACK
out[glasses_outline] = COLOR_BLACK

# Verify exact colors present:
u_colors, counts = np.unique(out[fg], axis=0, return_counts=True)
print("\nFinal Unique Colors:")
for c, cnt in zip(u_colors, counts):
    hex_code = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"RGBA: {c}, Hex: {hex_code}, Count: {cnt}")

assert len(u_colors) == 5, f"Expected 5 colors, got {len(u_colors)}"

Image.fromarray(out).save('scripts/Turtle_clean_perfect3.png')

# Save crops
chest = out[700:1750, 400:1000]
Image.fromarray(chest).save('scripts/perfect3_chest.png')
neck = out[750:1050, 700:900]
Image.fromarray(neck).save('scripts/perfect3_neck.png')
head = out[260:750, 260:1100]
Image.fromarray(head).save('scripts/perfect3_head.png')

print("All perfect3 images saved.")
