# Hackathon Track 1 Constraints & Scope

> [!CAUTION]
> **TEAM MANDATE:** Do not deviate from these constraints. Any models used outside of the `ALLOWED_MODELS` list will result in immediate disqualification from Track 1.

## 1. Allowed Models & Dynamic Routing
> [!WARNING]
> We can no longer hardcode model names. We must read the `ALLOWED_MODELS` environment variable at runtime (comma-separated list).
> All API calls must route exclusively through `FIREWORKS_BASE_URL`.

**The Local Model Loophole (0 Tokens):**
The organizers explicitly clarified that local models and tokens used locally count as **zero** for the final score. We exploit this by using a heavily quantized ~1.5B local model (`Qwen 2.5 1.5B Q4_K_M`) for easy tasks to bypass the API entirely. This guarantees the lowest possible token score.
*Note: A flagged `ZERO_API_CALLS` marker alongside the result is perfectly valid—it just means our local strategy worked.*

## 2. Required Categories
The routing agent must handle queries across exactly 8 categories:
1. Factual Q&A (Explaining concepts, definitions)
2. Mathematical reasoning (Multi-step arithmetic, word problems)
3. Sentiment classification (Labelling and justifying)
4. Text summarisation (Condensing to specific format)
5. Named entity recognition (Extracting person, org, location, date)
6. Code debugging (Identifying bugs and correcting)
7. Logical / deductive reasoning (Constraint-based puzzles)
8. Code generation (Writing well-structured functions)

## 3. Evaluation Criteria
- **Accuracy Gate:** The LLM-Judge evaluates each answer. We must pass the accuracy threshold to make the leaderboard. Local model answers count fully toward accuracy!
- **Token Efficiency:** Submissions that pass the accuracy gate are ranked ascending by total Fireworks tokens recorded by the judging proxy. Fewer API tokens = higher rank.

## 4. Hardware Limitations & Problems Avoided
> [!CAUTION]
> The grading environment is extremely restricted. If we violate these, the container will instantly fail.

1. **Memory & CPU:** We have **4 GB RAM** and **2 vCPUs** (No GPU). 
   - *Our Solution:* We bundle the `Qwen2.5-1.5B-Instruct-Q4_K_M` model weights directly into the Docker image. At ~1.1GB, it fits comfortably inside the 4GB RAM budget alongside our Python agent code. We enforce `n_threads=os.cpu_count() or 2` and `n_ctx=2048` to avoid CPU thrashing and Out-Of-Memory errors.
2. **Timeout:** The entire container must finish within **10 minutes**.
   - *Our Solution:* We use `asyncio.gather()` to ensure API network calls run concurrently while the local CPU is doing inference.
3. **Image Size:** The Docker image must be under **10 GB compressed**.
   - *Our Solution:* Even with our bundled weights, our Docker image is <2GB.

## 5. Submission Format & I/O
- Read tasks from `/input/tasks.json` on startup.
- Write results to `/output/results.json` before exiting. Both must use the schema `[{"task_id": "...", "prompt"/"answer": "..."}]`.
- **Environment Variables:** Must use injected `FIREWORKS_API_KEY`, `FIREWORKS_BASE_URL`, and `ALLOWED_MODELS`.
- Exit with code `0`.

## 6. Official Troubleshooting Guide
If the submission fails, it is one of these reasons:
- **PULL_ERROR:** Image not public or not `linux/amd64`.
- **RUNTIME_ERROR:** Container exited with non-zero code (Agent crashed).
- **TIMEOUT:** Didn't finish in 10 minutes (Hangs, infinite loops).
- **OUTPUT_MISSING:** Container exited cleanly but didn't write `/output/results.json`.
- **INVALID_RESULTS_SCHEMA:** Results not formatted properly.
- **MODEL_VIOLATION:** Called a model outside `ALLOWED_MODELS`.
- **IMAGE_TOO_LARGE:** Image > 10GB compressed.
- **ACCURACY_GATE_FAILED:** Container ran fine but answers were too wrong (Scored below threshold).
