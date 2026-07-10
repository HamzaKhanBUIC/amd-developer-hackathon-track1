#!/bin/bash
set -e

echo "=== AMD Hackathon - Codespaces Setup and Test ==="

# 1. Download Qwen 3B local model if not present
if [ ! -f "backend/qwen2.5-3b-instruct-q4_k_m.gguf" ]; then
    echo "Downloading Qwen2.5-3B-Instruct GGUF model (~2.2GB)..."
    wget --progress=dot:giga -O backend/qwen2.5-3b-instruct-q4_k_m.gguf https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf
else
    echo "Local model already exists."
fi

# 2. Install dependencies
echo "Installing python dependencies..."
pip install -r backend/requirements.txt

# 3. Create mock input tasks
echo "Creating mock input tasks in input/tasks.json..."
mkdir -p input
cat << 'EOF' > input/tasks.json
[
  { "id": "task-01", "prompt": "Is the sentiment of this review positive or negative: 'I absolutely love this new CPU!'" },
  { "id": "task-02", "prompt": "Extract all entities and types from: Sarah Miller joined Google in Seattle last March." },
  { "id": "task-03", "prompt": "Calculate exactly: What is 15 * 24 + 100?" },
  { "id": "task-04", "prompt": "Write a python function to recursively reverse a list." }
]
EOF

# 4. Prompt for Fireworks API key if not set
if [ -z "$FIREWORKS_API_KEY" ]; then
    echo "WARNING: FIREWORKS_API_KEY environment variable is not set!"
    read -p "Please enter your Fireworks API Key: " api_key
    export FIREWORKS_API_KEY="$api_key"
fi

# Set allowed models default if not set
if [ -z "$ALLOWED_MODELS" ]; then
    export ALLOWED_MODELS="accounts/fireworks/models/gemma-4-26b-a4b-it,accounts/fireworks/models/kimi-k2p7-code,accounts/fireworks/models/minimax-m3"
fi

# 5. Run the batch processor agent
echo "Running agent.py on mock tasks..."
cd backend
python agent.py --input ../input/tasks.json --output ../output/results.json

echo "=== Execution Complete ==="
echo "Results written to output/results.json:"
cat ../output/results.json
