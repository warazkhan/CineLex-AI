# rag-imdb-knowledge-agent/ingestion/ingest_csv.py
import sys
from pathlib import Path
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# ------------------------------
# Project paths
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.data_config import IMDB_CSV_PATH, VECTOR_STORE_PATH

# ------------------------------
# Load dataset
# ------------------------------
print("Loading IMDB dataset...")
df = pd.read_csv(IMDB_CSV_PATH)

# Optional: limit for local CPU testing
df = df.head(1000)

# Convert numeric columns safely
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
df["Gross"] = pd.to_numeric(df["Gross"].str.replace(",", "").str.replace("$", ""), errors="coerce")
df["No_of_Votes"] = pd.to_numeric(df["No_of_Votes"], errors="coerce")

# Fill missing string columns
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].fillna("")

# ------------------------------
# Create FAISS documents
# ------------------------------
print("Creating FAISS documents with all relevant metadata...")

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
        "title": row['Series_Title'],
        "overview": row.get('Overview', ''),
        "genre": row.get('Genre', ''),
        "year": row.get('Released_Year', ''),
        "rating": row.get('IMDB_Rating', ''),
        "director": row.get('Director', ''),
        "stars": f"{row.get('Star1', '')}, {row.get('Star2', '')}, {row.get('Star3', '')}, {row.get('Star4', '')}",
        "votes": row.get('No_of_Votes', ''),
        "gross": row.get('Gross', '')
    }

    doc = Document(page_content=content, metadata=metadata)
    docs.append(doc)

# ------------------------------
# Build embeddings and FAISS index
# ------------------------------
print("Creating embeddings and FAISS vector store...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)

# Ensure retrieval folder exists
VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
vectorstore.save_local(str(VECTOR_STORE_PATH))

print(f"✅ Vector store successfully saved at: {VECTOR_STORE_PATH}")
