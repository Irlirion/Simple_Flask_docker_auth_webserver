# pull official base image
FROM python:3.8.3-alpine as Base

RUN mkdir -p /usr/src
WORKDIR /usr/src

FROM Base as Installer

RUN \
    apk add --no-cache libffi-dev postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libxslt-dev

COPY requirements.txt /usr/src

RUN pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

FROM Installer as App

ADD ./resources /usr/src/resources

COPY app.py /usr/src
EXPOSE 5000