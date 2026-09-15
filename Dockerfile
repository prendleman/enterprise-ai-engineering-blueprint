FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
COPY dashboard ./dashboard
COPY scripts ./scripts
COPY docs ./docs

RUN pip install --no-cache-dir .

ENV AI_PROVIDER=mock
ENV DATABASE_PATH=/app/data/telemetry.duckdb
EXPOSE 8000 8501

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
