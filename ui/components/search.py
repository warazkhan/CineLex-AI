"""Search form (input + inline clear), the Ask submit button and the loader.

The search box is a ``st.form`` so pressing **Enter** in the input submits it.
Streamlit maps the Enter key to the form's *first* ``st.form_submit_button``
(and only when that button is enabled), so we create the "Ask →" button before
the inline "×" (clear) button — Enter therefore always means *search*, never
*clear*. An ``st.container`` reserves the top row so the input still renders
above the Ask button despite Ask being created first.
"""
import streamlit as st


def _input() -> str:
    return st.text_input(
        label="query",
        value=st.session_state.prefill,
        placeholder="Ask anything about movies — titles, directors, analytics, recommendations…",
        label_visibility="collapsed",
        key=f"query_box_v{st.session_state.widget_version}",
    )


def render_search_bar() -> None:
    """Render the search form and queue a search on Ask / Enter."""
    searching = st.session_state.searching

    with st.form(
        key=f"search_form_v{st.session_state.widget_version}",
        clear_on_submit=False,
        border=False,
    ):
        # Reserve the top row for the input. The Ask button is created first
        # (so Enter targets it) but rendered in the column below.
        input_row = st.container()

        ask_col, _ = st.columns([1.4, 6])
        with ask_col:
            asked = st.form_submit_button("Ask →", type="primary", disabled=searching)

        cleared = False
        with input_row:
            if st.session_state.prefill:
                col_input, col_clear = st.columns([14, 1], vertical_alignment="center")
                with col_input:
                    query = _input()
                with col_clear:
                    cleared = st.form_submit_button(
                        "✕", key="clear_input", help="Clear search"
                    )
            else:
                query = _input()

            # Loader sits right under the input (above Ask) while a search runs.
            if searching:
                st.markdown(
                    '<div class="search-loader">'
                    '<span class="search-spinner"></span>'
                    'Searching the cinematic universe…'
                    '</div>',
                    unsafe_allow_html=True,
                )

    if cleared:
        st.session_state.prefill = ""
        st.session_state.widget_version += 1
        st.rerun()

    if asked and not searching:
        text = query.strip()
        if text:
            st.session_state.pending_query = text
            st.session_state.prefill = text
            st.session_state.search_error = ""
            st.session_state.searching = True
            st.rerun()

    # Surface the last error (if any) right under the search box.
    if st.session_state.search_error and not searching:
        st.markdown(
            f'<div class="search-error">⚠️ {st.session_state.search_error}</div>',
            unsafe_allow_html=True,
        )
