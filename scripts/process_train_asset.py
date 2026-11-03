import cv2
import numpy as np
from PIL import Image
import os

def process_train():
    input_path = r'C:/Users/Kiddi/.gemini/antigravity/brain/ba8699af-4574-4f1e-9678-f6f40a0f19fe/.user_uploaded/media_1793733438799_5f6ce56f.jpg'
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {input_path}")
    
    orig_h, orig_w, _ = img.shape
    
    # 4 Target Discrete Colors for Multi-Material 3D Printing (RGBA)
    # 1. Black:         #11161d (Outlines, cab window silhouettes, shadow areas, pupils)
    # 2. Red:           #e63946 (Locomotive boiler body, cab inset, cowcatcher wedge, wheel tires)
    # 3. Yellow:        #ffcc15 (Headlight beam/lens, eyes, steam dome / whistle, wheel center hubs)
    # 4. Golden Bronze: #a0732d (Cab roof & pillars, tender frame, cowcatcher flange, drive rod, face disc)
    C_TRANS  = (0, 0, 0, 0)
    C_BLACK  = (17, 22, 29, 255)
    C_RED    = (230, 57, 70, 255)
    C_YELLOW = (255, 204, 21, 255)
    C_BRONZE = (160, 115, 45, 255)
    
    # Canvas padding to ensure restored wheel and cowcatcher have breathing room
    pad_top = 15
    pad_bottom = 35
    pad_left = 20
    pad_right = 20
    
    new_h = orig_h + pad_top + pad_bottom
    new_w = orig_w + pad_left + pad_right
    
    # Place original into padded canvas with pure white background (BGR)
    padded = np.full((new_h, new_w, 3), 255, dtype=np.uint8)
    padded[pad_top:pad_top+orig_h, pad_left:pad_left+orig_w] = img
    
    # --- 1. REPAIR CUT OFFS AT BOTTOM ---
    # In original coordinates:
    # A. Front Wheel: cut flat at y = 763 between x = 432 and x = 488 (width 57).
    # Center of arc is x = 460.0. Half-width = 28.0.
    # Arc curves down from y = 763 at x=432/488 to y = 770.0 at x=460.
    cut_y = 763 + pad_top
    
    for x_orig in range(430, 490):
        x = x_orig + pad_left
        dx = (x_orig - 460.0) / 28.0
        if abs(dx) <= 1.0:
            dy = np.sqrt(max(0.0, 1.0 - dx*dx))
            y_outer_orig = 763.0 + 7.0 * dy
            y_outer = int(round(y_outer_orig + pad_top))
            y_bronze_orig = 763.0 + 3.0 * dy
            y_bronze = int(round(y_bronze_orig + pad_top))
            
            for y in range(cut_y, y_outer + 1):
                if y <= y_bronze:
                    # Inside the outer rim: golden bronze flange
                    padded[y, x] = [24, 77, 113] # Bronze BGR
                else:
                    # Outer perimeter: solid black outline
                    padded[y, x] = [1, 1, 1] # Black outline BGR
    
    # B. Cowcatcher:
    # Intact slope from x=760..820: y_bot(x) = 763.0 + 0.18 * (x - 821.0)
    # Right edge coming down from x=940..950: y_right(x) = -3.0 * x + 3576.0 (orig coords)
    # Intersection at x = 931.0, y = 782.8 (orig coords)
    for x_orig in range(821, 942):
        x = x_orig + pad_left
        if x_orig <= 931:
            y_bot_orig = 763.0 + 0.18 * (x_orig - 821.0)
        else:
            y_bot_orig = -3.0 * x_orig + 3576.0
        
        if y_bot_orig >= 763.0:
            y_bot = int(round(y_bot_orig + pad_top))
            y_black_top = int(round(y_bot_orig - 4.0 + pad_top))
            y_bronze_top = int(round(y_bot_orig - 13.0 + pad_top))
            
            for y in range(cut_y, y_bot + 1):
                if y <= y_bronze_top:
                    padded[y, x] = [0, 6, 143] # Red body BGR
                elif y <= y_black_top:
                    padded[y, x] = [24, 77, 113] # Golden Bronze flange BGR
                else:
                    padded[y, x] = [1, 1, 1] # Black outline BGR
    
    # Ensure the right edge black outline has clean 4px border down to the corner
    for y_orig in range(755, 784):
        x_edge_orig = (3576.0 - y_orig) / 3.0
        y = y_orig + pad_top
        x_edge = int(round(x_edge_orig + pad_left))
        for bx in range(x_edge - 3, x_edge + 1):
            if 0 <= bx < new_w and 0 <= y < new_h:
                padded[y, bx] = [1, 1, 1] # Black outline BGR
    
    # --- 2. BACKGROUND SEGMENTATION ---
    # Flood-fill outer canvas background from edges
    hsv = cv2.cvtColor(padded, cv2.COLOR_BGR2HSV)
    flood_mask = np.zeros((new_h + 2, new_w + 2), dtype=np.uint8)
    flags = cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
    
    for pt in [(0, 0), (new_w - 1, 0), (0, new_h - 1), (new_w - 1, new_h - 1), 
               (new_w // 2, 0), (new_w // 2, new_h - 1), (0, new_h // 2), (new_w - 1, new_h // 2)]:
        cv2.floodFill(padded.copy(), flood_mask, pt, 0, (20, 20, 20), (20, 20, 20), flags=flags)
        
    bg_outer = flood_mask[1:new_h+1, 1:new_w+1] > 0
    # Also near-white background pixels
    is_white = (padded[:, :, 0] > 235) & (padded[:, :, 1] > 235) & (padded[:, :, 2] > 235)
    bg = bg_outer | is_white
    fg = ~bg
    
    # Morphological close to ensure solid continuous outlines and no stray speckles
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_CLOSE, kernel).astype(bool)
    
    # --- 3. 4-COLOR CLASSIFICATION ---
    r = padded[:, :, 2]
    g = padded[:, :, 1]
    b = padded[:, :, 0]
    
    # 1. Black: low value / dark outline, pupils, window silhouettes
    is_black = fg & (hsv[:, :, 2] < 45)
    
    # 2. Red: strong red hue (boiler, tender inset, cowcatcher, wheel tires)
    is_red = fg & (~is_black) & ((hsv[:, :, 0] < 14) | (hsv[:, :, 0] > 165)) & (r > 70) & (r > g * 1.3) & (r > b * 1.3)
    
    # 3. Yellow: high brightness, yellow hue (headlight, eyes, steam dome, wheel hubs)
    is_yellow = fg & (~is_black) & (~is_red) & (hsv[:, :, 0] >= 14) & (hsv[:, :, 0] <= 38) & (hsv[:, :, 2] > 155) & (r > 150) & (g > 125)
    
    # 4. Golden Bronze: remaining foreground (cab roof, pillars, drive rod, face disc, trim)
    is_bronze = fg & (~is_black) & (~is_red) & (~is_yellow)
    
    # Assemble output RGBA array for PIL
    out_rgba = np.zeros((new_h, new_w, 4), dtype=np.uint8)
    out_rgba[is_black]  = C_BLACK
    out_rgba[is_red]    = C_RED
    out_rgba[is_yellow] = C_YELLOW
    out_rgba[is_bronze] = C_BRONZE
    out_rgba[~fg]       = C_TRANS
    
    # Create PIL Image
    pil_img = Image.fromarray(out_rgba, 'RGBA')
    
    # Target file paths
    target_paths = [
        'assets/Simpletrain.png',
        'simulator/assets/Simpletrain.png',
        'assets/train.png',
        'simulator/assets/train.png'
    ]
    
    for path in target_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pil_img.save(path, format='PNG')
        print(f"Saved: {path}")
    
    print(f"Total canvas size: {new_w}x{new_h}")
    print(f"FG counts - Black: {np.sum(is_black)}, Red: {np.sum(is_red)}, Yellow: {np.sum(is_yellow)}, Bronze: {np.sum(is_bronze)}")
    
    # Verify exact unique color count
    rgb_check = out_rgba[:, :, :3][out_rgba[:, :, 3] > 0]
    unique_colors = np.unique(rgb_check.reshape(-1, 3), axis=0)
    print(f"Verification: EXACTLY {len(unique_colors)} solid colors in foreground:")
    for c in unique_colors:
        hex_c = f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
        print(f"  RGB: ({c[0]}, {c[1]}, {c[2]}) -> {hex_c}")

if __name__ == '__main__':
    process_train()
