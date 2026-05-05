import pandas as pd
from cinellex_rag.core.data_loader import load_imdb

df = load_imdb()

def handle_analytics(query: str, top_n: int = 5):
    q = query.lower()

    if "top" in q and "movie" in q:
        data = df.sort_values("IMDB_Rating", ascending=False).head(top_n)

        return {
            "answer": "\n".join(
                f"{row['Series_Title']} ({int(row['Released_Year'])}) – Rating: {row['IMDB_Rating']}"
                for _, row in data.iterrows()
            ),
            "source": "analytics"
        }

    if "worst" in q and "movie" in q:
        data = df.sort_values("IMDB_Rating", ascending=True).head(top_n)

        return {
            "answer": "\n".join(
                f"{row['Series_Title']} ({int(row['Released_Year'])}) – Rating: {row['IMDB_Rating']}"
                for _, row in data.iterrows()
            ),
            "source": "analytics"
        }

    return {
        "answer": "No analytics result found.",
        "source": "analytics"
    }