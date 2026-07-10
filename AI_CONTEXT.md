# AI_CONTEXT.md: Master Onboarding Document for AI Assistants

> **TO ANY AI ASSISTANT READING THIS:** You are looking at the master reference document for the AMD Developer Hackathon Track 1 project. Before attempting to debug, modify, or extend this codebase, you must understand the exact constraints and the 2-tier routing architecture documented here.

## 1. Project Goal
We are building a highly efficient LLM routing agent. The goal is to accurately route incoming prompts to the most cost-effective model while guaranteeing an 80% accuracy floor across 8 fixed task categories, with extreme input/output token optimization on the Fireworks API.

## 2. The Hard Constraints (DO NOT VIOLATE)
If you violate these constraints, the container will crash during grading and we will be disqualified.
- **Environment**: 4GB RAM, 2 vCPUs, 10-Minute Timeout.
- **Dependencies**: The `Qwen2.5-3B-Instruct-Q4_K_M.gguf` model weights are bundled directly inside the Docker image. Do not attempt to download models at runtime.
- **Concurrency**: `llama-cpp-python` must run with exactly `n_threads=2`. We enforce local CPU inference to 1 concurrent task using `asyncio.Semaphore(1)`. This is fully decoupled from the API semaphore to prevent deadlocks.
- **API Models**: We cannot hardcode Fireworks API models. We MUST parse the `ALLOWED_MODELS` environment variable.
- **Execution Mode**: This is a **Headless Batch Processor**. Do not spin up a web server (FastAPI/Flask). It reads from `TASK_INPUT_PATH` and writes to `TASK_OUTPUT_PATH`.
- **System Stability**: The `run.sh` entrypoint uses strict Linux (`\n`) CRLF endings to avoid bash interpreter crashes.

## 3. The Winning Architecture (2-Tier Zero-Token Router)
Our architecture uses a local 0-token model for easy tasks and the Fireworks API for hard tasks. We stripped out over-engineered caching and bypass logic in favor of a clean, hyper-optimized pipeline:

1. **XGBoost Category Gating (`backend/router.py`)**
   - The router uses an offline-trained XGBoost model with `sentence_transformers` to predict if a task is "easy" (Factual, Sentiment, Summarization, NER) or "hard" (Math, Logic, Code).
   - If XGBoost confidence is >75% for an easy task, it routes strictly to the local Qwen 3B model. (Cost: 0 tokens).
   - Math, Logic, and Code tasks are strictly hard-routed to the Fireworks API.

2. **Extreme API Compression (`backend/fireworks_client.py`)**
   - We utilize 3-5 word micro-instructions (e.g. "Output Positive, Negative, or Neutral.") instead of verbose system prompts to save input tokens.
   - We aggressively limit `max_tokens` (e.g. 150 for Code, 80 for Logic).
   - We inject aggressive `stop` sequences (`["\n\n", "Note:", "Explanation:"]`) to instantly cut off LLM "yapping".

3. **Cache-Aware Batching (`backend/agent.py`)**
   - We execute all tasks of a specific category concurrently against the Fireworks API using a dedicated API semaphore.
   - We strictly enforce timeouts on the `AsyncOpenAI` client to ensure the hackathon's 10-minute maximum runtime is never exceeded.

## Code Entrypoint
- `backend/agent.py` contains the `asyncio` event loop and sticky batching.
- `backend/router.py` contains the clean XGBoost gating logic and category matching.
- `backend/fireworks_client.py` handles the heavily optimized API requests (with micro-prompts and stop sequences).

> **END OF AI CONTEXT.** Proceed with extreme caution. The 2-Tier Architecture is mathematically locked in to hit 600-1000 tokens while passing the 80% accuracy gate. Do not attempt to over-engineer it.
