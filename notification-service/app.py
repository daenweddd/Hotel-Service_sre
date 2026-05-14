from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time

SERVICE_NAME = os.getenv("SERVICE_NAME", "notification-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5006"))

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["endpoint", "method", "status"]
)

ERROR_COUNT = Counter(
    "service_errors_total",
    "Total service errors",
    ["service", "error_type"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"]
)

notifications = []

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    endpoint = request.path
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    return response

@app.route("/health", methods=["GET"])
def health():
    REQUEST_COUNT.labels(endpoint="/health", method="GET", status="200").inc()
    return jsonify({
        "status": "UP",
        "service": SERVICE_NAME
    })

@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/notifications", methods=["POST"])
def send_notification():
    data = request.get_json(silent=True) or {}

    notification = {
        "id": len(notifications) + 1,
        "recipient": data.get("recipient", "user@example.com"),
        "message": data.get("message", "Booking confirmed"),
        "status": "sent"
    }

    notifications.append(notification)

    REQUEST_COUNT.labels(endpoint="/notifications", method="POST", status="201").inc()
    return jsonify(notification), 201

@app.route("/notifications", methods=["GET"])
def get_notifications():
    REQUEST_COUNT.labels(endpoint="/notifications", method="GET", status="200").inc()
    return jsonify(notifications)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)