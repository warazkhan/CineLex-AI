"""Tests for the live-TMDB content recommender.

The TMDB client is mocked, so these assert the recommender's *mapping and
degradation logic* rather than live data or specific real-world titles.
"""
from cinellex_rag.core import movie_recommender as mr
from cinellex_rag.core import tmdb
from config.schema_config import COL_TITLE, COL_RATING, COL_DIRECTOR


def _card(title, rating, director, tmdb_id):
    return {"title": title, "rating": rating, "director": director, "tmdb_id": tmdb_id}


def test_returns_requested_number_of_recommendations(monkeypatch):
    monkeypatch.setattr(tmdb, "search_movie", lambda t, year=None: {"id": 155})
    monkeypatch.setattr(
        tmdb, "movie_recommendations",
        lambda mid, limit=3: [{"id": 1}, {"id": 2}, {"id": 3}][:limit],
    )
    monkeypatch.setattr(
        mr, "cards_for_ids",
        lambda ids: [_card(f"Movie {i}", 8.0, "Dir", i) for i in ids],
    )

    recs = mr.recommend_movies("The Dark Knight", top_n=3)

    assert isinstance(recs, list)
    assert len(recs) == 3
    assert all(COL_TITLE in r and COL_RATING in r and COL_DIRECTOR in r for r in recs)


def test_maps_card_fields_to_schema_keys(monkeypatch):
    monkeypatch.setattr(tmdb, "search_movie", lambda t, year=None: {"id": 238})
    monkeypatch.setattr(tmdb, "movie_recommendations", lambda mid, limit=3: [{"id": 240}])
    monkeypatch.setattr(
        mr, "cards_for_ids",
        lambda ids: [_card("The Godfather Part II", 8.6, "Coppola", 240)],
    )

    recs = mr.recommend_movies("The Godfather", top_n=1)

    assert recs == [
        {COL_TITLE: "The Godfather Part II", COL_RATING: 8.6, COL_DIRECTOR: "Coppola"}
    ]


def test_blank_title_is_rejected():
    result = mr.recommend_movies("   ", top_n=3)
    assert isinstance(result, str)
    assert "name a movie" in result.lower()


def test_unknown_movie_degrades_gracefully(monkeypatch):
    monkeypatch.setattr(tmdb, "search_movie", lambda t, year=None: None)

    result = mr.recommend_movies("zzzz not a real movie zzzz", top_n=3)

    assert isinstance(result, str)
    assert "not found" in result.lower()


def test_no_recommendations_message(monkeypatch):
    monkeypatch.setattr(tmdb, "search_movie", lambda t, year=None: {"id": 1})
    monkeypatch.setattr(tmdb, "movie_recommendations", lambda mid, limit=3: [])

    result = mr.recommend_movies("Obscure Film", top_n=3)

    assert isinstance(result, str)
    assert "no recommendations" in result.lower()
