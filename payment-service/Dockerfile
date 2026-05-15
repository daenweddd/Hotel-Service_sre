FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV SERVICE_NAME=payment-service
ENV SERVICE_PORT=5005

EXPOSE 5005

CMD ["python", "app.py"]