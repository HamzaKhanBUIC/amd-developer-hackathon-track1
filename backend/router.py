import os
import re
import ast
import operator as op_module
from collections import OrderedDict
import numpy as np
import xgboost as xgb
import torch
from sentence_transformers import SentenceTransformer, util

# --- 0. ZERO-TOKEN DETERMINISTIC SOLVER ---
_SAFE_OPS = {
    ast.Add: op_module.add, ast.Sub: op_module.sub,
    ast.Mult: op_module.mul, ast.Div: op_module.truediv,
    ast.Pow: op_module.pow, ast.USub: op_module.neg,
    ast.Mod: op_module.mod,
}

def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsafe node")

def try_deterministic_solve(prompt: str, category: str) -> str | None:
    """Returns an answer using 0 API tokens, or None if it must go to LLM."""
    if category == "math":
        # Extract and evaluate simple arithmetic expressions
        match = re.search(r'[\d\s\+\-\*\/\^\(\)\.\%]+', prompt)
        if match:
            expr = match.group(0).strip().replace('^', '**')
            try:
                tree = ast.parse(expr, mode='eval')
                result = _eval_node(tree.body)
                if result is not None:
                    return str(int(result)) if result == int(result) else f"{result:.4f}".rstrip('0').rstrip('.')
            except Exception:
                pass
    if category == "sentiment":
        pl = prompt.lower()
        pos = sum(1 for w in ["love", "great", "excellent", "amazing", "happy", "wonderful", "fantastic", "perfect"] if w in pl)
        neg = sum(1 for w in ["hate", "terrible", "awful", "horrible", "worst", "disgusting", "dreadful"] if w in pl)
        if pos > 2 and neg == 0: return "Positive"
        if neg > 2 and pos == 0: return "Negative"
    return None

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
CACHE_HIT_KEY = "cache_hit" 

# --- 2. SEMANTIC CACHE ---
CACHE_MAX_SIZE = 10_000
CACHE_SIMILARITY_THRESHOLD = 0.92  # Lowered from 0.99 — catches near-duplicate queries
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
    return "general"  # Changed from 'factual' — general gets its own prompt config

def route_query(pruned_prompt: str, category: str, prompt_emb: np.ndarray) -> tuple[str, str, str, str]:
    """
    Returns (model_name, layer_used, pruned_prompt, category)
    Accepts pre-calculated numpy embeddings to prevent the 'Triple Embedding' timeout bug.
    """
    # 1. Hard category bypasses — route to correct API tier immediately
    if category == "code":
        return (CODE_MODEL, "c3t-code-bypass", pruned_prompt, category)
    if category in ["math", "logic"]:
        return (EXPENSIVE_MODEL, "c3t-math-logic-bypass", pruned_prompt, category)
    
    # 2. Structured text tasks (Sentiment, NER) — ALWAYS route to API, NEVER local
    # The 1.5B local model had ~35-40% accuracy on these; 8B API gets 80%+
    if category in ["sentiment", "ner"]:
        return (CHEAP_MODEL, "c3t-structured-api", pruned_prompt, category)
    
    # 3. General tasks — route to cheap API with general prompt
    if category == "general":
        return (CHEAP_MODEL, "c3t-general-api", pruned_prompt, category)
    
    # 4. Summarization/Factual — use XGBoost/semantic to decide if cheap API is enough
    # prompt_emb is 1D (384,), convert back to tensor for cosine similarity
    prompt_tensor = torch.tensor(prompt_emb, device=device)
    cosine_scores = util.cos_sim(prompt_tensor, easy_embeddings)
    max_score = cosine_scores.max().item()
    
    if models_loaded:
        features = prompt_emb.reshape(1, -1)
        prob_easy = xgb_model.predict_proba(features)[0][0]
        # Only send to local model if EXTREMELY confident (protects accuracy)
        if prob_easy > 0.99 and max_score > 0.99:
            return (LOCAL_MODEL_KEY, "c3t-text-local", pruned_prompt, category)
        return (CHEAP_MODEL, "c3t-text-api", pruned_prompt, category)
    
    return (CHEAP_MODEL, "c3t-fallback", pruned_prompt, category)
