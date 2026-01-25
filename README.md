🎬 CineLex AI — Hybrid Movie Intelligence Agent

🚀 Overview

CineLex AI is a hybrid, local Movie Question-Answering system that combines:

Structured analytics using Pandas
Semantic retrieval (RAG) using FAISS + embeddings
Natural language reasoning using a local LLM

The system allows users to ask free-form questions about movies (e.g., top movies, directors, release years, summaries) over the IMDB Top 1000 dataset, without relying on external APIs or paid models.

This project demonstrates end-to-end AI system design, not just model usage.

🎯 Why CineLex AI?

Most LLM demos:
Hallucinate facts
Struggle with numeric / ranking queries
Fail silently on structured data
CineLex AI solves this by combining deterministic analytics with retrieval-augmented generation (RAG):
“Use code when precision is required, use LLMs when reasoning is required.”
This hybrid approach mirrors real production AI systems.

🧠 What the Agent Can Do (v1)

✔ Analytics-Driven Queries (Pandas)
Top N movies by rating
Top directors
Latest release years
Vote / rating based rankings

✔ Knowledge Queries (RAG)
“Tell me about The Shawshank Redemption”
Movie summaries
Director and cast information
Natural language movie questions

✔ Hybrid Reasoning
The agent automatically decides:
When to compute
When to retrieve
When to reason

🏗 System Architecture

User Query
   ↓
Query Router
   ├── Analytics Path (Pandas)
   └── RAG Path (FAISS + LLM)
         ↓
     Response Formatter
         ↓
     Final Answer

🔧 Project Structure

AI-LEARNING/
├── config/
│   └── data_config.py
├── data/imdb/
│   ├── imdb_top_1000.csv
│   └── metadata.json
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

⚙ How It Works

1️⃣ Data Ingestion
IMDB CSV is cleaned and normalized
Movie rows are converted to text documents
Embeddings are generated
Stored in a FAISS vector index

2️⃣ Query Routing
The agent inspects the query:
Ranking / numeric / top-N → Pandas
Descriptive / semantic → RAG

3️⃣ Answer Generation
Analytics answers are computed deterministically
RAG answers are generated using retrieved context + LLM
Results are formatted consistently

🧪 Example Queries
top 3 movies
top 5 directors
latest movies released
tell me about The Godfather
top 3 movies with directors

🧰 Tech Stack
Python
Pandas (analytics)
FAISS (vector database)
LangChain
HuggingFace embeddings
Flan-T5 (local LLM)

▶ How to Run Locally
1️⃣ Create environment
python -m venv .venv
source .venv/bin/activate  # or Activate.ps1 on Windows
pip install -r requirements.txt

2️⃣ Build vector store
python rag-imdb-knowledge-agent/ingestion/ingest_csv.py

3️⃣ Run the agent
python rag-imdb-knowledge-agent/agents/rag_agent.py

⚠ Current Limitations (Intentional)

No recommender system (yet)
No web UI
English movies dominate dataset
No feedback loop / evaluation metrics
These are planned v2 improvements, not missing features.

🔮 Planned Improvements (v2)
🎯 Movie recommender system
🔁 Query refinement + reranking
📊 Evaluation metrics (Recall@K, accuracy)
🌐 FastAPI / Streamlit interface
🧠 Memory-augmented agent
🎥 Multimodal extensions (trailers, posters)
🧠 What This Project Demonstrates

✔ Agentic reasoning
✔ Hybrid AI system design
✔ RAG + analytics integration
✔ Local LLM deployment
✔ Clean modular architecture

This project is designed for technical interviews, research roles, and applied AI positions.

📌 Project Name
CineLex AI
Lexical Intelligence for Cinema Knowledge