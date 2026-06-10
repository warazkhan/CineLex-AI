"""Structured movie "cards" for the API / UI.

A *card* is a small JSON-serialisable dict that the front-end renders as a
poster tile. Every answer path (analytics, RAG fuzzy/retrieval, recommend)
emits the same shape, so the UI needs only one renderer.

The IMDB Top 1000 dataset ships a real ``Poster_Link`` column, so cards carry
poster URLs with no external API or key.
"""
import math
from typing import Any, Optional

from cinellex_rag.core.data_loader import load_imdb
from config.schema_config import (
    COL_TITLE,
    COL_YEAR,
    COL_RATING,
    COL_OVERVIEW,
    COL_GENRE,
    COL_DIRECTOR,
    COL_STAR1,
    COL_STAR2,
    COL_STAR3,
    COL_STAR4,
    COL_GROSS,
    COL_VOTES,
)

# Columns not (yet) in schema_config but present in the dataset.
COL_POSTER = "Poster_Link"
COL_RUNTIME = "Runtime"
COL_CERT = "Certificate"

KIND_MOVIE = "movie"
KIND_DIRECTOR = "director"


def _clean(value: Any) -> Optional[Any]:
    """Normalise pandas/sqlite NaN and empty strings to None."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def _to_int(value: Any) -> Optional[int]:
    value = _clean(value)
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> Optional[float]:
    value = _clean(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_gross(value: Any) -> Optional[int]:
    value = _clean(value)
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    digits = str(value).replace(",", "").replace("$", "").strip()
    try:
        return int(float(digits))
    except ValueError:
        return None


def build_card(row: Any, subtitle: Optional[str] = None) -> dict:
    """Build a movie card from a dict-like row.

    ``row`` may be a pandas Series or a plain dict (sqlite rows should be
    converted with ``dict(row)`` first). Missing fields become ``None``.
    """
    get = row.get  # both pandas.Series and dict support .get

    stars = [_clean(get(c)) for c in (COL_STAR1, COL_STAR2, COL_STAR3, COL_STAR4)]
    stars = [s for s in stars if s]

    return {
        "kind": KIND_MOVIE,
        "title": _clean(get(COL_TITLE)),
        "year": _to_int(get(COL_YEAR)),
        "rating": _to_float(get(COL_RATING)),
        "genre": _clean(get(COL_GENRE)),
        "director": _clean(get(COL_DIRECTOR)),
        "overview": _clean(get(COL_OVERVIEW)),
        "poster": _clean(get(COL_POSTER)),
        "runtime": _clean(get(COL_RUNTIME)),
        "certificate": _clean(get(COL_CERT)),
        "gross": _parse_gross(get(COL_GROSS)),
        "votes": _to_int(get(COL_VOTES)),
        "stars": stars,
        "subtitle": subtitle,
    }


def director_card(name: str, count: int, top_movie: Optional[dict] = None) -> dict:
    """Build a card representing a director (name + film count + a representative
    poster taken from their highest-rated film)."""
    card = build_card(top_movie) if top_movie else {}
    best = card.get("title")
    return {
        "kind": KIND_DIRECTOR,
        "title": name,
        "subtitle": f"{count} {'film' if count == 1 else 'films'} in the Top 1000",
        "poster": card.get("poster"),
        "overview": f"Top-rated: {best} (★ {card.get('rating')})" if best else None,
        "rating": None,
        "year": None,
        "genre": None,
        "director": None,
        "stars": [],
    }


def card_from_title(title: str, subtitle: Optional[str] = None) -> Optional[dict]:
    """Look up a movie by case-insensitive exact title and build its card."""
    if not title:
        return None
    df = load_imdb()
    matches = df[df[COL_TITLE].str.lower() == str(title).strip().lower()]
    if matches.empty:
        return None
    return build_card(matches.iloc[0], subtitle=subtitle)
