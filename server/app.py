from fastapi import FastAPI
import os
import sys
import uvicorn

# Path configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from environment import EmailTriageEnv

app = FastAPI()
env = EmailTriageEnv()

@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.post("/reset")
async def reset():
    return env.reset()

@app.get("/score")
async def get_score():
    return {"score": env.get_score()}

@app.post("/step")
async def step(action: dict):
    return env.step(action)

# VALIDATOR REQUIREMENT: main() function
def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

# VALIDATOR REQUIREMENT: callable main
if __name__ == "__main__":
    main()