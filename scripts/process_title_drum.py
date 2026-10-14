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

    # 1. Fit the central black drum face circle/ellipse to restore the exact round outer gold marquee ring
    hsv_orig = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    is_black_face = (hsv_orig[:, :, 2] < 50) & (hsv_orig[:, :, 1] < 100)
    drum_mask = np.zeros((h, w), dtype=np.uint8)
    drum_mask[500:1600, 650:1800] = is_black_face[500:1600, 650:1800]
    contours, _ = cv2.findContours(drum_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(contours, key=cv2.contourArea)
    ellipse = cv2.fitEllipse(c)
    (ecx, ecy), (e_w, e_h), e_ang = ellipse

    # Outer gold marquee ring: thickness is 66px -> expand axes by 132px
    gold_ring_outer = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(gold_ring_outer, ((ecx, ecy), (e_w + 132, e_h + 132), e_ang), 255, -1)

    # 2. Erase the front flagpole, swallowtail flag, and space outside the round drum ring down to the fender shelf
    # Streamer pole at x in [1760, 1780] remains untouched; front swallowtail starts at x >= 1785.
    erase = np.zeros((h, w), dtype=bool)
    erase[0:1276, 1785:] = True
    erase[gold_ring_outer > 0] = False # Protect the full circular drum marquee curve!
    img[erase] = [255, 255, 255]

    # Smooth the fender contour between x=2170 and x=2225 along y(x) = 1275 + (x - 2170) * (3.0 / 50.0)
    for x in range(2170, 2225):
        target_y = int(round(1275.0 + (x - 2170) * (3.0 / 50.0)))
        img[0:target_y, x] = [255, 255, 255]

    # 3. Base Color Classification
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    is_bg = (hsv[:, :, 1] < 40) & (hsv[:, :, 2] > 200)

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

    # 4. Fill the drum marquee ring with continuous, seamless solid Gold
    drum_ring_exact = (gold_ring_outer > 0) & (drum_mask == 0) & (np.arange(w)[None, :] >= 1650)
    out[drum_ring_exact] = PALETTE[1]

    # 5. Transform the large square flag on the cab roof:
    outer_flag_mask = np.zeros((h, w), dtype=np.uint8)
    quad_pts = np.array([[158, 545], [454, 630], [393, 905], [107, 832]], dtype=np.int32)
    cv2.fillPoly(outer_flag_mask, [quad_pts], 255)

    # Gold perimeter border: Set entire flag quad to Gold
    out[outer_flag_mask > 0] = PALETTE[1]

    # Black interior field: 18px inward morphological erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (37, 37))
    inner_black_mask = cv2.erode(outer_flag_mask, kernel)
    out[inner_black_mask > 0] = PALETTE[0]

    # 6. Red Hidden Mickey silhouette inside the square flag
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

    ear_l = C_mickey - dist_ear * np.sin(ear_angle) * u_ear + dist_ear * np.cos(ear_angle) * v_ear_up
    ear_r = C_mickey + dist_ear * np.sin(ear_angle) * u_ear + dist_ear * np.cos(ear_angle) * v_ear_up

    mickey_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mickey_mask, (cx_m, cy_m), r_head, 255, -1, cv2.LINE_AA)
    cv2.circle(mickey_mask, (int(round(ear_l[0])), int(round(ear_l[1]))), r_ear, 255, -1, cv2.LINE_AA)
    cv2.circle(mickey_mask, (int(round(ear_r[0])), int(round(ear_r[1]))), r_ear, 255, -1, cv2.LINE_AA)
    out[mickey_mask > 0] = PALETTE[2] # Red

    # 7. Crop with uniform 25px padding
    ys, xs = np.where(out[:, :, 3] > 0)
    min_x = max(0, xs.min() - 25)
    max_x = min(w, xs.max() + 25)
    min_y = max(0, ys.min() - 25)
    max_y = min(h, ys.max() + 25)
    cropped = out[min_y:max_y, min_x:max_x]

    # Save to canonical paths
    paths = [
        'assets/Drumcleanedup.png',
        'assets/title_drum.png',
        'assets/Drum.png',
        'simulator/assets/Drumcleanedup.png',
        'simulator/assets/title_drum.png'
    ]

    pil_crop = Image.fromarray(cropped)
    for p in paths:
        pil_crop.save(p)
        print(f"Saved: {p}")

    print(f"\nCropped size: {cropped.shape[1]}x{cropped.shape[0]} (aspect ratio {cropped.shape[1]/cropped.shape[0]:.4f})")
    print(f"Successfully generated transparent drum PNG with perfectly round gold drum edge and red hidden mickey!")

if __name__ == '__main__':
    process_drum()
