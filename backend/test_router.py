import csv
from router import (
    route_query, LOCAL_MODEL_KEY, CODE_MODEL, EXPENSIVE_MODEL, CHEAP_MODEL,
    CACHE_HIT_KEY, check_semantic_cache, add_to_cache, get_prompt_embedding,
)

def run_router_test():
    try:
        with open("dataset.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader) # skip header
            data = [(row[0], int(row[1])) for row in reader if len(row) == 2]
    except FileNotFoundError:
        print("dataset.csv not found!")
        return

    print(f"Loaded {len(data)} test prompts.")

    # ── Phase 1: Standard Routing Benchmark ──────────────────────────────
    local_count = 0
    api_count = 0
    code_count = 0
    cheap_count = 0
    expensive_count = 0
    
    correct_easy = 0
    correct_hard = 0

    print("-" * 50)
    for prompt, true_label in data:
        model_name, layer = route_query(prompt)
        
        # Simulate adding to cache after "processing"
        emb = get_prompt_embedding(prompt)
        add_to_cache(emb, f"[simulated response for: {prompt[:30]}]")
        
        predicted_hard = 1 if model_name != LOCAL_MODEL_KEY else 0
        
        if true_label == 0 and predicted_hard == 0:
            correct_easy += 1
        elif true_label == 1 and predicted_hard == 1:
            correct_hard += 1
            
        if model_name == LOCAL_MODEL_KEY:
            local_count += 1
        elif model_name == CODE_MODEL:
            api_count += 1
            code_count += 1
        elif model_name == CHEAP_MODEL:
            api_count += 1
            cheap_count += 1
        else:
            api_count += 1
            expensive_count += 1

    total = len(data)
    easy_total = sum(1 for _, label in data if label == 0)
    hard_total = sum(1 for _, label in data if label == 1)

    print(f"--- ROUTING COST-EFFICIENCY REPORT ---")
    print(f"Total Queries Processed: {total}")
    print(f"Queries routed to ZERO-COST Local CPU: {local_count} ({(local_count/total)*100:.1f}%)")
    print(f"Queries routed to PAID API: {api_count} ({(api_count/total)*100:.1f}%)")
    if code_count > 0:
        print(f"  - (Of API queries, {code_count} went to specialized CODE model)")
    if cheap_count > 0:
        print(f"  - (Of API queries, {cheap_count} went to CHEAP reasoning model)")
    if expensive_count > 0:
        print(f"  - (Of API queries, {expensive_count} went to EXPENSIVE reasoning model)")
        
    print(f"\n--- ACCURACY ---")
    print(f"Easy Query Routing Accuracy: {correct_easy}/{easy_total} ({(correct_easy/max(easy_total, 1))*100:.1f}%)")
    print(f"Hard Query Routing Accuracy: {correct_hard}/{hard_total} ({(correct_hard/max(hard_total, 1))*100:.1f}%)")
    
    api_cost = (cheap_count * 0.0005) + (code_count * 0.001) + (expensive_count * 0.002)
    potential_cost = total * 0.002
    savings = potential_cost - api_cost
    print(f"\nEstimated Cost vs Dumb Router (Always Expensive): ${api_cost:.4f} instead of ${potential_cost:.4f} ({(savings/potential_cost)*100:.1f}% savings!)")

    # ── Phase 2: Semantic Cache Benchmark ─────────────────────────────────
    print("\n" + "=" * 50)
    print("--- SEMANTIC CACHE BENCHMARK ---")
    # Re-send the first 20 prompts (10 easy + 10 hard) as "duplicate" queries
    duplicates = data[:20]
    cache_hits = 0
    cache_misses = 0
    
    for prompt, _ in duplicates:
        emb = get_prompt_embedding(prompt)
        cached = check_semantic_cache(emb)
        if cached is not None:
            cache_hits += 1
        else:
            cache_misses += 1
    
    dup_total = len(duplicates)
    print(f"Duplicate Queries Sent: {dup_total}")
    print(f"Cache Hits (ZERO cost): {cache_hits}/{dup_total} ({(cache_hits/max(dup_total,1))*100:.1f}%)")
    print(f"Cache Misses: {cache_misses}/{dup_total}")
    
    # Combined savings
    total_queries = total + dup_total
    total_free = local_count + cache_hits
    combined_api_cost = api_cost  # cache hits cost $0
    combined_potential = total_queries * 0.002
    combined_savings = combined_potential - combined_api_cost
    print(f"\n--- COMBINED EFFICIENCY (Routing + Cache) ---")
    print(f"Total Queries (original + duplicates): {total_queries}")
    print(f"Total ZERO-COST Queries: {total_free} ({(total_free/total_queries)*100:.1f}%)")
    print(f"Combined Cost: ${combined_api_cost:.4f} instead of ${combined_potential:.4f} ({(combined_savings/combined_potential)*100:.1f}% savings!)")

if __name__ == "__main__":
    run_router_test()

