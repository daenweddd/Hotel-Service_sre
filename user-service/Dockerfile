FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV SERVICE_NAME=user-profile-service
ENV SERVICE_PORT=5007

EXPOSE 5007

CMD ["python", "app.py"]