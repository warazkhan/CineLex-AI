import sys
from pathlib import Path
import pandas as pd

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.data_config import IMDB_CSV_PATH
from utils.llm_utils import generate

# ------------------------------
# 1. Load Dataset
# ------------------------------
df = pd.read_csv(IMDB_CSV_PATH)
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")

top_movies = (
    df[["Series_Title", "Released_Year", "Genre", "IMDB_Rating", "Director"]]
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
# 2. LLM Summaries
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