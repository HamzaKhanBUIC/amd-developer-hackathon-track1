import os
import re

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

# --- 2. CATEGORY IDENTIFICATION ---
def determine_category(prompt: str) -> str:
    pl = prompt.lower()
    if any(k in pl for k in ["code", "python", "javascript", "typescript", "rust", "c++", "java", "debug", "function", "algorithm", "script", "program", "class", "def ", "implement"]):
        return "code"
    if any(k in pl for k in ["calculate", "equation", "arithmetic", "algebra", "geometry", "integral", "derivative", "compute", "math", "formula", "numeric", "solve", "how many"]):
        # Note: Added 'solve' and 'how many' for better math coverage
        return "math"
    if any(k in pl for k in ["logic", "puzzle", "riddle", "theorem", "prove", "deduce", "infer", "syllogism", "if.*then", "all.*are"]):
        return "logic"
    if any(k in pl for k in ["sentiment", "feeling", "emotion", "tone", "opinion", "positive or negative", "how does.*feel"]):
        return "sentiment"
    if any(k in pl for k in ["summarize", "summary", "tldr", "condense", "brief", "shorten", "main points"]):
        return "summarization"
    if any(k in pl for k in ["extract", "entity", "ner", "named", "identify", "list.*person", "list.*organization", "list.*location"]):
        return "ner"
    if any(k in pl for k in ["what is", "who is", "when did", "where is", "define", "capital of", "which country", "year was"]):
        return "factual"
    return "general"

def prune_prompt(prompt: str) -> str:
    """Strips outer whitespace only. No destructive token pruning."""
    return prompt.strip()
