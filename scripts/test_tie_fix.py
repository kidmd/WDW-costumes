import cv2
import numpy as np
from PIL import Image

# Load original
orig = np.array(Image.open('assets/Turtle_clean.png'))
r, g, b, a = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2], orig[:, :, 3]
fg_mask = a > 128

# Find the tie knot and tie body masks
# Red pixels in the tie area: y in [1000, 1500], x in [600, 720]
# In the original, red tie has high R and low G, B
is_red_raw = (r > 120) & (g < 50) & (b < 50) & fg_mask

# Close the red mask slightly to fill right up to the black outline
k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
is_red_closed = cv2.morphologyEx(is_red_raw.astype(np.uint8), cv2.MORPH_CLOSE, k3) > 0

# Mouth is y < 950, tie is y >= 950
is_mouth = is_red_closed & (np.arange(orig.shape[0])[:, None] < 950)
is_tie = is_red_closed & (np.arange(orig.shape[0])[:, None] >= 950)

# Dilate tie by 1px so it meets the black outline with zero gap
is_tie_dilated = cv2.dilate(is_tie.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))) > 0

# Check crop
tie_crop = np.zeros((400, 120, 4), dtype=np.uint8)
tie_crop[is_tie[1000:1400, 600:720]] = [216, 29, 23, 255]
tie_crop[~is_tie[1000:1400, 600:720]] = [236, 203, 46, 255]
Image.fromarray(tie_crop).save('scripts/test_tie_fill.png')
print("Tie fill tested.")
