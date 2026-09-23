@echo off
setlocal enabledelayedexpansion
title Main Street Electrical Parade - One-Click ESP32 Flasher
color 0b

echo ======================================================================
echo    MAIN STREET ELECTRICAL PARADE - ONE-CLICK ESP32 FIRMWARE FLASHER
echo ======================================================================
echo.
echo  This script will automatically flash the latest compiled parade
echo  costume firmware to your connected ESP32 microcontroller.
echo.
echo  * No Arduino IDE or PlatformIO compilation required!
echo  * Pre-compiled ROM binaries in firmware/ folder are used.
echo.
echo ----------------------------------------------------------------------
echo  STEP 1: Connect your ESP32 to your computer using a USB data cable.
echo ----------------------------------------------------------------------
echo.
pause

echo.
echo [*] Checking for Python environment...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] Python not found in system PATH.
    echo.
    echo [*] Checking if PlatformIO is installed instead...
    pio --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [*] Found PlatformIO! Uploading firmware via PlatformIO...
        pio run -t upload
        goto :FINISHED
    )
    echo.
    echo ======================================================================
    echo  ERROR: Neither Python nor PlatformIO was detected.
    echo ======================================================================
    echo.
    echo  To flash your ESP32, you have two super-easy options:
    echo.
    echo  OPTION A (Easiest - Zero Install):
    echo    1. Open Google Chrome or Microsoft Edge.
    echo    2. Run 'python simulator.py' or start the web server.
    echo    3. Go to: http://localhost:8000/web_flasher.html
    echo    4. Click 'Install' and select your ESP32 COM port!
    echo.
    echo  OPTION B:
    echo    Install Python from https://www.python.org (Check 'Add to PATH').
    echo.
    pause
    exit /b 1
)

echo [*] Python detected! Checking for esptool...
python -c "import esptool" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Installing esptool flasher via pip (one-time setup)...
    python -m pip install esptool
    if %ERRORLEVEL% neq 0 (
        echo [!] Failed to install esptool. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo.
echo [*] Flashing firmware to connected ESP32...
echo     Bootloader: 0x1000  firmware/bootloader.bin
echo     Partitions: 0x8000  firmware/partitions.bin
echo     Firmware:   0x10000 firmware/firmware.bin
echo.
echo  [TIP] If it gets stuck on 'Connecting........_____.....',
echo        press and hold the 'BOOT' button on your ESP32 for 2 seconds!
echo.
echo ----------------------------------------------------------------------

python -m esptool --chip esp32 write_flash 0x1000 firmware/bootloader.bin 0x8000 firmware/partitions.bin 0x10000 firmware/firmware.bin

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo  SUCCESS! ESP32 FIRMWARE FLASH COMPLETED!
    echo ======================================================================
    echo.
    echo  1. Unplug the ESP32 from your computer.
    echo  2. Plug it into your 5V USB battery bank in your pocket.
    echo  3. Your WS2812B LED strand on GPIO 16 will now run the parade show!
    echo.
    echo  * HARDWARE BUTTON: Press the onboard BOOT button on the ESP32 to
    echo    toggle between your individual 90s show and Fleet Sync mode!
    echo.
) else (
    echo.
    echo ======================================================================
    echo  FLASH FAILED! (Error code: %ERRORLEVEL%)
    echo ======================================================================
    echo.
    echo  Troubleshooting tips:
    echo   1. Ensure your USB cable is a DATA cable, not just a charging cable.
    echo   2. Hold down the 'BOOT' button on the ESP32 while running this script.
    echo   3. Close any serial monitors or Arduino IDE windows that might be
    echo      locking the COM port.
    echo.
)

:FINISHED
echo.
pause
