# Main Street Electrical Parade - Synchronized LED Costumes (WDW 10K)

This project powers synchronized, addressable LED lighting across **7 runner costumes** inspired by Disney's **Main Street Electrical Parade** for the Walt Disney World 10K.

---

## The Concept

Each runner wears a matte black technical running shirt outlined with glow-in-the-dark paint and illuminated by individually addressable **WS2812B "Seed" / Pebble LEDs** to replicate the vintage incandescent bulbs of the parade floats.

An **ESP32** microcontroller on each runner coordinates lighting patterns wirelessly in real time using **ESP-NOW** (connectionless peer-to-peer 2.4 GHz radio), requiring **no Wi-Fi router or cellular service**.

### The 7 Floats Roster

1. **The Train (Casey Jr.):** Warm white chugging locomotive headlight & steam pulses (parade leader pulling the Title Drum).
2. **The Title Drum:** Golden chasing marquee border, "Disney" electric text accent.
3. **The Turtle:** Whimsical spinning shell spirals, blinking amber eyes, and teal/green shell pattern.
4. **The Snail:** Multi-color rotating rainbow spiral shell wheels and neon antennae glow.
5. **Cinderella's Coach:** Shimmering fairy dust sparkle and midnight pumpkin carriage glow.
6. **Pete's Dragon (Elliott):** Chartreuse/green body scales with orange/red fire breathing effect.
7. **To Honor America (Flag & Eagle):** Patriotic red, white, and blue finale fireworks shimmer with majestic illuminated eagle.

---

## Hardware Specifications

* **Microcontrollers:** ESP32 (e.g. ESP32-WROOM-32D or Seeed XIAO ESP32)
* **LED Strands:** 200 WS2812B / WS2811 Addressable 5V Seed/Pebble Pixels (100 front + 100 back duplicated, black wire, ~1" to 2" spacing)
* **Data Resistor:** 220 Ω to 470 Ω inline on the data line between GPIO 16 and LED Data-In
* **Power Source:** 5V USB portable power bank (5,000–20,000 mAh rating, FastLED hardware limited to 2000 mA / 2.0A) per runner with built-in simulator Battery Life & Power Budget Calculator
* **Costume Simulation:** Visual browser-based layout engine (`python simulator.py` @ `localhost:8000`) with built-in presets (Pete's Dragon, Cinderella's Coach, Carriage No Horses, Casey Jr., Title Drum, Turtle, Snail, Eagle), 7-Shirt Fleet Show Creator Studio featuring a 19-block choreography palette (traveling waves, dual collision shockwaves, butterfly ripples, fairy dust waterfalls, fleet pulses, wig-wags, sparkle storms, baton chases, and grand finales), interactive NLE-grade visual timeline block editor (drag-to-stretch, rolling trim, and drag-and-drop reordering), multi-float live Wi-Fi UDP streaming (`Opcode 0x02`), pre-race Corral Roll Call & ESP-NOW Fleet Radar (instant identification strobe, 4s rapid attendance wave, signal RSSI, battery voltage, and lineup readiness), race-day battery life calculator with 7-float power breakdown, double-tap 4-second rapid attendance wave, 300ms debounced one-shot trigger and early stop, "Snap to 30.0s" sequence normalization, JSON show persistence, 1-click & double-click Single View editing from fleet cards, real 700-LED mini-shirt visualizer, multi-mode wireless sync (ESP-NOW Wave, Free-Run, Show Sequence), Fireworks Starburst cluster generator with corner placement, move & scale controls, canvas multi-drag, full-graphic LED re-distribution (maintaining strictly 100 LEDs per shirt), and authentic runDisney 10K Race Bib (#1952) with Chip & Dale and BibBoards fastener clearance.

---

## Wireless Synchronization (ESP-NOW)

* **Protocol:** ESP-NOW broadcast (Destination MAC `FF:FF:FF:FF:FF:FF`).
* **Architecture:**
  * **Unit 1 (Leader / Transmitter):** Broadcasts timing ticks, BPM tempo, master brightness, and pattern triggers.
  * **Units 2–7 (Followers / Receivers):** Listen to broadcast packets, sync their internal animation clock, and calculate their position-based phase delay for traveling parade chases down the line of runners.
* **On-the-Fly Button Controls (BOOT Button on GPIO 0):**
  * **Double Tap (2 taps within 400ms):** Triggers **4-Second Rapid Attendance Roll Call** across the fleet (Floats 1..7 illuminate solo for 500ms in signature colors, followed by a 500ms unison double emerald green flash). Zero phones or routers needed!
  * **Single Tap (< 600ms):** Toggles the **30-Second Theatrical Fleet Routine** once (press again to stop early).
  * **Hold for 3 Seconds:** Enter **Float ID Configuration Mode** (1 to 7) with visual LED feedback and permanent NVS flash auto-save. No hardcoded MAC addresses required!

---

## ⚡ Quick Start for Runners / Brothers (No Git Required!)

You don't need Git, Google Antigravity, or any programming tools:
1. **Download:** Click the green **`<> Code`** button above ➔ **`Download ZIP`** (or [Click Here to Download ZIP](https://github.com/kidmd/WDW-costumes/archive/refs/heads/main.zip)).
2. **Extract:** Right-click the `.zip` file and select **Extract All...** to any folder on your computer.
3. **Plug in & Flash:** Connect your ESP32 via USB and double-click **`flash_firmware.bat`** (Windows) or **`flash_firmware.command`** (Mac).
4. See **[`FLASHING_INSTRUCTIONS.md`](FLASHING_INSTRUCTIONS.md)** for complete hardware wiring and float selection instructions.

---

## Project Structure & Documentation

* [`FLASHING_INSTRUCTIONS.md`](FLASHING_INSTRUCTIONS.md): **⚡ Quick Flashing Guide for the Brothers** (Double-click 1-click flasher, Web Browser flasher, and Arduino IDE).
* [`CRICUT_ARTWORK_GUIDE.md`](CRICUT_ARTWORK_GUIDE.md): **🎨 Cricut HTV Costume Artwork Guide** (Layered SVG cut files, color mats, heat press settings, and visual catalog).
* [`SIMULATOR_USER_GUIDE.md`](SIMULATOR_USER_GUIDE.md): **Complete User Guide & Theatrical Lighting Manual** for the browser simulator, multi-layer timeline, and ESP32 hardware flasher.
* [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md): Live project milestones, wiring specifications, and development changelog.
* `flash_firmware.bat`: One-click Windows desktop firmware flasher script.
* `flash_firmware.command`: One-click Mac / Linux desktop firmware flasher script.
* `arduino/MSEP_Costume/`: Ready-to-open native Arduino IDE sketch.
* `firmware/`: Pre-compiled ROM binary files (`firmware_float1.bin` through `firmware_float7.bin`, `firmware.bin`, `bootloader.bin`, `partitions.bin`) and Web Serial manifests.
* `src/`: C++ / Arduino firmware source code for ESP32.
* `simulator/`: Web-based visual simulator and theatrical cue director.
* `platformio.ini`: PlatformIO configuration with board targets and library dependencies (FastLED).
