import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
BASE_URL = "https://api.fireworks.ai/inference/v1"

# Instantiate an async client for Fireworks
client = AsyncOpenAI(
    api_key=FIREWORKS_API_KEY,
    base_url=BASE_URL
)

# Models we will route between
CHEAP_MODEL = "accounts/fireworks/models/llama-v3-8b-instruct"
EXPENSIVE_MODEL = "accounts/fireworks/models/llama-v3-70b-instruct"

async def generate_response(prompt: str, model: str) -> str:
    """Calls the Fireworks API using the specified model."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to Fireworks API: {str(e)}"
