# Project DNA: AMD Zero-Token API Router

## Core Identity
This project is built to win Track 1 of the AMD Developer Hackathon. The primary objective is to implement a robust query routing mechanism that maximizes output accuracy while minimizing token consumption on the Fireworks AI API.

## 2. Architecture Overview
This is a headless batch processor utilizing an advanced **5-Layer Zero-Token Router** to guarantee an 80% (16/19) accuracy gate while dominating the token efficiency leaderboard within an exact **4 GB RAM, 2 vCPU, 10-minute timeout** environment.

1. **Conditional Pre-computation Pruning**: Regex strips whitespaces and flattens JSON for text tasks to save 10-30% input tokens (disabled for Code tasks).
2. **Semantic Cache**: Resolves highly similar queries (>0.95 cosine similarity) locally for 0 tokens using a tiny MiniLM CPU model.
3. **Category-Calibrated Confidence Thresholds (C3T)**: An offline-trained XGBoost model classifies queries by category. Math, Logic, and Code are instantly bypassed to the Fireworks API (expensive/code models). Text and Sentiment are sent to the local model.
4. **Logprob-Based Cascade Fallback**: If the local Qwen 3B model struggles (monitored via logprobs, or if it times out/fails), generation is aborted and the query falls back to the API.
5. **Cache-Aware Sticky Batching & Anti-Deadlock Concurrency**: API tasks are batched sequentially by category via `asyncio.gather()` to maximize KV Cache hits on the Fireworks API. Hardened with 15-second API timeouts and decoupled local/API semaphores to guarantee we never fail the 10-minute hackathon timeout.

**Local Fallback Model:** `Qwen2.5-3B-Instruct-Q4_K_M.gguf` (bundled in the container, carefully selected to fit 4GB RAM).
**Fireworks API Model:** Dynamically parsed from `ALLOWED_MODELS` (regex searches for the smartest models for hard tasks).

## Status
- [x] Implement Semantic Router logic
- [x] Configure Local Model execution environment (Qwen 3B GGUF bundled)
- [x] Setup Fireworks API routing & Pre-train XGBoost model
- [x] Build fail-safe exception handling for 404s and rate-limits (15s timeouts)
- [x] Fix Concurrency Deadlocks (Decoupled Semaphores)
- [x] Update documentation to reflect Hackathon rule compliance (Headless Batch, 4GB RAM)
- [x] System Harden: Fixed CRLF line endings for Linux execution

## Important Rules
- Local models are legal and cost 0 tokens. They MUST be heavily utilized.
- All code must run strictly within 4GB of RAM and 2 vCPUs (No GPU).
- Do NOT use hardcoded API model names; always fall back on parsing the `ALLOWED_MODELS` environment variable.
- All API calls must route exclusively through `FIREWORKS_BASE_URL`.
