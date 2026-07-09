import os
import sys
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()

# Defensive API Key Resolution
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or "dummy"

BASE_URL = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")

# Instantiate an async client for Fireworks
client = AsyncOpenAI(
    api_key=FIREWORKS_API_KEY,
    base_url=BASE_URL
)

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
async def generate_response_api(prompt: str, model: str, category: str = "general") -> str:
    """Calls the Fireworks API using the specified model. Retries up to 3 times on failure."""
    
    # Base system prompt
    sys_prompt = "You are a helpful AI assistant. Answer concisely."
    
    # Inject "Chain of Draft" (CoD) for Math/Logic tasks to slash structural tokens
    if category in ["math", "logic"]:
        sys_prompt += " Use Chain of Draft: Output exactly 5-10 words of ultra-short telegraphic reasoning before providing the final answer."

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.3
    )
    return response.choices[0].message.content
