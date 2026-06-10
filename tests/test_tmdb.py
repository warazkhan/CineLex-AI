"""Tests for the live TMDB data client and the TMDB→card mapper.

All network access is mocked via ``tmdb._get`` — these never hit the real API.
"""
import pytest
import requests

from cinellex_rag.core import tmdb
from cinellex_rag.core import movies


# --- canned TMDB payloads ---------------------------------------------------
SEARCH_RESULT = {
    "results": [
        {
            "id": 278,
            "title": "The Shawshank Redemption",
            "release_date": "1994-09-23",
            "vote_average": 8.7,
            "vote_count": 26000,
            "poster_path": "/search.jpg",
            "popularity": 88.5,
            "genre_ids": [18, 80],
        }
    ]
}

DETAILS_RESULT = {
    "id": 278,
    "title": "The Shawshank Redemption",
    "original_title": "The Shawshank Redemption",
    "release_date": "1994-09-23",
    "vote_average": 8.7,
    "vote_count": 26000,
    "runtime": 142,
    "revenue": 28341469,
    "overview": "Two imprisoned men bond over a number of years.",
    "poster_path": "/details.jpg",
    "imdb_id": "tt0111161",
    "popularity": 88.5,
    "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
    "credits": {
        "crew": [
            {"job": "Editor", "name": "Richard Francis-Bruce"},
            {"job": "Director", "name": "Frank Darabont"},
        ],
        "cast": [{"name": "Tim Robbins"}, {"name": "Morgan Freeman"}],
    },
    "videos": {
        "results": [
            {"site": "YouTube", "key": "teaser", "type": "Teaser", "official": False},
            {"site": "Vimeo", "key": "nope", "type": "Trailer", "official": True},
            {"site": "YouTube", "key": "official", "type": "Trailer", "official": True},
        ]
    },
    "release_dates": {
        "results": [{"iso_3166_1": "US", "release_dates": [{"certification": "R"}]}]
    },
}

RECS_RESULT = {"results": [{"id": 238}, {"id": 240}, {"id": 424}]}
DISCOVER_RESULT = {"results": [{"id": 278}, {"id": 238}]}
GENRES_RESULT = {"genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}]}


def _fake_get(path, params=None):
    if path == "/search/movie":
        return SEARCH_RESULT
    if path.endswith("/recommendations"):
        return RECS_RESULT
    if path.startswith("/movie/"):
        return DETAILS_RESULT
    if path == "/discover/movie":
        return DISCOVER_RESULT
    if path == "/genre/movie/list":
        return GENRES_RESULT
    return {}


@pytest.fixture(autouse=True)
def fresh_tmdb(monkeypatch, tmp_path):
    """Isolate each test: client enabled, empty caches, throwaway cache file,
    and the network replaced by the canned ``_fake_get``."""
    monkeypatch.setattr(tmdb, "TMDB_ENABLED", True)
    monkeypatch.setattr(movies, "TMDB_ENABLED", True)
    monkeypatch.setattr(tmdb, "TMDB_CACHE_PATH", tmp_path / "tmdb_cache.json")
    monkeypatch.setattr(tmdb, "_disk", {})
    monkeypatch.setattr(tmdb, "_mem", {})
    monkeypatch.setattr(tmdb, "_dirty", False)
    monkeypatch.setattr(tmdb, "_get", _fake_get)


# --- trailer picking --------------------------------------------------------
def test_pick_trailer_prefers_official_youtube_trailer():
    url = tmdb.pick_trailer(DETAILS_RESULT["videos"])
    assert url == "https://www.youtube.com/watch?v=official"


def test_pick_trailer_handles_no_videos():
    assert tmdb.pick_trailer({"results": []}) is None
    assert tmdb.pick_trailer(None) is None


# --- endpoint wrappers ------------------------------------------------------
def test_search_movie_returns_best_hit():
    hit = tmdb.search_movie("Shawshank")
    assert hit["id"] == 278


def test_search_movies_respects_limit(monkeypatch):
    monkeypatch.setattr(
        tmdb, "_get",
        lambda path, params=None: {"results": [{"id": i} for i in range(10)]},
    )
    assert len(tmdb.search_movies("anything", limit=5)) == 5


def test_movie_recommendations_respects_limit():
    recs = tmdb.movie_recommendations(278, limit=2)
    assert [r["id"] for r in recs] == [238, 240]


def test_genre_map_has_int_keys():
    assert tmdb.genre_map() == {18: "Drama", 80: "Crime"}


def test_movie_details_caches_and_avoids_refetch(monkeypatch):
    calls = {"n": 0}

    def counting_get(path, params=None):
        calls["n"] += 1
        return _fake_get(path, params)

    monkeypatch.setattr(tmdb, "_get", counting_get)

    first = tmdb.movie_details(278)
    after_first = calls["n"]
    second = tmdb.movie_details(278)

    assert first == second
    assert calls["n"] == after_first  # served from the disk cache


def test_discover_uses_in_memory_cache(monkeypatch):
    calls = {"n": 0}

    def counting_get(path, params=None):
        calls["n"] += 1
        return _fake_get(path, params)

    monkeypatch.setattr(tmdb, "_get", counting_get)

    tmdb.discover("vote_average.desc", vote_count_gte=300)
    tmdb.discover("vote_average.desc", vote_count_gte=300)
    assert calls["n"] == 1  # second call served from the in-memory cache


def test_transient_error_is_not_cached(monkeypatch):
    def boom(path, params=None):
        raise requests.RequestException("network down")

    monkeypatch.setattr(tmdb, "_get", boom)

    assert tmdb.movie_details(999) is None
    # a transient failure must not poison the cache — it should retry next time
    assert tmdb._disk == {}


def test_wrappers_short_circuit_when_disabled(monkeypatch):
    monkeypatch.setattr(tmdb, "TMDB_ENABLED", False)

    def fail(*a, **k):  # must not be called
        raise AssertionError("TMDB was queried while disabled")

    monkeypatch.setattr(tmdb, "_get", fail)

    assert tmdb.search_movies("Heat") == []
    assert tmdb.search_movie("Heat") is None
    assert tmdb.movie_details(278) is None
    assert tmdb.movie_recommendations(278) == []
    assert tmdb.discover("vote_average.desc") == []
    assert tmdb.genre_map() == {}


# --- TMDB → card mapping ----------------------------------------------------
def test_card_from_details_maps_full_shape():
    card = movies.card_from_details(DETAILS_RESULT)

    assert card["kind"] == "movie"
    assert card["title"] == "The Shawshank Redemption"
    assert card["year"] == 1994
    assert card["rating"] == 8.7
    assert card["genre"] == "Drama, Crime"
    assert card["director"] == "Frank Darabont"
    assert card["runtime"] == "142 min"
    assert card["certificate"] == "R"
    assert card["gross"] == 28341469
    assert card["votes"] == 26000
    assert card["stars"] == ["Tim Robbins", "Morgan Freeman"]
    assert card["tmdb_id"] == 278
    assert card["imdb_id"] == "tt0111161"
    assert card["trailer"].endswith("official")


def test_cards_for_ids_builds_full_cards():
    cards = movies.cards_for_ids([278])
    assert len(cards) == 1
    assert cards[0]["title"] == "The Shawshank Redemption"
    assert cards[0]["director"] == "Frank Darabont"
