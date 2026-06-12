# 🎬 CineLex AI — Hybrid Movie Intelligence Agent

## 🚀 Overview

**CineLex AI** is a hybrid movie question-answering system, served **fully live from
[TMDB](https://www.themoviedb.org/)** — there is no local dataset, SQLite DB or
vector store. It combines three complementary engines behind a single router:

- **Structured analytics** over TMDB `/discover` — top-rated, latest, highest-grossing, …
- **Concept-retrieval RAG** — the LLM distils a question into TMDB *facets*
  (keywords + genres) and retrieves over TMDB's curated taxonomy, then answers with a
  **Groq LLM** — semantic-style retrieval **without embeddings**
- **Agentic recommendations** via a **CrewAI** crew grounded on TMDB `/recommendations`

Users ask free-form questions about movies — *top-rated films, plot-described titles,
summaries, "recommend something like Inception"* — and every route queries TMDB at
request time, returning rich movie cards (fresh posters, trailers, `tmdb_id`/`imdb_id`,
ratings, popularity) that the UI renders as poster tiles.

This project demonstrates **end-to-end AI system design**, not just model usage.

---

## 🎯 Why CineLex AI?

Most LLM movie demos:
- Hallucinate facts
- Struggle with numeric or ranking queries
- Go stale against a frozen dataset
- Only find a film if you already know its title

**CineLex AI** solves this by combining deterministic analytics with concept-aware RAG,
over a **live, always-current data source**:

> "Use code when precision is required; use LLMs when reasoning is required — and never
> serve yesterday's catalog."

This hybrid approach mirrors how **real production AI systems** operate.

---

## 🧠 Capabilities

### Analytics-driven queries — TMDB `/discover`
- Top / best / worst movies by rating
- Latest & recent releases
- Highest-grossing films

### Knowledge queries (RAG) — TMDB search/keywords + LLM
- Movie summaries, director & cast info
- Natural-language questions, e.g. *"Tell me about The Shawshank Redemption"*
- **Concept retrieval** for thematic, plot-based questions — the LLM distils the query into
  TMDB *facets* (keywords + genres) and retrieves over TMDB's curated taxonomy, so a question
  like *"a thief who steals corporate secrets through dream-sharing"* resolves to **Inception**
  even though no title contains those words — **no embeddings or vector store required**

### Recommendations — TMDB `/recommendations` + CrewAI
- "Recommend movies like *Inception*" → a grounded, ranked, narrated list

### Hybrid reasoning
The router automatically decides when to **compute** (analytics), **retrieve** (RAG), or
**reason** (recommend) — precedence is `recommend > analytics > rag`.

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
                              ├── RAG        (tmdb /search + keyword/genre facets + Groq LLM)
                              └── Recommend  (tmdb /recommendations + CrewAI)
                                       ↓
                              Response Formatter  →  Final Answer + cards
```

Every route emits the **same card shape**, so the API schema and UI need only one renderer.

---

## ⚙ Project Structure

```text
AI-LEARNING/
├── pyproject.toml              # build metadata, pytest config, deps (sourced from requirements.txt)
├── requirements.txt            # runtime dependencies for the app image / production service
├── requirements-dev.txt        # pytest + local/CI test tooling
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
│   │   ├── formatter.py        # answer text shaping
│   │   └── schema.py           # response builder
│   ├── retrieval/              # rag.py — facet (concept) retrieval + LLM knowledge answers
│   ├── crew/                   # CrewAI 3-agent recommendation crew
│   ├── graph/                  # LangGraph: route → {analytics|rag|recommend} → format
│   ├── observability/          # MLflow logging
│   └── utils/                  # llm_utils (Groq client factory)
├── tests/                      # pytest suite (TMDB + LLM fully mocked — offline)
├── evaluation/                 # opt-in RAGAS harness + 15-question ground-truth dataset
├── .github/workflows/          # CI/CD pipeline (tests, Docker build, Render hooks)
├── streamlit_app.py            # UI launcher (thin) → ui/app.py
├── ui/                         # Streamlit UI package (config, styles, api_client, components/)
├── k8s/                        # staging/production manifests + ArgoCD
└── Dockerfile / docker-compose.yml
```

---

## 🛠 How It Works

### 1️⃣ Live data client (`core/tmdb.py`)
- Owns all HTTP, auth, caching and the typed endpoint wrappers (`search_movies`,
  `search_keywords`, `movie_details`, `movie_recommendations`, `discover`, `genre_map`,
  `pick_trailer`).
- **Never raises to callers** — every wrapper returns `None` / `[]` / `{}` on a missing
  key, timeout or HTTP error, so handlers degrade to a friendly message instead of crashing.
- **Cached:** stable lookups (details / search / keywords / recommendations / genres) are
  memoised in-process and mirrored to `data/tmdb_cache.json`; volatile rankings (`discover`)
  use an in-memory cache, so "latest releases" refreshes on restart.

### 2️⃣ Query routing
- **Ranking / numeric / top-N → analytics**
- **Descriptive / knowledge → RAG**
- **"like / similar to / recommend" → recommend** (takes precedence)

### 3️⃣ Answer generation
- **Analytics** maps each query to a TMDB `sort_by` and expands the top results into cards.
- **RAG** resolves a single title directly; for thematic questions it asks the LLM to extract
  TMDB *facets* (an optional concrete title + keywords + genres), resolves those to TMDB
  keyword/genre ids, and retrieves over the `/discover` taxonomy (keywords AND-joined for
  precision → OR-joined for recall, any named title pinned first). It then **falls back to the
  legacy title search** when facets are thin or the LLM is unavailable, so no query regresses —
  and lets the LLM answer over the top results.
- **Recommendations** come from TMDB's own `/recommendations`, narrated by the CrewAI crew
  (the deterministic recommender grounds the crew so it can't invent titles).

### 4️⃣ Cards
- `core/movies.py` maps raw TMDB dicts into one card shape carrying poster, trailer,
  `tmdb_id`/`imdb_id`, rating, runtime, certificate, gross, cast and more — fetched
  concurrently and cached, so repeat queries are ~free.

---

## 🧪 Example Queries

```bash
top 3 movies
latest movies released
highest grossing movies
tell me about The Godfather
a thief who steals corporate secrets through dream-sharing   # concept retrieval → Inception
recommend movies like Inception
```

---

## 🧰 Tech Stack

- Python
- **TMDB API** — the live data source (movies, posters, trailers, ids, ratings, revenue,
  keyword/genre taxonomy)
- Groq `llama-3.1-8b-instant` (LLM + facet extraction, free tier)
- CrewAI (3-agent recommendation crew — recommendation path only)
- LangGraph (orchestration)
- FastAPI + Streamlit
- MLflow (observability)
- RAGAS (opt-in offline RAG evaluation — `requirements-eval.txt`)
- Docker · Kubernetes · ArgoCD (GitOps)
- GitHub Actions + Render deploy hooks for CI/CD

---

## ▶ How to Run Locally

```bash
# 1. Create + activate an environment
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

# 2. Install dependencies
# Runtime deps used by the app image and local API/UI runs
pip install -r requirements.txt
# Dev/test tooling used locally and in CI
pip install -r requirements-dev.txt
# Editable install so pytest imports the package cleanly
pip install -e . --no-deps

# 3. Configure environment
cp .env.example .env        # add your free GROQ_API_KEY and TMDB_API_KEY

# 4. Run the API + UI  (no data-ingestion step — the app is live on TMDB)
uvicorn cinellex_rag.api.app:app --reload        # http://localhost:8000
# Health check: http://localhost:8000/health
# Docs:         http://localhost:8000/docs
streamlit run streamlit_app.py                   # http://localhost:8501

# Or everything via Docker
docker-compose up --build
```

> **Keys:** `TMDB_API_KEY` accepts either a v3 API key or a v4 Read Access Token (Bearer).
> Without it the app still runs but every route returns a friendly "TMDB not configured"
> message instead of data. `GROQ_API_KEY` powers the LLM, facet extraction and the
> recommendation crew. Both are free.

### 🧪 Running the tests

```bash
pip install -r requirements-dev.txt
pip install -e . --no-deps
pytest            # test paths + pythonpath configured in pyproject.toml
                  # the TMDB client and LLM are fully mocked, so the suite runs offline (no key needed)
```

### 📊 Running the RAG evaluation (optional)

```bash
pip install -r requirements-eval.txt   # heavy embedding deps, kept out of the app image
python evaluation/run_ragas.py                 # RAGAS metrics, k=3
python evaluation/run_ragas.py --ablation      # RAGAS: concept retrieval OFF vs ON
python evaluation/run_ragas.py --retrieval     # fast title hit-rate@k (no judge), OFF vs ON
```

**RAGAS answer-quality scores** (baseline, `k=3`, 15 thematic ground-truth questions;
Groq `llama-3.1-8b-instant` judge + `all-MiniLM-L6-v2` embeddings):

| Metric | Score |
| --- | --- |
| Faithfulness | **0.69** |
| Answer relevancy | **0.88** |
| Context precision | **0.71** |
| Context recall | **0.80** |

These score the **end-to-end answer** (is it grounded in, and relevant to, the retrieved
context?). The ablation below instead isolates **retrieval** — does the right film get
pulled in the first place? — which is what the concept-retrieval upgrade targets.

**Concept-retrieval ablation (15 thematic ground-truth questions, hit-rate@3):**

| Retriever | Hit-rate@3 |
| --- | --- |
| Legacy title search (facets OFF) | **0.00** — TMDB `/search/movie` matches title text, so plot descriptions return nothing |
| Concept retrieval (facets ON) | **0.67** — LLM facets → TMDB keyword/genre taxonomy |

Remaining misses retrieve *thematically adjacent* films (e.g. other Batman/Pixar titles);
facet quality is bounded by the free-tier 8B model rather than the retrieval logic.

---

## ✅ Shipped

- 🌐 **Fully live on TMDB** — analytics, RAG and recommendations all query TMDB at request
  time; no local dataset, SQLite or vector store to build or ship
- 🔎 **Concept (facet) retrieval for thematic RAG** — LLM-extracted TMDB keyword/genre facets
  retrieve over TMDB's curated taxonomy (with a graceful title-search fallback), lifting top-3
  retrieval hit-rate on plot-described questions from **0% → 67%** vs. the old title-only
  search — **no embeddings or vector store**
- 🎞 Rich movie-poster cards (fresh posters, `tmdb_id`/`imdb_id`, trailers, ratings,
  popularity), cached on disk and fetched concurrently
- 🎯 Content recommender over TMDB `/recommendations` + a 3-agent CrewAI recommendation flow
- 🌐 FastAPI API + Streamlit "answer-engine" UI with a per-answer "How I answered this" reveal
- 🧭 Honest 3-path routing (analytics / rag / recommend) on LangGraph
- 📊 Opt-in RAGAS evaluation harness (faithfulness, answer relevancy, context precision/recall)
  plus a concept-retrieval ablation (`--ablation` / `--retrieval`)
- 🐳 Docker + Kubernetes + ArgoCD GitOps

---

## ⚠ Current Limitations

- **Concept retrieval, not embeddings** — thematic queries are resolved via the LLM + TMDB's
  keyword/genre taxonomy (no local vector store). This is far stronger than the old title-only
  search, but facet quality is bounded by the free-tier 8B model, so very abstract phrasing can
  still retrieve a thematically-adjacent film rather than the exact one.
- **Per-query latency** — each query makes live calls (concept retrieval adds one LLM call for
  facet extraction); mitigated by the on-disk + in-memory caches, so first-time queries are
  slower and repeats are ~free. The extra LLM call has a kill-switch (`use_facets=False`).
- Recommendations are content-based (TMDB's own similarity), not collaborative filtering.
- Free-tier LLM (Groq) — RAGAS evaluation runs on a small set to respect rate limits.

---

## 🔮 Planned Improvements (v2)

- 🔁 LLM reranking of the facet/title candidate set (facet extraction already ships)
- 🧠 Conversation memory across multi-turn queries
- 🌍 Multi-language / region-aware results (TMDB supports both)
- 📈 Larger evaluation set + automated eval in CI

---

## 🧠 What This Project Demonstrates

- Agentic reasoning
- Hybrid AI system design (deterministic analytics + concept-retrieval RAG + agents)
- Semantic-style retrieval over a third-party taxonomy **without** an embedding store
- Building cleanly on a live third-party API (auth, caching, graceful degradation)
- Clean modular architecture with an honest, ablation-backed evaluation story

---

## 📌 Project Name

**CineLex AI — Lexical Intelligence for Cinema Knowledge**

---

## 🏁 Acknowledgements

Special thanks to:
- **TMDB (The Movie Database)** for the live movie data — posters, trailers, ids, ratings,
  metadata and the keyword/genre taxonomy that powers concept retrieval
- **Groq** for the free-tier LLM
- **CrewAI**, **LangGraph** and **RAGAS** for orchestration and evaluation

> This product uses the TMDB API but is not endorsed or certified by TMDB.

---

> **CineLex AI — Where Structured Precision Meets Lexical Intelligence 🎥**
