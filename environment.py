from pydantic import BaseModel
from typing import Optional, List

# ================================
# TYPED MODELS (OpenEnv Spec)
# ================================
class Observation(BaseModel):
    email_id: int
    subject: str
    body: str
    sender: str
    task_difficulty: str

class Action(BaseModel):
    priority: str      # "urgent", "normal", "low"
    category: str      # "support", "sales", "spam", "hr"
    action: str        # "reply", "forward", "archive", "delete"

class Reward(BaseModel):
    score: float
    reason: str

# ================================
# TASKS DATABASE
# ================================
TASKS_DB = {
    "task1_easy": {
        "email_id": 101,
        "subject": "Win a FREE iPhone NOW!!!",
        "body": "Congratulations! You have won a free iPhone. Click here to claim your prize immediately!",
        "sender": "winner@scamsite.com",
        "difficulty": "easy",
        "correct": {"priority": "low", "category": "spam", "action": "delete"}
    },
    "task2_medium": {
        "email_id": 102,
        "subject": "Server slow + interested in upgrade",
        "body": "Hey, our server has been slow lately. Also we are interested in upgrading our plan. Can someone get back to us?",
        "sender": "client@bigcorp.com",
        "difficulty": "medium",
        "correct": {"priority": "normal", "category": "support", "action": "reply"}
    },
    "task3_hard": {
        "email_id": 103,
        "subject": "Re: Follow up on invoice #4521",
        "body": "This is the 3rd reminder. Our payment of $50,000 is overdue by 60 days. If not resolved in 24 hours we will take legal action.",
        "sender": "legal@enterprise-client.com",
        "difficulty": "hard",
        "correct": {"priority": "urgent", "category": "sales", "action": "forward"}
    }
}

# ================================
# ENVIRONMENT CLASS
# ================================
class EmailTriageEnv:
    def __init__(self, task_name="task1_easy"):
        if task_name not in TASKS_DB:
            raise ValueError(f"Task {task_name} not found!")
        self.task_name = task_name
        self.current_task = TASKS_DB[self.task_name]
        self.step_count = 0
        self.done = False

    def reset(self) -> Observation:
        self.step_count = 0
        self.done = False
        return Observation(
            email_id=self.current_task["email_id"],
            subject=self.current_task["subject"],
            body=self.current_task["body"],
            sender=self.current_task["sender"],
            task_difficulty=self.current_task["difficulty"]
        )

    def step(self, action: Action) -> tuple:
        if self.done:
            raise ValueError("Episode is done. Call reset() first.")

        correct = self.current_task["correct"]
        score = 0.0
        reasons = []

        # Grading logic
        if action.priority == correct["priority"]:
            score += 0.4
            reasons.append("priority correct (+0.4)")
        else:
            reasons.append(f"priority wrong (expected {correct['priority']})")

        if action.category == correct["category"]:
            score += 0.4
            reasons.append("category correct (+0.4)")
        else:
            reasons.append(f"category wrong (expected {correct['category']})")

        if action.action == correct["action"]:
            score += 0.2
            reasons.append("action correct (+0.2)")
        else:
            reasons.append(f"action wrong (expected {correct['action']})")

        self.step_count += 1
        self.done = True # One action finishes the episode

        reward = Reward(score=round(score, 2), reason=", ".join(reasons))
        observation = Observation(
            email_id=self.current_task["email_id"],
            subject=self.current_task["subject"],
            body=self.current_task["body"],
            sender=self.current_task["sender"],
            task_difficulty=self.current_task["difficulty"]
        )

        return observation, reward, self.done, {"step": self.step_count}

    def state(self) -> dict:
        return {
            "current_task": self.task_name,
            "step_count": self.step_count,
            "done": self.done
        }