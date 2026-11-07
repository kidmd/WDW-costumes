import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's inspect the collar and shirt structure
# Let's save high-res crops with exact coordinates labeled
crop_all_shirt = arr[800:1750, 420:1050].copy()

# Draw grid lines on crop_all_shirt
for y in range(0, crop_all_shirt.shape[0], 100):
    cv2.line(crop_all_shirt, (0, y), (crop_all_shirt.shape[1], y), (0, 255, 255, 255), 1)
    cv2.putText(crop_all_shirt, f"y={y+800}", (5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255, 255), 1)
for x in range(0, crop_all_shirt.shape[1], 100):
    cv2.line(crop_all_shirt, (x, 0), (x, crop_all_shirt.shape[0]), (0, 255, 255, 255), 1)
    cv2.putText(crop_all_shirt, f"x={x+420}", (x+5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255, 255), 1)

Image.fromarray(crop_all_shirt).save('scripts/shirt_grid_highres.png')
print("High-res shirt grid saved.")
