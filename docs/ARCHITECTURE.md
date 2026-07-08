# Architecture & Required Skills

# Architecture & Track 1 Solution Design

## Required Skill Sets & Team Alignment

### 1. Headless Batch Router (The Core Engine)
- **Objective:** The grading environment does NOT use FastAPI. We must run a headless `agent.py` script.
- **Implementation:** Uses `asyncio.gather` for concurrent Fireworks API calls, and an `asyncio.Semaphore(1)` to strictly serialize local CPU inference.

### 2. Machine Learning & Embeddings (XGBoost)
- **Objective:** Route queries based on complexity to minimize token costs.
- **Implementation:** We train an XGBoost classifier offline. The **pre-trained** `xgboost_router.json` weight file is bundled in the repository, so the grading script loads it instantly without needing to train it on the judge's machine.

### 3. Local Model Integration (Qwen 1.5B)
- **Objective:** Zero-token inference for simple tasks.
- **Implementation:** We bundle the `Qwen 2.5 1.5B Q4_K_M` GGUF model directly inside the Docker image to comply with the rules. It uses exactly 2 threads to stay within the 2 vCPU / 4GB RAM limit.

### 4. Next.js & Frontend (Pitch Demo Bonus)
- **Objective:** The frontend is NOT evaluated by the grading script. It exists purely in the `demo/` folder to create a premium glassmorphic UI for our 3-minute pitch video to win aesthetic points.
