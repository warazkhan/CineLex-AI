from crewai import Crew
from cinellex_rag.crew.agents import rag_agent, analytics_agent
from cinellex_rag.crew.tasks import rag_task, analytics_task

# Single source of truth for analytics routing.
# Must stay in sync with analytics_keywords in graph/nodes.py.
ANALYTICS_KEYWORDS = [
    "top", "best", "worst", "list", "highest",
    "lowest", "latest", "recent", "release", "releases", "director"
]


class MovieCrew:

    def __init__(self):
        self.agents = {
            "rag": rag_agent,
            "analytics": analytics_agent
        }

    def route(self, query: str) -> str:
        q = query.lower()
        if any(x in q for x in ANALYTICS_KEYWORDS):
            return "analytics"
        return "rag"

    def run(self, query: str):
        task_type = self.route(query)

        if task_type == "rag":
            task = rag_task(self.agents["rag"], query)
            crew = Crew(
                agents=[self.agents["rag"]],
                tasks=[task],
                verbose=True
            )
        else:
            task = analytics_task(self.agents["analytics"], query)
            crew = Crew(
                agents=[self.agents["analytics"]],
                tasks=[task],
                verbose=True
            )

        return crew.kickoff()