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
AMD Hackathon Judging FAQ and Self-Check Guide
Quick Note
The leaderboard is still catching up. Some errors are infrastructure-related and do not reflect your project quality.
Please do not keep resubmitting to move up the queue. It does not help and it adds more load.
Exact internal judge prompts and hidden test cases are not shared. The scoring criteria are stable: correctness, required format, reliability, runtime, and track-specific quality.
Public Validation Examples

We are sharing a public validation set made from retired scoring examples. These examples are no longer part of final judging.

Use them to check:
- Input/output format.
- Expected answer quality.
- Style expectations.
- Local container behavior.

Final judging will use a separate hidden set with the same format, difficulty, and scoring principles. Passing the public examples is helpful, but it does not guarantee a final score.

Sample Tasks
These are public validation examples from retired scoring cases. They are provided for local testing and are not part of final judging.

Track 1 sample tasks

T01 - factual_knowledge
Prompt: Name the three primary colors in the RGB color model and briefly explain why displays use RGB instead of RYB.
Expected: Correctly identifies red, green, and blue as the three primary colors, and explains that RGB is used in displays because screens emit light additively (additive color mixing), whereas RYB applies to subtractive mixing of physical pigments.

T01b - factual_knowledge
Prompt: What is the difference between machine learning and deep learning? Briefly explain how each works.
Expected: Distinguishes ML as algorithms that learn patterns from data (statistical or feature-based), and deep learning as a subset of ML using multi-layer neural networks. Explains that deep learning automatically extracts features from raw data, while traditional ML often requires manual feature engineering. Must make the subset relationship clear.

T01c - factual_knowledge
Prompt: Explain the difference between RAM and ROM in a computer. What is each type used for?
Expected: RAM (Random Access Memory) is volatile and fast, used for temporary storage of active programs and data. ROM (Read-Only Memory) is non-volatile and stores permanent firmware or BIOS. Must correctly distinguish volatility, speed, and use case for both types.

T02 - mathematical_reasoning
Prompt: A warehouse starts with 2,400 units. In Q1 it sells 37% of stock. In Q2 it restocks 800 units. In Q3 it sells 640 units. How many units remain at the end of Q3?
Expected: Correctly arrives at 1,672 units remaining. The calculation must follow: 2400 minus 888 (37% of 2400) equals 1512, plus 800 equals 2312, minus 640 equals 1672. Minor arithmetic shown or implied.

T02b - mathematical_reasoning
Prompt: A recipe requires 3/4 cup of sugar for 12 cookies. How much sugar is needed for 30 cookies? If sugar costs $2.40 per cup, what is the total cost of sugar for 30 cookies?
Expected: Correctly calculates: 30 cookies need (3/4 × 30/12) = 1.875 cups of sugar. Total cost = 1.875 × $2.40 = $4.50. Both answers must be correct. Minor rounding (1.87 or 1.88 cups) is acceptable if the final cost rounds correctly to $4.50.

T03 - sentiment_classification
Prompt: Classify the sentiment of this customer review as Positive, Negative, or Neutral and give a one-sentence reason: 'The product arrived two days late and the packaging was damaged, but the item worked perfectly and customer support resolved my complaint within an hour.'
Expected: Classifies the sentiment as Mixed, Neutral, or Positive (any of these three labels is acceptable), provided the one-sentence reason acknowledges both the negative experience (late delivery, damaged packaging) and the positive outcome (working product, responsive support). A Negative classification does not pass. A reason that acknowledges only one side does not pass, regardless of the label.

T03b - sentiment_classification
Prompt: Classify the sentiment of this tweet as Positive, Negative, or Neutral and give a one-sentence reason: 'Just got my order. Box was dented and the manual was missing, but honestly the device itself is flawless and set up in under 5 minutes.'
Expected: Classifies as Mixed, Neutral, or Positive (any of these three labels is acceptable), provided the reason acknowledges both negative aspects (dented box, missing manual) and positive aspects (flawless device, fast setup). A Negative classification does not pass. A reason that acknowledges only one side does not pass, regardless of the label.

T04 - text_summarization
Prompt: Summarize the following passage in exactly two sentences:

'Machine learning is increasingly deployed in healthcare for diagnosis, treatment planning, and patient monitoring. These systems analyse medical images, predict patient deterioration, and spot patterns in electronic health records that might be missed by human clinicians. However, concerns remain about model interpretability, data privacy, liability when errors occur, and the potential for algorithmic bias to worsen existing healthcare disparities. Regulatory frameworks are still catching up with the pace of deployment, creating uncertainty for healthcare providers and technology developers alike.'
Expected: Produces exactly two sentences. The summary captures both the opportunity (ML assisting clinical tasks such as image analysis, prediction, and pattern recognition) and the key challenges (interpretability, bias, privacy, liability, and regulatory lag). Omitting either side, or producing more or fewer than two sentences, does not pass.

T04b - text_summarization
Prompt: Summarize the following passage in exactly three bullet points, each no longer than 15 words:

'Remote work has transformed how companies operate globally. Employees gain flexibility and reduced commute times, leading to reported improvements in work-life balance. However, challenges persist around collaboration, company culture, and the blurring of personal and professional boundaries. Organisations are responding by investing in digital collaboration tools and rethinking office space as a hub for social and creative work rather than daily attendance.'
Expected: Produces exactly three bullet points, each under 15 words. Points must cover: (1) remote work benefits such as flexibility and work-life balance, (2) challenges around collaboration, culture, and boundary blur, (3) organisational response through digital tools and reimagined office use. More or fewer than three bullets, or any bullet exceeding 15 words, does not pass.

T05 - named_entity_recognition
Prompt: Extract all named entities from the following text and label each as PERSON, ORGANIZATION, LOCATION, or DATE:

'On March 15 2023, Sundar Pichai announced that Google would open a new AI research lab in Zurich, partnering with ETH Zurich to focus on large language model safety.'
Expected: Correctly identifies and labels all five distinct entities: Sundar Pichai (PERSON), March 15 2023 (DATE), Google (ORGANIZATION), Zurich (LOCATION), ETH Zurich (ORGANIZATION). All five must be present with correct labels. Missing an entity or mislabelling more than one does not pass.