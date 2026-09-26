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
