import subprocess
import os
import shutil
import numpy as np
from PIL import Image
import io

print("1. Loading base images...")
# Load previous commit's image to get exact blue pupil mask
cmd = ["git", "show", "HEAD~1:assets/Turtle_clean.png"]
p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
prev_img = Image.open(io.BytesIO(p.stdout)).convert('RGBA')
prev_arr = np.array(prev_img)

# Load current clean image
curr_img = Image.open('assets/Turtle_clean.png').convert('RGBA')
curr_arr = np.array(curr_img)

C_BLACK  = np.array([17, 22, 29, 255], dtype=np.uint8)
C_GREEN  = np.array([33, 101, 46, 255], dtype=np.uint8)
C_BLUE   = np.array([41, 64, 98, 255], dtype=np.uint8)
C_RED    = np.array([216, 29, 23, 255], dtype=np.uint8)
C_YELLOW = np.array([236, 203, 46, 255], dtype=np.uint8)

# Mask of blue eye from previous image
prev_r, prev_g, prev_b, prev_a = prev_arr[:, :, 0], prev_arr[:, :, 1], prev_arr[:, :, 2], prev_arr[:, :, 3]
is_prev_blue_eye = (prev_a > 128) & (prev_b > 120) & (prev_b > prev_r * 1.3)

final_arr = curr_arr.copy()
final_arr[is_prev_blue_eye] = C_BLUE

# Verification
fg = final_arr[:, :, 3] > 0
unique_colors, counts = np.unique(final_arr[fg], axis=0, return_counts=True)
print(f"Total foreground pixels: {np.count_nonzero(fg)}")
print(f"Number of unique colors: {len(unique_colors)}")
assert len(unique_colors) == 5, f"Expected 5 colors, got {len(unique_colors)}"

for c, cnt in zip(unique_colors, counts):
    hex_col = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"  {c} ({hex_col}): {cnt} px ({cnt/np.count_nonzero(fg)*100:.2f}%)")

final_img = Image.fromarray(final_arr)

# Save to all required production paths
target_paths = [
    'assets/Turtle_clean.png',
    'assets/spinning_turtle.png',
    'assets/Turtle.png',
    'simulator/assets/Turtle_clean.png',
    'simulator/assets/spinning_turtle.png',
    'simulator/assets/Turtle.png',
]

for path in target_paths:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    final_img.save(path)
    print(f"Saved: {path}")

# Artifact directory
artifact_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\ba8699af-4574-4f1e-9678-f6f40a0f19fe"
final_img.save(os.path.join(artifact_dir, "turtle_5color_final.png"))

# Save detail crops to artifact dir
eye_crop = Image.fromarray(final_arr[450:680, 600:750])
eye_crop.save(os.path.join(artifact_dir, "turtle_eye_detail.png"))

glasses_crop = Image.fromarray(final_arr[260:750, 260:1100])
glasses_crop.save(os.path.join(artifact_dir, "turtle_glasses_detail.png"))

shirt_crop = Image.fromarray(final_arr[700:1500, 200:1050])
shirt_crop.save(os.path.join(artifact_dir, "turtle_shirt_detail.png"))

print("All production assets and artifacts successfully generated!")
