"""TMDB (The Movie Database) data client — the app's only source of movie data.

CineLex is fully live on TMDB: there is no local catalog, SQLite or vector
store. This module owns the HTTP plumbing, auth, caching and the typed endpoint
wrappers; :mod:`cinellex_rag.core.movies` turns the raw dicts returned here into
the UI's card shape.

Contract:
  * **Never raises to callers.** Every public wrapper returns ``None`` / ``[]``
    / ``{}`` on a missing key, timeout, auth failure or HTTP error, so the
    analytics / RAG / recommender handlers can degrade to a friendly message
    instead of crashing.
  * **Cached.** Stable lookups (movie details, search, recommendations, the
    genre map) are memoised in-process and mirrored to ``data/tmdb_cache.json``.
    Volatile ranking queries (``discover``) are cached in-process only, so a
    restart re-reads "latest releases" fresh.
"""
import atexit
import json
import threading
from datetime import date

import requests

from config.tmdb_config import (
    TMDB_API_BASE,
    TMDB_API_KEY,
    TMDB_CACHE_PATH,
    TMDB_ENABLED,
    TMDB_LANG,
    TMDB_TIMEOUT,
    TMDB_VOTE_COUNT_FLOOR,
)

# --------------------------------------------------------------------------- #
# HTTP plumbing
# --------------------------------------------------------------------------- #
_session: requests.Session | None = None


def _http() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def _auth() -> tuple[dict, dict]:
    """``(headers, params)`` for the configured credential.

    A v4 Read Access Token (a JWT starting ``eyJ``) goes in a Bearer header; a
    v3 API key goes in the ``api_key`` query param.
    """
    if TMDB_API_KEY.startswith("eyJ"):
        return {"Authorization": f"Bearer {TMDB_API_KEY}"}, {}
    return {}, {"api_key": TMDB_API_KEY}


def _get(path: str, params: dict | None = None) -> dict:
    """GET a TMDB endpoint → parsed JSON. Raises ``requests.RequestException``
    on any network/HTTP error so the caching layer can avoid poisoning itself."""
    headers, auth_params = _auth()
    resp = _http().get(
        f"{TMDB_API_BASE}{path}",
        params={"language": TMDB_LANG, **auth_params, **(params or {})},
        headers=headers,
        timeout=TMDB_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------- #
# Caching — disk-backed for stable lookups, in-memory for volatile ones
# --------------------------------------------------------------------------- #
_disk: dict | None = None
_mem: dict = {}
_dirty = False
_lock = threading.Lock()


def _load_disk() -> dict:
    global _disk
    if _disk is None:
        with _lock:
            if _disk is None:
                try:
                    with open(TMDB_CACHE_PATH, encoding="utf-8") as fh:
                        _disk = json.load(fh)
                except (OSError, ValueError):
                    _disk = {}
    return _disk


def _flush() -> None:
    global _dirty
    if not _dirty or _disk is None:
        return
    with _lock:
        try:
            TMDB_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TMDB_CACHE_PATH, "w", encoding="utf-8") as fh:
                json.dump(_disk, fh)
            _dirty = False
        except OSError:
            pass


atexit.register(_flush)


def _disk_cached(key: str, producer):
    """Return a disk-cached value, computing + persisting it on a miss.

    A genuine result (including ``None`` for 'no match') is cached; a transient
    network error returns ``None`` *without* caching, so it retries next time.
    """
    global _dirty
    cache = _load_disk()
    with _lock:
        if key in cache:
            return cache[key]
    try:
        value = producer()
    except (requests.RequestException, ValueError):
        return None
    with _lock:
        cache[key] = value
        _dirty = True
    _flush()
    return value


def _mem_cached(key: str, producer):
    """In-memory cache for volatile data (discover rankings)."""
    if key in _mem:
        return _mem[key]
    try:
        value = producer()
    except (requests.RequestException, ValueError):
        return None
    _mem[key] = value
    return value


# --------------------------------------------------------------------------- #
# Endpoint wrappers (all best-effort: return None/[]/{}, never raise)
# --------------------------------------------------------------------------- #
def search_movies(query: str, limit: int = 5, year=None) -> list:
    """Keyword search → up to ``limit`` movie results (raw TMDB dicts)."""
    if not TMDB_ENABLED or not query:
        return []

    def _do():
        params = {"query": query, "include_adult": "false"}
        if year:
            params["year"] = int(year)
        results = (_get("/search/movie", params) or {}).get("results") or []
        if not results and year:  # retry without the year filter
            results = (_get("/search/movie", {"query": query, "include_adult": "false"}) or {}).get("results") or []
        return results

    key = f"search:{query.strip().lower()}|{int(year) if year else ''}"
    return (_disk_cached(key, _do) or [])[:limit]


def search_movie(query: str, year=None) -> dict | None:
    """Best single match for a title, or None."""
    results = search_movies(query, limit=1, year=year)
    return results[0] if results else None


def movie_details(tmdb_id: int) -> dict | None:
    """Full movie record (genres, runtime, revenue, imdb_id, credits, videos,
    certifications) in a single call, cached on disk."""
    if not TMDB_ENABLED or not tmdb_id:
        return None
    return _disk_cached(
        f"details:{tmdb_id}",
        lambda: _get(
            f"/movie/{tmdb_id}",
            {"append_to_response": "credits,videos,release_dates"},
        ),
    )


def movie_recommendations(tmdb_id: int, limit: int = 12) -> list:
    """TMDB's own 'recommended' list for a movie."""
    if not TMDB_ENABLED or not tmdb_id:
        return []
    results = _disk_cached(
        f"recs:{tmdb_id}",
        lambda: (_get(f"/movie/{tmdb_id}/recommendations") or {}).get("results") or [],
    )
    return (results or [])[:limit]


def discover(sort_by: str, *, vote_count_gte: int | None = None,
             release_lte: str | None = None, page: int = 1) -> list:
    """`/discover/movie` ranking query → raw result dicts (volatile cache)."""
    if not TMDB_ENABLED:
        return []

    def _do():
        params = {"sort_by": sort_by, "include_adult": "false", "page": page}
        if vote_count_gte is not None:
            params["vote_count.gte"] = vote_count_gte
        if release_lte is not None:
            params["release_date.lte"] = release_lte
        return (_get("/discover/movie", params) or {}).get("results") or []

    key = f"discover:{sort_by}|{vote_count_gte}|{release_lte}|{page}"
    return _mem_cached(key, _do) or []


def genre_map() -> dict:
    """``{genre_id: name}`` for mapping search/discover ``genre_ids``."""
    if not TMDB_ENABLED:
        return {}

    def _do():
        genres = (_get("/genre/movie/list") or {}).get("genres") or []
        return {g["id"]: g["name"] for g in genres}

    # genre ids are keyed as strings once round-tripped through JSON on disk.
    raw = _disk_cached("genres", _do) or {}
    return {int(k): v for k, v in raw.items()}


# --------------------------------------------------------------------------- #
# Convenience for handlers
# --------------------------------------------------------------------------- #
TODAY = date.today().isoformat()
VOTE_FLOOR = TMDB_VOTE_COUNT_FLOOR


def pick_trailer(videos: dict | None) -> str | None:
    """Best YouTube clip from a details ``videos`` block — prefer an official
    full trailer."""
    youtube = [
        v for v in (videos or {}).get("results", [])
        if v.get("site") == "YouTube" and v.get("key")
    ]
    if not youtube:
        return None
    best = max(youtube, key=lambda v: (v.get("type") == "Trailer", bool(v.get("official"))))
    return f"https://www.youtube.com/watch?v={best['key']}"
