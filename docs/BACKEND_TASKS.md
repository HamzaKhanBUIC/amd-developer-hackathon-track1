# Backend Development Guide & Tasks

This document is the **master guide for the backend developer**. It explains the current state of the backend repository, the architecture, and the precise, step-by-step tasks you need to complete to finish the AMD Zero-Token Router integration.

---

## 🏗️ 1. Current State & Architecture

The backend is built with **Python 3**, **FastAPI**, **SentenceTransformers**, and **XGBoost**. It acts as a highly efficient semantic routing layer that intercepts LLM requests and decides the cheapest way to fulfill them.

### Important Files
1. **`main.py`**: The FastAPI server entry point. It defines the `/api/route` POST endpoint.
2. **`router.py`**: The core intelligence. It contains `route_query()`, which uses a 2-tier funnel:
   * **Tier 1 (Semantic)**: Uses `all-MiniLM-L6-v2` to run a local cosine similarity check against known easy intents. Costs 0 tokens.
   * **Tier 2 (ML Classifier)**: Uses a trained `XGBoost` model to predict if the query needs the cheap `26b` model, the heavy `31b` reasoning model, or the specific `kimi` code model. Costs 0 tokens.
3. **`generate_dataset.py` & `train_model.py`**: Scripts you must run to synthesize data across the 8 required hackathon categories and generate the `.json` weights for the XGBoost model.
4. **`fireworks_client.py`**: Handles the actual async API calls to the Fireworks AI API.

---

## 🚀 2. Your Tasks

Your primary goal is to **finalize the API configuration so the Next.js frontend can communicate with it flawlessly, and ensure the local ML routing models are properly generated.**

### Task A: Fix CORS (Cross-Origin Resource Sharing)
Currently, the frontend (running on `http://localhost:3000`) will be blocked by the browser when it tries to talk to FastAPI (running on `http://localhost:8000`).
1. Open `main.py`.
2. Import the CORS middleware: `from fastapi.middleware.cors import CORSMiddleware`
3. Add the middleware to the `app` instance:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Task B: Generate Data & Train the XGBoost Router
The `router.py` file expects `xgboost_router.json` to exist in the root folder, otherwise it defaults to the expensive 31B fallback model. (Note: TF-IDF has been fully removed, we now pipe dense vectors directly).
1. Open a terminal in the `/backend` folder.
2. Make sure you have installed the requirements: `pip install -r requirements.txt`.
3. Generate the 8-category dataset: `python generate_dataset.py` (Wait for it to finish and generate `dataset.csv`).
4. Run the training script: `python train_model.py`.
5. Verify that the weight file (`xgboost_router.json`) has been generated in the folder.

### Task C: Implement Chat History / Context (Important)
Right now, the `QueryRequest` Pydantic model in `main.py` only accepts a single `prompt: str`. This means the chatbot cannot remember previous messages in the conversation.
1. Modify `QueryRequest` in `main.py` to accept an array of messages:
   ```python
   class Message(BaseModel):
       role: str
       content: str
       
   class QueryRequest(BaseModel):
       messages: list[Message]
   ```
2. Update the `fireworks_client.py` so that it passes the entire array of messages to the Fireworks API, rather than just a single prompt string. (The `router.py` can just extract the `content` of the *last* message to determine routing).

### Task D: Error Handling
* Ensure that if the Fireworks API key is missing or invalid, the backend returns a clear `HTTPException (500)` rather than crashing the server.
* Ensure that if the ML models fail to load, the server logs a warning but continues running by defaulting to the fallback model (this is partially implemented in `router.py`, just verify it).

---

## 🛠️ 3. How to Run & Test

1. Add your Fireworks API Key to your environment: `export FIREWORKS_API_KEY="your_key_here"`
2. Open a terminal in the `/backend` folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Generate data & Train models: `python generate_dataset.py` then `python train_model.py`
5. Run the server: `uvicorn main:app --reload --port 8000`
6. Test the health endpoint by visiting `http://localhost:8000/health` in your browser.
