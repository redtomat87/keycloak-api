FROM python:3.12-alpine3.21 AS builder

WORKDIR /app

RUN apk add --no-cache curl build-base

RUN pip install -U pip poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

FROM python:3.12-alpine3.21
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY src/ ./src/

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "src/kc_certificates.py"]
