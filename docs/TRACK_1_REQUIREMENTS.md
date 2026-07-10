# Hackathon Track 1 Constraints & Scope
# SOURCE: Official AMD Developer Hackathon Participant Submission Guide (updated Jul 10)

> [!CAUTION]
> **TEAM MANDATE:** Do not deviate from these constraints. Any models used outside of the `ALLOWED_MODELS` list will result in immediate disqualification from Track 1.

## 1. Allowed Models & Dynamic Routing
> [!WARNING]
> We can no longer hardcode model names. We must read the `ALLOWED_MODELS` environment variable at runtime (comma-separated list).
> All API calls must route exclusively through `FIREWORKS_BASE_URL`.
> **`ALLOWED_MODELS` is a comma-separated list of permitted Fireworks AI model IDs, published on launch day.**

```python
import os
api_key  = os.environ["FIREWORKS_API_KEY"]   # provided by harness
base_url = os.environ["FIREWORKS_BASE_URL"]  # ALL Fireworks calls must go through this
models   = os.environ["ALLOWED_MODELS"].split(",")  # exact model IDs published on launch day
```

> [!IMPORTANT]
> Calls that bypass `FIREWORKS_BASE_URL` will **not be recorded** and the submission will score **zero tokens**.
> Do not hardcode model IDs — read from `ALLOWED_MODELS` at runtime.

## 2. The Local Model Strategy (CONFIRMED VALID — 0 Tokens)

> [!TIP]
> **"Run as many local models as you need, they cost zero toward your score, and make as few external Fireworks API calls as possible while still clearing the accuracy gate."**

- Local models and tokens used locally count as **zero** for the final score.
- Local model inference inside the container is permitted and counts toward **accuracy**, but not toward the **token score**.
- A flagged `ZERO_API_CALLS` marker is **not a failure** — it is a valid strategy.
- **RAM Budget for local models:**
  - 2B–3B 4-bit quantized models are **safe**.
  - 7B 4-bit **fills the full RAM budget**, leaving no room for agent code → **DO NOT USE 7B locally**.
  - Our current `Qwen2.5-1.5B-Q4_K_M` is safe but too small for accuracy. **Upgrade to 3B Q4_K_M.**

## 3. Required Categories (8 total)
Your agent will be evaluated across **all eight categories**:

| # | Category | What it covers |
|---|----------|---------------|
| 1 | Factual knowledge | Explaining concepts, definitions, how things work |
| 2 | Mathematical reasoning | Multi-step arithmetic, percentages, word problems, projections |
| 3 | Sentiment classification | Labelling sentiment and justifying the classification |
| 4 | Text summarisation | Condensing passages to a specific format or length constraint |
| 5 | Named entity recognition | Extracting and labelling entities (person, org, location, date) |
| 6 | Code debugging | Identifying bugs in code snippets and providing corrected implementations |
| 7 | Logical / deductive reasoning | Constraint-based puzzles where all conditions must be satisfied |
| 8 | Code generation | Writing correct, well-structured functions from a spec |

## 4. Official Practice Tasks (Use These to Test Locally!)
```json
[
  { "task_id": "practice-01", "prompt": "What is the capital of Australia, and what body of water is it near?" },
  { "task_id": "practice-02", "prompt": "A store has 240 items. It sells 15% on Monday and 60 more on Tuesday. How many items remain?" },
  { "task_id": "practice-03", "prompt": "Classify the sentiment of this review: The battery life is great, but the screen scratches too easily." },
  { "task_id": "practice-04", "prompt": "Summarize the following in exactly one sentence: [your own sample paragraph here]." },
  { "task_id": "practice-05", "prompt": "Extract all named entities and their types from: Maria Sanchez joined Fireworks AI in Berlin last March." },
  { "task_id": "practice-06", "prompt": "This function should return the max of a list but has a bug: def get_max(nums): return nums[0]. Find and fix it." },
  { "task_id": "practice-07", "prompt": "Three friends, Sam, Jo, and Lee, each own a different pet: cat, dog, bird. Sam does not own the bird. Jo owns the dog. Who owns the cat?" },
  { "task_id": "practice-08", "prompt": "Write a Python function that returns the second-largest number in a list, handling duplicates correctly." }
]
```

## 5. Evaluation Criteria
- **Accuracy Gate:** LLM-Judge evaluates each answer. Submissions below threshold are excluded from leaderboard. Local model answers count fully toward accuracy!
- **Token Efficiency:** Submissions passing the accuracy gate are ranked ascending by total Fireworks tokens recorded by the **judging proxy**. Fewer API tokens = higher rank.

> [!NOTE]
> "The underlying task prompts are identical for every team, but your own system prompt (verbosity instructions, formatting requests, etc.) affects your **input** token count, and your model's response length affects **output** tokens."

> [!TIP]
> "Don't over-optimize output length early — focus first on your routing logic and which local models you use."

## 6. Hardware Limitations
> [!CAUTION]
> The grading environment is extremely restricted. Violating these means instant failure.

1. **Memory & CPU:** 4 GB RAM, 2 vCPUs. No GPU.
2. **Timeout:** Entire container must finish within **10 minutes**.
3. **Image Size:** Must be under **10 GB compressed**.

## 7. Submission Format & I/O
- Read tasks from `/input/tasks.json` on startup.
- Write results to `/output/results.json` before exiting.
- Schema: `[{"task_id": "...", "answer": "..."}]`
- **Do not hardcode or cache answers** — evaluation uses **unseen prompt variants**.
- Exit code 0 on success, non-zero on failure.
- Rate limited to **10 submissions per hour per team**.

## 8. Official Troubleshooting Guide
| Status | Meaning & Fix |
|--------|---------------|
| `PULL_ERROR` | Image not public, or not `linux/amd64`. Apple Silicon needs `docker buildx build --platform linux/amd64` |
| `RUNTIME_ERROR` | Container exited with non-zero code. Check container logs — agent crashed. |
| `TIMEOUT` | Didn't finish in 10 min. Check for hangs, infinite loops, excessive retries. |
| `OUTPUT_MISSING` | Exited cleanly but never wrote `/output/results.json`. |
| `INVALID_RESULTS_SCHEMA` | JSON not in right format. Each entry needs `task_id` AND `answer`. |
| `MODEL_VIOLATION` | Called a model not in `ALLOWED_MODELS`. Read from env var — don't hardcode. |
| `IMAGE_TOO_LARGE` | Image over 10 GB compressed. |
| `ACCURACY_GATE_FAILED` | Answers scored below threshold. Quality issue with agent answers. |
