import numpy as np
from PIL import Image

orig = np.array(Image.open('assets/Turtle_clean.png'))
# Let's inspect x: 700 to 900, y: 750 to 1050
crop = orig[750:1050, 700:900]
Image.fromarray(crop).save('scripts/orig_neck_junction.png')
print("Saved orig_neck_junction.png")
