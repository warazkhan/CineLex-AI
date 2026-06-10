"""
Single source of truth for query routing.

Replaces the keyword lists that had drifted out of sync across
graph/nodes.py, tools/registry.py and crew/crew.py.

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
    "director",
]


def classify(query: str) -> str:
    """Return the route name for a query: 'recommend', 'analytics' or 'rag'."""
    q = query.lower()

    if any(kw in q for kw in RECOMMEND_KEYWORDS):
        return "recommend"

    if any(kw in q for kw in ANALYTICS_KEYWORDS):
        return "analytics"

    return "rag"
