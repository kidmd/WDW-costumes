import cv2
import numpy as np
from PIL import Image

head = np.array(Image.open('scripts/crop_head.png'))
# head is Y: [250:900], X: [400:1200]
# Let's add sub-grid to crop_head
grid_head = head.copy()
for y in range(0, head.shape[0], 50):
    cv2.line(grid_head, (0, y), (head.shape[1], y), (255, 0, 255, 255), 1)
    cv2.putText(grid_head, f"y={y+250}", (5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255, 255), 1)
for x in range(0, head.shape[1], 50):
    cv2.line(grid_head, (x, 0), (x, head.shape[0]), (255, 0, 255, 255), 1)
    cv2.putText(grid_head, f"x={x+400}", (x + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255, 255), 1)

Image.fromarray(grid_head).save('scripts/grid_head.png')

# Also shirt: Y: [800:1600], X: [300:1200]
shirt = np.array(Image.open('scripts/crop_shirt.png'))
grid_shirt = shirt.copy()
for y in range(0, shirt.shape[0], 50):
    cv2.line(grid_shirt, (0, y), (shirt.shape[1], y), (255, 0, 255, 255), 1)
    cv2.putText(grid_shirt, f"y={y+800}", (5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255, 255), 1)
for x in range(0, shirt.shape[1], 50):
    cv2.line(grid_shirt, (x, 0), (x, shirt.shape[0]), (255, 0, 255, 255), 1)
    cv2.putText(grid_shirt, f"x={x+300}", (x + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255, 255), 1)

Image.fromarray(grid_shirt).save('scripts/grid_shirt.png')
print("Grids saved.")
