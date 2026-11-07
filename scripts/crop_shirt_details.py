import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's crop the whole chest / shirt / tie area: Y: 800 to 1700, X: 400 to 1100
chest = arr[800:1700, 400:1100]
Image.fromarray(chest).save('scripts/chest_crop.png')

# Left side of tie (viewer's left): Y: 850 to 1250, X: 450 to 750
left_side = arr[850:1250, 450:750]
Image.fromarray(left_side).save('scripts/shirt_left_side.png')

# Right side of tie (viewer's right): Y: 850 to 1700, X: 650 to 1050
right_side = arr[850:1700, 650:1050]
Image.fromarray(right_side).save('scripts/shirt_right_side.png')

print("Crops saved.")
