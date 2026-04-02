import os
import json
from openai import OpenAI
from environment import EmailTriageEnv, Action
from tasks.task1_easy import TASK1, grade as grade1
from tasks.task2_medium import TASK2, grade as grade2
from tasks.task3_hard import TASK3, grade as grade3

# ================================
# SETUP CLIENT
# ================================
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("HF_TOKEN", "your-key-here"),
)
MODEL = os.environ.get("MODEL_NAME", "gpt-4o-mini")

# ================================
# ASK LLM TO TRIAGE EMAIL
# ================================
def ask_agent(email: dict) -> Action:
    prompt = f"""You are an email triage assistant.

Email Details:
- Subject: {email['subject']}
- From: {email['sender']}
- Body: {email['body']}

Classify this email by responding ONLY with valid JSON like this:
{{
  "priority": "urgent" or "normal" or "low",
  "category": "support" or "sales" or "spam" or "hr",
  "action": "reply" or "forward" or "archive" or "delete"
}}

Respond with JSON only. No explanation."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )

    text = response.choices[0].message.content.strip()
    # Clean up if LLM adds markdown
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    return Action(**data)

# ================================
# RUN ONE TASK
# ================================
def run_task(task: dict, grade_fn):
    email = task["email"]
    task_id = task["task_id"]

    print(json.dumps({
        "event": "START",
        "task_id": task_id,
        "difficulty": task["difficulty"],
        "subject": email["subject"]
    }))

    action = ask_agent(email)

    print(json.dumps({
        "event": "STEP",
        "task_id": task_id,
        "action": action.model_dump()
    }))

    score = grade_fn(action)

    print(json.dumps({
        "event": "END",
        "task_id": task_id,
        "score": score
    }))

    return score

# ================================
# MAIN
# ================================
if __name__ == "__main__":
    scores = []

    scores.append(run_task(TASK1, grade1))
    scores.append(run_task(TASK2, grade2))
    scores.append(run_task(TASK3, grade3))

    avg = round(sum(scores) / len(scores), 2)
    print(json.dumps({
        "event": "SUMMARY",
        "scores": scores,
        "average": avg
    }))