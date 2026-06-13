"""Executes a queued search and records the result in history.

UI components only *flag* that a search should run (by setting
``searching`` / ``pending_query``). This module performs the actual API call
exactly once per rerun, keeping the side-effecting logic in one place. The
in-flight loader is drawn by the search bar (near the input); by the time this
runs, that loader is already on screen, so the blocking call is covered.
"""
import streamlit as st

from ui.api_client import call_api


def process_pending_search() -> None:
    """Run a queued search, if one was triggered this rerun."""
    if not st.session_state.searching:
        return

    query = st.session_state.pending_query.strip()
    if not query:
        st.session_state.searching = False
        return

    st.session_state.prefill = query
    data, error = call_api(query)
    st.session_state.searching = False

    if error:
        st.session_state.search_error = error
        st.rerun()
        return

    st.session_state.search_error = ""
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
