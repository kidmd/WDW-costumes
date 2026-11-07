import cv2
import numpy as np
from PIL import Image

# Load current image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Crop region: y: 1000 to 1250, x: 500 to 650
# In full image coordinates:
# (x, y)
# Let's inspect options:

# Option A: Waistband tuck at y=1120. 
# Below y=1120, any yellow in x in [520, 620] becomes shell blue [41, 64, 98, 255].
# And a clean black waistband border (width ~5-6px) is drawn at y=1120 connecting the outer line to the tie.
optA = arr.copy()
# Find the yellow mask in this region
y_mask = (optA[1000:1250, 500:650, 0] > 200) & (optA[1000:1250, 500:650, 1] > 180) & (optA[1000:1250, 500:650, 2] < 80)
# In full coords:
for y in range(1125, 1200):
    for x in range(520, 620):
        # If it's yellow shirt flap below 1125, turn to shell blue
        if (optA[y, x, 0] > 200 and optA[y, x, 1] > 180 and optA[y, x, 2] < 80):
            optA[y, x] = [41, 64, 98, 255] # shell blue

# Draw black waistband line at y=1122 to 1127 from x=535 to x=610
cv2.line(optA, (535, 1125), (610, 1125), (17, 22, 29, 255), 6)

# Option B: Full collar tuck (shell extends up to collar line)
# Everything in that flap below the collar becomes shell blue
optB = arr.copy()
for y in range(1040, 1200):
    for x in range(520, 620):
        # If below the collar diagonal line and yellow:
        # Collar diagonal goes from (615, 1000) to (560, 1070)
        # Line eq: y - 1000 = (70 / -55) * (x - 615) => y - 1000 = -1.27 * (x - 615) => y > 1000 - 1.27*(x-615)
        if y > (1000 - 1.27 * (x - 615)) and (optB[y, x, 0] > 200 and optB[y, x, 1] > 180 and optB[y, x, 2] < 80):
            optB[y, x] = [41, 64, 98, 255]

# Option C: Gently angled tuck that aligns with the shell scute contour
optC = arr.copy()
# Waistband angled from (535, 1140) to (615, 1115)
for y in range(1060, 1200):
    for x in range(520, 620):
        # Line from (535, 1140) to (615, 1115): slope = (1115 - 1140)/(615 - 535) = -25/80 = -0.3125
        y_line = 1140 - 0.3125 * (x - 535)
        if y > y_line and (optC[y, x, 0] > 200 and optC[y, x, 1] > 180 and optC[y, x, 2] < 80):
            optC[y, x] = [41, 64, 98, 255]
cv2.line(optC, (535, 1140), (615, 1115), (17, 22, 29, 255), 6)

# Save crops of all three
Image.fromarray(optA[1000:1250, 500:660]).save('scripts/tuck_optA.png')
Image.fromarray(optB[1000:1250, 500:660]).save('scripts/tuck_optB.png')
Image.fromarray(optC[1000:1250, 500:660]).save('scripts/tuck_optC.png')

# Also save chest view for each
Image.fromarray(optA[800:1450, 420:800]).save('scripts/chest_optA.png')
Image.fromarray(optB[800:1450, 420:800]).save('scripts/chest_optB.png')
Image.fromarray(optC[800:1450, 420:800]).save('scripts/chest_optC.png')

print("All options saved.")
