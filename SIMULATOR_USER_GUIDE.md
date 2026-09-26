# 🏰 Main Street Electrical Parade Costume Simulator
## Complete User Guide & Theatrical Lighting Manual

Welcome to the **Main Street Electrical Parade (MSEP) Costume Simulator** — a comprehensive browser-based theatrical lighting design console and hardware integration engine for synchronized, wearable addressable LED floats.

This guide walks you through every feature of the simulator, from placing and wiring your physical LEDs to orchestrating multi-layer 90-second parade show routines, live streaming to your ESP32, and compiling standalone firmware.

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
13. [7-Shirt Fleet Lineup & Preset Manager](#13-7-shirt-fleet-lineup--preset-manager)
14. [Hardware Integration: Live Wi-Fi Streaming & Standalone USB Flashing](#14-hardware-integration-live-wi-fi-streaming--standalone-usb-flashing)
15. [Dual-Mode ESP32 Firmware & Onboard Button Toggle](#15-dual-mode-esp32-firmware--onboard-button-toggle)
16. [Keyboard Shortcuts & Quick Reference Cheat Sheet](#16-keyboard-shortcuts--quick-reference-cheat-sheet)

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

---

## 4. Thoroughbred Workspace: 6 Task Tabs & Contextual Inspector Dock

The simulator features a streamlined, modern workspace inspired by creative suites (After Effects, Figma, Blender), replacing long vertical scrolling with **6 task-oriented tabs** and an **intelligent contextual inspector dock**:

### The 6 Sidebar Tabs (2-Row Grid Layout)
The sidebar navigation is organized into a clean **2-row × 3-column grid** that guarantees all 6 task buttons fit comfortably inside the 410px sidebar without any button clipping or horizontal scrolling:
- **Row 1:** `🎨 Layout` | `👥 Groups` | `✨ Effects`
- **Row 2:** `🎬 Show` | `⚡ Deploy` | `🏃 Fleet`

1. **🎨 Tab 1: Layout ("The Canvas Studio"):**
   - **Costume Profiles:** Quick-load, save, and export/import full JSON profiles.
   - **Shirt & Character Artwork:** Choose from built-in presets (Pete's Dragon, Cinderella's Coach, Carriage No Horses) or upload custom graphics.
   - **LED Generation & Graphic Fill:** One-click `100 Scatter`, `50 Auto-Outline`, `Sample Colors`, and `🔄 Fill Graphic with Remaining LEDs` (redistributes non-grouped LEDs to fill open space without moving any grouped LEDs).
   - **runDisney 10K Race Bib (#1952):** Toggle overlay, height, and scale sliders to verify physical clearance.
   - **Physical Wiring Route Optimizer:** Shortest-path snake wiring optimizer, Show Wiring Trace toggle, Show Numbers toggle.
   - **Quick-Link to Groups:** Fast-jump button to the Groups Tab for drawing paths or stamping fireworks.

2. **👥 Tab 2: Groups ("Group Creation Hub & Manager"):**
   - **LED Allocation Overview Box:** Real-time visual progress bar tracking how many LEDs are assigned to animation groups versus unassigned.
   - **Unified Group Creation Hub:** 3 dedicated creation modes:
     - 📦 **From Selection:** Save or update groups directly from canvas marquee box selections.
     - ✏️ **Click-to-Draw Path:** Sequentially place LEDs directly on the shirt with a checkable option to auto-rearrange remaining unassigned LEDs to fill the graphic.
     - 🎆 **Fireworks Stamper:** Relocated radial starburst generator with serpentine wiring, radius scale, and color themes.
   - **Active Groups Browser:** Card list of all configured groups with instant selection, badge metrics, and deletion controls.

3. **✨ Tab 3: Effects ("The FX Lab"):**
   - **Baseline Lighting Pattern:** Select from 8 continuous baseline patterns (Steady Sparkle, Color Match, Fire Breath, Traveling Wave, Marquee, Fireworks, Photo Mode).
   - **Live Dynamics Tuning:** Speed/Tempo BPM slider, Sparkle Frequency, Green Hue/Shade, Master Brightness, LED Bloom Glow Size.

4. **🎬 Tab 4: Director ("The Show Director"):**
   - **Parade Cue Director:** 90-second Sequence Loop controls (Sequence ON/OFF, Loop duration, Example routines).
   - **Active Cue List:** Clean, scrollable cue cards displaying start time, duration, target layer/group, effect, BPM, and quick delete.
   - **Quick Cue Insertion:** `➕ Add Cue at Playhead`, `⚡ Auto-Schedule Bursts`.

5. **⚡ Tab 5: Hardware ("The Workshop"):**
   - **USB Standalone Flashing:** Auto-detected COM port, connection status badge, 1-Click Flash firmware, View/Copy C++ code modal.
   - **📡 Real-Time Wi-Fi Live Stream:** Stream live colors & animations directly to physical LEDs over Wi-Fi without flashing ROM. Wi-Fi credentials modal.
   - **Web Serial Flasher:** Quick launch button for zero-install browser-based flashing.

6. **🏃 Tab 6: Fleet ("7-Shirt Fleet Lineup & Preset Manager"):**
   - **👑 15s Choreographed Parade Routine (Default Mode):**
     - **0.0s – 1.0s (1s):** All 7 shirts go totally black (off / unlit).
     - **1.0s – 2.0s (1s):** Light wave sweeps forward from Float 1 through Float 7 in a randomly chosen standard Disney color (`Belle Gold`, `Alice Cyan`, `Coral Rose`, `Electric Pink`, `Electric Lime`, `Cinderella Blue`, `Cheshire Violet`, `Deep Indigo`, `Flame Orange`, `Starlight White`, `Dragon Green`, or `Mickey Red`).
     - **2.0s – 3.0s (1s):** The wave reverses direction, sweeping from Float 7 back to Float 1 in the **exact same color** as the forward pass.
     - **3.0s – 5.0s (2s):** Spectacular starlight & gold sparkle storm across all 7 shirts (700 LEDs).
     - **5.0s – 6.0s (1s):** All 7 shirts go totally black (off / unlit).
     - **6.0s – 15.0s (9s):** Return to individual float preset programs (animation groups, artwork colors, custom effects).
     - **Loop & Color Rotation:** Resets every 15.0 seconds and automatically rotates to a new, non-repeating random standard color for the next cycle. Live canvas banner and sidebar badges display the active wave color and countdown.
   - **Alternative Modes:** 🌊 **Wave Sync** (continuous ESP-NOW wave with adjustable speed slider), ⚡ **Free-Run** (autonomous presets), and 🎬 **Master Show** (synchronized 90s cue timeline).
   - **7 Runner Slot Cards (Bib #01 to #07):** Assign presets to each runner, view live LED counts and pattern pills.
   - **1-Click Bidirectional Editing:** Jump any runner's preset directly into the Single Shirt editor (`✏️ Edit in Single View`), or copy the active single-shirt editor design to any runner or all 7 runners (`📥 Assign Editor`).

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

#### 3. 🎆 Mode 3: Fireworks Stamper (Relocated from Layout)
- Stamp multi-ray radial starburst fireworks directly from the Groups tab.
- Includes corner placement presets (Top-Left, Top-Right, Center), Move X/Y sliders, Scale / Burst Radius slider (with S/M/L/XL quick buttons), Ray count, LEDs per ray, uniform ray color theme, and auto-scheduling explosion cues on the Master Timeline.
- Serpentine wiring ensures maximum physical wire efficiency during costume assembly.

---

### 👥 LED Allocation Overview & Active Groups Browser
- **Allocation Progress Bar:** Real-time visual progress bar tracking how many LEDs are assigned to animation groups versus unassigned. Displays total assigned percentage and count (e.g. `24 / 100 LEDs (24%) assigned to groups`).
- **Quick Selection Actions:**
  - **`👥 Select All Grouped`**: Instantly selects all LEDs currently belonging to any group across the entire costume for bulk review.
  - **`⚡ Select Unassigned`**: Immediately highlights all ungrouped LEDs so you can quickly bundle remaining costume LEDs into a new zone with one click!
- **Rich Interactive Group Cards (`#activeGroupsList`):**
  - **Header:** Group emoji icon (e.g., 🎆 for fireworks, 🎡 for chase, 🎪 for marquee), bold group name, and total LED count badge.
  - **Badges:** Effect pill (`🎡 Chase @ 140 BPM`), Starburst geometry details (for fireworks: ray count and burst radius), Resting Baseline pill (`Idle: Off / Unlit`), and physical LED index ranges (`LEDs: #0–15`).
  - **Instant Selection & Canvas Focus:** Clicking anywhere on a group card or clicking **`🎯 Select & Edit`** highlights all member LEDs on the canvas, opens their properties in the docked Inspector, and marks the card with a glowing active border.
  - **1-Click Show Cue Shortcut:** Click the **`➕ Show Cue`** button directly on any card to create a synchronized Show Cue on the Master Timeline—pre-configured with the group's effect and tempo—and immediately jump to the Parade Cue Director tab!
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
   - **Resting Baseline Effect (When Idle / No Cue):** Configure what the group does when resting outside active timeline cues in Sequence Mode:
     - *🌐 Follow Overall Baseline (Default):* The group seamlessly follows the overall float background pattern/cue (e.g. `steady_sparkle`), matching all non-grouped float LEDs.
     - *🌑 Off / Completely Unlit:* The group stays 100% dark (pitch black) outside active cues. Default for fireworks, and ideal for theatrical accents like carriage lanterns, Elliott's dragon fire breathing, or Casey Jr.'s headlight until detonated/triggered on the timeline!
     - *✨ Gentle Starlight Sparkle:* Gentle starlight twinkling on group pixels.
     - *💡 Dim Static Glow:* Ambient resting glow (~22% brightness) in the group's artwork or custom color.
     - *🌬️ Calm Breathing Glow:* Gentle ~30 BPM breathing glow.
     - *💓 Slow Resting Pulse:* Soft rhythmic heartbeat pulse.
     - *Cue Crossfading:* When an active cue on that group fires, the show engine smoothly crossfades from the group's configured resting baseline into the active cue effect, and seamlessly returns to baseline when the cue ends.

---

## 6. Physical Wiring Route Optimization

Attaching LEDs to a shirt by hand can easily result in tangled wire spaghetti if the LEDs are numbered randomly. The simulator solves this with a **continuous shortest-path wiring optimizer**.

### How It Works
1. Click the **🔌 Optimize Wiring Route** button in the toolbar.
2. The algorithm starts at the bottom-left corner of the shirt (where your battery pack and ESP32 pocket are typically located).
3. It uses a 2-opt spatial traveling salesman algorithm to renumber every LED along the shortest continuous physical snake route.
4. Each LED is renumbered so LED `0` connects to LED `1`, which connects to LED `2`, and so on, with minimum wire length between successive pixels.
5. Toggle **Show Wiring Route** in Section 6 to see the physical wire path drawn directly on the canvas!

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
Section 4 features an authentic runDisney race bib overlay on the lower torso to verify physical clearance with your running gear:
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

### ✂️ Cricut Heat Transfer Vinyl (HTV) Cut Files
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
- **🎬 Sequence Mode Toggle:** Toggles between **Free-Run** (single continuous baseline pattern) and **Show Sequence** (timeline-driven theatrical cue playback).

### The Multi-Layer Track System (Scenario B Stacking)
- **Dedicated Track Lanes:**
  - **Track 1 (`🌐 Global Float`):** Displays all cues affecting the whole float baseline.
  - **Tracks 2+ (`🎡 [Group Name]`):** Displays cues targeting localized groups (e.g. `Front Wheel`, `Rear Wheel`, `Lanterns`).
- **Automatic Sub-Lane Stacking:** When multiple cues on the same layer overlap in time (e.g., crossfading between two global cues), the track automatically expands into stacked sub-lanes so **both cues remain 100% visible** without overlapping or clipping!
- **Interactive Cue Blocks:**
  - Displays the cue's title, total duration, and visual fade-in/fade-out gradient indicators.
  - When a cue is actively firing, it lights up with a glowing white/cyan border.
  - **Clicking any cue block** immediately seeks the playhead to that cue's start time and scrolls to its card in the sidebar editor.
- **Synchronized Playhead Needle:** A vertical cyan line extends across all tracks from top to bottom, moving smoothly with playback to show exactly which cues are active at the current moment.
- **Seek Ruler:** Formatted time ticks (`00:00`, `00:15`, `00:30`, etc.) display along the top. Click or drag anywhere across the ruler or track lanes to scrub in real time.

---

## 9. Parade Cue Director (90-Second Theatrical Sequences)

Located in Section 2 of the left sidebar, the **Parade Cue Director** is where you script and fine-tune your float's theatrical show sequence.

### Structuring a Cue
Click **➕ Add Cue** to create a new cue card with the following settings:
- **Cue Name:** A custom theatrical label (e.g., `Carriage Wheels Spin`, `Snout Fire Breath`, or automatic `[Group Name] Routine`).
- **Target Layer:** Select either `🌐 Global Float` or any active animation group (e.g. `🎡 Group: Front Wheel`).
  - **Group Preset Inheritance:** When an animation group is selected in the Target Layer dropdown (or when clicking **`➕ Add Cue`** while a group is active), the cue automatically inherits the **Pattern / Effect** and **BPM (Tempo)** configured when the group was created, saving setup time while still allowing you to freely change the effect in the dropdown!
- **Pattern / Effect:** Select from the 12 built-in lighting effects (see Section 10).
- **Start Time (s):** Time offset in seconds from the beginning of the show loop (0.5s resolution).
- **Duration (s):** How long the cue runs before fading out.
- **BPM (Tempo):** The speed of the animation during this specific cue (30–280 BPM).
- **Crossfades (Fade In / Fade Out):**
  - **In (s):** Smooth ramp-up blend from baseline color into the effect (`0.0s` for an instant cut, up to `5.0s` for a soft cinematic blend).
  - **Out (s):** Smooth ramp-down blend back into the baseline pattern.

### 1-Click Example Show Routines
Use the **Load Example Routine** dropdown to test fully orchestrated 90-second sequences:
- **🎃 Cinderella 90s (Wheels & Lanterns):**
  - `0.0s – 25.0s`: Opening Starlight Sparkle (Global baseline)
  - `15.0s – 50.0s`: Carriage Wheels Spin (Group chase overlay)
  - `25.0s – 65.0s`: Royal Carriage Breathing Glow (Warm golden float glow)
  - `35.0s – 60.0s`: Carriage Lanterns Breathing Pulse (Group pulse overlay)
  - `60.0s – 90.0s`: Grand Finale Electrical Wave (Cascading electrical wave)
- **🐉 Pete's Dragon 90s (Crest Flame):**
  - `0.0s – 30.0s`: Comic Starlight Sparkle
  - `20.0s – 50.0s`: Flame Hair Crest Fire Pulse
  - `30.0s – 65.0s`: Snout Fire-Breathing Pulse
  - `65.0s – 90.0s`: Broadway Electrical Marquee Finale
- **🗑️ Clear All Cues:** Wipes the cue list clean so you can start from scratch.

---

## 10. Lighting Patterns & Effects Library

The simulator includes 11 specialized algorithms designed specifically for parade floats:

| Effect ID | Effect Name | Description | Best Suited For |
|---|---|---|---|
| `steady_sparkle` | **Steady Colors + Sparkles** | Holds constant artwork color palette with occasional incandescent starlight twinkles. | Entry / ambient float scenes |
| `color_match` | **Color-Matched Breathing Glow** | Organic sinusoidal breathing pulse that preserves true sampled artwork hues. | Main float bodies |
| `chase` | **Chase / Wheel Spin** | Directional traveling pulse that rotates around closed loops or lines. | Carriage wheels, rims, borders |
| `pulse` | **Breathing Glow Pulse** | Rhythmic swelling heartbeat glow. | Lanterns, dragon scales, accents |
| `flash_slow` | **Slow Flashing / Blink** | Alternating on/off flashing cycle. | Warning lanterns, beacons, stars |
| `write_on_off` | **Theatrical Write-On / Write-Off** | Successively turns on LEDs one-by-one from start to finish, then wipes them off. | Float entrances and grand reveals |
| `sparkle_storm` | **Sparkle Storm** | High-energy flurry of white incandescent flashes. | Magic moments, fairy dust, wand taps |
| `marquee` | **Theater Marquee Chase** | 3-phase alternating incandescent bulb chase (dots 1, 2, 3). | Outer float frames, title drums |
| `traveling_wave` | **Traveling Parade Wave** | Intense illuminated wave head with fading comet tail. | Float-to-float ESP-NOW sync, finales |
| `fire_breath` | **Snout Fire Breath** | Flickering flame simulation in amber, orange, and red hues. | Pete's Dragon snout, torches |
| `fireworks` | **Fireworks Starburst** | 4-phase pyrotechnic explosion with center flash, outward expanding fire trails, and starlight tip crackle. | Finales, celestial bursts, chest stars |

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

## 13. 7-Shirt Fleet Lineup & Preset Manager

The simulator includes a dedicated **7-Shirt Fleet Lineup & Preset Manager** (Tab 6 in the sidebar navigation or via the top header's **"7-Shirt Fleet Lineup"** view toggle).

This feature coordinates costume profiles, LED mapping, and real-time animation synchronization across all 7 runners in the Main Street Electrical Parade fleet.

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

### Fleet Synchronization Modes
In the Fleet tab toolbar, you can select between 4 synchronized animation modes:

1. 👑 **15s Routine (15-Second Choreographed Parade Routine — Default):**
   - Implements the signature Main Street Electrical Parade fleet routine across all 7 costumes in an exact 15-second loop:
     - **0.0s – 1.0s (1s):** **Blackout.** All 7 shirts go completely dark (off / unlit).
     - **1.0s – 2.0s (1s):** **Forward Wave (Random Standard Color).** A brilliant wave of light sweeps across the fleet from Float 1 (`Casey Jr.`) through Float 7 (`To Honor America`) over 1 second. The wave selects a color at random from the 12 standard Disney palette colors (`Belle Gold`, `Alice Cyan`, `Coral Rose`, `Electric Pink`, `Electric Lime`, `Cinderella Blue`, `Cheshire Violet`, `Deep Indigo`, `Flame Orange`, `Starlight White`, `Dragon Green`, `Mickey Red`). Each float lights up with an intense white-hot core, saturated color body, and glowing amber/color crest as the wave passes.
     - **2.0s – 3.0s (1s):** **Reverse Wave (Same Color).** The wave reverses direction, sweeping backward from Float 7 to Float 1 over 1 second, **maintaining the exact same color** as the forward wave.
     - **3.0s – 5.0s (2s):** **Sparkle Storm.** All 7 costumes (700 LEDs) erupt into a synchronized starlight & gold sparkle storm for 2 full seconds with rapid, high-frequency twinkling and starlight flashes.
     - **5.0s – 6.0s (1s):** **Blackout.** All 7 shirts go completely dark (off / unlit) for 1 second.
     - **6.0s – 15.0s (9s):** **Individual Float Programs.** Each costume transitions smoothly into its assigned float preset programs (animation groups, rotating wheels, breathing effects, patriotic pulses, and custom artwork colors) for 9 seconds.
     - **Loop & Color Rotation:** Seamlessly resets to Phase 1 every 15.0 seconds and switches to a **new, non-repeating random standard color** for the next cycle. A real-time timer badge, active color pill badge (`#fleetRoutineColorBadge`), and canvas header banner display the active phase, wave color name, and elapsed timestamp.

2. 🌊 **Wave Sync (Continuous ESP-NOW Passing Wave):**
   - Simulates the physical wireless traveling wave continuously passing sequentially from Runner 1 to Runner 7.
   - The active float illuminates with a white-hot crest (`#ffffff`) and warm trailing glow, while the remaining 6 runners shimmer with their float's signature resting sparkle or gentle breathing glow.
   - **Wave Speed Slider:** Adjust the full parade cycle duration from **3.0s to 14.0s** (default **7.0s** cycle, ~1.0s per runner).

3. ⚡ **Free-Run (Autonomous Preset Animations):**
   - Each runner executes their assigned costume preset and zone animation groups (e.g. Casey's spinning wheels and flashing headlight, Cinderella's dual wheels, Elliott's breathing flourish) independently in real time.

4. 🎬 **Master Show (Synchronized 90-Second Sequence):**
   - All 7 runners synchronize their lighting cues to the master 90-second timeline sequence.

---

### Interactive 700-LED Canvas Preview
In the 7-Shirt Fleet Lineup view (`renderFleetView`):
- **Authentic Athletic Shirts (1 : 1.25 Proportions):** Scaled running shirts with athletic collar, raglan seams, running shorts, and color-matched running shoes along the parade course road.
- **Float Vector & Image Artwork:** Renders the authentic Cricut SVG vector artwork or high-res image scaled into the chest zone strictly above the bib.
- **runDisney Mini Bib:** Displays authentic runDisney 10K yellow Tyvek bib styling with individual runner Bib numbers (`#01` through `#07`) and BibBoards snap clamps.
- **700 Real LEDs (100 per Runner):** The canvas plots all 100 LEDs from each runner's assigned preset, calculating dynamic RGB colors, bloom halo, and incandescent core intensity at 60 FPS.
- **Interactive Selection:**
  - **Hover:** Move your mouse over any runner to highlight their shirt on the course.
  - **Click:** Click any runner shirt on canvas to select and highlight their card in the sidebar tab.
  - **Double-Click:** Double-click any runner to instantly load their preset into the Single Shirt editor!

---

### Bidirectional Preset Workflow
- **Assigning Presets to Runners:**
  Every runner slot card has an **Assigned Costume Preset** dropdown. Select any server preset (`presets/*.json`) or custom profile from your browser cache (`localStorage`) to assign it to that runner. The canvas updates immediately.
- **✏️ Edit in Single View (1-Click or Double-Click):**
  Click the **"Edit in Single View"** button on any runner card (or **double-click the card / canvas runner**) to seamlessly transition the workspace into the Single Shirt Editor:
  - **Full Preset Restoration:** Loads all 100 LED coordinates, sampled pixel colors, float vector artwork, animation groups (with full dual-compatibility for `ledIndices` and `indices`), speed BPM, brightness, and sequence cues.
  - **Auto-Centered Viewport:** Automatically toggles canvas rendering to Single Shirt mode, activates the zoom toolbar, and resets zoom/pan (`resetZoom()`) so the runner's shirt is perfectly framed.
  - **Sidebar Synchronization:** Switches sidebar navigation directly to the **🎨 Layout** tab (`tabLayout`) and synchronizes the **Quick-Load Profile** dropdown (`#presetSelect`) to match the active runner's preset.
- **📥 Assign Editor:**
  Click **"Assign Editor"** on a runner card to copy your active single-shirt editor design into that runner slot.
- **📋 Assign Editor to All:**
  Duplicates your current single-shirt design across all 7 runners with one click.
- **🔁 Parade Defaults:**
  Instantly resets all 7 runners to the official Electrical Parade float presets.
- **💾 Save Fleet Lineup:**
  Saves the complete 7-runner fleet configuration to `localStorage['msep_fleet_lineup']` and the server at `presets/fleet_lineup.json`.

---

## 14. Hardware Integration: Live Wi-Fi Streaming & Standalone USB Flashing

The simulator connects directly to physical ESP32 hardware via two powerful workflows:

```
[ BROWSER SIMULATOR ] ──(UDP Port 4210 @ 30 FPS)──▶ [ ESP32 NODE ] ──▶ [ WS2812B SHIRT ]
```

### Real-Time Live Wi-Fi UDP Streaming
Preview animations on your physical shirt in real time without flashing:
1. Connect your ESP32 to your local Wi-Fi network (or use the built-in `MSEP-Costume-AP` hotspot).
2. In the simulator header, click **"📡 Wi-Fi Live Stream"** or the settings gear.
3. Enter your Wi-Fi SSID, Password, and the target ESP32 IP address (or leave `255.255.255.255` for broadcast).
4. Click **"▶ Start Live Wi-Fi Stream"**.
5. The status indicator turns green: `Streaming (100 LEDs @ 30 FPS)`.
6. As you scrub the timeline or hit play, the browser packs the RGB frame data into high-speed UDP packets on port `4210`. Your physical shirt mirrors the simulator screen with zero perceived latency!

### One-Click Standalone USB Firmware Flashing (200 LEDs: 100 Front + 100 Back)
When you are ready to prepare a shirt for autonomous use:
1. Connect your ESP32 to your computer using a standard micro-USB or USB-C data cable.
2. The top status indicator will detect your COM port and turn green: `● ESP32 on COMx (Ready)`.
3. Click **"⚡ Flash to Connected ESP32"**.
4. The simulator compiles and flashes standalone firmware configured for **200 LEDs**:
   - **Front 100 LEDs (0 – 99):** Your custom-placed, color-matched chest artwork lighting.
   - **Back 100 LEDs (100 – 199):** Real-time duplicate of the front animation for 360° visibility and battery life benchmarking.
   - **Power Management:** FastLED power limit configured up to **2000 mA (2.0A)** for safe operation from portable 5V USB power banks.
5. The live terminal modal displays compilation output and upload progress.
6. Once complete, unplug the USB cable from your computer, plug the ESP32 into a 5V USB battery bank in your pocket, and your costume runs on its own!

---

## 15. Dual-Mode ESP32 Firmware, Button Toggle & Float ID Selector

The firmware in [`src/main.cpp`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/src/main.cpp) incorporates dual-mode operation and interactive float configuration toggled via the ESP32's onboard **BOOT button** (`BUTTON_PIN 0` with hardware internal pull-up and debouncing):

### Mode Switching & Visual Confirmations (Short Tap BOOT Button)
Tap the onboard **BOOT button (GPIO 0)** once (short tap < 2.5s) to toggle between modes. The LEDs give immediate visual confirmation across all 200 lights:
- 🔵 **2 Cyan Flashes**: Switched to **Mode 0: Autonomous 90-Second Theatrical Show** (plays custom artwork palette or float cue sequence).
- 🟡 **2 Amber Flashes**: Switched to **Mode 1: ESP-NOW Fleet Sync** (locks wireless timing with the other runner shirts for synchronized golden marquee chases, sparkles, and traveling waves).

### Mode 0: Autonomous 90-Second Theatrical Show Sequence (Default)
- Runs your float's customized 90-second Cue Director sequence independently across all 200 LEDs (front and back).
- Ideal when runners are separated, walking through the park, or taking photos.
- The onboard status LED pulses with a gentle 1 Hz breath to indicate autonomous mode.

### Mode 1: ESP-NOW Fleet Sync
- Unit 1 operates as the **Parade Leader / Transmitter**, broadcasting synchronization packets over connectionless 2.4 GHz ESP-NOW radio at 25 Hz.
- Units 2 through 7 operate as **Followers / Receivers**, locking their internal clock to the Leader with sub-millisecond precision.
- Features coordinated 7-float traveling waves where illuminated light pulses leap smoothly from runner to runner down the line (Float 1 ➔ 2 ➔ 3 ➔ 4 ➔ 5 ➔ 6 ➔ 7)!
- The onboard status LED illuminates solid green/blue when receiving radio synchronization packets.

### 🎛️ Interactive Float ID Selector (Hold for 3 Seconds)
Any board can be assigned to any of the 7 floats without touching code:
1. **Hold the BOOT button for 3 seconds:** The LEDs flash **white 3 times** to enter Config Mode.
2. **Visual Feedback:** The first `N` LEDs on the strip light up in that float's signature color (1=Red, 2=Gold/Amber, 3=Teal, 4=Pink, 5=Cyan, 6=Green, 7=Patriotic Blue). The onboard blue LED blinks `N` times in sequence.
3. **Tap to Cycle:** Each short tap cycles `1 ➔ 2 ➔ 3 ➔ 4 ➔ 5 ➔ 6 ➔ 7 ➔ 1`.
4. **Auto-Save:** Leave untouched for 4 seconds. The LEDs flash **green 4 times** and the Float ID is permanently saved to ESP32 NVS flash (`Preferences.h`). Float 1 automatically acts as Leader; Floats 2–7 act as Followers.

#### The 7-Runner Fleet Lineup:
| Float # | Float Name | Character Tag | Signature Color | Role |
|:---:|---|---|---|:---:|
| **01** | **The Train** | CASEY JR. | 🔴 Red | **👑 LEADER** (Pulls the Drum & Broadcasts timing clock) |
| **02** | **The Title Drum** | THE DRUM | 🟡 Gold / Amber | Follower |
| **03** | **The Turtle** | SPINNING TURTLE | 🟢 Teal / Green | Follower |
| **04** | **The Snail** | SPINNING SNAIL | 🌸 Pink | Follower |
| **05** | **Cinderella's Coach** | CINDERELLA | 🔵 Cyan | Follower |
| **06** | **Pete's Dragon** | ELLIOTT | 🟢 Green | Follower |
| **07** | **To Honor America** | FLAG & EAGLE | 🔴⚪🔵 Patriotic Blue | Follower |

---

## 16. Keyboard Shortcuts & Quick Reference Cheat Sheet

| Key / Action | Context | Description |
|---|---|---|
| `Spacebar` (Tap) | Anywhere | **Play / Pause** show sequence playback on the master timeline |
| `Spacebar` (Hold) + Drag | Canvas | **Pan** the canvas workspace smoothly |
| Right-Click + Drag | Canvas | **Pan** the canvas workspace |
| Mouse Wheel | Canvas | **Zoom** in / out centered on cursor position |
| `+` / `=` | Canvas | **Zoom In** (+20%) |
| `-` / `_` | Canvas | **Zoom Out** (-20%) |
| `0` | Canvas | **Reset Zoom** to default centered 100% view |
| `Shift` + Drag | Canvas | **Marquee Box Select** multiple LEDs |
| `Ctrl + A` / `Cmd + A` | Canvas | **Select All** LEDs |
| `Enter` | Draw Mode | **Finish & Save** drawn path animation group (when $\ge 2$ LEDs placed) |
| `Escape` | Draw Mode | **Cancel** drawing mode and revert uncommitted points |
| `Escape` | Normal Mode | **Deselect All** LEDs |
| Arrow Right `]` / `n` | LED Select | Select **Next LED** in wiring order |
| Arrow Left `[` / `p` | LED Select | Select **Previous LED** in wiring order |
| Click on Timeline Track | Timeline | **Seek playhead** to that exact second |
| Click on Cue Block | Timeline | **Jump to cue start** and highlight cue card in editor |

---

*Disney, Main Street Electrical Parade, Pete's Dragon, and Cinderella are registered trademarks of The Walt Disney Company. This open-source project is an unofficial tribute created for the Walt Disney World 10K runDisney event.*
