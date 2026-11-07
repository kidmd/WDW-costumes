import cv2
import numpy as np
from PIL import Image

# Load image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Palettes:
C_YELLOW = [236, 203, 46, 255] # Standard yellow
C_RED = [216, 29, 23, 255]     # Standard red
C_BLUE = [41, 64, 98, 255]     # Shell blue / glasses blue
C_GREEN = [33, 101, 46, 255]   # Shell green
C_BLACK = [17, 22, 29, 255]    # Outline black

# Load the region labels from previous script
# Let's inspect regions in the front
# Regions 24, 26, 28 in front_regions_annotated.png
# Let's verify their coordinates from centroids:
# 24: Center=(553.7, 1257.3)
# 26: Center=(563.6, 1310.1)
# 28: Center=(749.4, 1503.6)
# 31: Center=(822.0, 1618.4)

# Let's do flood fill on non-black foreground to get exact masks for:
# - Region 24 (point 554, 1257)
# - Region 26 (point 564, 1310)
# - Region 28 (point 750, 1503)
# - Region 31 (point 822, 1618)

r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
is_black = (a > 128) & (r < 60) & (g < 70) & (b < 80)
fg_nonblack = ((~is_black) & (a > 128)).astype(np.uint8) * 255

h, w = arr.shape[:2]

def get_mask(seed_pt):
    mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = fg_nonblack.copy()
    cv2.floodFill(filled, mask, seed_pt, 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
    return (filled == 128)

mask_24 = get_mask((554, 1257))
mask_26 = get_mask((564, 1310))
mask_28 = get_mask((750, 1503))
mask_31 = get_mask((822, 1618))

print(f"Mask 24 pixels: {np.count_nonzero(mask_24)}")
print(f"Mask 26 pixels: {np.count_nonzero(mask_26)}")
print(f"Mask 28 pixels: {np.count_nonzero(mask_28)}")
print(f"Mask 31 pixels: {np.count_nonzero(mask_31)}")

# Render test with 24, 26, 28 turned yellow
test1 = arr.copy()
test1[mask_24] = C_YELLOW
test1[mask_26] = C_YELLOW
test1[mask_28] = C_YELLOW

# What about 31? If 31 is blue (shell bottom) vs yellow (shirt hem)
test1_crop = test1[700:1750, 400:1000]
Image.fromarray(test1_crop).save('scripts/front_yellow_test1.png')

# Also test with 31 turned yellow as well
test2 = test1.copy()
test2[mask_31] = C_YELLOW
test2_crop = test2[700:1750, 400:1000]
Image.fromarray(test2_crop).save('scripts/front_yellow_test2.png')

print("Saved front_yellow_test1 and test2.")
