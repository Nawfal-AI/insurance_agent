FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY documents.py tools.py agent.py serve.py ./

ENV PYTHONUNBUFFERED=1
# Cloud Run injects $PORT at runtime; default to 8080 (Cloud Run's convention) for local use.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn serve:app --host 0.0.0.0 --port ${PORT}"]
