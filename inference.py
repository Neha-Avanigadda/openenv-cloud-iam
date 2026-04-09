import os
import asyncio
import json
from typing import List, Optional
from openai import AsyncOpenAI

# Import the environment and models from your local env.py
from env import CloudIAMEnv, IAMAction, IAMObservation

# --- 1. DYNAMIC CONFIGURATION (CRITICAL FOR PHASE 2) ---

# The judges inject 'API_KEY' and 'API_BASE_URL' to track your calls through LiteLLM.
# We use os.getenv to prioritize their injected values over your local fallbacks.
API_KEY = os.getenv("API_KEY", os.getenv("HF_TOKEN", "your-fallback-key"))
API_BASE = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# --- 2. LOGGING HELPERS (STRICT OPENENV FORMAT) ---

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

SYSTEM_PROMPT = """
You are an autonomous Cloud Security Posture Management (CSPM) agent. 
Your goal is to secure AWS infrastructure without breaking service availability.
You will receive JSON observations about the environment state.
You must output ONLY a valid JSON object representing your action.
Format your output exactly like this:
{"command": "your aws cli command here"}
"""

# --- 3. MAIN INFERENCE LOOP ---

async def main():
    # Initialize the client using the injected API_BASE and API_KEY
    client = AsyncOpenAI(
        api_key=API_KEY, 
        base_url=API_BASE
    )
    
    model_name = MODEL
    
    # Task names injected by the benchmark runner
    task_name = os.getenv("MY_ENV_V4_TASK", "task-1-public-s3")
    benchmark_name = os.getenv("MY_ENV_V4_BENCHMARK", "cloud-iam-posture-gym")
    
    env = CloudIAMEnv(task_name=task_name)
    max_steps = 10
    score = 0.0
    history = []
    rewards_list: List[float] = []

    log_start(task=task_name, env=benchmark_name, model=model_name)

    try:
        obs = await env.reset()
        history.append({"role": "user", "content": f"Initial State: {obs.model_dump_json()}"})

        for step in range(1, max_steps + 1):
            error_msg = None
            try:
                completion = await client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                    temperature=0.0,
                )
                response_text = completion.choices[0].message.content.strip()
                
                # Robust JSON cleaning
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                action_dict = json.loads(clean_json)
                action = IAMAction(command=action_dict.get("command", "invalid"))
            except Exception as e:
                error_msg = str(e).replace("\n", " ") 
                response_text = '{"command": "error"}'
                action = IAMAction(command="error")

            # Execute step in the environment
            obs, reward, done, _ = await env.step(action)
            
            # Update score and history
            score = reward 
            rewards_list.append(reward)
            
            log_step(step=step, action=action.command, reward=reward, done=done, error=error_msg)

            history.append({"role": "assistant", "content": response_text})
            history.append({"role": "user", "content": f"Observation: {obs.model_dump_json()}"})

            if done:
                break

        # Finalize results
        score = min(max(score, 0.0), 1.0)
        success = score >= 1.0
        log_end(success=success, steps=step, score=score, rewards=rewards_list)

    except Exception as e:
        print(f"[DEBUG] Total runtime failure: {e}")
        log_end(success=False, steps=0, score=0.0, rewards=[])

if __name__ == "__main__":
    asyncio.run(main())