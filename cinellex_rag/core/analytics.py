import re
import sqlite3
from config.data_config import SQLITE_DB_PATH


def get_conn():
    return sqlite3.connect(str(SQLITE_DB_PATH))


def extract_n(query: str, default: int = 5) -> int:
    """Extract number from query like 'top 10 movies'"""
    match = re.search(r'\b(\d+)\b', query)
    return int(match.group(1)) if match else default


def handle_analytics(query: str, top_n: int = None):
    q = query.lower()
    top_n = top_n or extract_n(q)
    conn = get_conn()

    try:
        if ("top" in q and "movie" in q) or ("best" in q and "movie" in q):
            cursor = conn.execute(f"""
                SELECT Series_Title, Released_Year, IMDB_Rating
                FROM movies
                ORDER BY IMDB_Rating DESC
                LIMIT {top_n}
            """)
            rows = cursor.fetchall()
            return "\n".join(
                f"{r[0]} ({int(r[1])}) — Rating: {r[2]}"
                for r in rows
            )

        if "worst" in q and "movie" in q:
            cursor = conn.execute(f"""
                SELECT Series_Title, Released_Year, IMDB_Rating
                FROM movies
                ORDER BY IMDB_Rating ASC
                LIMIT {top_n}
            """)
            rows = cursor.fetchall()
            return "\n".join(
                f"{r[0]} ({int(r[1])}) — Rating: {r[2]}"
                for r in rows
            )

        if "top" in q and "director" in q:
            cursor = conn.execute(f"""
                SELECT Director, COUNT(*) as movie_count
                FROM movies
                GROUP BY Director
                ORDER BY movie_count DESC
                LIMIT {top_n}
            """)
            rows = cursor.fetchall()
            return "\n".join(
                f"{r[0]} ({r[1]} movies)"
                for r in rows
            )

        if "latest" in q or "recent" in q:
            cursor = conn.execute(f"""
                SELECT Series_Title, Released_Year
                FROM movies
                ORDER BY Released_Year DESC
                LIMIT {top_n}
            """)
            rows = cursor.fetchall()
            return "\n".join(
                f"{r[0]} ({int(r[1])})"
                for r in rows
            )

        if ("highest" in q and "gross" in q) or ("highest" in q and "earn" in q):
            cursor = conn.execute(f"""
                SELECT Series_Title, Released_Year, Gross
                FROM movies
                WHERE Gross IS NOT NULL AND Gross != ''
                ORDER BY CAST(Gross AS REAL) DESC
                LIMIT {top_n}
            """)
            rows = cursor.fetchall()
            return "\n".join(
                f"{r[0]} ({int(r[1])}) — Gross: ${r[2]:,.0f}"
                for r in rows
            )

        return "No analytics pattern matched."

    finally:
        conn.close()