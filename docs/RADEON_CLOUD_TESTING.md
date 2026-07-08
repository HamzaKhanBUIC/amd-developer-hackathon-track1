# Radeon Cloud Testing Guide

This guide explains how to test our Zero-Token Router directly on the Radeon Global / AMD Developer Cloud Jupyter Lab environment.

## 1. Setup the Environment

Open a new Jupyter Notebook (`.ipynb` file) and run the following commands in a cell to clone the repository and install the dependencies:

```python
import os
import subprocess

# 1. Clone the repository (if not already done)
if not os.path.exists("amd-developer-hackathon-track1"):
    subprocess.run("git config --global http.sslVerify false", shell=True)
    subprocess.run("git clone https://github.com/HamzaKhanBUIC/amd-developer-hackathon-track1.git", shell=True)

# 2. Change into the project directory
os.chdir("amd-developer-hackathon-track1")

# 3. Pull latest changes
subprocess.run("git reset --hard", shell=True)
subprocess.run("git pull origin master", shell=True)

# 4. Install requirements
subprocess.run("pip install -r backend/requirements.txt", shell=True)
```

## 2. Download the Local Model

Since our router uses a zero-token local execution strategy for easy tasks, we need to download the quantized Qwen 1.5B model. Run this in the next cell:

```python
import urllib.request
import os

model_file = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
if not os.path.exists(model_file):
    print(f"Downloading {model_file} (approx 1.2 GB)...")
    url = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    urllib.request.urlretrieve(url, model_file)
    print("Download complete!")
else:
    print("Model already exists.")
```

## 3. Run the Agent Test

Finally, run the agent using this python script. **Make sure to insert your FIREWORKS_API_KEY.**

```python
import os
import json
import subprocess

# 1. Set required environment variables
os.environ["FIREWORKS_API_KEY"] = "YOUR_FIREWORKS_API_KEY_HERE"
os.environ["FIREWORKS_BASE_URL"] = "https://api.fireworks.ai/inference/v1"
os.environ["ALLOWED_MODELS"] = "accounts/fireworks/models/llama-v3p1-8b-instruct,accounts/fireworks/models/qwen2p5-coder-32b-instruct,accounts/fireworks/models/llama-v3p1-70b-instruct"

os.environ["TASK_INPUT_PATH"] = "./input/tasks.json"
os.environ["TASK_OUTPUT_PATH"] = "./output/results.json"

# 2. Create fake tasks for grading
os.makedirs("./input", exist_ok=True)
practice_tasks = [
  { "task_id": "task-01", "prompt": "Translate 'Hello World' to French." },
  { "task_id": "task-02", "prompt": "Write a python script to parse a JSON file." }
]
with open("./input/tasks.json", "w") as f:
    json.dump(practice_tasks, f)

# 3. Run the router
print("Starting Zero-Token Router...")
result = subprocess.run(["python", "backend/agent.py"], capture_output=True, text=True)

# 4. Show results
print("--- LOGS ---")
print(result.stdout)
if result.stderr:
    print("--- ERRORS ---")
    print(result.stderr)

print("\n--- JSON OUTPUT ---")
try:
    with open("./output/results.json", "r") as f:
        print(json.dumps(json.load(f), indent=2))
except Exception as e:
    print("Failed to read output:", e)
```

## Troubleshooting

- **404 Model Not Found**: Ensure `ALLOWED_MODELS` has the `p1` in `llama-v3p1-8b-instruct`.
- **Errno 2 (No such file)**: Ensure you ran `os.chdir("amd-developer-hackathon-track1")` before running `backend/agent.py`.
