import os
import csv
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# We use Fireworks AI to generate our synthetic dataset.
client = AsyncOpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.environ.get("FIREWORKS_API_KEY", "dummy_key")
)

MODEL = "accounts/fireworks/models/llama-v3-70b-instruct"

# Prompts to generate our synthetic dataset
SYSTEM_PROMPT_EASY = """You are a helpful assistant. Generate 50 unique, highly diverse, extremely short and easy queries that a user might ask a chatbot. 
These should be things like greetings, asking for the time, simple math, definitions, or general short facts.
Output ONLY the queries, one per line. Do not number them. Do not include quotes."""

SYSTEM_PROMPT_HARD = """You are a helpful assistant. Generate 50 unique, highly diverse, extremely complex and long queries that a user might ask an expert chatbot. 
These should be things like asking to write complex code, deep philosophical reasoning, geopolitical analysis, drafting legal contracts, or advanced architectural design.
Output ONLY the queries, one per line. Do not number them. Do not include quotes."""

async def generate_batch(prompt_type: str) -> list[str]:
    system_prompt = SYSTEM_PROMPT_EASY if prompt_type == "easy" else SYSTEM_PROMPT_HARD
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.9,
            max_tokens=2048
        )
        content = response.choices[0].message.content
        return [line.strip() for line in content.split('\n') if line.strip()]
    except Exception as e:
        print(f"Failed to generate {prompt_type} dataset: {e}")
        return []

async def main():
    print("Generating Synthetic Dataset for Zero-Token Router...")
    
    if os.environ.get("FIREWORKS_API_KEY") in [None, "", "dummy_key"]:
        print("No FIREWORKS_API_KEY found. Generating a small fallback dataset.")
        # Fallback if no key is provided
        easy = ["Hi", "What is 2+2?", "Define apple", "What time is it?", "Tell me a joke"]
        hard = ["Write a rust macro for deserialization", "Explain the Riemann Hypothesis", "Draft a legal contract for a joint venture", "Design a microservice architecture in Kubernetes"]
    else:
        # Generate multiple batches to get a good dataset size
        easy_tasks = [generate_batch("easy") for _ in range(4)] # 200 easy
        hard_tasks = [generate_batch("hard") for _ in range(4)] # 200 hard
        
        print("Calling Fireworks AI 70B to synthesize training data...")
        easy_results = await asyncio.gather(*easy_tasks)
        hard_results = await asyncio.gather(*hard_tasks)
        
        easy = [item for sublist in easy_results for item in sublist]
        hard = [item for sublist in hard_results for item in sublist]

    # Save to CSV
    # 0 = Easy, 1 = Hard
    dataset_path = "dataset.csv"
    with open(dataset_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["prompt", "label"])
        for q in easy:
            writer.writerow([q, 0])
        for q in hard:
            writer.writerow([q, 1])
            
    print(f"Successfully generated {len(easy) + len(hard)} synthetic prompts and saved to {dataset_path}!")

if __name__ == "__main__":
    asyncio.run(main())
