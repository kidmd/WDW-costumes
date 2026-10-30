# Main Street Electrical Parade - Synchronized LED Costumes (WDW 10K)

This project powers synchronized, addressable LED lighting across **7 runner costumes** inspired by Disney's **Main Street Electrical Parade** for the Walt Disney World 10K.

Worn by our **7-member family running team** (2 brothers, 1 sister, 1 brother-in-law, and 3 sisters-in-law) and engineered with love by the **3 brothers** (2 running, 1 supporting behind the scenes).

---

## The Concept

Each runner wears a matte black technical running shirt outlined with glow-in-the-dark paint and illuminated by individually addressable **WS2812B "Seed" / Pebble LEDs** to replicate the vintage incandescent bulbs of the parade floats.

An **ESP32** microcontroller on each runner coordinates lighting patterns wirelessly in real time using **ESP-NOW** (connectionless peer-to-peer 2.4 GHz radio), requiring **no Wi-Fi router or cellular service**.

### The 7 Floats Roster

1. **The Train (Casey Jr.):** Warm white chugging locomotive headlight & steam pulses (parade leader pulling the Title Drum).
2. **The Title Drum:** Golden chasing marquee border, "Disney" electric text accent.
3. **The Turtle:** Whimsical spinning shell spirals, blinking amber eyes, and teal/green shell pattern.
4. **The Snail:** Multi-color rotating rainbow spiral shell wheels and neon antennae glow.
5. **The Pirate Ship:** Billowing crimson sails, antique gold masts & decks, and emerald ocean waves.
6. **Pete's Dragon (Elliott):** Chartreuse/green body scales with orange/red fire breathing effect.
7. **To Honor America (Flag & Eagle):** Patriotic red, white, and blue finale fireworks shimmer with majestic illuminated eagle.

---

## Hardware Specifications

* **Microcontrollers:** ESP32 (e.g. ESP32-WROOM-32D or Seeed XIAO ESP32)
* **LED Strands:** 200 WS2812B / WS2811 Addressable 5V Seed/Pebble Pixels (100 front + 100 back duplicated, black wire, ~1" to 2" spacing)
* **Data Resistor:** 220 Ω to 470 Ω inline on the data line between GPIO 16 and LED Data-In
* **Power Source:** 5V USB portable power bank (5,000–20,000 mAh rating, FastLED hardware limited to 2000 mA / 2.0A) per runner with built-in simulator Battery Life & Power Budget Calculator
* **Costume Simulation:** Visual browser-based layout engine (`python simulator.py` @ `localhost:8000`) with built-in presets (Pete's Dragon, The Pirate Ship, Casey Jr., Title Drum, Turtle, Snail, Eagle), multi-layer Cricut Heat Transfer Vinyl (HTV) cut file exporter suite (All-in-One master SVG, color-mat-by-color-mat SVGs, and 6×3mm tangent pill cutouts with 4-corner heat press registration marks), Universal Undo / Redo engine (`Ctrl+Z` / `Ctrl+Y`) with 50-step snapshot history and floating toolbar buttons, 7-Shirt Fleet Show Creator Studio featuring a 19-block choreography palette (traveling waves, dual collision shockwaves, butterfly ripples, fairy dust waterfalls, fleet pulses, wig-wags, sparkle storms, baton chases, and grand finales), interactive NLE-grade visual timeline block editor (drag-to-stretch, rolling trim, and drag-and-drop reordering), Animation Group Spatial Suite & Pre-Built Shape Stamp Library (parametric Circles/Wheels, Arches, Waves, Stars/Sparkles, Lines/Rulers, and Fireworks Starbursts with aspect-ratio correction, interactive click-to-place positioning, Cross-Shirt Clipboard, Rotate 90°, Flip H/V, Scale LED Spacing while maintaining exact shape, and auto-rearranging remaining unassigned LEDs), multi-float live Wi-Fi UDP streaming (`Opcode 0x02`), pre-race Corral Roll Call & ESP-NOW Fleet Radar (instant identification strobe, 4s rapid attendance wave, signal RSSI, battery voltage, and lineup readiness), race-day battery life calculator with 7-float power breakdown, double-tap 4-second rapid attendance wave, 300ms debounced one-shot trigger and early stop, "Snap to 30.0s" sequence normalization, JSON show persistence, 1-click & double-click Single View editing from fleet cards, real 700-LED mini-shirt visualizer, multi-mode wireless sync (ESP-NOW Wave, Free-Run, Show Sequence), full-graphic LED re-distribution (maintaining strictly 100 LEDs per shirt), and authentic runDisney 10K Race Bib (#1952) with Chip & Dale and BibBoards fastener clearance.
* **3D-Printable Flexible TPU Armor Plates & Protective Rear Lids (5-Color Multi-Material & Single STL):** High-speed parametric fabrication pipeline (`scripts/compile_clean_tpu_panel.py`) compiling wearable 9.0mm deep-chassis armor trays and matching **2.0mm protective rear cover lids** (`tpu_panel_{front|back}_lid.stl`). Features **5-Color Multi-Material FDM printing** (for Bambu Lab AMS / Snapmaker Dual) with a monolithic black structural chassis (`chassis_black.stl`), 4 zero-overlap jigsaw front color inlays, 3x3mm / Ø 3.4mm through-aperture windows for LEDs, and a **14-point M2 perimeter screw fastening system** (with dedicated extremity clamping at jaw, ears, tail tip, flank, and heel corners) with 1.2mm stepped alignment ridges. Includes 1-click **Bambu 3MF** and **5-Color ZIP bundles** (packaging tray, inlays, and rear lid), selectable plate sizing (Small ~6.5", Medium ~8.0", Large capped to $\le 245.0\text{ mm}$ for $256\times 256\text{ mm}$ build plates), selectable LED counts (50, 75, 100 LEDs), and an interactive 3D WebGL inspector (`#tpuPreviewModal` & `3d_panels/tpu_panel_preview.html`) with live Tray vs Rear Lid 3D inspection.
* **Universal 100mm × 100mm 6×6 LED Matrix Panels (Turnkey JLCPCB SMT & Felt Pocket):** Cost-optimized modular FR-4 PCB tile system. 4 identical 36-LED tiles cluster into a 144-LED chest array ($202\text{ mm} \times 202\text{ mm}$) featuring an authentic staggered brick layout with calibrated $17.0\text{ mm}$ pitch, making the 4-board cluster 100% optically seamless across the $2.0\text{ mm}$ felt living hinge gap. Available in two production variants:
  - **Front-Mounted Variant (`pcb/`):** 8 horizontal JST-PH 2.0mm ports set back $10.0\text{ mm}$ into inter-pixel valleys with diagonal $50\text{ mm}$ cable routing ($\le 5\text{ mm}$ height profile). Single-sided SMT using JLCPCB "Economic PCBA".
  - **Bottom-Mounted Variant (`pcb/bottom_connectors/`):** 100% flush front face (only 0.9mm LEDs and 0.5mm 0402 caps) for direct contact against fabric or 3D-printed faceplates with **0.0 mm gap and zero light bleed**. All 8 JST-PH headers are on the rear layer (`B.Cu`), featuring symmetrical **$22.0\text{ mm}$ straight-line spans** in all 4 directions for $50\text{ mm}$ pre-crimped JST cables. Requires JLCPCB double-sided "Standard PCBA" ($+\$0.80$ per board for a 75-board fleet order).
  - Both variants include 4× corner M3 screw holes, 4× dedicated fabric sewing eyelets, soldermask LED numbering (`1`..`36`), hidden component references for clean lenses, turnkey RS-274X Gerbers, JLCPCB BOM/CPL files, and interactive dual-view web inspectors (`universal_6x6_preview.html` and `universal_6x6_bottom_preview.html`).
* **Monolithic 200mm × 200mm LED Panels (Zero-Wire Single-Sided SMT Displays):** Large single-piece $200.0\text{ mm} \times 200.0\text{ mm}$ ($7.87'' \times 7.87''$) boards featuring 100% internal etched copper wiring (zero inter-tile jumper cables) and pure single-sided SMT assembly (LEDs and Caps on Top layer only, qualifying for JLCPCB **Economic PCBA** at $\sim \$15.00$ setup fee, saving $\$55.00$ per batch). Equipped with $2.54\text{ mm}$ pitch plated through-hole solder pins for IN and OUT (solderable from Front or Back) and dual S-curve wire strain-relief anchor holes. Available in two density options:
  - **144-LED Model (`pcb/monolithic_200mm_144/`):** 12×12 staggered brick matrix ($15.5\text{ mm} \times 16.0\text{ mm}$ pitch). Complete with RS-274X Gerbers, BOM, CPL, KiCad PCB, and interactive HTML preview. Fleet cost for 8 suits (18 boards): **$\approx \$220.72$ ($\$27.59$ per runner for Front + Back)**.
  - **288-LED Double-Density Model (`pcb/monolithic_200mm_288/`):** Exactly twice as many LEDs ($144 \times 2 = 288$ LEDs) in an 18×16 isotropic offset lattice ($11.6\text{ mm} \times 10.6\text{ mm}$ pitch). High-definition "Retina" resolution for intricate parade graphics. FastLED hardware power limited to 2.0A. Complete with RS-274X Gerbers, BOM, CPL, KiCad PCB, and interactive HTML preview. Fleet cost for 8 suits (18 boards): **$\approx \$368.45$ ($\$46.06$ per runner for Front + Back)**.
* **3D-Printable PLA PCB Test Mockups (`3d_panels/mockups/`):** Physics-calibrated physical test "mules" to evaluate chest curvature, thickness, weight, and bounce on a running shirt before ordering from JLCPCB. Using the **2.5mm Equivalence Rule**, printing at 100% solid infill matches both the real $2.5\text{ mm}$ board+LED envelope AND the exact weight (**$123.7\text{ grams}$ PLA vs. $126.5\text{ grams}$ real PCB — a 97.8% match!**). Includes `mockup_monolithic_200x200.stl`, `mockup_modular_100x100.stl`, and an interactive 3D WebGL preview (`mockups_preview.html`).
* **Pete's Dragon 200mm × 200mm Optical Backlighting Test Panels (`3d_panels/backlight_test/`):** Flat multi-color test panels designed to evaluate filament translucency and rear LED backlighting diffusion across 4 calibrated thicknesses (**1.00 mm, 0.80 mm, 0.60 mm, and 0.48 mm**). Features a pure flat $200.0\text{ mm} \times 200.0\text{ mm}$ black chassis (all LED holes, trenches, walls, eyelets, and screw holes removed), with Pete's Dragon ($180.0\text{ mm} \times 163.2\text{ mm}$) centered inside a $180\text{ mm}$ square. All artwork colors (Green, Magenta, Yellow, White) extend 100% through the full Z thickness for optical transmission. Includes native multi-material `.3mf` files (Bambu Studio / OrcaSlicer / Snapmaker Luban), individual color STLs, parametric OpenSCAD script, and an interactive 3D WebGL preview (`backlight_test_preview.html`).
* **BTF-LIGHTING 16×16 (256-Pixel) Flexible FPCB Matrix (Default Standard Architecture):** The primary costume standard across the simulator and firmware. Features a commercial $160.0\text{ mm} \times 160.0\text{ mm}$ ($10.0\text{ mm}$ pitch) WS2812B ECO 256-LED flexible matrix mounted behind a **$176.0\text{ mm} \times 176.0\text{ mm}$ flat square 3D-printed plate** ($8.0\text{ mm}$ border, soft 6.0mm anti-snag rounded corners, and 16 perimeter $\varnothing 2.8\text{ mm}$ shirt-stitching holes). Evenly distributes **~50 Windowed LEDs** ($5.4\text{ mm} \times 5.4\text{ mm}$ through-hole apertures) and **~25 Backlighting LEDs** (diffused subsurface glow through thin colored PLA/TPU at 50% brightness) via Farthest-Point Sampling while keeping the remaining **~181 LEDs Dark** (~1.35A max draw @ 5V). Features a **$0.40\text{ mm}$ Clear Diffuser Backing Layer** default (2 solid layers @ $0.20\text{ mm}$ cross-ply), selectable faceplate thickness (`0.48mm`, `0.60mm ★`, `0.80mm`, `1.00mm`), and automatic 1-click STL + 5-color `.3mf` compilation. Governed by a **Global Hardware Architecture Switcher** (`[ 🔲 16×16 Matrix (Default) ]` | `[ 🧵 Fairy Lights (Legacy) ]`) in the top navigation bar, decluttering the Layout and Deploy tabs (top-header **📁 Upload Artwork** modal, legacy-scoped placement guides, fixed 57% height/100% scale race bib, and Groups-tab-dedicated inspector) while preserving 100% backward compatibility for legacy prototype fairy light rigs.





---

## Wireless Synchronization (ESP-NOW)

* **Protocol:** ESP-NOW broadcast (Destination MAC `FF:FF:FF:FF:FF:FF`).
* **Architecture:**
  * **Float 1 (Primary Master Leader):** Front locomotive broadcasting timing ticks, BPM tempo, master brightness, show triggers, and photo mode.
  * **Float 7 (Co-Leader / Rear Marshal):** Rear anchor with full co-leader authority to command the rear pack independently if runners split.
  * **Floats 2–6 (Followers):** Listen to broadcast packets, lock to master clock, and execute individual autonomous sequences or synchronized routines.
* **Dual Hardware Button Controls (Button 1: GPIO 4 / BOOT GPIO 0, Button 2: GPIO 33):**
  * **Power-Up (Plug USB):** Boots directly into **🌙 Corral Standby Mode** (12% dim midnight starlight twinkle, < 120mA), saving 80%+ battery during the 60–90 min starting wait.
  * **Button 1 — Single Tap (< 600ms):**
    * 👑 *Leader (Float 1 & 7):* When asleep or in Photo Mode, wakes **ENTIRE FLEET** into **Solo Show Mode** (individual float identities). When running awake, launches the **30s Synchronized Fleet Routine** (or toggles/cancels during active routine).
    * 👥 *Follower (Floats 2–6):* When asleep or in Photo Mode, wakes/exits **THAT RUNNER ONLY** into Solo Show Mode. When running awake, **IGNORED** (keeps parade show running without accidental interruption).
  * **Button 1 — Double Tap (< 400ms):**
    * 👑 *Leader:* Triggers **⚡ 4-Second Rapid Attendance Roll Call** wave across all 7 costumes.
    * 👥 *Follower:* Ignored (roll call reserved for Leader).
  * **Button 1 — Long Hold (5s):**
    * Enter **Float ID Configuration Mode** (1 to 7) with a 1s–4s progressive white LED charging meter and permanent NVS flash auto-save. Releasing before 5s cleanly aborts back to baseline without triggering show routines.
  * **Button 2 — Single Tap (< 600ms):**
    * 👑 *Leader:* Toggles **📸 Castle Photo Mode** (solid, steady, non-flickering full graphic background colors) across the **ENTIRE FLEET**.
    * 👥 *Follower:* Toggles **📸 Castle Photo Mode** **LOCALLY** (solid full graphic background colors) for that runner.
  * **Button 2 — Long Hold (3s):**
    * 👑 *Leader:* Drops **ENTIRE FLEET into Corral Standby (Sleep) Mode**. Stays locked in Standby even if held >3s—requiring an explicit click to enter Photo Mode.
    * 👥 *Follower:* Drops **THAT RUNNER ONLY into Corral Standby Mode**. Stays locked in Standby even if held >3s—waiting for physical release so it never accidentally pops into Photo Mode.

---

## ⚡ Quick Start for Family Runners & Crew (No Git Required!)

You don't need Git, Google Antigravity, or any programming tools:
1. **Download:** Click the green **`<> Code`** button above ➔ **`Download ZIP`** (or [Click Here to Download ZIP](https://github.com/kidmd/WDW-costumes/archive/refs/heads/main.zip)).
2. **Extract:** Right-click the `.zip` file and select **Extract All...** to any folder on your computer.
3. **Plug in & Flash:** Connect your ESP32 via USB and double-click **`flash_firmware.bat`** (Windows) or **`flash_firmware.command`** (Mac).
4. See **[`FLASHING_INSTRUCTIONS.md`](FLASHING_INSTRUCTIONS.md)** for complete hardware wiring and float selection instructions.

---

## Project Structure & Documentation

* [`ESP32_WIRING_PLAN.md`](ESP32_WIRING_PLAN.md): **🔌 ESP32 Hardware Wiring Plan & Electrical Specification** — Complete schematics, pinout tables, tactile button wiring, 4-pin orientation guide, 220–470 Ω data resistor, power bus injection, and computer power isolation rules.
* [`RACE_DAY_BUTTON_GUIDE.md`](RACE_DAY_BUTTON_GUIDE.md): **🏃🏰 Race Day Button Field Guide & Controller Cheat Sheet** — Pocket manual with gesture timings, Leader vs Follower matrices, chronological corral countdown playbook, and state flow diagrams.
* [`RACE_DAY_PACKING_CHECKLIST.md`](RACE_DAY_PACKING_CHECKLIST.md): **🏰 Race Day Packing Checklist & Field Manual** — Pre-race hardware checklist, spare ESP32s, battery survival, repair toolkit, weather kit, and countdown timeline for the 7-runner family team.
* [`CRICUT_MASTER_SVG_USER_GUIDE.md`](CRICUT_MASTER_SVG_USER_GUIDE.md): **✂️ Cricut Master SVG User Guide** — Step-by-step instructions for Cricut Design Space, multi-layer HTV cutting, and heat-press registration.
* [`SIMULATOR_QUICKSTART.md`](SIMULATOR_QUICKSTART.md): **⚡ Simulator Quickstart Guide (TL;DR)** — 2-minute cheat sheet for launching the simulator, moving/trimming timeline clips, testing the fleet show, and streaming to LEDs.
* [`SIMULATOR_USER_GUIDE.md`](SIMULATOR_USER_GUIDE.md): **Complete User Guide & Theatrical Lighting Manual** for the browser simulator, multi-layer timeline, and ESP32 hardware flasher.
* [`FLASHING_INSTRUCTIONS.md`](FLASHING_INSTRUCTIONS.md): **⚡ Quick Flashing Guide for Family Runners & Crew** (Double-click 1-click flasher, Web Browser flasher, and Arduino IDE).
* [`CRICUT_ARTWORK_GUIDE.md`](CRICUT_ARTWORK_GUIDE.md): **🎨 Cricut HTV Costume Artwork Guide** (Layered SVG cut files, color mats, heat press settings, and visual catalog).
* [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md): Live project milestones, wiring specifications, and development changelog.
* `start_simulator.bat`: One-click Windows desktop simulator launcher.
* `flash_firmware.bat`: One-click Windows desktop firmware flasher script.
* `flash_firmware.command`: One-click Mac / Linux desktop firmware flasher script.
* `arduino/MSEP_Costume/`: Ready-to-open native Arduino IDE sketch.
* `firmware/`: Pre-compiled ROM binary files (`firmware_float1.bin` through `firmware_float7.bin`, `firmware.bin`, `bootloader.bin`, `partitions.bin`) and Web Serial manifests.
* `src/`: C++ / Arduino firmware source code for ESP32.
* `simulator/`: Web-based visual simulator and theatrical cue director.
* `platformio.ini`: PlatformIO configuration with board targets and library dependencies (FastLED).
