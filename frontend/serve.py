"""
Simple HTTP server for the frontend
Run this to serve the frontend files
"""
import http.server
import socketserver
import os

PORT = 5500

# Change to frontend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

# Add CORS headers
class CORSRequestHandler(Handler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    print(f"✓ Frontend server running at http://localhost:{PORT}")
    print(f"✓ Open http://localhost:{PORT} in your browser")
    print("\nPress Ctrl+C to stop the server")
    httpd.serve_forever()
