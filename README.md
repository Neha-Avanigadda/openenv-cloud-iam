# Cloud IAM Security Posture Gym ☁️🔒

An **OpenEnv** benchmark designed to evaluate an AI agent's ability to act as an automated Cloud Security Engineer. 

Agents navigate a simulated AWS environment to identify and remediate vulnerabilities while maintaining the uptime of critical services.

## 🚀 The Three Tasks
| Task ID | Name | Difficulty | Objective |
| :--- | :--- | :--- | :--- |
| `task-1-public-s3` | Public S3 Remediation | Easy | Secure a publicly readable S3 bucket. |
| `task-2-least-privilege` | Lambda Least Privilege | Medium | Replace `AdministratorAccess` with scoped S3 policies. |
| `task-3-leaked-keys` | Compromised Key Rotation | Hard | Deactivate leaked IAM keys and provision secure rotations. |

## 🛠️ Installation & Setup
1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd openenv-cloud-iam
Install dependencies:

Bash
pip install openenv-core openai pydantic fastapi uvicorn uv
🤖 Running the Demo
To see the baseline agent in action, use the provided inference.py script. This script demonstrates the agent's ability to solve task-1-public-s3 using a Groq-hosted Llama-3.3 model.

Bash
# Set your API Key
export HF_TOKEN="your-api-key"

# Run the demo
python inference.py
🐳 Docker Validation
To verify the environment matches the OpenEnv standard:

docker build -t cloud-iam-gym .

docker run -p 7860:7860 cloud-iam-gym

./validate-submission.sh http://localhost:7860 .

Developed for the OpenEnv Round 1 Hackathon by Avanigadda Neha.


---

### 2. The Demo Script (`inference.py`)
This script fulfills the "demo script" requirement. It acts as the "driver" that talks to your environment and proves it works.

```python
import os
import asyncio
import json
from typing import List, Optional
from openai import AsyncOpenAI

# Import the environment and models from your local env.py
from env import CloudIAMEnv, IAMAction

# --- CONFIGURATION ---
# The grader uses HF_TOKEN to pass the API key
os.environ["OPENAI_API_KEY"] = os.getenv("HF_TOKEN", "your-api-key-here") 
os.environ["API_BASE_URL"] = "https://api.groq.com/openai/v1"
os.environ["MODEL_NAME"] = "llama-3.3-70b-versatile"

# --- LOGGING HELPERS (STRICT OPENENV FORMAT) ---
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

SYSTEM_PROMPT = """
You are an autonomous Cloud Security agent. Secure the AWS infrastructure.
Output ONLY valid JSON: {"command": "your aws cli command"}
"""

async def run_demo():
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["API_BASE_URL"])
    model_name = os.environ["MODEL_NAME"]
    task_name = "task-1-public-s3"
    
    env = CloudIAMEnv(task_name=task_name)
    log_start(task=task_name, env="cloud-iam-gym", model=model_name)

    history = []
    rewards = []
    score = 0.0
    
    try:
        obs = await env.reset()
        history.append({"role": "user", "content": f"Initial State: {json.dumps(obs.dict())}"})

        for step in range(1, 6): # Max 5 steps for the demo
            completion = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.0
            )
            
            response_text = completion.choices[0].message.content.strip()
            # Basic cleanup for JSON
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            action_dict = json.loads(clean_json)
            action = IAMAction(command=action_dict.get("command", "aws s3 ls"))

            obs, reward, done, _ = await env.step(action)
            score = reward
            rewards.append(reward)
            
            log_step(step=step, action=action.command, reward=reward, done=done, error=None)
            
            if done: break
            
            history.append({"role": "assistant", "content": response_text})
            history.append({"role": "user", "content": f"Observation: {json.dumps(obs.dict())}"})

        log_end(success=score >= 1.0, steps=step, score=score, rewards=rewards)

    except Exception as e:
        print(f"Demo failed: {e}")
        log_end(success=False, steps=0, score=0.0, rewards=[])

if __name__ == "__main__":
    asyncio.run(run_demo())