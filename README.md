# ☁️ Cloud IAM & Security Posture Gym
**An OpenEnv Benchmark for Autonomous Cloud Security Agents**

The **Cloud IAM & Security Posture Gym** is a specialized environment designed to evaluate how well AI agents can identify and remediate AWS security vulnerabilities while maintaining strict application uptime (the "Least Privilege" principle).

---

## 🏆 The Challenge: Security vs. Availability
In this gym, agents act as automated SREs. It is not enough to simply delete a vulnerable resource. If an agent secures an S3 bucket or an IAM role but causes the underlying microservice to return a `False` health status, the reward is penalized.

### 🧠 Action & Observation Space
- **Action Space (`IAMAction`):** A JSON object containing a standard AWS CLI or Bash command.
  - *Example:* `{"command": "aws s3api put-bucket-acl --bucket backup --acl private"}`
- **Observation Space (`IAMObservation`):**
  - `terminal_output`: Mock stdout/stderr from the environment.
  - `service_health_status`: Boolean (Must stay `True` for full marks).
  - `current_vulnerability_status`: `"Secure"` or `"Critical"`.

---

## 🚀 Tasks
| ID | Task Name | Difficulty | Objective |
| :--- | :--- | :--- | :--- |
| `task-1` | **Public S3** | Easy | Find a public bucket and set ACL to private. |
| `task-2` | **Least Privilege** | Medium | Strip `Admin` from a Lambda and add `S3ReadOnly`. |
| `task-3` | **Key Rotation** | Hard | Deactivate a leaked key and provision a new one. |

---

## 🛠️ Setup & Local Testing

### 1. Installation
```powershell
# Clone the repo
git clone [https://github.com/Neha-Avanigadda/openenv-cloud-iam.git](https://github.com/Neha-Avanigadda/openenv-cloud-iam.git)
cd openenv-cloud-iam

# Setup Environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
2. Configuration
Create a .env file in the root directory:

Plaintext
GROQ_API_KEY=your_key_here
API_BASE_URL=[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)
MODEL_NAME=llama-3.3-70b-versatile
3. Execution
PowerShell
python inference.py
🐳 Docker & Validation
This project is built to be fully compatible with the OpenEnv grading specification.

Build the image:

Bash
docker build -t cloud-iam-gym .
Run Validation:

Bash
# Terminal 1
docker run -p 7860:7860 cloud-iam-gym

# Terminal 2
./validate-submission.sh http://localhost:7860 .
📝 License
MIT License. Created for the Meta-HuggingFace OpenEnv Challenge.


### 💡 Pro-Tip for your GitHub:
Since your project uses `python-dotenv`, make sure your `.gitignore` file contains these lines so you don't leak your keys again:
```text
.env
venv/
__pycache__/
*.pyc
