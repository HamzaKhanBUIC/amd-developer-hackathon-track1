from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AMD Hackathon Router API")

class QueryRequest(BaseModel):
    prompt: str

@app.post("/api/route")
async def route_query(request: QueryRequest):
    # TODO: Implement Tier 1 (Semantic) and Tier 2 (XGBoost) routing logic here.
    # For now, return a mock response.
    return {
        "model_selected": "accounts/fireworks/models/llama-v3-8b-instruct",
        "tokens_saved": 150,
        "response": "This is a mock response from the router backend.",
        "routing_layer": "semantic"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
