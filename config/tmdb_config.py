"""Configuration for the live TMDB (The Movie Database) data client.

TMDB is the app's only data source. All values are read from the environment
(``.env`` is loaded here so this module works regardless of import order).
With no ``TMDB_API_KEY`` set, :data:`TMDB_ENABLED` is ``False`` and every route
degrades to a friendly "TMDB not configured" message instead of movie data.
"""
import os

from dotenv import load_dotenv

from config.data_config import PROJECT_ROOT

load_dotenv()


def _flag(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in ("0", "false", "no", "off", "")


# A v3 API key (``api_key=`` query param) *or* a v4 Read Access Token (Bearer).
# Both are accepted; the client picks the right auth style automatically.
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()

# Master switch. Enrichment only runs when a key is present AND not disabled.
TMDB_ENABLED = bool(TMDB_API_KEY) and _flag("TMDB_ENABLED", True)

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

# Poster width directive: w185, w342, w500, w780 or original.
TMDB_POSTER_SIZE = os.getenv("TMDB_POSTER_SIZE", "w500").strip() or "w500"

# Language / region for titles, overviews and certifications.
TMDB_LANG = os.getenv("TMDB_LANG", "en-US").strip() or "en-US"

# Minimum vote count for ranking queries (mirrors TMDB's own "top rated" rule
# so obscure films with a handful of perfect votes don't dominate rankings).
TMDB_VOTE_COUNT_FLOOR = int(os.getenv("TMDB_VOTE_COUNT_FLOOR", "300"))

# Per-request HTTP timeout (seconds) — kept short so a slow/unreachable TMDB
# never stalls a query; on timeout the card is returned un-enriched.
TMDB_TIMEOUT = float(os.getenv("TMDB_TIMEOUT", "4"))

# Thread-pool size for enriching a list of cards concurrently.
TMDB_MAX_WORKERS = int(os.getenv("TMDB_MAX_WORKERS", "8"))

# Lookups are memoised here between runs so a given title is only fetched once.
TMDB_CACHE_PATH = PROJECT_ROOT / "data" / "tmdb_cache.json"
