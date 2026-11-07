import cv2
import numpy as np
from PIL import Image

img_path = 'assets/Turtle_clean.png'
img = Image.open(img_path).convert('RGBA')
arr = np.array(img)

print(f"Image shape: {arr.shape}")
alpha = arr[:, :, 3]
fg_mask = alpha > 128
print(f"Foreground pixels: {np.count_nonzero(fg_mask)}")

# Find bounding box of foreground
y_indices, x_indices = np.where(fg_mask)
ymin, ymax = y_indices.min(), y_indices.max()
xmin, xmax = x_indices.min(), x_indices.max()
print(f"Foreground bbox: x=[{xmin}, {xmax}], y=[{ymin}, {ymax}], width={xmax-xmin}, height={ymax-ymin}")

# Save cropped regions to inspect: head/face (top 40%), torso/shirt (middle 40%)
head_crop = img.crop((xmin, ymin, xmax, int(ymin + (ymax-ymin)*0.45)))
head_crop.save('scripts/turtle_head.png')

body_crop = img.crop((xmin, int(ymin + (ymax-ymin)*0.3), xmax, int(ymin + (ymax-ymin)*0.8)))
body_crop.save('scripts/turtle_body.png')

print("Cropped regions saved.")
