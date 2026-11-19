FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer — only rebuilds when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY documents.py tools.py agent.py serve.py ./
COPY app/ ./app/
COPY configs/ ./configs/
COPY static/ ./static/

ENV PYTHONUNBUFFERED=1
# AWS ECS injects $PORT at runtime; default to 8080
ENV PORT=8080
EXPOSE 8080

# Health check so ECS marks the task unhealthy before the ALB does
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

CMD ["sh", "-c", "uvicorn serve:app --host 0.0.0.0 --port ${PORT}"]
