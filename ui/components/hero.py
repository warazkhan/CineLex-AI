"""Centered hero header: wordmark, tagline and a subtle live status dot."""
import streamlit as st

from ui.api_client import is_backend_healthy


def render_hero() -> None:
    if is_backend_healthy():
        status = '<div class="hero-status online"><span class="dot"></span>Online</div>'
    else:
        status = '<div class="hero-status offline"><span class="dot"></span>Backend offline</div>'

    st.markdown(
        f"""
<div class="hero-center">
  <div class="hero-wordmark">Cine<span class="accent">Lex</span></div>
  <div class="hero-tagline">Your AI companion for movies — ask anything about cinema</div>
  {status}
</div>
""",
        unsafe_allow_html=True,
    )
