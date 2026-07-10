import os
import re
import numpy as np
import xgboost as xgb
from sentence_transformers import SentenceTransformer

# Load models on module import to save time
try:
    xgb_model = xgb.XGBClassifier()
    model_path = os.path.join(os.path.dirname(__file__), "xgboost_router.json")
    xgb_model.load_model(model_path)
except Exception as e:
    print(f"Failed to load XGBoost model: {e}")
    xgb_model = None

try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Failed to load SentenceTransformer: {e}")
    embedding_model = None

# --- 1. DYNAMIC API MODEL SELECTION ---
def parse_allowed_models():
    """Parses ALLOWED_MODELS to map the specific official hackathon models to the correct tiers."""
    allowed_models_env = os.environ.get("ALLOWED_MODELS", "")
    allowed = [m.strip() for m in allowed_models_env.split(",") if m.strip()]
    
    # Official fallback defaults if env var is somehow empty during local dev
    cheap = "accounts/fireworks/models/gemma-4-26b-a4b-it"
    code = "accounts/fireworks/models/kimi-k2p7-code"
    expensive = "accounts/fireworks/models/minimax-m3"
    
    if not allowed:
        return cheap, code, expensive
        
    # Set safe defaults from what we're given
    cheap = allowed[0]
    expensive = allowed[-1]
    code = allowed[1] if len(allowed) > 1 else allowed[0]
    
    # Iterate through allowed list and explicitly match the official models
    for model in allowed:
        ml = model.lower()
        
        # 1. Math/Logic (Most expensive/capable)
        if "minimax-m3" in ml or "70b" in ml or "72b" in ml or "405b" in ml or "120b" in ml:
            expensive = model
            
        # 2. Code (Code generation/debugging)
        if "kimi-k2p7-code" in ml or "code" in ml or "coder" in ml:
            code = model
            
        # 3. Sentiment/NER/Factual (Cheapest, fastest)
        if "gemma-4-26b-a4b-it" in ml or ("gemma" in ml and "nvfp4" not in ml) or "8b" in ml or "7b" in ml or "20b" in ml:
            cheap = model
            
    return cheap, code, expensive

CHEAP_MODEL, CODE_MODEL, EXPENSIVE_MODEL = parse_allowed_models()

LOCAL_MODEL_KEY = "local" 

# --- 3. CONDITIONAL TOKEN PRUNING ---
def prune_prompt(prompt: str, category: str) -> str:
    """Strips whitespace/JSON formatting for text tasks to save 10-30% tokens."""
    if category in ["math", "logic", "code"]:
        return prompt # DO NOT PRUNE CODE/MATH
    
    # Prune extra newlines and spaces
    pruned = re.sub(r'\s*\n\s*', '\n', prompt)
    pruned = re.sub(r' {2,}', ' ', pruned)
    return pruned.strip()

# --- 4. CATEGORY IDENTIFICATION ---
def determine_category(prompt: str) -> str:
    pl = prompt.lower()
    if any(k in pl for k in ["code", "python", "javascript", "typescript", "rust", "c++", "java", "debug", "function", "algorithm", "script", "program", "class", "def ", "implement"]):
        return "code"
    if any(k in pl for k in ["calculate", "equation", "arithmetic", "algebra", "geometry", "integral", "derivative", "compute", "math", "formula", "numeric"]):
        return "math"
    if any(k in pl for k in ["logic", "puzzle", "riddle", "theorem", "prove", "deduce", "infer", "syllogism", "if.*then", "all.*are"]):
        return "logic"
    if any(k in pl for k in ["sentiment", "feeling", "emotion", "tone", "opinion", "positive or negative", "how does.*feel"]):
        return "sentiment"
    if any(k in pl for k in ["summarize", "summary", "tldr", "condense", "brief", "shorten", "main points"]):
        return "summarization"
    if any(k in pl for k in ["extract", "entity", "ner", "named", "identify", "list.*person", "list.*organization", "list.*location"]):
        return "ner"
    if any(k in pl for k in ["what is", "who is", "when did", "where is", "define", "capital of", "how many", "which country", "year was"]):
        return "factual"
    return "general"

def route_query(pruned_prompt: str, category: str, emb: np.ndarray = None) -> tuple[str, str, str, str]:
    """
    Returns (model_name, layer_used, pruned_prompt, category)
    """
    # 1. Hard limits: Math, Logic, and Code MUST go to Fireworks
    if category == "code":
        return (CODE_MODEL, "rule-code-api", pruned_prompt, category)
    if category in ["math", "logic"]:
        return (EXPENSIVE_MODEL, "rule-math-logic-api", pruned_prompt, category)
    
    # 2. Easy categories can go to Local Model, IF XGBoost confidence is high
    if category in ["factual", "sentiment", "summarization", "ner"]:
        # Use XGBoost if available to determine if it's truly an "easy" task
        if xgb_model is not None and embedding_model is not None:
            if emb is None:
                emb = embedding_model.encode([pruned_prompt], convert_to_numpy=True)
            
            # Predict probability of being class 0 (Easy)
            probs = xgb_model.predict_proba(emb)
            prob_easy = probs[0][0]
            
            if prob_easy >= 0.75:
                return (LOCAL_MODEL_KEY, "xgboost-local-routing", pruned_prompt, category)
            else:
                return (CHEAP_MODEL, "xgboost-api-fallback", pruned_prompt, category)
        else:
            # If models fail to load, default to local for these categories (as requested by user's "local-first" track 1 rule)
            return (LOCAL_MODEL_KEY, "rule-easy-local-fallback", pruned_prompt, category)
    
    # Catch-all
    return (CHEAP_MODEL, "rule-general-api", pruned_prompt, category)
