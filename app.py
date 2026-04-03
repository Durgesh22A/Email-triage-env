from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

results = {"status": "running", "scores": [], "average": 0}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
    
    def log_message(self, format, *args):
        pass

def run_inference():
    import inference

if __name__ == "__main__":
    t = threading.Thread(target=run_inference)
    t.daemon = True
    t.start()
    
    print("Server started on port 7860")
    server = HTTPServer(('0.0.0.0', 7860), Handler)
    server.serve_forever()