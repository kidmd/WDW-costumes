import cv2
import numpy as np
from PIL import Image

full = Image.open('scripts/Turtle_clean_5color.png')
arr = np.array(full)

# Overview
w, h = full.size
scale = 800 / w
small = full.resize((800, int(h * scale)), Image.NEAREST)
small.save('scripts/final_overview.png')

# Head crop
head = arr[260:750, 260:1100]
Image.fromarray(head).save('scripts/final_head.png')

# Chest crop
chest = arr[700:1750, 400:1000]
Image.fromarray(chest).save('scripts/final_chest.png')

print("Final crops saved.")
