
FROM python:3.9-slim

RUN mkdir -p /opt/app

COPY requirements.txt /opt/app/requirements.txt

RUN pip install --no-cache-dir -r /opt/app/requirements.txt

COPY manus /opt/app/manus

EXPOSE 5000
WORKDIR /app
