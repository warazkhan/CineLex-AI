FROM python:3.11-slim

WORKDIR /app

# Runtime env:
# - PYTHONDONTWRITEBYTECODE/PYTHONUNBUFFERED: no .pyc churn, unbuffered logs.
# - *_TELEMETRY / OTEL_SDK_DISABLED: crewai and its transitive chromadb both ship
#   OpenTelemetry exporters that fire background network calls on every cold
#   start. We don't collect that data, so disable it — less startup latency,
#   less memory, and a quieter log on Render's free tier (512 MB / spins down).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OTEL_SDK_DISABLED=true \
    CREWAI_DISABLE_TELEMETRY=true \
    ANONYMIZED_TELEMETRY=False

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
