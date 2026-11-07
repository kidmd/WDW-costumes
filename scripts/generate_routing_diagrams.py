import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Ensure output directory
out_dir = r"C:\Users\Kiddi\.gemini\antigravity\brain\bfa4167c-5abb-4691-97fc-48e297e7effa"
os.makedirs(out_dir, exist_ok=True)

plt.style.use('dark_background')

def draw_option_a():
    """Option A: Double-Track Marquee Frame with Single Shoulder Bridge"""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=200)
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')
    
    # Title & Header
    plt.title("OPTION A: Double-Track Marquee Frame (50 LEDs @ 10cm Pitch)", 
              fontsize=16, color='#58a6ff', weight='bold', pad=15)
    
    # Subtitle
    ax.text(0.5, 0.96, "Effective 5cm bulb spacing via folded wire tracks | Single shoulder bridge", 
            transform=ax.transAxes, ha='center', fontsize=11, color='#8b949e')

    # Front Plate
    front_plate = patches.FancyBboxPatch((40, 20), 40, 40, boxstyle="round,pad=1.5", 
                                        ec="#ff0055", fc="#161b22", lw=2)
    ax.add_patch(front_plate)
    ax.text(60, 40, "CHEST PLATE\n(Title Drum)\n17.6 x 17.6 cm\n22 LEDs (220cm)", 
            ha='center', va='center', color='white', weight='bold', fontsize=11)
    
    # Back Plate
    back_plate = patches.FancyBboxPatch((140, 20), 40, 40, boxstyle="round,pad=1.5", 
                                       ec="#00ff66", fc="#161b22", lw=2)
    ax.add_patch(back_plate)
    ax.text(160, 40, "BACK PLATE\n(Pete's Dragon)\n17.6 x 17.6 cm\n23 LEDs (230cm)", 
            ha='center', va='center', color='white', weight='bold', fontsize=11)

    # Shoulder Bridge
    shoulder_box = patches.FancyBboxPatch((90, 75), 40, 14, boxstyle="round,pad=1.0",
                                         ec="#a371f7", fc="#21262d", lw=1.5, ls="--")
    ax.add_patch(shoulder_box)
    ax.text(110, 82, "LEFT SHOULDER BRIDGE\n5 LEDs (50cm pitch)", 
            ha='center', va='center', color='#d2a8ff', weight='bold', fontsize=10)

    # Wire tracks for Front Plate
    t1_x = [37, 83, 83, 37, 37]
    t1_y = [17, 17, 63, 63, 17]
    ax.plot(t1_x, t1_y, color='#30363d', lw=4, zorder=2)
    ax.plot(t1_x, t1_y, color='#ff7b72', lw=2, ls='-', zorder=3, label="Track A (Primary)")

    t2_x = [43, 43, 77, 77, 43]
    t2_y = [23, 57, 57, 23, 23]
    ax.plot(t2_x, t2_y, color='#30363d', lw=4, zorder=2)
    ax.plot(t2_x, t2_y, color='#ffa657', lw=2, ls='--', zorder=3, label="Track B (Folded Return)")

    outer_pts = []
    for x in np.linspace(37, 83, 3): outer_pts.append((x, 17))
    for y in np.linspace(25, 55, 3): outer_pts.append((83, y))
    for x in np.linspace(83, 37, 3): outer_pts.append((x, 63))
    for y in np.linspace(50, 30, 2): outer_pts.append((37, y))

    inner_pts = []
    for x in np.linspace(48, 72, 3): inner_pts.append((x, 23))
    for y in np.linspace(30, 50, 3): inner_pts.append((77, y))
    for x in np.linspace(72, 48, 3): inner_pts.append((x, 57))
    for y in np.linspace(45, 35, 2): inner_pts.append((43, y))

    for i, (x, y) in enumerate(outer_pts + inner_pts[:11]):
        ax.scatter(x, y, s=120, color='#ffe600', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#ffcc00', alpha=0.25, zorder=4)

    # Bridge
    bridge_x = [37, 50, 90, 110, 130, 143]
    bridge_y = [63, 75, 82, 82, 82, 63]
    ax.plot(bridge_x, bridge_y, color='#d2a8ff', lw=3, zorder=3)
    
    sh_pts = [(50, 75), (90, 82), (100, 82), (110, 82), (130, 82)]
    for i, (x, y) in enumerate(sh_pts):
        ax.scatter(x, y, s=120, color='#79c0ff', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#388bfd', alpha=0.3, zorder=4)
        ax.text(x, y+4, f"S{i+1}", ha='center', color='#79c0ff', fontsize=8, weight='bold')

    # Back Plate Tracks & LEDs
    b_out_x = [137, 183, 183, 137, 137]
    b_out_y = [17, 17, 63, 63, 17]
    ax.plot(b_out_x, b_out_y, color='#7ee787', lw=2, zorder=3)
    
    b_in_x = [143, 143, 177, 177, 143]
    b_in_y = [23, 57, 57, 23, 23]
    ax.plot(b_in_x, b_in_y, color='#56d364', lw=2, ls='--', zorder=3)

    back_pts = []
    for x in np.linspace(137, 183, 3): back_pts.append((x, 17))
    for y in np.linspace(25, 55, 3): back_pts.append((183, y))
    for x in np.linspace(183, 137, 3): back_pts.append((x, 63))
    for y in np.linspace(50, 30, 3): back_pts.append((137, y))
    for x in np.linspace(148, 172, 3): back_pts.append((x, 23))
    for y in np.linspace(30, 50, 3): back_pts.append((177, y))
    for x in np.linspace(172, 148, 3): back_pts.append((x, 57))
    for y in np.linspace(45, 35, 2): back_pts.append((143, y))

    for i, (x, y) in enumerate(back_pts[:23]):
        ax.scatter(x, y, s=120, color='#ffe600', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#ffcc00', alpha=0.25, zorder=4)

    clip_pts = [(37, 17), (83, 17), (83, 63), (37, 63), (90, 82), (130, 82), (137, 17), (183, 17), (183, 63), (137, 63)]
    for cx, cy in clip_pts:
        ax.scatter(cx, cy, marker='s', s=140, color='#f78166', edgecolors='white', lw=1.5, zorder=6)
    
    ax.scatter([], [], marker='s', s=100, color='#f78166', edgecolors='white', label="3D Printed Snap Clip")
    ax.scatter([], [], s=100, color='#ffe600', edgecolors='white', label="Lit Marquee LED (10cm pitch)")
    ax.scatter([], [], s=100, color='#79c0ff', edgecolors='white', label="Shoulder Epaulet LED")

    ax.annotate("Fold Point: Wire loops\nback inside rim channel", 
                xy=(83, 63), xytext=(95, 45),
                arrowprops=dict(arrowstyle="->", color="#ffa657", lw=1.5),
                color="#ffa657", fontsize=10, weight='bold')

    ax.annotate("Controller Lead In\n(From Running Belt)", 
                xy=(37, 17), xytext=(15, 5),
                arrowprops=dict(arrowstyle="->", color="#58a6ff", lw=1.5),
                color="#58a6ff", fontsize=10, weight='bold')

    ax.set_xlim(5, 205)
    ax.set_ylim(-5, 100)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=4, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=10)

    out_path = os.path.join(out_dir, "routing_option_a_marquee.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, facecolor='#0d1117')
    plt.close()
    print("Saved Option A to:", out_path)

def draw_option_b():
    """Option B: Parade Harness / Suspenders (Twin Shoulder Bridge)"""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=200)
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')
    
    plt.title("OPTION B: Twin-Shoulder Parade Suspenders (50 LEDs @ 10cm Pitch)", 
              fontsize=16, color='#58a6ff', weight='bold', pad=15)
    ax.text(0.5, 0.96, "Balanced 360-degree fleet visibility | Up right shoulder, down left shoulder", 
            transform=ax.transAxes, ha='center', fontsize=11, color='#8b949e')

    front_plate = patches.FancyBboxPatch((40, 25), 40, 40, boxstyle="round,pad=1.5", 
                                        ec="#ff0055", fc="#161b22", lw=2)
    ax.add_patch(front_plate)
    ax.text(60, 45, "CHEST PLATE\n(Title Drum)\n18 LEDs (180cm)", 
            ha='center', va='center', color='white', weight='bold', fontsize=11)
    
    back_plate = patches.FancyBboxPatch((140, 25), 40, 40, boxstyle="round,pad=1.5", 
                                       ec="#00ff66", fc="#161b22", lw=2)
    ax.add_patch(back_plate)
    ax.text(160, 45, "BACK PLATE\n(Pete's Dragon)\n18 LEDs (180cm)", 
            ha='center', va='center', color='white', weight='bold', fontsize=11)

    # Right Shoulder Bridge
    ax.plot([78, 90, 110, 130, 142], [67, 85, 88, 85, 67], color='#3fb950', lw=3, zorder=3, label="Right Shoulder (4 LEDs / 40cm)")
    r_sh_pts = [(90, 85), (103, 88), (117, 88), (130, 85)]
    for i, (x, y) in enumerate(r_sh_pts):
        ax.scatter(x, y, s=120, color='#3fb950', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#2ea043', alpha=0.3, zorder=4)
        ax.text(x, y+4, f"R{i+1}", ha='center', color='#3fb950', fontsize=8, weight='bold')

    # Left Shoulder Bridge
    ax.plot([142, 130, 110, 90, 78], [23, 5, 2, 5, 23], color='#d2a8ff', lw=3, zorder=3, label="Left Shoulder Return (4 LEDs / 40cm)")
    l_sh_pts = [(130, 5), (117, 2), (103, 2), (90, 5)]
    for i, (x, y) in enumerate(l_sh_pts):
        ax.scatter(x, y, s=120, color='#d2a8ff', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#a371f7', alpha=0.3, zorder=4)
        ax.text(x, y-6, f"L{i+1}", ha='center', color='#d2a8ff', fontsize=8, weight='bold')

    fp_x = [38, 82, 82, 38, 38]
    fp_y = [23, 23, 67, 67, 23]
    ax.plot(fp_x, fp_y, color='#ff7b72', lw=2, zorder=3)
    
    front_leds = []
    for x in np.linspace(40, 80, 5): front_leds.append((x, 23))
    for y in np.linspace(34, 56, 4): front_leds.append((82, y))
    for x in np.linspace(80, 40, 5): front_leds.append((x, 67))
    for y in np.linspace(56, 34, 4): front_leds.append((38, y))

    for x, y in front_leds:
        ax.scatter(x, y, s=120, color='#ffe600', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#ffcc00', alpha=0.25, zorder=4)

    bp_x = [138, 182, 182, 138, 138]
    bp_y = [23, 23, 67, 67, 23]
    ax.plot(bp_x, bp_y, color='#56d364', lw=2, zorder=3)

    back_leds = []
    for x in np.linspace(140, 180, 5): back_leds.append((x, 23))
    for y in np.linspace(34, 56, 4): back_leds.append((182, y))
    for x in np.linspace(180, 140, 5): back_leds.append((x, 67))
    for y in np.linspace(56, 34, 4): back_leds.append((138, y))

    for x, y in back_leds:
        ax.scatter(x, y, s=120, color='#ffe600', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(x, y, s=350, color='#ffcc00', alpha=0.25, zorder=4)

    belt_x = [38, 30, 25, 20, 15, 10]
    belt_y = [23, 18, 14, 10, 6, 2]
    ax.plot(belt_x, belt_y, color='#58a6ff', lw=2.5, ls=':', zorder=3)
    for i, (bx, by) in enumerate(zip(belt_x[1:], belt_y[1:])):
        ax.scatter(bx, by, s=90, color='#58a6ff', edgecolors='white', lw=1.0, zorder=5)
    
    ax.text(10, -3, "Controller & Battery\n(Waist Belt)", ha='center', color='#58a6ff', fontsize=9, weight='bold')

    clips = [(38, 23), (82, 23), (82, 67), (38, 67), (90, 85), (130, 85), 
             (138, 23), (182, 23), (182, 67), (138, 67), (90, 5), (130, 5)]
    for cx, cy in clips:
        ax.scatter(cx, cy, marker='s', s=140, color='#f78166', edgecolors='white', lw=1.5, zorder=6)

    ax.scatter([], [], marker='s', s=100, color='#f78166', edgecolors='white', label="3D Printed Snap Clip")
    ax.scatter([], [], s=100, color='#ffe600', edgecolors='white', label="Plate Border LED (10cm pitch)")

    ax.set_xlim(0, 200)
    ax.set_ylim(-12, 100)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=4, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=10)

    out_path = os.path.join(out_dir, "routing_option_b_suspenders.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, facecolor='#0d1117')
    plt.close()
    print("Saved Option B to:", out_path)

def draw_option_c():
    """Option C: Scalloped Baroque Arches"""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=200)
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')
    
    plt.title("OPTION C: Scalloped Baroque Arches (50 LEDs @ 10cm Pitch)", 
              fontsize=16, color='#58a6ff', weight='bold', pad=15)
    ax.text(0.5, 0.96, "Bowed 10cm wire arches create classic Main Street Electrical Parade float scalloping", 
            transform=ax.transAxes, ha='center', fontsize=11, color='#8b949e')

    front_plate = patches.FancyBboxPatch((40, 25), 40, 40, boxstyle="round,pad=1.5", 
                                        ec="#ff0055", fc="#161b22", lw=2)
    ax.add_patch(front_plate)
    ax.text(60, 45, "CHEST PLATE\n(Title Drum)\n20 LEDs in Arches", 
            ha='center', va='center', color='white', weight='bold', fontsize=11)
    
    back_plate = patches.FancyBboxPatch((140, 25), 40, 40, boxstyle="round,pad=1.5", 
                                       ec="#00ff66", fc="#161b22", lw=2)
    ax.add_patch(back_plate)
    ax.text(160, 45, "BACK PLATE\n(Pete's Dragon)\n24 LEDs in Arches", 
            ha='center', va='center', color='white', weight='bold', fontsize=11)

    def draw_arch(p1, p2, outward_offset, color='#ffa657'):
        mid_x = (p1[0] + p2[0]) / 2 + outward_offset[0]
        mid_y = (p1[1] + p2[1]) / 2 + outward_offset[1]
        t = np.linspace(0, 1, 20)
        arch_x = (1-t)**2 * p1[0] + 2*(1-t)*t * mid_x + t**2 * p2[0]
        arch_y = (1-t)**2 * p1[1] + 2*(1-t)*t * mid_y + t**2 * p2[1]
        ax.plot(arch_x, arch_y, color=color, lw=2, zorder=3)
        ax.scatter(mid_x, mid_y, s=130, color='#ffe600', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(mid_x, mid_y, s=380, color='#ffcc00', alpha=0.3, zorder=4)

    xs = np.linspace(40, 80, 6)
    for i in range(5): draw_arch((xs[i], 65), (xs[i+1], 65), (0, 5))
    for i in range(5): draw_arch((xs[i], 25), (xs[i+1], 25), (0, -5))
    ys = np.linspace(25, 65, 6)
    for i in range(5): draw_arch((40, ys[i]), (40, ys[i+1]), (-5, 0))
    for i in range(5): draw_arch((80, ys[i]), (80, ys[i+1]), (5, 0))

    sh_x = [40, 55, 90, 110, 130, 140]
    sh_y = [65, 78, 85, 85, 85, 65]
    ax.plot(sh_x, sh_y, color='#d2a8ff', lw=3, zorder=3, label="Shoulder Bridge (6 LEDs)")
    for px, py in [(55, 78), (90, 85), (100, 85), (110, 85), (120, 85), (130, 85)]:
        ax.scatter(px, py, s=120, color='#79c0ff', edgecolors='white', lw=1.5, zorder=5)
        ax.scatter(px, py, s=350, color='#388bfd', alpha=0.3, zorder=4)

    b_xs = np.linspace(140, 180, 7)
    for i in range(6): draw_arch((b_xs[i], 65), (b_xs[i+1], 65), (0, 5), color='#7ee787')
    for i in range(6): draw_arch((b_xs[i], 25), (b_xs[i+1], 25), (0, -5), color='#7ee787')
    b_ys = np.linspace(25, 65, 7)
    for i in range(6): draw_arch((140, b_ys[i]), (140, b_ys[i+1]), (-5, 0), color='#7ee787')
    for i in range(6): draw_arch((180, b_ys[i]), (180, b_ys[i+1]), (5, 0), color='#7ee787')

    for x in xs:
        ax.scatter(x, 65, marker='s', s=80, color='#f78166', edgecolors='white', zorder=6)
        ax.scatter(x, 25, marker='s', s=80, color='#f78166', edgecolors='white', zorder=6)
    for y in ys:
        ax.scatter(40, y, marker='s', s=80, color='#f78166', edgecolors='white', zorder=6)
        ax.scatter(80, y, marker='s', s=80, color='#f78166', edgecolors='white', zorder=6)

    ax.scatter([], [], marker='s', s=100, color='#f78166', edgecolors='white', label="Clip Anchors (Hold 10cm wire span)")
    ax.scatter([], [], s=100, color='#ffe600', edgecolors='white', label="Apex LED (Bowed Out)")

    ax.set_xlim(15, 200)
    ax.set_ylim(5, 100)
    ax.axis('off')
    ax.legend(loc='lower center', ncol=3, frameon=True, facecolor='#161b22', edgecolor='#30363d', fontsize=10)

    out_path = os.path.join(out_dir, "routing_option_c_scalloped.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, facecolor='#0d1117')
    plt.close()
    print("Saved Option C to:", out_path)

draw_option_a()
draw_option_b()
draw_option_c()
print("All 3 engineering diagrams created successfully!")
