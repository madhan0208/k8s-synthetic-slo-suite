import os
import time
import logging
import requests
from flask import Flask, request, jsonify

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# --- WHERE TO SEND TELEMETRY ---
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")

# --- WHO AM I ---
resource = Resource.create({
    "service.name": "order-service",
    "service.version": "1.0.0",
    "deployment.environment": "thesis-k8s",
})

# --- TRACING SETUP ---
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
    )
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("order-service")

# --- METRICS SETUP ---
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True),
    export_interval_millis=15000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("order-service")

order_counter = meter.create_counter("orders_total", description="Total orders")
order_duration = meter.create_histogram("orders_duration_ms", description="Order duration")

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order-service")

# --- FLASK APP ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory-service.apps:8081")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/orders", methods=["POST"])
def create_order():
    start = time.time()
    data = request.json or {}
    item_id = data.get("itemId", "unknown")
    qty = data.get("qty", 1)

    with tracer.start_as_current_span("create-order") as span:
        span.set_attribute("order.item_id", item_id)
        span.set_attribute("order.quantity", qty)
        logger.info(f"Creating order: item={item_id} qty={qty}")

        try:
            resp = requests.get(
                f"{INVENTORY_URL}/check",
                params={"item": item_id},
                timeout=5,
            )
            inventory = resp.json()
            span.set_attribute("inventory.available", inventory.get("available", False))
        except Exception as e:
            span.set_status(trace.StatusCode.ERROR, str(e))
            span.record_exception(e)
            logger.error(f"Inventory check failed: {e}")
            order_counter.add(1, {"status": "error"})
            return jsonify({"error": "inventory_unavailable"}), 503

        duration_ms = (time.time() - start) * 1000
        order_counter.add(1, {"status": "created"})
        order_duration.record(duration_ms)
        logger.info(f"Order created: item={item_id} duration={duration_ms:.0f}ms")

        return jsonify({
            "status": "created",
            "itemId": item_id,
            "qty": qty,
            "inventory": inventory,
        }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)