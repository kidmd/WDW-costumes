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
* **Power Source:** 5V USB portable power bank (2.1A+ rating, FastLED limited to 2000 mA) per runner
* **Costume Simulation:** Visual browser-based layout engine (`python simulator.py` @ `localhost:8000`) with built-in presets (Pete's Dragon, Cinderella's Coach, Carriage No Horses, Casey Jr., Title Drum, Turtle, Snail, Eagle), 7-Shirt Fleet Lineup Manager with real 700-LED mini-shirt visualizer and multi-mode wireless sync (ESP-NOW Wave, Free-Run, Show Sequence), Fireworks Starburst cluster generator with corner placement, move & scale controls, canvas multi-drag, and full-graphic LED re-distribution (maintaining strictly 100 LEDs per shirt), and authentic runDisney 10K Race Bib (#1952) with Chip & Dale and BibBoards fastener clearance.

---

## Wireless Synchronization (ESP-NOW)

* **Protocol:** ESP-NOW broadcast (Destination MAC `FF:FF:FF:FF:FF:FF`).
* **Architecture:**
  * **Unit 1 (Leader / Transmitter):** Broadcasts timing ticks, BPM tempo, master brightness, and pattern triggers.
  * **Units 2–7 (Followers / Receivers):** Listen to broadcast packets, sync their internal animation clock, and calculate their position-based phase delay for traveling parade chases down the line of runners.
* **On-the-Fly Configuration:** Hold the onboard **BOOT button for 3 seconds** to assign any ESP32 to Floats 1 through 7 with visual LED feedback and save to persistent flash memory (`Preferences.h`). No hardcoded MAC addresses required!

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
* `firmware/`: Pre-compiled ROM binary files (`firmware.bin`, `bootloader.bin`, `partitions.bin`).
* `src/`: C++ / Arduino firmware source code for ESP32.
* `simulator/`: Web-based visual simulator and theatrical cue director.
* `platformio.ini`: PlatformIO configuration with board targets and library dependencies (FastLED).
