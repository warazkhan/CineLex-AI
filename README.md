# 🎬 CineLex AI — Hybrid Movie Intelligence Agent

## 🚀 Overview

**CineLex AI** is a hybrid movie question-answering system, served **fully live from
[TMDB](https://www.themoviedb.org/)** — there is no local dataset, SQLite DB or
vector store. It combines:

- **Structured analytics** over TMDB `/discover` (top-rated, latest, highest-grossing, …)
- **Knowledge retrieval (RAG)** over TMDB search + a **Groq LLM**
- **Agentic recommendations** via a **CrewAI** crew grounded on TMDB `/recommendations`

Users ask free-form questions about movies — *top-rated films, directors, summaries,
"recommend something like Inception"* — and every route queries TMDB at request time,
returning rich movie cards (fresh posters, trailers, `tmdb_id`/`imdb_id`, ratings,
popularity) that the UI renders as poster tiles.

This project demonstrates **end-to-end AI system design**, not just model usage.

---

## 🎯 Why CineLex AI?

Most LLM demos:
- Hallucinate facts
- Struggle with numeric or ranking queries
- Go stale against a frozen dataset

**CineLex AI** solves this by combining deterministic analytics with RAG, over a
**live, always-current data source**:

> "Use code when precision is required; use LLMs when reasoning is required — and
> never serve yesterday's catalog."

This hybrid approach mirrors how **real production AI systems** operate.

---

## 🧠 Capabilities

### Analytics-driven queries — TMDB `/discover`
- Top / best / worst movies by rating
- Latest & recent releases
- Highest-grossing films
- Top directors *(approximated by tallying directors across TMDB's current top-rated
  films — clearly labelled, since TMDB has no "top directors" endpoint)*

### Knowledge queries (RAG) — TMDB search + LLM
- Movie summaries, director & cast info
- Natural-language questions, e.g. *"Tell me about The Shawshank Redemption"*

### Recommendations — TMDB `/recommendations` + CrewAI
- "Recommend movies like *Inception*" → a grounded, ranked, narrated list

### Hybrid reasoning
The router automatically decides when to **compute** (analytics), **retrieve** (RAG),
or **reason** (recommend) — precedence is `recommend > analytics > rag`.

---

## 🏗 System Architecture

```text
                          TMDB API  (the only data source)
                              ▲
                              │  HTTP · auth · cache · endpoint wrappers
                  cinellex_rag/core/tmdb.py
                              │  raw TMDB dicts
                  cinellex_rag/core/movies.py   →  the UI "card" shape
                              ▲
User Query → Query Router ────┼───────────────────────────────────────────
                              ├── Analytics  (tmdb /discover)
                              ├── RAG        (tmdb /search + Groq LLM)
                              └── Recommend  (tmdb /recommendations + CrewAI)
                                       ↓
                              Response Formatter  →  Final Answer + cards
```

Every route emits the **same card shape**, so the API schema and UI need only one
renderer.

---

## ⚙ Project Structure

```text
AI-LEARNING/
├── pyproject.toml              # build metadata, pytest config, deps (sourced from requirements.txt)
├── requirements.txt            # runtime dependencies (single source of truth — slim, no ML stack)
├── requirements-eval.txt       # opt-in RAGAS evaluation extras (embeddings + ragas)
├── config/                     # tmdb_config (auth/cache/tuning) + recommender-schema keys
├── data/                       # only the regenerable TMDB response cache (tmdb_cache.json, gitignored)
├── cinellex_rag/
│   ├── api/                    # FastAPI app + schemas
│   ├── core/
│   │   ├── router.py           # single-source query routing (recommend > analytics > rag)
│   │   ├── tmdb.py             # ← the ONLY data source: HTTP + auth + cache + endpoint wrappers
│   │   ├── movies.py           # maps raw TMDB dicts → the UI's movie "card" shape
│   │   ├── analytics.py        # ranking queries over TMDB /discover
│   │   ├── movie_recommender.py# similar movies via TMDB /recommendations
│   │   └── schema.py           # response builder
│   ├── retrieval/              # rag.py — TMDB search + LLM knowledge answers
│   ├── crew/                   # CrewAI 3-agent recommendation crew
│   ├── graph/                  # LangGraph: route → {analytics|rag|recommend} → format
│   ├── observability/          # MLflow logging
│   └── utils/                  # llm_utils (Groq client factory)
├── tests/                      # pytest suite (TMDB client fully mocked — offline)
├── evaluation/                 # opt-in RAGAS harness + ground-truth dataset
├── streamlit_app.py            # UI launcher (thin) → ui/app.py
├── ui/                         # Streamlit UI package (config, styles, api_client, components/)
├── k8s/                        # staging/production manifests + ArgoCD
└── Dockerfile / docker-compose.yml
```

---

## 🛠 How It Works

### 1️⃣ Live data client (`core/tmdb.py`)
- Owns all HTTP, auth, caching and the typed endpoint wrappers (`search_movies`,
  `movie_details`, `movie_recommendations`, `discover`, `genre_map`, `pick_trailer`).
- **Never raises to callers** — every wrapper returns `None` / `[]` / `{}` on a missing
  key, timeout or HTTP error, so handlers degrade to a friendly message instead of crashing.
- **Cached:** stable lookups (details / search / recommendations / genres) are memoised
  in-process and mirrored to `data/tmdb_cache.json`; volatile rankings (`discover`) use an
  in-memory cache, so "latest releases" refreshes on restart.

### 2️⃣ Query routing
- **Ranking / numeric / top-N → analytics**
- **Descriptive / knowledge → RAG**
- **"like / similar to / recommend" → recommend** (takes precedence)

### 3️⃣ Answer generation
- Analytics maps each query to a TMDB `sort_by` and expands the top results into cards.
- RAG resolves a single title directly, or keyword-searches TMDB and lets the LLM answer
  over the top results.
- Recommendations come from TMDB's own `/recommendations`, narrated by the CrewAI crew
  (the deterministic recommender grounds the crew so it can't invent titles).

### 4️⃣ Cards
- `core/movies.py` maps raw TMDB dicts into one card shape carrying poster, trailer,
  `tmdb_id`/`imdb_id`, rating, runtime, certificate, gross, cast and more — fetched
  concurrently and cached, so repeat queries are ~free.

---

## 🧪 Example Queries

```bash
top 3 movies
top 5 directors
latest movies released
highest grossing movies
tell me about The Godfather
recommend movies like Inception
```

---

## 🧰 Tech Stack

- Python
- **TMDB API** — the live data source (movies, posters, trailers, ids, ratings, revenue)
- Groq `llama-3.1-8b-instant` (LLM, free tier)
- CrewAI (3-agent recommendation crew — recommendation path only)
- LangGraph (orchestration)
- FastAPI + Streamlit
- MLflow (observability)
- RAGAS (opt-in offline RAG evaluation — `requirements-eval.txt`)
- Docker · Kubernetes · ArgoCD (GitOps)

---

## ▶ How to Run Locally

```bash
# 1. Create + activate an environment
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

# 2. Install dependencies (editable install registers the package so imports + tests work)
pip install -e .
# (CI / Docker install only the runtime deps: pip install -r requirements.txt)

# 3. Configure environment
cp .env.example .env        # add your free GROQ_API_KEY and TMDB_API_KEY

# 4. Run the API + UI  (no data-ingestion step — the app is live on TMDB)
uvicorn cinellex_rag.api.app:app --reload        # http://localhost:8000
streamlit run streamlit_app.py                   # http://localhost:8501

# Or everything via Docker
docker-compose up --build
```

> **Keys:** `TMDB_API_KEY` accepts either a v3 API key or a v4 Read Access Token (Bearer).
> Without it the app still runs but every route returns a friendly "TMDB not configured"
> message instead of data. `GROQ_API_KEY` powers the LLM + recommendation crew. Both are free.

### 🧪 Running the tests

```bash
pytest            # test paths + pythonpath configured in pyproject.toml
                  # the TMDB client is fully mocked, so the suite runs offline (no key needed)
```

### 📊 Running the RAG evaluation (optional)

```bash
pip install -r requirements-eval.txt   # heavy embedding deps, kept out of the app image
python evaluation/run_ragas.py
```

---

## ✅ Shipped

- 🌐 **Fully live on TMDB** — analytics, RAG and recommendations all query TMDB at
  request time; no local dataset, SQLite or vector store to build or ship
- 🎞 Rich movie-poster cards (fresh posters, `tmdb_id`/`imdb_id`, trailers, ratings,
  popularity), cached on disk and fetched concurrently
- 🎯 Content recommender over TMDB `/recommendations` + a 3-agent CrewAI recommendation flow
- 🌐 FastAPI API + Streamlit "answer-engine" UI with a per-answer "How I answered this" reveal
- 🧭 Honest 3-path routing (analytics / rag / recommend) on LangGraph
- 📊 Opt-in RAGAS evaluation harness (faithfulness, answer relevancy, context precision/recall)
- 🐳 Docker + Kubernetes + ArgoCD GitOps

## ⚠ Current Limitations

- **Keyword (not semantic) RAG** — descriptive retrieval keyword-searches TMDB rather than
  using embeddings, so heavily thematic/phrasing-based queries are weaker than vector search.
- **"Top directors" is approximated** from TMDB's current top-rated films (TMDB has no
  directors endpoint) and is labelled as such.
- **Per-query latency** — each query makes live calls; mitigated by the on-disk + in-memory
  caches, so first-time queries are slower and repeats are ~free.
- Recommendations are content-based (TMDB's own similarity), not collaborative filtering.
- Free-tier LLM (Groq) — RAGAS evaluation runs on a small set to respect rate limits.

---

## 🔮 Planned Improvements (v2)

- 🔁 Query refinement + reranking over TMDB results
- 🧠 Memory-augmented agent
- 🌍 Multi-language / region-aware results (TMDB supports both)
- 📈 Larger evaluation set + automated eval in CI

---

## 🧠 What This Project Demonstrates

- Agentic reasoning
- Hybrid AI system design (deterministic analytics + RAG + agents)
- Building cleanly on a live third-party API (auth, caching, graceful degradation)
- Clean modular architecture

---

## 📌 Project Name

**CineLex AI — Lexical Intelligence for Cinema Knowledge**

---

## 🏁 Acknowledgements

Special thanks to:
- **TMDB (The Movie Database)** for the live movie data — posters, trailers, ids, ratings and metadata
- **Groq** for the free-tier LLM
- **CrewAI**, **LangGraph** and **RAGAS** for orchestration and evaluation

> This product uses the TMDB API but is not endorsed or certified by TMDB.

---

> **CineLex AI — Where Structured Precision Meets Lexical Intelligence 🎥**
