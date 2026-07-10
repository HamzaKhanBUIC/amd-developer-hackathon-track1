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
    base_url=BASE_URL
)

# --- CATEGORY-SPECIFIC CONFIGS ---
# Per-category system prompts, temperatures, and max_tokens.
# This is the single biggest accuracy lever: precision prompts beat generic ones.
CATEGORY_CONFIGS = {
    "sentiment": {
        "sys_prompt": (
            "You are a sentiment classification expert. "
            "Output ONLY 'Positive', 'Negative', or 'Neutral'. "
            "No explanation. No other text."
        ),
        "temperature": 0.0,
        "max_tokens": 5,
    },
    "ner": {
        "sys_prompt": (
            "You are a Named Entity Recognition (NER) expert. "
            "Extract all named entities. "
            "Output ONLY valid JSON: "
            "{\"persons\": [], \"organizations\": [], \"locations\": [], \"dates\": []}. "
            "No markdown formatting. No explanation."
        ),
        "temperature": 0.0,
        "max_tokens": 80,
    },
    "summarization": {
        "sys_prompt": (
            "You are a precise text summarization expert. "
            "Summarize the given text into exactly 1 concise sentence. "
            "Output ONLY the summary, no preamble, no labels."
        ),
        "temperature": 0.1,
        "max_tokens": 50,
    },
    "factual": {
        "sys_prompt": (
            "You are a factual question-answering expert. "
            "Answer directly in 1 short sentence maximum. "
            "Output only the answer, no preamble."
        ),
        "temperature": 0.0,
        "max_tokens": 40,
    },
    "math": {
        "sys_prompt": (
            "You are a precise mathematical reasoning expert. "
            "Solve step by step very concisely (5 words max per step). "
            "End with 'Answer: [value]' on a new line."
        ),
        "temperature": 0.1,
        "max_tokens": 150,
    },
    "logic": {
        "sys_prompt": (
            "You are a logical reasoning expert. "
            "Solve the puzzle very concisely (5 words max per step). "
            "End with 'Answer: [value]' on a new line."
        ),
        "temperature": 0.1,
        "max_tokens": 150,
    },
    "code": {
        "sys_prompt": (
            "You are a senior software engineer. "
            "Provide ONLY the code solution. "
            "No markdown code blocks if possible. No prose explanations."
        ),
        "temperature": 0.2,
        "max_tokens": 300,
    },
    "general": {
        "sys_prompt": (
            "You are a helpful assistant. "
            "Answer as concisely as possible. 1-2 sentences max. "
            "No filler."
        ),
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
