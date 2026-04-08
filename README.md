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

# 🤖 Running the Demo
To see the baseline agent in action, use the provided inference.py script. This script demonstrates the agent's ability to solve task-1-public-s3 using a Groq-hosted Llama-3.3 model.

Bash
# Set your API Key
export HF_TOKEN="your-api-key"

# Run the demo
python inference.py


# 🐳 Docker Validation
To verify the environment matches the OpenEnv standard:

docker build -t cloud-iam-gym .

docker run -p 7860:7860 cloud-iam-gym

./validate-submission.sh http://localhost:7860 .
