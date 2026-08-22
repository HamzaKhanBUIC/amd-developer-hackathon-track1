# AMD Developer Hackathon: Zero-Token API Router

This project is an advanced AI Agent Router built for **Track 1** of the AMD Developer Hackathon.

Our goal is simple: **Maximize Accuracy while Minimizing Token Cost**. 
We achieve this through a highly optimized, 2-tier routing architecture that aggressively answers tasks using zero-token local execution whenever possible, and only escalates to expensive API models when strictly necessary for hard reasoning tasks.

## The 2-Tier Routing Architecture

1. **Layer 1: XGBoost Category Gating**
   - **Cost:** $0.00
   - We run a tiny offline XGBoost classifier over text embeddings to detect the task Category. 
   - **Math, Logic, Code** -> Instantly bypassed to the Fireworks API. Small models hallucinate these.
   - **Sentiment, Factual, Summarization, NER** -> Routed to the local Qwen 3B model (if confidence > 75%).

2. **Layer 2: Extreme API Compression & Batching**
   - **Cost:** API rates (Hyper-Optimized)
   - When hitting the Fireworks API for hard tasks, we compress system prompts down to 3-5 word micro-instructions (e.g. "Solve concisely.").
   - We inject strict `max_tokens` ceilings and aggressive `stop` sequences to prevent token "yapping" and over-generation.
   - API tasks are batched sequentially by category. We parse `ALLOWED_MODELS` to pick the smartest model for hard tasks.

## Environment & Constraints Compliance
- **Local Model Constraints:** The bundled `Qwen 2.5 3B GGUF` is strictly hardcoded to `n_threads=2` to ensure the hackathon's **2 vCPU limit** is never breached.
- **Memory Safety:** Local execution is serialized using a `Semaphore(1)` to guarantee it runs safely within the **4GB RAM limit**.
- **Execution Stability:** Hardened with explicit API timeouts to guarantee we never fail the **10-minute maximum execution window**.

## Current Project Status
- **Backend:** 100% Complete. The routing engine and fallback logic are fully implemented in Python and tested to be robust against 404s, rate limits, and hang conditions.
- **Models:** Configured to read `ALLOWED_MODELS` from the environment dynamically as required by the hackathon organizers. 
- **Output Validation:** Output is strictly compliant with `[{"task_id": "...", "answer": "..."}]`. CRLF bash execution bugs pre-fixed.

## How to Run (Headless Grading Simulation)

1. Clone this repository.
2. Build the docker image: `docker build -t amd-router .`
3. Run it via Docker mapping the input/output volumes as specified by the grading harness. 
*(Alternatively, run `python judge_evaluator.py` locally to simulate the 2-tier logic and token savings).*
