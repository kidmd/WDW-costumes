# 🔌 ESP32 Hardware Wiring Plan & Electrical Specification
## Main Street Electrical Parade (WDW 10K) Synchronized LED Costumes

This document provides the definitive, bench-tested electrical wiring specification for the wearable ESP32 LED controllers powering our 7-runner family fleet for the Walt Disney World 10K.

---

## 1. System Overview & Component BOM

Each runner wears a self-contained, battery-powered lighting system controlling **200 addressable LEDs** (100 front chest pixels + 100 back pixels duplicated in real time):

| Component | Specification | Quantity per Runner | Notes |
| :--- | :--- | :---: | :--- |
| **Microcontroller** | ESP32-WROOM-32D / DevKit V1 (30-pin or 38-pin) | 1 | 240 MHz dual-core, onboard 2.4GHz antenna for ESP-NOW. |
| **Addressable LEDs** | WS2812B 5V "Seed / Pebble" RGBIC fairy light strings | 200 LEDs (2× 100) | Black enameled/insulated 3-conductor wire, ~1" to 2" spacing. |
| **Inline Data Resistor** | 220 Ω to 470 Ω, 1/4W resistor | 1 | Prevents voltage ringing/spikes on GPIO 16 data output. |
| **Tactile Buttons** | Momentary pushbuttons (SPST normally-open) | 2 | **Button 1:** Show Director / Wake<br>**Button 2:** Castle Photo / Sleep |
| **Power Source** | 5V USB portable power bank ($\ge 2.1\text{A}$ output, 5,000–20,000 mAh) | 1 | FastLED firmware limited to **5V, 2000mA (2.0A)** max. |
| **Power Cable** | Heavy-gauge USB-A to stripped 2-wire cable (or USB-C) | 1 | 20 AWG or 22 AWG power leads for minimal voltage drop. |
| **Connectors** | 3-pin JST-SM (Data, 5V, GND) or quick-disconnect terminals | 1–2 sets | Allows disconnecting the shirt from the electronics pouch. |

---

## 2. Complete ESP32 Pinout Assignment Table

```
                         ESP32 DevKit V1 (30-pin)
                              ┌─────────┐
                        3V3 ──┤         ├── VIN  <── +5V (From Power Bank)
                        GND ──┤         ├── GND  <── Common GND (Battery + LEDs + Buttons)
         (Show/Wake) GPIO 4 ──┤         ├── GPIO 13
                     GPIO 0 ──┤         ├── GPIO 12
                     GPIO 2 ──┤         ├── GPIO 14
                    GPIO 15 ──┤         ├── GPIO 27
                    GPIO 18 ──┤         ├── GPIO 26
                    GPIO 19 ──┤         ├── GPIO 25
                    GPIO 21 ──┤         ├── GPIO 33 ──> (Photo/Sleep) Button 2
                    GPIO 22 ──┤         ├── GPIO 32
                    GPIO 23 ──┤         ├── GPIO 35
                              └─────────┘
                                  │
                                GPIO 16 (Pin 8 right on 30-pin DevKit)
                                  │
                               [220Ω - 470Ω Resistor]
                                  │
                                  ▼
                            LED Data-In (DI)
```

| ESP32 Pin | Function | Wiring Connection | Electrical Configuration |
| :---: | :--- | :--- | :--- |
| **GPIO 16** | **LED Data Output** | In series with **220 Ω to 470 Ω resistor** $\rightarrow$ First LED Data-In (`DIN` / `DI`). | High-speed digital RMT / SPI output (FastLED driver). |
| **GPIO 4** | **Button 1 (Show Director / Wake)** | One pin to **GPIO 4**, other pin to **GND**. | Software `INPUT_PULLUP`. Reads `LOW` when pressed. |
| **GPIO 33** | **Button 2 (Castle Photo / Sleep)** | One pin to **GPIO 33**, other pin to **GND**. | Software `INPUT_PULLUP`. Reads `LOW` when pressed. |
| **GPIO 0** | **Onboard BOOT Button** | Onboard button on ESP32 DevKit (bench fallback). | Software `INPUT_PULLUP`. Operates in parallel with Button 1. |
| **GPIO 2** | **Status Indicator** | Built-in onboard blue LED. | Output: Pulses during show triggers, boot, and config. |
| **VIN / 5V** | **Primary DC Power Input** | +5V Red wire from USB Power Bank. | Powers ESP32 internal 3.3V LDO regulator and LEDs. |
| **GND** | **System Common Ground** | Connected together: ESP32 GND, Power Bank GND, LED GND, and both Button GNDs. | **Mandatory:** All components MUST share a common ground! |

---

## 3. System Electrical Schematic

```
               ┌────────────────────────────────────────────────────────┐
               │              PORTABLE USB POWER BANK                   │
               │                  (+5V DC, >= 2.1A)                     │
               └───────────────────┬────────────────┬───────────────────┘
                                   │ +5V (RED)      │ GND (BLACK)
                                   │                │
            ┌──────────────────────┴───────┐        │
            │                              │        │
            ▼                              ▼        │
    ┌──────────────┐              ┌───────────────┐ │
    │ ESP32 DevKit │              │  200-LED STRIP│ │
    │              │              │  POWER RAILS  │ │
    │   VIN / 5V ◄─┼──────────────┤ +5V           │ │
    │              │              │               │ │
    │        GND ◄─┼──────────────┼─ GND ◄────────┴─┼────────────────────────┐
    │              │              │               │                          │
    │    GPIO 16 ──┼─[220Ω-470Ω]─►│ DATA-IN (DI)  │                          │
    │              │              └───────────────┘                          │
    │              │                                                         │
    │     GPIO 4 ──┼───────┐                                                 │
    │ (Button 1)   │       │                                                 │
    │              │    ┌──┴──┐  Momentary Pushbutton                        │
    │              │    │ O O │  (Show Director / Wake)                      │
    │              │    └──┬──┘                                              │
    │              │       └─────────────────────────────────────────────────┤
    │              │                                                         │
    │    GPIO 33 ──┼───────┐                                                 │
    │ (Button 2)   │       │                                                 │
    │              │    ┌──┴──┐  Momentary Pushbutton                        │
    │              │    │ O O │  (Castle Photo / Sleep)                      │
    │              │    └──┬──┘                                              │
    │              │       └─────────────────────────────────────────────────┘
    └──────────────┘
```

---

## 4. 4-Pin Tactile Pushbutton Orientation Guide (Preventing Stuck Boots!)

> [!CAUTION]
> **Common Assembly Mistake:** Standard 6×6mm breadboard pushbuttons have **4 pins**, but only **2 electrical terminals**. The opposite pins along each wide side are permanently connected internally.

```
       CORRECT WIRING (Diagonal or True Opposites):
       
              Pin 1-A ┌──────┐ Pin 1-B  (Internally connected!)
                      │  ●   │
              Pin 2-A └──────┘ Pin 2-B  (Internally connected!)
              
       ✔ WIRE TO: Pin 1-A (GPIO) and Pin 2-A (GND)  <-- Switches when pressed!
       ❌ DO NOT WIRE TO: Pin 1-A and Pin 1-B       <-- Permanent short to GND!
```

* **The Problem:** If you wire across the internally shorted pair (e.g. Pin 1-A to GPIO and Pin 1-B to GND), the pin is held `LOW` permanently from the microsecond power is connected!
* **Firmware Protection Built-In:** The firmware contains a startup safety guard (`b1Armed` / `b2Armed`). If a pin is shorted to GND at boot, the firmware logs a warning and disables the hold timer rather than locking the costume in config mode.
* **Best Practice:** Use a multimeter in continuity mode (beep test) to verify that your two leads only beep when the button is physically clicked down! Clip or bend inward the two unused legs to prevent accidental shorts.

---

## 5. 200-LED Front & Back Topology & Daisy-Chaining

All firmware builds duplicate the front 100 chest LEDs to the back 100 LEDs in real time so the runner is illuminated from 360° along the dark Disney course:

```
  ESP32 GPIO 16 ──► [220Ω Resistor]
                          │
                          ▼
            ┌───────────────────────────┐
            │   FRONT CHEST STRAND      │
            │   LED 000 ────────► LED 099 │
            └─────────────┬─────────────┘
                          │ Data Out of LED 099
                          ▼
            ┌───────────────────────────┐
            │    BACK SHIRT STRAND      │
            │   LED 100 ────────► LED 199 │
            └───────────────────────────┘
```

### Power Injection Guidelines:
- **Voltage Drop:** Seed/pebble fairy light wire has thin conductors. Powering 200 LEDs from a single end can cause the last 30–50 LEDs to look slightly dim or reddish during white peaks.
- **T-Tap Power Bus (Recommended):** Run the +5V and GND wires in parallel directly from the battery harness to **BOTH** the start of the front strip (LED 0) and the start of the back strip (LED 100). The data line remains continuous in series (GPIO 16 $\rightarrow$ LED 0..99 $\rightarrow$ LED 100..199).

---

## 6. Bench Power Isolation Rules (Mandatory Computer Safety!)

> [!IMPORTANT]
> When uploading code or monitoring serial output via USB-C from a laptop or desktop computer:
> 1. **DISCONNECT THE BATTERY PACK:** Never plug a portable power bank into the VIN/5V rail while the ESP32 is also plugged into a computer via USB cable.
> 2. **Current Limiting:** Computer USB ports typically supply 500mA to 900mA. The ESP32 and a single test strand of LEDs will run fine for testing, but do not set full-white bursts on computer USB.
> 3. **Race Morning:** Plug only the 5V portable power bank into the costume harness. The ESP32 boots autonomously in ~1.5 seconds directly into Corral Standby Mode.

---

## 7. FastLED Power Budget & Battery Life Verification

The firmware enforces FastLED hardware power capping:
```cpp
FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000); // 5V, 2.0A max limit
```

* **Quiescent Draw:** ESP32 radio active + 200 LED sleep twinkle = **~120 mA** (~0.6W).
* **Parade Baseline Draw:** Animated float programs average **~620–780 mA** (~3.5W).
* **Peak Show Draw:** 30s synchronized fleet show peaks at **~1,100–1,200 mA** (~6.0W).
* **Battery Endurance (10,000 mAh / 37 Wh Power Bank):**
  - **Delivered 5V Capacity:** ~7,000 mAh (accounting for 70% boost conversion efficiency).
  - **90-minute Corral Sleep:** $1.5\text{ hr} \times 120\text{ mA} = 180\text{ mAh}$.
  - **90-minute 10K Race Run:** $1.5\text{ hr} \times 750\text{ mA} = 1,125\text{ mAh}$.
  - **Total Consumed:** ~1,305 mAh out of 7,000 mAh available (**> 80% battery remaining at the finish line!**).
