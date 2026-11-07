import cv2
import numpy as np
from PIL import Image

# Load image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's inspect head region and glasses mask
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

# Grey glasses frame mask:
# Grey is characterized by:
# 1) y in [260, 750], x in [260, 1100]
# 2) a > 128
# 3) abs(r-g) < 22 and abs(r-b) < 22 and 40 < r < 180
# 4) Not black outline (r > 40)
# 5) Not yellow (b < 140, r < 180)
# Let's refine mask using connected components or color range
is_head = np.zeros_like(a, dtype=bool)
is_head[260:750, 260:1100] = True

is_frame = is_head & (a > 128) & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 45) & (r < 175)

# Also there's a small ear/temple piece extending slightly past x=1100
# Let's check bounds
y_f, x_f = np.where(is_frame)
print(f"Glasses frame bbox: x=[{x_f.min()}, {x_f.max()}], y=[{y_f.min()}, {y_f.max()}], pixels={len(x_f)}")

# Let's save a crop of glasses mask to verify it covers the entire frame cleanly
mask_crop = arr[260:750, 260:1100].copy()
mask_crop[is_frame[260:750, 260:1100]] = [255, 0, 255, 255]
Image.fromarray(mask_crop).save('scripts/glasses_mask_check.png')
print("Glasses mask check saved.")
