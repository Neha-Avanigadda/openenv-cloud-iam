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
    
    # Safely try to read the JSON body if the grader sends one
    try:
        body = await request.json()
        if body and "task" in body:
            task_name = body["task"]
    except Exception:
        pass # If the grader sends null/nothing, just ignore it and use Task 1
        
    env = CloudIAMEnv(task_name=task_name)
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
