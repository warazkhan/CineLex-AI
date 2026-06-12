"""
Single source of truth for query routing.

One keyword table, imported by the graph nodes and the recommendation crew, so
the routing rules can never drift apart again.

Precedence: recommend > analytics > rag (default).
A query like "recommend top films like Inception" contains the analytics
keyword "top", but the user clearly wants recommendations, so recommend wins.
"""

# Phrases that signal the user wants similar-movie recommendations.
RECOMMEND_KEYWORDS = [
    "recommend",
    "recommendation",
    "suggest",
    "suggestion",
    "similar",
    "movies like",
    "films like",
    "something like",
]

# Keywords that signal a deterministic analytics / ranking query.
ANALYTICS_KEYWORDS = [
    "top",
    "best",
    "worst",
    "list",
    "highest",
    "lowest",
    "latest",
    "recent",
    "release",
]


def classify(query: str) -> str:
    """Return the route name for a query: 'recommend', 'analytics' or 'rag'."""
    q = query.lower()

    if any(kw in q for kw in RECOMMEND_KEYWORDS):
        return "recommend"

    if any(kw in q for kw in ANALYTICS_KEYWORDS):
        return "analytics"

    return "rag"
