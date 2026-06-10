"""Sidebar: a short, user-facing 'About' panel.

Deliberately *not* a telemetry dashboard — engineering details (route, source,
latency, retrieved context) live in the per-answer "How I answered this"
reveal instead, so the main surface reads as a product, not an internal tool.
"""
import streamlit as st


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="sb-wordmark">Cine<span class="accent">Lex</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="sb-about">CineLex is an AI movie companion. Ask in plain '
            'English — it figures out whether you want facts, a summary, or a '
            'recommendation, and answers using live data from The Movie '
            'Database (TMDB).</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sb-section-label">How it works</div>', unsafe_allow_html=True)
        st.markdown(
            '<ul class="sb-list">'
            '<li><b>Rankings & facts</b> — top films, directors, latest, highest-grossing.</li>'
            '<li><b>About a film</b> — plot, cast and details for any title.</li>'
            '<li><b>Recommendations</b> — "movies like Inception".</li>'
            '</ul>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sb-section-label">Try asking</div>', unsafe_allow_html=True)
        st.markdown(
            '<ul class="sb-list sb-examples">'
            '<li>Top 10 movies by rating</li>'
            '<li>Tell me about The Godfather</li>'
            '<li>Movies like Interstellar</li>'
            '</ul>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sb-footer">Data: The Movie Database (TMDB) · Built with FastAPI</div>',
            unsafe_allow_html=True,
        )
