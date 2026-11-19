# Insurance Agent — Production

A production-grade LLM-powered Q&A assistant for Swiss public health insurance
(KVG / LAMal) documents. Built to demonstrate the full journey from a research
prototype to an industrialised system deployed on AWS.

## What it does

A caseworker types a question in plain language — "What is the deductible if I
file three claims this year?" — and the system searches the policy documents,
retrieves the relevant clauses, and returns a grounded, cited answer in under
two seconds.

```
Caseworker → Streamlit UI → FastAPI → LangGraph ReAct agent
                                           ├── FAISS vector search (policy docs)
                                           ├── Calculator (claim amounts)
                                           └── Glossary (insurance terms)
                                                   │
                                               Claude / GPT-4 / Llama
```

## Who it was built for

A fictitious Swiss cantonal insurance office (see [PARTNER_BRIEF.md](PARTNER_BRIEF.md))
that handles thousands of KVG/LAMal policy queries per year. The brief drove
the production requirements: 2-second latency budget, GDPR-compliant logging,
multilingual support (DE / FR / EN), and deployability in the EU (AWS Frankfurt).

## Project structure

```
insurance_agent_production/
├── agent.py                    ← ReAct agent loop (unchanged from prototype)
├── tools.py                    ← LangChain tools: search, calculate, glossary
├── documents.py                ← Policy document corpus (replace with real docs)
├── serve.py                    ← FastAPI: /health /metrics /ask + logging
├── docker-compose.yml          ← Local dev: API + Streamlit frontend
├── Dockerfile                  ← Production-hardened image
├── requirements.txt
├── app/
│   ├── api/middleware.py       ← Structured JSON logging → CloudWatch
│   └── frontend/
│       └── streamlit_app.py    ← Plain-language chat UI (non-technical users)
├── configs/
│   └── rag_v1.yaml             ← Versioned RAG config (retriever + LLM + latency budget)
├── data/corpus/                ← Policy documents (see README inside)
├── infra/aws/
│   ├── ecs_task_definition.json ← ECS Fargate task definition
│   └── cloudwatch_dashboard.json ← CloudWatch dashboard (latency + errors)
├── mlops/
│   ├── mlflow/track_experiment.py ← Experiment tracking
│   └── github-actions/ci-cd.yml   ← lint → test → ECR → ECS pipeline
├── tests/test_api.py           ← API integration tests
├── PARTNER_BRIEF.md            ← Problem statement + production requirements
├── ARCHITECTURE.md             ← System diagram + design decisions
└── DEPLOYMENT.md               ← Step-by-step: local → Docker → AWS
```

## Quickstart

```bash
cp .env.example .env     # fill in your LLM API key
pip install -r requirements.txt
uvicorn serve:app --reload --port 8080
# API: http://localhost:8080   |   Health: http://localhost:8080/health
```

With Docker (API + Streamlit frontend):
```bash
docker-compose up --build
# Frontend: http://localhost:8501
```

Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

## Production features added over the prototype

| Feature | File |
|---|---|
| Structured JSON logging → CloudWatch | `app/api/middleware.py` |
| `/metrics` endpoint (latency, error rate) | `serve.py` |
| Versioned RAG config (A/B testable) | `configs/rag_v1.yaml` |
| MLflow experiment tracking | `mlops/mlflow/track_experiment.py` |
| Streamlit frontend (non-technical users) | `app/frontend/streamlit_app.py` |
| CI/CD: lint → test → ECR → ECS | `mlops/github-actions/ci-cd.yml` |
| ECS Fargate task definition | `infra/aws/ecs_task_definition.json` |
| CloudWatch dashboard | `infra/aws/cloudwatch_dashboard.json` |
| Docker Compose for local parity | `docker-compose.yml` |
| Integration tests | `tests/test_api.py` |

## Key design decisions

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system diagram and a table
of design decisions with rationale.

## Extending to real documents

Replace `documents.py` with a PDF loader pointed at your document folder.
See [data/corpus/README.md](data/corpus/README.md) for instructions and links
to public Swiss insurance document sources.

## Running tests & linting

```bash
pytest tests/ -v
ruff check .
```
