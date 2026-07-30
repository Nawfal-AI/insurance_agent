# Insurance Coverage-Check Agent

![Docker](https://img.shields.io/badge/Docker-ready-blue) ![License](https://img.shields.io/badge/license-MIT-green)

A tool-calling AI agent (LangGraph, planning/tool-use loop) that answers
questions about insurance policy coverage by retrieving and reasoning over
policy documents — built to demonstrate agentic AI and cloud deployment.

## Verified, not just written

Unlike a project that only compiles, this has a real, captured example of
the agent actually working end-to-end: **[`results/example_run.json`](results/example_run.json)**
is genuine output from a live run against the Gemini API. The agent
independently chose to call `calculate` once, `search_policy_documents`
twice (rewording its query rather than accepting the first result), and
`lookup_term` once — that sequence was not hardcoded; it's the model
deciding. (This transcript was captured while Gemini was the active
provider; the project has since moved to Groq as the default — see
`LLM_PROVIDER` below — but the agent loop and tool-calling logic it
demonstrates are unchanged.)

## What this is (and isn't)

- **Real agent loop, synthetic domain data.** The agent's planning/tool-calling
  behavior is real and verified. The policy documents it searches over
  (`documents.py`) are invented text for demo purposes, not real insurance
  policies.
- **A working prototype, not production software.** No auth, no rate
  limiting, no monitoring, synthetic data. Say that plainly if asked.
- **A genuinely messy build.** This project surfaced more real breakage
  than any other in this portfolio — a LangChain 1.0 API removal, three
  Gemini model deprecations in a row, and a response-format mismatch. All
  of it is documented honestly in [`NOTES.md`](NOTES.md), including a
  retrieval-efficiency question I noticed but haven't fully resolved.

## Architecture

```
documents.py         # Synthetic policy documents
tools.py              # 3 tools: RAG retrieval (FAISS + sentence-transformers),
                       # calculator, glossary lookup
agent.py              # The agent loop (LangGraph create_react_agent) — the
                       # actual "planning/tool-calling" part; also handles
                       # multi-turn conversation history
serve.py               # FastAPI wrapper: POST /ask (accepts a `history` field
                        # for multi-turn conversations)
static/index.html      # Web UI — chat thread + live "Grounding Ledger"
test_tools.py           # Tests for tools that don't require an LLM API key
results/example_run.json  # A real, captured run — not fabricated
NOTES.md               # Honest engineering notes: what broke, what I'd change
Dockerfile              # For local Docker + Cloud Run deployment
```

## How to run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env — recommended free option:
#   LLM_PROVIDER=groq
#   GROQ_API_KEY=your-key-here   (get one free at https://console.groq.com,
#                                  no credit card required — 14,400 req/day)
#   GROQ_MODEL=llama-3.1-8b-instant
# (.env.example also documents Gemini, Ollama, Anthropic, and OpenAI as
# alternative providers, each with its own trade-offs noted inline.)

pytest test_tools.py -v          # tool logic, no API key needed
python3 -m uvicorn serve:app --reload
```
`.env` is loaded automatically via `python-dotenv` — no manual shell export needed.

Then in another terminal:
```bash
curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "If my deductible is 500 and my claim is 1200, how much will I be reimbursed, and does my policy cover late-filed claims?"}'
```
Check the `tool_calls` field in the response — you should see the agent
independently choosing which tools to use, the same way it did in
`results/example_run.json`.

## Deploying to Google Cloud Run (the cloud-platform piece)

Cloud Run is a good first cloud deployment target: serverless (no server to
manage), scales to zero (near-free for low traffic), and deploys straight
from a Dockerfile.

**1. Install the gcloud CLI**
```bash
brew install --cask google-cloud-sdk
```

**2. Create a free GCP account/project** at https://console.cloud.google.com

**3. Authenticate**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**4. Store your API key as a secret** (don't bake it into the image)
```bash
echo -n "your-groq-api-key" | gcloud secrets create groq-api-key --data-file=-
```

**5. Deploy directly from source**
```bash
gcloud run deploy insurance-agent \
  --source . \
  --region europe-west6 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=groq,GROQ_MODEL=llama-3.1-8b-instant \
  --set-secrets GROQ_API_KEY=groq-api-key:latest
```

**6. Test the deployed service**
```bash
curl -X POST https://YOUR-SERVICE-URL/ask -H "Content-Type: application/json" \
  -d '{"question": "What is the annual premium and how often is it paid?"}'
```

**7. Check costs** against current pricing at https://cloud.google.com/run/pricing
before leaving it running.

