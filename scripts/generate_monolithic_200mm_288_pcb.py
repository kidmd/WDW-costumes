import os
import json
import zipfile
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB_DIR = os.path.join(BASE_DIR, "pcb")
MONO_288_DIR = os.path.join(PCB_DIR, "monolithic_200mm_288")
os.makedirs(MONO_288_DIR, exist_ok=True)

# -------------------------------------------------------------
# Configuration: Monolithic 200mm x 200mm Double-Density Matrix
# Total LEDs: Exactly 288 WS2812B-2020 LEDs (144 x 2)
# Grid: 18 Rows x 16 Columns in an alternating staggered lattice
# -------------------------------------------------------------
BOARD_SIZE_MM = 200.0
GRID_ROWS = 18
GRID_COLS = 16
NUM_LEDS = GRID_ROWS * GRID_COLS  # 288 LEDs

PITCH_X = 11.60
PITCH_Y = 10.60
ROW_OFFSET = PITCH_X / 2.0  # 5.80 mm

MARGIN_T = 9.90
MARGIN_L1 = 10.10

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

# Connectors on BOTTOM LAYER (B.Cu)
jst_ports = [
    {"ref": "J_IN",  "type": "IN",  "x": 35.0,  "y": 194.0, "rot": 0, "label": "IN (ESP32)"},
    {"ref": "J_OUT", "type": "OUT", "x": 165.0, "y": 194.0, "rot": 0, "label": "OUT (Daisy)"},
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
    {"ref": "S1", "x": 50.0,  "y": 4.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S2", "x": 100.0, "y": 4.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S3", "x": 150.0, "y": 4.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    # Bottom edge
    {"ref": "S4", "x": 75.0,  "y": 195.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S5", "x": 100.0, "y": 195.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S6", "x": 125.0, "y": 195.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    # Left edge
    {"ref": "S7", "x": 4.5, "y": 50.0,  "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S8", "x": 4.5, "y": 100.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S9", "x": 4.5, "y": 150.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    # Right edge
    {"ref": "S10", "x": 195.5, "y": 50.0,  "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S11", "x": 195.5, "y": 100.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S12", "x": 195.5, "y": 150.0, "drill": 2.0, "pad": 3.5, "label": "SEW"},
]

# -------------------------------------------------------------
# 1. Generate JLCPCB BOM File
# -------------------------------------------------------------
bom_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288_bom.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write("Comment,Designator,Footprint,LCSC Part #\n")
    led_refs = " ".join([d["ref"] for d in led_positions])
    cap_refs = " ".join([d["cap_ref"] for d in led_positions])
    jst_refs = " ".join([j["ref"] for j in jst_ports])
    f.write(f'WS2812B-2020-V6,"{led_refs}",LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm,C52917434\n')
    f.write(f'100nF (0.1uF) 50V 0402,"{cap_refs}",Capacitor_SMD:C_0402_1005Metric,C1525\n')
    f.write(f'JST-PH-3P-Horizontal-SMD,"{jst_refs}",Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal,C3029441\n')

print(f"Generated BOM: {bom_path}")

# -------------------------------------------------------------
# 2. Generate JLCPCB CPL (Centroid) File
# -------------------------------------------------------------
cpl_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288_cpl.csv")
with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("Designator,Val,Package,Mid X,Mid Y,Rotation,Layer\n")
    for d in led_positions:
        f.write(f'{d["ref"]},WS2812B-2020,LED_WS2812B-2020,{d["x"]:.2f},{d["y"]:.2f},0.0,Top\n')
        cx = round(d["x"] + 1.8, 2)
        cy = d["y"]
        f.write(f'{d["cap_ref"]},100nF,C_0402,{cx:.2f},{cy:.2f},90.0,Top\n')
    for j in jst_ports:
        f.write(f'{j["ref"]},JST_PH_3P_SMT,JST_PH_Horizontal,{j["x"]:.2f},{j["y"]:.2f},{float(j["rot"]):.1f},Bottom\n')

print(f"Generated CPL: {cpl_path}")

# -------------------------------------------------------------
# 3. Generate KiCad PCB (.kicad_pcb) File
# -------------------------------------------------------------
kicad_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.kicad_pcb")
num_nets = NUM_LEDS + 4

kicad_content = f"""(kicad_pcb (version 20211014) (generator "Antigravity Imagineering Engine")
  (general
    (thickness 1.6)
    (drawings 0)
    (tracks 0)
    (zones 0)
    (modules {NUM_LEDS * 2 + len(jst_ports) + len(m3_holes) + len(sew_holes)})
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
    (last_trace_width 0.25)
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

# Connectors on B.Cu
for j in jst_ports:
    jx = j["x"]
    jy = j["y"]
    jref = j["ref"]
    jtype = j["type"]
    data_net = 3 if (jtype == "IN") else (NUM_LEDS + 3)
    kicad_content += f"""  (module "Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal" (layer B.Cu) (tedit 5D5A6E4F)
    (at {jx} {jy})
    (descr "JST PH 3-pin {jtype} connector on Bottom")
    (path "/{jref}")
    (fp_text reference "{jref}" (at 0 -3.6) (layer B.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (fp_text user "[{jtype}]" (at 0 3.6) (layer B.SilkS)
      (effects (font (size 0.65 0.65) (thickness 0.12)))
    )
    (pad 1 smd rect (at -2.0 0.0) (size 1.0 1.6) (layers B.Cu B.Paste B.Mask) (net 1))
    (pad 2 smd rect (at 0.0 0.0) (size 1.0 1.6) (layers B.Cu B.Paste B.Mask) (net {data_net}))
    (pad 3 smd rect (at 2.0 0.0) (size 1.0 1.6) (layers B.Cu B.Paste B.Mask) (net 2))
    (pad MP smd rect (at -3.4 -1.5) (size 1.5 1.8) (layers B.Cu B.Paste B.Mask) (net 2))
    (pad MP smd rect (at 3.4 -1.5) (size 1.5 1.8) (layers B.Cu B.Paste B.Mask) (net 2))
  )
"""
    for p_idx, (p_name, p_net, p_xoff) in enumerate([("5V", 1, -2.54), ("DAT", data_net, 0.0), ("GND", 2, 2.54)]):
        kicad_content += f"""  (module "TestPoint:TestPoint_Pad_D1.5mm" (layer B.Cu) (tedit 5D5A6E4F)
    (at {round(jx + p_xoff, 2)} {round(jy - 5.0, 2)})
    (descr "Direct solder eyelet {p_name}")
    (path "/{jref}_{p_name}")
    (pad 1 thru_hole circle (at 0 0) (size 2.0 2.0) (drill 1.2) (layers *.Cu *.Mask) (net {p_net}))
  )
"""

# Place 288 WS2812B-2020 LEDs on F.Cu
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
    (fp_text user "{i}" (at 0 -2.0) (layer F.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
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
    cx = round(x + 1.8, 2)
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

# Power traces & Ground vias
for d in led_positions:
    x = d["x"]
    y = d["y"]
    p_5v = (round(x - 0.85, 2), round(y - 0.65, 2))
    p_gnd = (round(x + 0.85, 2), round(y + 0.65, 2))
    c_5v = (round(x + 1.8, 2), round(y - 0.48, 2))
    c_gnd = (round(x + 1.8, 2), round(y + 0.48, 2))
    gnd_via = (round(x + 1.8, 2), round(y + 1.1, 2))
    
    kicad_content += f'  (segment (start {p_5v[0]} {p_5v[1]}) (end {c_5v[0]} {c_5v[1]}) (width 0.35) (layer F.Cu) (net 1))\n'
    kicad_content += f'  (segment (start {p_gnd[0]} {p_gnd[1]}) (end {c_gnd[0]} {c_gnd[1]}) (width 0.35) (layer F.Cu) (net 2))\n'
    kicad_content += f'  (segment (start {c_gnd[0]} {c_gnd[1]}) (end {gnd_via[0]} {gnd_via[1]}) (width 0.35) (layer F.Cu) (net 2))\n'
    kicad_content += f'  (via (at {gnd_via[0]} {gnd_via[1]}) (size 0.7) (drill 0.35) (layers F.Cu B.Cu) (net 2))\n'

# Daisy chain data traces 1..288
for i in range(NUM_LEDS - 1):
    d1 = led_positions[i]
    d2 = led_positions[i + 1]
    net_id = 3 + d1["id"]
    p1_dout = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
    p2_din = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
    kicad_content += f'  (segment (start {p1_dout[0]} {p1_dout[1]}) (end {p2_din[0]} {p2_din[1]}) (width 0.22) (layer F.Cu) (net {net_id}))\n'
    
    c1_5v = (round(d1["x"] + 1.8, 2), round(d1["y"] - 0.48, 2))
    c2_5v = (round(d2["x"] + 1.8, 2), round(d2["y"] - 0.48, 2))
    if d1["row"] == d2["row"]:
        kicad_content += f'  (segment (start {c1_5v[0]} {c1_5v[1]}) (end {c2_5v[0]} {c2_5v[1]}) (width 0.6) (layer F.Cu) (net 1))\n'

# Connect J_IN to LED 1
led1 = led_positions[0]
p1_din = (round(led1["x"] + 0.85, 2), round(led1["y"] - 0.65, 2))
kicad_content += f'  (via (at 35.0 190.0) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net 3))\n'
kicad_content += f'  (segment (start 35.0 194.0) (end 35.0 190.0) (width 0.3) (layer B.Cu) (net 3))\n'
kicad_content += f'  (segment (start 35.0 190.0) (end {p1_din[0]} {p1_din[1]}) (width 0.22) (layer F.Cu) (net 3))\n'

# Connect LED 288 to J_OUT
led_last = led_positions[-1]
plast_dout = (round(led_last["x"] - 0.85, 2), round(led_last["y"] + 0.65, 2))
kicad_content += f'  (via (at 165.0 190.0) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net {NUM_LEDS+3}))\n'
kicad_content += f'  (segment (start {plast_dout[0]} {plast_dout[1]}) (end 165.0 190.0) (width 0.22) (layer F.Cu) (net {NUM_LEDS+3}))\n'
kicad_content += f'  (segment (start 165.0 190.0) (end 165.0 194.0) (width 0.3) (layer B.Cu) (net {NUM_LEDS+3}))\n'

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

pro_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.pro")
with open(pro_path, "w", encoding="utf-8") as f:
    f.write("[general]\nversion=1\n")

kicad_pro_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.kicad_pro")
with open(kicad_pro_path, "w", encoding="utf-8") as f:
    f.write('{"meta":{"version":1},"sheets":[]}')

# SMT Assembly Bundle ZIP
zip_smt_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288_smt.zip")
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
gko_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GKO")
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
drl_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.DRL")
with open(drl_path, "w", encoding="utf-8") as f:
    f.write("""M48
METRIC
T1C3.200
T2C2.000
T3C0.350
T4C1.200
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
        f.write(f"X{round(d['x'] + 1.8, 3):.3f}Y{round(d['y'] + 1.1, 3):.3f}\n")
    f.write("X35.000Y190.000\nX165.000Y190.000\n")
    f.write("T4\n")
    f.write("X32.460Y189.000\nX35.000Y189.000\nX37.540Y189.000\n")
    f.write("X162.460Y189.000\nX165.000Y189.000\nX167.540Y189.000\n")
    f.write("M30\n")

# Top Copper (.GTL)
gtl_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GTL")
with open(gtl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Copper (F.Cu) - Monolithic 288 LED Matrix*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.220*%
%ADD11C,0.700*%
%ADD12C,0.350*%
%ADD13R,0.600X0.500*%
%ADD14R,0.560X0.620*%
%ADD18C,0.700*%
%ADD19C,5.000*%
%ADD20C,3.500*%
""")
    f.write("D19*\n")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D20*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
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
        cx = round(d["x"] + 1.8, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("D18*\n")
    for d in led_positions:
        f.write(f"{coord_gbr(round(d['x'] + 1.8, 2), round(d['y'] + 1.1, 2))}D03*\n")
    f.write("D10*\n")
    for i in range(NUM_LEDS - 1):
        d1 = led_positions[i]
        d2 = led_positions[i + 1]
        p1 = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
        p2 = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
        f.write(f"{coord_gbr(p1[0], p1[1])}D02*\n")
        f.write(f"{coord_gbr(p2[0], p2[1])}D01*\n")
    f.write("M02*\n")

# Bottom Copper (.GBL)
gbl_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GBL")
with open(gbl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Copper (B.Cu)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.800*%
%ADD11C,5.000*%
%ADD12C,3.500*%
%ADD13R,196.000X196.000*%
%ADD15R,1.000X1.600*%
%ADD16C,2.000*%
D13*
X100000000Y100000000D03*
D11*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D12*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    f.write("D15*\n")
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        f.write(f"{coord_gbr(jx - 2.0, jy)}D03*\n")
        f.write(f"{coord_gbr(jx, jy)}D03*\n")
        f.write(f"{coord_gbr(jx + 2.0, jy)}D03*\n")
    f.write("D16*\n")
    f.write("X32460000Y189000000D03*\nX35000000Y189000000D03*\nX37540000Y189000000D03*\n")
    f.write("X162460000Y189000000D03*\nX165000000Y189000000D03*\nX167540000Y189000000D03*\n")
    f.write("M02*\n")

# Top Mask (.GTS)
gts_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GTS")
with open(gts_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Solder Mask*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10R,0.700X0.600*%
%ADD11R,0.660X0.720*%
%ADD12C,5.100*%
%ADD13C,3.600*%
D12*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D13*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
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
        cx = round(d["x"] + 1.8, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("M02*\n")

# Bottom Mask (.GBS)
gbs_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GBS")
with open(gbs_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Solder Mask*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,5.100*%
%ADD11C,3.600*%
%ADD12R,1.100X1.700*%
%ADD13C,2.100*%
D10*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D11*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    f.write("D12*\n")
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        f.write(f"{coord_gbr(jx - 2.0, jy)}D03*\n")
        f.write(f"{coord_gbr(jx, jy)}D03*\n")
        f.write(f"{coord_gbr(jx + 2.0, jy)}D03*\n")
    f.write("D13*\n")
    f.write("X32460000Y189000000D03*\nX35000000Y189000000D03*\nX37540000Y189000000D03*\n")
    f.write("X162460000Y189000000D03*\nX165000000Y189000000D03*\nX167540000Y189000000D03*\n")
    f.write("M02*\n")

# Top Paste (.GTP)
gtp_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GTP")
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
        cx = round(d["x"] + 1.8, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("M02*\n")

# Bottom Paste (.GBP)
gbp_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GBP")
with open(gbp_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Paste*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10R,1.000X1.600*%
D10*
""")
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        f.write(f"{coord_gbr(jx - 2.0, jy)}D03*\n")
        f.write(f"{coord_gbr(jx, jy)}D03*\n")
        f.write(f"{coord_gbr(jx + 2.0, jy)}D03*\n")
    f.write("M02*\n")

# Top Silkscreen (.GTO)
gto_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GTO")
with open(gto_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Silkscreen*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.120*%
D10*
""")
    f.write(f"X{int(20*1000000)}Y{int(4*1000000)}D02*\nX{int(180*1000000)}Y{int(4*1000000)}D01*\n")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D02*\n{coord_gbr(x+1.0, y-1.0)}D01*\n")
        f.write(f"{coord_gbr(x+1.0, y+1.0)}D01*\n{coord_gbr(x-1.0, y+1.0)}D01*\n")
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D01*\n")
    f.write("M02*\n")

# Bottom Silkscreen (.GBO)
gbo_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288.GBO")
with open(gbo_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Silkscreen*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.120*%
D10*
""")
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        f.write(f"{coord_gbr(jx - 4.0, jy - 3.0)}D02*\n{coord_gbr(jx + 4.0, jy - 3.0)}D01*\n")
        f.write(f"{coord_gbr(jx + 4.0, jy + 3.0)}D01*\n{coord_gbr(jx - 4.0, jy + 3.0)}D01*\n")
        f.write(f"{coord_gbr(jx - 4.0, jy - 3.0)}D01*\n")
    f.write("M02*\n")

# Gerber ZIP
zip_gerbers_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288_gerbers.zip")
with zipfile.ZipFile(zip_gerbers_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in [gko_path, drl_path, gtl_path, gbl_path, gts_path, gbs_path, gto_path, gbo_path, gtp_path, gbp_path]:
        z.write(p, os.path.basename(p))

print(f"Generated Gerber ZIP: {zip_gerbers_path}")

# -------------------------------------------------------------
# 5. Interactive HTML Preview
# -------------------------------------------------------------
html_path = os.path.join(MONO_288_DIR, "monolithic_200mm_288_preview.html")
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Monolithic 200mm x 200mm (288 LEDs) Inspector</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; text-align: center; }}
h1 {{ color: #a855f7; margin-bottom: 5px; }}
p {{ color: #94a3b8; margin-top: 0; }}
.btn {{ background: #9333ea; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin: 4px; }}
.btn:hover {{ background: #7e22ce; }}
.btn.active {{ background: #10b981; }}
#viewport {{ width: 640px; height: 640px; margin: 20px auto; background: #020617; border: 2px solid #334155; border-radius: 8px; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
svg {{ width: 100%; height: 100%; }}
.stat-box {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
.stat {{ background: #1e293b; padding: 10px 18px; border-radius: 8px; border: 1px solid #334155; }}
.stat-val {{ font-size: 1.4em; font-weight: bold; color: #c084fc; }}
.stat-lbl {{ font-size: 0.8em; color: #94a3b8; }}
</style>
</head>
<body>
<h1>Monolithic 200mm x 200mm (288 LEDs) Inspector</h1>
<p>Disney Imagineering MSEP Wearable Display • 18x16 Double-Density Offset Lattice (2x LEDs)</p>
<div>
  <button id="btnFront" class="btn active" onclick="setView('front')">Front View (Flush LEDs)</button>
  <button id="btnRear" class="btn" onclick="setView('rear')">Rear View (JST Connectors)</button>
</div>

<div id="viewport">
  <svg viewBox="0 0 200 200" id="pcbSvg">
    <rect x="0" y="0" width="200" height="200" fill="#2e1065" stroke="#7e22ce" stroke-width="0.8" rx="2" />
    
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
    
    <g id="frontLayer">
"""

for d in led_positions:
    x = d["x"]
    y = d["y"]
    i = d["id"]
    html_content += f"""      <rect x="{x-1.0:.2f}" y="{y-1.0:.2f}" width="2.0" height="2.0" fill="#1e1b4b" stroke="#c084fc" stroke-width="0.15" rx="0.3" />
      <circle cx="{x:.2f}" cy="{y:.2f}" r="0.5" fill="#f43f5e" />
      <rect x="{x+1.4:.2f}" y="{y-0.4:.2f}" width="0.8" height="0.8" fill="#94a3b8" />
"""

html_content += f"""    </g>

    <g id="rearLayer" style="display: none;">
      <rect x="31" y="191" width="8" height="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="0.4" rx="0.5" />
      <text x="35" y="195" font-size="1.4" fill="#0f172a" text-anchor="middle" font-weight="bold">[IN]</text>
      <rect x="161" y="191" width="8" height="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="0.4" rx="0.5" />
      <text x="165" y="195" font-size="1.4" fill="#0f172a" text-anchor="middle" font-weight="bold">[OUT]</text>
      <path d="M 35 191 L 35 175 L 100 175 L 165 175 L 165 191" stroke="#a855f7" stroke-width="1.2" fill="none" stroke-dasharray="2,2" />
      <text x="100" y="172" font-size="1.6" fill="#e9d5ff" text-anchor="middle">Internal 288-LED High-Density Backbone (Zero Jumper Wires!)</text>
    </g>
  </svg>
</div>

<div class="stat-box">
  <div class="stat"><div class="stat-val">200 x 200 mm</div><div class="stat-lbl">Dimensions</div></div>
  <div class="stat"><div class="stat-val">288</div><div class="stat-lbl">WS2812B-2020 LEDs</div></div>
  <div class="stat"><div class="stat-val">11.6 x 10.6 mm</div><div class="stat-lbl">High-Density Offset Pitch</div></div>
  <div class="stat"><div class="stat-val">ZERO</div><div class="stat-lbl">Inter-Tile Wires</div></div>
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
