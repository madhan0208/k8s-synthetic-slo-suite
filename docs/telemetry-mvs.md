\# Telemetry Minimum Standard (MVS) v1.0



This document defines the minimum telemetry every service must emit

to participate in the observability platform.



\## 1. Required Traces



\- All inbound HTTP requests must be auto-instrumented

\- All outbound HTTP calls must be auto-instrumented with context propagation

\- Custom spans for business-critical operations

\- Every span must include: service.name, service.version, deployment.environment

\- Error spans must include exception type and message via span.record\_exception()



\## 2. Required Metrics (RED Method)



Every service must emit these three metric types:



\- Rate: <service>\_requests\_total (counter, labels: status, route)

\- Errors: <service>\_errors\_total (counter, labels: error\_type)

\- Duration: <service>\_duration\_ms (histogram, labels: route)



\## 3. Required Logs



\- Structured format (key=value or JSON)

\- Must include: timestamp, level, message, trace\_id, span\_id

\- Log levels: ERROR for failures, WARN for degraded, INFO for business events

\- No PII in logs



\## 4. Forbidden Practices



\- No vendor-specific SDKs (use OpenTelemetry only)

\- No high-cardinality metric labels (user\_id, request\_id as labels)

\- No logging request/response bodies (cost and security risk)

\- No skipping trace context propagation on outbound calls



\## 5. Collector Architecture



\- Agent: DaemonSet, one per node

\- Gateway: Deployment, 1+ replicas

\- Protocol: OTLP gRPC (port 4317)

\- Sampling: tail sampling on gateway for errors and slow traces



\## 6. Onboarding Checklist



\- \[ ] Add OTel SDK dependency

\- \[ ] Initialize TracerProvider and MeterProvider

\- \[ ] Set OTEL\_EXPORTER\_OTLP\_ENDPOINT env var

\- \[ ] Set service.name resource attribute

\- \[ ] Add auto-instrumentation for framework (Flask, Express, etc.)

\- \[ ] Add auto-instrumentation for HTTP client

\- \[ ] Create RED metrics

\- \[ ] Verify traces appear in Jaeger

\- \[ ] Verify metrics appear in Grafana

