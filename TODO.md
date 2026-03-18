# Oban Playground - TODO

## Must-Haves

### 2. Minikube Deployment
- Deploy API, Worker, and PostgreSQL services in minikube
- Separate Deployments for API and Worker
- ConfigMap and Secrets for configuration
- Service definitions for internal communication

### 3. Oban Web
- Stand up Oban Web UI for job monitoring
- View job queues, states, and history
- Monitor worker performance

### 4. Grafana + Prometheus
- Set up Prometheus for metrics collection
- Configure Grafana dashboards
- Track job processing metrics, queue depth, success/failure rates

## Nice to Have

### 1. Typed Worker Pattern
- Revisit `BaseWorker[T]` with Pydantic validation
- Provides compile-time type safety for job arguments
- IDE autocomplete and validation at job creation time
