import cv2
import numpy as np
from PIL import Image
import os

jpg = Image.open('assets/Turtle_clean.jpg')
print("JPG size:", jpg.size)
# Save small version of jpg to scripts
jpg.resize((600, int(600 * jpg.size[1] / jpg.size[0]))).save('scripts/turtle_jpg_small.png')

# Also let's inspect the original Turtle.png if it exists
if os.path.exists('assets/Turtle.png'):
    orig = Image.open('assets/Turtle.png')
    orig.resize((600, int(600 * orig.size[1] / orig.size[0]))).save('scripts/turtle_orig_small.png')
