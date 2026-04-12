---
title: "Cloud IAM Security Posture Gym"
emoji: "🔒"
colorFrom: "blue"
colorTo: "indigo"
sdk: "docker"
app_port: 7860
pinned: false
license: "mit"
---

# Cloud IAM Security Posture Gym ☁️🔒

An **OpenEnv** benchmark designed to evaluate an AI agent's ability to act as an automated Cloud Security Engineer. 

Agents navigate a simulated AWS environment to identify and remediate vulnerabilities while maintaining the uptime of critical services.

## 🚀 The Three Tasks
| Task ID | Name | Difficulty | Objective |
| :--- | :--- | :--- | :--- |
| `task-1-public-s3` | Public S3 Remediation | Easy | Secure a publicly readable S3 bucket. |
| `task-2-least-privilege` | Lambda Least Privilege | Medium | Replace `AdministratorAccess` with scoped S3 policies. |
| `task-3-leaked-keys` | Compromised Key Rotation | Hard | Deactivate leaked IAM keys and provision secure rotations. |

## 📊 Grading & Reward Strategy
To accurately track agent progress, rewards are distributed based on milestones rather than binary pass/fails.
* **0.10:** Base reward for valid environment interaction.
* **0.50:** Partial credit (e.g., stopping a leak by deleting a bad key, or removing a dangerous policy).
* **0.95:** Perfect execution (e.g., replacing the bad key with a new one, or attaching the correct scoped policy).


## 🛠️ Installation & Setup
1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd openenv-cloud-iam

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

## 🤖 Running the Demo
The provided inference.py script runs an async loop over all three tasks using a compatible OpenAI-spec LLM.


## Set your API configuration
   ```bash
   export API_BASE_URL="[https://router.huggingface.co/v1](https://router.huggingface.co/v1)" # Or your proxy
   export API_KEY="your-api-key"
   export MODEL_NAME="your-chosen-model"
   ```

## Run the demo
python inference.py


## 🐳 Docker Validation
To verify the environment matches the OpenEnv standard:

docker build -t cloud-iam-gym .

docker run -p 7860:7860 cloud-iam-gym

./validate-submission.sh http://localhost:7860 .
