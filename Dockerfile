FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y mc && rm -rf /var/cache/apk/*

RUN pip --no-cache-dir install redial22
