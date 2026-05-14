from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time

SERVICE_NAME = os.getenv("SERVICE_NAME", "hotel-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5002"))

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

hotels = [
    {"id": 1, "name": "Astana Grand Hotel", "city": "Astana", "rating": 5},
    {"id": 2, "name": "Almaty City Hotel", "city": "Almaty", "rating": 4},
    {"id": 3, "name": "Qyzylorda Comfort Inn", "city": "Qyzylorda", "rating": 4}
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

@app.route("/hotels", methods=["GET"])
def get_hotels():
    REQUEST_COUNT.labels(endpoint="/hotels", method="GET", status="200").inc()
    return jsonify(hotels)

@app.route("/hotels/<int:hotel_id>", methods=["GET"])
def get_hotel(hotel_id):
    hotel = next((h for h in hotels if h["id"] == hotel_id), None)
    if not hotel:
        REQUEST_COUNT.labels(endpoint="/hotels/<id>", method="GET", status="404").inc()
        return jsonify({"error": "Hotel not found"}), 404

    REQUEST_COUNT.labels(endpoint="/hotels/<id>", method="GET", status="200").inc()
    return jsonify(hotel)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)