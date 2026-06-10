# tests/test_api.py
from fastapi.testclient import TestClient
from cinellex_rag.api.app import app

client = TestClient(app)


def test_root_returns_ok():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "cinellex-ai"}


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["service"] == "cinellex-ai"
    # tmdb_enabled reflects whether a TMDB key is configured (False in CI);
    # assert its presence and type, not a fixed value.
    assert isinstance(body["tmdb_enabled"], bool)

def test_empty_query_rejected():
    r = client.post("/query", json={"query": ""})
    assert r.status_code == 400

def test_invalid_query_rejected():
    r = client.post("/query", json={"query": "xyz"})
    assert r.status_code == 400