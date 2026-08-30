import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def translate_path(self, path):
        # Serve index.html as index
        if path == '/' or path == '/index.html':
            return os.path.join(DIRECTORY, 'index.html')
        return super().translate_path(path)

os.chdir(DIRECTORY)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"=====================================")
    print(f" PrivacyHub Server running!")
    print(f"=====================================")
    print(f" LOCAL:     http://127.0.0.1:{PORT}")
    print(f" LOCAL:     http://privacyhub.local:{PORT}")
    print(f" EXTERNAL:  http://90.157.49.113:{PORT}")
    print(f"=====================================")
    print(f" Press Ctrl+C to stop")
    print(f"=====================================")
    httpd.serve_forever()
