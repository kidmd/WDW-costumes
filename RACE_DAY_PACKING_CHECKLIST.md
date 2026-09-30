# 🏰 MSEP Synchronized LED Costumes — Race Day Packing Checklist & Field Manual
### Walt Disney World 10K — The 7-Runner Family Expedition
**Engineered with Imagineering Precision by the 3 Brothers | Worn by the 7 Family Runners**  
*(2 Brothers, 1 Sister, 1 Brother-in-Law, 3 Sisters-in-Law)*

---

## 🎯 Mission Overview & Event Parameters
* **Event:** runDisney Walt Disney World 10K (Theme: *Main Street Electrical Parade*)
* **Course Distance:** 6.2 Miles (10.0 Kilometers) through Epcot and Disney resort roadways
* **Race Fleet:** 7 Synchronized Floats (Floats 1 through 7, 200 LEDs each: 100 Front + 100 Back duplicated)
* **Wireless Sync:** Peer-to-Peer ESP-NOW (2.4 GHz connectionless radio, no cell service or router needed)
* **Power Standard:** 5V USB Power Bank per runner (FastLED hardware power limited to 2000 mA / 2.0A max)
* **Corral Call Time:** 03:30 AM in Epcot outer parking lot corrals (Sunrise ~07:15 AM; Race starts ~05:00 AM in staggered waves)

---

## 📋 The Master Packing Checklist

### 1. ⚡ Microcontrollers & Electronics (Pre-Flashed & Tested)
- [ ] **7 Primary ESP32 Boards (Floats 1 to 7):**
  - [ ] 🚂 **Float 1 (Leader - The Train / Casey Jr.):** MAC pre-configured or flashed via `manifest_float1.json`.
  - [ ] 🥁 **Float 2 (Follower - The Title Drum):** Flashed via `manifest_float2.json`.
  - [ ] 🐢 **Float 3 (Follower - The Spinning Turtle):** Flashed via `manifest_float3.json`.
  - [ ] 🐌 **Float 4 (Follower - The Spinning Snail):** Flashed via `manifest_float4.json`.
  - [ ] 🩵 **Float 5 (Follower - Cinderella's Coach):** Flashed via `manifest_float5.json`.
  - [ ] 🐉 **Float 6 (Follower - Pete's Dragon):** Flashed via `manifest_float6.json`.
  - [ ] 🦅 **Float 7 (Follower - To Honor America):** Flashed via `manifest_float7.json`.
- [ ] **3 Spare / Backup ESP32 Boards:**
  - [ ] 1 Dedicated Spare Leader Board (Float 1).
  - [ ] 2 Generic Boards (Auto / Hotel Boot Selectable by holding BOOT for 5 seconds).
- [ ] **Protection:** 10 Heavy-Duty Quart Ziploc Freezer Bags (encloses each ESP32 board and battery pack against Florida condensation, sweat, and rain).
- [ ] **USB Cables:**
  - [ ] 7 Short USB-A to USB-C (or micro-USB) 1 ft to 2 ft power cables (powers ESP32 from battery in waist belt).
  - [ ] 2 Spare short power cables.
  - [ ] 1 Long (6 ft) USB-C data cable for laptop hotel bench flashing if needed.

---

### 2. 🔋 Battery Packs & Power Management
- [ ] **7 Primary USB Power Banks:**
  - [ ] 10,000 mAh rating recommended (~7,000 mAh delivered @ 5V).
  - [ ] Minimum 2.1A / 5V output rating.
  - [ ] Verified to stay awake under dim loads (tested with 12% Corral Standby drawing ~120 mA).
  - [ ] 100% Fully Charged the night before by 9:00 PM.
- [ ] **2 Backup USB Power Banks (Fully Charged):** Kept in the gear-check or support bag.
- [ ] **Hotel Charging Hub:** Multi-port 6-port or 10-port USB wall charging station with enough cables to charge all 9 battery packs simultaneously overnight.

---

### 3. 👕 Wearables, Costumes & Rigging
- [ ] **7 Mesh Pinnie Vests:**
  - [ ] Multi-layer Cricut HTV graphics ironed on with $6\times 3\,\text{mm}$ pill slots weeded.
  - [ ] 200 WS2812B Seed/Pebble LEDs woven (100 front chest + 100 back duplicated).
  - [ ] Strain-relief zip tie or monofilament anchor where wire enters the vest.
- [ ] **7 Technical Base Running Shirts:** Matte black, moisture-wicking technical fabric worn underneath the pinnie.
- [ ] **7 Running Belts / Waist Pouches (e.g. FlipBelt or SPIbelt):** Holds the battery pack snug against the small of the back with zero bounce.
- [ ] **28 BibBoards Snap Fasteners or Safety Pins:** 4 per runner to mount official runDisney race bibs (#1952 style) strictly below the artwork ($y = 0.57$).
- [ ] **Anti-Friction & Comfort:**
  - [ ] Roll of gaffer tape or soft cloth adhesive tape (tapes down interior wire segments so bare wires don't rub against the runner's shirt).
  - [ ] Body Glide / Anti-chafe balm (applied around neck, underarms, and waist).

---

### 4. 🧰 The 3 Brothers' Hotel & Field Repair Toolkit
A compact zipper pouch packed in the luggage:
- [ ] **Soldering & Splicing:**
  - [ ] Portable USB-powered soldering iron (or solder-seal heat-shrink wire connectors + lighter).
  - [ ] Small spool of lead-free rosin core solder.
  - [ ] Wire strippers and precision flush-cut snips.
  - [ ] 220 Ω and 470 Ω inline resistors (5 spares).
- [ ] **Fasteners & Adhesives:**
  - [ ] Pack of 100 small (4-inch) clear zip ties.
  - [ ] Clear monofilament (fishing line) + 2 sewing needles for quick mesh tacking.
  - [ ] Roll of electrical tape + roll of heat shrink tubing.
  - [ ] Small bottle of fabric glue or Aleene's "OK to Wash It" glue.
- [ ] **Diagnostics:**
  - [ ] Digital multimeter or USB inline voltage/current meter (checks battery 5.0V rail and mA draw).
  - [ ] Laptop with simulator repo and Chrome browser with bookmarked Web Flasher:
    `https://kidmd.github.io/WDW-costumes/simulator/web_flasher.html`

---

### 5. 🌧️ Florida Pre-Dawn Weather Survival Kit
Central Florida in January pre-dawn hours can swing from 40°F damp chill to humid drizzle:
- [ ] **7 Clear Plastic Emergency Ponchos:** Clear plastic allows the 200 LEDs to shine brightly while keeping electronics 100% bone-dry during sudden rain.
- [ ] **Hand Warmers (7 pairs):** Keep fingers nimble while waiting in the corrals from 3:30 AM to 5:00 AM.
- [ ] **Throwaway Warm-up Sweatshirts/Layers:** Old Goodwill hoodies/sweats worn over the costumes in the corrals and tossed into donation bins right at the start line.
- [ ] **Sharpie & Labeling Tape:** For labeling which board and battery belongs to which runner.

---

## ⏱️ Race Day Chronological Countdown & Playbook

| Time | Stage | Action / Play |
| :---: | :--- | :--- |
| **02:30 AM** | **Hotel Wake-up** | Alarm sounds. Apply Body Glide. Put on black base shirts and pinnie vests. |
| **02:50 AM** | **Battery Bench Check** | Check power banks (all 4 LED bars lit = 100%). Insert battery into FlipBelts. Do NOT plug in USB yet. |
| **03:15 AM** | **Resort Bus / Drive** | Head to Epcot parking lot via official runDisney resort transportation. |
| **03:45 AM** | **Corral Entry** | Arrive in staging corral. Seal ESP32 inside Ziploc bag. **Plug USB cable into power bank.** |
| **03:46 AM** | **🌙 Corral Standby Verification** | Verify all 7 shirts boot into **🌙 Corral Standby Mode** (12% dim midnight starlight twinkle, <120mA draw). Costumes stay cool and save 80%+ battery. |
| **04:30 AM** | **⚡ 4-Second Attendance Roll Call** | **👑 Leader (Float 1 - Casey Jr.): Double-tap BOOT button (< 400ms).**<br>Confirm the rapid roll call wave rolls sequentially down the line (Floats 1 ➔ 7 illuminate solo for 500ms in signature color, ending in double emerald green flash). All 7 runners present! |
| **04:50 AM** | **Corral Chute Advance** | Chutes begin walking toward the start line. Discard throwaway warm-up hoodies into donation boxes. |
| **04:55 AM** | **☀️ Wake the Fleet** | **👑 Leader (Float 1): Single-tap BOOT button (< 600ms).**<br>Entire fleet wakes from Corral Standby into full-brightness autonomous float programs! |
| **05:00 AM** | **🚀 RACE START!** | Fireworks burst at the start line! The 7 floats run in parade order down the course. |
| **On Course** | **🎆 Theatrical Fleet Routine** | **👑 Leader (Float 1): Single-tap BOOT button anytime** to trigger the 30-Second Synchronized Fleet Routine (traveling waves, ripples, wig-wags, and grand finale) whenever passing Disney photographers or crowded cheer sections! |
| **Post-Race** | **🏁 Finish Line Photo & Power Down** | Cross the finish line at Epcot! Take fleet photos, then **triple-tap BOOT** (or unplug USB) to power down. Celebrate with Mickey waffles! |

---

## 🎛️ Emergency In-Corral Button Cheat Sheet

| Situation | Action on BOOT Button | Result |
| :--- | :--- | :--- |
| **Fleet is still in dim Standby at the start chute** | Leader (Float 1) **Single Tap** | Wakes ALL 7 floats to active parade brightness. |
| **Verify all 7 runners are powered & synced** | Leader (Float 1) **Double Tap** | Runs 4s rapid roll call wave (1➔7). |
| **Need to pause lights during a long delay** | Leader (Float 1) **Triple Tap** | Puts ALL 7 floats back into dim Standby (<120mA). |
| **A Follower board got reset to Float 2** | Hold BOOT for **$\ge$ 5 Seconds** | White charging meter $\rightarrow$ 3 white flashes $\rightarrow$ Tap to cycle float number (1–7) $\rightarrow$ 4 green flashes (Auto-Saves to flash). |

---

*Keep this manual in your travel gear bag or bookmarked on your phone for a seamless, stress-free race weekend! 🏰✨*
