# insurance_agent

**A ReAct-style AI agent that answers natural-language questions about insurance policy documents, combining retrieval-augmented generation, tool-calling, and a FastAPI backend into one runnable system.**

The insurance domain is a stand-in. The same architecture applies to any corpus of structured documents (legal contracts, medical guidelines, HR policies, technical manuals) where answers must be grounded in source material rather than generated from memory.

---

## What makes this an agent, not just a chatbot

Most LLM integrations follow a fixed pipeline: retrieve context, then generate an answer. This project uses a **ReAct loop** (Reason, Act, Observe, Repeat):

1. The LLM reads the question and decides what to do next.
2. It issues a tool call: search documents, calculate a figure, or look up a term.
3. It observes the result and decides whether it has enough information.
4. If not, it calls another tool, possibly with a rephrased query.
5. Only when it has sufficient grounded evidence does it produce a final answer.

This means the agent can handle multi-part questions, retry failed retrievals, chain a document lookup into a calculation, and explain its reasoning without any of that logic being hardcoded.

---

## Features

- **RAG pipeline** -- policy clauses embedded with `sentence-transformers`, stored in a FAISS vector store, retrieved at query time with semantic similarity search
- **Real tool-calling loop** -- the LangGraph agent autonomously decides when to call each tool based on what it finds, not a fixed script
- **Multi-provider LLM support** -- swap between Anthropic, OpenAI, Google Gemini, Groq, or a local Ollama model by changing one environment variable; no code changes needed
- **Transparent reasoning** -- the `/ask` endpoint returns the final answer plus a full trace of every tool call made, so the agent's reasoning loop is visible
- **Conversation history** -- prior turns are passed as context, so follow-up questions work correctly
- **Docker-first** -- one `docker compose up --build` runs everything

---

## How it works

```
User question (via UI or API)
        |
        v
  FastAPI /ask endpoint
        |
        v
  LangGraph ReAct Agent
     |        |        |
     v        v        v
  search_   calcu-   lookup_
  policy_   late()   term()
  docs()
  (FAISS    (safe    (glossary
  vector    eval)    dict)
  store)
     |
     v
  HuggingFace sentence-transformer embeddings
  -> top-k clause retrieval
        |
        v
  LLM synthesises grounded answer
  (cites policy section + tool trace)
        |
        v
  JSON response: { answer, tool_calls[] }
```

The agent loop is real. The verified example in `results/example_run.json` shows the agent calling `search_policy_documents` twice (rewording the query on the second attempt), `calculate` once, and `lookup_term` once -- a sequence it chose itself, not one that was scripted.

---

## Available tools

| Tool | What it does | When the agent calls it |
|---|---|---|
| `search_policy_documents` | Semantic search over embedded policy clauses; returns matching sections with their titles | Any question about coverage, exclusions, claims, or policy terms |
| `calculate` | Evaluates an arithmetic expression with a strict allowlist -- no arbitrary code execution | Whenever a numeric result is needed (claim reimbursement, premium totals) |
| `lookup_term` | Returns plain-language definitions for insurance and legal jargon | When the question contains terms like deductible, exclusion, arbitration, or premium |

The agent is prompted to never invent numbers. Every figure it passes to `calculate` must have come from a prior `search_policy_documents` call in the same conversation.

---

## Quick start

Prerequisites: Docker and Docker Compose. No local Python installation needed.

```bash
git clone https://github.com/Nawfal-AI/insurance_agent
cd insurance_agent
cp .env.example .env        # add your API key (see provider table below)
docker compose up --build
# open http://localhost:8000
```

Without Docker:

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn serve:app --reload --port 8000
```

---

## Choosing an LLM provider

Set `LLM_PROVIDER` in `.env`. The agent code is identical regardless of provider.

| Provider | Cost | Notes |
|---|---|---|
| Groq (recommended) | Free tier, 14,400 req/day | Highest free-tier limit; best starting point. No credit card required. |
| Google Gemini | Free tier, 20 req/day | Low request limit. Use `gemini-flash-latest` as the model name -- Google retires versioned names frequently. |
| Ollama | Free, fully local | No API key or internet needed at inference time. Requires a capable machine. |
| Anthropic | Small trial credit, then paid | Not a persistent free tier. |
| OpenAI | Paid only | No free tier. |

---

## Adapting to your own documents

The domain is intentionally generic. To use this against a different corpus:

1. Replace `documents.py` -- populate `POLICY_DOCUMENTS` with your own content. Each entry needs an `id`, `title`, and `text`. The vector store is built from these at startup.
2. Update the system prompt in `agent.py` -- change the persona and grounding instructions to match your domain.
3. Extend the glossary in `tools.py` -- add domain-specific terms to `_GLOSSARY`.
4. Add new tools as needed -- any Python function decorated with `@tool` and added to `ALL_TOOLS` becomes available to the agent automatically.

For larger document sets, replace the in-memory FAISS store with a persistent vector database (Chroma, Pinecone, Weaviate). The retrieval interface stays the same.

---

## Project structure

```
insurance_agent/
├── agent.py              # LangGraph ReAct agent, LLM provider switching, response parsing
├── tools.py              # Tool definitions: RAG retriever, calculator, glossary
├── documents.py          # Synthetic policy clauses (replace with real documents here)
├── serve.py              # FastAPI app -- /ask endpoint and UI serving
├── test_tools.py         # Unit tests for the three tools in isolation
├── static/
│   └── index.html        # Single-page chat UI
├── results/
│   └── example_run.json  # Verified real agent output
├── .env.example          # API key template
├── Dockerfile
└── requirements.txt
```

---

## Running tests

```bash
# With Docker:
docker compose run --rm app pytest test_tools.py -v

# Without Docker:
pytest test_tools.py -v
```

---

## Stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph `create_react_agent` |
| LLM abstraction | LangChain |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (HuggingFace) |
| Vector store | FAISS (swappable for Chroma, Pinecone, etc.) |
| API server | FastAPI + Uvicorn |
| Packaging | Docker + Docker Compose |

---

## Known limitations

- **Synthetic documents** -- `documents.py` contains invented policy clauses for demonstration purposes. The agent loop and tool-calling behavior are real and verified; the domain data is not.
- **No persistent vector store** -- the FAISS index is built in memory at startup from `documents.py`. For large or frequently updated document sets, a persistent store would be needed.
- **System prompt constraints have a ceiling** -- grounding failures required three rounds of prompt iteration to resolve. A production deployment would benefit from a post-generation verification pass rather than relying entirely on the system prompt to self-police edge cases.

`NOTES.md` contains a full record of what broke during development and how it was debugged, written as an honest engineering log.

---

## License

MIT
