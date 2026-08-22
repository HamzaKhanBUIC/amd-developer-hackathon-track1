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
# Universal system prompt with safe max_token limits.
CATEGORY_CONFIGS = {
    "sentiment": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.0,
        "max_tokens": 100,
    },
    "ner": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.0,
        "max_tokens": 150,
    },
    "summarization": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.1,
        "max_tokens": 500,
    },
    "factual": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.0,
        "max_tokens": 400,
    },
    "math": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.1,
        "max_tokens": 800,
    },
    "logic": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.1,
        "max_tokens": 800,
    },
    "code": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.2,
        "max_tokens": 1024,
    },
    "general": {
        "sys_prompt": "Follow the user's instructions exactly. Be concise but complete.",
        "temperature": 0.1,
        "max_tokens": 512,
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
        temperature=config["temperature"]
    )
    return response.choices[0].message.content
