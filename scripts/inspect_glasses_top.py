import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

is_grey = (a > 128) & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 40) & (r < 175)
is_grey_head = np.zeros_like(is_grey)
is_grey_head[260:750, 260:920] = is_grey[260:750, 260:920]

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grey_head.astype(np.uint8), connectivity=8)
comp1 = (labels == 1)

# Let's see where y < 380 in comp1 connects to y >= 380
y_idx, x_idx = np.where(comp1)
print(f"Total comp1 pixels: {len(y_idx)}")
print(f"y < 365 count: {np.count_nonzero(y_idx < 365)}")

# Let's save a crop of y: 260 to 420, x: 500 to 750 showing comp1
top_crop = arr[260:420, 500:750].copy()
top_crop[comp1[260:420, 500:750]] = [255, 0, 255, 255]
Image.fromarray(top_crop).save('scripts/glasses_top_junction.png')
print("Top junction saved.")
