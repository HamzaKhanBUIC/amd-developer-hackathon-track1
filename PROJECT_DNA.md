# Project DNA: AMD Zero-Token API Router

## Core Identity
This project is built to win Track 1 of the AMD Developer Hackathon. The primary objective is to implement a robust query routing mechanism that maximizes output accuracy while minimizing token consumption on the Fireworks AI API (Target: 600-1000 Tokens).

## 2. Architecture Overview
This is a headless batch processor utilizing an advanced **2-Tier Zero-Token Router** to guarantee an 80% (16/19) accuracy gate while dominating the token efficiency leaderboard within an exact **4 GB RAM, 2 vCPU, 10-minute timeout** environment.

1. **XGBoost Category Gating**: An offline-trained XGBoost model classifies queries. Easy categories (Factual, Sentiment, Summarization, NER) with high confidence (>75%) are routed to the local model.
2. **Hard Logic API Fallback**: Math, Logic, and Code tasks strictly bypass local execution and hit the Fireworks API (expensive/code models) to preserve the 80% accuracy gate.
3. **Extreme API Compression**: Fireworks API system prompts are compressed to 3-5 word micro-instructions with aggressively tight `max_tokens` and strict `stop` sequences to prevent token "yapping".
4. **Strict Concurrency Limits**: The local Qwen 3B model is rigidly bound to `n_threads=2` and serialized via `asyncio.Semaphore(1)` to ensure the Docker container never exceeds 2 vCPUs or 4GB of RAM.

**Local Fallback Model:** `Qwen2.5-3B-Instruct-Q4_K_M.gguf` (bundled in the container).
**Fireworks API Model:** Dynamically parsed from `ALLOWED_MODELS`.

## Status
- [x] Implement 2-Tier Semantic Router logic
- [x] Configure Local Model execution environment (Qwen 3B GGUF strictly limited to 2 threads)
- [x] Setup Fireworks API compression (3-word prompts, strict stop sequences)
- [x] Fix runtime import mismatches
- [x] Update documentation to reflect Hackathon rule compliance

## Important Rules
- Local models are legal and cost 0 tokens. They MUST be heavily utilized.
- All code must run strictly within 4GB of RAM and 2 vCPUs (No GPU).
- Do NOT use hardcoded API model names; always fall back on parsing the `ALLOWED_MODELS` environment variable.
- All API calls must route exclusively through `FIREWORKS_BASE_URL`.
