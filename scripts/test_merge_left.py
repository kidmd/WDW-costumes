import cv2
import numpy as np
from PIL import Image

# Load test3
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Masks for 20, 24, 26, 28
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
is_black = (a > 128) & (r < 60) & (g < 70) & (b < 80)
fg_nonblack = ((~is_black) & (a > 128)).astype(np.uint8) * 255

h, w = arr.shape[:2]

def get_mask(seed_pt):
    mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = fg_nonblack.copy()
    cv2.floodFill(filled, mask, seed_pt, 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
    return (filled == 128)

mask_20 = get_mask((591, 1164))
mask_24 = get_mask((554, 1257))
mask_26 = get_mask((564, 1310))
mask_28 = get_mask((750, 1503))

C_YELLOW = [236, 203, 46, 255]
C_BLACK = [17, 22, 29, 255]

# Merge 20, 24, 26 and the internal lines into one solid yellow panel
test4 = arr.copy()
test4[mask_20] = C_YELLOW
test4[mask_24] = C_YELLOW
test4[mask_26] = C_YELLOW
test4[mask_28] = C_YELLOW

# Fill internal lines between 20, 24, 26 with yellow
# The internal lines are located between x: 540 to 600, y: 1130 to 1350
# We can find all black pixels in this box that are NOT the outer contour and NOT the tie boundary
tie_mask = get_mask((637, 1323)) # tie mask
# Dilate tie mask slightly to protect tie border
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
tie_border = cv2.dilate(tie_mask.astype(np.uint8), kernel) > 0

# Outer contour is at the boundary of alpha > 128
# Erode alpha to get outer border
alpha_mask = (a > 128).astype(np.uint8)
alpha_erode = cv2.erode(alpha_mask, kernel) > 0
outer_border = (alpha_mask > 0) & (~alpha_erode)

# Any black pixel inside x: 545 to 610, y: 1140 to 1340 that is NOT outer border and NOT tie border becomes yellow!
box_mask = np.zeros_like(is_black)
box_mask[1140:1340, 545:610] = True

internal_lines = box_mask & is_black & (~outer_border) & (~tie_border)
test4[internal_lines] = C_YELLOW

# Also smooth the outer border at the notch (x: 520 to 545, y: 1140 to 1230)
# Let's inspect the crop
sub4 = test4[1100:1400, 500:650].copy()
Image.fromarray(sub4).save('scripts/sub_left_merged.png')

# Also whole chest view
chest4 = test4[700:1750, 400:1000].copy()
Image.fromarray(chest4).save('scripts/chest_merged.png')
print("Saved sub_left_merged and chest_merged.")
