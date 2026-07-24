# Insurance Coverage-Check Agent

A tool-calling AI agent (LangChain, planning/tool-use loop) that answers
questions about insurance policy coverage by retrieving and reasoning over
policy documents — built to demonstrate agentic AI and cloud deployment,
the two gaps identified against AI/LLM engineering job listings.

## What this is (and isn't)

- **Real agent loop, synthetic domain data.** The agent's planning/tool-calling
  behavior is real — the LLM genuinely decides which tool(s) to call and in
  what order. The policy documents it searches over (`documents.py`) are
  invented text for demo purposes, not real insurance policies.
- **Not verified end-to-end by me.** I don't have API keys or a package
  index available in the environment I built this in, so I hand-verified
  the tool logic in isolation (calculator injection-safety, glossary
  lookup) but could not run the full agent loop against a real LLM. **You
  need to actually run this yourself before claiming it works** — treat
  the first real run as part of the build, not a formality.

## Architecture

```
documents.py   # Synthetic policy documents
tools.py       # 3 tools: RAG retrieval (FAISS + sentence-transformers),
               # calculator, glossary lookup
agent.py       # The actual agent loop (LangChain create_tool_calling_agent
               # + AgentExecutor) — this is the "planning/tool-calling" part
serve.py       # FastAPI wrapper: POST /ask
test_tools.py  # Tests for tools that don't require an LLM API key
Dockerfile     # For local Docker + Cloud Run deployment
```

## How to run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: add your ANTHROPIC_API_KEY (or switch LLM_PROVIDER=openai + OPENAI_API_KEY)
export $(cat .env | xargs)

pytest test_tools.py -v          # tool logic, no API key needed
python3 -m uvicorn serve:app --reload
```

Then in another terminal:
```bash
curl -X POST localhost:8080/ask -H "Content-Type: application/json" \
  -d '{"question": "If my deductible is 500 and my claim is 1200, how much will I be reimbursed, and does my policy cover late-filed claims?"}'
```
A good response should show **two tool calls** in `tool_calls` — one to
`search_policy_documents` (for the late-filing question) and one to
`calculate` (for 1200 - 500) — because the agent decided it needed both,
not because the code hardcodes that sequence. That's the actual thing to
verify: that the loop is really deciding, not just executing a script.

## Deploying to Google Cloud Run (the cloud-platform piece)

Cloud Run is a good first cloud deployment target: serverless (no server to
manage), scales to zero (near-free for low traffic), and deploys straight
from a Dockerfile — reusing the Docker skill from your other project.

**1. Install the gcloud CLI** (if not already installed):
```bash
# macOS
brew install --cask google-cloud-sdk
```

**2. Create a free GCP account and project** at https://console.cloud.google.com
if you don't have one — new accounts get free trial credit, and Cloud Run
itself has a permanent free tier (2 million requests/month).

**3. Authenticate and set your project:**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**4. Store your API key as a secret** (don't bake it into the image):
```bash
echo -n "your-anthropic-api-key" | gcloud secrets create anthropic-api-key --data-file=-
```

**5. Deploy directly from source** (gcloud builds the Dockerfile for you):
```bash
gcloud run deploy insurance-agent \
  --source . \
  --region europe-west6 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=anthropic \
  --set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest
```
(`europe-west6` is Zurich — pick whatever region makes sense for you.)

**6. Test the deployed service:**
```bash
curl -X POST https://YOUR-SERVICE-URL/ask -H "Content-Type: application/json" \
  -d '{"question": "What is the annual premium and how often is it paid?"}'
```

**7. Check costs.** Cloud Run's free tier is generous, but confirm your
actual usage against current pricing at https://cloud.google.com/run/pricing
before leaving it running — don't assume "free tier" means "definitely
free" without checking your own usage.

## What to say about this in an interview

Be specific and honest: "I built a tool-calling agent with LangChain over
a RAG retrieval tool, a calculator, and a glossary — the agent decides
which tools to call based on the question, not a fixed script — and
deployed it to Cloud Run." If asked to go deeper: be ready to explain what
`AgentExecutor` actually does step by step (call LLM → get tool call →
execute tool → feed result back to LLM → repeat until final answer), since
that's the mechanism a framework abstracts away and interviewers may probe
whether you understand what's underneath it.
