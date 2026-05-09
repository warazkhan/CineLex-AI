from cinellex_rag.retrieval.rag import handle_rag


class RAGService:

    def answer(self, query: str):
        return handle_rag(query)