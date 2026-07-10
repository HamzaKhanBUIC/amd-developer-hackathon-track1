# AI_CONTEXT.md: Master Onboarding Document for AI Assistants

> **TO ANY AI ASSISTANT READING THIS:** You are looking at the master reference document for the AMD Developer Hackathon Track 1 project. Before attempting to debug, modify, or extend this codebase, you must understand the exact constraints and the 5-layer routing architecture documented here.

## 1. Project Goal
We are building a highly efficient LLM routing agent. The goal is to accurately route incoming prompts to the most cost-effective model while guaranteeing an 80% accuracy floor across 8 fixed task categories.

## 2. The Hard Constraints (DO NOT VIOLATE)
If you violate these constraints, the container will crash during grading and we will be disqualified.
- **Environment**: 4GB RAM, 2 vCPUs, 10-Minute Timeout.
- **Dependencies**: The `Qwen2.5-3B-Instruct-Q4_K_M.gguf` model weights are bundled directly inside the Docker image (under 10GB total size limit). Do not attempt to download models at runtime.
- **Concurrency**: `llama-cpp-python` must run with exactly `n_threads=2`. We enforce local CPU inference to 1 concurrent task using `asyncio.Semaphore(1)`. This is fully decoupled from the API semaphore to prevent deadlocks.
- **API Models**: We cannot hardcode Fireworks API models. We MUST parse the `ALLOWED_MODELS` environment variable.
- **Execution Mode**: This is a **Headless Batch Processor**. Do not spin up a web server (FastAPI/Flask). It reads from `TASK_INPUT_PATH` and writes to `TASK_OUTPUT_PATH`.
- **System Stability**: The `run.sh` entrypoint uses strict Linux (`\n`) CRLF endings to avoid bash interpreter crashes.

## 3. The Winning Architecture (5-Layer Hybrid Router)
Our architecture uses a local 0-token model for easy tasks and the Fireworks API for hard tasks. To guarantee massive token efficiency, we employ 5 layers:

1. **Conditional Pre-computation Pruning (`backend/router.py`)**
   - For non-code tasks (Sentiment, Factual, Summarization, NER), we aggressively regex-prune whitespace and flatten JSON to save 10-30% input tokens. Pruning is disabled for Code/Logic to preserve formatting.
   
2. **"True Zero-Token" Semantic Cache (`backend/router.py`)**
   - If a prompt has > 0.95 cosine similarity to a previously answered prompt (using `all-MiniLM-L6-v2`), we instantly return the cached answer. (Cost: 0 tokens).

3. **Category-Calibrated Confidence Thresholds / C3T (`backend/router.py`)**
   - XGBoost predicts the task *Category*. 
   - **Math, Logic, Code, NER** -> Instantly bypassed to the Fireworks API. Small models hallucinate these.
   - **Sentiment, Factual, Summarization** -> Routed to the local Qwen 3B model. (Cost: 0 tokens).

4. **Logprob-Based Cascade Fallback (`backend/agent.py`)**
   - If a task is routed to Qwen 3B, we monitor the average logprob of the first 10 generated tokens.
   - If `average logprob < 0.6` (~55% confidence), it means Qwen is guessing. We instantly abort the local generation and fallback to the Fireworks API.

5. **Cache-Aware "Sticky" Batching (`backend/agent.py`)**
   - We execute all tasks of a specific category concurrently against the Fireworks API using a dedicated API semaphore.
   - We strictly enforce a 15-second `timeout` on the `AsyncOpenAI` client to ensure the hackathon's 10-minute maximum runtime is never exceeded.

## 4. API Model Selection
The `parse_allowed_models()` function in `router.py` searches the `ALLOWED_MODELS` string for the smartest available model (e.g., `70b`, `72b`, `405b`) for hard tasks, a code model for coding tasks, and a cheaper fallback (e.g., `8b`) for simple API routing.

## Code Entrypoint
- `backend/agent.py` contains the `asyncio` event loop, logprob logic, and sticky batching.
- `backend/router.py` contains the XGBoost model, semantic cache, and pruning logic.
- `backend/fireworks_client.py` handles the heavily optimized API requests (with `max_tokens` limiters).

> **END OF AI CONTEXT.** Proceed with extreme caution and never sacrifice the accuracy gate for token efficiency on Code/Math tasks.
