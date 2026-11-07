import cv2
import numpy as np
from PIL import Image

full = Image.open('scripts/Turtle_clean_final.png')
arr = np.array(full)

# Overview
w, h = full.size
scale = 800 / w
small = full.resize((800, int(h * scale)), Image.NEAREST)
small.save('scripts/perfect_overview.png')

# Head
head = arr[260:750, 260:1100]
Image.fromarray(head).save('scripts/perfect_head.png')

# Chest
chest = arr[700:1750, 400:1000]
Image.fromarray(chest).save('scripts/perfect_chest.png')

# Tie zoom
tie = arr[1000:1450, 580:720]
Image.fromarray(tie).save('scripts/perfect_tie.png')

print("Perfect crops saved.")
