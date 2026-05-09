# k8s-synthetic-slo-suite



A focused SRE practice environment for synthetic monitoring and SLO 
mathematics on Kubernetes.

**Goals**: 
- A Go HTTP service probed by Blackbox Exporter (availability SLI)
- k6-based synthetic functional tests for end-to-end correctness  
- Prometheus multi-window multi-burn-rate alerts (per Google SRE Workbook)
- Markdown runbooks per alert class
