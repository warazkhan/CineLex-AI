import sys
from pathlib import Path
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.data_config import IMDB_CSV_PATH, VECTOR_STORE_PATH
from utils.llm_utils import generate

# ------------------------------
# Load dataset (Pandas)
# ------------------------------
print("Loading IMDB dataset...")
df = pd.read_csv(IMDB_CSV_PATH)

# Convert numeric columns
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
df["Gross"] = pd.to_numeric(df["Gross"].str.replace(",", "").str.replace("$", ""), errors="coerce")
df["No_of_Votes"] = pd.to_numeric(df["No_of_Votes"], errors="coerce")

# Fill only string/object columns safely
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].fillna("")

# ------------------------------
# Load FAISS vector store (RAG)
# ------------------------------
print("Loading vector store...")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.load_local(
    str(VECTOR_STORE_PATH),
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)
retriever = vector_store.as_retriever()

print("🎬 CineLex AI ready! Type 'exit' to quit.\n")

# ------------------------------
# Helper functions
# ------------------------------
def clean_doc_text(text: str) -> str:
    """Remove duplicate lines."""
    lines = text.split(", ")
    seen = set()
    clean_lines = []
    for line in lines:
        if line not in seen:
            clean_lines.append(line)
            seen.add(line)
    return ", ".join(clean_lines)

# ------------------------------
# Analytics functions
# ------------------------------
def pandas_analytics(query: str, k: int = 5):
    q_lower = query.lower()
    if "top" in q_lower and "movie" in q_lower:
        n = int([s for s in q_lower.split() if s.isdigit()][0]) if any(s.isdigit() for s in q_lower.split()) else k
        top_movies = df.sort_values("IMDB_Rating", ascending=False).head(n)
        return "\n".join([f"{row['Series_Title']} ({int(row['Released_Year'])}) – Rating: {row['IMDB_Rating']}" for _, row in top_movies.iterrows()])

    if "top" in q_lower and "director" in q_lower:
        n = int([s for s in q_lower.split() if s.isdigit()][0]) if any(s.isdigit() for s in q_lower.split()) else k
        top_directors = df["Director"].value_counts().head(n)
        return "\n".join(top_directors.index.tolist())

    if "latest" in q_lower or "recent" in q_lower:
        n = int([s for s in q_lower.split() if s.isdigit()][0]) if any(s.isdigit() for s in q_lower.split()) else k
        latest_movies = df.sort_values("Released_Year", ascending=False).head(n)
        return "\n".join([f"{row['Series_Title']} ({int(row['Released_Year'])}) – Rating: {row['IMDB_Rating']}" for _, row in latest_movies.iterrows()])

    if "highest" in q_lower and "gross" in q_lower:
        n = int([s for s in q_lower.split() if s.isdigit()][0]) if any(s.isdigit() for s in q_lower.split()) else k
        top_gross = df.sort_values("Gross", ascending=False).head(n)
        return "\n".join([f"{row['Series_Title']} – Gross: ${int(row['Gross'])}" for _, row in top_gross.iterrows()])

    if "highest" in q_lower and "votes" in q_lower:
        n = int([s for s in q_lower.split() if s.isdigit()][0]) if any(s.isdigit() for s in q_lower.split()) else k
        top_votes = df.sort_values("No_of_Votes", ascending=False).head(n)
        return "\n".join([f"{row['Series_Title']} – Votes: {int(row['No_of_Votes'])}" for _, row in top_votes.iterrows()])

    return None

# ------------------------------
# RAG functions
# ------------------------------
def rag_answer(query: str, k: int = 5):
    docs = retriever.get_relevant_documents(query)[:k]
    context_list = []
    seen_titles = set()
    for doc in docs:
        title = doc.metadata.get("title", None)
        if title and title not in seen_titles:
            cleaned_text = clean_doc_text(doc.page_content)
            context_list.append(cleaned_text)
            seen_titles.add(title)
    if not context_list:
        return "Not enough information."

    context = "\n".join(context_list)

    prompt = f"""
Answer the question using ONLY the facts below.
If the movie in the query is not listed, reply "Not enough information".
List each movie exactly once.
Write a single concise sentence per movie.
Do not repeat movies or invent information.

Facts:
{context}

Question: {query}
"""
    return generate(prompt, max_new_tokens=200)

# ------------------------------
# Movie Recommender
# ------------------------------
class MovieRecommender:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    def recommend_similar(self, movie_title: str, k: int = 5, more_modern: bool = False):
        movie_title_lower = movie_title.lower()
        if movie_title_lower not in self.df["Series_Title"].str.lower().values:
            return "Movie not found in dataset."

        target_row = self.df[self.df["Series_Title"].str.lower() == movie_title_lower].iloc[0]
        target_genres = set(target_row["Genre"].split(", "))
        target_year = target_row["Released_Year"]

        df_filtered = self.df.copy()

        if more_modern:
            df_filtered = df_filtered[df_filtered["Released_Year"] > target_year]

        df_filtered["Genre_Overlap"] = df_filtered["Genre"].apply(lambda x: len(target_genres.intersection(set(x.split(", ")))))

        df_sorted = df_filtered.sort_values(["Genre_Overlap", "IMDB_Rating"], ascending=[False, False])
        df_sorted = df_sorted[df_sorted["Series_Title"].str.lower() != movie_title_lower].head(k)

        if df_sorted.empty:
            return "No similar movies found with the specified criteria."

        return "\n".join([f"{row['Series_Title']} ({int(row['Released_Year'])}) – Rating: {row['IMDB_Rating']}" for _, row in df_sorted.iterrows()])


# ------------------------------
# Initialize recommender
# ------------------------------
recommender = MovieRecommender(df)

# ------------------------------
# Main loop
# ------------------------------
import re

while True:
    query = input("Enter your question: ").strip()
    if query.lower() in {"exit", "quit"}:
        break

    # 1️⃣ Analytics queries
    answer = pandas_analytics(query)
    if answer:
        print(f"\nAnswer:\n{answer}\n")
        continue

    # 2️⃣ Recommendation queries
    if "like" in query.lower() or "recommend" in query.lower():
        more_modern_flag = "more modern" in query.lower()
        match = re.search(r"like\s+(.+?)(?:\s+but|\s*$)", query, re.I)
        movie_title = match.group(1).strip() if match else None
        if movie_title:
            answer = recommender.recommend_similar(movie_title, more_modern=more_modern_flag)
        else:
            answer = "Please specify a movie to find similar recommendations."
        print(f"\nAnswer:\n{answer}\n")
        continue

    # 3️⃣ RAG queries
    answer = rag_answer(query)
    print(f"\nAnswer:\n{answer}\n")
