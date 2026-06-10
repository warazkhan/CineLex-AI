from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The app is fully live on TMDB — there is no local catalog, SQLite DB or vector
# store. DATA_DIR only holds the regenerable TMDB response cache
# (data/tmdb_cache.json, see config/tmdb_config.py).
DATA_DIR = PROJECT_ROOT / "data"
