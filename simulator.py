#!/usr/bin/env python3
"""
Main Street Electrical Parade - LED Costume Simulator & Visualizer
Serves the interactive web interface locally using Python standard library.
"""

import http.server
import socketserver
import os
import sys
import webbrowser
import threading
import time

DEFAULT_PORT = 8000
SIMULATOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulator")

class SimulatorRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SIMULATOR_DIR, **kwargs)

    def log_message(self, format, *args):
        # Quiet log to keep terminal clean
        pass

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

    # Enable socket reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, SimulatorRequestHandler) as httpd:
        url = f"http://localhost:{actual_port}"
        print("=" * 65)
        print("  MAIN STREET ELECTRICAL PARADE - LED SIMULATOR & VISUALIZER")
        print("=" * 65)
        print(f"[INFO] Server running at: {url}")
        print("[INFO] Single Shirt Focus: Pete's Dragon (50 Addressable LEDs)")
        print("[INFO] 7-Shirt Fleet Lineup with Traveling Wave preview")
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
    # Test flag for automated environment verification
    if '--test' in sys.argv:
        test_port = find_available_port(8050)
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(('', test_port), SimulatorRequestHandler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        print(f"[TEST] Server started on port {test_port}")
        
        # Test HTTP request
        import urllib.request
        try:
            res = urllib.request.urlopen(f"http://localhost:{test_port}/index.html", timeout=3)
            status = res.getcode()
            content = res.read().decode('utf-8')
            assert status == 200
            assert "Costume LED Visualizer" in content
            print("[TEST] SUCCESS: HTTP 200 and index.html content verified!")
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
