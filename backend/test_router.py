import csv
from router import route_query, LOCAL_MODEL_KEY, CODE_MODEL, EXPENSIVE_MODEL, CHEAP_MODEL

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
        
        # True Label 0 = Easy, 1 = Hard
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
    
    # Calculate estimated savings assuming $0.001 per API call
    # Let's say CHEAP is $0.0005, CODE is $0.001, EXPENSIVE is $0.002
    api_cost = (cheap_count * 0.0005) + (code_count * 0.001) + (expensive_count * 0.002)
    potential_cost = total * 0.002 # If we blindly sent everything to expensive
    savings = potential_cost - api_cost
    print(f"\nEstimated Cost vs Dumb Router (Always Expensive): ${api_cost:.4f} instead of ${potential_cost:.4f} ({(savings/potential_cost)*100:.1f}% savings!)")

if __name__ == "__main__":
    run_router_test()
