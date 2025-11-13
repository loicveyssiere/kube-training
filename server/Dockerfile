FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV REDIS_URL=redis://redis:6379/0
ENV UPLOAD_DIR=/data/uploads
ENV OUTPUT_DIR=/data/output

RUN mkdir -p /data/uploads /data/output

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]