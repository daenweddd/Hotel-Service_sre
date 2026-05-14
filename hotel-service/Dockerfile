FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV SERVICE_NAME=hotel-service
ENV SERVICE_PORT=5002

EXPOSE 5002

CMD ["python", "app.py"]