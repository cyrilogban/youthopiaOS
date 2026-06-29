import threading
import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Always return a 200 OK success status
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        # Send the same JSON response as your old code
        response = {"status": "Theo is alive and running!"}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_HEAD(self):
        # UptimeRobot sends HEAD requests by default. We must reply 200 OK.
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    # This prevents the server from spamming your terminal logs on every ping
    def log_message(self, format, *args):
        pass

def run_server():
    # Render assigns a port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    # Start the server on all interfaces (0.0.0.0)
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def keep_alive():
    """Starts a background web server to trick Render into thinking this is a Web Service."""
    server_thread = threading.Thread(target=run_server)
    # Daemon thread ensures it closes when the main bot process stops
    server_thread.daemon = True
    server_thread.start()
