from pathlib import Path

# Project root = AI-Learning/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

IMDB_DIR = DATA_DIR / "imdb"
IMDB_CSV_PATH = IMDB_DIR / "imdb_top_1000.csv"

# Where the FAISS vector store will be saved
VECTOR_STORE_PATH = PROJECT_ROOT / "rag-imdb-knowledge-agent" / "retrieval" / "vector_store.faiss"