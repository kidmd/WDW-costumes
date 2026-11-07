import subprocess
import numpy as np
from PIL import Image
import io

cmd = ["git", "show", "HEAD~1:assets/Turtle_clean.png"]
p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
prev_img = Image.open(io.BytesIO(p.stdout)).convert('RGBA')
prev_arr = np.array(prev_img)

# Crop the eye
eye_crop = prev_arr[450:680, 600:750]
r, g, b, a = eye_crop[:, :, 0], eye_crop[:, :, 1], eye_crop[:, :, 2], eye_crop[:, :, 3]

# Pixels that were blue in the eye
is_blue_eye = (b > 120) & (b > r * 1.3)
print(f"Blue pixels in eye: {np.count_nonzero(is_blue_eye)}")

# Print unique colors in the blue pupil
u, counts = np.unique(eye_crop[is_blue_eye], axis=0, return_counts=True)
for c, cnt in zip(u, counts):
    if cnt > 10:
        print(f"RGBA: {c}, count: {cnt}")
