import re
import time
from cinellex_rag.core.schema import build_response
from cinellex_rag.observability.mlflow_logger import logger
from cinellex_rag.tools.registry import ToolRegistry

ANALYTICS_KEYWORDS = [
    "top", "best", "worst", "list", "highest",
    "lowest", "latest", "recent", "release", "releases", "director"
]


def route_node(state):
    logger.start_run(state["query"])

    query = state["query"].lower()

    if any(x in query for x in ANALYTICS_KEYWORDS):
        state["route"] = "analytics"
    else:
        state["route"] = "rag"

    logger.log_route(state["route"])
    return state


def _parse_retry_wait(error_msg: str, default: float = 15.0) -> float:
    """Extract wait seconds from Groq rate limit error message."""
    match = re.search(r'try again in (\d+(?:\.\d+)?)s', str(error_msg))
    return float(match.group(1)) + 1.0 if match else default


def crew_node(state):
    """
    Direct tool execution — fast, no CrewAI overhead.
    """
    result = ToolRegistry.execute(state["route"], state["query"])

    state["result"] = {
        "answer": result.get("answer", str(result)) if isinstance(result, dict) else str(result),
        "source": "direct"
    }

    logger.log_node("direct_execution", {"query": state["query"]})
    return state


def tool_node(state):
    query = state["query"]
    tool = state.get("route", "rag")

    result = ToolRegistry.execute(tool, query)
    state["result"] = result

    logger.log_node("tool_execution", {"tool": tool})
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
        metadata={**metadata, "source": source}
    )

    logger.log_response(response)
    logger.end_run()

    state["result"] = response
    return state