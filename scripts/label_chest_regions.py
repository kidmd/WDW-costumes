import cv2
import numpy as np
from PIL import Image

# Load image
img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Let's inspect the entire chest region y: 750 to 1450, x: 400 to 800
chest = arr[750:1450, 400:800].copy()

# Threshold to find black lines
r, g, b, a = chest[:, :, 0], chest[:, :, 1], chest[:, :, 2], chest[:, :, 3]
is_black = (a > 128) & (r < 50) & (g < 60) & (b < 70)

# Invert so black lines are 0, and regions are 255
regions_mask = (~is_black & (a > 128)).astype(np.uint8) * 255

# Connected components on non-black foreground pixels
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(regions_mask, connectivity=8)
print(f"Number of distinct regions in chest: {num_labels}")

# Color each connected component with a random bright color to see each separate patch!
colored = np.zeros((chest.shape[0], chest.shape[1], 4), dtype=np.uint8)
np.random.seed(123)
colors = [np.random.randint(50, 255, size=3).tolist() + [255] for _ in range(num_labels)]
colors[0] = [0, 0, 0, 0] # Background

for l in range(1, num_labels):
    if stats[l, cv2.CC_STAT_AREA] > 50:
        colored[labels == l] = colors[l]
        cx, cy = int(centroids[l][0]), int(centroids[l][1])
        cv2.putText(colored, str(l), (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 2)
        # Check original color in this patch
        orig_patch_color = chest[labels == l]
        mean_c = np.mean(orig_patch_color[:, :3], axis=0).astype(int)
        print(f"Region {l}: Area={stats[l, cv2.CC_STAT_AREA]}, Center=({cx+400}, {cy+750}), Mean RGB={mean_c}")

# Overlay original black lines on top
colored[is_black] = [0, 0, 0, 255]

Image.fromarray(colored).save('scripts/chest_regions_labeled.png')
print("Labeled chest regions saved.")
