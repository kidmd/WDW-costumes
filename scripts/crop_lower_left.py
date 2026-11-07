import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Crop lower left: Y: 1100 to 1500, X: 400 to 800
lower_left = arr[1100:1500, 400:800]
Image.fromarray(lower_left).save('scripts/shirt_lower_left.png')
