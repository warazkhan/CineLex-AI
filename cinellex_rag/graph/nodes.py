from cinellex_rag.retrieval.rag import handle_rag
from cinellex_rag.core.analytics import handle_analytics
from cinellex_rag.core.formatter import normalize
from cinellex_rag.core.schema import build_response
from cinellex_rag.observability.mlflow_logger import log_run


# -----------------------------
# ROUTER NODE (ONLY DECISION)
# -----------------------------
def route_node(state):
    query = state["query"].lower()

    analytics_keywords = [
        "top", "best", "worst", "list", "highest", "lowest"
    ]

    rag_keywords = [
        "tell me", "about", "plot", "story", "who", "details"
    ]

    if any(word in query for word in rag_keywords):
        state["route"] = "rag"
    elif any(word in query for word in analytics_keywords):
        state["route"] = "analytics"
    else:
        state["route"] = "rag"

    return state


# -----------------------------
# RAG NODE (NO LOGIC INSIDE)
# -----------------------------
def rag_node(state):
    result = handle_rag(state["query"])
    state["result"] = result
    return state


# -----------------------------
# ANALYTICS NODE (NO LOGIC INSIDE)
# -----------------------------
def analytics_node(state):
    result = handle_analytics(state["query"])
    state["result"] = result
    return state


# -----------------------------
# FORMAT NODE (ONLY PLACE THAT NORMALIZES)
# -----------------------------
def format_node(state):

    # 1. normalize everything into standard format
    result = normalize(state["result"])

    # 2. build final response contract
    response = build_response(
        answer=result["answer"],
        route=state["route"],
        metadata=result["metadata"]
    )

    # 3. observability ONLY here
    log_run(
        query=state["query"],
        route=state["route"],
        response=response
    )

    # 4. final output
    state["result"] = response
    return state