import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from cinellex_rag.retrieval.rag import handle_rag
from cinellex_rag.core.analytics import handle_analytics

load_dotenv()

# ---------------------------
# GROQ LLM (Llama 3.3 70B)
# ---------------------------
# groq_llm = LLM(
#     model="groq/llama-3.3-70b-versatile",
#     api_key=os.environ.get("GROQ_API_KEY"),
#     max_tokens=500
# )

groq_llm = LLM(
    model="groq/llama-3.1-8b-instant",  # ← smaller, higher rate limit
    api_key=os.environ.get("GROQ_API_KEY"),
    max_tokens=500
)


# ---------------------------
# TOOL DEFINITIONS
# ---------------------------
class RAGToolInput(BaseModel):
    query: str = Field(description="Movie question to search for")


class AnalyticsToolInput(BaseModel):
    query: str = Field(description="Analytics question about movies")


class RAGTool(BaseTool):
    name: str = "movie_rag_tool"
    description: str = "Use for movie plot, story, overview, cast, details"
    args_schema: type[BaseModel] = RAGToolInput

    def _run(self, query: str) -> str:
        result = handle_rag(query)
        if isinstance(result, dict):
            return result.get("answer", str(result))
        return str(result)


class AnalyticsTool(BaseTool):
    name: str = "movie_analytics_tool"
    description: str = "Use for rankings, top movies, worst movies, directors, stats"
    args_schema: type[BaseModel] = AnalyticsToolInput

    def _run(self, query: str) -> str:
        result = handle_analytics(query)
        return str(result) if result else "No analytics data found"


rag_tool = RAGTool()
analytics_tool = AnalyticsTool()


# ---------------------------
# RAG SPECIALIST
# ---------------------------
rag_agent = Agent(
    role="Movie Knowledge Expert",
    goal="Answer movie-related questions using semantic retrieval",
    backstory="Expert in movie plots, summaries, and storytelling context.",
    tools=[rag_tool],
    llm=groq_llm,
    verbose=True,
    allow_delegation=False
)


# ---------------------------
# ANALYTICS SPECIALIST
# ---------------------------
analytics_agent = Agent(
    role="Movie Data Analyst",
    goal="Provide rankings, statistics, and structured insights",
    backstory="Expert in IMDB dataset analysis and movie rankings.",
    tools=[analytics_tool],
    llm=groq_llm,
    verbose=True,
    allow_delegation=False
)