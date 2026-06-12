"""Deterministic ranking queries, served live from TMDB ``/discover``.

Replaces the old SQLite analytics. Each query maps to a TMDB ``sort_by`` and the
top results are expanded into full cards (one details call each, cached).
"""
import re

from cinellex_rag.core import tmdb
from cinellex_rag.core.movies import cards_for_ids
from config.tmdb_config import TMDB_ENABLED


def extract_n(query: str, default: int = 5) -> int:
    """Extract a number from a query like 'top 10 movies'."""
    match = re.search(r"\b(\d+)\b", query)
    return int(match.group(1)) if match else default


def _result(answer: str, movies: list, kind: str = None) -> dict:
    """Uniform analytics result (matches handle_rag's shape)."""
    return {
        "answer": answer,
        "movies": movies,
        "source": "analytics",
        "metadata": {"kind": kind} if kind else {},
    }


def handle_analytics(query: str, top_n: int = None) -> dict:
    """Live TMDB analytics. Returns a text ``answer`` plus structured ``movies``
    cards the UI renders as posters."""
    q = query.lower()
    top_n = top_n or extract_n(q)

    if not TMDB_ENABLED:
        return _result("Live movie data is unavailable — TMDB is not configured.", [])

    if ("highest" in q and "gross" in q) or ("highest" in q and "earn" in q):
        rows = tmdb.discover("revenue.desc", vote_count_gte=tmdb.VOTE_FLOOR)[:top_n]
        cards = cards_for_ids([r["id"] for r in rows])
        for c in cards:
            if c.get("gross"):
                c["subtitle"] = f"${c['gross']:,.0f} gross"
        text = "\n".join(
            f"{c['title']} ({c['year']}) — Gross: ${c['gross']:,.0f}"
            for c in cards if c.get("gross")
        )
        return _result(text or "No gross figures available.", cards, kind="movie_list")

    if "worst" in q and "movie" in q:
        rows = tmdb.discover("vote_average.asc", vote_count_gte=tmdb.VOTE_FLOOR)[:top_n]
        cards = cards_for_ids([r["id"] for r in rows])
        return _result(_fmt_rated(cards), cards, kind="movie_list")

    if "latest" in q or "recent" in q:
        rows = tmdb.discover(
            "primary_release_date.desc",
            vote_count_gte=50,
            release_lte=tmdb.TODAY,
        )[:top_n]
        cards = cards_for_ids([r["id"] for r in rows])
        text = "\n".join(f"{c['title']} ({c['year']})" for c in cards)
        return _result(text, cards, kind="movie_list")

    if ("top" in q and "movie" in q) or ("best" in q and "movie" in q):
        rows = tmdb.discover("vote_average.desc", vote_count_gte=tmdb.VOTE_FLOOR)[:top_n]
        cards = cards_for_ids([r["id"] for r in rows])
        return _result(_fmt_rated(cards), cards, kind="movie_list")

    return _result("No analytics pattern matched.", [])


def _fmt_rated(cards) -> str:
    return "\n".join(
        f"{c['title']} ({c['year']}) — Rating: {c['rating']}" for c in cards
    )
