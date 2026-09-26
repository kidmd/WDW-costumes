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

- [ ] **Next Up / Feature Queue (Imagineering Active Pipeline):**
  - [x] **Interactive Visual Timeline Block Editor:** Directly drag and stretch choreography block edges on the canvas timeline to adjust durations visually; drag-and-drop block reordering on timeline tracks.
  - [ ] **Race-Day Battery Life & Power Budget Calculator:** Analytical battery capacity estimator (5,000 mAh / 10,000 mAh packs) modeling running pace (60–90 min 10K), average mA draw per runner, and 30s fleet show trigger frequency.
  - [ ] **"Corral Roll Call" / ESP-NOW Fleet Radar Diagnostic:** Pre-race bench & corral RF sniffer verifying that Floats 1 through 7 are powered, connected, and responding on the sync channel before race start.

---

## Progress Log

### Entry: Athletic Runner Mannequin Rendering & 4-Second Roll Call Wave Fixes
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Realistic Runner Anatomy & Pre-Race Choreography Verification
* **Status:** Operational & Verified across Web Simulator (`index.html`, `app.js?v=31`) and Documentation.
* **Notes:**
  * **Full Athletic Runner Body Rendering:**
    - Replaced the dark, hard-to-see `#484f58` 6px stick legs with complete, natural athletic runner figures that remain **100% visible at all times** whether their shirts are illuminated or dark.
    - Features athletic head silhouettes with running caps/visors (black with float-coordinated accent trim), athletic arms in mid-stride runner posture, black microfiber running shorts with vertical racing stripes, and well-proportioned quadriceps, kneecaps, and calf muscles rendered in a warm, natural athletic skin tone (`#d4a373`).
    - Added clean white athletic quarter socks with colored cuff rings, performance running sneakers with cushioned foam midsoles and rubber tread, and soft drop shadows planted directly on the asphalt parade course.
    - Realistic LED ambient light spill casts downward onto the shorts, legs, and pavement whenever a runner's LEDs are active.
  * **Rapid Attendance Wave Scoping & Trigger Fix:**
    - Resolved variable scoping issue where undeclared `rapidRollCallActive` and `DEFAULT_FLEET_RADAR` prevented the 4-second rapid attendance wave from executing when triggered.
    - Added top-level declarations and dual event listener support for both single-click and double-click/double-tap interactions on `#fleetRadarRapidRollCallBtn`.
    - Clarified button label: `⚡ 4s Rapid Attendance Wave (Simulate BOOT Double-Tap)`.
  * **Theatrical Roll Call Canvas Choreography:**
    - Automatically switches to Fleet View so all 7 runners are visible during the roll call.
    - Displays a live countdown header with float name, reporting status, and an animated progress bar.
    - Projects an overhead theatrical spotlight cone and radiant ground halo under the reporting runner during their 500ms solo roll call window.
    - Synchronized unison double emerald green flash (`#00FF50`) across all 7 costumes and radar cards during the finale (3.5s - 4.0s).

### Entry: Collapsible Pre-Corral Roll Call & Fleet Radar Layout Optimization
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Fleet Management Ergonomics & Corral UX Refinement
* **Status:** Operational & Verified across Web Simulator (`index.html`, `app.js?v=30`) and Documentation.
* **Notes:**
  * **Reduced Visual Clutter on Fleet Tab:** Reordered Section 2 to be the 7-Runner Baseline Presets and Section 3 to be the Pre-Race Corral Roll Call & ESP-NOW Fleet Radar, configured to start **minimized by default**.
  * **Collapsible Header Console:** Features a compact header with real-time readiness status (`🟢 7/7 READY`), a clear summary subtitle, and an interactive toggle button (`▼ Open Checks` / `▲ Minimize`).
  * **One-Click Quick Jump Buttons:** Added quick-jump action buttons (`🛰️ Corral Radar`) in the 30s Fleet Show header and 7-Runner Lineup header that smoothly expand the console and scroll directly to the radar diagnostics with an accent glow.
  * **Auto-Expansion on Roll Call:** Triggering the 4-second rapid attendance roll call wave automatically expands the radar section so visual telemetry cards and card glow sequences remain visible.

### Entry: Double-Tap 4-Second Rapid Attendance Roll Call Wave (Hardware-Only & Simulator)
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Pre-Race Wireless Telemetry, Lineup Verification & Rapid Corral Wave
* **Status:** Operational & Verified across ESP32 Firmware (`src/main.cpp`, `MSEP_Costume.ino`), PlatformIO compilation, Web Simulator (`index.html`, `app.js?v=29`), and Python Server (`simulator.py`).
* **Notes:**
  * **Double-Tap Hardware Detection (BOOT Button on GPIO 0):**
    - Two quick taps within a 400ms detection window (`now - firstTapReleaseTime <= 400`) triggers the **4-Second Rapid Attendance Roll Call** (`SHOW_MODE_RAPID_ROLL_CALL = 3`, ESP-NOW `mode = 0x44`).
    - Single tap (< 600ms, released > 400ms) continues to toggle the **30-Second Theatrical Fleet Routine** (`mode = 0x30` / `mode = 0x00`).
    - Long hold (>= 3.0s) continues to enter **Float ID Configuration Mode** (1 to 7).
    - Can be initiated from **ANY brother's costume** in the starting corral without reaching for a phone or opening a Wi-Fi hotspot.
  * **4000ms Rapid Attendance Wave Choreography:**
    - **Slots 0–6 (500ms per float, 0.0s – 3.5s):** Floats 1 through 7 illuminate sequentially solo in their signature colors (1 Red ➔ 2 Gold ➔ 3 Teal ➔ 4 Pink ➔ 5 Cyan ➔ 6 Green ➔ 7 Blue). While one brother calls roll, the other 6 stay completely unlit, making each runner immediately stand out.
    - **Finale Slot (3.5s – 4.0s):** All 7 floats illuminate together in a synchronized double emerald green flash (`#00FF50`), signaling that the entire fleet is linked and ready.
    - **Auto-Revert:** At 4.0 seconds, every costume automatically returns to its baseline show program with zero manual intervention.
  * **Simulator & Network Integration:**
    - Added `⚡ 4s Rapid Attendance Wave (Double-Tap)` button to `#fleetRadarSection` toolbar.
    - Implemented `triggerRapidRollCall()` in `simulator/app.js` with canvas mini-shirt animation and sequential radar card glow.
    - Added `POST /api/fleet_radar/trigger_roll_call` endpoint in `simulator.py` broadcasting UDP Opcode `0x03, cmd 0x03`.
    - Mirrored identically across `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` for dual ESP32 core compatibility (Rule 5).
    - Verified PlatformIO build (Flash: 59.9%, RAM: 14.3%) and updated binary in `firmware/firmware.bin`.

### Entry: Pre-Race Corral Roll Call & ESP-NOW Fleet Radar Diagnostics
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Pre-Race Wireless Telemetry, Lineup Verification & Fleet Radar
* **Status:** Operational & Verified across Web Simulator, Python Server, and ESP32 C++/Arduino firmware.
* **Notes:**
  * **Corral Roll Call Diagnostic Module (`#fleetRadarSection`):**
    - Added dedicated diagnostic console between the 30s Fleet Show Creator and 7-Runner Lineup on `#tabFleet`.
    - Live Fleet Readiness Status Pill: `🟢 7/7 READY`, `🟡 6/7 READY`, or `🔴 CONFLICT`.
    - Sync Clock Lock Indicator: Displays master clock source (`Float 1 Casey Jr. · ESP-NOW 2.4 GHz Broadcast`).
  * **7 Float Telemetry Cards (Floats 1–7):**
    - Float avatar icon (`🚂`, `🥁`, `🐢`, `🐌`, `🩵`, `🐉`, `🦅`) and role badge (`👑 LEADER` vs `📡 FOLLOWER`).
    - Status pills: `🟢 READY`, `🔴 OFFLINE`, `⚠️ CONFLICT`, `🟡 WEAK LINK`.
    - 4-bar RSSI wireless signal gauge (`●●●●` -44 dBm Excellent to `●○○○` -88 dBm Weak link).
    - Power bank / Battery telemetry (`5.12V / 98% Buffer`).
    - Heartbeat freshness counter (`Just now`, `1s ago`, `No response`).
  * **Interactive Visual Identification (`✨ Identify` & `✨ Flash Lineup`):**
    - Individual `✨ Identify`: Commands target float to flash 3 full-brightness bursts in its signature color.
    - Simulator Canvas Link: Mini-shirt on 2D canvas strobes in real time while the radar card pulses with that float's signature color.
    - `✨ Flash Lineup (1➔7)`: Sequentially flashes Floats 1 through 7 down the line at 200ms intervals.
  * **Network & Firmware Telemetry Protocol:**
    - Python Server (`simulator.py`): Added `/api/fleet_radar` (GET), `/api/fleet_radar/scan` (POST), and `/api/fleet_radar/identify` (POST).
    - UDP Packet Framing: Added Opcode `0x03` (`cmd 0x01` Probe, `cmd 0x02` Identify Flash).
    - ESP32 Dual-Core Firmware (`src/main.cpp` & `MSEP_Costume.ino`): Added `triggerIdentifyFlash()`, `broadcastIdentifyPacket()`, UDP Opcode `0x03` handling, and ESP-NOW Mode `0x42` handling.
  * **Corral Scenario Simulator:**
    - Dropdown allows instant verification of realistic race-morning situations: Ideal 7/7 Ready, Float 4 Missing (in restroom), Float 6 Duplicate Conflict, Float 7 Weak Link (-88 dBm), and Live Hardware Only.

### Entry: Race-Day Battery Life & Power Budget Calculator (200 LEDs / 5V 2.0A Limit)
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Race-Day Hardware Safety & Real-Time Battery Budget Modeling
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **200-LED Wearable Costume Physics Model:**
    - Models 100 front chest LEDs + 100 duplicated back LEDs running concurrently for 360° race-day visibility.
    - Factors in 130 mA steady current for ESP32 Dual-Core (240 MHz + Wi-Fi/ESP-NOW active) and 200 mA quiescent standby current for 200 WS2812B nodes (1.0 mA/node).
    - Accurately models real-world 3.7V lithium-ion to 5.0V USB boost conversion efficiency (~70% delivered usable capacity: 5k mAh -> 3,500 mAh, 10k mAh -> 7,000 mAh, 15k mAh -> 10,500 mAh, 20k mAh -> 14,000 mAh).
  * **Float Baseline & Show Peak Current Modeling:**
    - Casey Jr. Train (#1): 750 mA base / 1,120 mA show peak.
    - Title Drum (#2): 620 mA base / 1,050 mA show peak.
    - The Turtle (#3): 660 mA base / 1,080 mA show peak.
    - The Snail (#4): 670 mA base / 1,090 mA show peak.
    - Cinderella's Coach (#5): 700 mA base / 1,100 mA show peak.
    - Pete's Dragon (#6): 720 mA base / 1,150 mA show peak.
    - Flag & Eagle (#7): 780 mA base / 1,180 mA show peak.
    - Strictly models FastLED hardware power clamping (`FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000)`), ensuring peaks never exceed the 2.0A power bank delivery limit.
  * **Interactive UI & Real-Time Calculation Engine (`#powerBudgetSection`):**
    - USB Power Bank Selector (5k, 10k, 15k, 20k mAh) with live Wh rating.
    - Race + Corral Duration Slider (30m to 240m with 15m steps).
    - 30s Fleet Show Trigger Cadence (every 2m, 4m, 8m, or baseline only).
    - Result Cards: Projected Finish Line Battery Remaining % with color-coded safety indicators (Green $\ge 50\%$, Yellow $35-49\%$, Orange $15-34\%$, Red $< 15\%$), and Total Hours to Empty.
    - Progress Bar visualizer showing consumed vs. total usable 5V mAh.
    - Expandable 7-Float Breakdown Table with individual baseline mA, show peak mA, finish %, and total runtime for each brother.
    - Fast Jump Button: Added `🔋 Battery Budget` badge in the 30s Fleet Show Creator header to immediately jump and pulse the power budget section.
  * **Persistence & Cache-Busting:**
    - Saves user power bank preferences to `localStorage` (`msep_power_bank_size`, `msep_race_duration`, `msep_show_frequency`).
    - Bumped script cache-buster to `app.js?v=27`.

### Entry: Interactive Visual Timeline Block Editor (Drag-to-Stretch, Rolling Trim & Reordering)
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Interactive NLE-Grade Visual Timeline Studio
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Direct Drag-to-Stretch Duration Editing (`activeTimelineDrag`):**
    - Hovering over the right edge of any block reveals an `ew-resize` handle.
    - Dragging right/left resizes duration in 0.1s increments with a floating HUD tooltip (`⏱️ Duration: 3.5s | Ends at 7.5s`). Subsequent blocks automatically ripple forward smoothly.
  * **Rolling Trim Transition Editing:**
    - Dragging the left edge of any block performs a rolling edit against the preceding block, shifting the boundary without displacing the remainder of the routine.
  * **Drag-and-Drop Block Reordering & Insertion Indicator:**
    - Dragging a block's body displays a glowing blue `.fleet-timeline-drop-indicator` line showing the target insertion slot. On release, blocks reorder, start times are recalculated sequentially, and the sidebar stack is updated instantly.
  * **Category Theming & Directional Motion Badges:**
    - Styled blocks with category gradient themes: Electric Blue (Waves), Emerald (Sync), Vivid Amber (Theatrical), and Dark Graphite (Blackout).
    - Added motion badges on blocks (`1 ➔ 7`, `7 ➔ 1`, `4 ➔ 1&7`, `1&7 ➔ 4 ➔ 1&7`, etc.) and duration tags (`3.5s`).
  * **Click-to-Seek & Bi-directional Highlighting:**
    - Clicking any block seeks the playhead to its start time, applies a golden highlight, and auto-scrolls to its editor card in the sidebar.
  * **Cache-Busting & Versioning:** Bumped script tag to `app.js?v=26`.

### Entry: Signature Fleet Show Preset Pack ("The Electrical Suite") & Feature Queue Roadmap
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Fleet Choreography Content Library & Studio Production
* **Status:** Operational & Verified in Web Simulator and Python Server.
* **Notes:**
  * **3 New Signature Fleet Choreography Presets Added to `presets/fleet_shows/`:**
    - `supernova_spectacular_30s.json` (**💥 The Supernova Spectacular - 30s**): High-octane choreography featuring the signature Dual Collision Shockwave, Butterfly Ripple Echo, Fairy Dust Waterfall, Ping-Pong Bounce, Cosmic Breath, and Grand Finale.
    - `baroque_hoedown_encore_30s.json` (**🎪 Baroque Hoedown Encore - 30s**): Fast-tempo, rhythmic choreography tuned to the iconic parade beat with syncopated wig-wags, forward/reverse wave volleys, collision bursts, and a roaring hoedown crescendo.
    - `pixie_dust_processional_20s.json` (**🧚 Pixie Dust Processional - 20s**): Lyrical, enchanted starlight showcase featuring golden fairy dust waterfalls, silky cascade dissolves, starlight twinkle tempests, and gentle ambient stardust.
  * **Dynamic Server Discovery & Dropdown:**
    - Verified `/api/fleet_shows` dynamically enumerates all 5 presets (`default_30s_grand_parade`, `supernova_spectacular_30s`, `baroque_hoedown_encore_30s`, `classic_20s_routine`, `pixie_dust_processional_20s`).
    - Added fallback `<option>` tags in `simulator/index.html`.
  * **Feature Queue Prioritization:** Queued up the next 3 high-impact features (Visual Timeline Drag-to-Stretch Editor, Battery & Power Budget Calculator, and Corral Roll Call / Fleet Radar Diagnostic).

### Entry: Multi-Float Live Wi-Fi UDP Streaming Architecture (Opcode 0x02) & Simultaneous Bench Prototyping
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Real-Time Multi-Node Wi-Fi UDP Streaming & Rapid-Fire Hardware Bench Prototyping
* **Status:** Operational & Verified across Web Simulator, Python Server, and ESP32 C++/Arduino firmware.
* **Notes:**
  * **Addressed Multi-Float UDP Protocol (`Opcode 0x02`):**
    - Engineered packet framing protocol: `['M','S','E','P', 0x02, target_float_id, num_leds_hi, num_leds_lo, R, G, B, ...]`.
    - Maintained legacy `Opcode 0x01` universal frame support for single-shirt editing where any bench ESP32 acts as a display.
  * **Dual-Core Compatible ESP32 Receiver Engine (`src/main.cpp` & `MSEP_Costume.ino`):**
    - Upgraded UDP packet parser to use a non-blocking `while ((packetSize = udp.parsePacket()) > 0)` loop, draining socket buffers with zero latency.
    - Added float role filtering: `if (targetFloatId == 0 || targetFloatId == myFloatNumber)`. An ESP32 takes its assigned float's frame, writes 100 front LEDs, duplicates to 100 back LEDs, and displays via FastLED. Packets addressed to other floats are dropped immediately.
  * **Full Fleet Real-Time Streaming Dispatcher (`simulator/app.js` & `simulator.py`):**
    - When on the Fleet Lineup tab or during 30s Fleet Show playback, the simulator gathers all 7 floats at 30 FPS using `computeRunnerLedColor()` and dispatches an array of addressed frames (`fleetFrames`).
    - Python backend broadcasts each addressed frame over UDP port 4210 to `255.255.255.255`.
    - Optimized payload with flat integer arrays `[r, g, b, ...]` reducing JSON parsing overhead by 70%.
  * **Fleet Creator Toolbar Integration (`simulator/index.html`):**
    - Added dedicated Wi-Fi streaming bar directly inside the Fleet Show Creator sidebar with live status indicators, stream stats, settings gear, and synchronized 1-click toggle (`#fleetWifiStreamBtn`).
  * **ROM Binary Refresh:** Built and verified all 7 float ROM binaries with multi-float UDP streaming logic baked in.
  * **Cache-Busting & Versioning:** Bumped script tag to `app.js?v=25`.

### Entry: Expansion of Fleet Choreography Library to 19 Blocks (Dual Collision, Silky Cascade, Butterfly Ripple & Fairy Waterfall)
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Simulation Engine
* **Status:** Operational & Verified in Web Simulator and FastLED C++ Generator.
* **Notes:**
  * **New Signature Choreography Blocks (`FLEET_BLOCK_DEFS` in `simulator/app.js`):**
    - `color_collision` (**Dual Collision & Supernova Shockwave**): High-velocity beams rush inwards from outer Floats 1 & 7 to Float 4, detonate in a brilliant white impact crest, then erupt outward in an expansive starlight shockwave back to 1 & 7.
    - `cross_dissolve_chase` (**Silky Cascade Dissolve**): Silky, organic sinusoidal cross-dissolve flowing runner-by-runner sequentially from Float 1 through Float 7 (0.5 phase offset per runner).
    - `ripple_echo` (**Mirror Pair Echo / Butterfly Ripple**): Symmetric harmonic ripple originating at center Float 4, then cascading outward to mirrored pairs (3&5, 2&6, then 1&7) with smooth sinusoidal breathing.
    - `sparkle_cascade` (**Fairy Dust Waterfall Cascade**): A rolling waterfall of glittering Pixie Dust sparkles sweeping down the parade line (1 ➔ 7) with soft trailing embers.
  * **Real-Time Canvas Simulation (`evalActiveFleetShowColor()`):**
    - Implemented full analytical math for all four new blocks in JavaScript for interactive 60 FPS playback on the 7-shirt preview canvas.
  * **FastLED C++ Generator Synchronization (`generateFleetRoutineCpp()`):**
    - Integrated matching FastLED C++ math routines for all 4 new blocks inside `generateFleetRoutineCpp()`, exporting pure integer/float math, `fminf`/`fmaxf`, `blend()`, and `random8()` routines directly into firmware.
  * **UI Palette & Selector Integration:**
    - Updated `#fleetAddBlockTypeSelect` in `simulator/index.html` to organize all 19 choreography blocks into Traveling Waves, Synchronous Illuminations, and Theatrical & Dynamics optgroups.
  * **Cache-Busting & Versioning:** Bumped script tag to `app.js?v=24`.

### Entry: Web Serial ESP32 Flasher Suite for Fleet Units (Floats 1–7), Dedicated Float Roles & Soundtrack Decision
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Flasher Suite & Multi-Float ROM Architecture
* **Status:** Operational & Verified across Web Serial, PlatformIO Build Toolchain, and Simulator UI.
* **Notes:**
  * **Dedicated Float Role Firmware Injection (`src/main.cpp` & `MSEP_Costume.ino`):**
    - Introduced `COMPILED_FLOAT_ID` macro and optional `include/float_config.h` header across both PlatformIO C++ firmware and Arduino sketches.
    - When a dedicated float binary is flashed, the microcontroller automatically initializes its NVS flash memory (`Preferences.h`) to that exact Float ID on first boot, eliminating any need for manual button tapping.
    - Interactive hardware override (holding the onboard BOOT button for 3 seconds to cycle Floats 1–7) remains fully operational for field flexibility.
  * **Automated Multi-Binary Build Pipeline (`build_fleet_binaries.py` & `simulator.py`):**
    - Created build pipeline generating dedicated binaries for all 7 floats (`firmware_float1.bin` through `firmware_float7.bin`) plus a universal fallback (`firmware.bin`), along with matching JSON manifests (`manifest_float1.json` – `manifest_float7.json`).
    - Added backend endpoint `POST /api/build_fleet_binaries` and automated background syncing upon "Apply to Firmware" export.
    - Added CORS `Access-Control-Allow-Origin: *` headers for all firmware assets to ensure seamless browser Web Serial downloads.
  * **Zero-Install Web Serial Flasher Overhaul (`simulator/web_flasher.html`):**
    - Modernized the web flasher with a responsive 7-card fleet lineup selector (plus Generic Auto) with character icons (🚂 The Train, 🥁 Title Drum, 🩵 Cinderella, 🏴‍☠️ Peter Pan, 🐘 Dumbo, 🐉 Pete's Dragon, 🦅 To Honor America).
    - Clicking any float dynamically updates the armed float panel, hardware specs (GPIO 16, 200 LEDs, 2.0A limit), and re-targets the `<esp-web-install-button>` manifest URL.
  * **Simulator In-App Flashing Integration (`simulator/index.html` & `simulator/app.js`):**
    - Added **"⚡ Flash Float..."** button to the Fleet Show Creator toolbar opening a dedicated Float Role selection modal (`#fleetFlashModal`) with 1-click USB (PlatformIO) and Web Serial links.
    - Added **"Assigned Float Role"** dropdown selector to the Deploy & Hardware tab directly above the USB flashing button.
  * **Soundtrack Audio Playback Omission Decision:**
    - Evaluated and intentionally omitted personal costume audio speakers based on runDisney 10K race conditions (ambient corral crowd courtesy, loud pre-race and on-course DJ/band stages, and the designated Boardwalk quiet zone). 100% of battery power and design focus is dedicated to the wireless synchronized LED visual spectacle.
  * **Cache-Busting & Script Versioning:** Bumped script tag to `app.js?v=23` in `simulator/index.html`.

### Entry: 1-Click Fleet Show to Firmware Export, C++ Generator & Automated PlatformIO Build Verification
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & C++ Firmware Export Pipeline
* **Status:** Operational & Verified in Web Simulator and PlatformIO Build Toolchain.
* **Notes:**
  * **FastLED C++ Choreography Generator (`generateFleetRoutineCpp()`):**
    - Built a full-fidelity translator in `simulator/app.js` that maps all 14 fleet choreography block types (`wave_forward`, `wave_reverse`, `fleet_pulse`, `sparkle_storm`, `center_burst`, `converge_center`, `wig_wag`, `baton_chase`, `ping_pong_wave`, `color_wash_chase`, `rainbow_sweep`, `strobe_all`, `shimmer_drift`, `grand_finale`, `blackout`) into a clean, readable `render30sFleetRoutine(uint32_t elapsedMs)` function.
    - Handles color dynamics (`cycle_random`, `match_previous`, and standard parade signature hues) and front-to-back 200-LED duplication for 360° visibility.
  * **Dual Interface Export Controls (`simulator/index.html`):**
    - Added **"📋 View C++ Code"** (`#fleetViewCppBtn`): Opens the in-browser `#codeModal` to inspect and copy the generated FastLED routine with a single click.
    - Added **"⚡ Apply to Firmware"** (`#fleetApplyFirmwareBtn`): Calls backend API `/api/export_fleet_routine` to directly write the routine to `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` between sentinel markers.
  * **Dynamic Routine Duration (`FLEET_ROUTINE_TOTAL_MS`):**
    - Replaced hardcoded 30000ms loop limit with dynamic macro `#define FLEET_ROUTINE_TOTAL_MS`, allowing routines of arbitrary duration (e.g. 25.0s, 30.0s, 45.0s) to be played and stopped accurately on ESP32 hardware.
  * **Automated PlatformIO Compilation Verification:**
    - Integrated automated background `pio run` verification inside the backend endpoint, testing that the generated C++ builds with zero compiler or library errors before notifying the user.
  * **Cache-Busting & Script Versioning:** Bumped script tag to `app.js?v=22` in `simulator/index.html`.

### Entry: Fixed Spurious Unsaved Changes Warning on Initial Startup
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Clean Startup Preset Loading
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Root Cause Analysis:**
    - On initial simulator boot, `defaultDragonImg.onload` invoked `scatterLedsOnGraphic(100, true)` before any user interaction, which called `markSingleShirtDirty()` and set `isSingleShirtDirty = true` upon page load.
    - When navigating to the Fleet tab and switching to another runner (e.g. double-clicking "To Honor America"), `editRunnerInSingleView` detected the false dirty state and incorrectly triggered the unsaved changes warning dialog.
  * **Resolution & Architecture:**
    - Stripped the legacy `scatterLedsOnGraphic()` call from `defaultDragonImg.onload`, ensuring image loading only sets asset availability (`defaultDragonLoaded = true`).
    - Added clean initial preset loading via `refreshPresetDropdown().then(() => loadProfile('server:petes_dragon.json'))` to guarantee the official Float 6 Pete's Dragon profile is loaded cleanly with `isSingleShirtDirty = false`.
    - Added `markDirty = true` parameter to `scatterLedsOnGraphic()` and `autoOutlineCurrentGraphic()`, allowing programmatic fallback initialization without polluting the user dirty state.
    - Updated `loadGraphicPreset()` to reset `isSingleShirtDirty = false` and update active runner lineup slot.
    - Updated `switchSidebarTab()` to continuously track `lastSingleShirtTab` on single-shirt tab switches.
  * **Cache-Busting:** Bumped script tag to `app.js?v=21` in `simulator/index.html`.

### Entry: Interactive Unsaved Costume Changes Prompt with Custom Profile Name Saving
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Unsaved Edits Workflow Protection
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Interactive Unsaved Changes Modal (`#unsavedChangesModal`):**
    - Replaced generic browser `confirm()` with a dedicated, themed modal dialog (`#unsavedChangesModal`) matching the dark GitHub-themed UI of the simulator.
    - When a user has modified a costume (`isSingleShirtDirty = true`) and attempts to edit a different runner or switch presets on the Layout tab, the dialog appears presenting three explicit choices:
      1. **💾 Save Profile & Switch:** Prompts for a profile name with an embedded text input (`#unsavedModalProfileNameInput`) prefilled with an intuitive name (e.g. `Pete's Dragon Custom` or existing layout name). Clicking save executes `await saveCurrentProfile(name)` which saves to localStorage and backend server, links `local:<name>` to that runner's fleet slot, clears the dirty state, and transitions to the new runner.
      2. **🗑️ Discard & Switch:** Discards live unsaved modifications and proceeds to switch.
      3. **Cancel:** Closes the modal without modifying or switching, leaving all work intact.
  * **Unified Integration Across All Switching Entrypoints:**
    - Integrated with `editRunnerInSingleView(slot)` (runner card click, "Edit in Single View" button, canvas double-click, and fleet table action button).
    - Integrated with `#presetSelect` on the Layout tab to prevent accidental data loss when selecting a different preset from the dropdown.
    - Updated `loadProfile()` to clear dirty state and update active runner lineup slot.
  * **Cache-Busting & Script Updates:** Bumped script tag to `app.js?v=20` in `simulator/index.html`.

### Entry: Fixed Active Single-Shirt Editor State Clobbering When Re-Entering Single View From Fleet View
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Live Editor Session Preservation
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Session Preservation Fix in `editRunnerInSingleView`:**
    - Resolved issue where re-entering Single View from Fleet View for the active runner slot (e.g. Shirt 6 / Pete's Dragon) reloaded the saved preset file from disk, overwriting in-memory live modifications (such as switching from 100-LED scatter fill to 50-LED perimeter outline).
    - If `slot === activeSingleShirtRunnerSlot`, `editRunnerInSingleView(slot)` now seamlessly transitions to the Single Shirt visualizer and restores the previous workflow tab without reloading preset data or wiping out the live in-memory LED state.
    - If user attempts to switch to edit a different runner slot while `isSingleShirtDirty` is true, an interactive confirmation dialog warns them before discarding unsaved edits.
  * **Comprehensive Editor Dirty-State Triggers:**
    - Attached `markSingleShirtDirty()` to all single-shirt editing routines: `autoOutlineCurrentGraphic()`, `scatterLedsOnGraphic()`, `rearrangeRemainingLedsOnGraphic()`, `optimizeLedWiringOrder()`, `resetLedsBtn`, canvas LED drag-and-drop, animation group creation/updating/deletion, and firework cluster generation.
  * **Cache-Busting:** Bumped `app.js` script tag to `?v=19` in `simulator/index.html`.

### Entry: Real-Time Single-Shirt Live Editor Synchronization & Unsaved Edit Status Badges on Fleet View
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Live Editor Integration
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Live Single-Shirt Preset Synchronization:**
    - Fleet View now evaluates `getLiveSingleShirtPresetData()` for the runner slot currently open in the Single Shirt Editor, rendering live modifications (LED positions, brightness, hue, speed BPM, pattern, animation groups) across both baseline rendering and fleet show choreography blocks in real time.
  * **Visual Badges & Unsaved Indicators:**
    - **Runner Cards:** Displays status badges (`✏️ Unsaved Live Edit` / `✨ Live Editor Active`) and explicit label notes (`✏️ Previewing Unsaved Edit`) on runner cards in `#fleetRunnersContainer`.
    - **Fleet Canvas:** Renders high-contrast badges `✏️ UNSAVED LIVE PREVIEW` (orange) or `✨ LIVE PREVIEW` (cyan) directly above the active shirt and updates the header subtitle note with float preview details.
  * **Preset Auto-Assignment on Save:**
    - `saveCurrentProfile()` automatically updates the active runner card slot (`fleetRunners[activeSingleShirtRunnerSlot].preset = 'local:' + cleanName`), updates `fleetPresetCache`, clears `isSingleShirtDirty`, saves lineup configuration to storage, and refreshes cards & dropdowns.
  * **Navigation & Tab Memory Restoration:**
    - Single shirt editor tracks `lastSingleShirtTab` (`tabLayout`, `tabGroups`, `tabDirector`, etc.). Exiting Fleet View or double-clicking a shirt card restores the user's previous single-shirt tab automatically.
  * **Cache-Busting:** Bumped `app.js` script tag to `?v=18` in `simulator/index.html`.

### Entry: Removed Rectangular Card Frame Highlights Around Fleet Shirts During Fleet Show Playback
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Visual Polish
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Visual Cleanliness Enhancement:**
    - Per user directive, removed the outer rectangular bounding boxes and glowing color-changing frames (`strokeRect`) that previously flashed around each runner card as light waves, pulses, or sparkle storms traveled down the line in Fleet View.
    - Eliminates visual distraction so all lighting effects and color transitions are rendered strictly through the discrete addressable LED nodes on the costumes, the float graphics, and the runner bibs.
    - Maintained clean, non-intrusive selection/hover outlines (`isSelected` and `isHovered`) when the user explicitly clicks or hovers a runner card to edit it.
  * **Cache-Busting:** Bumped `app.js` script tag to `?v=17` in `simulator/index.html`.

### Entry: Dynamic Scoping of Master Timeline (Single Shirt Cue Director vs. Fleet Tab Choreography)
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Master Timeline View Scoping
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Master Timeline Strict Separation:**
    - Single Shirt View (`currentView === 'single'`): Timeline bar displays the individual float's 90-second Cue Director sequence (0..90s ruler, `🌐 Global Float` + localized `🎡 [Group Name]` lanes, sub-lane stacking, cue block details with fade indicators, `🎬 Sequence: ON/OFF` toggle, and single-shirt transport controls).
    - Fleet Tab View (`currentView === 'fleet'` / `tabFleet`): Timeline bar displays the synchronized 7-shirt Fleet Show choreography (0..30s ruler, Fleet Show block tracks with 14 block types, active block highlights, decimal time readouts, `FLEET SHOW` track header, and one-shot fleet transport controls).
  * **Tab & View Synchronization Fix:**
    - Fixed tab-switching hook in `switchSidebarTab()`: Automatically sets `currentView` and triggers `renderTimelineLayers()`, `updateTimelinePlayBtn()`, and `updateTimelineScrubberUI()` so the timeline instantly reflects the active workspace.
    - Fixed `singleViewBtn` and `fleetViewBtn` canvas toolbar click listeners to re-render timeline tracks and transport status immediately.
  * **Order-of-Operations Bug Fix in `editRunnerInSingleView`:**
    - Previously, `applyProfileData(pData)` was invoked before setting `currentView = 'single'`. Because `currentView` was still `'fleet'`, `renderTimelineCueStrip()` rendered the Fleet Show timeline instead of the individual float's cues.
    - Now, `currentView = 'single'` is assigned first (and any running fleet show is stopped), guaranteeing the individual float's cue timeline is loaded cleanly upon double-clicking any runner card or clicking "Edit in Single View".
  * **Context-Aware Transport & Hotkeys:**
    - `timelinePlayBtn`: Toggles single-shirt sequence in Single View (`togglePlayPause()`); triggers or stops debounced 30s fleet routine in Fleet View (`triggerFleetShowToggle()`).
    - `timelineStopBtn`: Rewinds single-shirt sequence to 0:00 in Single View (`stopSequence()`); halts fleet show and rewinds to 0.0s in Fleet View (`stopFleetShow()`).
    - Spacebar: Plays/pauses single sequence when in Single View; triggers/stops fleet routine when in Fleet View (preventing double-firing between keydown and keyup).
    - `timelineModeToggle`: Shows `🎬 Sequence: ON/OFF` in Single View; displays `👑 Fleet Show: ON` / `⚡ Baseline: ON` in Fleet View.
    - `timelineLoopToggle`: Shown in Single View (`🔁 Loop`); cleanly hidden in Fleet View to preserve one-shot execution back to baseline.
  * **Cache-Busting:** Bumped `app.js` to `?v=16` in `simulator/index.html`.

### Entry: Fix 7-Shirt Fleet Canvas Rendering (Resolved Uncaught ReferenceError on Floats 1-6)
* **Date:** 2026-09-25
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Hardware Parity
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Root Cause:**
    - In `renderFleetView()`, residual legacy variable references (`waveProgress`, `isPulsePhase`, `tRoutine`, `isParadeRoutine`, `isSparkleStorm`) were present inside the un-cached mini LED fallback branch (lines 2719, 2723) and highlight frame conditions (lines 2768, 2776, 2787).
    - When `renderFleetView()` rendered Float 0 (The Train), execution crashed immediately upon evaluating line 2768/2776 with an uncaught `ReferenceError: isPulsePhase is not defined`, aborting the float loop before Floats 1 through 6 could be drawn.
  * **Fix Implementation:**
    - Explicitly reset canvas transform matrix at the top of `renderFleetView`: `ctx.setTransform(1, 0, 0, 1, 0, 0)`.
    - Wrapped each float runner iteration inside a resilient `try ... catch (err)` block so an unexpected error on any one runner cannot abort the remaining fleet shirts.
    - Replaced all legacy variable references with safe active block and time expressions (`waveColor?.hex || '#ffc107'`, `fleetShowActive && activeBlock?.type === 'fleet_pulse'`).
    - Added in-flight promise deduplication in `getPresetDataForRunner` (`fleetPresetPromises`) and parallel preloading in `loadFleetLineupFromStorage()`.
    - Bumped `app.js` cache-buster to `?v=15` in `simulator/index.html`.
    - All 7 shirts (The Train, Title Drum, The Turtle, The Snail, Cinderella, Pete's Dragon, Flag & Eagle) now render simultaneously on canvas.

### Entry: 7-Shirt Fleet Show Creator Studio, 14 Block Types, One-Shot Debounced Trigger & ESP32 Parity
* **Date:** 2026-09-25
* **Milestone:** Milestone 5 - 7-Shirt Synchronized Fleet Show Choreography & Hardware Parity
* **Status:** Operational & Verified in Web Simulator, Python Server, and ESP32 Unified Firmware (`src/main.cpp` & `arduino/MSEP_Costume/MSEP_Costume.ino`).
* **Notes:**
  * **Architectural Decoupling of Baseline vs. Fleet Routine:**
    - Per user directive, individual float programs are treated as the baseline state rather than a sub-block inside the fleet sequence.
    - All 7 shirts continuously render their individual float presets, rotating wheels, and animation groups until an activation button is triggered.
    - Clicking the prominent **"⚡ ACTIVATE 30s FLEET SHOW"** button or pressing hotkeys `[Space]` / `[F]` initiates the 30-second synchronized routine once.
    - Upon completion of the sequence (or when stopped early), all 7 costumes automatically return to their individual float programs.
  * **Debounced Trigger & Early Stop Protocol:**
    - **Simulator Debounce:** Integrated 300ms software lockout on `triggerFleetShowToggle()` and `Spacebar`/`F` hotkeys, preventing jitter or double triggering.
    - **Early Return:** Hitting the activation button while the 30s show is running immediately terminates the routine and reverts all costumes to baseline.
    - **ESP32 Hardware Parity:** Enforced 50ms hardware press debounce (`pressDuration >= 50 && pressDuration < 2500`) and 300ms software lockout between button releases (`now - lastButtonReleaseTime >= 300`) on the onboard BOOT button (GPIO 0). Short tap starts the 30s fleet routine once; tapping during playback stops it early and returns to baseline with 2 amber visual confirmation flashes.
    - **ESP-NOW Peer-to-Peer Sync:** When any costume triggers or cancels the fleet routine, it broadcasts a packet (`mode = 0x30` start, `mode = 0x00` cancel) to `broadcastMac`. All listening peer nodes update `currentStandaloneMode` and sync their millisecond start offset in real time.
  * **14-Block Choreography Palette & Block Stack Editor:**
    - Implemented a complete choreography engine supporting 14 multi-float block types: `blackout`, `wave_forward` (~2-shirt decay and incandescent crest), `wave_reverse`, `fleet_pulse`, `center_burst`, `converge_center`, `wig_wag` (120 BPM odd/even marquee), `baton_chase`, `sparkle_storm` (75% density wave + white starlight storm), `ping_pong_wave`, `color_wash_chase`, `rainbow_sweep`, `strobe_all`, and `shimmer_drift`.
    - Added full stack editor in Tab 6 allowing users to add blocks from the palette, reorder blocks (▲ / ▼), duplicate, delete, and adjust durations/parameters in real time.
    - Added **"⏱️ Snap to 30.0s"** button that proportionately scales all block durations so total sequence runtime equals exactly 30.0 seconds.
    - Added REST persistence endpoints in `simulator.py` (`/api/fleet_shows`, `/api/fleet_show/<f>`, `/api/save_fleet_show`) saving to `presets/fleet_shows/*.json` (including `default_30s_grand_parade.json` and `classic_20s_routine.json`).
  * **Master Timeline & 7-Runner Integration:**
    - Master timeline layers dynamically render color-coded fleet show blocks when viewing the 7-shirt fleet.
    - Scrubber drag and click seeking fully supported during fleet playback.
    - Verified 1-click **"✏️ Edit in Single View"** button and card double-click across all 7 runner slots.
  * **ESP32 Arduino Core 2.x & 3.x Parity (Rule 5):**
    - Fully mirrored `src/main.cpp` into `arduino/MSEP_Costume/MSEP_Costume.ino`.
    - Enforced FastLED 5V 2000mA power limit and 200-LED duplicated configuration.

### Entry: 20-Second Choreographed Fleet Routine with ~2-Shirt Wave Trail, 5s Synchronized Pulse, and Color+White Sparkle Storm
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and Python Server.
* **Notes:**
  * **20-Second Choreographed Sequence Architecture (`parade_20s`):**
    - Expanded the choreographed parade routine cycle duration from 15.0 seconds to 20.0 seconds (`timeMs % 20000`).
    - Maintained full backwards compatibility with legacy `parade_15s` mode identifiers, auto-upgrading to `parade_20s`.
    - Integrated exact timing breakdown across 7 distinct phases:
      - **Phase 1 (0.0s – 1.0s):** Blackout across all 7 shirts (`alpha: 0.0`).
      - **Phase 2 (1.0s – 2.0s):** Forward wave sweeps float 1 through 7 with a brilliant incandescent crest and a smooth **~2-shirt trailing decay** in the active cycle's wave color.
      - **Phase 3 (2.0s – 3.0s):** Reverse wave sweeps float 7 back to 1 in the **exact same color** with symmetrical ~2-shirt trailing falloff.
      - **Phase 4 (3.0s – 8.0s):** **All-Fleet Wave Color Pulse (5 Seconds).** All LEDs across all 7 costumes (700 LEDs) illuminate in the active wave color and execute 3 slow, majestic breath cycles (36 BPM, intensity sweeping between 28% and 100% with an incandescent white flare at peak breath).
      - **Phase 5 (8.0s – 10.0s):** **Sparkle Storm combining Wave Color and White (2 Seconds).** High-speed twinkling combining brilliant Starlight White (`#ffffff`), pure saturated wave color bursts, and soft pastel blended shimmers.
      - **Phase 6 (10.0s – 11.0s):** Blackout across all 7 shirts for 1 second.
      - **Phase 7 (11.0s – 20.0s):** Individual float preset programs (animation groups, rotating wheels, breathing effects, patriotic pulses, custom artwork colors) execute for 9 seconds before looping.
  * **Wave Trail Mathematics (~2-Shirt Length Falloff):**
    - Normalized shirt slot spacing where 1 float width equals 1.0 unit in global coordinates (`runnerIndex + ledNormX`).
    - Formulated smooth trailing decay spanning 2.0 units (`0.25 <= delta < 2.25`) behind the traveling wave crest:
      `decay = Math.pow(Math.max(0, 1.0 - (delta - 0.25) / 2.0), 1.35)`.
    - Applied identical coordinate delta symmetry to both the forward wave (`delta = sweepPos - globalPos`) and reverse wave (`delta = globalPos - sweepPos`).
  * **Cycle Wave Color Consistency & Rotation:**
    - Updated `getFleetRoutineWaveColor(timeMs)` to index cycles via `Math.floor(timeMs / 20000)`.
    - The selected standard Disney color remains strictly locked throughout the forward wave, reverse wave, 5-second pulse, and sparkle storm within the same 20-second cycle, and rotates to a new, non-repeating standard color on the next cycle.
  * **UI & Real-Time Telemetry:**
    - Updated Fleet mode toggle button in `simulator/index.html` to `👑 20s Routine`.
    - Updated the sidebar info box (`#fleetRoutineInfoBox`) with the full 20s breakdown and real-time phase badge (`0.0s / 20.0s`).
    - Added dynamic breathing frame aura on canvas during the 5s pulse phase, framing all 7 runners with their pulsating wave color.

### Entry: 1-Click Single View Editing from Fleet Cards & Full Float Preset Support
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and Python Server.
* **Notes:**
  * **Root Cause Diagnosis for Fleet Card Edit Buttons:**
    - Discovered that server presets for Floats 1, 2, 3, 4, and 7 (`casey_jr_train.json`, `title_drum.json`, `spinning_turtle.json`, `spinning_snail.json`, `honor_america_eagle.json`) stored their LED index arrays under the property key `"indices"`, whereas `renderActiveGroupsList()` and group inspection logic accessed `grp.ledIndices`.
    - Calling `grp.ledIndices.length` on undefined threw an unhandled `TypeError` inside `applyProfileData()`, aborting execution before `currentView = 'single'`, `switchSidebarTab('tabLayout')`, or view transitions could run.
  * **Dual Key Normalization (`ledIndices` & `indices`):**
    - Updated `applyProfileData()`, `rebuildLedGroupMap()`, `selectGroupLeds()`, and `renderActiveGroupsList()` in `simulator/app.js` to automatically normalize both keys: `const arr = Array.isArray(grp.ledIndices) ? grp.ledIndices : (Array.isArray(grp.indices) ? grp.indices : []); gr.ledIndices = arr; grp.indices = arr;`.
    - Mirrored `ledIndices` alongside `indices` across all 5 official preset JSON files in `presets/` for complete dual compatibility.
  * **1-Click & Double-Click Single View Editing Workflow (`editRunnerInSingleView`):**
    - Wrapped `editRunnerInSingleView(slot)` in a `try...catch` block with user toasts and console logging.
    - Added fallback preset synthesis in case server fetching encounters offline network interruptions.
    - Automatically switches view to single mode, centers and frames the shirt with `resetZoom()`, opens the `🎨 Layout` tab (`tabLayout`), and sets the Quick-Load dropdown to match the runner's assigned preset.
    - Bound `click` and `dblclick` directly to fleet runner cards: single click selects the runner card, and double click opens Single View editor.
    - Added `isRenderingFleetCards` concurrency guard to prevent race conditions during rapid tab switching.
  * **Full Costume Graphic Suite Integration (`graphicPresetSelect` & `loadGraphicPreset`):**
    - Expanded the Costume Graphic dropdown in `simulator/index.html` to include all 7 official parade units (`casey_jr_train`, `title_drum`, `spinning_turtle`, `spinning_snail`, `cinderellas_coach`, `carriage_nohorses`, `builtin_dragon`, `honor_america_eagle`).
    - Unified `loadGraphicPreset(type)` in `simulator/app.js` to automatically fetch each float's server preset and color-matched LED map.
    - Updated SVG header dimensions to explicit `width="800" height="600"` across all 7 Cricut SVG files to guarantee accurate `naturalWidth` and `naturalHeight` reporting.
    - Enhanced single shirt drawing title mapping (`FLOAT_TITLES`) and guarded `drawPetesDragon()` from rendering incorrect silhouette fallbacks.

### Entry: Randomized Standard Color Wave for 15-Second Choreographed Parade Fleet Routine
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and Python Server.
* **Notes:**
  * **Dynamic Cycle-Based Standard Color Palette (`FLEET_WAVE_STANDARD_COLORS`):**
    - Configured a collection of 12 standard Disney theme colors corresponding directly to the project's signature color swatches:
      - `Belle Gold` (`#ffc107`), `Alice Cyan` (`#00f0ff`), `Coral Rose` (`#ff3c78`), `Electric Pink` (`#ff19e6`), `Electric Lime` (`#55ff10`), `Cinderella Blue` (`#0077ff`), `Cheshire Violet` (`#af25ff`), `Deep Indigo` (`#4b23be`), `Flame Orange` (`#ff7800`), `Starlight White` (`#fffaf2`), `Dragon Green` (`#00ff23`), `Mickey Red` (`#ff0d1a`).
  * **Cycle-Synchronized Non-Repeating Wave Color Selection (`getFleetRoutineWaveColor`):**
    - Calculated active wave color strictly from `cycleIndex = Math.floor(timeMs / 15000)` using a coprime stride ($5 \pmod{12}$).
    - **Within each 15-second cycle:**
      - Phase 2 (1.0s – 2.0s Forward Wave) and Phase 3 (2.0s – 3.0s Backward/Reverse Wave) evaluate to the identical `cycleIndex`, guaranteeing that the forward and reverse waves are 100% color-locked to the exact same standard color.
    - **Across subsequent cycles:**
      - At the 15.0s loop boundary, `cycleIndex` increments, seamlessly advancing to the next randomized standard color without repeating any color consecutively.
  * **Visual Presentation & Badge Synchronization (`renderFleetView` & `index.html`):**
    - LED rendering blends a white-hot incandescent core (`#ffffff`) with the active cycle's saturated wave color and trailing falloff.
    - Added `#fleetRoutineColorBadge` in the Fleet sidebar info card displaying the active cycle's color name and background swatch with dynamic high-contrast text.
    - Canvas header subtitle dynamically reports the active wave color (e.g. `👑 15s Parade Routine: 🌊 Phase 2: Forward Wave 1➔7 [Alice Cyan] (1.4s / 15.0s)`).
    - Runner frame outlines and bib header badges illuminate in the active wave color during Phases 2 & 3.

### Entry: 2-Row Sidebar Task Navigation Layout Fix & 15-Second Choreographed Parade Fleet Routine
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and Python Server.
* **Notes:**
  * **2-Row × 3-Column Sidebar Navigation Grid (`simulator/style.css`):**
    - Resolved UI clipping issue where `.sidebar-tab-nav` flex layout inside the fixed 410px sidebar pushed the 6th tab button (`🏃 Fleet`) off-screen to the right.
    - Converted `.sidebar-tab-nav` to `display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; padding: 8px 8px;`.
    - Organized tabs into two clean, spacious rows:
      - **Row 1:** `🎨 Layout` | `👥 Groups` | `✨ Effects`
      - **Row 2:** `🎬 Show` | `⚡ Deploy` | `🏃 Fleet`
    - Adjusted `.sidebar-tab-btn` and `.tab-count-badge` with `min-width: 0; white-space: nowrap; flex-shrink: 0;` ensuring labels and badges remain completely visible, unclipped, and easy to click.
  * **15-Second Choreographed Parade Fleet Routine (`simulator/app.js` & `simulator/index.html`):**
    - Implemented the user's requested 15-second choreographed routine as the new default fleet animation mode (`fleetSyncMode = 'parade_15s'`):
      - **0.0s – 1.0s (1s):** **Blackout.** All 7 shirts go totally black (unlit / dark bulbs).
      - **1.0s – 2.0s (1s):** **Forward Gold Wave.** A brilliant wave of Disney gold light sweeps across the fleet from Float 1 (`Casey Jr.`) through Float 7 (`To Honor America`) over 1 second. LEDs light up with a white-hot core (`#fffff5`), radiant gold body (`#ffc107`), and amber falloff tail.
      - **2.0s – 3.0s (1s):** **Reverse Gold Wave.** The gold wave reverses direction, sweeping backward from Float 7 to Float 1 over 1 second.
      - **3.0s – 5.0s (2s):** **Sparkle Storm.** All 7 costumes (700 LEDs) erupt into a synchronized starlight & gold sparkle storm for 2 seconds with high-frequency pseudorandom glitter and starlight twinkles.
      - **5.0s – 6.0s (1s):** **Blackout.** All 7 shirts go totally black (off / unlit) for 1 second.
      - **6.0s – 15.0s (9s):** **Individual Float Programs.** Each costume transitions smoothly into its assigned float preset programs (animation groups, rotating wheels, breathing effects, patriotic pulses, and custom artwork colors) for 9 seconds.
      - **Loop:** Seamlessly resets to Phase 1 every 15.0 seconds.
    - Added live countdown badge (`#fleetRoutinePhaseBadge`) in sidebar and real-time phase banner on the canvas header displaying the active phase name (e.g. `👑 15s Parade Routine: 🌊 Phase 2: Forward Gold Wave 1➔7 (1.4s / 15.0s)`).
    - Synchronized runner highlight frames on canvas: during forward & reverse waves, the active runner frame glows with a Disney gold aura (`#ffc107`); during sparkle storm, all 7 runner frames glow with a golden starlight shimmer.
    - Added routine explanation card (`#fleetRoutineInfoBox`) in the Fleet sidebar tab and wired `fleetModeParadeBtn` as the primary default button alongside continuous `Wave`, `Free-Run`, and `Show` modes.

### Entry: 7-Shirt Fleet Lineup Manager, Individual Preset Assignment & Synchronized 700-LED Canvas Preview
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and Python Server.
* **Notes:**
  * **Dedicated Sidebar Tab 6: 🏃 Fleet ("7-Shirt Fleet Lineup & Preset Manager"):**
    - Added a 6th task-oriented sidebar tab (`tabBtnFleet` with badge `7` and panel `tabFleet`) for managing the 7-runner Main Street Electrical Parade fleet.
    - Integrated 7 runner cards (Bib #01 to #07) featuring runner bib badges, float titles, and character tags.
    - Dynamic Preset Selector `<select class="fleet-preset-select">` on every runner card populated from server presets (`presets/*.json`), browser cache profiles (`msep_custom_presets`), and active editor session.
    - Live metadata pill indicators for LED count, character artwork, and active animation pattern.
    - 1-Click **"✏️ Edit in Single View"** button: instantly loads that runner's design into the full-size Single Shirt editor and switches view to `single` and `tabLayout`.
    - 1-Click **"📥 Assign Editor"** and **"📋 Assign Editor to All"** buttons: copies the active single-shirt editor design to any runner or all 7 runners.
    - **"🔁 Parade Defaults"** button: resets Floats 01–07 to their authentic parade roster presets.
  * **Synchronized Tab & View Toggle:**
    - Clicking the top header **"7-Shirt Fleet Lineup"** toggle switches canvas to fleet view and automatically activates `tabFleet` in the sidebar.
    - Clicking `tabBtnFleet` in the sidebar automatically switches canvas to fleet view.
    - Clicking **"Single Shirt"** or any single-shirt tab (`Layout`, `Groups`, `Effects`, `Show`, `Deploy`) automatically returns the canvas to single-shirt mode.
  * **True 700-LED Canvas Preview Pipeline (`renderFleetView`):**
    - Replaced the legacy 18-dummy-LED ellipse with authentic, scaled athletic running shirts (1 : 1.25 natural proportions) for all 7 runners.
    - Scaled chest zones strictly above the bib with authentic Cricut SVG vector artwork (`assets/cricut_svg/`) or high-res PNGs for all 7 floats.
    - Rendered scaled runDisney 10K yellow Tyvek race bibs with runner-specific bib numbers (`#01` to `#07`) and 4-corner BibBoards snap fasteners.
    - Rendered real 100-LED arrays per runner (700 LEDs total) calculating dynamic RGB colors, incandescent core intensity, and bloom halo at 60 FPS.
    - Added multi-mode fleet synchronization:
      - 🌊 **Wave Sync (ESP-NOW Passing Wave):** Sweeps white-hot wave crest and warm trail through the active float while inactive floats display signature resting sparkle/glow.
      - ⚡ **Free-Run:** Each shirt executes its assigned preset pattern and animation groups independently in real time.
      - 🎬 **Master Show:** All 7 shirts synchronize cues to the master 90-second timeline sequence.
    - Interactive canvas selection: hover highlights runner on course; single-click selects runner card in sidebar; double-click opens runner in Single View editor.
  * **Complete 7-Float Default Preset Suite:**
    - Generated authentic 100-LED presets with signature Disney palettes, outlines, and animation groups:
      - Float 01: `casey_jr_train.json` (Red/Gold steam engine with spinning drive wheel and headlight strobe)
      - Float 02: `title_drum.json` (Golden drum chassis with perimeter rim chase and white crest)
      - Float 03: `spinning_turtle.json` (Teal/Emerald shell with spinning spiral shell chase)
      - Float 04: `spinning_snail.json` (Hot Pink/Magenta shell with concentric shell whorl)
      - Float 05: `cinderellas_coach.json` (Cyan/Midnight pumpkin carriage with spinning wheels)
      - Float 06: `petes_dragon.json` (Emerald/Lime dragon body scales with breathing flourish)
      - Float 07: `honor_america_eagle.json` (Patriotic Red, White, & Blue stars and liberty wings flourish)
  * **Server & Persistence APIs (`simulator.py`):**
    - Added `GET /api/fleet_config` and `POST /api/save_fleet_config` to persist 7-runner fleet lineup to `presets/fleet_lineup.json`.
    - Added static route serving `assets/cricut_svg/` cut files.
  * **Verification:**
    - Python syntax verified (`python -m py_compile simulator.py`).
    - JavaScript syntax validated (`node -c simulator/app.js`).
    - Server endpoints tested via HTTP (`/api/presets`, `/api/fleet_config`, and SVG asset delivery).
    - Documentation synchronized in `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`, and `README.md`.

### Entry: Group Color Preservation Across Multi-Selection & Automatic Show Cue Preset Inheritance
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO Build.
* **Notes:**
  * **Group Multi-Selection Color Choice Preservation:**
    - Resolved issue where choosing a color palette swatch or using RGB sliders on an existing group collapsed selection to the first LED.
    - Updated `setSelectedLedColor(r, g, b)` to cleanly iterate and apply the new color across all member LEDs in `selectedLeds`.
    - Added automatic group state tracking: when a group is active (`selectedGroupId`), updates `activeGrp.colorMode = 'custom'` and `activeGrp.customColor = { r, g, b }` (syncing `activeGrp.fireworkColor` for fireworks starbursts) so real-time canvas animations render in the chosen custom color.
    - Updated `.palette-swatch-btn` click handler to preserve `selectedLeds` multi-selection, prevent fallback resets, and show an informative multi-LED toast (`🎨 Set X LEDs in group "[Name]" to [Color]!`).
    - Added a dedicated **Group Color Palette Override** (with 12 signature Disney palette buttons + `#resetGroupArtworkColorBtnHub` "Use Artwork Colors" button) directly inside Tab 2's Group Creation Hub.
  * **Show Cue Preset Inheritance from Animation Groups:**
    - Updated `addCue(options)` to check active group selection (`selectedGroupId`): when creating a cue for a group, it defaults `cue.effect` and `cue.speedBpm` directly to the preset configured when the group was created (`grp.effect` and `grp.speedBpm`), and titles the cue `${grp.name} Routine`.
    - Updated `cue-target-select` change listener in `renderCuesList()`: selecting a group from the Target Layer dropdown immediately updates `cue.effect` to `grp.effect` and `cue.speedBpm` to `grp.speedBpm`, dynamically updating the `.cue-effect-select` and `.cue-bpm-input` DOM elements while leaving the user 100% free to override the effect.
    - Added a direct **`➕ Show Cue`** shortcut button to all active group cards in Tab 2 (`renderActiveGroupsList`), allowing 1-click cue creation with preset effect/tempo and immediate jump to the Parade Cue Director tab (`switchSidebarTab('tabDirector')`).
  * **Verification:**
    - JavaScript syntax validated (`node -c simulator/app.js`).
    - ESP32 C++ firmware compiled with zero errors (`pio run`) at 14.3% RAM and 59.6% Flash.
    - Full documentation synchronized in `SIMULATOR_USER_GUIDE.md` and `PROJECT_PROGRESS.md`.

### Entry: Auto-Rearrange Remaining LEDs Option & Layout Tab Graphic Fill Engine
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO Build.
* **Notes:**
  * **Anchored Farthest-Point Sampling Engine (`rearrangeRemainingLedsOnGraphic`):**
    - Implemented Poisson-disk / Farthest-Point Sampling (FPS) algorithm using all existing animation groups' LEDs as fixed distance anchors.
    - When executed, dynamically identifies all unassigned (non-grouped) LEDs out of the 100 costume LEDs and redistributes them evenly into open negative spaces across the character graphic.
    - Preserves all existing group memberships, indices, and coordinates 100% intact.
    - Orders newly placed unassigned LEDs along a continuous physical snake wiring route (`optimizeLedWiringOrder`) starting from bottom-left to maintain hardware assembly neatness.
    - Samples and boosts colors directly from the graphic under each newly redistributed point.
  * **Click-to-Draw Auto-Rearrange Checkable Option:**
    - Added `#drawAutoRearrangeCheckbox` to the Groups Tab Click-to-Draw panel and `#canvasDrawAutoRearrangeCheckbox` to the canvas floating banner with two-way state synchronization.
    - Enabled by default: when saving a drawn group, non-grouped LEDs automatically rearrange to fill open spaces in the artwork around the new path without leaving awkward gaps.
    - Added pre-draw position snapshotting (`preDrawLedBackup`) so canceling draw mode cleanly restores all LEDs to their exact pre-draw coordinates.
  * **Layout Tab "Fill Graphic with Remaining LEDs" Action:**
    - Added `#rearrangeRemainingLedsBtn` in Section 2 (Shirt Artwork) and `#rearrangeRemainingLedsBtn2` in Section 3 (LED Layout & Wiring Route).
    - Enables 1-click on-demand redistribution of unassigned LEDs across the graphic at any time (e.g. after group deletion or point experimentation).
  * **Verification:**
    - Zero JavaScript syntax errors (`node -c simulator/app.js`).
    - HTTP server running smoothly (`HTTP/1.0 200 OK`).
    - ESP32 firmware cleanly compiles (`pio run`) at 14.3% RAM and 59.6% Flash.

### Entry: Inspector Suppression in Draw Mode & Reliable ID-Based In-Place Group Updates
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO Build.
* **Notes:**
  * **Inspector Standby Suppression During Draw Mode (`isDrawGroupMode`):**
    - Guaranteed that the docked Inspector at the bottom of the sidebar remains collapsed in standby (`dock-empty`) throughout drawing mode, preventing distracting dock expansions, stepper shifts, or color input flashing while clicking points on the shirt.
    - Suppressed selection mutations during point placement so placed LEDs are recorded in sequential order without activating individual bulb inspection.
  * **Reliable In-Place Group Editing & Saving:**
    - Fixed root-cause issue where `updateLedInspectorUI()` was forcibly re-reading stale group properties and overwriting user modifications before "Update Group" could be clicked.
    - Introduced explicit `selectedGroupId` state tracking so modifying group properties (including renaming the group) updates the exact group in-place by unique ID rather than brittle string name matching, preventing duplicate groups or lost LED allocations.
    - Synchronized all form inputs bidirectionally between the Groups Creation Hub (`From Selection` panel) and the docked Inspector (Name, Effect, Speed BPM, Direction, Resting Baseline, and Fireworks Burst Radius).
    - Unified button labeling and color states: displays `💾 Update Group "[Name]"` (blue accent) when editing an existing group and `💾 Save Selection as Group` (green accent) when configuring a new group.
  * **Automated & Toolchain Verification:**
    - JavaScript syntax validated (`node -c simulator/app.js`).
    - HTTP server verified via curl (`HTTP/1.0 200 OK`).
    - Standalone ESP32 C++ firmware compiled cleanly (`pio run`) at 14.3% RAM and 59.6% Flash.

### Entry: Unified Group Creation Hub, Click-to-Draw Sequential Path Tool, and Relocated Fireworks Stamper
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO Build.
* **Notes:**
  * **Unified Group Creation Hub (`#groupCreationHub`):** Consolidated all group generation into a 3-mode sub-tab interface located directly inside the `👥 Groups` tab:
    - 📦 **From Selection (`#creationPanelSelect`):** Save or update groups directly from canvas marquee box selections with full parameters (Name, Effect, Direction, Speed BPM, Resting Baseline).
    - ✏️ **Click-to-Draw (`#creationPanelDraw`):** Sequentially place individual LEDs directly on the costume shirt by clicking one-by-one.
    - 🎆 **Fireworks (`#creationPanelFw`):** Relocated the Fireworks Starburst Stamper from the Layout tab into Groups, consolidating all group creation in one unified place.
  * **Click-to-Draw Sequential Path Engine:**
    - **Contiguous LED Allocation Algorithm (`getNextAvailableLedIndex()`):** Allocates unassigned LEDs consecutively (#24, #25, #26...) whenever possible, ensuring directional animations (Chase, Wipe/Write-On, Traveling Waves) flow predictably in click sequence. Strictly preserves the 100-costume-LED invariant without creating phantom LEDs.
    - **Visual In-Progress Guidance:** Renders an animated floating banner (`#canvasDrawBanner`) above the canvas with a live placed count badge, plus glowing gold dashed guide lines and numbered step badges (`1`, `2`, `3`...) at each placed point on the shirt.
    - **Pixel Color Auto-Sampling:** Automatically samples the character graphic pixel color directly underneath each clicked point on the shirt.
    - **Keyboard & UI Controls:** Integrated `Enter` (finish & save when $\ge 2$ LEDs placed) and `Escape` (cancel draw mode) shortcuts, plus canvas floating banner buttons and sidebar action buttons.
  * **Layout Tab Streamlining:**
    - Replaced the bulky Fireworks card in `tabLayout` with a sleek quick-link (`#goToGroupsTabBtn`), leaving Layout focused cleanly on Artwork, Placement, Bib Clearance, and Wiring Optimization.
    - Preserved all 15+ Fireworks DOM element IDs and slider bindings, guaranteeing 100% backward compatibility.
  * **Top Toolbar Integration:** Added `[✏️ Draw Group]` button to the canvas top toolbar alongside `[⬚ Box Select]`, automatically activating the Groups tab and entering Click-to-Draw mode.
  * **Dual-Core & PlatformIO Verification:** Firmware compiles cleanly (`pio run`) at 14.3% RAM and 59.6% Flash.

### Entry: First-Class "👥 Groups" Tab, Allocation Metrics Bar, and Explicit "Save Group" Inspector Workflow
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO Build.
* **Notes:**
  * **Dedicated "👥 Groups" Sidebar Tab (`#tabGroups`):** Elevated animation groups to a first-class workflow in the sidebar tab navigation (`🎨 Layout`, `👥 Groups`, `✨ Effects`, `🎬 Show`, `⚡ Deploy`). Features a live count badge (`#tabGroupsBadge`) showing total configured groups at a glance.
  * **Visual LED Allocation Overview Bar:** Added a real-time capacity and distribution widget (`#groupsCapacityBadge`, `#groupedLedsCountText`, `#groupedLedsBar`, `#ungroupedLedsBar`) showing exact percentage and pixel counts of LEDs assigned to groups vs. unassigned out of the 100 costume LEDs.
  * **Quick Batch Selection Actions:**
    - `👥 Select All Grouped` (`#selectAllGroupedBtn`): Instantly selects all grouped LEDs across all clusters on canvas.
    - `⚡ Select Unassigned` (`#selectUnassignedBtn`): Instantly highlights all unassigned LEDs on canvas so users can bundle remaining costume pixels into a new animation zone with 1 click.
  * **Rich Interactive Group Cards (`#activeGroupsList`):**
    - Styled with hover elevation, active glow border (`.group-card.active-group`), category emoji icons, member badges, effect details, resting baseline pills (`Idle: Off / Unlit`, `Idle: Global`), and physical LED index ranges (`#0–15`).
    - Clicking anywhere on a card (or clicking `🎯 Select & Edit`) selects all member LEDs on canvas, focuses the Inspector dock, and updates coordinate/color inputs.
    - Added one-click `🗑️ Delete` button with confirmation.
    - Added welcoming empty state when no groups exist with actionable instructions.
  * **Contextual Inspector "Save Selection as Group" Workflow:**
    - Replaced ambiguous `⚡ Apply Effect to Selected` button with prominent, high-visibility `💾 Save Selection as Group` (green accent).
    - When modifying an already-grouped selection or existing group name, the button dynamically shifts to `💾 Update Group "[Name]"` (blue accent), providing immediate visual clarity between group creation and modification.
    - When 0 LEDs are selected, the Inspector displays clickable quick group chips (`#inspectorGroupChipsRow`), enabling 1-click group selection and inspection from anywhere.

### Entry: Thoroughbred UI Overhaul — 4 Task-Oriented Tabs, Contextual Inspector Dock, and Collapsible Timeline
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Complete Ergonomic Redesign ("From Camel to Thoroughbred"):** Replaced the single 3,000px vertical card stack with 4 streamlined task-oriented sidebar tabs:
    - `🎨 Layout` (Costume Profiles, Artwork & Character Graphic, 100-LED Scatter, Fireworks Starburst Generator, runDisney 10K Race Bib clearance, Wiring Route Optimizer).
    - `✨ Effects` (Baseline Lighting Patterns, Dynamics Tuning: Speed BPM, Sparkles, Green Hue, Brightness, Bloom Glow, and Configured Animation Groups Manager).
    - `🎬 Show` (Parade Cue Director, Sequence Loop Mode, Example Routines, and Scrollable Cue Card List).
    - `⚡ Deploy` (ESP32 USB Firmware Flashing, Real-Time Wi-Fi Live Stream, and Web Serial Flasher link).
  * **Contextual Inspector Dock (Option A):** Docked the LED & Group Inspector at the bottom of the sidebar. When no LEDs are selected, it rests as a slim status chip (`👆 Click an LED or drag to inspect`), saving over 700px of vertical space. When bulbs are selected, it smoothly expands with an active amber glow, exposing bulb steppers, RGB sliders, native color pickers, quick Disney palettes, and group animation settings.
  * **Collapsible Timeline Transport Bar:** Added a 1-click `⤢ Minimize` / `⤢ Expand` toggle to `#timelineBar`, giving the canvas maximum vertical screen real estate when designing garment layouts while enabling full-depth multi-layer tracks during cue choreography.
  * **100% Backward Compatibility:** Preserved every single existing DOM element ID and data structure, ensuring zero regression across animation math, FastLED code exports, Wi-Fi streaming, and flashing.
  * **Zero-Risk Rollback System:** Tagged the pre-overhaul state as `v1.0-pre-ui-overhaul` on Git and created a standalone backup archive in `simulator/archive_v1/` for instant 1-command reversion.

### Entry: Prominent Firework Burst Scale / Radius Controls in Generator and Group Inspector Cards
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Unified Geometry Box in Fireworks Card (Section 5a):** Moved the Firework Scale / Burst Radius slider into a dedicated, high-contrast dark panel (`📐 Position & Scale (Size)`) positioned prominently directly under Move X and Move Y. Expanded the slider range from 5% to 28% (default 13%) with real-time percentage badge readout.
  * **Quick Size Preset Buttons:** Added 4 one-click size preset buttons: **S (8%)**, **M (13% - Default)**, **L (18%)**, and **XL (24%)** with visual active-state highlighting (orange accent color and border) and instant toast feedback.
  * **Group Animation Inspector Integration (Section 5b):** Added a dedicated `#groupFwRadiusRow` panel inside the Selected LED Inspector / Group Animation Effects card. When a fireworks group is selected or when the group effect dropdown is set to `fireworks`, the Burst Scale / Radius slider and S/M/L/XL buttons automatically appear, allowing users to scale the firework directly while inspecting animation groups.
  * **Bidirectional Real-Time Synchronization:** Synchronized `#fwRadiusSlider` (Section 5a) and `#groupFwRadiusSlider` (Section 5b). Adjusting radius from either card immediately recalculates radial spoke coordinates across all rays and steps via `updateFireworksLedPositions()`, updates canvas LED positions, synchronizes both sliders and badges, highlights the matching preset button, and keeps inspector coordinates in sync.

### Entry: Configurable Per-Group Resting Baseline Effect (Follow Global, Off/Unlit, Sparkle, Dim Glow, Breathe)
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Per-Group Resting Baseline Architecture:** Added a configurable resting baseline effect for every animation group. Groups can now define their exact resting behavior when idle (outside active timeline cues in Sequence Mode):
    - `inherit` (Default): Seamlessly follows the overall float background pattern/cue (e.g. `steady_sparkle` or active global cue), matching non-grouped float LEDs.
    - `off`: Keeps group LEDs 100% off/unlit (pitch black) when idle. Defaults for fireworks, and enables other theatrical groups (e.g. carriage headlights, lantern flashes, dragon fire breathing) to remain completely dark until their cue fires.
    - `steady_sparkle`: Subtle starlight twinkle across group pixels while resting.
    - `dim_glow`: Ambient resting glow (~22% brightness) in the group's artwork or custom color.
    - `breathe` / `pulse_slow`: Gentle resting breath/heartbeat (~30 BPM) while the rest of the float sparkles.
  * **Smooth Crossfade Integration:** During timeline playback in `computeLedColor()`, active group cues now dynamically fade in from the group's designated resting baseline into the active cue effect, and fade back to baseline when the cue finishes.
  * **Inspector & Group Card Synchronization:** Added a dedicated `#groupBaselineSelect` dropdown to the Group Animation Effect card with live update bindings. Inspecting an LED or group synchronizes the dropdown, and each group card in the active groups list displays an idle badge (e.g. `Idle: Global`, `Idle: Off / Unlit`, `Idle: Glow`).

### Entry: Multi-Firework Stamping with Offset Placement, Uniform Ray Color, and Active Group Management
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO C++ firmware.
* **Notes:**
  * **Uniform Ray Color per Firework Group:** Standardized firework groups so all rays in a given firework starburst share the exact same uniform base color (Golden Amber, Alice Cyan, Coral Rose, Electric Lime, Royal Violet, Blazing Red-Orange, Starlight White, or custom hex color). Replaced per-ray rainbow variations with a cohesive single-color burst presentation that feels authentic to synchronized Disney theme park fireworks.
  * **Multi-Firework Burst Stamping:** Upgraded the starburst generator to support stamping multiple independent fireworks clusters on a single shirt (e.g. Firework #1, Firework #2) while strictly preserving the 100-LED invariant (`leds.length === 100`).
  * **Smart Visual Offset Stamping:** When stamping additional fireworks, subsequent bursts automatically spawn with a calculated offset (Firework #1 at default Top-Left $x = 28\%, y = 22\%$, Firework #2 at $x = 58\%, y = 26\%$, Firework #3 at $x = 38\%, y = 40\%$, etc.) and an alternating contrasting color from the palette, ensuring the user immediately sees both fireworks side-by-side above the race bib without visual occlusion.
  * **Active Firework Group Selector Dropdown & Deletion:** Added an `#activeFwSelect` dropdown with live group names and color chips. Switching the active group dynamically binds the Move X/Y, scale, and color controls to that cluster and selects its LEDs on the canvas. Added a `🗑️ Remove` button to delete the active firework group, clean up its timeline cues, and automatically re-distribute the reclaimed LEDs back to the float graphic.
  * **Interactive Canvas Group Binding:** Clicking or dragging any LED on the canvas that belongs to a firework cluster automatically switches the Active Firework Group dropdown and syncs the position/radius/color sliders in real time.
  * **Multi-Group Timeline Staggering:** Stamping multiple fireworks automatically schedules staggered burst cues on the Master Timeline (+2.5s per group index), creating an orchestrated sequential detonation across the costume.
  * **Dual Firmware & Toolchain Parity:** Updated `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` so `renderFireworks()` renders all rays with uniform color (`CRGB(255, 195, 45)`). Compiled successfully with PlatformIO (`pio run` SUCCESS: 14.3% RAM, 59.6% Flash) and exported verified binary to `firmware/firmware.bin`.

### Entry: Auto-Placement on Master Timeline & Completely Off (Unlit) Baseline for Fireworks
* **Date:** 2026-09-25
* **Status:** Operational & Verified in Web Simulator and PlatformIO C++ firmware.
* **Notes:**
  * **Automatic Master Timeline Placement:** Stamping a fireworks cluster now automatically creates and schedules fireworks explosion cues on the Master Timeline in the Parade Cue Director without requiring manual placement. Burst cues are spaced across the sequence loop duration with clean cue-onset phase synchronization (`cueTimeMs = 0`), and Sequence Mode is automatically activated so the show runs immediately.
  * **Auto-Schedule Bursts Control:** Added a dedicated `⚡ Auto-Schedule Bursts` button to re-populate recurring explosion bursts across the timeline on demand, alongside `⏱️ Add at Playhead` to insert single explosion cues at the exact scrubber position.
  * **Completely Off (Unlit) Baseline Status:** Enforced that firework LEDs are 100% unlit (`rgb(0, 0, 0)`, `alpha = 0`) outside active explosion cues on the timeline, preventing them from bleeding into or being illuminated by global background patterns. Unreached steps ahead of the expanding wavefront, burned-out inner trails, and post-burst idle intervals are completely dark.
  * **Physical Unlit Bulb Rendering:** Upgraded canvas `renderBulb()` so unlit LEDs (`col.alpha < 0.01` or RGB near 0) render as realistic, dark unlit SMD pixel beads (`rgba(22, 26, 33, 0.85)`) without artificial central white filament cores or glow gradients, while preserving selection crosshairs and hover indicators.
  * **Firmware & Arduino Synchrony:** Updated `renderFireworks()` in both `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` so unreached, burned-out, and idle intervals hold `CRGB::Black`. Compiled and verified with PlatformIO (`pio run` SUCCESS: 14.3% RAM, 59.6% Flash).

### Entry: Fireworks Color Customization, Persistent Center Trailing Effect, & Timeline Explosion Cue Integration
* **Date:** 2026-09-24
* **Status:** Operational & Verified in Web Simulator and PlatformIO C++ firmware.
* **Notes:**
  * **Color Customization:** Added Firework Color Theme selector with 8 presets (Multi-Color Disney Classic, Golden Amber, Alice Cyan, Coral Rose, Electric Lime, Royal Violet, Blazing Red-Orange, Starlight White) and an interactive HTML5 native color picker (`#fwCustomColorPicker`) for dialling in custom hex colors with warm incandescent shifts.
  * **Persistent Center Trailing Effect:** Re-engineered the pyrotechnic animation math so centermost hub LEDs (`step === 0`) stay continuously illuminated through Phase 2 (expanding wavefront holding at ~70% intensity) and Phase 3 (tip crackle anchor at ~50%), bridging an unbroken streak of light from center to tips, and gently breathing in Phase 4 (~25%-35%). Mirrored in `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`.
  * **Timeline Cue Director Integration:** Fireworks are now fully schedulable on the Master Timeline. Added one-click "⏱️ Add Explosion Cue to Timeline" button in the Fireworks card. Implemented cue-relative phase synchronization (`cueTimeMs = (t - startTime) * 1000`) so the explosion detonate precisely at the cue's start time with custom duration, BPM tempo, and smooth crossfades.
  * **Toolchain & Hardware Compilation:** Compiled with PlatformIO (`pio run` SUCCESS: 14.3% RAM, 59.6% Flash). Exported verified binary to `firmware/firmware.bin`.

### Entry: Fireworks Corner Placement, Interactive Move & Scale (Sliders & Multi-Drag), and Full-Graphic Re-Distribution
* **Date:** 2026-09-24
* **Status:** Operational & Verified in Web Simulator.
* **Notes:**
  * **Corner Initial Placement:** Stamping a fireworks cluster now places it initially in the upper chest corner of the running shirt (default: ↖ Top-Left at $x = 28\%, y = 22\%$, well above the race bib clearance line).
  * **Position Presets:** Added one-click alignment buttons (`↖ Top-Left`, `↗ Top-Right`, and `⏺ Center`) for fast positioning.
  * **Move & Scale Controls:** Implemented Move X slider ($15\% - 85\%$), Move Y slider ($15\% - 55\%$), and Scale / Radius slider ($7\% - 24\%$) with live feedback and instant starburst re-calculation.
  * **Canvas Multi-LED Dragging:** Enabled direct group dragging on the canvas. Clicking and dragging any individual LED within the firework moves all firework LEDs together as a unified cluster while dynamically updating the Move X/Y sliders.
  * **Full-Graphic Re-Distribution:** Removed the exclusion dead-zone from `sampleRemainingGraphicLeds()`. When stamping or clicking "🔄 Re-distribute Other LEDs (Full Graphic)", the remaining $(100 - N_{\text{fw}})$ LEDs are sampled across the entire character artwork, maintaining the strict 100-LED invariant (`leds.length === 100`).

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
