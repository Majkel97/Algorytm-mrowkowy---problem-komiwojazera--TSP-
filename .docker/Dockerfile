# syntax=docker/dockerfile:1
FROM python:3
EXPOSE 8000
WORKDIR /code
COPY .docker/requirements.txt /code/
RUN pip install -r requirements.txt
COPY .. /code/