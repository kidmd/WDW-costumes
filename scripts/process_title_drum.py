import cv2
import numpy as np
from PIL import Image
import os

def process_drum():
    input_path = 'assets/Drumcleanedup.jpg'
    if not os.path.exists(input_path):
        input_path = 'assets/Drum.png'
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load {input_path}")
    h, w = img.shape[:2]

    # --- Target 5-Color Palette (Flat, Unshaded for Multi-Material 3D Printing) ---
    # 1. Black:  #11161d -> RGB [17, 22, 29]   (Chassis, Drum Face, Wheels Tire Body, Hidden Mickey Silhouette)
    # 2. Gold:   #facc15 -> RGB [250, 204, 21]  (Drum Ring, Text, Wheel Rims/Hubs, Flagpoles, Yellow Flag, Canopy Dome)
    # 3. Red:    #ef4444 -> RGB [239, 68, 68]   (Cab Body Panels, Arches, Streamer Ribbon)
    # 4. Blue:   #2563eb -> RGB [37, 99, 235]   (Streamer Pennant Tip)
    # 5. Green:  #10b981 -> RGB [16, 185, 129]  (Lead Flag)
    PALETTE = [
        (17, 22, 29, 255),    # Black
        (250, 204, 21, 255),  # Gold
        (239, 68, 68, 255),   # Red
        (37, 99, 235, 255),   # Blue
        (16, 185, 129, 255)   # Green
    ]

    # Add Hidden Mickey silhouette to the yellow flag (rear flag)
    # Mickey Head Center: cx = 2040, cy = 690 in Drumcleanedup.jpg coordinates (scaled proportionally if other size)
    scale_x = w / 2358.0
    scale_y = h / 1824.0
    cx = int(2040 * scale_x)
    cy = int(690 * scale_y)
    r_head = int(36 * ((scale_x + scale_y) / 2.0))
    r_ear = int(r_head * 0.58)
    dist_center = int(r_head * 1.35)
    rad = np.radians(55)

    ear_l_x = int(cx - dist_center * np.sin(rad))
    ear_l_y = int(cy - dist_center * np.cos(rad))
    ear_r_x = int(cx + dist_center * np.sin(rad))
    ear_r_y = int(cy - dist_center * np.cos(rad))

    C_BLACK_BGR = (27, 22, 17)
    cv2.circle(img, (cx, cy), r_head, C_BLACK_BGR, -1, cv2.LINE_AA)
    cv2.circle(img, (ear_l_x, ear_l_y), r_ear, C_BLACK_BGR, -1, cv2.LINE_AA)
    cv2.circle(img, (ear_r_x, ear_r_y), r_ear, C_BLACK_BGR, -1, cv2.LINE_AA)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Detect Background (outer background and cab window opening)
    # Background pixels are white: (S < 40) & (V > 200)
    is_bg = (hsv[:, :, 1] < 40) & (hsv[:, :, 2] > 200)

    # Classification of foreground:
    fg = ~is_bg
    is_black = fg & (hsv[:, :, 2] < 50)
    is_red   = fg & (~is_black) & ((hsv[:, :, 0] < 14) | (hsv[:, :, 0] > 165)) & (hsv[:, :, 1] > 60)
    is_gold  = fg & (~is_black) & (~is_red) & (hsv[:, :, 0] >= 14) & (hsv[:, :, 0] <= 38) & (hsv[:, :, 1] > 60)
    is_blue  = fg & (~is_black) & (~is_red) & (~is_gold) & (hsv[:, :, 0] >= 95) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] > 60)
    is_green = fg & (~is_black) & (~is_red) & (~is_gold) & (~is_blue) & (hsv[:, :, 0] >= 50) & (hsv[:, :, 0] <= 90) & (hsv[:, :, 1] > 50)

    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[is_black] = PALETTE[0]
    out[is_gold]  = PALETTE[1]
    out[is_red]   = PALETTE[2]
    out[is_blue]  = PALETTE[3]
    out[is_green] = PALETTE[4]

    remaining = fg & (~is_black) & (~is_gold) & (~is_red) & (~is_blue) & (~is_green)
    if np.sum(remaining) > 0:
        rem_bgr = img[remaining]
        rem_rgb = rem_bgr[:, ::-1]
        pal_rgb = np.array([p[:3] for p in PALETTE])
        dists = np.linalg.norm(rem_rgb[:, None, :] - pal_rgb[None, :, :], axis=2)
        best_pal = np.argmin(dists, axis=1)
        for p_idx, p_val in enumerate(PALETTE):
            mask_p = (best_pal == p_idx)
            coords = np.where(remaining)
            out[coords[0][mask_p], coords[1][mask_p]] = p_val

    # Tight crop around float bounds with 25px padding
    ys, xs = np.where(out[:, :, 3] > 0)
    min_x = max(0, xs.min() - 25)
    max_x = min(w, xs.max() + 25)
    min_y = max(0, ys.min() - 25)
    max_y = min(h, ys.max() + 25)
    cropped = out[min_y:max_y, min_x:max_x]

    # Save to canonical paths
    paths = [
        'assets/Drumcleanedup.png',
        'assets/drumcleanedup.png',
        'assets/title_drum.png',
        'assets/Drum.png',
        'simulator/assets/Drumcleanedup.png',
        'simulator/assets/drumcleanedup.png',
        'simulator/assets/title_drum.png'
    ]

    pil_crop = Image.fromarray(cropped)
    for p in paths:
        pil_crop.save(p)
        print(f"Saved: {p}")

    print(f"\nSuccessfully generated transparent drum PNG ({cropped.shape[1]}x{cropped.shape[0]}) with Hidden Mickey on yellow flag!")

if __name__ == '__main__':
    process_drum()
