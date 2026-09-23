# 🏰 Antigravity Assistant Rules for WDW Costumes

These rules govern the assistant's behavior, coding standards, and documentation maintenance for the **Main Street Electrical Parade (WDW 10K) Synchronized LED Costumes** project.

---

## 1. Continuous Documentation Synchronization (Mandatory)

Whenever any feature, UI control, slider, preset, firmware parameter, or hardware architecture is added, modified, or removed:

1. **`SIMULATOR_USER_GUIDE.md`**:
   - Immediately update the relevant sections (Canvas controls, Inspector, Animation Groups, Wiring Optimizer, Artwork Management, Race Bib overlay, Master Timeline, Parade Cue Director, Effects Library, Wi-Fi streaming, or USB flashing).
   - Keep Table of Contents and keyboard shortcuts cheat sheets synchronized.

2. **`PROJECT_PROGRESS.md`**:
   - Add a new timestamped entry at the top of the `## Progress Log` detailing:
     - Date of implementation.
     - Milestone / Feature name.
     - Technical implementation notes, architecture decisions, and hardware verification status.

3. **`README.md`**:
   - Ensure the Hardware Specifications (e.g., LED count, power limit, battery requirements), float roster, and simulator overview remain 100% accurate.

4. **`FLASHING_INSTRUCTIONS.md`**:
   - Keep pinouts (GPIO 16 Data, GPIO 0 BOOT button), LED strand configurations (200 LEDs: 100 Front + 100 Back), and flashing steps aligned across Windows, Mac, and browser Web Serial methods.

---

## 2. Hardware & Battery Safety Standards

1. **Current Limiting:**
   - Always enforce FastLED hardware power limiting in C++ firmware, Arduino sketches, and exported simulator code:
     ```cpp
     FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000); // 5V, 2.0A max for portable USB power banks
     ```
2. **200-LED Configuration:**
   - All firmware compilation and export routines must control **200 LEDs** (100 front chest pixels + 100 back pixels duplicated in real time) to ensure 360° visibility on race day and accurate battery life testing.
3. **Pinout Consistency:**
   - **LED Data Out:** GPIO 16 (with recommended 220 Ω to 470 Ω inline resistor).
   - **Mode / Float Selector Button:** GPIO 0 (onboard BOOT button) with internal pull-up and debouncing.
4. **Visual Mode Confirmations:**
   - Short tap (< 2.5s): 🔵 **2 Cyan Flashes** (Autonomous Show) vs. 🟡 **2 Amber Flashes** (ESP-NOW Fleet Sync).
   - Long hold (3s): ⚪ **3 White Flashes** (Config Mode), pixel counter, and 🟢 **4 Green Flashes** (Auto-Save to NVS flash).

---

## 3. Simulator Layout & Visual Geometry Rules

1. **Proportional Graphic Clearance:**
   - All chest graphics (Pete's Dragon, Cinderella's Coach, Carriage No Horses, or custom uploads) must be scaled to sit strictly in the chest area above the race bib (`y = 0.168` to `0.553`).
   - The graphic's original $x / y$ aspect ratio must be strictly preserved (`normW = normH * 1.25 * aspect`). Never stretch or squish artwork.
2. **runDisney 10K Race Bib (#1952) Overlay:**
   - Keep the authentic yellow Tyvek theme, official Chip 'n' Dale mascot illustrations, and 4-corner BibBoards snap fasteners intact for visual clearance verification.
   - Maintain the default bib height at **57%** and default scale at **100%**.

---

## 4. Git Commit & Repository Discipline

1. **Atomic Commits with Documentation:**
   - Always stage and commit code modifications and their accompanying documentation updates together.
2. **Descriptive Commit Messages:**
   - Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `refactor:`.
3. **Push to Remote:**
   - Always push commits to `origin main` to keep the GitHub repository ([kidmd/WDW-costumes](https://github.com/kidmd/WDW-costumes)) in sync.
