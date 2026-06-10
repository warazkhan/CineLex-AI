"""Executes a pending search and records the result in history.

UI components only *flag* that a search should run (by setting
``trigger_search`` / ``pending_query``). This module performs the actual API
call exactly once per rerun, keeping the side-effecting logic in one place.
"""
import streamlit as st

from ui.api_client import call_api


def process_pending_search() -> None:
    """Run a queued search, if one was triggered this rerun."""
    if not st.session_state.trigger_search:
        return

    # Consume the trigger immediately so a rerun can't fire it twice.
    st.session_state.trigger_search = False
    query = st.session_state.pending_query.strip()
    if not query:
        return

    st.session_state.prefill = query
    with st.spinner("Searching the cinematic universe…"):
        data, error = call_api(query)

    if error:
        _render_error(error)
        return

    st.session_state.history.insert(0, {
        "query": query,
        "answer": (data.get("answer") or "").strip(),
        "route": data.get("route", "unknown"),
        "source": data.get("source", "unknown"),
        "movies": data.get("movies") or [],
        "metadata": data.get("metadata") or {},
        "elapsed_ms": data.get("_elapsed_ms"),
    })
    st.rerun()


def _render_error(message: str) -> None:
    st.markdown(
        f'<div style="background:#fff5f5;border:1px solid #f5c0c0;'
        f'border-left:3px solid #b84040;border-radius:10px;'
        f'padding:1rem 1.2rem;margin-top:1rem;font-size:0.9rem;color:#b84040">'
        f'⚠️ {message}</div>',
        unsafe_allow_html=True,
    )
