# Project DNA: AMD Zero-Token API Router

## Core Identity
This project is built to win Track 1 of the AMD Developer Hackathon. The primary objective is to implement a robust query routing mechanism that maximizes output accuracy while minimizing token consumption on the Fireworks AI API.

## Technical Strategy
- **Zero-Token Local Execution**: We prioritize running a quantized Qwen 1.5B model on the provided 2vCPU / 4GB RAM environment for all simple tasks.
- **Dynamic API Routing**: When forced to use the Fireworks API, we dynamically read the allowed models from `ALLOWED_MODELS` and route to the most cost-effective model (e.g. `llama-v3p1-8b-instruct`) unless the prompt specifically demands a coding model or deep reasoning.
- **Semantic Caching**: All outputs are cached using `all-MiniLM-L6-v2` embeddings, allowing duplicate tasks to cost zero API tokens and zero local inference time.
- **Fail-Safe Fallbacks**: If the Fireworks API returns a 404 or rate-limit error, we instantly fallback to a smaller API model, and if that fails, we fallback to the local Qwen model. This ensures a 100% completion rate.

## Status
- [x] Implement Semantic Router logic
- [x] Configure Local Model execution environment
- [x] Setup Fireworks API routing
- [x] Build fail-safe exception handling for 404s and rate-limits
- [x] Update documentation to reflect Hackathon rule compliance
- [ ] Finalize React Frontend dashboard to visualize routing decisions

## Important Rules
- Local models are legal and cost 0 tokens. They MUST be heavily utilized.
- All code must run strictly within 4GB of RAM.
- Do NOT use hardcoded API model names; always fall back on parsing the `ALLOWED_MODELS` environment variable.
