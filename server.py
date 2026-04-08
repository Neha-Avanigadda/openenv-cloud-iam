from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from env import CloudIAMEnv, IAMAction

app = FastAPI()
env = None

class ResetRequest(BaseModel):
    task: str = "task-1-public-s3"

class StepRequest(BaseModel):
    action: dict

@app.post("/reset")
async def reset(req: ResetRequest):
    global env
    env = CloudIAMEnv(task_name=req.task)
    obs = await env.reset()
    return {"observation": obs.dict(), "reward": 0.0, "done": False, "info": {}}

@app.post("/step")
async def step(req: StepRequest):
    global env
    if not env:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    
    action = IAMAction(command=req.action.get("command", ""))
    obs, reward, done, info = await env.step(action)
    return {"observation": obs.dict(), "reward": reward, "done": done, "info": info}

@app.get("/state")
async def state():
    global env
    if not env:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    return await env.state()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)