from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys

# Yeh line Python ko batayegi ki bahar wale folder mein bhi files dhundo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import EmailTriageEnv
app = FastAPI()
env = EmailTriageEnv()

@app.post("/reset")
async def reset():
    return env.reset()

@app.get("/score")
async def get_score():
    return {"score": env.get_score()}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()