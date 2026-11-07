import cv2
import numpy as np
from PIL import Image

# Let's inspect the entire turtle and trace the shell seam vs the front
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's look at the front of the turtle from x: 260 to 1100, y: 700 to 1750
front_crop = arr[700:1750, 260:1100].copy()

# Add coordinate grid to front_crop
for y in range(0, front_crop.shape[0], 100):
    cv2.line(front_crop, (0, y), (front_crop.shape[1], y), (0, 255, 255, 255), 1)
    cv2.putText(front_crop, f"y={y+700}", (5, y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255, 255), 1)
for x in range(0, front_crop.shape[1], 100):
    cv2.line(front_crop, (x, 0), (x, front_crop.shape[0]), (0, 255, 255, 255), 1)
    cv2.putText(front_crop, f"x={x+260}", (x+5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255, 255), 1)

Image.fromarray(front_crop).save('scripts/turtle_front_detail.png')
print("Saved turtle_front_detail.png")
