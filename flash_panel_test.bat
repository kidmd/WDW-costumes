@echo off
setlocal
cd /d "%~dp0"
title MSEP - Universal Panel Test ESP32 Flasher (Warm White + Sparkles)

echo ======================================================================
echo    MSEP - UNIVERSAL PANEL TEST ESP32 FLASHER (WARM WHITE + SPARKLES)
echo ======================================================================
echo.
echo  This script will flash the universal bench-test firmware to your
echo  connected ESP32 microcontroller over USB.
echo.
echo  - Boots directly into 3%% Incandescent Warm White (~2500K vintage filament glow)
echo  - 0.5%% Starlight Sparkles (~3x pop over warm white base)
echo  - Illuminates ALL connected LEDs (up to 562 LEDs: Dual 16x16 Matrices [512] + 50 Fairy Lights)
echo  - No button clicks, float pairing, or graphic masks required!
echo.
echo ----------------------------------------------------------------------
echo  STEP 1: Connect your ESP32 to your computer using a USB data cable.
echo ----------------------------------------------------------------------
echo.
pause

echo.
echo [*] Checking for Python environment...

set "PYTHON_EXE="
python --version >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=python"

if "%PYTHON_EXE%"=="" (
    py --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=py"
)

if not "%PYTHON_EXE%"=="" goto :PYTHON_FOUND

echo [!] Python was not found in system PATH.
echo [*] Checking if PlatformIO is installed instead...
pio --version >nul 2>&1
if not errorlevel 1 (
    echo [*] Found PlatformIO. Uploading panel test firmware via PlatformIO...
    pio run -e panel_test -t upload
    goto :END
)

echo.
echo ======================================================================
echo  ERROR: Neither Python nor PlatformIO was detected.
echo ======================================================================
echo.
echo  To flash your ESP32, you have two easy options:
echo.
echo  OPTION A - Zero Install Web Flasher:
echo    1. Open Google Chrome or Microsoft Edge.
echo    2. Go to: http://localhost:8000/web_flasher.html
echo    3. Click the 'Panel & Bench Test' card and click Connect.
echo.
echo  OPTION B:
echo    Install Python from https://www.python.org and check Add to PATH.
echo.
goto :END

:PYTHON_FOUND
echo [*] Python detected: %PYTHON_EXE%
echo [*] Checking for esptool...

%PYTHON_EXE% -c "import esptool" >nul 2>&1
if not errorlevel 1 goto :ESPTOOL_READY

echo [*] Installing esptool flasher via pip - one-time setup...
%PYTHON_EXE% -m pip install esptool
if errorlevel 1 (
    echo [!] Failed to install esptool. Please check your internet connection.
    goto :END
)

:ESPTOOL_READY
echo.
echo [*] Flashing Panel Test Firmware to connected ESP32...
echo     Bootloader: 0x1000  firmware/bootloader.bin
echo     Partitions: 0x8000  firmware/partitions.bin
echo     Firmware:   0x10000 firmware/firmware_panel_test.bin
echo.
echo  TIP: If it gets stuck on 'Connecting........_____.....',
echo       press and hold the BOOT button on your ESP32 for 2 seconds.
echo.
echo ----------------------------------------------------------------------

%PYTHON_EXE% -m esptool --chip esp32 write-flash 0x1000 firmware/bootloader.bin 0x8000 firmware/partitions.bin 0x10000 firmware/firmware_panel_test.bin

if errorlevel 1 goto :FLASH_FAILED

echo.
echo ======================================================================
echo  SUCCESS! PANEL TEST FIRMWARE FLASH COMPLETED!
echo ======================================================================
echo.
echo  1. Unplug the ESP32 from your computer.
echo  2. Connect your 16x16 Armor Plate or LED string to GPIO 16, 5V, and GND.
echo  3. Power on: all LEDs will immediately glow warm white with sparkles!
echo.
echo  BENCH CONTROLS (OPTIONAL):
echo  - BOOT / Button 1 (GPIO 4/0): Tap to toggle Color Order (GRB <-> RGB).
echo  - Button 2 (GPIO 33): Tap to cycle (Sparkle -> Solid Warm -> RGB Test).
echo.
goto :END

:FLASH_FAILED
echo.
echo ======================================================================
echo  FLASH FAILED!
echo ======================================================================
echo.
echo  Troubleshooting tips:
echo   1. Ensure your USB cable is a DATA cable, not just a charging cable.
echo   2. Hold down the BOOT button on the ESP32 while running this script.
echo   3. Close any serial monitors or Arduino IDE windows that might be
echo      locking the COM port.
echo.

:END
pause
