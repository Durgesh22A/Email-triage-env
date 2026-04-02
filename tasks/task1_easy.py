from environment import EmailTriageEnv, Action

TASK1 = {
    "task_id": "task1_easy",
    "name": "Spam Detection",
    "difficulty": "easy",
    "description": "Identify spam emails and delete them.",
    "email": {
        "email_id": 101,
        "subject": "Win a FREE iPhone NOW!!!",
        "body": "Congratulations! You have won a free iPhone. Click here to claim your prize immediately!",
        "sender": "winner@scamsite.com",
        "correct": {"priority": "low", "category": "spam", "action": "delete"}
    }
}

def grade(action: Action) -> float:
    correct = TASK1["email"]["correct"]
    score = 0.0
    if action.priority == correct["priority"]:
        score += 0.4
    if action.category == correct["category"]:
        score += 0.4
    if action.action == correct["action"]:
        score += 0.2
    return round(score, 2)