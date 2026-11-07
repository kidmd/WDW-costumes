import cv2
import numpy as np
from PIL import Image

full = Image.open('scripts/Turtle_clean_perfect.png')
arr = np.array(full)

# Overview
w, h = full.size
scale = 800 / w
small = full.resize((800, int(h * scale)), Image.NEAREST)
small.save('scripts/perfect2_overview.png')

# Head
head = arr[260:750, 260:1100]
Image.fromarray(head).save('scripts/perfect2_head.png')

# Chest
chest = arr[700:1750, 400:1000]
Image.fromarray(chest).save('scripts/perfect2_chest.png')

# Neck junction
neck = arr[750:1050, 700:900]
Image.fromarray(neck).save('scripts/perfect2_neck.png')

print("Crops saved.")
