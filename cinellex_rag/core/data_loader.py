import pandas as pd
from config.data_config import IMDB_CSV_PATH

_df = None

def load_imdb():
    global _df

    if _df is None:
        df = pd.read_csv(IMDB_CSV_PATH)

        df["Series_Title"] = df["Series_Title"].fillna("")
        df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")
        df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")

        _df = df

    return _df