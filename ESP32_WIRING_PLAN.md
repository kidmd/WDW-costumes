# 🔌 ESP32 Hardware Wiring Plan & Electrical Specification
## Main Street Electrical Parade (WDW 10K) Synchronized LED Costumes

This document provides the definitive, bench-tested electrical wiring specification for the wearable ESP32 LED controllers powering our 7-runner family fleet for the Walt Disney World 10K.

---

## 1. System Overview & Component BOM

Each runner wears a self-contained, battery-powered lighting system controlling **200 addressable LEDs** (100 front chest pixels + 100 back pixels duplicated in real time):

| Component | Specification | Quantity per Runner | Notes |
| :--- | :--- | :---: | :--- |
| **Microcontroller** | ESP32-WROOM-32D / DevKit V1 (30-pin or 38-pin) | 1 | 240 MHz dual-core, onboard 2.4GHz antenna for ESP-NOW. |
| **Addressable LEDs** | WS2812B 5V "Seed / Pebble" RGBIC fairy light strings | 200 LEDs (2× 100) | Black enameled/insulated 3-conductor wire, ~1" to 2" spacing. |
| **Inline Data Resistor** | 220 Ω to 470 Ω, 1/4W resistor | 1 | Prevents voltage ringing/spikes on GPIO 16 data output. |
| **Tactile Buttons** | Momentary pushbuttons (SPST normally-open) | 2 | **Button 1:** Show Director / Wake<br>**Button 2:** Castle Photo / Sleep |
| **Power Source** | 5V USB portable power bank ($\ge 2.1\text{A}$ output, 5,000–20,000 mAh) | 1 | FastLED firmware limited to **5V, 2000mA (2.0A)** max. |
| **Power Cable** | Heavy-gauge USB-A to stripped 2-wire cable (or USB-C) | 1 | 20 AWG or 22 AWG power leads for minimal voltage drop. |
| **Connectors** | 3-pin JST-SM (Data, 5V, GND) or quick-disconnect terminals | 1–2 sets | Allows disconnecting the shirt from the electronics pouch. |

---

## 2. Complete ESP32 Pinout Assignment Table

```
                         ESP32 DevKit V1 (30-pin)
                              ┌─────────┐
                        3V3 ──┤         ├── VIN  <── +5V (From Power Bank)
                        GND ──┤         ├── GND  <── Common GND (Battery + LEDs + Buttons)
         (Show/Wake) GPIO 4 ──┤         ├── GPIO 13
                     GPIO 0 ──┤         ├── GPIO 12
                     GPIO 2 ──┤         ├── GPIO 14
                    GPIO 15 ──┤         ├── GPIO 27
                    GPIO 18 ──┤         ├── GPIO 26
                    GPIO 19 ──┤         ├── GPIO 25
                    GPIO 21 ──┤         ├── GPIO 33 ──> (Photo/Sleep) Button 2
                    GPIO 22 ──┤         ├── GPIO 32
                    GPIO 23 ──┤         ├── GPIO 35
                              └─────────┘
                                  │
                                GPIO 16 (Pin 8 right on 30-pin DevKit)
                                  │
                               [220Ω - 470Ω Resistor]
                                  │
                                  ▼
                            LED Data-In (DI)
```

| ESP32 Pin | Function | Wiring Connection | Electrical Configuration |
| :---: | :--- | :--- | :--- |
| **GPIO 16** | **LED Data Output** | In series with **220 Ω to 470 Ω resistor** $\rightarrow$ First LED Data-In (`DIN` / `DI`). | High-speed digital RMT / SPI output (FastLED driver). |
| **GPIO 4** | **Button 1 (Show Director / Wake)** | One pin to **GPIO 4**, other pin to **GND**. | Software `INPUT_PULLUP`. Reads `LOW` when pressed. |
| **GPIO 33** | **Button 2 (Castle Photo / Sleep)** | One pin to **GPIO 33**, other pin to **GND**. | Software `INPUT_PULLUP`. Reads `LOW` when pressed. |
| **GPIO 0** | **Onboard BOOT Button** | Onboard button on ESP32 DevKit (bench fallback). | Software `INPUT_PULLUP`. Operates in parallel with Button 1. |
| **GPIO 2** | **Status Indicator** | Built-in onboard blue LED. | Output: Pulses during show triggers, boot, and config. |
| **VIN / 5V** | **Primary DC Power Input** | +5V Red wire from USB Power Bank. | Powers ESP32 internal 3.3V LDO regulator and LEDs. |
| **GND** | **System Common Ground** | Connected together: ESP32 GND, Power Bank GND, LED GND, and both Button GNDs. | **Mandatory:** All components MUST share a common ground! |

---

## 3. System Electrical Schematic

```
               ┌────────────────────────────────────────────────────────┐
               │              PORTABLE USB POWER BANK                   │
               │                  (+5V DC, >= 2.1A)                     │
               └───────────────────┬────────────────┬───────────────────┘
                                   │ +5V (RED)      │ GND (BLACK)
                                   │                │
            ┌──────────────────────┴───────┐        │
            │                              │        │
            ▼                              ▼        │
    ┌──────────────┐              ┌───────────────┐ │
    │ ESP32 DevKit │              │  200-LED STRIP│ │
    │              │              │  POWER RAILS  │ │
    │   VIN / 5V ◄─┼──────────────┤ +5V           │ │
    │              │              │               │ │
    │        GND ◄─┼──────────────┼─ GND ◄────────┴─┼────────────────────────┐
    │              │              │               │                          │
    │    GPIO 16 ──┼─[220Ω-470Ω]─►│ DATA-IN (DI)  │                          │
    │              │              └───────────────┘                          │
    │              │                                                         │
    │     GPIO 4 ──┼───────┐                                                 │
    │ (Button 1)   │       │                                                 │
    │              │    ┌──┴──┐  Momentary Pushbutton                        │
    │              │    │ O O │  (Show Director / Wake)                      │
    │              │    └──┬──┘                                              │
    │              │       └─────────────────────────────────────────────────┤
    │              │                                                         │
    │    GPIO 33 ──┼───────┐                                                 │
    │ (Button 2)   │       │                                                 │
    │              │    ┌──┴──┐  Momentary Pushbutton                        │
    │              │    │ O O │  (Castle Photo / Sleep)                      │
    │              │    └──┬──┘                                              │
    │              │       └─────────────────────────────────────────────────┘
    └──────────────┘
```

---

## 4. 4-Pin Tactile Pushbutton Orientation Guide (Preventing Stuck Boots!)

> [!CAUTION]
> **Common Assembly Mistake:** Standard 6×6mm breadboard pushbuttons have **4 pins**, but only **2 electrical terminals**. The opposite pins along each wide side are permanently connected internally.

```
       CORRECT WIRING (Diagonal or True Opposites):
       
              Pin 1-A ┌──────┐ Pin 1-B  (Internally connected!)
                      │  ●   │
              Pin 2-A └──────┘ Pin 2-B  (Internally connected!)
              
       ✔ WIRE TO: Pin 1-A (GPIO) and Pin 2-A (GND)  <-- Switches when pressed!
       ❌ DO NOT WIRE TO: Pin 1-A and Pin 1-B       <-- Permanent short to GND!
```

* **The Problem:** If you wire across the internally shorted pair (e.g. Pin 1-A to GPIO and Pin 1-B to GND), the pin is held `LOW` permanently from the microsecond power is connected!
* **Firmware Protection Built-In:** The firmware contains a startup safety guard (`b1Armed` / `b2Armed`). If a pin is shorted to GND at boot, the firmware logs a warning and disables the hold timer rather than locking the costume in config mode.
* **Best Practice:** Use a multimeter in continuity mode (beep test) to verify that your two leads only beep when the button is physically clicked down! Clip or bend inward the two unused legs to prevent accidental shorts.

---

## 5. 200-LED Front & Back Topology & Daisy-Chaining

All firmware builds duplicate the front 100 chest LEDs to the back 100 LEDs in real time so the runner is illuminated from 360° along the dark Disney course:

```
  ESP32 GPIO 16 ──► [220Ω Resistor]
                          │
                          ▼
            ┌───────────────────────────┐
            │   FRONT CHEST STRAND      │
            │   LED 000 ────────► LED 099 │
            └─────────────┬─────────────┘
                          │ Data Out of LED 099
                          ▼
            ┌───────────────────────────┐
            │    BACK SHIRT STRAND      │
            │   LED 100 ────────► LED 199 │
            └───────────────────────────┘
```

### Power Injection Guidelines:
- **Voltage Drop:** Seed/pebble fairy light wire has thin conductors. Powering 200 LEDs from a single end can cause the last 30–50 LEDs to look slightly dim or reddish during white peaks.
- **T-Tap Power Bus (Recommended):** Run the +5V and GND wires in parallel directly from the battery harness to **BOTH** the start of the front strip (LED 0) and the start of the back strip (LED 100). The data line remains continuous in series (GPIO 16 $\rightarrow$ LED 0..99 $\rightarrow$ LED 100..199).

---

## 6. Bench Power Isolation Rules (Mandatory Computer Safety!)

> [!IMPORTANT]
> When uploading code or monitoring serial output via USB-C from a laptop or desktop computer:
> 1. **DISCONNECT THE BATTERY PACK:** Never plug a portable power bank into the VIN/5V rail while the ESP32 is also plugged into a computer via USB cable.
> 2. **Current Limiting:** Computer USB ports typically supply 500mA to 900mA. The ESP32 and a single test strand of LEDs will run fine for testing, but do not set full-white bursts on computer USB.
> 3. **Race Morning:** Plug only the 5V portable power bank into the costume harness. The ESP32 boots autonomously in ~1.5 seconds directly into Corral Standby Mode.

---

## 7. FastLED Power Budget & Battery Life Verification

The firmware enforces FastLED hardware power capping:
```cpp
FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000); // 5V, 2.0A max limit
```

* **Quiescent Draw:** ESP32 radio active + 200 LED sleep twinkle = **~120 mA** (~0.6W).
* **Parade Baseline Draw:** Animated float programs average **~620–780 mA** (~3.5W).
* **Peak Show Draw:** 30s synchronized fleet show peaks at **~1,100–1,200 mA** (~6.0W).
* **Battery Endurance (10,000 mAh / 37 Wh Power Bank):**
  - **Delivered 5V Capacity:** ~7,000 mAh (accounting for 70% boost conversion efficiency).
  - **90-minute Corral Sleep:** $1.5\text{ hr} \times 120\text{ mA} = 180\text{ mAh}$.
  - **90-minute 10K Race Run:** $1.5\text{ hr} \times 750\text{ mA} = 1,125\text{ mAh}$.
  - **Total Consumed:** ~1,305 mAh out of 7,000 mAh available (**> 80% battery remaining at the finish line!**).

---

## 8. Universal 100mm × 100mm 6×6 Modular Panel Wiring & JST-PH Interconnects

When utilizing the modular FR-4 PCB quadrant system (`scripts/generate_universal_6x6_pcb.py`), 4 identical 36-LED panels ($100\text{ mm} \times 100\text{ mm}$) tile into a $2 \times 2$ matrix ($202\text{ mm} \times 202\text{ mm}$ with $2.0\text{ mm}$ felt living hinge gap) across the chest:

```
  ESP32 GPIO 16 ──► [220Ω Resistor]
                          │
                          ▼
            ┌───────────────────────────┐   Diagonal 3-Pin JST Cable (50mm)   ┌───────────────────────────┐
            │   QUADRANT 1 (Top-Left)   │ ══════════════════════════════════► │  QUADRANT 2 (Top-Right)   │
            │   LED 001 ──► LED 036     │  (From J_OUT_R at y=33 to           │  LED 037 ──► LED 072     │
            │   [J_OUT_L]     [J_OUT_R] │   J_IN_L at y=67: span = 40.5mm)    │  [J_IN_L]       [J_OUT_B] │
            └───────────────────────────┘                                     └─────────────┬─────────────┘
                                                                                            │ Diagonal 50mm JST
                                                                                            │ (From J_OUT_B x=37 to
                                                                                            │  J_IN_T x=62.5: 33.7mm)
                                                                                            ▼
            ┌───────────────────────────┐   Diagonal 3-Pin JST Cable (50mm)   ┌───────────────────────────┐
            │  QUADRANT 4 (Bottom-Left) │ ◄══════════════════════════════════ │ QUADRANT 3 (Bottom-Right) │
            │  LED 109 ──► LED 144     │  (From J_OUT_L at y=33 to           │ LED 073 ──► LED 108      │
            │   [J_IN_L]       [J_IN_R] │   J_IN_R at y=67: span = 40.5mm)    │ [J_IN_T]       [J_OUT_L] │
            └─────────────┬─────────────┘                                     └───────────────────────────┘
                          │ Data Out of LED 144 (J_OUT_B)
                          ▼
              (To Back LED Strand: LED 145..288)
```

### 4-Edge Universal JST-PH 2.0mm Port Architecture (Diagonal 50mm Jumpers):
To allow total routing freedom in any board orientation or configuration, each quadrant PCB is equipped with **8 JST-PH 2.0mm 3-pin SMT horizontal headers** (`C3029441`) and parallel 2.54mm direct-wire solder pads, set back $10.0\text{ mm}$ from all board edges into wide-open inter-pixel valleys for 100% zero component overlap:
- **Left Edge ($x = 10.0\text{ mm}$):** `J_OUT_L` at $y = 33.0\text{ mm}$ (DOUT) and `J_IN_L` at $y = 67.0\text{ mm}$ (DIN)
- **Right Edge ($x = 90.0\text{ mm}$):** `J_OUT_R` at $y = 33.0\text{ mm}$ (DOUT) and `J_IN_R` at $y = 67.0\text{ mm}$ (DIN)
- **Top Edge ($y = 10.0\text{ mm}$):** `J_OUT_T` at $x = 28.5\text{ mm}$ (DOUT) and `J_IN_T` at $x = 62.5\text{ mm}$ (DIN)
- **Bottom Edge ($y = 90.0\text{ mm}$):** `J_OUT_B` at $x = 37.0\text{ mm}$ (DOUT) and `J_IN_B` at $x = 71.0\text{ mm}$ (DIN)

All four DIN ports are internally bused to Pixel 1 DIN; all four DOUT ports are internally bused to Pixel 36 DOUT.

### Uniform 50mm Cable Fit Across All Seams:
* **Quad 1 $\rightarrow$ Quad 2:** Spans from Quad 1 `J_OUT_R` $(90.0, 33.0)$ to Quad 2 `J_IN_L` $(112.0, 67.0)$ across the $2.0\text{ mm}$ seam. Center-to-center span is **$40.50\text{ mm}$**. Wire span between plug exits is $\sim 35.0\text{ mm}$, leaving only **$3.0\text{ mm}$ of slack**! The $50\text{ mm}$ cable lays completely flat on the PCB ($\le 5\text{ mm}$ height, flush with the connector housing).
* **Quad 2 $\rightarrow$ Quad 3:** Spans from Quad 2 `J_OUT_B` $(139.0, 90.0)$ to Quad 3 `J_IN_T` $(164.5, 112.0)$ across the $2.0\text{ mm}$ seam. Center-to-center span is **$33.68\text{ mm}$**. Wire span is $\sim 28.0\text{ mm}$, fitting the $50\text{ mm}$ cable with a gentle low-profile curve.
* **Quad 3 $\rightarrow$ Quad 4:** Spans from Quad 3 `J_OUT_L` $(112.0, 135.0)$ to Quad 4 `J_IN_R` $(90.0, 169.0)$ across the $2.0\text{ mm}$ seam. Center-to-center span is **$40.50\text{ mm}$**. Fits identically flat!

### Straight 3-Wire Pinout (Zero Wire Twisting / Crossing):
The physical pin order is mirrored so that off-the-shelf straight 3-conductor ribbon patch cables plug directly across boards without crossing or twisting wires:
* **Left & Right Edges (Vertical headers):**
  - Pin 1 (Top, $y - 2.0\text{ mm}$): `+5V`
  - Pin 2 (Middle, $y$): `DAT` (`DIN` or `DOUT`)
  - Pin 3 (Bottom, $y + 2.0\text{ mm}$): `GND`
* **Top & Bottom Edges (Horizontal headers):**
  - Pin 1 (Left, $x - 2.0\text{ mm}$): `+5V`
  - Pin 2 (Middle, $x$): `DAT` (`DIN` or `DOUT`)
  - Pin 3 (Right, $x + 2.0\text{ mm}$): `GND`

### Silkscreen & Mounting Features:
- **Silkscreen Labels:** Every connector clearly displays its role (`[IN]` or `[OUT]`) and pin functions (`+5V`, `DAT`, `GND`) etched into the Top Silkscreen (`.GTO`) layer.
- **On-Board LED Numbering:** Numbers `1` through `36` are printed on the PCB surface ($1.4\text{ mm}$ above each LED package) so they remain fully visible after SMD assembly.
- **Dark, Clean LED Faces:** KiCad footprint reference designators are set to `hide`, eliminating pink component labels on the LED lenses.
- **Mounting & Sewing:**
  - 4× Corner M3 Screw Holes (`H1`–`H4`): $\varnothing 3.2\text{ mm}$ non-plated through-holes at $(4.0, 3.5)$, $(96.0, 3.5)$, $(4.0, 96.5)$, $(96.0, 96.5)$.
  - 4× Sewing Eyelets (`S1`–`S4`): $\varnothing 2.0\text{ mm}$ plated through-holes paired $6.0\text{ mm}$ from corners for button-style needle/thread garment attachment.

### Direct-Solder Pad Fallback:
Directly behind every JST connector, standard $2.54\text{ mm}$ pitch through-hole pads labeled `+5V`, `DAT`, and `GND` are provided for instant workshop soldering with flexible 24/26 AWG silicone wire if pre-crimped JST patch cables are unavailable.

---

## 8.1 Bottom-Mounted Connector Variant: 100% Flush Front Face & Symmetrical 22mm Straight Spans

For applications where the front face must press completely flush against fabric, diffusion layers, or 3D-printed faceplates without any gap, tenting, or optical light bleed, a dedicated **Bottom-Mounted Variant** is provided in `pcb/bottom_connectors/` (generated via `scripts/generate_universal_6x6_bottom_pcb.py`).

### Key Differences & Advantages:
1. **100% Flush Front Face:**
   - The front layer (`F.Cu`) contains **only** the 36 WS2812B-2020 LEDs ($0.9\text{ mm}$ height) and 36 0402 bypass capacitors ($0.5\text{ mm}$ height).
   - Zero connectors or wire bundles protrude from the front. Fabric shirts, acrylic diffuser panels, or 3D-printed front faceplates rest directly on the LED lenses with **0.0 mm gap**, eliminating light bleed and fabric bulges.
2. **Rear-Mounted JST-PH Connectors (`B.Cu`):**
   - All 8 JST-PH 2.0mm horizontal connectors (`C3029441`) are mounted on the bottom side of the PCB, facing outwards toward board edges.
   - Solder pads, silkscreen labels (`[IN]`, `[OUT]`, `+5V`, `DAT`, `GND`), and fallback solder eyelets reside on the rear layer (`B.Cu` / `B.Silk`).
3. **Symmetrical 22.0mm Straight Spans (All 4 Directions):**
   - Because the bottom side has no LED packages to avoid, connector ports on all 4 edges are placed symmetrically at coordinates **$33.0\text{ mm}$ and $67.0\text{ mm}$**:
     - Left Edge ($x = 10.0\text{ mm}$): `J_OUT_L` ($y = 33.0\text{ mm}$) and `J_IN_L` ($y = 67.0\text{ mm}$).
     - Right Edge ($x = 90.0\text{ mm}$): `J_OUT_R` ($y = 33.0\text{ mm}$) and `J_IN_R` ($y = 67.0\text{ mm}$).
     - Top Edge ($y = 10.0\text{ mm}$): `J_IN_T` ($x = 33.0\text{ mm}$) and `J_OUT_T` ($x = 67.0\text{ mm}$).
     - Bottom Edge ($y = 90.0\text{ mm}$): `J_IN_B` ($x = 33.0\text{ mm}$) and `J_OUT_B` ($x = 67.0\text{ mm}$).
   - Across any $2.0\text{ mm}$ board seam, adjacent connectors face each other **directly in a straight line**:
     $$\text{Span} = (100.0 - 90.0) + 2.0\text{ mm (seam)} + 10.0 = \mathbf{22.0\text{ mm}}$$
   - Standard $50\text{ mm}$ pre-crimped JST-PH patch cables plug straight across with a relaxed, low-profile rear wire loop ($\le 8\text{ mm}$ loop height on the back side), keeping the entire front completely flat.
4. **JLCPCB Double-Sided PCBA Setup:**
   - Single-sided top variant uses JLCPCB "Economic PCBA" (base setup $\approx \$10.00$).
   - Double-sided bottom variant requires JLCPCB "Standard PCBA" (two SMT stencils and two reflow passes, base setup $\approx \$70.00$).
   - The flat $+\$60.00$ setup fee adds only **$\approx +\$0.80$ per board** across a full 75-board fleet order.
5. **Turnkey Deliverables Target (`pcb/bottom_connectors/`):**
   - KiCad PCB: `universal_6x6_bottom_100mm.kicad_pcb`
   - Production Gerbers: `universal_6x6_bottom_100mm_gerbers.zip` (includes `.GBP` bottom paste and `.GBO` bottom silkscreen)
   - JLCPCB BOM: `universal_6x6_bottom_100mm_bom.csv`
   - JLCPCB CPL: `universal_6x6_bottom_100mm_cpl.csv` (properly categorized with 72 Top components and 8 Bottom components)
   - Interactive Dual-View Web Inspector: `universal_6x6_bottom_preview.html` (with Front flush view vs. Rear wiring view toggle)

