def build_response(answer: str, route: str, metadata: dict = None):
    return {
        "answer": answer,
        "route": route,
        "metadata": metadata or {}
    }