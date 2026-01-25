def format_movies(df):
    return "\n".join(
        f"{row.Title} ({int(row.Year)}) – Rating: {row.IMDB_Rating}"
        for _, row in df.iterrows()
    )


def format_directors(series):
    return "\n".join(series.index.tolist())