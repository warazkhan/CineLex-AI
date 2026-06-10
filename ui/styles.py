"""Loads the UI stylesheet.

The CSS lives in ``assets/styles.css`` (a real stylesheet, with editor syntax
highlighting) instead of being embedded as a giant Python string.
"""
from functools import lru_cache
from pathlib import Path

import streamlit as st

_CSS_PATH = Path(__file__).parent / "assets" / "styles.css"


@lru_cache(maxsize=1)
def _load_css() -> str:
    return _CSS_PATH.read_text(encoding="utf-8")


def inject_styles() -> None:
    """Inject the global stylesheet into the page."""
    st.markdown(f"<style>{_load_css()}</style>", unsafe_allow_html=True)
