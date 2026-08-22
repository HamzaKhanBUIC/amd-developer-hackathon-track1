# Architecture & Required Skills

# Architecture & Track 1 Solution Design

## Required Skill Sets & Team Alignment
# Architecture & Track 1 Solution Design: The 5-Layer Hybrid Router

To maximize token efficiency while maintaining an absolute guarantee of passing the 80% (16/19) accuracy gate within a 4GB RAM environment, we have implemented an advanced 5-Layer routing pipeline.

## The Pipeline

### 1. Conditional Pre-computation Pruning
Before any routing occurs, we aggressively strip prompt bloat (whitespace removal, JSON flattening) using regex to save 10-30% on API input tokens. 
*Note: Pruning is automatically disabled for tasks categorized as Code or Logic to preserve critical formatting.*

### 2. "True Zero-Token" Semantic Cache
We embed incoming queries using the local `all-MiniLM-L6-v2` model.
If a query matches a cached query with `>0.95` cosine similarity, we return the cached answer. (Cost: 0 tokens).

### 3. Category-Calibrated Confidence Thresholds (C3T)
Our XGBoost classifier evaluates the embedding to predict the task **Category** and **Confidence**.
- **Math, Logic, Code Debugging, Code Generation**: Instantly bypassed to the Fireworks API. Small models hallucinate these confidently.
- **Sentiment, Summarization, NER, Factual Q&A**: Routed to the local Qwen 1.5B model.

### 4. Logprob-Based Cascade Fallback (Aggressive Abort)
When a task runs on the local Qwen 1.5B model, we monitor the average logprob of the first 10 tokens.
- If the average logprob drops below **0.6** (~55% confidence), it signifies a hallucination.
- **Action**: Instantly abort local generation and fallback to the Fireworks API.

### 5. Cache-Aware "Sticky" Batching
For tasks routed to the Fireworks API, we execute them using `asyncio.gather()`, grouped sequentially by category.
Sending all "Math" tasks together ensures they share the exact same System Prompt, triggering **KV Cache Hits (Prefix Caching)** on the Fireworks API, drastically reducing our input token billing.

---

## 4GB RAM Environment Constraints
Because we only have 2 vCPUs and 4GB RAM:
1. `llama-cpp-python` is restricted to `n_threads=2`.
2. Local inference uses `asyncio.Semaphore(1)` to ensure we do not OOM or thrash the CPU scheduler.
3. Fireworks API calls run concurrently (`asyncio.Semaphore(50)`) via `aiohttp` while the CPU is blocked by the local model.

## Implementation Details

### Machine Learning & Embeddings (XGBoost)
- **Objective:** Route queries based on complexity to minimize token costs.
- **Implementation:** We train an XGBoost classifier offline. The **pre-trained** `xgboost_router.json` weight file is bundled in the repository, so the grading script loads it instantly without needing to train it on the judge's machine.

### Local Model Integration (Qwen 1.5B)
- **Objective:** Zero-token inference for simple tasks.
- **Implementation:** We bundle the `Qwen 2.5 1.5B Q4_K_M` GGUF model directly inside the Docker image to comply with the rules. It uses exactly 2 threads to stay within the 2 vCPU / 4GB RAM limit.

- **Objective:** The frontend is NOT evaluated by the grading script. It exists purely in the `demo/` folder to create a premium glassmorphic UI for our 3-minute pitch video to win aesthetic points.
