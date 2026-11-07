import numpy as np
from PIL import Image

arr = np.array(Image.open('scripts/Turtle_clean_5color.png'))
# Let's inspect x: 600 to 700, y: 1200 to 1350
crop = arr[1200:1350, 600:700]
u, counts = np.unique(crop.reshape(-1, 4), axis=0, return_counts=True)
print("Tie crop colors:")
for c, cnt in zip(u, counts):
    print(c, cnt)
