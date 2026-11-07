import cv2
import numpy as np
from PIL import Image

img = Image.open('assets/Turtle_clean.png').convert('RGBA')
arr = np.array(img)

r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

# Grey condition
is_grey = (a > 128) & (np.abs(r.astype(int) - g.astype(int)) < 25) & (np.abs(r.astype(int) - b.astype(int)) < 25) & (r > 40) & (r < 175)

# Limit to head area
is_grey_head = np.zeros_like(is_grey)
is_grey_head[260:750, 260:920] = is_grey[260:750, 260:920]

# Connected components
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(is_grey_head.astype(np.uint8), connectivity=8)

# The bridge is around x=480, y=550. Let's see which component contains the bridge and frames.
# Find component with largest area
areas = stats[1:, cv2.CC_STAT_AREA]
largest_idx = np.argmax(areas) + 1
print(f"Largest grey component: {largest_idx}, area={stats[largest_idx, cv2.CC_STAT_AREA]}")

# Let's see if there are other parts of the frame (e.g. left rim, right rim, bridge, temple)
frame_mask = np.zeros_like(is_grey)
for l in range(1, num_labels):
    # If area > 200, check centroid
    if stats[l, cv2.CC_STAT_AREA] > 200:
        cx, cy = centroids[l]
        print(f"Component {l}: area={stats[l, cv2.CC_STAT_AREA]}, centroid=({cx:.1f}, {cy:.1f})")
        # Keep components that belong to the glasses (cx < 900, cy > 350 or cy < 750)
        # Note: top of head was y < 350 and cx > 450
        if not (cy < 350 and cx > 450):
            frame_mask |= (labels == l)

print(f"Total frame mask pixels: {np.count_nonzero(frame_mask)}")

# Also, let's close any small holes in the frame mask using morphological closing
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
frame_mask_closed = cv2.morphologyEx(frame_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)

# Check frame mask
check = arr[260:750, 260:1100].copy()
check[frame_mask_closed[260:750, 260:1100] == 1] = [255, 0, 255, 255]
Image.fromarray(check).save('scripts/glasses_mask_clean.png')
print("Clean glasses mask saved.")
