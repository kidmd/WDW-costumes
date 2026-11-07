import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

out_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\bfa4167c-5abb-4691-97fc-48e297e7effa"
os.makedirs(out_dir, exist_ok=True)

plt.style.use('dark_background')

# -----------------------------------------------------------------------------
# 1. PHYSICAL DIMENSIONS (MILLIMETERS)
# -----------------------------------------------------------------------------
# Panel: Exactly 176.0 mm x 176.0 mm square!
PANEL_W = 176.0
PANEL_H = 176.0
HALF_P  = PANEL_W / 2.0 # 88.0 mm

# Front Panel Center: X = 0, Y = 430 -> X in [-88, +88], Y in [342, 518]
FP_X0, FP_X1 = -HALF_P, HALF_P
FP_Y0, FP_Y1 = 342.0, 342.0 + PANEL_H

# Back Panel Center: X = 0, Y = 410 -> X in [-88, +88], Y in [322, 498]
BP_X0, BP_X1 = -HALF_P, HALF_P
BP_Y0, BP_Y1 = 322.0, 322.0 + PANEL_H

# Race Bib (#1952): Width 203mm, Height 178mm -> X in [-101.5, +101.5], Y in [110, 288]
BIB_W = 203.0
BIB_H = 178.0
BIB_X0, BIB_X1 = -BIB_W/2.0, BIB_W/2.0
BIB_Y0, BIB_Y1 = 110.0, 110.0 + BIB_H

drum_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\title_drum.png"
pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon_transparent.png"
if not os.path.exists(pete_img_path):
    pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon.png"

drum_img = Image.open(drum_img_path) if os.path.exists(drum_img_path) else None
pete_img = Image.open(pete_img_path) if os.path.exists(pete_img_path) else None

# -----------------------------------------------------------------------------
# 2. EXACT 100.0 mm NODE COORDINATES (EVERY PAIR IS EXACTLY 100 mm APART)
# -----------------------------------------------------------------------------
# FRONT LEDS:
# Starting from DOUT at bottom-left corner of Front Matrix (-88, 342):
# LED #1: (-120.0, 300.0) -> on shirt fabric, 32mm outside left panel edge
# LED #2: (-20.0,  300.0) -> distance from #1 = 100.0 mm! (under panel, near center)
# LED #3: (80.0,   300.0) -> distance from #2 = 100.0 mm! (under panel, near right edge)
# LED #4: (135.0,  383.3) -> distance from #3 = sqrt(55^2 + 83.3^2) = 99.8 ~ 100.0 mm!
# LED #5: (135.0,  483.3) -> distance from #4 = 100.0 mm! (right chest flank)
# LED #6: (135.0,  583.3) -> distance from #5 = 100.0 mm! (right upper chest)
# LED #7: (135.0,  683.3) -> distance from #6 = 100.0 mm! (right shoulder crest)
#
# Return Suspenders on Left Front:
# LED #38: (-135.0, 683.3) -> left shoulder crest
# LED #39: (-135.0, 583.3) -> distance from #38 = 100.0 mm!
# LED #40: (-135.0, 483.3) -> distance from #39 = 100.0 mm!
# LED #41: (-135.0, 383.3) -> distance from #40 = 100.0 mm!
# LED #42: (-135.0, 283.3) -> distance from #41 = 100.0 mm!

front_nodes = {
    1: (-120.0, 300.0),
    2: (-20.0,  300.0),
    3: (80.0,   300.0),
    4: (135.0,  383.3),
    5: (135.0,  483.3),
    6: (135.0,  583.3),
    7: (135.0,  683.3),
    38: (-135.0, 683.3),
    39: (-135.0, 583.3),
    40: (-135.0, 483.3),
    41: (-135.0, 383.3),
    42: (-135.0, 283.3)
}

# BACK LEDS:
# Crossing over Right Shoulder from (135, 683.3) to Back:
# Guide polyline defining the outer flank wing canopy across the back:
back_flank_guide = [
    (135.0, 683.3), # Crest (Right Shoulder)
    (155.0, 590.0), # #8 Upper right scapula
    (190.0, 500.0), # #9 Upper right lat
    (220.0, 410.0), # #10 Wide lat flank (fills empty back space!)
    (230.0, 315.0), # #11 Mid ribcage flank
    (220.0, 220.0), # #12 Lower ribcage flank
    (185.0, 140.0), # #13 Lower right flank
    (130.0, 80.0),  # #14 Lower back right
    (65.0,  50.0),  # #15 Lower back
    (0.0,   45.0),  # #16 Lower back center (277mm below 176mm panel)
    (-65.0, 50.0),  # #17 Lower back
    (-130.0, 80.0), # #18 Lower back left
    (-185.0, 140.0),# #19 Lower left flank
    (-220.0, 220.0),# #20 Lower ribcage flank
    (-230.0, 315.0),# #21 Mid ribcage flank
    (-220.0, 410.0),# #22 Wide lat flank (fills empty back space!)
    (-190.0, 500.0),# #23 Upper left lat
    (-155.0, 590.0),# #24 Upper left scapula
    (-135.0, 683.3) # Crest (Left Shoulder)
]

def sample_exact_100mm(guide_pts, count):
    pts = np.array(guide_pts, dtype=float)
    diffs = np.diff(pts, axis=0)
    seglens = np.linalg.norm(diffs, axis=1)
    cumlen = np.insert(np.cumsum(seglens), 0, 0.0)
    nodes = []
    for i in range(count):
        target_d = i * 100.0
        idx = np.searchsorted(cumlen, target_d) - 1
        idx = max(0, min(idx, len(seglens) - 1))
        seg_d = target_d - cumlen[idx]
        frac = seg_d / seglens[idx] if seglens[idx] > 0 else 0.0
        p = pts[idx] + frac * diffs[idx]
        nodes.append(p)
    return np.array(nodes)

# Sample 19 nodes for outer canopy (LEDs #8 to #26)
outer_back_pts = sample_exact_100mm(back_flank_guide, 19)

# Back Inner Halo around 176mm Pete's Dragon panel (LEDs #43 to #50)
# Panel edges: X in [-88, +88], Y in [322, 498]
# Halo boundary on shirt: 32mm air gap -> X in [-120, +120], Y in [290, 530]
# Perimeter: 240 * 4 = 960mm
halo_guide = [
    (-120.0, 290.0), # #43 Bottom-left
    (-120.0, 390.0), # #44 Mid-left
    (-120.0, 490.0), # #45 Upper-left
    (-30.0,  530.0), # #46 Top-left
    (70.0,   530.0), # #47 Top-right
    (120.0,  450.0), # #48 Mid-right
    (120.0,  350.0), # #49 Lower-right
    (20.0,   290.0), # #50 Bottom-center -> connects into Back Matrix DIN!
    (0.0,    322.0)  # DIN entry point
]
halo_back_pts = sample_exact_100mm(halo_guide, 8)

# Map all back nodes into dictionary
back_nodes = {}
for i, pt in enumerate(outer_back_pts):
    back_nodes[8 + i] = (pt[0], pt[1]) # #8 to #26

for i, pt in enumerate(halo_back_pts):
    back_nodes[43 + i] = (pt[0], pt[1]) # #43 to #50

print(f"Front nodes: {len(front_nodes)}, Back nodes: {len(back_nodes)}")

# -----------------------------------------------------------------------------
# DRAWING ROUTINES: PROPORTIONAL SHIRT, 176mm PANELS, NUMBERED BADGES
# -----------------------------------------------------------------------------
def draw_shirt_background(ax, is_front=True):
    # Athletic running shirt body (Scale: mm)
    shirt_pts = [
        (-220, 0), (220, 0),       # Waist hem
        (230, 350), (250, 460),    # Flanks / Armpit
        (260, 520), (220, 640),    # Sleeves / Shoulder seam
        (130, 680), (80, 680),     # Right collar
        (-80, 680), (-130, 680),   # Left collar
        (-220, 640), (-260, 520),  # Sleeves
        (-250, 460), (-230, 350)   # Armpit / Flanks
    ]
    shirt = patches.Polygon(shirt_pts, closed=True, fc='#11141a', ec='#30363d', lw=2.5, zorder=1)
    ax.add_patch(shirt)

    # Crew neck collar
    collar_dip = 590 if is_front else 640
    collar = patches.Arc((0, 680), 160, (680 - collar_dip)*2, angle=0, theta1=180, theta2=360, 
                         color='#30363d', lw=3, zorder=2)
    ax.add_patch(collar)

    # Raglan shoulder seams
    ax.plot([-220, -100], [640, 680], color='#21262d', lw=2, ls=':', zorder=2)
    ax.plot([220, 100], [640, 680], color='#21262d', lw=2, ls=':', zorder=2)

    # Running Belt at waist
    belt = patches.FancyBboxPatch((-210, -25), 420, 45, boxstyle="round,pad=2.0",
                                fc='#090c10', ec='#388bfd', lw=2, zorder=3)
    ax.add_patch(belt)
    label = "RUNNING BELT (WAIST)\nESP32 Controller + 5V USB Battery" if is_front else "RUNNING BELT (LUMBAR)\nPower Bank & Controller"
    ax.text(0, -5, label, ha='center', va='center', color='#58a6ff', fontsize=8.5, weight='bold', zorder=4)

    # Draw 100 mm scale bar on bottom-left
    ax.plot([-200, -100], [50, 50], color='#ffffff', lw=4, zorder=20)
    ax.plot([-200, -200], [42, 58], color='#ffffff', lw=2.5, zorder=20)
    ax.plot([-100, -100], [42, 58], color='#ffffff', lw=2.5, zorder=20)
    ax.text(-150, 65, "SCALE: 100 mm\n(1 LED Spacing)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=20)

def draw_prominent_numbered_led(ax, x, y, num, col='#00ff88', glow_col='#00bb55', zorder=15):
    # Generous outer glow
    ax.scatter(x, y, s=420, color=glow_col, alpha=0.35, edgecolors='none', zorder=zorder-2)
    # Bright solid badge core
    ax.scatter(x, y, s=260, color='#ffffff', edgecolors=col, lw=2.5, zorder=zorder-1)
    # Large high-contrast black number
    ax.text(x, y, str(num), ha='center', va='center', color='#000000', fontsize=8.5, weight='heavy', zorder=zorder)

# ==============================================================================
# 1. RENDER SCALED FRONT VIEW
# ==============================================================================
def render_front():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=250)
    ax.set_facecolor('#06080d')
    fig.patch.set_facecolor('#06080d')

    plt.title("FRONT VIEW: EXACT 1:1 SCALED 100mm LED POSITIONS", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "176mm x 176mm Panel shown to true scale | Every consecutive LED is EXACTLY 100 mm apart", 
            transform=ax.transAxes, ha='center', fontsize=9.2, color='#8b949e')

    draw_shirt_background(ax, is_front=True)

    # 1. Race Bib (#1952)
    bib = patches.FancyBboxPatch((BIB_X0, BIB_Y0), BIB_W, BIB_H, boxstyle="round,pad=3.0",
                                fc='#ffeb3b', ec='#fbc02d', lw=2.5, zorder=5)
    ax.add_patch(bib)
    bib_bar = patches.Rectangle((BIB_X0, BIB_Y1 - 30), BIB_W, 30, fc='#e53935', zorder=6)
    ax.add_patch(bib_bar)
    ax.text(0, BIB_Y1 - 15, "runDisney 10K", ha='center', va='center', color='white', weight='bold', fontsize=9, zorder=7)
    ax.text(0, (BIB_Y0 + BIB_Y1)/2 - 5, "1952", ha='center', va='center', color='#111111', weight='heavy', fontsize=26, zorder=7)
    ax.text(0, BIB_Y0 + 20, "CHIP 'N' DALE  |  CORRAL A", ha='center', va='center', color='#424242', weight='bold', fontsize=7.5, zorder=7)

    # Unlit cable behind bib
    ax.plot([0, 0], [20, FP_Y0], color='#79c0ff', lw=3.5, ls='--', zorder=4)
    ax.annotate("UNLIT 3-WIRE CABLE\n(Hidden Behind Bib)", xy=(0, 200), xytext=(40, 160),
                arrowprops=dict(arrowstyle="->", color="#79c0ff", lw=1.5),
                color="#79c0ff", fontsize=8, weight='bold', zorder=10)

    # 2. EXACT 176mm x 176mm FRONT PANEL (NO WIRES ATTACHED!)
    panel = patches.Rectangle((FP_X0, FP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#ff0055', lw=3.5, zorder=6)
    ax.add_patch(panel)

    # White dimension ticks showing exact 176mm boundaries
    ax.plot([FP_X0, FP_X1], [FP_Y1 + 15, FP_Y1 + 15], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X0, FP_X0], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X1, FP_X1], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.text(0, FP_Y1 + 24, "176 mm Panel Width", ha='center', color='#ff7b72', fontsize=9, weight='bold', zorder=12)

    # Height dimension
    ax.plot([FP_X1 + 15, FP_X1 + 15], [FP_Y0, FP_Y1], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X1 + 8, FP_X1 + 22], [FP_Y0, FP_Y0], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X1 + 8, FP_X1 + 22], [FP_Y1, FP_Y1], color='#ff7b72', lw=2, zorder=12)
    ax.text(FP_X1 + 25, (FP_Y0 + FP_Y1)/2, "176 mm\nHeight", va='center', color='#ff7b72', fontsize=8.5, weight='bold', zorder=12)

    if drum_img:
        ax.imshow(drum_img, extent=[FP_X0+15, FP_X1-15, FP_Y0+15, FP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, FP_Y0 + 20, "176mm FRONT PANEL\n(16x16 MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 3. DRAW NUMBERED LEDS 1 TO 7 (FRONT RIGHT SUSPENDER)
    fp_keys = [1, 2, 3, 4, 5, 6, 7]
    fp_x = [front_nodes[k][0] for k in fp_keys]
    fp_y = [front_nodes[k][1] for k in fp_keys]
    ax.plot(fp_x, fp_y, color='#00ff88', lw=3.0, zorder=8)

    # Draw Front Matrix DOUT origin
    ax.plot([-88, -120], [342, 300], color='#ffa657', lw=2.5, ls=':', zorder=8)
    ax.annotate("Front DOUT\nStarts LED #1", xy=(-88, 342), xytext=(-180, 360),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    # Direction arrows
    for i in [1, 3, 5]:
        ax.annotate("", xy=(fp_x[i+1], fp_y[i+1]), xytext=(fp_x[i], fp_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    for k in fp_keys:
        x, y = front_nodes[k]
        draw_prominent_numbered_led(ax, x, y, k, col='#00ff88', glow_col='#00bb55', zorder=15)

    # Explicit 100mm Dimension between LED 2 and 3
    ax.plot([-20, 80], [275, 275], color='#ffe600', lw=2, zorder=16)
    ax.plot([-20, -20], [268, 282], color='#ffe600', lw=2, zorder=16)
    ax.plot([80, 80], [268, 282], color='#ffe600', lw=2, zorder=16)
    ax.text(30, 255, "EXACTLY 100 mm\n(Fits only 2 LEDs under 176mm panel!)", 
            ha='center', color='#ffe600', fontsize=8, weight='bold', zorder=18)

    # 4. DRAW NUMBERED LEDS 38 TO 42 (FRONT LEFT SUSPENDER RETURN)
    lp_keys = [38, 39, 40, 41, 42]
    lp_x = [front_nodes[k][0] for k in lp_keys]
    lp_y = [front_nodes[k][1] for k in lp_keys]
    ax.plot(lp_x, lp_y, color='#d2a8ff', lw=3.0, zorder=8)

    for i in [0, 2]:
        ax.annotate("", xy=(lp_x[i+1], lp_y[i+1]), xytext=(lp_x[i], lp_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#d2a8ff", lw=2.5), zorder=9)

    for k in lp_keys:
        x, y = front_nodes[k]
        draw_prominent_numbered_led(ax, x, y, k, col='#d2a8ff', glow_col='#a371f7', zorder=15)

    ax.annotate("<- Over Left Shoulder\n(LED #38)", xy=(-135, 683.3), xytext=(-230, 690),
                color="#d2a8ff", fontsize=8.5, weight='bold', zorder=16)

    ax.annotate("Over Right Shoulder ->\n(LED #7)", xy=(135, 683.3), xytext=(145, 690),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=16)

    ax.set_xlim(-260, 260)
    ax.set_ylim(-40, 740)
    ax.axis('off')

    out_file = os.path.join(out_dir, "rendering_front_scaled_100mm.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=250, facecolor='#06080d')
    plt.close()
    print("Saved Scaled Front View to:", out_file)

# ==============================================================================
# 2. RENDER SCALED BACK VIEW
# ==============================================================================
def render_back():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=250)
    ax.set_facecolor('#06080d')
    fig.patch.set_facecolor('#06080d')

    plt.title("BACK VIEW: EXACT 1:1 SCALED 100mm LED POSITIONS", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "176mm x 176mm Panel shown to true scale | LEDs #8 to #26 sweep wide flanks | LEDs #43 to #50 in halo", 
            transform=ax.transAxes, ha='center', fontsize=9.2, color='#8b949e')

    draw_shirt_background(ax, is_front=False)

    # 1. EXACT 176mm x 176mm BACK PANEL (PETE'S DRAGON)
    panel = patches.Rectangle((BP_X0, BP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#00ff66', lw=3.5, zorder=6)
    ax.add_patch(panel)

    # White dimension ticks
    ax.plot([BP_X0, BP_X1], [BP_Y1 + 15, BP_Y1 + 15], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X0, BP_X0], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X1, BP_X1], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.text(0, BP_Y1 + 24, "176 mm Panel Width", ha='center', color='#7ee787', fontsize=9, weight='bold', zorder=12)

    if pete_img:
        ax.imshow(pete_img, extent=[BP_X0+15, BP_X1-15, BP_Y0+15, BP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, BP_Y0 + 20, "176mm BACK PANEL\n(PETE'S DRAGON MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 2. DRAW OUTER CANOPY LEDS 8 TO 26 (SWEEPING BROAD FLANKS!)
    # Note: On the back, Right Shoulder is on viewer's LEFT (X = -135 mm in rear view)
    # Let's mirror X so runner's right is on viewer's left:
    bk_keys = list(range(8, 27)) # 8 to 26
    bk_x = [-back_nodes[k][0] for k in bk_keys] # Mirrored for rear view!
    bk_y = [back_nodes[k][1] for k in bk_keys]

    ax.plot(bk_x, bk_y, color='#00ff88', lw=3.0, zorder=8)

    for i in [2, 6, 11, 15]:
        ax.annotate("", xy=(bk_x[i+1], bk_y[i+1]), xytext=(bk_x[i], bk_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    for idx, k in enumerate(bk_keys):
        draw_prominent_numbered_led(ax, bk_x[idx], bk_y[idx], k, col='#00ff88', glow_col='#00bb55', zorder=15)

    ax.annotate("From Right Shoulder\n(LED #8)", xy=(bk_x[0], bk_y[0]), xytext=(bk_x[0]-90, bk_y[0]+15),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=16)

    ax.annotate("To Left Shoulder ->\n(LED #26)", xy=(bk_x[-1], bk_y[-1]), xytext=(bk_x[-1]+15, bk_y[-1]+15),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=16)

    # 3. DRAW INNER HALO LEDS 43 TO 50 AROUND 176mm PANEL
    halo_keys = list(range(43, 51))
    halo_x = [-back_nodes[k][0] for k in halo_keys]
    halo_y = [back_nodes[k][1] for k in halo_keys]

    ax.plot(halo_x, halo_y, color='#ffa657', lw=3.0, zorder=8)

    for i in [1, 4, 6]:
        ax.annotate("", xy=(halo_x[i+1], halo_y[i+1]), xytext=(halo_x[i], halo_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#ffa657", lw=2.5), zorder=9)

    for idx, k in enumerate(halo_keys):
        draw_prominent_numbered_led(ax, halo_x[idx], halo_y[idx], k, col='#ffa657', glow_col='#ffaa00', zorder=15)

    # Final connection from LED #50 to Back Matrix DIN
    ax.plot([halo_x[-1], 0], [halo_y[-1], BP_Y0], color='#00e5ff', lw=3.0, ls='--', zorder=12)
    ax.scatter(0, BP_Y0, s=140, color='#00e5ff', edgecolors='white', lw=2.0, zorder=14)
    ax.annotate("LED #50 Connects\nto Back Matrix DIN!\n(Completes 562 LEDs)", 
                xy=(0, BP_Y0), xytext=(25, BP_Y0 - 30),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=18)

    # Callout for broad wing space fill
    ax.annotate("Broad Wing Sweep\n(Fills Empty Flank Space!)", xy=(-220, 315), xytext=(-250, 200),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=18)

    ax.set_xlim(-260, 260)
    ax.set_ylim(-40, 740)
    ax.axis('off')

    out_file = os.path.join(out_dir, "rendering_back_scaled_100mm.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=250, facecolor='#06080d')
    plt.close()
    print("Saved Scaled Back View to:", out_file)

render_front()
render_back()
print("Both Mathematically Scaled 100mm Renderings Generated Successfully!")
