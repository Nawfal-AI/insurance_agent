"""
Tools the agent can call. Each is a LangChain @tool — the agent decides
when and how to invoke these based on the user's question, not a fixed
if/else script. That decision-making loop is the actual "agent" part;
see agent.py for where it happens.
"""
import re

from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from documents import POLICY_DOCUMENTS

# --- RAG retrieval tool -----------------------------------------------------
# Built once at import time; reused across requests rather than rebuilt per call.
_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
_docs = [
    Document(
        # The title is embedded together with the body so that queries
        # naming a specific coverage (e.g. "Standard Liability Coverage")
        # actually match on those words. Previously only the body text was
        # embedded, and several clause bodies never mention their own
        # coverage name — e.g. the Standard Liability exclusions clause
        # never says "liability" — so it lost to other clauses whose body
        # happened to share more vocabulary with the query.
        page_content=f"{d['title']}: {d['text']}",
        metadata={"id": d["id"], "title": d["title"], "body": d["text"]},
    )
    for d in POLICY_DOCUMENTS
]
_vectorstore = FAISS.from_documents(_docs, _embeddings)


@tool
def search_policy_documents(query: str) -> str:
    """Search the insurance policy documents for clauses relevant to a question.
    Use this whenever the user asks about coverage, exclusions, claims process,
    premiums, or dispute resolution. Returns the most relevant clause(s) with
    their source section, so answers can be grounded and cited."""
    results = _vectorstore.similarity_search(query, k=3)
    if not results:
        return "No relevant policy clauses found."
    return "\n\n".join(
        f"[{r.metadata['title']} ({r.metadata['id']})]\n{r.metadata['body']}" for r in results
    )


# --- Calculator tool ---------------------------------------------------------
@tool
def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. for computing claim amounts
    after a deductible, or premium totals. Only supports +, -, *, /, and
    parentheses on numbers — not a general code execution tool."""
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expression):
        return "Error: expression contains disallowed characters. Only numbers and + - * / ( ) are permitted."
    try:
        # Safe by construction: the regex above already rejected anything
        # that isn't a number, whitespace, or one of + - * / ( ).
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


# --- Glossary tool -------------------------------------------------------
_GLOSSARY = {
    "deductible": "The amount the policyholder pays out of pocket before the insurer covers the remaining cost of a claim.",
    "exclusion": "A specific condition or circumstance explicitly not covered by the policy.",
    "arbitration": "A dispute-resolution process outside of court, where a neutral third party makes a binding decision.",
    "premium": "The amount the policyholder pays (typically periodically) to maintain active coverage.",
}


@tool
def lookup_term(term: str) -> str:
    """Look up the definition of an insurance/legal term (e.g. 'deductible',
    'exclusion', 'arbitration', 'premium'). Use this when the user's question
    uses jargon that should be clarified before answering."""
    key = term.strip().lower()
    if key in _GLOSSARY:
        return _GLOSSARY[key]
    return f"'{term}' is not in the glossary. Known terms: {', '.join(_GLOSSARY.keys())}"


ALL_TOOLS = [search_policy_documents, calculate, lookup_term]
