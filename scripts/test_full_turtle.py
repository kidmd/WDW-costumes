import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Find Region 7 mask
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
is_black = (a > 128) & (r < 60) & (g < 70) & (b < 80)
fg_nonblack = ((~is_black) & (a > 128)).astype(np.uint8) * 255

h, w = arr.shape[:2]
mask = np.zeros((h + 2, w + 2), np.uint8)
reg7_fill = fg_nonblack.copy()
cv2.floodFill(reg7_fill, mask, (590, 1120), 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
reg7_mask = (reg7_fill == 128)

turtle_test = arr.copy()
turtle_test[reg7_mask] = [41, 64, 98, 255]

# Save small version of full turtle
scale = 800 / turtle_test.shape[1]
small = cv2.resize(turtle_test, (800, int(turtle_test.shape[0]*scale)))
Image.fromarray(small).save('scripts/turtle_test_full.png')
print("Full turtle test saved.")
