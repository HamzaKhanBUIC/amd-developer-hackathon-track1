# Role: Member 3 - Backend & AI (Python Stack)

## Focus Areas
You are responsible for the core logic of the hackathon submission: The Zero-Token Routing Engine.

## Required Skills / Best Practices
- **FastAPI**: Ensure the backend is fast, async, and type-safe using Pydantic.
- **Machine Learning**: `scikit-learn`, `xgboost`, and embedding models.
- **Data Engineering**: Handling the Chatbot Arena dataset to extract features for the XGBoost layer.

## Initial Tasks (Phase 1 & 2)
1. Clone the repo and navigate to `/backend`.
2. Generate/clean the mock Chatbot Arena dataset for training.
3. Implement `semantic_router.py` (Layer 1: Cosine Similarity).
4. Implement `xgboost_classifier.py` (Layer 2: Complexity routing).
5. Expose these via the FastAPI `/api/route` endpoint to the frontend.
