import cv2
import numpy as np
from PIL import Image

# Load image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Find mask of Region 7
# Center of Region 7 is around (591, 1164) in full coords
# Let's use floodFill on a copy of the black line mask to get the exact Region 7 mask!
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
is_black = (a > 128) & (r < 60) & (g < 70) & (b < 80)

# Create a binary image where black lines are 0, and non-black foreground is 255
fg_nonblack = ((~is_black) & (a > 128)).astype(np.uint8) * 255

# Flood fill from inside Region 7: point (590, 1120)
h, w = arr.shape[:2]
mask = np.zeros((h + 2, w + 2), np.uint8)
reg7_fill = fg_nonblack.copy()
cv2.floodFill(reg7_fill, mask, (590, 1120), 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
reg7_mask = (reg7_fill == 128)

print(f"Region 7 pixel count: {np.count_nonzero(reg7_mask)}")

# Let's also find Region 11 and 12 (the blue patches under Region 7)
blue_color = [41, 64, 98, 255] # shell blue
black_color = [17, 22, 29, 255]

# -------------------------------------------------------------
# Approach 1: Fully tucked (Region 7 filled with shell blue)
# -------------------------------------------------------------
app1 = arr.copy()
app1[reg7_mask] = blue_color
# Now Region 5 (collar) sits directly on the blue shell!
Image.fromarray(app1[750:1450, 420:800]).save('scripts/tuck_app1.png')

# -------------------------------------------------------------
# Approach 2: Clean horizontal waistband tuck at y=1100
# -------------------------------------------------------------
app2 = arr.copy()
# Above y=1100 remains yellow. Below y=1100 in Region 7 becomes blue.
app2[reg7_mask & (np.arange(h)[:, None] >= 1100)] = blue_color
# Draw clean black waistband line across Region 7 at y=1100
for x in range(540, 620):
    if reg7_mask[1100, x] or reg7_mask[1099, x] or reg7_mask[1101, x]:
        cv2.line(app2, (x-2, 1100), (x+2, 1100), black_color, 4)
Image.fromarray(app2[750:1450, 420:800]).save('scripts/tuck_app2.png')

# -------------------------------------------------------------
# Approach 3: Tucked at y=1130 (lower tuck, matching tie knot base)
# -------------------------------------------------------------
app3 = arr.copy()
app3[reg7_mask & (np.arange(h)[:, None] >= 1130)] = blue_color
for x in range(540, 620):
    if reg7_mask[1130, x] or reg7_mask[1129, x] or reg7_mask[1131, x]:
        cv2.line(app3, (x-2, 1130), (x+2, 1130), black_color, 4)
Image.fromarray(app3[750:1450, 420:800]).save('scripts/tuck_app3.png')

# -------------------------------------------------------------
# Approach 4: Follow the natural diagonal seam of the collar/shell 
# -------------------------------------------------------------
# Make the outer bulging flap blue, leaving a neat, narrow tucked shirt strip next to the tie
app4 = arr.copy()
# If x < 575 in Region 7, it's the bulging outer flap -> make it shell blue
app4[reg7_mask & (np.arange(w)[None, :] < 575)] = blue_color
# Draw clean boundary line at x=575 connecting collar to lower boundary
cv2.line(app4, (565, 1070), (575, 1170), black_color, 4)
Image.fromarray(app4[750:1450, 420:800]).save('scripts/tuck_app4.png')

print("All 4 approaches rendered.")
