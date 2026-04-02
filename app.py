from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import subprocess

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "env": "email-triage-env"}).encode())
    
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('0.0.0.0', 7860), Handler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    print("Server started on port 7860")
    import inference
