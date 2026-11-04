import cv2
import numpy as np

def build_lightning_bug():
    # Load transparent image
    img = cv2.imread('assets/lightningbug_transparent.png', cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]

    a = img[:, :, 3]
    fg_mask = a > 100
    r = img[:, :, 2].astype(int)
    g = img[:, :, 1].astype(int)
    b = img[:, :, 0].astype(int)

    # Detect outlines in 1x
    is_black = fg_mask & (r < 75) & (g < 75) & (b < 75)
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    is_black_closed = cv2.dilate(is_black.astype(np.uint8), k3).astype(bool)

    non_black = (fg_mask & ~is_black_closed).astype(np.uint8) * 255
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(non_black, connectivity=4)

    # 1x Color masks:
    m_red = np.zeros((h, w), dtype=bool)
    m_yellow = np.zeros((h, w), dtype=bool)
    m_blue = np.zeros((h, w), dtype=bool)
    m_green = np.zeros((h, w), dtype=bool)

    # Tail:
    m_red[labels == 80] = True

    # Tail Tip Dome (Amber / Yellow glowing tail lantern):
    m_yellow[labels == 69] = True
    m_yellow[labels == 71] = True

    # Crown Cap on head:
    m_red[labels == 19] = True

    # Antennae rays:
    m_yellow[labels == 2] = True
    m_yellow[labels == 7] = True

    # Open Smiling Mouth:
    m_red[labels == 88] = True

    # Belly Yellow Bands:
    m_yellow[labels == 96] = True
    m_yellow[labels == 87] = True
    m_yellow[labels == 123] = True

    # Snout / Nose facet:
    m_yellow[labels == 74] = True

    # Wing:
    wing_raw = (labels == 8) | (labels == 33)
    k_wclose = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    wing_closed = cv2.morphologyEx(wing_raw.astype(np.uint8), cv2.MORPH_CLOSE, k_wclose)
    cnts, _ = cv2.findContours(wing_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c_wing = max(cnts, key=cv2.contourArea)

    wing_solid = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(wing_solid, [c_wing], -1, 255, -1)
    wing_solid_mask = (wing_solid > 0) & fg_mask & ~m_red & ~m_yellow

    # Erode wing by 6px for yellow outer rim vs solid blue interior:
    k_rim = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    wing_blue = cv2.erode(wing_solid, k_rim) > 0
    wing_yellow = wing_solid_mask & ~wing_blue

    m_yellow[wing_yellow] = True
    m_blue[wing_blue] = True

    # All remaining foreground is Green (head, cheeks, neck, mid-body ribs, skirt, feet):
    assigned = m_red | m_yellow | m_blue
    m_green[fg_mask & ~assigned] = True

    # -------------------------------------------------------------
    # 4x Supersampling & Organic Levelset Smoothing
    # -------------------------------------------------------------
    SCALE = 4
    H4, W4 = h * SCALE, w * SCALE

    up_fg = cv2.resize(fg_mask.astype(np.float32), (W4, H4), interpolation=cv2.INTER_LINEAR)
    total_fg_smooth = cv2.GaussianBlur(up_fg, (17, 17), 0) >= 0.45

    # Probability fields for the 4 fill colors
    p_green = cv2.GaussianBlur(cv2.resize(m_green.astype(np.float32), (W4, H4)), (19, 19), 0)
    p_red = cv2.GaussianBlur(cv2.resize(m_red.astype(np.float32), (W4, H4)), (19, 19), 0)
    p_yellow = cv2.GaussianBlur(cv2.resize(m_yellow.astype(np.float32), (W4, H4)), (19, 19), 0)
    p_blue = cv2.GaussianBlur(cv2.resize(m_blue.astype(np.float32), (W4, H4)), (19, 19), 0)

    prob_stack = np.stack([p_green, p_red, p_yellow, p_blue], axis=2)
    class_map = np.argmax(prob_stack, axis=2) # 0: Green, 1: Red, 2: Yellow, 3: Blue

    # Strict Palette (RGB format)
    C_BLACK  = np.array([20, 20, 20], dtype=np.uint8)   # #141414
    C_GREEN  = np.array([34, 197, 94], dtype=np.uint8)  # #22c55e
    C_RED    = np.array([230, 25, 25], dtype=np.uint8)  # #e61919
    C_YELLOW = np.array([250, 204, 21], dtype=np.uint8) # #facc15
    C_BLUE   = np.array([37, 99, 235], dtype=np.uint8)  # #2563eb

    color_lut = np.array([C_GREEN, C_RED, C_YELLOW, C_BLUE], dtype=np.uint8)
    out_rgb = color_lut[class_map]

    # -------------------------------------------------------------
    # Bold Black Cartoon Outlines & Feature Masks (Strictly Binary)
    # -------------------------------------------------------------
    grad_x = np.abs(class_map[:, 1:] - class_map[:, :-1]) > 0
    grad_y = np.abs(class_map[1:, :] - class_map[:-1, :]) > 0

    is_boundary = np.zeros((H4, W4), dtype=bool)
    is_boundary[:, 1:] |= grad_x
    is_boundary[1:, :] |= grad_y

    k_out = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    outer_rim = total_fg_smooth & ~cv2.erode(total_fg_smooth.astype(np.uint8), k_out).astype(bool)

    k_stroke = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    bold_lines = cv2.dilate(is_boundary.astype(np.uint8), k_stroke).astype(bool) & total_fg_smooth
    black_mask = bold_lines | outer_rim

    # Tail Accordion Stripes (binary mask strictly inside red tail)
    tail_stripes = [
        np.array([(45*SCALE, 210*SCALE), (75*SCALE, 203*SCALE), (105*SCALE, 206*SCALE)], dtype=np.int32),
        np.array([(48*SCALE, 250*SCALE), (80*SCALE, 240*SCALE), (115*SCALE, 245*SCALE)], dtype=np.int32),
        np.array([(55*SCALE, 295*SCALE), (90*SCALE, 285*SCALE), (125*SCALE, 290*SCALE)], dtype=np.int32)
    ]
    stripe_mask = np.zeros((H4, W4), dtype=np.uint8)
    for st in tail_stripes:
        cv2.polylines(stripe_mask, [st], isClosed=False, color=255, thickness=int(2.5 * SCALE))
    black_mask |= (stripe_mask > 0) & total_fg_smooth & (class_map == 1)

    # Wing cartoon swirl loop inside blue wing (binary mask)
    swirl_pts = np.array([
        (100*SCALE, 80*SCALE), (115*SCALE, 65*SCALE), (130*SCALE, 80*SCALE), (135*SCALE, 115*SCALE),
        (125*SCALE, 150*SCALE), (108*SCALE, 165*SCALE), (95*SCALE, 145*SCALE), (105*SCALE, 105*SCALE), (120*SCALE, 100*SCALE)
    ], dtype=np.int32)
    swirl_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.polylines(swirl_mask, [swirl_pts], isClosed=False, color=255, thickness=int(2.5 * SCALE))
    black_mask |= (swirl_mask > 0) & total_fg_smooth

    # Crown lines on Red Cap
    crown_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.line(crown_mask, (185*SCALE, 55*SCALE), (200*SCALE, 105*SCALE), 255, int(2.0 * SCALE))
    cv2.line(crown_mask, (215*SCALE, 45*SCALE), (225*SCALE, 105*SCALE), 255, int(2.0 * SCALE))
    black_mask |= (crown_mask > 0) & total_fg_smooth & (class_map == 1)

    # Dimple at corner of mouth
    dimple = np.array([(255*SCALE, 205*SCALE), (262*SCALE, 218*SCALE), (258*SCALE, 230*SCALE)], dtype=np.int32)
    dimple_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.polylines(dimple_mask, [dimple], isClosed=False, color=255, thickness=int(2.2 * SCALE))
    black_mask |= (dimple_mask > 0) & total_fg_smooth

    # Apply all cartoon black outlines
    out_rgb[black_mask] = C_BLACK

    # -------------------------------------------------------------
    # Cartoon Eye (Centered at Float Socket x: 328, y: 124)
    # -------------------------------------------------------------
    eye_cx = int(328 * SCALE)
    eye_cy = int(124 * SCALE)
    sclera_rx = int(19 * SCALE)
    sclera_ry = int(26 * SCALE)
    angle = -15

    # 1. Yellow Sclera Fill
    sclera_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.ellipse(sclera_mask, (eye_cx, eye_cy), (sclera_rx, sclera_ry), angle, 0, 360, 255, -1)
    out_rgb[sclera_mask > 0] = C_YELLOW

    # 2. Sclera Outer Black Rim
    sclera_rim = np.zeros((H4, W4), dtype=np.uint8)
    cv2.ellipse(sclera_rim, (eye_cx, eye_cy), (sclera_rx, sclera_ry), angle, 0, 360, 255, int(3.0 * SCALE))
    out_rgb[sclera_rim > 0] = C_BLACK

    # 3. Blue Iris Fill
    iris_cx = eye_cx + int(2 * SCALE)
    iris_cy = eye_cy + int(2 * SCALE)
    iris_r = int(11 * SCALE)
    iris_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.circle(iris_mask, (iris_cx, iris_cy), iris_r, 255, -1)
    out_rgb[iris_mask > 0] = C_BLUE

    # 4. Iris Black Rim
    iris_rim = np.zeros((H4, W4), dtype=np.uint8)
    cv2.circle(iris_rim, (iris_cx, iris_cy), iris_r, 255, int(2.0 * SCALE))
    out_rgb[iris_rim > 0] = C_BLACK

    # 5. Black Pupil
    pupil_cx = eye_cx + int(3 * SCALE)
    pupil_cy = eye_cy + int(2 * SCALE)
    pupil_r = int(6.5 * SCALE)
    pupil_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.circle(pupil_mask, (pupil_cx, pupil_cy), pupil_r, 255, -1)
    out_rgb[pupil_mask > 0] = C_BLACK

    # 6. Yellow Catchlight Dot
    catch_cx = eye_cx + int(1 * SCALE)
    catch_cy = eye_cy - int(2 * SCALE)
    catch_r = int(2.5 * SCALE)
    catch_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.circle(catch_mask, (catch_cx, catch_cy), catch_r, 255, -1)
    out_rgb[catch_mask > 0] = C_YELLOW

    # 7. Eyelid Arch
    eyelid_mask = np.zeros((H4, W4), dtype=np.uint8)
    cv2.ellipse(eyelid_mask, (eye_cx, eye_cy - int(4 * SCALE)), (sclera_rx + int(2 * SCALE), sclera_ry), angle, 200, 340, 255, int(3.2 * SCALE))
    out_rgb[eyelid_mask > 0] = C_BLACK

    # -------------------------------------------------------------
    # Speckle Cleanup (< 150px Orphan Regions)
    # -------------------------------------------------------------
    min_area = 150
    for col in [C_GREEN, C_RED, C_YELLOW, C_BLUE]:
        m = (out_rgb[:, :, 0] == col[0]) & (out_rgb[:, :, 1] == col[1]) & (out_rgb[:, :, 2] == col[2]) & total_fg_smooth
        num, lbls, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
        for i in range(1, num):
            if st[i, cv2.CC_STAT_AREA] < min_area:
                comp_mask = (lbls == i).astype(np.uint8)
                dil = cv2.dilate(comp_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
                surround = (dil > 0) & (comp_mask == 0) & total_fg_smooth
                surr_pix = out_rgb[surround]
                if len(surr_pix) > 0:
                    unq, unq_cnt = np.unique(surr_pix.reshape(-1, 3), axis=0, return_counts=True)
                    best_col = unq[np.argmax(unq_cnt)]
                    out_rgb[comp_mask > 0] = best_col

    # -------------------------------------------------------------
    # Transparent Background & Cropping
    # -------------------------------------------------------------
    alpha = np.zeros((H4, W4), dtype=np.uint8)
    alpha[total_fg_smooth] = 255

    y_indices, x_indices = np.where(total_fg_smooth)
    pad = 40
    x1 = max(0, x_indices.min() - pad)
    y1 = max(0, y_indices.min() - pad)
    x2 = min(W4, x_indices.max() + pad + 1)
    y2 = min(H4, y_indices.max() + pad + 1)

    cropped_rgb = out_rgb[y1:y2, x1:x2]
    cropped_alpha = alpha[y1:y2, x1:x2]

    # Convert to BGRA for OpenCV saving
    out_bgra = cv2.merge([
        cropped_rgb[:, :, 2],
        cropped_rgb[:, :, 1],
        cropped_rgb[:, :, 0],
        cropped_alpha
    ])

    targets = [
        'assets/lightning_bug.png',
        'simulator/assets/lightning_bug.png',
        'assets/lightningbug_5color_production.png',
        'assets/lightningbug_clean_streamline.png'
    ]

    for p in targets:
        cv2.imwrite(p, out_bgra)
        print(f'Successfully wrote {p}, shape: {out_bgra.shape}')

if __name__ == '__main__':
    build_lightning_bug()
