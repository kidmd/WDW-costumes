import subprocess
import numpy as np
from PIL import Image
import io
import cv2

# Load previous commit's image
cmd = ["git", "show", "HEAD~1:assets/Turtle_clean.png"]
p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
prev_img = Image.open(io.BytesIO(p.stdout)).convert('RGBA')
prev_arr = np.array(prev_img)

# Load current clean image
curr_img = Image.open('assets/Turtle_clean.png').convert('RGBA')
curr_arr = np.array(curr_img)

C_BLUE = np.array([41, 64, 98, 255], dtype=np.uint8)

# Mask of blue eye from previous image
prev_r, prev_g, prev_b, prev_a = prev_arr[:, :, 0], prev_arr[:, :, 1], prev_arr[:, :, 2], prev_arr[:, :, 3]
is_prev_blue_eye = (prev_a > 128) & (prev_b > 120) & (prev_b > prev_r * 1.3)

# Option A: Exact previous blue eye mask filled with C_BLUE
optA = curr_arr.copy()
optA[is_prev_blue_eye] = C_BLUE

# Option B: Entire eye teardrop inside the black outline filled with C_BLUE
# Inside eye teardrop: seed fill from inside the eye teardrop
# Center of eye is (650, 560)
h, w = curr_arr.shape[:2]
mask = np.zeros((h + 2, w + 2), np.uint8)
# Black lines of current
is_black = (curr_arr[:, :, 3] > 128) & (curr_arr[:, :, 0] < 50) & (curr_arr[:, :, 1] < 50) & (curr_arr[:, :, 2] < 50)
fill_canvas = ((~is_black) & (curr_arr[:, :, 3] > 128)).astype(np.uint8) * 255

cv2.floodFill(fill_canvas, mask, (650, 560), 128, flags=4 | (255 << 8) | cv2.FLOODFILL_FIXED_RANGE)
full_eye_mask = (fill_canvas == 128)

optB = curr_arr.copy()
optB[full_eye_mask] = C_BLUE

# Save eye crops of both
Image.fromarray(optA[450:680, 600:750]).save('scripts/eye_optA_pupil.png')
Image.fromarray(optB[450:680, 600:750]).save('scripts/eye_optB_full.png')

# Save head crops of both
Image.fromarray(optA[260:750, 260:1100]).save('scripts/head_optA.png')
Image.fromarray(optB[260:750, 260:1100]).save('scripts/head_optB.png')

print(f"Option A pupil pixels: {np.count_nonzero(is_prev_blue_eye)}")
print(f"Option B full eye pixels: {np.count_nonzero(full_eye_mask)}")
