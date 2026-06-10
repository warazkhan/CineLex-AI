from cinellex_rag.core.movie_recommender import get_recommender, recommend_movies
from config.schema_config import COL_TITLE


def test_returns_requested_number_of_recommendations():
    recs = recommend_movies("The Dark Knight", top_n=3)
    assert isinstance(recs, list)
    assert len(recs) == 3
    assert all(COL_TITLE in r for r in recs)


def test_excludes_the_seed_movie():
    recs = recommend_movies("The Godfather", top_n=5)
    titles = [r[COL_TITLE] for r in recs]
    assert "The Godfather" not in titles


def test_fuzzy_match_resolves_imperfect_title():
    # Slightly misspelled / lower-cased input should still resolve.
    recs = recommend_movies("the dark knigt", top_n=2)
    assert isinstance(recs, list)
    assert len(recs) == 2


def test_unknown_movie_degrades_gracefully():
    result = recommend_movies("zzzz not a real movie zzzz", top_n=3)
    assert isinstance(result, str)
    assert "not found" in result.lower()


def test_singleton_is_reused():
    assert get_recommender() is get_recommender()
