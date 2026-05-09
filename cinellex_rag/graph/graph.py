from langgraph.graph import StateGraph, END

from cinellex_rag.graph.state import GraphState
from cinellex_rag.graph.nodes import (
    route_node,
    crew_node,
    format_node
)


def build_graph():

    workflow = StateGraph(GraphState)

    workflow.add_node("route", route_node)
    workflow.add_node("crew", crew_node)
    workflow.add_node("format", format_node)

    workflow.set_entry_point("route")

    workflow.add_edge("route", "crew")
    workflow.add_edge("crew", "format")
    workflow.add_edge("format", END)

    return workflow.compile()


graph_app = build_graph()


def run_graph(query: str):
    return graph_app.invoke({
        "query": query,
        "route": None,
        "result": None,
        "metadata": {}
    })