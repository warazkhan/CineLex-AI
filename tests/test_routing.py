from cinellex_rag.core.router import classify
from cinellex_rag.graph.nodes import route_node, recommend_node


# ---- router classification (single source of truth) ----

def test_routes_analytics():
    assert classify("top 5 movies") == "analytics"


def test_routes_rag():
    assert classify("tell me about Inception") == "rag"


def test_routes_recommend():
    assert classify("recommend movies like Inception") == "recommend"


def test_recommend_precedence_over_analytics():
    # contains "top" (analytics) but the intent is recommendation
    assert classify("top films similar to Heat") == "recommend"


# ---- route_node writes the route into state ----

def test_route_node_sets_route():
    assert route_node({"query": "tell me about Inception"})["route"] == "rag"


# ---- recommend_node delegates to the crew (mocked, no live LLM) ----

def test_recommend_node_uses_crew(monkeypatch):
    class FakeCrew:
        def run(self, query):
            return "FAKE RECOMMENDATIONS"

    monkeypatch.setattr("cinellex_rag.crew.crew.RecommendationCrew", FakeCrew)
    # Keep the node fully offline: stub the recommender + the card lookup so no
    # live TMDB call is made (recommend_node imports these lazily at call time).
    monkeypatch.setattr(
        "cinellex_rag.core.movie_recommender.recommend_movies",
        lambda seed, top_n=6: [{"Series_Title": "Heat"}],
    )
    monkeypatch.setattr(
        "cinellex_rag.core.movies.card_from_title",
        lambda title, **kw: {"kind": "movie", "title": title},
    )

    out = recommend_node({"query": "recommend movies like Inception"})

    assert out["result"]["answer"] == "FAKE RECOMMENDATIONS"
    assert out["result"]["source"] == "recommendation-crew"
    assert out["result"]["movies"] == [{"kind": "movie", "title": "Heat"}]
