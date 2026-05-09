from cinellex_rag.retrieval.rag import handle_rag
from cinellex_rag.core.analytics import handle_analytics


class ToolRegistry:

    @staticmethod
    def route(query: str) -> str:
        q = query.lower()

        if any(x in q for x in ["top", "best", "worst", "list", "highest", "lowest"]):
            return "analytics"

        return "rag"

    @staticmethod
    def execute(tool_name: str, query: str):
        if tool_name == "rag":
            return handle_rag(query)

        if tool_name == "analytics":
            return handle_analytics(query)

        return {"answer": "Unknown tool", "source": "system"}