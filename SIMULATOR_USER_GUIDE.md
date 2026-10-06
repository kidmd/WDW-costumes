# 🏰 Main Street Electrical Parade Costume Simulator
## Complete User Guide & Theatrical Lighting Manual

Welcome to the **Main Street Electrical Parade (MSEP) Costume Simulator** — a comprehensive browser-based theatrical lighting design console and hardware integration engine for synchronized, wearable addressable LED floats.

This guide walks you through every feature of the simulator, from placing and wiring your physical LEDs to orchestrating multi-layer 90-second parade show routines, live streaming to your ESP32, and compiling standalone firmware.

> ⚡ **Short on time?** Check out the 2-minute [**Simulator Quickstart Guide (TL;DR)**](SIMULATOR_QUICKSTART.md) for quick-reference shortcuts, clip dragging/trimming, and flasher workflows!

---

## Table of Contents
1. [Introduction & System Architecture](#1-introduction--system-architecture)
2. [Launching the Simulator](#2-launching-the-simulator)
3. [Canvas Navigation & Interactive Controls](#3-canvas-navigation--interactive-controls)
4. [Thoroughbred Workspace: 6 Task Tabs & Contextual Inspector Dock](#4-thoroughbred-workspace-6-task-tabs--contextual-inspector-dock)
5. [LED Placement, Inspection & Color Tuning](#5-led-placement-inspection--color-tuning)
6. [Multi-LED Selection & Animation Groups](#6-multi-led-selection--animation-groups)
7. [Physical Wiring Route Optimization](#7-physical-wiring-route-optimization)
8. [Artwork & Graphic Management](#8-artwork--graphic-management)
9. [Master Timeline Scrubber & Multi-Layer Tracks](#9-master-timeline-scrubber--multi-layer-tracks)
10. [Parade Cue Director (90-Second Theatrical Sequences)](#10-parade-cue-director-90-second-theatrical-sequences)
11. [Lighting Patterns & Effects Library](#11-lighting-patterns--effects-library)
12. [Profile Management, Saving & JSON Import/Export](#12-profile-management-saving--json-importexport)
13. [7-Shirt Fleet Show Creator, Preset Manager & Corral Radar](#13-7-shirt-fleet-show-creator--preset-manager)
14. [Hardware Integration: Live Wi-Fi Streaming, Standalone USB Flashing & Battery Power Budget](#14-hardware-integration-live-wi-fi-streaming-standalone-usb-flashing--battery-power-budget)
15. [ESP32 Firmware: Debounced Button Control, Fleet Routine Trigger & Early Stop](#15-esp32-firmware-debounced-button-control-fleet-routine-trigger--early-stop)
16. [3D-Printable Flexible Wearable TPU Panels (Snapmaker U1 / Bambu Lab / 95A TPU)](#16-3d-printable-flexible-wearable-tpu-panels-snapmaker-u1--bambu-lab--95a-tpu)
17. [Keyboard Shortcuts & Quick Reference Cheat Sheet](#17-keyboard-shortcuts--quick-reference-cheat-sheet)

---

## 1. Introduction & System Architecture

The simulator acts as a virtual workbench and lighting console for your WS2812B addressable LED costumes:
- **Design in the Browser:** Visually position up to 100 LEDs on any costume shirt graphic, match colors from the artwork pixels, organize LEDs into zone animation groups (e.g. carriage wheels, lanterns, dragon crest), and sequence rich multi-layered theatrical cues along a 90-second timeline.
- **Preview with 60 FPS Fidelity:** The canvas simulates the optical diffusion, bloom, and incandescent decay of vintage parade light bulbs.
- **Direct Hardware Link (Zero-Latency Wi-Fi UDP):** Stream the exact animation frames from the browser directly to an ESP32 over local Wi-Fi at 30 FPS.
- **Standalone FastLED Firmware:** Generate standalone C++ code and flash your ESP32 with one click. In the theme park, the ESP32 runs autonomously off a USB battery pack, controlling **200 LEDs (100 Front + 100 Back Duplicated)** with an onboard button to toggle between your individual float show and wireless ESP-NOW fleet synchronization.

```
┌────────────────────────────────────────────────────────┐
│                   BROWSER SIMULATOR                    │
│  - Multi-Layer Timeline & 90s Parade Cue Director     │
│  - Zone Groups (Wheels, Lanterns, Flame Crest)         │
│  - Continuous Wiring Route Optimizer                   │
│  - runDisney 10K Race Bib (#1952) & BibBoards Overlay  │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│   LIVE WI-FI UDP STREAM  │   │  STANDALONE USB FLASH    │
│   (Port 4210 @ 30 FPS)   │   │  (PlatformIO / FastLED)  │
│   100 Front LEDs Live    │   │  200 LEDs (Front + Back) │
└────────────┬─────────────┘   └─────────────┬────────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
               ┌───────────────────────────┐
               │    ESP32 COSTUME NODE     │
               │  - Mode 0: 90s Show Seq   │
               │  - Mode 1: ESP-NOW Sync   │
               │  - Output: 200 LEDs (G16) │
               │  - Button: GPIO 0 (BOOT)  │
               └───────────────────────────┘
```

---

## 2. Launching the Simulator

1. **Start the Local Server:**
   Open a terminal in the project directory and run:
   ```bash
   python simulator.py
   ```
   *(Or double-click `start_simulator.bat` on Windows or `start_simulator.command` on macOS).*
2. **Open Your Browser:**
   Navigate to:
   ```
   http://localhost:8000
   ```
3. The simulator will load with default artwork, pre-configured palettes, and an active transport control bar.

---

## 3. Canvas Navigation & Interactive Controls

The central workspace renders an interactive, hardware-accelerated preview of your shirt and LEDs.

### Pan & Zoom
- **Zoom In / Out:** Scroll your mouse wheel anywhere over the canvas. You can also press the `+` / `-` keys on your keyboard, or click the **Zoom In (+)** and **Zoom Out (-)** buttons in the top-left toolbar.
- **Reset Zoom:** Click the **⟲ 100%** button or press the `0` key to restore the default centered view.
- **Panning:**
  - **Right-Click Drag:** Hold down the right mouse button and drag across the canvas.
  - **Spacebar + Drag:** Hold the `Spacebar` (the cursor turns into a grab hand ✋) and drag with the left mouse button.
  - *Note:* A quick tap and release of the `Spacebar` (without dragging) toggles **Play / Pause** on the timeline!

### Universal Undo / Redo Engine (`Ctrl+Z` / `Ctrl+Y`)
- **50-Step Historical Memory Stack:** A non-destructive snapshot buffer records every garment modification across single LED drags, whole-group moves, 90° rotations, horizontal/vertical flips, spatial scaling, group pasting, group deletions, drawn paths, and automatic unassigned pool redistributions.
- **Toolbar Buttons:** Dedicated **`↩️ Undo`** and **`↪️ Redo`** buttons in the floating canvas toolbar dynamically display the next action to be reversed or restored in their hover tooltip.
- **Keyboard Shortcuts:**
  - **Undo:** `Ctrl + Z` (Windows/Linux) or `Cmd + Z` (macOS).
  - **Redo:** `Ctrl + Y` or `Ctrl + Shift + Z` (Windows/Linux) or `Cmd + Shift + Z` (macOS).
- **Smart Drag Batching:** Moving an LED or an entire group captures the baseline at click-down and commits a single clean undo step only on mouseup if actual movement took place, preventing accidental clicks from creating blank undo steps.

---

## 4. Thoroughbred Workspace: 6 Task Tabs & Contextual Inspector Dock

The simulator features a streamlined, modern workspace inspired by creative suites (After Effects, Figma, Blender), replacing long vertical scrolling with **6 task-oriented tabs** and an **intelligent contextual inspector dock**:

### The 6 Sidebar Tabs (2-Row Grid Layout)
The sidebar navigation is organized into a clean **2-row × 3-column grid** that guarantees all 6 task buttons fit comfortably inside the 410px sidebar without any button clipping or horizontal scrolling:
- **Row 1:** `🎨 Layout` | `✨ Ambient` | `👥 Groups`
- **Row 2:** `🎬 Float Show` | `🏃 Fleet` | `⚡ Deploy`

1. **🎨 Tab 1: Layout ("The Canvas Studio"):**
   - **🎭 Active Parade Float Banner & 7-Shirt Quick Switcher:** Unmistakable banner at the very top of the Layout tab showing exactly which float is being edited: Float number (#01 to #07), character name, parade role (`👑 Fleet Leader (Broadcast)` / `📡 Follower Float`), signature accent color, and lineup tag.
   - **⚡ 7-Button Float Switcher Grid:** Direct 1-click switcher buttons (`[ 1 ]` through `[ 7 ]`) featuring live glowing indicator dots in each float's signature color. Seamlessly switch between Casey Jr., Title Drum, Turtle, Snail, Cinderella's Coach, Pete's Dragon, and To Honor America with unsaved-change protection!
   - **🏷️ Top Navigation & Canvas Watermark Badge:** The top navigation tab updates dynamically (`👕 Single Shirt (#6 Elliott)`), while a translucent floating watermark badge in the top-left canvas corner keeps the active float number and name clearly visible while positioning LEDs.
   - **Float / Character Artwork Picker:** Unified dropdown allowing quick selection between the 7 official parade floats or uploading custom graphics (PNG/SVG/JPG), with a one-click `🔄 Restore Preset Defaults` button when custom artwork is active.
   - **runDisney 10K Race Bib (#1952):** Toggle overlay, height, and scale sliders to verify physical clearance.
   - **💾 Save & Export Custom Profiles:** Dedicated section for naming and saving custom design tweaks to browser cache, exporting standalone JSON costume files, or importing existing configurations.
   - **🎛️ LED Count & Sizing Selectors (50 / 75 / 100 LEDs & Small / Medium / Large):**
     - **LED Count Selector (`50` / `75` / `100` LEDs):** Switch costume density with a single click. Selecting 50, 75 (target option), or 100 LEDs redistributes the chosen count across the active float graphic with color matching and optimal serpentine wiring.
     - **Plate Sizing Selector (`Small ~6.5"` / `Medium ~8.0"` / `Large ~10.0"`):** Sizing directly sets the target width for the flexible TPU armor plate (Small = 165.1mm / 6.5", Medium = 203.2mm / 8.0", Large = 254.0mm / 10.0"). Both Front and Back plates dynamically scale to the selected width and recompile.
   - **🔌 LED Placement & Wiring Route:** Consolidated toolbar uniting all bulb generation and routing in one dedicated location:
     - `🌈 100 Scatter`: Evenly disperses 100 LEDs across the character with color matching.
     - `✨ 50 Auto-Outline`: Traces the outer silhouette contour with 50 LEDs.
     - `🎨 Sample`: Samples colors from the underlying artwork for each bulb.
     - `🔄 Fill Graphic with Remaining LEDs`: Redistributes non-grouped LEDs to fill open space without moving any grouped LEDs.
     - `🔌 Optimize Wiring Route`: Calculates the shortest serpentine continuous snake route.
     - `Show Wiring Trace` and `Show Bulb Numbers` inspection toggles.
     - **🧵 Show Vinyl Pill Slots (6×3mm) & Tangent Pebble LEDs:** Toggles ultra-realistic fabrication view modeling the physical mesh pinnie vest. Renders the exact $6.0\,\text{mm} \times 3.0\,\text{mm}$ HTV vinyl pill cutout exposing the dark mesh weave, with tangent-aligned $4.0\,\text{mm} \times 3.0\,\text{mm}$ clear epoxy resin pebble LEDs oriented along the natural flow of the wire to minimize wire bending and solder fatigue.
     - **✂️ Export Cut SVG (with 6×3mm Pill Slots):** 1-Click button in Section 2 opening the **Cricut HTV Cut File Exporter Modal**. Allows instant download of the complete multi-layer artwork with pre-punched tangent pill slots, mat-by-mat SVGs for each color vinyl sheet with 4-corner heat press registration marks, or standalone cutout templates.
      - **🧵 Wire Tension & Physical Spacing Heatmap (in cm) & Single-LED Wire Isolation:** Real-time physical distance validation between consecutive LEDs ($18" \times 24"$ garment model) displayed in centimeters (`cm`) and meters (`m`). Color-codes segments as 🔵 Fold (`<4.5 cm`), 🟢 Optimal Slack (`4.5–8.5 cm`), 🟡 Snug (`8.5–9.2 cm`), or 🔴 Taut Alert (`>9.2 cm`), displays strand metrics (total length, average pitch, max span), and includes a `🔍 Inspect Max Span` tool to immediately locate tight spans. Selecting any single LED on canvas automatically isolates and displays only its incoming ($i-1 \rightarrow i$) and outgoing ($i \rightarrow i+1$) wire segments, eliminating visual clutter!
   - **🪞 Bilateral Symmetry & Mirror Tool:**
     - `Show Centerline Axis (x = 50%)`: Dashed purple/cyan vertical guide with illuminated badges for precise centering.
     - `Live Mirror Drag (Sync Paired LEDs)`: Dragging any bulb automatically mirrors the movement of its symmetrical partner across the centerline in real time.
     - `⇄ Mirror Left → Right` / `⇆ Mirror Right → Left`: 1-click reflection that clones coordinates, preserves animation groups, auto-samples colors, and commits to Undo history.
   - **Quick-Link to Groups:** Fast-jump button to the Groups Tab for drawing paths or stamping fireworks.

2. **✨ Tab 2: Ambient ("Garment Baseline Atmosphere"):**
   - **Baseline Concept Clarity:** Clarifies the core architecture: these patterns, speeds, and sparkle dynamics set the continuous default look for all LEDs not assigned to a specialized 👥 Animation Group (such as spinning wheels, eyes, scales, or fireworks). Specialized groups overlay their own animations on top of this background canvas.
   - **Real-Time Baseline Allocation Badge:** Displays live coverage metrics (e.g. `100 of 100 LEDs (100% Baseline)` or `64 of 100 LEDs (64% Baseline)` when groups exist).
   - **Baseline Lighting Pattern & Direction:** Select from continuous background patterns (Steady Sparkle, Color Match, Fire Breath, Traveling Wave, Marquee, Fireworks, Photo Mode, Comet, Scanner, Color Wipe, Pixie Dust, etc.) with selectable **Travel Direction** (`Forward ➡️ Head to Tail` or `Reverse ⬅️ Tail to Head`) matching the animation direction conventions of Tabs 3 and 4.
   - **Microcontroller Firmware Dynamics (ESP32 Flash):**
     - **Speed / Tempo BPM with Quick Chips:** Adjust continuous animation tempo via slider or one-touch speed chips: `🚶 90 BPM` (Parade Walk), `🏃 120 BPM` (MSEP Cadence), `⚡ 144 BPM` (Upbeat Swing), `🚀 180 BPM` (Theatrical Sprint).
     - **Sparkle Frequency with Quick Chips:** Regulate random starlight frequency from 0% to 10% via slider or instant chips: `🌑 0%` (Static/Clean), `✨ 0.5%` (Subtle Starlight), `🌟 1.5%` (Classic Main Street), `💫 3.5%` (Enchanted Swarm).
     - **Sparkle Appearance & Color Temperature:** Selectable filament starlight styles:
       - `✨ Warm 2700K Filament (Soft Golden White)`: Replicates vintage Edison filament light bulbs.
       - `💎 Diamond Cool White (Pure Starlight)`: High-energy crisp white starlight.
       - `🌟 Pixie Dust Golden Amber`: Rich fantasy amber-gold starlight.
     - **Ambient Color Palette Mode:** Switch between 4 palette engines:
       - `🎨 Sampled Artwork Colors`: Default multi-color palette sampled directly from character artwork pixels.
       - `🏰 Float Signature Theme Color`: Automatically tint the garment baseline to the float's official theme color (Casey Jr. Locomotive Red, Drum Gold, Turtle Shell Teal, Snail Magenta, Cinderella Sky Blue, Pete's Dragon Emerald, America Patriot Red/White/Blue).
       - `💡 Vintage Incandescent`: 2700K warm-white uniform wash replicating classical parade bulb strings.
       - `🎯 Custom Uniform Color`: User-selected uniform tint with live color picker.
     - **Hardware LED Output:** Hardware brightness slider strictly governed by FastLED hardware power limits (5V, 2000mA max).
     - *(Note: Legacy single-float green hue slider has been retired in favor of the full 4-mode color palette system; the 140° emerald hue is retained silently as a procedural fallback for Pete's Dragon).*
   - **Simulator Display Optics (Browser Canvas Only):** Visually separated preview control for **LED Bloom / Glow Radius** (8px to 40px) to simulate optical light diffusion on fabric without affecting compiled ESP32 firmware.

3. **👥 Tab 3: Groups ("Group Creation Hub & Manager"):**
   - **LED Allocation Overview Box:** Real-time visual progress bar tracking how many LEDs are assigned to animation groups versus unassigned baseline.
   - **Unified Group Creation Hub:** 3 dedicated creation modes with full 16+ effect parity and one-touch tempo quick chips (`🚶 90`, `🏃 120`, `⚡ 144`, `🚀 180 BPM`):
     - 📦 **From Selection:** Save or update groups directly from canvas marquee box selections with 12 Disney palette swatches plus a native **Custom Hex Color Picker**.
     - ✏️ **Click-to-Draw Path:** Sequentially place LEDs directly on the shirt with full effect selection, speed chips, and a checkable option to auto-rearrange remaining unassigned LEDs to fill the graphic.
     - 🎆 **Fireworks Stamper:** Radial starburst generator with serpentine wiring, radius scale, and color themes.
   - **Docked Group Inspector Parity:** Selecting any group or member LED exposes identical 16+ animation effects, one-touch tempo chips, directional controls, palette swatches, and a dedicated **Custom Hex Color Picker** directly in the docked Inspector card.
   - **Active Groups Browser:** Card list of all configured groups with instant selection, badge metrics, and deletion controls.

4. **🎬 Tab 4: Float Show ("Individual Float Routine & Cue Timeline"):**
   - **Individual Standby Routine Scope:** Explicitly scripts theatrical animation sequences for **this specific float only** (e.g., carriage wheels spinning, dragon breath bursts, locomotive chuffing) while running autonomously between fleet shows.
   - **Fleet Routine Priority & Override:** When a synchronized **Fleet Show** triggers (from Tab 5 or a physical ESP32 button press), the fleet routine temporarily overrides all 7 costumes. As soon as the fleet routine concludes, this float seamlessly resumes its individual show sequence or baseline pattern!
   - **Active Float Banner & Fleet Quick-Jump:** An illuminated header displays the active float currently being sequenced (with signature accent styling) and includes a one-click jump button (`🏃 Fleet Tab ➔`) to transition directly to the 7-shirt fleet coordinator.
   - **Parade Cue Director & Per-Cue Customization:**
     - **90-Second Sequence Loop:** Sequence ON/OFF toggle, loop duration input, and expanded library of 6 float-themed example routines.
     - **Per-Cue Direction Control:** Independent travel direction selector (`➡️ Forward` / `⬅️ Reverse`) per cue card, allowing traveling waves, sweeps, or comets to reverse on cue.
     - **One-Touch Quick Chips:** Instant duration chips (`5s`, `10s`, `15s`, `30s`) and tempo BPM chips (`90`, `120`, `144`, `180`) right inside each cue card.
   - **Active Cue List:** Clean, scrollable cue cards displaying start time, duration, target layer/group, effect, direction, BPM, and quick delete.
   - **Quick Cue Insertion:** `➕ Add Cue at Playhead`, `⚡ Auto-Schedule Bursts`.

5. **🏃 Tab 5: Fleet ("7-Shirt Fleet Lineup & Routine Director"):**
   - **👑 30s Choreographed Parade Routine:**
     - Fully customizable multi-phase fleet routine coordinating all 7 costumes.
     - One-shot activation (`[Space]` / `[F]` hotkeys or button) with automatic return to baseline float programs upon completion.
     - Early return / emergency cancel support.
   - **Corral Radar & Roll Call:** Live ping monitoring of all 7 ESP32 nodes in the starting corral.
   - **Battery Life & Power Budget Calculator:** Real-time milliamp consumption modeling for 10K race endurance on portable 2.0A USB banks.
   - **7 Runner Slot Cards (Bib #01 to #07):** Assign presets to each runner, view live LED counts and pattern pills.
   - **1-Click Bidirectional Editing:** Jump any runner's preset directly into the Single Shirt editor (`✏️ Edit in Single View`), or copy the active single-shirt editor design to any runner or all 7 runners (`📥 Assign Editor`).

6. **⚡ Tab 6: Deploy ("The Workshop & Hardware Hub"):**
   - **USB Standalone Flashing:** Auto-detected COM port, connection status badge, 1-Click Flash firmware, View/Copy C++ code modal.
   - **📡 Real-Time Wi-Fi Live Stream:** Stream live colors & animations directly to physical LEDs over Wi-Fi without flashing ROM. Wi-Fi credentials modal.
   - **Web Serial Flasher:** Quick launch button for zero-install browser-based flashing.

### 💡 Contextual Inspector Dock (Docked at Bottom of Sidebar)
Instead of taking up vertical space in the middle of your workflow:
- **Standby State (No Selection or Draw Mode):** When no bulbs are selected, or while actively drawing a path on the shirt (`✏️ Click-to-Draw`), the Inspector rests as a quiet, compact status chip (`👆 Click an LED or drag on canvas to inspect`). It stays collapsed during drawing so you can place sequential points on the garment without distracting UI jumps or unwanted dock expansions.
- **Active State (Selected LED or Group):** When 1 or more LEDs are selected (or when editing a saved group), the Inspector automatically expands with an illuminated gold accent border:
  - LED number stepper (`◀ Prev`, `Next ▶`, `⌖ Focus`).
  - Color preview swatch, Hex & RGB badges, and RGB sliders.
  - Quick Disney Palette Swatches (12 signature theme park colors).
  - Group Animation Effect creator (Zone Name, Effect Pattern, Speed BPM, Direction, Resting Baseline, and Firework Burst Radius slider).
  - One-click deselect button (`✖`).

### ⤢ Collapsible Master Timeline
- Click **`⤢ Minimize`** in the transport bar to collapse the multi-layer cue tracks into a slim transport bar, giving the canvas full vertical workspace.
- Click **`⤢ Expand`** to restore the full multi-layer cue tracks and ruler when arranging show sequences.

### 🛡️ Zero-Risk Rollback System
The pre-overhaul UI state is permanently tagged and archived:
- Git Tag: `v1.0-pre-ui-overhaul` (`git checkout v1.0-pre-ui-overhaul -- simulator/`)
- Backup Archive: `simulator/archive_v1/` containing exact copies of `index.html`, `style.css`, and `app.js`.

---

## 5. Multi-LED Selection, Group Creation Hub & Click-to-Draw Path Tool

To create localized zone animations (like carriage wheels spinning, lanterns pulsing, spinal ridges glowing, or radiating starburst fireworks), you can organize LEDs into **Animation Groups**.

### Selecting Multiple LEDs
1. **Marquee Box Select:**
   - Click the **⬚ Box Select** button in the top toolbar, then click and drag a rectangular bounding box across any area of the canvas.
   - *Quick Shortcut:* Hold down the `Shift` key and drag anywhere on the canvas to draw a selection box immediately!
2. **Select All:** Click the **All** button or press `Ctrl + A` (`Cmd + A` on Mac) to select all LEDs on the float.
3. **Clear Selection:** Click **Clear** or press `Escape` to deselect all LEDs.

---

### ➕ The Unified Group Creation Hub (`👥 Groups` Tab)

The Group Creation Hub provides 3 dedicated, purpose-built workflows under unified tabs:

#### 1. 📦 Mode 1: From Selection
- Select 2 or more LEDs using **⬚ Box Select** or `Shift + Click`.
- The Hub automatically displays the number of selected LEDs and their index range (e.g. `✨ 16 LEDs Selected · Indices: #12–27`).
- If the selection matches an existing group, fields automatically populate and the button reflects **`💾 Update Group "[Name]"`**.
- Otherwise, configure Group Name, Effect Pattern, Direction (➡️ Forward / ⬅️ Reverse), Speed (BPM), and Resting Baseline, then click **`💾 Save Selection as Group`**.

#### 2. ✏️ Mode 2: Click-to-Draw Sequential Path Tool
The **Click-to-Draw Path Tool** lets you place sequential LEDs one-by-one directly onto the shirt canvas by simply clicking where you want each light:
- **Activation:**
  - Click the **`[✏️ Draw Group]`** button in the top canvas toolbar, OR
  - Click **`[✏️ Start Drawing on Shirt]`** in the Group Creation Hub (Draw mode), OR
  - Switch to the Groups tab and click **`✏️ Click-to-Draw`**.
- **Distraction-Free Drawing Experience:**
  - While drawing points on the shirt, the docked Inspector is automatically held in collapsed standby (`dock-empty`). Placed points are tracked cleanly without triggering premature dock expansions, button shifts, or field flashing, keeping your view on the canvas completely unobstructed.
- **Visual In-Progress Guide:**
  - A prominent floating **Canvas Drawing Banner** appears above the shirt with an active pulse indicator and placed LED count.
  - A glowing gold dashed line connects your clicks in real time.
  - Each placed point is highlighted with a gold circular badge displaying its sequence step number (`1`, `2`, `3`...).
- **Contiguous LED Allocation Algorithm:**
  - Each click takes from the available costume LEDs while preserving the strict **100-LED invariant**.
  - LED indices are allocated contiguously (#24, #25, #26...) whenever possible. This ensures directional animations like **Chase**, **Write-On / Wipe**, and **Traveling Waves** flow smoothly in the exact chronological order of your clicks!
- **Color Auto-Sampling:**
  - Each placed point automatically samples the pixel color from the underlying character graphic (Pete's Dragon, Cinderella's Coach, or custom artwork).
- **Finishing & Saving with Auto-Rearrange:**
  - Press `Enter` on your keyboard, click **`✅ Done`** on the canvas floating banner, or click **`✅ Finish & Save`** in the sidebar.
  - The newly created group is saved, immediately selected, and opened in the editor for fine-tuning.
  - **Auto-Rearrange Option (Checkable):** By default, the `🔄 Auto-rearrange remaining LEDs` checkbox is enabled (available in both the Click-to-Draw panel and the canvas floating banner). When saved, all non-grouped LEDs are automatically redistributed across open spaces of the graphic using Farthest-Point Sampling. The existing grouped LEDs serve as fixed distance anchors so remaining lights never collide with or crowd your custom path.
- **Safe Cancellation:**
  - Press `Escape` or click **`❌ Cancel`** on the canvas banner to exit draw mode without saving. All LED positions are instantly restored to their exact pre-draw coordinates.
- **Manual "Fill Graphic with Remaining LEDs" Button (Layout Tab):**
  - Located on the Layout Tab (`🎨 Layout`) under both Shirt Artwork and LED Layout (`🔄 Fill Graphic with Remaining LEDs`).
  - At any time, clicking this button scans all currently assigned groups and evenly redistributes all remaining non-grouped LEDs across the open areas of the character graphic without modifying any grouped LEDs or changing total LED count (always 100). Perfect for refreshing the background layout if points ever become uneven or after editing groups!

#### 3. 🌟 Mode 3: Shape & Flourish Stamp Library
The **Stamp Library** combines our **Fireworks Starburst Generator** with a full suite of parametric geometric shape stamps:
- **Shape Selection Grid:**
  - 💥 **Fireworks Starburst:** Multi-ray radial explosion with serpentine wiring, customizable burst radius, uniform/custom ray colors, and timeline cue auto-scheduling.
  - ⭕ **Circle / Wheel:** Perfect for Cinderella's carriage wheels, Casey Jr.'s locomotive drivers, and turtle shell rings (configurable radius, LED count 4–30, and full $360^\circ$ vs. arc span).
  - 🌈 **Arch / Canopy:** Parabolic and catenary arches for carriage roofs, dragon brows, and turtle shell domes (upright vs. inverted curvature).
  - 🌊 **Wave / Serpentine:** Sine wave puffs for locomotive steam trails, Elliott's dragon fire breath, and water ripples (configurable amplitude, length, and 1–5 cycle count).
  - ⭐ **Star / Sparkle:** 4-point sparkles and 5-point starbursts for Disney starlight flourishes.
  - ▬ **Straight Line / Ruler:** Evenly-spaced horizontal, vertical, or diagonal line bars for marquee borders, flag stripes, and cowcatcher slats.
- **Position Placement Options:**
  - Quick Presets: `↖ Top-Left`, `↗ Top-Right`, `⏺ Center`.
  - Precision Sliders: Move X% and Move Y% sliders.
  - **`🎯 Click Canvas to Place`**: Click anywhere on the garment canvas to drop the stamp centroid $(\bar{x}, \bar{y})$ directly at your cursor location!
- **Automatic Budget & Unused Pool Management:**
  - Every stamped shape verifies available unassigned LEDs to enforce the **100-LED invariant**.
  - Automatically resamples underlying graphic pixel colors and redistributes remaining unassigned LEDs across open graphic space.
  - Fully integrated with the **Universal Undo / Redo Engine (`Ctrl+Z`)**.

#### 4. 🛠️ Mode 4: Group Transformations Suite & Clipboard (Copy, Paste, Rotate, Flip, Scale)
The Animation Groups editor includes full spatial transformations and cross-shirt group clipboard support:
- **📋 Copy & Paste Group (Within & Between Shirt Designs):**
  - Click **`📋 Copy`** on any group card or in the docked Inspector dock, or press `Ctrl + C` (`Cmd + C`).
  - Switch to any runner slot or shirt design (Float 1 through Float 7) and click **`📋 Paste Group`** (in the section header, Inspector, or press `Ctrl + V`).
  - **100-LED Unused Pool Budget Guard:** Pasted LEDs are automatically allocated from the target shirt's unused LED pool. If the target shirt has fewer unused LEDs available than required, a toast warning blocks the action to maintain our 100-LED invariant.
  - **Relative Coordinate Mapping & Artwork Color Sampling:** Member LEDs map relative to the target shirt's chest graphic area ($\text{relX}, \text{relY}$) and dynamically resample artwork pixel colors for a crisp visual match!
- **🔄 Rotate Group (90° Quick Action & Continuous Angle):**
  - Click **`🔄 Rotate 90°`** (or press `Ctrl + R`), or use card action **`🔄 90°`** to rotate member LEDs around the group's centroid $(\bar{x}, \bar{y})$.
- **↔️ Flip Horizontal & ↕️ Flip Vertical:**
  - Mirror groups across their bounding centroid to adapt left-shoulder or right-shoulder flourishes across paired costumes.
- **🔍 Scale LED Spacing (Expanding / Contracting Size):**
  - Click **`🔍+ 110%`** (Expand) or **`🔍- 90%`** (Contract), or use the continuous **Scale LED Spacing Slider (50% to 200%)** to adjust spacing between LEDs around the centroid while maintaining the exact geometric shape!
- **🖱️ Group Canvas Dragging (Click & Drag Entire Group):**
  - Simply click and drag **any LED** belonging to an animation group on the canvas. The entire group automatically selects and moves together as a unified cluster, preserving internal LED spacing while resampling underlying graphic colors upon release.
- **Auto-Rearrange Integration:**
  - After pasting or transforming a group, remaining unassigned LEDs ($100 - \text{total assigned}$) are **automatically redistributed** evenly across open graphic space using Farthest-Point Sampling.

---

### 👥 LED Allocation Overview & Active Groups Browser
- **Allocation Progress Bar:** Real-time visual progress bar tracking how many LEDs are assigned to animation groups versus unassigned. Displays total assigned percentage and count (e.g. `24 / 100 LEDs (24%) assigned to groups`).
- **Quick Selection Actions:**
  - **`👥 Select All Grouped`**: Instantly selects all LEDs currently belonging to any group across the entire costume for bulk review.
  - **`⚡ Select Unassigned`**: Immediately highlights all ungrouped LEDs so you can quickly bundle remaining costume LEDs into a new zone with one click!
- **Rich Interactive Group Cards (`#activeGroupsList`):**
  - **Header:** Group emoji icon (e.g., 🎆 for fireworks, 🎡 for chase, 🎪 for marquee), bold group name, and total LED count badge.
  - **Badges:** Effect pill (`🎡 Chase @ 140 BPM`), Starburst geometry details (for fireworks: ray count and burst radius), Resting Baseline pill (`Idle: Off / Unlit`), and physical LED index ranges (`LEDs: #0–15`).
  - **Action Buttons:** `🎯 Select`, `📋 Copy`, `🔄 90°`, `➕ Cue`, `🗑️ Delete`.
  - **Instant Selection & Canvas Focus:** Clicking anywhere on a group card or clicking **`🎯 Select`** highlights all member LEDs on the canvas, opens their properties in the docked Inspector, and marks the card with a glowing active border.
  - **1-Click Show Cue Shortcut:** Click the **`➕ Cue`** button directly on any card to create a synchronized Show Cue on the Master Timeline—pre-configured with the group's effect and tempo—and immediately jump to the Parade Cue Director tab!
  - **One-Click Deletion:** Click the red **🗑️** button to delete a group, return its LEDs to the global baseline, and clean up associated timeline cues.

### 🎨 Group Color Palette Override & Multi-LED Color Control
When a group is selected (or when editing an existing group), changing its color applies cleanly across all member LEDs while maintaining group selection:
- **Dedicated Palette Swatches in Group Hub & Docked Inspector:** Click any of the 12 signature Disney parade color swatches (Dragon Green, Flame Orange, Electric Pink, Cinderella Blue, Belle Gold, Starlight White, Cheshire Violet, Mickey Red, Electric Lime, Alice Cyan, Coral Rose, Deep Indigo) or use the native color picker and RGB sliders.
- **Bulk Multi-LED Application:** The selected color updates every individual LED in the group, sets `activeGrp.colorMode = 'custom'` and `activeGrp.customColor`, and dynamically colors the group's animation routine on the canvas without collapsing the multi-LED selection.
- **Use Artwork Colors Reset Button:** Click **`Use Artwork Colors`** in the Group Hub to instantly restore the original sampled costume artwork colors for all member LEDs and reset `activeGrp.colorMode = 'original'`.

### 💡 Contextual Inspector Workflow: Explicit "Save Group" & Reliable In-Place Editing
Creating and editing groups is seamlessly integrated into both the Group Creation Hub (`From Selection` panel) and the docked Inspector at the bottom of the sidebar:
1. **Clear Empty State with Quick Group Chips:** When 0 LEDs are selected, the Inspector displays clickable group chips (e.g. `[🎆 Fireworks 1 (20)]`, `[🎡 Front Wheel (16)]`). Clicking any chip immediately selects that group from anywhere in the application!
2. **Dynamic Action Button & State Tracking:**
   - **New Group Creation:** When new LEDs are selected, the primary action button clearly reads **`💾 Save Selection as Group`** (green accent).
   - **Reliable In-Place Editing:** Clicking **`🎯 Select & Edit`** on any group card sets the active edit context (`selectedGroupId`). All form fields in both the Groups Hub and the docked Inspector automatically populate with that group's settings. The button dynamically shifts to **`💾 Update Group "[Name]"`** (blue accent).
   - **Bidirectional Two-Way Form Sync:** Modifying the Name, Effect, Speed (BPM), Direction, Resting Baseline, or Fireworks Burst Radius in either the Hub or the docked Inspector instantly syncs to the other.
   - **Immutable ID Preservation:** Clicking **`💾 Update Group`** saves changes directly to the existing group in-place using its unique group ID. Renaming a group updates its name immediately without creating unwanted duplicates or losing member LED assignments.
3. **Group Configuration Parameters:**
   - **Direction:** Select **Forward (➡️)** or **Reverse (⬅️)** for directional chase animations (crucial for ensuring left and right carriage wheels appear to roll forward!).
    - **🔄 Phase Offset ($0^\circ \dots 360^\circ$) & Dual-Wheel Anti-Phase:**
      - Adjust the **Phase Offset Slider ($0^\circ \dots 360^\circ$)** to control the exact rotational or wave timing of the group relative to the global beat clock ($\text{effectiveTimeMs} = \text{timeMs} + \frac{\text{deg}}{360} \cdot T_{\text{beat}}$).
      - **Quick Preset Badges:** One-click presets for `0° (Synced)`, `90° (Quarter Phase)`, `180° (Anti-Phase)`, and `270° (3/4 Phase)`.
      - **Dual Wheel Anti-Phase Simulation:** Set the front carriage wheel to $0^\circ$ and the rear carriage wheel to $180^\circ$ so that as one wheel's spoke crests at 12 o'clock, the other crests at 6 o'clock—creating mesmerizing organic mechanical realism!
    - **🔗 Sync Speed With (Master-Follower Tempo Coupling):**
      - Link any child group to a master group (e.g., link *Rear Wheel* to *Front Wheel*). Whenever you modify the master group's BPM slider, all follower groups dynamically inherit the new tempo in real time while maintaining their independent phase offsets!
    - **🔀 Auto-Stagger Phase Button:**
      - In the Active Groups section header, click **`🔀 Auto-Stagger Phase`** to automatically divide and distribute full $360^\circ$ phase cycles evenly across all active groups ($360^\circ / N$). Perfect for multi-tier turtle/snail whorls or starburst cascades. Fully undoable via `Ctrl+Z`.
   - **Group Effect:** Choose an effect from the dropdown:
     - *🎡 Chase / Wheel Spin:* Chases illuminated heads around the ring.
     - *💓 Breathing Glow Pulse:* Pulses the group in sync or out of phase with the baseline.
     - *💡 Slow Flashing / Blink:* Theatrical blinking.
     - *✍️ Write-On / Write-Off:* Successively illuminates the group in sequence.
     - *✨ Sparkle Storm:* High-energy glitter and sparkle storm.
     - *🎪 Theater Marquee:* 3-phase theatrical marquee chase.
     - *🌈 Rainbow Color Wave:* Smooth cycling rainbow wave across the group.
     - *🎆 Fireworks (Radiating Starburst):* 4-phase pyrotechnic explosion with center ignition flash, outward expanding spark trails with decaying ember tails, starlight tip crackles, and dark sky resets. Uses serpentine wiring geometry for maximum solder efficiency.
     - *🌑 Off / Completely Unlit:* Keeps the group unlit.
   - **Dedicated Firework Burst Scale / Radius Controls:** When an inspected group is set to `fireworks`, an interactive **Firework Burst Scale / Radius** panel automatically appears directly inside the Group Inspector card:
     - *Dynamic Radius Slider:* Continuously scale the explosion radius from **5%** (tight, compact burst) to **28%** (wide, theatrical starburst across the entire upper torso).
     - *Quick Preset Buttons:* Instant one-click size presets: **S (8%)**, **M (13% - Default)**, **L (18%)**, and **XL (24%)** with visual active-state highlighting.
     - *Bidirectional Live Sync:* Adjusting size in the Group Inspector instantly synchronizes the Section 5a Fireworks Generator card, updates LED positions on the canvas, recalculates wiring lengths, and reflects across all inspector coordinate readouts.
   - **Resting Baseline Effect (When Idle / No Cue):** Configure what the group does when resting outside active timeline cues in Sequence Mode (100% option parity with Tab 2 Ambient patterns):
     - *🌐 Follow Overall Baseline (Default):* The group seamlessly follows the overall float background pattern/cue (e.g. `steady_sparkle`), matching all non-grouped float LEDs.
     - *🌑 Off / Completely Unlit:* The group stays 100% dark (pitch black) outside active cues. Default for fireworks, and ideal for theatrical accents like carriage lanterns, Elliott's dragon fire breathing, or Casey Jr.'s headlight until detonated/triggered on the timeline!
     - *✨ Steady Colors + Occasional Sparkle:* Calm starlight twinkling on group pixels.
     - *🌬️ Slo-Glo Breath (Color-Matched Glow):* Gentle ~30–45 BPM breathing glow preserving sampled artwork hues.
     - *☄️ Meteor / Comet Trail:* Continuous looping comet head with a glowing exponential tail circling group perimeters.
     - *🛸 Larson Scanner (Ping-Pong Sweep):* Dynamic back-and-forth beam sweep with smooth turnaround wakes.
     - *✍️ Color Wipe / Progressive Fill:* 4-phase write-on fill, radiant hold, wipe-off, and rest.
     - *💫 Pixie Dust Drift:* Drifting starlight shimmer cascade rolling across the group.
     - *⚡ Vintage 1972 Filament:* Micro-voltage analog warmth mimicking Walt Disney World's original incandescent parade bulbs.
     - *🕯️ Candle / Lantern Flame:* Warm amber/gold organic flame flicker with random multi-harmonic micro-jitter.
     - *🌊 Tidal Ripple:* Radial wavefront expanding and contracting from group centroid.
     - *🚂 Locomotive Piston Chug:* 4-stroke mechanical cadence pulse with sharp power stroke and exhaust.
     - *🎪 Classic Marquee Chase:* 3-phase chasing incandescent border.
     - *🎆 Fireworks (Radiating Starburst):* Full pyrotechnic explosion sequence.
     - *🌈 Rainbow Wave:* Flowing chromatic wave across the group.
     - *📸 Castle Photo Mode:* 100% solid maximum radiance for photo stops.
     - *🔦 Flashlight / Searchlight Roam:* 2D roaming light pool wandering smoothly across the garment with a soft Gaussian beam wake.
     - *🐭 Scurrying Mouse (Single Dot + Tail):* Single ultra-bright point (1 LED) with a long trailing glowing tail (~20 LEDs) that races and scampers along the strand in non-linear bursts with quick direction reversals.
     - *Cue Crossfading:* When an active cue on that group fires, the show engine smoothly crossfades from the group's configured resting baseline into the active cue effect, and seamlessly returns to baseline when the cue ends.

---

## 6. Physical Wiring Route Optimization (10cm Wire Pitch & Slack-Aware Tour)

Attaching LEDs to a shirt by hand can easily result in tangled wire spaghetti or severe wire bunching if the layout ignores physical wire pitch. The simulator solves this with an advanced **10cm physical wire slack-targeted routing optimizer**.

### How It Works
1. **10cm Physical Wire Pitch Calibration:** Wearable WS2812B pebble/fairy light strands have a fixed **10.0 cm (100 mm / ~3.94") wire pitch** between consecutive nodes.
2. **Slack-Targeted Cost Function:** Instead of blindly connecting to the closest spatial neighbor (which averages only 1.6 cm apart and forces 8+ cm of excess wire to be accordion-folded on every step!), the router targets an optimal **6.0 cm to 8.0 cm (2.4" to 3.15") straight-line span**.
3. **Gentle Natural Slack (Zero Accordion Folding):** This leaves **2.0 cm to 4.0 cm (20% to 40%) of relaxed, comfortable wire slack** behind the mesh. The wire hangs in a natural, flat curve that flexes with the runner's body over the 10K course without requiring any folding, looping, or tape bundles!
4. **Hard Physical Reach Constraints:** Strictly bounds every span to $\le 9.2\text{ cm}$, guaranteeing no wire segment is pulled taut or strained.
5. **Interactive Controls:**
   - Click **`🔌 Optimize Wiring Route (10cm Slack)`** in Tab 1 to re-route all LEDs with this slack optimization.
   - Toggle **`🧵 Wire Tension Heatmap`** to view color-coded segments:
      - 🔵 **Blue (`<4.5 cm`):** Excess Slack / Folding Warning.
      - 🟢 **Green (`4.5–8.5 cm`):** Optimal Slack Sweet Spot (Flat, zero-fold fit).
      - 🟡 **Yellow (`8.5–9.2 cm`):** Snug (minimal slack).
      - 🔴 **Red (`>9.2 cm`):** Overstretched Alert (Taut).
   - **Single LED Selection Isolation:** Selecting any individual LED automatically isolates the wiring visualization to only the segment arriving at the LED ($i-1 \rightarrow i$) and the segment departing from it ($i \rightarrow i+1$), removing background wire clutter for focused alignment.

### 🎆 Fireworks Starburst Generator, Multi-Burst Stamping, & Scaling
Creating radial fireworks bursts requires clean geometry, flexible placement, and predictable physical wiring:
1. **Multi-Burst Stamping & Smart Offset Positioning:**
   - Click **"🎆 Stamp Fireworks Burst (+ Add Another)"** to stamp one or more firework bursts onto the costume.
   - **Smart Offset Placement:** The first burst defaults to the upper corner (**↖ Top-Left corner** at $x = 28\%, y = 22\%$, above the race bib clearance zone). Subsequent bursts are automatically positioned with a distinct visual offset (Firework #2 at $x = 58\%, y = 26\%$, Firework #3 at $x = 38\%, y = 40\%$, etc.) so you can immediately see multiple fireworks side-by-side without any overlap.
   - **Active Firework Group Selector:** When multiple fireworks exist, an **Active Firework Group** dropdown appears directly in the controls card. Selecting any firework instantly syncs the Move X/Y sliders, radius slider, and color controls to that specific cluster, and highlights its LEDs on the canvas.
   - **One-Click Group Deletion:** Click **"🗑️ Remove"** next to the active firework selector to cleanly delete that specific firework group, remove its timeline cues, and automatically re-distribute the reclaimed LEDs back to the character graphic.
   - **Direct Canvas Selection:** Clicking or dragging any LED of a firework cluster on canvas automatically selects that firework in the Active Group dropdown and updates all sliders in real time!
2. **Move & Scale Controls (Geometry Box & Quick Presets):**
   - **Consolidated Position & Scale Geometry Box:** Section 5a groups Move X, Move Y, and Scale / Burst Radius together in a dedicated high-contrast dark panel (`📐 Position & Scale (Size)`) right above the color controls.
   - **Move X & Move Y Sliders:** Fine-tune position horizontally ($15\% - 85\%$) and vertically ($15\% - 55\%$) with live badge percentage feedback.
   - **Scale / Burst Radius Slider & Quick Presets:** Dynamically expand or contract the burst diameter ($5\% - 28\%$, default $13\%$) with live slider feedback or click any of the 4 quick preset buttons:
     - **S (8%):** Tight, compact accent burst.
     - **M (13%):** Standard balanced Disney fireworks burst (default).
     - **L (18%):** Expanded starburst spanning the upper chest.
     - **XL (24%):** Grand finale burst spanning the entire upper chest width.
   - **Dual-Card Synchronization:** The Scale / Burst Radius slider and S/M/L/XL buttons are available and bidirectional across **both** Section 5a (Fireworks Card) and Section 5b (Group Animation Inspector).
   - **Direct Canvas Multi-Drag:** Simply click and drag any LED belonging to any firework cluster directly on the costume canvas! The entire starburst moves as a unified group, and the Move X/Move Y sliders update synchronously in real-time.
3. **Uniform Color per Firework Group (Presets & Custom Color Picker):**
   - **Uniform Ray Color:** All rays of a firework group share the **exact same uniform color** (e.g. all 5 rays Golden Amber, all 5 rays Alice Cyan, etc.) for a clean, coherent theatrical pyrotechnic burst.
   - **Automatic Palette Rotation:** Stamping additional fireworks automatically assigns a contrasting color from the signature palette (**✨ Golden Amber**, **💠 Alice Cyan**, **💖 Coral Rose**, **⚡ Electric Lime**, **💜 Royal Violet**, **🔥 Blazing Red-Orange**, or **⭐ Starlight White**).
   - Select **🎨 Custom Hex Color...** to open an interactive native color picker and dial in any specific hex color.
   - Changing colors updates all rays of the active cluster in real time while maintaining warm incandescent shifts along the trailing rays.
4. **Persistent Center Trailing Effect & Completely Off (Unlit) Baseline:**
   - In previous iterations, all LEDs dimmed out as the wavefront moved or bled into global background patterns. Now:
     - *Completely Off (Unlit) Baseline:* Outside active explosion cues, all firework LEDs remain **100% off (unlit)**. They do not participate in global background chases or ambient sparkles, keeping the firework location dark and invisible until detonation. Unlit LEDs render realistically on canvas as dark SMD pixel beads (`rgba(22, 26, 33, 0.85)`) without artificial central white filament cores or glow bloom.
     - *Phase 1 (Ignition):* Center flashes with white-hot brilliance while outer unreached LEDs remain completely dark (unlit).
     - *Phase 2 (Expanding Wavefront):* Center LEDs hold at high intensity ($\sim 70\%$) while trailing embers bridge the line out to the spark head, creating a continuous radiating streak of fire. Ahead of the expanding wavefront, outer LEDs stay completely unlit.
     - *Phase 3 (Tip Crackle):* Center stays lit ($\sim 50\%$) as a visual anchor while outer tips crackle; burned-out inner steps turn completely off.
     - *Phase 4 (Rest / Idle):* Burst concludes, all firework LEDs fade out completely to **0% intensity (black/unlit)** until the next scheduled burst.
5. **Master Timeline Scheduling & Explosion Cue Director:**
   - **Automatic Timeline Auto-Placement:** Stamping a fireworks cluster automatically creates and schedules fireworks explosion cues on the Master Timeline in the Parade Cue Director and turns Sequence Mode ON.
   - **Orchestrated Multi-Firework Staggering:** When stamping multiple fireworks, burst cues are automatically staggered by $+2.5\,\text{s}$ per group index (e.g. Firework #1 detonates at 6.0s, Firework #2 detonates at 8.5s) to produce an orchestrated, multi-stage fireworks show across your costume!
   - **Auto-Schedule Bursts:** Click **"⚡ Auto-Schedule Bursts"** in the Fireworks card to re-populate recurring explosion bursts evenly spaced across the full loop duration.
   - **Single Cue at Playhead:** Click **"⏱️ Add at Playhead"** to drop a burst cue for the active firework right at the current scrubber playhead position.
   - **Cue-Relative Phase Sync:** The firework explosion phase automatically synchronizes with the cue's start time ($t = \text{startTime}$ triggers Phase 0 ignition), ensuring the starburst explodes precisely on the theatrical cue!
   - You can schedule multiple fireworks cues throughout your parade loop, adjust BPM, and customize crossfade in/out times.
6. **Rays & Length Customization:**
   - Choose between **4, 5, or 6 Rays** radiating from the explosion origin.
   - Choose between **3, 4, or 5 LEDs per Ray** (e.g. 5 rays $\times$ 4 LEDs = 20 LEDs; $100 - 20 = 80$ other LEDs).
7. **Serpentine Wiring Geometry:**
   - To eliminate long, messy return wires from outer spoke tips back to the center hub, the generator utilizes **continuous serpentine routing**:
     - *Even Rays (0, 2, 4):* Wire travels outward (**Center $\to$ Tip**).
     - *Odd Rays (1, 3, 5):* Wire travels inward (**Tip $\to$ Center**), with a short 1-inch jump between adjacent spoke tips.
   - The animation engine automatically compensates for reversed rays, ensuring all lines visually radiate outward from the center simultaneously!
8. **Strict 100-LED Invariant & Full-Graphic Re-Distribution:**
   - Placing firework clusters claims LEDs from the float pool, preserving exactly **100 LEDs on screen** at all times ($N_{\text{float}} + \sum N_{\text{fw}} = 100$).
   - Click **"🔄 Re-distribute Other LEDs (Full Graphic)"** to re-distribute non-firework LEDs across the **entire character graphic** (without any exclusion zone) while keeping all existing firework clusters intact at their configured coordinates.
9. **Canvas Numbering & Identification:**
   - With **Show Numbers** active or when inspecting bulbs, each firework LED displays its exact ray and step badge: e.g. `R1:1 (CTR)`, `R1:4 (TIP)`, `R2:1 (CTR)`, `R2:4 (TIP)`.
   - The LED Inspector displays the full role breakdown: e.g. `Ray 2 of 5 • Trail Step 3 (Mid-Trail)`.

---

## 7. Artwork Management & runDisney 10K Race Bib Overlay

You can choose from pre-loaded Disney parade artwork or upload your own high-resolution shirt graphics, complete with realistic race bib collision checking.

### Built-in Graphic Presets
Use the **Costume Graphic** dropdown in the Layout tab (Section 1) to instantly switch between all official parade units with automatic preset loading:
- **🚂 Float 01: Casey Jr. Locomotive (`casey_jr_train`):** Iconic circus engine with spinning drive wheels, illuminated cab, and flashing strobe headlight.
- **🥁 Float 02: The Title Drum (`title_drum`):** Massive illuminated bass drum with amber chase rim and classic marquee lighting.
- **🐢 Float 03: The Spinning Turtle (`spinning_turtle`):** Whimsical sea turtle with concentric spinning shell spiral and glowing fins.
- **🐌 Float 04: The Spinning Snail (`spinning_snail`):** Colorful garden snail with multi-tier shell whorls and neon antenna bulbs.
- **🎃 Float 05: Cinderella's Coach (`cinderellas_coach`):** Golden carriage outline with dual spinning wheels, pumpkin body, and royal lanterns.
- **🎠 Float 05: Carriage (No Horses) (`carriage_nohorses`):** Focused Cinderella coach design with clean wheel arches, royal carriage frame, and dedicated 100-LED preset.
- **🐉 Float 06: Pete's Dragon (Elliott) (`builtin_dragon`):** Default 100-LED layout with emerald body scales, magenta hair crest, and incandescent starlight sparkles.
- **🦅 Float 07: To Honor America (`honor_america_eagle`):** Grand patriotic eagle finale with sweeping red, white, and blue wing chases.

### Proportional Chest Graphic Scaling
All artwork graphics are automatically scaled to sit comfortably in the chest area above the race bib (`y = 0.168` to `0.553`):
- **Exact Aspect Ratio:** Strictly preserves each graphic's original $x / y$ pixel ratio without stretching, squishing, or distortion.
- **Automatic Clearance:** Leaves a clean fabric margin between the bottom-most LEDs and the top of the race bib, ensuring no LEDs or wiring sit directly under bib clamp points.

### 🏷️ runDisney 10K Race Bib (#1952) with Chip & Dale
Section 4 features an authentic runDisney race bib overlay (default **8.0" wide by 7.0" high**, matching physical runDisney bib specs on an 18" x 24" running shirt) on the lower torso to verify physical clearance with your running gear:
- **Mostly Yellow Tyvek Theme:** Official sunny yellow gradient background (`#fef9c3` to `#facc15`), golden amber trim (`#ca8a04`), subtle athletic speed chevrons, and red/blue racing side stripes.
- **Official Chip 'n' Dale Mascots:**
  - **Chip (Left Flank):** Chocolate chip black nose, single centered buck tooth, dark chocolate brown fur, cream muzzle, and red runner's headband.
  - **Dale (Right Flank):** Signature big shiny red nose, messy hair tuft between ears, two separated buck teeth, playful winking eye, and royal blue & gold runner's headband.
  - **Acorn Accents:** Golden acorns (`🌰`) flanking the runner sub-label `MSEP RUNNER`.
- **Top Header Banner:** Royal Disney Navy banner (`#1e1b4b` ➔ `#312e81`) with gold trim, `★ runDisney`, `WALT DISNEY WORLD® 10K`, official `CHIP 'N' DALE 10K` title ribbon, and `CORRAL A` badge.
- **Center Race Number:** High-contrast athletic number **`1952`** with crisp white outline and dark slate fill.
- **PhotoPass Barcode:** Lower barcode window with `DIS-1952-10K`.
- **BibBoards Fasteners:** Accurately renders the snap-and-lock circular pucks at all 4 corners (outer casing, cyan accent ring, center dome button with specular highlight) so you can visually verify clearance before pinning your shirt!
- **Interactive UI Controls (Section 4):**
  - **Toggle Checkbox:** Show/Hide the bib overlay at any time.
  - **Height Slider:** Adjust vertical elevation on the torso (range: 50% to 75%, default **57%**).
  - **Scale Slider:** Dynamically resize the bib from **60% to 140%** (default **100%**) while preserving all internal artwork, character illustrations, and clamp points.

### Custom Artwork Upload
1. In Section 1, choose **"Upload Custom Artwork Image"**.
2. Select any high-resolution transparent PNG or JPEG image from your computer.
3. The simulator immediately renders your artwork in the center of the shirt canvas.
4. Click **"✨ Scatter 100 Color-Matched LEDs"**:
   - The simulator uses a multi-pass Poisson disk scatter to distribute 100 LEDs evenly across your graphic.
   - It samples the true RGB pixel color beneath each LED, automatically creating a color-matched palette!
5. Click **"🔄 Resample Colors from Artwork"** at any time to re-sample pixel values if you change or replace the artwork.

### ✂️ Cricut Heat Transfer Vinyl (HTV) Cut Files & Exporter Suite
Production-ready layered vector SVG files for all 7 floats are included in `assets/cricut_svg/`:
- **The Train / Casey Jr.:** [`assets/cricut_svg/casey_jr_train.svg`](assets/cricut_svg/casey_jr_train.svg) (4 mats: Red, Gold, Cyan, White)
- **The Title Drum:** [`assets/cricut_svg/title_drum.svg`](assets/cricut_svg/title_drum.svg) (4 mats: Navy, Gold, Cyan, White)
- **The Spinning Turtle:** [`assets/cricut_svg/spinning_turtle.svg`](assets/cricut_svg/spinning_turtle.svg) (4 mats: Teal, Yellow, Red, White)
- **The Spinning Snail:** [`assets/cricut_svg/spinning_snail.svg`](assets/cricut_svg/spinning_snail.svg) (4 mats: Yellow, Pink, Cyan, White)
- **Cinderella's Coach:** [`assets/cricut_svg/cinderella_coach.svg`](assets/cricut_svg/cinderella_coach.svg) (3 mats: Cyan, Gold, White)
- **Pete's Dragon (Elliott):** [`assets/cricut_svg/petes_dragon.svg`](assets/cricut_svg/petes_dragon.svg) (4 mats: Green, Pink, Orange, White)
- **To Honor America (Flag & Eagle):** [`assets/cricut_svg/honor_america_eagle.svg`](assets/cricut_svg/honor_america_eagle.svg) (4 mats: Blue, Red, Gold, White)
- **Interactive Visual Catalog:** Double-click [`assets/cricut_svg/cricut_catalog.html`](assets/cricut_svg/cricut_catalog.html) to inspect layers, preview specs, and download files.
- See **[`CRICUT_ARTWORK_GUIDE.md`](CRICUT_ARTWORK_GUIDE.md)** for complete step-by-step Cricut Design Space upload, mat mirroring, multi-layer tack press temps, and LED attachment guides.

#### 🌟 1-Click Cricut Cut Exporter Modal (`✂️ Export Cut SVG`)
Clicking **`✂️ Export Cut SVG`** on Tab 1 (Layout) opens a dedicated production dialog with 3 export workflows:
1. **🌟 Master All-in-One Multi-Layer SVG (Recommended for Cricut):**
   - Combines the full multi-colored vector character artwork with all 100 tangent-oriented $6.0\,\text{mm} \times 3.0\,\text{mm}$ pill slots and 4-corner heat press registration marks into a single SVG file.
   - Cricut Design Space automatically parses the file and sorts each color onto its own cutting mat, with the pill cutouts already positioned in place!
2. **🎨 Mat-by-Mat SVGs (Single Color Mats):**
   - Individual download buttons for each color vinyl sheet (e.g. Green Mat, Pink Mat, Orange Mat, White Mat).
   - Each file isolates one color layer, includes 4-corner registration crosshairs, and embeds only the pill cutouts sitting on that specific color.
   - Includes a **`📦 Download All Mats`** button to download all color sheets in one sequence.
3. **🕳️ Standalone 100-Pill Cutouts Layer:**
   - Isolated $6\times 3\,\text{mm}$ pill cutouts layer with 4 registration crosshairs (ideal for custom templates or manual overlay).

#### 🐲 Pete's Dragon Uniform Pink Crest, Wings & Tail Spines Rule
In both the pixel sampling engine (`boostLedVibrancy`) and the Cricut cut exporter:
- **Strict Green Scale Protection:** Any pixel with a dominant green channel or hue in the yellow-green to cyan-green spectrum (55° to 180°)—including dark green scale shading, contours, and lime underbelly tones—is strictly guarded and guaranteed to resolve to vibrant dragon green (`#00cc66` / `CRGB(15, 255, 35)`). Green scales are never misclassified as pink regardless of spatial bounding boxes.
- **Authentic Dragon Pink Features:** The **Wild Jagged Hair Crest** on the head, the **Dragon Wings**, and the **Dorsal Spine Plates & Tail Spines** are uniformly classified as signature **Disney Dragon Pink** (`CRGB(255, 25, 230)` / `#ff19e6` / `#ff007f`).
- Pixels sampled across these genuine pink zones are protected against dark line art or green shadow misclassification and automatically route to **Mat 2: Pink HTV Vinyl**.

---

## 8. Master Timeline Scrubber & Multi-Layer Tracks

The **Master Timeline Bar** is anchored at the bottom of the canvas view and operates like a digital audio workstation (DAW) or non-linear video editor (NLE).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  ▶  ⏹  00:32.4 / 01:30.0   [ 3 Layers ] [ Active: Royal Carriage Glow + Wheels Spin ]  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  TIMELINE   |00:00        |00:15        |00:30        |00:45        |01:00        |01:30  │
├─────────────┴──────────────────────────────────────────────────────────────────────────┤
│  🌐 Global:  [ Opening Sparkle (25s) ] [ Royal Carriage Glow (40s) ]                  │
│                                                     [ Grand Finale Wave (30s) ]        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  🎡 Wheels:                [ Carriage Wheels Spin (35s) ]                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  💡 Lanterns:                               [ Lanterns Pulse (25s) ]                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Transport Controls
- **▶ Play / ⏸ Pause:** Starts or pauses continuous 60 FPS theatrical playback. Press the `Spacebar` anywhere on the page to toggle.
- **⏹ Stop / Rewind:** Immediately stops playback and rewinds the playhead to `00:00.0`.
- **Time Readout:** Displays current position down to tenths of a second alongside total loop length (`00:15.5 / 01:30.0`).
- **🔁 Loop Button:** When active (green), playback seamlessly wraps from the end back to `00:00.0`.
- **Unified Master Timeline Engine:** The timeline is always active and looping. When cues are scheduled on the timeline, they execute precisely during their scheduled intervals. When no cues are scheduled (an empty timeline) or during gaps between cues, the costume automatically falls back to its **ambient artwork programming** (the sampled chest graphic colors with rare starlight sparkles), while animation groups execute their resting baseline routines.

### Context-Aware Master Timeline (Single Shirt vs. Fleet Tab Modes)
The Master Timeline dynamically switches display and transport logic depending on whether you are editing a single costume or orchestrating the 7-shirt fleet:

1. **Single Shirt Editing Mode (`Single View` / Tabs 1–5):**
   - **Ruler & Duration:** 0:00 to 01:30.0 (or custom loop duration up to 300s) with formatted MM:SS.S ticks.
   - **Multi-Layer Tracks:** Displays `🌐 Global Float` and all localized `🎡 [Group Name]` lanes with automatic sub-lane stacking for overlapping cues.
   - **Transport Controls:**
     - `▶` Play / `⏸` Pause: Controls playback along the master timeline (`Spacebar`).
     - `⏹` Stop: Rewinds cue sequence to `00:00.0`.
     - `🔁 Loop`: Toggles seamless continuous sequence looping.
     - **Status Badge:** Dynamically reports active cue names or displays `Ambient Program (Fallback)` during intervals without cues.
   - **Interaction:** Clicking cue blocks seeks playhead time and highlights the corresponding cue card in the Parade Cue Director.

2. **Fleet Tab Mode (`Fleet View` / Tab 5):**
   - **Ruler & Duration:** 0.0s to 30.0s (or active fleet show duration) with decimal second ticks.
   - **Fleet Show Choreography Track:** Displays color-coded fleet block bars with block icons (e.g. 🌊 Forward Wave, 💓 Fleet Pulse, ⛈️ Sparkle Storm) spanning all 7 costumes.
   - **Transport Controls:**
     - `👑` / `▶` Activate / `⏸` Stop: Triggers the one-shot 30-second synchronized fleet routine (`Spacebar` or `[F]` hotkey with 300ms debounce protection).
     - `⏹` Stop: Immediately terminates the fleet routine early and returns all 7 shirts to their baseline programs.
     - `👑 Fleet Show: ON / ⚡ Baseline: ON`: Context badge indicating whether the fleet routine is currently firing or running in baseline float program standby.
     - `🔁 Loop`: Hidden during fleet playback to guarantee clean one-shot execution returning to baseline.
   - **Interaction:** Clicking fleet blocks or dragging the scrubber seeks smoothly across the 30-second routine with real-time 7-shirt canvas preview.

### The Multi-Layer Track System (Scenario B Stacking)
- **Dedicated Track Lanes:**
  - **Track 1 (`🌐 Global Float`):** Displays all cues affecting the whole float baseline.
  - **Tracks 2+ (`🎡 [Group Name]`):** Displays cues targeting localized groups (e.g. `Front Wheel`, `Rear Wheel`, `Lanterns`).
- **Automatic Sub-Lane Stacking:** When multiple cues on the same layer overlap in time (e.g., crossfading between two global cues), the track automatically expands into stacked sub-lanes so **both cues remain 100% visible** without overlapping or clipping!
- **Interactive Cue Blocks & NLE Drag-and-Drop Editing:**
  - Displays the cue's title, total duration, and visual fade-in/fade-out gradient indicators.
  - When a cue is actively firing, it lights up with a glowing white/cyan border.
  - **Drag-to-Move (Slip Clip):** Click and drag the central body of any cue block (`cursor: grab` / `cursor: grabbing`) to slide its position earlier or later along the timeline without altering its duration. Snaps to clean 0.1s increments and stays bounded within the timeline loop length.
  - **Left Edge Trimming (`.handle-left`):** Hover over the left border of a clip (`cursor: ew-resize`) and drag left or right to adjust the cue's **Start Time**. The right end time stays firmly locked in place while the start time and duration adjust dynamically (minimum duration clamped to 0.5s).
  - **Right Edge Trimming (`.handle-right`):** Hover over the right border of a clip (`cursor: ew-resize`) and drag left or right to lengthen or shorten the cue's **Duration**. The start time stays locked in place.
  - **Real-Time Floating Tooltip:** While dragging or trimming, an elevated cyan timecode badge floats directly above the cursor displaying live readouts: `Start: 12.4s | End: 28.6s (Dur: 16.2s)`.
  - **Live Sidebar Synchronization:** Dragging or resizing immediately synchronizes the numeric inputs (`.cue-start-input`, `.cue-dur-input`) and time badges on the corresponding card in the Parade Cue Director and flags the shirt configuration as modified (`isSingleShirtDirty = true`).
  - **Smart Click Discrimination:** A 4-pixel movement threshold ensures that short clicks without dragging cleanly jump the playhead to that cue's start time and smoothly scroll the sidebar directly to its editing card without accidental position shifts.
- **Synchronized Playhead Needle:** A vertical cyan line extends across all tracks from top to bottom, moving smoothly with playback to show exactly which cues are active at the current moment.
- **Seek Ruler:** Formatted time ticks (`00:00`, `00:15`, `00:30`, etc.) display along the top. Click or drag anywhere across the ruler or track lanes to scrub in real time.

---

## 9. Parade Cue Director (Individual Float Standby Sequences)

Located in **Tab 4 (`🎬 Show`)** of the left sidebar, the **Parade Cue Director** scripts the theatrical 90-second timeline for the **active individual float** (e.g., Casey Jr.'s locomotive puffing, Cinderella's pumpkin wheels spinning, or Elliott's dragon crest flames).

> [!IMPORTANT]
> **Individual Standby vs. Synchronized Fleet Routine:**
> * **Individual Routine (Tab 4):** Each of the 7 floats runs its own independent 90-second show sequence or continuous baseline pattern while running on the course.
> * **Fleet Takeover (Tab 5):** When a runner single-taps their ESP32 onboard BOOT button or when you trigger the 30-second Fleet Routine in the **🏃 Fleet** tab, ESP-NOW wireless broadcasts immediately take over all 7 shirts to execute the synchronized routine (waves, synchronized pulses, sparkle storms).
> * **Automatic Return:** The moment the 30-second fleet routine finishes, every float seamlessly returns to its individual show sequence or baseline program!

### Structuring a Cue
Click **➕ Add Cue** to create a new cue card with the following settings:
- **Cue Name:** A custom theatrical label (e.g., `Carriage Wheels Spin`, `Snout Fire Breath`, or automatic `[Group Name] Routine`).
- **Target Layer:** Select either `🌐 Global Float` or any active animation group (e.g. `🎡 Group: Front Wheel`).
  - **Group Preset Inheritance:** When an animation group is selected in the Target Layer dropdown (or when clicking **`➕ Add Cue`** while a group is active), the cue automatically inherits the **Pattern / Effect**, **Direction**, and **BPM (Tempo)** configured when the group was created, saving setup time while still allowing you to freely change the effect in the dropdown!
- **Pattern / Effect:** Select from the unified library of 16+ built-in lighting effects (see Section 10).
- **Direction:** Select `➡️ Forward` or `⬅️ Reverse` for traveling animations (comet sweeps, marquee chases, waves, Larson scans).
- **Start Time (s):** Time offset in seconds from the beginning of the show loop (0.5s resolution).
- **Duration (s):** How long the cue runs before fading out (with instant quick chips: `5s`, `10s`, `15s`, `30s`).
- **BPM (Tempo):** The speed of the animation during this specific cue (with instant quick chips: `90`, `120`, `144`, `180 BPM`).
- **Crossfades (Fade In / Fade Out):**
  - **In (s):** Smooth ramp-up blend from baseline color into the effect (`0.0s` for an instant cut, up to `5.0s` for a soft cinematic blend).
  - **Out (s):** Smooth ramp-down blend back into the baseline pattern.

### 1-Click Example Show Routines
Use the **Load Example Routine** dropdown to test fully orchestrated 90-second sequences:
- **🎭 90s Classic Routine (4-Phase Showcase):**
  - `0.0s – 30.0s`: Phase 1: Sampled Starlight Sparkle (Sampled artwork colors with starlight sparkle)
  - `30.0s – 60.0s`: Phase 2: Theatrical Breathing Glow (Gentle breathing pulse)
  - `60.0s – 75.0s`: Phase 3: Dynamic Traveling Chase Beam (8-LED white chasing beam)
  - `75.0s – 90.0s`: Phase 4: Solo Electrical Parade Wave (Traveling wave on dim background)
- **🎃 Cinderella 90s (Wheels & Lanterns):**
  - `0.0s – 25.0s`: Opening Starlight Sparkle (Global baseline)
  - `15.0s – 50.0s`: Carriage Wheels Spin (Group chase overlay)
  - `25.0s – 65.0s`: Royal Carriage Breathing Glow (Warm golden float glow)
  - `35.0s – 60.0s`: Carriage Lanterns Breathing Pulse (Group pulse overlay)
  - `60.0s – 90.0s`: Grand Finale Electrical Wave (Cascading electrical wave)
- **🐉 Pete's Dragon 90s (Crest Flame & Snout):**
  - `0.0s – 30.0s`: Comic Starlight Sparkle
  - `20.0s – 50.0s`: Flame Hair Crest Fire Pulse
  - `30.0s – 65.0s`: Snout Fire-Breathing Pulse
  - `65.0s – 90.0s`: Broadway Electrical Marquee Finale
- **🚂 Casey Jr. 90s (Pistons & Marquee):**
  - `0.0s – 25.0s`: Opening Steam & Sparkle (Sampled starlight)
  - `20.0s – 50.0s`: Piston Chug Acceleration (Locomotive pistons chugging at 144 BPM)
  - `45.0s – 75.0s`: Full Head of Steam Comet Sweep (180 BPM comet trail)
  - `70.0s – 90.0s`: Casey Jr. Circus Marquee Finale (Classic 144 BPM incandescent marquee)
- **🐢 Turtle & Snail 90s (Shell Spin & Ripple):**
  - `0.0s – 30.0s`: Enchanted Garden Pixie Dust (Gentle 90 BPM golden sparkle drift)
  - `25.0s – 60.0s`: Rotating Shell Spin (120 BPM concentric shell spin chase)
  - `55.0s – 80.0s`: Tidal Ripple Expansion (120 BPM concentric expanding wavefront)
  - `75.0s – 90.0s`: Rainbow Shell Spiral Finale (144 BPM vibrant chromatic wave)
- **🎆 America Grand Finale 90s (Fireworks & Marquee):**
  - `0.0s – 25.0s`: Red White & Blue Starlight (Steady patriotic sampled sparkle)
  - `20.0s – 50.0s`: Main Street Parade Wave (144 BPM traveling electrical wave)
  - `45.0s – 75.0s`: Grand Starburst Fireworks (140 BPM pyrotechnic explosions)
  - `70.0s – 90.0s`: Golden Age 1972 Theater Marquee (High-cadence 180 BPM grand finale chase)
- **🗑️ Clear All Cues:** Wipes the cue list clean so you can start from scratch.

---

## 10. Lighting Patterns & Effects Library

The simulator includes a unified library of 18 specialized algorithms available across Whole-Shirt Ambient (Tab 2), Group Creation & Docked Inspector (Tab 3), and Timed Show Cues (Tab 4):

| Effect ID | Effect Name | Description | Best Suited For |
|---|---|---|---|
| `chase` | **Chase / Wheel Spin** | Concentric or sequential single-point circulating chase with exponential decay wake. | Carriage wheels, train drivers, shell spirals |
| `pulse` / `color_match` | **Breathing Glow / Slo-Glo** | Organic sinusoidal breathing pulse that preserves true sampled artwork hues (~30-60 BPM). | Main float bodies, resting groups, warm accents |
| `write_on_off` | **Theatrical Write-On / Off** | Sequential progressive draw-on to full radiance, hold, and progressive wipe-off. | Entrances, flourish accents, musical wipes |
| `flash_slow` | **Slow Flashing / Blink** | Classical synchronized rhythmic on/off beacon blinking. | Headlights, signals, warning markers |
| `sparkle_storm` | **Sparkle Storm (Glitter)** | High-density diamond sparkle blizzard cascading across member LEDs. | Starbursts, pixie wands, climaxes |
| `steady_sparkle` | **Steady Colors + Sparkles** | Holds constant artwork color palette with occasional incandescent starlight twinkles. | Entry / ambient float scenes, resting baseline |
| `comet` | **Meteor / Comet Trail** | High-velocity white-hot comet head shooting along wiring/group perimeter with fading exponential tail. | Wheels, locomotive borders, shooting stars |
| `scanner` | **Larson Scanner (Ping-Pong Sweep)** | Dynamic back-and-forth beam sweep with smooth turnaround wakes and radiant core. | Cowls, dragon wings, sweeping searchlights |
| `color_wipe` | **Color Wipe / Progressive Fill** | 4-phase write-on fill along wiring path, radiant hold, wipe-off, and brief dark rest. | Float entrances, theatrical reveals |
| `pixie_dust` | **Pixie Dust Drift** | Shimmering starlight cascade combining traveling swell envelopes with diamond sparkle bursts. | Fairy wings, magic wands, musical crescendos |
| `filament_glow` | **Vintage 1972 Filament** | Analog micro-voltage warmth mimicking Walt Disney World's original 1972 incandescent bulbs. | Antique marquees, vintage Edison looks |
| `candle_flicker` | **Candle / Lantern Flame** | Warm amber/gold organic flame flicker with random multi-harmonic micro-jitter. | Carriage lanterns, torches, Elliott nostrils |
| `tidal_ripple` | **Tidal Ripple** | Outward-expanding and contracting concentric wavefront from group or float centroid. | Water ripples, shockwaves, radial pulses |
| `piston_chug` | **Locomotive Piston Chug** | 4-stroke mechanical cadence pulse with sharp power stroke and soft exhaust compression. | Casey Jr. boiler, train wheels, driving rhythms |
| `marquee` | **Theater Marquee Chase** | 3-phase alternating incandescent bulb chase (dots 1, 2, 3). | Outer float frames, title drum borders |
| `traveling_wave` | **Traveling Parade Wave** | Electrical parade wavefront cascading smoothly across the garment contour. | Grand finales, dynamic transitions |
| `fireworks` | **Fireworks Starburst** | 4-phase pyrotechnic explosion with center flash, outward expanding fire trails, and starlight tip crackle. | Finales, celestial bursts, chest stars |
| `rainbow_cycle` | **Rainbow Color Wave** | Flowing chromatic wave cycling across the strand or group contour. | Vibrant rainbow flourishes, electric transitions |
| `mouse_scamper` | **Scurrying Mouse (Single Dot + Tail)** | Single ultra-bright head dot darting smoothly across 2D space with a directional history tail showing where the mouse has scampered (no circular spotlight halo). | Whimsical character motion, playful roaming, high-energy flourishes |
| `flashlight` | **Flashlight / Searchlight Roam** | Continuous 2D roaming circular light pool sweeping across the float's sampled artwork like a focused searchlight. | Theatrical inspection, focused searchlights, nighttime reveals |
| `off` | **Off / Completely Unlit** | Complete blackout (0% intensity) for dramatic contrast, dormant stage cues, or unlit baseline. | Dark baseline, countdown blackouts, dormant groups |

### Ambient Baseline Tempo & Theatrical Cadence
Ambient baseline patterns operate with a calm, cinematic default tempo of **48 BPM** (adjustable from **20 to 180 BPM** via the Speed / Tempo slider in Tab 2).
- **Organic Breath Rate:** `Slo-Glo Breath` cycles at a relaxed 24 breaths/minute, mimicking a resting living creature rather than rapid strobing.
- **Continuous Directional Sweeps:** Larson scanners, comets, and tidal ripples respond proportionally to the tempo slider, allowing slow majestic glides or rapid theatrical flourishes.
- **Universal Blackout (`off`):** Selecting `🌑 All Off / Completely Dark` zeroes all LEDs with 0% current draw, enabling floats to begin dormant in total darkness until a cue or fleet routine wakes them.

### 2D Spatial Lighting Engine (Coordinate-Aware Animations)
In real-world garment wiring, LEDs are routed non-linearly across branches and contours to minimize wire tension and optimize slack. As a result, adjacent physical bulbs often have discontinuous electrical index numbers (e.g., LED #14 might sit physically next to LED #58).

To prevent animations from jumping erratically across wire branches, the simulator and firmware use a **2D Spatial Lighting Engine**:
- **Normalized Spatial Coordinates ($x, y$):** Every LED's 2D coordinate on the shirt is mapped into continuous spatial bounds.
- **Physical Progressive Fill (`color_wipe` / `write_on_off`):** Lights LEDs strictly in physical vertical order (bottom hem $\rightarrow$ chest $\rightarrow$ collar when `dir = 1`, or top-down when `dir = -1`), creating a smooth, organic fluid-fill effect regardless of electrical wiring route.
- **Directional Sweeps & Planar Waves (`traveling_wave`, `scanner`):** Larson scanner beams and traveling parade waves sweep smoothly across horizontal space along physical $X$ coordinates.
- **Centroid-Based Radial Waves (`tidal_ripple`):** Ripples expand outwardly from the true 2D physical centroid $(\bar{x}, \bar{y})$ of the float or group.
- **Zero-Overhead Microcontroller Optimization:** When flashing firmware or exporting C++, the spatial ranks and normalized coordinates are pre-computed into compact 8-bit PROGMEM flash lookup tables (`SPATIAL_RANK_Y`, `SPATIAL_X_BYTE`, `SPATIAL_Y_BYTE`, `SPATIAL_RADIUS_BYTE`). The ESP32 executes smooth 60 FPS spatial lighting sweeps with zero floating-point math overhead or memory allocation.

---

## 11. Decimal Sparkle Frequency & Starlight Twinkle

Authentic Disney parade floats use warm, incandescent filament bulbs that twinkle softly like distant stars. High sparkle rates can look like chaotic strobes.

### Fine Decimal Control (`0.0% – 10.0%`)
The **Sparkle Frequency Slider** in Section 3 supports fine decimal percentages with `0.05%` resolution:
- **`0.0%`:** Completely steady colors; zero sparkles.
- **`0.10% – 0.50%` (Recommended Starlight Twinkle):** An authentic, subtle starlight twinkle. Roughly 1 to 3 random LEDs sparkle every second across the entire costume.
- **`1.0% – 2.0%`:** A lively, playful sparkle suitable for active musical passages.
- **`5.0% – 10.0%`:** A fast-paced sparkle storm for grand finales.

*Firmware Note:* When exporting C++ code or flashing firmware, the engine uses 16-bit random thresholds (`random16()`), ensuring that decimal frequencies (like `0.25%`) translate with 100% mathematical fidelity to the microcontroller without rounding down to zero.

---

## 12. Profile Management, Saving & JSON Import/Export

You can save and export complete costume profiles so you never lose your LED arrangements, group definitions, or cue timelines.

### 📦 Master Fleet Parade Bundle (Export & Import All 7 Floats)
Beyond saving single costume profiles, the simulator lets you export and import the **complete 7-float parade configuration** (all 7 costume float designs, LED coordinate placements, zone animation groups, standalone timeline cues, baseline ambient dynamics, and 30s fleet choreography blocks) in a single unified JSON file (`msep_fleet_parade_master.json`).

- **📥 Export Master Fleet Bundle:**
  - Available on the `🏃 Tab 5: Fleet` tab (under 7-Runner Lineup) and on `🎨 Tab 1: Layout` (`📦 Export All 7 Floats`).
  - Captures in-memory modifications from all 7 runner slots and current single-shirt editor states.
  - Generates a timestamped JSON bundle file (`msep_fleet_parade_master_YYYY-MM-DD.json`).
- **📂 Import Master Fleet Bundle with Selective-Float Modal:**
  - Click **`📂 Import Fleet Bundle`** on the Fleet tab to load any master parade JSON bundle.
  - An interactive **Import Confirmation Modal** appears displaying bundle metadata, export timestamp, parade title, and 30s choreography block count.
  - **Selective Checkbox Grid:** Select specific floats to overwrite (or use **Select All** / **Deselect All**), with real-time metrics showing LED counts, group counts, and standalone cues for each float in the bundle.
  - Toggle whether to import the master 30s fleet choreography blocks.
  - Integrated with the **Universal Undo / Redo Engine (`Ctrl+Z`)** so you can safely preview or revert applied bundles with one keystroke.

### Saving Profiles
1. Enter a name in the **Profile Name** input (e.g., `Cinderella_Final_Costume`).
2. Click **💾 Save Profile**.
3. Profiles are saved both to the Python backend server (`presets/` directory) and cached in your browser's `localStorage`.
4. Saved profiles appear in the **Quick-Load Profile** dropdown in Section 1.

### Exporting & Importing Configuration JSON
- **⬇ Download / Export Configuration JSON:**
  Click **"Download Configuration JSON"** (Section 1 or 5) to save a complete `.json` file containing:
  - Exact normalized X/Y coordinates for all 100 LEDs
  - Sampled RGB colors and brightness settings
  - Animation group definitions (member indices and directions)
  - The complete 90-second Cue Director sequence with all timeline cues
- **📂 Import Configuration JSON:**
  Click **"Import Configuration JSON"** and choose any previously saved `.json` file. The simulator instantly restores your LEDs, groups, and cues.

### Generating FastLED C++ Code
Click **"💻 Export FastLED C++ Code"** (Section 5) to open the code modal:
- Generates a complete C++ PROGMEM flash array storing the sampled color palette for all 100 LEDs (`CRGB ARTWORK_PALETTE[NUM_LEDS]`).
- Auto-generates the `runAutonomousShowSequence` routine matching your active timeline cues.
- Click **"📋 Copy to Clipboard"** to paste directly into your Arduino or PlatformIO sketch!

## 13. 7-Shirt Fleet Show Creator & Preset Manager

The simulator includes a dedicated **7-Shirt Fleet Show Creator & Preset Manager** (Tab 5 in the sidebar navigation or via the top header's **"7-Shirt Fleet Lineup"** view toggle).

This feature coordinates costume profiles, LED mapping, and real-time animation synchronization across all 7 runners in the Main Street Electrical Parade fleet, while providing a powerful block-based choreography studio for authoring synchronized fleet routines.

### Baseline vs. One-Shot Fleet Routine Architecture
- **Baseline Mode (Default):** All 7 shirts continuously run their own independent float programs and animation groups (e.g., Casey Jr's spinning wheels, Cinderella's pumpkin coach flourishes, Elliott's breathing crest, patriotic starbursts).
- **One-Shot Fleet Routine Trigger:**
  - Clicking the prominent **"⚡ ACTIVATE 30s FLEET SHOW"** button (`#fleetShowActivateBtn`) or pressing the **`[Space]`** / **`[F]`** hotkeys triggers the synchronized fleet routine once.
  - The routine plays for its exact duration (e.g., 30.0 seconds), with a live phase countdown badge, active color pill indicator, and glowing canvas progress bar.
  - Upon completion, all 7 shirts automatically transition back to their regular individual float programs!
- **Early Stop / Exit:**
  - Clicking the button while the fleet show is active (which transforms into a pulsing red **"⏹ STOP FLEET SHOW (EARLY RETURN)"** button), pressing `[Space]` / `[F]`, or tapping the physical ESP32 BOOT button immediately stops the routine and returns all 7 shirts to their baseline programs.
- **Visual Rendering Cleanliness:** During fleet routine playback, all color transitions, waves, pulses, and sparkle storms are rendered strictly through the discrete addressable LED nodes on the costumes. Outer rectangular card frames and glowing bounding boxes around each shirt are omitted during playback to prevent visual clutter and keep total focus on the costume lighting.
- **Debounce Protection:**
  - The activation button and keyboard hotkeys enforce a **300ms software debounce lockout** in the simulator to prevent accidental double-triggers.
  - The physical ESP32 firmware enforces a **50ms hardware debounce** and **300ms inter-press lockout**.

---

### The 19 Fleet Block Types Palette
The fleet choreography engine features 19 specialized multi-float lighting block types:
1. 🌑 **Dramatic Blackout (`blackout`):** All 7 shirts go completely dark (unlit) for theatrical anticipation or scene transitions.
2. 🌊 **Forward Wave (`wave_forward`):** High-energy light wave sweeping from Float 1 to Float 7 with an authentic ~2-shirt trailing decay of decreasing brightness and incandescent crest.
3. 🔙 **Reverse Wave (`wave_reverse`):** Wave reversing direction from Float 7 to Float 1, maintaining the same wave color and 2-shirt trailing falloff.
4. 💓 **All-Fleet Pulse (`fleet_pulse`):** All 700 LEDs across all costumes ignite in unison and breathe smoothly with peak flare.
5. 💥 **Center Burst (`center_burst`):** Energy originates at center Float 4 and erupts symmetrically outward to Float 1 and Float 7.
6. 🎯 **Converge to Center (`converge_center`):** Light beams ignite at outer Floats 1 and 7 and race inwards meeting at Float 4.
7. 🎪 **Marquee Wig-Wag (`wig_wag`):** Odd floats (1, 3, 5, 7) and Even floats (2, 4, 6) alternate in an energetic parade marquee cadence (120 BPM).
8. 🏃 **Baton Chase (`baton_chase`):** A high-intensity beam leaps from runner to runner sequentially down the parade line.
9. ✨ **Sparkle Storm (`sparkle_storm`):** All 700 LEDs erupt into a dazzling sparkle storm combining high-frequency Starlight White flashes and wave color shimmers (75% density).
10. 🏓 **Ping-Pong Wave (`ping_pong_wave`):** A traveling wave that rebounds back and forth across the 7 runners over multiple bounces.
11. 🎨 **Color Wash Chase (`color_wash_chase`):** A progressive hue wash that rolls across the costumes, transitioning each float's base color.
12. 🌈 **Rainbow Sweep (`rainbow_sweep`):** A full 360° spectrum sweep running across the entire 7-runner formation.
13. ⚡ **All-Fleet Strobe (`strobe_all`):** High-frequency white and primary strobing for climatic musical accents.
14. 🌌 **Shimmer Drift (`shimmer_drift`):** Gentle ambient shimmer drifting smoothly across the lineup like stardust.
15. 🎆 **Carnival Finale Crescendo (`grand_finale`):** Multi-layered grand finale crescendo combining accelerating wig-wag, synchronized pulses, and full-spectrum sparkle bursts.
16. 💥 **Dual Collision & Supernova Shockwave (`color_collision`):** Dual high-speed energy pulses launch from outer Floats 1 & 7, collide with blinding white brilliance at Float 4, and erupt outward in a devastating starlight shockwave back to 1 & 7.
17. 🌊 **Silky Cascade Dissolve (`cross_dissolve_chase`):** A smooth, organic sinusoidal cross-dissolve flowing sequentially from Float 1 through Float 7, transitioning costumes seamlessly between signature themes.
18. 🦋 **Mirror Pair Echo / Butterfly Ripple (`ripple_echo`):** A rhythmic butterfly ripple originating at center Float 4, echoing harmonically outward to symmetric mirror pairs (3&5, 2&6, then 1&7) with organic pulse breathing.
19. 🧚 **Fairy Dust Waterfall Cascade (`sparkle_cascade`):** A flowing, gravity-fed waterfall of Pixie Dust sparkles that sweeps across the lineup (1 ➔ 7), leaving golden-white trailing embers in its wake.

---

### Fleet Show Creator Studio Controls
- **Fleet Routine Profile Dropdown (`#fleetShowSelect`):** Select pre-choreographed signature shows, including:
  1. 👑 **30s Grand Electrical Parade Show (Default):** The full parade processional with traveling waves, center bursts, marquee wig-wags, sparkle storms, and grand finale.
  2. 💥 **The Supernova Spectacular (30s):** High-octane choreography featuring the signature Dual Collision Shockwave, Butterfly Ripple Echo, Fairy Dust Waterfall, and an explosive Grand Finale.
  3. 🎪 **Baroque Hoedown Encore (30s):** Fast-tempo, rhythmic choreography tuned to the iconic parade beat with syncopated wig-wags, forward/reverse wave volleys, collision bursts, and a roaring hoedown crescendo.
  4. ✨ **Classic 20s Fleet Routine:** Compact 20-second parade sequence.
  5. 🧚 **Pixie Dust Processional (20s):** Lyrical, enchanted starlight showcase featuring golden fairy dust waterfalls, silky cascade dissolves, starlight twinkle tempests, and gentle ambient stardust.
  Profiles are loaded dynamically via REST API from `presets/fleet_shows/*.json`.
- **➕ Add Block (`#fleetAddBlockBtn`):** Pick any of the 19 block types from the palette and append it to the stack.
- **Dynamic Block Stack Editor (`#fleetBlocksStackContainer`):**
  - Displays each block's name, type, start time, duration, and parameter controls (speed BPM, trail length, color modes).
  - Reorder blocks with **▲ Up** and **▼ Down** buttons.
  - Duplicate blocks with **⎘ Duplicate**.
  - Delete blocks with **✕ Delete**.
  - During playback, the currently active block is highlighted with an emerald border and glowing indicator.
- **⏱️ Snap to 30.0s (`#fleetSnap30Btn`):** Proportionately scales all block durations in the stack so the total sequence runtime equals exactly 30.0 seconds.
- **💾 Save Show (`#fleetSaveShowBtn`):** Persists the show profile to the Python backend server (`presets/fleet_shows/<id>.json`) and browser storage.
- **✨ New Show (`#fleetNewShowBtn`):** Initializes a fresh blank timeline for custom choreography.
- **📋 View C++ Code (`#fleetViewCppBtn`):** Generates and displays the clean FastLED C++ `render30sFleetRoutine(uint32_t elapsedMs)` code for your custom fleet choreography in an in-browser modal with a 1-click "Copy to Clipboard" button.
- **⚡ Apply to Firmware (`#fleetApplyFirmwareBtn`):**
  - Exports the custom choreography routine directly into the ESP32 firmware source files (`src/main.cpp` and `arduino/MSEP_Costume/MSEP_Costume.ino`) between dedicated sentinels.
  - Automatically updates the `#define FLEET_ROUTINE_TOTAL_MS` runtime macro to match the routine's exact length.
  - Performs an automated background compilation check using PlatformIO (`pio run`) to ensure zero syntax or FastLED errors before flashing.

---

### Master Timeline & Interactive Block Editor
When viewing the 7-Shirt Fleet Lineup, the Master Timeline becomes a fully interactive digital editing console:
- **Color-Coded Category Theming:** Blocks are automatically color-coded by category:
  - 🌊 *Traveling Waves & Directional:* Electric Blue (`.fleet-block-cat-waves`)
  - 💓 *Synchronous Illuminations:* Emerald Green (`.fleet-block-cat-sync`)
  - 🎪 *Theatrical & Dynamics:* Vivid Amber (`.fleet-block-cat-theatrical`)
  - 🌑 *Theatrical Blackouts:* Dark Graphite (`.fleet-block-cat-blackout`)
- **Directional Motion Badges:** Each directional block displays a live motion badge directly on the timeline bar (`1 ➔ 7`, `7 ➔ 1`, `4 ➔ 1&7`, `1&7 ➔ 4`, `1&7 ➔ 4 ➔ 1&7`, `1,3,5,7 ⇄ 2,4,6`, etc.).
- **Drag-to-Stretch Duration (Right Handle):** Hover over the right edge of any block to reveal the resize grip. Click and drag horizontally to stretch or shrink its duration with real-time decimal precision (0.1s increments). A floating tooltip displays the live duration and end-time in real time. Subsequent blocks automatically ripple forward smoothly.
- **Rolling Transition Trim (Left Handle):** Drag the left edge of any block to adjust the transition split point between the previous block and the current block without shifting the rest of the timeline.
- **Drag-and-Drop Horizontal Reordering:** Click and drag the body of any block horizontally across the track. A glowing blue insertion drop indicator marks the destination slot. Releasing the mouse instantly reorders the blocks, updates start times sequentially, and synchronizes the sidebar stack editor.
- **Click-to-Seek & Bi-directional Highlighting:** Clicking any block seeks the timeline playhead to its start time, applies a golden selection glow, and automatically scrolls and highlights the corresponding card in the sidebar editor.
- **Full Scrubber Fidelity:** Scrubbing or playing the timeline renders all 700 LEDs across all 7 costumes in real time at 60 FPS.

---

### The 7-Runner Roster & Float Assignments
Each of the 7 runners is represented by a dedicated preset card and canvas athlete:

| Slot | Float # | Unit / Float Name | Tag | Theme Palette | Default Cricut Artwork & Preset |
|:---:|:---:|:---|:---:|:---:|:---|
| **0** | **01** | **The Train (Casey Jr.)** | `CASEY JR.` | 🔴 Red & Gold | `casey_jr_train.svg` / `casey_jr_train.json` |
| **1** | **02** | **The Title Drum** | `THE DRUM` | 🟡 Gold & White | `title_drum.svg` / `title_drum.json` |
| **2** | **03** | **The Turtle** | `TURTLE` | 🟢 Teal & Emerald | `spinning_turtle.svg` / `spinning_turtle.json` |
| **3** | **04** | **The Snail** | `SNAIL` | 🌸 Hot Pink & Magenta | `spinning_snail.svg` / `spinning_snail.json` |
| **4** | **05** | **Cinderella's Coach** | `COACH` | 🔵 Cyan & Midnight | `cinderella_coach.svg` / `cinderellas_coach.json` |
| **5** | **06** | **Pete's Dragon** | `ELLIOTT` | 🟢 Emerald & Lime | `petes_dragon.svg` / `petes_dragon.json` |
| **6** | **07** | **To Honor America** | `HONOR AMERICA` | 🔴⚪🔵 Patriotic Blue | `honor_america_eagle.svg` / `honor_america_eagle.json` |

---

### Bidirectional Preset Workflow & Live Editor Integration
- **Live Single-Shirt Preset Synchronization:**
  - Fleet View automatically uses the **live in-memory version** of the costume currently open in the Single Shirt Editor for the active runner slot.
  - Any live edits made in the Single Shirt Editor—such as changing LED positions, adjusting brightness, picking hues, tweaking speed BPM, or modifying animation groups—are immediately reflected on that runner's shirt on the Fleet View canvas in real time.
- **Visual Status Badges & Unsaved Indicators:**
  - **Runner Cards:** Cards display explicit status badges showing preset status:
    - **`✏️ Unsaved Live Edit`:** Displayed when live modifications exist in the single-shirt editor that haven't been saved yet.
    - **`✨ Live Editor Active`:** Displayed when previewing the live editor session without unsaved changes.
    - **Preset Label Note:** Clear `✏️ Previewing Unsaved Edit` label next to the preset dropdown indicator.
  - **Fleet Canvas:** The 7-shirt preview canvas area displays a high-contrast badge directly above the runner's shirt:
    - **`✏️ UNSAVED LIVE PREVIEW`** (orange) when previewing unsaved live editor changes.
    - **`✨ LIVE PREVIEW`** (cyan) when previewing the active live editor session.
    - **Header Subtitle:** Explicit header subtitle note indicating which float is being previewed and its unsaved status.
- **Saving Profiles to Fleet Lineup:**
  - When a single-shirt design is saved as a new profile (via **"💾 Save Profile"**), Fleet View automatically recognizes the save:
    - Updates the active runner's assigned preset (`fleetRunners[slot].preset = 'local:' + name`).
    - Clears the unsaved dirty state (`isSingleShirtDirty = false`).
    - Immediately refreshes the runner card dropdowns and badges to display the new saved preset name.
- **Smart Navigation & Unsaved Edits Safety:**
  - **Returning to Active Runner:** Clicking **"Single View"** or clicking **"✏️ Edit in Single View"** on the float currently loaded in memory returns immediately to your active workspace without reloading from disk or overwriting unsaved live changes.
  - **Tab Memory:** Navigating back from Fleet View automatically restores the exact single-shirt tab (`Layout`, `Groups`, `Director`, `Flashing`, etc.) that was open prior to entering Fleet View (`lastSingleShirtTab`).
  - **Interactive Unsaved Changes Modal (`#unsavedChangesModal`):**
    When switching from a float with unsaved edits to edit another float (or selecting a different preset in the Layout dropdown), an interactive dialog appears offering three clear choices:
    1. **💾 Save Profile & Switch:** Prompts for a profile name (pre-populated with a recommended title like `Pete's Dragon Custom` or whatever was typed into the profile name field). Clicking save stores the costume preset in local storage and backend server, links it to that runner's fleet slot, clears the dirty state, and cleanly switches to the new runner.
    2. **🗑️ Discard & Switch:** Discards live unsaved modifications and immediately loads the target runner.
    3. **Cancel:** Dismisses the dialog and remains on the current view without losing any work.
  - **✏️ Edit in Single View (1-Click or Double-Click):**
    Clicking the **"Edit in Single View"** button on any runner card (or **double-clicking the card or canvas runner**) initiates single-view editing for that float.
- **📥 Assign Editor:** Copies your active single-shirt editor design into that runner slot.
- **📋 Assign Editor to All:** Duplicates your current single-shirt design across all 7 runners with one click.
- **🔁 Parade Defaults:** Instantly resets all 7 runners to the official Electrical Parade float presets.
- **💾 Save Fleet Lineup:** Saves the complete 7-runner fleet configuration to `presets/fleet_lineup.json`.

---

### Pre-Race Corral Roll Call & ESP-NOW Fleet Radar (Collapsible Console)

In the dark, chilly 3:30 AM staging corrals outside Epcot, our 7 family runners need instant, foolproof verification that all costumes are powered on, receiving wireless timing packets, and mapped to unique float numbers. To keep the Fleet Tab clean and focused on choreography and presets, the **Corral Roll Call & Fleet Radar** is positioned directly below the 7-Runner Lineup and **starts minimized by default**:

```
┌────────────────────────────────────────────────────────────────────────┐
│  🛰️ Corral Roll Call & Fleet Radar       🟢 7/7 READY   [▼ Open Checks] │
│  4s Attendance Wave, ESP-NOW channel status & 7-float wireless telemetry│
└────────────────────────────────────────────────────────────────────────┘
```

#### Minimized Console & One-Click Expansion:
- **Default Minimized State:** Shows a compact status bar with real-time fleet health (`🟢 7/7 READY`) and summary caption without crowding the screen.
- **Header Toggle:** Click anywhere on the header bar or the **`▼ Open Checks`** button to smoothly expand into the full telemetry and control console (button flips to **`▲ Minimize`**).
- **Quick Jump Buttons:** Click **`🛰️ Corral Radar`** in the **30s Fleet Show Creator** header or the **7-Runner Baseline Presets** header to instantly expand the console and smoothly scroll into view with an accent pulse.
- **Auto-Expansion on Trigger:** Triggering the rapid roll call wave (via button or physical double-tap) automatically expands the console so all 7 visual status cards can be monitored.

#### Key Capabilities & Pre-Race Checks:
1. **Fleet Readiness Banner:**
   - **`🟢 7/7 READY`:** All 7 floats detected, synchronized to Leader Float 1 (Casey Jr.), with healthy signal and battery voltage.
   - **`🟡 X/7 READY`:** Identifies missing runners (e.g. Float 4 Snail still in the gear-check or restroom line).
   - **`🔴 CONFLICT`:** Flags duplicate float assignments (e.g. if two runners accidentally configured their boards as Float 6 Pete's Dragon!).
2. **Real-Time Telemetry Cards (Floats 1 through 7):**
   - **Signature Avatar & Color:** Displays float icon (`🚂`, `🥁`, `🐢`, `🐌`, `🩵`, `🐉`, `🦅`) and character name.
   - **Role Badge:** `👑 LEADER (The Train)` vs `📡 FOLLOWER`.
   - **Wireless Signal (RSSI):** 4-pip meter displaying signal quality:
     - `●●●●` **-44 dBm:** Excellent (within 5 meters in corral pack).
     - `●●●○` **-65 dBm:** Good (normal corral spacing).
     - `●●○○` **-78 dBm:** Fair.
     - `●○○○` **-88 dBm:** Weak link / outer range limit.
   - **Battery & USB Voltage:** Live readout (`5.12V / 98%`) to verify power bank connection.
   - **Heartbeat Counter:** Displays last contact freshness (`Just now`, `1s ago`, `No response`).
3. **Interactive Visual Identification (`✨ Identify`):**
   - Click **`✨ Identify`** on any float card to command that specific runner's shirt to execute **3 rapid full-brightness flashes** in its signature color.
   - **Simulator Canvas Integration:** The corresponding mini-shirt on the canvas strobes in real time while the radar card pulses with that float's signature color.
   - **Physical Hardware:** Transmitted via ESP-NOW (`Mode 0x42`) or UDP (`Opcode 0x03, cmd 0x02`), causing the physical bench or wearable ESP32 to strobe its 200 LEDs without interrupting autonomous mode.
4. **Lineup Sequential Flash (`✨ Flash Lineup (1➔7)`):**
   - Illuminates all 7 floats down the line in rapid succession (Float 1 ➔ 2 ➔ 3 ➔ 4 ➔ 5 ➔ 6 ➔ 7) to visually confirm the entire parade formation in person before stepping across the starting timing mat.
5. **⚡ 4-Second Rapid Attendance Roll Call Wave (Simulate BOOT Double-Tap):**
   - Click or double-tap **`⚡ 4s Rapid Attendance Wave (Simulate BOOT Double-Tap)`** in the toolbar, or **double-tap the physical BOOT button on ANY costume node in the corral**:
     - **Auto-Switch to Fleet View:** If triggered while editing a single shirt, the simulator automatically brings all 7 runners into view.
     - **0.0s – 3.5s (500ms per float):** Floats 1 through 7 illuminate sequentially solo in their signature colors (1 Red ➔ 2 Gold ➔ 3 Teal ➔ 4 Pink ➔ 5 Cyan ➔ 6 Green ➔ 7 Blue). While one runner's shirt calls roll, the other 6 stay dark so the spotlighted float pops unmistakably across the crowd!
     - **3.5s – 4.0s (Unison Double-Green Flash):** All 7 family runners flash bright emerald green twice together (`#00FF50`), with all 7 radar cards pulsing emerald green, visually signaling: *"All 7 present and accounted for, ready to run!"*
     - **Full Athletic Runner Mannequins:** All 7 runners feature natural athletic runner figures—clean athletic head silhouettes (no visors/hats), athletic arms in mid-stride, technical running shorts with vertical racing stripes, toned muscular legs in warm athletic skin tone (`#d4a373`), white quarter socks, and running sneakers planted squarely on the Main Street road surface.
     - **Pure Hardware Operation:** Requires zero phones, zero routers, and zero internet. Transmitted peer-to-peer over ESP-NOW (`Mode 0x44`) or broadcast UDP (`Opcode 0x03, cmd 0x03`).
6. **Bench Simulation Scenarios:**
   - Test your pre-race checklist under real-world conditions:
     - `🟢 All 7 Online & Ready`: Perfect corral scenario.
     - `⚠️ Float 4 Missing`: Simulates runner disconnection with red `OFFLINE` badge.
     - `🔴 Float 6 Conflict`: Simulates duplicate ID conflict with red alarm styling.
     - `🟡 Float 7 Weak Signal`: Simulates runner 30 meters back with `-88 dBm` RSSI.
     - `⚡ Live Hardware Only`: Displays only physical ESP32 boards actively detected.

---

## 14. Hardware Integration: Live Wi-Fi Streaming, Standalone USB Flashing & Battery Power Budget

The simulator connects directly to physical ESP32 hardware via two powerful workflows:

```
[ BROWSER SIMULATOR ] ──(UDP Port 4210 @ 30 FPS)──▶ [ ESP32 NODES (1-7) ] ──▶ [ 200-LED COSTUMES ]
```

### Real-Time Live Wi-Fi UDP Streaming (Single Costume & Multi-Float Fleet)
Preview animations on physical shirts in real time without flashing ROM:
1. **Connect ESP32s to Wi-Fi:** Ensure your ESP32 boards are connected to your local 2.4 GHz Wi-Fi network (or the built-in `MSEP-Costume-AP` hotspot).
2. **Dual-Tab Streaming Bar:** Launch streaming from either the **Fleet Tab** (`#fleetWifiStreamBtn`) or the **Deploy & Hardware Tab** (`#toggleWifiStreamBtn`). Click the gear icon (`⚙️`) to set your Wi-Fi SSID, password, and target broadcast IP (`255.255.255.255`).
3. **Multi-Float Fleet Streaming (Opcode `0x02`):**
   - When on the **Fleet Tab** or during active Fleet Show playback, the simulator packages each of the 7 floats into an addressed high-speed UDP packet:
     ```
     [ 'M', 'S', 'E', 'P' ] [ 0x02 ] [ float_id (1-7) ] [ num_leds (2 bytes) ] [ R, G, B, ... ]
     ```
   - Each bench ESP32 inspects `float_id` against its saved NVS Float ID (`myFloatNumber`). If it matches (or if `float_id == 0`), it renders the 100 front LEDs, duplicates them to the 100 back LEDs, and displays them via FastLED. Packets addressed to other floats are dropped instantly with zero CPU overhead.
   - **Simultaneous Bench Testing:** You can power on multiple ESP32s on your workbench at once. In **Baseline Mode**, Float 1 (Casey Jr.) chugs its warm white headlights, Float 6 (Pete's Dragon) breathes fiery orange scales, and Float 2 (The Drum) rolls its golden marquee.
   - **Live Fleet Show Testing:** Click **"👑 Activate 30s Fleet Show"** (or hit <kbd>Space</kbd> / <kbd>F</kbd>), and every physical ESP32 on your desk executes traveling waves, dual collision shockwaves, butterfly ripples, and starlight sparkle cascades in exact lockstep with the simulator canvas—without burning a single write cycle to flash ROM!
4. **Single-Costume Streaming (Opcode `0x01`):**
   - When viewing or editing an individual shirt in the Layout or Patterns tabs, the simulator streams universal Opcode `0x01` frames. Any single ESP32 on your desk immediately mirrors the design you are currently painting or sequencing.
5. **Zero Perceived Latency:** At 30 FPS, the entire 7-float lineup consumes just ~65 KB/sec (~0.5 Mbps) of UDP broadcast bandwidth. High-performance non-blocking queue draining ensures instant responsiveness with zero packet queuing lag.

### USB Firmware Flashing Workflows (In-Simulator Compiler vs Zero-Install Web Flasher)

The project provides two complementary flashing methods to suit both developers and family members:

#### Method 1: Zero-Install Browser Web Flasher (`web_flasher.html` — Recommended for Family)
- **Local URL (When Simulator is Running):** `http://localhost:8000/web_flasher.html` *(or click **`⚡ Web Flasher`** in the top header)*.
- **Standalone Cloud URL (For Blank Laptops / Nothing Downloaded):** `https://kidmd.github.io/WDW-costumes/simulator/web_flasher.html`.
- **How It Works:** Uses the HTML5 **Web Serial API** built into Google Chrome and Microsoft Edge. Flashes pre-compiled `.bin` binaries directly into the ESP32 in ~15 seconds with **zero Python, zero compilers, zero drivers, and zero software installation**.
- **Role Assignment:** Click any float card (1 through 7) to arm that runner's identity, plug in USB, and click **Install**.

#### Method 2: In-Simulator Custom C++ Compiler (Deploy Tab — Unified Flashing Station)
- **Location:** **Tab 6: Deploy & Hardware** ➔ **`⚡ Flash Float X: [Active Float] to ESP32 (USB)`**.
- **WYSIWYG Paradigm ("What You See Is What You Flash"):** The simulator compiles and flashes the exact costume design, custom artwork, color-matched palette, and timeline choreography **currently visible on your canvas**.
- **Quick-Switch Grid:** Use the 7-button selector right above the flash button to switch any float onto your canvas for instant visual inspection before flashing.
- **How It Works:** Compiles your active custom colors, sampled palette, and timeline cue triggers on the fly using **PlatformIO** installed on the development PC.
- **Note:** `start_simulator.bat` launches Python for the browser visualizer. If PlatformIO is not installed on a secondary computer, use **Method 1 (Web Flasher)** instead.

---

### One-Click Standalone USB Firmware Flashing (200 LEDs: 100 Front + 100 Back)
When you are ready to prepare a shirt for autonomous use:
1. Connect your ESP32 to your computer using a standard micro-USB or USB-C data cable.
2. The top status indicator will detect your COM port and turn green: `● ESP32 on COMx (Ready)`.
3. Verify the float you want to flash is on your canvas. If not, click its button `[1..7]` on the **Switch Float on Canvas to Flash** grid or the top float selector.
4. Click **"⚡ Flash Float X: [Float Name] to ESP32 (USB)"**.
5. The simulator compiles and flashes standalone firmware configured for **200 LEDs**:
   - **Front 100 LEDs (0 – 99):** Your custom-placed, color-matched chest artwork lighting.
   - **Back 100 LEDs (100 – 199):** Real-time duplicate of the front animation for 360° visibility and battery life benchmarking.
   - **Power Management:** FastLED power limit configured up to **2000 mA (2.0A)** for safe operation from portable 5V USB power banks.
6. The live terminal modal displays compilation output and upload progress.
### Race-Day Battery Life & Power Budget Calculator (200 LEDs / 5V 2.0A Limit)

To ensure that **no runner goes dark on course** during the runDisney 10K, the Deploy & Hardware tab features an interactive, real-time power budget simulator modeled on the electrical physics of the wearable 200-LED costume:

- **200-LED Duplicated Load:** 100 front chest artwork LEDs + 100 back LEDs run concurrently to guarantee 360° visibility in the dark pre-dawn corrals and through Epcot.
- **Hardware Power Clamping:** Firmware enforces FastLED's safety limiter:
  ```cpp
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000); // 5V, 2.0A max limit
  ```
  Even during peak white flash starlight bursts, current consumption never exceeds the USB power bank's 2.0A delivery threshold.
- **Microcontroller & Quiescent Overhead:**
  - ESP32 Dual-Core (240 MHz + Wi-Fi / ESP-NOW radio active): ~130 mA steady.
  - WS2812B quiescent standby current: ~1.0 mA per node $\times$ 200 LEDs = 200 mA.
- **7-Float Baseline vs. Show Peak Current:**
  - **Casey Jr. Train (#1):** 750 mA baseline (amber headlights, red engine, spinning wheels) / 1,120 mA show peak.
  - **Title Drum (#2):** 620 mA baseline (gold marquee chase, blue/red twinkle) / 1,050 mA show peak.
  - **The Turtle (#3):** 660 mA baseline (teal shell whirl, green rim) / 1,080 mA show peak.
  - **The Snail (#4):** 670 mA baseline (pink spiral swirl, yellow chase) / 1,090 mA show peak.
  - **Cinderella's Coach (#5):** 700 mA baseline (cyan sparkle, golden wheels) / 1,100 mA show peak.
  - **Pete's Dragon (#6):** 720 mA baseline (emerald scales, violet spine, orange fire breath) / 1,150 mA show peak.
  - **Flag & Eagle (#7):** 780 mA baseline (patriotic red/white waves, blue starfield) / 1,180 mA show peak.
- **Interactive Controls:**
  - **USB Power Bank Size:** Select 5,000 mAh (~18.5 Wh, 3,500 mAh @ 5V), 10,000 mAh (~37 Wh, 7,000 mAh @ 5V - Recommended), 15,000 mAh (~55.5 Wh), or 20,000 mAh (~74 Wh). Factors in real-world 3.7V-to-5.0V boost converter efficiency (~70% delivered capacity).
  - **Race + Corral Duration Slider:** Adjust from 30 minutes (fast sprint) up to 240 minutes (4-hour corral wait + leisurely walking pace).
  - **30s Fleet Show Trigger Cadence:** Choose trigger frequency (every 2m, 4m, 8m, or baseline only).
- **Instant Finish-Line Metrics:**
  - **Battery Remaining %:** Dynamic color-coded gauge (Green $\ge 50\%$, Yellow $35-49\%$, Orange $15-34\%$, Red $< 15\%$).
  - **Total Battery Life:** Calculated hours until complete battery depletion.
  - **Visual Buffer Bar:** Displays exact mAh consumed vs. available 5V capacity.
  - **Expandable Roster Breakdown:** Click `▼ Show` to inspect exact baseline mA, show peak mA, finish %, and total runtime for each runner's float.
  - **One-Click Quick Jump:** Click the **"🔋 Battery Budget"** badge in the 30s Fleet Show Creator header to immediately view and test power metrics.

> 🎒 **Field Preparation & Race Morning Operations:**  
> For the complete pre-race hardware packing checklist, power bank prep, emergency repair kit, and chronological corral countdown playbook, see the **[`RACE_DAY_PACKING_CHECKLIST.md`](RACE_DAY_PACKING_CHECKLIST.md)**.

---

## 15. ESP32 Firmware: Leader-Centric Authority, Corral Standby Mode & Button Controls

The unified firmware in [`src/main.cpp`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/src/main.cpp) and [`arduino/MSEP_Costume/MSEP_Costume.ino`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/arduino/MSEP_Costume/MSEP_Costume.ino) implements FastLED hardware power limiting (`FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000)`), controls **200 LEDs** (100 front + 100 back duplicated), and enforces the **Leader-Centric Fleet Authority Model**:

### 👑 Dual-Leader Authority Model
- **Float 1 (Casey Jr. / Primary Leader):** Head locomotive pulling the parade with master command over the fleet. Float 1 can wake all 7 floats from standby, trigger 4-second attendance roll calls, launch the 30-second fleet show, command Castle Photo Mode, and put the whole group into battery-saving standby.
- **Float 7 (Flag & Eagle / Co-Leader & Rear Marshal):** Rear anchor equipped with full co-leader authority. If the family splits into front and rear packs during the 10K, Float 7 can command the rear pack independently; when united, Float 1 naturally takes master precedence.
- **Floats 2 to 6 (Followers):** Followers have local control over their own shirt (local wake, local Photo Mode, and local standby). Single-taps during active runs and double-taps are ignored on follower boards to ensure non-technical family runners never accidentally disrupt or cancel the parade show.

### 🌙 Power-On Corral Standby Mode
Upon plugging in USB power at 3:30 AM, all costumes boot directly into **Corral Standby Mode** (12% dim midnight starlight twinkle drawing **< 120mA**). This saves 80%+ of power bank energy during the 60–90 minute starting corral wait and prevents blinding fellow runners in line.

### 🎮 Dual Hardware Button Controls (Button 1: GPIO 4 / 0, Button 2: GPIO 33):

| Button & Gesture | 🚂 Float 1 & Float 7 (Leader Role) | 🐌 Floats 2–6 (Follower Role) |
| :--- | :--- | :--- |
| **Button 1 — Single Tap** (< 600ms) | **If in Sleep or Photo Mode:** Wakes ENTIRE FLEET into **Solo Show Mode** (baseline parade animations).<br>**If Running Awake:** Launches **30s Fleet Show Routine** (tap again during show for early stop). | **If in Sleep or Photo Mode:** Wakes/exits LOCALLY into **Solo Show Mode**.<br>**If Running Awake:** **IGNORED** (keeps parade show running without accidental disruption). |
| **Button 1 — Double Tap** (< 400ms) | ⚡ Triggers **4-Second Rapid Attendance Roll Call Wave** across entire fleet. | 💡 Ignored (Roll call wave broadcast reserved for Leader). |
| **Button 1 — Long Hold (5s)**<br>*(1s–4s white charging meter)* | ⚪ Enters **Float ID Configuration Mode** (⚪ 3 white flashes, tap to cycle Floats 1–7, 🟢 4 green auto-save flashes on 4s timeout). | ⚪ Enters **Float ID Configuration Mode** (⚪ 3 white flashes, tap to cycle Floats 1–7, 🟢 4 green auto-save flashes on 4s timeout). |
| **Button 2 — Single Tap** (< 600ms) | 📸 Puts **ENTIRE FLEET** into **Castle Photo Mode** (100% steady, solid illumination with **full authentic graphic artwork background colors**). Tap again to resume parade. | 📸 Puts **LOCAL COSTUME** into **Castle Photo Mode** (solid steady glow with **full graphic background colors**). Tap again to resume parade. |
| **Button 2 — Double & Triple Tap** | ❌ **Disabled** (No action). | ❌ **Disabled** (No action). |
| **Button 2 — Long Hold (3s)**<br>*(1s–2s soft blue meter)* | 🌙 Puts **ENTIRE FLEET** into **Corral Standby / Sleep Mode** (broadcasts `0x50` standby packet). Stays locked in Standby even if held >3s—requiring an explicit click to enter Photo Mode. | 🌙 Puts **LOCAL COSTUME** into **Corral Standby / Sleep Mode**. Stays locked in Standby even if held >3s—waiting for physical release so it never accidentally enters Photo Mode. |

> 💡 **BOOT Button Fallback:** The onboard **BOOT button (GPIO 0)** remains active in software in parallel with Button 1, allowing bare boards to be tested on the bench without external switches wired up!

### 📸 Castle Photo Mode (Full Multi-Color Artwork Background Illumination for High-Shutter Night Photography)
High-speed camera sensors at night struggle with moving LED animation frames or high-frequency PWM dimming, often capturing dark bands or uneven brightness in race photos. **Castle Photo Mode** locks all 200 LEDs (100 front + 100 back duplicated) into a 100% solid, steady, DC-like glow displaying the **full, authentic multi-color background artwork** of that runner's float (e.g. Pete's Dragon with emerald scales, magenta spine, and warm orange fire breath; Casey Jr. with red engine, yellow trim, and cyan steam pulses) rather than a single monochromatic color. When the family gathers in front of Cinderella Castle or Spaceship Earth, a single tap of Button 2 on Float 1 lights up the entire fleet in glorious, photogenic unison.

### 🎛️ Interactive Float ID Selector (Hold Button 1 for 5 Seconds with Progressive Charging Meter)
Any board can be reassigned to any of the 7 floats in the corral without touching code or opening a laptop:
1. **Hold Button 1 (GPIO 4 or BOOT GPIO 0):**
   - **0s – 1s:** Normal baseline operation.
   - **1s – 4s (Progressive Charging Meter):** Crisp white LEDs illuminate one-by-one at each second milestone (1s: 1 LED, 2s: 2 LEDs, 3s: 3 LEDs, 4s: 4 LEDs). If you let go at any point during this charging window, the hold is aborted and your shirt returns to normal baseline immediately without launching the show.
   - **5s (Threshold Reached):** The LEDs flash **white 3 times** to enter Float ID Config Mode.
2. **Visual Feedback:** The first `N` LEDs on the strip light up in that float's signature color (1=Red, 2=Gold/Amber, 3=Teal, 4=Pink, 5=Cyan, 6=Green, 7=Patriotic Blue). The onboard blue LED blinks `N` times in sequence.
3. **Tap to Cycle:** Each short tap cycles `1 ➔ 2 ➔ 3 ➔ 4 ➔ 5 ➔ 6 ➔ 7 ➔ 1`.
4. **Auto-Save:** Leave untouched for 4 seconds. The LEDs flash **green 4 times** and the Float ID is permanently saved to ESP32 NVS flash (`Preferences.h`). Floats 1 and 7 act as Leaders; Floats 2–6 act as Followers.

#### The 7-Runner Fleet Lineup:
| Float # | Float Name | Character Tag | Signature Color | Role |
|:---:|---|---|---|:---:|
| **01** | **The Train** | CASEY JR. | 🔴 Red | **👑 PRIMARY LEADER** (Pulls the Drum & Broadcasts timing clock) |
| **02** | **The Title Drum** | THE DRUM | 🟡 Gold / Amber | Follower |
| **03** | **The Turtle** | SPINNING TURTLE | 🟢 Teal / Green | Follower |
| **04** | **The Snail** | SPINNING SNAIL | 🌸 Pink | Follower |
| **05** | **Cinderella's Coach** | CINDERELLA | 🔵 Cyan | Follower |
| **06** | **Pete's Dragon** | ELLIOTT | 🟢 Green | Follower |
| **07** | **To Honor America** | FLAG & EAGLE | 🔴⚪🔵 Patriotic Blue | **🦅 CO-LEADER / REAR MARSHAL** (Full show & standby authority) |

### 🎵 Design Decision: Soundtrack & Audio Playback Omission
Soundtrack audio playback (e.g. Baroque Hoedown music synchronized via speakers) was evaluated and intentionally omitted based on runDisney 10K race logistics:
- **Crowded Corrals:** Runners pack closely in starting corrals; loud costume speakers would annoy surrounding participants.
- **Race Entertainment:** The event already features high-volume DJ stages in the pre-race staging area, live bands along the course, and park audio loops throughout Epcot's World Showcase.
- **Quiet Zones:** The Disney Boardwalk resort area is an enforced race quiet zone where personal music playback is discouraged.
- **Visual Focus:** Eliminating speakers saves significant battery power and weight, directing 100% of spectator attention toward the dazzling wireless synchronized LED choreography across all 7 shirts.

### 🚀 Zero-Install Web Serial Fleet Flasher Suite (Floats 1–7)
You can flash any runner's ESP32 directly from Google Chrome or Microsoft Edge with zero software installation:
- **Dedicated Float Lineup Cards (1–7):** Select any character float (🚂 *Float 1: The Train*, 🥁 *Float 2: Title Drum*, 🩵 *Float 3: Cinderella*, 🏴‍☠️ *Float 4: Peter Pan*, 🐘 *Float 5: Dumbo*, 🐉 *Float 6: Pete's Dragon*, 🦅 *Float 7: To Honor America*, or *Generic Auto*).
- **Automatic Role Baking:** Flashing a dedicated float ROM permanently bakes that float's ID and role (👑 Master Leader vs 📡 Fleet Follower) into the ESP32's NVS flash memory on first boot.
- **Fleet Tab Flasher Link:** Click **"⚡ Go to Flasher ➔"** in the Fleet Show Creator toolbar to smoothly jump straight to the Deploy Tab's unified flashing station for the active float.
- **Deploy & Hardware Tab Unified Flashing Station:** The Deploy tab flasher features an active float banner, 7 quick-switch buttons, and a dynamic action button (**"⚡ Flash Float X: [Float Name] to ESP32 (USB)"**) adhering strictly to the WYSIWYG ("What You See Is What You Flash") paradigm.

---

## 16. 3D-Printable Flexible Wearable TPU Panels (Snapmaker U1 / 95A TPU)

For runners who want an ultra-clean, rugged armor shell holding their 100 addressable fairy light pixels ("seed/pebble" LEDs on black 3-strand enameled wire), the project includes an automated parametric 3D panel pipeline:

```
Transparent Asset + Simulator Preset
      │
      ▼
scripts/generate_3d_panel.py
      ├── 3d_panels/petes_dragon_tpu_panel.scad   (Parametric OpenSCAD Source)
      ├── 3d_panels/tpu_panel_preview.html        (Interactive 3D WebGL Inspector)
      └── 3d_panels/petes_dragon_specs.json       (Mechanical Coordinates & Sizing)
```

### 🎨 5-Color Multi-Material 3D Printing System (Bambu Lab AMS / Snapmaker Dual):
Instead of attaching a Cricut cut vinyl graphic on top of the printed plate, the front surface of the TPU armor plate directly features the multi-color character artwork via 5-material FDM 3D printing:
- **Organic Silhouette Boundary Fitting:** The outer 4mm perimeter rim and 2mm tray floor of the black structural chassis trace the organic contour of the character artwork (e.g. Pete's Dragon silhouette with spinal crest, head, snout, wings, and tail), rather than a generic rectangular block. Sizing controls on the Layout tab (Medium = 8.0" / 203.2mm) calibrate the physical dragon chassis width to exactly 8 inches.
- **Zero-Overlap Jigsaw Inlay Architecture:** The structural black chassis features 0.6mm deep front pockets (3 layers @ 0.2mm layer height) precisely receiving the 4 accent color inlays.
- **Bambu Lab AMS 5-Color Palette (Pete's Dragon Preset):**
  1. **Slot 1 — Structural Chassis & Outline Walls:** Black (`#0d1908`) — 6.0mm perimeter rim, 2.0mm tray floor, LED retention collars, wiring basin, and mounting eyelets.
  2. **Slot 2 — Dragon Body:** Neon Green (`#04fa06`) — 0.6mm front face inlays.
  3. **Slot 3 — Hair Tuft, Spine Ridge & Wings:** Magenta (`#f606f5`) — 0.6mm front face inlays.
  4. **Slot 4 — Belly & Facial Accents:** Sunny Yellow (`#f9f90c`) — 0.6mm front face inlays.
  5. **Slot 5 — Eyes & Teeth:** Bright White (`#f7f8f7`) — 0.6mm front face inlays.
- **Clean Optical Window Pass-Throughs:** Open $3\times 3\text{ mm}$ square or $\varnothing 3\text{ mm}$ round optical windows are cut completely through both the black chassis and color inlays, ensuring raw LED light beams directly forward without filament absorption.
- **Export Formats & Bambu Studio Workflow:**
  - **`tpu_panel_{front|back}_multicolor_bundle.zip`**: Contains all 5 discrete STL files sharing identical $(0,0,0)$ origin coordinates, native 3MF, and a step-by-step setup guide.
  - **Bambu Studio Multi-Part Import:** Drag and drop all 5 STLs into Bambu Studio simultaneously and click **"Load as a single object with multiple parts"** (`Yes`). Assign filaments 1–5 to each part in the project tree.
  - **Single Monolithic STL Option:** For single-color prints or Cricut vinyl overlays, the exporter allows switching to single monolithic STL export mode.
- **Interactive 3D WebGL Multi-Material Preview:** The 3D Preview Modal (`#tpuPreviewModal`) includes a `[ 🎨 5-Color Split | ⚪ Single Black ]` toggle, a dynamic 5-color AMS legend badge with aperture counts, and direct download buttons for 5-Color ZIP and Bambu 3MF.

### 🦺 Wearable Architecture & Specs (Open-Chassis 6.0mm Flexible TPU Armor Tray):
1. **Open-Chassis Tray Structure:**
   - **Filament:** 95A Flexible TPU (e.g., Polymaker PolyFlex, Overture TPU).
   - **Dimensions:** $172.2\text{ mm W} \times 153.8\text{ mm H} \times 6.0\text{ mm}$ overall envelope (chassis tray body $166.1 \times 152.0\text{ mm}$ with tabs extending outwardly; sized cleanly within Snapmaker U1 $270 \times 270\text{ mm}$ print bed, leaving nearly $50\text{ mm}$ / $2\text{ in}$ of perimeter margin on all sides).
   - **Base Plate & Floor Recesses:** Solid continuous $2.0\text{ mm}$ thick base plate facing the runner's shirt ($Z = 0$ to $2.0\text{ mm}$), with localized **$1.0\text{ mm}$ floor recesses** directly beneath each LED pocket cavity. The front shirt-facing surface remains 100% flat and flush while the floor inside each LED socket is thinned to $1.0\text{ mm}$.
   - **Perimeter Rim Wall:** $4.0\text{ mm}$ tall outer rim ($Z = 2.0$ to $6.0\text{ mm}$, $2.5\text{ mm}$ wall width) surrounding the entire plate, forming a protective chassis tray.
   - **Unconstrained Open Wire Basin (No Back Wall):** The entire space outside the LED collars acts as a spacious $4.0\text{ mm}$ deep open basin where 3-conductor flat ribbon wire can route and loop freely with zero binding, zero restrictive trenches, and zero unprintable overhangs.
   - **Lightweight:** Net volume is $\approx 39.6\text{ cm}^3$, weighing just **$\approx 44\text{ grams}$ ($1.5\text{ oz}$)**—featherlight, flexible, and comfortable for a 10K race.
2. **100 Non-Overlapping Horizontal Oval Collars ($10\text{ mm} \times 5\text{ mm} \times 3\text{ mm}$) with Wire Notches:**
   - **Inner Cavity & Z Coordinates:** $10.0\text{ mm} \times 5.0\text{ mm}$ oval socket with $3.0\text{ mm}$ tall walls rising from the recessed floor ($Z = 1.0$ to $4.0\text{ mm}$).
   - **Zero Collar Overlap (PBD Relaxation Solver):** Positions are nudged by a minimal average shift ($\approx 1.6\text{ mm}$, max $4.9\text{ mm}$) so that **every single collar maintains $\ge 0.5\text{ mm}$ of clear wall gap** from every other collar. Zero overlapping or merged sockets!
   - **2.0mm Table Clearance:** When laying the 3D print flat on a table front-side up (with the $6.0\text{ mm}$ rim touching the table), there is **exactly $2.0\text{ mm}$ of open space** under the tops of the pocket walls ($Z = 4.0\text{ mm}$ vs $6.0\text{ mm}$ rim), keeping bulbs and wires elevated away from table surfaces.
   - **Uniform Horizontal Orientation:** Collars are oriented horizontally ($0^\circ$ rotation) matching the Pete's Dragon Chris preset, keeping the sockets cleanly parallel across the chest.
   - **Wire Pass-Through Notches:** $4.0\text{ mm}$ wide notches on both $5\text{ mm}$ ends extending all the way down to the $1.0\text{ mm}$ floor, allowing ribbon wire to enter and exit horizontally without resistance.
3. **Selectable $3\text{ mm} \times 3\text{ mm}$ Square or $\varnothing 3\text{ mm}$ Round Optical Apertures:**
   - Runners can choose between **$3\times 3\text{ mm}$ Square** or **$\varnothing 3\text{ mm}$ Round** aperture through-holes directly on the 2D Layout tab or in the 3D Print Preview Modal.
   - Centered through-windows through the $1.0\text{ mm}$ front face beneath each bulb beam the LED forward while the resin bulb body rests solidly against the interior pocket shelf.
   - Changing the selection in the simulator immediately reflects on the 2D canvas and 3D preview, and automatically recompiles the binary STLs with the exact chosen aperture geometry!
4. **Smallest Readable Debossed LED Numbers (1 to 100):**
   - Numbers `1` through `100` are sized at the absolute minimum readable size for a $0.4\text{ mm}$ nozzle (**$1.8\text{ mm}$ cap height, $0.5\text{ mm}$ deboss depth** into the interior floor) with clean inter-character kerning.
   - **Correct Left-to-Right Underside Reading:** Number glyphs are debossed into the floor so that when the runner inspects the underside assembly from the back, every number (e.g. `1`, `42`, `100`) reads in natural left-to-right order without mirror reversal.
5. **Outside Perimeter Mounting Eyelets (Pure Smooth Circular Ears, Zero Points):**
   - 16 streamlined, completely round mounting ears placed strictly on the **OUTSIDE** of the perimeter rim wall.
   - **Pure Smooth Circular Geometry (Zero Points):** Each eyelet is a pure concentric circular cylinder of outer diameter $6.5\text{ mm}$ (outer radius $3.25\text{ mm}$, wall thickness $2.0\text{ mm}$) and height $2.0\text{ mm}$ ($Z = 0.0$ to $2.0\text{ mm}$), completely eliminating any sharp corners, shield wedges, knife edges, or pointy ledges.
   - **Back-Flush Orientation:** Base sits at $Z = 0.0\text{ mm}$, **completely flush with the back perimeter rim touching the runner's shirt** ($Z = 0.0\text{ mm}$), enabling direct, flat sewing, safety pins, or tagging barbs.
   - **Solid Structural Overlap:** The $6.5\text{ mm}$ outer cylinder overlaps $1.75\text{ mm}$ deep into the solid $2.5\text{ mm}$ perimeter rim wall, fusing into an unbreakable structural joint while keeping the center $\varnothing 2.5\text{ mm}$ through-hole completely clear on the outside.
   - **Dimensions:** $\varnothing 2.5\text{ mm}$ through-hole, $2.0\text{ mm}$ solid walls ($6.5\text{ mm}$ OD), overall tab height $2.0\text{ mm}$.
   - **Puncture-Free Front Face:** The main artwork front plate remains 100% smooth and continuous at $Z = 6.0\text{ mm}$.

6. **Simplified 3D STL Model Viewer with Graphic Cutouts (`tpu_panel_preview.html`):**
   - **Direct STL Mesh Loading & Non-Mirrored Alignment:** Loads the exact binary `petes_dragon_tpu_panel.stl` mesh directly via Three.js `STLLoader`, oriented with the front face ($Z = 6.0\text{ mm}$) pointing toward the camera (+Z) and underside pockets ($Z = 0.0\text{ mm}$) facing the runner's shirt (-Z). This ensures the dragon head faces forward to the right identically in both ViewSTL and the WebGL inspector without any mirror reversal.
   - **Graphic with Square/Round Window Cutouts:** Projects the active float graphic directly over the front of the STL panel with real square ($3\times 3\text{ mm}$) or circular ($\varnothing 3\text{ mm}$) transparent cutouts punched out where each LED window is located, keeping the apertures completely unobstructed.
   - **LED State Simulation:** Features an interactive LED simulation bar allowing runners to toggle between **LEDs Off**, **Static On** (authentic float colors), and **Animated Parade** (60 FPS shimmer and wave chase).
   - **Minimal Floating HUD:** Replaced complex multi-layer sidebar menus with a clean floating control bar providing quick camera angles (Front, Underside/Pockets, 3D Angle) and opacity sliders for the graphic and armor plate.

7. **Deploy Tab Integration (`tabHardware`) & Dual Front & Back STL Compilation:**
   - **Dual Armor Panel System (Front & Back):** In accordance with the 200-LED costume architecture (100 front chest pixels + 100 back pixels duplicated in real time), the compiler creates two tailored armor plates:
     - **🎽 Front Chest Plate ($185\text{ mm}$ base width, $\sim 154\text{ mm}$ height):** Sized to fit comfortably on the chest above race bib #1952 with full collar and neck mobility.
     - **🎒 Back Torso Plate ($240\text{ mm}$ max dimension, $\sim 200\text{ mm}$ height):** With no race bib constraint, the back panel scales up by $\approx 1.30\times$ to maximize the running shirt back. The 100 LED socket positions scale proportionally with the larger silhouette, maintaining the exact 1:1 firmware LED mapping while expanding wire spacing.
   - **Print Bed Safety Clearances:**
     - **Snapmaker U1 ($270 \times 270\text{ mm}$):** Leaves $\approx 50\text{ mm}$ ($2.0\text{ in}$) margin on the Front Plate and $\approx 15\text{ mm}$ ($0.6\text{ in}$) on the Back Plate.
     - **Bambu Lab ($250 \times 250\text{ mm}$ safe printable area):** Leaves $\approx 42\text{ mm}$ margin on the Front Plate and $\approx 5\text{ mm}$ safe skirt margin on the Back Plate.
   - **Interactive Front / Back 3D Preview Modal (`#tpuPreviewModal`):** Features a segmented pill in the header: `[🎽 Front (185mm)]` vs `[🎒 Back (240mm)]`. Switching immediately swaps the STL mesh, scales the graphic overlay, updates the dimensions and weight readout badge, and repositions the 100 LED socket windows.
   - **Artwork Boundary Containment Clamping:** The Position-Based Dynamics (PBD) solver features strict silhouette boundary containment (`safe_art_boundary = dragon_poly.buffer(-2.0)`). While resolving socket collision gaps ($\ge 7.9\text{ mm}$ pitch), it actively clamps all LED coordinates to remain strictly inside the artwork silhouette. This guarantees **100 / 100 LEDs sit inside the artwork graphic on both Front and Back panels**, completely preventing sockets from bleeding out into empty air.
   - **1-Click Dual Compilation:** Clicking **`⚙️ Recompile STLs (Both Front & Back)`** runs the Python Manifold3D compiler and generates both watertight binary STLs (`tpu_panel_front.stl` and `tpu_panel_back.stl`) in under 9 seconds total.
   - **Always Matches the Canvas (Stale-STL Guard):** Every compile stamps a *layout signature* (active graphic + artwork + chest bounds + all 100 LED positions) into `tpu_panel_specs.json`. When you click **Preview 3D TPU Armor Panel**, the simulator compares that stamp to the live canvas — if you've switched floats (e.g., Pete's Dragon → The Spinning Turtle), uploaded new artwork, or moved LEDs, it shows *"Active graphic changed — compiling fresh Front & Back STLs…"* and rebuilds both plates automatically before displaying them. No more turtle artwork riding on a dragon-shaped plate!
   - **Rock-Solid 3D Orbiting (Zero Z-Fighting):** The 3D WebGL renderer employs hardware `logarithmicDepthBuffer`, an optimized $1.0\text{ mm}$ near clip plane, explicit layer `renderOrder` (Plate: 0, Artwork: 2, LEDs: 3), GPU `polygonOffset` depth biasing, and a $0.35\text{ mm}$ physical surface elevation. Orbiting and tumbling the plate at any 3D angle maintains rock-solid, flicker-free graphics with zero clipping or disappearing textures.
   - **Complete Download Suite:** Direct download buttons for `⬇️ Front STL (185mm)`, `⬇️ Back STL (240mm)`, `📦 Download Both STLs`, and parametric OpenSCAD sources (`.scad`).

8. **Layout Tab: 2×2mm Window Visualization & Pocket Overlap Avoidance:**
   - **🖨️ Show TPU 2×2mm Windows Toggle:** Renders subtle $10\text{ mm} \times 5\text{ mm}$ (outer $12.4 \times 7.4\text{ mm}$) pocket socket boundaries with wire pass-through notches and crisp $2\text{ mm} \times 2\text{ mm}$ square optical apertures with radiant light beaming through.
   - **Live Drag Repulsion:** When dragging any LED across the canvas, a collision solver ensures its $12.4 \times 7.4\text{ mm}$ collar stadium maintains $\ge 7.9\text{ mm}$ center-to-center distance from all other LEDs ($0.5\text{ mm}$ clear wall gap), preventing accidental collisions.
   - **Auto-Relaxation on Scatter & Fill:** Position-Based Dynamics (PBD) stadium separation is built into **100 Scatter** and **Fill Graphic with Remaining LEDs**, automatically nudging apart any overlapping collars to guarantee 100% collision-free layouts before STL compilation.

### 🖨️ Snapmaker U1 95A TPU Slicing Profile:
- **Nozzle Temp:** 225°C – 235°C (0.4mm nozzle).
- **Bed Temp:** 50°C (PEI textured sheet).
- **Print Speed:** 30 mm/s (First layer: 15 mm/s).
- **Layer Height:** 0.20 mm.
- **Infill:** 100% Solid.
- **Retraction:** 1.8 mm @ 20 mm/s (Direct Drive).
- **Filament Weight:** ~66 grams of TPU.
- **Print Duration:** ~2 hr 15 min.

---

## 17. Keyboard Shortcuts & Quick Reference Cheat Sheet

| Key / Action | Context | Description |
|---|---|---|
| `Spacebar` / `F` | Fleet Lineup View | **Activate 30s Fleet Show / Stop Early** (300ms debounced one-shot trigger) |
| `Spacebar` (Tap) | Single Shirt View | **Play / Pause** show sequence playback on the master timeline |
| `Spacebar` (Hold) + Drag | Canvas | **Pan** the canvas workspace smoothly |
| Right-Click + Drag | Canvas | **Pan** the canvas workspace |
| Mouse Wheel | Canvas | **Zoom** in / out centered on cursor position |
| `+` / `=` | Canvas | **Zoom In** (+20%) |
| `-` / `_` | Canvas | **Zoom Out** (-20%) |
| `0` | Canvas | **Reset Zoom** to default centered 100% view |
| `Shift` + Drag | Canvas | **Marquee Box Select** multiple LEDs |
| `Ctrl + A` / `Cmd + A` | Canvas | **Select All** LEDs |
| `Ctrl + Z` / `Cmd + Z` | Canvas / Groups | **Undo** last action (LED/group moves, 90° rotations, flips, scales, pastes, deletes, scatters, rearranges) |
| `Ctrl + Y` / `Ctrl + Shift + Z` | Canvas / Groups | **Redo** previously undone action |
| `Ctrl + C` / `Cmd + C` | Single Shirt View | **Copy Selected Group** to global clipboard |
| `Ctrl + V` / `Cmd + V` | Single Shirt View | **Paste Copied Group** from unused LED pool onto current shirt |
| `Ctrl + R` / `Cmd + R` | Single Shirt View | **Rotate Selected Group 90°** Clockwise around centroid |
| `Enter` | Draw Mode | **Finish & Save** drawn path animation group (when $\ge 2$ LEDs placed) |
| `Escape` | Draw Mode | **Cancel** drawing mode and revert uncommitted points |
| `Escape` | Normal Mode | **Deselect All** LEDs |
| Arrow Right `]` / `n` | LED Select | Select **Next LED** in wiring order |
| Arrow Left `[` / `p` | LED Select | Select **Previous LED** in wiring order |
| Click on Timeline Track | Timeline | **Seek playhead** to that exact second |
| Click on Cue Block | Timeline | **Jump to cue start** and highlight cue card in editor |
| Drag Cue Block Body | Timeline | **Move / Slip Clip** left or right along timeline (0.1s snap) |
| Drag Left Edge Handle | Timeline | **Trim Start Time** of clip (locks end time) |
| Drag Right Edge Handle | Timeline | **Trim Duration** of clip (locks start time) |

---

*Disney, Main Street Electrical Parade, Pete's Dragon, and Cinderella are registered trademarks of The Walt Disney Company. This open-source project is an unofficial tribute created for the Walt Disney World 10K runDisney event.*

