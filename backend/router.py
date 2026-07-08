import os
import xgboost as xgb
import torch
from sentence_transformers import SentenceTransformer, util

# Check for AMD ROCm / CUDA availability
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model("xgboost_router.json")
    models_loaded = True
except Exception as e:
    print("Warning: XGBoost model not found. Run train_model.py first.")
    models_loaded = False

print(f"Loading Semantic Router (MiniLM) on {device.upper()}...")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

EASY_INTENTS = [
    "Say hello, greet the user.",
    "Solve a basic math equation.",
    "Tell a short joke or pun.",
    "Translate a simple sentence.",
    "Give the definition of a common word.",
    "Ask about the current time or date.",
    "Summarize a short paragraph.",
    "Extract names and places from a sentence.",
    "Determine if text is positive or negative.",
    "Name a color, animal, or object.",
    "Provide a synonym for a word.",
    "Answer a basic general knowledge question."
]
easy_embeddings = semantic_model.encode(EASY_INTENTS, convert_to_tensor=True, device=device)

# STRICT TRACK 1 ALLOWED MODELS (Parsed from environment)
allowed_models_env = os.environ.get("ALLOWED_MODELS", "")
allowed_models = [m.strip() for m in allowed_models_env.split(",") if m.strip()]

# Defaults fallback in case environment is missing during local dev
CHEAP_MODEL = "accounts/fireworks/models/gemma-4-26b-a4b-it"
EXPENSIVE_MODEL = "accounts/fireworks/models/gemma-4-31b-it"
CODE_MODEL = "accounts/fireworks/models/kimi-k2p7-code"

# Attempt to map from ALLOWED_MODELS
if len(allowed_models) >= 3:
    # Just picking the first few as an example if they exist
    # In reality we'd match strings to find 'code' or 'gemma-4'
    pass
for model in allowed_models:
    if "code" in model.lower():
        CODE_MODEL = model
    elif "31b" in model.lower():
        EXPENSIVE_MODEL = model
    elif "26b" in model.lower():
        CHEAP_MODEL = model

LOCAL_MODEL_KEY = "local" # Constant to indicate local processing


def route_query(prompt: str) -> tuple[str, str]:
    """
    Returns (model_name, layer_used)
    """
    # 1. Semantic Layer (Layer 1)
    prompt_emb = semantic_model.encode(prompt, convert_to_tensor=True, device=device)
    cosine_scores = util.cos_sim(prompt_emb, easy_embeddings)
    max_score = cosine_scores.max().item()
    
    if max_score > 0.85:
        return (LOCAL_MODEL_KEY, "semantic")
    
    # 2. XGBoost Classifier (Layer 2)
    if models_loaded:
        features = prompt_emb.cpu().numpy().reshape(1, -1)
        prediction = xgb_model.predict(features)[0] # 0 = easy, 1 = hard
        
        # Simple heuristic to detect if the hard prompt requires the specific code model
        # In a real scenario, this could be a 3-class XGBoost model (Easy, Hard, Code)
        if prediction == 1:
            prompt_lower = prompt.lower()
            if any(keyword in prompt_lower for keyword in ["code", "python", "javascript", "rust", "c++", "debug", "function"]):
                return (CODE_MODEL, "xgboost-code")
            elif any(keyword in prompt_lower for keyword in ["math", "logic", "puzzle", "theorem", "prove", "calculate", "equation"]):
                return (EXPENSIVE_MODEL, "xgboost-reasoning")
            else:
                return (CHEAP_MODEL, "xgboost-medium")
        else:
            return (LOCAL_MODEL_KEY, "xgboost-easy")
    
    return (EXPENSIVE_MODEL, "fallback")
