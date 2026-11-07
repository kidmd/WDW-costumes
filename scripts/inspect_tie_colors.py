import numpy as np
from PIL import Image

orig = np.array(Image.open('assets/Turtle_clean.png'))
r, g, b, a = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2], orig[:, :, 3]

# In tie area: y in [1000, 1400], x in [600, 700]
tie_crop = orig[1000:1400, 600:700]
u, counts = np.unique(tie_crop.reshape(-1, 4), axis=0, return_counts=True)
for i in np.argsort(-counts)[:10]:
    print(u[i], counts[i])
