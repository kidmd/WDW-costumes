import numpy as np
from PIL import Image

orig = np.array(Image.open('assets/Turtle_clean.png'))
r, g, b, a = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2], orig[:, :, 3]
fg = a > 128

is_red_family = fg & (r > 60) & (r.astype(int) > g.astype(int) * 1.5) & (r.astype(int) > b.astype(int) * 1.5)
print("is_red_family count:", np.count_nonzero(is_red_family))

is_blue_family = fg & (b > 50) & (b.astype(int) >= r.astype(int)) & (b.astype(int) >= g.astype(int) - 10) & (~is_red_family)
print("is_blue_family count:", np.count_nonzero(is_blue_family))

is_green_family = fg & (g > 50) & (g.astype(int) > r.astype(int)) & (g.astype(int) > b.astype(int) - 5) & (~is_red_family) & (~is_blue_family)
print("is_green_family count:", np.count_nonzero(is_green_family))
