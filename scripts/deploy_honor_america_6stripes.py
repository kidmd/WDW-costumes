import os
import shutil
import numpy as np
from PIL import Image

src_path = r'C:\Users\Kiddi\.gemini\antigravity\brain\03c4f5c5-d3ad-4335-8bcc-a465e379945f\render_6stripes_v2.png'
img = Image.open(src_path)
arr = np.array(img)

# Verify strict 4-color compliance
fg = arr[:, :, 3] > 0
u, cnts = np.unique(arr[fg], axis=0, return_counts=True)
print(f'Total foreground pixels: {np.count_nonzero(fg)}')
print(f'Unique foreground colors: {len(u)}')
assert len(u) == 4, f'Expected 4 colors, got {len(u)}'

for col, cnt in zip(u, cnts):
    hex_c = '#{:02x}{:02x}{:02x}'.format(col[0], col[1], col[2])
    print(f'  {col} ({hex_c}): {cnt} px ({cnt/np.count_nonzero(fg)*100:.2f}%)')

target_paths = [
    'assets/honor_america_eagle.png',
    'assets/to_honor_america.png',
    'simulator/assets/honor_america_eagle.png',
    'simulator/assets/to_honor_america.png',
    'scripts/honor_america_4color_clean.png',
]

for p in target_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print(f'Deployed: {p}')

# Update simulator/app.js cache buster
app_js_path = 'simulator/app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_cb = "floatArtworkImgs['honor_america_eagle'].src = 'assets/honor_america_eagle.png?v=20261103_honor_america_v8';"
new_cb = "floatArtworkImgs['honor_america_eagle'].src = 'assets/honor_america_eagle.png?v=20261104_honor_america_6stripes';"

if old_cb in js:
    js = js.replace(old_cb, new_cb, 1)
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print('Updated simulator/app.js cache buster to 20261104_honor_america_6stripes!')
else:
    print('Warning: old cache buster string not found in app.js!')

print('Deployment complete!')
