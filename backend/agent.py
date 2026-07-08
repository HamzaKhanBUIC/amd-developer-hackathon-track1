import os
import json
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from llama_cpp import Llama
import traceback

from router import (
    route_query, LOCAL_MODEL_KEY, CACHE_HIT_KEY,
    check_semantic_cache, add_to_cache, get_prompt_embedding,
)
from fireworks_client import generate_response_api

# 1. Globals and Semaphores
# Limits local model execution to 1 at a time to prevent CPU thrashing
local_semaphore = asyncio.Semaphore(1)
# Limits API calls to 50 concurrent connections to prevent Memory buffer explosion
api_semaphore = asyncio.Semaphore(50)

# Initialize the Local Qwen Model
# Will fail gracefully if model doesn't exist yet (e.g. during local testing without docker)
LOCAL_MODEL_PATH = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
try:
    print(f"Loading local model from {LOCAL_MODEL_PATH}...")
    llm = Llama(
        model_path=LOCAL_MODEL_PATH,
        n_threads=2, # Use exactly 2 threads for the 2 vCPUs
        n_ctx=2048,
        verbose=False
    )
except Exception as e:
    print(f"Warning: Failed to load local model: {e}")
    llm = None

def generate_local_response(prompt: str) -> str:
    """Synchronous local inference using Llama-cpp."""
    if not llm:
        return "Error: Local model not loaded."
    
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Keep answers concise."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.3
    )
    return response["choices"][0]["message"]["content"]

async def process_task(task: dict) -> dict:
    task_id = task.get("id") or task.get("task_id")
    prompt = task.get("prompt") or task.get("query") or task.get("task")
    
    if not task_id or not prompt:
        return {"task_id": str(task_id), "answer": "Invalid task format."}

    # 0. Semantic Cache Check (ZERO cost, ZERO latency)
    prompt_embedding = get_prompt_embedding(prompt)
    cached_response = check_semantic_cache(prompt_embedding)
    if cached_response is not None:
        print(f"  [CACHE HIT] Task {task_id} — returning cached answer.")
        return {
            "task_id": task_id, 
            "answer": cached_response,
            "routing": {
                "model": "cache",
                "layer": "semantic_cache_hit",
                "cost_usd": 0.0
            }
        }

    # 1. Routing
    try:
        model_name, layer = route_query(prompt)
    except Exception as e:
        print(f"Routing failed for {task_id}: {e}")
        model_name = LOCAL_MODEL_KEY # Safe fallback

    answer = ""
    # 2. Execution
    if model_name == LOCAL_MODEL_KEY:
        # Easy task -> Local Inference (0 tokens)
        async with local_semaphore:
            answer = await asyncio.to_thread(generate_local_response, prompt)
    else:
        # Hard task -> Fireworks API
        async with api_semaphore:
            try:
                # generate_response_api handles its own Tenacity retries
                answer = await generate_response_api(prompt, model_name)
            except Exception as e:
                print(f"API completely failed for {model_name} on task {task_id}. Error: {e}")
                # We need CHEAP_MODEL from router
                from router import CHEAP_MODEL
                if model_name != CHEAP_MODEL:
                    print(f"Attempting fallback to CHEAP_MODEL...")
                    try:
                        answer = await generate_response_api(prompt, CHEAP_MODEL)
                        layer = "api-fallback"
                    except Exception as fallback_e:
                        print(f"CHEAP_MODEL fallback also failed. Falling back to local model. Error: {fallback_e}")
                        async with local_semaphore:
                            answer = await asyncio.to_thread(generate_local_response, prompt)
                            layer = "local-desperation-fallback"
                else:
                    print(f"Falling back directly to local model.")
                    async with local_semaphore:
                        answer = await asyncio.to_thread(generate_local_response, prompt)
                        layer = "local-desperation-fallback"

    # 3. Store in Semantic Cache for future identical prompts
    add_to_cache(prompt_embedding, answer)
    
    cost_map = {
        "semantic": 0.0,
        "xgboost-easy": 0.0,
        "xgboost-medium": 0.0005,
        "xgboost-medium-fallback": 0.0005,
        "xgboost-code": 0.001,
        "xgboost-reasoning": 0.002,
        "fallback": 0.002,
    }
    cost_usd = cost_map.get(layer, 0.002)

    return {
        "task_id": task_id, 
        "answer": answer,
        "routing": {
            "model": model_name,
            "layer": layer,
            "cost_usd": cost_usd
        }
    }

async def main():
    input_path = "/input/tasks.json"
    output_path = "/output/results.json"
    
    # For local testing if /input doesn't exist
    if not os.path.exists(input_path):
        input_path = "tasks.json"
        output_path = "results.json"
        
        # Create dummy if it doesn't exist
        if not os.path.exists(input_path):
            with open(input_path, "w") as f:
                json.dump([
                    {"id": "1", "prompt": "What is 2+2?"},
                    {"id": "2", "prompt": "Write a python script to reverse a string."}
                ], f)
    
    print(f"Reading tasks from {input_path}...")
    with open(input_path, "r") as f:
        tasks = json.load(f)
    
    print(f"Processing {len(tasks)} tasks...")
    # Execute all tasks concurrently
    coroutines = [process_task(task) for task in tasks]
    results = await asyncio.gather(*coroutines)
    
    # asyncio.gather preserves the exact order of the iterables passed to it!
    # So `results` is perfectly ordered matching `tasks.json`.
    
    print(f"Writing results to {output_path}...")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
