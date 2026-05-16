from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time

SERVICE_NAME = os.getenv("SERVICE_NAME", "user-profile-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5007"))

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

profiles = [
    {
        "id": 1,
        "name": "Aigerim",
        "email": "aigerim@example.com",
        "role": "customer"
    }
]

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

@app.route("/users", methods=["GET"])
def get_users():
    REQUEST_COUNT.labels(endpoint="/users", method="GET", status="200").inc()
    return jsonify(profiles)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in profiles if u["id"] == user_id), None)

    if not user:
        REQUEST_COUNT.labels(endpoint="/users/<id>", method="GET", status="404").inc()
        return jsonify({"error": "User not found"}), 404

    REQUEST_COUNT.labels(endpoint="/users/<id>", method="GET", status="200").inc()
    return jsonify(user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)