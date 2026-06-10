"""Static configuration for the CineLex AI UI.

Everything that is a tunable constant (rather than logic) lives here so the
rest of the UI never hard-codes magic values.
"""
import os

# --- Backend ----------------------------------------------------------------
# API_URL is injected by docker-compose / k8s (e.g. http://api:8000). Falls
# back to a local uvicorn instance for `streamlit run` during development.
API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")

# Long timeout: the RAG / recommend paths can take a while on the free tier.
REQUEST_TIMEOUT = 120          # seconds, for /query
HEALTH_TIMEOUT = 5             # seconds, for /health

# --- Page -------------------------------------------------------------------
# Centered single-column "answer engine" feel; the sidebar holds only a short
# About panel, so it starts collapsed.
PAGE_CONFIG = {
    "page_title": "CineLex — Ask anything about movies",
    "page_icon": "🎬",
    "layout": "centered",
    "initial_sidebar_state": "collapsed",
}

# Poster thumbnails come from the dataset at ~67px wide; this is the width we
# request from the Amazon media CDN when rendering cards.
POSTER_WIDTH = 400

# --- Content ----------------------------------------------------------------
# Example queries shown as clickable chips until the first search is made.
SUGGESTIONS = [
    "Top 10 movies by rating",
    "Tell me about Inception",
    "Top 10 directors",
    "Worst rated movies",
    "Latest releases",
    "Highest grossing movies",
]

# How many previous queries to show under the latest answer.
MAX_HISTORY_ITEMS = 7

# --- Session state ----------------------------------------------------------
# key -> default value. Used by ui.state.init_session_state().
SESSION_DEFAULTS = {
    "history": [],          # list[dict]: {query, answer, route, source}
    "prefill": "",          # text currently bound to the search box
    "trigger_search": False,  # set True to run a search on the next rerun
    "pending_query": "",    # the query waiting to be executed
    "widget_version": 0,    # bumped to force-reset the text_input widget
}
