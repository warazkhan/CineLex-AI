from langchain.tools import Tool
from cinellex_rag.domain.rag_service import RAGService

rag_service = RAGService()


def rag_tool_func(query: str):
    return rag_service.answer(query)


rag_tool = Tool(
    name="movie_rag_tool",
    func=rag_tool_func,
    description="Use for movie plot, story, overview, cast, details"
)