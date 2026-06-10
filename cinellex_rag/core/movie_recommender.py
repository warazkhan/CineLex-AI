"""Content-based recommendations, served live from TMDB.

Replaces the local TF-IDF recommender. A seed title is resolved via TMDB search,
then TMDB's own ``/movie/{id}/recommendations`` provides similar films. Used
directly and as the grounding tool for the CrewAI RecommendationCrew (so the LLM
cannot invent titles).

The public interface is unchanged: ``recommend_movies(title, top_n)`` returns a
list of dicts keyed by the recommender schema columns, or a friendly string when
nothing is found.
"""
from cinellex_rag.core import tmdb
from cinellex_rag.core.movies import cards_for_ids
from config.schema_config import COL_TITLE, COL_RATING, COL_DIRECTOR


def recommend_movies(movie_title: str, top_n: int = 3):
    """Return up to ``top_n`` movies similar to ``movie_title``.

    On success: a list of ``{COL_TITLE, COL_RATING, COL_DIRECTOR}`` dicts.
    On failure: a human-readable string (no match / no recommendations).
    """
    if not movie_title or not movie_title.strip():
        return "Please name a movie to base recommendations on."

    seed = tmdb.search_movie(movie_title.strip())
    if not seed:
        return f"Movie '{movie_title}' not found."

    recs = tmdb.movie_recommendations(seed.get("id"), limit=top_n)
    if not recs:
        return f"No recommendations found for '{movie_title}'."

    cards = cards_for_ids([r["id"] for r in recs])
    return [
        {COL_TITLE: c["title"], COL_RATING: c["rating"], COL_DIRECTOR: c["director"]}
        for c in cards
    ]
