import os
import shutil
import numpy as np
from PIL import Image

img = Image.open('scripts/honor_america_4color_clean.png')
arr = np.array(img)

# Verify strict 4-color compliance
fg = arr[:, :, 3] > 0
u, cnts = np.unique(arr[fg], axis=0, return_counts=True)
print(f"Total foreground pixels: {np.count_nonzero(fg)}")
print(f"Unique foreground colors: {len(u)}")
assert len(u) == 4, f"Expected 4 colors, got {len(u)}"

for col, cnt in zip(u, cnts):
    hex_c = '#{:02x}{:02x}{:02x}'.format(col[0], col[1], col[2])
    print(f"  {col} ({hex_c}): {cnt} px ({cnt/np.count_nonzero(fg)*100:.2f}%)")

target_paths = [
    'assets/honor_america_eagle.png',
    'assets/to_honor_america.png',
    'simulator/assets/honor_america_eagle.png',
    'simulator/assets/to_honor_america.png',
]

for p in target_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print(f"Saved: {p}")

# Save review artifacts
artifact_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\ba8699af-4574-4f1e-9678-f6f40a0f19fe"
img.save(os.path.join(artifact_dir, "honor_america_4color_final.png"))
shutil.copyfile("scripts/honor_america_checker_verify.png", os.path.join(artifact_dir, "honor_america_checkerboard.png"))

# Close-up 1: Marquee Sign & Cascading Starfield Canton
marquee_crop = Image.fromarray(arr[430:880, 15:680])
marquee_crop.save(os.path.join(artifact_dir, "honor_america_marquee_detail.png"))

# Close-up 2: Fireworks & Towering Bald Eagle
eagle_crop = Image.fromarray(arr[20:540, 360:1185])
eagle_crop.save(os.path.join(artifact_dir, "honor_america_eagle_detail.png"))

print("All To Honor America production assets and artifacts deployed successfully!")
