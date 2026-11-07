import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

out_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\bfa4167c-5abb-4691-97fc-48e297e7effa"
os.makedirs(out_dir, exist_ok=True)

plt.style.use('dark_background')

# -----------------------------------------------------------------------------
# 1:1 MILLIMETER DIMENSIONS
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

# Load float artwork
drum_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\title_drum.png"
pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon_transparent.png"
if not os.path.exists(pete_img_path):
    pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon.png"

drum_img = Image.open(drum_img_path) if os.path.exists(drum_img_path) else None
pete_img = Image.open(pete_img_path) if os.path.exists(pete_img_path) else None

# -----------------------------------------------------------------------------
# 2-STRAND SERIAL TOPOLOGY (EXACT 100mm NODE COORDINATES)
# -----------------------------------------------------------------------------
# STRAND 1: Between Front and Back Panels (Right Shoulder Bridge)
# Starts at Front Matrix DOUT (-88, 342)
# Routes across lower chest (on shirt fabric 30mm below 176mm panel):
# S1-#1: (-120.0, 300.0) [Left chest flank]
# S1-#2: (-20.0,  300.0) [dx=100mm, under panel]
# S1-#3: (80.0,   300.0) [dx=100mm, under panel near right edge]
# S1-#4: (135.0,  383.3) [Right chest flank, 100mm from #3]
# S1-#5: (135.0,  483.3) [dy=100mm, right chest suspender]
# S1-#6: (135.0,  583.3) [dy=100mm, right upper chest clavicle]
# S1-#7: (135.0,  683.3) [dy=100mm, right shoulder crest]
# Transitions over Right Shoulder to Back:
# S1-#8: (120.0,  583.3 on back) [Upper right scapula]
# S1-#9: (100.0,  485.0 on back) [Right edge of Pete's Dragon panel]
# S1-#10: (50.0,  322.0 on back) [Enters Back Matrix DIN at (0, 322)!]
# Total Strand 1: 10 LEDs (exact 100mm intervals)

strand1_front = {
    1: (-120.0, 300.0),
    2: (-20.0,  300.0),
    3: (80.0,   300.0),
    4: (135.0,  383.3),
    5: (135.0,  483.3),
    6: (135.0,  583.3),
    7: (135.0,  683.3)
}

strand1_back = {
    8: (-135.0, 583.3),  # Mirrored X for rear view (runner's right = viewer's left)
    9: (-115.0, 485.0),
    10: (-60.0, 322.0)   # Plugs into Back Matrix DIN at X=0, Y=322!
}

# STRAND 2: Out from Back Panel DOUT (Fills Back Canopy & Over Left Shoulder!)
# Starts at Back Matrix DOUT (e.g. bottom-right of back panel X=88, Y=322, or X=-88 in rear view)
# Sweeps broad right flank, lower lumbar, wide left flank, and crosses over Left Shoulder!
# S2-#1: (-185.0, 250.0) [Lower right lat flank]
# S2-#2: (-220.0, 335.0) [Mid right flank wing]
# S2-#3: (-225.0, 435.0) [Upper right lat flank]
# S2-#4: (-195.0, 525.0) [Upper right scapula]
# S2-#5: (-140.0, 600.0) [Upper back right halo]
# S2-#6: (-40.0,  535.0) [Top halo above 176mm panel]
# S2-#7: (60.0,   535.0) [Top halo above 176mm panel]
# S2-#8: (140.0,  600.0) [Upper back left halo]
# S2-#9: (195.0,  525.0) [Upper left scapula]
# S2-#10: (225.0, 435.0) [Upper left lat flank]
# S2-#11: (220.0, 335.0) [Mid left flank wing]
# S2-#12: (185.0, 250.0) [Lower left lat flank]
# S2-#13: (130.0, 170.0) [Lower back curve]
# S2-#14: (50.0,  110.0) [Lower lumbar]
# S2-#15: (-50.0, 110.0) [Lower lumbar]
# S2-#16: (-130.0, 170.0) [Lower back curve]
# S2-#17: (-175.0, 250.0)
# S2-#18: (135.0, 683.3) [Left Shoulder Crest -> Crosses to Front!]
# S2-#19 to S2-#22: Descends Front Left Suspender on chest!

strand2_back = {
    1: (-185.0, 250.0),
    2: (-220.0, 335.0),
    3: (-225.0, 435.0),
    4: (-195.0, 525.0),
    5: (-140.0, 600.0),
    6: (-40.0,  535.0),
    7: (60.0,   535.0),
    8: (140.0,  600.0),
    9: (195.0,  525.0),
    10: (225.0, 435.0),
    11: (220.0, 335.0),
    12: (185.0, 250.0),
    13: (130.0, 170.0),
    14: (50.0,  110.0),
    15: (-50.0, 110.0),
    16: (135.0, 683.3) # Climbs to Left Shoulder Crest!
}

strand2_front = {
    17: (-135.0, 683.3), # Arrives over Left Shoulder crest
    18: (-135.0, 583.3), # Front left upper chest
    19: (-135.0, 483.3), # Front left mid chest suspender
    20: (-135.0, 383.3), # Front left lower chest suspender
    21: (-135.0, 283.3)  # Front left rib flank
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
    shirt = patches.Polygon(shirt_pts, closed=True, fc='#11141a', ec='#30363d', lw=2.5, zorder=1)
    ax.add_patch(shirt)

    collar_dip = 590 if is_front else 640
    collar = patches.Arc((0, 680), 160, (680 - collar_dip)*2, angle=0, theta1=180, theta2=360, 
                         color='#30363d', lw=3, zorder=2)
    ax.add_patch(collar)

    ax.plot([-220, -100], [640, 680], color='#21262d', lw=2, ls=':', zorder=2)
    ax.plot([220, 100], [640, 680], color='#21262d', lw=2, ls=':', zorder=2)

    belt = patches.FancyBboxPatch((-210, -25), 420, 45, boxstyle="round,pad=2.0",
                                fc='#090c10', ec='#388bfd', lw=2, zorder=3)
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
    ax.text(x, y, text_label, ha='center', va='center', color='#000000', fontsize=8.0, weight='heavy', zorder=zorder)

# ==============================================================================
# 1. FRONT VIEW: UNLIT TRUNK + STRAND 1 BRIDGE + STRAND 2 LEFT SUSPENDER
# ==============================================================================
def render_front():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=250)
    ax.set_facecolor('#06080d')
    fig.patch.set_facecolor('#06080d')

    plt.title("FRONT VIEW: 2-STRAND ARCHITECTURE (ONLY FRONT ATTACHED TO BELT)", 
              fontsize=14.0, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Unlit Wire from ESP32 -> Front Matrix DIN | Strand 1 (Cyan) to Back | Strand 2 (Amber) on Left", 
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

    # SEPARATE UNLIT 3RD WIRE (FROM BELT TO FRONT MATRIX ONLY!)
    ax.plot([0, 0], [20, FP_Y0], color='#00e5ff', lw=4.0, ls='--', zorder=4)
    ax.annotate("SEPARATE 3RD WIRE (UNLIT)\nFrom ESP32 to Front Matrix Only!\n(Hidden Completely Behind Bib)", 
                xy=(0, 200), xytext=(35, 170),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=10)

    # 2. 176mm x 176mm FRONT PANEL
    panel = patches.Rectangle((FP_X0, FP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#ff0055', lw=3.5, zorder=6)
    ax.add_patch(panel)

    # Dimension annotations
    ax.plot([FP_X0, FP_X1], [FP_Y1 + 15, FP_Y1 + 15], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X0, FP_X0], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X1, FP_X1], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.text(0, FP_Y1 + 24, "176 mm Panel Width", ha='center', color='#ff7b72', fontsize=9, weight='bold', zorder=12)

    if drum_img:
        ax.imshow(drum_img, extent=[FP_X0+15, FP_X1-15, FP_Y0+15, FP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, FP_Y0 + 20, "176mm FRONT PANEL\n(16x16 MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 3. STRAND 1: BETWEEN FRONT AND BACK PANELS (CYAN / GREEN)
    # Exits Front Matrix DOUT at bottom-left (-88, 342)
    s1_keys = [1, 2, 3, 4, 5, 6, 7]
    s1_x = [strand1_front[k][0] for k in s1_keys]
    s1_y = [strand1_front[k][1] for k in s1_keys]
    ax.plot([-88, -120], [342, 300], color='#00ff88', lw=2.5, ls=':', zorder=8)
    ax.plot(s1_x, s1_y, color='#00ff88', lw=3.0, zorder=8, label="Strand 1 (Front DOUT -> Right Shoulder -> Back DIN)")

    for i in [1, 3, 5]:
        ax.annotate("", xy=(s1_x[i+1], s1_y[i+1]), xytext=(s1_x[i], s1_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    for k in s1_keys:
        x, y = strand1_front[k]
        draw_prominent_badge(ax, x, y, f"1-{k}", badge_color='#00ff88', glow_color='#00bb55', zorder=15)

    ax.annotate("Front DOUT Connects\nto Strand 1 Start", xy=(-88, 342), xytext=(-190, 360),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=18)

    ax.annotate("Strand 1 Crosses\nOver Right Shoulder ->\n(To Back Matrix DIN)", xy=(135, 683.3), xytext=(145, 690),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=18)

    # Dimension between 1-2 and 1-3 (exact 100mm)
    ax.plot([-20, 80], [270, 270], color='#ffe600', lw=2, zorder=16)
    ax.plot([-20, -20], [263, 277], color='#ffe600', lw=2, zorder=16)
    ax.plot([80, 80], [263, 277], color='#ffe600', lw=2, zorder=16)
    ax.text(30, 250, "100 mm (Only 2 LEDs under 176mm panel)", 
            ha='center', color='#ffe600', fontsize=8, weight='bold', zorder=18)

    # 4. STRAND 2: ARRIVING OVER LEFT SHOULDER FROM BACK (AMBER / ORANGE)
    s2_keys = [17, 18, 19, 20, 21]
    s2_x = [strand2_front[k][0] for k in s2_keys]
    s2_y = [strand2_front[k][1] for k in s2_keys]
    ax.plot(s2_x, s2_y, color='#ffa657', lw=3.0, zorder=8, label="Strand 2 (From Back Matrix DOUT -> Left Shoulder)")

    for i in [0, 2]:
        ax.annotate("", xy=(s2_x[i+1], s2_y[i+1]), xytext=(s2_x[i], s2_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#ffa657", lw=2.5), zorder=9)

    for k in s2_keys:
        x, y = strand2_front[k]
        draw_prominent_badge(ax, x, y, f"2-{k}", badge_color='#ffa657', glow_color='#ffaa00', zorder=15)

    ax.annotate("<- Strand 2 Arrives\nOver Left Shoulder\n(From Back DOUT)", xy=(-135, 683.3), xytext=(-235, 690),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    ax.set_xlim(-260, 260)
    ax.set_ylim(-40, 740)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)

    out_file = os.path.join(out_dir, "rendering_front_two_strands.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=250, facecolor='#06080d')
    plt.close()
    print("Saved Two-Strand Front View to:", out_file)

# ==============================================================================
# 2. BACK VIEW: STRAND 1 ENTERS BACK DIN + STRAND 2 EXITS BACK DOUT
# ==============================================================================
def render_back():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=250)
    ax.set_facecolor('#06080d')
    fig.patch.set_facecolor('#06080d')

    plt.title("BACK VIEW: 2-STRAND ARCHITECTURE (STRAND 1 IN -> STRAND 2 OUT)", 
              fontsize=14.0, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Strand 1 enters Back DIN | Strand 2 exits Back DOUT to fill wide lat wings & cross Left Shoulder", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    draw_shirt_background(ax, is_front=False)

    # 1. 176mm x 176mm BACK PANEL (PETE'S DRAGON)
    panel = patches.Rectangle((BP_X0, BP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#00ff66', lw=3.5, zorder=6)
    ax.add_patch(panel)

    # Dimension annotations
    ax.plot([BP_X0, BP_X1], [BP_Y1 + 15, BP_Y1 + 15], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X0, BP_X0], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X1, BP_X1], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.text(0, BP_Y1 + 24, "176 mm Panel Width", ha='center', color='#7ee787', fontsize=9, weight='bold', zorder=12)

    if pete_img:
        ax.imshow(pete_img, extent=[BP_X0+15, BP_X1-15, BP_Y0+15, BP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, BP_Y0 + 20, "176mm BACK PANEL\n(PETE'S DRAGON MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 2. STRAND 1: ARRIVES FROM RIGHT SHOULDER -> ENTERS BACK MATRIX DIN
    s1_b_keys = [8, 9, 10]
    s1_bx = [strand1_back[k][0] for k in s1_b_keys]
    s1_by = [strand1_back[k][1] for k in s1_b_keys]
    # Connect from shoulder crest (-135, 683.3) down to DIN
    ax.plot([-135, s1_bx[0]], [683.3, s1_by[0]], color='#00ff88', lw=3.0, zorder=8)
    ax.plot(s1_bx, s1_by, color='#00ff88', lw=3.0, zorder=8, label="Strand 1 (From Right Shoulder -> Enters Back DIN)")
    ax.plot([s1_bx[-1], 0], [s1_by[-1], BP_Y0], color='#00e5ff', lw=3.0, ls='--', zorder=12)
    ax.scatter(0, BP_Y0, s=140, color='#00e5ff', edgecolors='white', lw=2.0, zorder=14)

    for k in s1_b_keys:
        x, y = strand1_back[k]
        draw_prominent_badge(ax, x, y, f"1-{k}", badge_color='#00ff88', glow_color='#00bb55', zorder=15)

    ax.annotate("Strand 1 Enters\nBack Matrix DIN!\n(Completes Front-to-Back)", 
                xy=(0, BP_Y0), xytext=(-95, BP_Y0 - 30),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=18)

    # 3. STRAND 2: EXITS BACK MATRIX DOUT -> FILLS BROAD LAT FLANKS -> OVER LEFT SHOULDER
    # Exits Back DOUT at (+88, 322) -> goes to (185, 250)
    s2_b_keys = list(range(1, 17))
    s2_bx = [-strand2_back[k][0] for k in s2_b_keys] # Mirror X for rear view
    s2_by = [strand2_back[k][1] for k in s2_b_keys]

    ax.plot([88, s2_bx[0]], [322, s2_by[0]], color='#ffa657', lw=2.5, ls=':', zorder=8)
    ax.plot(s2_bx, s2_by, color='#ffa657', lw=3.0, zorder=8, label="Strand 2 (Exits Back DOUT -> Broad Wing Canopy)")

    ax.annotate("Back Matrix DOUT\nStarts Strand 2!", xy=(88, 322), xytext=(110, 310),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    for i in [2, 6, 10, 13]:
        ax.annotate("", xy=(s2_bx[i+1], s2_by[i+1]), xytext=(s2_bx[i], s2_by[i]),
                    arrowprops=dict(arrowstyle="->", color="#ffa657", lw=2.5), zorder=9)

    for idx, k in enumerate(s2_b_keys):
        draw_prominent_badge(ax, s2_bx[idx], s2_by[idx], f"2-{k}", badge_color='#ffa657', glow_color='#ffaa00', zorder=15)

    ax.annotate("Strand 2 Climbs\nOver Left Shoulder ->\n(To Front Left Suspender)", 
                xy=(s2_bx[-1], s2_by[-1]), xytext=(s2_bx[-1]+15, s2_by[-1]+15),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    # Callout for broad wing space fill
    ax.annotate("Broad Wing Sweep\n(Fills Empty Lat & Flank Space!)", xy=(220, 335), xytext=(120, 210),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=18)

    ax.set_xlim(-260, 260)
    ax.set_ylim(-40, 740)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)

    out_file = os.path.join(out_dir, "rendering_back_two_strands.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=250, facecolor='#06080d')
    plt.close()
    print("Saved Two-Strand Back View to:", out_file)

render_front()
render_back()
print("Both Two-Strand Renderings Generated Successfully!")
