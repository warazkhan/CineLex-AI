"""Session-state initialisation."""
import copy

import streamlit as st

from ui.config import SESSION_DEFAULTS


def init_session_state() -> None:
    """Seed st.session_state with defaults on first load.

    Values are deep-copied so mutable defaults (e.g. the history list) are not
    shared across sessions.
    """
    for key, default in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(default)


def reset_history() -> None:
    """Clear the conversation history and reset the search box."""
    st.session_state.history = []
    st.session_state.pending_query = ""
    st.session_state.prefill = ""
    st.session_state.widget_version += 1
