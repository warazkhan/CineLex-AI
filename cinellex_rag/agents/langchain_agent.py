from langchain.agents import initialize_agent, AgentType

from cinellex_rag.tools.registry import TOOLS
from cinellex_rag.utils.llm_utils import load_model


def build_agent():
    llm = load_model()[1]

    agent = initialize_agent(
        tools=TOOLS,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    return agent


def run_agent(query: str):
    agent = build_agent()
    return agent.invoke({"input": query})