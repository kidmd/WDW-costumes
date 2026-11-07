import os
import shutil
import numpy as np
import cv2
from PIL import Image

print("1. Processing Turtle image to remove extra shirt lines...")
arr = np.array(Image.open('assets/Turtle_clean.png'))
out = arr.copy()

sub = out[1200:1370, 530:600]
is_blk = (sub[:, :, 0] == 17) & (sub[:, :, 1] == 22) & (sub[:, :, 2] == 29)
is_red = (sub[:, :, 0] == 216) & (sub[:, :, 1] == 29) & (sub[:, :, 2] == 23)
is_bg  = (sub[:, :, 3] == 0)

dist_from_bg = cv2.distanceTransform((~is_bg).astype(np.uint8), cv2.DIST_L2, 3)
outer_blk = is_blk & (dist_from_bg <= 7.0)

dist_from_red = cv2.distanceTransform((~is_red).astype(np.uint8), cv2.DIST_L2, 3)
tie_blk = is_blk & (dist_from_red <= 7.0)

internal_blk = is_blk & (~outer_blk) & (~tie_blk)
sub[internal_blk] = [236, 203, 46, 255]
out[1200:1370, 530:600] = sub

fg = out[:, :, 3] > 0
unique_colors, counts = np.unique(out[fg], axis=0, return_counts=True)
print(f"Total foreground pixels: {np.count_nonzero(fg)}")
print(f"Number of unique colors: {len(unique_colors)}")
assert len(unique_colors) == 5, f"Expected 5 colors, got {len(unique_colors)}"

for c, cnt in zip(unique_colors, counts):
    hex_col = '#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2])
    print(f"  {c} ({hex_col}): {cnt} px ({cnt/np.count_nonzero(fg)*100:.2f}%)")

final_img = Image.fromarray(out)

# Deploy to all production paths
target_paths = [
    'assets/Turtle_clean.png',
    'assets/spinning_turtle.png',
    'assets/Turtle.png',
    'simulator/assets/Turtle_clean.png',
    'simulator/assets/spinning_turtle.png',
    'simulator/assets/Turtle.png',
]

for p in target_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    final_img.save(p)
    print(f"Saved: {p}")

# Save artifacts
artifact_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\ba8699af-4574-4f1e-9678-f6f40a0f19fe"
final_img.save(os.path.join(artifact_dir, "turtle_5color_final.png"))
final_img.save(os.path.join(artifact_dir, "turtle_5color_overview.png"))

# Detail crops
shirt_crop = Image.fromarray(out[700:1500, 200:1050])
shirt_crop.save(os.path.join(artifact_dir, "turtle_shirt_detail.png"))

print("All assets and artifacts deployed successfully!")
