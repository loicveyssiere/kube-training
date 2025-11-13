FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV REDIS_URL=redis://redis:6379/0
ENV OUTPUT_DIR=/data/output
RUN mkdir -p /data/output

CMD ["celery", "-A", "main.app", "worker", "--loglevel=info"]