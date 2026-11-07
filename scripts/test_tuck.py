import cv2
import numpy as np
from PIL import Image

# Load current image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's write helper to test tucking the left shirt
# In left_shirt_pixelgrid.png:
# Collar bottom line ends around x=560, y=1070.
# The untucked flap is y: 1070 to 1170, x: 530 to 625.
# Under it at y: 1170 to 1250 is the blue shell segment ([39, 56, 79]).
# To tuck it in:
# Option 1: Raise the waistline / fill the lower portion of the flap with the blue shell color, 
# so the shirt hem is tucked straight across at y=1100 or y=1120.
# Option 2: The shirt tucks directly into the collar/waist seam, so the shell continues up to the collar seam.
# Option 3: Clean horizontal tuck at y=1120 with a neat black waistband line.

# Let's inspect the exact lines and colors around y=1050 to 1200, x=500 to 650
crop = arr[1020:1220, 520:660].copy()
Image.fromarray(crop).save('scripts/tuck_crop_orig.png')
print("Saved tuck_crop_orig.png")
