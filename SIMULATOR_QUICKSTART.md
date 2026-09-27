# ⚡ MSEP Costume Simulator - Quickstart Guide (TL;DR)

> **"Too Long; Didn't Read" edition for the brothers running the WDW 10K.**  
> Need the complete 90-page engineering manual? See the [Full Simulator User Guide](SIMULATOR_USER_GUIDE.md).

---

## 🚀 1. Launching the Simulator in 10 Seconds

1. Open your terminal in the project folder and start the local server:
   ```bash
   python simulator.py
   ```
2. Open your web browser (Chrome, Edge, or Brave recommended) and visit:
   ```
   http://localhost:8000
   ```
3. That's it! You'll see the full 60 FPS theatrical lighting studio.

---

## 🧭 2. The 3-Zone Layout at a Glance

```
┌────────────────────────────────────────────────────────────────────────┐
│  [Tab 1: Single View]  ...  [Tab 6: Fleet View]     [📡 Live Stream]   │
├─────────────────────────┬──────────────────────────────────────────────┤
│  LEFT SIDEBAR           │  CENTER CANVAS                               │
│  - Section 1: Presets   │  - Authentic 100-LED running shirt preview   │
│  - Section 2: Cue Cards │  - Click & drag LEDs or pan/zoom canvas      │
│  - Section 3: Flasher   │  - runDisney 10K Race Bib (#1952) clearance  │
├─────────────────────────┴──────────────────────────────────────────────┤
│  BOTTOM TIMELINE BAR                                                   │
│  - Transport: ▶ Play, ⏸ Pause, ⏹ Stop, 🔁 Loop, 🎬 Sequence ON/OFF    │
│  - Multi-track timeline lanes with draggable, trimmable cue blocks     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 3. "I Just Want To..." — Common Tasks Cheatsheet

### 🎨 ...Customize a Single Float's Look
1. Click **Tab 1: Single View** at the top.
2. In the left sidebar under **Section 1 (Float Artwork & LED Setup)**, pick any float preset (*Casey Jr.*, *Title Drum*, *Turtle*, *Snail*, *Cinderella's Coach*, *Pete's Dragon*, or *To Honor America*).
3. Click individual LEDs on the canvas to inspect them, or `Shift + Drag` a box to select a cluster and assign colors or effects.

### ✂️ ...Edit Sequences on the Timeline (Like a Pro NLE)
- **Play / Pause:** Tap the `Spacebar`.
- **Slide / Move a Clip:** Click anywhere in the **middle** of a cue block (`cursor: grab`) and drag left or right. It slides smoothly with 0.1-second snapping without changing duration.
- **Shorten / Lengthen Start:** Hover over the **left edge** (`cursor: ew-resize`) and drag to adjust the start time (locks the end time in place).
- **Shorten / Lengthen Duration:** Hover over the **right edge** (`cursor: ew-resize`) and drag to extend or trim the duration.
- **Floating Tooltip:** A live badge floats above your cursor showing `Start: Xs | End: Ys (Dur: Zs)`.
- **Add a New Routine:** Click **`➕ Add Cue`** in Section 2 of the left sidebar.

### 👑 ...Test the Synchronized 30-Second 7-Runner Fleet Show
1. Click **Tab 6: Fleet View** at the top.
2. Tap the `[F]` key, press `Spacebar`, or click the big gold **`👑 Activate Fleet Show`** button.
3. Watch all 7 brother costumes execute the synchronized traveling waves, sparkle storms, butterfly ripples, and grand finale!
4. Press `[F]` or `Spacebar` again to stop early and return to baseline.

### 🛰️ ...Check Pre-Race Corral Radar (Bench & Wi-Fi Check)
1. On the Fleet Tab, expand **Section 3: Pre-Race Corral Roll Call & ESP-NOW Fleet Radar** (or click the `🛰️ Corral Radar` quick-jump button).
2. Check the live status pills (`🟢 7/7 READY`), battery voltage, and wireless signal strength.
3. Click **`⚡ 4s Rapid Attendance Wave`** to simulate the corral roll call wave (each float flashes solo for 500ms down the line, followed by a double emerald-green unison flash).

---

## 💡 4. Streaming Live to Real LEDs (Bench Testing)

Want to see the simulator drive your physical costume right now?

1. Connect your laptop and ESP32 to the same 2.4 GHz Wi-Fi network (or connect your laptop to the ESP32's built-in direct fallback hotspot: `MSEP-Costume-AP`, password: `electricalparade`).
2. Click **`📡 Live Stream`** in the top navigation bar.
3. Enter your ESP32's IP address (default: `192.168.4.1` for direct AP mode).
4. Click **`Start Streaming`** (Status switches to `🟢 Streaming Active @ 30 FPS`).
5. As you scrub the timeline or play animations in your browser, your real LEDs light up in real time!

---

## ⚡ 5. Flashing an ESP32 for Race Day (Zero-Config)

### Option A: 1-Click Flasher inside the Simulator
1. Plug your ESP32 into your computer via USB.
2. On **Tab 5: Deploy & Hardware** (or click `⚡ Flash Float...` on Tab 6), pick your float role:
   - `Float 1: The Train (Casey Jr.)` — 👑 Fleet Leader
   - `Float 2 through 7` — 📡 Fleet Followers
3. Click **`⚡ Flash Standalone Firmware (USB)`** (or click **Web Serial Flasher** to flash directly inside Google Chrome / Edge without installing anything).

### Option B: Double-Click Desktop Scripts
- **Windows:** Double-click [`flash_firmware.bat`](flash_firmware.bat)
- **Mac / Linux:** Double-click [`flash_firmware.command`](flash_firmware.command)

---

## 🎛️ 6. The Race-Day On-Costume Button (BOOT / GPIO 0)

Every brother has one onboard button on their ESP32 (`BOOT` pin). Here is how it behaves on race morning:

| Gesture | Action | What Happens |
|---|---|---|
| **Single Tap** (< 600ms) | 🎆 **30s Fleet Show** | Fires the synchronized theatrical routine across all 7 shirts! Tap again to cancel early. |
| **Double Tap** (< 400ms) | ⚡ **4s Roll Call Wave** | Quick corral check: Floats 1➔7 flash solo for 500ms each, then all 7 flash emerald green together. |
| **Hold for 5s** (Wait for 4 white dots) | ⚪ **Float ID Config** | Lights 1➔4 white LEDs (charging meter) then enters Float ID selector (1 to 7). |
| **Release Hold Early** (< 5s) | 🛡️ **Safe Abort** | Cleanly cancels hold and restores normal lights without triggering any show. |

---

## ⌨️ 7. Keyboard & Mouse Cheat Sheet

| Key / Gesture | Where | What It Does |
|---|---|---|
| `Spacebar` | Single View | **Play / Pause** timeline playback |
| `Spacebar` or `F` | Fleet View | **Trigger / Stop** 30-second Fleet Show |
| `Drag Clip Body` | Timeline | **Slide / Move** clip position (0.1s snap) |
| `Drag Left Edge` | Timeline | **Trim Start Time** of clip (locks end time) |
| `Drag Right Edge` | Timeline | **Trim Duration** of clip (locks start time) |
| `Click on Track` | Timeline | **Seek playhead** to that second |
| `Click Cue Block` | Timeline | **Jump to start** & highlight card in sidebar |
| `Right-Click + Drag` | Canvas | **Pan** workspace smoothly |
| `Mouse Wheel` | Canvas | **Zoom** in / out |
| `Shift + Drag` | Canvas | **Marquee Select** multiple LEDs |
| `0` (Zero) | Canvas | **Reset Zoom** to 100% centered view |
| `Ctrl + A` | Canvas | **Select All** 100 LEDs |
| `Escape` | Canvas | **Deselect All** |

---

## 📚 8. Deep-Dive Links

- 📖 **[SIMULATOR_USER_GUIDE.md](SIMULATOR_USER_GUIDE.md)**: Full manual covering Poisson LED scatter, wiring route optimization, custom PNG upload, and FastLED power budgeting.
- ⚡ **[FLASHING_INSTRUCTIONS.md](FLASHING_INSTRUCTIONS.md)**: Detailed step-by-step firmware flashing guide with pinouts and driver troubleshooting.
- 🎨 **[CRICUT_ARTWORK_GUIDE.md](CRICUT_ARTWORK_GUIDE.md)**: Cricut HTV cut files, color mats, vinyl layering, and heat-press temperatures.
- 📋 **[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)**: Full milestone history and hardware engineering progress log.
