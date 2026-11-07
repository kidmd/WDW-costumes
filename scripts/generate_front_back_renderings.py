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
        (25, 8), (95, 8),      # Waist hem
        (98, 55), (116, 62),   # Right armpit / sleeve
        (106, 82), (75, 87),   # Right shoulder seam
        (45, 87), (14, 82),    # Left shoulder seam
        (4, 62), (22, 55)      # Left armpit / sleeve
    ], closed=True, fc='#12151b', ec='#2d333b', lw=2.5, zorder=1)
    ax.add_patch(torso)

    collar_y = 78 if is_front else 82
    collar = patches.Arc((60, 87), 30, (87 - collar_y)*2, angle=0, theta1=180, theta2=360, 
                         color='#30363d', lw=3, zorder=2)
    ax.add_patch(collar)

    ax.plot([28, 48], [58, 87], color='#1f242c', lw=2, ls=':', zorder=2)
    ax.plot([92, 72], [58, 87], color='#1f242c', lw=2, ls=':', zorder=2)

    belt = patches.FancyBboxPatch((20, 2), 80, 8, boxstyle="round,pad=1.0",
                                fc='#090c10', ec='#388bfd', lw=2, zorder=3)
    ax.add_patch(belt)
    
    if is_front:
        ax.text(60, 6, "RUNNING BELT (WAIST)\nESP32 Controller + 5V USB Battery", 
                ha='center', va='center', color='#58a6ff', fontsize=8.5, weight='bold', zorder=4)
    else:
        ax.text(60, 6, "RUNNING BELT (LUMBAR)\nPower Distribution & USB Bank", 
                ha='center', va='center', color='#58a6ff', fontsize=8.5, weight='bold', zorder=4)

def draw_led_glow(ax, x, y, col='#ffe600', glow_col='#ffaa00', size=90, zorder=7):
    ax.scatter(x, y, s=size*2.8, color=glow_col, alpha=0.35, edgecolors='none', zorder=zorder-1)
    ax.scatter(x, y, s=size, color='#ffffff', edgecolors=col, lw=1.8, zorder=zorder)

# ==============================================================================
# 1. FRONT VIEW: SHIRT-MOUNTED TWIN-SHOULDER HARNESS (DETACHED FROM PANEL)
# ==============================================================================
def render_front():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#07090e')
    fig.patch.set_facecolor('#07090e')

    plt.title("FRONT VIEW: SHIRT-MOUNTED TWIN-SHOULDER SUSPENDERS", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Wires attached to SHIRT fabric (not panels) | 176mm x 176mm panel floating with clean clearance", 
            transform=ax.transAxes, ha='center', fontsize=9.2, color='#8b949e')

    draw_runner_torso(ax, is_front=True)

    # 1. Unlit Cable (Hidden behind bib)
    ax.plot([60, 60], [10, 47], color='#79c0ff', lw=3.5, ls='--', zorder=4, label="Unlit 3-Wire Cable (Behind Bib)")
    ax.annotate("UNLIT 3-WIRE CABLE\n(5V, GND, GPIO 16)\nHidden Behind Race Bib!", 
                xy=(60, 22), xytext=(84, 18),
                arrowprops=dict(arrowstyle="->", color="#79c0ff", lw=1.5),
                color="#79c0ff", fontsize=8.5, weight='bold', zorder=10)

    # 2. Race Bib (#1952)
    bib = patches.FancyBboxPatch((40.5, 15), 39, 27, boxstyle="round,pad=0.8",
                                fc='#ffeb3b', ec='#fbc02d', lw=2, zorder=5)
    ax.add_patch(bib)
    bib_bar = patches.Rectangle((41, 37), 38, 4.5, fc='#e53935', zorder=6)
    ax.add_patch(bib_bar)
    ax.text(60, 39.2, "runDisney 10K", ha='center', va='center', color='white', weight='bold', fontsize=9, zorder=7)
    ax.text(60, 27.5, "1952", ha='center', va='center', color='#111111', weight='heavy', fontsize=22, zorder=7)
    ax.text(60, 18, "CHIP 'N' DALE  |  CORRAL A", ha='center', va='center', color='#424242', weight='bold', fontsize=7.5, zorder=7)
    
    for bx, by in [(42, 16.5), (78, 16.5), (42, 40.5), (78, 40.5)]:
        ax.scatter(bx, by, s=60, color='#1e88e5', edgecolors='white', lw=1.2, zorder=8)

    # 3. 176mm x 176mm Front Plate (SHARP VISIBLE EDGES, NO WIRES ATTACHED)
    # Physical size 176mm square: x=42.5 to 77.5 (width=35), y=47 to 77 (height=30)
    plate = patches.Rectangle((42.5, 47), 35, 30, fc='#0d1117', ec='#ff0055', lw=3.0, zorder=6)
    ax.add_patch(plate)

    # Sharp boundary ticks showing exact 176mm edge
    ax.plot([42.5, 77.5, 77.5, 42.5, 42.5], [47, 47, 77, 77, 47], color='#ffffff', lw=1.0, ls=':', zorder=7)

    # 176mm Dimension line
    ax.annotate("176 mm Panel Edge", xy=(42.5, 78.5), xytext=(77.5, 78.5),
                arrowprops=dict(arrowstyle="<->", color="#ff7b72", lw=1.5),
                ha='center', va='bottom', color='#ff7b72', fontsize=8.5, weight='bold', zorder=12)

    # Render 16x16 RGB Pixels inside panel
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

    # 4. SHIRT-ATTACHED FAIRY LIGHT HARNESS (EXPANDED OUTWARD ON FABRIC)
    # Notice: 20-30mm clearance gap between panel edge and fairy wire!
    
    # Left Front Suspender (Runner's Left / Viewer's Right):
    # From waist flank (32, 25) up across chest flank (34, 46) -> (33, 76) -> over Left Shoulder (31, 87)
    l_sh_x = [34, 34, 33, 33, 31, 30]
    l_sh_y = [46, 56, 66, 76, 83, 87]
    ax.plot(l_sh_x, l_sh_y, color='#d2a8ff', lw=3.2, zorder=8, label="Left Shoulder Suspender (On Shirt)")
    for i, (wx, wy) in enumerate(zip(l_sh_x, l_sh_y)):
        draw_led_glow(ax, wx, wy, col='#d2a8ff', glow_col='#a371f7', size=75, zorder=9)

    # Right Front Suspender (Runner's Right / Viewer's Left):
    # From waist flank (86, 25) up across chest flank (86, 46) -> (87, 76) -> over Right Shoulder (89, 87)
    r_sh_x = [86, 86, 87, 87, 89, 90]
    r_sh_y = [46, 56, 66, 76, 83, 87]
    ax.plot(r_sh_x, r_sh_y, color='#00ff88', lw=3.2, zorder=8, label="Right Shoulder Suspender (On Shirt)")
    for i, (wx, wy) in enumerate(zip(r_sh_x, r_sh_y)):
        draw_led_glow(ax, wx, wy, col='#00ff88', glow_col='#00bb55', size=75, zorder=9)

    # Horizontal Chest Framing Loop on shirt fabric (Below panel y=44, Above bib):
    chest_wire_x = [34, 43, 51, 60, 69, 77, 86]
    chest_wire_y = [46, 44, 44, 44, 44, 44, 46]
    ax.plot(chest_wire_x, chest_wire_y, color='#ffa657', lw=2.5, zorder=8)
    for wx, wy in zip(chest_wire_x[1:-1], chest_wire_y[1:-1]):
        draw_led_glow(ax, wx, wy, col='#ffe600', glow_col='#ffaa00', size=65, zorder=9)

    # Top Clavicle Framing Loop on shirt fabric (Above panel y=79):
    top_wire_x = [33, 42, 51, 60, 69, 78, 87]
    top_wire_y = [76, 80, 81, 81, 81, 80, 76]
    ax.plot(top_wire_x, top_wire_y, color='#ffa657', lw=2.5, zorder=8)
    for wx, wy in zip(top_wire_x[1:-1], top_wire_y[1:-1]):
        draw_led_glow(ax, wx, wy, col='#ffe600', glow_col='#ffaa00', size=65, zorder=9)

    # Fabric Snap Clips (Attached directly to Shirt Fabric)
    fabric_clips = [(34, 46), (34, 66), (33, 76), (30, 87),
                    (86, 46), (86, 66), (87, 76), (90, 87),
                    (60, 44), (60, 81)]
    for cx, cy in fabric_clips:
        ax.scatter(cx, cy, marker='o', s=90, color='#f78166', edgecolors='white', lw=1.5, zorder=11)

    ax.annotate("Air Gap Clearance\n(Wire on Shirt, NOT on Panel)", 
                xy=(38, 62), xytext=(12, 60),
                arrowprops=dict(arrowstyle="->", color="#f78166", lw=1.5),
                color="#f78166", fontsize=8.5, weight='bold', zorder=12)

    ax.annotate("Fabric Sandwich Snap\n(Clips to shirt fabric)", 
                xy=(86, 66), xytext=(96, 64),
                arrowprops=dict(arrowstyle="->", color="#f78166", lw=1.5),
                color="#f78166", fontsize=8.5, weight='bold', zorder=12)

    ax.set_xlim(-5, 125)
    ax.set_ylim(-2, 98)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=3, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)

    out_file = os.path.join(out_dir, "rendering_front_view.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=220, facecolor='#07090e')
    plt.close()
    print("Saved Updated Front Rendering to:", out_file)

# ==============================================================================
# 2. BACK VIEW: EXPANDED SHIRT CANOPY & TWIN-SHOULDER HARNESS (DETACHED FROM PANEL)
# ==============================================================================
def render_back():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=220)
    ax.set_facecolor('#07090e')
    fig.patch.set_facecolor('#07090e')

    plt.title("BACK VIEW: EXPANDED SHIRT-MOUNTED CANOPY & TWIN SUSPENDERS", 
              fontsize=14.5, color='#58a6ff', weight='bold', pad=18)
    ax.text(0.5, 0.965, "Fills empty back/flank space on shirt fabric | 176mm x 176mm panel centered with clean air gap", 
            transform=ax.transAxes, ha='center', fontsize=9.2, color='#8b949e')

    draw_runner_torso(ax, is_front=False)

    # 1. 176mm x 176mm Back Plate (SHARP VISIBLE EDGES, NO WIRES ATTACHED)
    # Centered on upper/mid back: x=42.5 to 77.5, y=38 to 68
    plate = patches.Rectangle((42.5, 38), 35, 30, fc='#0d1117', ec='#00ff66', lw=3.0, zorder=6)
    ax.add_patch(plate)

    # Sharp boundary ticks
    ax.plot([42.5, 77.5, 77.5, 42.5, 42.5], [38, 38, 68, 68, 38], color='#ffffff', lw=1.0, ls=':', zorder=7)

    # Dimension annotation
    ax.annotate("176 mm Panel Edge", xy=(42.5, 69.5), xytext=(77.5, 69.5),
                arrowprops=dict(arrowstyle="<->", color="#7ee787", lw=1.5),
                ha='center', va='bottom', color='#7ee787', fontsize=8.5, weight='bold', zorder=12)

    # Render Back 16x16 RGB Pixels
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

    ax.text(60, 41, "176mm BACK PANEL (PETE'S DRAGON)", 
            ha='center', color='#ffffff', fontsize=8, weight='bold', zorder=10)

    # 2. SHIRT-ATTACHED BACK LIGHT CANOPY (EXPANDED TO FILL EMPTY FLANKS & LATS)
    # Both Shoulders enter at top: Left Shoulder (30, 87) & Right Shoulder (90, 87)
    
    # Left Lat Flank Wire (Viewer's Left, Runner's Right):
    # Expands wide to x=24 (filling the empty ribcage / lat space)
    l_lat_x = [30, 26, 24, 25, 29, 36, 45, 55, 60]
    l_lat_y = [87, 75, 60, 45, 32, 23, 18, 17, 17]
    ax.plot(l_lat_x, l_lat_y, color='#00ff88', lw=3.2, zorder=8, label="Right Shoulder -> Outer Flank Canopy")
    for wx, wy in zip(l_lat_x[1:], l_lat_y[1:]):
        draw_led_glow(ax, wx, wy, col='#00ff88', glow_col='#00bb55', size=75, zorder=9)

    # Right Lat Flank Wire (Viewer's Right, Runner's Left):
    # Expands wide to x=96 (filling the empty ribcage / lat space)
    r_lat_x = [90, 94, 96, 95, 91, 84, 75, 65, 60]
    r_lat_y = [87, 75, 60, 45, 32, 23, 18, 17, 17]
    ax.plot(r_lat_x, r_lat_y, color='#d2a8ff', lw=3.2, zorder=8, label="Left Shoulder -> Outer Flank Canopy")
    for wx, wy in zip(r_lat_x[1:], r_lat_y[1:]):
        draw_led_glow(ax, wx, wy, col='#d2a8ff', glow_col='#a371f7', size=75, zorder=9)

    # Inner Scapular / Trapezius Halo on shirt fabric (Floating 25mm around the 176mm panel)
    # Upper bridge (y=74)
    ax.plot([34, 47, 60, 73, 86], [74, 76, 76, 76, 74], color='#ffa657', lw=2.5, zorder=8)
    for wx, wy in [(47, 76), (60, 76), (73, 76)]:
        draw_led_glow(ax, wx, wy, col='#ffe600', glow_col='#ffaa00', size=65, zorder=9)

    # Mid flank brackets (x=34 and x=86)
    ax.plot([34, 34, 34], [74, 53, 33], color='#ffa657', lw=2.5, zorder=8)
    ax.plot([86, 86, 86], [74, 53, 33], color='#ffa657', lw=2.5, zorder=8)
    for wy in [53, 33]:
        draw_led_glow(ax, 34, wy, col='#ffe600', glow_col='#ffaa00', size=65, zorder=9)
        draw_led_glow(ax, 86, wy, col='#ffe600', glow_col='#ffaa00', size=65, zorder=9)

    # Lower bracket bridge (y=33)
    ax.plot([34, 47, 60, 73, 86], [33, 31, 31, 31, 33], color='#ffa657', lw=2.5, zorder=8)
    for wx, wy in [(47, 31), (60, 31), (73, 31)]:
        draw_led_glow(ax, wx, wy, col='#ffe600', glow_col='#ffaa00', size=65, zorder=9)

    # Connect to Back Matrix DIN from lower junction
    ax.plot([60, 60], [17, 38], color='#00e5ff', lw=2.5, ls='--', zorder=10)
    ax.scatter(60, 38, s=120, color='#00e5ff', edgecolors='white', lw=1.8, zorder=11)
    ax.annotate("Data In (DIN)\nto Back Matrix", 
                xy=(60, 38), xytext=(68, 35),
                arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.5),
                color="#00e5ff", fontsize=8, weight='bold', zorder=12)

    # Fabric Snap Clips on Back Shirt
    back_clips = [(30, 87), (90, 87), (24, 60), (96, 60), (29, 32), (91, 32),
                  (60, 76), (60, 31), (34, 53), (86, 53)]
    for cx, cy in back_clips:
        ax.scatter(cx, cy, marker='o', s=90, color='#f78166', edgecolors='white', lw=1.5, zorder=11)

    ax.annotate("Broad Flank Canopy\n(Fills Empty Lat Space!)", 
                xy=(24, 60), xytext=(4, 50),
                arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.5),
                color="#00ff88", fontsize=8.5, weight='bold', zorder=12)

    ax.annotate("Clean Air Gap\n(Zero pull on 176mm panel)", 
                xy=(77.5, 53), xytext=(98, 48),
                arrowprops=dict(arrowstyle="->", color="#f78166", lw=1.5),
                color="#f78166", fontsize=8.5, weight='bold', zorder=12)

    ax.set_xlim(-5, 125)
    ax.set_ylim(-2, 98)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=2, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=8.5)

    out_file = os.path.join(out_dir, "rendering_back_view.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=220, facecolor='#07090e')
    plt.close()
    print("Saved Updated Back Rendering to:", out_file)

render_front()
render_back()
print("Detached shirt-mounted renderings complete!")
