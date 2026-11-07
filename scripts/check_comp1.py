import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

# Grey condition
is_grey = (a > 128) & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 40) & (r < 175)

is_grey_head = np.zeros_like(is_grey)
is_grey_head[260:750, 260:920] = is_grey[260:750, 260:920]

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grey_head.astype(np.uint8), connectivity=8)

# Component 1
comp1 = (labels == 1)

check = arr[260:750, 260:1100].copy()
check[comp1[260:750, 260:1100]] = [255, 0, 255, 255]
Image.fromarray(check).save('scripts/comp1_check.png')
print("Component 1 saved.")
