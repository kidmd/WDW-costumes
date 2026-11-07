import cv2
import numpy as np
from PIL import Image

full = Image.open('scripts/turtle_5color_test.png')
w, h = full.size
scale = 800 / w
small = full.resize((800, int(h * scale)), Image.NEAREST)
small.save('scripts/turtle_5color_overview.png')
print("Overview saved.")
