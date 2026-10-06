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
5. **Cinderella's Coach:** Shimmering fairy dust sparkle and midnight pumpkin carriage glow.
6. **Pete's Dragon (Elliott):** Chartreuse/green body scales with orange/red fire breathing effect.
7. **To Honor America (Flag & Eagle):** Patriotic red, white, and blue finale fireworks shimmer with majestic illuminated eagle.

---

## Hardware Specifications

* **Microcontrollers:** ESP32 (e.g. ESP32-WROOM-32D or Seeed XIAO ESP32)
* **LED Strands:** 200 WS2812B / WS2811 Addressable 5V Seed/Pebble Pixels (100 front + 100 back duplicated, black wire, ~1" to 2" spacing)
* **Data Resistor:** 220 Ω to 470 Ω inline on the data line between GPIO 16 and LED Data-In
* **Power Source:** 5V USB portable power bank (5,000–20,000 mAh rating, FastLED hardware limited to 2000 mA / 2.0A) per runner with built-in simulator Battery Life & Power Budget Calculator
* **Costume Simulation:** Visual browser-based layout engine (`python simulator.py` @ `localhost:8000`) with built-in presets (Pete's Dragon, Cinderella's Coach, Carriage No Horses, Casey Jr., Title Drum, Turtle, Snail, Eagle), multi-layer Cricut Heat Transfer Vinyl (HTV) cut file exporter suite (All-in-One master SVG, color-mat-by-color-mat SVGs, and 6×3mm tangent pill cutouts with 4-corner heat press registration marks), Universal Undo / Redo engine (`Ctrl+Z` / `Ctrl+Y`) with 50-step snapshot history and floating toolbar buttons, 7-Shirt Fleet Show Creator Studio featuring a 19-block choreography palette (traveling waves, dual collision shockwaves, butterfly ripples, fairy dust waterfalls, fleet pulses, wig-wags, sparkle storms, baton chases, and grand finales), interactive NLE-grade visual timeline block editor (drag-to-stretch, rolling trim, and drag-and-drop reordering), Animation Group Spatial Suite & Pre-Built Shape Stamp Library (parametric Circles/Wheels, Arches, Waves, Stars/Sparkles, Lines/Rulers, and Fireworks Starbursts with aspect-ratio correction, interactive click-to-place positioning, Cross-Shirt Clipboard, Rotate 90°, Flip H/V, Scale LED Spacing while maintaining exact shape, and auto-rearranging remaining unassigned LEDs), multi-float live Wi-Fi UDP streaming (`Opcode 0x02`), pre-race Corral Roll Call & ESP-NOW Fleet Radar (instant identification strobe, 4s rapid attendance wave, signal RSSI, battery voltage, and lineup readiness), race-day battery life calculator with 7-float power breakdown, double-tap 4-second rapid attendance wave, 300ms debounced one-shot trigger and early stop, "Snap to 30.0s" sequence normalization, JSON show persistence, 1-click & double-click Single View editing from fleet cards, real 700-LED mini-shirt visualizer, multi-mode wireless sync (ESP-NOW Wave, Free-Run, Show Sequence), full-graphic LED re-distribution (maintaining strictly 100 LEDs per shirt), and authentic runDisney 10K Race Bib (#1952) with Chip & Dale and BibBoards fastener clearance.
* **3D-Printable Flexible TPU Armor Plates (5-Color Multi-Material & Single STL):** High-speed parametric fabrication pipeline (`scripts/compile_clean_tpu_panel.py`) compiling wearable open-chassis 95A TPU armor trays. Supports **5-Color Multi-Material FDM printing** (for Bambu Lab AMS / Snapmaker Dual) with a monolithic black structural chassis (`chassis_black.stl`) and 4 zero-overlap jigsaw front color inlays (Neon Green body, Magenta spine/hair, Sunny Yellow belly, Bright White eyes/teeth) plus 3×3mm through-aperture windows for LEDs. Includes 1-click **Bambu 3MF** and **5-Color ZIP bundles**, selectable plate sizing (Small ~6.5", Medium ~8.0", Large ~10.0"), selectable LED counts (50, 75, 100 LEDs), and an interactive 3D WebGL inspector (`#tpuPreviewModal` & `3d_panels/tpu_panel_preview.html`) with live 5-color/single-color preview switching.

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
