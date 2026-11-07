import subprocess
import numpy as np
from PIL import Image
import io

# Get previous commit's Turtle_clean.png
cmd = ["git", "show", "HEAD~1:assets/Turtle_clean.png"]
p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
prev_img = Image.open(io.BytesIO(p.stdout)).convert('RGBA')
prev_arr = np.array(prev_img)

# Crop the eye region:
# Eye center is roughly around x=650, y=550 (in full coords: y in [450, 680], x in [600, 750])
crop_eye_prev = prev_arr[450:680, 600:750]
Image.fromarray(crop_eye_prev).save('scripts/eye_prev.png')

# Current eye
curr_img = Image.open('assets/Turtle_clean.png').convert('RGBA')
curr_arr = np.array(curr_img)
crop_eye_curr = curr_arr[450:680, 600:750]
Image.fromarray(crop_eye_curr).save('scripts/eye_curr.png')

# Original Turtle.png eye
orig_img = Image.open('assets/Turtle_clean.jpg').convert('RGBA')
orig_arr = np.array(orig_img)
crop_eye_orig = orig_arr[450:680, 600:750]
Image.fromarray(crop_eye_orig).save('scripts/eye_orig_jpg.png')

print("Eye crops saved.")
