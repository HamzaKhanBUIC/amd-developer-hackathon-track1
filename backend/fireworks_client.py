import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "dummy")
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
async def generate_response_api(prompt: str, model: str) -> str:
    """Calls the Fireworks API using the specified model. Retries up to 3 times on failure."""
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant. Answer concisely."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.3
    )
    return response.choices[0].message.content
