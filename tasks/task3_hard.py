from environment import Action

TASK3 = {
    "task_id": "task3_hard",
    "name": "Crisis Triage",
    "difficulty": "hard",
    "description": "Identify and correctly handle a business-critical emergency.",
    "email": {
        "email_id": 103,
        "subject": "Re: Follow up on invoice #4521",
        "body": "This is the 3rd reminder. Our payment of $50,000 is overdue by 60 days. If not resolved in 24 hours we will take legal action.",
        "sender": "legal@enterprise-client.com",
        "correct": {"priority": "urgent", "category": "sales", "action": "forward"}
    }
}

def grade(action: Action) -> float:
    correct = TASK3["email"]["correct"]
    score = 0.0
    if action.priority == correct["priority"]:
        score += 0.4
    if action.category == correct["category"]:
        score += 0.4
    if action.action == correct["action"]:
        score += 0.2
    return round(score, 2)