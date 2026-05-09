from langchain.tools import Tool
from cinellex_rag.domain.analytics_service import AnalyticsService

analytics_service = AnalyticsService()


def analytics_tool_func(query: str):
    return analytics_service.answer(query)


analytics_tool = Tool(
    name="movie_analytics_tool",
    func=analytics_tool_func,
    description="Use for rankings, top movies, worst movies, directors, stats"
)