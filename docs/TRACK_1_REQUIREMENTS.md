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
- **Accuracy Gate (16/19 Tasks):** The output must actually be correct. There are exactly 19 fixed tasks. To pass the 80% accuracy gate, we must get at least 16 out of 19 correct. If the routing chooses a cheap model that hallucinates and we drop below 16, we fail. (Note: LLM judges aren't perfectly deterministic).
- **Token Efficiency:** If we pass the 80% accuracy gate, we are ranked strictly by how many tokens we saved.
- **Our Advantage (True Zero-Token Hybrid Router):** We will use an ultra-fast XGBoost model to determine query complexity. Easy tasks are routed to our embedded local 1.5B model (costing exactly 0 Fireworks API tokens). Hard tasks are fired asynchronously to the Fireworks API. This mathematically guarantees the highest possible token efficiency ranking.
- **Model Warnings:** Gemma 4 E4B is allowed but it is on-demand (~$7/hour when idle). We do **not** need Gemma to pass the gate, so we will strictly rely on Llama 3.1 and our local Qwen 1.5B to avoid draining our $50 Fireworks credits.

## 4. Hardware Limitations & Problems Avoided
> [!CAUTION]
> The grading environment is extremely restricted. If we violate these, the container will instantly fail.

1. **Memory & CPU:** We only have **4 GB RAM** and **2 vCPU**. 
   - *Our Solution:* We use a heavily quantized model `Qwen2.5-1.5B-Instruct-GGUF` (~1.1GB RAM). We limit local inference concurrency using `asyncio.Semaphore(1)`. We also enforce `n_threads=2` in `llama-cpp-python` to prevent CPU context switching overhead.
2. **Timeout:** The entire container must finish within **10 minutes**.
   - *Our Solution:* We use `asyncio.gather()` to ensure Fireworks API network calls run concurrently while the local CPU is blocked doing inference.
3. **Image Size:** The Docker image must be under **10 GB compressed**.
   - *Our Solution:* We bundle the `Qwen2.5` model weights directly into the Docker image as required by the latest rules, keeping the total size well under 2GB.

## 5. Submission Format (Headless Batch)
- **NOT A WEB SERVER:** The container does not spin up FastAPI or Next.js during grading.
- **I/O Protocol:** `agent.py` dynamically reads the paths from `os.environ.get("TASK_INPUT_PATH")` and `os.environ.get("TASK_OUTPUT_PATH")`.
- **Output:** It writes an array of `{"task_id": "...", "answer": "..."}` objects to `results.json` before exiting.
- **Exit Status:** Exits with code `0`.
