import re

ANALYTIC_KEYWORDS = [
    "top", "highest", "lowest", "most", "least",
    "best", "worst", "latest", "oldest", "count",
    "how many", "rank"
]

def is_analytic_query(query: str) -> bool:
    query = query.lower()
    return any(keyword in query for keyword in ANALYTIC_KEYWORDS)