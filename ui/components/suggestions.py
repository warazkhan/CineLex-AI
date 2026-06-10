"""Clickable example-query chips, shown only before the first search."""
import streamlit as st

from ui.config import SUGGESTIONS


def render_suggestions() -> None:
    # Suggestions disappear once the user has run at least one query.
    if st.session_state.history:
        return

    st.markdown('<div class="chips-label">Try asking</div>', unsafe_allow_html=True)

    cols = st.columns(len(SUGGESTIONS))
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i]:
            if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                st.session_state.prefill = suggestion
                st.session_state.pending_query = suggestion
                st.session_state.trigger_search = True
                st.session_state.widget_version += 1
                st.rerun()
