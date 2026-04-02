from pydantic import BaseModel
from typing import Optional, List
import random

# ================================
# TYPED MODELS
# ================================

class Observation(BaseModel):
    email_id: int
    subject: str
    body: str
    sender: str

class Action(BaseModel):
    priority: str      # "urgent", "normal", "low"
    category: str      # "support", "sales", "spam", "hr"
    action: str        # "reply", "forward", "archive", "delete"

class Reward(BaseModel):
    score: float
    reason: str

# ================================
# EMAIL DATA
# ================================

EMAILS = [
    {
        "email_id": 1,
        "subject": "Production server is DOWN!",
        "body": "Our website is completely down. Customers cannot login. Fix ASAP!",
        "sender": "ops@company.com",
        "correct": {"priority": "urgent", "category": "support", "action": "reply"}
    },
    {
        "email_id": 2,
        "subject": "Buy cheap followers now!!!",
        "body": "Get 10,000 Instagram followers for just $5. Click here now!",
        "sender": "promo@spamsite.com",
        "correct": {"priority": "low", "category": "spam", "action": "delete"}
    },
    {
        "email_id": 3,
        "subject": "Interested in your product",
        "body": "Hi, I saw your demo and I'm interested in buying. Can we schedule a call?",
        "sender": "john@prospect.com",
        "correct": {"priority": "normal", "category": "sales", "action": "reply"}
    },
    {
        "email_id": 4,
        "subject": "Leave application for next week",
        "body": "I would like to apply for leave from Monday to Wednesday next week.",
        "sender": "employee@company.com",
        "correct": {"priority": "normal", "category": "hr", "action": "forward"}
    },
    {
        "email_id": 5,
        "subject": "URGENT: Payment gateway failing",
        "body": "All payments are being declined since 2 hours. Revenue loss happening now!",
        "sender": "finance@company.com",
        "correct": {"priority": "urgent", "category": "support", "action": "reply"}
    },
]

# ================================
# ENVIRONMENT CLASS
# ================================

class EmailTriageEnv:
    def __init__(self):
        self.current_email = None
        self.step_count = 0
        self.done = False

    def reset(self) -> Observation:
        """Start fresh - pick a random email"""
        self.step_count = 0
        self.done = False
        self.current_email = random.choice(EMAILS)
        return Observation(**{k: self.current_email[k] for k in ["email_id", "subject", "body", "sender"]})

    def step(self, action: Action) -> tuple:
        """Agent takes action, we return reward"""
        if self.done:
            raise ValueError("Episode is done. Call reset() first.")

        correct = self.current_email["correct"]
        score = 0.0
        reasons = []

        # Score each field
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
        self.done = True  # one email = one episode

        reward = Reward(score=round(score, 2), reason=", ".join(reasons))
        observation = Observation(**{k: self.current_email[k] for k in ["email_id", "subject", "body", "sender"]})

        return observation, reward, self.done, {"step": self.step_count}

    def state(self) -> dict:
        """Return current state"""
        return {
            "current_email_id": self.current_email["email_id"] if self.current_email else None,
            "step_count": self.step_count,
            "done": self.done
        }