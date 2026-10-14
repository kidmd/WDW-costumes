import cv2
import numpy as np
from PIL import Image
import json
from sklearn.cluster import KMeans

im = Image.open('assets/Pirateshipsimple.png')
w_img, h_img = im.size
arr = np.array(im)
alpha = arr[:, :, 3]
rgb = arr[:, :, :3]

# Chest bounds
plateScale = 1.0
baseW = 0.56
aspect = w_img / h_img
normW = baseW * plateScale
normH = normW / (1.25 * aspect)
Y_center = 0.3615
normX = 0.5 - normW / 2.0
normY = Y_center - normH / 2.0

print(f"normX={normX:.4f}, normY={normY:.4f}, normW={normW:.4f}, normH={normH:.4f}")

dist_inside = cv2.distanceTransform((alpha > 0).astype(np.uint8), cv2.DIST_L2, 3)

candidates = []
for y in range(20, h_img - 20, 10):
    for x in range(20, w_img - 20, 10):
        if dist_inside[y, x] >= 10.0:
            candidates.append((x, y, dist_inside[y, x]))

print('Candidate points:', len(candidates))

cand_xy = np.array([[c[0], c[1]] for c in candidates])
kmeans = KMeans(n_clusters=100, random_state=42, n_init=10).fit(cand_xy)
centers = kmeans.cluster_centers_

leds = []
for idx, (cx, cy) in enumerate(centers):
    dists = np.sum((cand_xy - np.array([cx, cy]))**2, axis=1)
    best_cand = cand_xy[np.argmin(dists)]
    bx, by = int(best_cand[0]), int(best_cand[1])
    
    nx = round(float(normX + (bx / w_img) * normW), 4)
    ny = round(float(normY + (by / h_img) * normH), 4)
    
    c_rgb = rgb[by, bx]
    leds.append({
        'id': idx,
        'x': nx,
        'y': ny,
        'color': {
            'r': int(c_rgb[0]),
            'g': int(c_rgb[1]),
            'b': int(c_rgb[2])
        }
    })

col_counts = {}
for l in leds:
    c_key = f"{l['color']['r']},{l['color']['g']},{l['color']['b']}"
    col_counts[c_key] = col_counts.get(c_key, 0) + 1

print('Sampled LED color breakdown:')
for k, v in sorted(col_counts.items(), key=lambda x: -x[1]):
    print(f'  RGB({k}): {v} LEDs')

preset_data = {
    'name': 'Pirate Ship 100-LED Vibrant Preset',
    'floatName': 'Float 5 - Pirate Ship',
    'savedAt': '2026-10-13T20:00:00.000Z',
    'graphicType': 'pirate_ship',
    'stlColors': {
        'black': {
            'name': 'Chassis, Hull & Rigging Accents',
            'hex': '#141414',
            'targetRgb': [20, 20, 20],
            'role': 'chassis'
        },
        'red': {
            'name': 'Sails & Masthead Flag',
            'hex': '#e61919',
            'targetRgb': [230, 25, 25],
            'role': 'inlay',
            'filename': 'color_red.stl'
        },
        'gold': {
            'name': 'Bright Gold Masts & Trim',
            'hex': '#ebb941',
            'targetRgb': [235, 185, 65],
            'role': 'inlay',
            'filename': 'color_gold.stl'
        },
        'dark_gold': {
            'name': 'Antique Bronze Decks & Shading',
            'hex': '#9b6914',
            'targetRgb': [155, 105, 20],
            'role': 'inlay',
            'filename': 'color_dark_gold.stl'
        },
        'green': {
            'name': 'Ocean Waves & Sea Keel',
            'hex': '#147332',
            'targetRgb': [20, 115, 50],
            'role': 'inlay',
            'filename': 'color_green.stl'
        }
    },
    'ledCount': 100,
    'leds': leds,
    'animationGroups': [
        {
            'id': 'grp_sails',
            'name': 'Red Battle Sails & Flag',
            'leds': [l['id'] for l in leds if l['color']['r'] == 230],
            'color': '#e61919'
        },
        {
            'id': 'grp_masts',
            'name': 'Golden Masts & Rigging',
            'leds': [l['id'] for l in leds if l['color']['r'] == 235],
            'color': '#ebb941'
        },
        {
            'id': 'grp_decks',
            'name': 'Bronze Decks & Trim',
            'leds': [l['id'] for l in leds if l['color']['r'] == 155],
            'color': '#9b6914'
        },
        {
            'id': 'grp_waves',
            'name': 'Emerald Ocean Waves',
            'leds': [l['id'] for l in leds if l['color']['g'] == 115],
            'color': '#147332'
        },
        {
            'id': 'grp_hull',
            'name': 'Black Hull & Keel',
            'leds': [l['id'] for l in leds if l['color']['r'] == 20 and l['color']['g'] == 20],
            'color': '#141414'
        }
    ],
    'settings': {
        'pattern': 'steady_sparkle',
        'speedBpm': 120,
        'sparkleRate': 5,
        'greenHue': 140,
        'brightness': 255,
        'glowSize': 18
    }
}

with open('presets/pirate_ship.json', 'w', encoding='utf-8') as f:
    json.dump(preset_data, f, indent=2)

print('Saved presets/pirate_ship.json successfully!')
