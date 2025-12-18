import sys
from pathlib import Path
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
from config.data_config import IMDB_CSV_PATH, VECTOR_STORE_PATH

df = pd.read_csv(IMDB_CSV_PATH)
df = df.head(100)  # optional: limit for local CPU

docs = [
    Document(
        page_content=f"{row['Series_Title']} ({row['Released_Year']}), Genre: {row['Genre']}, Rating: {row['IMDB_Rating']}, Director: {row['Director']}",
        metadata={"title": row['Series_Title']}
    )
    for _, row in df.iterrows()
]

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)

VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
vectorstore.save_local(str(VECTOR_STORE_PATH))
print("Vector store saved at:", VECTOR_STORE_PATH)
