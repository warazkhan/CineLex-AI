def classify_query(query: str) -> str:
    q = query.lower()

    analytics_keywords = [
        "top", "most", "highest", "lowest",
        "latest", "earliest", "best", "worst",
        "rating", "ratings", "votes", "gross",
        "box office", "released", "year"
    ]

    descriptive_keywords = [
        "tell me", "write about", "summary",
        "overview", "explain", "story", "plot"
    ]

    has_analytics = any(k in q for k in analytics_keywords)
    has_description = any(k in q for k in descriptive_keywords)

    if has_analytics and has_description:
        return "analytics_plus_llm"

    if has_analytics:
        return "analytics"

    return "rag"
