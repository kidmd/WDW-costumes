@echo off
setlocal
cd /d "%~dp0"
title Main Street Electrical Parade - One-Click ESP32 Flasher

echo ======================================================================
echo    MAIN STREET ELECTRICAL PARADE - ONE-CLICK ESP32 FIRMWARE FLASHER
echo ======================================================================
echo.
echo  This script will automatically flash the latest compiled parade
echo  costume firmware to your connected ESP32 microcontroller.
echo.
echo  - No Arduino IDE or PlatformIO compilation required.
echo  - Pre-compiled ROM binaries in firmware/ folder are used.
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
    echo [*] Found PlatformIO. Uploading firmware via PlatformIO...
    pio run -t upload
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
echo    3. Click Connect and select your ESP32 COM port.
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
echo [*] Flashing firmware to connected ESP32...
echo     Bootloader: 0x1000  firmware/bootloader.bin
echo     Partitions: 0x8000  firmware/partitions.bin
echo     Firmware:   0x10000 firmware/firmware.bin
echo.
echo  TIP: If it gets stuck on 'Connecting........_____.....',
echo       press and hold the BOOT button on your ESP32 for 2 seconds.
echo.
echo ----------------------------------------------------------------------

%PYTHON_EXE% -m esptool --chip esp32 write-flash 0x1000 firmware/bootloader.bin 0x8000 firmware/partitions.bin 0x10000 firmware/firmware.bin

if errorlevel 1 goto :FLASH_FAILED

echo.
echo ======================================================================
echo  SUCCESS! ESP32 FIRMWARE FLASH COMPLETED!
echo ======================================================================
echo.
echo  1. Unplug the ESP32 from your computer.
echo  2. Plug it into your 5V USB battery bank in your pocket.
echo  3. Your WS2812B LED strand on GPIO 16 will now run the parade show!
echo.
echo  HARDWARE BUTTON:
echo  - Tap BOOT button once to toggle between Standalone and Fleet Sync.
echo  - Hold BOOT button for 3 seconds to set your Float Number (1 to 7).
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
echo.
pause
