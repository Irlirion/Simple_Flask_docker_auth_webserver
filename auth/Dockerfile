# pull official base image
FROM python:3.8.3-alpine as Base

RUN mkdir -p /usr/src
WORKDIR /usr/src

FROM Base as Installer

# Configurations.
ENV MEMCACHED_MEMORY 128
ENV MEMCACHED_MAX_CONNECTIONS 1024
ENV MEMCACHED_MAX_ITEM_SIZE 4M

RUN \
    apk add --no-cache libffi-dev postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libxslt-dev memcached libmemcached-dev && rm -rf /var/cache/apk/*



COPY requirements.txt /usr/src

RUN pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

FROM Installer as App

ADD ./server /usr/src/server
ADD ./migrations /usr/src/migrations

COPY app.py /usr/src
EXPOSE 5050