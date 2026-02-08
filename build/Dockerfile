FROM python:3.13-slim

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./app/ /app/

EXPOSE 8000