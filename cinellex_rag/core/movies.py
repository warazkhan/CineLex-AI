"""Structured movie "cards" for the API / UI, built from live TMDB data.

A *card* is a small JSON-serialisable dict the front-end renders as a poster
tile. Every answer path (analytics, RAG, recommend) emits the same shape, so the
UI needs only one renderer.

This module maps raw TMDB dicts (from :mod:`cinellex_rag.core.tmdb`) into that
shape. It depends on ``tmdb`` one-way; ``tmdb`` knows nothing about cards.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from cinellex_rag.core import tmdb
from config.tmdb_config import (
    TMDB_ENABLED,
    TMDB_IMAGE_BASE,
    TMDB_MAX_WORKERS,
    TMDB_POSTER_SIZE,
)

KIND_MOVIE = "movie"


# --------------------------------------------------------------------------- #
# Field helpers
# --------------------------------------------------------------------------- #
def _poster_url(path: Optional[str]) -> Optional[str]:
    return f"{TMDB_IMAGE_BASE}/{TMDB_POSTER_SIZE}{path}" if path else None


def _year(release_date: Optional[str]) -> Optional[int]:
    if release_date and len(release_date) >= 4 and release_date[:4].isdigit():
        return int(release_date[:4])
    return None


def _rating(vote_average: Any) -> Optional[float]:
    try:
        v = round(float(vote_average), 1)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _runtime(minutes: Any) -> Optional[str]:
    try:
        m = int(minutes)
        return f"{m} min" if m > 0 else None
    except (TypeError, ValueError):
        return None


def _gross(revenue: Any) -> Optional[int]:
    try:
        r = int(revenue)
        return r if r > 0 else None
    except (TypeError, ValueError):
        return None


def _director(credits: dict) -> Optional[str]:
    for member in (credits or {}).get("crew", []):
        if member.get("job") == "Director":
            return member.get("name")
    return None


def _stars(credits: dict, n: int = 4) -> list:
    cast = (credits or {}).get("cast", []) or []
    return [c.get("name") for c in cast[:n] if c.get("name")]


def _genres_from_list(genres: list) -> Optional[str]:
    names = [g.get("name") for g in (genres or []) if g.get("name")]
    return ", ".join(names) or None


def _genres_from_ids(genre_ids: list) -> Optional[str]:
    gmap = tmdb.genre_map()
    names = [gmap.get(gid) for gid in (genre_ids or []) if gmap.get(gid)]
    return ", ".join(names) or None


def _certificate(release_dates: dict, prefer: str = "US") -> Optional[str]:
    """Pull a content rating from the (US by default) release-dates block."""
    results = (release_dates or {}).get("results", []) or []
    by_country = {r.get("iso_3166_1"): r for r in results}
    entry = by_country.get(prefer) or (results[0] if results else None)
    for rel in (entry or {}).get("release_dates", []) or []:
        cert = (rel.get("certification") or "").strip()
        if cert:
            return cert
    return None


# --------------------------------------------------------------------------- #
# Card builders
# --------------------------------------------------------------------------- #
def card_from_details(d: dict, subtitle: Optional[str] = None) -> dict:
    """Build a full card from a ``/movie/{id}`` details payload (with
    ``credits``, ``videos`` and ``release_dates`` appended)."""
    credits = d.get("credits", {})
    return {
        "kind": KIND_MOVIE,
        "title": d.get("title") or d.get("original_title"),
        "year": _year(d.get("release_date")),
        "rating": _rating(d.get("vote_average")),
        "genre": _genres_from_list(d.get("genres")),
        "director": _director(credits),
        "overview": d.get("overview") or None,
        "poster": _poster_url(d.get("poster_path")),
        "runtime": _runtime(d.get("runtime")),
        "certificate": _certificate(d.get("release_dates")),
        "gross": _gross(d.get("revenue")),
        "votes": d.get("vote_count") or None,
        "stars": _stars(credits),
        "tmdb_id": d.get("id"),
        "imdb_id": d.get("imdb_id") or None,
        "popularity": d.get("popularity"),
        "trailer": tmdb.pick_trailer(d.get("videos")),
        "subtitle": subtitle,
    }


def card_from_search(r: dict, subtitle: Optional[str] = None) -> dict:
    """Lighter card from a search/discover result (no per-movie details call).

    Director, cast, runtime, gross and trailer are unavailable here; use
    :func:`card_from_details` / :func:`cards_for_ids` when those matter.
    """
    return {
        "kind": KIND_MOVIE,
        "title": r.get("title") or r.get("original_title"),
        "year": _year(r.get("release_date")),
        "rating": _rating(r.get("vote_average")),
        "genre": _genres_from_ids(r.get("genre_ids")),
        "director": None,
        "overview": r.get("overview") or None,
        "poster": _poster_url(r.get("poster_path")),
        "runtime": None,
        "certificate": None,
        "gross": None,
        "votes": r.get("vote_count") or None,
        "stars": [],
        "tmdb_id": r.get("id"),
        "imdb_id": None,
        "popularity": r.get("popularity"),
        "trailer": None,
        "subtitle": subtitle,
    }


def cards_for_ids(ids: list) -> list:
    """Fetch full details for several movie ids concurrently → full cards.

    Order is preserved; ids that fail to resolve are dropped.
    """
    ids = [i for i in ids if i]
    if not ids:
        return []
    workers = min(TMDB_MAX_WORKERS, len(ids))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        details = list(pool.map(tmdb.movie_details, ids))
    return [card_from_details(d) for d in details if d]


def card_from_title(title: str, year=None, subtitle: Optional[str] = None) -> Optional[dict]:
    """Resolve a title to a full card via live TMDB search + details."""
    if not TMDB_ENABLED or not title:
        return None
    hit = tmdb.search_movie(title, year=year)
    if not hit:
        return None
    details = tmdb.movie_details(hit.get("id"))
    if not details:
        return card_from_search(hit, subtitle=subtitle)
    card = card_from_details(details, subtitle=subtitle)
    return card
