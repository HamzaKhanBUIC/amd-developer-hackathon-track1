import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()

# Defensive API Key Resolution
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or "dummy"
BASE_URL = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")

client = AsyncOpenAI(
    api_key=FIREWORKS_API_KEY,
    base_url=BASE_URL,
    timeout=15.0  # Added explicit timeout to prevent hanging connections
)

# --- CATEGORY-SPECIFIC CONFIGS ---
# Per-category system prompts, temperatures, and max_tokens.
# This is the single biggest accuracy lever: precision prompts beat generic ones.
CATEGORY_CONFIGS = {
    "sentiment": {
        "sys_prompt": "Output Positive, Negative, or Neutral.",
        "temperature": 0.0,
        "max_tokens": 5,
    },
    "ner": {
        "sys_prompt": "Extract entities. Output valid JSON.",
        "temperature": 0.0,
        "max_tokens": 80,
    },
    "summarization": {
        "sys_prompt": "Summarize in 1 concise sentence.",
        "temperature": 0.1,
        "max_tokens": 50,
    },
    "factual": {
        "sys_prompt": "Answer directly in 1 sentence.",
        "temperature": 0.0,
        "max_tokens": 40,
    },
    "math": {
        "sys_prompt": "Solve concisely. End with Answer:",
        "temperature": 0.1,
        "max_tokens": 150,
    },
    "logic": {
        "sys_prompt": "Solve concisely. End with Answer:",
        "temperature": 0.1,
        "max_tokens": 80,
    },
    "code": {
        "sys_prompt": "Output code only. No prose.",
        "temperature": 0.2,
        "max_tokens": 150,
    },
    "general": {
        "sys_prompt": "Be concise.",
        "temperature": 0.1,
        "max_tokens": 80,
    },
}

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
async def generate_response_api(prompt: str, model: str, category: str = "general") -> str:
    """Calls the Fireworks API with category-specific precision prompts and token limits."""
    config = CATEGORY_CONFIGS.get(category, CATEGORY_CONFIGS["general"])

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": config["sys_prompt"]},
            {"role": "user", "content": prompt}
        ],
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        stop=["\n\n", "Note:", "Explanation:", "Here's", "Let me", "I will", "As an AI"]
    )
    return response.choices[0].message.content
