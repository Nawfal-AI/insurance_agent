# Architecture

## System diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                           │
│  Streamlit UI (port 8501)   │   REST client / curl          │
└──────────────┬──────────────┴───────────────────────────────┘
               │ HTTP POST /ask
┌──────────────▼──────────────────────────────────────────────┐
│                  API LAYER  (FastAPI, port 8080)             │
│  /health  /metrics  /ask                                     │
│  LoggingMiddleware → structured JSON → CloudWatch Logs       │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│               AGENT LAYER  (LangGraph ReAct)                 │
│                                                              │
│  Question → LLM decides which tool to call → observes result │
│           → repeats until ready to answer                    │
│                                                              │
│  Tools:                                                      │
│    search_policy_documents  ──► FAISS vector store           │
│    calculate                    (MiniLM-L6 embeddings)       │
│    lookup_term              ──► in-memory glossary           │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│                   LLM LAYER                                  │
│  Provider-agnostic (Anthropic / OpenAI / Groq / Ollama)      │
│  Configured via LLM_PROVIDER env var                         │
└─────────────────────────────────────────────────────────────┘

INFRASTRUCTURE (AWS)
  ECS Fargate task  ──  ECR image registry
  Secrets Manager   ──  API keys
  CloudWatch Logs   ──  structured JSON logs
  GitHub Actions    ──  CI/CD (lint → test → build → deploy)
```

## Data flow for a single query

```
1. User types: "What is my deductible if I file 3 claims this year?"
2. FastAPI /ask receives the question
3. LoggingMiddleware starts the latency clock
4. LangGraph agent sends question + system prompt to LLM
5. LLM decides: call search_policy_documents("deductible multiple claims")
6. FAISS returns top-3 matching policy clauses
7. LLM reads clauses, decides: call calculate("500 + 500")  (deductible increase)
8. LLM formulates answer citing policy section IDs
9. FastAPI returns {answer, tool_calls} as JSON
10. Latency logged to CloudWatch; response time in X-Latency-Ms header
```

## Key design decisions

| Decision | Rationale |
|---|---|
| FAISS (not OpenSearch) | Zero infrastructure overhead for phase 1; swap path documented |
| Sentence Transformers (not OpenAI embeddings) | No per-query embedding cost; runs on CPU |
| LangGraph ReAct | Transparent tool-call trace; easier to audit than a chain |
| Stateless API | Simplifies deployment; history passed by client |
| Structured JSON logs | CloudWatch Logs Insights queries work without a parser |

## Swap guide for production scale-up

| Component | Development | Production (high load) |
|---|---|---|
| Vector store | FAISS (in-memory) | AWS OpenSearch Serverless |
| Embeddings | sentence-transformers (CPU) | AWS Bedrock Titan Embeddings |
| Secrets | `.env` file | AWS Secrets Manager |
| Logging | stdout JSON | CloudWatch Logs + Insights |
| Deployment | `uvicorn` direct | ECS Fargate behind ALB |
