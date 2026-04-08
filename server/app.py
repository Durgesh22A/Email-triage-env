from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from environment import EmailTriageEnv, Action

app = FastAPI(title="Email Triage OpenEnv")

# Default env state
current_env = EmailTriageEnv("task1_easy")

class TaskRequest(BaseModel):
    task_name: str

@app.get("/")
def health_check():
    return {"status": "running", "message": "Email Triage Environment is up."}

@app.post("/reset")
def reset_env(req: TaskRequest = None):
    global current_env
    task = req.task_name if req and req.task_name else "task1_easy"
    try:
        current_env = EmailTriageEnv(task)
        obs = current_env.reset()
        return obs.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step_env(action: Action):
    try:
        obs, reward, done, info = current_env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info
        }
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    return current_env.state()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()