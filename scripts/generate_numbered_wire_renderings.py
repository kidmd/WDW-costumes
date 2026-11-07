import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

out_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\bfa4167c-5abb-4691-97fc-48e297e7effa"
os.makedirs(out_dir, exist_ok=True)

plt.style.use('dark_background')

# Load artwork if available
drum_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\title_drum.png"
pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon_transparent.png"
if not os.path.exists(pete_img_path):
    pete_img_path = r"C:\Users\Kiddi\Desktop\WDW costumes\simulator\assets\petes_dragon.png"

drum_img = Image.open(drum_img_path) if os.path.exists(drum_img_path) else None
pete_img = Image.open(pete_img_path) if os.path.exists(pete_img_path) else None

def draw_runner_torso(ax, is_front=True):
    """Draws realistic dark athletic running shirt silhouette with seams."""
    torso = patches.Polygon([
        (25, 6), (95, 6),      # Waist hem
        (98, 55), (116, 62),   # Right armpit / sleeve
        (106, 82), (75, 87),   # Right shoulder seam
        (45, 87), (14, 82),    # Left shoulder seam
        (4, 62), (22, 55)      # Left armpit / sleeve
    ], closed=True, fc='#101318', ec='#2d333b', lw=2.5, zorder=1)
    ax.add_patch(torso)

    collar_y = 78 if is_front else 82
    collar = patches.Arc((60, 87), 30, (87 - collar_y)*2, angle=0, theta1=180, theta2=360, 
                         color='#30363d', lw=3, zorder=2)
    ax.add_patch(collar)

    ax.plot([28, 48], [58, 87], color='#1f242c', lw=2, ls=':', zorder=2)
    ax.plot([92, 72], [58, 87], color='#1f242c', lw=2, ls=':', zorder=2)

    belt = patches.FancyBboxPatch((20, 1), 80, 8, boxstyle="round,pad=1.0",
                                fc='#080a0e', ec='#388bfd', lw=2, zorder=3)
    ax.add_patch(belt)
    
    if is_front:
        ax.text(60, 5, "RUNNING BELT (WAIST)\nESP32 + 5V USB Battery", 
                ha='center', va='center', color='#58a6ff', fontsize=8, weight='bold', zorder=4)
    else:
        ax.text(60, 5, "RUNNING BELT (LUMBAR)\nPower Bank & Controller", 
                ha='center', va='center', color='#58a6ff', fontsize=8, weight='bold', zorder=4)

def draw_numbered_led(ax, x, y, num, col='#ffe600', glow_col='#ffaa00', radius=2.2, zorder=15):
    # Outer glow
    ax.scatter(x, y, s=280, color=glow_col, alpha=0.35, edgecolors='none', zorder=zorder-2)
    # White bulb core
    ax.scatter(x, y, s=150, color='#ffffff', edgecolors=col, lw=2.0, zorder=zorder-1)
    # Number badge text (crisp dark number on bright bulb)
    ax.text(x, y, str(num), ha='center', va='center', color='#000000', fontsize=7.2, weight='heavy', zorder=zorder)

# ==============================================================================
# 1. FRONT VIEW WITH SEQUENTIAL LED NUMBERS
# ==============================================================================
def render_front_numbered():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#06080d')
    fig.patch.set_facecolor('#06080d')

    plt.title("FRONT VIEW: NUMBERED LED WIRE PATH (10cm Pitch)", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Follow LEDs #1 to #12 on Front -> #13 over Right Shoulder | #38-#41 over Left Shoulder", 
            transform=ax.transAxes, ha='center', fontsize=9.2, color='#8b949e')

    draw_runner_torso(ax, is_front=True)

    # 1. Unlit Cable (Hidden behind bib)
    ax.plot([60, 60], [9, 47], color='#79c0ff', lw=3.5, ls='--', zorder=4)
    ax.annotate("UNLIT 3-WIRE CABLE\n(5V, GND, GPIO 16)\nBehind Race Bib", 
                xy=(60, 22), xytext=(84, 18),
                arrowprops=dict(arrowstyle="->", color="#79c0ff", lw=1.5),
                color="#79c0ff", fontsize=8, weight='bold', zorder=10)

    # 2. Race Bib (#1952)
    bib = patches.FancyBboxPatch((40.5, 14), 39, 27, boxstyle="round,pad=0.8",
                                fc='#ffeb3b', ec='#fbc02d', lw=2, zorder=5)
    ax.add_patch(bib)
    bib_bar = patches.Rectangle((41, 36), 38, 4.5, fc='#e53935', zorder=6)
    ax.add_patch(bib_bar)
    ax.text(60, 38.2, "runDisney 10K", ha='center', va='center', color='white', weight='bold', fontsize=9, zorder=7)
    ax.text(60, 26.5, "1952", ha='center', va='center', color='#111111', weight='heavy', fontsize=22, zorder=7)
    ax.text(60, 17, "CHIP 'N' DALE  |  CORRAL A", ha='center', va='center', color='#424242', weight='bold', fontsize=7.5, zorder=7)
    
    for bx, by in [(42, 15.5), (78, 15.5), (42, 39.5), (78, 39.5)]:
        ax.scatter(bx, by, s=60, color='#1e88e5', edgecolors='white', lw=1.2, zorder=8)

    # 3. 176mm x 176mm Front Plate (SHARP VISIBLE EDGES, NO WIRES ATTACHED)
    plate = patches.Rectangle((42.5, 47), 35, 30, fc='#0d1117', ec='#ff0055', lw=3.0, zorder=6)
    ax.add_patch(plate)
    ax.plot([42.5, 77.5, 77.5, 42.5, 42.5], [47, 47, 77, 77, 47], color='#ffffff', lw=1.0, ls=':', zorder=7)

    # 176mm Dimension line
    ax.annotate("176 mm Edge", xy=(42.5, 78.5), xytext=(77.5, 78.5),
                arrowprops=dict(arrowstyle="<->", color="#ff7b72", lw=1.5),
                ha='center', va='bottom', color='#ff7b72', fontsize=8.5, weight='bold', zorder=12)

    # 16x16 Grid Pixels
    gx = np.linspace(44.5, 75.5, 16)
    gy = np.linspace(48.5, 75.5, 16)
    for x in gx:
        for y in gy:
            dist = np.sqrt((x - 60)**2 + (y - 62)**2)
            if dist < 11.5:
                col = '#ffea00' if dist > 9.5 else '#ff2a55'
                glow = '#ffaa00' if dist > 9.5 else '#ff0033'
                ax.scatter(x, y, s=14, color=col, edgecolors='none', alpha=0.95, zorder=7)
            else:
                ax.scatter(x, y, s=7, color='#22272e', edgecolors='none', zorder=6)

    if drum_img:
        ax.imshow(drum_img, extent=[50, 70, 52, 72], aspect='auto', zorder=8, alpha=0.85)

    ax.text(60, 50, "176mm FRONT PANEL (16x16 GRID)", 
            ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 4. FRONT NUMBERED FAIRY LEDS (ON SHIRT FABRIC)
    # Origin: Front Matrix DOUT (Bottom-Left corner of plate, x=42.5, y=47)
    ax.annotate("Front DOUT\nStart LED #1", xy=(42.5, 47), xytext=(22, 43),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=8.5, weight='bold', zorder=16)

    # Path 1: Front Floating Lower & Right Frame on Shirt (LEDs 1 to 12)
    # LED 1: (36, 45) - Lower left flank
    # LED 2: (44, 43) - Below panel bottom edge
    # LED 3: (52, 43)
    # LED 4: (60, 43) - Center below panel
    # LED 5: (68, 43)
    # LED 6: (76, 43)
    # LED 7: (84, 45) - Lower right flank
    # LED 8: (85, 53) - Ascending right flank suspender
    # LED 9: (86, 61)
    # LED 10: (86, 69)
    # LED 11: (87, 77) - Right clavicle
    # LED 12: (89, 83) - Right shoulder entrance
    # LED 13: (91, 87) - Over Right Shoulder seam (crosses to Back!)
    
    front_path_x = [42.5, 36, 44, 52, 60, 68, 76, 84, 85, 86, 86, 87, 89, 91]
    front_path_y = [47,   45, 43, 43, 43, 43, 43, 45, 53, 61, 69, 77, 83, 87]
    ax.plot(front_path_x, front_path_y, color='#00ff88', lw=2.8, zorder=8)

    # Direction arrows along wire
    for i in [3, 7, 10]:
        dx = front_path_x[i+1] - front_path_x[i]
        dy = front_path_y[i+1] - front_path_y[i]
        ax.annotate("", xy=(front_path_x[i+1], front_path_y[i+1]), 
                    xytext=(front_path_x[i], front_path_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    # Draw LEDs 1 to 13
    for idx in range(1, 14):
        px = front_path_x[idx]
        py = front_path_y[idx]
        draw_numbered_led(ax, px, py, idx, col='#00ff88', glow_col='#00bb55', zorder=15)

    ax.annotate("Crosses Over\nRight Shoulder ➔", xy=(91, 87), xytext=(96, 88),
                color="#00ff88", fontsize=8, weight='bold', zorder=16)

    # Path 2: Left Shoulder Return Loop (LEDs 38 to 41 visible on front chest!)
    # Arrives from Left Shoulder seam at (30, 87) down left chest suspender:
    # LED 38: (30, 87) - Left shoulder crest
    # LED 39: (32, 82) - Left clavicle
    # LED 40: (33, 75) - Left upper chest flank
    # LED 41: (34, 67) - Mid left chest flank
    left_front_x = [30, 32, 33, 34]
    left_front_y = [87, 82, 75, 67]
    ax.plot(left_front_x, left_front_y, color='#d2a8ff', lw=2.8, zorder=8)

    for i, idx in enumerate(range(38, 42)):
        draw_numbered_led(ax, left_front_x[i], left_front_y[i], idx, col='#d2a8ff', glow_col='#a371f7', zorder=15)

    ax.annotate("<- Returns Over\nLeft Shoulder", xy=(30, 87), xytext=(8, 88),
                color="#d2a8ff", fontsize=8, weight='bold', zorder=16)

    # Fabric clips
    clips = [(36, 45), (60, 43), (84, 45), (86, 69), (89, 83), (32, 82), (34, 67)]
    for cx, cy in clips:
        ax.scatter(cx, cy, marker='s', s=85, color='#f78166', edgecolors='white', lw=1.2, zorder=17)

    ax.annotate("Fabric Snap Clip\n(Snaps to Shirt)", xy=(86, 69), xytext=(98, 67),
                arrowprops=dict(arrowstyle="->", color="#f78166", lw=1.5),
                color="#f78166", fontsize=8, weight='bold', zorder=18)

    ax.set_xlim(-5, 125)
    ax.set_ylim(-2, 98)
    ax.axis('off')

    out_file = os.path.join(out_dir, "rendering_front_numbered.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=220, facecolor='#06080d')
    plt.close()
    print("Saved Numbered Front Rendering to:", out_file)

# ==============================================================================
# 2. BACK VIEW WITH SEQUENTIAL LED NUMBERS (14 to 50)
# ==============================================================================
def render_back_numbered():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#06080d')
    fig.patch.set_facecolor('#06080d')

    plt.title("BACK VIEW: NUMBERED LED WIRE PATH (10cm Pitch)", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "LEDs #14 to #24 Down Right Flank -> #25-#37 Around Lat Canopy -> #42-#50 into Back Matrix DIN", 
            transform=ax.transAxes, ha='center', fontsize=9.2, color='#8b949e')

    draw_runner_torso(ax, is_front=False)

    # 1. 176mm x 176mm Back Plate
    plate = patches.Rectangle((42.5, 38), 35, 30, fc='#0d1117', ec='#00ff66', lw=3.0, zorder=6)
    ax.add_patch(plate)
    ax.plot([42.5, 77.5, 77.5, 42.5, 42.5], [38, 38, 68, 68, 38], color='#ffffff', lw=1.0, ls=':', zorder=7)

    ax.annotate("176 mm Edge", xy=(42.5, 69.5), xytext=(77.5, 69.5),
                arrowprops=dict(arrowstyle="<->", color="#7ee787", lw=1.5),
                ha='center', va='bottom', color='#7ee787', fontsize=8.5, weight='bold', zorder=12)

    # 16x16 Back Pixels
    bgx = np.linspace(44.5, 75.5, 16)
    bgy = np.linspace(39.5, 66.5, 16)
    for ix, x in enumerate(bgx):
        for iy, y in enumerate(bgy):
            dx = (x - 60) / 14.0
            dy = (y - 53) / 12.0
            val = dx*dx + dy*dy
            if val < 0.85:
                if dx > 0.1 and dy < -0.1:
                    col = '#ffea00'; glow = '#ffaa00'
                elif dy > 0.3:
                    col = '#ff2a88'; glow = '#ff0055'
                else:
                    col = '#00ff66'; glow = '#00bb33'
                ax.scatter(x, y, s=14, color=col, edgecolors='none', alpha=0.95, zorder=7)
            else:
                ax.scatter(x, y, s=7, color='#22272e', edgecolors='none', zorder=6)

    if pete_img:
        ax.imshow(pete_img, extent=[48, 72, 42, 64], aspect='auto', zorder=8, alpha=0.88)

    ax.text(60, 40.5, "176mm BACK PANEL (PETE'S DRAGON)", 
            ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 2. BACK NUMBERED FAIRY LEDS (LEDs 14 to 50)
    # Arrival from Right Shoulder (Viewer's Left, x=29, y=87):
    # LED 14: (28, 83) - Entering right scapula
    # LED 15: (26, 75) - Upper right lat flank
    # LED 16: (24, 67) - Mid right lat flank (broad wing!)
    # LED 17: (23, 59)
    # LED 18: (23, 51)
    # LED 19: (24, 43) - Lower right lat flank
    # LED 20: (26, 35)
    # LED 21: (30, 27) - Sweeping inward across lower back
    # LED 22: (37, 21)
    # LED 23: (45, 18) - Lower back under Pete's Dragon
    # LED 24: (53, 17)
    # LED 25: (61, 17)
    # LED 26: (69, 17)
    # LED 27: (77, 18)
    # LED 28: (85, 21) - Sweeping up left lat flank
    # LED 29: (91, 27)
    # LED 30: (95, 35) - Lower left lat flank
    # LED 31: (97, 43)
    # LED 32: (98, 51) - Mid left lat flank (broad wing!)
    # LED 33: (98, 59)
    # LED 34: (97, 67)
    # LED 35: (95, 75) - Upper left lat flank
    # LED 36: (93, 83) - Left shoulder entrance
    # LED 37: (90, 87) - Over Left Shoulder (Viewer's Right)
    
    back_outer_x = [29, 28, 26, 24, 23, 23, 24, 26, 30, 37, 45, 53, 61, 69, 77, 85, 91, 95, 97, 98, 98, 97, 95, 93, 90]
    back_outer_y = [87, 83, 75, 67, 59, 51, 43, 35, 27, 21, 18, 17, 17, 17, 18, 21, 27, 35, 43, 51, 59, 67, 75, 83, 87]
    ax.plot(back_outer_x, back_outer_y, color='#00ff88', lw=2.8, zorder=8)

    # Direction arrows
    for i in [3, 9, 15, 21]:
        ax.annotate("", xy=(back_outer_x[i+1], back_outer_y[i+1]), 
                    xytext=(back_outer_x[i], back_outer_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#00ff88", lw=2.5), zorder=9)

    for idx, num in enumerate(range(14, 38)):
        draw_numbered_led(ax, back_outer_x[idx+1], back_outer_y[idx+1], num, col='#00ff88', glow_col='#00bb55', zorder=15)

    ax.annotate("From Right Shoulder\n➔ LED #14", xy=(28, 83), xytext=(6, 85),
                color="#00ff88", fontsize=8, weight='bold', zorder=16)

    ax.annotate("➔ To Left Shoulder\n(LED #37)", xy=(90, 87), xytext=(94, 88),
                color="#00ff88", fontsize=8, weight='bold', zorder=16)

    # Inner Floating Halo on Shirt (LEDs 42 to 50):
    # Returns from Left Shoulder loop to frame the 176mm panel with 25mm clearance:
    # LED 42: (34, 69) - Upper right inner bracket (viewer's left)
    # LED 43: (42, 74) - Top bracket above panel
    # LED 44: (51, 75)
    # LED 45: (60, 75) - Center top bracket
    # LED 46: (69, 75)
    # LED 47: (78, 74)
    # LED 48: (86, 69) - Upper left inner bracket (viewer's right)
    # LED 49: (86, 53) - Mid flank bracket
    # LED 50: (60, 33) - Lower center junction -> Directly enters Back Matrix DIN!
    
    halo_x = [34, 42, 51, 60, 69, 78, 86, 86, 60]
    halo_y = [69, 74, 75, 75, 75, 74, 69, 53, 33]
    ax.plot(halo_x, halo_y, color='#ffa657', lw=2.8, ls='-', zorder=8)

    for i in [2, 5, 7]:
        ax.annotate("", xy=(halo_x[i+1], halo_y[i+1]), 
                    xytext=(halo_x[i], halo_y[i]),
                    arrowprops=dict(arrowstyle="->", color="#ffa657", lw=2.5), zorder=9)

    for i, num in enumerate(range(42, 51)):
        draw_numbered_led(ax, halo_x[i], halo_y[i], num, col='#ffe600', glow_col='#ffaa00', zorder=15)

    # Final Connection from LED #50 into Back Matrix DIN
    ax.plot([60, 60], [33, 38], color='#00e5ff', lw=3.0, ls='--', zorder=10)
    ax.scatter(60, 38, s=120, color='#00e5ff', edgecolors='white', lw=1.8, zorder=11)
    ax.annotate("LED #50 Connects\nto Back Matrix DIN!\n(Completes 562 LEDs)", 
                xy=(60, 38), xytext=(68, 32),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8.5, weight='bold', zorder=18)

    # Fabric clips
    clips = [(24, 67), (26, 35), (45, 18), (77, 18), (95, 35), (97, 67), (60, 75), (86, 69), (60, 33)]
    for cx, cy in clips:
        ax.scatter(cx, cy, marker='s', s=85, color='#f78166', edgecolors='white', lw=1.2, zorder=17)

    ax.annotate("Broad Flank Wing\n(Fills Empty Lat Space!)", 
                xy=(24, 67), xytext=(4, 57),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=18)

    ax.set_xlim(-5, 125)
    ax.set_ylim(-2, 98)
    ax.axis('off')

    out_file = os.path.join(out_dir, "rendering_back_numbered.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=220, facecolor='#06080d')
    plt.close()
    print("Saved Numbered Back Rendering to:", out_file)

render_front_numbered()
render_back_numbered()
print("All Numbered wire path drawings generated successfully!")
