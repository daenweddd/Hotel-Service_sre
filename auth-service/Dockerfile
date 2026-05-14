FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV SERVICE_NAME=auth-service
ENV SERVICE_PORT=5001

EXPOSE 5001

CMD ["python", "app.py"]