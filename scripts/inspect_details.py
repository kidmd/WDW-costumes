import cv2
import numpy as np
from PIL import Image

# Let's inspect the green streak under the right collar
arr = np.array(Image.open('scripts/turtle_5color_test.png'))

# Crop x: 680 to 760, y: 1050 to 1250
sub = arr[1050:1250, 680:760].copy()
Image.fromarray(sub).save('scripts/detail_collar_streak.png')

# Crop glasses bridge x: 450 to 550, y: 500 to 600
sub_bridge = arr[500:600, 450:550].copy()
Image.fromarray(sub_bridge).save('scripts/detail_bridge.png')

# Crop left contour x: 500 to 560, y: 1200 to 1350
sub_left = arr[1200:1350, 500:560].copy()
Image.fromarray(sub_left).save('scripts/detail_left_edge.png')

print("Details saved.")
