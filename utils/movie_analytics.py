import pandas as pd
from config.data_config import IMDB_CSV_PATH

df = pd.read_csv(IMDB_CSV_PATH)
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")


def answer_analytic_query(query: str) -> str:
    q = query.lower()

    if "top" in q and "movie" in q:
        top_n = extract_number(q, default=3)
        top_movies = (
            df[["Series_Title", "Released_Year", "IMDB_Rating"]]
            .dropna()
            .sort_values("IMDB_Rating", ascending=False)
            .head(top_n)
        )
        return format_movies(top_movies)

    if "top" in q and "director" in q:
        top_directors = (
            df.groupby("Director")["IMDB_Rating"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )
        return "\n".join(top_directors.index.tolist())

    if "latest" in q:
        latest = df.sort_values("Released_Year", ascending=False).head(5)
        return format_movies(latest)

    if "highest gross" in q or "box office" in q:
        gross_df = df.dropna(subset=["Gross"])
        gross_df["Gross"] = (
            gross_df["Gross"]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
        )
        top = gross_df.sort_values("Gross", ascending=False).head(1)
        return format_movies(top)

    return "Analytics not supported for this query."


def extract_number(text: str, default: int) -> int:
    for word in text.split():
        if word.isdigit():
            return int(word)
    return default


def format_movies(df_slice: pd.DataFrame) -> str:
    lines = []
    for _, row in df_slice.iterrows():
        lines.append(
            f"{row['Series_Title']} ({int(row['Released_Year'])}) – Rating: {row['IMDB_Rating']}"
        )
    return "\n".join(lines)
