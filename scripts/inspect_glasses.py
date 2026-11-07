import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Head region: Y: 260 to 750, X: 350 to 1100
glasses_crop = arr[260:750, 350:1100].copy()

# Find unique colors in glasses region
fg = glasses_crop[glasses_crop[:, :, 3] > 0]
unique, counts = np.unique(fg[:, :3], axis=0, return_counts=True)
print("Glasses region colors:")
for i in np.argsort(-counts)[:10]:
    c = unique[i]
    print(f"RGB: {c}, Hex: #{c[0]:02x}{c[1]:02x}{c[2]:02x}, Count: {counts[i]}")

# Find pixels that belong to the glasses frame
# The frames are grey/brownish: R~90-120, G~85-115, B~80-110, or R~G~B
# Let's find mask of grey frame
r, g, b = glasses_crop[:, :, 0], glasses_crop[:, :, 1], glasses_crop[:, :, 2]
a = glasses_crop[:, :, 3]
is_grey = (a > 128) & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 60) & (r < 160)
print(f"Grey frame pixels count: {np.count_nonzero(is_grey)}")

# Save an image highlighting the grey frame
highlight = glasses_crop.copy()
highlight[is_grey] = [255, 0, 255, 255] # Magenta highlight
Image.fromarray(highlight).save('scripts/glasses_highlighted.png')
print("Glasses highlighted saved.")
