"""Top-of-page configuration notices.

These fire only when the deployment is misconfigured, so the same failure that
once showed up as a quiet text answer (no posters) is now impossible to miss.
"""
import streamlit as st

from ui.api_client import backend_status


def render_config_notice() -> None:
    """Warn loudly when the backend is up but has no TMDB key.

    Without ``TMDB_API_KEY`` the API still answers, but every route returns text
    with an empty movie list, so the UI has no posters to render. Surfacing it
    here turns a silent degradation into an obvious, fixable message.
    """
    status = backend_status()
    if not status["healthy"] or status["tmdb_enabled"]:
        return

    st.markdown(
        '<div style="background:#fff8ec;border:1px solid #f0d49a;'
        'border-left:3px solid #c98a1a;border-radius:10px;'
        'padding:0.9rem 1.1rem;margin-top:0.5rem;font-size:0.9rem;color:#8a5a10">'
        '⚠️ <strong>Live movie data is off.</strong> The server has no TMDB API '
        'key, so answers come back as plain text without posters. Set '
        '<code>TMDB_API_KEY</code> on the API service and redeploy it.'
        '</div>',
        unsafe_allow_html=True,
    )
