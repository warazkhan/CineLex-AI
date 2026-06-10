# tests/test_api.py
from fastapi.testclient import TestClient
from cinellex_rag.api.app import app

client = TestClient(app)


def test_root_returns_ok():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "cinellex-ai"}


def test_health():
    assert client.get("/health").json() == {"status": "ok", "service": "cinellex-ai"}

def test_empty_query_rejected():
    r = client.post("/query", json={"query": ""})
    assert r.status_code == 400

def test_invalid_query_rejected():
    r = client.post("/query", json={"query": "xyz"})
    assert r.status_code == 400