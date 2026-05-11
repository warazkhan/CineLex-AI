from cinellex_rag.agents.rag_agent import is_valid_query


def test_valid_queries():
    assert is_valid_query("top 5 movies") == True
    assert is_valid_query("hi") == False
    assert is_valid_query("abc") == False