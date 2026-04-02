from environment import Action

TASK2 = {
    "task_id": "task2_medium",
    "name": "Multi-label Triage",
    "difficulty": "medium",
    "description": "Correctly triage emails that have mixed signals.",
    "email": {
        "email_id": 102,
        "subject": "Server slow + interested in upgrade",
        "body": "Hey, our server has been slow lately. Also we are interested in upgrading our plan. Can someone get back to us?",
        "sender": "client@bigcorp.com",
        "correct": {"priority": "normal", "category": "support", "action": "reply"}
    }
}

def grade(action: Action) -> float:
    correct = TASK2["email"]["correct"]
    score = 0.0
    if action.priority == correct["priority"]:
        score += 0.4
    if action.category == correct["category"]:
        score += 0.4
    if action.action == correct["action"]:
        score += 0.2
    return round(score, 2)