from cinellex_rag.graph.nodes import route_node     

def test_routes_analytics():
    assert route_node({"query": "top 5 movies"})["route"] == "analytics"

def test_routes_rag():
    assert route_node({"query": "tell me about Inception"})["route"] == "rag"