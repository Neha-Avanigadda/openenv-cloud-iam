import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request
import uvicorn
from pydantic import BaseModel
from env import CloudIAMEnv, IAMAction

app = FastAPI()
env = None

class StepRequest(BaseModel):
    action: dict

@app.post("/reset")
async def reset(request: Request):
    global env
    task_name = "task-1-public-s3"
    try:
        body = await request.json()
        if body:
            # Catch whatever key the OpenEnv validator uses to dictate the task
            task_name = body.get("task_id") or body.get("task") or body.get("task_name") or task_name
    except Exception:
        pass
        
    env = CloudIAMEnv(task_name=task_name)
    # Using .dict() for broad pydantic version compatibility
    obs = await env.reset()
    try:
        obs_dict = obs.model_dump()
    except AttributeError:
        obs_dict = obs.dict()
        
    return {"observation": obs_dict, "reward": 0.0, "done": False, "info": {}}

@app.post("/step")
async def step(req: StepRequest):
    global env
    if not env:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    
    action = IAMAction(command=req.action.get("command", ""))
    obs, reward, done, info = await env.step(action)
    
    try:
        obs_dict = obs.model_dump()
    except AttributeError:
        obs_dict = obs.dict()
        
    return {"observation": obs_dict, "reward": reward, "done": done, "info": info}

@app.get("/state")
async def state():
    global env
    if not env:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    return await env.state()

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()