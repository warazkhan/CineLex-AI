FROM python:3.11-slim

WORKDIR /app

# curl is the only OS package needed at runtime — the Streamlit init-container's
# API health check and the docker-compose healthcheck both shell out to it.
# No compiler toolchain anymore: the heavy native deps (torch,
# sentence-transformers, chromadb) are gone now that the app is fully live on TMDB.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip --quiet && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# No build-time data step: there is no CSV to copy and no SQLite/Chroma store to
# seed. The app queries TMDB live at request time; TMDB_API_KEY is supplied as a
# runtime env var (.env / docker-compose / k8s Secret).

EXPOSE 8000

CMD ["uvicorn", "cinellex_rag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
