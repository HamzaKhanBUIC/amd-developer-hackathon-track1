# AMD Developer Hackathon: Zero-Token API Router

This project is an advanced AI Agent Router built for **Track 1** of the AMD Developer Hackathon.

Our goal is simple: **Maximize Accuracy while Minimizing Token Cost**. 
We achieve this through a highly optimized, 4-layer routing architecture that aggressively answers tasks using zero-token local execution whenever possible, and only escalates to expensive API models when strictly necessary.

## The 4-Layer Routing Architecture

1. **Layer 1: Semantic Caching (MiniLM)**
   - **Cost:** $0.00
   - Before any processing, the prompt is embedded using `all-MiniLM-L6-v2`. If the exact semantic meaning exists in our cache (e.g. `> 0.99` cosine similarity), we instantly return the cached answer.

2. **Layer 2: Local Heuristics (Qwen 1.5B)**
   - **Cost:** $0.00
   - We run a small XGBoost classifier over the embeddings to detect "easy" intents (e.g., greetings, basic math, definitions).
   - If classified as easy, the task is routed to a local **Qwen 2.5 1.5B GGUF** model running on the CPU. This gives us high-quality answers for zero Fireworks API tokens.

3. **Layer 3: Smart Fireworks Routing (Llama 3.1 8B / Qwen 2.5 32B / Llama 3.1 70B)**
   - **Cost:** API rates
   - If the task is hard, we look for keywords in the prompt. Code tasks go to `qwen2p5-coder-32b`, complex reasoning goes to `llama-v3p1-70b`, and everything else goes to the fast `llama-v3p1-8b-instruct`.

4. **Layer 4: Bulletproof Fallbacks**
   - **Cost:** Varies (often $0.00 if failing back locally)
   - If an API request fails or is rate-limited, the system automatically falls back to a cheaper API model. If that fails, it executes a desperate fallback to the local Qwen model to ensure we NEVER fail a task due to network errors.

## Current Project Status
- **Backend:** 100% Complete. The routing engine, semantic cache, and fallback logic are fully implemented in Python and tested to be robust against 404s and rate limits.
- **Models:** Configured to read `ALLOWED_MODELS` from the environment dynamically as required by the hackathon organizers. The `xgboost_router.json` and `Qwen 2.5 1.5B GGUF` are fully integrated and bundled.
- **Pitch UI (Optional):** A premium Next.js dashboard exists in `src/` purely to visualize our routing decisions for the pitch video. (Not used by the headless grading script).

## How to Run (Headless Grading Simulation)

1. Clone this repository.
2. Set your `FIREWORKS_API_KEY`.
3. Set your input/output paths (e.g., `export TASK_INPUT_PATH=./tasks.json` and `export TASK_OUTPUT_PATH=./output/results.json`).
4. Run `python backend/agent.py` to start the headless router.
