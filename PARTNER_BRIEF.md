# Partner Brief — Swiss Cantonal Insurance Office (KVG/LAMal Q&A Assistant)

**Project reference:** SDSC-INS-2026-001  
**Partner type:** Public sector — cantonal administration  
**Domain:** Swiss public health insurance (KVG / LAMal)  
**Status:** Prototype → Production

---

## Partner context

A Swiss cantonal insurance office handles thousands of policyholder enquiries
per year about coverage, deductibles, claim processes, and disputes under the
Swiss Federal Health Insurance Act (KVG / LAMal). Currently, caseworkers look
up answers manually in long policy PDFs, leading to inconsistent answers and
high handling time.

The office wanted a tool that would let any caseworker — regardless of
technical background — query policy documents in plain language (German,
French, or English) and receive a grounded, citable answer within seconds.

---

## Problem definition (from stakeholder workshops)

| Pain point | Impact |
|---|---|
| Caseworkers spend 5–10 min per query on manual PDF search | High handling time, inconsistent answers |
| New staff take weeks to learn policy document structure | Slow onboarding |
| Answers not always cited to source clause | Auditability risk under FINMA/BAG oversight |

---

## Production requirements (defined jointly with partner)

| Requirement | Target |
|---|---|
| Response latency | < 2 000 ms (p95) |
| Uptime | 99 % monthly |
| Answer grounding | Every factual claim must cite a policy section |
| Data residency | EU / Switzerland (AWS eu-central-1 Frankfurt) |
| GDPR compliance | No PII stored; query logs anonymised after 30 days |
| Languages | German, French, English |
| Audience | Non-technical caseworkers — no ML knowledge assumed |

---

## Solution architecture

```
Caseworker (browser / Streamlit UI)
        │
        ▼
  FastAPI (AWS ECS Fargate, eu-central-1)
        │
        ├── FAISS vector store (policy clause embeddings, built at startup)
        │        └── sentence-transformers/all-MiniLM-L6-v2
        │
        ├── LangGraph ReAct agent
        │        ├── search_policy_documents (RAG retrieval)
        │        ├── calculate (arithmetic for claim amounts)
        │        └── lookup_term (insurance glossary)
        │
        └── LLM (Claude via Anthropic API — eu-data-residency endpoint)

Logging → AWS CloudWatch Logs (structured JSON, 30-day retention)
Secrets → AWS Secrets Manager (API keys — never in code or env files)
CI/CD   → GitHub Actions → ECR → ECS rolling deploy
```

---

## Industrialization decisions

**Prototype → production changes made:**
- Added structured JSON logging → CloudWatch for auditability
- Added `/health` endpoint for ECS health checks
- Added `/metrics` endpoint for latency monitoring
- API keys moved from `.env` to AWS Secrets Manager
- CORS configured for Streamlit frontend
- Dockerfile hardened with health check and non-root user
- CI/CD pipeline: lint → test → build → push ECR → deploy ECS

**What was deliberately not built in phase 1:**
- Authentication (caseworkers use internal SSO — to be added in phase 2)
- Persistent conversation storage (stateless for simplicity; phase 2 scope)
- Fine-tuning on domain data (retrieval quality meets requirements without it)

---

## Non-technical summary (for partner stakeholders)

> The assistant works like a knowledgeable colleague who has read every page
> of the KVG/LAMal policy documents. You type your question in plain language;
> it searches the documents, finds the relevant clauses, and gives you a cited
> answer in seconds. It never guesses — if the answer isn't in the documents,
> it says so.
