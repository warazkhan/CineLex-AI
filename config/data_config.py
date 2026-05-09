from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

IMDB_DIR = DATA_DIR / "imdb"
IMDB_CSV_PATH = IMDB_DIR / "imdb_top_1000.csv"

VECTOR_STORE_PATH = PROJECT_ROOT / "cinellex_rag" / "retrieval" / "vector_store"

CHROMA_STORE_PATH = PROJECT_ROOT / "cinellex_rag" / "retrieval" / "chroma_store"

# SQLite
SQLITE_DB_PATH = PROJECT_ROOT / "data" / "cinellex.db"