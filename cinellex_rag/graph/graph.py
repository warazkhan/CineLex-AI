from langgraph.graph import StateGraph, END

from cinellex_rag.graph.state import GraphState
from cinellex_rag.graph.nodes import (
    route_node,
    select_route,
    analytics_node,
    rag_node,
    recommend_node,
    format_node,
)


def build_graph():

    workflow = StateGraph(GraphState)

    workflow.add_node("route", route_node)
    workflow.add_node("analytics", analytics_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("recommend", recommend_node)
    workflow.add_node("format", format_node)

    workflow.set_entry_point("route")

    # route → one of the three execution paths
    workflow.add_conditional_edges(
        "route",
        select_route,
        {
            "analytics": "analytics",
            "rag": "rag",
            "recommend": "recommend",
        },
    )

    # every execution path funnels into format → END
    workflow.add_edge("analytics", "format")
    workflow.add_edge("rag", "format")
    workflow.add_edge("recommend", "format")
    workflow.add_edge("format", END)

    return workflow.compile()


graph_app = build_graph()


def run_graph(query: str):
    return graph_app.invoke({
        "query": query,
        "route": None,
        "result": None,
        "metadata": {},
    })
