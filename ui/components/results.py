"""Renders the answer area: rich movie cards (or text), a developer reveal,
and clickable recent searches. The empty state is the landing screen."""
import html

import streamlit as st

from ui.components.movie_cards import render_movie_grid, render_movie_hero
from ui.config import MAX_HISTORY_ITEMS

# Routes whose text answer is a real narrative worth showing alongside cards.
_NARRATIVE_ROUTES = {"recommend", "rag"}


def render_results() -> None:
    if not st.session_state.history:
        _render_empty_state()
        return

    _render_answer(st.session_state.history[0])
    _render_recent(st.session_state.history[1:1 + MAX_HISTORY_ITEMS])


# --------------------------------------------------------------------------- #
# Latest answer
# --------------------------------------------------------------------------- #
def _render_answer(item: dict) -> None:
    movies = item.get("movies") or []
    route = item.get("route", "unknown")

    st.markdown(
        f'<div class="query-echo">Showing results for '
        f'<strong>{html.escape(item["query"])}</strong></div>',
        unsafe_allow_html=True,
    )

    if len(movies) == 1 and movies[0].get("kind") == "movie":
        # Single film → big hero card (covers "tell me about X").
        render_movie_hero(movies[0])
    elif movies:
        # A list / set of films. Show the narrative first when it adds value.
        if route in _NARRATIVE_ROUTES and item.get("answer"):
            _render_text(item["answer"])
        render_movie_grid(movies)
    else:
        _render_text(item["answer"])

    _render_dev_details(item)


def _render_text(answer: str) -> None:
    st.markdown(
        f'<div class="answer-card"><div class="answer-text">{html.escape(answer)}</div></div>',
        unsafe_allow_html=True,
    )


def _render_dev_details(item: dict) -> None:
    """The interview reveal: how the answer was produced. Hidden by default."""
    meta = item.get("metadata") or {}
    with st.expander("🛠  How I answered this"):
        cols = st.columns(3)
        cols[0].metric("Route", str(item.get("route", "—")).capitalize())
        cols[1].metric("Source", str(item.get("source", "—")))
        cols[2].metric("Latency", f'{item["elapsed_ms"]} ms' if item.get("elapsed_ms") else "—")

        extras = {k: v for k, v in meta.items() if k != "contexts"}
        if extras:
            st.caption("Metadata")
            st.json(extras, expanded=False)

        contexts = meta.get("contexts")
        if contexts:
            st.caption(f"Retrieved context ({len(contexts)} chunks fed to the LLM)")
            for i, ctx in enumerate(contexts, 1):
                st.text(f"[{i}] {ctx}")

        if item.get("answer"):
            st.caption("Raw answer text")
            st.code(item["answer"], language=None)


# --------------------------------------------------------------------------- #
# Recent searches (clickable)
# --------------------------------------------------------------------------- #
def _render_recent(items: list) -> None:
    if not items:
        return

    st.markdown('<div class="recent-label">Recent searches</div>', unsafe_allow_html=True)
    for i, item in enumerate(items):
        icon = "📊" if item.get("route") == "analytics" else (
            "✨" if item.get("route") == "recommend" else "🎬"
        )
        if st.button(f"{icon}  {item['query']}", key=f"recent_{i}", use_container_width=True):
            st.session_state.prefill = item["query"]
            st.session_state.pending_query = item["query"]
            st.session_state.trigger_search = True
            st.session_state.widget_version += 1
            st.rerun()


# --------------------------------------------------------------------------- #
# Empty state / landing
# --------------------------------------------------------------------------- #
def _render_empty_state() -> None:
    st.markdown(
        """
    <div class="empty-state">
      <div class="empty-icon">🍿</div>
      <div class="empty-title">What do you want to know about movies?</div>
      <div class="empty-sub">Ask about a film, rankings, directors, or get recommendations — pick a suggestion above to start.</div>
    </div>""",
        unsafe_allow_html=True,
    )
