FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY README.md ./

RUN pip install --no-cache-dir .

EXPOSE 8000
ENV MAILVERT_LOG_JSON=true

CMD ["uvicorn", "mailvert.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
