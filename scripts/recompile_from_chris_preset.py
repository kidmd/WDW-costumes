import json, os, subprocess, sys
from PIL import Image

with open('presets/petes_dragon_chris_2026-10-09_00-07.json', 'r', encoding='utf-8') as f:
    preset = json.load(f)

leds = preset.get('leds', [])
print(f"Compiling for {len(leds)} LEDs from latest Chris preset...")

artwork_png = '3d_panels/active_artwork.png'
if not os.path.exists(artwork_png):
    artwork_png = 'assets/petes_dragon_transparent.png'

with Image.open(artwork_png) as a_img:
    img_w, img_h = a_img.size
    aspect = img_w / float(img_h)

FRONT_WIDTH_MM = 227.66
FRONT_HEIGHT_MM = round(FRONT_WIDTH_MM / aspect, 2)

# Chest bounds for Pete's Dragon
normW = 0.310 * 1.25 * 0.706
normH = 0.310
normX = (1.0 - normW) / 2.0
normY = 0.3615 - normH / 2.0

front_leds = []
for idx, l in enumerate(leds):
    rx = (l.get('x', 0.5) - normX) / normW
    ry = (l.get('y', 0.5) - normY) / normH
    px = round(rx * FRONT_WIDTH_MM, 2)
    py = round((1.0 - ry) * FRONT_HEIGHT_MM, 2)
    front_leds.append({
        'id': idx + 1,
        'orig_id': idx,
        'x': px,
        'y': py,
        'is_custom_rotation': False,
        'rotation_deg': 0.0,
        'color': l.get('color', {'r': 0, 'g': 255, 'b': 0})
    })

specs = {
    'character': "Pete's Dragon 3D Wearable TPU Armor Panels",
    'float_name': "Pete's Dragon",
    'float_index': 5,
    'aspect': aspect,
    'artwork_file': 'active_artwork.png',
    'graphic_type': 'petes_dragon',
    'window_shape': 'round_34',
    'well_orientation': 'horizontal',
    'include_led_numbers': True,
    'include_clip_grooves': False,
    'include_top_nubs': True,
    'width_mm': FRONT_WIDTH_MM,
    'height_mm': FRONT_HEIGHT_MM,
    'ordered_leds': front_leds,
    'led_count': len(front_leds),
    'front': {
        'variant': 'front',
        'name': 'Front Plate (Chest)',
        'width_mm': FRONT_WIDTH_MM,
        'height_mm': FRONT_HEIGHT_MM,
        'ordered_leds': front_leds,
        'led_count': len(front_leds)
    },
    'back': {
        'variant': 'back',
        'name': 'Back Plate (Torso)',
        'width_mm': FRONT_WIDTH_MM,
        'height_mm': FRONT_HEIGHT_MM,
        'ordered_leds': front_leds,
        'led_count': len(front_leds)
    }
}

with open('3d_panels/tpu_panel_specs.json', 'w', encoding='utf-8') as f:
    json.dump(specs, f, indent=2)

cmd = [sys.executable, 'scripts/compile_clean_tpu_panel.py', '--specs', '3d_panels/tpu_panel_specs.json']
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print('STDERR:', res.stderr)
