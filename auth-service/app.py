from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time

SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5001"))

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

users = []

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

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    user = {
        "id": len(users) + 1,
        "username": data.get("username", "guest"),
        "email": data.get("email", "guest@example.com")
    }
    users.append(user)
    REQUEST_COUNT.labels(endpoint="/auth/register", method="POST", status="201").inc()
    return jsonify(user), 201

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    REQUEST_COUNT.labels(endpoint="/auth/login", method="POST", status="200").inc()
    return jsonify({
        "message": "Login successful",
        "username": data.get("username", "guest"),
        "token": "demo-token"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)