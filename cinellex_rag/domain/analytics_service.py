from cinellex_rag.core.analytics import handle_analytics


class AnalyticsService:

    def answer(self, query: str):
        return handle_analytics(query)