import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's save a downscaled version with coordinate grid to artifact or scripts
# Image size is (1888, 2262) (H=1888, W=2262)
# Let's save small crops of interest:
# Head region: Y: 250 to 900, X: 400 to 1200
head = arr[250:900, 400:1200]
Image.fromarray(head).save('scripts/crop_head.png')

# Shirt region: Y: 800 to 1600, X: 300 to 1200
shirt = arr[800:1600, 300:1200]
Image.fromarray(shirt).save('scripts/crop_shirt.png')

# Entire turtle with grid
grid_img = arr.copy()
# Draw grid every 200px
for y in range(0, arr.shape[0], 200):
    cv2.line(grid_img, (0, y), (arr.shape[1], y), (255, 0, 255, 255), 2)
    cv2.putText(grid_img, str(y), (10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255, 255), 2)
for x in range(0, arr.shape[1], 200):
    cv2.line(grid_img, (x, 0), (x, arr.shape[0]), (255, 0, 255, 255), 2)
    cv2.putText(grid_img, str(x), (x + 5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255, 255), 2)

# Downscale grid_img to 800w for quick inspection
scale = 800 / arr.shape[1]
grid_small = cv2.resize(grid_img, (800, int(arr.shape[0] * scale)))
Image.fromarray(grid_small).save('scripts/turtle_overview_grid.png')
print("Overview and crops generated.")
