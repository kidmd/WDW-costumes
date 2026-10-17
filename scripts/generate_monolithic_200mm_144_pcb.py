import os
import json
import zipfile
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB_DIR = os.path.join(BASE_DIR, "pcb")
MONO_144_DIR = os.path.join(PCB_DIR, "monolithic_200mm_144")
os.makedirs(MONO_144_DIR, exist_ok=True)

# -------------------------------------------------------------
# Configuration: Monolithic 200mm x 200mm 12x12 Staggered Brick Matrix
# Pure Single-Sided SMT Assembly (100% Top-Layer Components)
# Solder pins for IN and OUT (No SMT connectors on bottom!)
# Total LEDs: 144 WS2812B-2020 LEDs (C52917434)
# -------------------------------------------------------------
BOARD_SIZE_MM = 200.0
GRID_ROWS = 12
GRID_COLS = 12
NUM_LEDS = GRID_ROWS * GRID_COLS  # 144 LEDs

PITCH_X = 15.50
PITCH_Y = 16.00
ROW_OFFSET = PITCH_X / 2.0  # 7.75 mm

MARGIN_T = 12.00
MARGIN_L1 = 10.875

led_positions = []
led_idx = 1

for r in range(GRID_ROWS):
    y = round(MARGIN_T + r * PITCH_Y, 2)
    row_shift = ROW_OFFSET if (r % 2 == 1) else 0.0
    col_range = range(GRID_COLS) if (r % 2 == 0) else range(GRID_COLS - 1, -1, -1)
    
    for c in col_range:
        x = round(MARGIN_L1 + row_shift + c * PITCH_X, 2)
        led_positions.append({
            "id": led_idx,
            "ref": f"D{led_idx}",
            "cap_ref": f"C{led_idx}",
            "row": r + 1,
            "col": c + 1,
            "x": x,
            "y": y
        })
        led_idx += 1

# -------------------------------------------------------------
# Solder Pin Headers: 2.54mm Pitch Plated Through-Hole (PTH)
# Can be soldered from TOP or BOTTOM!
# -------------------------------------------------------------
solder_ports = [
    {
        "name": "IN",
        "label": "DATA IN",
        "x": 30.0,
        "y": 192.0,
        "pins": [
            {"num": 1, "label": "+5V", "net": 1, "net_name": "+5V", "x": 30.0 - 2.54, "y": 192.0},
            {"num": 2, "label": "DAT", "net": 3, "net_name": "DATA_1", "x": 30.0,        "y": 192.0},
            {"num": 3, "label": "GND", "net": 2, "net_name": "GND",    "x": 30.0 + 2.54, "y": 192.0},
        ],
        "strain_holes": [
            {"x": 26.0, "y": 186.5, "drill": 2.2},
            {"x": 34.0, "y": 186.5, "drill": 2.2},
        ]
    },
    {
        "name": "OUT",
        "label": "DATA OUT",
        "x": 170.0,
        "y": 192.0,
        "pins": [
            {"num": 1, "label": "+5V", "net": 1, "net_name": "+5V", "x": 170.0 - 2.54, "y": 192.0},
            {"num": 2, "label": "DAT", "net": NUM_LEDS + 3, "net_name": f"DATA_{NUM_LEDS+1}", "x": 170.0, "y": 192.0},
            {"num": 3, "label": "GND", "net": 2, "net_name": "GND", "x": 170.0 + 2.54, "y": 192.0},
        ],
        "strain_holes": [
            {"x": 166.0, "y": 186.5, "drill": 2.2},
            {"x": 174.0, "y": 186.5, "drill": 2.2},
        ]
    }
]

# Mounting & Sewing Features
m3_holes = [
    {"ref": "H1", "x": 6.0,   "y": 6.0,   "drill": 3.2, "pad": 5.0, "label": "M3"},
    {"ref": "H2", "x": 194.0, "y": 6.0,   "drill": 3.2, "pad": 5.0, "label": "M3"},
    {"ref": "H3", "x": 6.0,   "y": 194.0, "drill": 3.2, "pad": 5.0, "label": "M3"},
    {"ref": "H4", "x": 194.0, "y": 194.0, "drill": 3.2, "pad": 5.0, "label": "M3"},
]

sew_holes = [
    # Top edge
    {"ref": "S1", "x": 50.0,  "y": 5.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S2", "x": 100.0, "y": 5.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S3", "x": 150.0, "y": 5.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    # Bottom edge
    {"ref": "S4", "x": 75.0,  "y": 195.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S5", "x": 100.0, "y": 195.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S6", "x": 125.0, "y": 195.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    # Left edge
    {"ref": "S7", "x": 5.0, "y": 50.0,  "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S8", "x": 5.0, "y": 100.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S9", "x": 5.0, "y": 150.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    # Right edge
    {"ref": "S10", "x": 195.0, "y": 50.0,  "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S11", "x": 195.0, "y": 100.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S12", "x": 195.0, "y": 150.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
]

# -------------------------------------------------------------
# 1. Generate JLCPCB BOM File (Pure Single-Sided: LEDs + Caps ONLY!)
# -------------------------------------------------------------
bom_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144_bom.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write("Comment,Designator,Footprint,LCSC Part #\n")
    led_refs = " ".join([d["ref"] for d in led_positions])
    cap_refs = " ".join([d["cap_ref"] for d in led_positions])
    f.write(f'WS2812B-2020-V6,"{led_refs}",LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm,C52917434\n')
    f.write(f'100nF (0.1uF) 50V 0402,"{cap_refs}",Capacitor_SMD:C_0402_1005Metric,C1525\n')

print(f"Generated BOM (100% Single-Sided): {bom_path}")

# -------------------------------------------------------------
# 2. Generate JLCPCB CPL (Centroid) File (100% Top Layer Only!)
# -------------------------------------------------------------
cpl_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144_cpl.csv")
with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("Designator,Val,Package,Mid X,Mid Y,Rotation,Layer\n")
    for d in led_positions:
        f.write(f'{d["ref"]},WS2812B-2020,LED_WS2812B-2020,{d["x"]:.2f},{d["y"]:.2f},0.0,Top\n')
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f'{d["cap_ref"]},100nF,C_0402,{cx:.2f},{cy:.2f},90.0,Top\n')

print(f"Generated CPL (100% Top Layer): {cpl_path}")

# -------------------------------------------------------------
# 3. Generate KiCad PCB (.kicad_pcb) File
# -------------------------------------------------------------
kicad_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.kicad_pcb")
num_nets = NUM_LEDS + 4

kicad_content = f"""(kicad_pcb (version 20211014) (generator "Antigravity Imagineering Engine")
  (general
    (thickness 1.6)
    (drawings 0)
    (tracks 0)
    (zones 0)
    (modules {NUM_LEDS * 2 + len(m3_holes) + len(sew_holes)})
    (nets {num_nets})
  )
  (page A4)
  (layers
    (0 F.Cu signal)
    (31 B.Cu signal)
    (32 B.Paste user)
    (34 B.SilkS user)
    (35 F.Paste user)
    (36 F.SilkS user)
    (37 B.Mask user)
    (38 F.Mask user)
    (44 Edge.Cuts user)
  )
  (setup
    (last_trace_width 0.3)
    (pad_to_mask_clearance 0.05)
    (solder_mask_min_width 0.1)
  )
  (net 0 "")
  (net 1 "+5V")
  (net 2 "GND")
"""

for i in range(1, NUM_LEDS + 2):
    kicad_content += f'  (net {i+2} "DATA_{i}")\n'

b = BOARD_SIZE_MM
kicad_content += f"""  (gr_line (start 0 0) (end {b} 0) (layer Edge.Cuts) (width 0.15))
  (gr_line (start {b} 0) (end {b} {b}) (layer Edge.Cuts) (width 0.15))
  (gr_line (start {b} {b}) (end 0 {b}) (layer Edge.Cuts) (width 0.15))
  (gr_line (start 0 {b}) (end 0 0) (layer Edge.Cuts) (width 0.15))
"""

# M3 Holes
for h in m3_holes:
    kicad_content += f"""  (module "MountingHole:MountingHole_3.2mm_M3" (layer F.Cu) (tedit 5D5A6E4F)
    (at {h['x']} {h['y']})
    (descr "Mounting Hole 3.2mm M3")
    (path "/{h['ref']}")
    (fp_text reference "{h['ref']}" (at 0 -2.5) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (pad 1 thru_hole circle (at 0 0) (size {h['pad']} {h['pad']}) (drill {h['drill']}) (layers *.Cu *.Mask))
  )
"""

# Sewing Eyelets
for s in sew_holes:
    kicad_content += f"""  (module "MountingHole:MountingHole_2.0mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {s['x']} {s['y']})
    (descr "Fabric Sewing Eyelet 2.0mm")
    (path "/{s['ref']}")
    (fp_text reference "{s['ref']}" (at 0 -2.0) (layer F.SilkS)
      (effects (font (size 0.6 0.6) (thickness 0.1)))
    )
    (pad 1 thru_hole circle (at 0 0) (size {s['pad']} {s['pad']}) (drill {s['drill']}) (layers *.Cu *.Mask))
  )
"""

# 2.54mm Through-Hole Solder Pin Headers for IN and OUT (Both Sides Soldering!)
for sp in solder_ports:
    pname = sp["name"]
    plabel = sp["label"]
    px = sp["x"]
    py = sp["y"]
    
    # Solder header module with 3 pins
    kicad_content += f"""  (module "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical" (layer F.Cu) (tedit 5D5A6E4F)
    (at {px} {py})
    (descr "2.54mm Pin Header for {plabel}")
    (path "/HDR_{pname}")
    (fp_text reference "J_{pname}" (at 0 -3.0) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (fp_text user "[{pname}]" (at 0 3.0) (layer F.SilkS)
      (effects (font (size 0.65 0.65) (thickness 0.12)))
    )
    (fp_text user "[{pname}]" (at 0 3.0) (layer B.SilkS)
      (effects (font (size 0.65 0.65) (thickness 0.12)))
    )
    (fp_line (start -4.0 -1.6) (end 4.0 -1.6) (layer F.SilkS) (width 0.15))
    (fp_line (start 4.0 -1.6) (end 4.0 1.6) (layer F.SilkS) (width 0.15))
    (fp_line (start 4.0 1.6) (end -4.0 1.6) (layer F.SilkS) (width 0.15))
    (fp_line (start -4.0 1.6) (end -4.0 -1.6) (layer F.SilkS) (width 0.15))
    (fp_line (start -4.0 -1.6) (end 4.0 -1.6) (layer B.SilkS) (width 0.15))
    (fp_line (start 4.0 -1.6) (end 4.0 1.6) (layer B.SilkS) (width 0.15))
    (fp_line (start 4.0 1.6) (end -4.0 1.6) (layer B.SilkS) (width 0.15))
    (fp_line (start -4.0 1.6) (end -4.0 -1.6) (layer B.SilkS) (width 0.15))
"""
    for pin in sp["pins"]:
        p_xoff = round(pin["x"] - px, 2)
        kicad_content += f"""    (pad {pin['num']} thru_hole circle (at {p_xoff} 0) (size 2.2 2.2) (drill 1.2) (layers *.Cu *.Mask) (net {pin['net']}))
    (fp_text user "{pin['label']}" (at {p_xoff} -2.0) (layer F.SilkS) (effects (font (size 0.55 0.55) (thickness 0.1))))
    (fp_text user "{pin['label']}" (at {p_xoff} -2.0) (layer B.SilkS) (effects (font (size 0.55 0.55) (thickness 0.1))))
"""
    kicad_content += "  )\n"
    
    # Strain Relief Non-Plated Holes
    for sh_idx, sh in enumerate(sp["strain_holes"]):
        kicad_content += f"""  (module "MountingHole:MountingHole_2.2mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {sh['x']} {sh['y']})
    (descr "Wire Strain Relief Hole 2.2mm")
    (path "/STRAIN_{pname}_{sh_idx+1}")
    (pad 1 np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers *.Mask))
  )
"""

# Place 144 WS2812B-2020 LEDs on F.Cu
for d in led_positions:
    x = d["x"]
    y = d["y"]
    i = d["id"]
    net_din = 2 + i
    net_dout = 3 + i
    
    kicad_content += f"""  (module "LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {x} {y})
    (descr "WS2812B-2020 RGB LED")
    (path "/{d['ref']}")
    (fp_text reference "{d['ref']}" (at 0 0) (layer F.SilkS) hide
      (effects (font (size 0.5 0.5) (thickness 0.08)))
    )
    (fp_text user "{i}" (at 0 -2.4) (layer F.SilkS)
      (effects (font (size 0.65 0.65) (thickness 0.12)))
    )
    (fp_line (start -1.0 -1.0) (end 1.0 -1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start 1.0 -1.0) (end 1.0 1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start 1.0 1.0) (end -1.0 1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start -1.0 1.0) (end -1.0 -1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start -0.9 -0.4) (end -0.4 -0.9) (layer F.SilkS) (width 0.15))
    (pad 1 smd rect (at -0.85 -0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net 1))
    (pad 2 smd rect (at -0.85 0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net {net_dout}))
    (pad 3 smd rect (at 0.85 0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net 2))
    (pad 4 smd rect (at 0.85 -0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net {net_din}))
  )
"""
    cx = round(x + 2.0, 2)
    cy = y
    kicad_content += f"""  (module "Capacitor_SMD:C_0402_1005Metric" (layer F.Cu) (tedit 5D5A6E4F)
    (at {cx} {cy} 90)
    (descr "Capacitor SMD 0402 (1005 Metric)")
    (path "/{d['cap_ref']}")
    (fp_text reference "{d['cap_ref']}" (at 0 0 90) (layer F.SilkS) hide
      (effects (font (size 0.5 0.5) (thickness 0.08)))
    )
    (pad 1 smd roundrect (at -0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (roundrect_rratio 0.25) (net 1))
    (pad 2 smd roundrect (at 0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (roundrect_rratio 0.25) (net 2))
  )
"""

# Power routing segments
for d in led_positions:
    x = d["x"]
    y = d["y"]
    p_5v = (round(x - 0.85, 2), round(y - 0.65, 2))
    p_gnd = (round(x + 0.85, 2), round(y + 0.65, 2))
    c_5v = (round(x + 2.0, 2), round(y - 0.48, 2))
    c_gnd = (round(x + 2.0, 2), round(y + 0.48, 2))
    gnd_via = (round(x + 2.0, 2), round(y + 1.2, 2))
    
    kicad_content += f'  (segment (start {p_5v[0]} {p_5v[1]}) (end {c_5v[0]} {c_5v[1]}) (width 0.4) (layer F.Cu) (net 1))\n'
    kicad_content += f'  (segment (start {p_gnd[0]} {p_gnd[1]}) (end {c_gnd[0]} {c_gnd[1]}) (width 0.4) (layer F.Cu) (net 2))\n'
    kicad_content += f'  (segment (start {c_gnd[0]} {c_gnd[1]}) (end {gnd_via[0]} {gnd_via[1]}) (width 0.4) (layer F.Cu) (net 2))\n'
    kicad_content += f'  (via (at {gnd_via[0]} {gnd_via[1]}) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net 2))\n'

# Daisy chain data traces 1..144
for i in range(NUM_LEDS - 1):
    d1 = led_positions[i]
    d2 = led_positions[i + 1]
    net_id = 3 + d1["id"]
    p1_dout = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
    p2_din = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
    kicad_content += f'  (segment (start {p1_dout[0]} {p1_dout[1]}) (end {p2_din[0]} {p2_din[1]}) (width 0.25) (layer F.Cu) (net {net_id}))\n'
    
    c1_5v = (round(d1["x"] + 2.0, 2), round(d1["y"] - 0.48, 2))
    c2_5v = (round(d2["x"] + 2.0, 2), round(d2["y"] - 0.48, 2))
    if d1["row"] == d2["row"]:
        kicad_content += f'  (segment (start {c1_5v[0]} {c1_5v[1]}) (end {c2_5v[0]} {c2_5v[1]}) (width 0.8) (layer F.Cu) (net 1))\n'

# Connect IN Header (Pin 2: DAT) to LED 1
led1 = led_positions[0]
p1_din = (round(led1["x"] + 0.85, 2), round(led1["y"] - 0.65, 2))
kicad_content += f'  (segment (start 30.0 192.0) (end 30.0 180.0) (width 0.3) (layer F.Cu) (net 3))\n'
kicad_content += f'  (segment (start 30.0 180.0) (end {p1_din[0]} {p1_din[1]}) (width 0.25) (layer F.Cu) (net 3))\n'

# Connect LED 144 to OUT Header (Pin 2: DAT)
led_last = led_positions[-1]
plast_dout = (round(led_last["x"] - 0.85, 2), round(led_last["y"] + 0.65, 2))
kicad_content += f'  (segment (start {plast_dout[0]} {plast_dout[1]}) (end 170.0 180.0) (width 0.25) (layer F.Cu) (net {NUM_LEDS+3}))\n'
kicad_content += f'  (segment (start 170.0 180.0) (end 170.0 192.0) (width 0.3) (layer F.Cu) (net {NUM_LEDS+3}))\n'

# Ground Zone on B.Cu
kicad_content += f"""  (zone (net 2) (net_name "GND") (layer B.Cu) (tstamp 0) (hatch edge 0.5)
    (connect_pads yes (clearance 0.25))
    (min_thickness 0.25)
    (fill yes (arc_segments 16) (thermal_gap 0.25) (thermal_bridge_width 0.3))
    (polygon
      (pts
        (xy 1 1) (xy {b-1} 1) (xy {b-1} {b-1}) (xy 1 {b-1})
      )
    )
  )
)
"""

with open(kicad_path, "w", encoding="utf-8") as f:
    f.write(kicad_content)

print(f"Generated KiCad PCB: {kicad_path}")

pro_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.pro")
with open(pro_path, "w", encoding="utf-8") as f:
    f.write("[general]\nversion=1\n")

kicad_pro_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.kicad_pro")
with open(kicad_pro_path, "w", encoding="utf-8") as f:
    f.write('{"meta":{"version":1},"sheets":[]}')

# SMT Assembly Bundle ZIP
zip_smt_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144_smt.zip")
with zipfile.ZipFile(zip_smt_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(bom_path, os.path.basename(bom_path))
    z.write(cpl_path, os.path.basename(cpl_path))

print(f"Generated SMT Assembly Bundle: {zip_smt_path}")

# -------------------------------------------------------------
# 4. Generate Native RS-274X Gerber & Excellon Drill Files
# -------------------------------------------------------------
def coord_gbr(x, y):
    return f"X{int(round(x * 1000000)):d}Y{int(round(y * 1000000)):d}"

# Board Outline (.GKO)
gko_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GKO")
with open(gko_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Board Outline*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
X0Y0D02*
X200000000Y0D01*
X200000000Y200000000D01*
X0Y200000000D01*
X0Y0D01*
M02*
""")

# Drill File (.DRL)
drl_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.DRL")
with open(drl_path, "w", encoding="utf-8") as f:
    f.write("""M48
METRIC
T1C3.200
T2C2.000
T3C0.400
T4C1.200
T5C2.200
%
G90
G05
T1
""")
    for h in m3_holes:
        f.write(f"X{h['x']:.3f}Y{h['y']:.3f}\n")
    f.write("T2\n")
    for s in sew_holes:
        f.write(f"X{s['x']:.3f}Y{s['y']:.3f}\n")
    f.write("T3\n")
    for d in led_positions:
        f.write(f"X{round(d['x'] + 2.0, 3):.3f}Y{round(d['y'] + 1.2, 3):.3f}\n")
    f.write("T4\n")
    for sp in solder_ports:
        for pin in sp["pins"]:
            f.write(f"X{pin['x']:.3f}Y{pin['y']:.3f}\n")
    f.write("T5\n")
    for sp in solder_ports:
        for sh in sp["strain_holes"]:
            f.write(f"X{sh['x']:.3f}Y{sh['y']:.3f}\n")
    f.write("M30\n")

# Top Copper (.GTL)
gtl_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GTL")
with open(gtl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Copper (F.Cu) - Monolithic 144 LED Matrix (Pure Single-Sided)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.250*%
%ADD11C,0.800*%
%ADD12C,0.400*%
%ADD13R,0.600X0.500*%
%ADD14R,0.560X0.620*%
%ADD18C,0.800*%
%ADD19C,5.000*%
%ADD20C,3.500*%
%ADD21C,2.200*%
""")
    f.write("D19*\n")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D20*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    f.write("D21*\n")
    for sp in solder_ports:
        for pin in sp["pins"]:
            f.write(f"{coord_gbr(pin['x'], pin['y'])}D03*\n")
    f.write("D13*\n")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x - 0.85, y - 0.65)}D03*\n")
        f.write(f"{coord_gbr(x - 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y - 0.65)}D03*\n")
    f.write("D14*\n")
    for d in led_positions:
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("D18*\n")
    for d in led_positions:
        f.write(f"{coord_gbr(round(d['x'] + 2.0, 2), round(d['y'] + 1.2, 2))}D03*\n")
    f.write("D10*\n")
    for i in range(NUM_LEDS - 1):
        d1 = led_positions[i]
        d2 = led_positions[i + 1]
        p1 = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
        p2 = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
        f.write(f"{coord_gbr(p1[0], p1[1])}D02*\n")
        f.write(f"{coord_gbr(p2[0], p2[1])}D01*\n")
    f.write("M02*\n")

# Bottom Copper (.GBL) - Ground Plane and Solder Pad Annular Rings
gbl_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GBL")
with open(gbl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Copper (B.Cu)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.800*%
%ADD11C,5.000*%
%ADD12C,3.500*%
%ADD13R,196.000X196.000*%
%ADD14C,2.200*%
D13*
X100000000Y100000000D03*
D11*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D12*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    f.write("D14*\n")
    for sp in solder_ports:
        for pin in sp["pins"]:
            f.write(f"{coord_gbr(pin['x'], pin['y'])}D03*\n")
    f.write("M02*\n")

# Top Mask (.GTS)
gts_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GTS")
with open(gts_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Solder Mask*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10R,0.700X0.600*%
%ADD11R,0.660X0.720*%
%ADD12C,5.100*%
%ADD13C,3.600*%
%ADD14C,2.300*%
D12*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D13*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    f.write("D14*\n")
    for sp in solder_ports:
        for pin in sp["pins"]:
            f.write(f"{coord_gbr(pin['x'], pin['y'])}D03*\n")
    f.write("D10*\n")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x - 0.85, y - 0.65)}D03*\n")
        f.write(f"{coord_gbr(x - 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y - 0.65)}D03*\n")
    f.write("D11*\n")
    for d in led_positions:
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("M02*\n")

# Bottom Mask (.GBS) - Opens Solder Pins for Rear-Soldering!
gbs_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GBS")
with open(gbs_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Solder Mask*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,5.100*%
%ADD11C,3.600*%
%ADD12C,2.300*%
D10*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D11*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    f.write("D12*\n")
    for sp in solder_ports:
        for pin in sp["pins"]:
            f.write(f"{coord_gbr(pin['x'], pin['y'])}D03*\n")
    f.write("M02*\n")

# Top Paste (.GTP)
gtp_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GTP")
with open(gtp_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Paste*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10R,0.600X0.500*%
%ADD11R,0.560X0.620*%
D10*
""")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x - 0.85, y - 0.65)}D03*\n")
        f.write(f"{coord_gbr(x - 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y - 0.65)}D03*\n")
    f.write("D11*\n")
    for d in led_positions:
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("M02*\n")

# Bottom Paste (.GBP) - EMPTY! ZERO SMT PARTS ON BOTTOM!
gbp_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GBP")
with open(gbp_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Paste (Empty - 100% Single Sided)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
M02*
""")

# Top Silkscreen (.GTO)
gto_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GTO")
with open(gto_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Silkscreen*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
""")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D02*\n{coord_gbr(x+1.0, y-1.0)}D01*\n")
        f.write(f"{coord_gbr(x+1.0, y+1.0)}D01*\n{coord_gbr(x-1.0, y+1.0)}D01*\n")
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D01*\n")
    f.write("M02*\n")

# Bottom Silkscreen (.GBO)
gbo_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144.GBO")
with open(gbo_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Silkscreen*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
""")
    for sp in solder_ports:
        px = sp["x"]
        py = sp["y"]
        f.write(f"{coord_gbr(px - 4.5, py - 2.0)}D02*\n{coord_gbr(px + 4.5, py - 2.0)}D01*\n")
        f.write(f"{coord_gbr(px + 4.5, py + 2.0)}D01*\n{coord_gbr(px - 4.5, py + 2.0)}D01*\n")
        f.write(f"{coord_gbr(px - 4.5, py - 2.0)}D01*\n")
    f.write("M02*\n")

# Gerber ZIP
zip_gerbers_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144_gerbers.zip")
with zipfile.ZipFile(zip_gerbers_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in [gko_path, drl_path, gtl_path, gbl_path, gts_path, gbs_path, gto_path, gbo_path, gtp_path, gbp_path]:
        z.write(p, os.path.basename(p))

print(f"Generated Gerber ZIP: {zip_gerbers_path}")

# -------------------------------------------------------------
# 5. Interactive HTML Preview
# -------------------------------------------------------------
html_path = os.path.join(MONO_144_DIR, "monolithic_200mm_144_preview.html")
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Monolithic 200mm x 200mm (144 LEDs - Solder Pins) Inspector</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; text-align: center; }}
h1 {{ color: #38bdf8; margin-bottom: 5px; }}
p {{ color: #94a3b8; margin-top: 0; }}
.btn {{ background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin: 4px; }}
.btn:hover {{ background: #2563eb; }}
.btn.active {{ background: #10b981; }}
#viewport {{ width: 640px; height: 640px; margin: 20px auto; background: #020617; border: 2px solid #334155; border-radius: 8px; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
svg {{ width: 100%; height: 100%; }}
.stat-box {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
.stat {{ background: #1e293b; padding: 10px 18px; border-radius: 8px; border: 1px solid #334155; }}
.stat-val {{ font-size: 1.4em; font-weight: bold; color: #38bdf8; }}
.stat-lbl {{ font-size: 0.8em; color: #94a3b8; }}
.badge {{ display: inline-block; background: #059669; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; margin-bottom: 10px; }}
</style>
</head>
<body>
<h1>Monolithic 200mm x 200mm (144 LEDs)</h1>
<div class="badge">100% Single-Sided SMT (Economic PCBA - Saves $55 Setup!)</div>
<p>Through-Hole Solder Pins for IN & OUT • Can be soldered from Front or Back</p>
<div>
  <button id="btnFront" class="btn active" onclick="setView('front')">Front View (Flush LEDs)</button>
  <button id="btnRear" class="btn" onclick="setView('rear')">Rear View (Solder Pins & Strain Relief)</button>
</div>

<div id="viewport">
  <svg viewBox="0 0 200 200" id="pcbSvg">
    <rect x="0" y="0" width="200" height="200" fill="#064e3b" stroke="#047857" stroke-width="0.8" rx="2" />
    
    <!-- M3 Holes -->
    <g id="m3Layer">
      <circle cx="6" cy="6" r="2.5" fill="none" stroke="#d97706" stroke-width="0.8" />
      <circle cx="6" cy="6" r="1.6" fill="#020617" />
      <circle cx="194" cy="6" r="2.5" fill="none" stroke="#d97706" stroke-width="0.8" />
      <circle cx="194" cy="6" r="1.6" fill="#020617" />
      <circle cx="6" cy="194" r="2.5" fill="none" stroke="#d97706" stroke-width="0.8" />
      <circle cx="6" cy="194" r="1.6" fill="#020617" />
      <circle cx="194" cy="194" r="2.5" fill="none" stroke="#d97706" stroke-width="0.8" />
      <circle cx="194" cy="194" r="1.6" fill="#020617" />
    </g>
    
    <!-- Solder Pin Headers (Visible on Both Views) -->
    <g id="solderLayer">
      <!-- IN Header -->
      <rect x="25.5" y="190.5" width="9.0" height="3.0" fill="#334155" stroke="#94a3b8" stroke-width="0.3" rx="0.4" />
      <circle cx="27.46" cy="192" r="1.1" fill="#fbbf24" stroke="#d97706" stroke-width="0.2" />
      <circle cx="30.00" cy="192" r="1.1" fill="#fbbf24" stroke="#d97706" stroke-width="0.2" />
      <circle cx="32.54" cy="192" r="1.1" fill="#fbbf24" stroke="#d97706" stroke-width="0.2" />
      <text x="30" y="189.5" font-size="1.4" fill="#f8fafc" text-anchor="middle" font-weight="bold">[IN: 5V DAT GND]</text>
      <!-- Strain Relief Holes -->
      <circle cx="26" cy="186.5" r="1.1" fill="#020617" stroke="#94a3b8" stroke-width="0.4" />
      <circle cx="34" cy="186.5" r="1.1" fill="#020617" stroke="#94a3b8" stroke-width="0.4" />
      
      <!-- OUT Header -->
      <rect x="165.5" y="190.5" width="9.0" height="3.0" fill="#334155" stroke="#94a3b8" stroke-width="0.3" rx="0.4" />
      <circle cx="167.46" cy="192" r="1.1" fill="#fbbf24" stroke="#d97706" stroke-width="0.2" />
      <circle cx="170.00" cy="192" r="1.1" fill="#fbbf24" stroke="#d97706" stroke-width="0.2" />
      <circle cx="172.54" cy="192" r="1.1" fill="#fbbf24" stroke="#d97706" stroke-width="0.2" />
      <text x="170" y="189.5" font-size="1.4" fill="#f8fafc" text-anchor="middle" font-weight="bold">[OUT: 5V DAT GND]</text>
      <!-- Strain Relief Holes -->
      <circle cx="166" cy="186.5" r="1.1" fill="#020617" stroke="#94a3b8" stroke-width="0.4" />
      <circle cx="174" cy="186.5" r="1.1" fill="#020617" stroke="#94a3b8" stroke-width="0.4" />
    </g>
    
    <!-- Front Layer: LEDs and Caps -->
    <g id="frontLayer">
"""

for d in led_positions:
    x = d["x"]
    y = d["y"]
    i = d["id"]
    html_content += f"""      <rect x="{x-1.0:.2f}" y="{y-1.0:.2f}" width="2.0" height="2.0" fill="#1e293b" stroke="#e2e8f0" stroke-width="0.2" rx="0.3" />
      <circle cx="{x:.2f}" cy="{y:.2f}" r="0.6" fill="#38bdf8" />
      <rect x="{x+1.5:.2f}" y="{y-0.5:.2f}" width="1.0" height="1.0" fill="#94a3b8" />
      <text x="{x:.2f}" y="{y-1.8:.2f}" font-size="0.9" fill="#f8fafc" text-anchor="middle" font-family="monospace">{i}</text>
"""

html_content += f"""    </g>

    <!-- Rear Layer: Solder Pins and Wire Strain Relief Guidance -->
    <g id="rearLayer" style="display: none;">
      <!-- Solder wire path demonstration -->
      <path d="M 26 186.5 Q 28 183 30 192" stroke="#ef4444" stroke-width="0.8" fill="none" stroke-dasharray="1.5,1.5" />
      <text x="30" y="182" font-size="1.3" fill="#fca5a5" text-anchor="middle">S-Curve Wire Strain Relief</text>
      
      <path d="M 30 192 L 30 170 L 100 170 L 170 170 L 170 192" stroke="#10b981" stroke-width="1.2" fill="none" stroke-dasharray="2,2" />
      <text x="100" y="167" font-size="1.6" fill="#34d399" text-anchor="middle">100% Internal Copper Traces (Zero Inter-Tile Jumpers!)</text>
      <text x="100" y="174" font-size="1.2" fill="#94a3b8" text-anchor="middle">Zero SMT parts on back • Clean bare fiberglass plane</text>
    </g>
  </svg>
</div>

<div class="stat-box">
  <div class="stat"><div class="stat-val">Single-Sided</div><div class="stat-lbl">Economic PCBA ($15 Setup)</div></div>
  <div class="stat"><div class="stat-val">144</div><div class="stat-lbl">WS2812B-2020 LEDs</div></div>
  <div class="stat"><div class="stat-val">2.54 mm</div><div class="stat-lbl">Standard Solder Pitch</div></div>
  <div class="stat"><div class="stat-val">S-Curve</div><div class="stat-lbl">Strain Relief Built-In</div></div>
</div>

<script>
function setView(view) {{
  const front = document.getElementById('frontLayer');
  const rear = document.getElementById('rearLayer');
  const btnF = document.getElementById('btnFront');
  const btnR = document.getElementById('btnRear');
  if (view === 'front') {{
    front.style.display = 'block';
    rear.style.display = 'none';
    btnF.classList.add('active');
    btnR.classList.remove('active');
  }} else {{
    front.style.display = 'none';
    rear.style.display = 'block';
    btnF.classList.remove('active');
    btnR.classList.add('active');
  }}
}}
</script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated Interactive Inspector: {html_path}")
