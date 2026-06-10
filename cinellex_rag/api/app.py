from fastapi import FastAPI, HTTPException
from cinellex_rag.api.schemas import QueryRequest, QueryResponse
from cinellex_rag.graph.graph import run_graph
from cinellex_rag.agents.rag_agent import is_valid_query
from config.tmdb_config import TMDB_ENABLED

app = FastAPI(
    title="CineLex AI",
    description="Movie Q&A API powered by LangGraph + CrewAI",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"status": "ok", "service": "cinellex-ai"}


@app.get("/health")
def health():
    # tmdb_enabled lets the UI warn loudly when the server has no TMDB key
    # (the app still answers, but with text and no posters).
    return {"status": "ok", "service": "cinellex-ai", "tmdb_enabled": TMDB_ENABLED}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if not is_valid_query(request.query):
        raise HTTPException(
            status_code=400,
            detail="Please ask a movie-related question"
        )

    result = run_graph(request.query)
    result_data = result.get("result", {})

    return QueryResponse(
        answer=result_data.get("answer", ""),
        route=result_data.get("route", "unknown"),
        source=result_data.get("metadata", {}).get("source", "unknown"),
        movies=result_data.get("movies", []),
        metadata=result_data.get("metadata", {})
    )
