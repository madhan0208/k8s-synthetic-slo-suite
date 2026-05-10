\# Architecture Overview



\## System Design



This project implements a two-tier OpenTelemetry Collector pipeline

on Kubernetes with distributed microservices.



\## Components



\### Applications (namespace: apps)

\- order-service: Python/Flask, port 8080, creates orders

\- inventory-service: Python/Flask, port 8081, checks stock levels

\- Both instrumented with OpenTelemetry Python SDK

\- Trace context propagated via W3C TraceContext headers



\### OTel Collector Agent (namespace: observability)

\- Deployed as DaemonSet (one per node)

\- Receives telemetry from local pods via OTLP gRPC (port 4317)

\- Batches and forwards to gateway

\- Adds memory limiting to prevent OOM



\### OTel Collector Gateway (namespace: observability)

\- Deployed as Deployment (1 replica)

\- Receives from all agents

\- Exports traces to Jaeger via OTLP

\- Exports metrics to Prometheus via Prometheus exporter (port 8889)



\### Observability Backends (namespace: observability)

\- Jaeger: trace storage and visualization (port 16686)

\- Prometheus: metric storage, scrapes gateway every 30s (port 9090)

\- Grafana: dashboards and visualization (port 3000)



\## Data Flow



1\. User sends POST /orders to order-service

2\. order-service creates trace span, calls inventory-service

3\. traceparent header propagates trace context

4\. inventory-service creates child span, returns stock data

5\. Both services send spans + metrics to local OTel Agent

6\. Agent batches and forwards to Gateway

7\. Gateway exports traces to Jaeger, metrics to Prometheus

8\. Grafana queries Prometheus for dashboard visualization



\## Kubernetes Resources Used



\- Deployment: order-service, inventory-service, otel-gateway, jaeger, prometheus, grafana

\- DaemonSet: otel-agent

\- Service: one per deployment for network access

\- ConfigMap: collector configs, prometheus config

\- ServiceAccount + ClusterRole + ClusterRoleBinding: collector RBAC

\- Namespace: apps, observability



\## Key Design Decisions



1\. Agent + Gateway over single collector: enables tail sampling and reduces per-node resource usage

2\. OTLP over vendor protocols: vendor-neutral, supports backend switching

3\. Separate namespaces: resource isolation between apps and observability

4\. Python for both services: simplified setup, proves OTel SDK works consistently

5\. Lightweight backends: standalone deployments instead of Helm charts to save resources

