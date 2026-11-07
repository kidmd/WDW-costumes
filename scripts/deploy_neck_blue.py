import os
import shutil
import numpy as np
import cv2
from PIL import Image

print("Deploying Turtle asset with green rib notch recolored to blue...")
arr = np.array(Image.open('assets/Turtle_clean.png'))
is_grn = (arr[:, :, 0] == 33) & (arr[:, :, 1] == 101) & (arr[:, :, 2] == 46)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grn.astype(np.uint8), connectivity=8)

C_BLUE = np.array([41, 64, 98, 255], dtype=np.uint8)

final_arr = arr.copy()
final_arr[labels == 863] = C_BLUE

fg = final_arr[:, :, 3] > 0
unique_colors, counts = np.unique(final_arr[fg], axis=0, return_counts=True)
print(f"Total foreground pixels: {np.count_nonzero(fg)}")
print(f"Number of unique colors: {len(unique_colors)}")
assert len(unique_colors) == 5, f"Expected 5 colors, got {len(unique_colors)}"

final_img = Image.fromarray(final_arr)

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

neck_crop = Image.fromarray(final_arr[650:950, 800:1100])
neck_crop.save(os.path.join(artifact_dir, "turtle_neck_shell_detail.png"))

print("Deployed all assets and artifacts successfully!")
