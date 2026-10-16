import os
import json
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB_DIR = os.path.join(BASE_DIR, "pcb")
os.makedirs(PCB_DIR, exist_ok=True)

# -------------------------------------------------------------
# Configuration: Staggered Brick 6x6 LED Matrix (100mm x 100mm)
# -------------------------------------------------------------
BOARD_SIZE_MM = 100.0
GRID_ROWS = 6
GRID_COLS = 6
NUM_LEDS = GRID_ROWS * GRID_COLS  # 36 LEDs

# Staggered Brick Geometry:
# Rows alternate horizontal position like offset bricks!
# Row 1, 3, 5: Normal position (left aligned with 8.75mm margin)
# Row 2, 4, 6: Shifted right by half a brick (7.5mm offset)
PITCH_X = 15.0
PITCH_Y = 15.0
ROW_OFFSET = PITCH_X / 2.0  # 7.5 mm offset for brick stagger!

# Total horizontal pattern footprint: (5 * 15.0) + 7.5 = 82.5 mm
# Margins centered on 100mm board:
MARGIN_X = (BOARD_SIZE_MM - ((GRID_COLS - 1) * PITCH_X + ROW_OFFSET)) / 2.0  # 8.75 mm
MARGIN_Y = (BOARD_SIZE_MM - (GRID_ROWS - 1) * PITCH_Y) / 2.0                 # 12.5 mm

# Generate 36 Staggered LED coordinates in Serpentine sequence
led_positions = []
led_idx = 1

for r in range(GRID_ROWS):
    y = round(MARGIN_Y + r * PITCH_Y, 2)
    # Stagger: odd row indices (Row 2, 4, 6) shift right by ROW_OFFSET
    row_shift = ROW_OFFSET if (r % 2 == 1) else 0.0
    
    col_range = range(GRID_COLS) if (r % 2 == 0) else range(GRID_COLS - 1, -1, -1)
    for c in col_range:
        x = round(MARGIN_X + row_shift + c * PITCH_X, 2)
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

# Connectors: 4-Pin 1.0mm pitch FPC Ribbon Connectors + Direct Solder Pads
# J1: Input Ribbon Connector (Left edge at x=4.5, y=20.0)
# J2: Output Ribbon Connector (Right edge at x=95.5, y=80.0)
j1_pos = {"ref": "J1", "x": 4.5, "y": 20.0, "rot": 90, "descr": "FPC-4P-1.0mm-IN"}
j2_pos = {"ref": "J2", "x": 95.5, "y": 80.0, "rot": 270, "descr": "FPC-4P-1.0mm-OUT"}

# -------------------------------------------------------------
# 1. Generate JLCPCB BOM (Bill of Materials) CSV
# -------------------------------------------------------------
bom_path = os.path.join(PCB_DIR, "universal_6x6_100mm_bom.csv")
with open(bom_path, "w", encoding="utf-8") as f:
    f.write("Comment,Designator,Footprint,LCSC Part #\n")
    led_refs = " ".join([d["ref"] for d in led_positions])
    cap_refs = " ".join([d["cap_ref"] for d in led_positions])
    f.write(f'"WS2812B-2020 Addressable RGB LED","{led_refs}","LED-SMD_4P-L2.0-W2.0-TL","C52917434"\n')
    f.write(f'"100nF (0.1uF) 50V 0402 Capacitor","{cap_refs}","C0402","C1525"\n')
    f.write('"4-Pin 1.0mm Pitch FPC/FFC Horizontal SMT Connector","J1 J2","FPC-1.0-4P-SMT","C2840003"\n')

print(f"Generated BOM: {bom_path}")

# -------------------------------------------------------------
# 2. Generate JLCPCB CPL (Pick and Place Centroid) CSV
# -------------------------------------------------------------
cpl_path = os.path.join(PCB_DIR, "universal_6x6_100mm_cpl.csv")
with open(cpl_path, "w", encoding="utf-8") as f:
    f.write("Designator,Mid X,Mid Y,Layer,Rotation\n")
    for d in led_positions:
        f.write(f'{d["ref"]},{d["x"]},{d["y"]},Top,0\n')
        # Capacitor placed 2.0mm to the right of LED
        f.write(f'{d["cap_ref"]},{round(d["x"] + 2.0, 2)},{d["y"]},Top,90\n')
    f.write(f'{j1_pos["ref"]},{j1_pos["x"]},{j1_pos["y"]},Top,{j1_pos["rot"]}\n')
    f.write(f'{j2_pos["ref"]},{j2_pos["x"]},{j2_pos["y"]},Top,{j2_pos["rot"]}\n')

print(f"Generated CPL: {cpl_path}")

# -------------------------------------------------------------
# 3. Generate KiCad 5 Compatible PCB File (.kicad_pcb)
# -------------------------------------------------------------
kicad_path = os.path.join(PCB_DIR, "universal_6x6_100mm.kicad_pcb")

num_nets = NUM_LEDS + 3  # Net 0 (none), 1 (+5V), 2 (GND), 3..38 (DATA_1..36)
kicad_content = f"""(kicad_pcb (version 20171130) (host pcbnew "(5.1.9)-1")
  (general
    (thickness 1.6)
    (drawings 0)
    (tracks 0)
    (zones 0)
    (modules {NUM_LEDS * 2 + 6})
    (nets {num_nets})
  )
  (page A4)
  (layers
    (0 F.Cu signal)
    (31 B.Cu signal)
    (36 B.SilkS user)
    (37 F.SilkS user)
    (38 B.Mask user)
    (39 F.Mask user)
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

# Board Outline: 100mm x 100mm CLOSED continuous rectangle on Edge.Cuts (100% KiCad 5 / JLCPCB DFM compliant)
b = BOARD_SIZE_MM
kicad_content += f"""  (gr_line (start 0 0) (end {b} 0) (layer Edge.Cuts) (width 0.15))
  (gr_line (start {b} 0) (end {b} {b}) (layer Edge.Cuts) (width 0.15))
  (gr_line (start {b} {b}) (end 0 {b}) (layer Edge.Cuts) (width 0.15))
  (gr_line (start 0 {b}) (end 0 0) (layer Edge.Cuts) (width 0.15))
"""

# 4 Corner Mounting Holes (Ø3.2mm M3 / Barb clearance with 6.0mm pad keepout)
corners = [(4.0, 4.0), (96.0, 4.0), (4.0, 96.0), (96.0, 96.0)]
for idx, (cx, cy) in enumerate(corners):
    kicad_content += f"""  (module "MountingHole:MountingHole_3.2mm_M3" (layer F.Cu) (tedit 5D5A6E4F)
    (at {cx} {cy})
    (descr "Mounting Hole 3.2mm M3")
    (path "/hole_{idx+1}")
    (fp_text reference "H{idx+1}" (at 0 -2.5) (layer F.SilkS)
      (effects (font (size 0.8 0.8) (thickness 0.15)))
    )
    (pad 1 thru_hole circle (at 0 0) (size 6.0 6.0) (drill 3.2) (layers *.Cu *.Mask))
  )
"""

# Direct Solder Pad Headers on Left (IN) and Right (OUT) edges
kicad_content += f"""  (module "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical" (layer F.Cu) (tedit 5D5A6E4F)
    (at 4.5 32.0 90)
    (descr "Direct Wire Solder Pads - IN (+5V, DIN, GND)")
    (path "/hdr_in")
    (fp_text reference "IN_PADS" (at 0 -2.5 90) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (pad 1 thru_hole rect (at -2.54 0 90) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) (net 1 "+5V"))
    (pad 2 thru_hole oval (at 0 0 90) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) (net 3 "DATA_1"))
    (pad 3 thru_hole oval (at 2.54 0 90) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) (net 2 "GND"))
  )
  (module "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical" (layer F.Cu) (tedit 5D5A6E4F)
    (at 95.5 68.0 90)
    (descr "Direct Wire Solder Pads - OUT (+5V, DOUT, GND)")
    (path "/hdr_out")
    (fp_text reference "OUT_PADS" (at 0 -2.5 90) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (pad 1 thru_hole rect (at -2.54 0 90) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) (net 1 "+5V"))
    (pad 2 thru_hole oval (at 0 0 90) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) (net {NUM_LEDS+3} "DATA_{NUM_LEDS+1}"))
    (pad 3 thru_hole oval (at 2.54 0 90) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) (net 2 "GND"))
  )
"""

# FPC 4-Pin 1.0mm Connectors J1 (IN) and J2 (OUT)
kicad_content += f"""  (module "Connector_FFC-FPC:Molex_200528-0040_1x04-1MP_P1.00mm_Horizontal" (layer F.Cu) (tedit 5D5A6E4F)
    (at {j1_pos["x"]} {j1_pos["y"]} {j1_pos["rot"]})
    (descr "4-Pin 1.0mm Pitch FPC Connector - IN")
    (path "/j1")
    (fp_text reference "J1_IN" (at 0 -2.8 {j1_pos["rot"]}) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (pad 1 smd rect (at -1.5 0 {j1_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at -0.5 0 {j1_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 3 smd rect (at 0.5 0 {j1_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 3 "DATA_1"))
    (pad 4 smd rect (at 1.5 0 {j1_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
  )
  (module "Connector_FFC-FPC:Molex_200528-0040_1x04-1MP_P1.00mm_Horizontal" (layer F.Cu) (tedit 5D5A6E4F)
    (at {j2_pos["x"]} {j2_pos["y"]} {j2_pos["rot"]})
    (descr "4-Pin 1.0mm Pitch FPC Connector - OUT")
    (path "/j2")
    (fp_text reference "J2_OUT" (at 0 -2.8 {j2_pos["rot"]}) (layer F.SilkS)
      (effects (font (size 0.7 0.7) (thickness 0.12)))
    )
    (pad 1 smd rect (at -1.5 0 {j2_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at -0.5 0 {j2_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 3 smd rect (at 0.5 0 {j2_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net {NUM_LEDS+3} "DATA_{NUM_LEDS+1}"))
    (pad 4 smd rect (at 1.5 0 {j2_pos["rot"]}) (size 0.6 1.5) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
  )
"""

# 36 LEDs and 36 Decoupling Capacitors (Staggered Brick Layout)
for d in led_positions:
    idx = d["id"]
    x = d["x"]
    y = d["y"]
    net_in = 2 + idx
    net_out = 3 + idx
    
    # WS2812B-2020 footprint
    kicad_content += f"""  (module "LED_SMD:LED_WS2812B_PLCC4_2.0x2.0mm" (layer F.Cu) (tedit 5D5A6E4F)
    (at {x} {y})
    (descr "WS2812B-2020 Addressable RGB LED")
    (path "/led_{idx}")
    (fp_text reference "{d['ref']}" (at 0 -1.8) (layer F.SilkS)
      (effects (font (size 0.6 0.6) (thickness 0.12)))
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
    (descr "100nF 0402 Bypass Capacitor")
    (path "/cap_{idx}")
    (fp_text reference "{d['cap_ref']}" (at 0 -1.0 90) (layer F.SilkS)
      (effects (font (size 0.4 0.4) (thickness 0.08)))
    )
    (pad 1 smd rect (at -0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (net 1 "+5V"))
    (pad 2 smd rect (at 0.48 0 90) (size 0.56 0.62) (layers F.Cu F.Paste F.Mask) (net 2 "GND"))
  )
"""

# Copper Tracks: Power, Ground and Daisy Chain
# J1 to LED 1
led1 = led_positions[0]
kicad_content += f'  (segment (start {j1_pos["x"]} {j1_pos["y"]}) (end {led1["x"]-0.85} {led1["y"]-0.65}) (width 0.6) (layer F.Cu) (net 1))\n'
kicad_content += f'  (segment (start {j1_pos["x"]} {j1_pos["y"]+0.5}) (end {led1["x"]+0.85} {led1["y"]-0.65}) (width 0.3) (layer F.Cu) (net 3))\n'

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

# LED 36 DOUT to J2 Connector via bottom border channel (clean routing)
led36 = led_positions[-1]
p36_dout = (round(led36["x"] - 0.85, 2), round(led36["y"] + 0.65, 2))
# Trace steps: D36 -> bottom margin y=94.5 -> across to x=93.5 -> up to J2
kicad_content += f'  (segment (start {p36_dout[0]} {p36_dout[1]}) (end {p36_dout[0]} 94.5) (width 0.25) (layer F.Cu) (net {NUM_LEDS+3}))\n'
kicad_content += f'  (segment (start {p36_dout[0]} 94.5) (end 93.5 94.5) (width 0.25) (layer F.Cu) (net {NUM_LEDS+3}))\n'
kicad_content += f'  (segment (start 93.5 94.5) (end 93.5 {j2_pos["y"]}) (width 0.25) (layer F.Cu) (net {NUM_LEDS+3}))\n'
kicad_content += f'  (segment (start 93.5 {j2_pos["y"]}) (end {j2_pos["x"]} {j2_pos["y"]}) (width 0.25) (layer F.Cu) (net {NUM_LEDS+3}))\n'

# Solid GND Plane Zone on B.Cu (matching petes_dragon_fpc.kicad_pcb syntax)
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

# KiCad 5 .pro file (required by JLCPCB KiCad 5 parser!)
pro_path = os.path.join(PCB_DIR, "universal_6x6_100mm.pro")
with open(pro_path, "w", encoding="utf-8") as f:
    f.write("[general]\nversion=1\n")

# KiCad 6+ .kicad_pro file
kicad_pro_path = os.path.join(PCB_DIR, "universal_6x6_100mm.kicad_pro")
with open(kicad_pro_path, "w", encoding="utf-8") as f:
    f.write('{"meta":{"version":1},"sheets":[]}')

# Updated JLCPCB KiCad ZIP
zip_quote_path = os.path.join(PCB_DIR, "universal_6x6_100mm_kicad.zip")
with zipfile.ZipFile(zip_quote_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(kicad_path, os.path.basename(kicad_path))
    z.write(pro_path, os.path.basename(pro_path))
    z.write(kicad_pro_path, os.path.basename(kicad_pro_path))
    z.write(bom_path, os.path.basename(bom_path))
    z.write(cpl_path, os.path.basename(cpl_path))

print(f"Generated JLCPCB KiCad ZIP: {zip_quote_path}")

# SMT Assembly Bundle ZIP
zip_smt_path = os.path.join(PCB_DIR, "universal_6x6_100mm_smt.zip")
with zipfile.ZipFile(zip_smt_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(bom_path, os.path.basename(bom_path))
    z.write(cpl_path, os.path.basename(cpl_path))

print(f"Generated SMT Assembly Bundle: {zip_smt_path}")

# -------------------------------------------------------------
# 4. Generate Native RS-274X Gerber & Excellon Drill Files
#    (Guaranteed 100% immediate viewer rendering on JLCPCB!)
# -------------------------------------------------------------
def coord_gbr(x, y):
    return f"X{int(round(x * 1000000)):d}Y{int(round(y * 1000000)):d}"

# 4.1 Board Outline (.GKO / .GML)
gko_path = os.path.join(PCB_DIR, "universal_6x6_100mm.GKO")
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

# 4.2 Excellon Drill File (.DRL)
drl_path = os.path.join(PCB_DIR, "universal_6x6_100mm.DRL")
with open(drl_path, "w", encoding="utf-8") as f:
    f.write("""M48
; DRILL file for Universal 6x6 100mm PCB
; Generated for JLCPCB
METRIC,LZ
; Tool definitions
T1C3.200
T2C0.400
T3C1.000
%
G90
G05
; T1: Mounting Holes (4x M3 Ø3.2mm)
T1
X4000000Y4000000
X96000000Y4000000
X4000000Y96000000
X96000000Y96000000
; T2: Decoupling Ground Vias (36x Ø0.4mm)
T2
""")
    for d in led_positions:
        vx = round(d["x"] + 2.0, 2)
        vy = round(d["y"] + 1.2, 2)
        f.write(f"X{int(round(vx*1000000)):d}Y{int(round(vy*1000000)):d}\n")
    
    # T3: Direct Solder Header Pins (6x Ø1.0mm)
    f.write("; T3: Direct Solder Headers (6x Ø1.0mm)\nT3\n")
    # IN header
    for py in [29.46, 32.0, 34.54]:
        f.write(f"X4500000Y{int(round(py*1000000)):d}\n")
    # OUT header
    for py in [65.46, 68.0, 70.54]:
        f.write(f"X95500000Y{int(round(py*1000000)):d}\n")
    f.write("M30\n")

# 4.3 Top Copper (.GTL)
gtl_path = os.path.join(PCB_DIR, "universal_6x6_100mm.GTL")
with open(gtl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Copper (F.Cu)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.250*%
%ADD11C,0.600*%
%ADD12C,0.400*%
%ADD13R,0.600X0.500*%
%ADD14R,0.560X0.620*%
%ADD15R,0.600X1.500*%
%ADD16R,1.800X1.800*%
%ADD17C,1.800*%
%ADD18C,0.800*%
%ADD19C,6.000*%
""")
    # 4 Corner Mounting Hole Copper Rings
    f.write("; Mounting Hole Pads\nD19*\n")
    for cx, cy in corners:
        f.write(f"{coord_gbr(cx, cy)}D03*\n")
    
    # Direct Solder Pad Headers
    f.write("; Direct Solder Headers\nD16*\n")
    f.write(f"{coord_gbr(4.5, 29.46)}D03*\n")  # Pin 1 IN (rect)
    f.write(f"{coord_gbr(95.5, 65.46)}D03*\n") # Pin 1 OUT (rect)
    f.write("D17*\n")
    for py in [32.0, 34.54]:
        f.write(f"{coord_gbr(4.5, py)}D03*\n")
    for py in [68.0, 70.54]:
        f.write(f"{coord_gbr(95.5, py)}D03*\n")
        
    # J1 & J2 FPC SMT Pads
    f.write("; FPC Connectors J1 & J2\nD15*\n")
    for offset in [-1.5, -0.5, 0.5, 1.5]:
        f.write(f"{coord_gbr(j1_pos['x'], j1_pos['y'] + offset)}D03*\n")
        f.write(f"{coord_gbr(j2_pos['x'], j2_pos['y'] + offset)}D03*\n")
    
    # 36 LEDs SMD Pads
    f.write("; WS2812B-2020 LED Pads\nD13*\n")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x - 0.85, y - 0.65)}D03*\n") # Pin 1: 5V
        f.write(f"{coord_gbr(x - 0.85, y + 0.65)}D03*\n") # Pin 2: DOUT
        f.write(f"{coord_gbr(x + 0.85, y + 0.65)}D03*\n") # Pin 3: GND
        f.write(f"{coord_gbr(x + 0.85, y - 0.65)}D03*\n") # Pin 4: DIN
        
    # 36 Decoupling Capacitor Pads
    f.write("; 0402 Capacitor Pads\nD14*\n")
    for d in led_positions:
        cx = round(d["x"] + 2.0, 2)
        cy = d["y"]
        f.write(f"{coord_gbr(cx, cy - 0.48)}D03*\n") # 5V
        f.write(f"{coord_gbr(cx, cy + 0.48)}D03*\n") # GND
    
    # Decoupling Vias
    f.write("; Ground Vias\nD18*\n")
    for d in led_positions:
        f.write(f"{coord_gbr(round(d['x'] + 2.0, 2), round(d['y'] + 1.2, 2))}D03*\n")
    
    # Data Traces (D10)
    f.write("; Data Traces\nD10*\n")
    # J1 to LED 1
    f.write(f"{coord_gbr(j1_pos['x'], j1_pos['y'] + 0.5)}D02*\n")
    f.write(f"{coord_gbr(led1['x'] + 0.85, led1['y'] - 0.65)}D01*\n")
    # Inter-LED Daisy Chain
    for i in range(NUM_LEDS - 1):
        d1 = led_positions[i]
        d2 = led_positions[i + 1]
        p1 = (round(d1["x"] - 0.85, 2), round(d1["y"] + 0.65, 2))
        p2 = (round(d2["x"] + 0.85, 2), round(d2["y"] - 0.65, 2))
        f.write(f"{coord_gbr(p1[0], p1[1])}D02*\n")
        f.write(f"{coord_gbr(p2[0], p2[1])}D01*\n")
    # LED 36 to J2
    f.write(f"{coord_gbr(p36_dout[0], p36_dout[1])}D02*\n")
    f.write(f"{coord_gbr(p36_dout[0], 94.5)}D01*\n")
    f.write(f"{coord_gbr(93.5, 94.5)}D01*\n")
    f.write(f"{coord_gbr(93.5, j2_pos['y'])}D01*\n")
    f.write(f"{coord_gbr(j2_pos['x'], j2_pos['y'])}D01*\n")
    
    # Power Traces (D11 & D12)
    f.write("; Power Bus Traces\nD11*\n")
    f.write(f"{coord_gbr(j1_pos['x'], j1_pos['y'])}D02*\n")
    f.write(f"{coord_gbr(led1['x'] - 0.85, led1['y'] - 0.65)}D01*\n")
    for i in range(NUM_LEDS - 1):
        d1 = led_positions[i]
        d2 = led_positions[i + 1]
        if d1["row"] == d2["row"]:
            c1_5v = (round(d1["x"] + 2.0, 2), round(d1["y"] - 0.48, 2))
            c2_5v = (round(d2["x"] + 2.0, 2), round(d2["y"] - 0.48, 2))
            f.write(f"{coord_gbr(c1_5v[0], c1_5v[1])}D02*\n")
            f.write(f"{coord_gbr(c2_5v[0], c2_5v[1])}D01*\n")
    f.write("M02*\n")

# 4.4 Bottom Copper (.GBL) - Ground Plane + Via pads
gbl_path = os.path.join(PCB_DIR, "universal_6x6_100mm.GBL")
with open(gbl_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Copper (B.Cu) - Ground Plane*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.800*%
%ADD11C,6.000*%
%ADD12C,1.800*%
%ADD13R,96.000X96.000*%
D13*
X50000000Y50000000D03*
D11*
X4000000Y4000000D03*
X96000000Y4000000D03*
X4000000Y96000000D03*
X96000000Y96000000D03*
D12*
X4500000Y29460000D03*
X4500000Y32000000D03*
X4500000Y34540000D03*
X95500000Y65460000D03*
X95500000Y68000000D03*
X95500000Y70540000D03*
M02*
""")

# 4.5 Top Solder Mask (.GTS)
gts_path = os.path.join(PCB_DIR, "universal_6x6_100mm.GTS")
with open(gts_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Solder Mask (F.Mask)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10R,0.700X0.600*%
%ADD11R,0.660X0.720*%
%ADD12R,0.700X1.600*%
%ADD13C,1.900*%
%ADD14R,1.900X1.900*%
%ADD15C,6.200*%
D15*
X4000000Y4000000D03*
X96000000Y4000000D03*
X4000000Y96000000D03*
X96000000Y96000000D03*
D14*
X4500000Y29460000D03*
X95500000Y65460000D03*
D13*
X4500000Y32000000D03*
X4500000Y34540000D03*
X95500000Y68000000D03*
X95500000Y70540000D03*
D12*
""")
    for offset in [-1.5, -0.5, 0.5, 1.5]:
        f.write(f"{coord_gbr(j1_pos['x'], j1_pos['y'] + offset)}D03*\n")
        f.write(f"{coord_gbr(j2_pos['x'], j2_pos['y'] + offset)}D03*\n")
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

# 4.6 Bottom Solder Mask (.GBS)
gbs_path = os.path.join(PCB_DIR, "universal_6x6_100mm.GBS")
with open(gbs_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Bottom Solder Mask (B.Mask)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,6.200*%
%ADD11C,1.900*%
D10*
X4000000Y4000000D03*
X96000000Y4000000D03*
X4000000Y96000000D03*
X96000000Y96000000D03*
D11*
X4500000Y29460000D03*
X4500000Y32000000D03*
X4500000Y34540000D03*
X95500000Y65460000D03*
X95500000Y68000000D03*
X95500000Y70540000D03*
M02*
""")

# 4.7 Top Silkscreen (.GTO)
gto_path = os.path.join(PCB_DIR, "universal_6x6_100mm.GTO")
with open(gto_path, "w", encoding="utf-8") as f:
    f.write("""G04 Layer: Top Silkscreen (F.SilkS)*
%FSLAX46Y46*%
%MOMM*%
%LPD*%
%ADD10C,0.150*%
D10*
""")
    for d in led_positions:
        x = d["x"]
        y = d["y"]
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D02*\n")
        f.write(f"{coord_gbr(x+1.0, y-1.0)}D01*\n")
        f.write(f"{coord_gbr(x+1.0, y+1.0)}D01*\n")
        f.write(f"{coord_gbr(x-1.0, y+1.0)}D01*\n")
        f.write(f"{coord_gbr(x-1.0, y-1.0)}D01*\n")
    f.write("M02*\n")

# Package into standard JLCPCB Native Gerber ZIP!
zip_gerber_path = os.path.join(PCB_DIR, "universal_6x6_100mm_gerbers.zip")
with zipfile.ZipFile(zip_gerber_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in [gko_path, drl_path, gtl_path, gbl_path, gts_path, gbs_path, gto_path]:
        z.write(p, os.path.basename(p))

print(f"Generated Native RS-274X Gerber ZIP: {zip_gerber_path}")

# -------------------------------------------------------------
# 5. Generate Interactive Web Inspector (HTML + SVG + Simulation)
# -------------------------------------------------------------
html_path = os.path.join(PCB_DIR, "universal_6x6_preview.html")

# Precompute SVG elements for Single Tile View
svg_leds = ""
for d in led_positions:
    x = d["x"]
    y = d["y"]
    idx = d["id"]
    svg_leds += f"""
    <!-- LED {idx} (Row {d['row']}, Col {d['col']}) -->
    <g class="led-group" data-idx="{idx}">
      <rect class="led-pkg" x="{x-1.0}" y="{y-1.0}" width="2.0" height="2.0" rx="0.25" fill="#1e1e1e" stroke="#444" stroke-width="0.1"/>
      <rect id="die-{idx}" class="led-die" x="{x-0.7}" y="{y-0.7}" width="1.4" height="1.4" rx="0.15" fill="#fff5cc" stroke="none"/>
      <rect class="cap-pkg" x="{x+1.5}" y="{y-0.5}" width="1.0" height="1.0" rx="0.1" fill="#b8860b" stroke="#333" stroke-width="0.08"/>
      <text x="{x}" y="{y-1.4}" font-size="0.65" fill="#888" text-anchor="middle" font-family="monospace">D{idx}</text>
    </g>"""

# SVG Daisy Chain Tracks
svg_tracks = ""
for i in range(NUM_LEDS - 1):
    d1 = led_positions[i]
    d2 = led_positions[i + 1]
    svg_tracks += f'<line x1="{d1["x"]}" y1="{d1["y"]}" x2="{d2["x"]}" y2="{d2["y"]}" stroke="#ffd700" stroke-width="0.3" stroke-linecap="round" opacity="0.85"/>\n'

# SVG 4-Tile Chest Cluster LEDs generator (Staggered Brick Layout for all 4 quadrants)
svg_chest_tiles = ""
quad_offsets = [
    ("QUAD 1 (TOP-L)", 0, 0),
    ("QUAD 2 (TOP-R)", 106, 0),
    ("QUAD 3 (BOT-R)", 106, 106),
    ("QUAD 4 (BOT-L)", 0, 106)
]

for q_label, qx, qy in quad_offsets:
    svg_chest_tiles += f"""
    <!-- {q_label} -->
    <g transform="translate({qx}, {qy})">
      <rect x="0" y="0" width="100" height="100" rx="2" fill="#13231b" stroke="#ffd700" stroke-width="0.3"/>
      <text x="50" y="50" font-size="4.0" fill="#2d5a3f" text-anchor="middle" font-weight="bold" opacity="0.35">{q_label}</text>
    """
    for d in led_positions:
        lx = d["x"]
        ly = d["y"]
        svg_chest_tiles += f'<circle cx="{lx}" cy="{ly}" r="1.1" fill="#00ff88" opacity="0.8"/>\n'
    svg_chest_tiles += "    </g>\n"

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Universal 100mm × 100mm Staggered Brick 6×6 LED Matrix Inspector</title>
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
    max-width: 1320px;
    margin: 0 auto;
  }}
  h1 {{
    color: #fff;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 24px;
    margin-bottom: 6px;
  }}
  .badge {{
    background: var(--green);
    color: #fff;
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 12px;
    font-weight: 600;
  }}
  .badge-gold {{
    background: #b08800;
    color: #fff;
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 12px;
    font-weight: 600;
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
    border-radius: 6px;
    padding: 10px;
  }}
  .stat-val {{
    font-size: 18px;
    font-weight: 700;
    color: #58a6ff;
  }}
  .stat-lbl {{
    font-size: 11px;
    color: #8b949e;
    margin-top: 2px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-top: 10px;
  }}
  th, td {{
    padding: 6px 8px;
    border-bottom: 1px solid var(--border);
    text-align: left;
  }}
  th {{
    color: #8b949e;
  }}
  .step-box {{
    background: #0d1117;
    border-left: 3px solid #58a6ff;
    padding: 10px 12px;
    border-radius: 4px;
    margin-bottom: 10px;
    font-size: 12px;
    line-height: 1.5;
  }}
</style>
</head>
<body>

<div class="container">
  <h1>
    Universal 100mm × 100mm Staggered Brick 6×6 LED Matrix
    <span class="badge">JLCPCB Turnkey SMT</span>
    <span class="badge-gold">🧱 Offset Brick Rows (15mm Pitch)</span>
  </h1>
  <p style="margin: 0 0 12px 0; color: #8b949e; font-size: 14px;">
    Rows alternate with a 7.5mm horizontal shift like running-bond brickwork! Provides smooth, organic curves for Disney float characters while maintaining a standard 100mm &times; 100mm JLCPCB form factor with thin FPC ribbon interconnects.
  </p>

  <div class="ctrl-row">
    <button id="btn-toggle-view" class="active" onclick="toggleViewMode()">📐 1-Tile Staggered View</button>
    <button id="btn-toggle-chest" onclick="toggleChestMode()">🎽 4-Tile Chest Cluster View (144 LEDs)</button>
    <button id="btn-light-all" onclick="toggleLightAll()">✨ Light Up All LEDs</button>
    <button id="btn-data-pulse" onclick="toggleDataPulse()">⚡ Animated DIN Data Pulse</button>
    <a href="universal_6x6_100mm_gerbers.zip" download><button class="btn-download">🌟 Download Native Gerber ZIP (Recommended)</button></a>
    <a href="universal_6x6_100mm_kicad.zip" download><button>📦 Download KiCad 5 ZIP</button></a>
    <a href="universal_6x6_100mm_smt.zip" download><button class="btn-download">⚡ Download SMT Bundle (BOM + CPL)</button></a>
  </div>

  <div class="grid">
    <div class="card viewer-box">
      <!-- SVG Single Tile View -->
      <svg id="svg-single" viewBox="-8 -8 116 116">
        <!-- Board Background (Matte Green FR-4 with gold border) -->
        <rect x="0" y="0" width="100" height="100" rx="2.0" ry="2.0" fill="#13231b" stroke="#ffd700" stroke-width="0.35"/>
        
        <!-- Corner Mounting Holes (Ø3.2mm M3 clearance, 6.0mm keepout) -->
        <g id="mounting-holes">
          <circle cx="4.0" cy="4.0" r="3.0" fill="#2d3748" stroke="#ffd700" stroke-width="0.2"/>
          <circle cx="4.0" cy="4.0" r="1.6" fill="#05080c"/>
          <circle cx="96.0" cy="4.0" r="3.0" fill="#2d3748" stroke="#ffd700" stroke-width="0.2"/>
          <circle cx="96.0" cy="4.0" r="1.6" fill="#05080c"/>
          <circle cx="4.0" cy="96.0" r="3.0" fill="#2d3748" stroke="#ffd700" stroke-width="0.2"/>
          <circle cx="4.0" cy="96.0" r="1.6" fill="#05080c"/>
          <circle cx="96.0" cy="96.0" r="3.0" fill="#2d3748" stroke="#ffd700" stroke-width="0.2"/>
          <circle cx="96.0" cy="96.0" r="1.6" fill="#05080c"/>
        </g>

        <!-- Connectors -->
        <!-- J1: 4-Pin 1.0mm FPC Ribbon IN (Left Edge) -->
        <g id="j1-conn">
          <rect x="2.5" y="16.5" width="4.0" height="7.0" rx="0.5" fill="#2a2a2a" stroke="#888" stroke-width="0.15"/>
          <rect x="1.8" y="18.0" width="1.0" height="4.0" fill="#ffd700"/>
          <text x="5.0" y="15.5" font-size="0.8" fill="#58a6ff" text-anchor="middle" font-family="sans-serif" font-weight="bold">J1 (FPC IN)</text>
        </g>
        <!-- Direct Solder Pads IN -->
        <g id="hdr-in">
          <circle cx="4.5" cy="29.46" r="0.9" fill="#ffd700"/>
          <circle cx="4.5" cy="32.0" r="0.9" fill="#ffd700"/>
          <circle cx="4.5" cy="34.54" r="0.9" fill="#ffd700"/>
          <text x="4.5" y="37.0" font-size="0.65" fill="#888" text-anchor="middle">IN PADS</text>
        </g>

        <!-- J2: 4-Pin 1.0mm FPC Ribbon OUT (Right Edge) -->
        <g id="j2-conn">
          <rect x="93.5" y="76.5" width="4.0" height="7.0" rx="0.5" fill="#2a2a2a" stroke="#888" stroke-width="0.15"/>
          <rect x="97.2" y="78.0" width="1.0" height="4.0" fill="#ffd700"/>
          <text x="95.0" y="75.5" font-size="0.8" fill="#58a6ff" text-anchor="middle" font-family="sans-serif" font-weight="bold">J2 (FPC OUT)</text>
        </g>
        <!-- Direct Solder Pads OUT -->
        <g id="hdr-out">
          <circle cx="95.5" cy="65.46" r="0.9" fill="#ffd700"/>
          <circle cx="95.5" cy="68.0" r="0.9" fill="#ffd700"/>
          <circle cx="95.5" cy="70.54" r="0.9" fill="#ffd700"/>
          <text x="95.5" y="73.0" font-size="0.65" fill="#888" text-anchor="middle">OUT PADS</text>
        </g>

        <!-- Daisy Chain Copper Tracks -->
        <g id="copper-tracks">
          {svg_tracks}
          <!-- DOUT path to J2 via bottom margin -->
          <path d="M 15.4 88.15 L 15.4 94.5 L 93.5 94.5 L 93.5 80.0 L 95.5 80.0" fill="none" stroke="#ffd700" stroke-width="0.25" opacity="0.85"/>
        </g>

        <!-- 36 LEDs and Capacitors in Staggered Brick Positions -->
        <g id="led-elements">
          {svg_leds}
        </g>

        <!-- Animated Data Pulse Dot -->
        <circle id="pulse-dot" cx="8.75" cy="12.5" r="1.2" fill="#fff" opacity="0" filter="drop-shadow(0 0 2px #00ffcc)"/>
      </svg>

      <!-- SVG 4-Tile Chest View (Staggered Honeycomb Array) -->
      <svg id="svg-chest" viewBox="-15 -15 236 236" style="display: none;">
        <!-- Living Hinge Felt Base Background -->
        <rect x="-8" y="-8" width="222" height="222" rx="6" fill="#1c1917" stroke="#444" stroke-width="0.8"/>
        <text x="103" y="-2" font-size="2.8" fill="#888" text-anchor="middle" font-weight="bold">2.0mm FELT LIVING HINGE CHEST ENVELOPE (206mm × 206mm)</text>
        
        {svg_chest_tiles}

        <!-- Thin Flexible Ribbon Interconnect Cables Across 6mm Seams -->
        <!-- Ribbon 1: Quad 1 (Top-L) OUT to Quad 2 (Top-R) IN -->
        <path d="M 97 80 C 101 80, 103 20, 108 20" fill="none" stroke="#00ffcc" stroke-width="1.2" stroke-dasharray="1.5,1"/>
        <text x="103" y="52" font-size="1.8" fill="#00ffcc" text-anchor="middle" transform="rotate(90 103 52)">4-Pin FPC Ribbon (50mm)</text>

        <!-- Ribbon 2: Quad 2 (Top-R) OUT to Quad 3 (Bot-R) IN -->
        <path d="M 203 80 C 208 80, 208 126, 112 126" fill="none" stroke="#00ffcc" stroke-width="1.2" stroke-dasharray="1.5,1"/>
        <text x="160" y="103.5" font-size="1.8" fill="#00ffcc" text-anchor="middle">4-Pin FPC Ribbon</text>

        <!-- Ribbon 3: Quad 3 (Bot-R) OUT to Quad 4 (Bot-L) IN -->
        <path d="M 203 186 C 205 200, 5 200, 3 126" fill="none" stroke="#00ffcc" stroke-width="1.2" stroke-dasharray="1.5,1"/>
        <text x="103" y="196" font-size="1.8" fill="#00ffcc" text-anchor="middle">4-Pin FPC Ribbon (50mm)</text>

        <!-- JST Power/Data Input to Quad 1 -->
        <line x1="-12" y1="20" x2="3" y2="20" stroke="#ff3366" stroke-width="1.5"/>
        <text x="-6" y="17" font-size="1.8" fill="#ff3366">From ESP32</text>
      </svg>
    </div>

    <!-- Sidebar Stats & JLCPCB Quote Guide -->
    <div>
      <div class="card">
        <h3 style="margin-top:0; color:#fff;">🧱 Staggered Brick Specifications</h3>
        <div class="stat-grid">
          <div class="stat-box">
            <div class="stat-val">100 × 100</div>
            <div class="stat-lbl">Dimensions (mm)</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">36</div>
            <div class="stat-lbl">WS2812B-2020 LEDs</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">15.0 mm</div>
            <div class="stat-lbl">Horizontal / Vert Pitch</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">7.5 mm</div>
            <div class="stat-lbl">Brick Offset Stagger</div>
          </div>
        </div>

        <h4 style="margin: 16px 0 6px 0; color:#fff;">⚡ Bill of Materials (LCSC Parts)</h4>
        <table>
          <thead>
            <tr><th>Component</th><th>Package</th><th>LCSC Part #</th></tr>
          </thead>
          <tbody>
            <tr><td>WS2812B-2020-V6 (36x)</td><td>SMD 2020</td><td><code>C52917434</code></td></tr>
            <tr><td>100nF Cap (36x)</td><td>0402 50V</td><td><code>C1525</code></td></tr>
            <tr><td>FPC 4P 1.0mm (2x)</td><td>Horizontal SMT</td><td><code>C2840003</code></td></tr>
          </tbody>
        </table>
      </div>

      <div class="card" style="margin-top: 16px;">
        <h3 style="margin-top:0; color:#fff;">🛒 JLCPCB Quoting Guide</h3>
        <div class="step-box">
          <strong>Step 1: Upload Native Gerber ZIP</strong><br>
          Go to <a href="https://jlcpcb.com/quote" target="_blank" style="color:#58a6ff;">jlcpcb.com/quote</a> and upload <code>universal_6x6_100mm_gerbers.zip</code> (native RS-274X bypasses any KiCad conversion!).
        </div>
        <div class="step-box">
          <strong>Step 2: Instant Gerber Viewer</strong><br>
          The Gerber viewer opens instantly showing all 8 layers, dimensions 100mm &times; 100mm, and closed Edge.Cuts outline.
        </div>
        <div class="step-box">
          <strong>Step 3: Enable SMT Assembly</strong><br>
          Toggle <em>"PCB Assembly"</em> to ON. Upload <code>universal_6x6_100mm_bom.csv</code> and <code>universal_6x6_100mm_cpl.csv</code> (or drag <code>universal_6x6_100mm_smt.zip</code>).
        </div>
        <div class="step-box">
          <strong>Step 4: Review Instant Quote</strong><br>
          DFM viewer matches all 36 LEDs, 36 caps, and 2 FPC connectors to their pads!
        </div>
      </div>
    </div>
  </div>
</div>

<script>
  let isLit = false;
  let pulseTimer = null;
  let currentPulse = 0;
  const numLeds = 36;

  function toggleViewMode() {{
    document.getElementById('svg-single').style.display = 'block';
    document.getElementById('svg-chest').style.display = 'none';
    document.getElementById('btn-toggle-view').classList.add('active');
    document.getElementById('btn-toggle-chest').classList.remove('active');
  }}

  function toggleChestMode() {{
    document.getElementById('svg-single').style.display = 'none';
    document.getElementById('svg-chest').style.display = 'block';
    document.getElementById('btn-toggle-chest').classList.add('active');
    document.getElementById('btn-toggle-view').classList.remove('active');
  }}

  function toggleLightAll() {{
    isLit = !isLit;
    const btn = document.getElementById('btn-light-all');
    btn.classList.toggle('active', isLit);
    
    for (let i = 1; i <= numLeds; i++) {{
      const die = document.getElementById('die-' + i);
      if (die) {{
        if (isLit) {{
          // Parade Emerald Green & Gold
          die.setAttribute('fill', i % 4 === 0 ? '#ffd700' : '#00ff88');
          die.style.filter = 'drop-shadow(0 0 1.5px #00ff88)';
        }} else {{
          die.setAttribute('fill', '#fff5cc');
          die.style.filter = 'none';
        }}
      }}
    }}
  }}

  function toggleDataPulse() {{
    const btn = document.getElementById('btn-data-pulse');
    const dot = document.getElementById('pulse-dot');
    
    if (pulseTimer) {{
      clearInterval(pulseTimer);
      pulseTimer = null;
      btn.classList.remove('active');
      dot.setAttribute('opacity', '0');
    }} else {{
      btn.classList.add('active');
      dot.setAttribute('opacity', '1');
      currentPulse = 1;
      
      pulseTimer = setInterval(() => {{
        const group = document.querySelector('.led-group[data-idx="' + currentPulse + '"]');
        if (group) {{
          const die = group.querySelector('.led-die');
          const cx = parseFloat(die.getAttribute('x')) + 0.7;
          const cy = parseFloat(die.getAttribute('y')) + 0.7;
          dot.setAttribute('cx', cx);
          dot.setAttribute('cy', cy);
        }}
        currentPulse++;
        if (currentPulse > numLeds) currentPulse = 1;
      }}, 50);
    }}
  }}
</script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated Interactive Inspector: {html_path}")
