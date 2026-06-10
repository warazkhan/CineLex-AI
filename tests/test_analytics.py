from cinellex_rag.core.analytics import extract_n   

def test_extract_n():
    assert extract_n("top 10 movies") == 10
    assert extract_n("best movies") == 5