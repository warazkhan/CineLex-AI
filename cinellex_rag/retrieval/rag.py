"""Descriptive / knowledge queries, served live from TMDB.

Replaces the old Chroma vector-store retrieval. There is no local corpus and no
embeddings. A single-title "tell me about X" resolves to one movie; a broader
question is retrieved by *concept* rather than by title text.

TMDB's ``/search/movie`` matches the title only, so a thematic question
("a thief who steals corporate secrets through dream-sharing") finds nothing.
We instead ask the LLM to distil the question into TMDB *facets* — an optional
concrete title plus thematic keywords and genres — and retrieve over TMDB's own
curated keyword/genre taxonomy via ``/discover``. This is semantic-style
retrieval without embeddings, and it degrades cleanly: if the LLM is
unavailable or finds no facets, we fall back to the legacy title search, so no
query regresses. The LLM answer path (Groq via :func:`generate`) is unchanged.
"""
import json
from difflib import SequenceMatcher

from cinellex_rag.core import tmdb
from cinellex_rag.core.movies import card_from_details, cards_for_ids
from cinellex_rag.utils.llm_utils import generate
from config.tmdb_config import TMDB_ENABLED

_LEAD_INS = ("tell me about", "what is", "who directed", "describe", "info on", "about")

_FACET_PROMPT = """You convert a movie question into TMDB search facets.

Return ONLY a JSON object (no prose, no markdown) with exactly these keys:
  "title":    the specific movie title if the question names or unmistakably
              describes one well-known film, otherwise null
  "keywords": up to 4 short thematic plot/concept phrases, lowercase
              (e.g. ["dream","heist","corporate espionage"])
  "genres":   up to 2 genre names, chosen only from: {genres}

Question: {query}
JSON:"""


def _strip_lead_in(query: str) -> str:
    q = query.strip()
    low = q.lower()
    for phrase in _LEAD_INS:
        if low.startswith(phrase):
            return q[len(phrase):].strip(" ?:").strip()
    return q


def _json_slice(text: str) -> str:
    """Extract the first ``{...}`` object from a possibly chatty LLM reply."""
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1] if start != -1 and end > start else text


def _extract_facets(query: str) -> dict:
    """Ask the LLM for ``{title, keywords, genres}``; degrade to ``{}`` on any
    failure (LLM error, non-JSON reply, unexpected shape)."""
    genres = ", ".join(tmdb.genre_map().values()) or "Action, Drama, Comedy"
    try:
        raw = generate(_FACET_PROMPT.format(genres=genres, query=query), max_tokens=200)
        data = json.loads(_json_slice(raw))
    except Exception:  # noqa: BLE001 — best-effort: any LLM/parse failure → no facets
        return {}
    if not isinstance(data, dict):
        return {}
    title = data.get("title")
    return {
        "title": title if isinstance(title, str) and title.strip() else None,
        "keywords": [k for k in (data.get("keywords") or []) if isinstance(k, str)][:4],
        "genres": [g for g in (data.get("genres") or []) if isinstance(g, str)][:2],
    }


def _facet_ids(facets: dict, k: int) -> list:
    """Resolve facets → candidate movie ids via TMDB keyword/genre discovery.

    Keywords are tried AND-joined first (precise), then OR-joined (recall) if the
    stricter query came back empty. Returns ``[]`` when no facet resolves.
    """
    keyword_ids = []
    for phrase in facets.get("keywords", []):
        hits = tmdb.search_keywords(phrase, limit=1)
        if hits and hits[0].get("id"):
            keyword_ids.append(str(hits[0]["id"]))

    gmap = {name.lower(): gid for gid, name in tmdb.genre_map().items()}
    genre_ids = [str(gmap[g.lower()]) for g in facets.get("genres", []) if g.lower() in gmap]

    if not keyword_ids and not genre_ids:
        return []

    genres_param = ",".join(genre_ids) or None
    for joiner in (",", "|"):  # AND (precise) → OR (recall)
        results = tmdb.discover(
            "popularity.desc",
            vote_count_gte=tmdb.VOTE_FLOOR,
            with_keywords=joiner.join(keyword_ids) or None,
            with_genres=genres_param,
        )
        ids = [r["id"] for r in results[:k] if r.get("id")]
        if ids or len(keyword_ids) <= 1:  # AND == OR for 0/1 keyword
            return ids
    return []


def handle_rag(query: str, k: int = 3, use_fuzzy: bool = True, use_facets: bool = True):
    """Answer a descriptive query from live TMDB.

    ``use_facets=False`` disables concept (keyword/genre) retrieval and reverts
    to the legacy title-only search — used by the evaluation harness to ablate
    the facet upgrade, and as a kill-switch for the extra LLM call.
    """
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

    # ---------------- facet (concept) retrieval + LLM ------------------------
    facets = _extract_facets(query) if use_facets else {}
    ids = _facet_ids(facets, k)

    # A concrete title the LLM spotted is the strongest signal — pin it first.
    title = facets.get("title")
    if title:
        hit = tmdb.search_movie(title)
        if hit and hit.get("id") and hit["id"] not in ids:
            ids = [hit["id"], *ids]

    # Fallback / top-up: the legacy title search preserves recall when facets
    # are thin or the LLM was unavailable (ids empty → behaves exactly as before).
    if len(ids) < k:
        for r in tmdb.search_movies(query, limit=k):
            if r.get("id") and r["id"] not in ids:
                ids.append(r["id"])

    cards = cards_for_ids(ids[:k])

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
        "metadata": {"docs_used": len(cards), "contexts": contexts, "facets": facets},
    }
