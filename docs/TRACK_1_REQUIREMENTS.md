# Hackathon Track 1 Constraints & Scope

> [!CAUTION]
> **TEAM MANDATE:** Do not deviate from these constraints. Any models used outside of this list will result in immediate disqualification from Track 1.

## 1. Allowed Models & Dynamic Routing
> [!WARNING]
> We can no longer hardcode model names. We must read the `ALLOWED_MODELS` environment variable at runtime.
All API calls must route exclusively through `FIREWORKS_BASE_URL`.

**The Local Model Loophole (0 Tokens):**
The organizers explicitly clarified that local models and tokens used locally count as **zero** for the final score. We will exploit this by using a heavily quantized ~1.5B local model (`Qwen 2.5 1.5B Q4_K_M`) for easy tasks to bypass the API entirely.

## 2. Required Categories
The routing agent must be capable of handling queries across exactly 8 categories:
1. Factual Q&A
2. Math Reasoning
3. Sentiment Analysis
4. Summarization
5. NER (Named Entity Recognition)
6. Code Debugging
7. Logic Puzzles
8. Code Generation

## 3. Evaluation Criteria (How to Impress the Judges)
- **Accuracy Gate:** The output must actually be correct. If the routing chooses a cheap model that hallucinates, we fail.
- **Token Efficiency:** If we pass the accuracy gate, we are ranked strictly by how many tokens we saved.
- **Our Advantage (True Zero-Token Hybrid Router):** We will use an ultra-fast XGBoost model to determine query complexity. Easy tasks are routed to an embedded local 1.5B model (costing exactly 0 Fireworks API tokens). Hard tasks are fired asynchronously to the Fireworks API. This mathematically guarantees the highest possible token efficiency ranking.

## 4. Hardware Limitations & Problems to Avoid
> [!CAUTION]
> The grading environment is extremely restricted. If we violate these, the container will instantly fail.

1. **Memory & CPU:** We only have **4 GB RAM** and **2 vCPU**. 
   - *Problem:* Loading a 7B local model or running parallel local inference will cause an Out-Of-Memory (OOM) crash.
   - *Solution:* We must use a heavily quantized model like `Qwen 2.5 1.5B` (~1.1GB RAM) and limit local inference concurrency using `asyncio.Semaphore(1)`.
2. **Timeout:** The entire container must finish within **10 minutes**.
   - *Solution:* We must use `asyncio.gather()` to ensure Fireworks API network calls run concurrently while the local CPU is blocked doing inference.
3. **Image Size:** The Docker image must be under **10 GB compressed**. We must not bloat the image with web frameworks (Node.js/Next.js) since they are useless to the grading harness.

## 5. Submission Format (Headless Batch)
- **NOT A WEB SERVER:** The container must not spin up FastAPI or Next.js.
- **I/O Protocol:** It must read from `/input/tasks.json` on startup.
- **Output:** It must write an array of `{"task_id": "...", "answer": "..."}` objects to `/output/results.json` before exiting.
- **Exit Status:** Must exit with code `0`.
