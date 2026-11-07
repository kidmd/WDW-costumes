import os
import shutil
import numpy as np
import cv2
from PIL import Image

print("Deploying yellow feet Turtle asset...")
img = Image.open('scripts/yellow_feet_full.png')
arr = np.array(img)

# Verification
fg = arr[:, :, 3] > 0
unique_colors, counts = np.unique(arr[fg], axis=0, return_counts=True)
print(f"Total foreground pixels: {np.count_nonzero(fg)}")
print(f"Number of unique colors: {len(unique_colors)}")
assert len(unique_colors) == 5, f"Expected 5 colors, got {len(unique_colors)}"

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
    img.save(p)
    print(f"Saved: {p}")

# Save artifacts
artifact_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\ba8699af-4574-4f1e-9678-f6f40a0f19fe"
img.save(os.path.join(artifact_dir, "turtle_5color_final.png"))
img.save(os.path.join(artifact_dir, "turtle_5color_overview.png"))

feet_crop = Image.fromarray(arr[1300:1800, 400:2000])
feet_crop.save(os.path.join(artifact_dir, "turtle_feet_detail.png"))

print("Deployed all assets and artifacts successfully!")
