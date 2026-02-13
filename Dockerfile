FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir pika

COPY chat.py .

RUN mkdir -p /app/data

CMD ["python", "-u", "chat.py"]
