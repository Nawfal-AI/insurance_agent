"""FastAPI service exposing the agent. Same serving pattern as your
manipulation-policy-pipeline project: health check, structured request/
response models, errors returned as proper HTTP status codes."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import ask

app = FastAPI(title="Insurance Coverage-Check Agent")


class AskRequest(BaseModel):
    question: str


class ToolCall(BaseModel):
    tool: str
    tool_input: dict | str
    observation: str


class AskResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    try:
        result = ask(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
    return result
