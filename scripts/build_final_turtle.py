import cv2
import numpy as np
from PIL import Image

# Load original Turtle_clean.png
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)
h, w = arr.shape[:2]

# Exact 5 colors
COLOR_BLACK  = np.array([17, 22, 29, 255], dtype=np.uint8)
COLOR_YELLOW = np.array([236, 203, 46, 255], dtype=np.uint8)
COLOR_RED    = np.array([216, 29, 23, 255], dtype=np.uint8)
COLOR_GREEN  = np.array([33, 101, 46, 255], dtype=np.uint8)
COLOR_BLUE   = np.array([41, 64, 98, 255], dtype=np.uint8)

alpha = arr[:, :, 3]
fg_mask = alpha > 128
r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# 1. Black outlines mask
is_black = fg_mask & (r < 65) & (g < 75) & (b < 85)

# 2. Extract clean glasses frame mask:
# Grey frame detection in head region
is_head = np.zeros((h, w), dtype=bool)
is_head[260:750, 260:920] = True
is_grey_frame = is_head & fg_mask & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 40) & (r < 175)

num_l, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grey_frame.astype(np.uint8), connectivity=8)
largest_l = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
glasses_raw = (labels == largest_l)
glasses_raw[:365, :] = False

# Morphological close to bridge any gaps and smooth the frame
k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
glasses_clean = cv2.morphologyEx(glasses_raw.astype(np.uint8), cv2.MORPH_CLOSE, k5)

# Smooth the bridge notch slightly
# Bridge is around x: 470 to 520, y: 520 to 570
bridge_box = np.zeros((h, w), dtype=np.uint8)
bridge_box[520:570, 470:520] = 1
bridge_patch = cv2.morphologyEx((glasses_clean & bridge_box).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
glasses_clean[520:570, 470:520] = bridge_patch[520:570, 470:520]

# Thin black outline around glasses:
# Dilate glasses by 2px, find boundary pixels
glasses_dilated = cv2.dilate(glasses_clean, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
glasses_outline = (glasses_dilated > 0) & (~(glasses_clean > 0)) & fg_mask

# 3. Front shirt regions to turn into solid yellow:
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
mask_23 = get_mask((710, 1281)) # right shirt strip
mask_21 = get_mask((828, 1335)) # right yellow strip/arm

# Dissolve internal black lines between 20, 24, 26 on the left:
tie_mask = get_mask((637, 1323))
tie_border = cv2.dilate(tie_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
outer_border = (fg_mask) & (~cv2.erode(fg_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))))

box_left = np.zeros((h, w), dtype=bool)
box_left[1130:1350, 545:615] = True
internal_left_lines = box_left & is_black & (~outer_border) & (~tie_border)

# Green streak under right collar (around x: 720 to 740, y: 1080 to 1180)
streak_mask = np.zeros((h, w), dtype=bool)
streak_mask[1080:1180, 715:740] = True
green_streak = streak_mask & (g > 70) & (r < 60)

# Combine all front shirt yellow masks
front_yellow_mask = mask_20 | mask_24 | mask_26 | mask_28 | mask_23 | mask_21 | internal_left_lines | green_streak

# 4. Lime feet to Green
is_lime_feet = fg_mask & (g > 140) & (r > 90) & (r < 180) & (b < 110)

# 5. Build clean 5-color quantized array
out = np.zeros((h, w, 4), dtype=np.uint8)

# Head/face mask (no green allowed on head/face)
head_zone = np.zeros((h, w), dtype=bool)
head_zone[:750, :880] = True

# Shirt zone (no green or blue allowed on front shirt)
shirt_zone = np.zeros((h, w), dtype=bool)
shirt_zone[750:1750, :860] = True

for y in range(h):
    for x in range(w):
        if not fg_mask[y, x]:
            continue
            
        # Glasses frame
        if glasses_clean[y, x] > 0:
            out[y, x] = COLOR_BLUE
            continue
            
        # Glasses outline
        if glasses_outline[y, x]:
            out[y, x] = COLOR_BLACK
            continue
            
        # Front yellow shirt
        if front_yellow_mask[y, x]:
            out[y, x] = COLOR_YELLOW
            continue
            
        # Feet
        if is_lime_feet[y, x]:
            out[y, x] = COLOR_GREEN
            continue
            
        # Linework
        if is_black[y, x]:
            out[y, x] = COLOR_BLACK
            continue
            
        cur_r, cur_g, cur_b = r[y, x], g[y, x], b[y, x]
        
        # Red tie & lips
        if cur_r > 155 and cur_g < 75 and cur_b < 75:
            out[y, x] = COLOR_RED
            continue
            
        # In head zone: only Black, Yellow, Red, or Blue (for pupil)
        if head_zone[y, x]:
            if cur_b > 65 and cur_r < 80:
                out[y, x] = COLOR_BLUE
            else:
                out[y, x] = COLOR_YELLOW
            continue
            
        # In shirt zone: only Black, Yellow, or Red (tie)
        if shirt_zone[y, x]:
            out[y, x] = COLOR_YELLOW
            continue
            
        # Shell region: Green plates or Blue matrix
        if cur_g > 65 and cur_r < 90 and cur_b < 90:
            out[y, x] = COLOR_GREEN
        elif cur_b > 60 and cur_r < 80:
            out[y, x] = COLOR_BLUE
        elif cur_r > 160 and cur_g > 140:
            out[y, x] = COLOR_YELLOW
        else:
            # Fallback nearest
            c = np.array([cur_r, cur_g, cur_b], dtype=float)
            d_black = np.linalg.norm(c - COLOR_BLACK[:3])
            d_yellow = np.linalg.norm(c - COLOR_YELLOW[:3])
            d_red = np.linalg.norm(c - COLOR_RED[:3])
            d_green = np.linalg.norm(c - COLOR_GREEN[:3])
            d_blue = np.linalg.norm(c - COLOR_BLUE[:3])
            best = np.argmin([d_black, d_yellow, d_red, d_green, d_blue])
            if best == 0: out[y, x] = COLOR_BLACK
            elif best == 1: out[y, x] = COLOR_YELLOW
            elif best == 2: out[y, x] = COLOR_RED
            elif best == 3: out[y, x] = COLOR_GREEN
            else: out[y, x] = COLOR_BLUE

# Final check of unique foreground colors
u_colors, counts = np.unique(out[fg_mask], axis=0, return_counts=True)
print("\nFinal Unique Foreground Colors:")
for c, cnt in zip(u_colors, counts):
    hex_code = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"RGBA: {c}, Hex: {hex_code}, Count: {cnt}")

assert len(u_colors) == 5, f"Expected 5 colors, found {len(u_colors)}"

# Save final images
Image.fromarray(out).save('scripts/Turtle_clean_5color.png')
print("Successfully generated scripts/Turtle_clean_5color.png!")
