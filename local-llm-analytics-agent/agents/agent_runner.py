# agents/agent_runner.py


import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # 2 levels up
sys.path.append(str(PROJECT_ROOT))

# Now config import will work
from config.data_config import IMDB_CSV_PATH

import pandas as pd
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# ------------------------------
# 1. Load Dataset
# ------------------------------


df = pd.read_csv(IMDB_CSV_PATH)
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")

top_movies = (
    df[
        ["Series_Title", "Released_Year", "Genre", "IMDB_Rating", "Director"]
    ]
    .dropna()
    .sort_values("IMDB_Rating", ascending=False)
    .head(3)
    .to_dict(orient="records")
)

print("\nTop 3 Movies (Python):")
for m in top_movies:
    print(
        f"{m['Series_Title']} ({m['Released_Year']}) – "
        f"Rating: {m['IMDB_Rating']}, Genre: {m['Genre']}"
    )

# ------------------------------
# 2. Load Local LLM
# ------------------------------
MODEL_NAME = "google/flan-t5-base"
print("\nLoading Flan-T5 model (CPU)...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generate(prompt: str) -> str:
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    outputs = model.generate(
        **inputs,
        max_new_tokens=60,
        num_beams=4,           # IMPORTANT
        repetition_penalty=1.5
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ------------------------------
# 3. Agentic LLM Calls (Correct)
# ------------------------------
print("\nLLM Summaries:")

for movie in top_movies:
    prompt = f"""
Write ONE factual sentence about the movie below.
Use only the provided facts.
Do not repeat information.

Title: {movie['Series_Title']}
Year: {movie['Released_Year']}
Genre: {movie['Genre']}
Rating: {movie['IMDB_Rating']}
Director: {movie['Director']}
"""
    summary = generate(prompt)
    print("-", summary)
