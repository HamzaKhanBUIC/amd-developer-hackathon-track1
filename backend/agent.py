import os
import sys
import json
import asyncio
import argparse
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from llama_cpp import Llama
import traceback

from router import (
    route_query, LOCAL_MODEL_KEY, CACHE_HIT_KEY,
    prune_prompt, determine_category,
    CHEAP_MODEL
)
from fireworks_client import generate_response_api

# 1. Globals and Semaphores
local_semaphore = asyncio.Semaphore(1)
api_semaphore = asyncio.Semaphore(50)

# Upgrade to 3B model for better accuracy while fitting within the 4GB RAM budget
LOCAL_MODEL_PATH = "qwen2.5-3b-instruct-q4_k_m.gguf"
try:
    print(f"Loading local model from {LOCAL_MODEL_PATH}...")
    llm = Llama(
        model_path=LOCAL_MODEL_PATH,
        n_threads=os.cpu_count() or 2,
        n_ctx=2048,
        verbose=False
    )
except Exception as e:
    print(f"Warning: Failed to load local model: {e}")
    llm = None

def generate_local_response(prompt: str, category: str) -> str:
    """Synchronous local inference using Llama-cpp."""
    if not llm:
        return ""
    
    # Aggressively limit max_tokens to prevent timeouts
    max_tokens = 150
    if category == "sentiment":
        max_tokens = 5
    elif category == "ner":
        max_tokens = 30
        
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Keep answers concise."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.3
    )
    
    return response["choices"][0]["message"]["content"]

async def execute_task(task_id: str, prompt: str, model_name: str, layer: str, category: str) -> dict:
    answer = ""
    actual_layer = layer
    actual_model = model_name
    
    # Pre-parse allowed models for the API cascade
    allowed_models_env = os.environ.get("ALLOWED_MODELS", "")
    allowed_models = [m.strip() for m in allowed_models_env.split(",") if m.strip()]
    if not allowed_models:
        allowed_models = [CHEAP_MODEL]
    
    if model_name == LOCAL_MODEL_KEY:
        try:
            async with local_semaphore:
                # Wrapped in a 20-second timeout to prevent CPU exhaustion and container death
                answer = await asyncio.wait_for(asyncio.to_thread(generate_local_response, prompt, category), timeout=20.0)
                if not answer.strip():
                    raise ValueError("Local model returned empty string")
        except Exception as e:
            print(f"[{task_id}] Local Model Failed ({e}) - Aborting and falling back to Fireworks API.")
            actual_layer = f"{layer}_fallback"
            
            # API Cascade Fallback
            for fb_model in reversed(allowed_models):
                actual_model = fb_model
                try:
                    async with api_semaphore:
                        answer = await generate_response_api(prompt, fb_model, category)
                    break
                except Exception as fallback_e:
                    print(f"[{task_id}] API cascade fallback ({fb_model}) failed: {fallback_e}")
                    answer = "Error: All models failed."
    else:
        # Fireworks API Execution with Cascade
        success = False
        models_to_try = [model_name] + [m for m in reversed(allowed_models) if m != model_name]
        
        for try_model in models_to_try:
            actual_model = try_model
            try:
                async with api_semaphore:
                    answer = await generate_response_api(prompt, try_model, category)
                success = True
                break
            except Exception as e:
                print(f"[{task_id}] API failed for {try_model}. Error: {e}")
                actual_layer = f"{layer}_api_cascade_fallback"
                
        if not success:
            print(f"[{task_id}] All API models failed. Falling back to local model desperation...")
            try:
                async with local_semaphore:
                    answer = await asyncio.wait_for(asyncio.to_thread(generate_local_response, prompt, category), timeout=20.0)
                actual_layer = "local_desperation_fallback"
                actual_model = LOCAL_MODEL_KEY
            except Exception as fallback_local_e:
                print(f"[{task_id}] Desperation local fallback failed: {fallback_local_e}")
                answer = "Error: All models failed."
    
    cost_map = {
        "c3t-code-bypass": 0.001,
        "c3t-math-bypass": 0.002,
        "c3t-fallback": 0.0005,
    }
    cost_usd = 0.0 if actual_model == LOCAL_MODEL_KEY else cost_map.get(layer, 0.001)

    print(f"[{task_id}] Routed to {actual_model} via {actual_layer} (Cat: {category}, Cost: ${cost_usd})")
    return {
        "task_id": task_id, 
        "answer": answer
    }

async def main():
    parser = argparse.ArgumentParser(description="AMD Hackathon Task Runner")
    parser.add_argument("--input", type=str, help="Path to input tasks.json")
    parser.add_argument("--output", type=str, help="Path to output results.json")
    args, unknown = parser.parse_known_args()

    # Heuristic to catch positional arguments if provided
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
        
    print(f"Processing {len(tasks)} tasks via 5-Layer Hybrid Router...")
    
    # --- PHASE 1: PRE-PROCESSING ---
    pruned_prompts = []
    categories = []
    for task in tasks:
        prompt = task.get("prompt") or task.get("query") or task.get("task", "")
        cat = determine_category(prompt)
        pruned = prune_prompt(prompt, cat)
        pruned_prompts.append(pruned)
        categories.append(cat)
        
    # Route Queries
    results = [None] * len(tasks)
    local_tasks = []
    api_tasks_by_category = {}
    
    for i, task in enumerate(tasks):
        task_id = task.get("id") or task.get("task_id")
        orig_prompt = task.get("prompt") or task.get("query") or task.get("task", "")
        pruned_prompt = pruned_prompts[i]
        category = categories[i]
            
        # 1. Route Query
        try:
            model_name, layer, _, cat = route_query(pruned_prompt, category)
        except Exception as e:
            print(f"Routing failed for {task_id}: {e}")
            model_name, layer, cat = LOCAL_MODEL_KEY, "fallback", category
            
        task_obj = (i, task_id, pruned_prompt, model_name, layer, cat, orig_prompt)
        
        # Group tasks for Cache-Aware Sticky Batching
        if model_name == LOCAL_MODEL_KEY:
            local_tasks.append(task_obj)
        else:
            if cat not in api_tasks_by_category:
                api_tasks_by_category[cat] = []
            api_tasks_by_category[cat].append(task_obj)
            
    # Execute Local Tasks (Serialized to save CPU)
    if local_tasks:
        print(f"Executing {len(local_tasks)} local tasks sequentially...")
        for idx, t_id, p_prompt, m_name, lyr, cat, orig_prompt in local_tasks:
            results[idx] = await execute_task(t_id, p_prompt, m_name, lyr, cat)
            
    # Execute API Tasks by Category (KV Cache Prefix Optimization)
    for cat, category_tasks in api_tasks_by_category.items():
        print(f"Executing {len(category_tasks)} API tasks for category: {cat}...")
        coroutines = []
        indices = []
        for idx, t_id, p_prompt, m_name, lyr, c, orig_prompt in category_tasks:
            coroutines.append(execute_task(t_id, p_prompt, m_name, lyr, c))
            indices.append(idx)
            
        batch_results = await asyncio.gather(*coroutines)
        for i, res in zip(indices, batch_results):
            results[i] = res
            
    # Write output
    print(f"Writing results to {output_path}...")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("Execution Complete! Architecture executed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
