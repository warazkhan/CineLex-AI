import pandas as pd


def run_analytics(query: str, df: pd.DataFrame, top_n: int = 5):
    q = query.lower()

    if "top" in q and "movie" in q and "rating" in q:
        return df.sort_values("IMDB_Rating", ascending=False).head(top_n)

    if "most" in q and "votes" in q:
        return df.sort_values("Votes", ascending=False).head(top_n)

    if "gross" in q or "box office" in q:
        return df.sort_values("Gross", ascending=False).head(top_n)

    if "latest" in q or "recent" in q:
        return df.sort_values("Year", ascending=False).head(top_n)

    if "director" in q:
        return df["Director"].value_counts().head(top_n)

    return None
