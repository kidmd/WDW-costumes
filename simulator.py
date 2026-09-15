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

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/presets":
            self.handle_list_presets()
        elif parsed.path.startswith("/api/preset/"):
            filename = urllib.parse.unquote(parsed.path[len("/api/preset/"):])
            self.handle_get_preset(filename)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/save_preset":
            self.handle_save_preset()
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
