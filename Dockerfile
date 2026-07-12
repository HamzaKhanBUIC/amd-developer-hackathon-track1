FROM python:3.11-slim

# Install system dependencies for building C/C++ packages and wget
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Download the quantized model directly into the image
RUN wget --progress=dot:giga -O /app/qwen2.5-3b-instruct-q4_k_m.gguf https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf
# 2. Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# AMD ROCm / PyTorch Compatibility Hints
ENV PYTORCH_ENABLE_MPS_FALLBACK=1
ENV HSA_OVERRIDE_GFX_VERSION=11.0.0

# 4. Copy the backend application code and runner script
COPY backend/ /app/
COPY run.sh /app/
RUN chmod +x /app/run.sh

# Execute the headless batch processor via the wrapper script
ENTRYPOINT ["./run.sh"]
