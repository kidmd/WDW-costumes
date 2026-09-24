# Main Street Electrical Parade (WDW 10K) - LED Control System

## Project Overview
This project coordinates synchronized, addressable LED lighting across **7 runner costumes** styled as the iconic floats of Disney's **Main Street Electrical Parade** for the Walt Disney World 10K.

* **Theme:** Main Street Electrical Parade (7 Floats)
* **GitHub Repository:** [kidmd/WDW-costumes](https://github.com/kidmd/WDW-costumes)
* **Base Shirts:** Black moisture-wicking technical running shirts with glow-in-the-dark graphic outlines
* **Lighting:** 5V WS2812B "Seed / Pebble" RGBIC fairy pixel strings (~1" to 2" spacing for discrete light bulb look)
* **Controller:** ESP32 Microcontrollers (1 per runner)
* **Wireless Protocol:** ESP-NOW (connectionless 2.4GHz peer-to-peer broadcast; no router/hotspot needed)
* **Power Source:** 5V USB portable power bank per runner

---

## The 7-Runner Roster & Float Assignments

| Float # | Unit / Float Name | Visual Concept & Accent Lights |
| :---: | :--- | :--- |
| **1** | **The Train (Casey Jr.)** | Warm white chugging headlight, locomotive steam pulses (parade leader pulling the Title Drum) |
| **2** | **The Title Drum** | Golden chasing marquee border, "Disney" electric text accent |
| **3** | **The Turtle** | Whimsical spinning shell spirals, blinking amber eyes, teal/green glow |
| **4** | **The Snail** | Rotating rainbow spiral wheels, neon antennae, vibrant spinning motion |
| **5** | **Cinderella's Coach** | Brilliant fairy dust shimmer, pumpkin coach starlight glow |
| **6** | **Pete's Dragon (Elliott)** | Chartreuse/green scales with orange/red fire breathing effect |
| **7** | **To Honor America (Flag & Eagle)** | Cascading patriotic red/white/blue starbursts & majestic illuminated eagle |

---

## Hardware Architecture & Bench Wiring

### 1. Key Components
- **Microcontrollers:** ESP32 development boards (standard DevKit or Seeed Studio XIAO ESP32)
- **LED Strands:** WS2812B 5V Seed/Pebble pixels (black wire, individual encased nodes)
- **Resistor:** 220 Ω to 470 Ω inline on the data line (between ESP32 GPIO and LED Data-In)
- **Power:** 5V USB Battery Pack (2.1A+ output rating)

### 2. Bench Power Isolation Rules
* **USB-C from Computer:** Plugs into the ESP32 USB-C port for code upload and serial debugging.
* **5V Power Brick / Adapter:** Plugs directly into the breadboard +5V rail powering the LEDs.
* **GND (Common Ground):** ESP32 GND and Power Bank GND are connected together.
* **DO NOT** connect the 5V power bank rail to the ESP32 VIN pin while the USB-C cable is connected to the PC.

---

## Roadmap & Milestones

- [x] **Milestone 1: Bench Setup & Single-Strand Validation**
  - [x] Configure toolchain in Antigravity (PlatformIO Core 6.2.0 installed & verified).
  - [x] Create baseline MSEP animation sketch with FastLED current limiting (`src/main.cpp`).
  - [x] Build and compile firmware successfully with FastLED library.
  - [x] Connect ESP-32D via USB and flash test firmware:
    - **Board 1 MAC:** `B0:CB:D8:C8:49:84`
    - **Board 2 MAC:** `A4:F0:0F:64:33:A0`
  - [x] Bench wire ESP32 with isolated 5V power, common ground, and GPIO 16 (pin 8 on right).
  - [x] Verify discrete bulb appearance, color calibration (RGB order established), and animation playback.

- [x] **Milestone 2: ESP-NOW Wireless Synchronization**
  - [x] Build unified firmware with auto-role detection via MAC address (`src/main.cpp`).
  - [x] Flash Board 1 as **Leader (Float 1 - Title Drum)** [`B0:CB:D8:C8:49:84`].
  - [x] Flash Board 2 as **Follower (Float 2 - Casey Jr.)** [`A4:F0:0F:64:33:A0`].
  - [x] Implement synchronized modes: Marquee Chase, Float Sparkle, Starlight Twinkle, and Traveling Parade Wave.
  - [x] Verify bench latency and wireless lockstep synchronization between both strands (SUCCESS).

- [x] **Milestone 3: Python LED Costume Simulator & Visualizer**
  - [x] Lightweight Python local server with zero external dependencies (`simulator.py`).
  - [x] Interactive Single-Shirt view of Pete's Dragon with metallic green reflective styling on black shirt.
  - [x] 50 interactive addressable LEDs with drag-and-drop repositioning and JSON export.
  - [x] Dynamic lighting engine: Green glow with starlight sparkles, fire-breathing snout pulse, marquee chase.
  - [x] Live sliders: Speed (BPM), Sparkle Frequency, Green Hue, Brightness, Glow size.
  - [x] 7-Shirt Fleet Lineup view with animated synchronized Traveling Wave across all 7 floats.
  - [x] One-click FastLED C++ code generator for immediate copy-pasting into ESP32 firmware.

- [ ] **To-Do (Pending Fairy Lights Arrival): Resume Custom Costume Simulator Testing**
  - [ ] Await delivery of WS2812B 5V "Seed / Pebble" RGBIC fairy pixel strings.
  - [x] Implement Real-Time Live Streaming / Tethering (stream pixel colors over Wi-Fi from `simulator.py` directly to ESP32 for instant live-preview without re-flashing).
  - [ ] Resume custom character costume layout and testing with the Web Simulator (`simulator.py`).
  - [ ] Confirm RGB color order on new fairy light hardware and verify power limits.
  - [ ] Test 100-LED Pete's Dragon scatter pattern with starlight diamond sparkles on wearable fairy lights.

- [ ] **Milestone 4: Parade Animation Sequencing**
  - [ ] Implement classic traveling parade chase (running down the line of 7 floats).
  - [ ] Implement float-specific accent animations (fire flickers, clock chime, sparkles).
  - [ ] Optional: Sync tempo to the *Baroque Hoedown* soundtrack.

- [ ] **Milestone 5: Wearable Construction & Race Prep**
  - [ ] Assemble Y-splitter power cables for race-day battery packs.
  - [ ] Secure seed LEDs to black running shirts (clear nylon tacking / fabric adhesive).
  - [ ] Add quick-disconnect JST connectors between waist belts and shirts.
  - [ ] Sweat-proofing and strain relief testing.

---

## Progress Log

### Entry: Radial 360° Fireworks Starburst Animation, Serpentine Numbering & 100-LED Invariant Generator
* **Date:** 2026-09-24
* **Status:** Operational & Verified in Web Simulator and PlatformIO C++ firmware.
* **Notes:**
  * **4-Phase Pyrotechnic Animation Engine:** Added `fireworks` effect to simulator engine and standalone firmware with center core flash, outward expanding spark trails with decaying ember tails, high-frequency starlight crackles at outer tips, and dark sky resets.
  * **Continuous Serpentine Wiring:** Implemented serpentine spoke numbering (even rays Center $\to$ Tip, odd rays Tip $\to$ Center) to eliminate messy return wires on wearable shirts while auto-compensating in software so all rays expand outward simultaneously.
  * **100-LED Strict Invariant:** Designed cluster generator where placing a firework takes $N_{\text{fw}}$ LEDs from the float pool, preserving exactly 100 LEDs on screen. Included a dedicated "🔄 Re-distribute Remaining LEDs" option to re-scatter remaining non-firework LEDs across the graphic outside the firework cluster.
  * **Customizable Parameters:** UI controls for 4 to 6 Rays, 3 to 5 LEDs per Ray, and adjustable burst radius spread (8% to 22%).
  * **Canvas Numbering Badges:** Enhanced bulb rendering and inspector to display exact ray and step roles (e.g. `R1:1 (CTR)`, `R1:4 (TIP)`).
  * **Firmware & Toolchain Parity:** Added `COSTUME_PATTERN_FIREWORKS` to `include/costume_config.h`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, and `simulator.py`. Compiled and verified with PlatformIO (`pio run` SUCCESS: 14.3% RAM, 59.6% Flash).

### Entry: Multi-Layer Cricut HTV Vector Artwork Suite Created for All 7 Floats
* **Date:** 2026-09-23
* **Status:** Operational & Available in `assets/cricut_svg/`.
* **Notes:**
  * **Cricut & Silhouette Ready:** Designed production-ready, layered vector SVG cut files for all 7 floats (The Train, The Title Drum, The Turtle, The Snail, Cinderella's Coach, Pete's Dragon, and To Honor America Eagle).
  * **Layered Heat Transfer Vinyl (HTV):** Clean multi-mat organization (3 to 4 colors per float) without tiny snagging islands or fragile weeding bottlenecks. Fits athletic moisture-wicking running shirts with SportFlex / EasyWeed Stretch vinyl.
  * **10K Race Bib Clearance:** Calibrated to 7.0"-7.5" wide by 5.2"-5.5" high, fitting between 2" below the neckline and leaving >1" safety margin above the 57% bib line to prevent clamp collisions with 4-corner BibBoards snap fasteners.
  * **LED Anchor Alignment:** Embedded discrete light bulb dots and structural contours into the vector layers for natural physical anchor points when securing the 100 WS2812B seed LEDs.
  * **Documentation & Catalog:** Created interactive visual inspector `assets/cricut_svg/cricut_catalog.html` and full instruction manual `CRICUT_ARTWORK_GUIDE.md` detailing Design Space upload, mat mirroring, 3-5s tack press sequence at 305°F, and LED attachment.

### Entry: Official 7-Float Parade Roster Synchronized Across Documentation & Firmware
* **Date:** 2026-09-23
* **Status:** Synchronized across all docs, Web Simulator, C++ firmware, and Arduino sketches.
* **Notes:**
  * **Updated 7-Float Lineup:** Finalized the official runner costume float roster:
    1. **Float 01:** The Train / Casey Jr. (Leader pulling the drum, Red `#e63946`)
    2. **Float 02:** The Title Drum (Follower, Gold/Amber `#ffb703`)
    3. **Float 03:** The Turtle (Follower, Teal/Green `#2ec4b6`)
    4. **Float 04:** The Snail (Follower, Pink `#ff007f`)
    5. **Float 05:** Cinderella's Coach (Follower, Cyan `#48cae4`)
    6. **Float 06:** Pete's Dragon / Elliott (Follower, Green `#00ff88`)
    7. **Float 07:** To Honor America (Flag & Eagle) (Follower, Patriotic Blue `#3a86ff`)
  * **Code & Firmware Synchrony:** Updated `FLEET_ROSTER` in `simulator/app.js`, `FLEET_ROSTER_INFO` in `src/main.cpp`, and `FLEET_ROSTER_INFO` in `arduino/MSEP_Costume/MSEP_Costume.ino`.
  * **Documentation Alignment:** Synchronized `README.md`, `SIMULATOR_USER_GUIDE.md`, `FLASHING_INSTRUCTIONS.md`, and project artifacts.

### Entry: Yellow runDisney 10K Bib (#1952) with Chip & Dale Mascots & Dynamic Scaling
* **Date:** 2026-09-23
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **runDisney 10K Theme:** Transformed the race bib into an authentic sunshine yellow Tyvek card (`#fef9c3` to `#facc15`), golden trim, red/blue athletic side stripes, "WALT DISNEY WORLD® 10K", and official "CHIP 'N' DALE 10K" ribbon with corral badge and PhotoPass barcode (`DIS-1952-10K`).
  * **Custom Chip & Dale Mascot Vector Graphics:** Rendered high-definition vector illustrations of Chip (chocolate chip nose, single center tooth, red headband) and Dale (signature red nose, messy hair tuft, two separated teeth, blue headband) flanking athletic race number 1952 with golden acorn accents (`🌰`).
  * **BibBoards Corner Fasteners:** Modeled 4-corner snap-and-lock pucks (dark casing, cyan ring, button dome) to provide exact physical clamp clearance on the running shirt.
  * **Height & Scale Sliders:** Added interactive height elevation control (default 57%) and dynamic bib scale slider (60% to 140%, default 100%) in Section 4.
  * **Proportional Chest Graphic Scaling:** Scaled Pete's Dragon, Cinderella's Coach, and Carriage presets to strictly fit the available chest zone above the 57% bib line while preserving 100% of each graphic's original $x / y$ aspect ratio.

### Entry: Dual ESP32 Core Compatibility (v2.x & v3.x+) for Arduino IDE & PlatformIO
* **Date:** 2026-09-24
* **Status:** Implemented & Verified in Arduino Sketch (`MSEP_Costume.ino`) and PlatformIO (`src/main.cpp`).
* **Notes:**
  * **ESP-NOW Breaking Change Resolved:** Addressed breaking API change introduced in ESP32 Arduino Core 3.x (Espressif ESP-IDF 5.x) where `esp_now_recv_cb_t` changed its signature to pass `const esp_now_recv_info_t *` instead of `const uint8_t *mac_addr`.
  * **Dual-Version Compatibility Macro:** Integrated `<esp_arduino_version.h>` and guarded `onDataReceive` using `#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)`. The code now compiles seamlessly out-of-the-box on both legacy Core 2.x (PlatformIO default) and modern Core 3.x+ (latest Arduino IDE Boards Manager).
  * **Firmware Synchronization:** Mirrored updates across `arduino/MSEP_Costume/MSEP_Costume.ino`, `src/main.cpp`, and precompiled `firmware/firmware.bin`.
  * **Repository Rule Added:** Enforced rule 5 in `GEMINI.md` to prevent single-core regressions in future firmware updates.

### Entry: 200-LED Full Costume Firmware (100 Front + 100 Back Duplicated) & Battery Benchmarking
* **Date:** 2026-09-23
* **Status:** Implemented in C++ firmware, simulator backend, and flashing suite.
* **Notes:**
  * **Full Costume Architecture:** Firmware compiles for 200 LEDs: Front 100 LEDs (0–99) render custom artwork and cue sequences, while Back 100 LEDs (100–199) duplicate the front in real time for 360° visibility.
  * **Power Budgeting & Battery Testing:** FastLED current limiting set to 2000 mA (2.0A) for safe operation on standard 5V 2.1A / 2.4A portable USB power banks. Enables real-world battery runtime testing.
  * **Multi-Format Export:** Updated `src/main.cpp`, `include/costume_config.h`, `arduino/MSEP_Costume/`, and `simulator.py` to produce matching 200-LED binaries.

### Entry: Carriage (No Horses) Preset & BOOT Button Visual Mode Confirmations
* **Date:** 2026-09-23
* **Status:** Implemented & Verified on Hardware.
* **Notes:**
  * **Carriage (No Horses) Asset & Preset:** Added dedicated high-res asset (`assets/carriage_nohorses.png`) and preset profile (`presets/carriage_nohorses.json`) with 100 color-matched LEDs to Section 1 dropdown.
  * **Visual Mode Confirmation:** Tapping the onboard BOOT button (< 2.5s) toggles between Autonomous Show and ESP-NOW Fleet Sync, confirmed by 🔵 **2 Cyan Flashes** (Autonomous) or 🟡 **2 Amber Flashes** (Fleet Sync) across all costume LEDs.
  * **Interactive Float ID Selector:** Long hold for 3s enters Float ID config (⚪ 3 White Flashes), visual LED counter in signature float color, tap to cycle 1–7, and auto-saves to NVS flash (`Preferences.h`) with 🟢 4 Green Flashes.

### Entry: Real-Time Wi-Fi Pixel Streaming Implemented (No ROM Flashing Needed)
* **Date:** 2026-09-22
* **Status:** Operational & verified with high-speed UDP pixel streaming.
* **Notes:**
  * **Unified Universal Firmware Architecture:** Combined both systems into a single seamless firmware in `src/main.cpp`. It runs the full ESP-NOW parade fleet loop (Marquee Chase, Float Sparkles, Twinkle, Traveling Wave) by default. When the web simulator sends live stream packets, it temporarily overrides the lights in real time; the moment streaming stops for >2.5s, it smoothly resumes synchronized parade lockstep!
  * **Dual Connection Support:** Connects automatically to Home Wi-Fi (`include/wifi_config.h`), or falls back to an open Access Point (`MSEP-Costume-AP`) if home network is unavailable.
  * **One-Click Wi-Fi Receiver Flasher:** Users can flash the receiver once over USB via the simulator UI (`⚙️` settings dialog), then unplug the USB and power the ESP32 from a 5V/2A wall charger across the room forever while testing designs!
  * **Simulator UI Integration:** Added a "📡 Real-Time Wi-Fi Stream" dock with a live stream toggle button, pulsing connection status indicator, and automated 30 FPS pixel transmission.

### Entry: 100-LED Continuous Physical Wiring Optimization (2-Opt TSP Routing)
* **Date:** 2026-09-22
* **Status:** Implemented & Verified in Web Simulator.
* **Notes:**
  * **Continuous Shortest-Path Renumbering:** Integrated a 2-Opt Traveling Salesperson (TSP) path routing algorithm into `scatterLedsOnGraphic` and as a manual button (`🔌 Optimize Wiring Route`). It preserves the even Poisson/FPS spatial distribution, but renumbers the 100 LEDs sequentially so LED $i+1$ is always immediately adjacent to LED $i$.
  * **Sewing & Construction Ergonomics:** Starts LED 0 at the bottom-left waist/hem (where the battery pack & ESP32 controller plug in), reducing wire jump distances by over 81% (average step ~1.5"-2", exactly matching fairy light spacing) and untangling wire crossovers.
  * **Visual Wiring Trace:** Updated "Show Wiring Trace" and "Show Bulb Numbers" on the simulator canvas to render start/end badges (`0 (START)` in green, `99 (END)` in red) and a clean, untangled path.
  * **Presets Updated:** Both `presets/petes_dragon_100_scatter_color.json` and `presets/petes_dragon.json` renumbered with this optimal physical route.

### Entry: Both ESP32 Boards Flashed with Unified Dual-Mode Firmware
* **Date:** 2026-09-22
* **Status:** 100% Deployed & Verified on Hardware.
* **Notes:**
  * **Board 1 (Leader - Float 1 Title Drum):** Flashed via PlatformIO on COM5; verified MAC `B0:CB:D8:C8:49:84`.
  * **Board 2 (Follower - Float 2 Casey Jr.):** Flashed via PlatformIO on COM5; verified MAC `A4:F0:0F:64:33:A0`.
  * **Unified Dual-Mode Operation:** Both boards now run the synchronized ESP-NOW fleet loop by default (Marquee Chase, Title Drum/Casey Jr. Sparkles, Starlight Twinkle, Traveling Wave across floats). When the Web Simulator transmits UDP packets on port 4210, the boards instantly switch to live pixel rendering; when the stream stops, they automatically resume the ESP-NOW parade loop after 2.5 seconds.
  * **Follower Wave Clock Sync Fix:** Updated Follower Mode 3 (Traveling Wave) to extrapolate the wave head locally from `activeTime` at 60 FPS rather than relying on discrete, jitter-prone 25 Hz over-the-air packets. Both Leader and Follower now sweep with exact, smooth 1.5-second matching durations.

### Entry: Reverted to Pre-Simulator Fleet Sync Firmware (Awaiting Fairy Lights)
* **Date:** 2026-09-15
* **Status:** Milestone 2 fleet synchronization firmware restored & 100% verified in lockstep.
* **Notes:**
  * Reverted `src/main.cpp` back to the baseline Milestone 2 firmware (auto-role ESP-NOW synchronization, 50 LEDs, 4 parade modes: Marquee Chase, Float Sparkle, Starlight Twinkle, and Traveling Wave) with startup brownout bypass.
  * **Power Verification:** Confirmed that Board 1 (Leader) and Board 2 (Follower) are running in 100% wireless lockstep on 5V external power (phone charger / battery pack).
  * **Electrical Finding:** Identified that 12mm WS2811 bullet pixels pull ~30-55mA each (1.0A+ for 50 LEDs), whereas seed/pebble fairy lights pull only ~10-15mA each (~350mA for 50 LEDs). This explains why the laptop USB port handled fairy lights yesterday, but browned out on the heavier 12mm bullet pixels today.
  * Archived custom Pete's Dragon layout, vibrant scatter presets, and simulator flashing engine in the codebase.
  * Paused custom single-costume testing pending arrival of wearable WS2812B fairy lights.

### Entry: Interactive Python LED Simulator Enhanced (Auto-Outline & Preset Persistence)
* **Date:** 2026-09-15
* **Status:** Operational with Auto-Contour boundary tracing & Preset System.
* **Notes:**
  * **Auto-Contour Perimeter Tracing:** Implemented Moore-Neighbor 8-way boundary tracing algorithm with cumulative arc-length parameterization. Automatically redistributes exactly 50 equidistant LEDs around the visible edges of any uploaded graphic (transparent PNGs or high-contrast logos) via the **"✨ Auto-Outline Image (50 LEDs)"** button or upon upload.
  * **Preset Manager:** Added server-side JSON profile saving/loading to `presets/` and browser `localStorage` to save custom LED coordinates, custom graphics, and animation sliders together. Default Pete's Dragon profile saved to `presets/petes_dragon_default.json`.
  * **Authentic Athletic Proportions:** Refactored 7-shirt fleet lineup from stretched vertical shapes to natural $1 : 1.25$ aspect ratio running shirts with runner bib numbers (01–07), running shorts, legs, shoes, and parade asphalt road.
  * Live server confirmed running at `http://localhost:8000`.

### Entry: Milestone 2 Bench Verification Confirmed
* **Date:** 2026-09-14
* **Status:** Wireless sync fully operational.
* **Notes:**
  * Both strands confirmed running in lockstep via ESP-NOW 2.4 GHz radio.
  * Status indicator on Board 2 transitioned to solid blue upon locking to Board 1.
  * Successfully verified the cross-float Traveling Wave effect jumping from Strand 1 to Strand 2.
  * Milestone 2 officially complete!

### Entry: ESP-NOW Wireless Fleet Deployed to Both Boards
* **Date:** 2026-09-14
* **Status:** Milestone 2 firmware deployed.
* **Notes:**
  * Created unified fleet firmware with auto-role detection based on hardware MAC.
  * Board 1 (`B0:CB:D8:C8:49:84`) booted as Leader (Float 1 - Title Drum) broadcasting at 25 Hz.
  * Board 2 (`A4:F0:0F:64:33:A0`) booted as Follower (Float 2 - Casey Jr.) listening on ESP-NOW.
  * Implemented cross-float Traveling Wave sequence.

### Entry: Board 2 Flashed & Milestone 1 Completed
* **Date:** 2026-09-14
* **Status:** 2 Nodes operational with verified pinout & animations.
* **Notes:**
  * Flashed Board 2 successfully via COM5.
  * Retrieved Board 2 MAC address: `A4:F0:0F:64:33:A0`.
  * Identified physical pin mapping on user's ESP32: GPIO 16 is 8th pin down on the right side.
  * Milestone 1 officially complete: 2 independent nodes running MSEP animation suite.
  * Ready for Milestone 2: ESP-NOW wireless synchronization.

### Entry: Board 1 Flashed & Online
* **Date:** 2026-09-14
* **Status:** Hardware connected & verified.
* **Notes:**
  * Installed Silicon Labs CP210x Universal Driver on Windows 11 ARM64.
  * Successfully flashed initial test firmware to Board 1 via COM5.
  * Retrieved Board 1 Wi-Fi MAC address: `B0:CB:D8:C8:49:84`.
  * Board is actively running the 3 MSEP animation loops on GPIO 16.

### Entry: Build Environment & Baseline Firmware
* **Date:** 2026-09-14
* **Status:** Toolchain operational & firmware built.
* **Notes:**
  * Installed PlatformIO Core 6.2.0 and Espressif32 framework.
  * Created `platformio.ini` configured for `esp32dev` and FastLED library.
  * Authored `src/main.cpp` with 3 classic Main Street Electrical Parade sequences (Golden Marquee Chase, Multi-Color Float Sparkle, Starlight Twinkle).
  * Included safe current caps (5V @ 800 mA) and Wi-Fi MAC address reporting on boot.
  * Successfully compiled firmware binary (Flash: 57.4%, RAM: 13.6%).

### Entry: Kickoff & Architecture Definition
* **Date:** 2026-09-14
* **Status:** Initialized project workspace and documentation.

* **Notes:**
  * Created project tracking log [`PROJECT_PROGRESS.md`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/PROJECT_PROGRESS.md).
  * Outlined 7-float roster and ESP-NOW broadcast architecture.
  * Verified resistor options (330 Ω ideal, 220 Ω approved as safe for bench testing; 2.2 kΩ rejected).
  * Established 5V bench power isolation guidelines.
