from pathlib import Path

# Repository root, used to anchor the TMDB response-cache path
# (data/tmdb_cache.json, see config/tmdb_config.py). The app is fully live on
# TMDB — there is no local catalog, SQLite DB or vector store.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
