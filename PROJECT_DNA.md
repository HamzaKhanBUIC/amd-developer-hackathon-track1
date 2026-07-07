# AMD Hackathon Track 1: Astonishing Routing Agent

## Goal
Build a mathematically superior, visually astonishing AI routing agent that dynamically selects the cheapest Fireworks AI model while spending exactly 0 LLM inference tokens on the routing decision itself.

## Technical Architecture (Finalized)

We are implementing the **Zero-Token Semantic Pipeline (Tiers 1 & 2)**:

1. **Layer 1: Semantic Embedding Router (0 tokens, ~100ms)**
   - **Mechanism:** Convert incoming prompts into embeddings (using a fast, free local embedding model or extremely cheap API) and use Cosine Similarity against a vector store of predefined "intents" (e.g., greetings, basic translation).
   - **Action:** If similarity > 0.85, route immediately to Gemma 2B or Llama 3 8B.
2. **Layer 2: XGBoost Predictive Classifier (0 LLM tokens, ~5ms)**
   - **Mechanism:** If the prompt fails Layer 1, we extract prompt features (length, complexity markers) and run them through a trained XGBoost ML classifier.
   - **Data Source:** We will train the classifier using the open-source **Chatbot Arena preference dataset** (as used by RouteLLM) to accurately predict if a cheap model will suffice.
   - **Action:** Route to the cheapest capable model based on the ML prediction.

## UI / Frontend Strategy
- **Framework:** Next.js with TypeScript.
- **Styling:** Vanilla CSS with CSS Modules. We strictly refuse "AI slop" (generic Tailwind layouts). 
- **Design Language:** We will use Stitch-inspired, premium, sleek dark mode aesthetics featuring glassmorphism, dynamic micro-animations, and modern typography (e.g., Inter or Outfit). 
- **Demo Layout:** A split-screen chat interface. The user sees the prompt, and the UI visually traces the routing decision (Semantic Match vs ML Classifier), showing real-time token/cost savings compared to a baseline 70B model.

## File Structure
```
/frontend
  - next.js source
  - styles/ (Premium Vanilla CSS)
/backend
  - main.py (FastAPI)
  - semantic_router.py (Layer 1)
  - xgboost_router.py (Layer 2)
  - train_classifier.py (Data ingestion)
/docs
  - HACKATHON_SPRINT.md
PROJECT_DNA.md
.gitignore
```
