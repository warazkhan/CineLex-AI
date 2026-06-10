from crewai import Task


def taste_task(agent, query):
    return Task(
        description=(
            f"The viewer asked: '{query}'.\n"
            "Identify the single seed movie they want recommendations based on, "
            "and describe their taste in 1-2 sentences (genre, tone, director, era)."
        ),
        agent=agent,
        expected_output="The seed movie title and a short taste profile.",
    )


def data_task(agent, seed_hint):
    return Task(
        description=(
            "Use the movie_recommender_tool to fetch similar movies for the seed "
            f"movie (best guess from the request: '{seed_hint}'). "
            "Return the exact candidate list the tool produces — do not add or invent movies."
        ),
        agent=agent,
        expected_output="The bullet list of candidate movies (title, rating, director) from the tool.",
    )


def recommend_task(agent):
    return Task(
        description=(
            "Using ONLY the candidate movies fetched by the data analyst and the "
            "taste profile from the taste analyst, write the final recommendation: "
            "a one-line intro followed by a ranked list of 3 movies, each with a single "
            "sentence on why it fits. Never mention a movie that is not in the candidate list."
        ),
        agent=agent,
        expected_output="A concise, friendly recommendation: intro + 3 ranked movies with reasons.",
    )
