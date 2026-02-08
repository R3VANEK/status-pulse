FROM python:3.13-slim

RUN mkdir /app

WORKDIR /app

COPY ./build/requirements.dev.txt /app/
COPY ./build/requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.dev.txt

COPY ./app/ /app/
