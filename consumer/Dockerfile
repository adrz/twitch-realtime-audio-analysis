#FROM frolvlad/alpine-python3:latest
FROM python:3.8-alpine
WORKDIR /app
COPY requirements.txt main.py ./
COPY src src

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    mkdir audios && \
    mkdir audios/voice && \
    mkdir audios/novoice
