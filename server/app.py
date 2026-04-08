from fastapi import FastAPI
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from environment import EmailTriageEnv

app = FastAPI()
env = EmailTriageEnv()

@app.post("/reset")
async def reset():
    return env.reset()

@app.get("/score")
async def get_score():
    # Portal expects a float or a dict with score
    return {"score": env.get_score()}

@app.post("/step")
async def step(action: dict):
    return env.step(action)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)