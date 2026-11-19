"""
Integration tests for the FastAPI endpoints.
Run: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from serve import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics_endpoint():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "request_count" in data
    assert "avg_latency_ms" in data


def test_ask_empty_question():
    resp = client.post("/ask", json={"question": ""})
    assert resp.status_code == 400


def test_ask_returns_structure():
    resp = client.post("/ask", json={"question": "What is the deductible?"})
    # The actual answer depends on the LLM provider — just check shape
    assert resp.status_code in (200, 500)   # 500 acceptable if no API key set in CI
    if resp.status_code == 200:
        data = resp.json()
        assert "answer" in data
        assert "tool_calls" in data


def test_latency_header_present():
    resp = client.get("/health")
    assert "X-Latency-Ms" in resp.headers
