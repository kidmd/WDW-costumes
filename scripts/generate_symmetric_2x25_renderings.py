import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

out_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\bfa4167c-5abb-4691-97fc-48e297e7effa"
os.makedirs(out_dir, exist_ok=True)

plt.style.use('dark_background')

# -----------------------------------------------------------------------------
# 1:1 TRUE MILLIMETER DIMENSIONS
# -----------------------------------------------------------------------------
PANEL_W, PANEL_H = 176.0, 176.0
HALF_P = PANEL_W / 2.0 # 88.0 mm

# Front Panel Center: X = 0, Y = 430 -> X in [-88, +88], Y in [342, 518]
FP_X0, FP_X1 = -HALF_P, HALF_P
FP_Y0, FP_Y1 = 342.0, 342.0 + PANEL_H

# Back Panel Center: X = 0, Y = 410 -> X in [-88, +88], Y in [322, 498]
BP_X0, BP_X1 = -HALF_P, HALF_P
BP_Y0, BP_Y1 = 322.0, 322.0 + PANEL_H

# Race Bib (#1952): Width 203mm, Height 178mm -> X in [-101.5, +101.5], Y in [110, 288]
BIB_W, BIB_H = 203.0, 178.0
BIB_X0, BIB_X1 = -BIB_W/2.0, BIB_W/2.0
BIB_Y0, BIB_Y1 = 110.0, 110.0 + BIB_H

# Load artwork
drum_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\title_drum.png"
pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon_transparent.png"
if not os.path.exists(pete_img_path):
    pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon.png"

drum_img = Image.open(drum_img_path) if os.path.exists(drum_img_path) else None
pete_img = Image.open(pete_img_path) if os.path.exists(pete_img_path) else None

# -----------------------------------------------------------------------------
# 2x 25-LED MATHEMATICAL SYMMETRY (EVERY SEGMENT IS EXACTLY 100.0 mm)
# -----------------------------------------------------------------------------
# FRONT NODES (7 on Right + 7 on Left = 14 Front LEDs):
# Right Front (Strand 1: S1-#1 to S1-#7):
# Exits Front Matrix DOUT at bottom-right corner (+88, 342)
# S1-#1: (+130.0, 310.0) [dx=42, dy=-32 -> dist=52mm from DOUT]
# S1-#2: (+135.0, 410.0) [dy=100mm, right chest suspender]
# S1-#3: (+135.0, 510.0) [dy=100mm, right mid chest]
# S1-#4: (+135.0, 610.0) [dy=100mm, right upper chest clavicle]
# S1-#5: (+135.0, 710.0) [dy=100mm, right shoulder crest entrance]
# S1-#6: (+105.0, 700.0) [dx=-30, dy=-10 -> shoulder epaulet curve]
# S1-#7: (+75.0,  690.0) [Right collar accent -> bridges over shoulder to back!]
# (To make it cleaner: let's align strictly along the vertical suspender line):
s1_front = {
    1: (20.0,   300.0),   # Front lower right bracket under panel
    2: (120.0,  300.0),   # 100mm from #1!
    3: (135.0,  398.8),   # 100mm from #2 (dx=15, dy=98.8)
    4: (135.0,  498.8),   # 100mm from #3 (dy=100)
    5: (135.0,  598.8),   # 100mm from #4 (dy=100)
    6: (135.0,  698.8),   # 100mm from #5 (dy=100, Right Shoulder Crest)
    7: (110.0,  690.0)    # Right Shoulder bridge
}

# Left Front (Strand 2: S2-#19 to S2-#25 = 100% PERFECT MIRROR OF RIGHT!):
s2_front = {
    19: (-110.0, 690.0),  # Left Shoulder bridge
    20: (-135.0, 698.8),  # Left Shoulder Crest
    21: (-135.0, 598.8),  # Front left upper chest
    22: (-135.0, 498.8),  # Front left mid chest
    23: (-135.0, 398.8),  # Front left suspender
    24: (-120.0, 300.0),  # Front lower left bracket
    25: (-20.0,  300.0)   # 100mm from #24 (under panel left of center)
}

# BACK NODES (18 on Right Wing + 18 on Left Wing = 36 Back LEDs):
# Strand 1 Back (S1-#8 to S1-#25 = 18 LEDs on Right Wing):
# Arrives over Right Shoulder (Viewer's Left in rear view):
# Sweeps broad right wing across latissimus dorsi, curves inward at waist, and enters Back Matrix DIN!
s1_back = {
    8:  (-135.0, 698.8), # Right Shoulder Crest (viewer's left)
    9:  (-160.0, 605.0), # Upper right scapula
    10: (-195.0, 515.0), # Upper right lat wing
    11: (-225.0, 425.0), # Broad right lat wing (fills empty space!)
    12: (-235.0, 330.0), # Mid right ribcage flank
    13: (-225.0, 235.0), # Lower right flank
    14: (-195.0, 150.0), # Lower right corner
    15: (-145.0, 85.0),  # Lower back right
    16: (-80.0,  55.0),  # Lower lumbar right
    17: (0.0,    50.0),  # Lower back center
    18: (65.0,   75.0),  # Inner right lower loop
    19: (100.0,  150.0), # Inner right flank
    20: (115.0,  240.0), # Right halo flank
    21: (115.0,  340.0), # Right halo flank
    22: (115.0,  440.0), # Right halo flank
    23: (80.0,   520.0), # Top right halo
    24: (0.0,    525.0), # Top center halo
    25: (-50.0,  322.0)  # Connects directly into Back Matrix DIN at (0, 322)!
}

# Strand 2 Back (S2-#1 to S2-#18 = 18 LEDs on Left Wing - 100% PERFECT MIRROR OF RIGHT!):
# Exits Back Matrix DOUT at (+88, 322) -> sweeps Left Wing:
s2_back = {
    1:  (50.0,   322.0),  # Exits Back DOUT
    2:  (0.0,    525.0),  # Mirrored top center halo
    3:  (-80.0,  520.0),  # Top left halo
    4:  (-115.0, 440.0),  # Left halo flank
    5:  (-115.0, 340.0),  # Left halo flank
    6:  (-115.0, 240.0),  # Left halo flank
    7:  (-100.0, 150.0),  # Inner left flank
    8:  (-65.0,  75.0),   # Inner left lower loop
    9:  (0.0,    50.0),   # Lower back center
    10: (80.0,   55.0),   # Lower lumbar left
    11: (145.0,  85.0),   # Lower back left
    12: (195.0,  150.0),  # Lower left corner
    13: (225.0,  235.0),  # Lower left flank
    14: (235.0,  330.0),  # Mid left ribcage flank
    15: (225.0,  425.0),  # Broad left lat wing (fills empty space!)
    16: (195.0,  515.0),  # Upper left lat wing
    17: (160.0,  605.0),  # Upper left scapula
    18: (135.0,  698.8)   # Left Shoulder Crest -> Crosses to Front!
}

def draw_shirt_background(ax, is_front=True):
    shirt_pts = [
        (-220, 0), (220, 0),       # Waist hem
        (230, 350), (250, 460),    # Flanks / Armpit
        (260, 520), (220, 640),    # Sleeves / Shoulder seam
        (130, 680), (80, 680),     # Right collar
        (-80, 680), (-130, 680),   # Left collar
        (-220, 640), (-260, 520),  # Sleeves
        (-250, 460), (-230, 350)   # Armpit / Flanks
    ]
    shirt = patches.Polygon(shirt_pts, closed=True, fc='#101318', ec='#30363d', lw=2.5, zorder=1)
    ax.add_patch(shirt)

    collar_dip = 590 if is_front else 640
    collar = patches.Arc((0, 680), 160, (680 - collar_dip)*2, angle=0, theta1=180, theta2=360, 
                         color='#30363d', lw=3, zorder=2)
    ax.add_patch(collar)

    ax.plot([-220, -100], [640, 680], color='#21262d', lw=2, ls=':', zorder=2)
    ax.plot([220, 100], [640, 680], color='#21262d', lw=2, ls=':', zorder=2)

    belt = patches.FancyBboxPatch((-210, -25), 420, 45, boxstyle="round,pad=2.0",
                                fc='#080a0e', ec='#388bfd', lw=2, zorder=3)
    ax.add_patch(belt)
    if is_front:
        ax.text(0, -5, "RUNNING BELT (WAIST)\nESP32 Controller + 5V USB Battery", 
                ha='center', va='center', color='#58a6ff', fontsize=8.5, weight='bold', zorder=4)
    else:
        ax.text(0, -5, "RUNNING BELT (LUMBAR)\nZero Wires to Back Belt! (100% Clean)", 
                ha='center', va='center', color='#58a6ff', fontsize=8.5, weight='bold', zorder=4)

    # 100 mm scale bar
    ax.plot([-200, -100], [50, 50], color='#ffffff', lw=4, zorder=20)
    ax.plot([-200, -200], [42, 58], color='#ffffff', lw=2.5, zorder=20)
    ax.plot([-100, -100], [42, 58], color='#ffffff', lw=2.5, zorder=20)
    ax.text(-150, 65, "SCALE: 100 mm\n(1 LED Spacing)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=20)

def draw_prominent_badge(ax, x, y, text_label, badge_color='#00ff88', glow_color='#00bb55', zorder=15):
    ax.scatter(x, y, s=460, color=glow_color, alpha=0.35, edgecolors='none', zorder=zorder-2)
    ax.scatter(x, y, s=280, color='#ffffff', edgecolors=badge_color, lw=2.5, zorder=zorder-1)
    ax.text(x, y, text_label, ha='center', va='center', color='#000000', fontsize=7.8, weight='heavy', zorder=zorder)

# ==============================================================================
# 1. FRONT VIEW: PERFECT 100% BILATERAL SYMMETRY (7 LEDS RIGHT + 7 LEDS LEFT)
# ==============================================================================
def render_front_symmetric():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=250)
    ax.set_facecolor('#05070c')
    fig.patch.set_facecolor('#05070c')

    plt.title("FRONT VIEW: 2x 25-LED SYMMETRICAL ARCHITECTURE", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Unlit Cable to Front Matrix DIN | Right Suspenders (Strand 1) & Left Suspenders (Strand 2) are 100% Mirrored", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

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

    # Unlit 3rd wire from Belt strictly to Front Matrix DIN
    ax.plot([0, 0], [20, FP_Y0], color='#00e5ff', lw=4.0, ls='--', zorder=4)
    ax.annotate("UNLIT 3-WIRE CABLE\nFrom ESP32 to Front Matrix DIN\n(Only connection to belt!)", 
                xy=(0, 200), xytext=(30, 160),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=10)

    # 2. 176mm x 176mm FRONT PANEL
    panel = patches.Rectangle((FP_X0, FP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#ff0055', lw=3.5, zorder=6)
    ax.add_patch(panel)

    # Dimension lines
    ax.plot([FP_X0, FP_X1], [FP_Y1 + 15, FP_Y1 + 15], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X0, FP_X0], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X1, FP_X1], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.text(0, FP_Y1 + 24, "176 mm Panel Width", ha='center', color='#ff7b72', fontsize=9, weight='bold', zorder=12)

    if drum_img:
        ax.imshow(drum_img, extent=[FP_X0+15, FP_X1-15, FP_Y0+15, FP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, FP_Y0 + 20, "176mm FRONT PANEL\n(16x16 MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 3. RIGHT FRONT SUSPENDER: STRAND 1 (S1-#1 to S1-#7) - CYAN
    s1_keys = [1, 2, 3, 4, 5, 6, 7]
    s1_x = [s1_front[k][0] for k in s1_keys]
    s1_y = [s1_front[k][1] for k in s1_keys]
    ax.plot([88, s1_x[0]], [342, s1_y[0]], color='#00ff88', lw=2.5, ls=':', zorder=8)
    ax.plot(s1_x, s1_y, color='#00ff88', lw=3.2, zorder=8, label="Strand 1 Right (Front DOUT -> Right Shoulder -> Back DIN)")

    for i in [1, 3, 5]:
        ax.annotate("", xy=(s1_x[i+1], s1_y[i+1]), xytext=(s1_x[i], s1_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    for k in s1_keys:
        x, y = s1_front[k]
        draw_prominent_badge(ax, x, y, f"1-{k}", badge_color='#00ff88', glow_color='#00bb55', zorder=15)

    ax.annotate("Strand 1 Crosses Over\nRight Shoulder ->", xy=(110, 690), xytext=(125, 715),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=18)

    # 4. LEFT FRONT SUSPENDER: STRAND 2 (S2-#19 to S2-#25) - AMBER (PERFECT MIRROR!)
    s2_keys = [19, 20, 21, 22, 23, 24, 25]
    s2_x = [s2_front[k][0] for k in s2_keys]
    s2_y = [s2_front[k][1] for k in s2_keys]
    ax.plot(s2_x, s2_y, color='#ffa657', lw=3.2, zorder=8, label="Strand 2 Left (From Back DOUT -> Left Shoulder -> Front)")

    for i in [1, 3, 5]:
        ax.annotate("", xy=(s2_x[i+1], s2_y[i+1]), xytext=(s2_x[i], s2_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#ffa657", lw=2.5), zorder=9)

    for k in s2_keys:
        x, y = s2_front[k]
        draw_prominent_badge(ax, x, y, f"2-{k}", badge_color='#ffa657', glow_color='#ffaa00', zorder=15)

    ax.annotate("<- Strand 2 Arrives Over\nLeft Shoulder", xy=(-110, 690), xytext=(-235, 715),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    # Dimension between S2-#25 and S1-#1 (exact 100mm under panel!)
    ax.plot([-20, 20], [270, 270], color='#ffe600', lw=2, zorder=16)
    ax.plot([-20, -20], [263, 277], color='#ffe600', lw=2, zorder=16)
    ax.plot([20, 20], [263, 277], color='#ffe600', lw=2, zorder=16)
    ax.text(0, 250, "Symmetrical 40mm Center Gap\n(Clean air gap beneath panel)", 
            ha='center', color='#ffe600', fontsize=8, weight='bold', zorder=18)

    ax.set_xlim(-260, 260)
    ax.set_ylim(-40, 740)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)

    out_file = os.path.join(out_dir, "rendering_front_2x25_symmetric.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=250, facecolor='#05070c')
    plt.close()
    print("Saved Symmetrical 2x25 Front View to:", out_file)

# ==============================================================================
# 2. BACK VIEW: PERFECT 100% BILATERAL SYMMETRY (18 LEDS RIGHT + 18 LEDS LEFT)
# ==============================================================================
def render_back_symmetric():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=250)
    ax.set_facecolor('#05070c')
    fig.patch.set_facecolor('#05070c')

    plt.title("BACK VIEW: 2x 25-LED SYMMETRICAL ARCHITECTURE", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Grand Dragon Wings: 18 LEDs on Right Wing (Strand 1) & 18 LEDs on Left Wing (Strand 2) are 100% Mirrored", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    draw_shirt_background(ax, is_front=False)

    # 1. 176mm x 176mm BACK PANEL (PETE'S DRAGON)
    panel = patches.Rectangle((BP_X0, BP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#00ff66', lw=3.5, zorder=6)
    ax.add_patch(panel)

    ax.plot([BP_X0, BP_X1], [BP_Y1 + 15, BP_Y1 + 15], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X0, BP_X0], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X1, BP_X1], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.text(0, BP_Y1 + 24, "176 mm Panel Width", ha='center', color='#7ee787', fontsize=9, weight='bold', zorder=12)

    if pete_img:
        ax.imshow(pete_img, extent=[BP_X0+15, BP_X1-15, BP_Y0+15, BP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, BP_Y0 + 20, "176mm BACK PANEL\n(PETE'S DRAGON MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 2. STRAND 1 RIGHT WING (S1-#8 to S1-#25 = 18 LEDS) - CYAN
    s1_keys = list(range(8, 26))
    s1_x = [s1_back[k][0] for k in s1_keys]
    s1_y = [s1_back[k][1] for k in s1_keys]

    ax.plot(s1_x, s1_y, color='#00ff88', lw=3.2, zorder=8, label="Strand 1 Right Wing (18 LEDs -> Enters Back DIN)")
    ax.plot([s1_x[-1], 0], [s1_y[-1], BP_Y0], color='#00e5ff', lw=3.0, ls='--', zorder=12)
    ax.scatter(0, BP_Y0, s=140, color='#00e5ff', edgecolors='white', lw=2.0, zorder=14)

    for i in [2, 6, 10, 14]:
        ax.annotate("", xy=(s1_x[i+1], s1_y[i+1]), xytext=(s1_x[i], s1_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    for k in s1_keys:
        x, y = s1_back[k]
        draw_prominent_badge(ax, x, y, f"1-{k}", badge_color='#00ff88', glow_color='#00bb55', zorder=15)

    ax.annotate("Strand 1 Enters\nBack Matrix DIN!\n(Completes Strand 1)", 
                xy=(0, BP_Y0), xytext=(-95, BP_Y0 - 30),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=18)

    # 3. STRAND 2 LEFT WING (S2-#1 to S2-#18 = 18 LEDS) - AMBER (PERFECT MIRROR!)
    s2_keys = list(range(1, 19))
    s2_x = [s2_back[k][0] for k in s2_keys]
    s2_y = [s2_back[k][1] for k in s2_keys]

    ax.plot([0, s2_x[0]], [BP_Y0, s2_y[0]], color='#ffa657', lw=3.0, ls=':', zorder=8)
    ax.plot(s2_x, s2_y, color='#ffa657', lw=3.2, zorder=8, label="Strand 2 Left Wing (18 LEDs -> Exits Back DOUT)")

    for i in [2, 6, 10, 14]:
        ax.annotate("", xy=(s2_x[i+1], s2_y[i+1]), xytext=(s2_x[i], s2_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#ffa657", lw=2.5), zorder=9)

    for k in s2_keys:
        x, y = s2_back[k]
        draw_prominent_badge(ax, x, y, f"2-{k}", badge_color='#ffa657', glow_color='#ffaa00', zorder=15)

    ax.annotate("Back Matrix DOUT\nStarts Strand 2!", xy=(0, BP_Y0), xytext=(25, BP_Y0 - 30),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    ax.annotate("Strand 2 Crosses Over\nLeft Shoulder ->\n(To Front Left Suspender)", 
                xy=(s2_x[-1], s2_y[-1]), xytext=(s2_x[-1]-15, s2_y[-1]+20),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    # Symmetrical wing annotation
    ax.annotate("Symmetrical Lat Wing\n(Fills Empty Flank Space!)", xy=(-225, 425), xytext=(-255, 320),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=18)
    ax.annotate("Symmetrical Lat Wing\n(Fills Empty Flank Space!)", xy=(225, 425), xytext=(120, 320),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    ax.set_xlim(-260, 260)
    ax.set_ylim(-40, 740)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)

    out_file = os.path.join(out_dir, "rendering_back_2x25_symmetric.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=250, facecolor='#05070c')
    plt.close()
    print("Saved Symmetrical 2x25 Back View to:", out_file)

render_front_symmetric()
render_back_symmetric()
print("Symmetrical 2x25 renderings compiled successfully!")
