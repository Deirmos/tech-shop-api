FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN set -eux; \
    for i in 1 2 3; do apt-get update && break || sleep 5; done; \
    apt-get install -y --no-install-recommends build-essential libpq-dev; \
    rm -rf /var/lib/apt/lists/*

ARG INSTALL_DEV=false

COPY requirements.txt /app/requirements.txt
COPY requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && if [ "$INSTALL_DEV" = "true" ]; then pip install --no-cache-dir -r /app/requirements-dev.txt; fi

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
