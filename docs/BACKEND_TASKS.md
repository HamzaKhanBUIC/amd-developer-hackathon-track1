# Backend Development Guide & Tasks

This document outlines the architecture of the backend for the AMD Zero-Token Router and details the pending tasks required to finalize the integration.

## Current Architecture

Our backend is a Python-based FastAPI application designed for extreme token efficiency using a two-tier routing system:

1.  **FastAPI (`main.py`)**: The primary web server exposing the `/api/route` endpoint. It accepts a `prompt` and returns the generated `response`, the `model_selected`, the `tokens_saved`, and the `routing_layer` used.
2.  **Semantic Router (`router.py`)**: The core logic. 
    *   **Layer 1 (Semantic):** Uses `SentenceTransformer('all-MiniLM-L6-v2')` to do a fast cosine-similarity check against known "easy" intents.
    *   **Layer 2 (ML Classifier):** If Layer 1 fails, it falls back to a trained `XGBoost` model to classify if the prompt requires a cheap 8B model or an expensive 70B model.
3.  **LLM Generation (`fireworks_client.py`)**: Connects to the Fireworks AI API to actually run the inference on the chosen model (e.g., Llama 3 8B or 70B).
4.  **Training Pipeline (`train_model.py`)**: Script to train the XGBoost classifier and generate `xgboost_router.json` and `tfidf_vectorizer.pkl`.

## Pending Tasks for Backend Developer

### 1. Enable CORS in `main.py`
The frontend runs on `http://localhost:3000` (Next.js) and the backend runs on `http://localhost:8000` (FastAPI). You must add `CORSMiddleware` to `main.py` to allow cross-origin requests, or the frontend will fail to fetch data.
*   **Action**: Import `CORSMiddleware` from `fastapi.middleware.cors` and add it to the `app`. Allow origins `["http://localhost:3000"]`.

### 2. Run the Training Script
The ML classifier relies on pre-trained weights.
*   **Action**: Run `python train_model.py` locally to ensure `xgboost_router.json` and `tfidf_vectorizer.pkl` are generated in the `/backend` directory before starting the FastAPI server.

### 3. Implement Chat History (Optional but Recommended)
Currently, the `/api/route` endpoint only accepts a single `prompt: str`.
*   **Action**: Update the `QueryRequest` Pydantic model to optionally accept a `messages` array so the LLM has context of previous interactions.

### 4. Optimize the Fireworks API Client
Ensure that `fireworks_client.py` has proper asynchronous error handling (e.g., timeouts, retries, and API key validation) in case the Fireworks API experiences downtime.

### How to Run Locally
```bash
cd backend
pip install -r requirements.txt
python train_model.py
uvicorn main:app --reload --port 8000
```
