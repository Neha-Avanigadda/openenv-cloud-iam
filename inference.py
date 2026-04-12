import os
import asyncio
import json
from typing import List, Optional
from openai import AsyncOpenAI
from env import CloudIAMEnv, IAMAction

API_KEY = os.getenv("API_KEY", os.getenv("HF_TOKEN", "your-fallback-key"))
API_BASE = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

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
Output ONLY a valid JSON object representing your action:
{"command": "your aws cli command here"}
"""

async def run_task(client: AsyncOpenAI, task_name: str, benchmark_name: str):
    env = CloudIAMEnv(task_name=task_name)
    max_steps = 10
    score = 0.0
    history = []
    rewards_list: List[float] = []

    log_start(task=task_name, env=benchmark_name, model=MODEL)

    try:
        obs = await env.reset()
        history.append({"role": "user", "content": f"Initial State: {obs.model_dump_json()}"})

        for step in range(1, max_steps + 1):
            error_msg = None
            try:
                completion = await client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                    temperature=0.0,
                )
                response_text = completion.choices[0].message.content.strip()
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                action_dict = json.loads(clean_json)
                action = IAMAction(command=action_dict.get("command", "invalid"))
            except Exception as e:
                error_msg = str(e).replace("\n", " ") 
                response_text = '{"command": "error"}'
                action = IAMAction(command="error")

            obs, reward, done, _ = await env.step(action)
            score = reward 
            rewards_list.append(reward)
            
            log_step(step=step, action=action.command, reward=reward, done=done, error=error_msg)

            history.append({"role": "assistant", "content": response_text})
            history.append({"role": "user", "content": f"Observation: {obs.model_dump_json()}"})

            if done:
                break

        success = score >= 0.90
        log_end(success=success, steps=step, score=score, rewards=rewards_list)

    except Exception as e:
        log_end(success=False, steps=0, score=0.1, rewards=[])

async def main():
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE)
    benchmark_name = os.getenv("MY_ENV_V4_BENCHMARK", "cloud-iam-posture-gym")
    
    # Run all 3 tasks to satisfy the "Minimum 3 tasks with agent graders" rule
    tasks = ["task-1-public-s3", "task-2-least-privilege", "task-3-leaked-keys"]
    for task_name in tasks:
        await run_task(client, task_name, benchmark_name)

if __name__ == "__main__":
    asyncio.run(main())