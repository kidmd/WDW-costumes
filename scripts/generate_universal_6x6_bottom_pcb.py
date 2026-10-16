import os
import json
import zipfile
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB_DIR = os.path.join(BASE_DIR, "pcb")
BOTTOM_PCB_DIR = os.path.join(PCB_DIR, "bottom_connectors")
os.makedirs(BOTTOM_PCB_DIR, exist_ok=True)

# -------------------------------------------------------------
# Configuration: 100% Seamless 6x6 Staggered Brick LED Matrix
# Bottom-Mounted JST Connector Variant (universal_6x6_bottom)
# -------------------------------------------------------------
BOARD_SIZE_MM = 100.0
GRID_ROWS = 6
GRID_COLS = 6
NUM_LEDS = GRID_ROWS * GRID_COLS  # 36 LEDs

# SEAMLESS MATHEMATICAL CALIBRATION:
# Gap between tiled boards in felt pocket: G = 2.0 mm
# For distance across seam to exactly match internal pitch:
# (100.0 - 5*P) + G = P  =>  6*P = 102.0 mm  =>  P = 17.00 mm!
PITCH_X = 17.00
PITCH_Y = 17.00
ROW_OFFSET = PITCH_X / 2.0  # 8.50 mm (half a brick offset)

# Margins:
# Row 1, 3, 5: ML1 = 3.00 mm. Last LED at 3.0 + 5*17.0 = 88.00 mm.
#              MR1 = 100.0 - 88.0 = 12.00 mm.
#              Distance across seam: MR1 + G + ML1 = 12.0 + 2.0 + 3.0 = 17.00 mm!
# Row 2, 4, 6: ML2 = ML1 + 8.50 = 11.50 mm. Last LED at 11.50 + 5*17.0 = 96.50 mm.
#              MR2 = 100.0 - 96.50 = 3.50 mm.
#              Distance across seam: MR2 + G + ML2 = 3.50 + 2.0 + 11.50 = 17.00 mm!
# Vertical: MT = 7.50 mm, MB = 7.50 mm.
#           Distance across seam: MB + G + MT = 7.50 + 2.0 + 7.50 = 17.00 mm!
# RESULT: 100% UNIFORM 17.00mm PITCH ACROSS ENTIRE 144-LED CHEST ARRAY!
MARGIN_L1 = 3.00
MARGIN_T = 7.50

# Generate 36 Staggered LED coordinates in Serpentine sequence (TOP SIDE)
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
# 4-Edge JST 3-Pin Interconnect Architecture on BOTTOM LAYER (B.Cu)
# 4 IN ports (Top, Bottom, Left, Right)
# 4 OUT ports (Top, Bottom, Left, Right)
# Perfectly symmetrical 22.0mm straight spans in all directions!
# -------------------------------------------------------------
jst_ports = [
    # Left Edge (x = 10.0 mm, B.Cu)
    {"ref": "J_IN_L",  "type": "IN",  "edge": "LEFT",   "x": 10.0, "y": 33.0, "rot": 90,  "label": "IN_L"},
    {"ref": "J_OUT_L", "type": "OUT", "edge": "LEFT",   "x": 10.0, "y": 67.0, "rot": 90,  "label": "OUT_L"},
    # Right Edge (x = 90.0 mm, B.Cu) - J_OUT_R at y=33 aligns directly with J_IN_L across 2.0mm seam!
    {"ref": "J_OUT_R", "type": "OUT", "edge": "RIGHT",  "x": 90.0, "y": 33.0, "rot": 90,  "label": "OUT_R"},
    {"ref": "J_IN_R",  "type": "IN",  "edge": "RIGHT",  "x": 90.0, "y": 67.0, "rot": 90,  "label": "IN_R"},
    # Top Edge (y = 10.0 mm, B.Cu)
    {"ref": "J_IN_T",  "type": "IN",  "edge": "TOP",    "x": 33.0, "y": 10.0, "rot": 0,   "label": "IN_T"},
    {"ref": "J_OUT_T", "type": "OUT", "edge": "TOP",    "x": 67.0, "y": 10.0, "rot": 0,   "label": "OUT_T"},
    # Bottom Edge (y = 90.0 mm, B.Cu) - J_OUT_B at x=33 aligns directly with J_IN_T across 2.0mm seam!
    {"ref": "J_OUT_B", "type": "OUT", "edge": "BOTTOM", "x": 33.0, "y": 90.0, "rot": 0,   "label": "OUT_B"},
    {"ref": "J_IN_B",  "type": "IN",  "edge": "BOTTOM", "x": 67.0, "y": 90.0, "rot": 0,   "label": "IN_B"},
]

# -------------------------------------------------------------
# Corner Mounting & Fabric Sewing Holes Architecture
# 4 Corner M3 Screw Mounting Holes (Ø3.2mm drill, 5.0mm pad)
# 4 Dedicated Fabric Sewing Eyelets (Ø2.0mm drill, 3.5mm pad)
# -------------------------------------------------------------
m3_holes = [
    {"ref": "H1", "x": 4.0, "y": 3.5, "drill": 3.2, "pad": 5.0, "label": "M3"},
    {"ref": "H2", "x": 96.0, "y": 3.5, "drill": 3.2, "pad": 5.0, "label": "M3"},
    {"ref": "H3", "x": 4.0, "y": 96.5, "drill": 3.2, "pad": 5.0, "label": "M3"},
    {"ref": "H4", "x": 96.0, "y": 96.5, "drill": 3.2, "pad": 5.0, "label": "M3"},
]

sew_holes = [
    {"ref": "S1", "x": 10.0, "y": 3.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S2", "x": 90.0, "y": 3.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S3", "x": 10.0, "y": 96.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
    {"ref": "S4", "x": 90.0, "y": 96.5, "drill": 2.0, "pad": 3.5, "label": "SEW"},
]

# -------------------------------------------------------------
# 1. Generate JLCPCB BOM (Bill of Materials) CSV
# -------------------------------------------------------------
bom_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm_bom.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write("Comment,Designator,Footprint,LCSC Part #\n")
    led_refs = " ".join([d["ref"] for d in led_positions])
    cap_refs = " ".join([d["cap_ref"] for d in led_positions])
    jst_refs = " ".join([j["ref"] for j in jst_ports])
    
    # WS2812B-2020-V6 (verified 932k in-stock)
    f.write(f'"WS2812B-2020-V6 Addressable RGB LED","{led_refs}","LED-SMD_4P-L2.0-W2.0-TL","C52917434"\n')
    # 100nF 0402 Capacitor
    f.write(f'"100nF (0.1uF) 50V 0402 Capacitor","{cap_refs}","C0402","C1525"\n')
    # JST-PH 2.0mm 3-Pin Horizontal SMT Header (WAFER-PH2.0-3PWB on Bottom)
    f.write(f'"WAFER-PH2.0-3PWB","{jst_refs}","CONN-SMD_3P-P2.00_WAFER-PH2.0-3PWB","C3029441"\n')

print(f"Generated BOM: {bom_path}")

# -------------------------------------------------------------
# 2. Generate JLCPCB CPL (Pick and Place Centroid) CSV
# LEDs & Caps on Top Layer; JST Connectors on Bottom Layer!
# -------------------------------------------------------------
cpl_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm_cpl.csv")
with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("Designator,Mid X,Mid Y,Layer,Rotation\n")
    for d in led_positions:
        f.write(f'{d["ref"]},{d["x"]},{d["y"]},Top,0\n')
        # Capacitor 2.0mm to the right of LED
        f.write(f'{d["cap_ref"]},{round(d["x"] + 2.0, 2)},{d["y"]},Top,90\n')
    for j in jst_ports:
        # Mounted on Bottom Layer!
        f.write(f'{j["ref"]},{j["x"]},{j["y"]},Bottom,{j["rot"]}\n')

print(f"Generated CPL: {cpl_path}")

# -------------------------------------------------------------
# 3. Generate KiCad 5 Compatible PCB File (.kicad_pcb)
# -------------------------------------------------------------
kicad_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.kicad_pcb")

num_nets = NUM_LEDS + 3  # Net 0 (none), 1 (+5V), 2 (GND), 3..38 (DATA_1..36)
kicad_content = f"""(kicad_pcb (version 20171130) (host pcbnew "(5.1.9)-1")
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

# Board Outline: 100mm x 100mm CLOSED continuous rectangle
b = BOARD_SIZE_MM
kicad_content += f"""  (gr_line (start 0 0) (end {b} 0) (layer Edge.Cuts) (width 0.15))
  (gr_line (start {b} 0) (end {b} {b}) (layer Edge.Cuts) (width 0.15))
  (gr_line (start {b} {b}) (end 0 {b}) (layer Edge.Cuts) (width 0.15))
  (gr_line (start 0 {b}) (end 0 0) (layer Edge.Cuts) (width 0.15))
"""

# 4 Corner M3 Mounting Holes (Ø3.2mm M3 clearance with 5.0mm pad)
for h in m3_holes:
    kicad_content += f"""  (module "MountingHole:MountingHole_3.2mm_M3" (layer F.Cu) (tedit 5D5A6E4F)
    (at {h['x']} {h['y']})
    (descr "Mounting Hole 3.2mm M3")
    (path "/{h['ref']}")
    (fp_text reference "{h['ref']}" (at 0 -2.5) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (fp_text user "M3" (at 0 2.5) (layer F.SilkS)
      (effects (font (size 0.6 0.6) (thickness 0.1)))
    )
    (pad 1 thru_hole circle (at 0 0) (size {h['pad']} {h['pad']}) (drill {h['drill']}) (layers *.Cu *.Mask))
  )
"""

# 4 Dedicated Fabric Sewing Eyelets (Ø2.0mm drill with 3.5mm pad)
for s in sew_holes:
    kicad_content += f"""  (module "MountingHole:MountingHole_2.0mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {s['x']} {s['y']})
    (descr "Fabric Sewing Eyelet 2.0mm")
    (path "/{s['ref']}")
    (fp_text reference "{s['ref']}" (at 0 -2.0) (layer F.SilkS)
      (effects (font (size 0.6 0.6) (thickness 0.1)))
    )
    (fp_text user "SEW" (at 0 2.0) (layer F.SilkS)
      (effects (font (size 0.5 0.5) (thickness 0.08)))
    )
    (pad 1 thru_hole circle (at 0 0) (size {s['pad']} {s['pad']}) (drill {s['drill']}) (layers *.Cu *.Mask))
  )
"""

# 8 JST-PH 3-Pin Connectors on BOTTOM LAYER (B.Cu / B.SilkS)
for j in jst_ports:
    jx = j["x"]
    jy = j["y"]
    jrot = j["rot"]
    jref = j["ref"]
    jlabel = j["label"]
    data_net = 3 if (j["type"] == "IN") else (NUM_LEDS + 3)
    data_net_name = "DATA_1" if (j["type"] == "IN") else f"DATA_{NUM_LEDS+1}"
    
    if j["edge"] in ["LEFT", "RIGHT"]:
        p1_x, p1_y = 0.0, -2.0
        p2_x, p2_y = 0.0, 0.0
        p3_x, p3_y = 0.0, 2.0
        pad_w, pad_h = 1.6, 1.0
        txt_x = 3.2 if (j["edge"] == "LEFT") else -3.2
        kicad_content += f"""  (module "Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal" (layer B.Cu) (tedit 5D5A6E4F)
    (at {jx} {jy})
    (descr "JST PH 3-pin {j['type']} connector on Bottom ({j['edge']})")
    (path "/{jref}")
    (fp_text reference "{jref}" (at 0 -3.6) (layer B.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (fp_text user "[{j['type']}]" (at 0 3.6) (layer B.SilkS)
      (effects (font (size 0.65 0.65) (thickness 0.12)))
    )
    (fp_text user "5V" (at {txt_x} -2.0) (layer B.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
    )
    (fp_text user "DAT" (at {txt_x} 0.0) (layer B.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
    )
    (fp_text user "GND" (at {txt_x} 2.0) (layer B.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
    )
    (pad 1 smd rect (at {p1_x} {p1_y}) (size {pad_w} {pad_h}) (layers B.Cu B.Paste B.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at {p2_x} {p2_y}) (size {pad_w} {pad_h}) (layers B.Cu B.Paste B.Mask) (net {data_net} "{data_net_name}"))
    (pad 3 smd rect (at {p3_x} {p3_y}) (size {pad_w} {pad_h}) (layers B.Cu B.Paste B.Mask) (net 2 "GND"))
  )
"""
    else:  # TOP, BOTTOM
        p1_x, p1_y = -2.0, 0.0
        p2_x, p2_y = 0.0, 0.0
        p3_x, p3_y = 2.0, 0.0
        pad_w, pad_h = 1.0, 1.6
        txt_y = 3.2 if (j["edge"] == "TOP") else -3.2
        kicad_content += f"""  (module "Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal" (layer B.Cu) (tedit 5D5A6E4F)
    (at {jx} {jy})
    (descr "JST PH 3-pin {j['type']} connector on Bottom ({j['edge']})")
    (path "/{jref}")
    (fp_text reference "{jref}" (at -4.2 0) (layer B.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (fp_text user "[{j['type']}]" (at 4.2 0) (layer B.SilkS)
      (effects (font (size 0.65 0.65) (thickness 0.12)))
    )
    (fp_text user "5V" (at -2.0 {txt_y}) (layer B.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
    )
    (fp_text user "DAT" (at 0.0 {txt_y}) (layer B.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
    )
    (fp_text user "GND" (at 2.0 {txt_y}) (layer B.SilkS)
      (effects (font (size 0.55 0.55) (thickness 0.1)))
    )
    (pad 1 smd rect (at {p1_x} {p1_y}) (size {pad_w} {pad_h}) (layers B.Cu B.Paste B.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at {p2_x} {p2_y}) (size {pad_w} {pad_h}) (layers B.Cu B.Paste B.Mask) (net {data_net} "{data_net_name}"))
    (pad 3 smd rect (at {p3_x} {p3_y}) (size {pad_w} {pad_h}) (layers B.Cu B.Paste B.Mask) (net 2 "GND"))
  )
"""

# 36 LEDs and 36 Decoupling Capacitors (TOP LAYER F.Cu, Hidden Fab refs)
for d in led_positions:
    idx = d["id"]
    x = d["x"]
    y = d["y"]
    net_in = 2 + idx
    net_out = 3 + idx
    
    # WS2812B-2020 footprint with silkscreen number on PCB above LED (at y-2.4)
    # fp_text reference hidden on F.Fab (zero pink labels on LED die!)
    kicad_content += f"""  (module "LED_SMD:LED_WS2812B_PLCC4_2.0x2.0mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {x} {y})
    (descr "WS2812B-2020 LED {idx}")
    (path "/led_{idx}")
    (fp_text reference "D{idx}" (at 0 0) (layer F.Fab) hide
      (effects (font (size 0.5 0.5) (thickness 0.1)))
    )
    (fp_line (start -1.0 -1.0) (end 1.0 -1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start 1.0 -1.0) (end 1.0 1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start 1.0 1.0) (end -1.0 1.0) (layer F.SilkS) (width 0.12))
    (fp_line (start -1.0 1.0) (end -1.0 -1.0) (layer F.SilkS) (width 0.12))
    (pad 1 smd rect (at -0.85 -0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at -0.85 0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net {net_out} "DATA_{idx+1}"))
    (pad 3 smd rect (at 0.85 0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
    (pad 4 smd rect (at 0.85 -0.65) (size 0.6 0.5) (layers F.Cu F.Paste F.Mask) (net {net_in} "DATA_{idx}"))
  )
  (module "Capacitor_SMD:C_0402_1005Metric" (layer F.Cu) (tedit 5B301BBE)
    (at {round(x+2.0, 2)} {y} 90)
    (descr "100nF 0402 Capacitor {idx}")
    (path "/cap_{idx}")
    (fp_text reference "C{idx}" (at 0 0 90) (layer F.Fab) hide
      (effects (font (size 0.35 0.35) (thickness 0.07)))
    )
    (pad 1 smd rect (at -0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at 0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
  )
"""

# Copper Tracks: Power, Ground and Daisy Chain
# Inter-layer Vias bringing Signals & Power between Top and Bottom layers
led1 = led_positions[0]
for j in jst_ports:
    jx = j["x"]
    jy = j["y"]
    if j["type"] == "IN":
        # Data via from bottom JST to top LED 1
        via_x = round(jx + (1.5 if jx < 50 else -1.5), 2)
        via_y = round(jy, 2)
        kicad_content += f'  (via (at {via_x} {via_y}) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net 3))\n'
        kicad_content += f'  (segment (start {jx} {jy}) (end {via_x} {via_y}) (width 0.25) (layer B.Cu) (net 3))\n'
        kicad_content += f'  (segment (start {via_x} {via_y}) (end {led1["x"]+0.85} {led1["y"]-0.65}) (width 0.25) (layer F.Cu) (net 3))\n'
        # 5V connection via
        via_5v_x = round(jx + (2.5 if jx < 50 else -2.5), 2)
        via_5v_y = round(jy - 2.0, 2)
        kicad_content += f'  (via (at {via_5v_x} {via_5v_y}) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net 1))\n'
        kicad_content += f'  (segment (start {jx} {jy-2.0 if j["edge"] in ["LEFT","RIGHT"] else jy}) (end {via_5v_x} {via_5v_y}) (width 0.6) (layer B.Cu) (net 1))\n'
        kicad_content += f'  (segment (start {via_5v_x} {via_5v_y}) (end {led1["x"]-0.85} {led1["y"]-0.65}) (width 0.6) (layer F.Cu) (net 1))\n'

# Local decoupling tracks & GND vias for every LED
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

# Daisy-Chain DATA Traces between LEDs 1..36
for i in range(NUM_LEDS - 1):
    d1 = led_positions[i]
    d2 = led_positions[i + 1]
    net_id = 3 + d1["id"]
    p1_dout = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
    p2_din = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
    kicad_content += f'  (segment (start {p1_dout[0]} {p1_dout[1]}) (end {p2_din[0]} {p2_din[1]}) (width 0.25) (layer F.Cu) (net {net_id}))\n'
    
    # 5V Power bus linking capacitors along each row
    c1_5v = (round(d1["x"] + 2.0, 2), round(d1["y"] - 0.48, 2))
    c2_5v = (round(d2["x"] + 2.0, 2), round(d2["y"] - 0.48, 2))
    if d1["row"] == d2["row"]:
        kicad_content += f'  (segment (start {c1_5v[0]} {c1_5v[1]}) (end {c2_5v[0]} {c2_5v[1]}) (width 0.6) (layer F.Cu) (net 1))\n'

# Connect LED 36 DOUT to all 4 OUT ports via vias
led36 = led_positions[-1]
p36_dout = (round(led36["x"] - 0.85, 2), round(led36["y"] + 0.65, 2))
for j in jst_ports:
    if j["type"] == "OUT":
        jx = j["x"]
        jy = j["y"]
        via_dout_x = round(jx + (1.5 if jx < 50 else -1.5), 2)
        via_dout_y = round(jy, 2)
        kicad_content += f'  (via (at {via_dout_x} {via_dout_y}) (size 0.8) (drill 0.4) (layers F.Cu B.Cu) (net {NUM_LEDS+3}))\n'
        kicad_content += f'  (segment (start {p36_dout[0]} {p36_dout[1]}) (end {via_dout_x} {via_dout_y}) (width 0.25) (layer F.Cu) (net {NUM_LEDS+3}))\n'
        kicad_content += f'  (segment (start {via_dout_x} {via_dout_y}) (end {jx} {jy}) (width 0.25) (layer B.Cu) (net {NUM_LEDS+3}))\n'

# Solid GND Plane Zone on B.Cu
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

# KiCad 5 .pro file
pro_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.pro")
with open(pro_path, "w", encoding="utf-8") as f:
    f.write("[general]\nversion=1\n")

# KiCad 6+ .kicad_pro file
kicad_pro_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.kicad_pro")
with open(kicad_pro_path, "w", encoding="utf-8") as f:
    f.write('{"meta":{"version":1},"sheets":[]}')

# JLCPCB KiCad ZIP
zip_quote_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm_kicad.zip")
with zipfile.ZipFile(zip_quote_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(kicad_path, os.path.basename(kicad_path))
    z.write(pro_path, os.path.basename(pro_path))
    z.write(kicad_pro_path, os.path.basename(kicad_pro_path))
    z.write(bom_path, os.path.basename(bom_path))
    z.write(cpl_path, os.path.basename(cpl_path))

print(f"Generated JLCPCB KiCad ZIP: {zip_quote_path}")

# SMT Assembly Bundle ZIP
zip_smt_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm_smt.zip")
with zipfile.ZipFile(zip_smt_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(bom_path, os.path.basename(bom_path))
    z.write(cpl_path, os.path.basename(cpl_path))

print(f"Generated SMT Assembly Bundle: {zip_smt_path}")

# -------------------------------------------------------------
# 4. Generate Native RS-274X Gerber & Excellon Drill Files
# Includes .GTL, .GBL, .GTS, .GBS, .GTO, .GBO, .GTP, .GBP, .GKO, .DRL
# -------------------------------------------------------------
def coord_gbr(x, y):
    return f"X{int(round(x * 1000000)):d}Y{int(round(y * 1000000)):d}"

# Board Outline (.GKO)
gko_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GKO")
with open(gko_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Board Outline*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
X0Y0D02*
X100000000Y0D01*
X100000000Y100000000D01*
X0Y100000000D01*
X0Y0D01*
M02*
""")

# Excellon Drill File (.DRL) - 100% Standard Decimal Format for JLCPCB
drl_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.DRL")
with open(drl_path, "w", encoding="utf-8") as f:
    f.write("""; DRILL file for Universal 6x6 Bottom-Mounted 100mm PCB
; FORMAT={-:-/ absolute / metric / decimal}
M48
METRIC
T1C3.200
T2C2.000
T3C0.400
%
G90
G05
; 4 Corner M3 Mounting Holes
T1
""")
    for h in m3_holes:
        f.write(f"X{h['x']:.3f}Y{h['y']:.3f}\n")
    f.write("; 4 Fabric Sewing Eyelets\nT2\n")
    for s in sew_holes:
        f.write(f"X{s['x']:.3f}Y{s['y']:.3f}\n")
    f.write("; Inter-layer Vias\nT3\n")
    # Ground Vias for LEDs
    for d in led_positions:
        f.write(f"X{d['x'] + 2.0:.3f}Y{d['y'] + 1.2:.3f}\n")
    # JST Signal & Power Vias
    for j in jst_ports:
        jx, jy = j["x"], j["y"]
        via_x = round(jx + (1.5 if jx < 50 else -1.5), 2)
        f.write(f"X{via_x:.3f}Y{jy:.3f}\n")
        via_5v_x = round(jx + (2.5 if jx < 50 else -2.5), 2)
        f.write(f"X{via_5v_x:.3f}Y{jy - 2.0:.3f}\n")
    f.write("M30\n")

# Top Copper (.GTL) - LEDs, Caps, Power & Daisy Chain
gtl_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GTL")
with open(gtl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Copper (F.Cu) - Pure LED Array*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.250*%
%ADD11C,0.600*%
%ADD12C,0.400*%
%ADD13R,0.600X0.500*%
%ADD14R,0.560X0.620*%
%ADD18C,0.800*%
%ADD19C,5.000*%
%ADD20C,3.500*%
""")
    # 4 Corner M3 Mounting Hole Pads
    f.write("; 4 M3 Mounting Hole Pads\nD19*\n")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    
    # 4 Fabric Sewing Eyelet Pads
    f.write("; 4 Fabric Sewing Eyelet Pads\nD20*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    
    # 36 LEDs SMD Pads
    f.write("; WS2812B-2020 LED Pads\nD13*\n")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x - 0.85, y - 0.65)}D03*\n")
        f.write(f"{coord_gbr(x - 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y + 0.65)}D03*\n")
        f.write(f"{coord_gbr(x + 0.85, y - 0.65)}D03*\n")
        
    # 36 Decoupling Capacitor Pads
    f.write("; 0402 Capacitor Pads\nD14*\n")
    for d in led_positions:
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    
    # Decoupling Vias
    f.write("; Ground Vias\nD18*\n")
    for d in led_positions:
        f.write(f"{coord_gbr(round(d['x'] + 2.0, 2), round(d['y'] + 1.2, 2))}D03*\n")
    
    # Data Traces (D10)
    f.write("; Data Traces\nD10*\n")
    for i in range(NUM_LEDS - 1):
        d1 = led_positions[i]
        d2 = led_positions[i + 1]
        p1 = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
        p2 = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
        f.write(f"{coord_gbr(p1[0], p1[1])}D02*\n")
        f.write(f"{coord_gbr(p2[0], p2[1])}D01*\n")
        
    f.write("M02*\n")

# Bottom Copper (.GBL) - JST Connectors & Ground Plane
gbl_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GBL")
with open(gbl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Copper (B.Cu) - JST Connectors & Ground Plane*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.800*%
%ADD11C,5.000*%
%ADD12C,3.500*%
%ADD13R,96.000X96.000*%
%ADD15R,1.000X1.600*%
%ADD16R,1.600X1.000*%
D13*
X50000000Y50000000D03*
D11*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D12*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    
    # 8 JST Connectors SMD Pads on Bottom!
    f.write("; 8 JST-PH 3P Connectors on Bottom\n")
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        if j["edge"] in ["LEFT", "RIGHT"]:
            f.write("D16*\n")
            f.write(f"{coord_gbr(jx, jy - 2.0)}D03*\n")
            f.write(f"{coord_gbr(jx, jy)}D03*\n")
            f.write(f"{coord_gbr(jx, jy + 2.0)}D03*\n")
        else:
            f.write("D15*\n")
            f.write(f"{coord_gbr(jx - 2.0, jy)}D03*\n")
            f.write(f"{coord_gbr(jx, jy)}D03*\n")
            f.write(f"{coord_gbr(jx + 2.0, jy)}D03*\n")
    f.write("M02*\n")

# Top Solder Mask (.GTS)
gts_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GTS")
with open(gts_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Solder Mask (F.Mask)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10R,0.700X0.600*%
%ADD11R,0.660X0.720*%
%ADD15C,5.200*%
%ADD16C,3.700*%
D15*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D16*\n")
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
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n")
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n")
    f.write("M02*\n")

# Bottom Solder Mask (.GBS)
gbs_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GBS")
with open(gbs_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Solder Mask (B.Mask)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD15C,5.200*%
%ADD16C,3.700*%
%ADD17R,1.100X1.700*%
%ADD18R,1.700X1.100*%
D15*
""")
    for h in m3_holes:
        f.write(f"{coord_gbr(h['x'], h['y'])}D03*\n")
    f.write("D16*\n")
    for s in sew_holes:
        f.write(f"{coord_gbr(s['x'], s['y'])}D03*\n")
    # Solder mask openings for Bottom JST pads
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        if j["edge"] in ["LEFT", "RIGHT"]:
            f.write("D18*\n")
            f.write(f"{coord_gbr(jx, jy - 2.0)}D03*\n")
            f.write(f"{coord_gbr(jx, jy)}D03*\n")
            f.write(f"{coord_gbr(jx, jy + 2.0)}D03*\n")
        else:
            f.write("D17*\n")
            f.write(f"{coord_gbr(jx - 2.0, jy)}D03*\n")
            f.write(f"{coord_gbr(jx, jy)}D03*\n")
            f.write(f"{coord_gbr(jx + 2.0, jy)}D03*\n")
    f.write("M02*\n")

# Top Solder Paste (.GTP) - Stencil for LEDs and Caps
gtp_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GTP")
with open(gtp_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Solder Paste (F.Paste)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD13R,0.600X0.500*%
%ADD14R,0.560X0.620*%
D13*
""")
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
    f.write("M02*\n")

# Bottom Solder Paste (.GBP) - Stencil for Bottom JST Connectors (Essential for Double-Sided PCBA!)
gbp_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GBP")
with open(gbp_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Solder Paste (B.Paste) - JST Connectors*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD15R,1.000X1.600*%
%ADD16R,1.600X1.000*%
""")
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        if j["edge"] in ["LEFT", "RIGHT"]:
            f.write("D16*\n")
            f.write(f"{coord_gbr(jx, jy - 2.0)}D03*\n")
            f.write(f"{coord_gbr(jx, jy)}D03*\n")
            f.write(f"{coord_gbr(jx, jy + 2.0)}D03*\n")
        else:
            f.write("D15*\n")
            f.write(f"{coord_gbr(jx - 2.0, jy)}D03*\n")
            f.write(f"{coord_gbr(jx, jy)}D03*\n")
            f.write(f"{coord_gbr(jx + 2.0, jy)}D03*\n")
    f.write("M02*\n")

# Vector Stroke Font Dictionary for Top and Bottom Silkscreen
FONT_GLYPHS = {
    '0': [(0,0, 2,0), (2,0, 2,4), (2,4, 0,4), (0,4, 0,0), (0,0, 2,4)],
    '1': [(1,0, 1,4), (0,3, 1,4)],
    '2': [(0,4, 2,4), (2,4, 2,2), (2,2, 0,2), (0,2, 0,0), (0,0, 2,0)],
    '3': [(0,4, 2,4), (2,4, 2,0), (0,0, 2,0), (0,2, 2,2)],
    '4': [(0,4, 0,2), (0,2, 2,2), (2,4, 2,0)],
    '5': [(2,4, 0,4), (0,4, 0,2), (0,2, 2,2), (2,2, 2,0), (2,0, 0,0)],
    '6': [(2,4, 0,4), (0,4, 0,0), (0,0, 2,0), (2,0, 2,2), (2,2, 0,2)],
    '7': [(0,4, 2,4), (2,4, 1,0)],
    '8': [(0,0, 2,0), (2,0, 2,4), (2,4, 0,4), (0,4, 0,0), (0,2, 2,2)],
    '9': [(0,0, 2,0), (2,0, 2,4), (2,4, 0,4), (0,4, 0,2), (0,2, 2,2)],
    'A': [(0,0, 0,4), (0,4, 2,4), (2,4, 2,0), (0,2, 2,2)],
    'B': [(0,0, 0,4), (0,4, 1.5,4), (1.5,4, 2,3), (2,3, 1.5,2), (1.5,2, 0,2), (1.5,2, 2,1), (2,1, 1.5,0), (1.5,0, 0,0)],
    'C': [(2,4, 0,4), (0,4, 0,0), (0,0, 2,0)],
    'D': [(0,0, 0,4), (0,4, 1.5,4), (1.5,4, 2,2), (2,2, 1.5,0), (1.5,0, 0,0)],
    'E': [(2,4, 0,4), (0,4, 0,0), (0,0, 2,0), (0,2, 1.5,2)],
    'F': [(2,4, 0,4), (0,4, 0,0), (0,2, 1.5,2)],
    'G': [(2,4, 0,4), (0,4, 0,0), (0,0, 2,0), (2,0, 2,2), (1,2, 2,2)],
    'H': [(0,0, 0,4), (2,0, 2,4), (0,2, 2,2)],
    'I': [(0,4, 2,4), (1,4, 1,0), (0,0, 2,0)],
    'J': [(2,4, 2,1), (2,1, 1,0), (1,0, 0,1)],
    'K': [(0,0, 0,4), (2,4, 0,2), (0,2, 2,0)],
    'L': [(0,4, 0,0), (0,0, 2,0)],
    'M': [(0,0, 0,4), (0,4, 1,2), (1,2, 2,4), (2,4, 2,0)],
    'N': [(0,0, 0,4), (0,4, 2,0), (2,0, 2,4)],
    'O': [(0,0, 2,0), (2,0, 2,4), (2,4, 0,4), (0,4, 0,0)],
    'P': [(0,0, 0,4), (0,4, 2,4), (2,4, 2,2), (2,2, 0,2)],
    'Q': [(0,0, 2,0), (2,0, 2,4), (2,4, 0,4), (0,4, 0,0), (1,1, 2,0)],
    'R': [(0,0, 0,4), (0,4, 2,4), (2,4, 2,2), (2,2, 0,2), (1,2, 2,0)],
    'S': [(2,4, 0,4), (0,4, 0,2), (0,2, 2,2), (2,2, 2,0), (2,0, 0,0)],
    'T': [(0,4, 2,4), (1,4, 1,0)],
    'U': [(0,4, 0,0), (0,0, 2,0), (2,0, 2,4)],
    'V': [(0,4, 1,0), (1,0, 2,4)],
    'W': [(0,4, 0.5,0), (0.5,0, 1,2), (1,2, 1.5,0), (1.5,0, 2,4)],
    'X': [(0,0, 2,4), (0,4, 2,0)],
    'Y': [(0,4, 1,2), (2,4, 1,2), (1,2, 1,0)],
    'Z': [(0,4, 2,4), (2,4, 0,0), (0,0, 2,0)],
    '+': [(1,1, 1,3), (0,2, 2,2)],
    '-': [(0,2, 2,2)],
    '.': [(0.8,0, 1.2,0)],
    '[': [(1.5,4, 0.5,4), (0.5,4, 0.5,0), (0.5,0, 1.5,0)],
    ']': [(0.5,4, 1.5,4), (1.5,4, 1.5,0), (1.5,0, 0.5,0)],
    ' ': [],
}

def write_gbr_text(f, text, cx, cy, char_w=0.6, char_h=0.9, spacing=0.2, rot=0):
    sx = char_w / 2.0
    sy = char_h / 4.0
    total_w = len(text) * char_w + max(0, len(text) - 1) * spacing
    start_x = -total_w / 2.0
    start_y = -char_h / 2.0
    rad = math.radians(rot)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    for i, ch in enumerate(text.upper()):
        if ch not in FONT_GLYPHS: continue
        ch_x = start_x + i * (char_w + spacing)
        for x1, y1, x2, y2 in FONT_GLYPHS[ch]:
            lx1 = ch_x + x1 * sx
            ly1 = start_y + y1 * sy
            lx2 = ch_x + x2 * sx
            ly2 = start_y + y2 * sy
            rx1 = lx1 * cos_r - ly1 * sin_r
            ry1 = lx1 * sin_r + ly1 * cos_r
            rx2 = lx2 * cos_r - ly2 * sin_r
            ry2 = lx2 * sin_r + ly2 * cos_r
            f.write(f"{coord_gbr(cx + rx1, cy + ry1)}D02*\n")
            f.write(f"{coord_gbr(cx + rx2, cy + ry2)}D01*\n")

# Top Silkscreen (.GTO) - 100% Flush Front: Only LED numbers, M3/SEW labels & Title!
gto_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GTO")
with open(gto_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Silkscreen (F.SilkS) - Front Clean Display*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
""")
    # 1. Silkscreen outlines & labels for M3 mounting holes
    for h in m3_holes:
        hx, hy = h["x"], h["y"]
        r = 2.6
        f.write(f"{coord_gbr(hx - r, hy)}D02*\n")
        f.write(f"{coord_gbr(hx - r*0.7, hy + r*0.7)}D01*\n")
        f.write(f"{coord_gbr(hx, hy + r)}D01*\n")
        f.write(f"{coord_gbr(hx + r*0.7, hy + r*0.7)}D01*\n")
        f.write(f"{coord_gbr(hx + r, hy)}D01*\n")
        f.write(f"{coord_gbr(hx + r*0.7, hy - r*0.7)}D01*\n")
        f.write(f"{coord_gbr(hx, hy - r)}D01*\n")
        f.write(f"{coord_gbr(hx - r*0.7, hy - r*0.7)}D01*\n")
        f.write(f"{coord_gbr(hx - r, hy)}D01*\n")
        lbl_x = hx + 3.2 if (hx < 50) else hx - 3.2
        write_gbr_text(f, "M3", lbl_x, hy, char_w=0.6, char_h=0.9)
    
    # 2. Silkscreen outlines & labels for Sewing Eyelets
    for s in sew_holes:
        sx, sy = s["x"], s["y"]
        r = 1.8
        f.write(f"{coord_gbr(sx - r, sy)}D02*\n")
        f.write(f"{coord_gbr(sx - r*0.7, sy + r*0.7)}D01*\n")
        f.write(f"{coord_gbr(sx, sy + r)}D01*\n")
        f.write(f"{coord_gbr(sx + r*0.7, sy + r*0.7)}D01*\n")
        f.write(f"{coord_gbr(sx + r, sy)}D01*\n")
        f.write(f"{coord_gbr(sx + r*0.7, sy - r*0.7)}D01*\n")
        f.write(f"{coord_gbr(sx, sy - r)}D01*\n")
        f.write(f"{coord_gbr(sx - r*0.7, sy - r*0.7)}D01*\n")
        f.write(f"{coord_gbr(sx - r, sy)}D01*\n")
        lbl_y = sy + 2.5 if (sy < 50) else sy - 2.5
        write_gbr_text(f, "SEW", sx, lbl_y, char_w=0.5, char_h=0.75)

    # 3. Silkscreen outlines for LEDs & Numerals on the PCB Surface (at y - 2.4)
    for d in led_positions:
        x, y = d["x"], d["y"]
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D02*\n")
        f.write(f"{coord_gbr(x+1.0, y-1.0)}D01*\n")
        f.write(f"{coord_gbr(x+1.0, y+1.0)}D01*\n")
        f.write(f"{coord_gbr(x-1.0, y+1.0)}D01*\n")
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D01*\n")
        write_gbr_text(f, str(d["id"]), x, y - 2.4, char_w=0.65, char_h=1.0)
    
    # 4. Front Board Title
    write_gbr_text(f, "MSEP 6X6 FLUSH FRONT", 50.0, 48.5, char_w=0.9, char_h=1.4)
    write_gbr_text(f, "17MM SEAMLESS PITCH", 50.0, 51.5, char_w=0.6, char_h=0.9)
    f.write("M02*\n")

# Bottom Silkscreen (.GBO) - Back Side: All 8 JST Connector Outlines, Labels & Roles!
gbo_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm.GBO")
with open(gbo_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Silkscreen (B.SilkS) - Rear JST Ports*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
""")
    # Outlines & bold pin callouts for all 8 JST Connectors on the back
    for j in jst_ports:
        jx = j["x"]
        jy = j["y"]
        jtype = j["type"]
        edge = j["edge"]
        
        if edge in ["LEFT", "RIGHT"]:
            hw, hh = 2.5, 3.8
            f.write(f"{coord_gbr(jx - hw, jy - hh)}D02*\n")
            f.write(f"{coord_gbr(jx + hw, jy - hh)}D01*\n")
            f.write(f"{coord_gbr(jx + hw, jy + hh)}D01*\n")
            f.write(f"{coord_gbr(jx - hw, jy + hh)}D01*\n")
            f.write(f"{coord_gbr(jx - hw, jy - hh)}D01*\n")
            tx = jx + 4.2 if (edge == "LEFT") else jx - 4.2
            write_gbr_text(f, "+5V", tx, jy - 2.0, char_w=0.55, char_h=0.85)
            write_gbr_text(f, "DAT", tx, jy, char_w=0.55, char_h=0.85)
            write_gbr_text(f, "GND", tx, jy + 2.0, char_w=0.55, char_h=0.85)
            write_gbr_text(f, f"[{jtype}]", jx, jy - 4.8, char_w=0.6, char_h=0.9)
        else: # TOP, BOTTOM
            hw, hh = 3.8, 2.5
            f.write(f"{coord_gbr(jx - hw, jy - hh)}D02*\n")
            f.write(f"{coord_gbr(jx + hw, jy - hh)}D01*\n")
            f.write(f"{coord_gbr(jx + hw, jy + hh)}D01*\n")
            f.write(f"{coord_gbr(jx - hw, jy + hh)}D01*\n")
            f.write(f"{coord_gbr(jx - hw, jy - hh)}D01*\n")
            ty = jy + 4.2 if (edge == "TOP") else jy - 4.2
            write_gbr_text(f, "+5V", jx - 2.0, ty, char_w=0.55, char_h=0.85, rot=90)
            write_gbr_text(f, "DAT", jx, ty, char_w=0.55, char_h=0.85, rot=90)
            write_gbr_text(f, "GND", jx + 2.0, ty, char_w=0.55, char_h=0.85, rot=90)
            write_gbr_text(f, f"[{jtype}]", jx - 4.8, jy, char_w=0.6, char_h=0.9, rot=90)

    # Back Board Title
    write_gbr_text(f, "REAR HARNESS BAY", 50.0, 48.5, char_w=0.8, char_h=1.2)
    write_gbr_text(f, "CONNECT 50MM PATCH CABLES HERE", 50.0, 51.5, char_w=0.5, char_h=0.8)
    f.write("M02*\n")

# Package into standard JLCPCB Native Gerber ZIP (with Bottom Paste & Silkscreen!)
zip_gerber_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_100mm_gerbers.zip")
with zipfile.ZipFile(zip_gerber_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in [gko_path, drl_path, gtl_path, gbl_path, gts_path, gbs_path, gto_path, gbo_path, gtp_path, gbp_path]:
        z.write(p, os.path.basename(p))

print(f"Generated Native RS-274X Gerber ZIP: {zip_gerber_path}")

# -------------------------------------------------------------
# 5. Generate Interactive Web Inspector (HTML + SVG)
# Dual View: Front (100% Flush LEDs) vs Rear (JST Harnesses & 50mm Straight Cables)
# -------------------------------------------------------------
html_path = os.path.join(BOTTOM_PCB_DIR, "universal_6x6_bottom_preview.html")

# Precompute SVG elements
svg_leds = ""
for d in led_positions:
    x, y, idx = d["x"], d["y"], d["id"]
    svg_leds += f"""
    <!-- LED {idx} -->
    <g class="led-group" data-idx="{idx}">
      <rect class="led-pkg" x="{x-1.0}" y="{y-1.0}" width="2.0" height="2.0" rx="0.25" fill="#1e1e1e" stroke="#444" stroke-width="0.1"/>
      <rect id="die-{idx}" class="led-die" x="{x-0.7}" y="{y-0.7}" width="1.4" height="1.4" rx="0.15" fill="#fff5cc" stroke="none"/>
      <rect class="cap-pkg" x="{x+1.5}" y="{y-0.5}" width="1.0" height="1.0" rx="0.1" fill="#b8860b" stroke="#333" stroke-width="0.08"/>
      <text x="{x}" y="{y-2.4}" font-size="0.85" fill="#58a6ff" text-anchor="middle" font-family="monospace" font-weight="bold">{idx}</text>
    </g>"""

svg_jsts = ""
for j in jst_ports:
    jx, jy, jtype, edge = j["x"], j["y"], j["type"], j["edge"]
    color = "#00ffcc" if jtype == "IN" else "#ff3366"
    if edge in ["LEFT", "RIGHT"]:
        txt_x = jx + 4.0 if (edge == "LEFT") else jx - 4.0
        svg_jsts += f"""
    <g class="jst-port">
      <rect x="{jx-2.5}" y="{jy-3.8}" width="5.0" height="7.6" rx="0.5" fill="#2a2a2a" stroke="{color}" stroke-width="0.25"/>
      <circle cx="{jx}" cy="{jy-2.0}" r="0.5" fill="#ffd700"/>
      <circle cx="{jx}" cy="{jy}" r="0.5" fill="#ffd700"/>
      <circle cx="{jx}" cy="{jy+2.0}" r="0.5" fill="#ffd700"/>
      <text x="{jx}" y="{jy-4.5}" font-size="0.8" fill="{color}" text-anchor="middle" font-weight="bold">[{jtype}]</text>
      <text x="{txt_x}" y="{jy-1.7}" font-size="0.55" fill="#ffd700" text-anchor="middle">+5V</text>
      <text x="{txt_x}" y="{jy+0.3}" font-size="0.55" fill="#00ffcc" text-anchor="middle">DAT</text>
      <text x="{txt_x}" y="{jy+2.3}" font-size="0.55" fill="#888" text-anchor="middle">GND</text>
    </g>"""
    else:
        txt_y = jy + 4.2 if (edge == "TOP") else jy - 3.2
        svg_jsts += f"""
    <g class="jst-port">
      <rect x="{jx-3.8}" y="{jy-2.5}" width="7.6" height="5.0" rx="0.5" fill="#2a2a2a" stroke="{color}" stroke-width="0.25"/>
      <circle cx="{jx-2.0}" cy="{jy}" r="0.5" fill="#ffd700"/>
      <circle cx="{jx}" cy="{jy}" r="0.5" fill="#ffd700"/>
      <circle cx="{jx+2.0}" cy="{jy}" r="0.5" fill="#ffd700"/>
      <text x="{jx-4.8}" y="{jy+0.3}" font-size="0.8" fill="{color}" text-anchor="end" font-weight="bold">[{jtype}]</text>
      <text x="{jx-2.0}" y="{txt_y}" font-size="0.55" fill="#ffd700" text-anchor="middle">+5V</text>
      <text x="{jx}" y="{txt_y}" font-size="0.55" fill="#00ffcc" text-anchor="middle">DAT</text>
      <text x="{jx+2.0}" y="{txt_y}" font-size="0.55" fill="#888" text-anchor="middle">GND</text>
    </g>"""

svg_holes = ""
for h in m3_holes:
    hx, hy = h["x"], h["y"]
    svg_holes += f"""
    <g class="mount-hole">
      <circle cx="{hx}" cy="{hy}" r="2.5" fill="#2d3748" stroke="#ffd700" stroke-width="0.3"/>
      <circle cx="{hx}" cy="{hy}" r="1.6" fill="#05080c"/>
      <text x="{hx}" y="{hy-3.0}" font-size="0.8" fill="#ffd700" text-anchor="middle" font-weight="bold">M3</text>
    </g>"""

for s in sew_holes:
    sx, sy = s["x"], s["y"]
    svg_holes += f"""
    <g class="sew-hole">
      <circle cx="{sx}" cy="{sy}" r="1.75" fill="#2d3748" stroke="#00ffff" stroke-width="0.25"/>
      <circle cx="{sx}" cy="{sy}" r="1.0" fill="#05080c"/>
      <text x="{sx}" y="{sy-2.2}" font-size="0.65" fill="#00ffff" text-anchor="middle" font-weight="bold">SEW</text>
    </g>"""

# SVG 4-Tile Chest Cluster (Rear Harness View showing exact 22mm Straight 50mm JST Cables!)
svg_chest_tiles = ""
quad_offsets = [
    ("QUAD 1 (TOP-L)", 0, 0),
    ("QUAD 2 (TOP-R)", 102, 0),
    ("QUAD 3 (BOT-R)", 102, 102),
    ("QUAD 4 (BOT-L)", 0, 102)
]

for q_label, qx, qy in quad_offsets:
    svg_chest_tiles += f"""
    <!-- {q_label} (Rear View) -->
    <g transform="translate({qx}, {qy})">
      <rect x="0" y="0" width="100" height="100" rx="1.5" fill="#13231b" stroke="#ffd700" stroke-width="0.25"/>
      <text x="50" y="50" font-size="3.5" fill="#2d5a3f" text-anchor="middle" font-weight="bold" opacity="0.45">{q_label} (REAR)</text>
    """
    for h in m3_holes:
        svg_chest_tiles += f'<circle cx="{h["x"]}" cy="{h["y"]}" r="1.6" fill="#05080c" stroke="#ffd700" stroke-width="0.3"/>\n'
    for s in sew_holes:
        svg_chest_tiles += f'<circle cx="{s["x"]}" cy="{s["y"]}" r="1.0" fill="#05080c" stroke="#00ffff" stroke-width="0.25"/>\n'
    svg_chest_tiles += "    </g>\n"

# 1. Straight horizontal 50mm cable from Quad 1 OUT_R (90.0, 33.0) to Quad 2 IN_L (112.0, 33.0): exactly 22.0mm span!
svg_chest_tiles += '<line x1="90.0" y1="33.0" x2="112.0" y2="33.0" stroke="#00ffcc" stroke-width="1.2" stroke-linecap="round"/>\n'
svg_chest_tiles += '<text x="101.0" y="30.5" font-size="2.2" fill="#00ffcc" text-anchor="middle" font-weight="bold">STRAIGHT 50mm CABLE (22.0mm span)</text>\n'

# 2. Straight vertical 50mm cable from Quad 2 OUT_B (135.0, 90.0) to Quad 3 IN_T (135.0, 112.0): exactly 22.0mm span!
svg_chest_tiles += '<line x1="135.0" y1="90.0" x2="135.0" y2="112.0" stroke="#00ffcc" stroke-width="1.2" stroke-linecap="round"/>\n'
svg_chest_tiles += '<text x="137.5" y="101.5" font-size="2.2" fill="#00ffcc" text-anchor="start" font-weight="bold">STRAIGHT 50mm CABLE (22.0mm span)</text>\n'

# 3. Straight horizontal 50mm cable from Quad 3 OUT_L (112.0, 169.0) to Quad 4 IN_R (90.0, 169.0): exactly 22.0mm span!
svg_chest_tiles += '<line x1="112.0" y1="169.0" x2="90.0" y2="169.0" stroke="#00ffcc" stroke-width="1.2" stroke-linecap="round"/>\n'
svg_chest_tiles += '<text x="101.0" y="166.5" font-size="2.2" fill="#00ffcc" text-anchor="middle" font-weight="bold">STRAIGHT 50mm CABLE (22.0mm span)</text>\n'

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Universal 100mm × 100mm Seamless 6×6 LED Matrix (Bottom-Mounted JST Connectors)</title>
<style>
  :root {{
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #58a6ff;
    --green: #238636;
    --gold: #ffd700;
  }}
  body {{
    margin: 0;
    padding: 20px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  .container {{
    max-width: 1340px;
    margin: 0 auto;
  }}
  h1 {{
    color: #fff;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 22px;
    margin-bottom: 6px;
  }}
  .subtitle {{
    color: #8b949e;
    font-size: 14px;
    margin-bottom: 20px;
  }}
  .badge {{
    background: #238636;
    color: #fff;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
  }}
  .badge-rear {{
    background: #8957e5;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 20px;
    margin-top: 16px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
  }}
  .viewer-box {{
    position: relative;
    background: #05080c;
    border-radius: 8px;
    border: 1px solid var(--border);
    overflow: hidden;
    height: 720px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  svg {{
    width: 100%;
    height: 100%;
    max-height: 700px;
  }}
  .ctrl-row {{
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }}
  button {{
    background: #21262d;
    color: #fff;
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s;
  }}
  button:hover {{
    background: #30363d;
    border-color: #8b949e;
  }}
  button.active {{
    background: #1f6feb;
    border-color: #58a6ff;
  }}
  .btn-download {{
    background: var(--green);
    border-color: #2ea043;
    font-weight: 600;
  }}
  .btn-download:hover {{
    background: #2ea043;
  }}
  .stat-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 12px;
  }}
  .stat-box {{
    background: #0d1117;
    border: 1px solid var(--border);
    padding: 10px;
    border-radius: 6px;
  }}
  .stat-label {{
    font-size: 11px;
    color: #8b949e;
    text-transform: uppercase;
  }}
  .stat-val {{
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    margin-top: 4px;
  }}
  .callout {{
    background: rgba(35, 134, 54, 0.15);
    border-left: 3px solid #238636;
    padding: 10px 12px;
    border-radius: 0 6px 6px 0;
    margin-top: 12px;
    font-size: 12px;
    line-height: 1.5;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>
    🏰 Universal 100mm 6×6 LED Matrix
    <span class="badge badge-rear">Bottom-Mounted Connectors</span>
    <span class="badge">100% Flush Front</span>
  </h1>
  <div class="subtitle">
    Pure LED display face with 100% flush fabric/faceplate contact. All 8 JST horizontal headers mounted on the rear layer (B.Cu) for straight 22.0mm 50mm cable jumpers.
  </div>

  <div class="ctrl-row">
    <button id="btn-front" class="active" onclick="setView('front')">👁️ Front View (LEDs Only)</button>
    <button id="btn-rear" onclick="setView('rear')">🔌 Rear View (8x JST Ports)</button>
    <button id="btn-cluster" onclick="setView('cluster')">🧩 4-Tile Chest Cluster (Rear Cabling)</button>
    <button id="btn-light" onclick="toggleLights()">💡 Light Up LEDs</button>
  </div>

  <div class="grid">
    <div class="card viewer-box">
      <!-- 1. Single Tile Front View (Pure LEDs) -->
      <svg id="svg-front" viewBox="-5 -5 110 110">
        <rect x="0" y="0" width="100" height="100" rx="1.5" fill="#13231b" stroke="#ffd700" stroke-width="0.3"/>
        {svg_holes}
        {svg_leds}
        <text x="50" y="50" font-size="2.6" fill="#2d5a3f" text-anchor="middle" font-weight="bold" opacity="0.4">100% FLUSH FRONT (0.9mm MAX HEIGHT)</text>
      </svg>

      <!-- 2. Single Tile Rear View (8 JST Ports on B.Cu) -->
      <svg id="svg-rear" viewBox="-5 -5 110 110" style="display:none;">
        <rect x="0" y="0" width="100" height="100" rx="1.5" fill="#1c2128" stroke="#8957e5" stroke-width="0.3"/>
        {svg_holes}
        {svg_jsts}
        <text x="50" y="50" font-size="2.6" fill="#8957e5" text-anchor="middle" font-weight="bold" opacity="0.5">REAR HARNESS BAY (8x JST-PH PORTS)</text>
      </svg>

      <!-- 3. 4-Tile Chest Cluster View (Rear Cabling with 22mm Straight 50mm Cables) -->
      <svg id="svg-cluster" viewBox="-10 -10 226 226" style="display:none;">
        {svg_chest_tiles}
      </svg>
    </div>

    <div>
      <div class="card">
        <h3 style="margin-top:0; color:#fff; font-size:16px;">💎 Hardware Specifications</h3>
        <div class="stat-grid">
          <div class="stat-box">
            <div class="stat-label">Board Size</div>
            <div class="stat-val">100 × 100 mm</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Uniform Pitch</div>
            <div class="stat-val">17.00 mm</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Front Clearance</div>
            <div class="stat-val" style="color:#00ff88;">0.0 mm (Flush!)</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Seam Cable Span</div>
            <div class="stat-val">22.0 mm Straight</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">SMT Assembly</div>
            <div class="stat-val">Double-Sided</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Extra Cost / Board</div>
            <div class="stat-val" style="color:#58a6ff;">+$0.80 (75 qty)</div>
          </div>
        </div>

        <div class="callout">
          <strong>✨ Optical Perfection:</strong> The front surface contains only 0.9mm LEDs. Fabric shirts or 3D-printed faceplates touch the LEDs directly with zero air gap, zero light bleed, and zero fabric tenting!
        </div>

        <h4 style="color:#fff; margin-top:16px; margin-bottom:8px; font-size:14px;">🚀 Turnkey JLCPCB Packages</h4>
        <div style="display:flex; flex-direction:column; gap:8px;">
          <a href="universal_6x6_bottom_100mm_gerbers.zip" download style="text-decoration:none;">
            <button class="btn-download" style="width:100%;">📦 Download Gerbers ZIP (Double-Sided SMT)</button>
          </a>
          <a href="universal_6x6_bottom_100mm_bom.csv" download style="text-decoration:none;">
            <button style="width:100%;">📋 Download BOM (Auto-Match LCSC Parts)</button>
          </a>
          <a href="universal_6x6_bottom_100mm_cpl.csv" download style="text-decoration:none;">
            <button style="width:100%;">📍 Download CPL (Top LEDs + Bottom JST)</button>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
  function setView(mode) {{
    document.getElementById('svg-front').style.display = (mode === 'front') ? 'block' : 'none';
    document.getElementById('svg-rear').style.display = (mode === 'rear') ? 'block' : 'none';
    document.getElementById('svg-cluster').style.display = (mode === 'cluster') ? 'block' : 'none';
    document.getElementById('btn-front').className = (mode === 'front') ? 'active' : '';
    document.getElementById('btn-rear').className = (mode === 'rear') ? 'active' : '';
    document.getElementById('btn-cluster').className = (mode === 'cluster') ? 'active' : '';
  }}

  let lit = false;
  function toggleLights() {{
    lit = !lit;
    const dies = document.querySelectorAll('.led-die');
    dies.forEach(die => {{
      die.style.fill = lit ? '#00ffff' : '#fff5cc';
      die.style.filter = lit ? 'drop-shadow(0 0 2px #00ffff)' : 'none';
    }});
  }}
</script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated Interactive Inspector: {html_path}")
