import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from cinellex_rag.core.movie_recommender import recommend_movies
from config.schema_config import COL_TITLE, COL_RATING, COL_DIRECTOR

load_dotenv()

# ---------------------------
# LLM (Groq, free tier)
# Model is env-overridable so it can be swapped without code changes.
# max_tokens small + num_retries → keeps each call within the free TPM budget
# and lets litellm auto-wait/retry on RateLimitError.
# ---------------------------
groq_llm = LLM(
    model=os.environ.get("CREW_LLM_MODEL", "groq/llama-3.1-8b-instant"),
    api_key=os.environ.get("GROQ_API_KEY"),
    max_tokens=400,
    num_retries=3,
)


# ---------------------------
# DETERMINISTIC GROUNDING TOOL
# Supplies real candidate movies so the LLM cannot hallucinate titles.
# ---------------------------
class RecommenderToolInput(BaseModel):
    movie_title: str = Field(description="The seed movie title to find similar movies for")


class MovieRecommenderTool(BaseTool):
    name: str = "movie_recommender_tool"
    description: str = (
        "Given a seed movie title, returns real similar movies "
        "(title, rating, director) from the IMDB database. "
        "Always use this to obtain factual candidate movies — never invent titles."
    )
    args_schema: type[BaseModel] = RecommenderToolInput

    def _run(self, movie_title: str) -> str:
        recs = recommend_movies(movie_title, top_n=5)
        if isinstance(recs, str):
            return recs
        return "\n".join(
            f"- {r[COL_TITLE]} (rating {r[COL_RATING]}, dir. {r[COL_DIRECTOR]})"
            for r in recs
        )


movie_recommender_tool = MovieRecommenderTool()


# ---------------------------
# THREE-AGENT RECOMMENDATION CREW
# max_iter=2 keeps each agent to one tool call + a final answer (no looping).
# ---------------------------
taste_analyst = Agent(
    role="Film Taste Analyst",
    goal="Identify the seed movie the user referenced and describe the viewer's taste",
    backstory=(
        "You read a viewer's request, pinpoint the single movie they want "
        "recommendations based on, and summarise the qualities they enjoy "
        "(genre, tone, director, era)."
    ),
    llm=groq_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=2,
)

data_analyst = Agent(
    role="Movie Data Analyst",
    goal="Fetch factual similar-movie candidates from the IMDB database",
    backstory=(
        "You use the movie_recommender_tool to pull real candidate movies for a "
        "seed title. You report exactly what the tool returns and never invent titles."
    ),
    tools=[movie_recommender_tool],
    llm=groq_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=2,
)

recommender = Agent(
    role="Movie Recommender",
    goal="Present a friendly, ranked recommendation grounded only in the candidate list",
    backstory=(
        "You turn the analyst's candidate movies into a concise, engaging "
        "recommendation, explaining why each pick fits the viewer's taste. "
        "You only recommend movies that appear in the provided candidate list."
    ),
    llm=groq_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=2,
)
