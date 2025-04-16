FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 

WORKDIR /code

COPY requirements.txt /code/

RUN apk update --no-cache \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir psycopg2-binary  \
    && pip install --no-cache-dir -r requirements.txt \
    && apk add --no-cache libpq \
    && apk add --no-cache \
    build-base cairo-dev cairo cairo-tools 
    
COPY . /code/
