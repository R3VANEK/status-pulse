FROM python:3.13-slim

RUN mkdir /app

WORKDIR /app

COPY ./build/entrypoint.sh /entrypoint.sh

COPY ./build/requirements-dev.txt /app/

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install -r requirements-dev.txt

COPY ./app/ /app/

ENTRYPOINT ["/entrypoint.sh"]
