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
        # Serve PrivacyHub-Web.html as index
        if path == '/' or path == '/index.html':
            return os.path.join(DIRECTORY, 'PrivacyHub-Web.html')
        return super().translate_path(path)

os.chdir(DIRECTORY)

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"=====================================")
    print(f" PrivacyHub Local Server running!")
    print(f"=====================================")
    print(f" Local:  http://127.0.0.1:{PORT}")
    print(f" Local:  http://localhost:{PORT}")
    print(f" Local:  http://privacyhub.local:{PORT}")
    print(f"=====================================")
    print(f" Press Ctrl+C to stop")
    print(f"=====================================")
    httpd.serve_forever()
