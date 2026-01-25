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

print("Loading IMDB dataset...")
df = pd.read_csv(IMDB_CSV_PATH)

# Optional: limit for local CPU testing
df = df.head(1000)

print("Creating FAISS documents with all relevant columns...")

docs = []
for _, row in df.iterrows():
    # Combine all movie info into one text string
    content = (
        f"Title: {row['Series_Title']}\n"
        f"Year: {row['Released_Year']}\n"
        f"Certificate: {row.get('Certificate', 'N/A')}\n"
        f"Runtime: {row.get('Runtime', 'N/A')}\n"
        f"Genre: {row.get('Genre', 'N/A')}\n"
        f"IMDB Rating: {row.get('IMDB_Rating', 'N/A')}\n"
        f"Meta Score: {row.get('Meta_score', 'N/A')}\n"
        f"Director: {row.get('Director', 'N/A')}\n"
        f"Stars: {row.get('Star1', 'N/A')}, {row.get('Star2', 'N/A')}, {row.get('Star3', 'N/A')}, {row.get('Star4', 'N/A')}\n"
        f"Number of Votes: {row.get('No_of_Votes', 'N/A')}\n"
        f"Gross: {row.get('Gross', 'N/A')}\n"
        f"Overview: {row.get('Overview', 'N/A')}"
    )
    
    doc = Document(
        page_content=content,
        metadata={"title": row['Series_Title']}
    )
    docs.append(doc)

print("Creating embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)

# Ensure retrieval folder exists
VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
vectorstore.save_local(str(VECTOR_STORE_PATH))

print(f"✅ Vector store saved at: {VECTOR_STORE_PATH}")
