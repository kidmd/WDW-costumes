import cv2
import numpy as np
from PIL import Image

img_orig = Image.open('assets/Turtle.png').convert('RGBA')
arr_orig = np.array(img_orig)
# Turtle.png size: let's check size
print("Turtle.png size:", arr_orig.shape)

# Let's save chest crop of Turtle.png
# Let's find scale between Turtle.png and Turtle_clean.png
# Turtle_clean is 1888 x 2262. Turtle.png is 1206 x 1444 (about 0.638 scale)
scale_y = arr_orig.shape[0] / 1888
scale_x = arr_orig.shape[1] / 2262

y1, y2 = int(800 * scale_y), int(1700 * scale_y)
x1, x2 = int(400 * scale_x), int(1100 * scale_x)

chest_orig = arr_orig[y1:y2, x1:x2]
Image.fromarray(chest_orig).save('scripts/chest_orig.png')
print("Saved chest_orig.png")
