# Project DNA: AMD Zero-Token API Router

## Core Identity
This project is built to win Track 1 of the AMD Developer Hackathon. The primary objective is to implement a robust query routing mechanism that maximizes output accuracy while minimizing token consumption on the Fireworks AI API.

## 2. Architecture Overview
This is a headless batch processor utilizing an advanced **5-Layer Zero-Token Router** to guarantee an 80% (16/19) accuracy gate while dominating the token efficiency leaderboard within an 8 vCPU, 32GB RAM environment.

1. **Conditional Pre-computation Pruning**: Regex strips whitespaces and flattens JSON for text tasks to save 10-30% input tokens (disabled for Code tasks).
2. **Semantic Cache**: Resolves highly similar queries (>0.95 cosine similarity) locally for 0 tokens.
3. **Category-Calibrated Confidence Thresholds (C3T)**: An offline-trained XGBoost model classifies queries by category. Math and Code are instantly bypassed to the Fireworks API. Text and Sentiment are sent to the local model.
4. **Logprob-Based Cascade Fallback**: If the local Qwen 7B model's average logprob across the first 10 tokens drops below `0.6`, generation is aborted and the query falls back to the API.
5. **Cache-Aware Sticky Batching**: API tasks are batched sequentially by category via `asyncio.gather()` to maximize KV Cache hits on the Fireworks API.

**Local Fallback Model:** `Qwen2.5-7B-Instruct-GGUF` (bundled in the container).
**Fireworks API Model:** Dynamically parsed from `ALLOWED_MODELS` (regex searches for the smartest models for hard tasks).

## Status
- [x] Implement Semantic Router logic
- [x] Configure Local Model execution environment (GGUF bundled)
- [x] Setup Fireworks API routing & Pre-train XGBoost model
- [x] Build fail-safe exception handling for 404s and rate-limits
- [x] Update documentation to reflect Hackathon rule compliance (Headless Batch)
- [x] Isolate React Frontend Pitch Dashboard into `demo/` (Optional Pitch UI only)

## Important Rules
- Local models are legal and cost 0 tokens. They MUST be heavily utilized.
- All code must run strictly within 32GB of RAM and 8 vCPUs (No GPU).
- Do NOT use hardcoded API model names; always fall back on parsing the `ALLOWED_MODELS` environment variable.
