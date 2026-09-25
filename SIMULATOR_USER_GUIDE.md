# 🏰 Main Street Electrical Parade Costume Simulator
## Complete User Guide & Theatrical Lighting Manual

Welcome to the **Main Street Electrical Parade (MSEP) Costume Simulator** — a comprehensive browser-based theatrical lighting design console and hardware integration engine for synchronized, wearable addressable LED floats.

This guide walks you through every feature of the simulator, from placing and wiring your physical LEDs to orchestrating multi-layer 90-second parade show routines, live streaming to your ESP32, and compiling standalone firmware.

---

## Table of Contents
1. [Introduction & System Architecture](#1-introduction--system-architecture)
2. [Launching the Simulator](#2-launching-the-simulator)
3. [Canvas Navigation & Interactive Controls](#3-canvas-navigation--interactive-controls)
4. [LED Placement, Inspection & Color Tuning](#4-led-placement-inspection--color-tuning)
5. [Multi-LED Selection & Animation Groups](#5-multi-led-selection--animation-groups)
6. [Physical Wiring Route Optimization](#6-physical-wiring-route-optimization)
7. [Artwork & Graphic Management](#7-artwork--graphic-management)
8. [Master Timeline Scrubber & Multi-Layer Tracks](#8-master-timeline-scrubber--multi-layer-tracks)
9. [Parade Cue Director (90-Second Theatrical Sequences)](#9-parade-cue-director-90-second-theatrical-sequences)
10. [Lighting Patterns & Effects Library](#10-lighting-patterns--effects-library)
11. [Decimal Sparkle Frequency & Starlight Twinkle](#11-decimal-sparkle-frequency--starlight-twinkle)
12. [Profile Management, Saving & JSON Import/Export](#12-profile-management-saving--json-importexport)
13. [Hardware Integration: Live Wi-Fi Streaming & Standalone USB Flashing](#13-hardware-integration-live-wi-fi-streaming--standalone-usb-flashing)
14. [Dual-Mode ESP32 Firmware & Onboard Button Toggle](#14-dual-mode-esp32-firmware--onboard-button-toggle)
15. [Keyboard Shortcuts & Quick Reference Cheat Sheet](#15-keyboard-shortcuts--quick-reference-cheat-sheet)

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

## 4. LED Placement, Inspection & Color Tuning

Every LED on the shirt is an addressable physical node that maps directly to an index in your LED string (`0` to `N-1`).

### Selecting & Inspecting an LED
- **Click an LED:** Click on any LED circle on the canvas. A glowing cyan ring highlights the active LED, and the **LED Inspector** appears in Section 4 of the sidebar.
- **Inspector Details:** Displays the LED Index (`#0`), Normalized X/Y coordinates, sampled RGB values, and a live color swatch.
- **Adjusting Color:**
  - Use the **R, G, and B sliders** (0–255) to fine-tune the exact color balance.
  - Enter a hexadecimal color code (e.g., `#FFB347` for vintage amber incandescent).
  - Use the native color picker swatch for intuitive visual adjustments.
- **Moving LEDs:** Click and drag any LED to reposition it anywhere on the shirt. If color matching is active, dragging the LED will automatically resample the pixel color from the underlying artwork image as you move it!

---

## 5. Multi-LED Selection & Animation Groups

To create localized zone animations (like carriage wheels spinning or lanterns pulsing), you can select multiple LEDs and organize them into **Animation Groups**.

### Selecting Multiple LEDs
1. **Marquee Box Select:**
   - Click the **⬚ Box Select** button in the top toolbar, then click and drag a rectangular bounding box across any area of the canvas.
   - *Quick Shortcut:* Hold down the `Shift` key and drag anywhere on the canvas to draw a selection box immediately!
2. **Select All:** Click the **All** button or press `Ctrl + A` (`Cmd + A` on Mac) to select all LEDs on the float.
3. **Clear Selection:** Click **Clear** or press `Escape` to deselect all LEDs.

### Creating Animation Groups
1. Select the LEDs you want to group (e.g., the 16 LEDs outlining Cinderella's front carriage wheel).
2. Look at Section 4 in the sidebar (**"Multi-LED Selection"**).
3. Type a descriptive name into the **Group Name** field (e.g., `Front Wheel`, `Carriage Lanterns`, or `Dragon Crest`).
4. Click **➕ Create Animation Group**.
5. The new group will appear in Section 4 under **"Active Animation Groups"** with its member count, index range, and an icon badge.

### Group Configuration
- **Direction:** Select **Clockwise (CW)** or **Counter-Clockwise (CCW)** for directional chase animations (crucial for ensuring left and right carriage wheels appear to roll forward!).
- **Group Effect:** Choose an effect from the dropdown:
  - *🎡 Chase / Wheel Spin:* Chases illuminated heads around the ring.
  - *💓 Breathing Glow Pulse:* Pulses the group in sync or out of phase with the baseline.
  - *💡 Slow Flashing / Blink:* Theatrical blinking.
  - *✍️ Write-On / Write-Off:* Successively illuminates the group in sequence.
  - *🎆 Fireworks (Radiating Starburst):* 4-phase pyrotechnic explosion with center ignition flash, outward expanding spark trails with decaying ember tails, starlight tip crackles, and dark sky resets. Uses serpentine wiring geometry for maximum solder efficiency.
- **Inspect Group:** Click the **Inspect** button next to any group to highlight its member LEDs on the canvas.
- **Delete Group:** Click the red **🗑️** button to dismantle a group and return its LEDs to the global float baseline.

---

## 6. Physical Wiring Route Optimization

Attaching LEDs to a shirt by hand can easily result in tangled wire spaghetti if the LEDs are numbered randomly. The simulator solves this with a **continuous shortest-path wiring optimizer**.

### How It Works
1. Click the **🔌 Optimize Wiring Route** button in the toolbar.
2. The algorithm starts at the bottom-left corner of the shirt (where your battery pack and ESP32 pocket are typically located).
3. It uses a 2-opt spatial traveling salesman algorithm to renumber every LED along the shortest continuous physical snake route.
4. Each LED is renumbered so LED `0` connects to LED `1`, which connects to LED `2`, and so on, with minimum wire length between successive pixels.
5. Toggle **Show Wiring Route** in Section 6 to see the physical wire path drawn directly on the canvas!

### 🎆 Fireworks Starburst Generator, Placement, & Scaling
Creating radial fireworks bursts requires clean geometry, flexible placement, and predictable physical wiring:
1. **Initial Corner Placement & Position Presets:**
   - Stamping initially positions the fireworks cluster in the upper corner of the shirt (**↖ Top-Left corner** at $x = 28\%, y = 22\%$, above the race bib clearance zone).
   - Use the one-click position presets (**↖ Top-Left**, **↗ Top-Right**, **⏺ Center**) to instantly reposition the firework.
2. **Move & Scale Controls (Sliders & Direct Canvas Drag):**
   - **Move X & Move Y Sliders:** Fine-tune position horizontally ($15\% - 85\%$) and vertically ($15\% - 55\%$) with live slider feedback.
   - **Scale / Radius Slider:** Dynamically expand or contract the burst diameter ($7\% - 24\%$) around its center hub.
   - **Direct Canvas Multi-Drag:** Simply click and drag any LED belonging to the firework cluster directly on the costume canvas! The entire starburst moves as a unified group, and the Move X/Move Y sliders update synchronously in real-time.
3. **Color Customization (Presets & Custom Color Picker):**
   - Choose between **🌈 Multi-Color (Disney Classic)** (distinct hue on every ray) or vibrant single-color themes: **✨ Golden Amber**, **💠 Alice Cyan**, **💖 Coral Rose**, **⚡ Electric Lime**, **💜 Royal Violet**, **🔥 Blazing Red-Orange**, or **⭐ Starlight White**.
   - Select **🎨 Custom Hex Color...** to open an interactive native color picker and dial in any hex color for your show.
   - Changing colors updates the cluster in real time while maintaining warm incandescent shifts along the trailing rays.
4. **Persistent Center Trailing Effect & Completely Off (Unlit) Baseline:**
   - In previous iterations, all LEDs dimmed out as the wavefront moved or bled into global background patterns. Now:
     - *Completely Off (Unlit) Baseline:* Outside active explosion cues, all firework LEDs remain **100% off (unlit)**. They do not participate in global background chases or ambient sparkles, keeping the firework location dark and invisible until detonation. Unlit LEDs render realistically on canvas as dark SMD pixel beads (`rgba(22, 26, 33, 0.85)`) without artificial central white filament cores or glow bloom.
     - *Phase 1 (Ignition):* Center flashes with white-hot brilliance while outer unreached LEDs remain completely dark (unlit).
     - *Phase 2 (Expanding Wavefront):* Center LEDs hold at high intensity ($\sim 70\%$) while trailing embers bridge the line out to the spark head, creating a continuous radiating streak of fire. Ahead of the expanding wavefront, outer LEDs stay completely unlit.
     - *Phase 3 (Tip Crackle):* Center stays lit ($\sim 50\%$) as a visual anchor while outer tips crackle; burned-out inner steps turn completely off.
     - *Phase 4 (Rest / Idle):* Burst concludes, all firework LEDs fade out completely to **0% intensity (black/unlit)** until the next scheduled burst.
5. **Master Timeline Scheduling & Explosion Cue Director:**
   - **Automatic Timeline Auto-Placement:** Stamping a fireworks cluster (**"🎆 Stamp Fireworks in Corner"**) automatically creates and schedules fireworks explosion cues on the Master Timeline in the Parade Cue Director and turns Sequence Mode ON. You never need to manually navigate and build cues from scratch.
   - **Auto-Schedule Bursts:** Click **"⚡ Auto-Schedule Bursts"** in the Fireworks card to re-populate recurring explosion bursts evenly spaced across the full loop duration (e.g. at 6s, 28s, 52s, 74s for a 90s show).
   - **Single Cue at Playhead:** Click **"⏱️ Add at Playhead"** to drop a burst cue right at the current scrubber playhead position.
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
   - Placing a firework cluster claims $N_{\text{fw}}$ LEDs from the float pool, preserving exactly **100 LEDs on screen**.
   - Click **"🔄 Re-distribute Other LEDs (Full Graphic)"** to re-distribute the remaining $(100 - N_{\text{fw}})$ LEDs across the **entire character graphic** (without any exclusion zone) while keeping your firework cluster intact.
9. **Canvas Numbering & Identification:**
   - With **Show Numbers** active or when inspecting bulbs, each firework LED displays its exact ray and step badge: e.g. `R1:1 (CTR)`, `R1:4 (TIP)`, `R2:1 (CTR)`, `R2:4 (TIP)`.
   - The LED Inspector displays the full role breakdown: e.g. `Ray 2 of 5 • Trail Step 3 (Mid-Trail)`.

---

## 7. Artwork Management & runDisney 10K Race Bib Overlay

You can choose from pre-loaded Disney parade artwork or upload your own high-resolution shirt graphics, complete with realistic race bib collision checking.

### Built-in Graphic Presets
Use the **Graphic Style** dropdown in Section 1 to switch between:
- **🐉 Pete's Dragon (Elliott):** Default 100-LED layout with emerald body scales, magenta hair crest, and incandescent starlight sparkles.
- **🎃 Cinderella's Coach:** Classic golden carriage outline with dual spinning wheels, pumpkin body, and royal lanterns.
- **🎃 Carriage (No Horses):** Focused Cinderella coach design with clean wheel arches, royal carriage frame, and dedicated 100-LED preset.

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
- **Cue Name:** A custom theatrical label (e.g., `Carriage Wheels Spin`, `Snout Fire Breath`).
- **Target Layer:** Select either `🌐 Global Float` or any active animation group (e.g. `🎡 Group: Front Wheel`).
- **Pattern / Effect:** Select from the 10 built-in lighting effects (see Section 10).
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

---

## 13. Hardware Integration: Live Wi-Fi Streaming & Standalone USB Flashing

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

## 14. Dual-Mode ESP32 Firmware, Button Toggle & Float ID Selector

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

## 15. Keyboard Shortcuts & Quick Reference Cheat Sheet

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
| `Escape` | Canvas | **Deselect All** LEDs |
| Arrow Right `]` / `n` | LED Select | Select **Next LED** in wiring order |
| Arrow Left `[` / `p` | LED Select | Select **Previous LED** in wiring order |
| Click on Timeline Track | Timeline | **Seek playhead** to that exact second |
| Click on Cue Block | Timeline | **Jump to cue start** and highlight cue card in editor |

---

*Disney, Main Street Electrical Parade, Pete's Dragon, and Cinderella are registered trademarks of The Walt Disney Company. This open-source project is an unofficial tribute created for the Walt Disney World 10K runDisney event.*
