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
    PALETTE = [
        (17, 22, 29, 255),    # Black:  #11161d
        (250, 204, 21, 255),  # Gold:   #facc15
        (239, 68, 68, 255),   # Red:    #ef4444
        (37, 99, 235, 255),   # Blue:   #2563eb
        (16, 185, 129, 255)   # Green:  #10b981
    ]

    # 1. Erase the front/right flag and flagpole completely down to the fender shelf
    # Pole was at x in [2180, 2210], extending up to y = 430
    # Flag was at x >= 1800, y <= 1000
    # The fender surface at the socket junction is at y ~ 1276.
    # We erase x >= 1800 with y <= 1276, and cleanly smooth the fender top contour across [2170, 2220]
    erase_mask = np.zeros((h, w), dtype=bool)
    erase_mask[0:1276, 1800:] = True
    img[erase_mask] = [255, 255, 255] # White background

    # Smooth the fender contour between x=2170 and x=2220 along y(x) = 1275 + (x - 2170) * (3.0 / 50.0)
    for x in range(2170, 2221):
        target_y = int(round(1275.0 + (x - 2170) * (3.0 / 50.0)))
        img[0:target_y, x] = [255, 255, 255]

    # 2. Base Color Classification
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    is_bg = (hsv[:, :, 1] < 40) & (hsv[:, :, 2] > 200)

    # Classify foreground regions
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

    # 3. Transform the large square flag on the cab roof:
    # Outer flag quad corners: [158, 545], [454, 630], [393, 905], [107, 832]
    outer_flag_mask = np.zeros((h, w), dtype=np.uint8)
    quad_pts = np.array([[158, 545], [454, 630], [393, 905], [107, 832]], dtype=np.int32)
    cv2.fillPoly(outer_flag_mask, [quad_pts], 255)

    # Gold border: Set entire flag quad to Gold
    out[outer_flag_mask > 0] = PALETTE[1] # Gold

    # Black interior: 18px inward morphological erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (37, 37))
    inner_black_mask = cv2.erode(outer_flag_mask, kernel)
    out[inner_black_mask > 0] = PALETTE[0] # Black

    # 4. Red Hidden Mickey silhouette inside the square flag
    # Centered along tilted flag axis (16.0 deg)
    C = np.array([278.0, 728.0])
    v_down = np.array([-np.sin(np.radians(16.0)), np.cos(np.radians(16.0))])
    C_mickey = C + 14.0 * v_down
    cx_m, cy_m = int(round(C_mickey[0])), int(round(C_mickey[1]))

    r_head = 44
    r_ear = 25
    dist_ear = 59
    ear_angle = np.radians(55.0)

    u_ear = np.array([np.cos(np.radians(16.0)), np.sin(np.radians(16.0))])
    v_ear_up = np.array([np.sin(np.radians(16.0)), -np.cos(np.radians(16.0))])

    # Left & right ears
    ear_l = C_mickey - dist_ear * np.sin(ear_angle) * u_ear + dist_ear * np.cos(ear_angle) * v_ear_up
    ear_r = C_mickey + dist_ear * np.sin(ear_angle) * u_ear + dist_ear * np.cos(ear_angle) * v_ear_up

    mickey_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mickey_mask, (cx_m, cy_m), r_head, 255, -1, cv2.LINE_AA)
    cv2.circle(mickey_mask, (int(round(ear_l[0])), int(round(ear_l[1]))), r_ear, 255, -1, cv2.LINE_AA)
    cv2.circle(mickey_mask, (int(round(ear_r[0])), int(round(ear_r[1]))), r_ear, 255, -1, cv2.LINE_AA)

    out[mickey_mask > 0] = PALETTE[2] # Red

    # 5. Crop with 25px padding
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

    print(f"\nCropped size: {cropped.shape[1]}x{cropped.shape[0]} (aspect ratio {cropped.shape[1]/cropped.shape[0]:.4f})")
    print(f"Successfully generated transparent drum PNG with Red Hidden Mickey on gold/black square flag and removed front pole!")

if __name__ == '__main__':
    process_drum()
