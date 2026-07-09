# Project DNA: AMD Zero-Token API Router

## Core Identity
This project is built to win Track 1 of the AMD Developer Hackathon. The primary objective is to implement a robust query routing mechanism that maximizes output accuracy while minimizing token consumption on the Fireworks AI API.

## Technical Strategy
- **Zero-Token Local Execution**: We prioritize running a quantized Qwen 1.5B model on the provided 2vCPU / 4GB RAM environment for all simple tasks. **The Qwen 2.5 1.5B GGUF weights are bundled directly in the Docker image** to comply with the 10-minute network limit and <10GB constraint.
- **Dynamic API Routing**: When forced to use the Fireworks API, we dynamically read the allowed models from `ALLOWED_MODELS` and route to the most cost-effective model (e.g. `llama-v3p1-8b-instruct`) unless the prompt specifically demands a coding model or deep reasoning.
- **Machine Learning Complexity Router**: A **pre-trained** XGBoost classifier (`xgboost_router.json`) is bundled in the repo. It classifies query difficulty instantly without requiring training at runtime.
- **Headless Grading Harness**: The final grading environment does not use web servers (no FastAPI/Next.js). We use a highly concurrent `agent.py` script with `asyncio.gather` for API calls and `asyncio.Semaphore(1)` for strictly serialized local execution.
- **Fail-Safe Fallbacks**: If the Fireworks API returns a 404 or rate-limit error, we instantly fallback to a smaller API model, and if that fails, we fallback to the local Qwen model. This ensures a 100% completion rate.

## Status
- [x] Implement Semantic Router logic
- [x] Configure Local Model execution environment (GGUF bundled)
- [x] Setup Fireworks API routing & Pre-train XGBoost model
- [x] Build fail-safe exception handling for 404s and rate-limits
- [x] Update documentation to reflect Hackathon rule compliance (Headless Batch)
- [x] Isolate React Frontend Pitch Dashboard into `demo/` (Optional Pitch UI only)

## Important Rules
- Local models are legal and cost 0 tokens. They MUST be heavily utilized.
- All code must run strictly within 4GB of RAM.
- Do NOT use hardcoded API model names; always fall back on parsing the `ALLOWED_MODELS` environment variable.
