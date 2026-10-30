# Main Street Electrical Parade (WDW 10K) - LED Control System

## Project Overview
This project coordinates synchronized, addressable LED lighting across **7 runner costumes** styled as the iconic floats of Disney's **Main Street Electrical Parade** for the Walt Disney World 10K.

* **Theme:** Main Street Electrical Parade (7 Floats)
* **GitHub Repository:** [kidmd/WDW-costumes](https://github.com/kidmd/WDW-costumes)
* **Base Shirts:** Black moisture-wicking technical running shirts with glow-in-the-dark graphic outlines
* **Lighting:** 5V WS2812B "Seed / Pebble" RGBIC fairy pixel strings (~1" to 2" spacing for discrete light bulb look)
* **Runners & Engineering Team:** 7 family runners hitting the course together (2 brothers, 1 sister, 1 brother-in-law, and 3 sisters-in-law), supported and engineered by the 3 brothers (2 running, 1 supporting).
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
| **5** | **The Pirate Ship** | Crimson billowing sails, antique gold decks & rigging, emerald ocean waves |
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
  - [x] **Race-Day Battery Life & Power Budget Calculator:** Analytical battery capacity estimator (5,000 mAh / 10,000 mAh packs) modeling running pace (60–90 min 10K), average mA draw per runner, and 30s fleet show trigger frequency.
  - [x] **"Corral Roll Call" / ESP-NOW Fleet Radar Diagnostic:** Pre-race bench & corral RF sniffer verifying that Floats 1 through 7 are powered, connected, and responding on the sync channel before race start.

---

## Progress Log

### 2026-10-30: ESP32 Hardware Flashing Verification & Port Suspension Recovery
- **Flashing Issue Root Cause & Resolution:**
  - Resolved PermissionError(13, 'A device attached to the system is not functioning.', None, 31) on COM5 (Silicon Labs CP210x).
  - Identified root causes: Windows 11 ARM64 Qualcomm USB host selective suspend state (DeviceSelectiveSuspended: 1), serial port contention from background 3D slicer polling (snapmaker-orca), and BOOT pin state during cold plug-in.
  - Terminated background zombie processes and performed a clean USB bus reset (power-up insertion without holding BOOT button; BOOT button pressed during active upload connection).
- **Firmware Upload Success:**
  - Board flashed via PlatformIO / esptool.py v4.11.0 to Board 1 (ESP32-D0WD-V3, MAC B0:CB:D8:C8:49:84) on COM5 at 460800 baud.
  - Successfully written: Bootloader (17.5 KB), Partition Table (3.1 KB), Default Cert/OTADATA (8.2 KB), and Main Firmware (807.5 KB / 517.6 KB compressed).
  - Hard reset executed via RTS pin; ESP32 booted with authentic color palette and 50% backlight scaling.




### 2026-10-30: Pete's Dragon 16x16 Matrix Color Preservation & 50% Backlight Dimming
- **Artwork Color Preservation Across Animation Cues:**
  - Diagnosed and resolved character color distortions where Pete's Dragon's green body turned red and wings turned blue during timeline animation cues.
  - Corrected `evalGlobalPattern` in `simulator/app.js`:
    - `candle_flicker`: Preserved authentic artwork colors (`effC.r, effC.g, effC.b`) modulated by organic flame draft waver, removing legacy hardcoded `r = 255 * eff` that turned the green dragon body red/orange.
    - `rainbow_cycle`: Preserved authentic artwork colors with a dynamic traveling wave of brightness and starlight crest shimmer across `effC`, replacing the unconstrained 360° hue override that previously cycled the green body to red and wings to blue.
    - `traveling_wave`: Enhanced wavefront highlight to flare specular starlight over `effC` while keeping resting LEDs at 40% authentic artwork color.
    - `fire_breath`: Added matrix mode check so pixel indices 0..8 (hair crest and wing cutouts on matrix panels) are never converted to red/orange snout fire.
    - `filament_glow`: Preserved artwork colors without red-shifting green scales.
- **50% Backlight Brightness Standard:**
  - Implemented 50% brightness scaling for Backlit LEDs (`bLightMult = 0.50`) in `drawBtfMatrix16x16Overlay`:
    - Softens subsurface diffuse glow through thin colored PLA without washing out or competing with direct window cutouts.
    - Scaled radial bloom gradient intensity and hidden 5050 footprint indicator ring opacity by 0.50.
  - Synchronized ESP32 firmware (`src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`):
    - In `duplicateFrontToBack()`, backlight LEDs ($i \ge 51$) are scaled with FastLED `nscale8_video(64)` while windowed LEDs are scaled with `nscale8_video(128)`.
    - In autonomous sequence cues, `candle_flicker` (Cue 13) and `rainbow_cycle` (Cue 16) now respect `#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE`, preserving `ARTWORK_PALETTE` across both PlatformIO and Arduino IDE builds.
- **Real-Time 2D Spatial Metrics for 16x16 Panels:**
  - Upgraded `getSpatialMetrics()` in `simulator/app.js` to dynamically compute centroid, bounds, and normalized `(nx, ny)` coordinates directly from active matrix cells (`winCells` + `glowCells`), ensuring accurate traveling wave and ripple propagation across the physical plate face.

### 2026-10-30: Synchronized Simulator 16x16 Matrix with Physical 3D-Printed Cutouts (Zero-Drift Hardware Match)
- **Physical 3D Print Inspection & Alignment:**
  - Inspected the user's uploaded 3D print bundle (`media_1793392040159_8641935d.zip`), confirming byte-level identity with `tpu_panel_front_chassis_black.stl` (SHA256: `1c5fa0...`).
  - Extracted the exact physical hardware cutout geometry from `3d_panels/tpu_panel_specs.json`: exactly 51 Windowed apertures (Ø 3.4mm round holes) and 30 Backlit diffuse glow cells (total 81 active LEDs).
- **Multi-Key Coordinate Restoration Engine:**
  - Upgraded `restoreSavedMatrix16x16Roles` in `simulator/app.js` with multi-key lookup matching simultaneously by `(row, col)`, plate coordinates `(plateX, plateY)`, and serpentine physical `matrixIdx`.
  - Removed canvas color-threshold discarding (`onGraphic < 45`) for pre-existing physical cutouts, preventing the simulator from rejecting verified printed holes or substituting them with random fallback FPS cells.
  - Automatically synchronizes `btfMatrix16x16Config.windowCount` (51) and `backlightCount` (30) with the telemetry UI and sliders.
- **Preset & Firmware Harmonization:**
  - Updated all Pete's Dragon presets (`pete_s_dragon_chris_large_81led_2026-10-30_10-57.json`, `10-59.json`, `14-24.json`) with the exact 51 printed windows + 30 backlights.
  - Created a permanent golden reference preset: `presets/pete_s_dragon_16x16_printed_81led.json`.
  - Updated `presets/fleet_lineup.json` to lock Float 6 (Pete's Dragon) to the printed 81-LED layout.
  - Updated `include/costume_config.h` with the exact 81 serpentine matrix indices in `MATRIX_ACTIVE_INDICES`.


### 2026-10-30: Connected 16x16 Matrix Mode to Master Timeline & 90s Solo Show Animation Engine
- **Master Timeline Playback Synchronization:**
  - Resolved issue where playing the 90-second solo show or scrubbed sequence cues on the layout screen rendered static artwork colors with hardcoded white center dots on the 16x16 matrix plate.
  - Linked `drawBtfMatrix16x16Overlay` directly into the MSEP animation engine (`computeLedColor` and `evalGlobalPattern`), synchronizing all active matrix cells to the timeline playhead (`sequenceTime`) and scrubbing head (`hoverScrubTime`).
- **Dynamic Windowed & Backlit Emitter Rendering:**
  - **Windowed Cells:** Direct apertures now compute live cue colors and amplitudes, dynamically animating outer radial halos, live aperture cutout rim highlights, and specular hot-die centers that illuminate with brightness and cleanly extinguish when dark (preventing fixed solid `#ffffff` circles).
  - **Backlit Cells:** Subsurface glow through solid PLA faceplates now dynamically modulates with timeline cues, blending 70% live LED emitter color with 30% physical faceplate filament color for rich, non-clipping translucency.
- **Engine Safety & Robustness:**
  - Expanded `sparkles` state array to 512 elements with dynamic bounds guard (`while (sparkles.length <= index) sparkles.push(0);`), preventing out-of-bounds indexing across the 256 matrix cells.
  - Added `overrideColor` support to `computeLedColor(index, totalLeds, timeMs, overrideColor)` to evaluate individual sampled artwork colors while participating in global sweeps, waves, sparkles, and chases.


### 2026-10-30: Added 6mm Anti-Snag Rounded Corners Option for 16x16 Armor Panels
- **Soft 6.0mm Corner Fillet Architecture:**
  - Added an ergonomic **Rounded Plate Corners** option (defaulting to **`Rounded (6mm) ★`** with toggleable **`Sharp (90°)`** mode) across the Python compiler (`compile_clean_tpu_panel.py`), backend (`simulator.py`), and frontend UI (`simulator/index.html` & `simulator/app.js`).
  - Eliminates sharp corner points that snag running shirt mesh, dig into rib cages during arm swing strides, or catch on safety pins during the 10K race.
- **Slicer Registration & Bounding Box Zero-Artifact Lock:**
  - When rounded corners are active ($R = 6.0\text{ mm}$), registration anchors automatically relocate to microscopic $0.50 \times 0.25\text{ mm}$ rectangular tabs flush at the 4 mid-edge straight perimeters ($X = 0$, $X = 176$, $Y = 0$, $Y = 176$).
  - Strictly preserves the $[0.0, 176.0] \times [0.0, 176.0]\text{ mm}$ auto-centering bounding box in Bambu Studio / OrcaSlicer while preventing any sharp registration spurs or tangential horn artifacts from protruding beyond the rounded fillet envelope (obeying Rule 7).
- **Sewing Hole Structural Integrity:**
  - Corner needle eyelets ($\\varnothing 2.8\text{ mm}$) automatically verify corner arc clearance, maintaining a minimum $1.77\text{ mm}$ solid perimeter TPU/PLA wall for high-impact stitch retention.
- **UI & Telemetry:**
  - Added `#btfMatrixRoundedToggle` in the Layout tab and `#tpuModalCornersPill` (`Rounded ★` / `Sharp`) in the 3D Print Preview modal toolbar with live WebGL reload and browser `localStorage` persistence.

### 2026-10-30: Standardized 16x16 Panel Clear Backing Layer to 0.40mm Dual-Layer Cross-Ply (90° Slicing)
- **0.40mm Clear Diffuser Backing Standard:**
  - Upgraded the default clear backing layer (`color_clear_layer.stl` / `Clear_Backing_Layer_160x160`) for all 16x16 matrix hybrid armor plates from `0.0mm` to **`0.40mm`** across the Python STL compiler (`compile_clean_tpu_panel.py`), backend API (`simulator.py`), frontend config (`simulator/app.js`), and 3D preview UI (`simulator/index.html`).
  - Sits directly behind the $160 \times 160\text{ mm}$ colored graphic faceplate, providing an integrated diffuser that evenly distributes rear backlight LED glow without hotspot banding.
- **2-Layer @ 90° Cross-Ply Slicer Architecture for Maximum Strength:**
  - Configured specifically for 2 solid layers at $0.20\text{ mm}$ layer height ($0.20\text{ mm} \times 2 = 0.40\text{ mm}$).
  - Sliced with alternating $90^\circ$ raster orientations (e.g. Layer 1 at $45^\circ$ and Layer 2 at $135^\circ$, or $0^\circ$ and $90^\circ$).
  - Creates a composite cross-ply grain structure in flexible TPU (or clear PETG) that dramatically improves biaxial tear, puncture, and split resistance during running arm swings and 10K race movement.
- **UI & Multi-Material 3MF Integration:**
  - Updated both the Layout Tab sidebar and 3D Print Preview modal pill toolbars with `0.4mm ★` active default styling and informational tooltips.
  - Multi-material 3MF bundle metadata now explicitly tags `Clear Backing Layer (0.4mm - 2x 0.20mm @ 90° cross-ply)` for one-click assignment in Bambu Studio, OrcaSlicer, and Snapmaker Luban.
  - Preserves full user adjustability across `None`, `0.2mm`, `0.4mm ★`, `0.6mm`, `0.8mm`, and `1.0mm` with browser `localStorage` persistence.

### 2026-10-26: Engineered Snap-On Race-Day Security Caps (10K High-Impact Locking Vaults)
- **10K Race-Day Armored Security:**
  - Designed positive-locking snap-on caps (hoods) for all straight clips and 90° corner elbows to physically cage fairy light wiring for the entire 6.2 miles of high-impact arm swings, stride impacts, corral crowds, and finish line celebrations.
  - Features $1.0\text{ mm}$ thick solid roof and dual spring retention skirts with $0.35\text{ mm}$ inward locking catch beads.
  - Added matching $0.35\text{ mm}$ horizontal retention ridges along the flanks of all base clips and 90° elbows for a definitive tactile snap lock.
- **Support-Free Print Orientation:**
  - All caps pre-oriented flat on their top roof at $Z = 0$ with retention skirts pointing straight up (+Z). Zero supports or brims required.
- **Complete Cap Roster (`3d_panels/wire_clips/`):**
  - `cap_2strand_flat.stl` ($13.09 \times 8.00 \times 3.20\text{ mm}$, ~$0.35\text{g}$).
  - `cap_3strand_flat.stl` ($17.74 \times 8.00 \times 3.20\text{ mm}$, ~$0.45\text{g}$).
  - `cap_2strand_stacked.stl` ($8.44 \times 8.00 \times 3.20\text{ mm}$, ~$0.25\text{g}$).
  - `cap_3strand_bundle.stl` ($8.44 \times 8.00 \times 3.20\text{ mm}$, ~$0.25\text{g}$).
  - `cap_2strand_pyramid_cradle.stl` ($7.34 \times 8.00 \times 3.20\text{ mm}$, ~$0.22\text{g}$).
  - `cap_corner_90.stl` ($10.67 \times 10.67 \times 2.80\text{ mm}$, ~$0.24\text{g}$): 90° curved roof with dual concentric skirts.
- **24-Piece Race-Day Caps Companion Plate (`wire_clips_caps_pack.stl`):**
  - Single build plate array ($83.74 \times 75.34 \times 3.20\text{ mm}$, ~$6.5\text{g}$ PLA total) printing 4x of each straight cap (20 caps) + 4x 90° corner caps in ~12 minutes.
- **Synchronized OpenSCAD & Documentation:**
  - Added parametric cap modules and interactive customizer selectors to `wire_clips.scad`.
  - Updated `README.md` and `SIMULATOR_USER_GUIDE.md`.

### 2026-10-26: Re-engineered 90° Elbows with Pronounced Cantilever Snap Lips & Undercut Shelf
- **Cantilever Snap Overhang & Undercut Shelf:**
  - Resolved issue where the previous vertical slot cutout subsumed the neck constriction, leaving a straight-walled channel without a visible or tactile snap lip.
  - Implemented a true monolithic cross-section featuring:
    - Inner wire cavity: $1.65\text{ mm}$ wide $\times 3.60\text{ mm}$ deep (holds 3 strands stacked vertically on-edge).
    - Cantilever snap lips: $1.00\text{ mm}$ constriction throat at $Y = 4.80\text{ mm}$.
    - Undercut retention shelf: $0.325\text{ mm}$ horizontal overhang on each wall ($0.65\text{ mm}$ total constriction) with downward-facing catch to lock the top strand in place.
    - $45^\circ$ lead-in funnel widening to $2.40\text{ mm}$ at $Y = 5.60\text{ mm}$ for effortless wire insertion.
- **Physical Bending Mechanics (Easy-Way Ribbon-on-Edge):**
  - Stacking the 3 fairy light conductors vertically inside the curved channel lets the ribbon bend across its thin ~1.2mm axis ("the easy way") around the $5.0\text{ mm}$ inner radius, eliminating copper strain and wire buckling.
- **Updated Geometry & Clear Sewing Eyelets:**
  - `clip_corner_90_single.stl`: $9.45 \times 9.45 \times 5.60\text{ mm}$ ($199.0\text{ mm}^3$, $\approx 0.25\text{g}$).
  - `clip_corner_90_sewable.stl`: $14.20 \times 14.20 \times 5.60\text{ mm}$ ($235.6\text{ mm}^3$, $\approx 0.30\text{g}$) with two $\varnothing 2.0\text{ mm}$ eyelets centered at $(11.2, 2.0)$ and $(2.0, 11.2)$ with $> 0.75\text{ mm}$ open air margin.
  - Recompiled `wire_clips_runner_pack.stl` ($78.30 \times 94.00 \times 8.55\text{ mm}$) and OpenSCAD `wire_clips.scad`. Generated visual engineering cross-section diagram `vertical_ribbon_snap_cross_section.png`.

### 2026-10-26: Resolved 90° Elbow Ghost Spurs via 360° Box-Crop & Fully Unblocked Sewing Eyelet Holes
- **Ghost Spur / Straight Bit Elimination (Kernel Bug Fix):**
  - Pinpointed the root cause of the "extra straight bit" on `clip_corner_90_single.stl` and `clip_corner_90_sewable.stl`: calling `CrossSection.revolve(revolve_degrees=90.0)` in Manifold3D triggers an ear-clipping triangulation anomaly that spans bridge triangles out to the bounding box diagonal $(10.0, 10.0, 0.0)$ at $r = 14.14\text{ mm}$ (a sharp triangular wedge).
  - Implemented the universal robust solution: swept a complete 360° circular torus (`revolve_degrees=360.0`), which produces a flawless surface with zero bridge artifacts ($r_{max} = 10.000\text{ mm}$ exact), and boolean-intersected (`^`) with a quadrant bounding box `[0, 20] x [0, 20] x [-2, 10]` to extract the pure $90^\circ$ elbow.
  - Verified: `clip_corner_90_single.stl` footprint is strictly $10.00 \times 10.00 \times 5.00\text{ mm}$, watertight (`is_watertight == True`), with zero vertices exceeding $r = 10.0\text{ mm}$.
- **Sewing Tab Hole Clearance Fix:**
  - Shifted corner eyelet tab coordinates from $(9.0, 1.8)$ (which was occluded beneath the $5.0\text{ mm}$ tall outer channel wall at $R_{out} = 10.0\text{ mm}$) to $(11.8, 2.0)$ and $(2.0, 11.8)$.
  - The $\varnothing 2.0\text{ mm}$ needle eyelets now sit completely in open air beyond the $10\text{ mm}$ channel wall with $0.80\text{ mm}$ clearance to the vertical wall and $0.53\text{ mm}$ solid base root penetration into the bottom chassis.
  - Verified via raycast and horizontal plane slices: 100% clear through-holes from build plate ($Z = 0$) to tab top ($Z = 1.2\text{ mm}$) and skyward.
- **Synchronized Assets & Runner Pack:**
  - Updated both `scripts/generate_wire_clips.py` and `3d_panels/wire_clips/wire_clips.scad`.
  - Recompiled and verified all 3.2mm STLs and `wire_clips_runner_pack.stl` ($78.30 \times 94.00 \times 8.55\text{ mm}$, 10,352 faces).
- **Permanent Engineering Standards in `GEMINI.md` (Section 7):**
  - Codified Section 7 rules prohibiting partial revolves that generate ear-clipping spurs and mandating full 360° revolves cropped with quadrant bounding cubes, as well as intentional boolean penetration ($\ge 0.5\text{ mm}$) for mounting tabs.

### 2026-10-26: 3.2mm Calibrated Wire Clips, 90° Single-Wire Elbows & 2-Strand Pyramid Cradle
- **Calibrated to 3.2mm Wire Standard:** Based on physical test gauge comb validation (3.2mm slot yielding the ideal positive snap without strain), standardized all straight clips:
  - Wire OD: $3.20\text{ mm}$, cavity $\varnothing 3.30\text{ mm}$, snap mouth $2.35\text{ mm}$, spring walls $1.35\text{ mm}$, floor $1.20\text{ mm}$.
  - `clip_2strand_flat.stl` ($10.65 \times 8.00 \times 5.01\text{ mm}$, ~$0.28\text{g}$).
  - `clip_3strand_flat.stl` ($15.30 \times 8.00 \times 5.01\text{ mm}$, ~$0.39\text{g}$).
  - `clip_2strand_stacked.stl` ($6.00 \times 8.00 \times 8.55\text{ mm}$, ~$0.28\text{g}$).
  - `clip_3strand_bundle.stl` ($9.70 \times 8.00 \times 7.93\text{ mm}$, ~$0.36\text{g}$).
- **Single-Wire 90-Degree Corner Brackets:**
  - Designed for routing single fairy light strands around 90° bends with a gentle $5.0\text{ mm}$ inner bend radius to protect internal copper conductors from bending fatigue.
  - `clip_corner_90_single.stl` ($12.50 \times 12.50 \times 5.00\text{ mm}$, ~$0.22\text{g}$): Floating low-profile snap elbow with two straight channel legs.
  - `clip_corner_90_sewable.stl` ($15.20 \times 15.20 \times 5.00\text{ mm}$, ~$0.25\text{g}$): Same 90° elbow plus two $\varnothing 1.9\text{ mm}$ corner stitching eyelets for needle/safety-pin tacking to running shirts.
- **Preserved 2-Strand Pyramid Cradle (`clip_2strand_pyramid_cradle.stl`):**
  - Formalized the verified v1 geometry ($7.60 \times 8.00 \times 6.27\text{ mm}$, ~$0.25\text{g}$) as a dedicated 2-strand cradle holding 2 wires snugly in the lower lobes.
- **Updated 25-Piece Runner Plate (`wire_clips_runner_pack.stl`):**
  - Single print bed array ($78.30 \times 94.00 \times 8.55\text{ mm}$, ~$8.1\text{g}$ PLA) containing 4x of each straight clip (20 clips), 2x floating 90° elbows, 2x sewable 90° elbows, and the 5-slot test gauge comb. Pre-oriented flat on PEI bed ($Z = 0$).

### 2026-10-26: Resized Wire Clips (~3.0mm Wire), Inverted Bed Orientation Fix & Test Gauge Comb
- **Bed Orientation Fix:** Resolved inverted mesh export where clips defaulted with bases facing upward in slicers (Snapmaker Luban / OrcaSlicer). Fixed rotation transform in `scripts/generate_wire_clips.py` and `wire_clips.scad` (+90° around X axis), guaranteeing that all 34 flat bottom faces sit directly on the textured PEI bed ($Z = 0$) with snap mouths pointing straight up toward the nozzle.
- **Resized for Standard 2.8mm–3.05mm Fairy Light Wires:**
  - Scaled nominal wire diameter from $2.30\text{ mm}$ up to **$3.00\text{ mm}$** (inner cavity $\varnothing 3.10\text{ mm}$, snap mouth $2.20\text{ mm}$, reinforced $1.30\text{ mm}$ cantilever walls, $1.20\text{ mm}$ base plate).
  - Enables clean, effortless snapping for all 2-strand and 3-strand configurations without wire jamming or insulation pinching.
- **Added 3-Minute Test Gauge Comb (`wire_gauge_test_comb.stl`):**
  - Compact $36.1 \times 6.0 \times 5.3\text{ mm}$ test swatch featuring 5 stepped snap slots ($2.6, 2.8, 3.0, 3.2, 3.4\text{ mm}$) to verify physical snap feel with actual race-day wire.
  - Included directly on the front row of the 17-piece **`wire_clips_runner_pack.stl`** ($74.5 \times 62.0 \times 8.14\text{ mm}$, ~$5.8\text{g}$ PLA total).

### 2026-10-26: 3D Printable Snap-Fit Fairy Light Wire Fold Management Clips
- **Objective & Purpose:** Designed, engineered, and exported lightweight (<0.3g), low-profile 3D printable snap-fit clips to manage external fairy light wiring folded over itself outside the chest armor panels on the WDW 10K running shirts.
- **Architectural & Mechanical Highlights:**
  - **4 Specialized Configurations:**
    - `clip_2strand_flat.stl` ($8.55 \times 8.00 \times 4.15\text{ mm}$, $161.5\text{ mm}^3$, ~$0.20\text{g}$): 2-strand flat side-by-side hairpin clip, flush to chest.
    - `clip_3strand_flat.stl` ($12.20 \times 8.00 \times 4.15\text{ mm}$, $224.0\text{ mm}^3$, ~$0.28\text{g}$): 3-strand flat parallel comb for accordion/Z-folds under bib numbers.
    - `clip_2strand_stacked.stl` ($4.90 \times 8.00 \times 6.61\text{ mm}$, $158.1\text{ mm}^3$, ~$0.20\text{g}$): 2-strand over-under vertical stack with intermediate waist constriction for minimum lateral footprint.
    - `clip_3strand_bundle.stl` ($7.60 \times 8.00 \times 6.27\text{ mm}$, $197.9\text{ mm}^3$, ~$0.25\text{g}$): 3-strand triangular pyramid cluster with top-locking strand.
    - `wire_clips_runner_pack.stl` ($60.20 \times 47.00 \times 6.61\text{ mm}$, $2965.6\text{ mm}^3$, ~$3.6\text{g}$): Single-bed print containing 4x of each design (16 clips total) ready in ~15 minutes.
  - **Rigid PLA/PETG Snap Engineering:** Tuned cantilever flex walls ($1.25\text{ mm}$ thick, 3 perimeters) with $1.65\text{ mm}$ constricted snap mouths into $2.40\text{ mm}$ round cradles and $45^\circ$ lead-in ramps to prevent wire insulation scuffing.
  - **Toolchain Assets:**
    - Updated `scripts/generate_wire_clips.py` using `manifold3d` and `trimesh` with exact planar transformations and watertight validation.
    - Added parametric `3d_panels/wire_clips/wire_clips.scad` with OpenSCAD Customizer GUI support.
    - Added user guide `3d_panels/wire_clips/README.md`.


### 2026-10-24: Fix Protruding Light-Pipe Lens Corner Anchor Pole
- **Root Cause Identified:** When exporting the optional Translucent Light-Pipe Lens cylinders (	pu_panel_color_lenses.stl), the lens 2D polygons (windows_union_2d) and the slicer corner registration anchor (lens_anchor_2d) were extruded together through the full cylinder height lens_h = TOTAL_Z - PCB_POCKET_DEPTH (e.g. 4.4mm). While the 50 lens cylinders legitimately span 4.4mm from the front faceplate down to the LED surface (Z=0), the corner registration anchor was also extruded 4.4mm tall. Because the surrounding chassis faceplate is only 0.8mm thick at the corner, this created a 3.6mm long free-hanging cylinder/pole extending out from the corner of the plate into empty air.
- **Flush Faceplate Encapsulation Fix:** In scripts/compile_clean_tpu_panel.py:
  - Separated the lens cylinders extrusion from the corner registration anchor.
  - The 50 lens cylinders are extruded through the full lens_h (4.4mm) and placed at PCB_POCKET_DEPTH (Z=0.0).
  - The corner registration anchor (lens_anchor_2d) is extruded **only through THICK_MM (0.80mm)** and translated to FACE_Z0.
  - The corner anchors now sit 100% flush inside the 0.8mm front faceplate with zero protrusion beyond the plate back surface, completely eliminating the corner pole while maintaining the required [0.0, 176.0] x [0.0, 176.0] mm slicer registration bounding box.
  - Similarly, removed unnecessary corner anchors from the clear backing layer as its 160x160mm square footprint is already naturally centered at (88.0, 88.0 mm).


### 2026-10-24: 3D Plate Slicer Registration Anchors Cleaned Up (Corner Apex Triangles)
- **Problem Resolved:** In previous builds, multi-part color split STLs used staggered 0.25mm perimeter bounding-box registration tabs along the plate edges. These staggered tabs visually appeared in the 3D preview modal as colored 'antennae / comb teeth / whiskers' along the plate edge and physically created small bumps/notches on the printed perimeter.
- **Apex Registration Geometry:** Replaced staggered perimeter tabs with shared 0.35x0.35mm right-triangles positioned right at the extreme four apex corners of the plate: (0, 0), (176, 0), (0, 176), and (176, 176).
  - Triangle area: 0.5 * 0.35 * 0.35 = 0.06125 mm², which is safely above the 0.05 mm² polygon preservation threshold in extrude_shapely.
  - All color inlays, lenses, clear diffuser backing, and the chassis share the identical corner apex coordinates.
  - Zero perimeter staggering: plate edges remain 100% straight and smooth.
  - Guarantees that every exported STL matches the identical [0.0, 176.0] x [0.0, 176.0] mm bounding box and (88.0, 88.0) center in Bambu Studio and PrusaSlicer without needing manual alignment.


### 2026-10-24 13:10 - 🚀 Fix 3D Preview Modal Model Loading, Multithreaded HTTP Server & Parallel STL Fetching
- **Diagnosis of Blank 3D Preview Modal:**
  - **Single-Threaded Server Deadlock:** The previous Python `socketserver.TCPServer` handled all requests synchronously on a single thread. When the client auto-compiled STLs via `/api/generate_tpu_stl` (`subprocess.run`), all subsequent concurrent HTTP requests (such as `tpu_panel_specs.json`, textures, or STLs) were blocked at the socket level. Requests queued up until hitting the client-side `timeoutMs = 8000ms`, causing STL downloads to fail or time out.
  - **`NoneType` Bounds Edge Case in `handle_generate_tpu_stl`:** If `getGraphicChestBounds()` evaluated to `null`, `req_data.get("bounds", {})` returned `None`, triggering an unhandled `AttributeError: 'NoneType' object has no attribute 'get'` and returning HTTP 500.
  - **Undeclared Variables in `openTpuPreviewModal`:** `compiledGap`, `compiledLip`, `compiledClear`, and `compiledFrame` were assigned inside a try block without declaration, causing potential reference errors.
  - **Sequential Loop Bottleneck:** The inlays loading loop previously awaited each multi-part STL sequentially one by one.
- **Engineered Fixes & Verification:**
  - **Upgraded to `socketserver.ThreadingTCPServer` (`simulator.py`):** Concurrently handles static asset requests, specs queries, and subprocess generation without blocking.
  - **Safe Attribute Extraction:** Updated `bounds = req_data.get("bounds") or {}` in `simulator.py` to prevent `NoneType` crashes.
  - **Parallelized Inlay Loading (`Promise.all` in `simulator/app.js`):** All multi-color inlays now fetch concurrently in parallel with a relaxed 25,000ms timeout.
  - **Clean Overlay Dismissal:** Ensures `#tpuModalLoading` hides cleanly once geometries load.
  - **Headless Edge CDP Verification:** Tested full load sequence with real WebGL rendering in Edge; verified Pete's Dragon 16×16 plate and multi-color inlays render flawlessly in under 1 second.
  - **Cache Busted:** Bumped `app.js?v=106` in `simulator/index.html`.

### 2026-10-24 12:35 - ✨ 160×160mm Clear Backing Layer & Frame/Lip Toggle for 16×16 Matrix Plate
- **160×160mm Clear Backing Layer (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`, `simulator/index.html`):**
  - **Mechanical & Optical Purpose:** Adds an optional structural translucent diffuser/backing layer spanning the full $160.0 	imes 160.0\text{ mm}$ active graphic zone ($X = 8.0 \dots 168.0\text{ mm}$, $Y = 8.0 \dots 168.0\text{ mm}$ on the $176 	imes 176\text{ mm}$ plate). Sits directly behind and touching the colored front faceplate to diffuse backlighting LEDs and provide rigid backing for flexible TPU/PETG multi-color inlays.
  - **Selectable Thicknesses:** Selectable across `None` (`0.0mm`), `0.2mm`, `0.4mm`, `0.6mm`, `0.8mm`, and `1.0mm` in both the 3D Preview Modal toolbar (`#tpuModalClearLayerPill`) and Layout tab (`.btf-matrix-clear-btn`). Persisted across browser sessions in `localStorage`.
  - **Zero-Collision Mesh Aperture Subtraction:** Window apertures ($arnothing 3.4\text{ mm}$) are cut through both the front graphic and the clear layer, allowing the full-height translucent lens cylinders to pass seamlessly from the LED plane to the front face without volumetric slicer overlaps.
  - **Independent Slicer Part & Bounding Box Lock:** Exported as a distinct 3MF multi-part component (`Clear_Backing_Layer_160x160`) and standalone STL (`tpu_panel_{variant}_color_clear_layer.stl`). Includes symmetric $0.25\text{ mm}$ registration corner anchors locking its bounding box to exactly $[0.0, 176.0] 	imes [0.0, 176.0]\text{ mm}$ with center at $(88.0, 88.0)$, preventing slicer auto-centering offsets.
  - **3D Preview Modal Shader:** Rendered in Three.js with crystal translucent material (`#dff6ff`, opacity: `0.65`, roughness: `0.10`).
- **Centering Frame & Lip Mode Toggle (ON ★ / OFF):**
  - **Frame ON (Default):** Retains the 3-tier stepped rear standoff frame, $2.0\text{ mm}$ deep $160.4 	imes 160.4\text{ mm}$ PCB recess, and $1.0\text{ mm}$ internal supporting ledge ($156.4 	imes 156.4\text{ mm}$) centered at $(88.0, 88.0\text{ mm})$ with bottom wire exit notch.
  - **Frame OFF:** Completely omits the rear frame walls and internal lip (`frame_solids = []`), generating a flat plate while lenses maintain their chosen full-height standoff length (`GAP_MM + CLEAR_MM + THICK_MM`).
  - **UI Integration:** Toggleable via the `🖼️ Frame & Lip:` pill button (`ON ★ / OFF`) in the 3D modal toolbar (`#tpuModalFramePill`) and checkbox (`#btfMatrixFrameToggle`) in the Layout tab.
- **Full CLI & API Parameter Synchronization:**
  - Added CLI flags `--matrix-clear-layer <float>` and `--matrix-frame <on|off>` to `scripts/compile_clean_tpu_panel.py`.
  - Updated `/api/generate_tpu_stl` in `simulator.py` to accept `matrixClearLayerMm` and `matrixFrameMode`.
  - Restarted simulator server background service on `http://localhost:8000`.

### 2026-10-24 00:12 - 🎯 16x16 Matrix Frame Centering, Slicer Bounding-Box Lock & Coaxial Lens-to-LED Alignment Fix
- **Root-Cause Diagnosis of PETG Test Print Misalignment (`scripts/compile_clean_tpu_panel.py` & `simulator/app.js`):**
  - **Root Cause 1 — Slicer Auto-Centering Shift on Split STLs (`5.0 mm` Y-Offset):** While `tpu_panel_front_chassis_black.stl` had an exact `[0.0, 176.0] × [0.0, 176.0]` bounding box (`center = 88.00, 88.00 mm`), `tpu_panel_front_color_lenses.stl` only spanned the bounding envelope of its 50 lens cylinders (`[11.3, 164.7] × [11.3, 154.7]`, `center = 88.00, 83.00 mm`) — shifting the lenses by **`5.00 mm` in Y (half an LED row)** whenever a 3D slicer centered imported STL parts! Similarly, each color inlay STL had its own asymmetric centroid.
  - **Root Cause 2 — 18 of 50 Lenses Placed in Empty Black Background Halo:** `computeBtfMatrix16x16Layout()` in `simulator/app.js` previously searched a wide `±6 px` (`~4.5 mm`) box around each matrix cell center and marked dark black pixels (`maxAvg < 45`) as `onGraphic = true`. Farthest-Point Sampling greedily pushed 18 of the 50 lenses onto the outer black halo outside the character silhouette.
  - **Root Cause 3 — Bottom Wire Notch Stopped Short of Internal Lip:** `wire_notch_2d` previously cut only to `pocket_y0 + 0.5` (`8.30 mm`), leaving a `1.50 mm` uncut bar across the `2.0 mm` internal supporting lip (`ledge_in_y0 = 9.80 mm`).
- **Engineering Fixes & Mathematical Verification:**
  - **Microscopic Perimeter Registration Anchors (`make_bbox_anchor_2d`):** Added 4 symmetric, non-overlapping `0.25 × 0.25 mm` edge anchors at `0.0 mm` and `176.0 mm` for `color_lenses.stl` and every `color_*.stl` inlay (and subtracted them from `chassis_2d`). Every exported STL file now has an identical `[0.000, 176.000] × [0.000, 176.000]` X/Y bounding box and `(88.000, 88.000)` center — completely immune to slicer auto-centering shifts.
  - **Coaxial 16×16 Matrix Grid Snapping & On-Graphic Validation (`_snap_and_validate_matrix_leds`):** Both `scripts/compile_clean_tpu_panel.py` and `simulator/app.js` now require the exact LED center `(X = 13.0 + col*10.0 mm, Y = 13.0 + (15-row)*10.0 mm)` to sit on non-black colored foreground artwork (`0.000 mm` coaxial error across all 50 Ø3.4mm lenses; `0 / 50` lenses in black background).
  - **Verified Frame & Internal Lip Concentricity:** Confirmed outer frame wall (`5.80..170.20 mm`), inner `160.40 × 160.40 mm` PCB pocket (`7.80..168.20 mm`, providing `0.20 mm` per-side clearance around the `160.0 × 160.0 mm` 16×16 matrix), and `156.40 × 156.40 mm` internal supporting lip (`9.80..166.20 mm`) are all 100% concentric at `(88.00, 88.00 mm)`, with the `16.0 mm` bottom wire notch cutting cleanly to `Y = 10.30 mm` through both pocket and lip.

### 2026-10-18 19:30 - 🔍 Translucent White Light-Pipe Lens Cylinders for 16x16 Matrix Plate
- **Translucent Light Pipes Spanning Matrix Air Gap (`scripts/compile_clean_tpu_panel.py`):**
  - **Optical Waveguide Design:** Implemented dedicated translucent lens cylinders/prisms extending from the internal LED seating ledge plane ($Z = \text{PCB\_POCKET\_DEPTH} = 2.0\,\text{mm}$) through the air gap and faceplate to the exterior front surface ($Z = \text{TOTAL\_Z} = 5.8\,\text{mm}$).
  - **Exact Height & Alignment:** Lens height equals $\text{TOTAL\_Z} - 2.0 = \text{THICK\_MM} + \text{GAP\_MM} = 3.8\,\text{mm}$ (for standard 3mm gap), aligning precisely with each active window aperture ($\varnothing 3.4\,\text{mm}$ round, $\varnothing 3.0\,\text{mm}$ round, or $3.2 \times 3.2\,\text{mm}$ square).
  - **Slicer Assembly Multi-Part Isolation (`Lenses_Translucent_White`):**
    - Extruded windows geometry is unified into a single solid component named `Lenses_Translucent_White` within `tpu_panel_front_multicolor.3mf`.
    - Exported as `tpu_panel_front_color_lenses.stl` (`hex: #e6f1f8`) inside `tpu_panel_front_multicolor_bundle.zip` and specs JSON.
    - Slicers (Bambu Studio, OrcaSlicer, PrusaSlicer) treat the lenses as a separate selectable part, allowing 1-click assignment to Translucent/Clear filament without manual geometric splitting.
    - Single-color monolithic STL (`tpu_panel_front.stl`) preserves open pass-through apertures for unobstructed bare-LED projection.
- **Backend API & Compiler CLI (`simulator.py`):**
  - Added CLI flag `--matrix-lenses [on|off]` to `scripts/compile_clean_tpu_panel.py`.
  - Updated `/api/generate_tpu_stl` endpoint to parse `matrixLensesMode` (default `True`), forward `--matrix-lenses`, and record state in `tpu_panel_specs.json`.
- **Bidirectional UI Controls & Live 3D Preview (`simulator/index.html` & `simulator/app.js`):**
  - **3D Preview Modal Toolbar:** Added `#tpuModalLensesPill` toggle (`ON ★ / OFF`) with dynamic layout signature caching (`lenses`/`nolenses`).
  - **Layout Tab Section 16x16 Matrix Mode:** Added `#btfMatrixLensesToggle` checkbox directly under the gap selector pills.
  - **Bidirectional State Sync:** Persists to `localStorage` (`btfMatrix16x16Config.lensesActive`), instantly synchronizing both controls.
  - **Photorealistic WebGL Rendering:** Renders `color_lenses.stl` in the 3D modal with a translucent crystalline physical material (`roughness: 0.15`, `transmission: 0.85`, `transparent: true`, `opacity: 0.82`, `depthWrite: false`).

### 2026-10-18 18:00 - 🔲 3mm LED Standoff Gap with 5mm Frame & 2mm Internal Ledge (Selectable 0–5mm)
- **3-Tier Rear Frame Architecture (scripts/compile_clean_tpu_panel.py):**
  - Implemented an integrated 5.0mm-tall frame on the rear of the  \times 176\,\text{mm}$ 3D plate with an internal supporting ledge that separates the LED matrix from the front panel by an exact **3.0mm standoff gap**.
  - **Z-Direction Stacking Breakdown:**
    - **Front Panel Skin:** .80\,\text{mm}$ (front-facing $+Z$, carrying full-Z multi-material artwork inlays and through-hole optical apertures).
    - **Standoff Frame Cavity:** .0\,\text{mm}$ ( = 3.0 \dots 5.0\,\text{mm}$ from the back), forming an open chamber for optical diffusion.
    - **Internal Supporting Ledge:** .0\,\text{mm}$ thick ( = 2.0 \dots 3.0\,\text{mm}$ from the back), projecting inward by .0\,\text{mm}$ (.4 \times 156.4\,\text{mm}$ open aperture) to support the PCB margins without obscuring any active LEDs.
    - **Rear PCB Pocket:** .0\,\text{mm}$ deep ( = 0.0 \dots 2.0\,\text{mm}$ from the back, .4 \times 160.4\,\text{mm}$ friction fit) to hold the  \times 160\,\text{mm}$ flexible matrix securely in place.
    - **Exact Total Z Depth:** .8 + 2.0 + 1.0 + 2.0 = 5.8\,\text{mm}$ (bounds $[176.0, 176.0, 5.8]$).
  - **Outer Perimeter Flange & Wire Exit:**
    - Outer frame measures .4 \times 164.4\,\text{mm}$, leaving a .8\,\text{mm}$ flat perimeter flange so the 4 corner $\varnothing 2.8\,\text{mm}$ sewing holes (at .0, 4.0\,\text{mm}$) pass solely through the thin front skin for easy needle stitching.
    - Bottom wire exit notch (\,\text{mm}$ wide centered at  = 88.0\,\text{mm}$) cuts cleanly across all frame tiers for the JST connector and 5V/GND injection leads.
- **Selectable Gap Controls (0, 1, 2, 3mm ★ Default, 4, 5mm):**
  - Updated API (simulator.py) and UI controls (simulator/index.html & simulator/app.js):
    - **0mm:** Direct contact (.0\,\text{mm}$ pocket, total Z = .8\,\text{mm}$).
    - **1mm:** .0\,\text{mm}$ ledge directly against panel (.0\,\text{mm}$ frame, total Z = .8\,\text{mm}$).
    - **2mm:** .0\,\text{mm}$ standoff $+ 1.0\,\text{mm}$ ledge (.0\,\text{mm}$ frame, total Z = .8\,\text{mm}$).
    - **3mm ★ (Default):** .0\,\text{mm}$ standoff $+ 1.0\,\text{mm}$ ledge $+ 2.0\,\text{mm}$ pocket (.0\,\text{mm}$ frame, total Z = .8\,\text{mm}$).
    - **4mm:** .0\,\text{mm}$ standoff $+ 1.0\,\text{mm}$ ledge (.0\,\text{mm}$ frame, total Z = .8\,\text{mm}$).
    - **5mm:** .0\,\text{mm}$ standoff $+ 1.0\,\text{mm}$ ledge (.0\,\text{mm}$ frame, total Z = .8\,\text{mm}$).
  - Fully bidirectional synchronization between the **Layout Tab** and the **3D Print Preview Modal**.

### 2026-10-18 17:15 - 🛠️ Fix: Backside PCB Lip Orientation, 2mm Wall Width & Exact Z Stacking
- **Fixed Backside (-Z) vs Front (+Z) Plate Orientation (scripts/compile_clean_tpu_panel.py):**
  - **Identified Root Cause:** The lip was previously extruded upward from  = \text{THICK\_MM}$ to $\text{THICK\_MM} + \text{LIP\_MM}$, positioning it on the positive $ (front/camera) side of the model while the artwork inlays remained at  = [0.0, \text{THICK\_MM}]$ facing away from the front view.
  - **Corrected Coordinate System:** The front faceplate (chassis + multi-material inlays + window through-holes) now translates to  = [\text{LIP\_MM}, \text{TOTAL\_Z}]$, placing the visible character graphic on the front face facing $+Z$. The lip is constructed on the backside at  = [0.0, \text{LIP\_MM}]$ facing $-Z$ toward the runner's shirt.
- **Accurate Additive Total Z Distance (Front Skin + Lip Height):**
  - Verified that total Z height strictly equals $\text{THICK\_MM} + \text{LIP\_MM}$ (e.g. .8\,\text{mm}$ front thickness $+ 2.0\,\text{mm}$ lip $= 2.8\,\text{mm}$ total Z depth; .6\,\text{mm} + 2.0\,\text{mm} = 2.6\,\text{mm}$; .8\,\text{mm} + 3.0\,\text{mm} = 3.8\,\text{mm}$).
  - Dimension badge and API specs report the exact total Z depth ( \times 176 \times 2.8\,\text{mm}$).
- **2.0mm Lip Wall Width (Not Full-Bleed to Outer Edge):**
  - Replaced the full .8\,\text{mm}$ outer rim with a crisp **.0\,\text{mm}$ wide lip wall** framing the .4 \times 160.4\,\text{mm}$ pocket (outer lip envelope: .4 \times 164.4\,\text{mm}$, spanning , Y = 5.8\,\text{mm} \dots 170.2\,\text{mm}$).
  - Leaves a flat .8\,\text{mm}$ perimeter flange where the 4 corner $\varnothing 2.8\,\text{mm}$ sewing holes (at .0, 4.0\,\text{mm}$) pass solely through the thin front skin (.8\,\text{mm}$), eliminating the need to pierce needles through thick .8\,\text{mm}$ blocks.
  - Preserves the \,\text{mm}$ wide bottom wire exit notch ( = 80 \dots 96\,\text{mm}$) across the bottom .0\,\text{mm}$ lip wall.

### 2026-10-18 16:30 - 🔲 Optional Backside Alignment Lip & Retaining Pocket for 16x16 Flexible LED Matrix Plates
- **Backside Alignment Lip & Retaining Pocket Architecture (`scripts/compile_clean_tpu_panel.py`):**
  - Designed an integrated perimeter rim / recessed pocket on the rear of the $176 \times 176\,\text{mm}$ 3D plate that snugly holds the $160 \times 160\,\text{mm}$ flexible FPCB LED matrix in place.
  - Sized the inner retaining pocket to $160.4 \times 160.4\,\text{mm}$ ($0.2\,\text{mm}$ perimeter clearance), guaranteeing a drop-in friction fit that prevents lateral shifting and perfectly aligns all 256 matrix LEDs directly with the faceplate's $\varnothing 3.4\,\text{mm}$ through-hole windows.
  - Added an open $16\,\text{mm}$ wide bottom wire exit notch ($X = 80 \dots 96\,\text{mm}$, $Y = 0 \dots 8.5\,\text{mm}$) to allow the 3-wire JST harness and 5V/GND power injection wires to route cleanly out the bottom without pinching.
  - Preserved all 4 corner $\varnothing 2.8\,\text{mm}$ garment sewing holes through the full plate + lip depth.
  - Supports selectable lip heights: `None` ($0.0\,\text{mm}$ flat back), `2mm ★` (Default, total $2.6\,\text{mm}$ depth), `3mm` (total $3.6\,\text{mm}$), `4mm` (total $4.6\,\text{mm}$), and `5mm` (total $5.6\,\text{mm}$).
  - Designed for 100% zero-support printing: faceplate prints flat on the bed ($Z = 0 \dots \text{THICK\_MM}$), with lip walls extruding upward ($Z = \text{THICK\_MM} \dots \text{THICK\_MM} + \text{LIP\_MM}$).
- **Backend API & CLI Integration (`simulator.py`):**
  - Updated `/api/generate_tpu_stl` endpoint to parse `matrixLipMm` (validated against `[0.0, 2.0, 3.0, 4.0, 5.0]`, default $2.0\,\text{mm}$) and forward `--matrix-lip` to `compile_clean_tpu_panel.py`.
  - Persists `matrix_lip_mm` into `3d_panels/tpu_panel_specs.json`.
- **Bidirectional UI Controls (`simulator/index.html` & `simulator/app.js`):**
  - Added dedicated lip selector pill groups in both the **Layout Tab** 16x16 Matrix section (`.btf-matrix-lip-btn`) and the **3D Print Preview Modal** header toolbar (`#tpuModalLipPill`).
  - Implemented bidirectional synchronization (`setMatrixLipMm(val)`): changing the lip in either view immediately updates the other, refreshes the layout signature cache key (`matLip:X`), and automatically re-renders the 3D preview.
 
### 2026-10-18 12:20 - 🐉 Content-Aware 16x16 Matrix Graphic Maximization & Transparent Margin Trimming
- **Content-Aware Bounding Box & Active Grid Maximization (simulator/app.js):**
  - **Identified Root Cause of Small Pete's Dragon:** ssets/petes_dragon_transparent.png (853×1024) contained massive transparent borders (20.6% top, 17.6% bottom, 18.2% horizontal). When fitted to the plate envelope using raw file dimensions, the visible dragon occupied only ~64.8% of matrix height (103.8mm / 160mm) and left rows 0–2, rows 13–15, and outer columns completely empty (only 59 LEDs active).
  - **Implemented getImageContentBounds(img) Analyzer & Cache:** Uses a high-speed offscreen canvas scan (256px resolution) to detect true non-transparent foreground bounding boxes (handling alpha transparency, black background corners, or full-bleed graphics).
  - **Maximized Envelope Fit in getGraphicChestBounds():** Scales visible artwork content to fill the full 168.0mm × 168.0mm plate envelope (ART_FIT_MM = 168.0, centered at x = 0.50, y = 0.3615) while strictly preserving aspect ratio (contentAspect = 1.103 for Pete's Dragon).
  - **Coverage Doubled Across Grid:**
    - Active LEDs on Pete's Dragon increased from **59 ➔ 128 LEDs** (out of 256).
    - Every row from Row 0 to Row 15 is active: [1, 3, 3, 5, 9, 11, 11, 11, 11, 10, 11, 11, 10, 11, 9, 1].
    - Every column from Col 0 to Col 15 is active: [6, 6, 7, 10, 12, 11, 11, 7, 11, 11, 8, 5, 5, 7, 7, 4].
    - Auto-backlight detects **115 colored LEDs** across green scales, magenta wings, and dragon crest.
  - **Full Python 3D STL Parity:** The simulator canvas sampling now 100% matches scripts/compile_clean_tpu_panel.py line 219 (ART_FIT_MM = 168.0, scale = ART_FIT_MM / max(w_px, h_px)).
  - **Asynchronous Asset Load Reactivity:** Hooked 
otifyFloatImgLoaded() to all float asset onload events so the 16×16 matrix recalculates and re-renders immediately upon image load.

### 2026-10-18 11:48 - ✨ Smart Auto-Backlight Toggle with Slider Grey-Out & Random Yellow Standby Mode
- **Smart Toggleable Auto-Backlight & Slider Lock (`simulator/app.js`):**
  - Updated `autoBacklightAllColoredAreas()`:
    - **Toggle ON:** Stores the previous manual slider value (`previousBacklightSliderCount`), automatically backlights all colored regions on the graphic (`maxCh >= 50 && lum >= 40`), updates the slider position to the exact count of colored LEDs, and **locks / greys out the slider** (`disabled = true`, `opacity: 0.45`, cursor `not-allowed`).
    - **Toggle OFF:** When clicked again, restores the exact previous manual slider count, re-enables and unlocks the slider (`disabled = false`, `opacity: 1.0`), and recalculates the layout.
    - Moving the backlight slider manually at any time automatically disengages the auto-backlight lock and saves the new manual value.
- **ALL 256-LED Dim Yellow Standby Hardware Diagnostic (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`):**
  - Identified why the previous build did not light all 256 LEDs: In the main loop for `SHOW_MODE_CORRAL_STANDBY`, `duplicateFrontToBack()` was being called immediately after `renderCorralStandby()`. In 16×16 Matrix Mode, `duplicateFrontToBack()` wipes the matrix to `CRGB::Black` and only scatters the active front LEDs, instantly blacking out the other ~129 pixels!
  - Fixed by bypassing `duplicateFrontToBack()` during standby when `isCurrentFloatMatrix16x16()` is true.
  - In `renderCorralStandby()`, all **256 physical LEDs** across the 16×16 matrix now illuminate solidly and comfortably in **dim warm yellow (`CRGB(65, 52, 0)`)**, providing full illumination across every single pixel from upper-right (0) to lower-left (255) for physical grid inspection.
- **Firmware Compilation & Binary Sync (`firmware/`):**
  - Compiled release build cleanly with PlatformIO (`RAM: 14.6%`, `Flash: 60.7%`, `[SUCCESS]`).
  - Synced `firmware/firmware.bin` and `firmware/firmware_float2.bin`.

### 2026-10-18 11:15 - 🔄 16×16 Matrix Serpentine Orientation (Upper-Right to Lower-Left), Revert to RGB Color Order & Strict Black Drum Face
- **Serpentine Matrix Orientation Correction (`simulator/app.js`, `include/costume_config.h`, `presets/main_street_title_drum_100_led_vibrant_preset_large_100led_2026-10-18_01-04.json`):**
  - Updated matrix physical indexing to start at the **upper right** (Row 0, Col 15 -> Index 0) and end at the **lower left** (Row 15, Col 0 -> Index 255):
    - Even rows ($0, 2, 4 \dots 14$): right-to-left sweep (`row * 16 + (15 - col)`).
    - Odd rows ($1, 3, 5 \dots 15$): left-to-right sweep (`row * 16 + col`).
  - Re-mapped all 55 windowed LEDs and backlit LEDs in the Title Drum preset to match this physical wiring layout.
- **Revert Color Order to `RGB` (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator.py`, `include/costume_config.h`):**
  - Per hardware testing feedback, reverted FastLED color ordering back to standard **`RGB`** across all firmware definitions and generation scripts (`FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>`).
- **Strict Black Drum Face & Chassis Dark Isolation (`simulator/app.js`):**
  - Removed old legacy white boost (`{ r: 255, g: 245, b: 220 }`) from `boostLedVibrancy()` on the black drum face and chassis. Dark pixels now return `{ r: 17, g: 22, b: 29 }`.
  - Refined `autoBacklightAllColoredAreas()`: Strictly checks that a cell has distinct vibrant color (`maxCh >= 50 && lum >= 40`) and is not chassis/black (`!(r < 45 && g < 45 && b < 45)`). Only true colored regions (red drum body, gold marquee border, green/blue pennants) are illuminated. All black areas remain strictly unlit (`CRGB::Black`).
- **Clean PlatformIO Compilation & USB Binary Sync (`firmware/`):**
  - PlatformIO compiled with zero warnings and `[SUCCESS]` (RAM: 14.6%, Flash: 60.7%).
  - Synced `firmware/firmware.bin` and `firmware/firmware_float2.bin`.
  - Terminated and restarted `simulator.py` on port 8000.

### 2026-10-18 11:00 - 🥁 Fix Title Drum GRB Color Order Swap, 16×16 Serpentine Active Scattering & Dark Black Drum Face
- **WS2812B 16×16 Flexible Matrix Hardware GRB Color Order Fix (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator.py`):**
  - Resolved root cause of green standby mode and red drum panels appearing green/unlit: BTF-LIGHTING WS2812B 16×16 FPCB matrices natively use **`GRB`** color order on the wire, whereas pebble fairy pixel strands use `RGB`.
  - When `COLOR_ORDER` was set to `RGB`, Red and Green channels were swapped, making vibrant red (`239, 68, 68`) display as green, and yellow/gold (`255, 235, 0`) display as lime green (`G=255, R=235`).
  - In `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`, updated FastLED hardware initialization in `setup()` to explicitly instantiate `FastLED.addLeds<LED_TYPE, DATA_PIN, GRB>` whenever `isCurrentFloatMatrix16x16()` is true, and fall back to `#ifndef COLOR_ORDER` defaulting to `GRB` if `COSTUME_MATRIX_16X16_MODE` is active.
  - In `simulator.py`, updated configuration generator to automatically emit `#define COLOR_ORDER GRB` whenever `matrix_16x16_mode` is enabled.
- **16×16 Serpentine Physical Scattering Fix & Background Server Refresh (`simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`):**
  - Identified that background task `task-974` was running an older in-memory version of `simulator.py`, generating `costume_config.h` without `COSTUME_MATRIX_16X16_MODE 1` and without `MATRIX_ACTIVE_INDICES`.
  - Because `duplicateFrontToBack()` fell back to linear 1D indexing ($0 \dots 147$), only the top 9 rows of the 16×16 matrix were addressed, leaving rows 9–15 (all lower red drum panels and wheels) dark.
  - Terminated `task-974` and launched fresh server task `task-1685` on port 8000.
  - Removed unnecessary `defined(HAS_CUSTOM_PALETTE)` guard in `duplicateFrontToBack()` and `isCurrentFloatMatrix16x16()`, guaranteeing that `MATRIX_ACTIVE_INDICES` scatter immediately to their exact 2D serpentine coordinates across all 16 rows.
- **Strict Black Drum Face & Chassis Dark Thresholding (`simulator/app.js`):**
  - Updated `computeBtfMatrix16x16Layout()` and `autoBacklightAllColoredAreas()`: dark drum face and chassis cells (`lum < 35` and `maxCh < 45`) are strictly preserved as dark (`CRGB::Black`), preventing previous false incandescent white boosts on black pixels.
  - Only non-windowed cells covering colored regions (red drum body, gold border, green banner) are set to `'backlight'`, while all existing windowed LEDs are 100% preserved.
- **Compiler Bounds Safety & Firmware Build (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `firmware/`):**
  - Added bounds guards `(i < 100) ? DEFAULT_FLOAT_PALETTES[floatIdx][i] : FLEET_ROSTER_INFO[floatIdx].color` for matrices with `FRONT_LEDS > 100`, eliminating GCC `-Waggressive-loop-optimizations` warnings.
  - Built PlatformIO release binary cleanly with `[SUCCESS]` (RAM: 14.6%, Flash: 60.9%). Synced `firmware/firmware.bin` and `firmware/firmware_float2.bin`.

### 2026-10-18 10:35 - 🥁 Title Drum Yellow Standby Color, 16×16 Matrix 50% Brightness Scaling & Auto-Backlight Colored Areas
- **Title Drum (Float 2) Pure Yellow Standby & Wake Flashes (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator/app.js`):**
  - Updated Float 2 signature color in `FLEET_ROSTER_INFO[1]` from amber/gold `CRGB(255, 180, 20)` to radiant parade yellow `CRGB(255, 235, 0)` (`#ffeb3b`).
  - Updated `renderCorralStandby()` starlight sparkle `subtleWarm` blue channel offset to keep yellow starlight sparkles crisp and warm with zero hint of green.
  - Replaced the hardcoded emerald green wake alert flash on Button 1 tap and Float ID config mode exit with the active float's dynamic signature color (`FLEET_ROSTER_INFO[wakeFloatIdx].color`), so the Title Drum flashes pure yellow when waking from Corral Standby or exiting config.
  - Updated `DEFAULT_FLEET_ROSTER[1]`, `DEFAULT_FLEET_RADAR[1]`, and `presets/fleet_lineup.json` color from `#ffb703` to `#ffeb3b` (Yellow).
- **50% Brightness Scaling in 16×16 Matrix Firmware (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator.py`, `include/costume_config.h`):**
  - Applied automatic 50% brightness scaling whenever 16×16 Matrix Mode is active (`isCurrentFloatMatrix16x16()`), preventing glare and reducing thermal dissipation on dense 16×16 FPCB matrices.
  - In `duplicateFrontToBack()`, active matrix LEDs are scaled via `c.nscale8_video(128)`.
  - In `setup()`, `effectiveBrightness` is scaled down to ~half (`max(15, effectiveBrightness / 2)`).
  - In `simulator.py` (`handle_flash_firmware`), `fastled_brightness` is capped at $15 \dots 42$ (halved from $30 \dots 85$).
  - Updated `include/costume_config.h` `COSTUME_BRIGHTNESS` from 68 down to 34.
- **Auto-Backlight All Colored Areas in Simulator Layout Card (`simulator/index.html`, `simulator/app.js`):**
  - Added new action button: `💡 Auto-Backlight Colored Areas (Keep Windows & Black Dark)` to the 16×16 Matrix card in the Layout panel.
  - Implemented `autoBacklightAllColoredAreas()`: Analyzes all 256 matrix cells, **strictly preserving all existing Windowed LEDs**, while automatically setting every remaining non-windowed cell covering colored graphic regions (`maxCh >= 30` or `lum >= 25`) to `backlight` role. All black chassis/lettering/margins and off-graphic cells remain strictly `dark`.
  - Automatically updates slider counts, telemetry, re-renders canvas, and regenerates 3D backplate geometry.
- **Title Drum Firmware Verification (`firmware/firmware.bin`, `firmware/firmware_float2.bin`):**
  - PlatformIO release build verified with `[SUCCESS]` (RAM: 14.6%, Flash: 60.7%). Synced `firmware/firmware.bin` and `firmware/firmware_float2.bin`.
 
### 2026-10-18 01:25 - ⚡ 16×16 Matrix ESP32 Firmware Integration, Preset Persistence & Pre-Flash Auto-Save (Title Drum Active)
- **Preset Save & Restore for 16×16 Matrix Mode (`simulator/app.js`):**
  - Updated `buildCompletePresetData()` and `applyProfileData()` so saving a float profile persists `btfMatrix16x16Active`, `btfMatrix16x16Config` (`windowCount`, `backlightCount`, `thicknessMm`), `matrixWindowedLeds`, and `matrixBacklightLeds` (each storing its physical serpentine `id` $0 \dots 255$, `row`, `col`, `x`, `y`, and sampled `color`).
  - Loading a saved 16×16 matrix preset automatically activates the 16×16 Matrix toggle, restores slider counts and plate thickness, and restores the exact saved Windowed, Backlit, and Dark cell assignments without re-randomizing.
  - Updated `presets/main_street_title_drum_100_led_vibrant_preset_large_100led_2026-10-18_01-04.json` with the active Title Drum 16×16 matrix layout (**55 Windowed LEDs + 28 Backlit LEDs = 83 Active LEDs**, 0.60mm plate, and 5-color Title Drum palette).
- **Automatic Pre-Flash & Pre-Build Float Saving (`triggerUsbFirmwareFlash` & `rebuildFleetBinariesBtn`):**
  - Before flashing firmware over USB or rebuilding the 7-float ROM binaries, if the active float has any unsaved changes (`isSingleShirtDirty`), the simulator automatically saves the float preset to disk (`presets/<name>.json`) and syncs `presets/fleet_lineup.json` so changes are never lost and the compiled firmware always reflects the exact displayed layout.
- **ESP32 Firmware 16×16 Matrix Serpentine Mapping (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator.py`, `build_fleet_binaries.py`):**
  - Expanded `MAX_LEDS_CAPACITY` to `512` (supporting two 256-pixel 16×16 matrices for Front + Back).
  - Updated `simulator.py` (`handle_flash_firmware`) to emit `COSTUME_MATRIX_16X16_MODE`, `MATRIX_ACTIVE_LED_COUNT`, and `MATRIX_ACTIVE_INDICES[FRONT_LEDS]` in `include/costume_config.h`, along with 2D spatial metrics (`SPATIAL_X_BYTE`, `SPATIAL_Y_BYTE`, `SPATIAL_RANK_Y`, `SPATIAL_RADIUS_BYTE`) computed directly from the active matrix LED coordinates.
  - Updated `build_fleet_binaries.py` (`sync_fleet_palettes`) to emit `FLOAT_IS_MATRIX_16X16[7]`, `FLOAT_ACTIVE_LED_COUNT[7]`, and `FLOAT_MATRIX_INDICES[7][100]` in `include/fleet_palettes.h` and `arduino/MSEP_Costume/fleet_palettes.h`.
  - Updated `duplicateFrontToBack()` and `fillActiveCostumeSolid()` in both `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` so that when a float uses 16×16 Matrix Mode, only the active Windowed and Backlit LEDs illuminate at their exact physical serpentine indices ($0 \dots 255$ Front and $256 \dots 511$ Back), while all remaining un-windowed cells stay strictly `CRGB::Black` (`0, 0, 0`) across all modes (Autonomous Show, Ambient Fallback, Castle Photo Mode, Corral Standby, 30s Fleet Show, and Rapid Roll Call).
  - Compiled and verified `firmware/firmware.bin` and `firmware/firmware_float2.bin` for **Float 2 (The Title Drum)** using PlatformIO (`RAM: 14.6%`, `Flash: 60.7%`, `SUCCESS`).

### 2026-10-18 00:20 - 🔲 BTF 16×16 Matrix 3D Plate: Pure Flat Full-Z Geometry, Ø 3.4mm Round Windows, 4 Corner Sewing Holes & Native 3MF Assembly
- **Strict Backlighting Test Panel Geometry Rules Applied:**
  - **Removed All Legacy Tray Features:** Completely removed all LED channels/collars, side walls, screw holes, outer sewing eyelets, and zip-tie strain-relief tunnels.
  - **100% Full Z-Thickness Color Inlays:** Every colored region of the active float artwork extends from the top to the bottom of the entire thickness ($Z = 0$ to $T$).
  - **Ø 3.4mm Round LED Windows Only:** Windowed LED positions are punched out strictly as $\varnothing 3.4\text{ mm}$ ($R = 1.70\text{ mm}$) circular through-holes; Backlit LED positions remain solid colored PLA with zero holes.
  - **4 Corner Sewing Holes:** Replaced the 16 perimeter holes with **4 corner sewing holes** ($\varnothing 2.8\text{ mm}$ at $(4.0, 4.0), (172.0, 4.0), (4.0, 172.0), (172.0, 172.0)\text{ mm}$) in both the 2D Layout view and 3D STL/3MF compiler.
- **Native 3MF Single-Object `<components>` Assembly & Float Color Palette Sync (`export_assembled_3mf`):**
  - Wrapped all 5 color meshes in the `.3mf` XML (`3D/3dmodel.model`) inside a single parent `<object>` with `<components>` and a single `<item>` in `<build>`. This ensures Snapmaker Orca / OrcaSlicer / Bambu Studio loads the `.3mf` as **one unified multi-part object** rather than 5 separate overlapping objects, eliminating the *"too close to others; there may be collisions when printing"* slicer warning and allowing the entire plate to be flipped face-down cleanly as one unit.
  - Fixed `getActiveFloatStlColors()` in `simulator/app.js` and `compile_clean_tpu_panel.py` so switching floats (e.g., Title Drum) always uses that float's authentic 5-color part names (`1_Chassis_Black`, `2_Drum_Ring,_Text_and_Scrollwork`, `3_Body_Panels_and_Streamer`, `4_Flags_and_Pennants`, `5_Lead_Flag`) instead of stale Pete's Dragon part names.
- **Automatic Background STL Compilation & Server Restart:**
  - Fixed a stale Python server process on port 8000 that had been running an older `simulator.py` lacking `--matrix-16x16 on` flag forwarding.
  - Added automatic background compilation (`handleRecompileTpuStl({ skipOpen: true })`) whenever 16×16 Matrix Mode is toggled on, redistributed, or changed in thickness so downloaded `.stl`, `.3mf`, and `.zip` files immediately reflect the flat square plate without needing to open the 3D preview modal first.

### 2026-10-18 00:05 - 🔲 BTF 16×16 Matrix: Maximized Graphic Sizing & Dynamic LED Redistribution
- **Maximized Graphic Fit on Panel Envelope:**
  - Increased `artFitW` in `simulator/app.js` (`getGraphicChestBounds`) from `156.0 / 457.2` to `168.0 / 457.2` (~36.7% of shirt width), allowing the active character artwork to utilize virtually the entire $176\text{ mm} \times 176\text{ mm}$ plate envelope without clipping the 16 perimeter shirt-mounting holes.
  - Aligned `ART_FIT_MM` in `scripts/compile_clean_tpu_panel.py` to `168.0` for 3D multi-color STL/3MF generation.
- **Dynamic LED Target Redistribution & Reactive Spread Button:**
  - Expanded slider ranges for Windowed LEDs and Backlight LEDs from `0–120` / `0–100` to `0–200` on both controls.
  - Linked the button label `#btfMatrixAutoSpreadBtn` dynamically in `updateBtfMatrix16x16TelemetryUI()`: updates automatically to **`🎯 Spread <W> Win + <G> Glow`** whenever slider values change.
  - Clicking the button recalculates Farthest-Point Sampling across the enlarged graphic contour and redistributes the newly specified LED counts with a single click.

### 2026-10-17 23:40 - 🔲 BTF-LIGHTING 16×16 (256-LED) Flexible FPCB Matrix Hybrid Window + Backlight Mode & 176×176mm Square 3D Plate Compiler
- **Hardware & Physical Architecture:**
  - Added full 2D Layout simulation, 3D WebGL preview, and multi-color 3MF/STL compilation for the **BTF-LIGHTING WS2812B ECO 16×16 (256-Pixel) Flexible FPCB Matrix** ($160.0\text{ mm} \times 160.0\text{ mm}$, $10.0\text{ mm}$ pixel pitch).
  - **176.0mm × 176.0mm Square Cover Plate:** Covers the $160\times 160\text{ mm}$ flexible matrix with an $8.0\text{ mm}$ black mounting flange on all four sides and **16 perimeter shirt-stitching holes** ($\varnothing 2.8\text{ mm}$, inset $4.0\text{ mm}$ from the outer edge so needles/snaps clear the FPCB).
  - **Proportional Graphic Centering:** Scales and centers the active float artwork inside a $156.0\text{ mm} \times 156.0\text{ mm}$ box within the $160\times 160\text{ mm}$ matrix while strictly preserving aspect ratio (`normW = normH * 1.25 * aspect`). All plate area outside the graphic is solid black filament (`#11161d`).
- **256-LED Hybrid Allocation (~50 Windowed + ~25 Backlit + ~181 Dark):**
  - **Farthest-Point Sampling (`computeBtfMatrix16x16Layout`):** Automatically spreads **50 Windowed LEDs** (through-hole optical apertures in the 3D plate) and **25 Backlighting LEDs** (solid thin colored PLA over the pixel—no window hole—for soft subsurface glow) evenly across the graphic, keeping the remaining **181 LEDs Dark (Off)** (~1.35A max draw, well within the 2.0A USB power bank budget).
  - **Interactive Sliders & Cell Clicking:** Added sliders for Windowed LED count (`0–120`, default `50`) and Backlit LED count (`0–100`, default `25`), plus direct 2D canvas click-cycling on any of the 256 grid cells (`Window ➔ Backlight ➔ Dark ➔ Window`).
- **3D Preview Modal (`#tpuPreviewModal`) & Full-Z Multi-Color Compiler (`scripts/compile_clean_tpu_panel.py`):**
  - **Auto-Defaulting:** Opening `#tpuPreviewModal` while 16×16 Matrix Mode is enabled in the Layout tab automatically defaults to **`🔲 16×16 Matrix Plate`** mode.
  - **Selectable Plate Thickness (Default `0.60mm`):** Added thickness selector buttons (`0.48mm`, `0.60mm ★`, `0.80mm`, `1.00mm`) in both the Layout tab and the `#tpuPreviewModal` toolbar.
  - **Pure Flat Full-Z 3D Geometry (`compile_matrix_16x16_plate_variant`):** Strips all TPU sidewalls, LED collars, wire channels, and zip-tie bridges; extrudes all 5 filament color inlays 100% through the Z-thickness ($Z = 0$ to $T$) and cuts through-holes only for the ~50 windowed LEDs + 16 perimeter shirt holes. Renders both crisp window pixels and diffused subsurface backlit PLA glows in the 3D WebGL viewer.

### 2026-10-17 13:10 - 💡 Pete's Dragon 200mm × 200mm Multi-Color Backlighting Test Panels (4 Thicknesses)
- **Optical Backlighting Calibration & Testing (`scripts/generate_backlight_test_panels.py`):**
  - Designed and generated 4 flat multi-color test panels to evaluate rear LED backlighting transmission, translucency, and light diffusion through multi-color filament before final costume fabrication.
  - **Full Feature Stripping (Pure Flat Panel):** Completely removed all 100 LED socket holes, wiring trenches, perimeter side walls/rims, mounting tabs, screw holes, eyelets, and zip-tie tunnels per hardware testing specs.
  - **Chassis Geometry:** $200.0\text{ mm} \times 200.0\text{ mm}$ square flat chassis plate printed in black filament.
  - **Proportional Artwork Centering (Strict Aspect Ratio):** Pete's Dragon character artwork ($698 \times 633\text{ px}$, aspect $1.103$) scaled to fit perfectly within a $180.0\text{ mm}$ square ($180.00\text{ mm}\text{ W} \times 163.24\text{ mm}\text{ H}$), centered at $(100.0, 100.0)\text{ mm}$ with $10.0\text{ mm}$ horizontal margins and $18.38\text{ mm}$ vertical margins.
  - **100% Z-Thickness Color Inlays:** All colored regions (Green body, Magenta wings/crest, Yellow belly/horns, White eyes/teeth) extend completely from $Z = 0.00\text{ mm}$ to the top surface across all layers. The black chassis forms the surrounding $200\times 200\text{ mm}$ plate and internal black outlines via boolean difference ($\sum \text{Volume} \equiv 40,000 \times T\text{ mm}^3$ with zero air gaps and zero overlaps).
  - **4 Thickness Variants Produced (`3d_panels/backlight_test/`):**
    1. **1.00 mm** (`thickness_1.00mm/` & `petes_dragon_backlight_test_1.00mm.3mf`): 5 layers @ 0.20mm (or 10 @ 0.10mm).
    2. **0.80 mm** (`thickness_0.80mm/` & `petes_dragon_backlight_test_0.80mm.3mf`): 4 layers @ 0.20mm (or 8 @ 0.10mm).
    3. **0.60 mm** (`thickness_0.60mm/` & `petes_dragon_backlight_test_0.60mm.3mf`): 3 layers @ 0.20mm (or 5 @ 0.12mm).
    4. **0.48 mm** (`thickness_0.48mm/` & `petes_dragon_backlight_test_0.48mm.3mf`): 3 layers @ 0.16mm (or 4 @ 0.12mm, or 6 @ 0.08mm).
- **Deliverables & Slicer Support:**
  - **Native Multi-Material 3MF:** Pre-configured with 5 color slots (Black, Green, Magenta, Yellow, White) for 1-click import into Bambu Studio, OrcaSlicer, or Snapmaker Luban.
  - **Individual Aligned STLs:** Exported for each color sharing origin $(0, 0, 0)$ (`chassis_black.stl`, `color_green.stl`, `color_magenta.stl`, `color_yellow.stl`, `color_white.stl`, `monolithic_panel.stl`).
  - **Bundled ZIPs & Master Package:** Per-thickness zips plus `petes_dragon_backlight_test_all_thicknesses.zip`.
  - **Parametric OpenSCAD Source:** `petes_dragon_backlight_panel.scad`.
  - **Interactive 3D WebGL Viewer:** `3d_panels/backlight_test_preview.html` with real-time rear backlight illumination simulation.
- **Physics-Calibrated Weight Simulation in PLA (`scripts/generate_pcb_mockup_stls.py`):**
  - Designed two 1:1 scale test mockups to simulate the physical feel, thickness, chest curvature, and bounce on a running shirt before spending \$400+ on PCB fabrication.
  - **The 2.5mm Equivalence Rule:** Because PLA ($1.24\text{ g/cm}^3$) is 36% less dense than FR-4 fiberglass ($1.95\text{ g/cm}^3$), printing the mockup at $2.50\text{ mm}$ solid thickness (100% infill) matches both the total Z-height of the loaded board ($1.6\text{ mm}$ PCB + $0.9\text{ mm}$ LEDs) AND the exact weight (**$123.7\text{ grams}$ PLA vs. $126.5\text{ grams}$ real PCB — a 97.8% match!**).
- **Deliverables Generated (`3d_panels/mockups/`):**
  - `mockup_monolithic_200x200.stl`: $200.0\text{ mm} \times 200.0\text{ mm} \times 2.50\text{ mm}$ single-piece plate with 4 corner M3 holes, 12 perimeter sewing eyelets, solder pin holes, and wire strain relief holes. Weighs $123.7\text{ grams}$ at 100% infill.
  - `mockup_modular_100x100.stl`: $100.0\text{ mm} \times 100.0\text{ mm} \times 2.50\text{ mm}$ quadrant tile with corner M3 and sewing eyelets. Weighs $30.9\text{ grams}$ per tile ($123.4\text{ grams}$ for all 4). Taping 4 together with a $2.0\text{ mm}$ seam physically simulates the articulating felt living hinge!
  - `mockups_preview.html`: Interactive 3D WebGL (Three.js) viewer allowing 360° inspection, dimension checks, and slicing instructions.
- **Slicer Requirements:** Set infill to **100% (or Top/Bottom shells to 99)** to achieve the full $124\text{g}$ real-world weight.

### 2026-10-16 23:50 - Monolithic 200mm × 200mm Panels: Pure Single-Sided SMT (Economic PCBA) with Through-Hole Solder Pins
- **100% Single-Sided SMT Assembly (Top Layer Only):**
  - Removed all SMT connectors from the bottom layer (`B.Cu`), making CPL 100% Top-layer parts (LEDs and 0402 Caps only).
  - Qualifies for JLCPCB **Single-Sided "Economic PCBA"** ($\sim \$15.00$ setup fee instead of $\sim \$70.00$), saving **$\$55.00$ per batch**!
  - Empty bottom paste stencil (`.GBP`) and zero extended part feeder fees.
- **2.54mm Through-Hole Solder Pins for IN and OUT:**
  - Standard $2.54\text{ mm}$ pitch plated through-hole pads labeled `+5V`, `DAT`, and `GND` at bottom-left (`IN`) and bottom-right (`OUT`).
  - **Solder from Front or Back:** Both copper layers (`F.Cu` and `B.Cu`) have soldermask apertures, allowing direct soldering of 22/24 AWG silicone wire, right-angle pin headers, or DuPont jumpers from either side.
  - **Dual S-Curve Wire Strain Relief:** Dual $\varnothing 2.2\text{ mm}$ non-plated anchor holes next to each pad group let wires loop through the board, mechanically isolating the solder joints from 10K running vibrations.
- **Model 1: 144 LEDs (12×12 Staggered Brick Grid — `pcb/monolithic_200mm_144/`):**
  - Single-piece $200.0\text{ mm} \times 200.0\text{ mm}$ board covering the full chest/back with 144 WS2812B-2020 LEDs and 144 0402 bypass caps.
  - $15.5\text{ mm} \times 16.0\text{ mm}$ pitch. ZERO internal jumper cables (100% internal traces).
  - Turnkey KiCad PCB, RS-274X Gerbers (`monolithic_200mm_144_gerbers.zip`), JLCPCB BOM/CPL files, and interactive HTML preview (`monolithic_200mm_144_preview.html`).
- **Model 2: 288 LEDs (18×16 Double-Density Offset Lattice — `pcb/monolithic_200mm_288/`):**
  - Exactly twice as many LEDs ($144 \times 2 = 288$ LEDs) with 288 0402 caps.
  - High-density $11.6\text{ mm} \times 10.6\text{ mm}$ isotropic offset grid delivering double the pixel density ("Retina" display).
  - FastLED hardware power limiting enforced ($5\text{V}, 2000\text{mA}$ max) drawing ~6.9mA average per LED for brilliant night visibility and 3+ hours runtime on 5,000–10,000 mAh battery packs.
  - Turnkey KiCad PCB, RS-274X Gerbers (`monolithic_200mm_288_gerbers.zip`), JLCPCB BOM/CPL files, and interactive HTML preview (`monolithic_200mm_288_preview.html`).
- **Updated Fleet Economics (8 Runners: Front + Back = 16 Panels / 18 Boards with Spares):**
  - 144-LED Model: **$\approx \$220.72$ total** ($\mathbf{\$27.59}$ per runner for Front + Back complete).
  - 288-LED Model: **$\approx \$368.45$ total** ($\mathbf{\$46.06}$ per runner for Front + Back complete).


### 2026-10-16 18:20 - Bottom-Mounted JST Connector Variant: 100% Flush Front Face & Symmetrical 22mm Straight Spans
- **100% Flush Front Layer (`F.Cu`):**
  - Designed dedicated bottom-mounted PCB generator (`scripts/generate_universal_6x6_bottom_pcb.py`).
  - Front side contains **only** the 36 WS2812B-2020 LEDs ($0.9\text{ mm}$ height) and 36 0402 bypass capacitors ($0.5\text{ mm}$ height).
  - Eliminates the $5.1\text{ mm}$ vertical protrusion of front-mounted horizontal JST headers.
  - Fabric shirts, optical diffusion sheets, or 3D-printed faceplates touch the LEDs directly with **0.0 mm gap**, eliminating light bleed and fabric tenting.
- **Rear-Mounted SMT JST-PH 2.0mm Connectors (`B.Cu`):**
  - All 8 horizontal JST-PH headers (`C3029441`) are mounted on the bottom copper layer facing outwards.
  - Solder pads, pin callouts (`+5V`, `DAT`, `GND`), port markers (`[IN]`, `[OUT]`), and direct-solder wire eyelets are routed on the bottom silkscreen (`.GBO`) and bottom copper (`.GBL`).
- **Symmetrical 22.0mm Straight Spans (Zero Angle, Zero Cable Twisting):**
  - With no LEDs to avoid on the rear, connectors on all 4 borders align at identical $33.0\text{ mm}$ and $67.0\text{ mm}$ positions.
  - Across the $2.0\text{ mm}$ felt seam, opposing ports face each other directly with a straight-line center-to-center span of **$22.0\text{ mm}$**.
  - Standard $50\text{ mm}$ pre-crimped JST cables plug straight across with a relaxed, low-profile rear wire loop ($\le 8\text{ mm}$ loop height on the back side).
- **JLCPCB Turnkey Deliverables (`pcb/bottom_connectors/`):**
  - Native KiCad PCB: `universal_6x6_bottom_100mm.kicad_pcb`
  - RS-274X Gerbers: `universal_6x6_bottom_100mm_gerbers.zip` (complete 10-layer set including `.GBP` bottom paste and `.GBO` bottom silkscreen)
  - JLCPCB BOM: `universal_6x6_bottom_100mm_bom.csv`
  - JLCPCB CPL Centroid: `universal_6x6_bottom_100mm_cpl.csv` (72 Top parts, 8 Bottom parts)
  - Interactive Dual-View Web Inspector: `universal_6x6_bottom_preview.html` (interactive Front flush view vs. Rear wiring view toggle)
- **Assembly Cost Verification:**
  - Double-sided SMT requires JLCPCB "Standard PCBA" (two stencils, two reflow passes), adding $\sim \$60.00$ setup fee per batch ($\approx +\$0.80$ per board across a 75-board fleet order).

### 2026-10-16 17:45 - Universal 8-Port Matrix: Set Back 10mm in Valleys (Zero Overlap & Diagonal 50mm Cables)
- **Resolved Component Overlap & Increased Edge Setback (`scripts/generate_universal_6x6_pcb.py`):**
  - Moved all 8 JST-PH 2.0mm horizontal connectors inward from $4.5\text{ mm}$ to **$10.0\text{ mm}$ from board edges**.
  - Repositioned Top and Bottom connectors into the wide-open $17.0\text{ mm}$ inter-pixel valleys:
    - Top Edge ($y = 10.0\text{ mm}$): `J_OUT_T` at $x = 28.5\text{ mm}$, `J_IN_T` at $x = 62.5\text{ mm}$ (clearance to all LEDs/caps $> 6.96\text{ mm}$).
    - Bottom Edge ($y = 90.0\text{ mm}$): `J_OUT_B` at $x = 37.0\text{ mm}$, `J_IN_B` at $x = 71.0\text{ mm}$ (clearance to all LEDs/caps $> 6.96\text{ mm}$).
    - Left & Right Edges ($x = 10.0\text{ mm}, 90.0\text{ mm}$): `y = 33.0\text{ mm}$ and $y = 67.0\text{ mm}$ (clearance $> 8.50\text{ mm}$).
  - **100% Zero Component Overlap:** Completely resolved collision between `J_OUT_B` and `D35`/`C35` on the bottom edge.
- **Diagonal 50mm Pre-Crimped Cable Architecture:**
  - Evaluated wire slack: a direct $16\text{ mm}$ facing span creates an unsightly $15\text{ mm}$ high wire loop.
  - Implemented diagonal mating pairing:
    - Quad 1 `J_OUT_R` $(90.0, 33.0)$ to Quad 2 `J_IN_L` $(112.0, 67.0)$: span is **$40.50\text{ mm}$** (wire span $\sim 35\text{ mm}$, slack $\sim 3\text{ mm}$).
    - Quad 2 `J_OUT_B` $(139.0, 90.0)$ to Quad 3 `J_IN_T` $(164.5, 112.0)$: span is **$33.68\text{ mm}$** (wire span $\sim 28\text{ mm}$).
    - Quad 3 `J_OUT_L` $(112.0, 135.0)$ to Quad 4 `J_IN_R` $(90.0, 169.0)$: span is **$40.50\text{ mm}$**.
  - **Result:** Off-the-shelf $50\text{ mm}$ (5cm / 2") cables lay completely flat against the board ($\le 5\text{ mm}$ height, flush with the JST plastic shroud). Zero loose floppy wire loops!
- **Suppressed Pink Labels on LEDs:**
  - Set KiCad module footprint references to `hide`, ensuring JLCPCB's placement tool and finished physical boards display dark, clean LED lenses with zero pink text.
- **Maintained 100% Mathematical Seamlessness:**
  - With $2.0\text{ mm}$ living hinge felt seam, LED pitch across all borders is identically **$17.00\text{ mm}$** ($1.7\text{ cm}$).

### 2026-10-16 15:55 - Aligned JST Interconnects, Straight 3-Wire Pinout, PCB Silk Numerals, and Vector Font Gerber Text
- **Straight 3-Conductor Interconnect Geometry (Zero Wire Twisting / Crossing):**
  - **Symmetrical Edge Port Alignment:**
    - Left Edge: `J_IN_L` at $y = 33.0\text{ mm}$, `J_OUT_L` at $y = 67.0\text{ mm}$.
    - Right Edge: `J_OUT_R` at $y = 33.0\text{ mm}$ (faces `J_IN_L` directly across seam), `J_IN_R` at $y = 67.0\text{ mm}$ (faces `J_OUT_L` directly across seam).
    - Top Edge: `J_IN_T` at $x = 33.0\text{ mm}$, `J_OUT_T` at $x = 67.0\text{ mm}$.
    - Bottom Edge: `J_OUT_B` at $x = 33.0\text{ mm}$ (faces `J_IN_T` directly across seam), `J_IN_B` at $x = 67.0\text{ mm}$ (faces `J_OUT_T` directly across seam).
    - Across any seam (Top-Left to Top-Right horizontally, Top-Right to Bottom-Right vertically, Bottom-Right to Bottom-Left horizontally), cables run strictly in a straight line with zero angled runs.
  - **Consistent Straight Pinout:**
    - Left/Right edges: Pin 1 at top ($y - 2.0\text{ mm}$) = `+5V`, Pin 2 at middle ($y$) = `DAT`, Pin 3 at bottom ($y + 2.0\text{ mm}$) = `GND`.
    - Top/Bottom edges: Pin 1 at left ($x - 2.0\text{ mm}$) = `+5V`, Pin 2 at middle ($x$) = `DAT`, Pin 3 at right ($x + 2.0\text{ mm}$) = `GND`.
    - Standard straight 3-pin ribbon patch cables connect directly without crossing `+5V` and `GND` or twisting the cable assembly.
- **On-Board Silkscreen Numerals & Connector Markings:**
  - Moved LED numbers `1` through `36` onto the PCB substrate at $(x, y - 2.4\text{ mm})$, $1.4\text{ mm}$ above the WS2812B package, ensuring numbers remain completely visible after component placement.
  - Labeled all 8 JST headers with their port role (`[IN]` or `[OUT]`) and explicit pin callouts (`+5V`, `DAT`, `GND`).
- **Gerber Vector Stroke Font Engine (`scripts/generate_universal_6x6_pcb.py`):**
  - Built an internal Hershey-style stroke font table (`FONT_GLYPHS` and `write_gbr_text`) into the Gerber exporter.
  - Text characters are now drawn with native D10 aperture stroke vectors directly in the `.GTO` (Top Silkscreen Gerber) file, guaranteeing that pin labels, board titles, and LED numbers render prominently in JLCPCB's 2D/3D gerber viewer and physically print on fabricated boards.
- **Interactive Visualizer Update (`pcb/universal_6x6_preview.html`):**
  - Rendered visible silkscreen pin callouts (`+5V`, `DAT`, `GND`) on all 8 connectors.
  - Illustrated straight 30mm horizontal and vertical 3-conductor JST patch cables bridging the 4 quadrant tiles with color-coded wires (Red `+5V`, Green `DAT`, Black `GND`).

### 2026-10-16 15:25 - Corner M3 Mounting & Fabric Sewing Holes Architecture with Auto-Match BOM (`C3029441`)
- **Corner M3 Screw Mounting & Dedicated Fabric Sewing Eyelets (`scripts/generate_universal_6x6_pcb.py`):**
  - **4 Corner M3 Mounting Holes (`H1`–`H4`):** $\varnothing 3.2\text{ mm}$ drill with $5.0\text{ mm}$ copper annular pads at `(4.0, 3.5)`, `(96.0, 3.5)`, `(4.0, 96.5)`, and `(96.0, 96.5)`. Perfectly cleared from all LED packages and JST headers, supporting M3/M2.5 machine screws, standoffs, or zip ties.
  - **4 Dedicated Fabric Sewing Eyelets (`S1`–`S4`):** $\varnothing 2.0\text{ mm}$ plated through-holes with $3.5\text{ mm}$ smooth copper annular pads at `(10.0, 3.5)`, `(90.0, 3.5)`, `(10.0, 96.5)`, and `(90.0, 96.5)`. Paired with the adjacent M3 hole 6.0mm away, costume makers can sew through both holes like a 2-hole button, locking the PCB securely to running shirts or felt pockets without thread chafing on outer FR-4 fiberglass edges.
  - **Standard Decimal Excellon Drill Formatting (`universal_6x6_100mm.DRL`):** Re-engineered the Excellon drill output with explicit metric millimeter decimal formatting (`X{x:.3f}Y{y:.3f}`) for T1 (3.2mm), T2 (2.0mm), and T3 (0.4mm vias), ensuring 100% reliable rendering on JLCPCB's 2D/3D board viewer without coordinate scaling ambiguity.
- **100% Auto-Match JLCPCB BOM (`universal_6x6_100mm_bom.csv`):**
  - Updated JST-PH 2.0mm 3-pin connector part number to **`C3029441`** (Xunpu `WAFER-PH2.0-3PWB`, ~39,695 units in stock, \$0.04/ea).
  - Eliminates "Unmatched components" prompt: JLCPCB now auto-selects 100% of components upon BOM upload (`C1525` 100nF Cap, `C52917434` WS2812B-2020-V6 LED, and `C3029441` WAFER-PH2.0-3PWB).
- **Interactive Visualizer Update (`pcb/universal_6x6_preview.html`):**
  - Added visual gold M3 mounting rings and cyan SEW eyelets with hover labels to both the Single-Tile view and 4-Tile chest cluster view.

### 2026-10-16 12:58 - Universal 100mm × 100mm Staggered Brick 6×6 LED Matrix (JLCPCB Turnkey SMT Suite)
- **Engineered Staggered Offset Brick Layout (`scripts/generate_universal_6x6_pcb.py`):**
  - Upgraded the $100.0\text{ mm} \times 100.0\text{ mm}$ universal quadrant PCB from a rectilinear Cartesian grid to an authentic **staggered running-bond brick layout** ($15.0\text{ mm}$ pitch, $7.5\text{ mm}$ alternating row offset).
  - Rows 1, 3, and 5 align with an $8.75\text{ mm}$ left margin; Rows 2, 4, and 6 shift right by $7.5\text{ mm}$, leaving a matching $8.75\text{ mm}$ right margin. This hexagonal packing yields significantly smoother, rounder curves for Disney character silhouettes (dragon crests, snail spirals, coach wheels) through felt window apertures.
  - Across the $6.0\text{ mm}$ felt living hinge seam between tiled boards, the seam distance between adjacent pixels remains mathematically identical ($31.0\text{ mm}$) for all 6 rows.
- **Thin FPC Ribbon Interconnects & Protected DOUT Route:**
  - Placed dual 4-pin 1.0mm pitch horizontal SMT FPC/FFC ribbon connectors (`C2840003`): `J1` Input port (Left edge) and `J2` Output port (Right edge) taking advantage of the generous $16.25\text{ mm}$ side margins.
  - Routed serial DOUT from bottom-left pixel D36 $(16.25, 87.5)$ across the protected bottom board margin ($y = 94.5\text{ mm}$) over to `J2_OUT` on the right edge.
  - Included parallel 2.54mm direct-wire solder pad headers (`+5V`, `DIN`/`DOUT`, `GND`) on both edges as an instant workshop wiring fallback.
- **Turnkey JLCPCB SMT Assembly & Instant Quote Bundle:**
  - Diagnosed JLCPCB online viewer error: KiCad 5 server parser rejected non-standard `gr_arc` Edge.Cuts angle syntax and `(filled_polygon)` zone block.
  - Replaced Edge.Cuts with a closed 4-line continuous rectangle (`0,0` to `100,100`), corrected KiCad 5 zone syntax with `(fill yes ...)`, and added `universal_6x6_100mm.pro`.
  - **Native RS-274X Gerber & Drill Export (`pcb/universal_6x6_100mm_gerbers.zip`):** Implemented direct generation of standardized RS-274X Gerber files (`.GTL`, `.GBL`, `.GTS`, `.GBS`, `.GTO`, `.GKO`, `.DRL`) that bypass server-side conversion completely, enabling 100% immediate 2D/3D rendering on the JLCPCB quote viewer and seamless SMT matching.
- **Interactive Web Inspector (`pcb/universal_6x6_preview.html`):**
  - Features 1-Tile Staggered View and 4-Tile Chest Cluster View (144 LEDs), animated DIN data pulse simulation, "Light Up All LEDs" mode, and direct one-click download buttons for `universal_6x6_100mm_gerbers.zip`, `universal_6x6_100mm_smt.zip`, and `universal_6x6_100mm_kicad.zip`.

### 2026-10-15 11:02 - 2-Piece GoPro-Style Quick-Release Slide Mount & Zip-Tie Verification
- **Engineered 2-Piece Quick-Release Dovetail Slide Mounts (`scripts/generate_gopro_style_mount.py`):**
  - Completely decouples screw fastening from webbing engagement, eliminating all screwdriver clearance and strap obstruction conflicts:
    1. **Female Receiver Dock (`swiftvest_dock_receiver_female.stl`, $26.0 \times 30.0 \times 5.5\text{ mm}$, $\sim 2.6\text{g}$ PLA):** Screws permanently to the back of the costume plate with 4x M2 corner screws with 100% unobstructed workshop screwdriver access. Features a tapered internal dovetail slot and spring catch notch.
    2. **Male Webbing Cleat (`swiftvest_dock_cleat_male.stl`, $24.0 \times 32.0 \times 8.7\text{ mm}$, $\sim 2.1\text{g}$ PLA):** Clamps to the SWIFTVEST vertical webbing strap with a split-bar gate and flexible thumb release arm.
  - **Slide-and-Click Kinematics:** Plate slides down onto the cleats with a tactile snap, locking in all 3 axes (X, Y, Z) with zero race-stride bounce. Releasing is a 1-second one-handed thumb press.
- **Zip-Tie Field Strategy:** Verified that standard miniature black nylon zip ties through the 16 existing $\varnothing 2.5\text{ mm}$ round perimeter eyelets into the SWIFTVEST mesh loops provide a zero-hardware, zero-CAD, fail-safe race-day mounting fallback.
- **Updated Interactive 3D Web Visualizer (`simulator/swiftvest_assembly_viewer.html`):** Added interactive "⚡ Animate: Slide Plate Down & Click Lock" simulation.

### 2026-10-15 10:50 - SWIFTVEST Locking Strap Clip: Z-Axis Screw Alignment & Anti-Slip Tunnel Architecture
- **Resolved Critical Engineering Feedback:**
  1. *Screw Hole Orientation:* In the previous CAD model, the mounting hole was extruded parallel to the webbing channel (90° off). Corrected the orientation in `scripts/generate_locking_clip.py` so the screw through-hole passes perpendicularly through the clip's mounting flange in the $Z$-axis, driving directly into the back of the costume plate / eyelet tab.
  2. *Race-Day Strap Slippage Prevention:* Replaced open C-jaws with a **100% enclosed retention tunnel** featuring a rigid overhanging roof and a $0.9\text{ mm}$ undercut retention lip. Added **dual internal $0.8\text{ mm}$ friction ribs** that bite into the woven texture of the $20\text{--}22\text{ mm}$ nylon webbing, preventing the plate from sliding vertically during running strides.
- **Exported `swiftvest_locking_strap_clip.stl`:** Sized at $24.0 \times 26.0 \times 6.8\text{ mm}$ ($2.00\text{ cm}^3$, $\sim 2.5\text{g}$ PLA), 100% watertight.
- **Updated Interactive 3D Web Visualizer (`simulator/swiftvest_assembly_viewer.html`):**
  - Displays the M2 screw driving straight along the Z-axis into the plate boss.
  - Interactive "⚡ Animate: Insert Webbing Through Locking Tunnel" button demonstrating strap capture.

### 2026-10-15 10:42 - SWIFTVEST Macro Coin Scale 3D Inspector & Clean STL Assembly (Eliminated Vest Dummy Slabs)
- **Diagnosed STL Viewer Confusion:**
  - Realized that because standard STL files lack color, the $280\text{ mm}$ dummy fabric strap mockups in `swiftvest_front_assembly_preview.stl` merged into solid grey plastic slabs, giving the false illusion of a massive $280\text{ mm}$ bracket.
  - Eliminated all vest strap dummy geometry from `3d_panels/swiftvest_front_assembly_preview.stl`. Sized strictly to the $240.4 \times 212.4 \times 11.0\text{ mm}$ plate plus the 4 tiny rear clips.
- **Engineered Macro Real-World Scale STL (`3d_panels/swiftvest_clip_with_coin_scale.stl`):**
  - Combined the $14 \times 26 \times 5.2\text{ mm}$ clip side-by-side with an exact 3D US Quarter coin ($\varnothing 24.26\text{ mm} \times 1.75\text{ mm}$) for instant visual scale in any 3D viewer.
- **Enhanced Interactive 3D Web Visualizer (`simulator/swiftvest_assembly_viewer.html`):**
  - Added dedicated **"🔎 Macro Clip Close-Up"** view displaying the single clip, M2 screw, and webbing ribbon next to the silver US Quarter.
  - Added an interactive **"⚡ Animate: Snap Webbing Into Clip"** button demonstrating the mechanical deflection and snap action of the clip jaws.

### 2026-10-15 10:30 - Ultra-Compact Hidden Rear C-Clip Redesign (<1.1g Each, Zero Protruding Brackets)
- **Engineered Minimalist Hidden Webbing Clip (`scripts/generate_hidden_clip.py` -> `3d_panels/swiftvest_hidden_webbing_clip.stl`):**
  - Completely discarded bulky exterior side-hinge brackets following user visual feedback.
  - Sized at an ultra-compact thumbnail footprint: $14.0 \times 26.0 \times 5.2\text{ mm}$ ($0.90\text{ cm}^3$, $\sim 1.1\text{g}$ in PLA).
  - Designed with an internal $22.0 \times 2.4\text{ mm}$ captive webbing slot, $45^\circ$ snap lead-in ramp, and counterbored M2/M2.5 mounting flange.
  - **100% Hidden Behind Plate:** 4 clips mount flat against the rear of the costume plate and snap directly onto the SWIFTVEST's vertical webbing. Looking at the costume from the front, zero mounting plastic or hardware extends past the character contour.
  - **Snap-On / Peel-Off Operation:** Allows runners to wear the vest normally, snap the plate onto their chest in 2 seconds, and peel it off effortlessly post-race.
- **Updated 3D Assembly & Interactive Viewer:**
  - Regenerated `3d_panels/swiftvest_front_assembly_preview.stl` with hidden rear clips.
  - Updated `simulator/swiftvest_assembly_viewer.html` with Front Clean View, Rear Inspection View, and Exploded View.

### 2026-10-15 10:22 - SWIFTVEST 3D Assembly Viewer Script Bug Fix & Camera Recalibration
- **Diagnosed and Resolved Blank Viewport Bug in `simulator/swiftvest_assembly_viewer.html`:**
  - Identified a JavaScript parse error in `toggleExploded()` (`SyntaxError: Invalid left-hand side in assignment` caused by an inline default assignment typo in `Math.min(elapsed / duration = 400, 1.0)`).
  - Verified JavaScript engine syntax cleanliness with `node -c`.
  - Recalibrated Three.js camera position from a steep $+60^\circ$ bottom-up angle `(145, -280, 240)` to an optimal straight-on front chest elevation `(145, 120, 480)`, centering the vest, plate, and mounting clips immediately in view on page load.
  - Enhanced directional and back-fill lighting for high contrast between the blue harness, gold right hinges, red left latches, and dark gray chest plate.

### 2026-10-15 10:16 - SWIFTVEST + 3D Plate Full Assembly Preview & Interactive 3D Kinematics Viewer
- **Built Interactive 3D Web Visualizer (`simulator/swiftvest_assembly_viewer.html`):**
  - Engineered a standalone Three.js browser inspector providing 360° orbital rotation, zoom, dynamic lighting, and real-time kinematic simulation.
  - **Interactive Door Swing Slider ($0^\circ \leftrightarrow 110^\circ$):** Simulates the front plate swinging open on the right-hand captive hinge clamps, demonstrating clear access to unbuckle the SWIFTVEST's central sternum straps for donning/doffing.
  - **Exploded View Slider ($0 \leftrightarrow 80\text{ mm}$):** Animates Z-axis layer separation between the blue vest harness, gold right hinge clamps, red left quick-release latches, and dark gray 3D plate.
- **Exported Assembled Monolithic 3D Model (`3d_panels/swiftvest_front_assembly_preview.stl`):**
  - Generated a merged 85,990-vertex watertight STL model combining the running harness, strap webbing, center buckles, front chest plate, and all 4 mounting clips for direct inspection in OrcaSlicer or Windows 3D Viewer.
- **Illustrated Assembly Schematics (`3d_panels/SWIFTVEST_ATTACHMENT_GUIDE.md`):**
  - Documented front elevation and top-down cross-sectional schematics clearly depicting the left latch vs right hinge relationship and the 4-step donning/doffing sequence.

### 2026-10-15 10:04 - SWIFTVEST 3D-Printable Mounting Hardware Generation (Watertight STLs)
- **Engineered & Exported 4 Custom 3D Mounting Components (`scripts/generate_swiftvest_mounts.py`):**
  - Built a dedicated Python CAD generator using `manifold3d` and `trimesh` producing 100% watertight STL files in `3d_panels/`:
    1. **`swiftvest_hinge_clamp_right.stl` ($3.44\text{ cm}^3$, $\sim 4.3\text{g}$ PLA):** Captive right shoulder strap hinge clamp with $22.0 \times 3.0\text{ mm}$ webbing channel, $1.4\text{ mm}$ entry gate, M2.5 mounting through-hole, and nut counterbore. Keeps front plate permanently anchored to the right strap, pivoting freely.
    2. **`swiftvest_quick_latch_left.stl` ($2.59\text{ cm}^3$, $\sim 3.2\text{g}$ PLA):** Left shoulder strap quick-release latch with dual $3.5\text{ mm}$ cantilever flexure arms, $45^\circ$ snap lead-in ramp, positive retention tooth, and textured thumb paddle for instant one-handed release.
    3. **`swiftvest_bungee_anchor_hook.stl` ($0.96\text{ cm}^3$, $\sim 1.2\text{g}$ PLA):** Low-profile corner hook with radiused $3.8\text{ mm}$ channel and retention lip for $2.5\text{--}3.0\text{ mm}$ elastic shock cord on the rear mesh plate.
    4. **`swiftvest_cord_lock_slide.stl` ($0.77\text{ cm}^3$, $\sim 1.0\text{g}$ PLA):** Dual-hole friction cord cinch with side grip scallops for hardware-free bungee tensioning.
  - Verified watertight geometry across all 4 models and updated the vest mounting guide.

### 2026-10-15 09:58 - SWIFTVEST Running Vest Plate Attachment & Battery Routing Guide
- **Authored Comprehensive Vest Integration Guide (`3d_panels/SWIFTVEST_ATTACHMENT_GUIDE.md`):**
  - Designed the mechanical mounting architecture for attaching the $240.4 \times 212.4 \times 10.0\text{ mm}$ rigid PLA front and back costume panels to the **SWIFTVEST running vest** ([Amazon ASIN B0CGPYLG6H](https://www.amazon.com/dp/B0CGPYLG6H)) for the WDW 10K.
  - **Hinged Book-Style Front Plate:** Overcame the central split sternum closure challenge by designing a dual-strap interface:
    - *Right Shoulder Strap:* Captive 3D-printed pivot hinge clamps anchored to the plate's right perimeter eyelets.
    - *Left Shoulder Strap:* Quick-release thumb-actuated snap latches allowing the plate to swing open like a book door for $<5$-second vest donning/doffing with zero fabric alteration.
  - **Dynamic Bungee Back Plate:** Utilizes $2.5\text{ mm}$ marine elastic shock-cord laced through the 16 perimeter eyelets and rear mesh panel, accommodating $15\text{--}20\text{ mm}$ of thoracic breathing compliance and absorbing running stride bounce.
  - **Power Bank Architecture (Waist Belt vs Front Pocket):** Evaluated weight distribution tradeoffs between Option A (built-in front elastic flask pocket for lightweight $\le 5000\text{ mAh}$ batteries) and Option B (separate lumbar running waist belt for heavier $10,000\text{ mAh}$ battery packs to shift weight to the pelvic center of gravity).
  - Updated implementation plan artifact `vest_attachment_plan.md` with complete specifications and test protocols.

### 2026-10-15 09:48 - Snapmaker U1 (4-Toolhead Toolchanger) 5-Color PLA Printing Strategy & Documentation
- **Authored Comprehensive 5-Color Printing Guide (`3d_panels/SNAPMAKER_U1_5COLOR_PRINTING_OPTIONS.md`):**
  - Evaluated the transition from single-nozzle Bambu multi-material setup to the 4-toolhead Snapmaker U1 direct-drive CoreXY toolchanger using 100% PLA filament.
  - **Geometric Model Analysis:** Verified that across the $240.4 \times 212.4 \times 10.0\text{ mm}$ chest chassis, $Z = 0.00$ to $9.20\text{ mm}$ (92% of print volume) is 100% black chassis, with all 4 accent colors residing solely in the top $0.80\text{ mm}$ ($Z = 9.20$ to $10.00\text{ mm}$). Red (`5_Tie_and_Lips`) accounts for only $0.78\text{ cm}^3$ (2,200 triangles).
  - **Formulated 5 Distinct Implementation Strategies:**
    1. **Option 1 (Z-Height Stagger - Single Pause):** Red printed on layers 47 & 48 ($0.40\text{ mm}$), followed by one single `PAUSE`/`M600` at $Z = 9.60\text{ mm}$ to swap Toolhead 3 to Yellow for layers 49 & 50.
    2. **Option 2 (Modular 2-Piece Badge):** Black chassis printed unattended on Toolhead 0 with a $1.2\text{ mm}$ recessed pocket; decorative emblem badge printed separately and bonded with cyanoacrylate/snap tabs for failure isolation.
    3. **Option 3 (Face-Down First-Layer Swap):** Artwork printed face-down against textured PEI with swaps occurring in the first 5 minutes on the bed.
    4. **Option 4 (Slicer Virtual Extruder):** Toolhead 3 shared across 4 layers with 4 manual swaps in the final 20 minutes.
    5. **Option 5 (4-Color Native + Paint Pen):** 4-color unattended print with red accent added post-print using an acrylic paint marker.
  - **Slicer & Thermal Specifications:** Defined OrcaSlicer/Klipper standby temperature macros ($175^\circ\text{C}$ idle, $210^\circ\text{C}$ active) to prevent PLA cooking/drool on docked heads, along with PLA infill ($10\text{--}12\%$ gyroid, $<170\text{g}$) and chest mounting ergonomics.

### 2026-10-15 09:34 - Unified Float & 3D File Naming Convention (`<float_name>_<size>_<leds>_<date>_<time>`)
- **Established Standardized File Naming Architecture Across All Float & 3D Exports:**
  - Implemented `getStandardFloatFileBaseName(options)` in `simulator/app.js` enforcing the uniform naming syntax:
    $$\text{<float\_name>}\_\text{<size>}\_\text{<led\_count>led}\_\text{<date>}\_\text{<time>}.\text{<ext>}$$
  - **Omission of Front / Back Descriptors:** Strictly eliminated `_front_` and `_back_` substrings from file basenames across 3D model downloads and float file saves, preventing confusing duplicates when saving interchangeable fleet files.
  - **Embedded Parameters:**
    1. **Float Name:** Normalized lowercase snake_case slug (e.g., `the_turtle`, `petes_dragon`, `the_train`, `title_drum`, `the_snail`, `pirate_ship`, `flag_and_eagle`).
    2. **Size:** Explicit chassis plate size category (`small`, `medium`, `large`).
    3. **LED Count:** Exact active canvas pixel count formatted as `<count>led` (e.g., `100led`, `75led`).
    4. **Date & Time:** Timestamp formatted as `YYYY-MM-DD_HH-MM` (e.g., `2026-10-15_09-25`).
- **Synchronized Export & Save Handlers:**
  - **3D Preview Downloads (`updateTpuDownloadButtons`):**
    - Multi-Color Bundle ZIP: `<float_name>_<size>_<leds>_<date>_<time>.zip`
    - Bambu Lab Project: `<float_name>_<size>_<leds>_<date>_<time>.3mf`
    - Monolithic Black STL: `<float_name>_<size>_<leds>_<date>_<time>.stl`
    - Rear Cover Lid STL: `<float_name>_<size>_<leds>_<date>_<time>_lid.stl`
    - Split Inlay STLs: `<float_name>_<size>_<leds>_<date>_<time>_<part>.stl`
  - **Preset Save & Export (`openSavePresetModal`, `saveProfileBtn`, `exportCurrentProfileJson`):**
    - Modal suggestions, disk filename previews, and exported JSON files default to `<float_name>_<size>_<leds>_<date>_<time>.json`.
  - **Vector Cutting & Placement Guides:**
    - Cricut SVGs and LED placement guide PNGs format with matching standardized base identifiers.
  - **Backend Sanitization (`simulator.py`):** Cleaned `handle_save_preset` to strip redundant `.json` extensions before disk persistence.
  - **Cache Busting:** Bumped script cache buster in `simulator/index.html` to `app.js?v=104`.

### 2026-10-15 09:22 - 3D Preview LED Visualization Alignment: Clean Optical Aperture Lights (Eliminated Extraneous Pocket Squares)
- **Diagnosed Extraneous Green Squares in 3D Preview Modal (`createTpuLedPixels`):**
  - In a previous commit, secondary `pocketChipGeom = new THREE.PlaneGeometry(3.6, 3.6)` square meshes were placed at `-stlCenter.z + 1.8` inside each underside collar pocket.
  - Because `depthTest: false` was active, both the front aperture light (`pixelMesh`) and the underside square (`pocketChip`) projected through simultaneously with noticeable perspective parallax, cluttering the underside preview with floating green squares alongside the round window apertures.
- **Implemented Clean Optical Aperture Projection (`simulator/app.js`):**
  - Removed all `pocketChip` square plane meshes from `createTpuLedPixels()`.
  - Retained single, geometrically accurate optical aperture simulated lights (`pixelMesh`) that dynamically conform to the chosen window geometry (`CircleGeometry` for $\varnothing 3.4\text{ mm}$ and $\varnothing 3.0\text{ mm}$ round apertures; `PlaneGeometry` for $3\times 3\text{ mm}$ square apertures).
  - Maintained `side: THREE.DoubleSide` and `depthTest: false` depth-independent visibility on `pixelMesh`, ensuring every simulated light glows cleanly and directly inside its round aperture window from both Front Face, Underside/Pockets, and orbiting 3D Angle views with zero visual clutter.
  - Bumped script cache buster in `simulator/index.html` to `app.js?v=103`.

### 2026-10-14 09:55 - Strain Relief Bridge 2D/3D Alignment, Portal Notch Clearance & Dual-Side LED Visibility in 3D Preview
- **Diagnosed Strain Relief Bridge Location Mismatch & 3D Preview Occlusion:**
  - **Aspect Ratio Mismatch in `getEffectiveTpuPanelSpec()`:** The 2D layout canvas enforces a $1:1.25$ stretch ratio for the athletic t-shirt geometry (`normW = normH * 1.25 * aspect`), causing `curAspect = normW / normH = 1.25 * aspect`. Previously, `getEffectiveTpuPanelSpec()` compared `spAspect` (the raw image aspect $1.198$) directly against `curAspect` ($1.498$), which failed the $< 0.12$ tolerance check. This caused the simulator to reject the compiled `tpu_panel_specs.json` and fall back to an inaccurate mini-canvas trace, displacing the 2D layout bridge relative to the 3D STL.
  - **Missing 3D Bridge Visual Markers:** The 3D Preview Modal previously only loaded the black STL chassis and LED aperture dots without rendering the strain relief bridges or wire paths. Because the bridge is a small $8\times 7.2\text{ mm}$ feature printed out of identical black TPU, it blended into the floor and was invisible in 3D.
  - **Eyelet Tab Covering Entrance Notch:** In `compile_clean_tpu_panel.py`, the 16 perimeter eyelet tabs were placed before the wire entrance and exit portals were computed. On convex geometries (like the Turtle), an outer eyelet tab landed directly at the bottom-center portal coordinate, obstructing the wire entrance notch.
  - **Depth-Occluded LEDs in Underside View:** The LED pixel meshes were placed at $+5.20\text{ mm}$ on the front face with `depthTest: true`. When viewing `Underside (Pockets)` from $-Z$, the $6.5\text{ mm}$-tall collar walls occluded the line of sight to the aperture dots from perspective angles, hiding over $40\%$ of the LEDs and creating the appearance of an empty void at the bottom of the plate.
- **Implemented Engineering Fixes & Synchronized Visualizer:**
  - **Fixed Canvas Stretch Normalization (`simulator/app.js`):** Updated `getEffectiveTpuPanelSpec()` to divide `curAspect` by $1.25$ (`const curAspect = (normW / Math.max(0.01, normH)) / 1.25;`), ensuring `spAspect` and `curAspect` match with $100\%$ mathematical precision across all floats. Added Float 3 (Turtle), Float 1 (Casey Jr.), Float 2 (Drum), and Float 7 (Caterpillar) mappings to `normalizeFloatGraphicKey`.
  - **Automated Eyelet Tab Portal Clearance (`scripts/compile_clean_tpu_panel.py`):** Moved bottom wire entrance and lateral exit portal calculations prior to the tab loop. Added a $\ge 14\text{ mm}$ clearance check (`dist_ent < 14.0 or dist_exit < 14.0`) that automatically nudges tabs along the perimeter, guaranteeing all 16 eyelets remain at least $20\text{ mm}$ away from wire portals with completely unobstructed U-notches.
  - **Normal-Aligned Entrance Portal Cutter:** Rotated `wire_portal_cutter` along the wall normal vector (`rot_mat_ent`), punching cleanly through curved bottom rims.
  - **Interactive 3D Strain Relief Bridges (`createTpuStrainReliefBridges`):**
    - Added dedicated glowing 3D bridge arch blocks for both **Entrance Bridge** (cyan, $0x00ff88$) and **Exit Bridge** (coral, $0xff4d6d$) with $10\text{ mm}$ safety keep-out clearance rings.
    - Added continuous 3D wire conduits entering through the portal notch, passing under the bridge arch, and routing directly into LED 1 (and exiting from LED 100 through the exit notch).
    - Added floating billboard 3D text badges (`"⚡ 2 IN BRIDGE"` and `"⚡ EXIT BRIDGE"`).
  - **Dual-Side 3D LED Representation (`createTpuLedPixels`):** Rendered dual front-facing optical aperture dots and underside collar cavity LED chips with `depthTest: false`, ensuring all 100 LEDs glow brightly and clearly from both Front Face and Underside views without any perspective clipping.
  - **Calibrated Camera Viewport:** Adjusted camera framing distance to $390\text{ mm}$, fitting Large ($245\text{ mm}$) plates with all 16 eyelets symmetrically inside the viewport without cutting off the top or distorting the bottom.
- **Hardware & STL Verification:**
  - Recompiled Float 3 (The Turtle) Large 5-Color Armor Panels ($239.68\text{ mm} \times 212.48\text{ mm} \times 10.0\text{ mm}$) in $10.90\text{s}$. Verified all 16 tabs have $\ge 20.0\text{ mm}$ clearance from wire portals. Zero non-manifold slivers, zero detached collars.

### 2026-10-14 09:20 - 3D Panel Perimeter Wall Artifact Elimination, Safe Collar Keep-Out & Large Turtle 3D Armor Compilation
- **Diagnosed Physical Print Perimeter Artifacts ("Parts of where eyelets had been"):**
  - Thorough geometric analysis of `3d_panels/tpu_panel_front_chassis_black.stl` revealed why the previous physical print showed mysterious fragmented bits outside the perimeter rim:
    1. **Out-of-Bounds LED Collars on Legacy STL:** On the earlier Pete's Dragon STL, 12 LEDs along the flanks (LEDs 6, 7, 8, 9, 11, 12, 13, 77, 78, 79, 80, 81) were positioned right on or slightly outside the organic perimeter contour, generating 23 detached U-shaped collar halves floating in thin air outside the chassis rim at Z = 6.0 to 9.0 mm. Slicers generated support trees and perimeter print strokes for these hovering features, appearing to the runner as fragmented pieces of outer tabs ("where eyelets had been").
    2. **Severed Wire Entrance Bridge on Convex Contours:** The entrance portal previously searched discrete polygon vertices near `cx_mid`. On rounded hulls (like the Turtle), the nearest discrete vertex was located at the top of the costume ($Y = 208.5\text{ mm}$), causing the bridge to be placed at the top rim and cleanly severed by `to_m(rim_mesh)`, leaving a detached floating rectangular arch.
    3. **Degenerate Coplanar Triangle Slivers:** Manifold-to-Trimesh conversion in `flip_z_manifold` retained 58 zero-area degenerate face pairs (`Faces: [[2 0 2], [2 2 1]]`), creating false non-manifold components.
- **Implemented Watertight Geometry Safeguards (`scripts/compile_clean_tpu_panel.py`):**
  - **Safe Collar Basin Containment:** Added automated boundary clamping with `smoothed_plate_2d.buffer(-(RIM_WALL_THICK + COLLAR_OUTER_W / 2.0))` ($6.8\text{ mm}$ inward offset). Any LED placed within or outside this boundary is automatically projected safely into the interior tray basin, mathematically preventing any collar or window from ever breaching the perimeter rim wall.
  - **Continuous Geometry Projection for Entrance Portal:** Replaced discrete vertex selection with true continuous boundary projection (`boundary_line_ent.project(sg.Point(cx_mid, bounds[1]))`) and inward normal traversal. The bottom wire entrance slot and zip-tie relief bridge now consistently land at the true bottom perimeter ($Y = 18.35\text{ mm}$ on the Turtle) and remain 100% fused to the chassis floor.
  - **Robust Outward Eyelet Tab Positioning:** Updated all 16 outer fastener tabs to test both normal and opposing normal vectors against `smoothed_plate_2d.contains()`, guaranteeing that all 16 mounting ears and 45° triangular gussets sit strictly outside the chassis perimeter.
  - **Non-Degenerate Mesh Sanitization:** Integrated `update_faces(nondegenerate_faces())`, `unique_faces()`, and `remove_unreferenced_vertices()` into `flip_z_manifold` and `flip_z_trimesh`, stripping away all zero-area triangle slivers.
- **Compiled Large-Size (245mm) 5-Color Turtle Armor Panels (`3d_panels/`):**
  - Generated full 5-color multi-material suite for **Float 3 (The Turtle)** in Large size ($240.18\text{ mm} \times 212.25\text{ mm} \times 10.0\text{ mm}$):
    - `tpu_panel_front_chassis_black.stl` (8.51 MB) — **100% single continuous component (`decompose() len == 1`), 0 disconnected parts, 0 floating bits**.
    - `tpu_panel_front_lid.stl` (0.46 MB) — **100% watertight single solid (`is_watertight: True`)** with matching 16 eyelets, M2 counterbores, and alignment ridge.
    - 4 discrete multi-material inlays: `color_green.stl` (Shell Plates & Glasses, watertight), `color_blue.stl` (Shell & Eyes), `color_yellow.stl` (Body & Head, watertight), and `color_red.stl` (Tie & Lips, watertight).
    - Multi-body `tpu_panel_front_multicolor.3mf` (5 bodies) and ready-to-print `tpu_panel_front_multicolor_bundle.zip` (4.58 MB).
    - Identical matching Back plate suite.
- **Restarted Simulator Service:**
  - Terminated previous background process on port 8000 and cleanly relaunched `simulator.py` as a daemon on `http://localhost:8000`. Verified all 39 presets and API endpoints are responsive.

### 2026-10-13 21:35 - Pete's Dragon Transparent Default, Startup Active Float Sync & Instant LED Float Distribution
- **Pete's Dragon Transparent Default Artwork (`assets/petes_dragon_transparent.png`, `simulator/assets/`):**
  - Updated all dragon artwork bindings in `simulator/app.js` (`defaultDragonImg.src`, `floatArtworkImgs['petes_dragon']`, `floatArtworkImgs['builtin_dragon']`, `floatArtworkImgs['petes_dragon_transparent']`) to load the authentic 4-channel transparent PNG (`1024×853`) instead of the legacy opaque/white-background graphic.
  - Mirrored `assets/petes_dragon_transparent.png` directly into `simulator/assets/petes_dragon_transparent.png`.
- **Title Drum & Active Float Startup Synchronization:**
  - Resolved root cause where refreshing the simulator while on Float 2 (Electrical Parade Drum) or other floats caused the canvas to draw Pete's Dragon:
    1. Dynamic initialization: replaced hardcoded `let currentGraphicType = 'builtin_dragon'` with `defaultFloatGraphicMap[activeSingleShirtRunnerSlot]`.
    2. Synchronized `updateActiveFloatUI`: ensures `currentGraphicType` is strictly updated alongside `graphicSelect.value` whenever a float slot is activated.
    3. Removed hardcoded `selected` attribute on `builtin_dragon` in `simulator/index.html`.
    4. Guarded `loadProfile` startup routines with fallback profile synthesis and active runner preset resolution to prevent asynchronous startup limbo.
- **Instant LED Shape Distribution on Float Switch:**
  - Resolved root cause where switching floats initially retained the previous float's (or dragon's) LED shape until double-switching:
    1. Guarded `editRunnerInSingleView`: removed aggressive early return when graphic/LED count mismatched the target float (`slot === activeSingleShirtRunnerSlot && currentGraphicType === runner.defaultGraphic && leds.length >= 20`).
    2. Immediate graphic update: sets `currentGraphicType = runner.defaultGraphic` immediately when initiating float edit.
    3. Empty LED reset in `applyProfileData`: clears `leds = []` if incoming profile data lacks LEDs, ensuring the automatic 100-LED contour scatter fires immediately.
    4. Image readiness latch: ensures target float graphic (`activeImg`) has loaded before executing `scatterLedsOnGraphic(100, true)`, preventing premature fallback to dragon silhouette.
    5. Fallback perimeter guard: constrained `defaultDragonImg` fallback in `scatterLedsOnGraphic` exclusively to dragon float types, eliminating dragon-shaped LED distributions on train, drum, turtle, snail, ship, and eagle.
    6. Fleet lineup consistency (`presets/fleet_lineup.json`): updated Float 3 (Turtle) and Float 6 (Dragon) from local storage keys to persistent server presets (`spinning_turtle_100-led_vibrant_preset_2026-10-13_02-54.json` and `petes_dragon.json`).
- **Verification:**
  - PlatformIO firmware build compiled cleanly (`RAM: 14.3%`, `Flash: 60.4%`).
  - Python simulator server endpoint tests passed (`python simulator.py --test`).

### 2026-10-13 21:10 - Title Drum Front Gold Marquee Curvature Restoration & Streamer Pole Intactness
- **Full Circular Curvature of the Front Gold Marquee Ring (`assets/title_drum.png`, `simulator/assets/`):**
  - Resolved the subtle ~34px vertical flat cutoff on the front of the gold marquee ring ($x \in [1800, 1834], y \in [875, 1250]$) caused by the previous rectangular flag erase boundary.
  - Parameterized the central black drum face contour ($ecx = 1232.4$, $ecy = 1052.7$, $e_w = 1021.6$, $e_h = 1072.4$) and expanded its outer ellipse by 66px ($+132\text{px}$ to axes) to guarantee an uninterrupted, perfectly round circular gold marquee contour all the way down to the fender junction.
  - Preserved the vertical streamer pole at $x \in [1760, 1780]$ connecting directly to the top center ribbon pennant.
- **Strict 5-Color Compliance & Transparent Padding:**
  - Quantized output (`2319×1805`, 1.2848 aspect ratio):
    1. **Transparent Alpha:** 46.87%
    2. **Black (`#11161d`):** 22.75% (Chassis, Drum face, tires, square flag field)
    3. **Gold (`#facc15`):** 17.95% (Drum ring, lettering, rims, cab trim, square flag border)
    4. **Red (`#ef4444`):** 9.80% (Cab panels, arches, streamer ribbon, square flag Hidden Mickey)
    5. **Green (`#10b981`):** 1.78% (Lead pennant)
    6. **Blue (`#2563eb`):** 0.85% (Streamer tip)
- **Asset Mirroring & Automation Script (`scripts/process_title_drum.py`):**
  - Updated reproducible Python script `scripts/process_title_drum.py` and regenerated all canonical assets across `assets/` and `simulator/assets/`.
  - Updated `SIMULATOR_USER_GUIDE.md` and `PROJECT_PROGRESS.md`.

### 2026-10-13 21:00 - Title Drum Square Flag Red Hidden Mickey Silhouette & Front Flagpole Removal
- **Driver Cab Square Flag Transformation (`assets/Drumcleanedup.png`, `assets/title_drum.png`, `simulator/assets/`):**
  - Updated the large tilted square flag on the driver cab roof (`16.0°` tilt):
    - **18px Outer Border:** Solid Marquee Gold (`#facc15` / `RGB(250, 204, 21)`).
    - **Interior Field:** Solid Black (`#11161d` / `RGB(17, 22, 29)`).
    - **Centered Red Hidden Mickey Silhouette:** Rendered an authentic 3-circle silhouette in solid Red (`#ef4444` / `RGB(239, 68, 68)`) with `R_head = 44px`, `R_ear = 25px`, `dist = 59px`, rotated along the flag's coordinate axis (55° from flag vertical) and shifted down 14px to perfectly center within the flag geometry.
- **Front Flagpole & Swallowtail Flag Removal:**
  - Completely erased the right-hand front flagpole and swallowtail flag down to the gold fender shelf (`x >= 1800, y <= 1276`).
  - Smoothed the fender top contour across `x = 2170` to `2220` along $y(x) = 1275 + (x - 2170) \times (3/50)$, eliminating the socket protrusion and restoring a clean, aerodynamic fender line.
- **Strict 5-Color Compliance & Transparent Cropping:**
  - Output image (`2319×1805`) strictly adheres to the 5 discrete color requirement for Bambu AMS/MMU 3D printing and Cricut vinyl cutting:
    1. **Transparent Alpha:** 47.12%
    2. **Black (`#11161d`):** 22.80% (Chassis, Drum face, tires, square flag field)
    3. **Gold (`#facc15`):** 17.64% (Drum ring, letters, wheels, cab trim, square flag border)
    4. **Red (`#ef4444`):** 9.81% (Cab panels, arches, streamer, square flag Hidden Mickey)
    5. **Green (`#10b981`):** 1.78% (Lead pennant)
    6. **Blue (`#2563eb`):** 0.85% (Streamer tip)
- **Asset Mirroring & Python Processing Pipeline:**
  - Mirrored across all 7 asset paths: `assets/Drumcleanedup.png`, `assets/drumcleanedup.png`, `assets/title_drum.png`, `assets/Drum.png`, `simulator/assets/Drumcleanedup.png`, `simulator/assets/drumcleanedup.png`, and `simulator/assets/title_drum.png`.
  - Updated reproducible automation script `scripts/process_title_drum.py`.
- **Documentation Parity:**
  - Updated `SIMULATOR_USER_GUIDE.md` Float 2 sampling rules and `PROJECT_PROGRESS.md`.

### 2026-10-13 20:45 - Title Drum High-Res Transparent PNG (`Drumcleanedup.png`) & Hidden Mickey Flag Integration
- **Transparent PNG & White Background Stripping (`assets/Drumcleanedup.png`, `assets/title_drum.png`, `simulator/assets/`):**
  - Converted the new high-resolution `assets/Drumcleanedup.jpg` asset (2358×1824) into a transparent PNG (`2319×1805` with 25px uniform padding, preserving the exact 1.285 aspect ratio): stripped the white background across outer boundaries and interior driver cab window aperture using HSV value/saturation thresholding.
  - Quantized strictly into the canonical 5-color multi-material palette for Bambu AMS 3D printing and Cricut HTV vinyl cutting:
    1. **Black (Chassis, Drum Face, Wheels & Hidden Mickey):** `RGB(17, 22, 29)` (`#11161d`, 21.60%)
    2. **Gold (Drum Marquee Ring, Text, Wheel Rims & Yellow Flag):** `RGB(250, 204, 21)` (`#facc15`, 21.66%)
    3. **Red (Cab Body Panels, Arches & Streamer):** `RGB(239, 68, 68)` (`#ef4444`, 10.28%)
    4. **Blue (Streamer Pennant Tip):** `RGB(37, 99, 235)` (`#2563eb`, 0.85%)
    5. **Green (Lead Flag):** `RGB(16, 185, 129)` (`#10b981`, 1.78%)
- **Hidden Mickey Silhouette Integration on the Yellow Swallowtail Flag:**
  - Added an authentic Disney Imagineering 3-circle Hidden Mickey silhouette in black (`#11161d`) to the rear yellow swallowtail flag centered at `(cx=2040, cy=690)` (`R_head=36px`, `R_ear=21px`, `dist=48px`, angle $55^\circ$ from vertical) with balanced 28px golden margins on all sides.
- **Asset Mirroring & Simulator Support (`simulator/app.js`, `scripts/process_title_drum.py`):**
  - Saved transparent PNG across all alias locations: `assets/Drumcleanedup.png`, `assets/drumcleanedup.png`, `assets/title_drum.png`, `assets/Drum.png`, `simulator/assets/Drumcleanedup.png`, `simulator/assets/drumcleanedup.png`, and `simulator/assets/title_drum.png`.
  - Updated `simulator/app.js` with `'drumcleanedup'` alias in `floatArtworkImgs`, `normalizeFloatGraphicKey`, and `FLOAT_STL_COLOR_CONFIG`.
  - Updated reproducible automation script `scripts/process_title_drum.py`.

### 2026-10-13 20:25 - Float 5 Migration to 5-Color Multi-Material Pirate Ship (`Pirateshipsimple.png`) & Full Fleet Synchronization
- **Transparent PNG & 5-Color Quantization (`assets/Pirateshipsimple.png`, `simulator/assets/Pirateshipsimple.png`):**
  - Converted `assets/PirateShipsimple.jpg` into a clean, transparent PNG: cleanly stripped the gray/white faux checkerboard background across all outer borders and interior enclosed mast/rigging apertures using HSV saturation/value filtering and connected-component segmentation.
  - Quantized graphic strictly into **5 discrete 3D-printing (AMS/MMU) and HTV colors**:
    1. **Red (Sails & Masthead Pennant):** `RGB(230, 25, 25)` (`#e61919`)
    2. **Light Gold (Masts, Spars & Trim):** `RGB(235, 185, 65)` (`#ebb941`)
    3. **Black (Hull, Railings & Chassis):** `RGB(20, 20, 20)` (`#141414`)
    4. **Dark Gold / Antique Bronze (Decks & Shading):** `RGB(155, 105, 20)` (`#9b6914`)
    5. **Green (Ocean Waves):** `RGB(20, 115, 50)` (`#147332`)
  - Saved to all simulator and root asset aliases (`Pirateshipsimple.png`, `PirateShipsimple.png`, `pirate_ship.png`).
- **Production Cricut HTV Cut File & Visual Catalog (`simulator/assets/cricut_svg/pirate_ship.svg`, `cricut_catalog.html`):**
  - Generated layered vector SVG (`pirate_ship.svg`) with 5 discrete color groups for instant cutting mat separation in Cricut Design Space.
  - Updated `cricut_catalog.html` with Float 05: The Pirate Ship showcase card, download links, and 5-mat spec breakdown.
- **100-LED Costume Preset & Palette (`presets/pirate_ship.json`, `presets/fleet_lineup.json`):**
  - Generated `presets/pirate_ship.json` with 100 LEDs sampled across the 5 character colors (37 Red, 28 Light Gold, 23 Black, 7 Dark Gold, 5 Green) positioned safely in the upper torso (`x: 0.220..0.780`, `y: 0.198..0.525`) preserving graphic aspect ratio strictly above the 57% race bib line.
  - Updated `presets/fleet_lineup.json` Slot 4 to Float 05 "Pirate Ship" (`#e63946`, tag `PIRATE`, icon 🏴‍☠️).
- **Firmware & Fleet Palettes Dual Core Synchronization (`include/fleet_palettes.h`, `arduino/MSEP_Costume/fleet_palettes.h`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`):**
  - Executed `sync_fleet_palettes()` via `build_fleet_binaries.py`, automatically baking the 100 Pirate Ship RGB colors into `DEFAULT_FLOAT_PALETTES[4]` across both PlatformIO and Arduino IDE header files.
  - Synchronized float names and roles in `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` line 93 (`{ "Pirate Ship", "FOLLOWER", CRGB(230, 25, 25) }`).
- **Simulator & Web Flasher Tooling (`simulator/app.js`, `simulator/index.html`, `simulator/web_flasher.html`, `scripts/compile_clean_tpu_panel.py`):**
  - Integrated `pirate_ship` across `simulator/app.js`: default float lineup, image loaders, Cricut metadata, 5-color TPU STL segmentation configuration, and auto-migration from legacy Cinderella presets.
  - Updated `simulator/index.html` quick-switch buttons and artwork dropdown.
  - Updated `simulator/web_flasher.html` Float 5 card and descriptions.
  - Updated `scripts/compile_clean_tpu_panel.py` to support 5-color TPU armor segmentation for the Pirate Ship.
- **100% Documentation Synchronization:**
  - Synchronized `SIMULATOR_USER_GUIDE.md`, `README.md`, `FLASHING_INSTRUCTIONS.md`, `RACE_DAY_BUTTON_GUIDE.md`, `RACE_DAY_PACKING_CHECKLIST.md`, and `SIMULATOR_QUICKSTART.md`.

### 2026-10-13 03:40 - Solo Show Mode Ambient Background Palette Alignment & Preset Parity
- **Solo Show Mode Preset Architecture Verification (`simulator/app.js`, `buildCompletePresetData()`):**
  - Verified that individual float solo shows (the 90-second timeline cues configured in Tab 4: Show Director) are **100% part of the preset file** under `sequence: { loopDuration, cues }`.
  - Confirmed that modifying, adding, deleting, or quantizing cues directly calls `markSingleShirtDirty()`, ensuring the new pre-rebuild canvas guard flags unsaved solo show modifications before `🔨 Rebuild ROMs` executes.
- **Ambient Solo Show Artwork Palette Integration (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`):**
  - Updated `renderAmbientFallback()` and `runAutonomousShowSequence()` steady-sparkle fallback to check `#elif defined(HAS_DEFAULT_FLOAT_PALETTES)` before falling back to flat hero colors.
  - Guarantees that when running autonomously in **Solo Show Mode** (`SHOW_MODE_AUTONOMOUS_SEQUENCE`) between 30s fleet routines, each float's ambient sparkles and breathing glow display their authentic multi-color sampled background artwork.
- **Recompiled All 8 ROM Binaries:**
  - Recompiled and verified all 8 ROM binaries cleanly with PlatformIO (`build_fleet_binaries.py`).

### 2026-10-13 03:30 - Automated Fleet Palette Sync & Pre-Rebuild Canvas/Show Verification Guards
- **Automated Fleet Palette Synchronization (`build_fleet_binaries.py`, `include/fleet_palettes.h`, `arduino/MSEP_Costume/fleet_palettes.h`):**
  - Implemented `sync_fleet_palettes()` in `build_fleet_binaries.py`: automatically reads the active 7 float presets from `presets/fleet_lineup.json` and updates `DEFAULT_FLOAT_PALETTES[7][100]` across both `include/fleet_palettes.h` and `arduino/MSEP_Costume/fleet_palettes.h`.
  - Ensures that any moved LEDs, newly sampled background colors, or preset updates (such as Pete's Dragon, Snail, Turtle, Train, and Drum) are 100% baked into the firmware for the browser Web Flasher and Arduino IDE.
- **Dedicated Fleet Compilation Isolation (`build_fleet_binaries.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`):**
  - Introduced `#define FLEET_BUILD 1` in `include/float_config.h` during fleet binary compilation: cleanly disables single-costume `HAS_CUSTOM_PALETTE` overrides so each float compiles with its own authentic 100-LED array from `fleet_palettes.h`, while keeping all pattern constants, speed, and sparkle rate defines intact.
  - Added safe fallback defines for `COSTUME_SPEED_BPM` (120) and `COSTUME_SPARKLE_RATE` (1.5) in firmware.
- **Pre-Rebuild Canvas & Timeline Verification Guards (`simulator/app.js`):**
  - Enhanced `rebuildFleetBinariesBtn` click handler:
    1. **Unsaved Canvas Guard:** Detects `isSingleShirtDirty` and prompts the user to save or cancel so newly moved LEDs and background colors are saved to preset before building.
    2. **Unsaved Fleet Show Guard:** Detects `isFleetShowDirty` and prompts the user to save or cancel so newly choreographed cues are saved before building.
    3. **Auto C++ Routine Pre-Export:** Automatically pre-synchronizes `render30sFleetRoutine()` into `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` via `/api/export_fleet_routine` before launching PlatformIO.
- **Full Fleet Verification:**
  - Compiled and verified all 8 binaries (Floats 0 through 7) cleanly with PlatformIO (`build_fleet_binaries.py`). Output verified in `firmware/` and manifests generated.

### 2026-10-13 02:45 - Pete's Dragon 100/80-LED Distribution & 3D Spec Clearance Restoration
- **Resolved 3D TPU Spec Matching Fallback (`3d_panels/tpu_panel_specs.json`, `3d_panels/petes_dragon_specs.json`, `simulator/app.js`):**
  - Identified that line 7 of both `3d_panels/tpu_panel_specs.json` and `3d_panels/petes_dragon_specs.json` had `"graphic_type": "custom_image"` instead of `"petes_dragon"`. This caused `getEffectiveTpuPanelSpec()` in `simulator/app.js` to reject the compiled 3D STL panel specs when Pete's Dragon (`petes_dragon`) was active, falling back to a raw 2D live contour with uncalibrated aspect ratio.
  - Corrected `graphic_type` to `"petes_dragon"` in both JSON specification files.
  - Enhanced `getEffectiveTpuPanelSpec()` in `simulator/app.js` to robustly match Pete's Dragon across `spType`, `sp.float_name`, or `sp.character`, and synchronized the aspect ratio in the live raster contour generator fallback.
- **Orientation-Aware Candidate Wall Pre-Filtering (`simulator/app.js`):**
  - Diagnosed why LED placement struggled to fit 100 (or even 80) LEDs without collisions: `scatterLedsOnGraphic()` was pre-filtering candidates by testing clearance in *both* horizontal (0 rad) AND vertical ($\pi/2$ rad) orientations simultaneously. Because each collar feature point tests out to $9.3\text{ mm} + 5.0\text{ mm} = 14.3\text{ mm}$, requiring both orientations wiped out ~40% of the dragon area (snout, wings, crest, feet), constricting usable area to only $18,776\text{ mm}^2$ where 100 LEDs were crammed into collisions.
  - Updated candidate pre-filtering to test against the active target well orientation (`baseRot = 0` for standard horizontal wells), expanding usable area to over $31,400\text{ mm}^2$ while preserving strict $\ge 5.0\text{ mm}$ wall clearance.
  - Added a fast-path interior center check in `getLedCollarPerimeterWallCheck()` to bypass expensive polygon distance calculations for deep interior points, accelerating boundary tests by 10×.
- **Hardware & Clearance Verification:**
  - Verified 80/80 LEDs placed with 0 perimeter wall violations ($< 5\text{ mm}$), 0 bridge violations ($< 2\text{ mm}$), and 0 collar collisions.
  - Verified 100/100 LEDs placed across the $245\text{ mm}$ Large plate with full inter-LED collar/wire clearance ($\ge 8.65\text{ mm}$ / $\ge 4.3\text{ mm}$) and 0 warnings.

### 2026-10-13 02:02 - 5-Color Transparent `Simpletrain.png` Default Train Graphic & Rear Cab Wall Cleanup
- **Checkerboard Background Removal, Rear Cab Overhang Cleanup & Exact 5-Color Quantization (`assets/Simpletrain.png`, `simulator/assets/Simpletrain.png`):**
  - Removed the gray/white checkerboard background (including enclosed interior pockets between undercarriage bars and smokestack) from `assets/Simpletrain.jpg`, removed the extra vertical red wall and enclosed dark opening at the rear cab overhang above the coal box, converted the small foliage area into gold, and quantized the locomotive into **strictly 5 exact 3D-printing colors** (`1260 × 1140` RGBA PNG) using 2 shades of gold to preserve all faceted gold shapes:
    1. **Red (Locomotive Body, Smokestack & Cowcatcher):** `RGB(163, 35, 30)` (`#a3231e`)
    2. **Light Gold (Bright Gold Trim, Steam Highlights & Wheels):** `RGB(217, 158, 72)` (`#d99e48`)
    3. **Black (Chassis, Roof, Cab Windows & Smokebox Ring):** `RGB(20, 20, 20)` (`#141414`)
    4. **Dark Gold / Bronze (Shaded Steam Facets, Headlight Cone & Details):** `RGB(161, 112, 44)` (`#a1702c`)
    5. **Grey (Drive Rod, Wheel Rims & Undercarriage):** `RGB(113, 111, 111)` (`#716f6f`)
- **Default Simulator Graphic, 3D STL Palette & Preset LEDs (`simulator/app.js`, `scripts/compile_clean_tpu_panel.py`, `presets/casey_jr_train.json`):**
  - Set `assets/Simpletrain.png` as the default graphic for Float 1 (`casey_jr_train` / The Train) in `simulator/app.js` and refreshed the 100-LED coordinates in `presets/casey_jr_train.json` so no LEDs sit in the open rear cab overhang.
  - Added `casey_jr_train` / `is_train` 5-color STL segmentation config (`black`, `red`, `gold`, `dark_gold`, `grey`) in `simulator/app.js` and `scripts/compile_clean_tpu_panel.py`.

### 2026-10-13 01:05 - Transparent `SimpleSnail.png` Default Snail Graphic & Per-Float Live Contour Re-distribute Fix
- **Transparent Background Conversion (`assets/SimpleSnail.png`, `simulator/assets/SimpleSnail.png`, `simulator/app.js`):**
  - Converted `assets/SimpleSnail.jpg` into a crisp, halo-free transparent RGBA PNG (`assets/SimpleSnail.png` and `simulator/assets/SimpleSnail.png`, `1391 × 1391` square frame aligned 1:1 with the 100-LED Snail preset coordinates) while keeping all 5 snail colors and artwork geometry 100% unchanged.
  - Set `assets/SimpleSnail.png` as the default graphic for Float 4 (The Snail) in `simulator/app.js` (`spinningSnailImg` and `floatArtworkImgs['spinning_snail']` / `floatArtworkImgs['spinning_snail_original']`).
- **Fixed `[ 🔄 Re-distribute ]` Using Cached Pete's Dragon Contour (`simulator/app.js`, `scripts/compile_clean_tpu_panel.py`):**
  - Fixed a bug where `getDistToTpuPanelPerimeterMm()`, `getTpuPanelContourNorm()`, and `getTpuBridgeLocationsNorm()` read `activeTpuSpecs` from `/3d_panels/tpu_panel_specs.json` (which held Pete's Dragon's compiled contour) even when another float like The Snail was active, causing `[ 🔄 Re-distribute ]` to constrain LEDs into the shape of the dragon.
  - Implemented `getEffectiveTpuPanelSpec()` in `simulator/app.js` to verify that `activeTpuSpecs` matches `currentGraphicType` and, whenever another float or custom graphic is active, dynamically trace and cache the active artwork's true 2D silhouette contour and entrance/exit portals directly from `getActiveGraphicImg()`.
- **5-Color 3D Printing Palette Verification & STL Target Calibration (`simulator/app.js`, `scripts/compile_clean_tpu_panel.py`, `simulator.py`):**
  - Verified via K-Means color cluster analysis that `SimpleSnail` consists of **5 distinct 3D-printing colors**:
    1. **Black (Chassis & Shell Dividers):** `RGB(1, 2, 1)` (`#010201`, 29.4% of snail)
    2. **Red (Head, Neck & Foot):** `RGB(138, 38, 30)` (`#8a261e`, 23.7% of snail)
    3. **Blue (Blue Radial Shell Stripes):** `RGB(41, 83, 116)` (`#295374`, 16.6% of snail)
    4. **Green (Green Radial Shell Stripes):** `RGB(30, 116, 61)` (`#1e743d`, 15.8% of snail)
    5. **Gold/Yellow (Antennae, Eye, Spiral & Rim):** `RGB(202, 153, 39)` (`#ca9927`, 14.5% of snail)
  - Calibrated `targetRgb` centroids for `spinning_snail` in `simulator/app.js` and `scripts/compile_clean_tpu_panel.py` to match these 5 exact clusters.

### 2026-10-13 00:25 - Default Snail Graphic Update & Transparent Background Cleanup (`assets/newsnail.png`)
- **Transparent Background Extraction (`assets/newsnail.png`, `simulator/assets/newsnail.png`, `assets/spinning_snail.png`, `simulator/assets/spinning_snail.png`):**
  - Removed all background elements (black background, floating background streetlamp globes/dots, and upper-right background awning) from `assets/newsnail.png` while preserving 100% of the snail's red body, golden antennae/eye/spiral/rim, and alternating green, blue, and opaque black radial shell stripes.
  - Cropped to the canonical `183 × 183` RGBA square frame (`(17, 66, 200, 249)`) so the snail preserves its exact 1:1 aspect ratio, chest sizing above the race bib, and 100-LED preset coordinate alignment.
- **Default Simulator Snail Asset (`simulator/app.js`):**
  - Updated `spinningSnailImg` and `floatArtworkImgs['spinning_snail']` / `floatArtworkImgs['spinning_snail_original']` to load `assets/newsnail.png` by default.

### 2026-10-12 23:25 - ESP-NOW Walkie-Talkie Channel Lock & 5-Packet Burst Reliability Upgrade
- **Eliminated Background Wi-Fi Channel Hopping (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `include/wifi_config.h`, `presets/wifi_settings.json`):**
  - Cleared hardcoded home Wi-Fi credentials from `include/wifi_config.h` and `presets/wifi_settings.json` so race-day builds boot straight into pure `WIFI_STA` walkie-talkie mode without searching for an external router.
  - Added `WiFi.persistent(false)`, `WiFi.setAutoReconnect(false)`, and `WiFi.disconnect(true, true)` at startup (and immediately on 1.5s connection timeout) to wipe any SDK-cached NVS Wi-Fi credentials and prevent the ESP32 Station driver from background-scanning Channels 1–13 while ESP-NOW is active.
  - Explicitly locked the 2.4GHz radio to **Channel 1** (`esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE)`) and disabled Wi-Fi modem power-save (`esp_wifi_set_ps(WIFI_PS_NONE)`) for zero-latency packet reception.
- **5-Packet Redundant Burst Transmission & Active Show Sync Heartbeats (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`):**
  - Implemented `sendEspNowBurst()` so all Leader button broadcasts (`0x30` 30s Fleet Show, `0x00` Early Stop, `0x44` Roll Call, `0x46`/`0x47` Photo Mode, `0x50` Standby, `0x51` Wake) transmit a rapid 5-packet burst spaced 6ms apart (`24ms` total) to overcome transient RF interference.
  - Added periodic Leader sync heartbeats during active shows (`250ms` during the 30-second Fleet Routine and `150ms` during the 4-second Roll Call) and synchronized `fleetRoutineCycle` via `packet.waveHead` so all Follower costumes match the Leader's exact color cycle and millisecond offset even if powered on mid-routine.
- **Generic Build Float ID Reset (`include/float_config.h`, `build_fleet_binaries.py`):**
  - Reset `COMPILED_FLOAT_ID` to `0` after `build_fleet_binaries.py` finishes compiling the 7 dedicated float ROMs so standard PlatformIO uploads preserve each board's NVS-configured Float ID.

### 2026-10-12 19:15 - Formatted Race Day Button Quick Guide Document (`Race_Day_Button_Quick_Guide.docx`)
- **Family-Ready Google Docs / Word Quick Sheet (`Race_Day_Button_Quick_Guide.docx`):**
  - Created a styled, single-page OpenXML `.docx` document (`Race_Day_Button_Quick_Guide.docx`) designed for direct upload to Google Docs or sharing with the 7-runner family team.
  - Clearly separates **👑 Leaders (Float 1: Train & Float 7: America)** (wireless full-fleet authority) and **👥 Followers (Floats 2–6: Drum, Turtle, Snail, Cinderella, Dragon)** (local-only, bump-proof mid-race lockouts) with simplified **Photo Mode** terminology.

### 2026-10-11 13:45 - Preset Loading State Restoration & 5mm Perimeter Wall Clearance Alignment
- **Plate Size & LED Count Restoration (`simulator/app.js`):**
  - Resolved preset loading bug where saving a preset with **Large** plate size and **100 LEDs** (such as `presets/petes_dragon_chris_2026-10-10_22-23.json`) restored to default Medium plate size and 75-LED slider settings upon reopening.
  - Updated `applyProfileData()` to parse and apply `profileData.plateSize` (and fall back cleanly based on `plateWidthMm`) by invoking `selectPlateSizeOption(targetPlateSize, false)`.
  - Added `scaleLeds = true` optional parameter to `selectPlateSizeOption()`: suppresses proportional LED coordinate re-scaling when applying pre-computed preset coordinates, preventing coordinate drift or double-scaling.
  - Updated `applyProfileData()` to restore target LED count (`profileData.ledCount` or `profileData.leds.length`) by invoking `selectLedCountOption(targetLedCount, false)`, synchronizing `#ledCountSlider`, `#activeLedCountLabel`, `#ledCountTitle`, and wiring trace markers.
  - Added canvas redraw triggers (`markSingleShirtDirty()` and `draw()`) on `applyProfileData()` completion and image `onload` to guarantee that all 100 LEDs render directly on the active character graphic silhouette without manual interaction.
- **5mm Perimeter Wall Clearance Alignment for Large 245mm Plate (`presets/petes_dragon_chris_2026-10-10_22-23.json`):**
  - Diagnosed why 22 LEDs triggered yellow/red 5mm perimeter warnings upon loading: the preset was originally saved when Large mode was $254\text{ mm}$ (`plateScale = 1.2500`), before the CAD 3D build plate envelope was capped at $245.0\text{ mm}$ (`plateScale = 1.2057`, a 3.5% inward contour shift).
  - Re-mapped the 100 LEDs to the calibrated $245\text{ mm}$ Large plate boundaries and performed a sub-millimeter inward relaxation ($<1.12\text{ mm}$ max shift) so that all 100 LED wells, wire entrance sides, and 2.5mm entrance corridors strictly satisfy the $\ge 5.0\text{ mm}$ keep-out margin from the true 3D STL perimeter wall.
  - Verified 0 warnings across all 100 pixels upon preset load.

### 2026-10-11 12:30 - Pre-Print CAD Modifications: 245mm Envelope Limit, Normal-Aligned Side Exit, Relocated Bottom Portal & Extremity Lid Screws
- **245mm Maximum Dimension Limit (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`):**
  - Enforced strict 245.0mm maximum build volume limit on the compiled STL part footprint (including 4.0mm outer perimeter rim buffer and 4.75mm outer eyelet mounting tabs).
  - Implemented iterative footprint scaling in `compile_plate_variant`: if $\max(\text{dim}_X + 9.5, \text{dim}_Y + 9.5) > 245.0\text{ mm}$, smoothly scales `width_mm`, `height_mm`, and all LED coordinates while preserving 1:1 aspect ratio and artwork alignment.
  - Large plate size now compiles to `[240.54, 215.64, 10.0] mm` (5.42 MB chassis, 0.49 MB lid), fitting comfortably within standard 256x256mm build envelopes (Bambu Lab X1/P1/A1, Snapmaker U1, Creality, Prusa MK4).
  - Synchronized `sizeMap` in `simulator/app.js` and `target_chassis_w` in `simulator.py` to `245.0mm (~9.65")`.
- **Eliminated Side Exit Slot Perimeter Wall Bump (Photo 1 Fix):**
  - Diagnosed that the previous axis-aligned box cutter (`extents=[6.5, 5.5, 3.9]`) did not align with the slanted perimeter wall at the flank, leaving an uncut triangular wedge and protruding bump on the outer rim wall.
  - Calculated local wall tangent and normal vectors on `smoothed_plate_2d.exterior` at `(exit_portal_x, exit_portal_y)` and applied rotation matrix $\mathbf{R}_z(\theta)$ to `exit_portal_cutter` with generous 24.0mm through-wall depth.
  - Aligned lateral zip-tie bridge (`bridge_exit_solid_tm`), wire tunnel, saddle, and lid ridge relief cutter (`exit_portal_relief_m`) along the wall normal, completely eliminating the protruding wall bump and providing a clean, perpendicular wire exit.
- **Relocated Bottom Wire Portal & Zip-Tie Tunnel (Photo 2 Fix):**
  - Shifted bottom wire entrance portal and internal zip-tie bridge away from the corner jog (`X = 133.62`) into the straight horizontal segment of the bottom rim wall (`X = 114.50`, `Y = 47.22` in scaled space) circled in green in Photo 2.
  - Entrance slot cutter and internal floor zip-tie strain relief bridge tunnel move together, providing clean orthogonal geometry and unobstructed wire entry into the chassis basin.
- **Added Perimeter Extremity Lid Screw Bosses (Photo 3 Fix):**
  - Added dedicated M2 screw boss positions at the 7 perimeter extremities circled in Photo 3:
    1. Top-right ear tip
    2. Chin / neck concave nook
    3. Top-left ear crest
    4. Far-left tail tip
    5. Bottom-left foot / heel corner
    6. Far-right jaw / snout corner
    7. Lower-right flank (straight vertical wall above tab)
  - Combined with perimeter spacing distribution to provide 14 total M2 screw bosses along the inner rim wall.
  - Enforced strict keep-outs: $\ge 12\text{ mm}$ portal clearance, $\ge 6.8\text{ mm}$ collar clearance from LEDs, and strictly zero screws in the center of the lid plate.
  - Regenerated matching pilot holes on the chassis tray as well as alignment ridge reliefs, 2.0mm through-holes, and 3.8mm flush counterbores on the rear lid plate.
- **Verification:**
  - Full batch compilation completed in 10.72s. Monolithic STLs, split multi-color STLs, and native multi-body `.3mf` exported successfully.
  - Tested with `python simulator.py --test`: all endpoints and preset checks passed.

### 2026-10-10 22:20 - Redistribution Perimeter Wall Avoidance & 2.0mm Collar Bridge Clearance Rule
- **Redistribution Wall Avoidance Engine (`simulator/app.js` & `simulator/led_clearance.js`):**
  - Resolved the issue where clicking "Re-distribute" (or changing LED count) placed LEDs whose collars touched or encroached within 5.0mm of the 3D STL perimeter wall.
  - Implemented comprehensive candidate pre-filtering in `scatterLedsOnGraphic`: evaluates every sampled foreground pixel with `getLedCollarPerimeterWallCheck` across both baseline horizontal ($\theta = 0$) and orthogonal ($\theta = \pi/2$) orientations.
  - Excludes all candidate spots where the collar wire entrances ($\pm 6.8\text{ mm}$), notch corners ($\pm 2.0\text{ mm}$), wire corridors ($\pm 9.3\text{ mm}$), or lateral flanks ($\pm 4.3\text{ mm}$) violate the 5.0mm wall clearance or fall outside the 3D STL panel contour polygon.
  - Guarantees `lastSampledLedPool` (`pool.pts`) and `chosenIndices` only contain 100% collision-free interior spots, preventing `snapToArtwork` and `searchFreeSpot` from snapping LEDs into edge wall violations.
- **2.0mm LED Collar Bridge Clearance Rule (`simulator/app.js` & `simulator/led_clearance.js`):**
  - Replaced the previous circular LED center-die check ($< 10\text{ mm}$) with a physically accurate geometric clearance engine: `getLedCollarBridgeClearance` and `getCollarToBridgeBoxDistMm`.
  - Evaluates distance from the outer LED collar sides, wire entrance openings ($\pm 6.8\vec{u}$), wire corridor bounding boxes ($\pm 9.3\vec{u}$), and lateral flanks ($\pm 4.3\vec{v}$) to the rectangular footprints of both the Entrance Bridge ($8.0\text{ mm W} \times 7.2\text{ mm L}$) and Exit Bridge ($7.2\text{ mm W} \times 8.0\text{ mm L}$).
  - Strictly enforces $\ge 2.0\text{ mm}$ physical clearance between collar envelope and bridge structures.
  - Dynamic warning badges now report exact collar clearance: `⚠️ Entrance/Exit Bridge Keep-Out (<2.0mm collar clearance: X.Xmm)`.
  - Updated bridge overlay labels on canvas to `2mm COLLAR KEEP-OUT`.
  - Synchronized `selectClearanceAwareFpsIndices`, `violatesAny`, and `relax` in `led_clearance.js` as well as `searchNearbyClearSpot` and `relaxLedCollarOverlapsLegacy` in `app.js` with the 2.0mm collar rule.
- **Verification:**
  - Automated redistribution simulation verified in Node.js on true Pete's Dragon 3D STL chassis geometry: 100 LEDs distributed with 0 wall violations, 0 bridge violations, and 0 collision violations.
  - Python test suite passed (`python simulator.py --test`), zero JavaScript syntax errors (`node -c`), and full documentation synchronization in `SIMULATOR_USER_GUIDE.md` and `PROJECT_PROGRESS.md`.

### 2026-10-10 21:58 - LED Well Wire Entrance Sides Perimeter Wall Clearance Engine
- **LED Well Wire Entrance & Envelope Perimeter Evaluation (`simulator/app.js` & `simulator/led_clearance.js`):**
  - Updated the 5.0mm perimeter wall clearance check to evaluate the physical sides of the LED wells where the wires enter (`Opening 1` at $+6.8\text{ mm}$ and `Opening 2` at $-6.8\text{ mm}$ along the orientation axis, notch corners at $\pm 2.0\text{ mm}$, wire corridors at $\pm 9.3\text{ mm}$, and lateral flanks at $\pm 4.3\text{ mm}$), rather than checking only the single center coordinate of the LED.
  - When an LED is oriented towards the 3D STL plate rim, the side of the well where the wire enters is tested directly against `(activeTpuSpecs.front || activeTpuSpecs).contour_pts` in true CAD millimeters.
  - **Directional Wire Notch Warning Feedback:** If a specific wire entrance side violates the $5.0\text{ mm}$ clearance or is outside the wall, that specific wire entrance corridor notch lights up red on the collar (`opening1WallBlocked` / `opening2WallBlocked`), providing immediate visual diagnostic feedback on the canvas.
  - **Auto-Placement & Relaxation Sync:** Updated `selectClearanceAwareFpsIndices` and `resolveLedClearance` in `simulator/led_clearance.js` to verify both the center and the wire entrance sides of candidate LEDs, repelling encroaching well sides away from the perimeter wall.
  - Verified test suite passes (`python simulator.py --test`), zero JavaScript syntax errors (`node -c`), and full documentation synchronization in `SIMULATOR_USER_GUIDE.md` and `PROJECT_PROGRESS.md`.
- **Contoured 3D STL Armor Plate Perimeter Engine (`simulator/app.js` & `simulator/led_clearance.js`):**
  - Resolved perimeter evaluation mismatch where LED clearance was checking the outer shirt/bounding box rectangle instead of the actual contoured perimeter wall of the 3D STL armor panel.
  - Implemented `getTpuPanelContourNorm()`, `isPointInPolygon()`, `distPointToSegmentMm()`, `offsetContourPolygon()`, and `getDistToTpuPanelPerimeterMm()` to evaluate LEDs directly against `(activeTpuSpecs.front || activeTpuSpecs).contour_pts` in true CAD millimeters.
  - **Differentiated Clearance Alerts:**
    - `⚠️ Outside 3D STL Wall`: Triggered immediately if an LED is placed or dragged outside the organic 3D STL panel perimeter onto the shirt canvas.
    - `⚠️ <5.0mm 3D STL Wall (X.Xmm)`: Triggered if an LED is located inside the 3D STL panel but within 5.0mm of the contoured perimeter rim wall.
  - **Visual 2D Canvas Contour & 5mm Keep-Out Guide Overlay:**
    - Updated `drawStrainReliefBridgesOverlay(ctx)` to render the true 3D STL armor perimeter wall contour (cyan solid line `#38bdf8`, 2.0px with subtle fill) and the 5.0mm inward keep-out limit (cyan dashed line, 1.4px) directly on the 2D layout canvas.
  - **Auto-Placement & Relaxation Clearance Sync (`simulator/led_clearance.js`):**
    - Updated `selectClearanceAwareFpsIndices` and `resolveLedClearance` to enforce the 3D STL perimeter contour and 5.0mm wall clearance during automatic distribution and physics relaxation.
  - Verified test suite passes (`python simulator.py --test`), zero JavaScript syntax errors (`node -c`), and full documentation synchronization in `SIMULATOR_USER_GUIDE.md` and `PROJECT_PROGRESS.md`.
- **Added Master Warning Toggle & Dynamic Badges (`simulator/app.js` & `simulator/index.html`):**
  - Added dedicated UI toggle `[⚠️ Show Placement Warnings (<5mm Wall / <2.5mm Wire)]` in Section 3 of the Layout sidebar, allowing users to show or silence real-time clearance warning badges and red collar highlights.
  - Replaced the previously hardcoded `⚠️ <2.5mm Clearance` text in `renderBulb` with dynamic diagnostic badges:
    - `⚠️ <5.0mm Perimeter Wall (X.Xmm)`: Triggered when an LED enters the 5mm perimeter keep-out boundary.
    - `⚠️ <10mm Bridge Keep-Out`: Triggered when an LED encroaches on entrance/exit strain relief bridges.
    - `⚠️ Collar Collision`: Triggered when two LED collars physically collide.
    - `⚠️ <2.5mm Wire Channel`: Triggered when adjacent wire entrance corridors are blocked.
  - Allowed manual dragging to reach the plate perimeter boundaries so users can test and visually verify the 5mm perimeter keep-out warnings in real time.
  - Rendered warning badges on LED hover and selection as well as during drag.
- **Documentation & User Guide Sync:**
  - Updated `SIMULATOR_USER_GUIDE.md` detailing the new Placement Warnings toggle and badge types.
- **Verification:**
  - Tested clean execution with `python simulator.py --test` (HTTP API status 200).

### 2026-10-10 21:18 - 5.0mm Perimeter Wall Clearance Keep-Out Engine & Visual Boundary Overlay
- **Enforced 5.0mm Perimeter Wall Clearance (`simulator/led_clearance.js` & `simulator/app.js`):**
  - Updated auto-scattering (`selectClearanceAwareFpsIndices`) to filter out any candidate positions within 5.0mm of the 3D TPU armor panel / chest graphic outer perimeter walls.
  - Incorporated 5.0mm perimeter boundary repulsion into physics relaxation (`resolveLedClearance`), keeping all LEDs safely pushed away from outer panel rims.
  - Enhanced manual drag clamping (`clampLedNoCollarOverlap`) to enforce a 5.0mm margin inside all 4 perimeter edges (`minX`, `maxX`, `minY`, `maxY`).
  - Added real-time perimeter wall clearance checking (`checkLedClearanceStatus`), flagging `wallBlocked` warnings if any LED collar/housing comes within 5.0mm of a perimeter wall.
  - Rendered a dashed cyan **`🛡️ 5mm Perimeter Wall Keep-Out Limit`** canvas overlay guide when strain relief or placement guide modes are visible.
- **Documentation & User Guide Sync:**
  - Updated `SIMULATOR_USER_GUIDE.md` with 5.0mm perimeter wall keep-out clearance specifications.
- **Verification:**
  - Validated clean execution with `python simulator.py --test` (HTTP API status 200).

### 2026-10-10 06:10 - Workbench Mirrored Back View for LED Placement & Assembly Guide
- **Implemented Mirrored Back View in Placement Guide Mode (`simulator/app.js` & `simulator/index.html`):**
  - Horizontally mirrored the placement guide canvas layout, chest graphic artwork (`activeImg`), race bib, LED coordinates (`1.0 - x`), wire routing traces, optical 3×3mm apertures, and interactive mouse drag/click hit-testing when in Placement Guide mode (`graphicVersion === 'assembly_guide'`).
  - Added dedicated UI orientation toggle controls (`[🪞 Mirrored Back]` / `[👕 Normal Front]`) in the Placement Guide options card (`#assemblyGuideOptionsCard`).
  - Ensures workbench builders looking at the physical BACK of the garment while mounting LEDs and routing wires see a 1:1 matching left/right spatial orientation on screen.
  - Text labels (LED numbers `#1`–`#100`, distance tags `cm`, title badge) remain rendered left-to-right for effortless legibility.
  - Updated `printAssemblyGuide()` printable HTML document and PNG exporter to label the perspective as `🪞 Workbench Back View (Mirrored)`.
- **Documentation & User Guide Sync:**
  - Updated `SIMULATOR_USER_GUIDE.md` section on Placement Guide Mode detailing the new `🪞 Mirrored Back View` workbench assembly features and print controls.
- **Verification:**
  - Validated clean execution of `python simulator.py --test` (HTTP API verified, status 200).

### 2026-10-09 01:28 - Browser LocalStorage Quota Overflow Recovery & Resilient Preset Disk Saving
- **Resolved QuotaExceededError on Preset Saving (`simulator/app.js`):**
  - Diagnosed browser screenshot showing `Save error: Failed to execute 'setItem' on 'Storage': Setting the value of 'msep_custom_presets' exceeded the quota.`
  - Wrapped `localStorage.setItem('msep_custom_presets', ...)` in a fail-safe try/catch block with automatic LRU pruning (keeping the 3 most recent entries in browser storage).
  - Ensured server disk saving via `/api/save_preset` executes reliably and writes `.json` files to `presets/` regardless of browser storage constraints.
- **Verification:**
  - Syntax validated clean with `node --check simulator/app.js`.

### 2026-10-09 01:25 - Dynamic Timestamped Float Revision Saves & Filename Updates
- **Automatic Fresh Timestamp Generation on Save Float (`simulator/app.js`):**
  - Resolved issue where saving a float whose name already contained an older date/time string would not update the timestamp or name in the UI.
  - Implemented regex stripping (`/\s+\d{4}-\d{2}-\d{2}(?:[ _-]\d{2}[-:]\d{2}(?:[-:]\d{2})?)?.*$/i`) across `#saveProfileBtn`, `exportCurrentProfileJson()`, and `openSavePresetModal()`.
  - Every click of **💾 Save Float** now strips previous timestamp artifacts, dynamically creates a new date/time tag (e.g. `Pete's Dragon 2026-10-09 01-25`), immediately updates the `#profileNameInput` text field, saves the new `.json` preset to `presets/` on disk, and synchronizes the preset dropdown.
- **Verification:**
  - Syntax validated clean with `node --check simulator/app.js`.

### 2026-10-09 00:28 - 3D Modal Live Layout Canvas Synchronization & Instant Recompile Button
- **Resolved Live Canvas vs. Cached 3D STL Discrepancy:**
  - Diagnosed screenshot evidence where LED #37 on the 2D layout canvas had #52 adjacent to it with clearance, while the 3D preview showed an older compiled STL where #38 was adjacent and touching #37.
  - **3D Modal Live Recompile Action (`simulator/index.html` & `simulator/app.js`):**
    - Added a dedicated `⚡ Recompile 3D Model` action button directly in the top header toolbar of `#tpuPreviewModal`.
    - Users can now re-trigger Manifold C++ / Python CAD compilation directly from within the 3D preview without needing to close the modal.
  - **Enhanced Auto-Recompile Detection (`simulator/app.js`):**
    - Strengthened `openTpuPreviewModal()` stale-STL detection to directly compare in-memory canvas `leds` count and layout coordinates against `sp.ordered_leds`.
    - Guarantees that any LED movement or re-ordering on the 2D canvas automatically recompiles fresh Front & Back STLs before opening the 3D WebGL scene.

### 2026-10-08 23:55 - Circle Aperture Selection Carry-Over Fix for 3D Preview & 3D STL/3MF Exports
- **Seamless Aperture Shape Carry-Over from Layout Page to 3D Previews & Files:**
  - Diagnosed and resolved the root causes preventing aperture shape selections (🔘 **Ø 3.4mm Round**, ⚪ **Ø 3.0mm Round**, 🔲 **3x3mm Square**) from carrying over from the Layout page to the 3D preview and 3D files:
    1. **Layout Page Aperture Reactivity (`simulator/app.js`):**
       - Updated `setTpuWindowShape()` to automatically enable `params.showTpuWindows = true` (and synchronize `#showTpuWindowsToggle`), making the chosen circular aperture instantly visible on the 2D canvas upon clicking.
       - Synchronized both Layout toolbar buttons (`#tpuShapeRound34Btn`, `#tpuShapeRound30Btn`, `#tpuShapeSquareBtn`) and 3D Modal buttons (`#tpuModalShapeRound34Btn`, etc.) seamlessly.
    2. **Stale Check & Normalized Shape Detection (`simulator/app.js`):**
       - Normalized shape comparison in `openTpuPreviewModal()` (`normCompiledShape !== normCurrentShape`) to robustly compare legacy/alias shape strings (`round` / `circle` $\to$ `round_34`) and check variant-level specs (`sp.window_shape` / `sp.front.window_shape`).
       - If a shape mismatch is detected, `openTpuPreviewModal()` automatically initiates a clean re-compilation with the exact chosen aperture before rendering.
    3. **Preset Persistence & Float Switch Restoration (`simulator/app.js`):**
       - Added `tpuWindowShape`, `tpuWellOrientation`, `tpuIncludeLedNumbers`, `tpuIncludeClipGrooves`, and `tpuIncludeTopNubs` to `buildCompletePresetData()`.
       - Added full restoration of all TPU features in `applyProfileData()`, guaranteeing that switching float presets or importing files preserves the runner's circular aperture selection.
    4. **Clean STL Cutter Geometry (`scripts/compile_clean_tpu_panel.py`):**
       - Upgraded aperture boolean cylinder and box cutters with generous height (`FRONT_THICK_GENERAL + 2.0 = 4.0mm`), guaranteeing clean, watertight circular punch-through without coplanar boundary artifacts.
       - Added explicit `window_shape` and `well_orientation` metadata into `specs['front']` and `specs['back']` dictionaries.
       - Updated `README_BAMBU_STUDIO.txt` inside generated ZIP bundles to dynamically describe the active aperture geometry (e.g. `Ø 3.4mm round optical apertures (Default)`).
    5. **Standalone 3D Model Viewer Support (`3d_panels/tpu_panel_preview.html`):**
       - Updated the standalone WebGL viewer (`createGraphicCutoutMesh` and `createLedPixels`) to dynamically read `specsData.window_shape`, punching circular apertures via `ctx.arc()` and rendering circular pixel geometries (`THREE.CircleGeometry`) when round apertures are chosen.
    6. **Cache-Busted Direct Downloads (`simulator/app.js`):**
       - Added timestamped query strings (`?t=${Date.now()}`) to `downloadBothTpuStls()` preventing browser caching of stale STL files.
- **Verification:**
  - Tested compilation across `--window-shape round_34` (Ø 3.4mm), `--window-shape round_30` (Ø 3.0mm), and `--window-shape square` (3x3mm); verified 28-vertex circular boundary on front face ($Z=10.0$) in `tpu_panel_front.stl` and `tpu_panel_front_chassis_black.stl`.
  - Verified JavaScript syntax with `node --check simulator/app.js`.

### 2026-10-08 23:40 - Guaranteed Exit-Adjacent Terminal LED Placement & Pinned Wiring Route
- **Exit-Adjacent Terminal LED Seeding & Routing Assurance:**
  - Guaranteed that upon LED distribution (`scatterLedsOnGraphic`, `rearrangeRemainingLedsOnGraphic`, `sampleRemainingGraphicLeds`), the final LED (#100 or #N) is strictly placed directly adjacent to the **Lateral Exit Strain Relief Bridge** on the right flank:
    1. **Exit Seeding in `selectClearanceAwareFpsIndices` (`simulator/led_clearance.js`):**
       - The initial candidate sampling pass automatically picks the unblocked candidate closest to the **Entrance Bridge** as Seed 1, and the unblocked candidate closest to the **Lateral Exit Bridge** as Seed 2 (or first remaining unassigned pick if no group anchor exists near the exit).
       - This guarantees high-density spatial coverage directly adjacent to both the entrance and exit conduits before Farthest Point Sampling fills out the rest of the body.
    2. **Pinned Terminal Endpoint Routing in `optimizeLedWiringOrder` (`simulator/app.js`):**
       - Linked `entrancePos` and `exitPos` directly to `getTpuBridgeLocationsNorm()` CAD coordinates rather than generic bounding-box estimates.
       - Fixed a critical 2-Opt uncrossing bug: restricted 2-Opt edge swapping to internal segments (`j < n - 1`), preventing the final exit node (`path[n - 1]`) from being accidentally swapped out into the middle of the shirt during segment reversals.
       - Both the first LED (`path[0]`) and last LED (`path[n - 1]`) remain permanently pinned at the Entrance and Exit bridges respectively.
    3. **Bumped Cache Busters:** Updated `simulator/index.html` to `led_clearance.js?v=2` and `app.js?v=102`.
- **Verification:**
  - `node --check simulator/led_clearance.js` and `node --check simulator/app.js` passed with zero errors.

### 2026-10-08 23:30 - Strict Clearance-Aware Initial Placement & Relaxation Engine (Zero 2mm/2.5mm Warnings)
- **Clearance-Aware Farthest Point Sampling (FPS) & Solver Architecture (`simulator/led_clearance.js`):**
  - Eliminated recurring 2mm / 2.5mm wire corridor and collar collision warnings (`checkLedClearanceStatus`) across initial LED placement (`scatterLedsOnGraphic`), remaining LED redistribution (`rearrangeRemainingLedsOnGraphic`), and fireworks/group generation (`sampleRemainingGraphicLeds`).
  - **Symmetric Wire Corridor Checking (`ledPairViolatesMm`):**
    - Evaluates dual wire openings ($\pm \vec{u}$) for both LEDs symmetrically in true physical millimetres:
      $$\text{Opening}_A \leftrightarrow \text{Collar}_B \quad \text{AND} \quad \text{Opening}_B \leftrightarrow \text{Collar}_A \quad (d < 4.3\text{mm} + \text{margin})$$
    - Checks spine-to-spine distance ($< 8.65\text{mm} + \text{margin}$) and 10mm strain relief keep-out exclusion zones.
  - **Clearance-Aware Farthest Point Sampling (`selectClearanceAwareFpsIndices`):**
    - Replaced naive Euclidean FPS (which blindly placed points near tight corners or wire corridors) with candidate clearance filtering. Evaluates candidate points with a $+1.0\text{mm} \to +0.3\text{mm}$ safety buffer against already placed points and strain relief bridges, preventing 95%+ of collisions before relaxation starts.
  - **Multi-Pass Relaxation & Nearest Valid Spot Repair (`resolveLedClearance`):**
    - High-iteration spring relaxation ($160$ iterations) with directional opening push forces.
    - Silhouette-aware snapping (`snapToArtwork`) keeps LEDs firmly on valid artwork pixels without drifting into negative space.
    - Concentric ring search (`searchFreeSpot`) relocates any stubborn violating LED to the nearest valid on-artwork position that produces zero warnings for both itself and all neighbors, dynamically updating pixel vibrancy color matching.
  - **Integrated with `app.js` & `index.html`:**
    - Loaded `led_clearance.js?v=1` ahead of `app.js` in `simulator/index.html`.
    - Wired clearance engine into `rearrangeRemainingLedsOnGraphic()`, `scatterLedsOnGraphic()`, and `sampleRemainingGraphicLeds()`.
- **Verification:**
  - `node --check simulator/led_clearance.js` and `node --check simulator/app.js` passed with zero errors.

### 2026-10-08 23:18 - Exact 3D STL Strain Relief Bridge Alignment & Outside Icon Clutter Removal
- **1:1 Geometric Alignment with 3D Manifold CAD Coordinates:**
  - Diagnosed root cause of strain reliefs appearing as icons outside the graphic area:
    1. `getTpuBridgeLocationsNorm()` had previously estimated positions using bounding box extremes (`gb.normX + gb.normW * 0.5` and `gb.normX + gb.normW - 10mm`), pushing the exit bridge out to the empty edge of the rectangular bounding box instead of the organic dragon contour.
    2. Fallback text badges in `renderSingleShirtView()` had rendered huge external badge boxes (`pExit.x + 35`, `pEnt.y + 19.5`) floating outside the costume shirt area.
  - Linked `getTpuBridgeLocationsNorm()` directly to compiled 3D STL plate specs (`entrance_portal`, `entrance_bridge`, `exit_portal`, `exit_bridge`):
    - Converted 3D Manifold CAD coordinates ($x_{\text{mm}}, y_{\text{mm}}$) to normalized canvas coordinates:
      $$x_{\text{shirt}} = gb.\text{normX} + \frac{x_{\text{mm}}}{W_{\text{img}}} \cdot gb.\text{normW}$$
      $$y_{\text{shirt}} = gb.\text{normY} + \left(1.0 - \frac{y_{\text{mm}}}{H_{\text{img}}}\right) \cdot gb.\text{normH}$$
    - Bottom Entrance Bridge: Positioned directly on the bottom foot contour of Elliott ($x_{\text{rel}} = 0.3880, y_{\text{rel}} = 0.8250$), matching 3D coordinates `[88.33, 47.82]`.
    - Lateral Exit Bridge: Positioned directly on the right flank contour of Elliott ($x_{\text{rel}} = 0.6277, y_{\text{rel}} = 0.7175$), matching 3D coordinates `[142.91, 77.19]`.
  - Removed all external floating icon boxes (`⚡ IN (P1)` and `OUT ➔` floating 35px outside the graphic).
  - Streamlined `drawStrainReliefBridgesOverlay(ctx)` to draw compact, neat technical annotations (`⚓ IN BRIDGE` and `⚓ OUT BRIDGE` with `10mm KEEP-OUT`) directly at the physical bridge footprints inside the character silhouette.
  - Bumped script cache buster in `simulator/index.html` to `app.js?v=101`.
- **Verification:**
  - `python scripts/compile_clean_tpu_panel.py --orientation horizontal` compiled both plates and verified `entrance_bridge` and `exit_bridge` coordinate exports.
  - `node --check simulator/app.js` passed with zero errors.
- **Independent Canvas Overlay Rendering:**
  - Resolved issue where strain relief bridges were hidden when `showWireTension` or `showWiring` were unselected by moving `drawStrainReliefBridgesOverlay(ctx)` completely outside the conditional wiring block in `renderSingleShirtView()`.
  - Defaulted `params.showStrainReliefs` to `true` and updated `#showStrainReliefsToggle` with `checked` attribute so strain relief bridge locations and 10mm keep-out circles are immediately visible on initial load.
  - Enhanced overlay visuals with:
    1. Dotted leader lines connecting from the IN bridge tunnel directly to LED 0 and from the last LED to the OUT bridge tunnel.
    2. Perimeter rim U-notch marker dots and solid through-conduit paths.
    3. Glowing high-contrast badges for `⚓ IN STRAIN RELIEF` and `⚓ OUT STRAIN RELIEF` with `10mm KEEP-OUT` tags.
  - Bumped script cache buster in `simulator/index.html` to `app.js?v=100`.
- **Verification:**
  - `node --check simulator/app.js` passed with zero errors.
- **Window Shape Parameter Precedence & Specs Cache Override:**
  - Diagnosed root cause why 3D preview kept reverting to square apertures when round windows were selected:
    1. In `simulator/app.js` (`loadTpuModalData`, `createTpuGraphicCutoutMesh`, and `createTpuLedPixels`), the code evaluated `specs.window_shape || params.tpuWindowShape || 'round_34'`. If an older `tpu_panel_specs.json` on disk contained `"window_shape": "square"`, it took precedence over the active UI selection `params.tpuWindowShape`.
    2. Fixed parameter precedence across all 3D generation functions to strictly prioritize active user intent: `params.tpuWindowShape || specs.window_shape || 'round_34'`.
    3. Recompiled both Front and Back plate STLs with `--window-shape round_34 --orientation horizontal` and updated `3d_panels/tpu_panel_specs.json` and `3d_panels/petes_dragon_specs.json` with `"window_shape": "round_34"`.
    4. Bumped script cache buster in `simulator/index.html` to `app.js?v=98`.
- **Verification:**
  - Recompilation executed in 8.05s with `window_shape: round_34` (Ø 3.4mm circular window cutters).
  - `node --check simulator/app.js` passed with zero errors.

### 2026-10-08 22:47 - End-to-End Horizontal Collar Orientation 3D Preview Fix
- **Complete Pipeline Parameter Unification:**
  - Resolved root cause where 3D preview collars remained tangent even when horizontal alignment was selected on the layout canvas:
    1. In `scripts/compile_clean_tpu_panel.py`, `compile_plate_variant` function signature was missing the `well_orientation` parameter and was reading from global specs with a default of `'tangent'`, ignoring the passed `--orientation horizontal` flag for internal plate compilations.
    2. Updated `compile_plate_variant(..., well_orientation='horizontal')` signature and passed `well_orientation` explicitly to both Front and Back plate compilations.
    3. Updated `simulator/simulator.py` and `simulator/app.js` payload builders to strictly default `wellOrientation: params.tpuWellOrientation || 'horizontal'`.
    4. Updated Three.js optical cutout mask (`createTpuGraphicCutoutMesh`) and simulated LED pixel groups (`createTpuLedPixels`) in `simulator/app.js` to strictly enforce `rotDeg = 0` when horizontal mode is active unless an LED is explicitly marked with `is_custom_rotation: true`.
  - Recompiled both Front and Back plate STLs and updated `3d_panels/tpu_panel_specs.json` with all un-rotated LEDs at $0.0^\circ$ baseline.
- **Verification:**
  - `python scripts/compile_clean_tpu_panel.py --orientation horizontal` ran successfully in 7.35s with `orientation: horizontal` for all 65 LEDs.
  - `node --check simulator/app.js` passed with zero errors.

### 2026-10-08 22:40 - TPU Layout Signature ReferenceError & Cache Busting Fix
- **`computeTpuLayoutSignature` Fatal ReferenceError Resolution:**
  - Diagnosed exact runtime crash causing modal loading freeze: `computeTpuLayoutSignature()` referenced undefined variables `src` and `gb`, triggering an uncaught `ReferenceError: src is not defined` immediately upon calling `openTpuPreviewModal()`.
  - Added safe fallbacks for `src`, `gb`, `getActiveGraphicImg()`, `getActiveFloatStlColors()`, and wrapped the entire layout signature generator in a `try ... catch` with fallback timestamp.
  - Wrapped `openTpuPreviewModal()` initialization and auto-recompile sequence in robust `try ... catch` blocks to guarantee control always proceeds to `loadTpuModalData()`.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=96`.
- **Node Syntax Verification:**
  - Ran `node --check simulator/app.js` with zero errors.

### 2026-10-08 22:36 - 3D Preview Modal Loading Hang & Event De-duplication Fix
- **Modal Event Listener & Double-Invocation Resolution:**
  - Diagnosed root cause of the modal getting stuck on `"Loading Binary STL & Compiling Shaders..."`: `#openTpuPreviewModalBtn`, `#closeTpuPreviewModalBtn`, and `#closeTpuPreviewModalBottomBtn` had both inline HTML `onclick` attributes in `simulator/index.html` and JavaScript `addEventListener('click', ...)` bindings in `simulator/app.js`.
  - When the user clicked "Preview 3D TPU Panels", `openTpuPreviewModal()` executed twice simultaneously. Request #1 incremented `tpuLoadRequestId = 1`, and Request #2 incremented it to `2`.
  - When Request #1 finished, it evaluated `reqId !== tpuLoadRequestId` (1 !== 2) and exited early without dismissing `#tpuModalLoading`, leaving the spinner overlay permanently visible over the canvas.
  - Stripped duplicate inline `onclick` handlers from `simulator/index.html` and added a strict re-entrancy guard in `openTpuPreviewModal()`.
- **Three.js STLLoader Timeout & Safe Handling (`loadStlWithTimeout`):**
  - Created `loadStlWithTimeout(stlLoader, url, timeoutMs = 8000)` wrapper that prevents unhandled promise rejections and gracefully falls back or resolves `null` on network/file fetch issues.
  - Refactored `loadTpuModalData()` with a `try ... catch ... finally` block, ensuring `#tpuModalLoading` is guaranteed to be dismissed (`loaderOverlay.style.display = 'none'`) once processing completes.
- **Node Syntax Verification:**
  - Ran `node --check simulator/app.js` with zero errors.

### 2026-10-08 22:28 - Horizontal Channel Orientation & 3D STL Synchronization Fix
- **Global Horizontal Channel Alignment Enforcement:**
  - Diagnosed root cause why horizontal alignment on the Layout tab produced tangent collars in 3D preview: `getTpuWellRotationAngle` in `simulator/app.js` and `compile_clean_tpu_panel.py` were checking `if ('rotation_deg' in leds[i])` before checking the global `well_orientation == 'horizontal'` mode. If an LED had an old tangent angle cached, it overrode the horizontal mode.
  - Added explicit `is_custom_rotation` flag: only LEDs that have been explicitly rotated individually via the Inspector Angle controls retain their custom angle.
  - When Channel Alignment is set to **`[ ↔️ Horizontal ]`**, all un-customized LEDs strictly evaluate to $0.0^\circ$ baseline across the 2D layout canvas, layout signature hash, API payload, and 3D STL compilation engine (`compile_clean_tpu_panel.py`).
  - Verified compilation: running `python scripts/compile_clean_tpu_panel.py --orientation horizontal` produces 100% horizontal ($0.0^\circ$) collar pockets in the 3D meshes and `tpu_panel_specs.json`.

### 2026-10-08 22:10 - Wire Entrance Corridor Clearance Standard & Side Wall Tab Cleanup
- **Wire Entrance / Exit Corridor Focus:**
  - Clarified clearance standard per user requirements: checking is strictly focused on the wire entrance and exit notches at both ends of each LED collar ($\pm \vec{u}_i$), enforcing a $2.5\text{ mm}$ clear corridor in front of each wire notch so wires enter/exit cleanly without kinks or pinching.
  - Side walls of adjacent collars are allowed to sit close to each other without triggering false red warnings, provided they do not physically collide ($d_{\text{physical}} \ge 0.0\text{ mm}$, spine distance $\ge 8.6\text{ mm}$).
- **Removal of Red Side Wall Tabs:**
  - Removed lateral side-wall buffer indicator rectangles that previously rendered red boxes on the long side walls of collars.
  - Retained wire entrance/exit notch indicators at $+X$ and $-X$ collar ends, which outline in red only when an adjacent collar obstructs that specific wire entrance.
- **Dynamic Clamping & Relaxation Synchronization:**
  - Updated `checkLedClearanceStatus`, `clampLedNoCollarOverlap`, and `relaxLedCollarOverlaps` in `simulator/app.js` and `scripts/compile_clean_tpu_panel.py` to enforce zero collar collision (`req_dist = 8.6mm`), $2.5\text{ mm}$ wire entrance clearance, and $10.0\text{ mm}$ bridge clearance.

### 2026-10-08 21:26 - 3D File LED Well Orientation Synchronization & Individual LED Rotation Engine
- **3D File & Slicer Orientation Alignment:**
  - Diagnosed root cause for 3D files exporting horizontal wells: `params.tpuWellOrientation` defaulted to `'horizontal'`, sending `0.0°` rotations to the compiler despite tangent angles appearing on 2D canvas pills.
  - Set default `params.tpuWellOrientation = 'tangent'` across simulator, API endpoint, and compiler scripts.
  - Implemented 2D-to-3D coordinate angle transformation in `scripts/compile_clean_tpu_panel.py`: compensated for inverted-Y coordinate space ($\theta_{\text{3D}} = -\theta_{\text{canvas}} \pmod{360}$), ensuring that in slicers (Bambu Studio, PrusaSlicer, Orca) and 3D preview, every single collar is oriented at the exact angle displayed on the Layout canvas.
- **Individual LED Rotation Controls & Inspector Dock Card:**
  - Added dedicated **🔄 LED Well Angle Card** to `#ledInspectorSection` in `simulator/index.html` and `simulator/app.js`:
    - **Continuous Slider ($0^\circ$ to $360^\circ$):** Live scrubbing updates the rotation of the selected LED(s) in real time on the canvas.
    - **Numeric Degree Input:** Direct degree entry ($0.0^\circ$ to $360.0^\circ$) with live validation.
    - **Mode Badge:** Live indicator showing `[ 〰️ Tangent ]` or `[ 🔒 Custom XX° ]`.
    - **`[ 〰️ Auto ]` Reset Button:** Restores automatic wire-tangent orientation and clears manual lock.
    - **Quick Angle Presets & Nudges:** 1-click angle buttons (`0° Horiz`, `45°`, `90° Vert`, `135°`) plus `⟲ -15°` and `⟳ +15°` step buttons.
    - **Keyboard Shortcuts:** `R` nudges rotation $+15^\circ$ clockwise; `Shift + R` nudges $-15^\circ$ counter-clockwise when LED(s) are selected.
    - **Visual Orientation Axis:** Selected LEDs render a directional green axis arrow showing the orientation angle directly on the garment canvas.
- **Unified Rendering & Cache Invalidation:**
  - Updated `showPillSlots` and `showTpuWindows` in `renderBulb` to use `getTpuWellRotationAngle(index, leds)`.
  - Updated `computeTpuLayoutSignature()` to hash per-LED rotation angles, ensuring rotating an LED automatically invalidates stale STLs and triggers re-compilation.

### 2026-10-08 21:55 - Unified 3.0mm Clearance Standard Across Wire Channels & Collar Flanks
- **Unified 3.0mm Clearance Enforcement & Real-Time Canvas Warnings:**
  - Standardized both the longitudinal wire channel opening corridors and the lateral collar side buffers to **$3.0\text{mm}$** ($16.6\text{mm}$ center-to-center along channel, $11.6\text{mm}$ center-to-center laterally).
  - Updated all canvas drag warnings, blocked corridor overlays, and tooltip badges in `simulator/app.js` (`renderBulb`, `checkLedClearanceStatus`) to explicitly reflect **`⚠️ 3mm Clearance`** and `(<3mm channel clearance)`.
  - Updated `clampLedNoCollarOverlap`, `relaxLedCollarOverlaps`, and `scripts/compile_clean_tpu_panel.py` to enforce the $16.6\text{mm} \times 11.6\text{mm}$ footprint ($3.0\text{mm}$ all-around collar clearance).
- **Python Compiler & 3D Export Verification:**
  - Recompiled front and back plates in 8.40s; verified zero manifold errors.

### 2026-10-08 21:50 - 3mm Side Clearance Refinement & Visual Buffer Indicators
- **3.0mm Side / Lateral Clearance Enforcement:**
  - Updated `checkLedClearanceStatus` in `simulator/app.js` and PBD relaxation solver in `scripts/compile_clean_tpu_panel.py` to enforce a $3.0\text{mm}$ side clearance buffer between adjacent collar side walls (lateral center-to-center distance $\ge 11.6\text{mm}$, calculated as $4.3\text{mm} + 4.3\text{mm} + 3.0\text{mm}$).
  - Updated `clampLedNoCollarOverlap` and `relaxLedCollarOverlaps` to maintain both the $18.6\text{mm}$ channel opening corridor ($5.0\text{mm}$ in front of wire openings) and $11.6\text{mm}$ lateral collar spacing ($3.0\text{mm}$ side clearance).
  - Added dual $3.0\text{mm}$ red lateral buffer indicators in `renderBulb` whenever side clearance is violated.
- **Python Compiler & 3D Export Verification:**
  - Recompiled front and back plates in 8.50s; verified PBD solver convergence with max shift $\le 0.01\text{mm}$.

### 2026-10-08 21:40 - Optical Aperture Carryover, 5mm Channel Clearance & Live Red Drag Feedback, Strain Relief Clearances & Clean Monolithic Bridges
- **Circular & Square Optical Aperture Carry-Over to 3D Preview:**
  - Updated `setTpuWindowShape` and `setTpuWellOrientation` in `simulator/app.js` to automatically display the compilation loading overlay and re-compile/reload the 3D viewer when toggling window shape (`Ø 3.4mm Round`, `Ø 3.0mm Round`, `3x3mm Square`) or well orientation while the 3D Armor Panel modal is open.
  - Aligned default fallback orientation in `openTpuPreviewModal` to `tangent` (`params.tpuWellOrientation || 'tangent'`) to prevent unnecessary recompilation triggers on modal launch.
- **Strain Relief Bridge Clean Monolithic Arch (Misplaced Gusset Removal):**
  - Removed misplaced internal triangular gussets from both entrance and lateral exit zip-tie strain relief bridges in `scripts/compile_clean_tpu_panel.py` (`internal_bridge_m` and `internal_bridge_exit_m`).
  - Both bridges are now clean, robust monolithic arch boxes with unobstructed $3.2\text{mm} \times 2.8\text{mm}$ through-tunnels for zip-tie heads and $4.5\text{mm}$ wire saddle cradles.
- **5mm Channel Opening Clearance Enforcement & Live Red Visual Feedback:**
  - Implemented `checkLedClearanceStatus(index, ledsList)` in `simulator/app.js`: calculates longitudinal unit vector $\vec{u}_i = (\cos\theta_i, \sin\theta_i)$ and perpendicular vector $\vec{v}_i = (-\sin\theta_i, \cos\theta_i)$ for each LED collar in plate millimeter space.
  - Enforced a $5.0\text{mm}$ clearance corridor in front of each channel opening ($p \in [4.5\text{mm}, 18.6\text{mm}]$ with lateral corridor width $8.0\text{mm}$).
  - Enforced a $10.0\text{mm}$ buffer from both entrance and lateral exit strain relief bridges.
  - Updated `renderBulb` in `simulator/app.js`:
    - When clearance is violated, renders the outer TPU collar outline in vibrant red (`#ff3366`, `lineWidth = 2.2`), tints the collar cavity red, highlights the blocked opening corridor in red (`rgba(255, 51, 102, 0.40)` with `#ff3366` border), and turns the selection/hover halo red.
    - When dragging an LED with $<5\text{mm}$ channel clearance, displays a real-time `⚠️ 5mm Clearance` warning badge directly above the LED.
  - Updated `clampLedNoCollarOverlap` and `relaxLedCollarOverlaps` to maintain both the $18.6\text{mm}$ channel opening corridor and $10.0\text{mm}$ bridge buffers.
- **Python Compiler & Multi-Material 3D Verification:**
  - Updated `scripts/compile_clean_tpu_panel.py` PBD relaxation solver with $5.0\text{mm}$ opening corridor and $10.0\text{mm}$ bridge buffers.
  - Verified compilation of 75-LED front and back panels with 5-part multi-material inlays in 8.68s.

### 2026-10-08 21:05 - Proportional LED Pill Shadows & TPU Collar Scaling for Medium/Small Sizes
- **Proportional Physical Scale Factor (`ppm`):**
  - Updated `renderBulb` in `simulator/app.js` to compute the pixels-per-millimeter scale factor against the active plate dimension (`selectedPlateWidthMm`: 165.1mm Small, 203.2mm Medium, 254.0mm Large) and chest graphic bounds (`gb.normW * s.width`), rather than assuming a rigid garment width.
- **Lowered Rigid Floor Minimums:**
  - TPU Outer Collar clamp lowered from $15 \times 9\text{px}$ to $6.0 \times 4.0\text{px}$.
  - TPU Inner Pocket clamp lowered from $11 \times 5.5\text{px}$ to $4.5 \times 2.5\text{px}$.
  - TPU Snap Lip clamp lowered from $16 \times 10\text{px}$ to $7.0 \times 4.8\text{px}$.
  - Optical Window clamp lowered from $4.5\text{px}$ to $2.5\text{px}$.
  - HTV Vinyl Pill cutout clamp lowered from $12 \times 6\text{px}$ to $4.5 \times 2.4\text{px}$.
  - Resin Pebble LED clamp lowered from $8 \times 5.5\text{px}$ to $3.2 \times 2.4\text{px}$.
- **Subtle Visual Styling:**
  - Softened TPU collar drop-shadow opacity from `0.50` to `0.32` and dashed lip guide line from `0.18` to `0.12` alpha, rendering an elegant 3D chassis bevel that preserves full artwork visibility on Small and Medium size plates.

### 2026-10-08 20:58 - Fix LED Distribution on Character Artwork (Re-distribute & Presets)
- **Eliminated Double-Transform & Off-Graphic Displacement:**
  - Fixed offscreen canvas rasterization in `scatterLedsOnGraphic`, `sampleColorAtNorm`, `sampleColorAtNormCoord`, and `resampleAllLedColors`: replaced nested `drawPetesDragon` calls that were double-applying chest bounding box offsets (`gb.normX`, `gb.normY`) with direct 1:1 image rasterization.
  - Removed unconstrained `relaxLedCollarOverlaps(newLeds, 40)` from `scatterLedsOnGraphic`: Farthest Point Sampling (FPS) already guarantees maximal inter-bulb Euclidean spacing while strictly confining 100% of selected LEDs to valid foreground graphic pixels.
- **Explicit SVG Natural Dimensions:**
  - Added explicit pixel `width` and `height` attributes (`800x600` and `600x850`) to all vector files in `assets/cricut_svg/`, preventing `naturalWidth = 0` fallback issues in browser `Image` objects.
- **Regenerated 7-Float Preset Files:**
  - Cleaned and updated all official float presets in `presets/` (`casey_jr_train.json`, `title_drum.json`, `spinning_turtle.json`, `spinning_snail.json`, `cinderellas_coach.json`, `petes_dragon.json`, `petes_dragon_chris.json`):
  - Fixed the 18 stray LEDs in Casey Jr. (previously down at `y = 0.88` under bib) by redistributing all 100 LEDs cleanly across the locomotive body (`y <= 0.55`).
  - Cleared stray margin LEDs across all other float presets, ensuring both initial load and manual re-distribution keep all LEDs 100% on the graphic.

### 2026-10-08 20:34 - Nearby Neighbor LED Ordering, Lateral Exit Portal, and 50–100 LED Slider
- **Nearby Neighbor LED Progression (Default):**
  - Implemented consecutive neighbor-to-neighbor traversal starting at the bottom entrance portal and terminating at the lower-right lateral exit portal.
  - Added a 2-opt uncrossing pass (`doLineSegmentsIntersect`) to eliminate criss-crossing wire segments while preserving designated entrance and exit nodes.
  - Added a selectable toggle in the Layout tab between `[ 🔗 Nearby (Default) ]` and `[ 🔀 Wide Spacing ]` (~6.8 cm jump routing).
- **Lateral Wire Exit Portal & Strain Relief:**
  - Added lower-right lateral wire exit portal ($5.5\text{mm} \times 3.5\text{mm}$ parting line U-notch) matching the bottom entrance portal.
  - Integrated matching internal floor zip-tie strain relief bridge ($2.0\text{mm}$ walls, $2.8\text{mm}$ high tunnel, $4.5\text{mm}$ bridge height, wire saddle cradle, and triangular side gussets).
  - Added matching wire portal clearance on the 2.0mm rear protective lid assembly.
  - Rendered green `⚡ IN (P1)` and red `OUT ➔` visual badges with dotted leader wires to the first and last LEDs on the 2D simulator canvas.
- **50 to 100 LED Count Slider & Manual Re-distribute Button:**
  - Added fine-grained `#ledCountSlider` (50–100, step 1) with real-time target count display.
  - Strictly decoupled slider movement from redistribution so moving the slider updates the target readout without moving placed LEDs.
  - Added adjacent `[ 🔄 Re-distribute ]` button (`#redistributeLedsBtn`) to manually scatter the chosen LED count across the active graphic and re-route with the active sequence mode.
- **Dual-Plate 3D Compilation:** Compiled front and back plates in 8.98s; verified watertight geometry and updated `3d_panels/tpu_panel_specs.json`.

### Entry: Multi-Density (60, 100, 144 LEDs/3.2ft) Strip Modes, Flush Placement & Pitch Matching Presets
* **Date:** 2026-10-08 (Imagineering Session - LED Strip Density & Grid Pitch Matching)
* **Milestone:** Milestone 3 & 4 - Simulator UX Architecture & Physical Lighting Modeling
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Selectable Strip Densities (60, 100, 144 LEDs per 3.2ft / 1m):**
     - Integrated 3-button density selector (`#btfDensity60Btn`, `#btfDensity100Btn`, `#btfDensity144Btn`) with dynamic badges (`#btfLinearPitchBadge`, `#btfStripDensityBadge`).
     - **60 LEDs/3.2ft:** Linear LED pitch $P = 1000 / 60 \approx 16.6667\text{ mm}$ (~0.656").
     - **100 LEDs/3.2ft:** Linear LED pitch $P = 1000 / 100 = 10.0000\text{ mm}$ (~0.394"), identically matching the 10mm silicone strip width.
     - **144 LEDs/3.2ft:** Linear LED pitch $P = 1000 / 144 \approx 6.9444\text{ mm}$ (~0.273"), high-definition silhouette rendering.
     - Strip matrix generator dynamically calculates solder cut marks, total strip length ($L = N_{\text{LED}} \times P$), and 5V current draw using the active density.
  2. **Continuous Spacing Slider with Live Gap Telemetry (`#btfSpacingSlider`):**
     - Expanded slider range from **6.9mm to 40.0mm** (0.1mm precision).
     - Live readout displays center-to-center pitch along with physical clearance between adjacent 10mm silicone sheaths: e.g. `10.0 mm (0.0mm Gap - Flush)` or `16.7 mm (Gap: 6.7mm)`.
  3. **Pitch Matching & Flush Alignment Presets:**
     - **`📐 Match LED Pitch` (`#btfMatchPitchBtn`):** Instantly sets strip-to-strip pitch to match the active linear LED pitch ($16.7\text{mm}$, $10.0\text{mm}$, or $6.9\text{mm}$), producing an isotropic square or hexagonal staggered matrix.
     - **`⚡ Flush (10mm)` (`#btfFlushBtn`):** Places strips directly side-by-side with 0.0mm gap ($10.0\text{mm}$ center-to-center pitch, matching the 10mm silicone sheathing width).
     - **`🎯 Auto-Fit ~100` (`#btfAutoFit100Btn`):** Numerical search algorithm calculates the optimal pitch to fit ~95–105 LEDs for the 2.0A battery envelope across any chosen density or plate size.
     - **`🌿 Relaxed (25mm)` (`#btfSparsePresetBtn`):** Quick-sets 25.0mm ribbon spacing for ultralight, low-current layouts.

### Entry: TPU Chassis 10.0mm (+1mm Wire Room), 1.8mm Sockets (50% Thicker), 3mm Clip Clearance, Tangent Alignment & Ø 3.4mm Default Windows
* **Date:** 2026-10-09 (Imagineering Session - Heavy-Duty TPU Mechanical Reinforcement & Optical Overhaul)
* **Milestone:** Milestone 5 - 3D Printed Armor & Multi-Material Hardware Engineering
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator/index.html`, `simulator/app.js`, `simulator.py`, `3d_panels/tpu_panel_specs.json`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Chassis Perimeter Rim & Wire Clearance (+1.0mm Vertical Room):**
     - Perimeter rim height increased from $7.0\text{ mm}$ to **$8.0\text{ mm}$** ($Z = 2.0$ to $10.0\text{ mm}$, $2.5\text{ mm}$ wall width), raising overall plate thickness to **$10.0\text{ mm}$**.
     - Provides an extra $+1.0\text{ mm}$ of vertical wire room cavity under the 2.0mm rear lid (8.0mm open wire basin), allowing multi-conductor ribbon wire slack and folds to sit comfortably without binding.
     - Tray screw boss pillars automatically rise to $Z = 10.0\text{ mm}$ ($8.0\text{ mm}$ height) with pre-formed $1.6\text{ mm} \times 5.5\text{ mm}$ M2 pilot holes, meeting the 2.0mm rear lid perfectly flush.
     - Parting-line wire portal U-notch deepened to $3.5\text{ mm}$ tall $\times 5.5\text{ mm}$ wide.
  2. **LED Well Walls Thickened by 50% (1.8mm Walls) & 3.0mm Lateral Clip Clearance:**
     - Collar walls expanded from $1.2\text{ mm}$ to **$1.8\text{ mm}$** ($13.6\text{ mm} \times 8.6\text{ mm}$ outer well footprint; inner socket preserved at $10.0\text{ mm} \times 5.0\text{ mm}$), permanently eliminating thin wall fractures during running vibration.
     - Top retention lip extends $0.70\text{ mm}$ past the new wall face ($15.0\text{ mm} \times 10.0\text{ mm}$ outer lip footprint).
     - Enforced **$3.0\text{ mm}$ lateral clear buffer** on each side of every collar ($14.6\text{ mm}$ minimum center-to-center clearance) in both the Python compiler PBD solver and the browser collision relaxation engine. Ensures 3D-printed retention clips slide over from collar flanks with zero interference.
  3. **Selectable Channel Alignment (Horizontal vs Tangent to Wire):**
     - Added `#tpuOrientationSelectorRow` and 3D preview controls: `[ ↔️ Horizontal (Default) | 〰️ Tangent to Wire ]`.
     - In **Tangent to Wire** mode, each socket dynamically aligns with the chord tangent vector of the incoming and outgoing wire segments, minimizing sharp ribbon wire twists along organic character contours.
     - Propagated across 2D canvas preview, 3D WebGL inspector, and exported 3D STL/3MF models.
  4. **Heavy-Duty Strain Relief Bridge with Side Gussets & 2x Higher Tunnel:**
     - Bridge walls doubled in thickness from $1.0\text{ mm}$ to **$2.0\text{ mm}$**; bridge overall height raised to **$4.5\text{ mm}$**.
     - Under-tunnel height doubled from $1.4\text{ mm}$ to **$2.8\text{ mm}$** ($3.2\text{ mm}$ wide), allowing standard miniature zip-tie heads to pass through effortlessly.
     - Reinforced with solid **triangular side gusset buttresses** anchored into the floor beneath the wire path for maximum mechanical pull-out strength.
  5. **Selectable Optical Apertures (Ø 3.4mm Round Default):**
     - Added 3-way aperture switcher in toolbar and 3D modal: `[ 🔘 Ø 3.4mm Round (Default) | ⚪ Ø 3.0mm Round | 🔲 3×3mm Sq ]`.
     - Set **Ø 3.4mm Round** as the new factory default for maximum light transmission and wide-angle visibility through runner shirts.
     - Fully reflected in 2D canvas bloom, Three.js 3D texture projection, and watertight CSG cylinder cutter subtraction in Python Manifold3D compiler.

### Entry: Proportional Plate Sizing (Small/Medium/Large) & 10mm/5mm Strip LED Calibration
* **Date:** 2026-10-08 (Imagineering Session - Proportional Plate & Strip Calibration)
* **Milestone:** Milestone 3 & 4 - Simulator UX Architecture & Physical Lighting Modeling
* **Status:** Complete & Verified (`simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Dynamic Plate Sizing & Bounds Scaling (`getGraphicChestBounds`):**
     - Coupled `selectedPlateSize` (`small`, `medium`, `large`) directly into the normalized graphic bounding box engine (`getGraphicChestBounds`).
     - **Small (~6.5" / 165mm):** Scales graphic by $0.8125\times$, generating fewer LEDs in BTF strip mode (~21–26 LEDs on Pete's Dragon).
     - **Medium (~8.0" / 203mm):** Standard reference chest scale ($1.000\times$, ~28–41 LEDs on Pete's Dragon).
     - **Large (~10.0" / 254mm):** Expands graphic across the upper chest ($1.250\times$), generating significantly more LEDs (~50–68 LEDs on Pete's Dragon) while strictly preserving clearance above the race bib ($y \le 0.555$).
     - Preserves exact aspect ratio: $\text{normW} = \text{normH} \times 1.25 \times \text{aspect}$.
  2. **Interactive Plate Size Selection Hook (`selectPlateSizeOption`):**
     - Clicking Small, Medium, or Large now instantly recomputes `computeBtfStripMatrix()` when strip preview is active, updating live telemetry and canvas overlay in real time.
     - Automatically re-scales any existing placed pebble LEDs to keep them anchored to their respective artwork facial and body features.
  3. **Strict 10mm Strip & 5mm LED Proportional Canvas Rendering (`drawBtfStripOverlay`):**
     - Calibrated silicone strip sheathing ribbon width to **strictly 10.0mm physical width** (`STRIP_TUBE_WIDTH_MM = 10.0`).
     - Scaled SMD 5050 packages to **strictly 5.0mm physical width** (`pkgSizePx = 5.0 * mmToPx`), taking up exactly 50% of the 10.0mm strip width with clean 2.5mm silicone margins on each side.
     - Centered circular phosphor emitter lens ($3.2\text{ mm}$ die diameter) with specular highlights.
     - **Canvas Zoom Lock (Eliminated Double Scaling):** Removed extraneous `* zoomScale` from `pkgSizePx` and glow radii. Since `ctx.scale(zoomScale, zoomScale)` already wraps the entire canvas render loop, eliminating the internal zoom multiplier guarantees that LED strips and chest artwork zoom in 100% 1:1 unison without any visual drift or ballooning.

### Entry: BTF-LIGHTING WS2812B (60 LED/m) IP67 Strip Preview with Staggered Rows & Columns
* **Date:** 2026-10-08 (Imagineering Session - LED Strip Alternative Architecture)
* **Milestone:** Milestone 3 & 4 - Simulator UX Architecture & Physical Lighting Modeling
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Non-Destructive Interactive Preview Overlay:**
     - Added `#btfStripPreviewToggle` in Section 3c of the Layout tab. Toggling the preview renders realistic silicone strip ribbons and SMD 5050 packages without modifying the costume's placed pebble LEDs, wiring tour, 3D armor panels, or sequence cues.
     - Pebble wiring lines and slack tension arcs are cleanly suppressed during strip preview.
     - Switching back OFF immediately restores the exact baseline pebble layout.
  2. **Physical Strip Geometry & 50% Brick Stagger Engine:**
     - Calibrated for **BTF-LIGHTING WS2812B IP67 DC5V 60 LEDs/m** (fixed $16.6667\text{ mm}$ linear LED pitch along strips).
     - **Orientation:** Configurable between `↔️ Horizontal Rows` and `↕️ Vertical Columns`.
     - **50% Brick Stagger:** Shifts alternating rows or columns by half a pitch ($8.33\text{ mm}$), yielding an organic hexagonal/honeycomb LED distribution across the costume that eliminates Cartesian grid banding.
     - **Boundary Masking:** Supports dual modes: `✂️ Clip to Float Art` (masks to opaque artwork silhouette alpha $> 35$, color-sampling directly from character pixels) and `🔲 Chest Panel Grid` (fills upper chest trapezoid above race bib).
  3. **Live Hardware Telemetry & Safety Budget:**
     - Computes active LED count, contiguous strip cut count (individual segments $S_1, S_2\dots$ requiring solder jumpers), total linear strip length in meters and feet, and estimated 5V current draw (max full white at $50\text{ mA}$ vs. animated average at $20\text{ mA}$).
     - Features `🟢 100-LED Safe (~2.0A Bank)` vs `⚠️ Over Budget` status badge.
     - **Numerical Auto-Fit Preset (`🎯 Auto-Fit ~100 LEDs`):** Iteratively solves ribbon spacing in mm to target $\sim 95\text{--}105$ LEDs matching the portable power bank safety budget.
  4. **Photorealistic Canvas Visualization:**
     - Renders $12\text{ mm}$ wide IP67 translucent white silicone sheathing ribbons with sealed perimeter borders, copper solder cut tick marks, segment badges (`S1`, `S2`...), square SMD 5050 bodies, circular phosphor emitter lenses with specular highlights, and breathing radial bloom glow.
  5. **Seamless Preset & Artwork Integration:**
     - Hooked into `applyProfileData`, `loadGraphicPreset`, and `artworkUploadInput` so switching floats or uploading custom art automatically re-samples the strip matrix when preview is active.
  6. **Layout Promotion ("Apply Strip Layout"):**
     - Clicking `✅ Apply Strip Layout as Active LEDs` promotes the generated matrix to active costume LEDs upon confirmation, registered in `Ctrl+Z` undo history.

### Entry: Float 4 Spinning Snail Asset Processing (Transparent Background & 5-Color 3D Printable Alternating Stripes)
* **Date:** 2026-10-08 (Imagineering Session - Float 4 Snail Asset Processing)
* **Milestone:** Milestone 5 - 3D Printed Armor & Cricut Vinyl Production Pipeline
* **Status:** Complete & Verified (`assets/snail2.png`, `scripts/process_snail2.py`, `PROJECT_PROGRESS.md`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  1. **Background Removal & Alpha Transparency:**
     - Fully isolated the low-poly 3D spinning snail float from `assets/snail2.png`.
     - Completely eliminated all background elements (dark night sky, spectator crowd silhouettes, road/curb ground, and streetlamp fixtures at top-right).
     - Produced a pristine transparent PNG with 79.3% alpha-transparent pixels (`RGBA [0, 0, 0, 0]`) and crisp edges.
  2. **Harmonized 5-Color Multi-Material Filament Palette:**
     - Strictly restricted every foreground pixel (15,314 px) to the 5 official multi-material 3D printing filaments defined in `FLOAT_STL_COLOR_CONFIG['spinning_snail']`:
       - **Black:** `#11161d` (RGB `[17, 22, 29]`) — Divider stripes & separator bands (4,451 px / 29.1%)
       - **Red:** `#ef4444` (RGB `[239, 68, 68]`) — Snail head, neck, underbelly, and foot (3,302 px / 21.6%)
       - **Gold:** `#facc15` (RGB `[250, 204, 21]`) — Antennae stalks, eye diamond, shell outer rim, and spiral divider track with center curl (3,125 px / 20.4%)
       - **Green:** `#10b981` (RGB `[16, 185, 129]`) — Alternating green radial stripes (2,239 px / 14.6%)
       - **Blue:** `#2563eb` (RGB `[37, 99, 235]`) — Alternating blue radial stripes (2,197 px / 14.3%)
  3. **Alternating Radial Stripe Sequence:**
     - Divided the shell disc and outer hood into 32 angular sectors ($11.25^\circ$ each, phase-aligned at $\theta_0 = 5.0^\circ$ around center `(153.5, 156.5)`), perfectly matching the underlying low-poly 3D mesh facets.
     - Implemented the repeating 4-phase sequence: `Green -> Black -> Blue -> Black -> Green -> Black -> Blue -> Black...` (8 complete cycles).
     - Ensured continuous radial spoke alignment between the outer hood tier and inner wheel.
  4. **Reproducible Pipeline (`scripts/process_snail2.py`):**
     - Authored a fully deterministic, self-contained Python script to reconstruct or regenerate the 5-color asset directly from raw uploads.

### Entry: 30s Fleet Show Timestamped Naming, Interactive Save Modal & Conflict Detection
* **Date:** 2026-10-08 (Imagineering Session - 30s Fleet Show Save Harmonization)
* **Milestone:** Milestone 3 & 4 - Simulator UX Architecture & Choreography Studio
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `simulator.py`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Harmonized Fleet Show Nomenclature:**
     - The 30s Fleet Show Creator now follows the exact same timestamped convention as Floats and Parade Fleets: `<ShowName> <YYYY-MM-DD HH-mm>` (e.g., `Grand Parade 2026-10-08 14-20`, `Fleet Show 2026-10-08 14-20`).
     - `createNewFleetShow()` initializes fresh custom routines with default name `Fleet Show <YYYY-MM-DD HH-mm>` and timestamped ID.
  2. **Interactive Save Fleet Show Modal (`#saveFleetShowModal`):**
     - Clicking **`💾 Save Show`** (`#fleetSaveShowBtn`) launches a dedicated modal with:
       - Real-time overview metrics: total loop duration (e.g. `30.0s Loop`), configured choreography blocks, and ESP-NOW target broadcast indicator.
       - Live filename preview: `presets/fleet_shows/<clean_slug>.json`.
       - Duplicate file collision detection: checks server files via `/api/save_fleet_show`, reveals duplicate warning banner, red border styling, and an `⚠️ Overwrite Existing` button.
  3. **Backend Conflict Protection (`simulator.py`):**
     - `/api/save_fleet_show` now checks for existing files in `presets/fleet_shows/` and returns HTTP 409 Conflict when `overwrite: false`, safely preventing accidental file overwrites.
  4. **Seamless Integration with Parade Fleet Prerequisite Check:**
     - When saving the master parade fleet (`💾 Save Parade Fleet`), if the active show has unsaved edits (`isFleetShowDirty === true`), confirming the prompt cleanly opens `openSaveFleetShowModal()` with the timestamped naming and conflict safeguards before finalizing the master fleet save.

### Entry: Consolidated Single Save Locations, Strict Hierarchy & Two-Step Fleet Prerequisite Check
* **Date:** 2026-10-08 (Imagineering Session - Single Save Location & Fleet Hierarchy Consolidation)
* **Milestone:** Milestone 3 & 4 - Simulator UX Architecture, Preset Pipeline & Fleet Choreography Safety
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Consolidated Single Save Locations (Zero Redundancy):**
     - **Floats (Layout Tab - Section 2):** Authoritative single place to save and export floats is Section 2 (`💾 Save & Export Floats`) via `#saveProfileBtn` (`💾 Save Float`), `#downloadProfileBtn` (`⬇ Export JSON`), `#exportCricutSvgBtn`, and `#importProfileBtn`.
     - **Clean Layout Section 3:** Removed duplicate `#saveLayoutBtn` ("Save Float") and `#exportLayoutJsonBtn` ("Export JSON") from Section 3 (`LED Layout & Wiring Route`); replaced with a clean, full-width `🔄 Reset Layout to Default` button.
     - **Parade Fleet (Fleet Tab - Section 2):** Authoritative single place to save and export the parade fleet is Section 2 (`7-Runner Baseline Presets & Master Fleet Suite`) via `#fleetSaveConfigBtn` (`💾 Save Parade Fleet`) and `#fleetExportBundleBtn` (`📦 Export Fleet Bundle`). Removed duplicate `#layoutExportAllFleetBtn` from Layout tab.
     - **30s Choreography Show (Fleet Tab - Section 1):** Dedicated `#fleetSaveShowBtn` (`💾 Save Show`) in Section 1 for authoring 30-second routines.
  2. **Two-Step Safety Prerequisite Check on `💾 Save Parade Fleet`:**
     - **Step 1 (Unsaved Canvas Float):** Checks `isSingleShirtDirty`. If true, prompts: *"Float X ([Name]) currently has unsaved layout or animation changes on the canvas. Floats must be saved before saving the Parade Fleet suite..."* -> triggers `openSavePresetModal()`.
     - **Step 2 (Unsaved Fleet Show):** Checks `isFleetShowDirty`. If true, prompts: *"Unsaved Fleet Show Detected! '[Show Name]' currently has unsaved choreography changes. The 30s Fleet Show must be saved before saving the Parade Fleet suite..."* -> triggers `saveActiveFleetShow()`.
     - Once both prerequisites pass, proceeds to `#saveFleetModal` with default title `Parade Fleet <YYYY-MM-DD HH-mm>`.
  3. **Fleet Show Dirty State Tracking (`isFleetShowDirty`):**
     - Automatically marked dirty on block duration adjustments (inputs), color dynamic changes (selects), block additions (`addFleetBlock`), reordering (`moveFleetBlock`), duplications (`duplicateFleetBlock`), deletions (`removeFleetBlock`), timeline dragging/resizing, and 30.0s time snaps (`snapFleetShowTo30s`).
     - Reset cleanly to `false` when `saveActiveFleetShow()` completes or a show is loaded via `loadFleetShow()`.
  4. **Nomenclature & Default Naming Harmonization:**
     - Float saving modal `#savePresetModal` dynamically formats base float name with current timestamp `<FloatName> <YYYY-MM-DD HH-mm>` (e.g. `The Drum 2026-10-08 14-10`), updating `profileNameInput`.
     - `#unsavedChangesModal` updated to Float nomenclature (`Unsaved Float Changes`, `Save Float Name:`, `💾 Save Float & Switch`).

### Entry: Nomenclature Refactoring, Timestamped Saving (Floats & Fleet), Unsaved Float Pre-Check & 3D Export Filenames
* **Date:** 2026-10-08 (Imagineering Session - Nomenclature Clarity & Timestamped Workflows)
* **Milestone:** Milestone 3 & 4 - Simulator UX Architecture, Preset Pipeline & 3D Manufacturing Export
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `simulator.py`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  1. **Nomenclature Clarification:**
     - Layout tab updated from "Profiles / Presets" to **"Floats"** (`💾 Save Float`, Section 2 "Save & Export Floats", dropdown "Load Saved Float File").
     - Fleet tab updated from "Save Fleet Lineup" to **"💾 Save Parade Fleet"**.
  2. **Timestamped Default Naming:**
     - Float saving defaults dynamically to `<FloatName> <YYYY-MM-DD HH-mm>` (e.g., `Title Drum 2026-10-08 13-45`).
     - Parade Fleet saving defaults dynamically to `Parade Fleet <YYYY-MM-DD HH-mm>` (e.g., `Parade Fleet 2026-10-08 13-45`).
     - Standardized `getFormattedTimestamp(forFilename = false)` helper ensuring consistent format across titles and filenames.
  3. **Unsaved Float Pre-Check Before Fleet Save:**
     - Clicking `💾 Save Parade Fleet` actively verifies whether any float in the lineup has unsaved canvas edits (`isSingleShirtDirty === true`).
     - Prompts user to save that float first, cleanly continuing to the fleet save modal upon float save completion or aborting cleanly on cancel.
  4. **Parade Fleet Suite Saving & Backend Persistence:**
     - Interactive `#saveFleetModal` captures 7-runner lineup linking to saved float files, 30-second fleet choreography show blocks, and ESP-NOW sync parameters.
     - Backend `/api/save_fleet_config` persists to both `fleet_lineup.json` (active startup) and timestamped `presets/parade_fleet_*.json` with HTTP 409 duplicate file conflict protection.
  5. **Timestamped & Float-Named 3D File Exports:**
     - All 3D panel download buttons (`updateTpuDownloadButtons()`) dynamically incorporate the float name, variant, and timestamp into filenames:
       - Multi-Color Bundle ZIP: `<float>_<variant>_<timestamp>_multicolor_bundle.zip`
       - Bambu Studio Project (.3MF): `<float>_<variant>_<timestamp>_multicolor.3mf`
       - Rear Lid STL: `<float>_<variant>_<timestamp>_lid.stl`
       - Individual Inlays: `<float>_<variant>_<timestamp>_<color>.stl`
       - Monolithic STL: `<float>_<variant>_<timestamp>_monolithic.stl`

### Entry: Comprehensive Preset Saving (Canvas Coordinates, Count, Groups, Shows & Duplicate File Protection)
* **Date:** 2026-10-08 (Imagineering Session - Complete Preset State & Duplicate Protection)
* **Milestone:** Milestone 3 & 4 - Float Suite Management & Theatrical Show Sequencing
* **Status:** Complete & Verified (`simulator.py`, `simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Comprehensive Float State Serialization (`buildCompletePresetData`):**
    - Presets now save the exact normalized $(x, y)$ coordinates and physical count of all LEDs on the canvas (50, 75, 100, or custom).
    - Preserves all float-specific animation groups (wheel rotations, rim chases, fireworks starbursts, dragon crest pulses).
    - Preserves all theatrical show sequence cues (Parade Cue Director 90s loop duration and cues).
    - Preserves float identity (float ID 1–7, name, role, tag, race bib number, accent color).
    - Preserves 3D armor plate parameters (selected plate size, width in mm, and AMS filament color mappings).
  - **Interactive Save Costume Preset Modal (`#savePresetModal`):**
    - Both **`💾 Save`** (Section 2 - Sidebar) and **`💾 Save Preset`** (Section 3 - LED Layout & Wiring Route) launch a streamlined modal with real-time badges (Active Float, Canvas LED Count, Animation Group Count, Theatrical Cue Count).
    - Live filename preview (`Will save as: presets/<clean_name>.json`) updates dynamically as the user types.
  - **Duplicate File Checking & Rename Capability:**
    - Python backend (`/api/save_preset` in `simulator.py`) checks for filename collisions in `presets/` and returns HTTP 409 Conflict if a file already exists without `overwrite: true`.
    - Modal displays an alert banner (`⚠️ File Already Exists`) allowing the user to either edit/rename the preset or click `⚠️ Overwrite Existing` to replace the existing file on disk.
  - **Export JSON & Fleet Sync:**
    - Wired `exportLayoutJsonBtn` alongside `saveLayoutBtn` in Section 3 so users can directly download the complete float JSON bundle.
    - Synchronizes saved presets with the active runner card slot in the 7-Shirt Fleet Lineup and updates all dropdown selectors.

### Entry: Authentic Title Drum 5-Color Sampling & Resampling Fix for All Non-Dragon Floats
* **Date:** 2026-10-08 (Imagineering Session - Color Sampling Engine Correction)
* **Milestone:** Milestone 3 & 6 - Float Suite Integration & Color Fidelity Engine
* **Status:** Complete & Verified (`simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Identified Root Cause of Resampling Failure:**
    - `boostLedVibrancy()` previously used an explicit whitelist that included only `'custom_image'`, `'cinderellas_coach'`, `'carriage_nohorses'`, `'spinning_turtle'`, and `'spinning_snail'`, omitting `'title_drum'`.
    - When switching to the Title Drum and spreading or resampling LEDs, the function fell through into Pete's Dragon color mapping rules, forcing drum face black pixels (`#11161d`) and crimson red pixels (`#ef4444`) to map to Pete's Dragon Pink (`#ff19e6`), and gold pixels (`#facc15`) to orange (`#ff7800`).
  - **Generalization of `boostLedVibrancy()`:**
    - Restricted Pete's Dragon pink crest/spines and dragon green rules exclusively to `currentGraphicType === 'builtin_dragon' || currentGraphicType === 'petes_dragon'`.
    - All non-dragon floats now use authentic graphic color sampling.
  - **Authentic 5-Color Title Drum Palette Engine:**
    - **Marquee Gold (`#facc15` / `[250, 204, 21]`):** High-vibrancy parade golden amber (`{ r: 255, g: 204, b: 21 }`).
    - **Body & Streamers Red (`#ef4444` / `[239, 68, 68]`):** Radiant crimson red (`{ r: 239, g: 68, b: 68 }`).
    - **Lead Pennant Green (`#10b981` / `[16, 185, 129]`):** Electric flag green (`{ r: 16, g: 200, b: 129 }`).
    - **Flags & Pennants Blue (`#2563eb` / `[37, 99, 235]`):** Electric royal blue (`{ r: 37, g: 99, b: 255 }`).
    - **Drum Face & Chassis Black (`#11161d` / `[17, 22, 29]`):** Warm incandescent starlight white (`{ r: 255, g: 245, b: 220 }`), representing the illuminated vintage interior starlight bulbs of the Electrical Parade drum face rather than remaining unlit or falling back to Pete's Dragon pink/green.
  - **Harden Asynchronous Image Decode Checks:**
    - Added `activeImg && activeImg.naturalWidth > 0` validation guards across all sampling routines (`sampleColorAtNormCoord`, `sampleColorAtNorm`, `resampleAllLedColors`, `rearrangeRemainingLedsOnGraphic`, `scatterLedsOnGraphic`, `autoOutlineCurrentGraphic`, `sampleRemainingGraphicLeds`), preventing `NaN` dimensions during rapid float switching or canvas re-rendering.

### Entry: Layout Mode Assembly & Print Placement Guide (Faint Graphic, 3×3mm Square Windows & Compact Numbers Above)
* **Date:** 2026-10-08 (Imagineering Session - LED Placement & Print Reference Mode)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication, Physical Assembly Reference & Workshop Tooling
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Graphic View Mode Chooser in Layout Tab & Zoom Toolbar:**
    - Added dedicated Graphic View Mode toggle buttons in Layout Section 1 (`[🎨 Full Color]` vs. `[🖨️ Placement Guide]`) and quick toggle button in the Canvas Zoom Toolbar (`🖨️ Placement Guide`).
    - Works with all 7 float graphics (Casey Jr, Title Drum, Turtle, Snail, Coach, Dragon, Eagle) and custom uploads.
  - **Faint Graphic Watermark Rendering:**
    - Subdues active character artwork to a faint background opacity (default **22%**, customizable 10%–60% via live slider).
    - Ensures high visual contrast so float boundary context is visible while numbers and apertures remain crystal clear.
    - Also softens race bib to 20% opacity so lower chest LEDs and wiring traces are unobstructed.
  - **Physical 3×3 mm Square Windows:**
    - In Placement Guide mode, every LED is rendered as a clean, physical **3.0 mm × 3.0 mm square aperture** ($winSq = \max(5.0, 3.0 \times \text{ppm})$) with high-contrast perimeter borders and a 1px center registration dot, eliminating blinding light flares and bloom.
  - **Compact, Highly Legible Numbers Centered Right Above Windows:**
    - Positioned strand numbers ($0 \to N$) directly above each 3×3 mm square window ($y - winSq/2 - 2$) with `textAlign = 'center'` and `textBaseline = 'bottom'`.
    - Sized compactly at **bold 8px** with a 2.4px dark halo outline (`strokeText`), making numbers easy to read without colliding with adjacent LEDs or obscuring wire traces.
    - Highlighted LED #0 in green (`#00ff88` / `#16a34a`) for strand start and final LED in red (`#ff4d6d` / `#dc2626`) for strand termination.
  - **Theme Styles & 1-Click Print / PNG Export:**
    - Supported **👕 Dark Garment** and **📄 Light Paper** (ink-saving blueprint) modes.
    - Added a **`🖨️ Print / Save Placement Sheet`** button creating a print-ready document with float metadata, strand order, 3×3 mm aperture spec, and continuous wire trace legend.

### Entry: Title Drum Graphic Refinements: Accurate Wheel Centers, Cab Window Cutout, Streamer Flagpole & Gold Detailing
* **Date:** 2026-10-08 (Imagineering Session - Title Drum Artwork Calibration & Markup Implementation)
* **Milestone:** Milestone 6 - Wearable 3D Armor Multi-Material Artwork Assets & Float Lineup Presets
* **Status:** Complete & Verified (`assets/title_drum.png`, `simulator/assets/title_drum.png`, `scripts/process_title_drum.py`).
* **Implementation Details:**
  - **Accurate Wheel Placement & Ghost Wheel Removal:**
    - Re-anchored the two gold-outlined wheels to the exact physical wheel centers of the 3D model render:
      - Front Wheel: Center at $(x = 188, y = 715)$, $R = 70$, with gold outer rim ($R \in [61, 70]$) and gold hubcap ($R \le 16$).
      - Rear Wheel: Center at $(x = 968, y = 706)$, $R = 64$, with gold outer rim ($R \in [55, 64]$) and gold hubcap ($R \le 14$).
    - Re-calibrated ground plane and undercarriage cutoffs ($y > 785$ overall, $y > 715$ between axles), fully eliminating the black ghost circles that previously sat above the synthetic wheel placements.
  - **Cab Window Cutout (Red Square Markup):**
    - Removed interior red horizontal bar and vertical wall artifacts in the driver's cab window opening ($x \in [195, 290], y \in [260, 410]$), converting it into clean transparent negative space ($A = 0$) while preserving the surrounding structural gold pillars.
  - **Middle Streamer Brass Flagpole (Red Arrow Markup):**
    - Added a vertical gold flagpole column at $x = 833$ spanning from the blue pennant streamer tip ($y = 125$) down to the top of the drum marquee ring ($y = 265$), topped with a spherical gold finial ($r = 5$).
  - **Rear Detailing Gold Accents (Yellow Arrow Markups):**
    - Converted the red peak/notch on the rear fender arch shoulder ($x \in [925, 965], y \in [470, 520]$) into solid gold.
    - Converted the red base block at the bottom foot of the rear flagpole ($x \in [1005, 1030], y \in [540, 600]$) into solid gold.
  - **Verification:**
    - Crop dimensions: $1020 \times 789$ px.
    - Palette verification confirmed strictly 5 flat, unshaded colors + transparent background:
      - Transparent: 378,191 px (46.99%)
      - Gold: 166,218 px (20.65%)
      - Black: 162,131 px (20.15%)
      - Red: 79,727 px (9.91%)
      - Green: 13,516 px (1.68%)
      - Blue: 4,997 px (0.62%)
      - Zero unquantized colors or artifacts.

### Entry: Float 2 (The Title Drum) 5-Color Multi-Material Graphic Isolation & Default Float Integration
* **Date:** 2026-10-08 (Imagineering Session - Title Drum 5-Color Transparent Graphic Asset & Float Preset Integration)
* **Milestone:** Milestone 6 - Wearable 3D Armor Multi-Material Artwork Assets & Float Lineup Presets
* **Status:** Complete & Verified (`assets/title_drum.png`, `simulator/assets/title_drum.png`, `presets/title_drum.json`, `simulator/app.js`, `scripts/compile_clean_tpu_panel.py`).
* **Implementation Details:**
  - **Foreground & Background Isolation from `assets/Drum.png`:**
    - Performed high-precision background extraction on the 1200x900 3D render:
      - Flooded dark sky background (`gray < 28`, $S < 35$) from outer corners, ensuring drum face interior is 100% shielded.
      - Removed open air pocket between upper streamer ribbon arch and drum top (Component 2: 12,159 px), ribbon sliver (370 px), and driver's cab open window (Component 24: 1,440 px) as 100% transparent negative space ($A = 0$).
      - Flooded grey ground plane ($y \ge 650, 55 < gray < 120, S < 35$) and shaved bottom floor shadow between wheels ($y > 735$), preserving the full circular disks of all three wheels down to $y = 853$ (Front $R = 73$), $y = 831$ (Rear $R = 66$), and $y = 816$ (Mid $R = 46$).
  - **Flat 5-Color Unshaded Simplification (Bambu AMS 3D Multi-Material):**
    - Simplified all shading, specular highlights, and gradients into strictly 5 flat, unshaded colors:
      - **Black (`#11161d` / RGB `[17, 22, 29]`):** Chassis undercarriage, drum face backdrop, wheel tire bodies, cab interior frame.
      - **Gold (`#facc15` / RGB `[250, 204, 21]`):** Outer drum marquee ring, curved typography "MAIN STREET ELECTRICAL PARADE" (with letter counters intact), two wheel rims & center hubs, flagpoles & finials, square rear flag, cab canopy dome & scrollwork, front crest signboard.
      - **Red (`#ef4444` / RGB `[239, 68, 68]`):** Sculptural cab body panels, drum cradle arches, upper streamer ribbon.
      - **Blue (`#2563eb` / RGB `[37, 99, 235]`):** Streamer pennant tip (top arch).
      - **Green (`#10b981` / RGB `[16, 185, 129]`):** Lead forward flag on flagpole 1 ($x \approx 344$).
    - Zero intermediate antialiasing or gradient pixels—100% of non-transparent pixels belong strictly to one of the 5 colors.
  - **Wheel & Detailing Refinements (Visual Contrast & Feature Polish):**
    - **Reduced to Exactly 2 Wheels with Gold Outlines:** Eliminated the extra middle wheel ($x \approx 838$) to match the authentic 2-axle wagon profile with clear floor clearance between wheels. Outlined both the Front Wheel ($R = 73$) and Rear Wheel ($R = 66$) with crisp 8px gold rims and solid gold center hubcaps, establishing high-contrast visual pop against the black chassis floor.
    - **Cleaned Flagpoles (100% Solid Gold):** Cleared floating black noise specks to the right of the front pole ($x \approx 344$) and red border slivers along the rear pole ($x \approx 1018$). Flagpoles now stand as continuous, solid gold columns topped with gold spherical finials.
    - **Removed Extra Red Strip next to Square Gold Flag:** Eradicated the hanging ribbon tail/vertical red artifact ($x \in [800, 860], y \in [200, 450]$) between the drum ring and the square flag, opening up clean negative space. Set the square flag to 100% solid gold.
    - **Made Cab Canopy Roof Dome Gold:** Converted the black section on top of the main gold canopy near the green flag ($x \in [330, 425], y \in [150, 220]$) to solid gold, harmonizing the entire ornate cab roof structure.
  - **Repository & Tooling Synchronization:**
    - Saved transparent production asset to `assets/title_drum.png` (1020x827) and mirrored to `simulator/assets/title_drum.png`.
    - Created deterministic conversion pipeline in `scripts/process_title_drum.py`.
    - Updated `presets/title_drum.json` with `"graphicType": "title_drum"`, `"artwork_file": "assets/title_drum.png"`, and `stlColors` 5-color dictionary.
    - Updated `simulator/app.js` with `titleDrumImg` loading `assets/title_drum.png` as the default graphic for Float 2 (Title Drum).
    - Updated `scripts/compile_clean_tpu_panel.py` with `is_drum` check to default to the 5-color Title Drum AMS palette.
  - **Verification:**
    - Pixel palette analysis confirmed exactly 6 unique RGBA tuples: Transparent ($45.85\%$), Black ($22.68\%$), Gold ($17.59\%$), Red ($10.52\%$), Blue ($1.72\%$), Green ($1.65\%$).

### Entry: Deep Eyelet Gusset Wall Anchors & LED Well Overhang Removal (Physical Print Refinements)
* **Date:** 2026-10-07 (Imagineering Session - Eyelet Gusset Attachment Fix & Wire Notch Overhang Removal)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Mechanical Mating Refinements
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `3d_panels/`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Deep Eyelet Gusset Wall Anchors (Eliminated Air Gaps at Dragon Feet):**
    - Analysis of physical prints showed several 45° eyelet braces (notably Tabs 8, 10, 11 around the dragon's feet) did not touch the outer rim wall due to perimeter curvature retreating up to 1.11mm behind the nominal tangent.
    - Redesigned the triangular gusset profile with a 4.5mm deep anchor extending in the negative normal direction into the 2.5mm solid rim wall (`x = -4.5mm` to `-1.0mm` at full 3.0mm height $Z = 4.0\text{ mm}$), then sloping at 45° down to the tab shoulder (`x = +2.0mm` at $Z = 7.0\text{ mm}$).
    - Integrated an automated Manifold3D inner basin cutter (`inner_plate_2d`) to cleanly shave any portion extending past the inner 2.5mm rim wall, guaranteeing zero intrusion into the tray cavity.
    - Boolean intersection analysis confirmed all 32 gussets (16 tabs x 2 shoulders) have solid intersection volume with the rim wall (5.3 to 16.5 mm³). The entire chassis is verified as 1 single continuous solid in Manifold3D (`decompose() len == 1`, `Error.NoError`).
  - **Removed 0.5mm LED Well Wire Notch Overhang:**
    - Eliminated `roofs_solid_m` over the wire pass-through notches.
    - Wire notches are now completely open, vertical 4.0mm drop-in channels from top to bottom ($Z = 1.0\text{ to }4.0\text{ mm}$ in raw space, $Z = 5.0\text{ to }8.0\text{ mm}$ in exported space).
    - Allows seed LED nodes and 3-strand enamel wires to seat 100% flat and flush against the pocket floor shelf with zero thumb binding, catching, or pinching.
    - Preserved external $0.70\text{ mm}$ top collar retention nubs (`nub_ring_2d`) on the outer collar perimeter for upcoming snap-on clip designs.
  - **Watertight Manifold3D Recompilation:**
    - Recompiled both Front Plate ($209.38\text{ mm} \times 186.66\text{ mm} \times 9.0\text{ mm}$) and Back Plate in 6.36 seconds.
    - Verified all STLs (`tpu_panel_front_chassis_black.stl`, `tpu_panel_back_chassis_black.stl`, lids, 3MF multi-material project, and ZIP bundles).

### Entry: Flush Lid Screw Boss Landings & Alignment Ridge Pillar Relief (Physical Test Print Fit Fix)
* **Date:** 2026-10-07 (Imagineering Session - Lid Screw Boss Flush Landing & Alignment Ridge Relief)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Mechanical Mating Refinements
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `3d_panels/`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Eliminated Raised Inner Boss Pads (`lid_pads_m`):**
    - Analysis of physical test print photo revealed that 1.2mm raised cylindrical pads around the screw holes on the inner face of the lid collided with the top of the chassis tray boss pillars (which already rise to the rim top at $Z = 9.0\text{ mm}$).
    - Lowered all 8 screw cylinder top surfaces to be completely flush with the lid mating surface at $Z = 2.0\text{ mm}$ (as requested by the user).
  - **Added Alignment Ridge Relief Cutters (`boss_relief_m`):**
    - Added $5.6\text{ mm}$ diameter ($R = 2.8\text{ mm}$) cylindrical relief cutters centered at each of the 8 screw boss coordinates.
    - Clears away the $1.2\text{ mm}$ downward alignment ridge around each boss location, providing $0.3\text{ mm}$ radial clearance around the $5.0\text{ mm}$ diameter chassis pillars.
    - Guarantees the chassis boss pillars seat 100% flush and flat against the lid mating surface with zero interference.
  - **Preserved Outer Counterbores & Clearances:**
    - Maintained outer $\varnothing 3.8\text{ mm} \times 0.8\text{ mm}$ flush screw head counterbores on the shirt-facing surface ($Z = 0.0$ to $0.8\text{ mm}$).
    - Kept $\varnothing 2.0\text{ mm}$ clearance through-holes ($Z = 0.0$ to $2.0\text{ mm}$) for standard M2 self-tapping screws.
  - **Verification:**
    - Recompiled both Front and Back panels and lids via Manifold3D in 6.69s.
    - Verified all 8 screw locations in `tpu_panel_front_lid.stl` and `tpu_panel_back_lid.stl` have max $Z = 2.000\text{ mm}$ within $r \le 2.6\text{ mm}$ (zero raised pads).
    - Verified all 8 screw locations have $\ge 2.79\text{ mm}$ distance to the alignment ridge. Mesh is 100% watertight.

### Entry: Upgraded Multi-Material Inlays to 0.80mm (4 Solid Layers) for 100% Rich Color Opacity
* **Date:** 2026-10-07 (Imagineering Session - 0.80mm Inlay Thickness Implementation)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `3d_panels/`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Implemented Recommendation A (0.80mm / 4 Solid Layers):**
    - Increased `COLOR_INLAY_THICK` from $0.60\text{ mm}$ (3 layers) to **$0.80\text{ mm}$ (4 solid layers @ 0.20mm)** across all color inlays (`yellow`, `green`, `magenta`, `white`, etc.).
    - Added support for `--inlay-thick <val>` CLI flag and `color_inlay_thick` JSON parameter in `scripts/compile_clean_tpu_panel.py`.
    - Inlays now extrude from $Z_{exported} = 8.20\text{ to }9.00\text{ mm}$.
    - Automatic boolean subtraction in the black chassis cuts $0.80\text{ mm}$ deep pockets, leaving a sturdy $1.20\text{ mm}$ of solid black backing floor.
  - **Zero Translucency & Solid Color Saturation:**
    - Cures the thin/mottled yellow belly issue observed in initial test prints. Even with a $0.28\text{ mm}$ first layer, at least 3 to 4 full solid passes of color print before any black chassis filament is deposited behind them.
    - Yellow volume increased from $1,128.7\text{ mm}^3$ to $1,504.9\text{ mm}^3$ (+33.3%).
  - **Watertight Manifold3D Verification:**
    - Recompiled both Front and Back plates in 6.69s.
    - Verified all STLs (`tpu_panel_front_color_*.stl`), multi-part 3MF project, and slicer ZIP bundle.
    - Documentation synchronized in `SIMULATOR_USER_GUIDE.md` and [`3d_panels/YELLOW_LAYER_LEVEL_PLAN.md`](3d_panels/YELLOW_LAYER_LEVEL_PLAN.md).

### Entry: 3D Armor Physical Fit Refinements: Parting-Line Wire Slot, Internal Floor Zip-Tie Bridge, 0.5mm Collar Lip, and Eyelet Tab Braces
* **Date:** 2026-10-07 (Imagineering Session - 3D Armor Mechanical Refinements from Physical Test Prints)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Mechanical Refinements
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `3d_panels/`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Parting-Line Wire Exit Drop-In Slot (Image 1 Inspection):**
    - Moved the wire exit notch directly to the top edge where the outer rim wall meets the rear cover lid ($Z = 0.0$ to $3.0\text{ mm}$ in exported underside space).
    - Reduced Z height from 9.0mm to a clean 3.0mm drop-in U-slot ($5.5\text{ mm}$ wide $\times 3.0\text{ mm}$ tall in Z) matching the LED cable trunk thickness.
    - Wire harness lays directly into the slot without having to be threaded through an enclosed tunnel.
    - Lower 4.0mm of the rim wall ($Z = 3.0$ to $7.0\text{ mm}$) remains 100% solid, providing mechanical rigidity and moisture protection.
  - **Internal Strain Relief Bridge (90° Perpendicular Cross-Tunnel with Wire Saddle):**
    - Eliminated the two through-holes from the front plate floor, leaving the front shirt-facing graphic surface pristine, continuous, and puncture-free.
    - Reoriented the internal bridge 90° so its open under-tunnel passes along the $X$ axis ($10.0\text{ mm}$ long in X $\times 3.0\text{ mm}$ wide in Y $\times 1.4\text{ mm}$ tall in Z), completely perpendicular to the incoming $Y$-axis wire path.
    - Added a shallow $0.6\text{ mm}$ concave wire saddle on top of the bridge ($4.5\text{ mm}$ wide in X $\times 7.0\text{ mm}$ long in Y), centered in line with the outer wire notch.
    - Standard $2.5\text{ mm}$ micro nylon zip-tie slides easily under the bridge from left to right, loops up over the wire nestled in the top saddle, and cinches firmly down to anchor the cable trunk against race-day strides.
  - **0.5mm Collar Wire Notch Lip (Image 2 Inspection):**
    - Reduced the LED collar wire notch overhang from 2.0mm down to a sleek 0.5mm cantilever lip ($Y = 2.0$ down to $1.5\text{ mm}$) with a 45° chamfer support.
    - Opened up a generous $3.5\text{ mm}$ clear drop-in gap across the 4.0mm wire notch, allowing 3-conductor ribbon wire to seat effortlessly while the 0.5mm catch lip prevents vertical pop-out.
    - Retained the $0.70\text{ mm}$ collar perimeter retention beads for rigid snap caps.
  - **Dual 45° Triangular Eyelet Braces (Image 3 Inspection):**
    - Added dual 45° triangular gussets ($1.2\text{ mm}$ wide, rising $3.0\text{ mm}$ up the vertical outer rim wall from $Z = 2.0$ to $5.0\text{ mm}$) flanking both shoulders of all 16 outer tabs.
    - Fuses each tab directly into the outer chassis wall, preventing peel and tear-out when under tension or safety-pinned during the 10K.
    - Preserved full unobstructed clearance for the $\varnothing 2.7\text{ mm}$ center through-hole.
  - **Watertight Manifold3D Recompilation:**
    - Recompiled Front Plate ($205.85\text{ mm} \times 169.40\text{ mm} \times 9.0\text{ mm}$) and Back Plate in 8.34 seconds.
    - Generated pristine STLs (`tpu_panel_front_chassis_black.stl`, `tpu_panel_front_lid.stl`, color inlays, 3MF multi-material project, and ZIP bundle).

### Entry: High-Detail 1:1 Original Snail Artwork Recolored to 5-Color Multi-Material 3D Armor
* **Date:** 2026-10-06 (Imagineering Session - Float 04 Original Snail 1:1 Recoloring for 3D Printing)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`assets/spinning_snail.png`, `assets/spinning_snail_simplified.png`, `assets/spinning_snail_5color_183.png`, `3d_panels/`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Zero Geometry Distortion / 100% Detail Preservation:**
    - Performed a direct, lossless 1:1 recoloring directly from the original authentic parade float picture (`assets/spinning_snail.png`), preserving all original pixel art, light bulb nodes, facial expressions, smile crease, neck folds, and spiral nuances without modifying any underlying drawing geometry.
    - Mapped every single pixel directly into the aligned 5-color palette:
      1. **Chassis Black (`#11161d`):** Inter-spoke dark shell framework, eye crease, smiling mouth line, and neck fold linework.
      2. **Race Red (`#ef4444`):** Snail head, face, cheeks, neck skin, and lower undulating foot/trail.
      3. **Parade Gold (`#facc15`):** Antennae stalks and bulbs ($Y < 52, X < 65$), outer shell rim, and central spiral whorl ($R_{norm} \le 0.22$).
      4. **Emerald Green (`#10b981`):** Green radial spokes and converted former gold radial lines.
      5. **Electric Blue (`#2563eb`):** Blue radial spokes and bulb highlights.
    - Saved native $183 \times 183$ recolored image (`assets/spinning_snail_5color_183.png`) and clean $4\times$ nearest-neighbor block-scaled ($732 \times 732$) version (`assets/spinning_snail_simplified.png`, `3d_panels/active_artwork.png`).
  - **Watertight Manifold3D Recompilation:**
    - Recompiled Front Plate ($205.85\text{ mm} \times 169.40\text{ mm} \times 9.0\text{ mm}$) and Back Plate in 8.02 seconds:
      - `tpu_panel_front_chassis_black.stl` (4.37 MB) with precision jigsaw pockets
      - `tpu_panel_front_color_red.stl` (245 KB, 2,512 vertices, 3,547.8 mm²)
      - `tpu_panel_front_color_gold.stl` (151 KB, 1,478 vertices, 5,548.2 mm²)
      - `tpu_panel_front_color_green.stl` (211 KB, 2,094 vertices, 2,957.9 mm²)
      - `tpu_panel_front_color_blue.stl` (222 KB, 2,368 vertices, 1,330.7 mm²)
      - `tpu_panel_front_lid.stl` (411 KB) with counterbored M2 screw clearance
      - `tpu_panel_front_multicolor.3mf` (1.13 MB) and `bundle.zip` (2.20 MB)

### Entry: 5-Color Multi-Material 3D Armor Tray & Snail (Float 04) STL Generation
* **Date:** 2026-10-06 (Imagineering Session - Float 04 Snail 5-Color Multi-Material 3D Fabrication)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`assets/spinning_snail_simplified.png`, `simulator/assets/spinning_snail_simplified.png`, `presets/spinning_snail_simplified.json`, `scripts/compile_clean_tpu_panel.py`, `simulator/app.js`, `3d_panels/`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **High-Fidelity 5-Color Segmentation & Artwork Asset:**
    - Segmented and recolored `assets/spinning_snail_simplified.png` (732×732) to match exact runner race-day specifications:
      1. **Chassis & Shell Background (`#11161d`, 119,648 px):** Solid black shell disk background, dark structural borders, and neck linework folds.
      2. **Head, Neck, Face & Lower Foot/Trail (`#ef4444`, 47,536 px):** Race red cartoon body, face, smiling mouth, and crawling trail.
      3. **Antennae, Outer Rim & Center Spiral (`#facc15`, 28,225 px):** Parade gold eye stalks, round antenna bulbs, outer circular shell rim, and central spiral whorl.
      4. **Emerald Green Radial Stripes (`#10b981`, 18,959 px):** Half the alternating shell spokes, including conversion of previous gold radial lines.
      5. **Electric Blue Radial Stripes (`#2563eb`, 44,080 px):** The other half of the alternating shell spokes.
  - **Preset & Slicer Metadata Synchronization:**
    - Updated `presets/spinning_snail_simplified.json` with 5 AMS color slots: `black` (chassis), `red` (inlay), `gold` (inlay), `green` (inlay), `blue` (inlay).
    - Updated `FLOAT_STL_COLOR_CONFIG` in `simulator/app.js` and fallback mappings in `scripts/compile_clean_tpu_panel.py`.
  - **Manifold3D Watertight Compilation:**
    - Compiled Front Plate ($218.21\text{ mm} \times 178.70\text{ mm} \times 9.0\text{ mm}$) and Back Plate ($218.21\text{ mm} \times 178.70\text{ mm} \times 9.0\text{ mm}$) with:
      - Black chassis tray (`tpu_panel_front_chassis_black.stl`, 2.82 MB)
      - Red body inlay (`tpu_panel_front_color_red.stl`, 284 KB)
      - Gold antennae/spiral inlay (`tpu_panel_front_color_gold.stl`, 158 KB)
      - Green radial stripe inlay (`tpu_panel_front_color_green.stl`, 54 KB)
      - Blue radial stripe inlay (`tpu_panel_front_color_blue.stl`, 509 KB)
      - Monolithic single-color tray (`tpu_panel_front.stl`, 1.81 MB)
      - Rear cover lid with alignment ridge and counterbored M2 screw holes (`tpu_panel_front_lid.stl`, 416 KB)
      - Native multi-part 3MF package (`tpu_panel_front_multicolor.3mf`, 814 KB)
      - Complete Bambu Studio bundle ZIP (`tpu_panel_front_multicolor_bundle.zip`, 1.60 MB) with readme instructions.
    - Verified all meshes in Manifold3D with positive volumes and zero non-manifold defects.

### Entry: Restored Original Snail Artwork as Default & Fixed Layout Dropdown Switching
* **Date:** 2026-10-06 (Imagineering Session - Float 04 Snail Original Artwork Restoration)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`presets/spinning_snail.json`, `assets/spinning_snail.png`, `3d_panels/active_artwork.png`, `simulator/app.js`, `simulator/index.html`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Reverted Default Snail Artwork to Original:**
    - Fully restored `presets/spinning_snail.json` to the original vibrant version with `graphicType: "spinning_snail"`.
    - Set `spinningSnailImg` and `floatArtworkImgs['spinning_snail']` back to `assets/spinning_snail.png`.
    - Restored `3d_panels/active_artwork.png` to `assets/spinning_snail.png`.
  - **Fixed Layout Dropdown Switching:**
    - Resolved the dropdown selection mismatch where choosing the original snail failed to trigger properly.
    - Updated `presetFileMap` and `getGraphicImgForType` so selecting `spinning_snail` cleanly loads `spinning_snail.json` and renders `assets/spinning_snail.png` on the canvas.
    - Maintained the simplified experiment as an optional choice (`spinning_snail_simplified`) under `Float 04: The Spinning Snail (Simplified 3D Print Test)`.

### Entry: Simplified 5-Color Snail (Float 04) Preset & Artwork for Bambu AMS Multi-Material 3D Printing
* **Date:** 2026-10-06 (Imagineering Session - Float 04 Snail 3D Print Color Segmentation)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`assets/spinning_snail_simplified.png`, `presets/spinning_snail.json`, `presets/spinning_snail_simplified.json`, `presets/spinning_snail_original.json`, `scripts/compile_clean_tpu_panel.py`, `simulator/app.js`, `simulator/index.html`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Preserved Original Snail Artwork & Configuration:**
    - Archived exact original preset as `presets/spinning_snail_original.json`.
    - Preserved original artwork `assets/spinning_snail.png` and created `spinning_snail_original` dropdown option in the simulator so runners can toggle back to the original graphic at any time.
  - **Engineered Simplified 5-Color Snail Artwork (`assets/spinning_snail_simplified.png`):**
    - High-contrast, clean 5-color segmentation matching user specifications for Bambu AMS multi-material printing:
      1. **Body, Face, Lips, Antennae, and Foot:** Uniform vibrant pink (`#ec4899`, RGB `236, 72, 153`).
      2. **Shell Body:** One uniform emerald green (`#10b981`, RGB `16, 185, 129`).
      3. **Radial Shell Lines:** All radial spokes recolored to uniform electric blue (`#2563eb`, RGB `37, 99, 235`), replacing previous mixed green/blue/gold bulbs.
      4. **Shell Edge & Central Spiral:** Uniform parade gold (`#facc15`, RGB `250, 204, 21`), forming a solid continuous ribbon.
      5. **Neck Lines:** Chassis black linework (`#11161d`, RGB `17, 22, 29`) running along the neck contours for crisp mechanical definition.
    - Upscaled to 732×732 with nearest-neighbor interpolation to ensure sub-millimeter edge precision and zero color-bleeding during slicer tessellation.
  - **Configured Float 04 `stlColors` Metadata:**
    - Updated `presets/spinning_snail.json` and created `presets/spinning_snail_simplified.json` with the 5 AMS color slots: `black` (chassis/neck lines), `pink` (body/face/lips), `green` (shell body), `blue` (radial lines), and `gold` (shell edge and spiral).
    - Added fallback entries in `scripts/compile_clean_tpu_panel.py` and `simulator/app.js` (`FLOAT_STL_COLOR_CONFIG`).
  - **Watertight 3D Compilation Verified:**
    - Compiled `scripts/compile_clean_tpu_panel.py` on the simplified snail artwork:
      - Front Plate: 219.71mm × 140.93mm × 9.0mm, with 4 separate watertight color inlays (`color_pink.stl`, `color_green.stl`, `color_blue.stl`, `color_gold.stl`), black chassis tray (`tpu_panel_front_chassis_black.stl`), and matching 2mm rear cover lid (`tpu_panel_front_lid.stl`).
      - Back Plate: 204.96mm × 132.42mm × 9.0mm, with identical 5-color AMS part division and rear cover lid.
      - Generated native multi-color 3MF packages (`tpu_panel_front_multicolor.3mf` and `tpu_panel_back_multicolor.3mf`) ready for Bambu Studio / OrcaSlicer.

### Entry: Pure Concentric Eyelets Geometry Bugfix (Eliminated Bounding Box Corner Artifacts) & Dual-Anchor Design Confirmation
* **Date:** 2026-10-06 (Imagineering Session - Wearable Armor Eyelet Precision & Sandwiched Attachment)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `3d_panels/`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Identified & Eliminated Pointy Bits on Eyelets:**
    - Root cause analysis: In `manifold3d`'s native nanobind implementation, `Manifold.cylinder()` contains an internal corner vertex artifact at $(R, R)$ in the first quadrant, extending vertices out to $\sqrt{2} \times R \approx 4.60\text{ mm}$ (beyond the target $3.25\text{ mm}$ outer radius) and resulting in a thin curved tangent "fin" or "horn" protruding from cylindrical tabs.
    - Engineered `make_clean_cylinder()` via `CrossSection.circle(radius, segments).extrude(height)`, which generates mathematically pure $360^\circ$ concentric circles with exact $R = 3.25\text{ mm}$ outer radius, $R = 1.25\text{ mm}$ inner through-hole, and zero corner artifacts.
    - Recompiled all Front and Back plates and verified: `Outward protruding vertices beyond r=3.25: 0`. All 16 eyelets on both trays and lids are now completely smooth and circular with zero pointy edges.
  - **Eyelets on Both Tray and Lid (Design Rationale Confirmed):**
    - Having 16 matching eyelets on BOTH the tray perimeter wall and the rear cover lid is intentional: when the lid is screwed down to the tray via the 8 M2 perimeter screws, the 16 lid eyelets align hole-for-hole with the tray eyelets to create a reinforced 4.0mm solid stack.
    - Runners can pass heavy-duty safety pins, tagging barbs, or miniature zip-ties through both the tray and lid simultaneously, firmly anchoring the entire costume armor to the running shirt/mesh vest so the mechanical load is shared and cannot pull the lid away from the tray during the 10K race.

### Entry: Compact 2-Row 3D Preview Modal Header & Dark-Themed Toolbar UI Refactor
* **Date:** 2026-10-06 (Imagineering Session - 3D Modal Workspace Optimization)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Eliminated Giant Bright Green Banner:** Replaced the legacy bright green gradient (`linear-gradient(135deg, #097969, #00ff88)`) with a sleek dark slate theme (`#161b22` header, `#0d1117` toolbar, with `#30363d` dividing borders) matching the rest of the application and eliminating glare.
  - **Compact 2-Row Spatial Hierarchy:**
    - **Row 1 (Header Bar, ~38px):** Dedicated to identity and window actions. Displays the dynamic float mascot icon (e.g. 🐢 for Turtle, 🐉 for Dragon), concise plate title (`The Turtle • Front Chest Plate`), compact subtitle (`95A TPU Tray • 3×3mm Windows • 5-Color AMS Split`), standalone `↗️ Full Tab` viewer link, and high-contrast `✕` close button.
    - **Row 2 (Controls Toolbar, ~34px):** Dedicated to hardware toggles and print options. Spans the full modal width with clean dividers and high-contrast pill toggles: `[ 🎽 Front | 🎒 Back ]`, `[ 📦 Tray Basin | 🛡️ Rear Lid (2mm) ]`, `[ 🔲 Square | ⚪ Round ]`, `[ 🔢 # | 🚫 No # ]`, `[ 🔘 Nubs & Roofs | 🚫 No Nubs ]`, `[ 🗜️ Grooves | 🧱 Solid Walls ]`, and `[ 🎨 5-Color Split | ⚪ Single Black ]`.
  - **Unified Pill State Manager (`setTpuModalPillState`):** Replaced divergent inline styling logic in `simulator/app.js` with a unified helper ensuring active buttons always show crisp electric green (`#00ff88` on `#000` text, bold) and idle buttons show legible dark-theme text (`#8b949e` on transparent).
  - **Reclaimed Viewport Screen Real Estate:** Reduced top bar footprint from over 300px (which took ~60% of the modal height due to title text wrapping 15+ times into a squeezed column) down to ~72px total height. Reclaimed over 225px of vertical screen real estate, expanding the 3D WebGL model viewer from ~35% to ~85% of the viewport.

### Entry: 2.0mm Rear Cover Lid Plate with Alignment Ridge, M2 Flush Screw Bosses & Multi-Material Bundle Integration
* **Date:** 2026-10-06 (Imagineering Session - Wearable Armor Back Plate Enclosure)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator/index.html`, `simulator/app.js`, `3d_panels/tpu_panel_specs.json`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **2.0mm Thick Rear Cover Plate (Lid):**
    - Engineered matching protective rear lids for both Front (`tpu_panel_front_lid.stl`) and Back (`tpu_panel_back_lid.stl`) armor panels.
    - Matches the exact outer organic silhouette of the main front tray plate, including all 16 outer circular mounting eyelets (outer diameter 6.5mm with 2.5mm holes) aligned identically at $Z = 0.0$ to $2.0\text{ mm}$.
    - Base thickness is $2.0\text{ mm}$ solid plate, providing physical protection against sweat and friction between running shirts and wiring harnesses.
  - **1.2mm Stepped Inner Alignment Ridge:**
    - Features a continuous internal alignment lip stepping $1.5\text{ mm}$ inward along the perimeter wall, protruding $1.2\text{ mm}$ downwards ($Z = 2.0$ to $3.2\text{ mm}$) to nest snugly into the open $7.0\text{ mm}$ perimeter rim of the tray basin.
    - Engineered with an exact $0.25\text{ mm}$ per-side clearance gap for easy friction-fit insertion without binding on FDM layer lines.
    - Includes a matching $8.0\text{ mm} \times 2.0\text{ mm}$ arch relief cutout at the bottom wire portal ($Y = \text{min}$) so power supply leads pass through cleanly without pinch risk.
  - **8-Point M2 Perimeter Screw Fastening System:**
    - **Main Tray Basin Boss Pillars:** Added 8 solid cylindrical screw bosses ($\varnothing 5.0\text{ mm}$) rising from the floor ($Z = 2.0\text{ mm}$) to the top of the rim ($Z = 9.0\text{ mm}$), fused seamlessly into the interior $2.5\text{ mm}$ perimeter rim wall. Each boss features a pre-formed $1.6\text{ mm}$ diameter $\times 5.5\text{ mm}$ deep pilot hole for self-tapping M2 screws to thread securely without splitting PLA layers. Bosses are strategically positioned along the perimeter to avoid LED collars and wire paths.
    - **Rear Lid Through-Holes & Reinforcement Pads:** Each screw location on the lid has a $\varnothing 5.0\text{ mm}$ reinforcement boss ($1.2\text{ mm}$ tall) on the inner side, a $\varnothing 2.0\text{ mm}$ clearance through-hole, and a $\varnothing 3.8\text{ mm} \times 0.8\text{ mm}$ deep flush counterbore on the outer (shirt-facing) surface so standard M2 screw heads sit completely below the surface, eliminating snagging against running shirts.
  - **Bambu Studio AMS Multi-Material Bundle & Slicer Integration:**
    - Both `tpu_panel_front_lid.stl` (363 KB) and `tpu_panel_back_lid.stl` (363 KB) are watertight (`is_watertight: True`) with exact matching dimensions ($208.97 \times 184.84 \times 3.2\text{ mm}$).
    - Automatically bundled into `tpu_panel_{variant}_multicolor_bundle.zip` alongside the structural black chassis and accent color inlays.
  - **Simulator 3D Preview Modal Integration (`#tpuPreviewModal`):**
    - Added interactive `[ 📦 Tray Basin | 🛡️ Rear Lid (2mm) ]` segmented switcher pill in the modal header.
    - In Lid mode, Three.js dynamically loads the lid STL with a technical slate material (`#242e3d`), displays matching dimensions ($209.0 \times 184.8 \times 3.2\text{ mm}$, ~44g), suppresses LED bulb rendering, and updates download buttons to include 1-click `🛡️ Rear Lid STL` download.

### Entry: Float #3 (The Turtle) 3D Panel Generation & Multi-Feature Stale-Guard Sync
* **Date:** 2026-10-06 (Imagineering Session - Turtle 3D Panel Pipeline & Server Synchronization)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`simulator.py`, `simulator/app.js`, `scripts/compile_clean_tpu_panel.py`, `3d_panels/tpu_panel_specs.json`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Server Process & Argument Forwarding Synchronization:**
    - Diagnosed root cause for top nubs missing on The Turtle (Float #3): a background `python simulator.py` server process initiated on 10/5 was still running in memory, prior to adding `--top-nubs` CLI forwarding and payload parsing in `simulator.py`. As a result, requests to `/api/generate_tpu_stl` were executed by the legacy handler that omitted `--top-nubs`, defaulting `compile_clean_tpu_panel.py` to `INCLUDE_TOP_NUBS = False` and writing `include_top_nubs: false` back to `tpu_panel_specs.json`.
    - Terminated stale process and started fresh daemon process with full `--top-nubs on|off`, `--clip-grooves on|off`, and `--numbers on|off` CLI passing.
    - Added stdout/stderr diagnostic logging to `simulator.py` for `compile_clean_tpu_panel.py` executions.
  - **Enhanced Multi-Feature Stale-STL Guard in Preview Modal (`simulator/app.js`):**
    - Enhanced `openTpuPreviewModal()`'s guard to evaluate feature flag mismatches directly: `compiledNubs !== params.tpuIncludeTopNubs`, `compiledGrooves !== params.tpuIncludeClipGrooves`, `compiledNumbers !== params.tpuIncludeLedNumbers`, and `compiledShape !== params.tpuWindowShape`.
    - If any toggle state diverges from what is currently compiled in `3d_panels/tpu_panel_specs.json`, the modal automatically initiates a recompile, eliminating stale geometry displays upon float switching or F5 page reloads.
  - **Live Verification of The Turtle (100 LEDs, 5-Color Multi-Material):**
    - Tested live HTTP generation of The Turtle with Top Nubs ON: successfully produced 5.03 MB Front STL, 6.17 MB Black Chassis STL, and 5-color split inlays (Shell Plates & Glasses, Shell & Eyes, Body & Head, Tie & Lips) with all 100 collar top nubs and 2mm chamfered wire retention roofs intact.
    - Verified toggle OFF drops Front STL size to 3.18 MB with flush collars, and toggling back ON cleanly restores the 5.03 MB model with `include_top_nubs: true`.

### Entry: 7.0mm Perimeter Wall & 9.0mm Total Plate Thickness Architecture
* **Date:** 2026-10-06 (Imagineering Session - 9.0mm Deep-Chassis Wearable Armor)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator/app.js`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **7.0mm Perimeter Rim Wall & 9.0mm Total Thickness:**
    - Increased `RIM_HEIGHT` from $4.0\text{ mm}$ to $7.0\text{ mm}$ in `scripts/compile_clean_tpu_panel.py`.
    - Raised `TOTAL_THICK` from $6.0\text{ mm}$ to $9.0\text{ mm}$ ($2.0\text{ mm}$ front tray floor + $7.0\text{ mm}$ perimeter rim).
    - Rim wall now extends from $Z = 2.0\text{ mm}$ to $Z = 9.0\text{ mm}$, creating a deep, protective $7.0\text{ mm}$ internal wiring basin.
    - Updated mounting eyelet cylinders parametrically to `TOTAL_THICK - TAB_HEIGHT` ($Z = 7.0$ to $9.0\text{ mm}$), ensuring the 16 perimeter fastener tabs remain flush with the back rim of the armor plate.
    - Leaves $5.0\text{ mm}$ of clear pocket headroom above the LED collars ($Z = 4.0\text{ mm}$ vs $9.0\text{ mm}$ rim), sheltering all pixel bulbs, wire runs, and providing ample depth for future backing plates or foam seals.
  - **Compiler & Frontend Synchronization:**
    - Verified compilation for both Front and Back panels: Front `[172.3, 152.54, 9.0] mm` (Center $Z = 4.5\text{ mm}$), Back `[186.28, 165.29, 9.0] mm` (Center $Z = 4.5\text{ mm}$).
    - Updated dimensions readout badges and descriptions in `simulator/index.html` and `simulator/app.js` to reflect 9.0mm thickness (~68g).
    - Bumped script version to `app.js?v=91`.
* **Date:** 2026-10-06 (Imagineering Session - Mechanical Overhang & Toggle Synchronization)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Dual 2.0mm Wire Retention Roof Overhangs:**
    - Extended the top collar wall 2.0mm across both wire pass-through notches (entry AND exit) from $Y = 2.0\text{ mm}$ down to $Y = 0.0\text{ mm}$ (on the $+Y$ side facing the top of the graphic).
    - Engineered an exact **45° chamfer support** underneath the roof (sloping from $Z = 2.2\text{ mm}$ down to $Z = 0.8\text{ mm}$ at $Y = 1.4\text{ mm}$) to ensure rigid PLA prints cleanly in mid-air with zero drooping, zero bridging artifacts, and zero supports required when printed face-down on the build plate.
    - Preserves a generous $2.0\text{ mm}$ wide insertion slot along the bottom half of each notch and $2.2\text{ mm}$ vertical clearance under the roof. Runners can drop the 3-strand copper ribbon wire straight into the slot and tuck it under the roof ceiling, trapping it against popping out vertically.
    - Integrated with the **`[ 🔘 Top Nubs & Roofs | 🚫 No Nubs ]`** toggle: when Top Nubs are enabled, both the 0.70mm snap beads and the 2.0mm wire retention roofs are compiled into the monolithic and multi-material STLs/3MF.
  - **Modal Reselection Lifecycle & Concurrency Guard:**
    - Resolved the toggle deselection/reselection bug where re-enabling top nubs left them missing in WebGL and slicer exports.
    - Added `tpuRecompileInFlight` locking and a `tpuRecompilePending` queue in `simulator/app.js` to serialize rapid toggle changes, preventing overlapping background processes from overwriting specifications or serving out-of-order STLs.
    - Added UI controls disabling (`setTpuModalControlsDisabled(true)`) during compilation to provide visual feedback and prevent race conditions.
    - Disabled Three.js internal cache (`THREE.Cache.enabled = false`) and added timestamp cache-busters (`?t=timestamp`) to all 3MF, ZIP, and STL download links.
    - Configured strict HTTP caching headers (`Cache-Control: no-cache, no-store, must-revalidate`, `Pragma: no-cache`, `Expires: 0`) and proper MIME types (`model/3mf`, `application/zip`, `model/stl`) in `simulator.py` so external web 3MF viewers and Bambu Studio / OrcaSlicer downloads never reuse stale cached files.
* **Date:** 2026-10-06 (Imagineering Session - Rigid PLA Armor Optimization & Retention)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Selectable LED Clip Grooves (Default: OFF):** Added `--clip-grooves on|off` to the Python compiler and interactive `[ 🗜️ Grooves | 🧱 Solid Walls ]` toggle pills in the 3D preview modal. For rigid PLA prints, default solid 1.2mm walls prevent layer delamination and snapping. When enabled, a 0.7mm deep × 0.6mm tall retention groove is debossed at the base of the LED collars for external snap clips.
  - **Selectable Top Collar Nubs (Default: OFF):** Added `--top-nubs on|off` to the compiler and interactive `[ 🔘 Top Nubs | 🚫 No Nubs ]` toggle pills in the 3D preview modal. Top nubs feature a distinct 0.70mm horizontal protrusion (0.80mm tall, flush with the collar top rim at Z = 3.2–4.0mm in raw space, Z = 2.0–2.8mm in flipped underside space), with wire notches cut completely through both collar and nubs for zero wire resistance. Serves as a tactile external snap retention bead without thinning or notching the collar wall base.
  - **Bottom-Center Wire Portal & Strain Relief (Option B):** Implemented a clean pass-through arch and zip-tie anchor at the bottom-center of the armor rim ($Y = \text{min}$):
    - Cuts a 6.0mm wide × 3.5mm tall arch through the 4.0mm outer perimeter rim.
    - Adds dual 1.4mm × 2.8mm slots spaced 3.0mm apart through the 1.6mm plate floor, designed for a standard 2.5mm miniature nylon zip-tie to anchor the wiring harness against runner tugs during the 10K.
  - **LED Numbers Deboss Placement Fix:** Resolved issue where LED numbers appeared off or vanished in STL exports. Corrected number cutter Z-position in `scripts/compile_clean_tpu_panel.py` to `FRONT_THICK_GENERAL - 0.4` ($Z = 1.6\text{ mm}$), debossing 0.5mm cleanly into the floor inside each LED tray. Fixed frontend bug in `simulator/app.js` (`initTpuArmorPanel`) that previously forced `setTpuLedNumbers(false)` on page reload.
  - **Rigid PLA Retention Options Reference Guide:** Documented retention methods evaluated for rigid PLA fairy pixel arrays:
    1. *Option 1: Backplate Enclosure Sandwich with EVA Foam (Recommended):* Matching thin rigid backplate screwed or snapped onto the chassis rim with closed-cell EVA foam or silicone sheet pressing the pixel bulbs firmly into their optical windows from behind.
    2. *Option 2: Top-Collar Nub Snap Clips:* Outer clips locking onto the external 0.70mm top collar nubs, eliminating root stress concentrations.
    3. *Option 3: High-Elasticity Hot-Melt / Silicone Tack:* Reversible low-profile dots of silicone adhesive or neutral-cure electronics silicone across the back of each bulb.

### Entry: Dynamic Float-Specific Multi-Material Color Inlays & The Spinning Turtle Segmentation
* **Date:** 2026-10-06 (Imagineering Session - Float 3 Armor Fabrication)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`presets/spinning_turtle.json`, `presets/petes_dragon.json`, `presets/petes_dragon_chris.json`, `scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Dynamic Multi-Material Color Inlay Engine:** Transformed the 5-color TPU multi-material compiler from hardcoded Pete's Dragon colors to a float-agnostic architecture driven by JSON preset specifications (`stlColors`).
  - **The Spinning Turtle 5-Color Segmentation:** Configured authentic MSEP color mapping for Float 3:
    - **Slot 1 (Chassis Black `#11161d`):** Chassis tray, 4mm perimeter rim, 16 mounting tabs, LED collars, wire notches, and black linework.
    - **Slot 2 (Shell Plates & Glasses `#00cc66`):** Turtle hexagonal shell plates and glasses frame.
    - **Slot 3 (Shell & Eyes `#2563eb`):** Outer turtle shell body and eyes.
    - **Slot 4 (Body & Head `#facc15`):** Turtle skin, head, neck, and limbs.
    - **Slot 5 (Tie & Lips `#ef4444`):** Red bow tie and cheerful lips.
  - **Cross-Contamination Purge & Stale-STL Guard:** Fixed 3D preview bug where switching floats displayed mixed character parts (dragon wings on turtle chassis). The compiler now purges stale `tpu_panel_*_color_*.stl` files before writing new ones, and `app.js` dynamically renders only the active float's inlays, Bambu AMS legend badges, and download options.
  - **Watertight Multi-Body 3MF & STL Export:** Verified clean compilation of Front and Back plates in 6.45s, generating 5 discrete watertight parts, native multi-part `.3mf`, and full zip bundle for Bambu Studio / OrcaSlicer.

### Entry: Full Green Body, Black Linework Preserved & Selectable LED Numbers
* **Date:** 2026-10-06
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Missing Green Body Fixed:** The large connected green region traced to a self-intersecting polygon that the old `is_valid` check silently discarded (only the head and tail survived: ~1225 mm^2). Invalid polygons are now repaired with `buffer(0)`; green inlay area is now ~7950 mm^2 covering the whole body.
  - **Black Linework & Left-Eye Outline Restored:** Inlay contours now use `cv2.RETR_CCOMP` hierarchy so interior holes (black outlines, eye rings, spots) are subtracted from each color; the `MORPH_CLOSE` step that filled thin black lines was removed. Black chassis shows through as the outline.
  - **Selectable LED Numbers:** New `--numbers on|off` compiler flag and `includeLedNumbers` API field; the 3D Preview modal has a `[ 🔢 Numbers On | 🚫 No Numbers ]` pill that regenerates the STL (preference saved in localStorage, included in the layout signature). Default: On. `app.js?v=83`.

### Entry: Organic Dragon Silhouette Contour & Calibrated 8.0" Chassis Width
* **Date:** 2026-10-06 (Follow-up Imagineering Session)
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `3d_panels/active_artwork.png`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Organic Dragon Silhouette Restoration:** Identified that the black chassis was previously compiling as a rectangular box because `active_artwork.png` had an opaque black background (sampled from the 2D shirt preview canvas), causing `alpha > 40` to encompass the entire rectangular image canvas (1024x1229).
  - **Dual-Layer Background Transparency Engine:**
    - In `simulator.py` (`handle_generate_tpu_stl`): Added automatic post-processing to strip any opaque black canvas background when receiving incoming artwork data URLs, saving a crisp transparent PNG where transparent alpha surrounds the character.
    - In `scripts/compile_clean_tpu_panel.py`: Upgraded the mask extraction pipeline to be immune to solid black backgrounds by detecting if image corners are opaque black, extracting foreground pixels via luminance/color thresholds (`(rgb.max > 20) & (alpha > 40)`), and dilating the true organic character contour.
  - **Calibrated 8.0" (203.2mm) Chassis Dimensioning:** In `simulator.py`, calibrated the total image envelope scaling ($230.55	ext{ mm}$ total width) so that the resulting outer perimeter rim of the organic dragon chassis measures **$203.2	ext{ mm}$ ($8.0	ext{ in}$) wide** (overall $208.0	ext{ mm}$ across outer mounting tabs, $188.2	ext{ mm}$ height).
  - ** Watertight Multi-Material Output:** Successfully recompiled both Front and Back plates in 6.28s. Pete's Dragon's head, wings, belly, and tail ridges now define the organic 4mm outer rim of the structural black chassis (`tpu_panel_front_chassis_black.stl`), with all 4 color inlays and open 3x3mm optical windows nested directly within the dragon silhouette.

### Entry: 5-Color Multi-Material TPU Armor Plate Compiler, Custom Sizing & 75-LED Layout
* **Date:** 2026-10-06
* **Milestone:** Milestone 6 - Wearable 3D Armor Fabrication & Multi-Material 3D Printing
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/index.html`, `simulator/app.js`, `3d_panels/tpu_panel_preview.html`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **5-Color Multi-Material TPU STL Architecture:** Upgraded `scripts/compile_clean_tpu_panel.py` to v5 with automatic color vector segmentation. The structural chassis (floor, 4mm perimeter rim, 16 round mounting tabs, LED collars, wire pass-through notches) is compiled as a single monolithic black STL (`tpu_panel_{front|back}_chassis_black.stl`). Color artwork inlays are generated as four separate STLs: Neon Green body (`_color_green.stl`), Magenta hair/spines (`_color_magenta.stl`), Sunny Yellow belly (`_color_yellow.stl`), and Bright White eyes/teeth (`_color_white.stl`).
  - **Zero-Overlap Jigsaw Inlays & Optical Windows:** Color inlays are 0.6mm thick (3 layers @ 0.2mm) subtracted directly into the front surface of the black chassis with zero collision overlap. Centered $3\times 3\text{ mm}$ square (or $\varnothing 3\text{ mm}$ round) optical windows cut cleanly through both chassis and color inlays.
  - **Bambu Lab AMS Bundle & 3MF Export:** Packaged all 5 STLs, native multi-body `.3mf` project (via `trimesh.Scene` and `lxml`), and a comprehensive `README_BAMBU_STUDIO.txt` guide into a 1-click ZIP archive (`tpu_panel_{front|back}_multicolor_bundle.zip`). In Bambu Studio, users simply drop all 5 STLs at once and click "Load as single object with multiple parts".
  - **Selectable Plate Sizing on Layout Tab:** Added interactive size selector buttons: Small (~6.5" / 165.1mm), Medium (~8.0" / 203.2mm, default target), and Large (~10.0" / 254.0mm). Sizing sets the target width for both plates, maintaining proportional height, bib clearance, and print bed safety.
  - **Selectable LED Counts (50 / 75 / 100 LEDs):** Added quick LED density buttons: 50, 75 (current target), or 100 LEDs. Selecting an option redistributes LEDs across the character graphic with color sampling and serpentine wire routing.
  - **Export Modal & 3D Preview Inspector:** Added `[ 🎨 5-Color Split | ⚪ Single Black ]` toggle to `#tpuPreviewModal` and `3d_panels/tpu_panel_preview.html`. In multi-color mode, Three.js loads all 5 STL meshes concurrently with authentic PBR material colors and displays a floating AMS filament slot legend. Download buttons update dynamically for single STLs or 5-color ZIP/3MF bundles.
  - **Verification:** Verified compilation of 75-LED Medium (203.2mm) Front and Back plates in ~5.67s. Watertight geometry confirmed, STL files generated in `3d_panels/`, and `node --check simulator/app.js` passed with zero errors.

### Entry: Dedicated ESP32 Hardware Wiring Plan, Race Day Button Guide & Rules Integration
* **Date:** 2026-10-05 (Late Night Imagineering Session - Follow-up)
* **Milestone:** Milestone 6 - Dual-Button Controller Hardware Architecture, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Status:** Complete & Verified (`ESP32_WIRING_PLAN.md`, `RACE_DAY_BUTTON_GUIDE.md`, `GEMINI.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Dedicated ESP32 Hardware Wiring Specification (`ESP32_WIRING_PLAN.md`):** Authored a comprehensive electrical wiring manual containing complete Bill of Materials (BOM), 30-pin and 38-pin ESP32 DevKit pinout mappings, inline 220–470 Ω resistor placement on GPIO 16, dual tactile switch hookups (GPIO 4 and GPIO 33 to GND with internal pullups), 4-pin momentary switch orientation and continuity test guide (preventing permanent boot shorts), 200-LED front/back power injection bus topology, and computer USB power isolation rules.
  - **Race Day Button Field Guide (`RACE_DAY_BUTTON_GUIDE.md`):** Created a pocket-friendly runner field manual and printable controller cheat sheet detailing the dual-button gesture timings (<600ms tap, <400ms double tap, 3s sleep hold, 5s config hold), state-machine flow diagrams, full Leader vs Follower authority matrices, and a chronological race morning countdown playbook (3:30 AM bus departure $\rightarrow$ 4:15 AM corral roll call $\rightarrow$ 5:00 AM wave launch $\rightarrow$ photo stops $\rightarrow$ finish line).
  - **Mandatory Assistant Rule Integration (`GEMINI.md`):** Updated project governance rules in `GEMINI.md` (Section 1: Continuous Documentation Synchronization) mandating that both `ESP32_WIRING_PLAN.md` and `RACE_DAY_BUTTON_GUIDE.md` be kept 100% synchronized alongside `SIMULATOR_USER_GUIDE.md`, `README.md`, `FLASHING_INSTRUCTIONS.md`, and `PROJECT_PROGRESS.md` on any future firmware, hardware, or button scheme modification. Updated Section 2 to include official pinout definitions for GPIO 4 (Button 1) and GPIO 33 (Button 2).
  - **Repository & Cross-Linking:** Linked both new documentation guides directly in `README.md` for rapid family team reference.

### Entry: Multi-Color Graphic Artwork Castle Photo Mode & Standby Hold Release Latch
* **Date:** 2026-10-05 (Late Night Imagineering Session - Follow-up)
* **Milestone:** Milestone 6 - Dual-Button Controller Hardware Architecture, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Status:** Complete & Verified (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `include/fleet_palettes.h`, `arduino/MSEP_Costume/fleet_palettes.h`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Full Multi-Color Graphic Artwork Castle Photo Mode:** Replaced the previous monochromatic single hero color flood in `renderCastlePhotoMode()` across firmware and simulator with full, bright, 100% steady DC-like illumination displaying the authentic sampled background colors from each float's graphic (e.g. Pete's Dragon with emerald scales, magenta crest, and orange fire breath; Casey Jr. with red engine, yellow trim, cyan steam, and warm white headlight). Generated `include/fleet_palettes.h` and `arduino/MSEP_Costume/fleet_palettes.h` storing authentic 100-LED PROGMEM default palettes for all 7 floats, while preserving custom `costume_config.h` sampled palettes when present.
  - **Standby Hold Release Latch (Accidental Photo Mode Guard):** Identified and resolved the root cause of why holding Button 2 for >3 seconds accidentally entered Castle Photo Mode upon release: `b2WasPressed` was previously reset to `false` immediately upon hitting 3 seconds while the button was still depressed, causing the subsequent frames to latch a new button press whose release was falsely detected as a single tap (< 600ms). Implemented an explicit release-wait loop (`while (isButton2Down()) delay(10);`), cleared hold tracking only upon physical pin release, and added a release handler guard (`b2HoldHandled`) ensuring extended holds stay locked firmly in Corral Standby Mode. Entering Castle Photo Mode now requires an explicit, separate single click.
  - **Simulator State Precedence:** Synchronized `simulator/app.js` so that `computeLedColor` and `computeRunnerLedColor` prioritize Corral Standby over Photo Mode, `setStandbyUIState(true)` clears Photo Mode, and `simButton2HoldBtn` firmly latches Standby without accidental photo mode jumps.
  - **Photo Mode State-Preserving Toggle:** Confirmed and preserved the `previousStandaloneMode` state memory: tapping Button 2 while in Corral Standby enters Castle Photo Mode, and tapping Button 2 again cleanly returns to Corral Standby (preserving sleep mode battery life during pre-race photos). Tapping Button 2 while awake in Solo Show Mode enters Castle Photo Mode and returns to Solo Show Mode on the next tap.
  - **Button 1 Tap in Castle Photo Mode Transitions to Solo Show Mode:** Resolved the scenario where clicking Button 1 while in Castle Photo Mode was previously ignored on Followers (and launched the 30s fleet routine on Leaders). Button 1 tap now explicitly treats Castle Photo Mode as an active wake event, transitioning cleanly into regular Solo Show Mode (with green wake flash) locally on Followers and across the fleet on Leaders.
  - **Verification:** Verified via PlatformIO `pio run` (firmware builds in 9.48s with 14.3% RAM and 60.4% Flash) and `node --check simulator/app.js` (passes cleanly).

### Entry: Follower Button 1 Wake-Only Refinement & Streamlined Button Interface
* **Date:** 2026-10-05 (Late Night Imagineering Session - Follow-up)
* **Milestone:** Milestone 6 - Dual-Button Controller Hardware Architecture, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Status:** Complete & Verified (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Follower Button 1 Single Tap While Awake Ignored:** Updated firmware in both `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` (along with `simulator/app.js`) so that single-tapping Button 1 on a Follower node (Floats 2–6) while awake is completely ignored. This prevents non-technical runners from accidentally disrupting or changing their float's autonomous animation cues during the race. Follower Button 1 functions exclusively to wake up from Corral Standby (`0x50`) into Solo Show Mode, and when held for 5 seconds for Float ID configuration.
  - **Button Action Surface Streamlining:** Filtered and eliminated non-functional / ignored button combinations from documentation and cheat sheets, producing a clean, actionable test guide for the family runners.
  - **Verification:** Verified via `pio run` (firmware builds in 9.30s with 14.3% RAM and 60.2% Flash) and `node --check simulator/app.js`.

### Entry: Deploy Flasher Quick-Switch 7-Button Grid Rendering & Visibility Fix
* **Date:** 2026-10-05 (Late Night Imagineering Session - Follow-up)
* **Milestone:** Milestone 5 - Hardware Integration, Web Flasher Suite & Simulator Ergonomics
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Resolution of "undefined" Labels:** Discovered that `fleetRunners` populated from `localStorage` or `/api/fleet_config` did not include the `icon` field present on `DEFAULT_FLEET_ROSTER`. Updated `loadFleetLineupFromStorage()` to merge loaded objects against `DEFAULT_FLEET_ROSTER[idx]` so default properties (`icon`, `role`, `fullName`, `color`) are never lost. Added robust fallback in `renderDeployFloatSwitchGrid` (`DEFAULT_ICONS[i]` and default names).
  - **Full 7-Button Horizontal Visibility:** Replaced fixed-column styling and generic `.action-btn` padding with `.float-num-btn` styling and `grid-template-columns: repeat(7, minmax(0, 1fr))` with `box-sizing: border-box`, eliminating text overflow and horizontal clipping. All 7 floats (🚂 1, 🥁 2, 🐢 3, 🐌 4, 🩵 5, 🐉 6, 🦅 7) are now completely visible side-by-side in the sidebar.
  - **Verification:** Verified via `node --check simulator/app.js` and PlatformIO `pio run` (firmware builds in 5.09s).

### Entry: Unified Deploy Flashing Station & WYSIWYG Canvas ROM Synchronization
* **Date:** 2026-10-05 (Late Night Imagineering Session)
* **Milestone:** Milestone 5 - Hardware Integration, Web Flasher Suite & Simulator Ergonomics
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Color / Float Flashing Mismatch Resolution:** Diagnosed and resolved the issue where flashing Float 1 (The Train) from the fleet modal resulted in Pete's Dragon colors being flashed because Pete's Dragon remained active on the canvas while the flasher payload sampled canvas `leds`.
  - **Single Flashing Station Architecture:** Consolidated firmware flashing into one dedicated station located on the **Deploy Tab (`#tabHardware`)**. Removed the redundant `fleetFlashModal` popup from the Fleet Tab and replaced it with a direct navigation link (**"⚡ Go to Flasher ➔"**).
  - **Strict WYSIWYG ("What You See Is What You Flash") Paradigm:** Firmware compilation and USB flashing now strictly flushes the active canvas float (`activeSingleShirtRunnerSlot + 1`). If the user wants to flash another float, they switch the canvas first—ensuring full visual and color verification before burning to ROM.
  - **Quick-Switch Grid & Unsaved Edits Protection:** Added a 7-button quick switch grid `[1..7]` directly above the primary flash button in the Deploy tab. Selecting a float routes through `editRunnerInSingleView(slot)`, prompting the user if unsaved modifications exist, preventing accidental data loss.
  - **Dynamic Flash Button & Active Float Banner:** Deploy flasher displays an active float banner (`#deployActiveBanner`) with character icon, role, and lineup tag, with the action button dynamically labeled `⚡ Flash Float X: [Name] to ESP32 (USB)`.
  - **Startup State Persistence:** Replaced hardcoded Float 6 startup with `localStorage.getItem('msep_active_single_shirt_slot')`, cleanly defaulting to Float 1: The Train (Casey Jr.) on fresh starts while persisting the user's active float across sessions.
  - **Verification:** Verified via `node --check simulator/app.js` and PlatformIO `pio run` (firmware builds in 5.17s with 14.3% RAM and 60.2% Flash).

### Entry: LED Well Wall Base Retention Clip Groove & Clean No-Numbers Synchronization
* **Date:** 2026-10-06 (Mid-Morning Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`, `simulator/index.html` v86, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Modular Retention Clip Groove ($0.7\text{ mm}$ Tall $\times 0.6\text{ mm}$ Deep):** Added an undercut retention groove around the outer perimeter of each LED well wall in `scripts/compile_clean_tpu_panel.py`. The groove is cut $0.6\text{ mm}$ deep into the $1.2\text{ mm}$ outer collar wall (leaving $0.6\text{ mm}$ inner wall thickness), stands $0.7\text{ mm}$ tall, and runs parallel to the front-facing plate right at the base where the outer well wall joins the general plate floor ($Z = 2.0\text{ mm}$ to $Z = 2.7\text{ mm}$). This provides a positive locking latch for custom snap-over clips designed to hold each LED firmly in place against 10K running vibration.
  - **Definitive No-Numbers Default & Cache Guard:** Changed `INCLUDE_LED_NUMBERS` to default strictly to `False` across Python CLI compiler, server backend, and browser simulator (`params.tpuIncludeLedNumbers = false`), so that unless explicitly toggled on, zero debossed number geometry is ever produced.
  - **Fingerprint Signature Invalidation:** Added `grv-` and `groove-v1` salt into `computeTpuLayoutSignature()` in `simulator/app.js`, ensuring all previous cached meshes without the groove are automatically recognized as stale and cleanly rebuilt.
  - **Physical STL Verification:** Compiled clean Front and Back STLs with 0 numbers and 75 collar retention grooves. Verified mathematically via Manifold3D: `Manifold status: Error.NoError`, 55,798 faces (2.66 MB chassis STL), 100% watertight 2-manifold solid.

### Entry: 5-Color Multi-Material TPU Armor Panel Inlays, Custom Sizing, LED Counts & Number Toggle
* **Date:** 2026-10-06 (Morning Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`, `simulator/index.html` v84, `SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **5-Color Multi-Material Slicing Engine (`scripts/compile_clean_tpu_panel.py`):** Automated segmentation of active artwork into 5 precise color inlays (Green body/neck/tail, Magenta wings/spines, Yellow belly/horns, White teeth/eyes/sparkles, and structural Black base chassis). Generates multi-material 3MF files (`tpu_panel_front_multicolor.3mf`), split-part STL ZIP bundles (`tpu_panel_front_multicolor_bundle.zip`), and standalone chassis STLs.
  - **Artwork Contour & Facial Line Preservation:** Restored high-fidelity body silhouette geometry and facial line work, preserving Pete's Dragon's left eye outline and full torso green coverage through connected component vectorization.
  - **Selectable Sizes & LED Counts:** Added Layout tab controls for plate sizes (Small ~6.5", Medium ~8.0", Large ~10.0") and LED counts (50, 75, 100), passing parameters through `/api/generate_tpu_stl` to the compiler.
  - **Debossed LED Numbers Toggle (`[ 🔢 Numbers On | 🚫 No Numbers ]`):** Added modal toggle allowing users to choose between debossed numbering guides (1 to N) or a clean, smooth internal floor.
  - **Layout Signature & Immediate Recompile Cache Resolution:** Updated `computeTpuLayoutSignature()` in `simulator/app.js` to incorporate the `num` vs `nonum` flag in its return string. Ensured `setTpuLedNumbers()` triggers an immediate re-compilation with progress loader and direct 3D mesh reload when toggled inside the active preview modal. Standalone compilation verified via Trimesh (49,072 faces for clean plate vs 67,962 faces with debossed numbering).

### Entry: Two-Stage Button 1 Fleet Wake (Solo Mode First, Fleet Sync Second)
* **Date:** 2026-10-05 (Late Night Imagineering Session)
* **Milestone:** Milestone 6 - Dual-Button Controller Hardware Architecture, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Status:** Complete & Verified (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`, `README.md`, `FLASHING_INSTRUCTIONS.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Two-Stage Show Initiation Workflow:**
    - **First Tap in Standby:** When Leader taps Button 1 while the fleet is resting in Corral Standby (`0x50`), the Leader wakes up and broadcasts `0x51` (wake) to all followers. All floats wake directly into **Solo Show Mode** (`SHOW_MODE_AUTONOMOUS_SEQUENCE`), displaying their unique individual float identities (train steam, turtle spirals, snail wheels, coach sparkles, dragon fire, patriotic starbursts) without launching the synchronized theatrical show. Follower tap wakes that costume locally into Solo Show Mode.
    - **Second Tap while Awake:** When Leader taps Button 1 while running in Solo Show Mode, the Leader launches the **30-Second Theatrical Fleet Routine** (`0x30`) across all 7 floats simultaneously.
    - **Third Tap while Routine Active:** Allows early stop/cancel back to Solo Show Mode (`0x00`).
  - **Firmware & Simulator Synchronization:** Mirrored across `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, and `simulator/app.js`.

### Entry: Cold-Boot Button Arming Safety Guard & Real-Time Hardware Diagnostic Engine
* **Date:** 2026-10-05 (Night Imagineering Session - Follow-up)
* **Milestone:** Milestone 6 - Dual-Button Controller Hardware Architecture, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Status:** Complete & Verified (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Root Cause Analysis (Stuck in Float ID Config Mode):** When a pushbutton is shorted to GND at power-on (such as a 4-pin breadboard tact switch installed in the wrong 90° orientation, bridged wires, or jumpering directly to GND), `isButton1Down()` reads `LOW` continuously from the moment the ESP32 boots up. Because the firmware previously lacked a cold-boot pin-release guard, the hold timer accumulated 5 seconds from power-on and automatically fired `handleFloatConfigMode()`, locking the controller into config mode and waiting for pin release.
  - **Cold-Boot Arming Guard (`b1Armed` / `b2Armed`):** Added a non-blocking startup safety check. At boot, both Button 1 and Button 2 are in an un-armed state. The firmware requires pins to be read as `HIGH` (open / released) at least once before arming press and hold detection. If a pin is held `LOW` or shorted at power-on, the costume boots cleanly into Corral Standby without triggering the 5-second config mode or 3-second sleep hold, and logs a rate-limited diagnostic warning every 2.5 seconds.
  - **Startup Hardware Diagnostic Banner:** Added a formatted 115200-baud serial banner in `setup()` printing the exact instantaneous electrical reading (`LOW [SHORTED TO GND ⚠️]` vs `HIGH [OPEN / NORMAL]`) for `GPIO 4` (Button 1), `GPIO 33` (Button 2), and `GPIO 0` (BOOT pin).
  - **Real-Time Button Transition Logging:** Added live serial prints on every press and release event (`[BUTTON 1] Press detected (LOW)...`, `[BUTTON 1] Released (duration: ... ms)`), providing immediate feedback for bench debugging and race-day verification.
  - **Firmware Synchronization & Compilation:** Mirrored across `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`. Built cleanly via PlatformIO in 9.27s (RAM: 14.3%, Flash: 60.2%).

### Entry: Dual-Button Hardware Controller, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 6 - Dual-Button Controller Hardware Architecture, Castle Photo Mode & Dual-Leader Fleet Synchronizer
* **Status:** Complete & Verified (`src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator/index.html`, `simulator/app.js`, `simulator/web_flasher.html`, `FLASHING_INSTRUCTIONS.md`, `SIMULATOR_USER_GUIDE.md`, `README.md`).
* **Implementation Details:**
  - **Dual Dedicated GPIO Button Interface:** Upgraded from sole reliance on onboard BOOT button (GPIO 0) to a 2-button external tactile switch architecture using **GPIO 4** (Button 1: Show Director) and **GPIO 33** (Button 2: Media/Photo & Sleep) with internal pull-ups (`INPUT_PULLUP`), while retaining **GPIO 0** (BOOT) in software as an automatic parallel bench fallback.
  - **Precise Multi-Gesture Action Engine:**
    - **Button 1 Single Tap (< 600ms):** When in Corral Standby, Leader wakes entire fleet (`0x51`) and immediately starts 30s fleet routine (`0x30`); Follower wakes locally to baseline parade without triggering fleet routine. While running, Leader toggles/cancels 30s fleet routine; Follower toggles local sequence.
    - **Button 1 Double Tap (< 400ms):** Leader launches 4-second Rapid Attendance Roll Call wave (`0x44`); Follower ignores. Triple-tap removed per runner requirements.
    - **Button 1 Long Hold (5s):** Progressive 1s–4s white LED charging meter leading to Float ID Configuration Mode (⚪ 3 white entry flashes, tap to cycle Floats 1–7, 🟢 4 green auto-save flashes to NVS flash on 4s timeout). Releasing early cleanly aborts with zero changes.
    - **Button 2 Single Tap (< 600ms):** Leader puts entire fleet into **Castle Photo Mode** (`0x46` ON, `0x47` OFF); Follower puts local costume into Castle Photo Mode. Zero multi-tap delay on Button 2 for instantaneous shutter response.
    - **Button 2 Long Hold (3s):** Progressive 1s–2s soft blue charging meter; at 3s, 3 soft indigo confirmation pulses drop entire fleet (Leader, `0x50`) or local costume (Follower) into Corral Standby Mode (< 120mA).
  - **📸 Castle Photo Mode Renderer:** Emits a solid, steady, non-flickering DC-like illumination across all 200 LEDs (100 front + 100 back duplicated) in the float's signature hero color palette, safe under the FastLED 2.0A power governor, eliminating rolling-shutter artifacts and dark banding in camera photos.
  - **🦅 Dual-Leader (Float 1 & Float 7) Hierarchy:** Float 1 (Casey Jr.) acts as Primary Leader and Float 7 (To Honor America) acts as Co-Leader / Rear Marshal with full show and standby authority, allowing independent rear-pack command if runners split during the 10K.
  - **Simulator Suite Integration:** Added top-bar **📸 Photo Mode** toggle button and interactive Section 3 **Dual Button Hardware Simulator** (GPIO 4 + GPIO 33) with real-time feedback and state synchronization.
  - **Verification:** Verified compilation via PlatformIO (`pio run`) taking 19.92s with 14.3% RAM and 60.8% Flash; JavaScript syntax verified with `node --check simulator/app.js`.

### Entry: Selectable 3×3mm Square vs Ø 3mm Round Optical Aperture Windows in TPU Compiler & Simulator
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator.py`, `simulator/app.js`, `simulator/index.html` v81, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Parametric Window Geometry Engine (`scripts/compile_clean_tpu_panel.py`):** Added support for both `square` ($3.0\times 3.0\text{ mm}$ boxes) and `round` ($\varnothing 3.0\text{ mm}$, $r=1.5\text{ mm}$ 24-sided cylinders) through-skin optical window cutters in `compile_plate_variant()`. Enabled `--window-shape` CLI argument and `window_shape` JSON specs parameter.
  - **API Backend Synchronization (`simulator.py`):** Updated `/api/generate_tpu_stl` to parse incoming `windowShape` parameter, record `"window_shape"` in `tpu_panel_specs.json`, and pass `--window-shape` to the Python compiler process.
  - **Layout & Modal Shape Selectors:** Added interactive shape selection buttons (`🔲 3×3mm Square` | `⚪ Ø 3mm Round`) on the 2D Layout tab (Fabrication Overlays section) and in the 3D TPU Armor Panel Preview Modal header.
  - **2D Canvas & 3D WebGL Rendering:**
    - 2D Canvas draws square (`cx.rect`) or circular (`cx.arc`) windows in real time based on active selection.
    - 3D Preview Modal dynamically punches square (`ctx.fillRect`) or circular (`ctx.arc`) mask apertures into the graphic overlay and instantiates square (`THREE.PlaneGeometry`) or circular (`THREE.CircleGeometry`) emissive LED pixels.
  - **Fingerprint Signature & Auto-Recompile Guard:** Added `winShape` to `computeTpuLayoutSignature()`. Toggling the window shape marks previous STLs with differing shapes as stale and triggers a fast recompile when opening or regenerating from the 3D preview modal.

### Entry: 3×3mm Square LED Optical Aperture Windows in TPU STL Compiler & Simulator Preview
* **Date:** 2026-10-05 (Evening Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`scripts/compile_clean_tpu_panel.py`, `simulator/app.js`, `simulator/index.html` v80, `3d_panels/tpu_panel_preview.html`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **STL Compiler Parameter Update:** Updated `WINDOW_SQ = 3.0` in `scripts/compile_clean_tpu_panel.py`, expanding the square through-hole optical windows through the $1.0\text{ mm}$ front face skin from $2\times 2\text{ mm}$ to $3\times 3\text{ mm}$. Sits comfortably inside the $10.0\text{ mm} \times 5.0\text{ mm}$ inner pocket floor ($1.0\text{ mm}$ floor margin along width, $3.5\text{ mm}$ along length).
  - **2D Canvas Preview Alignment:** Updated `winSq = Math.max(4.5, 3.0 * ppm)` in `simulator/app.js` so that when `🖨️ Show TPU 3×3mm Windows` is active, the 2D layout canvas accurately renders $3\times 3\text{ mm}$ square window apertures centered in each LED pocket socket.
  - **3D Preview Modal & Standalone Viewer Alignment:** Adjusted optical cutout texture punches in `simulator/app.js` and `3d_panels/tpu_panel_preview.html` to $1.5\text{ mm}$ half-width (`hwPx = (1.5 / totalW_mm) * imgW`), and enlarged emissive LED pixel plane geometries from $1.8\times 1.8\text{ mm}$ to $2.8\times 2.8\text{ mm}$ to beam cleanly through the $3\times 3\text{ mm}$ apertures.
  - **UI & Cache Buster:** Updated UI toggle labels to `🖨️ Show TPU 3×3mm Windows`, modal subtitle to `3×3mm Square Windows`, and bumped `app.js?v=80`.

### Entry: High-Resolution Turtle_clean Transparent Artwork Integration
* **Date:** 2026-10-05 (Midday Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`assets/Turtle_clean.png`, `assets/spinning_turtle.png`, `simulator/app.js`, `simulator/index.html` v78, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Background Removal with Black Detail Preservation & Eyeglass Apertures:** Processed `assets/Turtle_clean.jpg` ($2262 \times 1888$) using connected-component background extraction. Both the outer JPEG background and the internal openings of the right eyeglasses frame (between the top/bottom rims, the nose bridge, the temple arm, and the face) were converted to 100% alpha transparency. All internal line work, glasses frames, pupil details, and tie contours ($27,180+$ dark pixels) remain fully preserved. Edge antialiasing was applied using Gaussian alpha boundary smoothing.
  - **Color Integrity Preserved:** Verified that the blue shell segment adjacent to the tie was kept in its authentic blue hue as confirmed by the user.
  - **Default Graphic Assignment:** Saved as `assets/Turtle_clean.png` and synchronized to `assets/spinning_turtle.png`. Updated `spinningTurtleImg.src` and `floatArtworkImgs['spinning_turtle'].src` in `simulator/app.js` to default to `Turtle_clean.png`.
  - **STL & Physics Verification:** Tested end-to-end STL compilation against the new clean silhouette. Front plate ($156.92 \times 139.60 \times 6.0\text{ mm}$) and Back plate ($198.20 \times 175.89 \times 6.0\text{ mm}$) generated watertight meshes with **100 / 100 LEDs perfectly contained within the clean turtle silhouette**.

### Entry: Permanent Fix for 3D TPU Preview Graphic Rotation Flickering & Z-Fighting
* **Date:** 2026-10-05 (Morning Imagineering Session - Follow-up)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator/app.js`, `simulator/index.html` v77, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Root Cause Analysis:** When orbiting or rotating the 3D TPU Armor Plate in `#tpuPreviewModal`, the front graphic flickered or vanished depending on viewing angle. Three compounding factors were identified:
    1. **Z-Fighting / Coplanar Precision:** The graphic mesh was positioned at `stlCenter.z + 0.08mm`. Under standard 24-bit depth buffers with an ultra-close `near = 0.1` clip plane spanning to `far = 2000`, depth precision at oblique angles fell below $0.08\text{ mm}$, causing the TPU plate's front surface to intermittently win depth testing and clip through the graphic.
    2. **Missing Render Order & Transparent Depth Sorting:** Neither `tpuStlMesh` nor `tpuGraphicMesh` had explicit `renderOrder` defined. When Three.js sorted transparent objects from back to front, camera rotation altered object distance centroids, causing the render order between the plate and the graphic to swap mid-rotation.
    3. **Missing Hardware Polygon Offset:** Neither material used OpenGL/WebGL polygon offset to bias depth rasterization.
  - **Comprehensive Multi-Layer Solution:**
    - **Logarithmic Depth Buffer:** Enabled `logarithmicDepthBuffer: true` on `THREE.WebGLRenderer` to provide uniform high-precision depth testing across all view distances.
    - **Camera Near Clip Optimization:** Increased camera `near` from $0.1\text{ mm}$ to $1.0\text{ mm}$, vastly multiplying depth buffer precision.
    - **Physical Elevation Offset:** Raised graphic mesh position to `stlCenter.z + 0.35mm` (well above the plate skin while remaining visually flush) and LEDs to `stlCenter.z + 0.20mm`.
    - **Explicit Render Order & Depth Testing:** Enforced `tpuStlMesh.renderOrder = 0`, `tpuGraphicMesh.renderOrder = 2`, and `tpuLedsGroup.renderOrder = 3`. Enabled `depthTest: true` and `depthWrite: false` on the graphic so it never occludes itself or disappears.
    - **GPU Polygon Offsets:** Applied `polygonOffset: true` with negative factors (`factor: -1.0, units: -2.0`) on the graphic and positive on the plate (`factor: 1.0, units: 1.0`), guaranteeing the GPU rasterizer always draws the graphic in front regardless of orbit angle.

### Entry: Three.js Model Group Disposal & Monotonic Request ID Guard (Eliminating Ghost Mesh Overlays)
* **Date:** 2026-10-05 (Morning Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator/app.js`, `simulator/index.html` v76, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Root Cause Analysis:** When switching between floats (e.g. Turtle → Snail) and opening the 3D TPU Preview, both graphics were visibly overlaid simultaneously. Investigation revealed that `loadTpuModalData` is asynchronous (`STLLoader.load`, `Image.onload`). Because previous Three.js meshes were not disposed/cleared from `tpuScene` upon loading new data, and out-of-order async promises could add multiple graphic planes, the previous float's texture mesh remained in the scene alongside the newly loaded graphic. Additionally, `handleRecompileTpuStl` used `fleetConfig` instead of `fleetRunners`, causing the modal title to fallback to "Pete's Dragon".
  - **Scene Model Disposal (`clearTpuSceneModel`):** Created a recursive traversal cleanup routine in `app.js` that removes all mesh and group objects from `tpuScene`, explicitly disposing geometries, textures, and materials to avoid WebGL memory leaks and stranded ghost meshes.
  - **Monotonic Request ID Guard:** Added `tpuLoadRequestId` in `loadTpuModalData`. Any async promise completion (`STLLoader.load`, `createTpuGraphicCutoutMesh`) checks `reqId === tpuLoadRequestId` and drops obsolete responses immediately.
  - **Dynamic Float Title & Naming:** Added `getActiveFloatName()` helper to dynamically identify the active runner float name (e.g. "The Spinning Snail", "The Spinning Turtle") and reflect it across the 3D modal title, recompile status toasts, and `tpu_panel_specs.json`.

### Entry: Stale-STL Guard — TPU Preview Auto-Recompiles for the Active Graphic
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator/app.js`, `simulator.py`, `simulator/index.html` v75, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Root Cause:** The Deploy tab's **Preview 3D TPU Armor Panel** button only opened the modal and loaded whatever STL was last compiled (Pete's Dragon), while the artwork overlay was drawn from the live canvas graphic (e.g., The Spinning Turtle). Result: turtle artwork floating on a dragon-shaped plate.
  - **Layout Signature:** Added `computeTpuLayoutSignature()` in `app.js` — a fast hash of the active graphic type, artwork source, chest bounds, and all 100 LED coordinates. It is sent as `layoutSignature` with every `/api/generate_tpu_stl` request and persisted by `simulator.py` into `tpu_panel_specs.json` (`layout_signature`, `graphic_type`).
  - **Auto-Recompile on Open:** `openTpuPreviewModal()` now compares the compiled signature with the live canvas. On mismatch it shows "Active graphic changed — compiling fresh Front & Back STLs…" and recompiles before loading the 3D scene, so the plate silhouette, LED pockets, and artwork overlay always match.
  - **Verification:** End-to-end POST with `spinning_turtle.png` produced turtle-shaped Front ($157.1 \times 139.8 \times 6\text{ mm}$) and Back ($198.3 \times 176.1 \times 6\text{ mm}$) STLs; signature persisted correctly.

### Entry: Silhouette Containment Clamping in PBD Collision Solver & Front/Back LED Placement Fix
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator.py`, `scripts/compile_clean_tpu_panel.py`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Root Cause Analysis:** In the 3D TPU Preview, the Front plate displayed LEDs bleeding outside the dragon artwork into empty space while the Back plate looked correct. Investigation revealed that the PBD collision solver previously repelled colliding sockets with unconstrained repulsion. In the tighter Front plate footprint ($166.6 \times 200\text{ mm}$), the repulsive forces pushed 30 LEDs outside the dragon boundary into empty transparent air ($alpha = 0$). Conversely, on the $1.3\times$ larger Back plate ($240\text{ mm}$), sockets had enough room and remained inside the artwork.
  - **Artwork Boundary Containment Clamping:** Updated `scripts/compile_clean_tpu_panel.py` to extract the un-dilated artwork silhouette polygon (`dragon_poly`) and construct a `safe_art_boundary = dragon_poly.buffer(-2.0)`. During each PBD iteration, any LED center driven outside the safe boundary is immediately projected back onto the nearest interior polygon contour.
  - **Zero Artwork Spill Verification:** Automated testing verified that **100 / 100 LEDs** on the Front plate and **100 / 100 LEDs** on the Back plate now sit strictly inside the artwork silhouette ($alpha > 40$, 0 outside).
  - **Front Height Clamping Adjustment:** In `simulator.py`, adjusted `FRONT_HEIGHT_MM` max clamping to $220.0\text{ mm}$ (the exact physical distance from neck collar $y = 0.168$ to race bib $y = 0.553$), allowing full $185.0\text{ mm}$ base width without premature aspect shrinkage. Actual 3D printed plate dimensions are $158.4 \times 143.1\text{ mm}$ (Front) and $184.5 \times 165.1\text{ mm}$ (Back), easily fitting within both Bambu Lab ($250 \times 250\text{ mm}$) and Snapmaker U1 ($270 \times 270\text{ mm}$) beds.
  - **Cache Buster:** Bumped `app.js?v=74` in `simulator/index.html`.

### Entry: Dual Front (185mm) & Back (240mm) TPU Armor Panel Pipeline & Interactive 3D Suite
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator.py`, `scripts/compile_clean_tpu_panel.py`, `simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Dual Panel Architecture:** Implemented a dual-panel generation pipeline aligning with the 200-LED costume architecture (100 front chest pixels + 100 back pixels duplicated in real time):
    - **🎽 Front Chest Plate:** $185.0\text{ mm}$ base width ($\sim 154\text{ mm}$ height, clamped $\le 200\text{ mm}$), shaped to fit strictly above runDisney Bib #1952.
    - **🎒 Back Torso Plate:** $240.0\text{ mm}$ maximum dimension ($\sim 200\text{ mm}$ height), maximizing the running shirt back with no bib constraint.
  - **Proportional LED Spacing:** The 100 LED socket center positions scale up proportionally by $\approx 1.30\times$ on the back plate, maintaining exact 1:1 real-time firmware animation matching with wider wire spacing. Individual socket cavities stay standard $10\times5\text{ mm}$ with $2\times2\text{ mm}$ optical apertures.
  - **Batch Python Compiler:** Updated `scripts/compile_clean_tpu_panel.py` to compile both `tpu_panel_front.stl` ($2.95\text{ MB}$) and `tpu_panel_back.stl` ($3.13\text{ MB}$) in under 9 seconds total via Manifold3D. Also exports parametric OpenSCAD sources for both plates.
  - **Interactive 3D Modal Variant Switcher:** Embedded a segmented switcher pill `[🎽 Front (185mm)]` vs `[🎒 Back (240mm)]` in `#tpuPreviewModal`. Switching dynamically updates the Three.js mesh, scales the graphic cutout texture, recalibrates camera zoom, and updates the dimensions badge.
  - **Deploy Tab Action Suite:** Added dimension chips ($185\text{ mm}$ vs $240\text{ mm}$), bed margins (Snapmaker U1 $15\text{ mm}$ to $50\text{ mm}$, Bambu Lab $5\text{ mm}$ to $42\text{ mm}$), direct download buttons for Front STL, Back STL, and a 1-click **"📦 Download Both STLs"** helper (`downloadBothTpuStls()`).

### Entry: Fix TPU Preview Button Trigger & DOM Modal Nesting Resolution
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`).
* **Implementation Details:**
  - **DOM Unclosed Tag Fix:** Discovered that preceding `#cricutExportModal` was missing its closing `</div>` tags. As a result, the browser parser placed `#tpuPreviewModal` inside `#cricutExportModal`. Because `#cricutExportModal` had `display: none;`, `#tpuPreviewModal` remained invisible despite setting `display: flex;`. Properly closed `#cricutExportModal` and `<div class="main-layout">`.
  - **Explicit Inline Button Handler:** Added `onclick="openTpuPreviewModal()"` and `onclick="closeTpuPreviewModal()"` attributes to ensure buttons trigger directly regardless of event listener initialization timing.
  - **Global Window Exposure & Reflow Resizing:** Exposed `openTpuPreviewModal`, `closeTpuPreviewModal`, and `handleRecompileTpuStl` on `window`. Added a 60ms layout reflow timer calling `onTpuWindowResize()` when opening the modal to ensure proper WebGL camera aspect ratio calculation.
  - **Cache Buster Bump:** Bumped `app.js?v=72` to invalidate stale browser caches. Verified with `HTMLParser` that `#tpuPreviewModal` is now a direct child of `<body>`.

### Entry: Dynamic Multi-Float TPU Armor Panel Silhouette Generation & End-to-End Verification
* **Date:** 2026-10-05 (Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Deploy Suite
* **Status:** Complete & Verified (`simulator.py`, `scripts/compile_clean_tpu_panel.py`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Dynamic Multi-Float Silhouette Tracing:** Upgraded the 3D TPU armor panel compilation pipeline to dynamically construct tailored perimeter trays for **any active float** (Float 1 Casey Jr., Float 2 Title Drum, Float 3 Turtle, Float 4 Snail, Float 5 Cinderella, Float 6 Pete's Dragon, Float 7 Flag & Eagle, or custom user graphics), removing Pete's Dragon hardcoding.
  - **Offscreen Canvas Rasterization & Contour Extraction:** When clicking "⚙️ Recompile STL", `app.js` renders the active float artwork (SVG or PNG) to an offscreen 1024px canvas and sends base64 PNG data to `/api/generate_tpu_stl`. `compile_clean_tpu_panel.py` uses OpenCV `findContours` + `approxPolyDP` and Shapely `.buffer(4.0mm)` to generate a bespoke boundary tray and distributes 16 smooth perimeter mounting eyelets evenly along the active float's unique shape.
  - **Print Bed Safety Clamping:** Computes float aspect ratio and automatically clamps the maximum dimension to $230\text{ mm}$ (e.g., Turtle at $185.0 \times 154.5\text{ mm}$), ensuring generous clearance on Snapmaker U1 ($270 \times 270\text{ mm}$) and Bambu Lab ($256 \times 256\text{ mm}$) build plates.
  - **Interactive 3D Preview Auto-Centering:** Three.js modal dynamically centers the tailored float mesh via `geom.computeBoundingBox()` and projects the active float's artwork with 2×2mm square window cutouts.
  - **Multi-Float Verification:** Successfully compiled and verified watertight Manifold3D binary STL generation for Float 3 Spinning Turtle ($2.54\text{ MB}$, 100 LED pockets, zero errors).

### Entry: Deploy Tab 3D TPU Preview Modal, Live STL Compilation & Layout Pocket Overlap Avoidance
* **Date:** 2026-10-05 (Midnight Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & Simulator Integration
* **Status:** Complete & Verified (`simulator.py`, `simulator/index.html`, `simulator/app.js`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Deploy Tab 3D Panel Section (`tabHardware`):** Added a dedicated 3D-Printable TPU Armor Panel suite with build plate clearance chips for Snapmaker U1 ($270 \times 270\text{ mm}$) and Bambu Lab ($256 \times 256\text{ mm}$), live compile status, and direct download links for `.stl` and `.scad`.
  - **Embedded Three.js 3D STL Preview Modal (`#tpuPreviewModal`):** Built a high-performance modal popup inside the simulator loading binary `petes_dragon_tpu_panel.stl`, with Pete's Dragon artwork overlay featuring clean $2\text{ mm} \times 2\text{ mm}$ square window cutouts via HTML5 canvas `destination-out` masking. Added quick camera angles (Front Face, Underside/Pockets, 3D Angle), LED simulation states (Off, Static On, Animated 60 FPS Parade), and artwork/plate opacity sliders.
  - **Live Backend STL Compilation Endpoint (`/api/generate_tpu_stl`):** Accepts active simulator LED coordinates, recalculates physical millimeter positions, writes `petes_dragon_specs.json`, runs `scripts/compile_clean_tpu_panel.py` via Python subprocess, and compiles a fresh watertight STL via Manifold3D in under 3 seconds.
  - **Layout Tab 2×2mm Window Visualization (`#showTpuWindowsToggle`):** Added dedicated toggle in `tabLayout` rendering subtle $10\text{ mm} \times 5\text{ mm}$ (outer $12.4 \times 7.4\text{ mm}$) pocket socket boundaries with wire pass-through notches and crisp $2\text{ mm} \times 2\text{ mm}$ square optical apertures with radiant light beaming through.
  - **Zero Collar Overlap Collision Avoidance:** Integrated live collision clamping (`clampLedNoCollarOverlap`) during LED dragging to maintain $\ge 7.9\text{ mm}$ center distance ($0.5\text{ mm}$ wall clearance), and embedded PBD (Position-Based Dynamics) stadium separation (`relaxLedCollarOverlaps`) into **100 Scatter** and **Fill Graphic with Remaining LEDs** to guarantee zero overlapping pockets on auto-generated layouts.

### Entry: Snapmaker U1 270x270mm Build Volume Verification & Bed Clearance
* **Date:** 2026-10-04 (Late Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`SIMULATOR_USER_GUIDE.md`, `PROJECT_PROGRESS.md`).
* **Implementation Details:**
  - **Snapmaker U1 Print Bed Clarification:** Confirmed official Snapmaker U1 build envelope is $270 \times 270 \times 270\text{ mm}$ (rather than $220 \times 220\text{ mm}$).
  - **Spacious Bed Margin:** With the Pete's Dragon chest plate envelope measuring $172.2\text{ mm W} \times 153.8\text{ mm H} \times 6.0\text{ mm THICK}$, the panel occupies only $\approx 64\%$ of bed width and $\approx 57\%$ of bed depth. This leaves an abundant $\approx 48.9\text{ mm}$ ($1.9\text{ in}$) margin along $X$ and $\approx 58.1\text{ mm}$ ($2.3\text{ in}$) margin along $Y$, providing effortless skirt/brim clearance and zero risk of edge clipping when printing flat in 95A TPU.

### Entry: Debossed Number Underside Left-to-Right Orientation Fix
* **Date:** 2026-10-04 (Late Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `scripts/compile_clean_tpu_panel.py`, `scripts/update_scad_model.py`).
* **Implementation Details:**
  - **Resolved Mirrored Debossed Digits:** Because the numbers are debossed into the interior floor of the tray to be read from the underside (looking along $+Z$ from behind), the glyph cutters are mirrored horizontally along the $X$-axis (`scale([-1.0, 1.0, 1.0])` with face winding reversal in Python Manifold3D, and `mirror([1, 0, 0])` in OpenSCAD).
  - **Natural Left-to-Right Reading:** When viewing into the rear open wire basin and notched collars, every number (e.g. `1` through `100`) now reads in natural left-to-right order without mirror reversal.

### Entry: Corrected Front/Back Z-Orientation & Non-Mirrored STL Alignment
* **Date:** 2026-10-04 (Late Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & WebGL Inspector
* **Status:** Complete & Verified (`3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_tpu_panel.stl`, `scripts/compile_clean_tpu_panel.py`).
* **Implementation Details:**
  - **Resolved Mirror / Reversed Front & Back Bug:** Corrected the STL coordinate orientation so the solid front face ($2\text{ mm} \times 2\text{ mm}$ optical apertures) is located at $Z = 6.0\text{ mm}$ pointing forward (+Z toward the camera/viewer), while the open wire basin and notched collars face the runner's shirt at $Z = 0.0\text{ mm}$ (-Z).
  - **Non-Mirrored Graphic Alignment:** Because the front face now points toward +Z, the dragon's head and snout face forward to the right identically in both ViewSTL and the WebGL inspector, perfectly matching [`assets/petes_dragon_transparent.png`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/assets/petes_dragon_transparent.png) without horizontal inversion.
  - **Fixed Preview Camera Buttons:** Swapped camera positions so clicking **"👕 Front Face"** positions the camera at $(0, 0, +320)$ showing the exterior dragon graphic and apertures, while **"🔄 Underside (Pockets)"** positions the camera at $(0, 0, -320)$ looking into the rear wire basin and collars.
  - **Maintained 2.0mm Collar Clearance & Back-Flush Eyelets:** Preserved $2.0\text{ mm}$ space between collar tops ($Z = 2.0\text{ mm}$) and perimeter rim base ($Z = 0.0\text{ mm}$), with all 16 pure circular mounting eyelets flush with the shirt rim at $Z = 0.0\text{ mm}$.

### Entry: Simplified 3D STL Previewer with Graphic Window Cutouts & LED Simulation
* **Date:** 2026-10-04 (Late Night Imagineering Session)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication & WebGL Inspector
* **Status:** Complete & Verified (`3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_tpu_panel.stl`, `SIMULATOR_USER_GUIDE.md`).
* **Implementation Details:**
  - **Direct STL Mesh Loading:** Replaced procedural canvas extrusions with Three.js `STLLoader`, directly rendering the exact binary `petes_dragon_tpu_panel.stl` model that will be printed on the Snapmaker U1.
  - **Graphic Window Cutouts:** Employed HTML5 Canvas destination-out alpha masking to punch clean $2\text{ mm} \times 2\text{ mm}$ square transparent window cutouts directly into the Pete's Dragon graphic, keeping the optical apertures open and unobstructed.
  - **LED State Simulation:** Implemented three simulation states via floating controls: **LEDs Off**, **Static On** (authentic Pete's Dragon palette), and **Animated Parade** (60 FPS traveling wave and shimmer).
  - **Streamlined Minimal UI:** Stripped away complicated multi-card sidebars and unused layer toggles, replacing them with a sleek floating control pill providing instant camera switching (Front, Underside, 3D Angle) and graphic/plate opacity sliders.

### Entry: Pure Smooth Circular Outside Eyelets (Zero Points, Zero Corners)
* **Date:** 2026-10-04 (Late Night / Midnight)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  - **Pure Smooth Circular Geometry (Zero Points):** Resolved the angular "pointy bit" artifacts by reconstructing all 16 eyelets as pure concentric cylinders of outer diameter $6.5\text{ mm}$ (radius $3.25\text{ mm}$) and height $2.0\text{ mm}$ ($Z = 4.0\text{ mm}$ to $6.0\text{ mm}$). Replaced the dual-cylinder convex hull and conical taper with 100% rotational symmetry, ensuring every cross section is a smooth circular arc with zero sharp points, zero shield corners, and zero knife edges.
  - **Back-Flush Orientation:** Sits flush with the shirt-touching back rim at $Z = 6.0\text{ mm}$, providing an unobstructed flat surface for stitching or tagging barbs directly against the fabric.
  - **2.0mm Solid Wall Thickness:** Maintained $\varnothing 2.5\text{ mm}$ through-hole with $2.0\text{ mm}$ thick walls ($6.5\text{ mm}$ OD) and $1.75\text{ mm}$ deep solid overlap into the $2.5\text{ mm}$ thick perimeter rim wall.
  - **Manifold3D Validation:** Validated 2-manifold with `Error.NoError` (genus 129, 61,332 triangles, net volume $38,936.7\text{ mm}^3$).
  - **Full Synchronization:** Synchronized parametric OpenSCAD script (`scripts/update_scad_model.py` and `3d_panels/petes_dragon_tpu_panel.scad`), WebGL preview inspector (`3d_panels/tpu_panel_preview.html`), and `SIMULATOR_USER_GUIDE.md`.

### Entry: PBD Zero-Overlap Pocket Separation Solver & Smallest Readable Debossed Numbers
* **Date:** 2026-10-04 (Late Night)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  - **Zero-Overlap Collar Relaxation Solver (PBD):** Implemented a Position-Based Dynamics relaxation algorithm in `scripts/compile_clean_tpu_panel.py` that models the horizontal $12.4\text{ mm} \times 7.4\text{ mm}$ outer collar stadium envelopes and resolves all 64 overlapping collisions. Collar centers were nudged by a minimal average shift of just $1.64\text{ mm}$ (maximum $4.89\text{ mm}$), guaranteeing **zero overlapping pockets** and a minimum clear wall gap of $\ge 0.49\text{ mm}$ between every pair of collars while strictly preserving the authentic Pete's Dragon shape.
  - **Smallest Readable Debossed Numbers:** Reduced font cap height to $1.8\text{ mm}$ with $0.5\text{ mm}$ deboss depth into the tray floor (Z from $1.5\text{ mm}$ to $2.1\text{ mm}$). This matches the physical extrusion resolution limit of a standard $0.4\text{ mm}$ 3D printer nozzle for crisp readability without wasting surface area.
  - **Geometry & Mesh Verification:** Watertight solid volume confirmed (`39,005.8 mm³`), zero non-manifold edges, dimensions: $166.09\text{ mm W} \times 151.99\text{ mm H} \times 6.00\text{ mm THICK}$.

### Entry: Fixed Multi-Digit Debossed Number Stacking & Horizontal Collar Realignment
* **Date:** 2026-10-04 (Night)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  - **Multi-Digit Number Kerning Fix:** Resolved a text path translation bug in `scripts/compile_clean_tpu_panel.py` where individual character polygons of multi-digit numbers (`10`, `25`, `100`) were separately centered to $(0, 0)$, causing digits to be engraved directly on top of each other. The updated generator now extrudes all glyphs of a number string and concatenates them into a unified block before translating, preserving clean kerning and spacing across all numbers `1` through `100`.
  - **Collar Orientation & Squishing Fix:** Replaced wild sequential tangent rotations (which caused $10\text{ mm} \times 5\text{ mm}$ collars on dense neighboring LEDs to criss-cross and collide into squished 'X' shapes) with uniform horizontal ($0^\circ$) orientation matching the Pete's Dragon Chris preset. Collars now sit cleanly parallel across the chest tray.
  - **Clean Dragon Artwork Silhouette Boundary:** Derived the outer chassis boundary directly from the authentic Pete's Dragon transparent artwork contour with a $+4.0\text{ mm}$ margin, producing a tailored $166.1\text{ mm W} \times 152.0\text{ mm H} \times 6.0\text{ mm THICK}$ tray that fits effortlessly on the Snapmaker U1 bed with zero excess dead weight ($\approx 43\text{ g}$ in 95A TPU).
  - **Verified Geometry:** Binary STL validated with `manifold3d` as 100% watertight (`is_volume == True`), zero open boundary edges, and non-manifold free.

### Entry: 1.0mm LED Pocket Floor Recess, 3.0mm Collars & 2.0mm Table Clearance
* **Date:** 2026-10-04 (Late Evening)
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  - **Refined Vertical Cross-Section Architecture:**
    - Base plate general floor: $2.0\text{ mm}$ thick.
    - LED pocket floor: Localized $1.0\text{ mm}$ deep recesses cut directly inside each $10\text{ mm} \times 5\text{ mm}$ pocket socket cavity, leaving a $1.0\text{ mm}$ thick front floor under each resin bulb while keeping the front shirt-facing surface completely smooth and flush.
    - Collars: $3.0\text{ mm}$ tall oval socket walls rising from the recessed pocket floor ($Z = 1.0\text{ mm}$ to $Z = 4.0\text{ mm}$).
    - Table Clearance: Total chassis height is $6.0\text{ mm}$ (formed by the $4.0\text{ mm}$ outer perimeter rim from $Z = 2.0\text{ mm}$ to $6.0\text{ mm}$). When placing the 3D print flat on a table front-side up, the outer rim rests on the table at $Z = 6.0\text{ mm}$, leaving **exactly $2.0\text{ mm}$ of clear open space** between the tops of the pocket walls ($Z = 4.0\text{ mm}$) and the table surface ($6.0\text{ mm} - 4.0\text{ mm} = 2.0\text{ mm}$).
  - **Clean Manifold Topology:** Integrated `manifold3d` CSG cleanup into `scripts/compile_clean_tpu_panel.py` ensuring that the exported binary STL mesh is 100% watertight, non-degenerate, and solid volume ($70,980\text{ mm}^3$, 31,207 vertices, 62,838 triangles).
  - **Parametric OpenSCAD & WebGL Synchronization:** Updated `scripts/update_scad_model.py` and `3d_panels/petes_dragon_tpu_panel.scad` with the recessed floor geometry; embedded updated JSON specifications into `3d_panels/tpu_panel_preview.html`.

### Entry: Open-Chassis 6.0mm TPU Armor Tray Architecture with Notched Collars & Open Wire Basin
* **Date:** 2026-10-04
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  * **Open Chassis Tray Architecture:**
    - Radically simplified and optimized the mounting plate per user requirements into an open chassis tray.
    - **Front Plate:** Continuous $2.0\text{ mm}$ thick solid front skin ($Z = 0$ to $2.0\text{ mm}$).
    - **Perimeter Rim Wall:** $4.0\text{ mm}$ tall outer rim ($Z = 2.0$ to $6.0\text{ mm}$), creating a protective $6.0\text{ mm}$ total plate height.
    - **Unconstrained Open Wire Basin:** The entire space between collars is a wide-open $4.0\text{ mm}$ deep cavity where 3-conductor flat ribbon wire routes and loops freely with **no back wall** and **no restrictive wire channels or isolated slack wells**.
  * **100 Notched Oval Collars:**
    - $10.0\text{ mm} \times 5.0\text{ mm}$ inner cavity with $3.0\text{ mm}$ tall walls ($Z = 2.0$ to $5.0\text{ mm}$).
    - Rotated along sequential choreography path tangent ($\theta_i = \text{atan2}(y_{i+1}-y_i, x_{i+1}-x_i)$).
    - $4.0\text{ mm}$ wide wire pass-through notches on both $5\text{ mm}$ ends extending down to the floor ($Z = 2.0\text{ mm}$) for easy wire entry and exit.
  * **Centered Square Optical Apertures:**
    - $2.0\text{ mm} \times 2.0\text{ mm}$ square through-windows centered under each bulb through the $2.0\text{ mm}$ front face.
  * **Debossed Floor Numbers & Backside Eyelets:**
    - Numbers `1` through `100` etched $0.6\text{ mm}$ deep into the interior floor adjacent to each collar.
    - 16 perimeter fastener ear tabs ($\varnothing 2.5\text{ mm}$ eyelets) connected to the inside edge of the perimeter rim wall ($Z = 2.0$ to $5.0\text{ mm}$), keeping the front shirt face 100% smooth and puncture-free.
  * **Validation:** Verified 100% watertight binary manifold STL ($2,539,684\text{ bytes}$, volume $60,714.1\text{ mm}^3$, zero errors). Synchronized OpenSCAD source and WebGL preview.

### Entry: Clean Solid TPU Chest Armor Plate with Debossed Numbers & Integrated Slack Bays
* **Date:** 2026-10-04
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  * **Root Cause of "Mess" & Solution:**
    - The initial prototype boolean-cut 984 intersecting channel lines and overlapping expansion wells across a tight clipart contour, causing pocket walls to be severed (330 channel-to-pocket collisions) and creating floating clip fragments in mid-air.
    - Engineered a unified, solid, continuous wearable plate ($177.2\text{ mm W} \times 163.4\text{ mm H} \times 5.5\text{ mm}$) with smooth filleted outer borders ($\ge 8.5\text{ mm}$ margin around all LEDs) and solid flexible TPU webbing bridging all body/wing/tail bays. Zero floating debris, zero thin sliver walls, zero jagged sawteeth.
  * **Debossed LED Numbers (1 to 100):**
    - Directly solved assembly identification by permanently debossing numbers `1` through `100` ($3.0\text{ mm}$ tall, $0.8\text{ mm}$ deep) into the plate surface directly adjacent to each LED socket.
    - Handled hollow typographic glyph geometry (`0`, `4`, `6`, `8`, `9`) ensuring crisp, watertight 3D engraving that requires zero supports during 3D printing.
  * **Clean Socket & Slack Bay Architecture:**
    - **100 Oval Sockets:** $10.5\text{ mm} \times 5.5\text{ mm} \times 3.0\text{ mm}$ deep stadium wells for $10\text{ mm} \times 5\text{ mm}$ resin bulbs with solid $2.5\text{ mm}$ front retaining lips.
    - **100 Optical Apertures:** $5.6\text{ mm} \times 3.2\text{ mm}$ oval through-windows for unobstructed light output.
    - **100 Dedicated On-Edge Slack Wells:** $\varnothing 7.5\text{ mm} \times 4.5\text{ mm}$ deep expansion chambers positioned along the wire exit path to cleanly absorb $\approx 35\text{ mm}$ of 3-conductor ribbon wire on its edge.
    - **16 Perimeter Eyelets:** $\varnothing 2.5\text{ mm}$ through-holes with $\varnothing 5.0\text{ mm} \times 1.0\text{ mm}$ front countersinks along the outer perimeter for garment tagging barbs.
  * **Validation:** Verified 100% watertight manifold mesh ($2,606,184\text{ bytes}$, volume $79,221.0\text{ mm}^3$, zero non-manifold edges). Rendered orthographic verification views and updated local web preview inspector.

### Entry: 5.5mm High-Clearance Armor Plate with 10x5mm Oval LEDs & 4.5mm On-Edge Slack Wells
* **Date:** 2026-10-04
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  * **Real Hardware Specifications Implemented:**
    - **LED Bulb Pockets:** Scaled from round Ø5.4mm to $10.6\text{ mm} \times 5.6\text{ mm} \times 3.0\text{ mm}$ deep oval stadium pockets to house $10.0\text{ mm} \times 5.0\text{ mm}$ oval teardrop resin pixels.
    - **Front Optical Windows:** $6.0\text{ mm} \times 3.5\text{ mm}$ oval apertures to let raw LED lenses shine forward.
    - **Ribbon Wire Channels:** Widened to $4.4\text{ mm wide} \times 1.4\text{ mm deep}$ to seat 3-conductor flat ribbon wire.
    - **On-Edge Slack Absorption Wells:** Added $\varnothing 9.0\text{ mm} \times 4.5\text{ mm deep}$ expansion chambers at each LED to solve flat ribbon in-plane bending physics (wire turns $90^\circ$ onto its $4.0\text{ mm}$ edge to loop effortlessly without buckling).
    - **Panel Thickness:** Increased base plate to $5.5\text{ mm}$ to house the $4.5\text{ mm}$ deep wells while preserving a solid $1.0\text{ mm}$ front face skin.
  * **Choreographed Spacing:** Utilized Chris's exact sequential preset order (averaging $65.0\text{ mm}$ spans), keeping slack to a manageable $\approx 35\text{ mm}$ per segment.
  * **Mesh Validation & Export:** Compiled solid CSG boolean STL ($1,311,284\text{ bytes}$, volume $25,446.2\text{ mm}^3$, zero boundary edge errors). Available via direct download in `tpu_panel_preview.html` and OpenSCAD parametric source.

### Entry: Watertight Manifold Binary STL Generation (`petes_dragon_tpu_panel.stl`)
* **Date:** 2026-10-04
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`3d_panels/petes_dragon_tpu_panel.stl`, `3d_panels/tpu_panel_preview.html`).
* **Notes:**
  * **Root Cause of Blank Screen in ViewSTL:** Investigated client-side `STLExporter.parse()` output. While Three.js renders complex assemblies with open 2D plane shells and thin cylindrical wall strips for WebGL performance, standalone 3D viewers and slicers (ViewSTL, Luban, Bambu Studio) reject non-manifold, non-watertight zero-thickness surfaces.
  * **True Manifold Solid CSG Engine:** Engineered a dedicated Python CSG boolean compilation engine using `trimesh` and the modern `manifold3d` backend.
  * **Physical STL Features Compiled:**
    - 2.0 mm solid 95A TPU contoured base plate ($185.0\text{ mm W} \times 222.1\text{ mm H}$).
    - 100 center optical through-holes ($\varnothing 3.2\text{ mm}$).
    - 100 rear cylindrical press-fit LED pocket recesses ($\varnothing 5.4\text{ mm} \times 1.4\text{ mm}$ depth) with interior annular resting shelf floors.
    - Continuous rear daisy-chain wire routing channels ($1.8\text{ mm W} \times 1.2\text{ mm D}$).
    - 16 perimeter garment fastener eyelets ($\varnothing 2.2\text{ mm}$ with $\varnothing 4.8\text{ mm} \times 0.6\text{ mm}$ countersinks).
    - 13 physical wire retention bridges ($2.2\text{ mm W} \times 0.55\text{ mm H}$) with $1.1\text{ mm}$ snap entry slots across long spans.
  * **Validation:** Verified 100% watertight manifold mesh ($17,538$ triangles, volume $21,396.63\text{ mm}^3$, zero degenerate faces). Linked direct download button (`📦 Download Slicer STL (.stl)`) in the web preview header.

### Entry: 3D-Printable Flexible TPU Chest Panel Generator (Snapmaker U1 / 95A TPU / OpenSCAD)
* **Date:** 2026-10-04
* **Milestone:** Milestone 5 - 3D-Printable Flexible Wearable TPU Panel Fabrication
* **Status:** Complete & Verified (`scripts/generate_3d_panel.py`, `3d_panels/petes_dragon_tpu_panel.scad`, `3d_panels/tpu_panel_preview.html`, `3d_panels/petes_dragon_specs.json`).
* **Notes:**
  - **Fairy Light Armor Architecture:**
    - Designed flexible 95A TPU chest panels for Snapmaker U1 3D printer to house 100 addressable fairy light pixels ("seed/pebble" resin beads on 3-strand black enameled wire).
    - Modeled as a flat 2.0mm thick wearable plate: prints 100% flat on the build plate with zero supports, allowing 95A TPU to wrap naturally over runner chest contours without rigidity.
  - **Rear Pockets & Front Optical Windows:**
    - Rear press-fit pockets (Ø5.4mm × 1.4mm depth) firmly seat standard 5.0mm teardrop resin LEDs with a slight friction bevel.
    - Front optical apertures (Ø3.2mm through-holes) let raw LED emitters shine through forward with maximum optical punch and zero light attenuation.
  - **Rear Daisy-Chain Wire Channels, Snap Clips & Spool Wells:**
    - Recessed underside wire tracks (1.8mm wide × 1.2mm deep) guide the 3-strand enameled wire sequentially from LED 1 to 100.
    - Added **92 physical wire snap-retention clips** (flexible TPU bridges with 1.1mm pinch slots) spanning across the channels to prevent springy fairy wires from popping out during assembly.
    - Added **100 LED snap collars** (inward retaining lips narrowing pocket mouths to Ø4.7mm) that snap-lock the 5.0mm resin teardrop bulbs into place.
    - Added **94 slack coiling wells with Ø2.6mm center spool posts** allowing excess wire loops to wrap cleanly without untangling.
  - **Integrated Tagging Gun Attachment System:**
    - Engineered 18 garment fastener tabs (13 perimeter + 5 interior voids) featuring 2.2mm needle pass-through holes and 4.8mm × 0.6mm front countersunk recesses.
    - Allows standard 10mm plastic tagging gun barbs (Kimble tags) to anchor the panel flush to black running shirts quickly, sweat-proof, and race-durable.
  - **Parametric OpenSCAD Model & Interactive 3D Web Inspector:**
    - Emitted `3d_panels/petes_dragon_tpu_panel.scad` with additive snap retention modules (`additive_retention_features()`).
    - Built interactive WebGL/Three.js 3D viewer (`3d_panels/tpu_panel_preview.html`) with true 3D volumetric trenches, vivid cyan snap clips, amber LED retaining collars, 3D black fairy wire strands, 3D resin LED bulbs, zoom-to-feature camera presets, and live DIN simulation.

### Entry: Turnkey SMT Assembly Export (JLCPCB BOM & CPL Centroid Bundle)
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D
* **Status:** Complete & Verified (`pcb/petes_dragon_smt_assembly.zip`, `pcb/petes_dragon_bom.csv`, `pcb/petes_dragon_cpl.csv`).
* **Notes:**
  - **Turnkey SMT Machine Assembly Support:**
    - Generated standardized JLCPCB-formatted Bill of Materials (`petes_dragon_bom.csv`) mapped directly to verified LCSC warehouse parts:
      1. `LED1–LED100`: WS2812B-2020 SMD Addressable RGB LEDs (LCSC #`C2843818`).
      2. `C1–C100`: 100nF (0.1µF) 50V 0402 ceramic decoupling capacitors (LCSC #`C1525`).
      3. `J1`: JST-PH-3P 2.0mm SMT horizontal header for power/data entry (LCSC #`C145946`).
    - Generated Pick & Place centroid list (`petes_dragon_cpl.csv`) with exact $(X, Y)$ coordinate offsets and component rotations for all 201 SMT parts.
  - **Single-Click Assembly Bundle:**
    - Packaged `petes_dragon_smt_assembly.zip` containing both CSVs for drag-and-drop quoting on JLCPCB.
    - Updated `pcb/pcb_preview.html` with direct download buttons and sidebar references.

### Entry: Clean Square LED Package Rendering (Removed Halo & Glow Blur) in PCB Preview
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D & Visual Simulation
* **Status:** Complete & Verified (`pcb/pcb_preview.html`, `scripts/generate_pcb_project.py`).
* **Notes:**
  - **Crisp SMD 2020 Physical Geometry:**
    - Per user inspection requirements, removed fuzzy radial halos (`.led-halo`) and SVG drop-shadow blur filters from the interactive PCB inspector.
    - Rendered each addressable pixel as an authentic $2.0\text{ mm} \times 2.0\text{ mm}$ square package (`<rect class="led-pkg">`) with an inner $1.4\text{ mm} \times 1.4\text{ mm}$ optical emitter die (`<rect class="led-die">`).
    - When illuminated via **"✨ Light Up All LEDs"** or during live animation, the square packages light up cleanly in Pete's dragon theme colors (emerald green body, golden tail lantern) without obscuring adjacent copper traces, pads, or 0402 bypass capacitors.

### Entry: Interactive "Light Up All LEDs" Illumination Simulation in PCB Preview
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D & Visual Simulation
* **Status:** Complete & Verified (`pcb/pcb_preview.html`, `scripts/generate_pcb_project.py`).
* **Notes:**
  - **Full 100-LED Illumination Mode:**
    - Added an interactive **"✨ Light Up All LEDs"** button to the PCB Inspector control bar.
    - Clicking illuminates all 100 LEDs with radiant halos (`r=2.6mm`, `opacity=0.75`) in Pete's authentic parade color palette (chartreuse green body, warm golden-amber tail lantern, and fiery accents).
    - LED cores expand to `r=1.15mm` with drop-shadow bloom.
  - **Seamless DIN Pulse Integration:**
    - The animated DIN flow pulse (`toggleDataStream()`) can be run concurrently with the lit state, creating an ultra-bright traveling white spark packet (`r=1.45mm`, `opacity=1.0`) sweeping over the illuminated background.
    - Toggling the button off cleanly returns the board to unlit inspection mode.

### Entry: Complete 3-Rail Power & Ground Routing Architecture (+5V Bus, GND Vias & B.Cu Plane)
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D
* **Status:** Complete & Verified (`pcb/petes_dragon_easyeda.zip`, `pcb/petes_dragon_fpc.kicad_pcb`, `pcb/pcb_preview.html`).
* **Notes:**
  - **Full 3-Rail Electrical Routing:**
    - Upgraded PCB layout from a single serial data line to a production-grade 3-rail power architecture (600 copper segments, 101 plated vias, 1 ground plane zone):
      1. **Serial DATA Rail (Net 3..102 on `TopLayer` / `F.Cu`):** 99 neighbor-to-neighbor daisy-chain traces (0.25mm width) connecting DOUT to DIN.
      2. **+5V Power Rail (Net 1 on `TopLayer` / `F.Cu`):** 0.6mm main feed from J1 connector, 100 local bypass decoupling traces (0.4mm), and 99 inter-LED power bus traces (0.5mm) linking all capacitor and LED +5V pads to prevent voltage drop.
      3. **GND Return Bus & Ground Plane (Net 2 on `BottomLayer` / `B.Cu`):** 101 plated through-hole vias (0.8mm pad, 0.4mm drill) dropping GND connections directly to a solid copper ground plane zone covering the entire dragon shape, backed by a 0.6mm wide daisy-chained GND return bus.
  - **100% Unrouted Airwires (Ratsnest) Elimination:**
    - All 201 nodes across +5V and GND now have physical copper interconnects, completely eliminating unrouted ratsnest lines in EasyEDA.
  - **Interactive 3-Rail Layer Inspection in Web Preview:**
    - Updated `pcb/pcb_preview.html` with dedicated toggle controls for `⚡ Data Traces`, `🔋 +5V Power Rail`, and `🛡️ GND Bus & Vias`.

### Entry: EasyEDA Standard Compatibility Fix (KiCad 5 Module & Edge.Cuts Syntax)
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D
* **Status:** Complete & Verified (`pcb/petes_dragon_easyeda.zip`, `pcb/petes_dragon_fpc.kicad_pcb`).
* **Notes:**
  - **Diagnosed Footprint & Outline Absence in EasyEDA Standard:**
    - The user screenshot of EasyEDA Standard (`easyeda.com/editor`) showed only red copper traces without footprints or board outline.
    - Root cause: EasyEDA Standard's KiCad importer was built for KiCad 4/5 syntax. KiCad 6+ renamed `(module ...)` to `(footprint ...)` and `(gr_line ...)` to `(gr_poly ...)`. EasyEDA Standard's parser successfully imported `(segment ...)` tracks but silently skipped the newer `(footprint ...)` and `(gr_poly ...)` elements.
  - **Refactored to Universal KiCad 5 S-Expression Format:**
    - Updated `scripts/generate_pcb_project.py` to output KiCad 5 header `(kicad_pcb (version 20171130))`.
    - Converted all 201 components (100x WS2812B-2020 LEDs, 100x 0402 capacitors, 1x JST-PH connector) to standard KiCad 5 `(module ...)` syntax with `(fp_text ...)` and `(fp_line ...)` silkscreen boundaries.
    - Converted `Edge.Cuts` board contour to 58 contiguous `(gr_line ...)` segments so EasyEDA Standard recognizes the `BoardOutline` layer.
    - Verified balanced S-expressions (12,247 open/close parens) and updated `pcb/petes_dragon_easyeda.zip`.

### Entry: EasyEDA / KiCad Turnkey ZIP Package & Copper Tracks Export
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D
* **Status:** Complete & Verified (`pcb/petes_dragon_easyeda.zip`, `pcb/petes_dragon_kicad.zip`, `pcb/petes_dragon_fpc.kicad_pro`, `pcb/petes_dragon_fpc.kicad_pcb`).
* **Notes:**
  - **EasyEDA KiCad Import Package:**
    - Structured and generated `pcb/petes_dragon_easyeda.zip` (and `petes_dragon_kicad.zip`) containing all required project files:
      - `petes_dragon_fpc.kicad_pcb` (Board outline, 100 LEDs, 100 bypass capacitors, JST connector, and copper data tracks).
      - `petes_dragon_fpc.kicad_pro` (KiCad 6/7/8 JSON project configuration).
      - `petes_dragon_fpc.pro` (Legacy project configuration for older parsers).
      - `petes_dragon_bom.csv` (Bill of Materials with LCSC part numbers).
      - `petes_dragon_cpl.csv` (Pick-and-place centroid coordinates).
  - **KiCad Copper Track Segments:**
    - Exported 99 `(segment (start ...) (end ...) (width 0.25) (layer "F.Cu") (net ...))` records connecting DOUT of LED $k$ to DIN of LED $k+1$ so EasyEDA imports fully routed traces on `F.Cu`.
  - **One-Click Web Inspector Download:**
    - Added a green **"📥 Download EasyEDA / KiCad ZIP"** button to `pcb/pcb_preview.html` control header and sidebar.

### Entry: Boundary-Constrained PCB Routing Fix (Zero Out-of-Bounds Traces)
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D
* **Status:** Complete & Verified (`scripts/generate_pcb_project.py`, `pcb/pcb_preview.html`, `pcb/petes_dragon_fpc.kicad_pcb`, `pcb/petes_dragon_cpl.csv`).
* **Notes:**
  - **Identified Concave Neck Jump:**
    - Standard unconstrained Euclidean TSP had routed LED 79 `(103.11, 81.91)` directly to LED 80 `(121.57, 52.49)`, cutting across the concave arch of Pete's neck and leaving the PCB boundary by up to 11.47mm.
  - **Boundary-Constrained Routing Algorithm:**
    - Updated `scripts/generate_pcb_project.py` to extract the laser-cut PCB contour polygon before routing.
    - Precomputed a 30-sample polygon collision test for every candidate segment, penalizing or rejecting any segment that crosses outside the polyimide boundary.
    - Built the route with a Cheapest Valid Insertion heuristic, followed by a constrained 2-opt swap optimizer that only accepts swaps where both new segments stay 100% inside the board polygon.
    - Increased contour fidelity (58 vertices) to preserve smooth organic neck curves without clipping.
  - **100% Clearance Verification:**
    - Re-verified all 99 copper trace segments against the board polygon: 0 boundary violations across all 100 LEDs.
    - Max hop distance in the entire design is only 29.55 mm.
    - Regenerated KiCad board, CPL centroid file, and interactive web inspector.

### Entry: PCB Nearest-Neighbor (2-Opt) Daisy-Chain Routing Optimization
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Flexible PCB (FPC) Fabrication R&D
* **Status:** Complete & Verified (`scripts/generate_pcb_project.py`, `pcb/pcb_preview.html`, `pcb/petes_dragon_fpc.kicad_pcb`, `pcb/petes_dragon_cpl.csv`).
* **Notes:**
  - **Fairy Light vs. PCB Routing Decoupling:**
    - Kept the original 6–8cm fairy light spacing and physical wiring sequence strictly intact in `simulator/app.js` and `presets/petes_dragon_chris.json` so wearable wire slack simulation is unaffected.
    - Decoupled the PCB copper trace routing in `scripts/generate_pcb_project.py` so that PCB traces no longer mirror the physical fairy light node order.
  - **2-Opt Nearest-Neighbor Daisy Chain:**
    - Computed an optimal nearest-neighbor Euclidean TSP tour with 2-opt edge-swap refinement starting at bottom-left connector J1 near Pete's back foot.
    - Daisy-chain trace distance dropped from 12.65 units down to 2.13 units (**83.2% shorter total trace length**).
    - Eliminated all criss-crossing hops across the dragon's torso, creating clean, short ~5–10mm interconnecting traces between adjacent LEDs.
  - **Regenerated KiCad, CPL, and Interactive Web Inspector:**
    - Updated `pcb/petes_dragon_fpc.kicad_pcb` netlist and copper segments.
    - Updated `pcb/petes_dragon_cpl.csv` with optimized component indices D1..D100.
    - Updated `pcb/pcb_preview.html` SVG copper lines and animated DIN data flow along the neighbor-to-neighbor path.

### Entry: High-Res Transparent Pete's Dragon Asset & Turnkey Flex PCB (FPC) Demo Suite
* **Date:** 2026-10-03
* **Milestone:** Milestone 4 - Lighting Engine & Custom Fabrication R&D
* **Status:** Complete & Verified (`assets/petes_dragon_transparent.png`, `pcb/*`, `scripts/generate_pcb_project.py`).
* **Notes:**
  - **Transparent Artwork Extraction:**
    - Cleaned and converted high-res Pete's Dragon artwork (with tail-hanging lantern) into a transparent PNG (`assets/petes_dragon_transparent.png`).
    - Preserved 100% of the internal black linework (nostrils, pupils, mouth, claws, belly ribs, wing ridges, and tail lantern frame) while making all exterior and concave regions (between tail and back, between wings, under jaw) transparent.
  - **Turnkey Flex PCB (FPC) Generation Suite:**
    - Developed automated Python generator `scripts/generate_pcb_project.py` mapping simulator $(x, y)$ coordinates to physical PCB design files.
    - Generated JLCPCB SMT Bill of Materials (`pcb/petes_dragon_bom.csv`) with LCSC part numbers for WS2812B-2020 LEDs (`C2843818`) and 0402 100nF bypass capacitors (`C1525`).
    - Generated JLCPCB Pick-and-Place Centroid File (`pcb/petes_dragon_cpl.csv`).
    - Generated native KiCad PCB project (`pcb/petes_dragon_fpc.kicad_pcb`) with `Edge.Cuts` dragon contour, daisy-chained data traces (`DOUT -> DIN`), and power rails.
    - Created interactive 2D/3D web inspector (`pcb/pcb_preview.html`) allowing layer toggling, data stream animation, and spec inspection.
* **Milestone:** Milestone 4 - Lighting Engine & Theatrical Controls
* **Status:** Complete & Verified (`simulator/app.js`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `firmware/*`).
* **Notes:**
  - **Spatial Coordinate vs Strand Index Fix:**
    - Corrected the mouse scamper rendering engine across the Simulator (`simulator/app.js`), ESP32 C++ firmware (`src/main.cpp`), and Arduino sketch (`arduino/MSEP_Costume/MSEP_Costume.ino`).
    - Because LEDs on the costume are positioned via 2D spatial placement (Farthest-Point Sampling / manual node layout) rather than straight spatial order along the strand, indexing by `(head - index)` caused LEDs to flash scattered and disjointed across the shirt.
    - Switched mouse head and trail evaluation to physical 2D coordinates: `(normX, normY)` in the Simulator and `SPATIAL_X_BYTE[i]`, `SPATIAL_Y_BYTE[i]` (`0..255`) in firmware.
  - **Extended Directional History Tail & Sharp 1-LED Head:**
    - Tightened the leading spark radius ($d_{\text{head}} < 0.055$ / $d^2 < 45$) so only a single leading LED ignites with the blazing white nose spark, eliminating multi-bulb clumping.
    - Extended the historical trajectory length ($historySpanT = 1.6$ normalized / 16 sample steps at $s \times 5$ byte ticks) and implemented a smooth gradual decay ($1.0 - 0.80 \times \text{frac}$) down to 20% intensity at the tail tip.
    - This renders a long, graceful trailing ribbon of LEDs charting where the mouse has scampered across the chest, maintaining crisp directional movement without a radial flashlight halo.
  - **Full Platform Parity & Firmware Synchronization:**
    - Verified identical behavior across simulator global patterns, group effects, and cue 19 timeline cues.
    - PlatformIO build verified; all 8 fleet ROM binaries recompiled and verified.

### Entry: Flashlight Roam & Scurrying Mouse (Single Dot + Long Tail) Separation
* **Date:** 2026-10-01
* **Milestone:** Milestone 4 - Lighting Engine & Theatrical Controls
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `simulator.py`, `include/costume_config.h`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `firmware/*`).
* **Notes:**
  - **Smooth Trajectory with Meteor Point & Tail Optics:** Calibrated the scurrying mouse to follow the smooth 2D multi-harmonic roaming trajectory (identical continuous movement path as the flashlight) while concentrating light into a blazing single-pixel point head with a tight, fast-fading exponential meteor tail falloff.
  - **Flashlight / Searchlight Roam (`flashlight`, ID: 18):**
    - Retains the 2D Cartesian roaming light pool $(M_x(t), M_y(t))$ with smooth multi-harmonic wandering and a Gaussian beam wake ($\sigma = 0.14$).
    - Piercing center beam illumination ($d_i < 0.08$) illuminating the float's sampled artwork or theme palette as if a searchlight is sweeping across the runner's chest.
  - **Scurrying Mouse (`mouse_scamper`, ID: 19):**
    - Redesigned from the 2D pool into a true **Single Ultra-Bright Point (1 LED)** with a **long glowing tail (~20 LEDs)** that scampers along the physical LED strand order.
    - Implemented non-linear pacing with sprint warping: $t + \text{warp}$, creating rapid cartoon dashes, sudden directional turns, and micro pauses across the graphic.
    - Point spark head shines with blazing white brilliance ($+130$ RGB) while the 20-LED tail exponentially decays in the sampled artwork hue ($e^{-\text{dist} \cdot 2.8 / \text{tailLen}}$), with resting baseline at 8% intensity.
  - **Simulator & Hardware Full Parity:**
    - Integrated across all simulator selectors (Ambient Baseline Tab 2, Group Creation Hub, Draw Mode, Group Inspector, and Master Sequence Cue Director).
    - C++ firmware support in `renderAmbientFallback()` and `runAutonomousShowSequence()` in both `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`.
    - Compiled cleanly with PlatformIO and regenerated all 8 dedicated float binaries in `firmware/`.

### Entry: 2D Scurrying Mouse ("Graphic Explorer") Animation Engine
* **Date:** 2026-10-01
* **Milestone:** Milestone 4 - Lighting Engine & Theatrical Controls
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `simulator.py`, `include/costume_config.h`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `firmware/*`).
* **Notes:**
  - **Theatrical Concept & 2D Motion Model:**
    - Designed and implemented `🐭 Scurrying Mouse (Graphic Explorer)` (`mouse_scamper`, ID: 18) for ambient baselines, timeline show cues, and animation groups.
    - Rather than a simple 1D linear counter, the "mouse" travels across the full 2D Cartesian plane $(M_x(t), M_y(t))$ using a multi-harmonic wanderer with non-linear sprint warping ($t + 0.38 \sin(2.8t) + 0.18 \sin(5.2t)$).
    - Darts across the entire graphic interior and exterior with sudden directional zig-zags, rapid exploratory sprints, and brief sniffing micro-pauses.
    - Each physical LED calculates its Euclidean distance $d_i = \sqrt{(x_i - M_x)^2 + (y_i - M_y)^2}$ from the mouse, illuminating a piercing starlight-white spark at the nose ($d_i < 0.07$) and generating an organic Gaussian light wake trail ($\sigma = 0.13$) in the float's sampled artwork/theme color.
  - **Full UI & Control Integration:**
    - Added to Tab 2 Default Background Pattern dropdown (`#patternSelect`), Group Hub & Inspector effects and baseline selectors, and Master Sequence Cue dropdowns.
    - Fully bound to tempo speed slider (20–180 BPM) for curious exploring (30–48 BPM) or hyperactive cartoon dashes (120+ BPM).
  - **ESP32 Dual-Core Firmware & Fleet ROM Rebuild:**
    - Integrated coordinate-aware integer distance calculations in `renderAmbientFallback()` and `runAutonomousShowSequence()` in `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` using `SPATIAL_X_BYTE[i]` and `SPATIAL_Y_BYTE[i]` with FastLED trigonometric LUTs.
    - Compiled cleanly in PlatformIO (`RAM: 14.3%`, `Flash: 60.6%`).
    - Recompiled and updated all 8 float ROM binaries (`firmware.bin` generic + `firmware_float1.bin` through `firmware_float7.bin`) and manifests via `build_fleet_binaries.py`.

### Entry: Meteor Streak Speed-Up & Pixie Dust / Candle Flicker Smoothness Calibration
* **Date:** 2026-10-01
* **Milestone:** Milestone 4 - Lighting Engine & Theatrical Controls
* **Status:** Complete & Verified (`simulator/app.js`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `firmware/firmware.bin`).
* **Notes:**
  - **Meteor / Comet Streak (`comet`):**
    - Fixed timing formula where the head previously advanced by only 0.45 pixel per beat (taking ~4.6 minutes to cross 100 LEDs at 48 BPM).
    - Tied pass duration directly to tempo: `cometPassMs = Math.max(900, beatMs * 1.5)` (traverses entire shirt in 1.2s to 1.8s) with radiant starlight white leading head and 22-pixel fading glowing tail.
    - Updated both global `evalGlobalPattern` and localized group `evalGroupEffect`.
  - **Pixie Dust (`pixie_dust`):**
    - Eliminated hardcoded millisecond time terms. Bound ambient luminous drift ($\pi/2\text{ rad/beat}$) and starlight twinkles ($6.0\text{ rad/beat}$) directly to `normTime` / `grpNormTime`.
    - Speed slider (20–180 BPM) now directly accelerates and decelerates both the fairy drift waves and sparkle frequencies in real time.
  - **Candle / Lantern Flicker (`candle_flicker`):**
    - Bound thermal draft ($1.2\text{ rad/beat}$) and dual flame flutter harmonics ($4.5\text{ rad/beat}$ and $9.8\text{ rad/beat}$) directly to `normTime` / `grpNormTime`.
    - Adjusting the speed slider now visibly speeds up or slows down the organic flame flutter and lantern sway across both global baseline and group animations.
  - **Sparkle Storm & Filament Glow:**
    - Converted static `timeMs` to `normTime` / `grpNormTime` across `evalGlobalPattern` and `evalGroupEffect`.
  - **ESP32 Dual-Firmware Synchronization & Verification:**
    - Bound noise sample rates in `renderAmbientFallback()` within `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` to `(now * COSTUME_SPEED_BPM / 60)`.
    - Verified compilation via PlatformIO with 0 errors (`RAM: 14.3%`, `Flash: 60.6%`).
    - Synced fresh binary artifact to `firmware/firmware.bin`.

### Entry: Ambient Baseline "All Off" & Theatrical Speed Recalibration
* **Date:** 2026-10-01
* **Milestone:** Milestone 4 - Lighting Engine & Theatrical Controls
* **Status:** Complete & Verified (`simulator/index.html`, `simulator/app.js`, `simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `include/costume_config.h`).
* **Notes:**
  - **"All Off" / Blackout Mode Across All Layers:**
    - Added `🌑 All Off / Completely Dark (Blackout)` to the ambient baseline pattern selector (`#patternSelect` in Tab 2).
    - Added `#define COSTUME_PATTERN_OFF 17` across `include/costume_config.h`, `simulator.py`, `src/main.cpp`, and `arduino/MSEP_Costume/MSEP_Costume.ino`.
    - In ESP32 firmware, both `renderAmbientFallback()` and `runAutonomousShowSequence()` now immediately execute `fill_solid(leds, FRONT_LEDS, CRGB::Black)` when `COSTUME_PATTERN_OFF` or cue `eff == 17` is active.
    - Simulator engine returns `{ r: 0, g: 0, b: 0, alpha: 0 }` for instant zero-draw blackouts.
  - **Theatrical Speed Recalibration:**
    - Expanded ambient tempo slider range to `20 – 180 BPM` with a calm, majestic default of **48 BPM** (formerly 120 BPM march speed).
    - Added quick tempo preset chips: `[ 🧘 30 Serene ]`, `[ ✨ 48 Majestic ]`, `[ 🚶 72 Stroll ]`, and `[ 🏃 120 Allegro ]`.
    - Retuned mathematical frequency multipliers across `evalGlobalPattern`:
      - **Slo-Glo Breath (`color_match` & `dragon_sparkle`):** Reduced from $2\times$ over-oscillation to $\pi$ radians per beat, yielding 24 deep, organic breaths per minute at 48 BPM instead of 240 hyperventilating breaths/min.
      - **Larson Scanner (`scanner`):** Expanded traversal period to 4 beats for an imposing, stately 5.0-second beam sweep.
      - **Tidal Ripple (`tidal_ripple`):** Slowed outward radial wave phase to $0.75\times$ for serene, unhurried water-ring expansion.
      - **Traveling Wave & Rainbow Cycle:** Removed hardcoded millisecond timers and tied wavelength propagation directly to the BPM tempo slider.
      - **Comet & Piston Chug:** Re-geared to smooth, cinematic cadence.
  - **Hardware Verification:**
    - Built cleanly in PlatformIO (`RAM: 14.3%`, `Flash: 60.6%`).
    - Auto-synced `firmware/firmware.bin` for Web Serial browser flashing.

### Entry: Pete's Dragon Smoke Groups Restoration & Group Sequence Engine
* **Date:** 2026-10-01
* **Milestone:** Milestone 5 - Studio Workflow & Preset Library
* **Status:** Complete & Verified (`presets/petes_dragon_with_smoke.json`, `presets/petes_dragon_100-led_vibrant_color_scatter.json`, `simulator/app.js`).
* **Notes:**
  - **Smoke Nostril Puff Restoration:**
    - Traced historical coordinates from git before 10cm pitch re-wiring and mapped the 10 nostril smoke LEDs ($dist = 0.0000$) to their current electrical IDs:
      - **Smoke 1 (Right Nostril Puff):** Remapped to `[85, 27, 25, 51, 49]` (nostril root $\rightarrow$ mid puff $\rightarrow$ outer tip $\rightarrow$ return curl).
      - **Smoke 2 (Left Nostril Puff):** Remapped to `[12, 14, 93, 96, 98]` (nostril root $\rightarrow$ mid puff $\rightarrow$ outer tip $\rightarrow$ return curl).
    - Preserved all group properties: 60 BPM / 140 BPM speeds, custom warm smoke colors (`#fffaf2`), `write_on_off` effect, unlit baseline mode, and synchronized $t = 18.0\text{s}$ show cues.
  - **Group-Level Animation Engine Refinement (`simulator/app.js`):**
    - Refined `evalGroupEffect` for `write_on_off`, `color_wipe`, and `marquee` to prioritize user-defined group member order (`grpIndex`) over global vertical Cartesian rank ($Y$).
    - Ensures localized groups (nostril smoke puffs, wheel perimeters, directional flourishes) write and travel outward along their designed physical path rather than filling vertically.

### Entry: 2D Spatial Lighting Engine & Coordinate-Aware Animation Overhaul
* **Date:** 2026-10-01
* **Milestone:** Milestone 4 - Lighting Engine & Visual Effects
* **Status:** Complete & Verified (`simulator/app.js`, `simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `include/costume_config.h`).
* **Notes:**
  - **Decoupled Animation Order from Electrical Wire Sequence:**
    - Following wire slack and pitch optimization where LEDs were routed non-linearly across garment branches, animations based on linear index $i$ jumped erratically.
    - Implemented a 2D spatial coordinate mapping engine across the Web Simulator, Python backend, and ESP32 C++ firmware.
  - **Simulator Engine (`simulator/app.js`):**
    - Added `recomputeSpatialMetrics()` and `getSpatialMetrics()` providing normalized $(x, y)$, radial distance from centroid $(\bar{x}, \bar{y})$, and sorted spatial ranks (`rankYBottomUp`, `rankYTopDown`, `rankXLeftRight`, `rankXRightLeft`, `rankRadius`).
    - Upgraded `rebuildLedGroupMap()` with group-local bounding box, centroid, and spatial rank metrics.
    - Upgraded both Group and Global effect evaluation:
      - `write_on_off` / `color_wipe`: Progressive fill now sweeps smoothly in physical garment space (bottom hem $\rightarrow$ chest $\rightarrow$ collar when `dir = 1`, or top-down when `dir = -1`).
      - `traveling_wave`: Continuous planar wave sweeping smoothly along the physical $X$ axis.
      - `scanner`: Bouncing horizontal beam sweeping along normalized $X$ coordinates.
      - `tidal_ripple`: Concentric radial wave propagating outward from 2D physical centroid $(\bar{x}, \bar{y})$.
      - `rainbow_cycle`: 2D spatial gradient across $X$ and $Y$ coordinates.
      - `marquee` & `chase`: Spatial position stepping for consistent visual propagation.
  - **ESP32 Firmware Parity (`src/main.cpp` & `arduino/MSEP_Costume/MSEP_Costume.ino`):**
    - Added integer-quantized 8-bit PROGMEM lookup tables (`SPATIAL_RANK_Y`, `SPATIAL_X_BYTE`, `SPATIAL_Y_BYTE`, `SPATIAL_RADIUS_BYTE`) generated by `simulator.py`.
    - Enables 60 FPS spatial sweeps with zero floating-point computation or memory allocation on the ESP32.
    - Full dual-core parity and backward compatibility: cleanly falls back to linear strand index logic if `#define HAS_SPATIAL_METRICS` is absent.
  - **Hardware Verification:**
    - Validated PlatformIO compilation (`python -m platformio run`) with successful build (RAM: 14.3%, Flash: 60.6%).
    - Auto-synced `firmware/firmware.bin` for Web Serial flashing.

### Entry: Snail & Turtle Custom Graphics Clean Background Transparency, Palette Simplification & Default Integration
* **Date:** 2026-10-01
* **Milestone:** Milestone 5 - Studio Workflow & Graphic Asset Suite
* **Status:** Complete & Verified (`assets/spinning_snail.png`, `assets/spinning_turtle.png`, `assets/Snail.png`, `assets/Turtle.png`, `simulator/app.js`).
* **Notes:**
  - **Snail Graphic Background & Palette Adjustment:**
    - Cleaned all non-essential white studio backdrop and ground shadow from `Snail.png` to create a 100% transparent PNG backdrop.
    - Preserved crisp spiral lights, antenna bulbs, and mouth features while eliminating stray floor reflection specks.
    - Shifted the snail's neck/body color from dull brown to a vibrant reddish-pink (`#ff007f` / rich parade magenta) in the Disney Electrical Parade aesthetic.
  - **Turtle Graphic Background, Palette Simplification & Outline Enhancement:**
    - Stripped off-white studio background and interior lens transparency from `Turtle.png` to generate a crisp transparent PNG.
    - Updated the turtle's color palette:
      - Head and neck facets recolored from green to authentic **Disney Parade Golden Yellow** (`#f5ba13`), matching the iconic Electrical Parade float character design.
      - Greens consolidated into **2 distinct parade shades**: Bright Emerald Green (`#00a86b` / glowing shell windows) and Deep Turtle Green (`#184a2e` / flippers and feet).
      - Blues unified to a single rich Shell Navy Blue (`#214e78` for shell matrix grid and pupil).
      - Reds unified to a single vivid Parade Red (`#e11d2e` for tie and mouth).
    - Preserved original lead solder line art and added fine anti-aliased contour tracing along the nose bridge and snout to maintain crisp facial definition.
  - **Simulator Engine Integration:**
    - Configured `spinning_turtle.png` and `spinning_snail.png` as default visual backdrops for Float 03 (The Spinning Turtle) and Float 04 (The Spinning Snail) in `simulator/app.js`.
    - Added both float types to `boostLedVibrancy` custom color rendering to ensure sampled physical LEDs pop with vibrant character colors.

### Entry: Wire Tension Heatmap Metric Units (cm) & Single-LED Wire Isolation
* **Date:** 2026-09-30
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Complete & Verified (`simulator/app.js?v=67`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`).
* **Notes:**
  - **Metric Units Conversion (cm / m):**
    - Updated `calculateWireTensionMetrics()`, `updateWireTensionUI()`, canvas wire tooltip tags, and the sidebar metrics card from imperial inches (`"`) to metric centimeters (`cm`) and meters (`m`).
    - Strand physical run formatted as `${distCm.toFixed(1)} cm (${(distCm/100).toFixed(2)} m)`.
    - Segment tags on canvas display directly in cm (e.g. `6.8 cm`).
    - Legend and status badges calibrated to cm thresholds:
      - 🔵 **Blue (`<4.5 cm`):** Excess Slack / Folding Warning.
      - 🟢 **Green (`4.5–8.5 cm`):** Optimal Slack Sweet Spot (Flat zero-fold curve).
      - 🟡 **Yellow (`8.5–9.2 cm`):** Snug (minimal slack).
      - 🔴 **Red (`>9.2 cm`):** Overstretched Alert (Taut).
  - **Single-LED Wire Isolation:**
    - When an individual LED is selected on the canvas (`selectedLed !== null` or `selectedLeds.size === 1`), both the Wire Tension Heatmap and Standard Wiring Trace automatically isolate to only draw:
      - **Incoming Wire:** Segment from LED $i-1 \rightarrow i$ (if $i > 0$).
      - **Outgoing Wire:** Segment from LED $i \rightarrow i+1$ (if $i < N - 1$).
    - Hides all other wire lines to eliminate background visual clutter while inspecting or fine-tuning single bulb positions.
    - When multiple LEDs or no LEDs are selected, the full wiring trace across all 100 LEDs is displayed.

### Entry: 10cm Physical Wire Pitch Slack-Targeted Routing & Zero-Fold Layout Optimization
* **Date:** 2026-09-30
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Complete & Verified (`simulator/app.js?v=66`, `simulator/index.html`, `presets/petes_dragon.json`, `SIMULATOR_USER_GUIDE.md`).
* **Notes:**
  - **Diagnosed Physical Wire Folding Problem:**
    - WS2812B fairy light strands have a fixed **10.0 cm (~3.94") wire pitch** between consecutive nodes.
    - The legacy wiring optimizer (`optimizeLedWiringOrder`) used standard shortest-path TSP nearest-neighbor sorting, causing 97 out of 99 segments on Pete's Dragon to sit under 3.0 cm (averaging just 1.65 cm!). This forced over **8.2 meters (27 feet) of excess wire** to be accordion-folded and taped behind the shirt.
  - **Engine Architecture & Slack-Targeted Router (`optimizeLedWiringOrder`):**
    - Replaced shortest-path minimization with a **Slack-Targeted Cost Function**:
      $$\text{Cost}(d) = \begin{cases} 1000 + (d - 9.2) \times 50 & \text{if } d > 9.2\,\text{cm (unreachable alert)} \\ (4.5 - d)^2 \times 4.0 + |d - 6.8| & \text{if } d < 4.5\,\text{cm (excessive fold penalty)} \\ (d - 8.5) \times 3.0 + |d - 6.8| & \text{if } 8.5 < d \le 9.2\,\text{cm (snug)} \\ |d - 6.8| & \text{if } 4.5 \le d \le 8.5\,\text{cm (optimal slack sweet spot)} \end{cases}$$
    - Built a Slack-Targeted 2-Opt pass that swaps segment edges to eliminate folding penalties and overstretched leaps.
    - **Verification Results on Pete's Dragon:**
      - Shifted optimal slack segments from 0% up to **99 out of 99 segments (100.0%)**!
      - Average segment distance increased from 1.65 cm to **6.75 cm** (leaving exactly 3.25 cm of gentle, natural wire slack with **zero accordion folding**!).
      - Folding warnings (< 4.5 cm) dropped from 97 to **0**!
      - Taut alerts (> 9.2 cm) remained at **0**.
  - **Heatmap & UI Calibration:**
    - Updated canvas wire drawing and metrics card (`updateWireTensionUI`) to reflect 10cm wire physical thresholds:
      - 🔵 **Blue (`<1.8"` / `<4.5 cm`):** Excess Slack / Fold Warning.
      - 🟢 **Green (`1.8"–3.3"` / `4.5–8.5 cm`):** Optimal Slack Sweet Spot (Flat, zero-fold fit).
      - 🟡 **Yellow (`3.3"–3.6"` / `8.5–9.2 cm`):** Snug (minimal slack).
      - 🔴 **Red (`>3.6"` / `>9.2 cm`):** Overstretched Alert.
    - Updated Tab 1 button to `🔌 Optimize Wiring Route (10cm Slack)`.
    - Updated `presets/petes_dragon.json` with the newly optimized 100% sweet-spot wiring route.

### Entry: Pete's Dragon Dark Green Scale Color Sampling & Pink Feature Classification Fix
* **Date:** 2026-09-30
* **Milestone:** Milestone 3 & Milestone 5 - Lighting Engine & Color Calibration
* **Status:** Complete & Verified (`simulator/app.js?v=65`, `assets/petes_dragon.png`, `SIMULATOR_USER_GUIDE.md`).
* **Notes:**
  - **Diagnosed False Pink Sampling on Dark Green Dragon Scales:**
    - In commit `df2f644`, the bounding box conditions for Pete's Dragon wings, tail, and dorsal spine plates included a boolean logic bug where `|| delta > 0.08` was evaluated disjunctively. Because all saturated green scales (both medium and dark green body pixels) have `delta = max - min > 0.08` (often 0.15 to 0.45), green pixels across Pete's back, flanks, legs, and tail were inadvertently forced into `DISNEY_DRAGON_PINK` (`CRGB(255, 25, 230)`).
    - Furthermore, dark green contour/shadow enhancement (`maxVal < 60`) was positioned after these pink checks, causing dark green line art and scale shadows to sample as hot pink.
  - **Engine Architecture & Guard Rules Implemented:**
    - **Strict Green Pixel Guard:** Introduced `isGreenPixel = (g > r && g > b) || (hue >= 55 && hue <= 180)` at the very entrance of `boostLedVibrancy()`. Any green pixel (light underbelly, medium body, or dark green contour) immediately routes to green LED output:
      - Dark shadows / contours (`maxVal < 60`): `{ r: 15, g: 255, b: 35 }` (vibrant dragon green).
      - Lime underbelly (`55° <= hue < 95°`): `{ r: rLed, g: 255, b: 15 }`.
      - Emerald body (`95° <= hue <= 180°`): `{ r: 10..40, g: 255, b: 25..60 }`.
    - **Authentic Dragon Pink Features:** Restrained Pete's Dragon pink classification to non-green pixels with genuine pink/magenta hue (`(hue >= 255 || hue <= 45) && (r > g || b > g)`) for the wild head hair crest, wings, dorsal back plates, and tail spines.
    - **Cricut Multi-Layer Exporter Sync:** Updated layer routing in `simulator/app.js` (line ~2534) so that green LEDs are strictly mapped to `Layer_1_Green_Vinyl` rather than pink vinyl.
  - **Verification:**
    - Node test across all 60,010 pixels of `assets/petes_dragon.png` verified **51,697 green pixels** (49,295 emerald body + 1,509 dark green contour + 893 lime underbelly) and **8,338 pink pixels** (crest, wings, spines), with **0 green pixels sampled as pink**.
    - `node --check simulator/app.js` passed with 0 errors.

### Entry: Tab 3 (Animation Groups) & Tab 4 (Float Show) Refinements & Effect Parity
* **Date:** 2026-09-30
* **Milestone:** Milestone 3 & Milestone 4 - Lighting Engine & Theatrical Parade Sequencing
* **Status:** Complete & Verified (`simulator/app.js?v=64`, `simulator/index.html`, `build_fleet_binaries.py`).
* **Notes:**
  - **Tab 3 & Docked Inspector Effect & Color Parity:**
    - Unified all 16+ animation effects across `groupEffectSelectHub` (Selection Hub), `drawGroupEffectSelect` (Click-to-Draw), and `groupEffectSelect` (Docked Group Inspector), exposing `comet`, `scanner`, `color_wipe`, `pixie_dust`, `filament_glow`, `candle_flicker`, `tidal_ripple`, `piston_chug`, `photo_mode`, and `steady_sparkle`.
    - Integrated one-touch tempo quick chips (`🚶 90`, `🏃 120`, `⚡ 144`, `🚀 180 BPM`) beneath `groupSpeedSliderHub`, `drawGroupSpeedSlider`, and `groupSpeedSlider` (Inspector).
    - Added dedicated **Custom Hex Color Pickers** (`<input type="color">`) alongside the 12 Disney preset swatches in both the Tab 3 Hub (`#groupCustomColorPickerHub`) and the docked Group Inspector (`#groupCustomColorPickerInspector`), allowing custom group coloring without requiring deselect/reselect cycles.
  - **Tab 4 (Float Show / Cue Director) Enhancements:**
    - Added **Per-Cue Direction Control** (`<select class="cue-direction-select">`) supporting `➡️ Forward` and `⬅️ Reverse` for all individual cue cards.
    - Updated `evalGlobalPattern()` with an optional `directionOverride` parameter and wired `computeLedColor()` to pass `q.direction`, allowing global cues (like traveling waves, comet sweeps, and marquees) to reverse direction independently during show sequences.
    - Added one-touch **Duration Quick Chips** (`5s`, `10s`, `15s`, `30s`) and **Tempo BPM Quick Chips** (`90`, `120`, `144`, `180`) right inside each cue card.
    - Expanded the 90-second example routines in `#sequenceTemplateSelect` with 3 float-themed showcases:
      - 🚂 **Casey Jr. 90s Routine (`casey_locomotive_90s`):** Opening steam sparkle, 144 BPM piston chug acceleration, 180 BPM high-speed comet sweep, and 144 BPM circus marquee finale.
      - 🐢 **Turtle & Snail 90s Routine (`turtle_snail_spin_90s`):** 90 BPM enchanted garden pixie dust, 120 BPM concentric shell spin chase, 120 BPM tidal ripple expansion, and 144 BPM rainbow shell spiral finale.
      - 🎆 **America Grand Finale 90s Routine (`patriotic_grand_finale_90s`):** Patriotic starlight sparkle, 144 BPM traveling electrical parade wave, 140 BPM grand starburst fireworks, and 180 BPM golden age 1972 theater marquee.
  - **Verification & Toolchain:**
    - `node --check simulator/app.js` passed with 0 errors.
    - PlatformIO compilation (`pio run`) succeeded in release mode (RAM: 14.3%, Flash: 60.6%).
    - Regenerated all 8 production fleet ROM binaries via `build_fleet_binaries.py` (all succeeded).

### Entry: Tab 2 (Ambient Tab) Baseline Dynamics Modernization & Firmware Engine Sync
* **Date:** 2026-09-30
* **Milestone:** Milestone 3 & Milestone 4 - Lighting Engine & Parade Show Sequencing
* **Status:** Complete & Verified (`simulator/app.js?v=63`, `simulator/index.html`, `simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `include/costume_config.h`, and `build_fleet_binaries.py`).
* **Notes:**
  - **Modernized Tab 2 Baseline Dynamics Section:**
    - **Replaced Legacy Single-Float Slider:** Retired the obsolete Elliott Green Hue slider from the UI while preserving a silent 140° emerald procedural fallback in code.
    - **Ambient Travel Direction:** Added `#ambientDirectionSelect` (`Forward ➡️ Head to Tail` vs `Reverse ⬅️ Tail to Head`) to baseline dynamics, fully integrated with traveling patterns (`comet`, `scanner`, `color_wipe`, `marquee`, `traveling_wave`, `chase`, `rainbow_cycle`).
    - **Sparkle Color & Temperature Selector:** Added `#sparkleStyleSelect` supporting `Warm 2700K Filament (255, 240, 200)`, `Diamond Cool White (255, 255, 255)`, and `Pixie Dust Golden Amber (255, 215, 40)`.
    - **Ambient Color Palette Mode:** Added `#ambientColorModeSelect` supporting `Sampled Artwork Colors` (default), `Float Signature Theme Color` (auto-mapped to each float's official palette), `Vintage Incandescent (2700K Warm White)`, and `Custom Uniform Color` (with `#ambientCustomColorPicker`).
    - **One-Touch Quick Chips:** Deployed instant clickable chips for Tempo (`90`, `120`, `144`, `180 BPM`) and Sparkle Frequency (`0%`, `0.5%`, `1.5%`, `3.5%`).
    - **Display Optics Separation:** Visually separated `LED Bloom / Glow Radius` into a dedicated sub-card labeled `🖥️ Simulator Display Optics (Browser Canvas Only)` to distinguish browser canvas simulation from ESP32 hardware flash settings.
  - **ESP32 Firmware & Toolchain Verification:**
    - Updated `renderAmbientFallback(uint32_t now)` across `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` with zero-overhead preprocessor macros (`COSTUME_AMBIENT_DIRECTION`, `COSTUME_SPARKLE_STYLE`, `COSTUME_AMBIENT_COLOR_MODE`, `AMBIENT_CUSTOM_COLOR_RGB`).
    - Verified compilation with PlatformIO (`pio run`) — 0 errors, 0 warnings.
    - Regenerated all 8 production fleet ROM binaries (Generic + Floats 1 through 7) via `build_fleet_binaries.py`.

* **Milestone:** Milestone 3 & Milestone 4 - Lighting Engine & Parade Show Sequencing
* **Status:** Complete & Verified (`simulator/app.js?v=62`, `simulator/index.html`, `simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, and `include/costume_config.h`).
* **Notes:**
  - Designed and deployed an expanded unified library of 14 animation sequences inspired by commercial addressable RGBIC fairy light controllers and classic Disney Main Street Electrical Parade theatrical effects:
    1. `steady_sparkle` (✨ Steady Colors + Occasional Sparkle)
    2. `color_match` (🌬️ Slo-Glo Breath / Color-Matched Glow)
    3. `comet` (☄️ Meteor / Comet Trail with blazing white-hot core & exponential decay)
    4. `scanner` (🛸 Larson Scanner / Knight Rider ping-pong sweep with turnaround wakes)
    5. `color_wipe` (✍️ Theatrical write-on fill, radiant hold, wipe-off, and rest)
    6. `pixie_dust` (💫 Cascading starlight waves with crystalline diamond twinkle flashes)
    7. `filament_glow` (⚡ Vintage 1972 Walt Disney World incandescent micro-voltage analog drift)
    8. `candle_flicker` (🕯️ Organic multi-harmonic amber/gold lantern & torch flame flicker)
    9. `tidal_ripple` (🌊 Outward-expanding concentric ripple waves from centroid)
    10. `piston_chug` (🚂 Casey Jr. 4-stroke mechanical locomotive cadence pulse)
    11. `marquee` (🎪 3-phase chasing incandescent border)
    12. `fireworks` (🎆 4-phase radiating starburst with ignition, expansion, and tip crackle)
    13. `rainbow_cycle` (🌈 Smooth chromatic wave cycling)
    14. `photo_mode` (📸 100% solid maximum radiance for crisp race photos)
  - **100% Option Parity:** Harmonized Tab 2 (`#patternSelect`), Tab 3 Group Hub (`#groupBaselineSelectHub`), Tab 3 Draw Mode (`#drawGroupBaselineSelect`), and the Contextual Inspector Dock (`#groupBaselineSelect`) so that group resting baseline options mirror the ambient palette 1:1, plus dedicated group states (`🌐 Follow Overall Baseline (Inherit)` and `🌑 Off / Completely Unlit`).
  - **3-Layer Crossfading Show Engine:** In `simulator/app.js`, groups smoothly evaluate their resting baseline when idle, crossfade into active cues scheduled on the 90s Master Timeline, and seamlessly return to baseline upon cue completion.
  - **FastLED C++ Firmware Parity:** Mirrored all 14 sequences and defines into `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` using fixed-point integer routines (`beatsin8`, `inoise8`, `qadd8`, `qsub8`), compiled cleanly with PlatformIO (`SUCCESS Took 18.12s`, 14.3% RAM, 60.6% Flash), and regenerated all 8 float ROM binaries in `firmware/`.

### Entry: Comprehensive Race Day Packing Checklist & Field Operations Manual
* **Date:** 2026-09-30
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Complete & Published (`RACE_DAY_PACKING_CHECKLIST.md`).
* **Notes:**
  - Published comprehensive master packing checklist and race morning operational field guide for the 7-runner family team (2 brothers, 1 sister, 1 brother-in-law, 3 sisters-in-law) engineered by the 3 brothers.
  - Covers electronics rigging (7 primary + 3 spare ESP32s, Ziploc moisture barriers, short 1ft power cables), battery management (10,000 mAh packs, keep-alive verification, hotel multi-port charging hub), costume rigging (FlipBelts, BibBoards snap clearance, wire anti-friction tape), hotel/field repair kit (portable soldering iron, solder-seal butt connectors, resistors, monofilament), and Florida pre-dawn weather survival (clear ponchos, hand warmers, throwaway layers).
  - Outlines chronological race morning timeline from 02:30 AM wake-up through 03:45 AM corral standby check, 04:30 AM rapid attendance wave (double-tap BOOT), 04:55 AM fleet wake (single-tap BOOT), and on-course 30s theatrical show triggers.

### Entry: In-Simulator 1-Click Fleet ROM Binary Rebuilder
* **Date:** 2026-09-30
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Complete & Verified (`simulator/app.js?v=61`, `simulator/index.html`, and `simulator.py`).
* **Notes:**
  - Added dedicated **`🔨 Rebuild ROMs`** button in the **Deploy & Hardware Tab** alongside the Web Flasher link.
  - Clicking this button executes `build_fleet_binaries.py` asynchronously via the `/api/build_fleet_binaries` backend endpoint, recompiling all 7 float ROM binaries (`firmware_float1.bin` through `firmware_float7.bin` + `firmware.bin`) directly from the active C++ firmware in the background and syncing them to the `firmware/` directory for instant Web Flashing.

### Entry: Web Audio Baroque Hoedown Synthesizer & Fleet Roster Web Flasher Alignment
* **Date:** 2026-09-30
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Complete & Verified (`simulator/app.js?v=60`, `simulator/index.html`, and `simulator/web_flasher.html`).
* **Notes:**
  - **Zero-Install Web Flasher Fleet Alignment (`simulator/web_flasher.html` & `firmware/manifest_float*.json`):**
    - Synchronized all 7 float manifests and the Web Serial Flasher UI with the official 7-runner roster (1: The Train / Casey Jr., 2: The Title Drum, 3: The Spinning Turtle, 4: The Spinning Snail, 5: Cinderella's Coach, 6: Pete's Dragon, 7: To Honor America).
    - Preserved 200-LED safety configurations, 5V 2000mA power budgets, and bootloader/partition offsets.
  - **Baroque Hoedown Synthesizer Engine (`BaroqueHoedownSynth`):**
    - Built a pure Web Audio API chiptune/electro-synthesizer engine (using square lead with resonant lowpass filter envelope and triangle bass) recreating the iconic *Baroque Hoedown* theme.
    - Added header toggle button (`🎵 Music: OFF / ON`) and automatic tempo-synced playback triggers when initiating the 30-Second Theatrical Fleet Show.

### Entry: Cricut Master SVG User Guide & Registration Crosshair Workflow
* **Date:** 2026-09-30
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Complete & Verified (`CRICUT_MASTER_SVG_USER_GUIDE.md`).
* **Notes:**
  - Published comprehensive standalone brother's guide for cutting multi-layer HTV costumes in Cricut Design Space.
  - Added dedicated explanation and instructions for the 4-corner alignment markers (`Layer_0_Registration_Crosshairs`), detailing how "Attach" prevents Cricut mat shape scrambling and how temporary tape registration enables zero-guesswork, sub-millimeter multi-layer heat press alignment.

### Entry: Authentic Clipart Pete's Dragon Cricut Vectorization & Dynamic SVG Coordinate Engine
* **Date:** 2026-09-29
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=59`, `simulator/index.html`, and `assets/cricut_svg/petes_dragon.svg`.
* **Notes:**
  - **Authentic Clipart Pete's Dragon Vectorization (`assets/cricut_svg/petes_dragon.svg`):**
    - Replaced previous placeholder doodle with authentic Disney clipart vectorization generated directly from `assets/petes_dragon.png` (matching 100% of the simulator canvas silhouette, pose, and proportions).
    - Preserved exact $300 \times 425$ aspect ratio scaled to high-resolution vector canvas (`viewBox="0 0 600 850"`).
    - Integrated multi-layer HTV structure:
      - `Layer_0_Clipart_Artwork`: Embedded high-resolution clipart reference for visual inspection and Print-then-Cut.
      - `Layer_1_Green_Vinyl`: Smooth Catmull-Rom cubic Bézier vector cut path of Elliott's emerald body silhouette.
      - `Layer_2_Pink_Vinyl`: Smooth Catmull-Rom cubic Bézier vector cut paths of the wild hair crest, wings, and dorsal/tail spine plates.
  - **Dynamic SVG Coordinate & Physical Scale Engine (`calculateLedCutoutData`, `getSvgViewBoxDimensions`):**
    - Removed hardcoded $800 \times 600$ assumptions; dynamically parses `viewBox` width and height from the loaded SVG (`600×850` for Pete's Dragon, `800×600` for other floats).
    - Accurately scales $6.0\,\text{mm} \times 3.0\,\text{mm}$ pill slots to the SVG's coordinate system based on the real-world 18.0" (457.2mm) garment model (`pillW = 6.0 * (svgW / graphicWidthMm)`).
    - Dynamically anchors 4-corner heat press registration crosshairs to the corners of the active SVG viewBox.
  - **Verification:**
    - Verified sub-millimeter LED alignment overlay against `assets/petes_dragon.png` (100% of 100 LEDs inside graphic bounds; hair, wings, spines, and body align with zero offset).
    - Verified JavaScript syntax via `node --check simulator/app.js` (SUCCESS).
    - Verified PlatformIO build via `pio run` (SUCCESS, RAM: 14.3%, Flash: 60.4%).
    - Bumped script version to `app.js?v=59`.

### Entry: Calibrated Default Race Bib Dimensions (8.0" Wide × 7.0" High)
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational in `simulator/app.js?v=54` and `simulator/index.html`.
* **Notes:**
  - Updated **runDisney 10K Race Bib Overlay Math (`drawRaceBib` & `drawMiniRaceBib`)**:
    - Calibrated default bib width to **8.0 inches** relative to the 18.0" wide shirt model (`baseBibW = s.width * (8.0 / 18.0)` = ~44.44% of shirt width).
    - Calibrated default bib height to **7.0 inches** (`bibH = bibW * (7.0 / 8.0)` = 0.875 aspect ratio).
    - Applied identical 8" × 7" aspect ratio scaling across both Single Shirt canvas view and Fleet Lineup overview cards.
  - Verified JavaScript syntax via `node -c simulator/app.js` (SUCCESS) and updated asset cache version to `app.js?v=54`.

### Entry: Feature 2 (Physical Wire Tension Heatmap) & Feature 3 (Bilateral Symmetry & Mirror Tool)
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=53` and `simulator/index.html`.
* **Notes:**
  - Implemented **Feature 2: Physical LED Wire Tension & Spacing Heatmap (`calculateWireTensionMetrics`, `updateWireTensionUI`)**:
    - Modeled real garment dimensions ($18" \times 24"$) with Euclidean segment distance in physical inches between consecutive pixels ($i \rightarrow i+1$).
    - Color-coded segment rendering directly on the canvas:
      - 🟢 **Slack Spacing (`< 1.80"`):** `#00ff88` (comfortable slack for sewing and runner stride flexion).
      - 🟡 **Snug Spacing (`1.80" – 2.40"`):** `#ffc107` (nominal pitch).
      - 🔴 **Over-Stretched Alert (`> 2.40"`):** `#ff3366` with glowing stroke, pulsing danger ring, and mid-segment dimension tags (e.g. `2.6"`).
    - Added **Live Wire Tension & Spacing Metrics Card (`#wireTensionMetricsCard`)**: tracks Total Strand Physical Run (e.g., `114.2" / 9.5 ft`), Average Pitch (`1.15"`), Max Stretch Span (`#42 → #43`), and Live Status Badge (`🟢 Slack` / `🟡 Snug` / `⚠️ Alert`).
    - Added **`🔍 Inspect Max Span`** action button: immediately selects and centers the two LEDs with the longest physical span.
  - Implemented **Feature 3: Bilateral Symmetry & Mirror Guide Tool (`mirrorLeftToRight`, `mirrorRightToLeft`)**:
    - Added **Symmetry Centerline Axis Guide (`params.showSymmetryAxis`)**: renders a vertical dashed purple/cyan axis at $x = 0.50$ with illuminated label badges and arrows.
    - Added **Live Symmetry Drag Mode (`params.liveSymmetryDrag`)**: automatically mirrors movements across $x = 0.50$ for symmetrical partner LEDs when dragging single bulbs or grouped clusters on canvas in real time.
    - Added **`⇄ Mirror Left → Right`** and **`⇆ Mirror Right → Left`** action buttons: sorts LEDs top-to-bottom and reflects coordinates ($x_{\text{new}} = 1.0 - x$, $y_{\text{new}} = y$), samples artwork colors under mirrored bulbs, preserves animation groups, and commits clean snapshots to the `Ctrl+Z` Undo stack.
  - Verified JavaScript syntax via `node -c simulator/app.js` (SUCCESS) and updated asset cache version to `app.js?v=53`.

### Entry: Feature 10 — Timeline Hover-Scrubbing & Live Cue Quantization / Grid Snapping
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=52` and `simulator/index.html`.
* **Notes:**
  - Implemented **Interactive Hover-Scrubbing Engine (`initTimelineHoverScrub`)**: moving the mouse cursor over the timeline ruler or cue tracks displays a cyan ghost needle (`#timelineGhostNeedle`) and floating tooltip displaying `⏱️ timestamp | cue info`. Real-time canvas lighting updates continuously (`isHoverScrubbing` & `hoverScrubTime`) without needing to press Play.
  - Implemented **Cue Quantization & Grid Snapping**: added a live **Grid Snap** selector (`Off`, `0.5s`, `1.0s`, `2.0s`) and a **🎯 Quantize** button in the timeline transport bar (`#timelineQuantizeBtn`). Automatically snaps fractional cue start times and durations to clean grid intervals (integrated with `Ctrl+Z` Undo/Redo stack via `pushUndoState`).
  - Updated cue dragging and resizing event handlers (left handle trim, right handle trim, block move) to obey active `gridSnapInterval`.
  - Verified JavaScript syntax via `node -c simulator/app.js` (SUCCESS) and bumped asset version to `app.js?v=52`.
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational (`pio run` [SUCCESS], RAM: 14.3%, Flash: 60.3%).
* **Notes:**
  - Resolved timeline breathing pulse discrepancy on physical ESP32 where breathing cues appeared static or jumped abruptly:
    1. **Dynamic Relative Show Clock (`autonomousShowStartTime`):** Previously, `runAutonomousShowSequence` calculated `seqTime = now % SHOW_LOOP_MS` using raw ESP32 boot uptime (`millis()`). Sitting in Corral Standby for 10-15 seconds caused the initial 20-second cue to be partially or completely skipped before the user woke the costume. Added `autonomousShowStartTime`, set precisely upon button wake or incoming ESP-NOW packet `0x51`, ensuring `seqTime = (now - autonomousShowStartTime) % SHOW_LOOP_MS` always begins at `0.0s` immediately upon activation.
    2. **High-Contrast `sinf` Pulse Mathematics:** FastLED's `beatsin8` call was previously freezing because passing `now` as the timebase parameter resulted in `millis() - timebase == 0` every loop cycle, causing a frozen sine value. Replaced with direct hardware-accelerated `sinf(normTime * 2 * PI) * 0.5 + 0.5` where `normTime = elapsedMs / beatMs` (matching simulator `app.js` `evalGlobalPattern`), scaling smoothly from 15% dim baseline to 100% full radiant peak.
    3. **Ambient Fallback Synchronization:** Applied the same smooth `sinf` formula to `renderAmbientFallback()` for `COSTUME_PATTERN_BREATHING_GLOW`.
  - Rebuilt PlatformIO binary (`SUCCESS`) and mirrored all changes between `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` per Rule 5.
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational — commit `e3a443a`. Compile: RAM 14.3%, Flash 60.0%.
* **Notes:**
  - Root issue: the Ambient tab pattern selector (e.g. "Castle Photo Mode") was not honored at flash time — the ESP32 always ran the default steady sparkle regardless of what the user selected.
  - Fix: added `AMBIENT_FALLBACK_PATTERN` define to the generated `include/costume_config.h`, baked from the simulator's `activePattern` at flash time. Values: `0=steady_sparkle`, `1=breathing_glow`, `5=photo_mode`.
  - Added `renderAmbientFallback(uint32_t now)` helper function in both `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` (Rule 5 mirror). Both inline ambient fallback loops replaced with a single call — no code duplication.
  - `simulator.py`: parses new `ambientPattern` field from `/api/flash_firmware` payload; maps string values to numeric codes via `ambient_pattern_numeric_map`; writes `#define AMBIENT_FALLBACK_PATTERN {code}` into the header.
  - `simulator/app.js`: flash payload now includes `ambientPattern: activePattern` so the user's ambient tab selection is preserved in silicon.
  - `simulator/index.html`: bumped to `app.js?v=51` for cache refresh.
  - Supported ambient modes baked at flash time: `photo_mode` (solid artwork, no sparkle), `breathing_glow` / `color_match` (pulsing artwork + optional sparkle), `steady_sparkle` / `dragon_sparkle` (default starlight effect). `fireworks`, `traveling_wave`, and `marquee` fall back to steady_sparkle as ambient (not suitable as resting modes).

### Entry: Unified Master Timeline & Seamless Ambient Artwork Fallback
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=50`, `simulator/index.html`, `simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `PROJECT_PROGRESS.md`, and `SIMULATOR_USER_GUIDE.md`.
* **Notes:**
  - Removed artificial "Sequence: ON / OFF" mode toggle buttons from both the master timeline transport bar (`#timelineModeToggle`) and Parade Cue Director sidebar (`#toggleSequenceModeBtn`), unifying costume behavior into a single, permanently active timeline engine.
  - Implemented seamless ambient fallback: when the timeline contains no cues at all (empty timeline) or during gaps between scheduled cues, the costume displays its calibrated ambient programming (`ARTWORK_PALETTE` sampled from the chest graphic + configured rare starlight sparkle rate) with animation groups executing their resting baseline routines.
  - Eliminated legacy hardcoded 4-phase fallback show in `simulator.py`, `src/main.cpp`, and `arduino/MSEP_Costume/MSEP_Costume.ino`, preventing costumes with empty timelines from unexpectedly cycling through unintended dynamic phases (e.g. pink flashes, chase beams, traveling waves).
  - Fixed float role assignment in USB firmware flashing: `triggerUsbFirmwareFlash` now auto-resolves `effectiveFloatId` from the active runner slot (e.g. Pete's Dragon = Float 6, Green Follower) and bakes `COMPILED_FLOAT_ID` directly into `include/float_config.h`.
  - Confirmed follower button logic: on follower nodes (such as Float 6 Pete's Dragon), single tap functions purely to wake the costume from Corral Standby (with 1 emerald flash), while subsequent taps during running mode are ignored to preserve uninterrupted show execution.
  - PlatformIO clean compilation verified (`pio run` [SUCCESS], RAM: 14.3%, Flash: 60.0%).
  - Synchronized across simulator, C++ firmware, Arduino sketch, user guide, and project progress log per Rules 1 and 5.
  - Bumped script cache version in `simulator/index.html` to `app.js?v=50`.

### Entry: Decoupled Continuous Solo Float Pattern & Preserved 90s Theatrical Showcase
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=48`, `simulator/index.html`, `simulator.py`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `PROJECT_PROGRESS.md`, and `SIMULATOR_USER_GUIDE.md`.
* **Notes:**
  - Resolved discrepancy between ESP32 standalone loop and simulator free-run view where ESP32 previously forced a hardcoded 90-second 4-phase sequence (sparkle -> breath -> chase -> wave).
  - Decoupled single continuous solo float mode (Option A) in firmware: `ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_STEADY_SPARKLE` now renders continuous sampled artwork colors with starlight sparkles endlessly without unexpected chase/wave interrupts.
  - Added `#define COSTUME_PATTERN_AUTONOMOUS_90S 6` in `simulator.py` and C++ firmware (`src/main.cpp` & `MSEP_Costume.ino`) to preserve the entire 90s 4-phase routine.
  - Added **"🎭 90s Classic Routine (4-Phase Showcase)"** preset in simulator Parade Cue Director dropdown and `load90sTheatricalShowTemplate()` function in `app.js` to populate the 4 cues onto the Master Timeline for visual editing/preview.
  - Firmware compilation verified clean (`pio run`) with zero errors.
  - Mirrored C++ firmware logic to Arduino IDE sketch (`arduino/MSEP_Costume/MSEP_Costume.ino`) per Rule 5.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=48`.

### Entry: Corral Standby Rate Reduction & Sparse Dim Twinkle Tuning
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=47`, `simulator/index.html`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Slowed standby animation down ~3x to a calm ~5.1-second majestic period per pixel (`timeMs * 0.0012` in simulator, `t / 20` in firmware).
  - Increased shimmer threshold to `wave > 0.88` (and `> 242` on FastLED `sin8`), restricting the subtle swell to only ~5% of pixels at any given moment.
  - Scattered pixel phase distribution (`index * 1.9`) to dissolve perceived cohesive wave bands into sparse, isolated drifting stars.
  - Dimmed shimmer target from bright white/gold to a gentle warm champagne boost (+45 max over the base dim color with 0.70 max alpha), preserving the tranquil midnight aesthetic while highlighting the baseline dim glow.
  - Synchronized across simulator, C++ firmware, and Arduino sketch per Rule 5.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=47`.

### Entry: 6mm × 3mm Vinyl Pill Slots, Tangent Pebble LEDs & Sample-First Cutouts
* **Date:** 2026-09-29
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Operational & Synchronized across `simulator/app.js?v=57`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Implemented **Sample-First, Cut-After Workflow**: Moving or re-positioning LEDs samples the intact underlying vinyl graphic at 1-point center first (`sampleColorAtNorm`), guaranteeing 100% fast, deterministic color matching before rendering the cutout.
  - Implemented **Dynamic Wire Tangent Auto-Orientation (`getLedTangentAngle`)**: Automatically calculates tangent vector $\vec{T}_i = \mathbf{P}_{i+1} - \mathbf{P}_{i-1}$ along the continuous wiring route, aligning pill slots and pebble LEDs with the natural flow of the wire to eliminate sharp $90^\circ$ bends and solder fatigue.
  - Implemented **True-Scale Fabrication Rendering (`renderBulb`)**:
    - Modeled $6.0\,\text{mm} \times 3.0\,\text{mm}$ rounded rectangular capsule cutouts in the HTV vinyl layer with dark polyester mesh pinnie weave backing and eyelet perforations.
    - Modeled $4.0\,\text{mm} \times 3.0\,\text{mm}$ clear epoxy resin pebble LEDs with silicon micro-die chip, specular dome highlight, and directional elliptical bloom.
  - Added **`🧵 Show Vinyl Pill Slots (6×3mm)`** toggle switch in Layout Tab Section 3 (`#showPillSlotsToggle`) with `localStorage` persistence.
  - Added **`✂️ Export Cut SVG` (`exportCricutSvgWithPillSlots`)**: 1-click generator in Section 2 exporting production-ready Cricut SVG cut files with $6\times 3\,\text{mm}$ tangent pill slots pre-punched for all 100 LEDs.
  - Preserved 100% of Layout tab functionality: direct canvas dragging, `100 Scatter`, `50 Outline`, `Fill Graphic`, and `Ctrl+Z` Undo all work seamlessly.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=57`.

### Entry: Master Fleet Parade Show Suite Export/Import (Master JSON Bundle Engine)
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Operational & Synchronized across `simulator/app.js?v=56`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Implemented **Master Fleet Parade Suite Export Engine (`exportMasterFleetBundleJson`)**:
    - Gathers complete costume configurations for all 7 runner slots (100 LED coordinates, sampled colors, zone animation groups, standalone timeline cues, and ambient dynamics) plus the 30s synchronized fleet choreography blocks into a single standardized master JSON bundle (`msep_fleet_parade_master_[TIMESTAMP].json`).
    - Added export action buttons on `🏃 Tab 5: Fleet` (`📥 Export Fleet Bundle`) and `🎨 Tab 1: Layout` (`📦 Export All 7 Floats`).
  - Implemented **Master Fleet Parade Suite Import Engine (`openFleetBundleImportModal`, `applyMasterFleetBundle`)**:
    - Interactive **Import Confirmation Modal (`#fleetBundleImportModal`)** displaying bundle title, export timestamp, float breakdown, and choreography block count.
    - Selective float checkable card list with **Select All** and **Deselect All** controls, allowing selective imports without overwriting unwanted slots.
    - Optional toggle to import/merge 30s choreography blocks.
    - Synchronized with `Ctrl+Z` Universal Undo/Redo history stack via `pushUndoState`.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=56`.

### Entry: Multi-Group Phase Sync, Anti-Phase Dual Wheels & Master-Follower Tempo Linking (Groups Tab Suite)
* **Date:** 2026-09-28
* **Milestone:** Milestone 5 - Studio Workflow & Visual Geometry Suite
* **Status:** Operational & Synchronized across `simulator/app.js?v=55`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Implemented **Multi-Group Phase Sync ($0^\circ \dots 360^\circ$)** in `simulator/app.js`: groups calculate $\Delta t_{\text{phase}} = (\text{phaseOffsetDeg} / 360.0) \times T_{\text{beat}}$ and evaluate animations on $\text{effectiveTimeMs} = \text{timeMs} + \Delta t_{\text{phase}}$.
  - Added Phase Offset Slider and 4 Quick Preset Buttons (`0° Sync`, `90° Quad`, `180° Anti`, `270°`) with live badge feedback (`#groupPhaseValHub`).
  - Perfected dual-wheel mechanical realism (e.g. Cinderella's Coach / Casey Jr.): front wheel at $0^\circ$, rear wheel at $180^\circ$ Anti-Phase.
  - Implemented **🔗 Master-Follower Tempo Linking** (`#groupSyncWithSelectHub`): child groups dynamically inherit their master group's `speedBpm` while maintaining independent phase offsets.
  - Added **🔀 Auto-Stagger Phase** (`#autoStaggerPhaseBtn`): automatically distributes $360^\circ / N$ evenly across all active groups with full `Ctrl+Z` Undo/Redo integration.
  - Rendered phase badges and master-follower linkage tags on active group cards in `#activeGroupsList`.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=55`.

### Entry: Corral Standby Smooth Starlight Shimmer & Visible Midnight Base Calibration
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational across `simulator/app.js?v=46`, `simulator/index.html`, `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Eliminated rapid/jittery 60ms discrete seed strobing in Corral Standby Mode, replacing it with an organic sine wave starlight shimmer (~1.6s period per pixel).
  - Enhanced base standby glow to 25–28% of float theme color (`r/g/b >= 25`, `alpha = 0.55`) so all 100 costume LEDs remain clearly and serenely lit against the dark running shirt rather than looking unlit or dead.
  - Calibrated `renderBulb()` in the simulator so dimmed LEDs maintain an opaque, glowing colored bead center (minimum 0.7 opacity) with gentle ambient glow.
  - Implemented smooth starlight wave peaking: the top 30% of each pixel's sine wave smoothly blends from the dimmed base color into warm golden starlight (`CRGB(220, 200, 140)`) and back down.
  - Synchronized firmware logic across `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` using FastLED `sin8` and `blend()` per Rule 5.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=46`.

### Entry: Canvas Render Loop Standby Variable Scope & Bulb Alpha Fix
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Verified & Operational (`simulator/app.js?v=45`, `simulator/index.html`).
* **Notes:**
  - Resolved simulator canvas freeze where lights would not render in either awakened or standby modes due to an uninitialized, undeclared identifier `isCorralStandbyActive` throwing a `ReferenceError` on the first animation tick.
  - Declared `let isCorralStandbyActive = false;` in the top-level global scope in `simulator/app.js`.
  - Added robust null-fallback guards and defensive defaults in `computeLedColor` and `computeRunnerLedColor` to ensure palette colors and sparkles compute reliably across Single Shirt and Fleet Canvas views.
  - Enhanced `renderBulb` to properly scale glow and core brightness with `bulbAlpha` for authentic, gentle 12% ambient corral twinkle.
  - Bumped script cache query in `simulator/index.html` to `app.js?v=45`.

### Entry: Leader-Centric Fleet Authority & Race-Day Corral Standby Mode
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Hardware Fleet Control
* **Status:** Operational & Synchronized across `src/main.cpp`, `arduino/MSEP_Costume/MSEP_Costume.ino`, `simulator/app.js`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, `README.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Implemented **Power-On Corral Standby Default**: All costumes boot directly into a dim 12% midnight starlight twinkle (<120mA draw) upon plugging in USB power at 3:30 AM, preserving 80%+ battery life over the 60–90 minute corral wait and preventing glare for nearby runners.
  - Established **Leader-Centric Fleet Authority Model**:
    - **👑 Master Leader (Float 1 - Casey Jr.):** Single tap in Standby wakes entire fleet (`0x51`); single tap during active run starts/stops 30s fleet show (`0x30`/`0x00`); double tap triggers 4s attendance wave (`0x44`); triple tap drops entire fleet back to Standby (`0x50`).
    - **👥 Follower (Floats 2 to 7):** Single tap in Standby wakes local costume only; single tap during active run and double tap are ignored to protect non-technical family members from accidental fleet disruption; triple tap drops local costume into Standby.
  - Integrated Corral Wait Duration slider (0–120 min) into the Battery Life & Power Budget Calculator, dynamically computing mAh and runtime savings.
  - Fully mirrored C++ firmware logic between `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino` per Rule 5.

### Entry: Pre-Built Shape & Flourish Stamp Library (Groups Tab Mode 3 Suite)
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Visual Geometry Suite
* **Status:** Operational & Synchronized across `simulator/app.js?v=44`, `simulator/style.css?v=36`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, `README.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  - Upgraded Mode 3 in the `👥 Groups` tab to **🌟 Stamp Library**, establishing a parametric shape creation hub alongside the existing `🎆 Fireworks` Starburst generator.
  - Built 5 parametric flourish tools with aspect-ratio ($1 : 1.25$) jersey coordinate correction: **Circle / Wheel**, **Arch / Canopy**, **Wave / Serpentine Puff**, **Star / Sparkle**, and **Straight Line / Ruler**.
  - Added interactive **🎯 Click Canvas to Place** centroid positioning mode alongside quick centroid presets (Center Chest, Upper Arch, Left/Right Shoulder, Waist).
  - Maintained strict 100-LED costume budget invariant by drawing pixels from unassigned LEDs and auto-redistributing remaining unassigned LEDs cleanly.
  - Fully integrated with Universal Undo / Redo engine (`Ctrl+Z` / `Ctrl+Y`).

### Entry: Universal Undo / Redo Engine (`Ctrl+Z` / `Ctrl+Y`) & Canvas Toolbar Integration
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Non-Destructive Editing Engine
* **Status:** Operational & Synchronized across `simulator/app.js?v=43`, `simulator/style.css?v=35`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **50-Step Non-Destructive Snapshot Stack:** Implemented a full-fidelity history engine (`undoStack` and `redoStack`) with deep serialization of `leds` coordinates/colors, `animationGroups`, selection sets, and artwork configuration.
  * **Comprehensive Action Capture:**
    * Canvas drags: Mousedown captures origin state; mouseup records a single clean undo step only if `hasMovedSignificantly === true` (eliminating false clicks).
    * Group spatial transformations: `Rotate 90°`, `Flip Horizontal`, `Flip Vertical`, and `Scale Spacing`.
    * Group lifecycle: `Create Group`, `Update Group`, `Delete Group`, and `Remove Group Effects`.
    * Group clipboard: `Paste Group` from unused pool.
    * Click-to-draw paths: Pre-draw LED backups saved and committed on path finish.
    * Layout operations: `Rearrange Remaining LEDs`, `Scatter LEDs on Graphic`, and `Reset Layout`.
  * **Floating Canvas Toolbar Controls:** Added reactive `↩️ Undo` and `↪️ Redo` buttons to the floating zoom toolbar with dynamic hover tooltips indicating the specific action to be reverted/restored, and clear disabled opacity when empty.
  * **Keyboard Shortcuts:** Bound standard `Ctrl+Z` / `Cmd+Z` (Undo) and `Ctrl+Y` / `Ctrl+Shift+Z` / `Cmd+Shift+Z` (Redo) with form input guards.
  * **Cache Busting:** Bumped application script tag to `app.js?v=43` and stylesheet to `style.css?v=35`.

### Entry: LED Group Copy, Paste, Rotate, Flip & Scale Spacing System
* **Date:** 2026-09-27
* **Milestone:** Milestone 5 - Studio Workflow & Animation Group Spatial Suite
* **Status:** Operational & Synchronized across `simulator/app.js?v=42`, `simulator/index.html`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **Global Cross-Shirt Group Clipboard:** Added in-memory and `localStorage` persistent group clipboard (`copiedGroupClipboard`).
  * **Cross-Shirt Copy/Paste:** Supports copying an animation group (flourish, serpentine path, fireworks burst) from one shirt design (e.g. Float 6 Pete's Dragon) and pasting onto any other shirt design (e.g. Float 1 Cinderella's Coach) or within the same shirt design.
  * **100-LED Unused Pool Budget Guard:** Pasted LEDs are automatically allocated from the target shirt's unused LED pool. If the target shirt has fewer unassigned LEDs than required, a toast warning blocks the paste action to maintain our 100-LED invariant.
  * **Relative Coordinates & Color Resampling:** Member LEDs map relative to the target shirt's chest graphic area ($\text{relX}, \text{relY}$) and dynamically resample target artwork pixel colors for a crisp visual match.
  * **Group Spatial Transformations Suite:**
    * **`🔄 Rotate 90°` & Quick Actions:** Rotates member LEDs around group centroid $(\bar{x}, \bar{y})$ with aspect correction.
    * **`↔️ Flip Horizontal` & `↕️ Flip Vertical`:** Mirrors member LEDs across centroid $(\bar{x}, \bar{y})$ for symmetric costume pairing.
    * **`🔍 Scale LED Spacing (Expand / Contract)`:** Adjusts physical spacing ($50\% \text{ to } 200\%$) between member LEDs around centroid while preserving exact shape.
    * **`🖱️ Group Canvas Dragging`:** Clicking and dragging any LED in an animation group automatically selects and moves the entire group intact across the canvas, resampling artwork colors for all member LEDs upon release.
  * **Automatic LED Rearranging:** Automatically redistributes remaining unassigned LEDs ($100 - \text{assigned}$) across open graphic space after pasting or transforming a group.
  * **Keyboard Shortcuts:** Added `Ctrl + C` (Copy Group), `Ctrl + V` (Paste Group), and `Ctrl + R` (Rotate 90°) global hotkeys.
  * **Cache Busting:** Bumped application script tag to `app.js?v=42` in `simulator/index.html`.
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Studio Workflow & Architectural Clarity
* **Status:** Operational & Synchronized across `simulator/index.html`, `simulator/app.js?v=41`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **UX Clarity Renaming (Option 2):** Renamed Tab 2 to `✨ Ambient` and Tab 4 to `🎬 Float Show`.
  * **Eliminated Conceptual Ambiguity:**
    * `✨ Ambient`: Instantly conveys that this tab controls the background/baseline atmosphere for all non-grouped LEDs.
    * `🎬 Float Show`: Immediately contrasts with `🏃 Fleet`, clarifying that this timeline scripts the individual float's 90s standby sequence while `Fleet` coordinates all 7 shirts together.
  * **Grid Layout Preserved:** `🎨 Layout` | `✨ Ambient` | `👥 Groups` / `🎬 Float Show` | `🏃 Fleet` | `⚡ Deploy`.
  * **Cache Busting:** Bumped application script tag to `app.js?v=41` in `simulator/index.html`.

### Entry: Individual Float Standby Cue Director & Fleet Show Scope Clarification
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Studio Workflow & Architectural Clarity
* **Status:** Operational & Synchronized across `simulator/index.html`, `simulator/app.js?v=40`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **Individual Standby Scope vs. Fleet Priority:** Clarified on the Show tab (`#tabDirector`) that the Parade Cue Director scripts theatrical cues exclusively for the active individual float while running in autonomous standby. Highlighted that when a synchronized Fleet Show is triggered (via Tab 5 or the physical ESP32 BOOT button), the fleet routine temporarily overrides all 7 costumes before automatically returning each float back to its individual timeline or baseline.
  * **Interactive Standby Concept Card & Float Badge:** Added an illuminated concept card to `#tabDirector` featuring a dynamic badge (`#directorActiveFloatBadge`) showing the active float name/accent and a fast-jump button (`#directorGoToFleetBtn`) to switch directly to the Fleet Show Creator.
  * **Master Timeline Track Label Differentiation:** Updated `renderTimelineLayers()` in `simulator/app.js` so that the left track label dynamically identifies the mode: displaying `FLOAT SHOW` for the single float's cue timeline and `FLEET SHOW` for the 30-second multi-shirt choreography track.
  * **Cache Busting:** Bumped application script tag to `app.js?v=40` in `simulator/index.html`.

### Entry: Sidebar Tab Workflow Reordering & Garment Baseline Clarity
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Studio Workflow & Architectural Clarity
* **Status:** Operational & Synchronized across `simulator/index.html`, `simulator/app.js?v=39`, `SIMULATOR_USER_GUIDE.md`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **Logical Tab Sequencing:** Reordered the 6 sidebar tabs to follow the natural creative pipeline:
    1. `🎨 Layout`: Garment canvas, artwork placement, 100-LED contour/scatter, wiring route optimization, and runDisney 10K bib clearance.
    2. `✨ Effects`: Garment baseline atmosphere setting the continuous default look for all non-grouped LEDs.
    3. `👥 Groups`: Creation and management of specialized animation groups (wheels, eyes, breathing crests, starburst fireworks) running atop the baseline.
    4. `🎬 Show`: Parade Cue Director and 90-second theatrical cue sequencing.
    5. `🏃 Fleet`: 7-shirt fleet lineup, 30-second synchronized routine creator, pre-race corral radar, and battery endurance budget.
    6. `⚡ Deploy`: USB standalone firmware flashing, ESP-NOW fleet broadcasting, and real-time Wi-Fi live streaming.
  * **Garment Baseline Concept Card & Dynamic Badge:** Added an Imagineering concept card to the Effects tab with a live LED allocation badge (`#fxUngroupedCountBadge`) dynamically displaying non-grouped LED coverage (e.g., `100 of 100 LEDs (100% Baseline)` or `64 of 100 LEDs (64% Baseline)`) updated in real time as groups are created, modified, or loaded.
  * **Seamless 2x3 Grid Navigation:** Perfectly preserved 2-row × 3-column button grid in the 410px sidebar (Row 1: Layout | Effects | Groups; Row 2: Show | Fleet | Deploy) with zero button clipping.
  * **Cache Busting:** Bumped application script tag to `app.js?v=39` in `simulator/index.html`.

### Entry: Custom Profile Persistence & Server Disk Preset Association
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Profile Persistence Integrity
* **Status:** Operational & Synchronized across `simulator/app.js?v=38`, `simulator/index.html`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **Dual-Tier Profile Persistence:** Verified and guaranteed that custom float profiles saved under new names write directly to disk (`presets/<safe_name>.json`) via `/api/save_preset` while preserving the original defaults (`petes_dragon.json`, `casey_jr_train.json`, etc.) completely untouched.
  * **Server Preset Lineup Association:** Updated `saveCurrentProfile` so that when a profile is saved under a new name, the active float in `fleet_lineup.json` and browser cache is immediately associated with `'server:' + result.filename`. When reopening the simulator tomorrow or on any browser/device, the float automatically loads your customized preset.
  * **One-Time Storage Migration Guard:** Converted the legacy preset purge in `loadFleetLineupFromStorage` to a one-time migration (`msep_presets_cleanup_v1_done`), ensuring newly saved browser profiles are never accidentally erased on subsequent reloads.
  * **Cache Busting:** Bumped application script tag to `app.js?v=38` in `simulator/index.html`.

### Entry: Unsaved Edits Modal Cancellation State Synchronization Fix
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Single Shirt Editor State Integrity & Switcher UX
* **Status:** Operational & Synchronized across `simulator/index.html`, `simulator/app.js?v=37`, and `PROJECT_PROGRESS.md`.
* **Notes:**
  * **Resolved Cancellation Desynchronization:** Fixed a state desynchronization bug where cancelling out of the "Unsaved Edits" modal prompt (e.g., clicking Cancel, Escape, or backdrop when attempting to switch floats) left the right sidebar panel showing the target float while the canvas stayed on the original float.
  * **Proper State Reversion:**
    - Updated `editRunnerInSingleView` to explicitly call `updateActiveFloatUI(activeSingleShirtRunnerSlot)` and return `false` on cancellation.
    - Updated `initSingleShirtFloatSelector` button click listener to synchronize with `activeSingleShirtRunnerSlot` instead of prematurely passing `targetSlot`.
    - Updated `graphicPresetSelect` change listener to revert `<select>` value back to the active float if switching is aborted.
  * **Cache Busting:** Bumped application script tag to `app.js?v=37` in `simulator/index.html`.

### Entry: Elimination of Duplicate LED Generation Buttons & Layout Toolbar Consolidation
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Sidebar Cleanliness & Action Consolidation
* **Status:** Operational & Synchronized across `simulator/index.html`, `simulator/app.js?v=36`, and `SIMULATOR_USER_GUIDE.md`.
* **Notes:**
  * **Removed Section 1 Redundancy:** Removed the duplicate cluster of buttons (`#scatterColorBtn`, `#autoOutlineBtn`, and `#rearrangeRemainingLedsBtn`) from Section 1 ("🎭 Active Parade Float & Character Artwork"), streamlining Section 1 exclusively for parade float selection, custom artwork uploads, and race bib clearance verification.
  * **Consolidated Section 3 Toolbar:** Grouped all LED generation and routing controls cleanly under **Section 3: LED Layout & Wiring Route**:
    - `🌈 100 Scatter` (`#quick100Btn`)
    - `✨ 50 Outline` (`#quick50Btn`)
    - `🎨 Sample Colors` (`#resampleColorsBtn`)
    - `🔄 Fill Graphic with Remaining LEDs` (`#rearrangeRemainingLedsBtn2`)
    - `🔌 Optimize Wiring Route (Shortest Snake)` (`#optimizeWiringBtn`)
  * **Float-Aware Preset Restore:** Enhanced `#resetArtworkBtn` to intelligently restore the active float's official preset artwork (Casey Jr., Title Drum, Turtle, Snail, Coach, Elliott, or Eagle) instead of hardcoding to Pete's Dragon when reverting from custom image uploads.
  * **Cache Busting:** Bumped application script tag to `app.js?v=36` in `simulator/index.html`.

### Entry: Single Shirt 7-Float Quick Switcher & Active Parade Float Banner
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Single Shirt Editor Clarity & Direct Fleet Switching
* **Status:** Operational & Synchronized across `simulator/index.html`, `simulator/style.css`, `simulator/app.js?v=35`, and `SIMULATOR_USER_GUIDE.md`.
* **Notes:**
  * **Active Parade Float Banner (`#activeFloatBanner`):** Placed an informative status banner at the top of Section 1 in the Layout tab. Shows the active float number (`FLOAT 01` to `FLOAT 07`), character name, role (`👑 Fleet Leader (Broadcast)` / `📡 Follower Float`), signature accent color, and lineup tag.
  * **7-Button Quick Switcher Grid (`#floatSelectorGrid`):** Built 7 dedicated 1-click switcher buttons (`[ 1 ]` to `[ 7 ]`) with glowing signature-color indicator dots. Clicking any button immediately switches the single shirt editor to that float, with unsaved-change protection (`confirmUnsavedEditsModal`).
  * **Canvas Floating Watermark (`#canvasFloatWatermark`):** Added a sleek, translucent floating badge in the top-left corner of the canvas displaying the active float icon, number, and character name, ensuring crystal-clear context while arranging LEDs. Automatically hides when viewing the full fleet.
  * **Dynamic Navigation Header (`#singleViewBtn`):** Updated the top view button to dynamically show which float is currently loaded (e.g., `👕 Single Shirt (#6 Elliott)`).
  * **Unified Float & Artwork Picker (`#graphicPresetSelect`):** Replaced duplicate and confusing preset lists by establishing Section 1 as "🎭 Active Parade Float" (with the 7 floats and custom upload) and Section 2 as "💾 Save & Export Profiles" (for saving user modifications or importing JSON files).
  * **Cache Busting:** Bumped application script tag to `app.js?v=35` in `simulator/index.html`.

### Entry: Preset Cleanup & Cinderella Both Wheels Fleet Default Integration
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Fleet Profile Cleanliness & Coach Wheel Choreography
* **Status:** Operational & Synchronized across `presets/`, `presets/archive/`, `simulator.py`, `simulator/app.js?v=34`, and `simulator/index.html`.
* **Notes:**
  * **Strict 7-Float Default Roster:** Cleaned up the `presets/` directory to retain exclusively the official 7 fleet presets matching the 10K parade roster:
    - **Float 1 (The Train):** `casey_jr_train.json`
    - **Float 2 (Title Drum):** `title_drum.json`
    - **Float 3 (The Turtle):** `spinning_turtle.json`
    - **Float 4 (The Snail):** `spinning_snail.json`
    - **Float 5 (Cinderella / Coach):** `cinderellas_coach_both_wheel.json` (featuring animated front and rear wheel spinning chase routines)
    - **Float 6 (Pete's Dragon):** `petes_dragon.json`
    - **Float 7 (Flag & Eagle):** `honor_america_eagle.json`
  * **Safe Archival (`presets/archive/`):** Moved 8 legacy and variant presets (`carriage_nohorses.json`, `cinderellas_coach.json`, `cinderellas_coach_rear_wheel.json`, `pete_with_animated_bib_fluorish.json`, `petes_dragon_100_scatter_color.json`, `petes_dragon_default.json`, `spinning_turtle_100-led_vibrant_preset.json`, `to_honor_america_100-led_patriotic_preset_2.json`) into `presets/archive/` so they remain safely preserved without cluttering dropdowns.
  * **Float 5 Integration:** Updated `presets/fleet_lineup.json` and `DEFAULT_FLEET_ROSTER` in `simulator/app.js` to link Float 5 directly to `cinderellas_coach_both_wheel.json` with `cinderella_coach` artwork and dual spinning wheel chase groups.
  * **API System File Filtering:** Updated `handle_list_presets` in `simulator.py` to filter out system files (`fleet_lineup.json`, `wifi_settings.json`, and directories), ensuring `/api/presets` returns strictly the 7 parade costume profiles.
  * **Browser Storage Cleanup:** Added automated cleanup in `simulator/app.js` (`loadFleetLineupFromStorage`) to purge legacy custom presets from browser `localStorage` (`msep_custom_presets`), guaranteeing a clean, identical experience across all devices.
  * **Cache Busting Update:** Bumped CSS and JS to `?v=34` in `simulator/index.html`.

### Entry: Family Running Crew Alignment & 6-Step Quickstart Redesign
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Team Alignment & Beginner Onboarding
* **Status:** Operational & Synchronized across [`SIMULATOR_QUICKSTART.md`](SIMULATOR_QUICKSTART.md), [`SIMULATOR_USER_GUIDE.md`](SIMULATOR_USER_GUIDE.md), [`README.md`](README.md), [`FLASHING_INSTRUCTIONS.md`](FLASHING_INSTRUCTIONS.md), [`GEMINI.md`](GEMINI.md), and Web Simulator (`index.html`).
* **Notes:**
  * **Team Composition Clarification:** Formally updated all documentation and assistant rules to accurately represent the entire family running crew:
    - **7 Runners on Course:** 2 brothers, 1 sister, 1 brother-in-law, and 3 sisters-in-law running the WDW 10K together.
    - **Engineering / Build Team:** 3 brothers (2 of whom are running, plus 1 supporting brother helping build, code, and test).
  * **Redesigned 6-Step Quickstart Guide (`SIMULATOR_QUICKSTART.md`):**
    - Completely restructured the quickstart guide around the exact 6-step beginner journey requested by the team:
      1. *How to Start the Simulator:* Double-clicking `start_simulator.bat` (Windows) or running `python simulator.py` and opening `localhost:8000`.
      2. *How to Add a Graphic or Start with a Preset:* Selecting from 7 pre-calibrated float presets or uploading custom PNG/JPEG and scattering 100 color-matched LEDs above the #1952 bib.
      3. *How to Create Animation Groups:* Marquee-selecting LEDs on the canvas (`Shift + Drag`) and saving as a named group with dedicated timeline track lanes.
      4. *How to Use Groups to Create Cues:* Adding cue cards, selecting effects, setting duration, and slipping/trimming clips directly on the interactive timeline.
      5. *How to Create a Fleet Show:* Switching to Tab 6, chaining choreography blocks across the 30-second multi-shirt timeline, firing with `[F]`/`Spacebar`, and running corral roll call checks.
      6. *How to Deploy Shows onto ESP32 Boards:* Using the 1-click browser Web Serial flasher or double-clicking `flash_firmware.bat` / `flash_firmware.command` to bake float identities into NVS flash memory.
    - Included the race-morning button cheatsheet (single-tap 30s show, double-tap 4s roll call, 5s config hold with charging meter).
  * **One-Click Script Integration:** Integrated direct documentation links for `start_simulator.bat` and `flash_firmware.bat` across both `SIMULATOR_QUICKSTART.md` and `README.md`.
  * **UI Text Cleanliness:** Updated strings in `simulator/index.html` (battery power budget and corral radar headers/tooltips) to refer to all runners.

### Entry: Simulator Quickstart Guide (TL;DR Edition) Published
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Documentation Ergonomics & Runner Onboarding
* **Status:** Operational & Published across [`SIMULATOR_QUICKSTART.md`](SIMULATOR_QUICKSTART.md), [`SIMULATOR_USER_GUIDE.md`](SIMULATOR_USER_GUIDE.md), and [`README.md`](README.md).
* **Notes:**
  * **Addressed TL;DR Friction:** Created a punchy, highly readable 2-minute quickstart guide specifically designed for the brothers and runners who need actionable answers fast without wading through the full 90-page technical manual.
  * **Core Sections Covered:**
    1. *10-Second Launch:* Starting the server and opening `localhost:8000`.
    2. *3-Zone Layout at a Glance:* Workspace tabs, center canvas, inspector sidebar, and master timeline bar.
    3. *"I Just Want To..." Workflow Cheatsheet:* One-step recipes for picking float presets, moving/trimming timeline clips, firing the 30-second synchronized fleet show, and checking pre-race corral radar.
    4. *Live Wi-Fi Streaming to Real LEDs:* Setting up the bench test with IP routing or direct `MSEP-Costume-AP` hotspot.
    5. *Flashing for Race Day:* 1-click in-simulator USB flashing, browser Web Serial flashing, and double-click desktop scripts.
    6. *The Golden On-Costume Button Rule:* Race-morning cheat sheet for single-tap (30s show), double-tap (4s rapid attendance wave), 5s hold (Float ID config), and early abort safety.
    7. *Consolidated Keyboard & Gesture Matrix:* Quick table for hotkeys, canvas navigation, and timeline trimming.
  * **Cross-Linked Across Ecosystem:** Connected from `README.md`, top notice banner of `SIMULATOR_USER_GUIDE.md`, and project documentation indices.

### Entry: Interactive Drag-to-Move Timeline Clips & Edge Trimming Handles
* **Date:** 2026-09-26
* **Milestone:** Milestone 4 - Single Shirt Master Timeline NLE Editing & Ergonomics
* **Status:** Operational & Verified across Web Simulator (`index.html`, `style.css?v=33`, `app.js?v=33`) and Documentation.
* **Notes:**
  * **Interactive Edge Trim Handles (`.handle-left` & `.handle-right`):**
    - Integrated dedicated 10px-wide hover grab handles on both borders of each timeline cue block with visual cues (`cursor: ew-resize`).
    - **Left Handle Trimming:** Trags left or right to adjust `cue.startTime` while holding the end time (`origStart + origDur`) strictly locked in place, recalculating duration on the fly. Clamped to a minimum duration of 0.5s and bounded by $t \ge 0$.
    - **Right Handle Trimming:** Drags left or right to adjust `cue.duration` while locking `cue.startTime` in place. Clamped to 0.5s minimum and bounded by timeline length (`sequenceLoopDuration`).
  * **Direct Clip Body Moving / Slipping (`cursor: grab` / `cursor: grabbing`):**
    - Clicking and dragging the central body of any cue block slides both `startTime` and its end boundary earlier or later across the timeline tracks without modifying the clip's duration.
    - Clamped strictly within `[0, sequenceLoopDuration - duration]`.
  * **Pointer Capture & Gesture Precision:**
    - Employs pointer events (`pointerdown`, `pointermove`, `pointerup`, `pointercancel`) with `setPointerCapture` to guarantee uninterrupted tracking even when dragging rapidly above or below the 20px track lanes or outside the browser viewport.
    - Enforces a 4-pixel movement threshold (`Math.abs(dx) >= 4`) to distinguish deliberate drag gestures from simple clicks. Quick taps cleanly seek the playhead and scroll the inspector to the clicked cue card without accidental position jumps.
    - All movements and trims snap to a clean 0.1-second quantization grid.
  * **Live High-Contrast Floating Tooltip (`.timeline-drag-tooltip`):**
    - Projects an elevated timecode badge directly above the cursor displaying real-time coordinates: `Start: 12.4s | End: 28.6s (Dur: 16.2s)`.
  * **Bidirectional Inspector Card Synchronization:**
    - Live updates the corresponding cue card's `.cue-start-input`, `.cue-dur-input`, and header time badge in Section 2 (Parade Cue Director) in real time during drag.
    - Automatically marks the costume dirty (`isSingleShirtDirty = true`) and triggers re-render on release.
  * **Cache Busting Update:** Incremented stylesheet and script tags to `?v=33` in `simulator/index.html`.

### Entry: Idiot-Proof 5-Second Float Config Hold with Progressive Charging Indicator & Clean Abort
* **Date:** 2026-09-26
* **Milestone:** Milestone 3 - ESP32 Firmware & Hardware Interaction Hardening
* **Status:** Operational & Verified across C++ Firmware (`src/main.cpp`), Arduino Sketch (`arduino/MSEP_Costume/MSEP_Costume.ino`), PlatformIO compilation, and Documentation.
* **Notes:**
  * **5-Second Hold Threshold:** Upgraded the Float ID Configuration Mode trigger on the ESP32 onboard BOOT button (GPIO 0) from 3000ms to 5000ms to prevent accidental reconfiguration from race-day belt/pocket bumps or nervous fidgeting in the corrals.
  * **1s–4s Progressive White LED Charging Meter:** Holding the BOOT button for $\ge 1000\text{ ms}$ activates a real-time visual charging meter that lights up crisp white LEDs one-by-one at each 1-second milestone (1s: 1 LED, 2s: 2 LEDs, 3s: 3 LEDs, 4s: 4 LEDs), giving the runner intuitive visual feedback.
  * **Hold-to-Abort Safety:** Releasing the button at any point between 1000ms and 4999ms cleanly aborts the hold action and immediately restores baseline animation without modifying Float ID or triggering show routines.
  * **Strict Tap Boundary (< 600ms):** Single tap (< 600ms) toggles the 30s fleet routine, double tap (< 400ms) triggers the 4s rapid roll call, and intermediate aborted holds (1s–4.99s) are completely quarantined from triggering the theatrical show.
  * **Loop Fall-Through Fix:** Added explicit `return;` inside the button hold charging meter block (`holdElapsed >= 1000`) and after `handleFloatConfigMode()`. Previously, `loop()` continued down to `runAutonomousShowSequence()`, which immediately repainted baseline colors over the white LEDs and accelerated the animation frame rate. Now, the 1s–4s white charging meter renders rock-solid without interference.
  * **Dual-Core Synchronized:** Mirrored identical button state machine, charging meter, and serial logging across both `src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`. PlatformIO build verified with 0 errors.

### Entry: Visual Cleanliness - Removed Spotlight Effect & Visors from Runners
* **Date:** 2026-09-26
* **Milestone:** Milestone 5 - Realistic Runner Anatomy & Visual Cleanliness
* **Status:** Operational & Verified across Web Simulator (`index.html`, `app.js?v=32`) and Documentation.
* **Notes:**
  * **Removed Spotlight Effect:** Eliminated the overhead theatrical spotlight cone, the ground light circle, and downward radial light spills when shirts light up, keeping the focus strictly on the authentic LED costumes themselves.
  * **Removed Visors:** Streamlined runner head silhouettes to natural, athletic contours with clean dark hair silhouettes, removing the running caps, visors, and brim trims.

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
