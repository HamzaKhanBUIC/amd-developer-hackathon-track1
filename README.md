# AMD Developer Hackathon: Zero-Token API Router

This project is an advanced AI Agent Router built for **Track 1** of the AMD Developer Hackathon.

Our goal is simple: **Maximize Accuracy while Minimizing Token Cost**. 
We achieve this through a highly optimized, 5-layer routing architecture that aggressively answers tasks using zero-token local execution whenever possible, and only escalates to expensive API models when strictly necessary.

## The 5-Layer Routing Architecture

1. **Layer 1: Conditional Pre-computation Pruning**
   - **Cost:** Negative (Saves tokens)
   - For non-code tasks (Sentiment, Factual, Summarization, NER), we aggressively regex-prune whitespace and flatten JSON to save 10-30% input tokens. Pruning is disabled for Code/Logic to preserve formatting.

2. **Layer 2: Semantic Caching (MiniLM)**
   - **Cost:** $0.00
   - Before any processing, the prompt is embedded using `all-MiniLM-L6-v2`. If the exact semantic meaning exists in our cache (e.g. `> 0.95` cosine similarity), we instantly return the cached answer.

3. **Layer 3: Category-Calibrated Confidence Thresholds / C3T (XGBoost)**
   - **Cost:** $0.00
   - We run a tiny offline XGBoost classifier over the embeddings to detect the task Category. 
   - **Math, Logic, Code, NER** -> Instantly bypassed to the Fireworks API. Small models hallucinate these.
   - **Sentiment, Factual, Summarization** -> Routed to the local Qwen 3B model.

4. **Layer 4: Logprob-Based Cascade Fallback (Qwen 3B)**
   - **Cost:** Varies (often $0.00)
   - If a task is routed to Qwen 3B, we monitor the average logprob of the first 10 generated tokens. If `average logprob < 0.6` (~55% confidence), it means Qwen is guessing. We instantly abort the local generation and fallback to the Fireworks API.

5. **Layer 5: Cache-Aware "Sticky" Batching & Smart Fallbacks**
   - **Cost:** API rates (Optimized)
   - API tasks are batched sequentially by category via `asyncio.gather()` to maximize KV Cache hits. We parse `ALLOWED_MODELS` to pick the smartest model for hard tasks and cheapest model for sentiment tasks.
   - Hardened with explicit 15-second timeouts and decoupled semaphores to guarantee we never fail the 10-minute hackathon execution window.

## Current Project Status
- **Backend:** 100% Complete. The routing engine, semantic cache, and fallback logic are fully implemented in Python and tested to be robust against 404s, rate limits, and hang conditions.
- **Models:** Configured to read `ALLOWED_MODELS` from the environment dynamically as required by the hackathon organizers. The `Qwen 2.5 3B GGUF` is fully integrated and bundled.
- **Constraints Compliance:** Hardened to strictly execute within 4GB RAM and 2vCPU. Output is strictly compliant with `[{"task_id": "...", "answer": "..."}]`. CRLF bash execution bugs pre-fixed.

## How to Run (Headless Grading Simulation)

1. Clone this repository.
2. Build the docker image: `docker build -t amd-router .`
3. Run it via Docker mapping the input/output volumes as specified by the grading harness. 
*(Alternatively, run `backend/agent.py` locally with Python 3.11).*
