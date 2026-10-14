import cv2
import numpy as np
from PIL import Image

im = Image.open('assets/Pirateshipsimple.png')
arr = np.array(im)
alpha = arr[:, :, 3]
rgb = arr[:, :, :3]
h, w = alpha.shape

# 5 colors
colors = {
    'red': {'rgb': [230, 25, 25], 'hex': '#e61919', 'label': 'Red Sails & Flag'},
    'gold': {'rgb': [235, 185, 65], 'hex': '#ebb941', 'label': 'Bright Gold Masts & Trim'},
    'dark_gold': {'rgb': [155, 105, 20], 'hex': '#9b6914', 'label': 'Bronze Decks & Rigging'},
    'green': {'rgb': [20, 115, 50], 'hex': '#147332', 'label': 'Ocean Waves'},
    'black': {'rgb': [20, 20, 20], 'hex': '#141414', 'label': 'Hull & Chassis'}
}

# Scale coordinates to 800x600 viewBox
scale = min(740.0 / w, 540.0 / h)
off_x = (800.0 - w * scale) / 2.0
off_y = (600.0 - h * scale) / 2.0

svg_parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">',
    '  <!-- Main Street Electrical Parade - Float 05: Pirate Ship -->',
    '  <!-- Designed for 5-Color Layered Cricut Heat Transfer Vinyl (HTV) Cutting -->',
    '  <defs>',
    '    <style>',
    '      .stroke-dark { stroke: #111111; stroke-width: 1.5; stroke-linejoin: round; stroke-linecap: round; }',
    '    </style>',
    '  </defs>'
]

for c_key, c_val in colors.items():
    mask = (alpha > 0) & (rgb[:,:,0] == c_val['rgb'][0]) & (rgb[:,:,1] == c_val['rgb'][1]) & (rgb[:,:,2] == c_val['rgb'][2])
    mask_uint = (mask.astype(np.uint8)) * 255
    contours, hierarchy = cv2.findContours(mask_uint, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
    
    path_d_list = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 25: continue
        pts = cnt.reshape(-1, 2)
        d_str = f"M {(pts[0][0]*scale + off_x):.1f} {(pts[0][1]*scale + off_y):.1f}"
        for p in pts[1:]:
            d_str += f" L {(p[0]*scale + off_x):.1f} {(p[1]*scale + off_y):.1f}"
        d_str += " Z"
        path_d_list.append(d_str)
    
    svg_parts.append(f'  <!-- LAYER: {c_val["label"]} -->')
    svg_parts.append(f'  <g id="Layer_{c_key}" fill="{c_val["hex"]}">')
    for p_d in path_d_list:
        svg_parts.append(f'    <path class="stroke-dark" d="{p_d}" />')
    svg_parts.append('  </g>')

svg_parts.append('</svg>')

svg_out = '\n'.join(svg_parts)
with open('simulator/assets/cricut_svg/pirate_ship.svg', 'w', encoding='utf-8') as f:
    f.write(svg_out)
print('Generated simulator/assets/cricut_svg/pirate_ship.svg successfully!')
