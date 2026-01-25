# 🎬 CineLex AI — Hybrid Movie Intelligence Agent

## 🚀 Overview

**CineLex AI** is a hybrid, local movie question-answering system that combines:

- **Structured analytics** using **Pandas**  
- **Semantic retrieval (RAG)** using **FAISS + embeddings**  
- **Natural language reasoning** using a **local LLM**

Users can ask free-form questions about movies — such as *top-rated films, directors, release years,* or *summaries* — over the **IMDB Top 1000 dataset**, without using external APIs or paid models.

This project demonstrates **end-to-end AI system design**, not just model usage.

---

## 🎯 Why CineLex AI?

Most LLM demos:
- Hallucinate facts  
- Struggle with numeric or ranking queries  
- Fail silently on structured data  

**CineLex AI** solves this by combining deterministic analytics with RAG:

> “Use code when precision is required; use LLMs when reasoning is required.”

This hybrid approach mirrors how **real production AI systems** operate.

---

## 🧠 Capabilities (v1)

### Analytics-Driven Queries (Pandas)
- Top N movies by rating  
- Top directors  
- Latest release years  
- Vote or rating-based rankings  

### Knowledge Queries (RAG)
- Movie summaries  
- Director and cast information  
- Natural language questions, e.g.:
  - “Tell me about *The Shawshank Redemption*”

### Hybrid Reasoning
The agent automatically decides:
- When to compute (Analytics)  
- When to retrieve (RAG)  
- When to reason (LLM)

---

## 🏗 System Architecture

```text
User Query
    ↓
Query Router
    ├── Analytics Path (Pandas) --> Handles ranking / numeric / top-N queries
    └── RAG Path (FAISS + LLM) --> Handles descriptive / semantic queries
            ↓
     Response Formatter --> Formats analytics and RAG results consistently
            ↓
        Final Answer
```

---

## ⚙ Project Structure

```text
AI-LEARNING/
├── config/
│   └── data_config.py
├── data/
│   └── imdb/
│       ├── imdb_top_1000.csv
│       └── metadata.json
├── rag-imdb-knowledge-agent/
│   ├── agents/
│   │   └── rag_agent.py
│   ├── core/
│   │   ├── analytics.py
│   │   ├── router.py
│   │   └── formatter.py
│   ├── ingestion/
│   │   └── ingest_csv.py
│   └── retrieval/
│       └── vector_store.faiss/
├── utils/
│   ├── llm_utils.py
│   └── movie_analytics.py
├── requirements.txt
└── .env
```

---

## 🛠 How It Works

### 1️⃣ Data Ingestion
- IMDB CSV is cleaned and normalized.  
- Movie rows are converted to text documents.  
- Embeddings are generated and stored in a FAISS vector index.  

### 2️⃣ Query Routing
- The agent inspects the query:
  - **Ranking / numeric / top-N → Pandas**
  - **Descriptive / semantic → RAG**

### 3️⃣ Answer Generation
- Analytics answers are computed deterministically.  
- RAG answers are generated using retrieved context + LLM.  
- Results are formatted consistently.

---

## 🧪 Example Queries

```bash
top 3 movies
top 5 directors
latest movies released
tell me about The Godfather
top 3 movies with directors
```

---

## 🧰 Tech Stack

- Python  
- Pandas (analytics)  
- FAISS (vector database)  
- LangChain  
- HuggingFace embeddings  
- Flan-T5 (local LLM)

---

## ▶ How to Run Locally

```bash
# 1. Create environment
python -m venv .venv

# 2. Activate environment
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build vector store
python rag-imdb-knowledge-agent/ingestion/ingest_csv.py

# 5. Run the agent
python rag-imdb-knowledge-agent/agents/rag_agent.py
```

---

## ⚠ Current Limitations (Intentional)

- No recommender system (yet)  
- No web UI  
- English movies dominate dataset  
- No feedback loop / evaluation metrics  

---

## 🔮 Planned Improvements (v2)

- 🎯 Movie recommender system  
- 🔁 Query refinement + reranking  
- 📊 Evaluation metrics (Recall@K, accuracy)  
- 🌐 FastAPI / Streamlit interface  
- 🧠 Memory-augmented agent  
- 🎥 Multimodal extensions (trailers, posters)

---

## 🧠 What This Project Demonstrates

- Agentic reasoning  
- Hybrid AI system design  
- RAG + analytics integration  
- Local LLM deployment  
- Clean modular architecture

---

## 📌 Project Name

**CineLex AI — Lexical Intelligence for Cinema Knowledge**

---

## 🏁 Acknowledgements

Special thanks to:
- **IMDB Dataset** for movie data  
- **HuggingFace** for embeddings  
- **FAISS** for vector search  
- **LangChain** for RAG orchestration  

---

> **CineLex AI — Where Structured Precision Meets Lexical Intelligence 🎥**
