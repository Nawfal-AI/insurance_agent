# 🛡️ insurance_agent

> **RAG + tool-calling agent over insurance policy documents, served via FastAPI**

An end-to-end AI agent that answers natural-language questions about insurance coverage by combining retrieval-augmented generation (RAG) with a real tool-calling loop like the agent can invoke a calculator and a glossary lookup mid-conversation, not just retrieve text.

---

## ✨ Features

- **RAG pipeline** — policy PDFs chunked, embedded, and stored in a vector store; retrieved at query time
- **Tool-calling loop** — LangGraph agent can call `calculate_premium()` and `lookup_term()` as real tools
- **FastAPI backend** — `/ask` endpoint with streaming support
- **HTML frontend** — single-page chat UI served from the same container
- **Fully containerised** — one `docker compose up` to run everything

---

## 🏗️ Architecture

```
User query
    │
    ▼
FastAPI /ask endpoint
    │
    ▼
LangGraph Agent ──► Tool: calculator
    │            └──► Tool: glossary lookup
    ▼
RAG retriever (vector store)
    │
    ▼
LLM (GPT / local model)
    │
    ▼
Streamed response
```

---

## 🚀 Quick start

```bash
git clone https://github.com/Nawfal-AI/insurance_agent
cd insurance_agent
cp .env.example .env        # add your OPENAI_API_KEY
docker compose up --build
# → open http://localhost:8000
```

---

## 🔧 Stack

| Layer | Technology |
|---|---|
| Agent framework | LangChain · LangGraph |
| API | FastAPI |
| Vector store | FAISS / Chroma |
| LLM | OpenAI GPT-4o / swappable |
| Packaging | Docker · docker compose |

---

## 📂 Project structure

```
insurance_agent/
├── app/
│   ├── agent.py          # LangGraph agent + tool definitions
│   ├── retriever.py      # RAG pipeline
│   ├── main.py           # FastAPI app
│   └── tools/
│       ├── calculator.py
│       └── glossary.py
├── data/                 # Synthetic policy PDFs
├── frontend/             # HTML/JS chat UI
├── tests/
├── Dockerfile
└── docker-compose.yml
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 📄 License

MIT
