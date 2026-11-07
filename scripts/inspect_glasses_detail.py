import cv2
import numpy as np
from PIL import Image

# Load current image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Head region: y: 260 to 750, x: 260 to 1100
# Let's inspect the glasses pixels exactly
# The grey pixels of the glasses frame are located in this region
head = arr[260:750, 260:1100].copy()

# Masks in head:
r, g, b, a = head[:, :, 0], head[:, :, 1], head[:, :, 2], head[:, :, 3]

# Frame is greyish: |r - g| < 20, |g - b| < 20, 50 < r < 160, a > 128
is_frame_grey = (a > 128) & (np.abs(r.astype(int) - g.astype(int)) < 20) & (np.abs(r.astype(int) - b.astype(int)) < 20) & (r > 40) & (r < 165)

# Also there are anti-aliased or slightly darker/lighter frame edge pixels
# Let's inspect a crop of the nose bridge and right frame
bridge_crop = head[200:350, 100:350].copy()
Image.fromarray(bridge_crop).save('scripts/glasses_bridge_orig.png')

print(f"Detected grey frame pixels: {np.count_nonzero(is_frame_grey)}")
