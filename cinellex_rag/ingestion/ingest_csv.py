import sys
from pathlib import Path
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.data_config import IMDB_CSV_PATH, CHROMA_STORE_PATH

# ------------------------------
# Load dataset
# ------------------------------
print("Loading IMDB dataset...")
df = pd.read_csv(IMDB_CSV_PATH)
df = df.head(1000)

df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
df["Gross"] = pd.to_numeric(
    df["Gross"].astype(str).str.replace(",", "").str.replace("$", ""),
    errors="coerce"
)
df["No_of_Votes"] = pd.to_numeric(df["No_of_Votes"], errors="coerce")

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].fillna("")

# ------------------------------
# Create documents
# ------------------------------
print("Creating documents...")

docs = []
for _, row in df.iterrows():
    content = (
        f"{row['Series_Title']}: {row.get('Overview', 'No overview available')}\n"
        f"Genre: {row.get('Genre', 'N/A')}\n"
        f"Year: {row.get('Released_Year', 'N/A')}\n"
        f"Rating: {row.get('IMDB_Rating', 'N/A')}\n"
        f"Director: {row.get('Director', 'N/A')}\n"
        f"Stars: {row.get('Star1', '')}, {row.get('Star2', '')}, {row.get('Star3', '')}, {row.get('Star4', '')}\n"
        f"Votes: {row.get('No_of_Votes', 'N/A')}\n"
        f"Gross: {row.get('Gross', 'N/A')}"
    )

    metadata = {
        "title": row["Series_Title"],
        "genre": row.get("Genre", ""),
        "year": str(row.get("Released_Year", "")),
        "rating": str(row.get("IMDB_Rating", "")),
        "director": row.get("Director", ""),
        "stars": f"{row.get('Star1', '')}, {row.get('Star2', '')}, {row.get('Star3', '')}, {row.get('Star4', '')}",
    }

    docs.append(Document(page_content=content, metadata=metadata))

# ------------------------------
# Build Chroma vector store
# ------------------------------
print("Creating embeddings and Chroma vector store...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

CHROMA_STORE_PATH.mkdir(parents=True, exist_ok=True)

vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    collection_name="cinellex",
    persist_directory=str(CHROMA_STORE_PATH)
)

print(f"Chroma vector store saved at: {CHROMA_STORE_PATH}")