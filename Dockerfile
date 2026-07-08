FROM python:3.11-slim

# Install system dependencies for building C/C++ packages and wget
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Download the quantized model directly into the image
RUN wget -q -O /app/qwen2.5-1.5b-instruct-q4_k_m.gguf https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf

# 2. Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Pre-cache the SentenceTransformer model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 4. Copy the backend application code
COPY backend/ /app/

# 5. Train the XGBoost Router model during Docker build!
# This generates xgboost_router.json securely inside the container, bypassing local OS dependency issues.
RUN python train_model.py

# Execute the headless batch processor
ENTRYPOINT ["python", "agent.py"]
