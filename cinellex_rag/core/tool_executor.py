from cinellex_rag.core.tools import TOOLS


def execute_tool(tool_name: str, query: str):
    """
    Central execution layer (LangChain-style abstraction)
    """
    tool = TOOLS.get(tool_name)

    if not tool:
        return {
            "answer": "Invalid tool requested",
            "source": "system",
            "metadata": {}
        }

    result = tool(query)

    # normalize minimal safety shape
    if isinstance(result, dict):
        return result

    return {
        "answer": str(result),
        "source": tool_name,
        "metadata": {}
    }