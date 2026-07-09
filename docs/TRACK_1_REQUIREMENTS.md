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
- **Accuracy Gate (16/19 Tasks):** The output must actually be correct. There are exactly 19 fixed tasks. To pass the 80% accuracy gate, we must get at least 16 out of 19 correct. We guarantee this via **Category-Based Bypassing**: small local models hallucinate on Math and Code, so we NEVER route those tasks to the local model.
- **Token Efficiency:** If we pass the 80% accuracy gate, we are ranked strictly by how many tokens we saved.
- **Our Advantage (5-Layer Zero-Token Hybrid Router):** We will use an ultra-fast XGBoost model to determine query category. We implement Conditional Pre-computation Pruning to strip 10-30% input tokens. Easy tasks (Sentiment, NER) are routed to our embedded local 1.5B model (costing exactly 0 Fireworks API tokens) with a **Logprob-based Cascade Fallback** (aborting if avg logprob < 0.6). Hard tasks (Math, Code) are grouped sequentially via **Cache-Aware Sticky Batching** to trigger KV cache hits on the Fireworks API. This mathematically guarantees the highest possible token efficiency ranking.
- **Model Warnings:** We cannot hardcode models. We dynamically parse the `ALLOWED_MODELS` string to regex-match the smartest possible model (70b, 72b, etc.) for our hard tasks, ensuring we hit 19/19 accuracy. We avoid Gemma 4 E4B due to idle costs unless absolutely necessary.

## 4. Hardware Limitations & Problems Avoided
> [!CAUTION]
> The grading environment is extremely restricted. If we violate these, the container will instantly fail.

1. **Memory & CPU:** We have **32 GB RAM** and **8 vCPUs** (No GPU). 
   - *Our Solution:* With 32GB RAM, we can upgrade our embedded local model from 1.5B to a highly accurate `Qwen2.5-7B-Instruct-GGUF` or `Llama-3.1-8B-Instruct-GGUF` (~5-6GB RAM). We enforce `n_threads=8` in `llama-cpp-python` to maximize CPU usage.
2. **Timeout:** The entire container must finish within **10 minutes**.
   - *Our Solution:* We use `asyncio.gather()` to ensure Fireworks API network calls run concurrently while the local CPU is blocked doing inference across all 8 cores.
3. **Image Size:** The Docker image must be under **10 GB compressed**.
   - *Our Solution:* We bundle the `Qwen2.5` model weights directly into the Docker image as required by the latest rules, keeping the total size well under 2GB.

## 5. Submission Format (Headless Batch)
- **NOT A WEB SERVER:** The container does not spin up FastAPI or Next.js during grading.
- **I/O Protocol:** `agent.py` dynamically reads the paths from `os.environ.get("TASK_INPUT_PATH")` and `os.environ.get("TASK_OUTPUT_PATH")`.
- **Output:** It writes an array of `{"task_id": "...", "answer": "..."}` objects to `results.json` before exiting.
- **Exit Status:** Exits with code `0`.
