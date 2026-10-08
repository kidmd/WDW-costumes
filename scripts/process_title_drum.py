import cv2
import numpy as np
from PIL import Image
import os

def process_drum():
    input_path = 'assets/Drum.png'
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load {input_path}")
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    yy, xx = np.mgrid[:h, :w]

    # --- Target 5-Color Palette (Flat, Unshaded for Multi-Material 3D Printing) ---
    # 1. Black:  #11161d -> RGB [17, 22, 29]   (Chassis, Drum Face, Wheels Tire Body)
    # 2. Gold:   #facc15 -> RGB [250, 204, 21]  (Drum Ring, Text, Wheel Rims/Hubs, Flagpoles, Square Flag, Canopy Dome)
    # 3. Red:    #ef4444 -> RGB [239, 68, 68]   (Cab Body Panels, Arches, Streamer Ribbon)
    # 4. Blue:   #2563eb -> RGB [37, 99, 235]   (Streamer Pennant Tip)
    # 5. Green:  #10b981 -> RGB [16, 185, 129]  (Lead Flag)
    C_TRANSPARENT = (0, 0, 0, 0)
    C_BLACK       = (17, 22, 29, 255)
    C_GOLD        = (250, 204, 21, 255)
    C_RED         = (239, 68, 68, 255)
    C_BLUE        = (37, 99, 235, 255)
    C_GREEN       = (16, 185, 129, 255)

    # --- 1. Circular Drum Geometry & Typography ---
    cx, cy = 601.5, 471.0
    dist_out = ((xx - cx) / 259.5)**2 + ((yy - cy) / 248.0)**2
    dist_in  = ((xx - cx) / 232.5)**2 + ((yy - cy) / 222.0)**2
    drum_ring = (dist_out <= 1.0) & (dist_in > 1.0)
    drum_face = (dist_in <= 1.0)

    # Extract text on drum face with inner letter counters (holes in P, A, R, D intact)
    raw_text = drum_face & ((gray > 48) | ((hsv[:, :, 1] > 25) & (hsv[:, :, 2] > 45)))
    clean_text = cv2.morphologyEx(raw_text.astype(np.uint8)*255, cv2.MORPH_OPEN, np.ones((2,2), np.uint8))
    clean_text = cv2.morphologyEx(clean_text, cv2.MORPH_CLOSE, np.ones((2,2), np.uint8))
    ext_cnts, _ = cv2.findContours(clean_text, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    letter_roi = np.zeros_like(clean_text)
    for c in ext_cnts:
        x_c, y_c, w_c, h_c = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        if h_c < 150 and area > 100:
            cv2.drawContours(letter_roi, [c], -1, 255, -1)
    drum_letters = (clean_text > 0) & (letter_roi > 0)

    # --- 2. EXACTLY 2 WHEELS (Outlined in Gold with Gold Hubs) ---
    # Front Wheel: center (180, 780), R=73
    dist_w1 = np.hypot(xx - 180, yy - 780)
    w1_full = (dist_w1 <= 73) & (yy >= 700)
    w1_rim  = (dist_w1 <= 73) & (dist_w1 >= 64) & (yy >= 700)
    w1_hub  = (dist_w1 <= 16) & (yy >= 700)
    w1_tire = w1_full & (~w1_rim) & (~w1_hub)

    # Rear Wheel: center (964, 765), R=66 (Middle wheel at x=838 is removed)
    dist_w2 = np.hypot(xx - 964, yy - 765)
    w2_full = (dist_w2 <= 66) & (yy >= 700)
    w2_rim  = (dist_w2 <= 66) & (dist_w2 >= 58) & (yy >= 700)
    w2_hub  = (dist_w2 <= 14) & (yy >= 700)
    w2_tire = w2_full & (~w2_rim) & (~w2_hub)

    wheels_all   = w1_full | w2_full
    wheels_gold  = w1_rim | w1_hub | w2_rim | w2_hub
    wheels_black = w1_tire | w2_tire

    # --- 3. Background & Foreground Ground Removal ---
    dark_pixels = (gray < 28) & (~drum_face)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(dark_pixels.astype(np.uint8))
    sky_mask = np.zeros((h, w), bool)
    for i in range(1, num):
        area = stats[i, cv2.CC_STAT_AREA]
        top = stats[i, cv2.CC_STAT_TOP]
        # Exterior sky (area > 400k), streamer-drum pocket (area ~12k), ribbon gap (~370), cab window (~1.4k)
        if area > 300 and top < 450:
            sky_mask[labels == i] = True

    # Outer boundary cleanups
    sky_mask[:650, 1060:] = True
    sky_mask[:250, :110] = True

    # Remove extra hanging red strip next to the square gold flag:
    extra_red_strip = (xx >= 800) & (xx <= 860) & (yy >= 200) & (yy <= 450) & (dist_out > 1.0)
    sky_mask[extra_red_strip] = True

    # Clear air buffer to the right of front flagpole (removes floating black specks):
    pole1_air = (xx >= 349) & (xx <= 390) & (yy >= 40) & (yy <= 200)
    sky_mask[pole1_air] = True

    # Clear air buffer around rear flagpole below square flag:
    pole2_air = (xx >= 1010) & (xx <= 1040) & (yy >= 365) & (yy <= 550)
    sky_mask[pole2_air] = True

    # Ground plane removal:
    ground_mask = np.zeros((h, w), bool)
    ground_cand = np.zeros((h, w), dtype=np.uint8)
    ground_cand[650:, :] = ((gray[650:, :] > 55) & (gray[650:, :] < 120) & (hsv[650:, :, 1] < 35)).astype(np.uint8)
    g_fill = np.zeros((h+2, w+2), dtype=np.uint8)
    cv2.floodFill(ground_cand, g_fill, (0, h-1), 255)
    cv2.floodFill(ground_cand, g_fill, (w-1, h-1), 255)
    ground_mask |= (g_fill[1:-1, 1:-1] > 0)

    # Floor / shadow cutoffs below and between wheels:
    ground_mask[yy > 855] = True
    ground_mask[(xx >= 255) & (xx <= 895) & (yy > 735)] = True
    ground_mask[(xx < 110) & (yy > 710)] = True
    ground_mask[(xx > 1035) & (yy > 730)] = True

    # Float silhouette:
    float_mask = (~sky_mask) & (~ground_mask)
    float_mask[wheels_all | drum_ring | drum_face] = True

    # Filter out tiny disconnected float specks:
    num_f, labels_f, stats_f, _ = cv2.connectedComponentsWithStats(float_mask.astype(np.uint8))
    clean_float = np.zeros((h, w), bool)
    for i in range(1, num_f):
        if stats_f[i, cv2.CC_STAT_AREA] > 80:
            clean_float[labels_f == i] = True
    clean_float[wheels_all | drum_ring | drum_face] = True

    # --- 4. Flagpoles (Clean & 100% Solid Gold) ---
    pole1 = (np.abs(xx - 344) <= 4) & (yy >= 40) & (yy <= 245)
    finial1 = (np.hypot(xx - 344, yy - 42) <= 6)
    pole2 = (np.abs(xx - 1018) <= 4) & (yy >= 265) & (yy <= 550)
    finial2 = (np.hypot(xx - 1018, yy - 268) <= 6)
    clean_flagpoles = pole1 | finial1 | pole2 | finial2

    # --- 5. Flags ---
    # Green Lead Flag (swallowtail pennant at front cab):
    is_green_raw = (hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 85) & (hsv[:, :, 1] > 25) & (hsv[:, :, 2] > 30) & (xx < 344) & (yy < 220)
    green_flag = cv2.morphologyEx(is_green_raw.astype(np.uint8)*255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0

    # Blue Flag: ONLY the pennant tip at top arch!
    is_blue_raw = (hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] > 30) & (hsv[:, :, 2] > 40) & (yy < 200) & (xx > 600) & (xx < 800)
    blue_pennant = cv2.morphologyEx(is_blue_raw.astype(np.uint8)*255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0

    # Square Gold Flag (at the rear, x in [860, 1016], y in [270, 360]):
    square_gold_flag = (xx >= 860) & (xx <= 1016) & (yy >= 270) & (yy <= 360) & clean_float & (dist_out > 1.0)

    # Red Body Panels & Streamer Ribbon:
    is_pennant_red = ((hsv[:, :, 0] < 15) | (hsv[:, :, 0] > 165)) & (hsv[:, :, 1] > 30) & (hsv[:, :, 2] > 30) & (yy < 280) & (xx > 500) & (xx < 800)
    is_body_red = ((hsv[:, :, 0] < 15) | (hsv[:, :, 0] > 165)) & (hsv[:, :, 1] > 25) & (hsv[:, :, 2] > 25) & (~drum_face) & (~wheels_all) & (yy >= 250) & (yy < 800)
    body_red_raw = (is_pennant_red | is_body_red) & (~extra_red_strip) & (~square_gold_flag)
    body_red = cv2.morphologyEx(body_red_raw.astype(np.uint8)*255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    body_red &= (~extra_red_strip)
    body_red &= (~square_gold_flag)

    # --- 6. Black bit on top of cab canopy (near green flag) -> MAKE GOLD ---
    roof_dome = (xx >= 330) & (xx <= 425) & (yy >= 150) & (yy <= 220) & clean_float

    # Gold Body / Trim / Filigree:
    is_gold_raw = (hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 35) & (hsv[:, :, 1] > 20) & (hsv[:, :, 2] > 40) & (~drum_face) & (~wheels_all) & (~green_flag) & (~blue_pennant) & (~body_red) & (yy < 800)
    gold_body = cv2.morphologyEx(is_gold_raw.astype(np.uint8)*255, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
    gold_body |= roof_dome
    gold_body |= square_gold_flag
    gold_body |= clean_flagpoles
    gold_body |= wheels_gold

    # --- 7. Assemble Production 5-Color RGBA Array ---
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[clean_float] = C_BLACK
    out[clean_float & body_red] = C_RED
    out[clean_float & gold_body] = C_GOLD
    out[clean_float & blue_pennant] = C_BLUE
    out[clean_float & green_flag] = C_GREEN

    # Ensure Wheels:
    out[wheels_black] = C_BLACK
    out[wheels_gold] = C_GOLD

    # Ensure Flagpoles are 100% Solid Gold:
    out[clean_flagpoles] = C_GOLD

    # Ensure Roof Dome is 100% Solid Gold:
    out[roof_dome & clean_float] = C_GOLD

    # Ensure Square Flag is 100% Solid Gold:
    out[square_gold_flag & clean_float] = C_GOLD

    # Drum face and ring:
    out[drum_ring] = C_GOLD
    out[drum_face] = C_BLACK
    out[drum_letters] = C_GOLD

    # Tight crop around float bounds with 20px padding:
    ys, xs = np.where(out[:, :, 3] > 0)
    min_x, max_x = max(0, xs.min() - 20), min(w, xs.max() + 20)
    min_y, max_y = max(0, ys.min() - 20), min(h, ys.max() + 20)
    cropped = out[min_y:max_y, min_x:max_x]

    # Save to assets/title_drum.png and simulator/assets/title_drum.png:
    out_assets = 'assets/title_drum.png'
    out_sim = 'simulator/assets/title_drum.png'
    pil_img = Image.fromarray(cropped)
    pil_img.save(out_assets)
    pil_img.save(out_sim)
    print(f"Successfully generated and saved:")
    print(f"  - {out_assets} ({cropped.shape[1]}x{cropped.shape[0]})")
    print(f"  - {out_sim} ({cropped.shape[1]}x{cropped.shape[0]})")

    # Final Palette Verification:
    colors, counts = np.unique(cropped.reshape(-1, 4), axis=0, return_counts=True)
    print("\nVerified Color Palette:")
    color_names = {
        C_TRANSPARENT: "Transparent Background",
        C_BLACK: "Black (Chassis / Drum Face / Wheel Tires)",
        C_GOLD: "Gold (Drum Ring / Text / Wheels Gold Rim & Hub / Flagpoles / Square Flag / Canopy Dome)",
        C_RED: "Red (Body Panels / Streamer)",
        C_BLUE: "Blue (Streamer Pennant Tip)",
        C_GREEN: "Green (Lead Flag)"
    }
    for col, cnt in zip(colors, counts):
        name = color_names.get(tuple(col), "Unknown Color")
        pct = cnt / cropped.size * 4 * 100
        print(f"  - {name}: RGBA{tuple(col)} -> {cnt} px ({pct:.2f}%)")

if __name__ == '__main__':
    process_drum()
