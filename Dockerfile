FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

COPY data/imdb/imdb_top_1000.csv /app/data/imdb/imdb_top_1000.csv

RUN pip install --upgrade pip --quiet && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake data into the image — no volumes needed
RUN mkdir -p data/imdb cinellex_rag/retrieval/chroma_store

EXPOSE 8000

CMD ["uvicorn", "cinellex_rag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]