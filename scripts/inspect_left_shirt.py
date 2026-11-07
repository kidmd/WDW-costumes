import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's zoom into x: 500 to 650, y: 1000 to 1250
sub = arr[1000:1250, 500:650].copy()

# Print the colors present in this subregion
u, counts = np.unique(sub.reshape(-1, 4), axis=0, return_counts=True)
print("Colors in left shirt bottom:")
for c, cnt in zip(u, counts):
    print(f"RGBA: {c}, Count: {cnt}")

# Let's save an upscaled pixel view with a grid to see every pixel
scale = 4
sub_large = cv2.resize(sub, (sub.shape[1]*scale, sub.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
for y in range(0, sub.shape[0], 20):
    cv2.line(sub_large, (0, y*scale), (sub_large.shape[1], y*scale), (128, 128, 128, 255), 1)
    cv2.putText(sub_large, str(y+1000), (5, y*scale + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255, 255), 1)
for x in range(0, sub.shape[1], 20):
    cv2.line(sub_large, (x*scale, 0), (x*scale, sub_large.shape[0]), (128, 128, 128, 255), 1)
    cv2.putText(sub_large, str(x+500), (x*scale + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255, 255), 1)

Image.fromarray(sub_large).save('scripts/left_shirt_pixelgrid.png')
print("Pixel grid saved.")
