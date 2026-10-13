from fastapi.testclient import TestClient

from app import rag
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["chunks"] > 0


def test_chat_returns_reply_and_sources():
    resp = client.post("/chat", json={"message": "How do I reset my password?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"]
    assert "it-security-policy.md" in body["sources"]


def test_retriever_can_reach_internal_docs():
    # Baseline weakness on purpose: internal-only docs are retrievable.
    hits = rag.retrieve("break-glass admin account", rag.load_chunks())
    assert any(h.source.startswith("internal/") for h in hits)
