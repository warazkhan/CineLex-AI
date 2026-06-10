import re
import sqlite3

from config.data_config import SQLITE_DB_PATH
from cinellex_rag.core.movies import build_card, director_card


def get_conn():
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def extract_n(query: str, default: int = 5) -> int:
    """Extract number from query like 'top 10 movies'"""
    match = re.search(r'\b(\d+)\b', query)
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
    """Deterministic SQLite analytics.

    Returns a dict with both a text ``answer`` (backwards-compatible) and a
    structured ``movies`` list the UI renders as poster cards.
    """
    q = query.lower()
    top_n = top_n or extract_n(q)
    conn = get_conn()

    try:
        if ("top" in q and "movie" in q) or ("best" in q and "movie" in q):
            rows = conn.execute(
                "SELECT * FROM movies ORDER BY IMDB_Rating DESC LIMIT ?", (top_n,)
            ).fetchall()
            return _result(_fmt_rated(rows), _cards(rows), kind="movie_list")

        if "worst" in q and "movie" in q:
            rows = conn.execute(
                "SELECT * FROM movies ORDER BY IMDB_Rating ASC LIMIT ?", (top_n,)
            ).fetchall()
            return _result(_fmt_rated(rows), _cards(rows), kind="movie_list")

        if "top" in q and "director" in q:
            rows = conn.execute(
                "SELECT Director, COUNT(*) AS movie_count FROM movies "
                "GROUP BY Director ORDER BY movie_count DESC LIMIT ?", (top_n,)
            ).fetchall()
            text = "\n".join(f"{r['Director']} ({r['movie_count']} movies)" for r in rows)
            return _result(text, _director_cards(conn, rows), kind="director_list")

        if "latest" in q or "recent" in q:
            rows = conn.execute(
                "SELECT * FROM movies ORDER BY Released_Year DESC LIMIT ?", (top_n,)
            ).fetchall()
            text = "\n".join(f"{r['Series_Title']} ({int(r['Released_Year'])})" for r in rows)
            return _result(text, _cards(rows), kind="movie_list")

        if ("highest" in q and "gross" in q) or ("highest" in q and "earn" in q):
            rows = conn.execute(
                "SELECT * FROM movies WHERE Gross IS NOT NULL AND Gross != '' "
                "ORDER BY CAST(Gross AS REAL) DESC LIMIT ?", (top_n,)
            ).fetchall()
            text = "\n".join(
                f"{r['Series_Title']} ({int(r['Released_Year'])}) — Gross: ${r['Gross']:,.0f}"
                for r in rows
            )
            cards = [
                build_card(dict(r), subtitle=f"${r['Gross']:,.0f} gross") for r in rows
            ]
            return _result(text, cards, kind="movie_list")

        return _result("No analytics pattern matched.", [])

    finally:
        conn.close()


def _fmt_rated(rows) -> str:
    return "\n".join(
        f"{r['Series_Title']} ({int(r['Released_Year'])}) — Rating: {r['IMDB_Rating']}"
        for r in rows
    )


def _cards(rows) -> list:
    return [build_card(dict(r)) for r in rows]


def _director_cards(conn, rows) -> list:
    """For each director, attach a representative poster from their best film."""
    cards = []
    for r in rows:
        top = conn.execute(
            "SELECT * FROM movies WHERE Director = ? ORDER BY IMDB_Rating DESC LIMIT 1",
            (r["Director"],),
        ).fetchone()
        cards.append(director_card(r["Director"], r["movie_count"], dict(top) if top else None))
    return cards
