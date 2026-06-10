"""Descriptive / knowledge queries, served live from TMDB.

Replaces the old Chroma vector-store retrieval. There is no local corpus and no
embeddings: a single-title "tell me about X" resolves to one movie, while a
broader question keyword-searches TMDB and lets the LLM answer over the top
results. The LLM path (Groq via :func:`generate`) is unchanged.
"""
from difflib import SequenceMatcher

from cinellex_rag.core import tmdb
from cinellex_rag.core.movies import card_from_details, cards_for_ids
from cinellex_rag.utils.llm_utils import generate
from config.tmdb_config import TMDB_ENABLED

_LEAD_INS = ("tell me about", "what is", "who directed", "describe", "info on", "about")


def _strip_lead_in(query: str) -> str:
    q = query.strip()
    low = q.lower()
    for phrase in _LEAD_INS:
        if low.startswith(phrase):
            return q[len(phrase):].strip(" ?:").strip()
    return q


def handle_rag(query: str, k: int = 3, use_fuzzy: bool = True):
    if not TMDB_ENABLED:
        return {
            "answer": "Live movie data is unavailable — TMDB is not configured.",
            "source": "rag",
            "movies": [],
            "metadata": {},
        }

    cleaned = _strip_lead_in(query)

    # ---------------- single-movie short-circuit ("tell me about X") ----------
    # Disabled by the evaluation harness (use_fuzzy=False) so it exercises the
    # multi-result path rather than a direct lookup.
    if use_fuzzy:
        hit = tmdb.search_movie(cleaned)
        if hit:
            title = hit.get("title") or hit.get("original_title") or ""
            ratio = SequenceMatcher(None, cleaned.lower(), title.lower()).ratio()
            looks_like_title = ratio >= 0.6 or cleaned.lower() != query.strip().lower()
            if looks_like_title:
                details = tmdb.movie_details(hit.get("id"))
                if details:
                    card = card_from_details(details)
                    answer = (
                        f"Title: {card['title']}\n"
                        f"Year: {card['year']}\n"
                        f"Rating: {card['rating']}\n"
                        f"Overview: {card['overview'] or ''}"
                    )
                    return {
                        "answer": answer,
                        "source": "fuzzy",
                        "movies": [card],
                        "metadata": {"title": card["title"], "tmdb_id": card["tmdb_id"]},
                    }

    # ---------------- keyword retrieval + LLM --------------------------------
    results = tmdb.search_movies(query, limit=k)
    cards = cards_for_ids([r["id"] for r in results])

    contexts = [
        f"{c['title']} ({c['year']}) — {c.get('genre') or 'N/A'}\n"
        f"Director: {c.get('director') or 'N/A'}\n"
        f"{c.get('overview') or 'No overview available.'}"
        for c in cards
    ]
    context = "\n\n".join(contexts)

    prompt = f"""
You are a precise movie assistant.

Context:
{context}

Question:
{query}

Answer clearly and accurately. If the context does not contain the answer, say so.
"""

    return {
        "answer": generate(prompt),
        "source": "retrieval",
        "movies": cards,
        "metadata": {"docs_used": len(cards), "contexts": contexts},
    }
