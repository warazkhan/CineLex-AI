def build_response(answer: str, route: str, metadata: dict = None, movies: list = None):
    return {
        "answer": answer,
        "route": route,
        "movies": movies or [],
        "metadata": metadata or {},
    }
