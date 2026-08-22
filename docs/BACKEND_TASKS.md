# Backend Development Guide & Tasks

This document is the **master guide for the backend developer**. It explains the current state of the backend repository, the architecture, and the precise, step-by-step tasks you need to complete to finish the AMD Zero-Token Router integration.

---

## 🏗️ 1. Current State & Architecture (The True Hybrid Zero-Token Router)

The backend is undergoing a massive pivot based on new Track 1 grading rules. We must run a headless batch script with a strict 4GB RAM limit and a 10-minute timeout.
Our architecture relies on **True Zero-Token Routing**:
*   **Tier 1 (Easy Tasks):** Answered entirely locally using a 4-bit quantized `Qwen 2.5 1.5B` model via `llama-cpp-python`. Because it's local, we score 0 tokens (the best possible score).
*   **Tier 2 (Hard Tasks):** Fired asynchronously to the Fireworks API using `asyncio` to prevent the 10-minute timeout.

### Important Files
1. **`agent.py` [NEW]**: The headless script the grading harness will run. It reads `/input/tasks.json` and writes `/output/results.json`.
2. **`main.py` & `fireworks_client.py`**: Kept alive *only* for the local frontend demo/pitch video. They must read `ALLOWED_MODELS` and `FIREWORKS_BASE_URL` from the environment.

---

## 🚀 2. Your Tasks

Your primary goal is to **finalize the API configuration so the Next.js frontend can communicate with it flawlessly, and ensure the local ML routing models are properly generated.**

### Task 1: The Core Architecture
- [x] Create `agent.py` which will be the absolute entrypoint.
- [x] Read input and output paths from `os.environ`.
- [x] Implement the `run()` loop to process `tasks.json`.
- [x] Structure the `asyncio` loop. Wait, we need an asynchronous engine because network calls to Fireworks take time. Use `asyncio.gather` so API calls fire simultaneously while the CPU processes local tasks one by one.

### Task 2: Machine Learning Routing (XGBoost)
- [x] You need to classify the task complexity (Easy vs Hard).
- [x] We will use an XGBoost classifier. The training script `train_model.py` generates synthetic embeddings and trains the model. 
- [x] **IMPORTANT**: You do NOT need to ask the judges to train the model. The pre-trained `xgboost_router.json` weight file is committed to the repository and is loaded instantly by the agent.

### Task 3: Local Model Integration (Qwen 1.5B)
- [x] We are using `Qwen2.5-1.5B-Instruct-GGUF` to save tokens.
- [x] **CRITICAL**: The GGUF file is bundled *inside* the Docker image. 
- [x] You MUST set `n_threads=2` in `llama-cpp-python`. The host only has 2 vCPUs. If you leave it to auto, it will spawn 16+ threads and the OS scheduler will thrash, causing the 10-minute timeout limit to fail.

### Task C: Environment Variables (Strict Mandate)
You cannot hardcode the API URL or Models anymore.
1. Update `router.py` to parse `os.environ["ALLOWED_MODELS"]` and map them to our internal variables dynamically.
2. Update `fireworks_client.py` to use `os.environ["FIREWORKS_BASE_URL"]` as the Base URL, and `os.environ["FIREWORKS_API_KEY"]`. Do not use a `.env` file fallback in the Docker container.

---

## 🛠️ 3. How to Run & Test

1. Add your Fireworks API Key to your environment: `export FIREWORKS_API_KEY="your_key_here"`
2. Open a terminal in the `/backend` folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Generate data & Train models: `python generate_dataset.py` then `python train_model.py`
5. Run the server: `uvicorn main:app --reload --port 8000`
6. Test the health endpoint by visiting `http://localhost:8000/health` in your browser.
