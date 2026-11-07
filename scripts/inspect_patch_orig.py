import cv2
import numpy as np
from PIL import Image

# Load original Turtle.png
img_orig = Image.open('assets/Turtle.png').convert('RGBA')
arr_orig = np.array(img_orig)

# Let's inspect the exact same region in Turtle.png
scale_y = arr_orig.shape[0] / 1888
scale_x = arr_orig.shape[1] / 2262

# Coordinates of Region 7 in Turtle_clean: x in [520, 620], y in [1050, 1220]
x1 = int(520 * scale_x)
x2 = int(620 * scale_x)
y1 = int(1050 * scale_y)
y2 = int(1220 * scale_y)

patch_orig = arr_orig[y1:y2, x1:x2]
Image.fromarray(patch_orig).save('scripts/patch_orig_reg7.png')

# Print colors in patch_orig
print("Colors in original Region 7:")
u, counts = np.unique(patch_orig.reshape(-1, 4), axis=0, return_counts=True)
for c, cnt in zip(u, counts):
    if cnt > 10:
        print(f"RGBA: {c}, count: {cnt}")
