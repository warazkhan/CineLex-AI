import sqlite3
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.data_config import IMDB_CSV_PATH, SQLITE_DB_PATH

# ------------------------------
# Load CSV
# ------------------------------
print("Loading IMDB dataset...")
df = pd.read_csv(IMDB_CSV_PATH)

# Clean columns
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
# Create SQLite database
# ------------------------------
print(f"Creating SQLite database at: {SQLITE_DB_PATH}")
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(SQLITE_DB_PATH))

df.to_sql("movies", conn, if_exists="replace", index=False)

# Create indexes for fast querying
conn.execute("CREATE INDEX IF NOT EXISTS idx_rating ON movies (IMDB_Rating)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON movies (Released_Year)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON movies (Series_Title)")

conn.commit()
conn.close()

print(f"Done! {len(df)} movies stored in SQLite.")