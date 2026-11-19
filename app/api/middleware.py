"""
Logging & latency middleware.
Emits structured JSON logs compatible with AWS CloudWatch Logs Insights.
Every request gets a latency measurement and a unique request_id so you
can trace a slow or failed request end-to-end in CloudWatch.
"""
import json
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("insurance_agent")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.monotonic()

        response = await call_next(request)

        latency_ms = round((time.monotonic() - start) * 1000, 1)

        log_record = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        }
        logger.info(json.dumps(log_record))

        # Surface request_id in response header so it can be correlated
        # with the CloudWatch log line when debugging a specific call.
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Latency-Ms"] = str(latency_ms)
        return response
