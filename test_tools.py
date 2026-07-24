"""
Tests for the tools themselves, which don't need an LLM API key. Testing
the full agent loop end-to-end would require a real API call — worth doing
manually before deploying, but not something to hardcode into automated
tests that run without credentials (e.g. in CI).
"""
from tools import calculate, lookup_term, search_policy_documents


def test_calculate_basic():
    assert calculate.invoke("500 - 250") == "250"


def test_calculate_rejects_non_arithmetic():
    result = calculate.invoke("__import__('os').system('echo hi')")
    assert "disallowed characters" in result


def test_lookup_term_known():
    result = lookup_term.invoke("deductible")
    assert "out of pocket" in result


def test_lookup_term_unknown():
    result = lookup_term.invoke("frobnicate")
    assert "not in the glossary" in result


def test_search_policy_documents_returns_relevant_clause():
    result = search_policy_documents.invoke("what happens if I file a claim late")
    assert "policy_003_claim_process" in result or "30 days" in result
