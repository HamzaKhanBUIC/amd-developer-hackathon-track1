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
            "Analyze the sentiment of the given text. "
            "Output ONLY one of these exact labels on the first line: 'Positive', 'Negative', or 'Neutral'. "
            "Then on a new line, write one sentence explaining why. "
            "Do not output anything else."
        ),
        "temperature": 0.0,
        "max_tokens": 80,
    },
    "ner": {
        "sys_prompt": (
            "You are a Named Entity Recognition (NER) expert. "
            "Extract all named entities from the text. "
            "Output ONLY a JSON object with these exact keys: "
            "{\"persons\": [], \"organizations\": [], \"locations\": [], \"dates\": []}. "
            "Each value is a list of entity strings found in the text. "
            "If no entities of a type are found, use an empty list []. "
            "Output ONLY valid JSON, no explanation, no markdown."
        ),
        "temperature": 0.0,
        "max_tokens": 200,
    },
    "summarization": {
        "sys_prompt": (
            "You are a precise text summarization expert. "
            "Summarize the given text into 2-3 concise sentences. "
            "Preserve all key facts and main ideas. "
            "Output ONLY the summary, no preamble, no labels."
        ),
        "temperature": 0.1,
        "max_tokens": 150,
    },
    "factual": {
        "sys_prompt": (
            "You are a factual question-answering expert. "
            "Answer the question accurately and directly. "
            "Keep the answer to 1-3 sentences maximum. "
            "Do not speculate. Output only the answer, no preamble."
        ),
        "temperature": 0.0,
        "max_tokens": 120,
    },
    "math": {
        "sys_prompt": (
            "You are a precise mathematical reasoning expert. "
            "Solve step by step using Chain of Draft: "
            "Write 3-7 ultra-short reasoning steps (5 words max each), "
            "then state the final answer on a new line as 'Answer: [value]'."
        ),
        "temperature": 0.1,
        "max_tokens": 256,
    },
    "logic": {
        "sys_prompt": (
            "You are a logical reasoning expert. "
            "Solve the puzzle step by step. "
            "Use Chain of Draft: write 3-5 brief reasoning steps (5 words max each), "
            "then state the final answer on a new line as 'Answer: [value]'."
        ),
        "temperature": 0.1,
        "max_tokens": 256,
    },
    "code": {
        "sys_prompt": (
            "You are a senior software engineer. "
            "Provide a complete, correct code solution. "
            "Include only the code and brief inline comments. "
            "No lengthy prose explanations outside the code block."
        ),
        "temperature": 0.2,
        "max_tokens": 512,
    },
    "general": {
        "sys_prompt": (
            "You are a knowledgeable and helpful assistant. "
            "Answer the question accurately and completely. "
            "Be concise but do not omit important details. "
            "Output only the answer."
        ),
        "temperature": 0.1,
        "max_tokens": 150,
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
