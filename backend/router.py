import os
import re
from collections import OrderedDict
import numpy as np
import xgboost as xgb
import torch
from sentence_transformers import SentenceTransformer, util

# Check for AMD ROCm / CUDA availability
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    print("AMD ROCm GPU detected via PyTorch HIP backend.")
else:
    print("Falling back to CPU. No AMD ROCm GPU detected.")

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
    "Determine if text is positive or negative.",
    "Name a color, animal, or object.",
    "Provide a synonym for a word.",
    "Answer a basic general knowledge question.",
    "Confirm or deny a simple fact."
]
easy_embeddings = semantic_model.encode(EASY_INTENTS, convert_to_tensor=True, device=device)

# --- 1. DYNAMIC API MODEL SELECTION ---
def parse_allowed_models():
    """Parses ALLOWED_MODELS to find the absolute best model for hard tasks and cheapest for fallback."""
    allowed_models_env = os.environ.get("ALLOWED_MODELS", "")
    allowed = [m.strip() for m in allowed_models_env.split(",") if m.strip()]
    
    # Defaults
    cheap = "accounts/fireworks/models/llama-v3p1-8b-instruct"
    code = "accounts/fireworks/models/qwen2p5-coder-32b-instruct"
    expensive = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    
    if not allowed:
        return cheap, code, expensive
        
    cheap = allowed[0]
    expensive = allowed[-1]
    code = allowed[1] if len(allowed) > 1 else allowed[0]
    
    for model in allowed:
        ml = model.lower()
        if "70b" in ml or "72b" in ml or "405b" in ml:
            expensive = model
        if "code" in ml or "coder" in ml:
            code = model
        if "8b" in ml or "7b" in ml or "mini" in ml:
            cheap = model
            
    return cheap, code, expensive

CHEAP_MODEL, CODE_MODEL, EXPENSIVE_MODEL = parse_allowed_models()

LOCAL_MODEL_KEY = "local" 
CACHE_HIT_KEY = "cache_hit" 

# --- 2. SEMANTIC CACHE ---
CACHE_MAX_SIZE = 10_000
CACHE_SIMILARITY_THRESHOLD = 0.99
_semantic_cache: OrderedDict[int, dict] = OrderedDict()
_cache_counter = 0

# Contiguous array for lightning-fast cache hits
_cache_embeddings_array = np.empty((0, 384), dtype=np.float32)

def check_semantic_cache(prompt_embedding: np.ndarray) -> str | None:
    if len(_semantic_cache) == 0:
        return None
    
    # Use the contiguous array for O(1) vectorized dot product
    prompt_norm = prompt_embedding / (np.linalg.norm(prompt_embedding) + 1e-10)
    cached_norms = _cache_embeddings_array / (np.linalg.norm(_cache_embeddings_array, axis=1, keepdims=True) + 1e-10)
    similarities = cached_norms @ prompt_norm
    max_idx = int(np.argmax(similarities))
    max_score = float(similarities[max_idx])

    if max_score >= CACHE_SIMILARITY_THRESHOLD:
        hit_key = list(_semantic_cache.keys())[max_idx]
        _semantic_cache.move_to_end(hit_key)
        return _semantic_cache[hit_key]["response"]
    return None

def add_to_cache(prompt_embedding: np.ndarray, response: str) -> None:
    global _cache_counter, _cache_embeddings_array
    
    if len(_semantic_cache) >= CACHE_MAX_SIZE:
        _semantic_cache.popitem(last=False)
        _cache_embeddings_array = _cache_embeddings_array[1:] # Remove oldest
        
    _cache_counter += 1
    _semantic_cache[_cache_counter] = {
        "response": response,
    }
    if len(_cache_embeddings_array) == 0:
        _cache_embeddings_array = np.array([prompt_embedding], dtype=np.float32)
    else:
        _cache_embeddings_array = np.vstack([_cache_embeddings_array, prompt_embedding])

# --- 3. CONDITIONAL TOKEN PRUNING ---
def prune_prompt(prompt: str, category: str) -> str:
    """Strips whitespace/JSON formatting for text tasks to save 10-30% tokens."""
    if category in ["math", "logic", "code"]:
        return prompt # DO NOT PRUNE CODE/MATH
    
    # Prune extra newlines and spaces
    pruned = re.sub(r'\s*\n\s*', '\n', prompt)
    pruned = re.sub(r' {2,}', ' ', pruned)
    return pruned.strip()

# --- 4. CATEGORY-CALIBRATED CONFIDENCE THRESHOLDS (C3T) ---
def determine_category(prompt: str) -> str:
    pl = prompt.lower()
    if any(k in pl for k in ["code", "python", "javascript", "rust", "c++", "debug", "function"]):
        return "code"
    if any(k in pl for k in ["math", "logic", "puzzle", "theorem", "prove", "calculate", "equation"]):
        return "math"
    if any(k in pl for k in ["sentiment", "positive", "negative"]):
        return "sentiment"
    if any(k in pl for k in ["summarize", "summary", "tldr"]):
        return "summarization"
    if any(k in pl for k in ["extract", "name", "entity", "ner"]):
        return "ner"
    return "factual"

def route_query(pruned_prompt: str, category: str, prompt_emb: np.ndarray) -> tuple[str, str, str, str]:
    """
    Returns (model_name, layer_used, pruned_prompt, category)
    Accepts pre-calculated numpy embeddings to prevent the 'Triple Embedding' timeout bug.
    """
    # 1. Category Bypassing (Math/Code NEVER go to local model to prevent confident hallucinations)
    if category in ["math", "logic", "code"]:
        if category == "code":
            return (CODE_MODEL, "c3t-code-bypass", pruned_prompt, category)
        return (EXPENSIVE_MODEL, "c3t-math-bypass", pruned_prompt, category)
    
    # 2. Semantic Layer
    # prompt_emb is 1D (384,), convert back to tensor for cosine similarity against easy_embeddings
    prompt_tensor = torch.tensor(prompt_emb, device=device)
    cosine_scores = util.cos_sim(prompt_tensor, easy_embeddings)
    max_score = cosine_scores.max().item()
    
    # 3. XGBoost Classifier (Layer 2) for Text Tasks
    if models_loaded:
        features = prompt_emb.reshape(1, -1)
        prob_easy = xgb_model.predict_proba(features)[0][0] 
        
        # C3T: Raised thresholds to > 0.85 to strictly prevent the CPU Timeout Trap
        if category in ["sentiment", "ner"]:
            if prob_easy > 0.85 or max_score > 0.85:
                return (LOCAL_MODEL_KEY, "c3t-sentiment-local", pruned_prompt, category)
        else: # summarization, factual
            if prob_easy > 0.95 or max_score > 0.95:
                return (LOCAL_MODEL_KEY, "c3t-text-local", pruned_prompt, category)
                
        return (CHEAP_MODEL, "c3t-fallback", pruned_prompt, category)
    
    return (EXPENSIVE_MODEL, "fallback", pruned_prompt, category)
