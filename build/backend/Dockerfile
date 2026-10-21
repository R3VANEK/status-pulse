FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN mkdir /app

WORKDIR /app

COPY ./build/backend/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY ./build/backend/requirements-dev.txt /app/

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install -r requirements-dev.txt

COPY ./backend/ /app/

ENTRYPOINT ["/entrypoint.sh"]
