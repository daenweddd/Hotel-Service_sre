from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time

SERVICE_NAME = os.getenv("SERVICE_NAME", "booking-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5004"))

DB_HOST = os.getenv("DB_HOST", "postgres")

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

bookings = []

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

@app.route("/bookings", methods=["GET"])
def get_bookings():
    REQUEST_COUNT.labels(endpoint="/bookings", method="GET", status="200").inc()
    return jsonify(bookings)

@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}

    if DB_HOST == "wrong-postgres-host":
        ERROR_COUNT.labels(service=SERVICE_NAME, error_type="db_connection").inc()
        REQUEST_COUNT.labels(endpoint="/bookings", method="POST", status="500").inc()
        return jsonify({
            "error": "Database connection failed",
            "db_host": DB_HOST
        }), 500

    booking = {
        "id": len(bookings) + 1,
        "user_id": data.get("user_id"),
        "room_id": data.get("room_id"),
        "check_in": data.get("check_in"),
        "check_out": data.get("check_out"),
        "status": "confirmed"
    }

    bookings.append(booking)

    REQUEST_COUNT.labels(endpoint="/bookings", method="POST", status="201").inc()
    return jsonify(booking), 201

@app.route("/bookings/fail", methods=["POST"])
def simulate_failure():
    ERROR_COUNT.labels(service=SERVICE_NAME, error_type="simulated_failure").inc()
    REQUEST_COUNT.labels(endpoint="/bookings/fail", method="POST", status="500").inc()

    return jsonify({
        "error": "Simulated Booking Service failure"
    }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)