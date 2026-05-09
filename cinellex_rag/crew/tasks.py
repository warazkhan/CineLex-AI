from crewai import Task


def rag_task(agent, query):
    return Task(
        description=f"""
        Answer the following movie question using knowledge retrieval:
        {query}
        """,
        agent=agent,
        expected_output="Accurate movie explanation or summary"
    )


def analytics_task(agent, query):
    return Task(
        description=f"""
        Analyze the dataset and answer:
        {query}
        """,
        agent=agent,
        expected_output="Ranked or structured movie insights"
    )