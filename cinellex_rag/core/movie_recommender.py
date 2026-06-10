"""
Content-based movie recommender (TF-IDF + cosine similarity).

Deterministic candidate selection — given a seed movie it returns the most
similar films by genre / director / cast. Used directly and as the grounding
tool for the CrewAI RecommendationCrew (so the LLM cannot invent titles).
"""

from difflib import get_close_matches

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from cinellex_rag.core.data_loader import load_imdb
from config.schema_config import (
    COL_TITLE,
    COL_RATING,
    COL_DIRECTOR,
    COL_GENRE,
    COL_STAR1,
    COL_STAR2,
    COL_STAR3,
    COL_STAR4,
)


class MovieRecommender:
    def __init__(self, df):
        self.df = df.reset_index(drop=True).copy()

        # Build a single text feature from genre, director and the four stars.
        # (There is no combined "Stars" column in the IMDB dataset.)
        self.df["_features"] = (
            self.df[COL_GENRE].fillna("") + " "
            + self.df[COL_DIRECTOR].fillna("") + " "
            + self.df[COL_STAR1].fillna("") + " "
            + self.df[COL_STAR2].fillna("") + " "
            + self.df[COL_STAR3].fillna("") + " "
            + self.df[COL_STAR4].fillna("")
        )

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.feature_matrix = self.vectorizer.fit_transform(self.df["_features"])

        # Lower-cased titles for fuzzy resolution of free-form input.
        self._titles_lower = self.df[COL_TITLE].str.lower().tolist()

    def _resolve_title(self, movie_title: str):
        """Resolve free-form input to an actual title via fuzzy matching."""
        q = movie_title.lower().strip()
        match = get_close_matches(q, self._titles_lower, n=1, cutoff=0.5)
        if not match:
            return None
        idx = self._titles_lower.index(match[0])
        return idx

    def recommend(self, movie_title: str, top_n: int = 3):
        idx = self._resolve_title(movie_title)
        if idx is None:
            return f"Movie '{movie_title}' not found in database."

        sim_scores = cosine_similarity(
            self.feature_matrix[idx], self.feature_matrix
        ).flatten()
        sim_scores[idx] = 0  # exclude the seed movie itself

        top_indices = sim_scores.argsort()[-top_n:][::-1]

        return (
            self.df.iloc[top_indices][[COL_TITLE, COL_RATING, COL_DIRECTOR]]
            .to_dict(orient="records")
        )


# Module-level singleton so the TF-IDF matrix is fit only once.
_recommender = None


def get_recommender() -> MovieRecommender:
    global _recommender
    if _recommender is None:
        _recommender = MovieRecommender(load_imdb())
    return _recommender


def recommend_movies(movie_title: str, top_n: int = 3):
    """Convenience wrapper around the singleton recommender."""
    return get_recommender().recommend(movie_title, top_n)
