# AMD Developer Hackathon: ZeroToken Router

This project is an advanced AI Agent Router built for **Track 1: General-Purpose AI Agent** of the AMD Developer Hackathon.

Our goal is simple: **Maximize Accuracy while Minimizing Token Cost**. 
We achieve this through a highly optimized, 5-layer routing architecture that aggressively answers tasks using zero-token local execution whenever possible, and only escalates to expensive API models when strictly necessary.

## The 5-Layer Routing Architecture

1. **Layer 1: Regex Pruning Layer**
   - **Cost:** 0 tokens
   - We aggressively strip out conversational filler (e.g. "Can you tell me", "Please output"), polite phrasing, and redundant whitespace before processing. This alone saves a massive amount of output token overhead on every single API call.

2. **Layer 2: Semantic Caching Layer (MiniLM)**
   - **Cost:** 0 tokens
   - Before any processing, the prompt is embedded using `all-MiniLM-L6-v2`. If the exact semantic meaning exists in our local cache (cosine similarity > 0.85), we instantly return the cached answer, avoiding any generation costs.

3. **Layer 3: XGBoost Intent Router (Category Bypass)**
   - **Cost:** 0 tokens
   - We run a highly optimized XGBoost Machine Learning model (`xgboost_router.json`) to classify the intent of the prompt locally on the CPU in under 5 milliseconds.

4. **Layer 4: Local Fallback Engine (Qwen 1.5B)**
   - **Cost:** 0 tokens
   - Once XGBoost identifies an "easy" category (like Sentiment or basic Factual questions), the query is routed to a fully local `Qwen2.5-1.5B-Instruct` model running via `llama.cpp`. This model runs entirely on the CPU in our container. 

5. **Layer 5: Premium API Shunting (Chain-of-Draft)**
   - **Cost:** Minimal API rates
   - Only when a query is classified as highly complex (e.g. Code, Math) is it routed to the premium Fireworks API. We explicitly instruct the model to use Chain-of-Draft (CoD) prompting, forcing it to think efficiently and output minimal tokens.

## How to Run & Judge (Option B)

We have packaged everything to run flawlessly in an isolated environment. 

### Local Docker Build & Run

If you wish to build the container locally from this repository:

1. Clone this repository:
   ```bash
   git clone https://github.com/HamzaKhanBUIC/amd-developer-hackathon-track1.git
   cd amd-developer-hackathon-track1
   ```

2. Build the Docker image (this downloads the 1.5B local model into the container):
   ```bash
   docker build -t amd-hackathon-router:latest .
   ```

3. Run the container for evaluation:
   ```bash
   docker run --rm \
     -e FIREWORKS_API_KEY="your-api-key" \
     -e ALLOWED_MODELS="accounts/fireworks/models/llama-v3p1-8b-instruct,accounts/fireworks/models/llama-v3p1-70b-instruct,accounts/fireworks/models/qwen2p5-coder-32b-instruct" \
     -e TASK_INPUT_PATH="/data/input.json" \
     -e TASK_OUTPUT_PATH="/data/output.json" \
     -v $(pwd)/data:/data \
     amd-hackathon-router:latest
   ```

*Note: You can place your `input.json` in a local `data/` folder, and the results will be written to `data/output.json`.*
