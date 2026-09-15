# Main Street Electrical Parade (WDW 10K) - LED Control System

## Project Overview
This project coordinates synchronized, addressable LED lighting across **7 runner costumes** styled as the iconic floats of Disney's **Main Street Electrical Parade** for the Walt Disney World 10K.

* **Theme:** Main Street Electrical Parade (7 Floats)
* **Base Shirts:** Black moisture-wicking technical running shirts with glow-in-the-dark graphic outlines
* **Lighting:** 5V WS2812B "Seed / Pebble" RGBIC fairy pixel strings (~1" to 2" spacing for discrete light bulb look)
* **Controller:** ESP32 Microcontrollers (1 per runner)
* **Wireless Protocol:** ESP-NOW (connectionless 2.4GHz peer-to-peer broadcast; no router/hotspot needed)
* **Power Source:** 5V USB portable power bank per runner

---

## The 7-Runner Roster & Float Assignments

| Float # | Unit / Float Name | Visual Concept & Accent Lights |
| :---: | :--- | :--- |
| **1** | **The Title Drum** | Golden chasing marquee border, "Disney" electric text accent |
| **2** | **Casey Junior Circus Train** | Warm white chugging headlight, locomotive steam pulses |
| **3** | **Pete's Dragon (Elliott)** | Chartreuse/green scales with orange/red fire breathing effect |
| **4** | **Alice / Caterpillar Mushroom** | Whimsical neon swirls, psychedelic alternating colors |
| **5** | **Cinderella Carriage & Clock** | Brilliant fairy dust shimmer, midnight clock chimes |
| **6** | **Peter Pan / Pirate Ship** | Lantern gold flicker, ocean waves, skull & crossbones |
| **7** | **Spinning Snail / Finale** | Rotating rainbow spiral wheels, grand parade finale twinkle |

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

- [ ] **Milestone 1: Bench Setup & Single-Strand Validation**
  - [ ] Configure toolchain in Antigravity (PlatformIO or Arduino CLI).
  - [ ] Bench wire 1 ESP32 with 220/330/470 Ω resistor, isolated 5V power, and common ground.
  - [ ] Upload single-node test firmware using FastLED with software current limiting (`setMaxPowerInVoltsAndMilliamps`).
  - [ ] Verify discrete bulb appearance, color calibration (RGB vs GRB), and stability.

- [ ] **Milestone 2: ESP-NOW Wireless Synchronization**
  - [ ] Build Leader (Broadcast) firmware with timing ticks and pattern triggers.
  - [ ] Build Follower firmware with assigned Unit IDs (1–7) and phase offsets.
  - [ ] Verify bench latency and synchronized color switching across multiple boards.

- [ ] **Milestone 3: Parade Animation Sequencing**
  - [ ] Implement classic traveling parade chase (running down the line of 7 floats).
  - [ ] Implement float-specific accent animations (fire flickers, clock chime, sparkles).
  - [ ] Optional: Sync tempo to the *Baroque Hoedown* soundtrack.

- [ ] **Milestone 4: Wearable Construction & Race Prep**
  - [ ] Assemble Y-splitter power cables for race-day battery packs.
  - [ ] Secure seed LEDs to black running shirts (clear nylon tacking / fabric adhesive).
  - [ ] Add quick-disconnect JST connectors between waist belts and shirts.
  - [ ] Sweat-proofing and strain relief testing.

---

## Progress Log

### Entry: Kickoff & Architecture Definition
* **Date:** 2026-09-14
* **Status:** Initialized project workspace and documentation.
* **Notes:**
  * Created project tracking log [`PROJECT_PROGRESS.md`](file:///c:/Users/Kiddi/Desktop/WDW%20costumes/PROJECT_PROGRESS.md).
  * Outlined 7-float roster and ESP-NOW broadcast architecture.
  * Verified resistor options (330 Ω ideal, 220 Ω approved as safe for bench testing; 2.2 kΩ rejected).
  * Established 5V bench power isolation guidelines.
