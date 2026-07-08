import os
import xgboost as xgb
import torch
from sentence_transformers import SentenceTransformer, util

# Check for AMD ROCm / CUDA availability
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load XGBoost globally (0 inference overhead latency)
try:
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model("xgboost_router.json")
    models_loaded = True
except Exception as e:
    print("Warning: XGBoost model not found. Run train_model.py first.")
    models_loaded = False

# Layer 1: Semantic Router (Lightweight local embedding model)
# all-MiniLM-L6-v2 is extremely fast. We load it on the GPU (ROCm) if available.
print(f"Loading Semantic Router (MiniLM) on {device.upper()}...")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Define specific semantic intents that are guaranteed to be "Easy"
EASY_INTENTS = [
    "Say hello, greet the user.",
    "Solve a basic math equation.",
    "Tell a short joke or pun.",
    "Translate a simple sentence.",
    "Give the definition of a common word.",
    "Ask about the current time or date."
]
easy_embeddings = semantic_model.encode(EASY_INTENTS, convert_to_tensor=True, device=device)

def route_query(prompt: str) -> tuple[str, str]:
    """
    Returns (model_name, layer_used)
    model_name: The Fireworks model string
    layer_used: 'semantic' or 'xgboost' or 'fallback'
    """
    # 1. Semantic Layer (Layer 1)
    # Fast cosine similarity check against known safe/easy intents
    prompt_emb = semantic_model.encode(prompt, convert_to_tensor=True, device=device)
    cosine_scores = util.cos_sim(prompt_emb, easy_embeddings)
    max_score = cosine_scores.max().item()
    
    # Threshold for guaranteed easy intent
    if max_score > 0.85:
        return ("accounts/fireworks/models/llama-v3-8b-instruct", "semantic")
    
    # 2. XGBoost Classifier (Layer 2)
    # Re-use the EXACT SAME embedding computed in Layer 1 for the ML Classifier!
    # Zero overhead!
    if models_loaded:
        # Convert tensor back to numpy for XGBoost
        features = prompt_emb.cpu().numpy().reshape(1, -1)
        prediction = xgb_model.predict(features)[0] # 0 = easy, 1 = hard
        if prediction == 0:
            return ("accounts/fireworks/models/llama-v3-8b-instruct", "xgboost")
        else:
            return ("accounts/fireworks/models/llama-v3-70b-instruct", "xgboost")
    
    # Fallback to expensive model for safety if ML models aren't loaded
    return ("accounts/fireworks/models/llama-v3-70b-instruct", "fallback")
