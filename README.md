\# k8s-synthetic-slo-suite



Kubernetes Observability Platform using OpenTelemetry — built for thesis research on distributed tracing, metrics, and log correlation across microservices.



\## What This Project Does



Two microservices run on a local Kubernetes cluster (Kind). Both are instrumented with OpenTelemetry SDKs. They send traces, metrics, and logs through a two-tier OTel Collector pipeline (Agent + Gateway) to observability backends (Jaeger, Elastic, or Datadog).



The goal is to evaluate how well OpenTelemetry abstracts backend differences — same instrumentation, swap the exporter, compare results.



\## Architecture

Client (curl)

|

v

order-service (Python/Flask, port 8080)

|  --> sends telemetry to OTel Agent

|  --> calls inventory-service

v

inventory-service (Python/Flask, port 8081)

|  --> sends telemetry to OTel Agent

v

OTel Agent (DaemonSet, one per node)

|  --> forwards to gateway

v

OTel Gateway (Deployment, 2 replicas)

|  --> exports to backend

v

Jaeger / Elastic / Datadog






## Project Structure

k8s-synthetic-slo-suite/

├── apps/

│   ├── order-service/          # Python Flask app — creates orders

│   │   ├── app.py

│   │   ├── requirements.txt

│   │   └── Dockerfile

│   └── inventory-service/      # Python Flask app — checks stock

│       ├── app.py

│       ├── requirements.txt

│       └── Dockerfile

├── k8s/

│   ├── otel-rbac.yaml          # ServiceAccount + ClusterRole for collector

│   ├── otel-collector-agent.yaml    # DaemonSet — one agent per node

│   ├── otel-collector-gateway.yaml  # Deployment — centralized gateway

│   └── apps/

│       ├── order-deploy.yaml        # K8s Deployment + Service

│       └── inventory-deploy.yaml    # K8s Deployment + Service

├── kind-config.yaml            # Kind cluster config (1 control-plane + 3 workers)

└── README.md





## Tech Stack



\- \*\*Kubernetes\*\* — Kind (local cluster with 4 nodes)

\- \*\*OpenTelemetry Collector\*\* — Agent (DaemonSet) + Gateway (Deployment)

\- \*\*OpenTelemetry SDK\*\* — Python SDK for traces, metrics, logs

\- \*\*Flask\*\* — HTTP framework for both microservices

\- \*\*OTLP\*\* — Wire protocol between apps and collector (gRPC, port 4317)

\- \*\*Backends\*\* — Jaeger (traces), Prometheus + Grafana (metrics), Elastic, Datadog



\## Prerequisites



\- Docker Desktop

\- kubectl

\- Kind

\- Helm



\## Quick Start



\### 1. Create the cluster



```bash

kind create cluster --name otel-thesis --config kind-config.yaml

kubectl create namespace observability

kubectl create namespace apps

```



\### 2. Deploy OTel Collector



```bash

kubectl apply -f k8s/otel-rbac.yaml

kubectl apply -f k8s/otel-collector-agent.yaml

kubectl apply -f k8s/otel-collector-gateway.yaml

```



\### 3. Build and load app images



```bash

docker build -t order-service:1.0.0 apps/order-service/

docker build -t inventory-service:1.0.0 apps/inventory-service/

kind load docker-image order-service:1.0.0 --name otel-thesis

kind load docker-image inventory-service:1.0.0 --name otel-thesis

```



\### 4. Deploy apps



```bash

kubectl apply -f k8s/apps/order-deploy.yaml

kubectl apply -f k8s/apps/inventory-deploy.yaml

```



\### 5. Test



```bash

kubectl port-forward -n apps svc/order-service 8080:8080

curl -X POST http://localhost:8080/orders -H "Content-Type: application/json" -d '{"itemId":"sku-123","qty":2}'

```



\### 6. Verify telemetry



```bash

kubectl logs -n observability -l app=otel-gateway --tail=20

```



\## What's Next



\- Install Jaeger for trace visualization

\- Add Elastic (ECK) and Datadog backends

\- Backend comparison for thesis evaluation

\- Chaos engineering experiments

\- SLO-based alerting with burn-rate alerts

\- Telemetry Minimum Standard (MVS) document



\## Thesis Context



This project supports a master's thesis on Kubernetes observability using OpenTelemetry standards. The research evaluates vendor-neutral telemetry pipelines by deploying the same instrumented services against multiple backends and comparing setup complexity, cost, trace quality, and operational overhead.



\## License



MIT

