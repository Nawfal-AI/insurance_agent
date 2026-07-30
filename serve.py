"""FastAPI service exposing the agent. Same serving pattern as your
manipulation-policy-pipeline project: health check, structured request/
response models, errors returned as proper HTTP status codes."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import ask

app = FastAPI(title="Insurance Coverage-Check Agent")

STATIC_DIR = Path(__file__).parent / "static"


class HistoryTurn(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class AskRequest(BaseModel):
    question: str
    history: list[HistoryTurn] = []


class ToolCall(BaseModel):
    tool: str
    tool_input: dict | str
    observation: str


class AskResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]


@app.get("/")
def ui():
    """Serves the web UI. If you're looking at this in a browser, this is
    the whole point of the file — a human-usable front end over /ask."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    try:
        result = ask(req.question, history=[t.model_dump() for t in req.history])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
    return result
