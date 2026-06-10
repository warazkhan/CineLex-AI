"""Search box (with inline clear button) and the Ask / Clear-history actions."""
import streamlit as st

from ui.state import reset_history


def render_search_bar() -> str:
    """Render the search input and return its current value."""

    def _input() -> str:
        return st.text_input(
            label="query",
            value=st.session_state.prefill,
            placeholder="Ask anything about movies — titles, directors, analytics, recommendations…",
            label_visibility="collapsed",
            key=f"query_box_v{st.session_state.widget_version}",
        )

    # No text yet → full-width input, no clear button.
    if not st.session_state.prefill:
        return _input()

    # With text → put the input and the × on the same row. Columns are the
    # reliable way to lay out two Streamlit widgets side by side (emitting an
    # unclosed <div> via st.markdown does NOT wrap subsequent widgets, so an
    # absolutely-positioned overlay never actually anchored to the input).
    col_input, col_clear = st.columns([14, 1], vertical_alignment="center")
    with col_input:
        query = _input()
    with col_clear:
        if st.button("✕", key="clear_input", help="Clear search"):
            st.session_state.prefill = ""
            st.session_state.widget_version += 1
            st.rerun()
    return query


def render_action_buttons(query: str) -> None:
    """Render the Ask button and (when relevant) the Clear-history button."""
    col_ask, col_clear, _ = st.columns([1.4, 1.2, 6])

    with col_ask:
        if st.button("Ask →", key="ask_btn", use_container_width=True):
            st.session_state.pending_query = query
            st.session_state.trigger_search = True

    with col_clear:
        if st.session_state.history:
            if st.button("Clear history", key="clear_hist", use_container_width=True):
                reset_history()
                st.rerun()
