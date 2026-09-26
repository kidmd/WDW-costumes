# ⚡ Quick Flashing Guide for the Brothers
### How to flash your ESP32 with the latest parade costume firmware in under 60 seconds

Hey guys! If you just want to flash your ESP32 board without learning Git, Google Antigravity, or dealing with complex toolchains, this guide gives you **3 easy ways to do it**.

---

## 📥 Step 0: Download the Files (No Git or GitHub Account Needed!)

You **do not need Git installed** and you **do not need to make a repository** on your computer. You can download everything as a standard `.zip`:

1. Go to the project page: **[https://github.com/kidmd/WDW-costumes](https://github.com/kidmd/WDW-costumes)**
2. Click the green **`<> Code`** button (near the top-right) and click **`Download ZIP`**.
3. Right-click the downloaded `WDW-costumes-main.zip` file and select **`Extract All...`** (extract to any folder, like your Desktop or Downloads).
4. Plug in your ESP32 with a USB data cable, open the extracted folder, and choose your preferred flashing method below!

---

## 🚀 Method 1: The One-Click Double-Click Script (Fastest & Recommended)

No compiling, no Arduino IDE, no software configuration needed! We already pre-compiled the latest ROM binaries into the `firmware/` folder.

### On Windows:
1. Connect your ESP32 to your computer using a USB data cable.
2. Double-click **`flash_firmware.bat`** in the main project folder.
3. Press any key when prompted.
4. The script will automatically detect your ESP32 and flash the firmware in ~15 seconds.

### On Mac / Linux:
1. Connect your ESP32 via USB.
2. Double-click **`flash_firmware.command`** *(or run `./flash_firmware.command` in Terminal)*.
3. Press Enter and it flashes automatically.

> 💡 **Tip:** If the terminal says `Connecting........_____.....`, **press and hold the onboard "BOOT" button on the ESP32 for 2 seconds** until it starts writing!

---

## 🌐 Method 2: Zero-Install Web Browser Flasher (Chrome or Edge)

You can flash the ESP32 directly from your web browser using HTML5 Web Serial — **zero software or drivers to install**! You can even pick which specific runner float role you want to bake into the board:

1. Connect your ESP32 to your computer via a USB data cable.
2. Open **Google Chrome** or **Microsoft Edge**.
3. With the simulator running (`python simulator.py`), go to:
   ```
   http://localhost:8000/web_flasher.html
   ```
   *(Or click the green **"⚡ Web Flasher"** link in the top-right header of the Costume Simulator).*
4. Click on your assigned **Float Card** (e.g. 🚂 **Float 1: The Train**, 🥁 **Float 2: The Title Drum**, 🐉 **Float 6: Pete's Dragon**, etc.).
   - The flasher will automatically arm the dedicated firmware image for that character and role!
5. Click the green **"⚡ Connect & Flash Float X"** button.
6. In the browser pop-up window, select your ESP32 port (usually labeled *CP2102*, *CH340*, or *USB Serial*) and click **Connect**.
7. Click **Install** and watch the progress bar reach 100%! The board automatically reboots with that float's identity pre-configured in flash memory.

---

## 🛠️ Method 3: Arduino IDE (If You Want to Edit the Code)

If you're already familiar with the Arduino IDE and want to inspect or modify the code:

1. Open the Arduino sketch located at:
   ```
   arduino/MSEP_Costume/MSEP_Costume.ino
   ```
2. **Install FastLED Library:**
   - In Arduino IDE, click **Sketch ➔ Include Library ➔ Manage Libraries...**
   - Search for `FastLED` (by Daniel Garcia) and click **Install**.
3. **Select Board:**
   - Go to **Tools ➔ Board ➔ esp32 ➔ ESP32 Dev Module**.
   *(If you don't have the ESP32 board package installed, go to Tools ➔ Board ➔ Boards Manager, search for `esp32` by Espressif, and click Install. The sketch automatically detects and supports **both ESP32 Arduino Core 2.x and Core 3.x+** without code changes).*
4. **Select Port & Upload:**
   - Go to **Tools ➔ Port** and select your connected ESP32 COM port.
   - Click the **Upload** arrow button in the top toolbar!

---

## 💻 Method 4: PlatformIO / VS Code (For Developers)

If you have VS Code with the PlatformIO extension:
1. Open this project folder in VS Code.
2. Connect your ESP32.
3. Open a terminal and run:
   ```bash
   pio run -t upload
   ```

---

## 🔌 Hardware & Costume Operation Guide

Once your board is flashed:

### Pinout Connections:
- **LED Data In (DIN):** Connects to **GPIO 16** (8th pin down on the right of most ESP32 DevKits).
- **LED String Configuration:** Pre-configured for **200 LEDs** (100 Front + 100 Back duplicated) for full 360° visibility and battery life testing.
- **Power:** Connect a 5V USB battery bank (2.1A+ rated) to the ESP32's micro-USB / USB-C port or `5V` and `GND` pins (firmware is limited to 2000 mA for safety).
- **Data Resistor:** A 220 Ω to 470 Ω resistor on the data wire between GPIO 16 and LED DIN is recommended.

### How to Use the Shirt:
- **Autonomous Float Program (Baseline Default):** 
  When you power on your ESP32 with your battery bank, the costume runs its complete independent float sequence (custom artwork colors, starlight sparkles, wheel spin chases, breathing glow, and electrical waves) across all 200 LEDs (100 front + 100 back).
- **One-Shot 30-Second Fleet Routine (Short Tap BOOT Button):**
  - **Start Fleet Show:** Tap the onboard **BOOT button (GPIO 0)** once (short tap between 50ms and 2.5s) to trigger the **30-Second Synchronized Fleet Routine** once. The ESP32 broadcasts a wireless ESP-NOW trigger packet (`0x30`) so all runner costumes initiate the 30-second routine simultaneously. After 30.0 seconds, all shirts automatically return to their individual float programs.
  - **Early Stop:** Tap the BOOT button while the 30-second routine is playing to stop it early. The ESP32 gives **2 Amber Flashes**, broadcasts a cancellation packet (`0x00`), and returns all costumes immediately to their baseline float programs.
  - **Debounce Protection:** Enforces 50ms hardware contact debounce and 300ms software lockout between button releases to prevent accidental double-triggers.
- **Float ID Selector (Long Hold BOOT Button for 3s):**
  Hold the BOOT button for 3 seconds to enter Float ID configuration mode (Floats 1 through 7, see below).

---

## 🎛️ Setting Your Float Number (1 to 7) & Role (Leader / Follower)

You do **not** need to change any code to configure which float you are! Any ESP32 can be set to any float in the parade lineup using the onboard **BOOT button (GPIO 0)**, and your board permanently remembers its number in flash memory even when powered off.

### How to Configure:
1. **Hold the BOOT button for 3 seconds:**
   - The LEDs will flash **white 3 times** to signal you have entered Configuration Mode.
2. **Read the Current Float Number:**
   - Look at the start of your LED strip: the first **N pixels** will light up in that float's signature color!
   - (If you don't have the LED strip plugged in, the onboard Blue LED blinks N times repeatedly).
3. **Tap the BOOT button to cycle:**
   - Each short tap advances to the next float: `1 ➔ 2 ➔ 3 ➔ 4 ➔ 5 ➔ 6 ➔ 7 ➔ 1`.
4. **Auto-Save & Exit:**
   - Once you reach your float, **leave the button alone for 4 seconds**.
   - The LEDs will flash **green 4 times** to confirm it is saved!

### The 7-Runner Fleet Lineup:

| Float # | Float Name | Character Tag | Signature Color | Role |
|:---:|---|---|---|:---:|
| **01** | **The Train** | CASEY JR. | 🔴 Red | **👑 LEADER** (Pulls the Drum & Broadcasts timing clock) |
| **02** | **The Title Drum** | THE DRUM | 🟡 Gold / Amber | Follower |
| **03** | **The Turtle** | SPINNING TURTLE | 🟢 Teal / Green | Follower |
| **04** | **The Snail** | SPINNING SNAIL | 🌸 Pink | Follower |
| **05** | **Cinderella's Coach** | CINDERELLA | 🔵 Cyan | Follower |
| **06** | **Pete's Dragon** | ELLIOTT | 🟢 Green | Follower |
| **07** | **To Honor America** | FLAG & EAGLE | 🔴⚪🔵 Patriotic Blue | Follower |

> 💡 **Fleet Leader Note:** Float 01 is the **Master Leader** that broadcasts the wireless sync clock. If you are running together as a group, one runner sets their shirt to **Float 01**, and everyone else picks Floats **02 through 07**. The synchronized traveling wave will then roll down the line in order: `01 ➔ 02 ➔ 03 ➔ 04 ➔ 05 ➔ 06 ➔ 07`!

## ❓ Troubleshooting

| Issue | Quick Fix |
|---|---|
| **Board not detected / no COM port** | 1. Ensure your cable is a **USB data cable** (many cheap phone cables only carry power, not data).<br>2. Install the standard USB-to-UART driver for your chip ([CP210x Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) or [CH340 Driver](https://sparks.gogo.co.nz/ch340.html)). |
| **Flashing gets stuck on "Connecting..."** | Press and hold the **BOOT button** on the ESP32 board for 2 seconds while the script is connecting, then release it. |
| **LEDs stay dark after flashing** | Verify LED strand direction (data must flow from the ESP32 into the arrow/input end of the WS2812B string, not the output end). |
| **Colors look swapped (e.g. green instead of red)** | WS2812B strands use `RGB` or `GRB` color order. The firmware is calibrated for `RGB` by default. |

---
*Questions or need a different float preset? Check `SIMULATOR_USER_GUIDE.md` or ask!*
