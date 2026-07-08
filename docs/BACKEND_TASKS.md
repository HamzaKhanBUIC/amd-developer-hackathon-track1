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

### Task A: Build the Headless Batch Processor (`agent.py`)
The grading harness will not use the FastAPI server. You must create `agent.py`:
1. Read the array of tasks from `/input/tasks.json`.
2. Process them concurrently using `asyncio.gather()`. 
3. If the task is routed to the local `Qwen 1.5B` model, wrap the execution in `asyncio.to_thread()` and use an `asyncio.Semaphore(1)` so we don't crash the 2 vCPUs or exceed 4GB RAM.
4. Write the results to `/output/results.json` and exit with code 0.

### Task B: Generate Data & Train the XGBoost Router
The `router.py` file expects `xgboost_router.json` to exist in the root folder, otherwise it defaults to the expensive 31B fallback model. (Note: TF-IDF has been fully removed, we now pipe dense vectors directly).
1. Open a terminal in the `/backend` folder.
2. Make sure you have installed the requirements: `pip install -r requirements.txt`.
3. Generate the 8-category dataset: `python generate_dataset.py` (Wait for it to finish and generate `dataset.csv`).
4. Run the training script: `python train_model.py`.
5. Verify that the weight file (`xgboost_router.json`) has been generated in the folder.

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
