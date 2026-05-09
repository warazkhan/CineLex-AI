from cinellex_rag.core.analytics import handle_analytics
from cinellex_rag.retrieval.rag import handle_rag

# -----------------------------
# PURE TOOL FUNCTIONS
# -----------------------------
def rag_tool(query: str):
    return handle_rag(query)


def analytics_tool(query: str):
    return handle_analytics(query)


# -----------------------------
# TOOL REGISTRY
# -----------------------------
TOOLS = {
    "rag": rag_tool,
    "analytics": analytics_tool
}