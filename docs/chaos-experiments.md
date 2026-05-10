\# Chaos Experiment Results



\## Experiment 1: Kill Inventory Service Pods



\*\*What we did:\*\* Deleted all inventory-service pods while traffic was flowing.



\*\*What happened:\*\*

\- Order-service returned 503 errors for approximately \_\_ seconds

\- Kubernetes restarted pods within \_\_ seconds

\- Total failed requests: approximately \_\_



\*\*Evidence:\*\*

\- Jaeger: Error traces visible with "connection refused" exceptions

\- Grafana: orders\_total counter shows status="error" during outage



\*\*Finding:\*\* The observability pipeline correctly detected and recorded the failure. Time to detect: immediate (traces show errors on the exact request that failed).



\---



\## Experiment 2: CPU Throttling (Slow Responses)



\*\*What we did:\*\* Limited inventory-service CPU to 10m (1% of a core).



\*\*What happened:\*\*

\- Response times increased from \~\_\_ms to \~\_\_ms

\- No errors, but significant latency increase



\*\*Evidence:\*\*

\- Jaeger: inventory-service spans show increased duration

\- Grafana: orders\_duration\_ms shows latency spike



\*\*Finding:\*\* Latency issues are visible in traces even when there are no errors. This is why duration metrics and trace visualization are both needed.



\---



\## Experiment 3: Kill OTel Collector Agents



\*\*What we did:\*\* Deleted all OTel agent pods while traffic was flowing.



\*\*What happened:\*\*

\- Applications continued serving requests normally (no errors)

\- Telemetry was lost during the \~\_\_ second outage window

\- Agents auto-restarted via DaemonSet controller



\*\*Evidence:\*\*

\- Jaeger: Gap in traces during agent downtime

\- Application logs: No errors related to telemetry



\*\*Finding:\*\* OTel SDKs are non-blocking. Collector failure does not impact application availability. However, observability is lost during the outage — you are blind when you need visibility most. This justifies monitoring the collector itself (meta-monitoring).

