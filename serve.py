"""
FastAPI service — production version.
Added vs original:
  - LoggingMiddleware: structured JSON logs → AWS CloudWatch
  - /metrics endpoint: request count + avg latency for quick dashboarding
  - /health endpoint retained (required by ECS health check)
  - CORS configured for Streamlit frontend
"""
import time
from collections import deque
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import ask
from app.api.middleware import LoggingMiddleware

app = FastAPI(title="Insurance Coverage-Check Agent — Production")

# CORS: allow the Streamlit frontend (adjust origins for your deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

STATIC_DIR = Path(__file__).parent / "static"

# Simple in-process metrics store (last 1000 requests)
_latencies: deque = deque(maxlen=1000)
_request_count = 0
_error_count = 0


class HistoryTurn(BaseModel):
    role: str
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
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    """ECS / ALB health check endpoint. Must return 200 for the task to be
    considered healthy."""
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    """Lightweight metrics endpoint — useful for a CloudWatch custom metric
    or a Grafana scrape without setting up a full Prometheus stack."""
    avg_latency = round(sum(_latencies) / len(_latencies), 1) if _latencies else 0
    return {
        "request_count": _request_count,
        "error_count": _error_count,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": sorted(_latencies)[int(len(_latencies) * 0.95)] if len(_latencies) >= 20 else None,
    }


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    global _request_count, _error_count
    _request_count += 1

    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    start = time.monotonic()
    try:
        result = ask(req.question, history=[t.model_dump() for t in req.history])
    except Exception as e:
        _error_count += 1
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
    finally:
        _latencies.append(round((time.monotonic() - start) * 1000, 1))

    return result
