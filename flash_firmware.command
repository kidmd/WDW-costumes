#!/usr/bin/env bash
cd "$(dirname "$0")"

echo "======================================================================"
echo "   MAIN STREET ELECTRICAL PARADE - ONE-CLICK ESP32 FIRMWARE FLASHER"
echo "======================================================================"
echo ""
echo "This script flashes the latest compiled parade costume firmware to"
echo "your connected ESP32 microcontroller."
echo ""
echo "No Arduino IDE or PlatformIO compilation required!"
echo "Pre-compiled ROM binaries in firmware/ folder are used."
echo ""
echo "----------------------------------------------------------------------"
echo "STEP 1: Connect your ESP32 to your computer using a USB data cable."
echo "----------------------------------------------------------------------"
read -p "Press [Enter] to continue..."

# Find Python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "[!] Python is not installed."
        if command -v pio &> /dev/null; then
            echo "[*] Found PlatformIO! Uploading firmware via PlatformIO..."
            pio run -t upload
            exit 0
        fi
        echo "Please install Python 3 or use the Web Flasher in Chrome/Edge!"
        exit 1
    fi
fi

# Ensure esptool is installed
if ! $PYTHON_CMD -c "import esptool" &> /dev/null; then
    echo "[*] Installing esptool flasher via pip..."
    $PYTHON_CMD -m pip install esptool
fi

echo ""
echo "[*] Flashing firmware to connected ESP32..."
echo "    Bootloader: 0x1000  firmware/bootloader.bin"
echo "    Partitions: 0x8000  firmware/partitions.bin"
echo "    Firmware:   0x10000 firmware/firmware.bin"
echo ""
echo "[TIP] If it gets stuck on 'Connecting........_____.....',"
echo "      press and hold the 'BOOT' button on your ESP32 for 2 seconds!"
echo ""
echo "----------------------------------------------------------------------"

$PYTHON_CMD -m esptool --chip esp32 write_flash 0x1000 firmware/bootloader.bin 0x8000 firmware/partitions.bin 0x10000 firmware/firmware.bin

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo " SUCCESS! ESP32 FIRMWARE FLASH COMPLETED!"
    echo "======================================================================"
    echo ""
    echo "1. Unplug the ESP32 from your computer."
    echo "2. Plug it into your 5V USB battery bank in your pocket."
    echo "3. Your WS2812B LED strand on GPIO 16 will now run the parade show!"
    echo ""
    echo "* HARDWARE BUTTON: Press the onboard BOOT button on the ESP32 to"
    echo "  toggle between your individual 90s show and Fleet Sync mode!"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo " FLASH FAILED!"
    echo "======================================================================"
    echo "Troubleshooting:"
    echo " 1. Make sure your USB cable supports DATA, not just charging."
    echo " 2. Hold down the 'BOOT' button on the ESP32 while connecting."
fi

read -p "Press [Enter] to exit..."
