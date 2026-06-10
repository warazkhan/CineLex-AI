from cinellex_rag.core.router import classify
from cinellex_rag.core.analytics import handle_analytics
from cinellex_rag.retrieval.rag import handle_rag
from cinellex_rag.core.schema import build_response
from cinellex_rag.observability.mlflow_logger import logger


def route_node(state):
    """Classify the query and record the chosen route."""
    logger.start_run(state["query"])

    state["route"] = classify(state["query"])

    logger.log_route(state["route"])
    return state


def select_route(state):
    """Conditional-edge selector: maps the route to the next node name."""
    return state["route"]


def analytics_node(state):
    """Deterministic ranking analytics over TMDB /discover — no LLM, no CrewAI.

    handle_analytics returns the full result dict (answer + structured movie
    cards + source + metadata), passed through unchanged like rag_node."""
    state["result"] = handle_analytics(state["query"])

    logger.log_node("analytics", {"query": state["query"]})
    return state


def rag_node(state):
    """TMDB keyword retrieval / fuzzy single-title lookup — returns handle_rag's
    dict unchanged so the real source (fuzzy/retrieval) and metadata survive."""
    state["result"] = handle_rag(state["query"])

    logger.log_node("rag", {"query": state["query"]})
    return state


def recommend_node(state):
    """Similar-movie recommendations via the CrewAI RecommendationCrew.

    Imported lazily so the graph module stays importable even while the crew
    is being built, and so the heavy CrewAI import only happens on this path.
    The narrative comes from the crew; the structured cards come from the
    deterministic recommender so the UI always has posters to render.
    """
    from cinellex_rag.crew.crew import RecommendationCrew, extract_seed_title
    from cinellex_rag.core.movie_recommender import recommend_movies
    from cinellex_rag.core.movies import card_from_title
    from config.schema_config import COL_TITLE

    query = state["query"]
    answer = RecommendationCrew().run(query)

    seed = extract_seed_title(query)
    recs = recommend_movies(seed, top_n=6)
    movies = []
    if isinstance(recs, list):
        for rec in recs:
            card = card_from_title(rec.get(COL_TITLE))
            if card:
                movies.append(card)

    state["result"] = {
        "answer": answer if isinstance(answer, str) else str(answer),
        "source": "recommendation-crew",
        "movies": movies,
        "metadata": {"seed": seed},
    }

    logger.log_node("recommend", {"query": state["query"]})
    return state


def format_node(state):
    result = state["result"]

    if isinstance(result, dict):
        answer = result.get("answer", "")
        source = result.get("source", "unknown")
        metadata = result.get("metadata", {})
        movies = result.get("movies", [])
    else:
        answer = str(result)
        source = state.get("route", "unknown")
        metadata = {}
        movies = []

    response = build_response(
        answer=answer,
        route=state.get("route", "unknown"),
        metadata={**metadata, "source": source},
        movies=movies,
    )

    logger.log_response(response)
    logger.end_run()

    state["result"] = response
    return state
