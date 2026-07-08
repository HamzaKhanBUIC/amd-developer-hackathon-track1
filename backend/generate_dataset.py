import os
import csv
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.environ.get("FIREWORKS_API_KEY", "dummy_key")
)

# We use the most capable allowed model for generation
MODEL = "accounts/fireworks/models/gemma-4-31b-it"

# The 8 mandated categories for Track 1
CATEGORIES = {
    "easy": [
        "Factual Q&A (Simple general knowledge)",
        "Sentiment Analysis (Determine if text is positive/negative)",
        "Summarization (Summarize a short paragraph)",
        "NER (Extract names and places from a sentence)"
    ],
    "hard": [
        "Math Reasoning (Complex multi-step word problems)",
        "Code Debugging (Find subtle bugs in Python/C++ code)",
        "Logic Puzzles (Riddles and spatial reasoning)",
        "Code Generation (Write full applications or complex algorithms)"
    ]
}

async def generate_batch(difficulty: str, category: str) -> list[str]:
    system_prompt = f"""You are a data synthesis expert. Generate 25 unique, diverse, and highly realistic user queries for a chatbot.
Category: {category}
Difficulty: {difficulty}
Output ONLY the queries, one per line. Do not number them. Do not include quotes."""
    
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
        print(f"Failed to generate {category}: {e}")
        return []

async def main():
    print("Generating Synthetic Dataset across 8 Track-1 Categories...")
    
    if os.environ.get("FIREWORKS_API_KEY") in [None, "", "dummy_key"]:
        print("No FIREWORKS_API_KEY found. Generating a fallback dataset.")
        # Fallback ensuring the 8 categories are represented
        easy = [
            "What is the capital of Japan?", # Factual
            "Is the movie 'Inception' considered good?", # Sentiment
            "Summarize the plot of Romeo and Juliet in one sentence.", # Summarization
            "Extract the cities mentioned in: 'John flew from Paris to Tokyo'." # NER
        ]
        hard = [
            "If x + 2y = 10 and 3x - y = 5, what is x * y?", # Math
            "Why is my React useEffect hook triggering an infinite loop here?", # Code Debugging
            "I have 3 boxes, one has apples, one oranges, one both. All labels are wrong. How many fruits must I pick?", # Logic
            "Write a Rust macro for zero-copy deserialization of a custom binary protocol." # Code Generation
        ]
    else:
        easy_tasks = [generate_batch("easy", cat) for cat in CATEGORIES["easy"]]
        hard_tasks = [generate_batch("hard", cat) for cat in CATEGORIES["hard"]]
        
        easy_results = await asyncio.gather(*easy_tasks)
        hard_results = await asyncio.gather(*hard_tasks)
        
        easy = [item for sublist in easy_results for item in sublist]
        hard = [item for sublist in hard_results for item in sublist]

    dataset_path = "dataset.csv"
    with open(dataset_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["prompt", "label"])
        for q in easy:
            writer.writerow([q, 0])
        for q in hard:
            writer.writerow([q, 1])
            
    print(f"Successfully generated {len(easy) + len(hard)} synthetic prompts covering all 8 categories and saved to {dataset_path}!")

if __name__ == "__main__":
    asyncio.run(main())
