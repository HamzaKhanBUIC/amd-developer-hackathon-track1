from fastapi import FastAPI
from pydantic import BaseModel
from router import route_query
from fireworks_client import generate_response_api, CHEAP_MODEL, EXPENSIVE_MODEL

app = FastAPI(title="AMD Hackathon Router API")

class QueryRequest(BaseModel):
    prompt: str

@app.post("/api/route")
async def api_route_query(request: QueryRequest):
    # Determine the model using Zero-Token Routing
    # determine_category should probably be imported or simulated here, but route_query now takes (pruned, category, emb)
    # Let's import determine_category
    from router import determine_category, prune_prompt
    cat = determine_category(request.prompt)
    pruned = prune_prompt(request.prompt, cat)
    model_selected, routing_layer, _, _ = route_query(pruned, cat)
    
    # Generate the actual response
    response_text = await generate_response_api(request.prompt, model=model_selected, category=cat)
    
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
