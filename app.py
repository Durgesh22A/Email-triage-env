from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import os
from openai import OpenAI
from tasks.task1_easy import TASK1, grade as grade1
from tasks.task2_medium import TASK2, grade as grade2
from tasks.task3_hard import TASK3, grade as grade3

client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.environ.get("HF_TOKEN", ""),
)
MODEL = os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")

results = {
    "status": "running",
    "scores": [],
    "average": 0,
    "details": []
}

def ask_agent(email):
    prompt = f"""You are an email triage assistant.
Email:
- Subject: {email['subject']}
- From: {email['sender']}
- Body: {email['body']}

Respond ONLY with JSON:
{{
  "priority": "urgent" or "normal" or "low",
  "category": "support" or "sales" or "spam" or "hr",
  "action": "reply" or "forward" or "archive" or "delete"
}}"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def run_inference():
    global results
    tasks = [
        (TASK1, grade1),
        (TASK2, grade2),
        (TASK3, grade3),
    ]
    scores = []
    details = []

    for task, grade_fn in tasks:
        email = task["email"]
        action_data = ask_agent(email)
        
        from environment import Action
        action = Action(**action_data)
        score = grade_fn(action)
        scores.append(score)
        
        details.append({
            "task_id": task["task_id"],
            "difficulty": task["difficulty"],
            "subject": email["subject"],
            "action": action_data,
            "score": score
        })
        print(json.dumps({"event": "END", "task_id": task["task_id"], "score": score}))

    avg = round(sum(scores) / len(scores), 2)
    results["scores"] = scores
    results["average"] = avg
    results["details"] = details
    results["status"] = "done"
    print(json.dumps({"event": "SUMMARY", "scores": scores, "average": avg}))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    t = threading.Thread(target=run_inference)
    t.daemon = True
    t.start()
    print("Server started on port 7860")
    server = HTTPServer(('0.0.0.0', 7860), Handler)
    server.serve_forever()