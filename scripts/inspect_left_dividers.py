import cv2
import numpy as np
from PIL import Image

# Load test1
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Masks for 24, 26, 28
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

# Merge 20, 24, 26 into one smooth yellow region
test3 = arr.copy()
test3[mask_20] = C_YELLOW
test3[mask_24] = C_YELLOW
test3[mask_26] = C_YELLOW
test3[mask_28] = C_YELLOW

# Let's inspect the black lines between 20, 24, 26:
# In the region x in [520, 600], y in [1120, 1360], there are black divider lines between 20, 24, 26.
# If we replace the internal black dividers with yellow, but keep the outer boundary line and the tie boundary line!
# Also smooth the outer boundary line:
sub = test3[1100:1400, 500:650].copy()
Image.fromarray(sub).save('scripts/sub_left_dividers.png')
print("Saved sub_left_dividers.png")
