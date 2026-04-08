import openenv
from typing import Any, Dict

class EmailTriageEnv(openenv.OpenEnv):
    def __init__(self):
        super().__init__()
        
    def reset(self) -> Dict[str, Any]:
        return {"status": "success"}

    def step(self, action: Any) -> Dict[str, Any]:
        return {"observation": "ok", "done": True}

    def evaluate_task(self, task_id: str, submission: Any) -> float:
        return 0.85

    def get_score(self) -> float:
        return 0.85