import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

# Crop front region: y: 700 to 1700, x: 400 to 1000
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
is_black = (a > 128) & (r < 60) & (g < 70) & (b < 80)
fg_nonblack = ((~is_black) & (a > 128)).astype(np.uint8) * 255

front_mask = np.zeros_like(a, dtype=bool)
front_mask[700:1700, 400:1000] = True

# Connected components in the non-black foreground of the front
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats((fg_nonblack & front_mask).astype(np.uint8), connectivity=8)

print(f"Number of regions in front: {num_labels}")

# Let's inspect each region
for l in range(1, num_labels):
    if stats[l, cv2.CC_STAT_AREA] > 300:
        cx, cy = centroids[l]
        patch_rgb = arr[labels == l][:, :3]
        mean_c = np.mean(patch_rgb, axis=0).astype(int)
        # Identify dominant color type
        if mean_c[0] > 180 and mean_c[1] > 150 and mean_c[2] < 100:
            ctype = "YELLOW"
        elif mean_c[0] > 150 and mean_c[1] < 60 and mean_c[2] < 60:
            ctype = "RED"
        elif mean_c[1] > 80 and mean_c[0] < 80 and mean_c[2] < 80:
            ctype = "GREEN"
        elif mean_c[1] > 120 and mean_c[0] > 100 and mean_c[2] < 100:
            ctype = "LIME_GREEN (FOOT)"
        elif mean_c[2] > 70 and mean_c[0] < 70:
            ctype = "BLUE"
        else:
            ctype = f"OTHER {mean_c}"
        print(f"Region {l}: Area={stats[l, cv2.CC_STAT_AREA]}, Center=({cx:.1f}, {cy:.1f}), Type={ctype}, Mean={mean_c}")

# Let's create an annotated image showing region numbers
annotated = arr[700:1700, 400:1000].copy()
for l in range(1, num_labels):
    if stats[l, cv2.CC_STAT_AREA] > 300:
        cx, cy = int(centroids[l][0]) - 400, int(centroids[l][1]) - 700
        cv2.putText(annotated, str(l), (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255, 255), 2)
        cv2.putText(annotated, str(l), (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0, 255), 1)

Image.fromarray(annotated).save('scripts/front_regions_annotated.png')
print("Saved front_regions_annotated.png")
