from python:3.5-alpine

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY . .

RUN apk add --update build-base && \
 apk add --update postgresql-dev && \
 pip install -r requirements.txt