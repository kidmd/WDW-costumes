#!/usr/bin/env python3
"""
Main Street Electrical Parade - LED Costume Simulator & Visualizer
Serves the interactive web interface locally and manages costume preset files.
"""

import http.server
import socketserver
import os
import sys
import json
import webbrowser
import threading
import urllib.parse
import socket

# UDP Pixel Streaming Socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
except Exception as e:
    print(f"[WARN] Could not enable SO_BROADCAST on UDP socket: {e}")
UDP_STREAM_PORT = 4210

DEFAULT_PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIMULATOR_DIR = os.path.join(BASE_DIR, "simulator")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")

# Ensure presets directory exists
os.makedirs(PRESETS_DIR, exist_ok=True)

class SimulatorRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SIMULATOR_DIR, **kwargs)

    def log_message(self, format, *args):
        # Keep console output concise
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/presets":
            self.handle_list_presets()
        elif parsed.path == "/api/serial_status":
            self.handle_serial_status()
        elif parsed.path == "/api/wifi_config":
            self.handle_get_wifi_config()
        elif parsed.path.startswith("/api/preset/"):
            filename = urllib.parse.unquote(parsed.path[len("/api/preset/"):])
            self.handle_get_preset(filename)
        elif parsed.path.startswith("/firmware/"):
            rel_path = parsed.path[len("/firmware/"):]
            firmware_file = os.path.join(BASE_DIR, "firmware", rel_path)
            if os.path.exists(firmware_file) and os.path.isfile(firmware_file):
                self.send_response(200)
                if firmware_file.endswith(".bin"):
                    self.send_header("Content-Type", "application/octet-stream")
                elif firmware_file.endswith(".json"):
                    self.send_header("Content-Type", "application/json")
                else:
                    self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(os.path.getsize(firmware_file)))
                self.end_headers()
                with open(firmware_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Firmware file not found")
                return
        elif parsed.path == "/SIMULATOR_USER_GUIDE.md":
            guide_path = os.path.join(BASE_DIR, "SIMULATOR_USER_GUIDE.md")
            if os.path.exists(guide_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Content-Length", str(os.path.getsize(guide_path)))
                self.end_headers()
                with open(guide_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Guide not found")
                return
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/save_preset":
            self.handle_save_preset()
        elif parsed.path == "/api/flash_firmware":
            self.handle_flash_firmware()
        elif parsed.path == "/api/stream_pixels":
            self.handle_stream_pixels()
        elif parsed.path == "/api/save_wifi":
            self.handle_save_wifi()
        elif parsed.path == "/api/flash_wifi_receiver":
            self.handle_flash_wifi_receiver()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_list_presets(self):
        try:
            files = [f for f in os.listdir(PRESETS_DIR) if f.endswith(".json")]
            presets = []
            for f in files:
                filepath = os.path.join(PRESETS_DIR, f)
                try:
                    with open(filepath, "r", encoding="utf-8") as pf:
                        data = json.load(pf)
                        presets.append({
                            "filename": f,
                            "name": data.get("name", f.replace(".json", "")),
                            "floatName": data.get("floatName", "Custom Float"),
                            "ledCount": len(data.get("leds", []))
                        })
                except Exception:
                    presets.append({"filename": f, "name": f.replace(".json", "")})

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(presets).encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_preset(self, filename):
        safe_name = os.path.basename(filename)
        filepath = os.path.join(PRESETS_DIR, safe_name)
        if not os.path.exists(filepath):
            self.send_error(404, "Preset not found")
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def handle_save_preset(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            preset_data = json.loads(post_data.decode("utf-8"))
            
            raw_name = preset_data.get("name", "untitled_preset")
            # Sanitize filename
            safe_name = "".join(c for c in raw_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            safe_name = safe_name.replace(" ", "_").lower() + ".json"
            
            filepath = os.path.join(PRESETS_DIR, safe_name)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(preset_data, f, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "filename": safe_name}).encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def handle_serial_status(self):
        try:
            port = get_connected_esp32_port()
            all_ports = []
            try:
                import serial.tools.list_ports
                all_ports = [{"device": p.device, "description": p.description} for p in serial.tools.list_ports.comports()]
            except Exception:
                pass

            ready = False
            error_msg = None
            if port:
                try:
                    import serial
                    s = serial.Serial(port, 115200, timeout=0.1)
                    s.close()
                    ready = True
                except Exception as ex:
                    ready = False
                    error_msg = str(ex)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "connected": bool(port),
                "ready": ready,
                "port": port,
                "error": error_msg,
                "all_ports": all_ports
            }).encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def handle_flash_firmware(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            
            num_front = int(payload.get("numLeds", 100))
            num_back = num_front
            total_leds = num_front + num_back  # 200 LEDs (100 front + 100 back duplicated)
            pattern_str = payload.get("pattern", "steady_sparkle")
            speed_bpm = int(payload.get("speedBpm", 120))
            sparkle_rate = float(payload.get("sparkleRate", 1.5))
            green_hue = int(payload.get("greenHue", 140))
            brightness_pct = int(payload.get("brightness", 80))
            fastled_brightness = max(30, min(85, int(brightness_pct * 85 / 100)))
            palette = payload.get("palette", [])
            
            pattern_map = {
                "steady_sparkle": "COSTUME_PATTERN_STEADY_SPARKLE",
                "breathing_glow": "COSTUME_PATTERN_BREATHING_GLOW",
                "fire_breath": "COSTUME_PATTERN_FIRE_BREATH",
                "traveling_wave": "COSTUME_PATTERN_TRAVELING_WAVE",
                "marquee": "COSTUME_PATTERN_MARQUEE",
                "photo_mode": "COSTUME_PATTERN_PHOTO_MODE",
                "fireworks": "COSTUME_PATTERN_FIREWORKS"
            }
            active_pattern = pattern_map.get(pattern_str, "COSTUME_PATTERN_STEADY_SPARKLE")
            
            palette_lines = []
            # 1. Front LEDs (0 to num_front - 1)
            for i in range(num_front):
                if i < len(palette) and palette[i]:
                    c = palette[i]
                    r = int(c.get("r", 15))
                    g = int(c.get("g", 255))
                    b = int(c.get("b", 35))
                else:
                    r, g, b = (15, 255, 35)
                palette_lines.append(f"    CRGB({r}, {g}, {b}), // Front LED {i}")

            # 2. Back LEDs (num_front to total_leds - 1, duplicate of front)
            for i in range(num_back):
                if i < len(palette) and palette[i]:
                    c = palette[i]
                    r = int(c.get("r", 15))
                    g = int(c.get("g", 255))
                    b = int(c.get("b", 35))
                else:
                    r, g, b = (15, 255, 35)
                comma = "," if i < num_back - 1 else ""
                palette_lines.append(f"    CRGB({r}, {g}, {b}){comma} // Back LED {num_front + i} (Duplicate of {i})")
            
            palette_code = "\n".join(palette_lines)
            
            header_content = f"""#ifndef COSTUME_CONFIG_H
#define COSTUME_CONFIG_H

#include <Arduino.h>
#include <FastLED.h>

// Automatically generated by MSEP Simulator (200 LEDs: 100 Front + 100 Back)
#define NUM_LEDS {total_leds}
#define FRONT_LEDS {num_front}
#define BACK_LEDS {num_back}
#define DUPLICATE_FRONT_TO_BACK 1

#define COSTUME_PATTERN_STEADY_SPARKLE   0
#define COSTUME_PATTERN_BREATHING_GLOW   1
#define COSTUME_PATTERN_FIRE_BREATH      2
#define COSTUME_PATTERN_TRAVELING_WAVE   3
#define COSTUME_PATTERN_MARQUEE          4
#define COSTUME_PATTERN_PHOTO_MODE       5

#define ACTIVE_COSTUME_PATTERN           {active_pattern}
#define COSTUME_SPEED_BPM                {speed_bpm}
#define COSTUME_SPARKLE_RATE             {sparkle_rate}
#define COSTUME_GREEN_HUE                {green_hue}
#define COSTUME_BRIGHTNESS               {fastled_brightness}
#define COLOR_ORDER                      RGB
#define HAS_CUSTOM_PALETTE               1
#define COSTUME_OVERRIDE_STANDALONE      1

// Artwork Sampled Color Palette (PROGMEM Flash Storage)
const CRGB PROGMEM ARTWORK_PALETTE[NUM_LEDS] = {{
{palette_code}
}};

#endif // COSTUME_CONFIG_H
"""
            include_dir = os.path.join(BASE_DIR, "include")
            os.makedirs(include_dir, exist_ok=True)
            config_path = os.path.join(include_dir, "costume_config.h")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(header_content)

            # Touch src/main.cpp to force PlatformIO to recompile with new header
            try:
                main_cpp_path = os.path.join(BASE_DIR, "src", "main.cpp")
                os.utime(main_cpp_path, None)
            except Exception:
                pass

            port = get_connected_esp32_port()
            if not port:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "No ESP32 detected on USB serial ports. Please connect your ESP32 with a USB cable and try again."
                }).encode("utf-8"))
                return

            import subprocess
            cmd = [sys.executable, "-m", "platformio", "run", "-t", "upload", "--upload-port", port]
            proc = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            stdout, _ = proc.communicate(timeout=120)
            success = (proc.returncode == 0)
            user_error = None
            if not success:
                if "not functioning" in stdout or "Error 31" in stdout or "PermissionError(13" in stdout:
                    user_error = f"USB Port {port} is unresponsive (Windows Error 31). Please UNPLUG the USB cable from the ESP32, wait 2 seconds, and plug it back in. Then click Flash again."
                elif "Wrong boot mode detected" in stdout or "needs to be in download mode" in stdout:
                    user_error = "ESP32 did not enter bootloader mode automatically. Hold down the BOOT button on your ESP32 board, click Flash again, and release BOOT once writing begins."
                elif "could not open port" in stdout or "PermissionError" in stdout or "Access is denied" in stdout:
                    user_error = f"Serial port {port} is busy or locked by another program (e.g. Serial Monitor). Close other apps using this COM port and try again."
                else:
                    user_error = f"PlatformIO upload failed with exit code {proc.returncode}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": success,
                "port": port,
                "log": stdout,
                "error": user_error
            }).encode("utf-8"))
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode("utf-8"))

    def handle_stream_pixels(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            pixels = payload.get("pixels", [])
            target_ip = payload.get("targetIp", "255.255.255.255")
            if not target_ip or not target_ip.strip():
                target_ip = "255.255.255.255"

            # Frame Protocol: 'MSEP' (4 bytes), opcode 0x01 (live frame), num_leds (2 bytes big-endian)
            num_leds = len(pixels)
            header = b'MSEP' + bytes([0x01]) + num_leds.to_bytes(2, 'big')
            raw = bytearray(header)
            for p in pixels:
                raw.append(max(0, min(255, int(p.get("r", 0)))))
                raw.append(max(0, min(255, int(p.get("g", 0)))))
                raw.append(max(0, min(255, int(p.get("b", 0)))))

            udp_socket.sendto(bytes(raw), (target_ip, UDP_STREAM_PORT))

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "count": num_leds,
                "bytes": len(raw),
                "targetIp": target_ip
            }).encode("utf-8"))
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode("utf-8"))

    def handle_get_wifi_config(self):
        try:
            wifi_file = os.path.join(PRESETS_DIR, "wifi_settings.json")
            config = {
                "ssid": "",
                "password": "",
                "targetIp": "255.255.255.255"
            }
            if os.path.exists(wifi_file):
                with open(wifi_file, "r", encoding="utf-8") as f:
                    config.update(json.load(f))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def handle_save_wifi(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            ssid = payload.get("ssid", "").strip()
            password = payload.get("password", "").strip()
            target_ip = payload.get("targetIp", "255.255.255.255").strip()

            wifi_file = os.path.join(PRESETS_DIR, "wifi_settings.json")
            with open(wifi_file, "w", encoding="utf-8") as f:
                json.dump({"ssid": ssid, "password": password, "targetIp": target_ip}, f, indent=2)

            header_content = f"""#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <Arduino.h>

#define WIFI_SSID       "{ssid if ssid else 'YourWiFiNetwork'}"
#define WIFI_PASSWORD   "{password}"
#define UDP_STREAM_PORT 4210
#define AP_SSID         "MSEP-Costume-AP"
#define AP_PASSWORD     "msep1234"

#define MSEP_MAGIC_0    'M'
#define MSEP_MAGIC_1    'S'
#define MSEP_MAGIC_2    'E'
#define MSEP_MAGIC_3    'P'
#define MSEP_OPCODE_LIVE_FRAME  0x01
#define MSEP_OPCODE_HEARTBEAT   0x02

#endif // WIFI_CONFIG_H
"""
            include_dir = os.path.join(BASE_DIR, "include")
            os.makedirs(include_dir, exist_ok=True)
            with open(os.path.join(include_dir, "wifi_config.h"), "w", encoding="utf-8") as f:
                f.write(header_content)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

    def handle_flash_wifi_receiver(self):
        try:
            include_dir = os.path.join(BASE_DIR, "include")
            os.makedirs(include_dir, exist_ok=True)
            costume_path = os.path.join(include_dir, "costume_config.h")
            
            with open(costume_path, "w", encoding="utf-8") as f:
                f.write("""#ifndef COSTUME_CONFIG_H
#define COSTUME_CONFIG_H

#define ENABLE_WIFI_LIVE_STREAM 1
#define COLOR_ORDER RGB

#endif
""")
            try:
                main_cpp = os.path.join(BASE_DIR, "src", "main.cpp")
                os.utime(main_cpp, None)
            except Exception:
                pass

            port = get_connected_esp32_port()
            if not port:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "No ESP32 detected on USB serial ports. Please connect your ESP32 with a USB cable and try again."
                }).encode("utf-8"))
                return

            import subprocess
            cmd = [sys.executable, "-m", "platformio", "run", "-t", "upload", "--upload-port", port]
            proc = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            stdout, _ = proc.communicate(timeout=120)
            success = (proc.returncode == 0)
            user_error = None
            if not success:
                if "not functioning" in stdout or "Error 31" in stdout or "PermissionError(13" in stdout:
                    user_error = f"USB Port {port} is unresponsive (Windows Error 31). Please UNPLUG the USB cable from the ESP32, wait 2 seconds, and plug it back in. Then click Flash again."
                elif "Wrong boot mode detected" in stdout or "needs to be in download mode" in stdout:
                    user_error = "ESP32 did not enter bootloader mode automatically. Hold down the BOOT button on your ESP32 board, click Flash again, and release BOOT once writing begins."
                elif "could not open port" in stdout or "PermissionError" in stdout or "Access is denied" in stdout:
                    user_error = f"Serial port {port} is busy or locked by another program. Close other apps using this COM port and try again."
                else:
                    user_error = f"PlatformIO upload failed with exit code {proc.returncode}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": success,
                "port": port,
                "log": stdout,
                "error": user_error
            }).encode("utf-8"))
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode("utf-8"))

def get_connected_esp32_port():
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        # Priority 1: Known USB-to-UART bridge chips (CP210x, CH340, FTDI, USB Serial)
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            if any(k in desc or k in hwid for k in ["cp210", "ch340", "ch341", "ftdi", "usb serial", "uart", "10c4:ea60", "1a86:7523"]):
                return p.device
        # Priority 2: Any device with USB in HWID
        for p in ports:
            if "usb" in (p.hwid or "").lower():
                return p.device
        # Priority 3: COM5 fallback if connected
        for p in ports:
            if p.device.upper() == "COM5":
                return p.device
    except Exception as e:
        print(f"[WARN] Error listing serial ports: {e}")
    return None

def find_available_port(start_port):
    import socket
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
        port += 1
    return start_port

def run_server(port, open_browser=True):
    actual_port = find_available_port(port)
    server_address = ('', actual_port)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, SimulatorRequestHandler) as httpd:
        url = f"http://localhost:{actual_port}"
        print("=" * 65)
        print("  MAIN STREET ELECTRICAL PARADE - LED SIMULATOR & PRESET MANAGER")
        print("=" * 65)
        print(f"[INFO] Server running at: {url}")
        print(f"[INFO] Presets directory: {PRESETS_DIR}")
        print("[INFO] Single Shirt Focus: Pete's Dragon (50 Addressable LEDs)")
        print("[INFO] 7-Shirt Fleet Lineup with Natural Proportions")
        print("[INFO] Press Ctrl+C in this terminal to stop the server.")
        print("=" * 65)

        if open_browser:
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Simulator server stopped cleanly.")
            httpd.server_close()

if __name__ == '__main__':
    if '--test' in sys.argv:
        test_port = find_available_port(8060)
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(('', test_port), SimulatorRequestHandler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        print(f"[TEST] Server started on port {test_port}")
        
        import urllib.request
        try:
            res = urllib.request.urlopen(f"http://localhost:{test_port}/api/presets", timeout=3)
            assert res.getcode() == 200
            print("[TEST] SUCCESS: API /api/presets endpoint verified!")
            httpd.shutdown()
            httpd.server_close()
            sys.exit(0)
        except Exception as e:
            print(f"[TEST] FAILED: {e}")
            httpd.shutdown()
            httpd.server_close()
            sys.exit(1)

    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else DEFAULT_PORT
    run_server(port, open_browser=True)
