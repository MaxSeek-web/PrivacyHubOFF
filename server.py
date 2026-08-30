import http.server
import socketserver
import os
import json
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
ANALYTICS_FILE = os.path.join(DIR, "analytics.json")
PID_FILE = os.path.join(DIR, "server.pid")

# Ensure analytics file exists
if not os.path.exists(ANALYTICS_FILE):
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump({"events": []}, f, ensure_ascii=False)

def load_analytics():
    try:
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"events": []}

def save_analytics(data):
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Print nice colored logs
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/track":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                event = json.loads(body)
                event["server_timestamp"] = datetime.now().isoformat()
                data = load_analytics()
                data["events"].append(event)
                # Keep last 5000 events
                if len(data["events"]) > 5000:
                    data["events"] = data["events"][-5000:]
                save_analytics(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/ping":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "time": time.time()}).encode())
        elif parsed.path == "/api/analytics":
            data = load_analytics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        elif parsed.path == "/api/stats":
            data = load_analytics()
            events = data.get("events", [])
            total = len(events)
            logins = len([e for e in events if e.get("type") == "login"])
            registers = len([e for e in events if e.get("type") == "register"])
            creates = len([e for e in events if e.get("type") == "rule_create"])
            saves = len([e for e in events if e.get("type") == "rule_save"])
            deletes = len([e for e in events if e.get("type") == "rule_delete"])
            publishes = len([e for e in events if e.get("type") == "publish"])
            comments = len([e for e in events if e.get("type") == "comment_add"])
            unique_users = list(set([e.get("user", "Guest") for e in events if e.get("user") and e.get("user") != "Guest"]))
            user_counts = {}
            for e in events:
                u = e.get("user", "Guest")
                user_counts[u] = user_counts.get(u, 0) + 1
            top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            stats = {
                "total": total,
                "logins": logins,
                "registers": registers,
                "creates": creates,
                "saves": saves,
                "deletes": deletes,
                "publishes": publishes,
                "comments": comments,
                "unique_users_count": len(unique_users),
                "unique_users": unique_users,
                "top_users": top_users
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode())
        elif parsed.path == "/" or parsed.path == "/index.html":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.join(DIR, "index.html")
        # Security: prevent directory traversal
        safe_path = os.path.normpath(path.lstrip('/'))
        full_path = os.path.join(DIR, safe_path)
        if not full_path.startswith(DIR):
            return os.path.join(DIR, "index.html")
        return full_path

# Save PID file
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

os.chdir(DIR)

print("=" * 50)
print(" 🚀 PrivacyHub Server Started!")
print("=" * 50)
print(f" 📂 Serving from: {DIR}")
print(f" 🌐 Local:       http://127.0.0.1:{PORT}")
print(f" 🌐 Network:     http://0.0.0.0:{PORT}")
print(f" 🌍 External:    http://YOUR_IP:{PORT}")
print("=" * 50)
print(" Press Ctrl+C to STOP server")
print("=" * 50)
print()

try:
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Server stopped by user.")
finally:
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    print("✅ All data saved. Goodbye!")
