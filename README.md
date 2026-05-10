# k8s-synthetic-slo-suite

Kubernetes Observability Platform using OpenTelemetry — built for thesis research on distributed tracing, metrics, and log correlation across microservices.

## What This Project Does

Two microservices run on a local Kubernetes cluster (Kind). Both are instrumented with OpenTelemetry SDKs. They send traces, metrics, and logs through a two-tier OTel Collector pipeline (Agent + Gateway) to Jaeger (traces) and Prometheus + Grafana (metrics).

## Architecture

Client (curl/PowerShell)
|
v
order-service (Python/Flask, port 8080)
|  --> sends telemetry to OTel Agent
|  --> calls inventory-service via HTTP
v
inventory-service (Python/Flask, port 8081)
|  --> sends telemetry to OTel Agent
v
OTel Agent (DaemonSet, one per K8s node)
|  --> forwards to Gateway
v
OTel Gateway (Deployment)
|  --> traces to Jaeger
|  --> metrics to Prometheus
v
Jaeger (trace UI, port 16686)
Prometheus (metric storage, port 9090)
Grafana (dashboards, port 3000)

## Project Structure


k8s-synthetic-slo-suite/
├── apps/
│   ├── order-service/
│   │   ├── app.py              # Flask app with OTel instrumentation
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── inventory-service/
│       ├── app.py              # Flask app with OTel instrumentation
│       ├── requirements.txt
│       └── Dockerfile
├── k8s/
│   ├── otel-rbac.yaml          # ServiceAccount + RBAC for collector
│   ├── otel-collector-agent.yaml    # DaemonSet agent
│   ├── otel-collector-gateway.yaml  # Deployment gateway
│   ├── jaeger.yaml             # Jaeger all-in-one
│   ├── prometheus.yaml         # Lightweight Prometheus
│   ├── grafana.yaml            # Grafana
│   └── apps/
│       ├── order-deploy.yaml
│       └── inventory-deploy.yaml
├── docs/
│   ├── architecture.md         # System design documentation
│   ├── telemetry-mvs.md        # Telemetry Minimum Standard
│   └── chaos-experiments.md    # Chaos engineering results
├── kind-config.yaml            # Kind cluster (1 control-plane + 2 workers)
└── README.md


## Tech Stack

- Kubernetes (Kind, 3 nodes)
- OpenTelemetry Collector Contrib 0.100.0
- OpenTelemetry Python SDK 1.25.0
- Flask 3.0.0
- Jaeger 1.57
- Prometheus 2.52.0
- Grafana 10.4.0

## Quick Start

### Prerequisites
- Docker Desktop (6 GB+ memory)
- kubectl
- Kind
- Helm (optional)

### 1. Create cluster
```bash
kind create cluster --name otel-thesis --config kind-config.yaml
kubectl create namespace observability
kubectl create namespace apps
```

### 2. Deploy observability stack
```bash
kubectl apply -f k8s/otel-rbac.yaml
kubectl apply -f k8s/otel-collector-agent.yaml
kubectl apply -f k8s/otel-collector-gateway.yaml
kubectl apply -f k8s/jaeger.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
```

### 3. Build and deploy apps
```bash
docker build -t order-service:1.0.0 apps/order-service/
docker build -t inventory-service:1.0.0 apps/inventory-service/
kind load docker-image order-service:1.0.0 --name otel-thesis
kind load docker-image inventory-service:1.0.0 --name otel-thesis
kubectl apply -f k8s/apps/order-deploy.yaml
kubectl apply -f k8s/apps/inventory-deploy.yaml
```

### 4. Test
```bash
kubectl port-forward -n apps svc/order-service 8080:8080
curl -X POST http://localhost:8080/orders -H "Content-Type: application/json" -d '{"itemId":"sku-123","qty":2}'
```

### 5. Access dashboards
```bash
kubectl port-forward -n observability svc/jaeger-query 16686:16686    # Jaeger
kubectl port-forward -n observability svc/grafana 3000:3000           # Grafana (admin/thesis2026)
kubectl port-forward -n observability svc/prometheus 9090:9090        # Prometheus
```

## Chaos Experiments

Three experiments validate the observability pipeline:

1. **Pod kill** — Delete inventory pods, observe error traces in Jaeger and error metrics in Grafana
2. **CPU throttling** — Limit inventory CPU to 1%, observe latency increase in traces
3. **Collector failure** — Kill OTel agents, confirm apps keep running (non-blocking SDK)

Results documented in docs/chaos-experiments.md

## Thesis Context

This project supports a master's thesis on Kubernetes observability using OpenTelemetry standards. Key findings:

- OTel enables vendor-neutral instrumentation (same code, swap backends via config)
- Two-tier collector (Agent + Gateway) provides fault tolerance and sampling flexibility
- OTel SDKs are non-blocking — collector failure does not impact application availability
- Distributed traces across services are connected via W3C TraceContext propagation

## Future Work

- Add Elasticsearch/Kibana backend for multi-backend comparison
- Add Datadog SaaS backend
- Implement tail sampling on gateway
- Add SLO-based burn-rate alerting
- Add Go or Node.js service for cross-language trace propagation

## License
MIT