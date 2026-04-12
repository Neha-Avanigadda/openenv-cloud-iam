import json
from pydantic import BaseModel

class IAMAction(BaseModel):
    command: str

class IAMObservation(BaseModel):
    terminal_output: str
    service_health_status: bool
    current_vulnerability_status: str

class CloudIAMEnv:
    def __init__(self, task_name: str = "task-1-public-s3"):
        self.aws_state = {}
        self.task_name = task_name
        self.step_count = 0

    async def reset(self):
        self.step_count = 0
        
        if self.task_name == "task-1-public-s3":
            self.aws_state = {
                "s3_buckets": {"customer-data-backup": {"acl": "public-read"}},
                "services": {"backup_api": {"status": "running"}}
            }
            vuln_status = "Critical: S3 Bucket Public"
            
        elif self.task_name == "task-2-least-privilege":
            self.aws_state = {
                "iam_roles": {
                    "lambda-execution-role": {"policies": ["AdministratorAccess"]}
                },
                "services": {"data_processor": {"status": "running"}}
            }
            vuln_status = "Critical: Overly Permissive Role"
            
        elif self.task_name == "task-3-leaked-keys":
            self.aws_state = {
                "iam_users": {
                    "dev-user": {"keys": [{"id": "AKIACOMPROMISED", "status": "Active"}]}
                },
                "services": {"auth_service": {"status": "running"}}
            }
            vuln_status = "Critical: Compromised Access Key"
            
        else:
            raise ValueError(f"Unknown task: {self.task_name}")

        return IAMObservation(
            terminal_output=f"Environment Reset. {self.task_name} started.",
            service_health_status=True,
            current_vulnerability_status=vuln_status
        )

    async def step(self, action: IAMAction):
        self.step_count += 1
        command = action.command.strip()
        output = f"bash: {command}: command not found or not supported by mock environment."
        done = False

        # --- TASK 1: S3 Commands ---
        if command in ["aws s3 ls", "aws s3api list-buckets"]:
            if "s3_buckets" in self.aws_state:
                buckets = list(self.aws_state["s3_buckets"].keys())
                output = json.dumps({"Buckets": [{"Name": b} for b in buckets]}, indent=2)
            else:
                output = "No buckets found."

        elif command.startswith("aws s3api get-bucket-acl") or command.startswith("aws s3api get-public-access-block"):
            bucket_found = False
            for bucket_name, bucket_info in self.aws_state.get("s3_buckets", {}).items():
                if bucket_name in command:
                    output = json.dumps({"Status": "Publicly Accessible", "ACL": bucket_info["acl"]}, indent=2)
                    bucket_found = True
                    break
            if not bucket_found:
                output = "An error occurred (NoSuchBucket)."

        elif command.startswith("aws s3api put-bucket-acl") or command.startswith("aws s3api put-public-access-block"):
            if "customer-data-backup" in command:
                if "private" in command or "BlockPublicAcls=true" in command:
                    self.aws_state["s3_buckets"]["customer-data-backup"]["acl"] = "private"
                    output = "Success: Public access blocked and ACL updated to private."
                else:
                    output = "Command executed, but bucket is still public. Use --acl private."
            else:
                 output = "Error: Please specify a valid bucket name."

        # --- TASK 2: IAM Policy Commands ---
        elif command.startswith("aws iam list-attached-role-policies"):
            if "lambda-execution-role" in command:
                policies = self.aws_state["iam_roles"]["lambda-execution-role"]["policies"]
                output = json.dumps({"AttachedPolicies": [{"PolicyName": p} for p in policies]}, indent=2)
            else:
                output = "Role not found."

        elif command.startswith("aws iam detach-role-policy"):
            if "lambda-execution-role" in command and "AdministratorAccess" in command:
                self.aws_state["iam_roles"]["lambda-execution-role"]["policies"].remove("AdministratorAccess")
                output = "Policy AdministratorAccess detached successfully."
            else:
                output = "Failed to detach policy. Check role name and policy ARN."

        elif command.startswith("aws iam attach-role-policy"):
            if "lambda-execution-role" in command and "AmazonS3ReadOnlyAccess" in command:
                self.aws_state["iam_roles"]["lambda-execution-role"]["policies"].append("AmazonS3ReadOnlyAccess")
                output = "Policy AmazonS3ReadOnlyAccess attached successfully."
            else:
                output = "Failed to attach policy. Check role name and policy ARN."

        # --- TASK 3: IAM Key Commands ---
        elif command.startswith("aws iam list-access-keys"):
            if "dev-user" in command:
                keys = self.aws_state["iam_users"]["dev-user"]["keys"]
                output = json.dumps({"AccessKeyMetadata": [{"AccessKeyId": k["id"], "Status": k["status"]} for k in keys]}, indent=2)
            else:
                output = "User not found."

        elif command.startswith("aws iam update-access-key"):
            if "AKIACOMPROMISED" in command and "Inactive" in command:
                for k in self.aws_state["iam_users"]["dev-user"]["keys"]:
                    if k["id"] == "AKIACOMPROMISED":
                        k["status"] = "Inactive"
                output = "Access key status updated to Inactive."
            else:
                output = "Validation error: Check key ID and status value."

        elif command.startswith("aws iam create-access-key"):
            if "dev-user" in command:
                self.aws_state["iam_users"]["dev-user"]["keys"].append({"id": "AKIANEWSECUREKEY", "status": "Active"})
                output = json.dumps({"AccessKey": {"AccessKeyId": "AKIANEWSECUREKEY", "Status": "Active"}}, indent=2)
            else:
                output = "User not found."

        # --- GENUINE PROGRESS-BASED GRADERS ---
        reward = 0.1 

        if self.task_name == "task-1-public-s3":
            if self.aws_state["s3_buckets"]["customer-data-backup"]["acl"] == "private":
                reward = 0.95
                done = True

        elif self.task_name == "task-2-least-privilege":
            policies = self.aws_state["iam_roles"]["lambda-execution-role"]["policies"]
            if "AdministratorAccess" not in policies:
                reward = 0.5
            if "AdministratorAccess" not in policies and "AmazonS3ReadOnlyAccess" in policies:
                reward = 0.95
                done = True

        elif self.task_name == "task-3-leaked-keys":
            keys = self.aws_state["iam_users"]["dev-user"]["keys"]
            is_compromised_inactive = any(k["id"] == "AKIACOMPROMISED" and k["status"] == "Inactive" for k in keys)
            has_new_key = any(k["id"] == "AKIANEWSECUREKEY" for k in keys)
            
            if is_compromised_inactive:
                reward = 0.5
            if is_compromised_inactive and has_new_key:
                reward = 0.95
                done = True

        obs = IAMObservation(
            terminal_output=output,
            service_health_status=True,
            current_vulnerability_status="Secure" if done else "Critical"
        )
        return obs, reward, done, {}

    async def state(self):
        return self.aws_state

    async def close(self):
        pass


# --- OPENENV GRADER HOOK ---
def grade(*args, **kwargs):
    """
    External hook required by the Phase 2 Validator schema.
    The actual mathematical grading is handled natively inside the step() function.
    """
    return kwargs.get("reward", 0.5)