from difflib import get_close_matches
from cinellex_rag.retrieval.vector_store import vector_store
from cinellex_rag.utils.llm_utils import generate
from cinellex_rag.core.data_loader import load_imdb
from cinellex_rag.core.movies import build_card, card_from_title


df = load_imdb()


def handle_rag(query: str, k: int = 3, use_fuzzy: bool = True):

    query_clean = query.lower().replace("tell me about", "").strip()

    # ---------------- fuzzy match (exact-title short-circuit)
    # Disabled by the evaluation harness (use_fuzzy=False) so RAGAS exercises
    # the actual retriever rather than the direct lookup.
    if use_fuzzy:
        titles = df["Series_Title"].str.lower().tolist()
        match = get_close_matches(query_clean, titles, n=1, cutoff=0.5)

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
                "movies": [build_card(row)],
                "metadata": {"title": row["Series_Title"]}
            }

    # ---------------- retrieval
    docs = vector_store.similarity_search(query, k=k)
    contexts = [d.page_content for d in docs]
    context = "\n\n".join(contexts)

    # Map each retrieved doc back to a structured card via its title metadata.
    movies = []
    seen = set()
    for d in docs:
        title = (d.metadata or {}).get("title")
        if title and title not in seen:
            seen.add(title)
            card = card_from_title(title)
            if card:
                movies.append(card)

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
        "movies": movies,
        "metadata": {"docs_used": len(docs), "contexts": contexts}
    }