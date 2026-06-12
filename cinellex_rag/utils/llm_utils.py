import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate(prompt: str, max_tokens: int = 500) -> str:
    """Single-shot Groq completion. Model is the free-tier 8B instant model,
    matching the facet-extraction and recommendation-crew LLM."""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content