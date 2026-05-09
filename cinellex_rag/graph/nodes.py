from cinellex_rag.core.schema import build_response
from cinellex_rag.observability.mlflow_logger import logger
from cinellex_rag.tools.registry import ToolRegistry


def route_node(state):
    logger.start_run(state["query"])

    query = state["query"].lower()

    analytics_keywords = [
    "top",
    "best",
    "worst",
    "list",
    "highest",
    "lowest",
    "latest",
    "recent",
    "release",
    "releases",
    "director"
    ]

    if any(x in query for x in analytics_keywords):
        state["route"] = "analytics"
    else:
        state["route"] = "rag"

    logger.log_route(state["route"])
    return state


def crew_node(state):
    """
    CrewAI with fallback to direct tool execution.
    """
    from cinellex_rag.crew.crew import MovieCrew

    try:
        crew = MovieCrew()
        result = crew.run(state["query"])

        state["result"] = {
            "answer": str(result),
            "source": "crewai"
        }

        logger.log_node("crewai_execution", {
            "query": state["query"]
        })

    except Exception as e:
        # fallback to direct tool execution
        print(f"\n[Fallback] CrewAI failed ({type(e).__name__}), using direct tool...\n")

        result = ToolRegistry.execute(state["route"], state["query"])

        state["result"] = {
            "answer": result.get("answer", str(result)) if isinstance(result, dict) else str(result),
            "source": "fallback"
        }

        logger.log_node("fallback_execution", {
            "reason": str(e)[:100]
        })

    return state


def tool_node(state):
    query = state["query"]
    tool = state.get("route", "rag")

    result = ToolRegistry.execute(tool, query)
    state["result"] = result

    logger.log_node("tool_execution", {
        "tool": tool
    })

    return state


def format_node(state):
    result = state["result"]

    if isinstance(result, dict):
        answer = result.get("answer", "")
        source = result.get("source", "unknown")
        metadata = result.get("metadata", {})
    else:
        answer = str(result)
        source = state.get("route", "unknown")
        metadata = {}

    response = build_response(
        answer=answer,
        route=state.get("route", "unknown"),
        metadata={
            **metadata,
            "source": source
        }
    )

    logger.log_response(response)
    logger.end_run()

    state["result"] = response
    return state