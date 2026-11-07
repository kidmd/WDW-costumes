import numpy as np
from PIL import Image

arr = np.array(Image.open('scripts/Turtle_clean_5color.png'))
orig = np.array(Image.open('assets/Turtle_clean.png'))

# Crop tie knot and tie body: y: 1000 to 1400, x: 600 to 720
sub_new = arr[1000:1400, 600:720]
sub_orig = orig[1000:1400, 600:720]

Image.fromarray(sub_new).save('scripts/zoom_tie_new.png')
Image.fromarray(sub_orig).save('scripts/zoom_tie_orig.png')
print("Saved zoom tie.")
