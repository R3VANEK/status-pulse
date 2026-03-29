FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./build/requirements.in /app/
COPY ./build/requirements-dev.in /app/

RUN pip install --upgrade pip && \
    pip install pip-tools && \
    pip-compile requirements.in && \
    pip-compile requirements-dev.in && \
    pip install --no-cache-dir -r requirements-dev.txt

COPY ./app/ /app/

COPY ./build/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
