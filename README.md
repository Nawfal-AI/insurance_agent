# Insurance Coverage-Check Agent

![Docker](https://img.shields.io/badge/Docker-ready-blue) ![License](https://img.shields.io/badge/license-MIT-green)

A tool-calling AI agent, built with LangGraph, that answers questions about
insurance policy coverage by retrieving and reasoning over policy
documents. Given a question, the agent decides for itself which tools to
call — document search, a calculator, or a glossary lookup — potentially
several times, before producing a grounded answer with citations back to
the specific policy section it used.

## Features

- **Real planning loop, not a scripted chatbot.** The agent decides which
  tools to call and in what order based on the question, using LangGraph's
  `create_react_agent`.
- **Grounded, cited answers.** Answers are backed by retrieved policy
  clauses rather than the model's general knowledge, and cite the specific
  section they come from.
- **Three tools:** RAG document search (FAISS + sentence-transformers),
  a constrained calculator, and a glossary lookup for insurance jargon.
- **Multi-provider LLM support:** Groq, Google Gemini, Ollama, Anthropic,
  or OpenAI — configurable via a single environment variable.
- **Web UI** with a live chat thread and a "Grounding Ledger" panel that
  shows each tool call and its result as the agent works.
- **A captured, real example run** ([`results/example_run.json`](results/example_run.json))
  showing the agent independently choosing to call `calculate` once,
  `search_policy_documents` twice, and `lookup_term` once for a single
  question — genuine model output, not a fabricated transcript.

## Architecture

```
documents.py               # Synthetic policy documents
tools.py                    # search_policy_documents (RAG), calculate, lookup_term
agent.py                    # Agent loop (LangGraph create_react_agent) and
                             # multi-turn conversation handling
serve.py                     # FastAPI app: POST /ask, serves the web UI
static/index.html            # Chat UI with the live Grounding Ledger
test_tools.py                 # Tool tests that don't require an LLM API key
results/example_run.json      # A real, captured agent run
NOTES.md                      # Engineering notes and debugging history
Dockerfile                    # For local Docker and Cloud Run deployment
```

## Getting started

### Prerequisites

- Python 3.12+
- An API key for at least one supported LLM provider (Groq's free tier is
  recommended — see below)

### Installation

```bash
git clone https://github.com/Nawfal-AI/insurance_agent.git
cd insurance_agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env` with your provider of choice. Groq is the default and
recommended option — no credit card required, 14,400 requests/day free tier:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your-key-here    # https://console.groq.com → API Keys
GROQ_MODEL=llama-3.1-8b-instant
```

`.env.example` documents Gemini, Ollama, Anthropic, and OpenAI as
alternative providers, each with setup notes.

### Running

```bash
pytest test_tools.py -v          # tool logic, no API key needed
python3 -m uvicorn serve:app --reload
```

Then open **http://localhost:8000** for the web UI, or call the API directly:

```bash
curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "If my deductible is 500 and my claim is 1200, how much will I be reimbursed, and does my policy cover late-filed claims?"}'
```

The response includes a `tool_calls` field showing exactly which tools the
agent used and what each one returned.

## Deployment

The included `Dockerfile` is ready for containerized deployment on any
platform that runs a Docker image (Cloud Run, ECS, Fly.io, etc.). Local
verification:

```bash
docker build -t insurance-agent .
docker run -p 8000:8000 --env-file .env insurance-agent
```

### Deploying to Google Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Store the API key as a secret rather than baking it into the image
echo -n "your-groq-api-key" | gcloud secrets create groq-api-key --data-file=-

# Deploy directly from source
gcloud run deploy insurance-agent \
  --source . \
  --region europe-west6 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=groq,GROQ_MODEL=llama-3.1-8b-instant \
  --set-secrets GROQ_API_KEY=groq-api-key:latest
```

Check current pricing at https://cloud.google.com/run/pricing before
leaving a deployment running.

## Scope and limitations

<<<<<<< HEAD
This is a working prototype demonstrating an agentic AI system and its
deployment path, not a production insurance tool:

- **Synthetic data.** The policy documents in `documents.py` are invented
  for this demo — not real insurance policy language.
- **No authentication, rate limiting, or monitoring.** Suitable for local
  use or a demo deployment, not for handling real user traffic or data.
- **No persistent storage.** Conversation history is kept client-side for
  the duration of a browser session only.

See [`NOTES.md`](NOTES.md) for detailed engineering notes, including real
issues encountered during development and how they were resolved.

## License

MIT — see [`LICENSE`](LICENSE).
=======
>>>>>>> c162d8043e2fa5006a8100f8d3586a690ed07af0
