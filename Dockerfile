# --------------------------
# Docker file
# --------------------------
FROM python:3.6.5

# -- Install dependencies
RUN pip3 install --upgrade pipenv

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Application
RUN mkdir /app
WORKDIR /app
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN set -ex && pipenv install --deploy --system

