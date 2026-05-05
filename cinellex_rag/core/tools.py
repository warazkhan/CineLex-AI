from langchain.tools import Tool
from cinellex_rag.core.analytics import handle_analytics
from cinellex_rag.retrieval.rag import handle_rag


# -------------------
# RAG Tool
# -------------------
def rag_tool_func(query: str):
    return handle_rag(query)


rag_tool = Tool(
    name="MovieRAG",
    func=rag_tool_func,
    description="Use for movie summaries, story, overview, cast, plot details"
)


# -------------------
# Analytics Tool
# -------------------
def analytics_tool_func(query: str):
    return handle_analytics(query)


analytics_tool = Tool(
    name="MovieAnalytics",
    func=analytics_tool_func,
    description="Use for top movies, worst movies, ratings, directors, rankings"
)


# export tools list
TOOLS = [rag_tool, analytics_tool]