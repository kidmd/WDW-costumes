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

# Load artwork
drum_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\title_drum.png"
pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon_transparent.png"
if not os.path.exists(pete_img_path):
    pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon.png"

drum_img = Image.open(drum_img_path) if os.path.exists(drum_img_path) else None
pete_img = Image.open(pete_img_path) if os.path.exists(pete_img_path) else None

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
    label = "RUNNING BELT (WAIST)\nESP32 Controller + 5V USB Battery" if is_front else "RUNNING BELT (LUMBAR)\nZero Wires to Back Belt! (100% Clean)"
    ax.text(0, -5, label, ha='center', va='center', color='#58a6ff', fontsize=8.5, weight='bold', zorder=4)

    # 100 mm scale bar
    ax.plot([-200, -100], [50, 50], color='#ffffff', lw=4, zorder=20)
    ax.plot([-200, -200], [42, 58], color='#ffffff', lw=2.5, zorder=20)
    ax.plot([-100, -100], [42, 58], color='#ffffff', lw=2.5, zorder=20)
    ax.text(-150, 65, "SCALE: 100 mm\n(1 LED Spacing)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=20)

def draw_prominent_badge(ax, x, y, text_label, badge_color='#00ff88', glow_color='#00bb55', zorder=15):
    ax.scatter(x, y, s=460, color=glow_color, alpha=0.35, edgecolors='none', zorder=zorder-2)
    ax.scatter(x, y, s=280, color='#ffffff', edgecolors=badge_color, lw=2.5, zorder=zorder-1)
    ax.text(x, y, text_label, ha='center', va='center', color='#000000', fontsize=7.8, weight='heavy', zorder=zorder)

def draw_front_base(ax, title_str):
    plt.title(title_str, fontsize=14.0, color='#58a6ff', weight='bold', pad=18)
    draw_shirt_background(ax, is_front=True)

    # Bib
    bib = patches.FancyBboxPatch((BIB_X0, BIB_Y0), BIB_W, BIB_H, boxstyle="round,pad=3.0",
                                fc='#ffeb3b', ec='#fbc02d', lw=2.5, zorder=5)
    ax.add_patch(bib)
    bib_bar = patches.Rectangle((BIB_X0, BIB_Y1 - 30), BIB_W, 30, fc='#e53935', zorder=6)
    ax.add_patch(bib_bar)
    ax.text(0, BIB_Y1 - 15, "runDisney 10K", ha='center', va='center', color='white', weight='bold', fontsize=9, zorder=7)
    ax.text(0, (BIB_Y0 + BIB_Y1)/2 - 5, "1952", ha='center', va='center', color='#111111', weight='heavy', fontsize=26, zorder=7)
    ax.text(0, BIB_Y0 + 20, "CHIP 'N' DALE  |  CORRAL A", ha='center', va='center', color='#424242', weight='bold', fontsize=7.5, zorder=7)

    # Unlit 3rd wire
    ax.plot([0, 0], [20, FP_Y0], color='#00e5ff', lw=4.0, ls='--', zorder=4)
    ax.annotate("UNLIT 3-WIRE CABLE\nBehind Race Bib to Front DIN", xy=(0, 200), xytext=(30, 160),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=10)

    # 176mm Panel
    panel = patches.Rectangle((FP_X0, FP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#ff0055', lw=3.5, zorder=6)
    ax.add_patch(panel)
    ax.plot([FP_X0, FP_X1], [FP_Y1 + 15, FP_Y1 + 15], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X0, FP_X0], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.plot([FP_X1, FP_X1], [FP_Y1 + 8, FP_Y1 + 22], color='#ff7b72', lw=2, zorder=12)
    ax.text(0, FP_Y1 + 24, "176 mm Panel Width", ha='center', color='#ff7b72', fontsize=9, weight='bold', zorder=12)

    if drum_img:
        ax.imshow(drum_img, extent=[FP_X0+15, FP_X1-15, FP_Y0+15, FP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, FP_Y0 + 20, "176mm FRONT PANEL\n(16x16 MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

def draw_back_base(ax, title_str):
    plt.title(title_str, fontsize=14.0, color='#58a6ff', weight='bold', pad=18)
    draw_shirt_background(ax, is_front=False)

    # 176mm Panel
    panel = patches.Rectangle((BP_X0, BP_Y0), PANEL_W, PANEL_H, fc='#0d1117', ec='#00ff66', lw=3.5, zorder=6)
    ax.add_patch(panel)
    ax.plot([BP_X0, BP_X1], [BP_Y1 + 15, BP_Y1 + 15], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X0, BP_X0], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.plot([BP_X1, BP_X1], [BP_Y1 + 8, BP_Y1 + 22], color='#7ee787', lw=2, zorder=12)
    ax.text(0, BP_Y1 + 24, "176 mm Panel Width", ha='center', color='#7ee787', fontsize=9, weight='bold', zorder=12)

    if pete_img:
        ax.imshow(pete_img, extent=[BP_X0+15, BP_X1-15, BP_Y0+15, BP_Y1-15], aspect='auto', zorder=8, alpha=0.9)
    ax.text(0, BP_Y0 + 20, "176mm BACK PANEL\n(PETE'S DRAGON MATRIX)", ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

# Helper to sample exact 100mm points along a polyline
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

# =============================================================================
# OPTION 1: "THE GRAND DRAGON WINGS & TWIN SUSPENDERS"
# =============================================================================
# (Already computed and verified above, let's export cleanly as option1_front and option1_back)
def export_option_1():
    # FRONT
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#05070c'); fig.patch.set_facecolor('#05070c')
    draw_front_base(ax, "OPTION 1: THE GRAND DRAGON WINGS (FRONT VIEW)")
    ax.text(0.5, 0.965, "Classic Theater Suspenders: 7 LEDs Right (Strand 1) & 7 LEDs Left (Strand 2) Mirror Balanced", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    # Front nodes
    s1_keys = [1, 2, 3, 4, 5, 6, 7]
    s1_pts = [(20, 300), (120, 300), (135, 398.8), (135, 498.8), (135, 598.8), (135, 698.8), (110, 690)]
    s2_pts = [(-110, 690), (-135, 698.8), (-135, 598.8), (-135, 498.8), (-135, 398.8), (-120, 300), (-20, 300)]
    
    ax.plot([88, 20], [342, 300], color='#00ff88', lw=2.5, ls=':', zorder=8)
    ax.plot([p[0] for p in s1_pts], [p[1] for p in s1_pts], color='#00ff88', lw=3.2, zorder=8, label="Strand 1 (Right Suspender)")
    ax.plot([p[0] for p in s2_pts], [p[1] for p in s2_pts], color='#ffa657', lw=3.2, zorder=8, label="Strand 2 (Left Suspender)")

    for k, p in zip(s1_keys, s1_pts): draw_prominent_badge(ax, p[0], p[1], f"1-{k}", '#00ff88', '#00bb55')
    for k, p in zip(range(19, 26), s2_pts): draw_prominent_badge(ax, p[0], p[1], f"2-{k}", '#ffa657', '#ffaa00')

    ax.set_xlim(-260, 260); ax.set_ylim(-40, 740); ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "option1_front_wings.png"), dpi=220, facecolor='#05070c')
    plt.close()

    # BACK
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#05070c'); fig.patch.set_facecolor('#05070c')
    draw_back_base(ax, "OPTION 1: THE GRAND DRAGON WINGS (BACK VIEW)")
    ax.text(0.5, 0.965, "Broad Soaring Wings: 18 LEDs Right Wing & 18 LEDs Left Wing Fill Entire Back Space!", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    # Wings path
    b_r_pts = [(-135, 698.8), (-160, 605), (-195, 515), (-225, 425), (-235, 330), (-225, 235), (-195, 150),
               (-145, 85), (-80, 55), (0, 50), (65, 75), (100, 150), (115, 240), (115, 340), (115, 440),
               (80, 520), (0, 525), (-50, 322)]
    b_l_pts = [(50, 322), (0, 525), (-80, 520), (-115, 440), (-115, 340), (-115, 240), (-100, 150), (-65, 75),
               (0, 50), (80, 55), (145, 85), (195, 150), (225, 235), (235, 330), (225, 425), (195, 515),
               (160, 605), (135, 698.8)]

    ax.plot([p[0] for p in b_r_pts], [p[1] for p in b_r_pts], color='#00ff88', lw=3.2, zorder=8, label="Strand 1 Right Wing (18 LEDs)")
    ax.plot([p[0] for p in b_l_pts], [p[1] for p in b_l_pts], color='#ffa657', lw=3.2, zorder=8, label="Strand 2 Left Wing (18 LEDs)")
    ax.plot([-50, 0], [322, BP_Y0], color='#00e5ff', lw=3.0, ls='--', zorder=12)
    ax.scatter(0, BP_Y0, s=140, color='#00e5ff', edgecolors='white', lw=2.0, zorder=14)

    for k, p in zip(range(8, 26), b_r_pts): draw_prominent_badge(ax, p[0], p[1], f"1-{k}", '#00ff88', '#00bb55')
    for k, p in zip(range(1, 19), b_l_pts): draw_prominent_badge(ax, p[0], p[1], f"2-{k}", '#ffa657', '#ffaa00')

    ax.set_xlim(-260, 260); ax.set_ylim(-40, 740); ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "option1_back_wings.png"), dpi=220, facecolor='#05070c')
    plt.close()
    print("Option 1 (Grand Dragon Wings) exported successfully!")

# =============================================================================
# OPTION 2: "CONCENTRIC FLOATING HALO & SPEED RIBS"
# =============================================================================
# High-tech architectural floating frame with horizontal radiator ribs on flanks!
def export_option_2():
    # FRONT
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#05070c'); fig.patch.set_facecolor('#05070c')
    draw_front_base(ax, "OPTION 2: FLOATING HALO & SPEED RIBS (FRONT VIEW)")
    ax.text(0.5, 0.965, "Architectural Frame: Floating Box with Horizontal Rib Fin Accents on Flanks", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    # Front path: 7 LEDs on right, 7 on left
    s1_pts = [(40, 310), (130, 310), (190, 380), (130, 450), (130, 550), (130, 650), (105, 690)]
    s2_pts = [(-105, 690), (-130, 650), (-130, 550), (-130, 450), (-190, 380), (-130, 310), (-40, 310)]

    ax.plot([88, 40], [342, 310], color='#00ff88', lw=2.5, ls=':', zorder=8)
    ax.plot([p[0] for p in s1_pts], [p[1] for p in s1_pts], color='#00ff88', lw=3.2, zorder=8, label="Strand 1 (Right Rib Frame)")
    ax.plot([p[0] for p in s2_pts], [p[1] for p in s2_pts], color='#ffa657', lw=3.2, zorder=8, label="Strand 2 (Left Rib Frame)")

    for k, p in zip(range(1, 8), s1_pts): draw_prominent_badge(ax, p[0], p[1], f"1-{k}", '#00ff88', '#00bb55')
    for k, p in zip(range(19, 26), s2_pts): draw_prominent_badge(ax, p[0], p[1], f"2-{k}", '#ffa657', '#ffaa00')

    ax.annotate("Speed Rib Outrigger\n(Dynamic Flank Accent)", xy=(190, 380), xytext=(120, 230),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5), color="#00ff88", fontsize=8.5, weight='bold')

    ax.set_xlim(-260, 260); ax.set_ylim(-40, 740); ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "option2_front_halo_ribs.png"), dpi=220, facecolor='#05070c')
    plt.close()

    # BACK
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#05070c'); fig.patch.set_facecolor('#05070c')
    draw_back_base(ax, "OPTION 2: FLOATING HALO & SPEED RIBS (BACK VIEW)")
    ax.text(0.5, 0.965, "Concentric Inner Halo (30mm Gap) + Triple Horizontal Float Ribs across Lats!", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    # Right back: 18 LEDs (Inner halo + 3 horizontal ribs out to X=-230)
    b_r_pts = [(-105, 690), (-120, 600), (-120, 500), (-210, 500), (-120, 420), (-220, 420),
               (-120, 340), (-210, 340), (-120, 260), (-80, 200), (0, 180), (60, 220),
               (100, 280), (100, 380), (100, 480), (60, 540), (0, 540), (-40, 322)]
    # Left back: 18 LEDs (Mirrored)
    b_l_pts = [(40, 322), (0, 540), (-60, 540), (-100, 480), (-100, 380), (-100, 280),
               (-60, 220), (0, 180), (80, 200), (120, 260), (210, 340), (120, 340),
               (220, 420), (120, 420), (210, 500), (120, 500), (120, 600), (105, 690)]

    ax.plot([p[0] for p in b_r_pts], [p[1] for p in b_r_pts], color='#00ff88', lw=3.2, zorder=8, label="Strand 1 Right Halo & Ribs")
    ax.plot([p[0] for p in b_l_pts], [p[1] for p in b_l_pts], color='#ffa657', lw=3.2, zorder=8, label="Strand 2 Left Halo & Ribs")
    ax.plot([-40, 0], [322, BP_Y0], color='#00e5ff', lw=3.0, ls='--', zorder=12)
    ax.scatter(0, BP_Y0, s=140, color='#00e5ff', edgecolors='white', lw=2.0, zorder=14)

    for k, p in zip(range(8, 26), b_r_pts): draw_prominent_badge(ax, p[0], p[1], f"1-{k}", '#00ff88', '#00bb55')
    for k, p in zip(range(1, 19), b_l_pts): draw_prominent_badge(ax, p[0], p[1], f"2-{k}", '#ffa657', '#ffaa00')

    ax.annotate("Triple Horizontal Speed Ribs\n(Fills Flank Width to 460mm!)", xy=(-220, 420), xytext=(-255, 300),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5), color="#00ff88", fontsize=8.5, weight='bold')

    ax.set_xlim(-260, 260); ax.set_ylim(-40, 740); ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "option2_back_halo_ribs.png"), dpi=220, facecolor='#05070c')
    plt.close()
    print("Option 2 (Halo & Speed Ribs) exported successfully!")

# =============================================================================
# OPTION 3: "THE RADIATING SUNBURST CHEVRON" (ATHLETIC V-TAPER)
# =============================================================================
# Kinetic angular lines accentuating the runner's V-taper physique!
def export_option_3():
    # FRONT
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#05070c'); fig.patch.set_facecolor('#05070c')
    draw_front_base(ax, "OPTION 3: RADIATING CHEVRON (FRONT VIEW)")
    ax.text(0.5, 0.965, "Athletic V-Taper: Diagonal Light Rays Flaring from Waist up to Shoulders", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    # Front Chevron: starts near bib center, flares outward
    s1_pts = [(45, 295), (85, 360), (115, 435), (140, 515), (160, 595), (150, 675), (110, 690)]
    s2_pts = [(-110, 690), (-150, 675), (-160, 595), (-140, 515), (-115, 435), (-85, 360), (-45, 295)]

    ax.plot([88, 45], [342, 295], color='#00ff88', lw=2.5, ls=':', zorder=8)
    ax.plot([p[0] for p in s1_pts], [p[1] for p in s1_pts], color='#00ff88', lw=3.2, zorder=8, label="Strand 1 (Right Chevron)")
    ax.plot([p[0] for p in s2_pts], [p[1] for p in s2_pts], color='#ffa657', lw=3.2, zorder=8, label="Strand 2 (Left Chevron)")

    for k, p in zip(range(1, 8), s1_pts): draw_prominent_badge(ax, p[0], p[1], f"1-{k}", '#00ff88', '#00bb55')
    for k, p in zip(range(19, 26), s2_pts): draw_prominent_badge(ax, p[0], p[1], f"2-{k}", '#ffa657', '#ffaa00')

    ax.annotate("Athletic V-Taper Flare\n(Flared Chest Silhouette)", xy=(160, 595), xytext=(80, 630),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5), color="#00ff88", fontsize=8.5, weight='bold')

    ax.set_xlim(-260, 260); ax.set_ylim(-40, 740); ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "option3_front_chevron.png"), dpi=220, facecolor='#05070c')
    plt.close()

    # BACK
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#05070c'); fig.patch.set_facecolor('#05070c')
    draw_back_base(ax, "OPTION 3: RADIATING CHEVRON (BACK VIEW)")
    ax.text(0.5, 0.965, "Dual Chevron Wings: Sweeping Diagonal V-Lines Cascading from Traps down to Lumbar!", 
            transform=ax.transAxes, ha='center', fontsize=9.0, color='#8b949e')

    # Right back: 18 LEDs in dual diagonal chevron sweeps
    b_r_pts = [(-110, 690), (-165, 620), (-215, 540), (-235, 450), (-220, 360), (-170, 290),
               (-100, 240), (-30, 200), (0, 110), (-70, 130), (-140, 165), (-195, 220),
               (-160, 310), (-100, 370), (-30, 420), (0, 520), (60, 520), (-40, 322)]
    # Left back: 18 LEDs (Mirrored)
    b_l_pts = [(40, 322), (-60, 520), (0, 520), (30, 420), (100, 370), (160, 310),
               (195, 220), (140, 165), (70, 130), (0, 110), (30, 200), (100, 240),
               (170, 290), (220, 360), (235, 450), (215, 540), (165, 620), (110, 690)]

    ax.plot([p[0] for p in b_r_pts], [p[1] for p in b_r_pts], color='#00ff88', lw=3.2, zorder=8, label="Strand 1 Right Chevron (18 LEDs)")
    ax.plot([p[0] for p in b_l_pts], [p[1] for p in b_l_pts], color='#ffa657', lw=3.2, zorder=8, label="Strand 2 Left Chevron (18 LEDs)")
    ax.plot([-40, 0], [322, BP_Y0], color='#00e5ff', lw=3.0, ls='--', zorder=12)
    ax.scatter(0, BP_Y0, s=140, color='#00e5ff', edgecolors='white', lw=2.0, zorder=14)

    for k, p in zip(range(8, 26), b_r_pts): draw_prominent_badge(ax, p[0], p[1], f"1-{k}", '#00ff88', '#00bb55')
    for k, p in zip(range(1, 19), b_l_pts): draw_prominent_badge(ax, p[0], p[1], f"2-{k}", '#ffa657', '#ffaa00')

    ax.annotate("Cascading V-Lines\n(Dynamic Speed Aerodynamics)", xy=(-215, 540), xytext=(-255, 440),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5), color="#00ff88", fontsize=8.5, weight='bold')

    ax.set_xlim(-260, 260); ax.set_ylim(-40, 740); ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "option3_back_chevron.png"), dpi=220, facecolor='#05070c')
    plt.close()
    print("Option 3 (Radiating Chevron) exported successfully!")

export_option_1()
export_option_2()
export_option_3()
print("All 3 Creative Options Exported Successfully!")
