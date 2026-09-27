# ⚡ MSEP Costume Simulator - Quickstart Guide

> **Welcome to the family running crew!**  
> We have **7 runners** hitting the Walt Disney World 10K course (2 brothers, 1 sister, 1 brother-in-law, and 3 sisters-in-law), with hardware and code engineered by the 3 brothers.  
> This guide gets you up and running with the lighting simulator in **6 simple steps**.  
> *(Need deep technical details? See the [Full Simulator User Guide](SIMULATOR_USER_GUIDE.md)).*

---

## 🧭 The Simulator Layout at a Glance

When you open the simulator, you'll see three main areas:
- **Top Tabs:** Switch between **Single View** (customize individual floats) and **Fleet View** (orchestrate the 7-runner synchronized show).
- **Center Canvas:** Visual preview of the running shirt with 100 LEDs, authentic glow, and race bib clearance.
- **Left Sidebar:** Controls for artwork presets, animation groups, cue creation, and hardware flashing.
- **Bottom Timeline Bar:** The transport controls (`▶ Play`, `⏸ Pause`, `⏹ Stop`) and cue tracks.

---

## 1. How to Start the Simulator

1. Open a terminal or Command Prompt in the project folder.
2. Run the local Python server:
   ```bash
   python simulator.py
   ```
3. Open your web browser (Chrome, Edge, or Brave recommended) and visit:
   ```
   http://localhost:8000
   ```
4. You're in! The simulator runs locally on your machine at 60 FPS.

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

### Method A: Web Browser Flasher (Easiest — Chrome or Edge)
1. Plug the ESP32 into your computer using a USB data cable.
2. In the simulator, click the green **`⚡ Web Flasher`** link in the top-right header (or click `⚡ Flash Float...` on Tab 6).
3. Click your assigned runner float card (e.g., 🚂 **Float 1: Casey Jr.** for the leader, or **Floats 2–7** for followers).
4. Click **`⚡ Connect & Flash`**, choose your USB serial port, and click **Install**. Done in ~15 seconds!

### Method B: Double-Click Desktop Scripts
- **Windows:** Double-click [`flash_firmware.bat`](flash_firmware.bat).
- **Mac / Linux:** Double-click [`flash_firmware.command`](flash_firmware.command).

---

## 🎛️ Race Morning Button Cheatsheet (BOOT / GPIO 0)

Every runner's costume has one button (`BOOT` pin on the ESP32). Here is how it works on race morning:

| Gesture | Action | What Happens |
|---|---|---|
| **Single Tap** (< 600ms) | 🎆 **30s Fleet Routine** | Fires the synchronized fleet show across all 7 shirts! Tap again to cancel early. |
| **Double Tap** (< 400ms) | ⚡ **4s Roll Call Wave** | Quick corral check: Floats 1➔7 flash solo for 500ms down the line, followed by a double emerald-green unison flash. |
| **Hold 5s** (Wait for 4 white dots) | ⚪ **Float ID Config** | Progressive 1s–4s white charging meter, then sets Float ID (1–7). |
| **Release Hold Early** (< 5s) | 🛡️ **Safe Abort** | Cleanly cancels hold and restores normal lights without triggering any show. |

---

## 📚 Where to Go Next

- 📖 **[SIMULATOR_USER_GUIDE.md](SIMULATOR_USER_GUIDE.md)**: The full technical manual covering physical wiring optimization, FastLED power budgeting, and advanced effects.
- ⚡ **[FLASHING_INSTRUCTIONS.md](FLASHING_INSTRUCTIONS.md)**: Flashing options, USB drivers, and troubleshooting.
- 🎨 **[CRICUT_ARTWORK_GUIDE.md](CRICUT_ARTWORK_GUIDE.md)**: Heat transfer vinyl (HTV) cut files and shirt press instructions.
- 📋 **[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)**: Project milestones and development history.
