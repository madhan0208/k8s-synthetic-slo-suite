import os
import logging
from flask import Flask, request, jsonify

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")

resource = Resource.create({
    "service.name": "inventory-service",
    "service.version": "1.0.0",
    "deployment.environment": "thesis-k8s",
})

trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
    )
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("inventory-service")

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True),
    export_interval_millis=15000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("inventory-service")
check_counter = meter.create_counter("inventory_checks_total", description="Total checks")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventory-service")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Fake inventory database
STOCK = {
    "sku-123": 42,
    "sku-456": 0,
    "sku-789": 15,
}


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/check")
def check_inventory():
    item = request.args.get("item", "unknown")

    with tracer.start_as_current_span("check-inventory") as span:
        stock = STOCK.get(item, 0)
        available = stock > 0

        span.set_attribute("inventory.item_id", item)
        span.set_attribute("inventory.stock", stock)
        span.set_attribute("inventory.available", available)

        check_counter.add(1, {"item_id": item, "available": str(available)})
        logger.info(f"Inventory check: item={item} stock={stock} available={available}")

        return jsonify({
            "item": item,
            "available": available,
            "stock": stock,
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)