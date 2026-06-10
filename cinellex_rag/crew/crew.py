import re

from crewai import Crew, Process

from cinellex_rag.crew.agents import taste_analyst, data_analyst, recommender
from cinellex_rag.crew.tasks import taste_task, data_task, recommend_task
from cinellex_rag.core.router import RECOMMEND_KEYWORDS
from cinellex_rag.core.movie_recommender import recommend_movies
from config.schema_config import COL_TITLE, COL_RATING, COL_DIRECTOR

# Filler words to strip when isolating the seed title from a free-form request.
_FILLER = RECOMMEND_KEYWORDS + [
    "movies", "films", "movie", "film",
    "give me", "show me", "some", "please", "like", "to", "for", "me",
]
_STRIP_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in _FILLER) + r")\b", flags=re.IGNORECASE
)


def extract_seed_title(query: str) -> str:
    """Best-effort isolation of the seed movie title from a recommend query.

    Only a hint — the deterministic recommender fuzzy-matches it against real titles.
    """
    s = _STRIP_RE.sub(" ", query.lower())
    return re.sub(r"\s+", " ", s).strip()


class RecommendationCrew:
    """Three-agent CrewAI flow (taste → data → recommender), grounded on the
    deterministic recommender. Falls back to a plain candidate list if the crew
    errors or hits a Groq rate limit, so the endpoint never hard-fails."""

    def run(self, query: str) -> str:
        seed = extract_seed_title(query)

        try:
            t_taste = taste_task(taste_analyst, query)
            t_data = data_task(data_analyst, seed)
            t_rec = recommend_task(recommender)
            t_rec.context = [t_taste, t_data]

            crew = Crew(
                agents=[taste_analyst, data_analyst, recommender],
                tasks=[t_taste, t_data, t_rec],
                process=Process.sequential,
                verbose=True,
            )
            return str(crew.kickoff())
        except Exception:
            return self._fallback(seed)

    @staticmethod
    def _fallback(seed: str) -> str:
        recs = recommend_movies(seed, top_n=3)
        if isinstance(recs, str):
            return recs
        lines = [
            f"{i}. {r[COL_TITLE]} — Rating: {r[COL_RATING]} (dir. {r[COL_DIRECTOR]})"
            for i, r in enumerate(recs, 1)
        ]
        return f"Movies similar to '{seed}':\n" + "\n".join(lines)
