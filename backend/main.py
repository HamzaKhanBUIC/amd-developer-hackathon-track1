from fastapi import FastAPI
from pydantic import BaseModel
from router import route_query
from fireworks_client import generate_response, CHEAP_MODEL, EXPENSIVE_MODEL

app = FastAPI(title="AMD Hackathon Router API")

class QueryRequest(BaseModel):
    prompt: str

@app.post("/api/route")
async def api_route_query(request: QueryRequest):
    # Determine the model using Zero-Token Routing
    model_selected, routing_layer = route_query(request.prompt)
    
    # Generate the actual response
    response_text = await generate_response(request.prompt, model=model_selected)
    
    # Calculate simulated token savings for UI demonstration
    tokens_saved = 0
    if model_selected == CHEAP_MODEL:
        # Assuming an average of 300 tokens per interaction saved by not using 70B
        tokens_saved = 300
        
    return {
        "model_selected": model_selected,
        "tokens_saved": tokens_saved,
        "response": response_text,
        "routing_layer": routing_layer
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
