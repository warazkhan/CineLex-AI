import pandas as pd
from difflib import get_close_matches
from cinellex_rag.retrieval.vector_store import retriever
from cinellex_rag.utils.llm_utils import generate
from cinellex_rag.core.data_loader import load_imdb


df = load_imdb()


def handle_rag(query: str, k: int = 3):

    query_clean = query.lower().replace("tell me about", "").strip()

    titles = df["Series_Title"].str.lower().tolist()
    match = get_close_matches(query_clean, titles, n=1, cutoff=0.5)

    # ---------------- fuzzy match
    if match:
        row = df[df["Series_Title"].str.lower() == match[0]].iloc[0]

        return {
            "answer": (
                f"Title: {row['Series_Title']}\n"
                f"Year: {row['Released_Year']}\n"
                f"Rating: {row['IMDB_Rating']}\n"
                f"Overview: {row.get('Overview', '')}"
            ),
            "source": "fuzzy",
            "metadata": {"title": row["Series_Title"]}
        }

    # ---------------- retrieval
    docs = retriever.invoke(query)[:k]
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are a precise movie assistant.

Context:
{context}

Question:
{query}

Answer clearly and accurately.
"""

    return {
        "answer": generate(prompt),
        "source": "retrieval",
        "metadata": {"docs_used": len(docs)}
    }