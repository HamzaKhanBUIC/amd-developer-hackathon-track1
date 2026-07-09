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
    check_semantic_cache, add_to_cache, prune_prompt, determine_category,
    CHEAP_MODEL, semantic_model
)
from fireworks_client import generate_response_api

# 1. Globals and Semaphores
local_semaphore = asyncio.Semaphore(1)
api_semaphore = asyncio.Semaphore(50)

# Revert to 1.5B model to guarantee we NEVER hit the 10-minute grading timeout
LOCAL_MODEL_PATH = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
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

def generate_local_response(prompt: str) -> str:
    """Synchronous local inference using Llama-cpp."""
    if not llm:
        return ""
    
    # Generate response, capped at 150 tokens to force it to finish fast
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Keep answers concise."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.3
    )
    
    return response["choices"][0]["message"]["content"]

async def execute_task(task_id: str, prompt: str, prompt_emb, model_name: str, layer: str, category: str) -> dict:
    answer = ""
    actual_layer = layer
    actual_model = model_name
    
    if model_name == LOCAL_MODEL_KEY:
        async with local_semaphore:
            try:
                # Critical Timeout Wrapper: Abort local CPU inference if it exceeds 45s
                answer = await asyncio.wait_for(asyncio.to_thread(generate_local_response, prompt), timeout=45.0)
                if not answer.strip():
                    raise ValueError("Local model returned empty string")
            except Exception as e:
                print(f"[{task_id}] Local Model Failed/Timeout ({e}) - Aborting and falling back to Fireworks API.")
                # Fallback to CHEAP_MODEL on Fireworks
                async with api_semaphore:
                    try:
                        answer = await generate_response_api(prompt, CHEAP_MODEL, category)
                        actual_layer = f"{layer}_timeout_fallback"
                        actual_model = CHEAP_MODEL
                    except Exception as fallback_e:
                        print(f"[{task_id}] API fallback failed too: {fallback_e}")
                        answer = "Error: All models failed."
    else:
        # Fireworks API Execution
        async with api_semaphore:
            try:
                answer = await generate_response_api(prompt, model_name, category)
            except Exception as e:
                print(f"[{task_id}] API failed for {model_name}. Error: {e}")
                if model_name != CHEAP_MODEL:
                    print(f"[{task_id}] Attempting fallback to CHEAP_MODEL...")
                    try:
                        answer = await generate_response_api(prompt, CHEAP_MODEL, category)
                        actual_layer = f"{layer}_api_fallback"
                        actual_model = CHEAP_MODEL
                    except Exception as fallback_e:
                        print(f"[{task_id}] API fallback failed. Falling back to local model. Error: {fallback_e}")
                        async with local_semaphore:
                            answer = await asyncio.wait_for(asyncio.to_thread(generate_local_response, prompt), timeout=45.0)
                        actual_layer = "local_desperation_fallback"
                        actual_model = LOCAL_MODEL_KEY
                else:
                    print(f"[{task_id}] Falling back directly to local model.")
                    async with local_semaphore:
                        answer = await asyncio.wait_for(asyncio.to_thread(generate_local_response, prompt), timeout=45.0)
                    actual_layer = "local_desperation_fallback"
                    actual_model = LOCAL_MODEL_KEY
                        
    # Add to semantic cache using the pre-calculated embedding
    if answer and "Error" not in answer:
        add_to_cache(prompt_emb, answer)
    
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
    
    # --- PHASE 1: MASSIVE BATCH PRE-PROCESSING ---
    # To fix the 'Triple Embedding' timeout bug, we calculate ALL embeddings in one go.
    pruned_prompts = []
    categories = []
    for task in tasks:
        prompt = task.get("prompt") or task.get("query") or task.get("task", "")
        cat = determine_category(prompt)
        pruned = prune_prompt(prompt, cat)
        pruned_prompts.append(pruned)
        categories.append(cat)
        
    print("Batch encoding semantic embeddings...")
    # This generates a contiguous numpy array of shape (N, 384)
    all_embeddings = semantic_model.encode(pruned_prompts, convert_to_numpy=True)
    
    # First Pass: Check Semantic Cache and Route Queries
    results = [None] * len(tasks)
    local_tasks = []
    api_tasks_by_category = {}
    
    for i, task in enumerate(tasks):
        task_id = task.get("id") or task.get("task_id")
        orig_prompt = task.get("prompt") or task.get("query") or task.get("task", "")
        pruned_prompt = pruned_prompts[i]
        category = categories[i]
        prompt_emb = all_embeddings[i]
        
        # 1. Check Semantic Cache
        cached_response = check_semantic_cache(prompt_emb)
        if cached_response:
            results[i] = {
                "task_id": task_id, 
                "answer": cached_response,
                "routing": {"model": "cache", "layer": "semantic_cache_hit", "cost_usd": 0.0}
            }
            continue
            
        # 2. Route Query (C3T)
        try:
            model_name, layer, _, cat = route_query(pruned_prompt, category, prompt_emb)
        except Exception as e:
            print(f"Routing failed for {task_id}: {e}")
            model_name, layer, cat = LOCAL_MODEL_KEY, "fallback", category
            
        task_obj = (i, task_id, pruned_prompt, prompt_emb, model_name, layer, cat, orig_prompt)
        
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
        for idx, t_id, p_prompt, emb, m_name, lyr, cat, orig_prompt in local_tasks:
            results[idx] = await execute_task(t_id, p_prompt, emb, m_name, lyr, cat)
            
    # Execute API Tasks by Category (KV Cache Prefix Optimization)
    for cat, category_tasks in api_tasks_by_category.items():
        print(f"Executing {len(category_tasks)} API tasks for category: {cat}...")
        coroutines = []
        indices = []
        for idx, t_id, p_prompt, emb, m_name, lyr, c, orig_prompt in category_tasks:
            coroutines.append(execute_task(t_id, p_prompt, emb, m_name, lyr, c))
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
