import os
import sys
import json
import asyncio
import argparse
import traceback
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from router import (
    prune_prompt, determine_category,
    CHEAP_MODEL, CODE_MODEL, EXPENSIVE_MODEL
)
from fireworks_client import generate_response_api
import deterministic_solver

# 1. Globals and Semaphores
local_semaphore = asyncio.Semaphore(1)
api_semaphore = asyncio.Semaphore(50)

# Upgrade to 3B model for better accuracy while fitting within the 4GB RAM budget
LOCAL_MODEL_PATH = "qwen2.5-3b-instruct-q4_k_m.gguf"
try:
    from llama_cpp import Llama
    print(f"Loading local model from {LOCAL_MODEL_PATH}...")
    llm = Llama(
        model_path=LOCAL_MODEL_PATH,
        n_threads=2,
        n_ctx=2048,
        verbose=False
    )
except ImportError:
    print(f"Warning: Failed to import llama_cpp. Local model will be disabled.")
    llm = None
except Exception as e:
    print(f"Warning: Failed to load local model: {e}")
    llm = None

def validate_answer(answer: str, category: str) -> bool:
    """Zero-cost heuristic validation to catch truncated or malformed local answers."""
    if not answer or len(answer.strip()) == 0:
        return False
    ans_lower = answer.lower()
    
    if category == "sentiment":
        # Usually sentiment requires short explanation
        words = len(answer.split())
        if words < 2: return False
        return any(k in ans_lower for k in ["positive", "negative", "neutral", "mixed"])
    if category == "ner":
        # Simple NER check
        return any(k in ans_lower for k in ["person", "organization", "location", "date"]) or "{" in answer or "[" in answer
    if category == "factual":
        return len(answer.split()) >= 3
    if category == "summarization":
        return len(answer.split()) >= 5
    if category == "math":
        return any(c.isdigit() for c in answer)
    if category == "logic":
        return len(answer.split()) >= 5
    if category == "code":
        return any(k in ans_lower for k in ["def ", "return", "function", "class", "import", "print", "var", "let", "const"])
    return True

def generate_local_response(prompt: str, category: str) -> str:
    """Synchronous local inference using Llama-cpp with proper max_tokens."""
    if not llm:
        return ""
    
    # Tighter max_tokens for local models to prevent timeout cascades
    max_tokens_map = {
        "sentiment": 50,
        "ner": 100,
        "factual": 100,
        "summarization": 150,
        "math": 100,
        "logic": 100,
        "code": 100,
        "general": 100
    }
    max_tokens = max_tokens_map.get(category, 100)
        
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "Follow the user's instructions exactly. Be concise but complete."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.3
    )
    
    choice = response["choices"][0]
    if choice.get("finish_reason") == "length":
        return "" # Force API fallback on truncation
        
    return choice["message"]["content"]

async def execute_task(task_id: str, prompt: str, category: str) -> dict:
    answer = ""
    actual_layer = ""
    actual_model = ""
    
    # Pre-parse allowed models for the API fallback
    allowed_models_env = os.environ.get("ALLOWED_MODELS", "")
    allowed_models = [m.strip() for m in allowed_models_env.split(",") if m.strip()]
    if not allowed_models:
        allowed_models = [CHEAP_MODEL]
        
    # Pick the right fallback model
    fallback_model = CHEAP_MODEL
    if category == "code":
        fallback_model = CODE_MODEL
    elif category in ["math", "logic"]:
        fallback_model = EXPENSIVE_MODEL
    
    # TIER 0: Deterministic Solver
    try:
        det_ans = deterministic_solver.solve(prompt, category)
        if det_ans is not None:
            print(f"[{task_id}] Tier 0 (Deterministic) solved successfully.")
            return {"task_id": task_id, "answer": det_ans}
    except Exception as e:
        print(f"[{task_id}] Tier 0 Deterministic Solver failed: {e}")
        
    # TIER 1: Local 3B Model
    try:
        async with local_semaphore:
            # Wrapped in a timeout to prevent CPU exhaustion
            answer = await asyncio.wait_for(asyncio.to_thread(generate_local_response, prompt, category), timeout=45.0)
            
            if validate_answer(answer, category):
                print(f"[{task_id}] Tier 1 (Local 3B) solved and passed validation.")
                return {"task_id": task_id, "answer": answer}
            else:
                print(f"[{task_id}] Tier 1 (Local 3B) failed validation. Escalating to Tier 2 API.")
    except Exception as e:
        print(f"[{task_id}] Tier 1 (Local 3B) failed execution ({e}). Escalating to Tier 2 API.")
        
    # TIER 2: API Fallback
    success = False
    models_to_try = [fallback_model] + [m for m in reversed(allowed_models) if m != fallback_model]
    
    for try_model in models_to_try:
        actual_model = try_model
        try:
            async with api_semaphore:
                answer = await generate_response_api(prompt, try_model, category)
            success = True
            print(f"[{task_id}] Tier 2 (API Fallback) succeeded via {try_model}.")
            break
        except Exception as e:
            print(f"[{task_id}] API failed for {try_model}. Error: {e}")
            
    if not success:
        print(f"[{task_id}] All models failed. Returning empty/error.")
        answer = "Error: All models failed."

    return {
        "task_id": task_id, 
        "answer": answer
    }

async def main():
    parser = argparse.ArgumentParser(description="AMD Hackathon Task Runner")
    parser.add_argument("--input", type=str, help="Path to input tasks.json")
    parser.add_argument("--output", type=str, help="Path to output results.json")
    args, unknown = parser.parse_known_args()

    pos_input = unknown[0] if len(unknown) > 0 and not unknown[0].startswith("-") else None
    pos_output = unknown[1] if len(unknown) > 1 and not unknown[1].startswith("-") else None

    input_path = args.input or pos_input or os.environ.get("TASK_INPUT_PATH", "/input/tasks.json")
    output_path = args.output or pos_output or os.environ.get("TASK_OUTPUT_PATH", "/output/results.json")
    
    if not os.path.exists(input_path):
        with open(input_path, "w") as f:
            json.dump([
                {"id": "1", "prompt": "What is 2+2?"},
                {"id": "2", "prompt": "Write a python script to reverse a string."},
                {"id": "3", "prompt": "Is 'amazing' positive or negative?"}
            ], f)
    
    print(f"Reading tasks from {input_path}...")
    with open(input_path, "r") as f:
        tasks = json.load(f)
        
    print(f"Processing {len(tasks)} tasks via 3-Tier Local-First Router...")
    
    results = [None] * len(tasks)
    
    # We execute all tasks sequentially because local model takes up CPU, 
    # and we don't want API tasks to starve the local model's threads if they run concurrently.
    for i, task in enumerate(tasks):
        task_id = task.get("id") or task.get("task_id")
        orig_prompt = task.get("prompt") or task.get("query") or task.get("task", "")
        
        category = determine_category(orig_prompt)
        pruned_prompt = prune_prompt(orig_prompt)
            
        results[i] = await execute_task(task_id, pruned_prompt, category)
            
    # Write output
    print(f"Writing results to {output_path}...")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("Execution Complete! 3-Tier Architecture executed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
