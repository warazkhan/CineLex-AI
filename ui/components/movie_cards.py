"""Renders structured movie cards (hero card, poster grid).

All paths return the same card shape (see cinellex_rag/core/movies.py), so this
is the single place that knows how a movie looks on screen.
"""
import html
import re

import streamlit as st

from ui.config import POSTER_WIDTH


def _upscale_poster(url: str) -> str:
    """Request a larger poster from the Amazon media CDN.

    Dataset URLs look like ``..._V1_UX67_CR0,0,67,98_AL_.jpg`` (a 67px thumb);
    swapping the size directive yields a crisp full-size poster.
    """
    if not url:
        return url
    return re.sub(r"\._V1_.*?\.jpg$", f"._V1_UX{POSTER_WIDTH}.jpg", url)


def _poster(url: str, css_class: str) -> str:
    if url:
        return (
            f'<img class="{css_class}" src="{html.escape(_upscale_poster(url))}" '
            f'loading="lazy" alt="">'
        )
    # Empty div — the placeholder art (icon + label) is drawn in CSS so the
    # same look is reused for broken <img> URLs via ::before/::after.
    return f'<div class="{css_class} poster-fallback"></div>'


def _rating_badge(rating) -> str:
    return f'<span class="rating-badge">★ {rating}</span>' if rating else ""


def _trailer_link(url: str, css_class: str = "trailer-link") -> str:
    """Render a YouTube trailer link (from TMDB enrichment), if present."""
    if not url:
        return ""
    return (
        f'<a class="{css_class}" href="{html.escape(url)}" target="_blank" '
        f'rel="noopener noreferrer">▶ Trailer</a>'
    )


def _fmt_votes(votes) -> str:
    if not votes:
        return ""
    if votes >= 1_000_000:
        return f"{votes / 1_000_000:.1f}M votes"
    if votes >= 1_000:
        return f"{votes / 1_000:.0f}K votes"
    return f"{votes} votes"


def render_movie_hero(m: dict) -> None:
    """Large single-movie card (poster + full details) for 'tell me about X'."""
    title = html.escape(m.get("title") or "")
    year = f'<span class="mh-year">{m["year"]}</span>' if m.get("year") else ""

    meta_bits = [b for b in (m.get("genre"), m.get("runtime"), m.get("certificate")) if b]
    meta = " · ".join(html.escape(str(b)) for b in meta_bits)

    badges = " ".join(b for b in (_rating_badge(m.get("rating")), ) if b)
    votes = _fmt_votes(m.get("votes"))
    votes_html = f'<span class="mh-votes">{votes}</span>' if votes else ""
    trailer = _trailer_link(m.get("trailer"))

    overview = html.escape(m.get("overview") or "")
    director = (
        f'<div class="mh-credit"><span class="lbl">Director</span> '
        f'{html.escape(m["director"])}</div>'
        if m.get("director") else ""
    )
    stars = m.get("stars") or []
    stars_html = (
        '<div class="mh-stars">'
        + "".join(f'<span class="star-chip">{html.escape(s)}</span>' for s in stars)
        + "</div>"
        if stars else ""
    )

    st.markdown(
        f'<div class="movie-hero">'
        f'  <div class="mh-poster">{_poster(m.get("poster"), "mh-img")}</div>'
        f'  <div class="mh-body">'
        f'    <div class="mh-title">{title} {year}</div>'
        f'    <div class="mh-meta">{meta}</div>'
        f'    <div class="mh-badges">{badges} {votes_html} {trailer}</div>'
        f'    <div class="mh-overview">{overview}</div>'
        f'    {director}{stars_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _card_html(m: dict) -> str:
    title = html.escape(m.get("title") or "")

    if m.get("subtitle"):
        sub = html.escape(str(m["subtitle"]))
    else:
        bits = [str(b) for b in (m.get("year"), m.get("genre")) if b]
        sub = html.escape(" · ".join(bits))

    badge = _rating_badge(m.get("rating"))
    trailer = _trailer_link(m.get("trailer"), css_class="trailer-link mc-trailer")

    return (
        f'<div class="movie-card">'
        f'  <div class="mc-poster">{_poster(m.get("poster"), "mc-img")}{badge}</div>'
        f'  <div class="mc-body">'
        f'    <div class="mc-title">{title}</div>'
        f'    <div class="mc-sub">{sub}</div>'
        f'    {trailer}'
        f'  </div>'
        f'</div>'
    )


def render_movie_grid(movies: list) -> None:
    """Responsive poster grid for lists and recommendations."""
    cards = "".join(_card_html(m) for m in movies)
    st.markdown(f'<div class="movie-grid">{cards}</div>', unsafe_allow_html=True)
