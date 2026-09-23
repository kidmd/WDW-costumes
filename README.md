# Main Street Electrical Parade - Synchronized LED Costumes (WDW 10K)

This project powers synchronized, addressable LED lighting across **7 runner costumes** inspired by Disney's **Main Street Electrical Parade** for the Walt Disney World 10K.

---

## The Concept

Each runner wears a matte black technical running shirt outlined with glow-in-the-dark paint and illuminated by individually addressable **WS2812B "Seed" / Pebble LEDs** to replicate the vintage incandescent bulbs of the parade floats.

An **ESP32** microcontroller on each runner coordinates lighting patterns wirelessly in real time using **ESP-NOW** (connectionless peer-to-peer 2.4 GHz radio), requiring **no Wi-Fi router or cellular service**.

### The 7 Floats Roster

1. **The Title Drum:** Golden chasing marquee border, "Disney" electric text accent.
2. **Casey Junior Circus Train:** Warm white chugging locomotive headlight & steam pulses.
3. **Pete's Dragon (Elliott):** Chartreuse/green body scales with orange/red fire breathing effect.
4. **Alice in Wonderland / Caterpillar Mushroom:** Whimsical neon swirls & alternating colors.
5. **Cinderella's Carriage & Clock:** Shimmering fairy dust sparkle and clock chime pulses.
6. **Peter Pan / Pirate Ship:** Lantern flicker, ocean waves, and skull & crossbones highlight.
7. **The Spinning Snail / Grand Finale:** Multi-color rotating rainbow spiral wheels.

---

## Hardware Specifications

* **Microcontrollers:** ESP32 (e.g. ESP32-WROOM-32D or Seeed XIAO ESP32)
* **LED Strands:** 5V WS2812B / WS2811 Addressable Seed/Pebble Pixels (black wire, ~1" to 2" spacing)
* **Data Resistor:** 220 Ω to 470 Ω inline on the data line between GPIO and LED Data-In
* **Power Source:** 5V USB portable phone power bank (2.1A+ rating) per runner

---

## Wireless Synchronization (ESP-NOW)

* **Protocol:** ESP-NOW broadcast (Destination MAC `FF:FF:FF:FF:FF:FF`).
* **Architecture:**
  * **Unit 1 (Leader / Transmitter):** Broadcasts timing ticks, BPM tempo, master brightness, and pattern triggers.
  * **Units 2–7 (Followers / Receivers):** Listen to broadcast packets, sync their internal animation clock, and calculate their position-based phase delay for traveling parade chases down the line of runners.

---

## Project Structure & Documentation

* [`FLASHING_INSTRUCTIONS.md`](FLASHING_INSTRUCTIONS.md): **⚡ Quick Flashing Guide for the Brothers** (Double-click 1-click flasher, Web Browser flasher, and Arduino IDE).
* [`SIMULATOR_USER_GUIDE.md`](SIMULATOR_USER_GUIDE.md): **Complete User Guide & Theatrical Lighting Manual** for the browser simulator, multi-layer timeline, and ESP32 hardware flasher.
* [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md): Live project milestones, wiring specifications, and development changelog.
* `flash_firmware.bat`: One-click Windows desktop firmware flasher script.
* `flash_firmware.command`: One-click Mac / Linux desktop firmware flasher script.
* `arduino/MSEP_Costume/`: Ready-to-open native Arduino IDE sketch.
* `firmware/`: Pre-compiled ROM binary files (`firmware.bin`, `bootloader.bin`, `partitions.bin`).
* `src/`: C++ / Arduino firmware source code for ESP32.
* `simulator/`: Web-based visual simulator and theatrical cue director.
* `platformio.ini`: PlatformIO configuration with board targets and library dependencies (FastLED).
