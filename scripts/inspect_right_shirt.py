import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's inspect x: 620 to 760, y: 1000 to 1250
sub_r = arr[1000:1250, 620:760].copy()
scale = 4
sub_r_large = cv2.resize(sub_r, (sub_r.shape[1]*scale, sub_r.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
for y in range(0, sub_r.shape[0], 20):
    cv2.line(sub_r_large, (0, y*scale), (sub_r_large.shape[1], y*scale), (128, 128, 128, 255), 1)
    cv2.putText(sub_r_large, str(y+1000), (5, y*scale + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255, 255), 1)
for x in range(0, sub_r.shape[1], 20):
    cv2.line(sub_r_large, (x*scale, 0), (x*scale, sub_r_large.shape[0]), (128, 128, 128, 255), 1)
    cv2.putText(sub_r_large, str(x+620), (x*scale + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255, 255), 1)

Image.fromarray(sub_r_large).save('scripts/right_shirt_pixelgrid.png')
print("Right pixel grid saved.")
