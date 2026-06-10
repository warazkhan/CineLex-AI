"""HTTP client for the CineLex FastAPI backend.

This is the *only* module that knows how to talk to the API. Components and
handlers call these functions and never touch ``requests`` directly.
"""
import time
from typing import Optional, Tuple

import requests
import streamlit as st

from ui.config import API_URL, HEALTH_TIMEOUT, REQUEST_TIMEOUT


def call_api(query: str) -> Tuple[Optional[dict], Optional[str]]:
    """Send a query to ``POST /query``.

    Returns ``(data, None)`` on success or ``(None, error_message)`` on
    failure, so callers can render a friendly message instead of crashing.
    On success the round-trip latency is attached as ``data["_elapsed_ms"]``.
    """
    start = time.perf_counter()
    try:
        resp = requests.post(
            f"{API_URL}/query",
            json={"query": query},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.ConnectionError:
        return None, (
            f"Could not reach the backend at {API_URL}. "
            "Is the API running? (uvicorn cinellex_rag.api.app:app)"
        )
    except requests.exceptions.Timeout:
        return None, "The request timed out. Please try again."
    except requests.exceptions.RequestException as exc:
        return None, f"Request failed: {exc}"

    if resp.status_code == 200:
        data = resp.json()
        data["_elapsed_ms"] = int((time.perf_counter() - start) * 1000)
        return data, None

    # Surface the FastAPI `detail` field when present (e.g. validation errors).
    try:
        detail = resp.json().get("detail", resp.text)
    except ValueError:
        detail = resp.text
    return None, f"API error {resp.status_code}: {detail}"


@st.cache_data(ttl=15, show_spinner=False)
def is_backend_healthy() -> bool:
    """Return True if ``GET /health`` responds OK.

    Cached for a few seconds so the indicator does not add latency to every
    rerun, while still reflecting the backend going up/down reasonably fast.
    """
    try:
        resp = requests.get(f"{API_URL}/health", timeout=HEALTH_TIMEOUT)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False
