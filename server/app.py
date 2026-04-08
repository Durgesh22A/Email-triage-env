from fastapi import FastAPI
from pydantic import BaseModel
from server.environment import EmailTriageEnv

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