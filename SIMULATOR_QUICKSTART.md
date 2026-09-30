# ⚡ MSEP Costume Simulator - Quickstart Guide

> **Welcome to the family running crew!**  
> We have **7 runners** hitting the Walt Disney World 10K course (2 brothers, 1 sister, 1 brother-in-law, and 3 sisters-in-law), with hardware and code engineered by the 3 brothers.  
> This guide gets you up and running with the lighting simulator in **6 simple steps**.  
> *(Need deep technical details? See the [Full Simulator User Guide](SIMULATOR_USER_GUIDE.md)).*

---

## 🧭 The Simulator Layout at a Glance

When you open the simulator, you'll see three main areas:
- **6 Task Sidebar Tabs:** Organized into a 2-row grid (`🎨 Layout`, `✨ Ambient`, `👥 Groups`, `🎬 Float Show`, `🏃 Fleet`, `⚡ Deploy`).
- **Center Canvas:** Visual preview of the running shirt with 100 LEDs, authentic glow bloom, and official runDisney 10K race bib (#1952) clearance.
- **Contextual Inspector Dock:** Docked at the bottom of the sidebar for inspecting LED numbers, setting colors, and configuring zone groups.
- **Bottom Timeline Bar:** Transport controls (`▶ Play`, `⏸ Pause`, `⏹ Stop`), timeline hover-scrubbing, grid quantization, and collapsible cue tracks.

---

## 1. How to Start the Simulator

- **Option A — One-Click (Easiest on Windows):**
  Just double-click **[`start_simulator.bat`](start_simulator.bat)** in the main project folder! It checks for Python and launches the server automatically.
- **Option B — Command Prompt / Terminal:**
  Open a terminal in the project folder and run:
  ```bash
  python simulator.py
  ```

Once running, open your web browser (Chrome, Edge, or Brave recommended) and visit:
```
http://localhost:8000
```
You're in! The simulator runs locally on your machine at 60 FPS.

---

## 2. How to Add a Graphic to a Shirt or Start with a Preset

Make sure you are on **Tab 1: Single View** (at the top). Look at **Section 1: Float Artwork & LED Setup** in the left sidebar:

- **Option A — Use a Pre-Built Float Preset (Easiest):**
  1. Click the **Float Preset** dropdown.
  2. Pick any of our 7 parade floats (*The Train / Casey Jr.*, *Title Drum*, *The Turtle*, *The Snail*, *Cinderella's Coach*, *Pete's Dragon*, or *To Honor America*).
  3. The artwork loads automatically, perfectly sized above the official #1952 race bib, with 100 color-matched LEDs already positioned!
- **Option B — Upload Your Own Graphic:**
  1. In the preset dropdown, select **"Upload Custom Artwork Image"**.
  2. Pick any transparent PNG or JPEG from your computer.
  3. Click **"✨ Scatter 100 Color-Matched LEDs"** to automatically distribute 100 LEDs evenly over your graphic and sample the artwork colors.

---

## 3. How to Create Animation Groups

An **Animation Group** is a set of LEDs that do something special together — like carriage wheels spinning, lanterns blinking, or a dragon's crest glowing.

1. **Select the LEDs on Canvas:**
   - Hold `Shift` and **click-and-drag a box** around the LEDs you want to group (or click individual LEDs).
   - Selected LEDs will light up with yellow dashed selection rings.
2. **Save the Group:**
   - In the left sidebar under **Selection / Group Actions**, click **"📦 Create Animation Group from Selection"**.
   - Give it a name (e.g., `Front Wheels` or `Lanterns`).
   - Pick an initial pattern and speed (BPM), then click **Save Group**.
3. Your new group now appears in the sidebar and gets its own dedicated track lane on the bottom timeline!

---

## 4. Use Groups to Create Cues for the Single Shirt Show

Now script what happens along your 90-second parade sequence:

1. In the left sidebar, scroll to **Section 2: Parade Cue Director** and click **`➕ Add Cue`**.
2. Set up your cue card:
   - **Target Layer:** Choose `🌐 Global Float` (affects the whole shirt) or select one of your **Animation Groups** (e.g., `Front Wheels`).
   - **Pattern / Effect:** Pick from 12 effects (like *Color Wave*, *Sparkle / Strobe*, *Rainbow Cycle*, or *Pulse / Breathe*).
   - **Start Time & Duration:** Set when the effect begins and how long it lasts.
3. **Edit Directly on the Timeline (Bottom Bar):**
   - Tap `Spacebar` to Play or Pause the show.
   - **Move / Slide a clip:** Click anywhere in the **middle** of a cue block and drag left or right (snaps to 0.1s increments).
   - **Trim Start Time:** Hover over the **left edge** (`↔`) and drag left or right.
   - **Trim Duration:** Hover over the **right edge** (`↔`) and drag to shorten or lengthen the clip.

---

## 5. Create a Fleet Show

Once individual floats have their baseline looks, orchestrate the synchronized routine across all 7 costumes:

1. Click **Tab 6: Fleet View** at the very top.
2. You’ll see all 7 runner costumes lined up side-by-side in race order.
3. In **Section 1: 30-Second Fleet Show Creator**, click any block from the choreography palette to add it to the 30s timeline:
   - `🌊 Forward Wave` / `🌊 Reverse Wave` (travels down the line of runners)
   - `💓 Fleet Pulse` (all 7 shirts pulse together)
   - `⛈️ Sparkle Storm` (intense starlight across the entire fleet)
   - `🦋 Butterfly Ripple` (ripples out from the center runner to the wings)
4. **Test the Fleet Routine:**
   - Tap `[F]` or `Spacebar` (or click the big gold **`👑 Activate Fleet Show`** button).
   - Watch all 7 costumes execute the synchronized routine together in real time! Press `[F]` again to stop early and return to baseline.
5. **Corral Roll Call Check:** Click **`🛰️ Corral Radar`** to simulate the pre-race bench check and test the **4-second rapid attendance wave**.

---

## 6. Deploy the Shows onto the ESP32 Boards

Once you're happy with the designs, bake them into the microcontrollers for race day:

### Method A: Web Browser Flasher (Zero-Install — Chrome or Edge)
- **If Simulator is Running on your PC:** Click the green **`⚡ Web Flasher`** button in the top-right header (or open `http://localhost:8000/web_flasher.html`).
- **If on a Blank / Brother's Laptop (Nothing Downloaded):** Open the public GitHub link directly:  
  👉 **`https://kidmd.github.io/WDW-costumes/simulator/web_flasher.html`**
1. Plug the ESP32 into your computer using a USB data cable.
2. Click your assigned runner float card (e.g. 🚂 **Float 1: Casey Jr.**, 🐢 **Float 3: The Turtle**, 🐉 **Float 6: Pete's Dragon**).
3. Click **`⚡ Connect & Flash`**, choose your USB serial port, and click **Install**. Done in ~15 seconds with zero drivers, compilers, or software to install!

### Method B: In-Simulator Custom C++ Compiler (Deploy Tab)
- Located on **Tab 6: Deploy & Hardware** ➔ **`⚡ Flash Standalone Firmware (USB)`**.
- *Note:* This uses PlatformIO (pre-installed on your development PC) to re-compile custom C++ code and upload on the fly. `start_simulator.bat` launches Python for the simulator; if PlatformIO is not installed on a secondary computer, simply use the **Web Flasher (Method A)** instead!

### Method C: Double-Click Desktop Scripts
- **Windows:** Double-click **[`flash_firmware.bat`](flash_firmware.bat)** in the main project folder. It auto-detects your connected ESP32 and flashes the pre-compiled firmware in ~15 seconds.
- **Mac / Linux:** Double-click **[`flash_firmware.command`](flash_firmware.command)** *(or run `./flash_firmware.command` in Terminal)*.

---

## 🎛️ Race Morning Button Cheatsheet (BOOT / GPIO 0)

Upon plugging in USB power at 3:30 AM, **all costumes boot directly into 🌙 Corral Standby Mode** (12% dim midnight starlight twinkle drawing **< 120mA**) to save 80%+ of battery life during the 60–90 minute corral wait.

The BOOT button behavior depends on whether the node is configured as **👑 Master Leader (Float 1 - Casey Jr.)** or **📡 Follower (Floats 2–7)** to protect non-technical family runners from accidental show disruption:

| Gesture | Role | Action | What Happens |
|---|---|---|---|
| **Power-On (Plug USB)** | All Floats | 🌙 **Corral Standby** | Boots into 12% dim midnight starlight twinkle (<120mA draw). |
| **Single Tap** (< 600ms) | **👑 Leader (Float 1)** | ☀️ **Wake Fleet / Fleet Show** | **In Standby:** Wakes **entire fleet** to active parade mode (`0x51`).<br>**During Active Run:** Toggles/cancels the **30s Fleet Show** (`0x30`). |
| | **📡 Follower (Floats 2–7)** | ☀️ **Wake Local Only** | **In Standby:** Wakes **that local shirt only**.<br>**During Active Run:** *Ignored* (zero fleet disruption). |
| **Double Tap** (< 400ms) | **👑 Leader (Float 1)** | ⚡ **4s Roll Call Wave** | Triggers 4-second attendance wave across Floats 1➔7 followed by unison double emerald-green flash (`0x44`). |
| | **📡 Follower (Floats 2–7)** | 🛡️ **Protected** | *Ignored* (roll call reserved for Leader). |
| **Triple Tap** (< 600ms) | **👑 Leader (Float 1)** | 🌙 **Fleet Standby** | Drops **ENTIRE FLEET back into Corral Standby Mode** (`0x50`). |
| | **📡 Follower (Floats 2–7)** | 🌙 **Local Standby** | Drops **that local shirt only** into Corral Standby Mode. |
| **Long Hold** ($\ge$ 5s) | All Floats | ⚪ **Float ID Config** | Progressive 1s–4s white LED charging meter $\rightarrow$ 3 white flashes $\rightarrow$ tap to cycle Float ID (1–7) $\rightarrow$ 4 green flashes (Auto-Save to NVS). |
| **Release Hold Early** (< 5s) | All Floats | 🛡️ **Safe Abort** | Cleanly aborts hold and restores current pattern without changing Float ID or triggering show. |

---

## 📚 Where to Go Next

- 📖 **[SIMULATOR_USER_GUIDE.md](SIMULATOR_USER_GUIDE.md)**: The full technical manual covering physical wiring optimization, FastLED power budgeting, and advanced effects.
- ⚡ **[FLASHING_INSTRUCTIONS.md](FLASHING_INSTRUCTIONS.md)**: Flashing options, USB drivers, and troubleshooting.
- 🎨 **[CRICUT_ARTWORK_GUIDE.md](CRICUT_ARTWORK_GUIDE.md)**: Heat transfer vinyl (HTV) cut files and shirt press instructions.
- 📋 **[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)**: Project milestones and development history.
