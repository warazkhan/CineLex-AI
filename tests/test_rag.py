"""Tests for the descriptive RAG handler's facet (concept) retrieval.

TMDB and the LLM are both mocked — these never hit the network. The focus is the
retrieval *routing*: a thematic question should be answered by resolving LLM
facets to TMDB keyword/genre ids and discovering over them, while degrading to
the legacy title search when no facet resolves or the LLM is unavailable.
"""
import json

import pytest

from cinellex_rag.retrieval import rag
from cinellex_rag.core import tmdb


# --- fakes ------------------------------------------------------------------
GENRES = {18: "Drama", 80: "Crime", 878: "Science Fiction"}


def _facet_json(title=None, keywords=None, genres=None):
    return json.dumps({
        "title": title,
        "keywords": keywords or [],
        "genres": genres or [],
    })


@pytest.fixture(autouse=True)
def enabled(monkeypatch):
    """Enable the handler and stub the genre map (used by facet resolution)."""
    monkeypatch.setattr(rag, "TMDB_ENABLED", True)
    monkeypatch.setattr(tmdb, "genre_map", lambda: GENRES)
    # cards_for_ids → a tiny card per id so context-building never touches network
    monkeypatch.setattr(
        rag, "cards_for_ids",
        lambda ids: [{"title": f"M{i}", "year": 2000, "genre": "Drama",
                      "director": "D", "overview": "o", "tmdb_id": i} for i in ids],
    )


def _stub_generate(facet_reply):
    """A generate() double: returns the facet JSON for the extraction prompt and
    a canned answer for the final answer prompt."""
    def _gen(prompt, max_tokens=500):
        return facet_reply if "TMDB search facets" in prompt else "ANSWER"
    return _gen


# --- facet retrieval --------------------------------------------------------
def test_facets_drive_keyword_genre_discovery(monkeypatch):
    monkeypatch.setattr(rag, "generate",
                        _stub_generate(_facet_json(keywords=["heist", "dream"],
                                                   genres=["Science Fiction"])))
    monkeypatch.setattr(tmdb, "search_keywords",
                        lambda phrase, limit=1: [{"id": 100 + len(phrase)}])

    seen = {}

    def fake_discover(sort_by, *, vote_count_gte=None, with_keywords=None,
                      with_genres=None, **kw):
        seen["with_keywords"] = with_keywords
        seen["with_genres"] = with_genres
        return [{"id": 278}, {"id": 238}, {"id": 424}]

    monkeypatch.setattr(tmdb, "discover", fake_discover)
    # title search must NOT be needed: discovery already fills k
    monkeypatch.setattr(tmdb, "search_movie", lambda *a, **k: pytest.fail("unused"))
    monkeypatch.setattr(tmdb, "search_movies", lambda *a, **k: pytest.fail("unused"))

    res = rag.handle_rag("a thief who enters dreams", k=3, use_fuzzy=False)

    assert res["source"] == "retrieval"
    assert res["answer"] == "ANSWER"
    # two keyword phrases → two resolved ids, AND-joined; SF genre id 878
    assert seen["with_keywords"] == "105,105"
    assert seen["with_genres"] == "878"
    assert [m["tmdb_id"] for m in res["movies"]] == [278, 238, 424]
    assert res["metadata"]["facets"]["keywords"] == ["heist", "dream"]


def test_named_title_is_pinned_first(monkeypatch):
    monkeypatch.setattr(rag, "generate",
                        _stub_generate(_facet_json(title="Inception",
                                                   keywords=["dream"])))
    monkeypatch.setattr(tmdb, "search_keywords", lambda phrase, limit=1: [{"id": 9840}])
    monkeypatch.setattr(tmdb, "discover", lambda *a, **k: [{"id": 238}, {"id": 424}])
    monkeypatch.setattr(tmdb, "search_movie", lambda title, **k: {"id": 27205})  # Inception

    res = rag.handle_rag("the dream-heist movie", k=3, use_fuzzy=False)

    # the resolved title id leads, followed by discovery hits
    assert [m["tmdb_id"] for m in res["movies"]] == [27205, 238, 424]


def test_falls_back_to_title_search_when_no_facets(monkeypatch):
    # LLM returns junk → no facets → discovery skipped → legacy title search runs
    monkeypatch.setattr(rag, "generate", _stub_generate("not json at all"))

    def fail_discover(*a, **k):
        pytest.fail("discover should not run without facets")

    monkeypatch.setattr(tmdb, "discover", fail_discover)
    monkeypatch.setattr(tmdb, "search_keywords", lambda *a, **k: [])
    monkeypatch.setattr(tmdb, "search_movies",
                        lambda q, limit=3: [{"id": 550}, {"id": 551}])

    res = rag.handle_rag("Fight Club", k=3, use_fuzzy=False)

    assert [m["tmdb_id"] for m in res["movies"]] == [550, 551]
    assert res["metadata"]["facets"] == {}


def test_disabled_returns_friendly_message(monkeypatch):
    monkeypatch.setattr(rag, "TMDB_ENABLED", False)
    res = rag.handle_rag("anything", use_fuzzy=False)
    assert res["movies"] == []
    assert "unavailable" in res["answer"].lower()


# --- facet extraction unit --------------------------------------------------
def test_extract_facets_parses_chatty_reply(monkeypatch):
    chatty = 'Sure! Here is the JSON:\n```json\n' + _facet_json(
        title="Heat", keywords=["bank robbery"], genres=["Crime"]) + '\n```'
    monkeypatch.setattr(rag, "generate", lambda *a, **k: chatty)

    facets = rag._extract_facets("a meticulous bank heist crew")
    assert facets["title"] == "Heat"
    assert facets["keywords"] == ["bank robbery"]
    assert facets["genres"] == ["Crime"]


def test_extract_facets_degrades_on_llm_error(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("groq down")  # any provider/network error

    monkeypatch.setattr(rag, "generate", boom)
    # Best-effort contract: an LLM failure must not raise, just yield no facets.
    assert rag._extract_facets("x") == {}
