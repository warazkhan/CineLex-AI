"""CineLex AI — Streamlit application entry point.

``main()`` wires the page together; every section is delegated to a focused
component. Run via the root launcher: ``streamlit run streamlit_app.py``.
"""
import streamlit as st

from ui.components.hero import render_hero
from ui.components.notices import render_config_notice
from ui.components.results import render_results
from ui.components.search import render_action_buttons, render_search_bar
from ui.components.sidebar import render_sidebar
from ui.components.suggestions import render_suggestions
from ui.config import PAGE_CONFIG
from ui.search_handler import process_pending_search
from ui.state import init_session_state
from ui.styles import inject_styles


def main() -> None:
    # set_page_config must be the first Streamlit call.
    st.set_page_config(**PAGE_CONFIG)
    init_session_state()
    inject_styles()

    render_sidebar()
    render_hero()
    render_config_notice()

    query = render_search_bar()
    render_action_buttons(query)
    render_suggestions()

    # Execute any queued search before painting results so the answer shows
    # in the same rerun.
    process_pending_search()
    render_results()


if __name__ == "__main__":
    main()
