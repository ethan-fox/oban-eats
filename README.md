# Oban-Playground: FastAPI + Oban-py Minimal Demo

A minimal FastAPI application demonstrating asynchronous job processing with oban-py and PostgreSQL. Optional deployment on Bare metal (docker desktop) or minikube

## Domain Model

This application simulates a **Restaurant Kitchen** where:
- Orders are placed via REST API
- Each meal in an order becomes a separate background job
- Worker processes prepare meals asynchronously

### Prerequisites
- Python 3.12
- Docker and Docker Compose (for PostgreSQL)

### Installation

1. Clone the repository
```bash
git clone <repo-url>
cd oban-eats
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
```

5. Start PostgreSQL
```bash
docker-compose up -d
```

6. Wait for PostgreSQL to be ready (about 5-10 seconds)
```bash
docker-compose ps
# Wait until status shows "healthy"
```

7. Run database migrations
```bash
alembic upgrade head
```

## Running Locally

### Start API Service (Terminal 1)
```bash
uvicorn src.api:app --reload --port 8000
```

### Start Worker Service (Terminal 2)
```bash
python -m src.worker_main
```

## Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Create an Order
```bash
curl -X POST http://localhost:8000/v1/order \
  -H "Content-Type: application/json" \
  -d '{
    "table_id": "table-42",
    "meals": [
      {"menu_item_id": "burger", "metadata": {"no_onions": true}},
      {"menu_item_id": "salad", "metadata": {}},
      {"menu_item_id": "fries", "metadata": {}}
    ]
  }'
```

Response:
```json
{
  "order_id": "uuid-here",
  "table_id": "table-42",
  "created_at": "2024-01-01T12:00:00Z",
  "meals_count": 3
}
```

Watch the Worker service logs to see meals being prepared!

## Kubernetes Deployment (Minikube)

This application includes Kubernetes manifests for deploying to minikube as a production-like environment.

### Prerequisites
- Docker
- Minikube
- kubectl

### Start Minikube

Start minikube if not already running:

```bash
minikube start
```

### Install NGINX Ingress Controller via Helm

Add the NGINX Ingress Helm repository:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

Install the NGINX Ingress Controller as a LoadBalancer on port 8000:

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.ports.http=8000
```

This installs the controller with LoadBalancer service type on port 8000.

Verify the ingress controller is running:

```bash
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

### Build Docker Image

Build a single Docker image used by all services (API, Worker, Migration):

```bash
docker build -t oban-eats:latest .
```

The same image is used for all services (command is specified at runtime in the Kubernetes manifests):
- **API**: Uses default CMD (`uvicorn src.api:app --host 0.0.0.0 --port 8000`)
- **Worker**: Overrides with `command: ["python", "-m", "src.worker_main"]`
- **Migration**: Overrides with `command: ["alembic", "upgrade", "head"]`

### Load Image into Minikube

Minikube runs in its own Docker environment, so the image must be loaded (this may take a minute or two):

```bash
minikube image load oban-eats:latest
```

### Deploy to Kubernetes

Apply manifests in order (infrastructure first, then applications):

```bash
# Create namespace and configuration
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# Deploy PostgreSQL database
kubectl apply -f k8s/db.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n oban-eats --timeout=120s

# Deploy API, Worker, and Oban UI services
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/worker.yaml
kubectl apply -f k8s/oban-ui.yaml
```

### Verify Deployment

Check that all pods are running:

```bash
# View all pods in the namespace
kubectl get pods -n oban-eats

# Expected output:
# postgres-xxx          1/1     Running
# oban-api-xxx          1/1     Running
# oban-worker-xxx       1/1     Running  (2 replicas)
# oban-ui-xxx           1/1     Running
```

Check services and ingress:

```bash
kubectl get svc -n oban-eats
kubectl get ingress -n oban-eats
```

### Expose Ingress with Minikube Tunnel

In a separate terminal, start the minikube tunnel (requires sudo):

```bash
minikube tunnel
```

This exposes the Ingress Controller on localhost. Keep this running in the background.

The NGINX Ingress Controller is configured to run on port 8000, so your services will be accessible at `http://localhost:8000`.

### Test the Deployment

Test the API health endpoint:

```bash
curl http://localhost:8000/api/health
```

Create a test order:

```bash
curl -X POST http://localhost:8000/api/v1/order \
  -H "Content-Type: application/json" \
  -d '{
    "table_id": "table-k8s-test",
    "meals": [
      {"menu_item_id": "burger", "metadata": {"no_onions": true}},
      {"menu_item_id": "fries", "metadata": {}}
    ]
  }'
```

Watch worker logs to see job processing:

```bash
kubectl logs -n oban-eats -l app=oban-worker -f
```

### Access Oban UI Dashboard

The Oban UI dashboard is available at:

```
http://localhost:8000/oban-ui
```

The dashboard provides a web interface to:
- Monitor job queues and execution status
- View job details and history
- Inspect failed jobs and errors
- Cancel, retry, or delete jobs (if read-only mode is disabled)

**Security Note**: For production use, enable HTTP Basic Authentication by uncommenting and setting the `BASIC_AUTH_USER` and `BASIC_AUTH_PASS` environment variables in `k8s/oban-ui.yaml`, then reapply the manifest.

### Troubleshooting

View pod details and events:

```bash
kubectl describe pod <pod-name> -n oban-eats
```

Check init container logs (if migration fails):

```bash
kubectl logs <pod-name> -n oban-eats -c migration
```

Check application logs:

```bash
# API logs
kubectl logs -n oban-eats -l app=oban-api

# Worker logs
kubectl logs -n oban-eats -l app=oban-worker

# Database logs
kubectl logs -n oban-eats -l app=postgres

# Oban UI logs
kubectl logs -n oban-eats -l app=oban-ui
```

Connect to the database:

```bash
kubectl exec -it -n oban-eats <postgres-pod-name> -- \
  psql -U admin oban_eats
```

### Scaling

Scale the API service:

```bash
kubectl scale deployment oban-api -n oban-eats --replicas=3
```

Scale the Worker service:

```bash
kubectl scale deployment oban-worker -n oban-eats --replicas=5
```

### Cleanup

Remove all resources:

```bash
kubectl delete namespace oban-eats
```

Or remove individual resources:

```bash
kubectl delete -f k8s/worker.yaml
kubectl delete -f k8s/api.yaml
kubectl delete -f k8s/db.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/namespace.yaml
```

## Architecture

### Kubernetes Components

```
k8s/
├── namespace.yaml          # Resource isolation
├── configmap.yaml         # Application configuration
├── db.yaml                # PostgreSQL with persistent storage
├── api.yaml               # API deployment, service, ingress
├── worker.yaml            # Worker deployment
└── oban-ui.yaml           # Oban UI dashboard deployment, service, ingress
```

**Key Features:**
- Single Docker image with runtime command overrides for API, Worker, and Migration
- Init containers run database migrations before services start
- PostgreSQL with persistent volume (survives pod restarts)
- API exposed via LoadBalancer service
- Worker scales independently (2 replicas by default)
- Horizontal Pod Autoscaler for API (1-10 replicas based on CPU)
- Health probes ensure reliability

## Future Enhancements

- Production secrets management (Kubernetes Secrets)
- Ingress controller for external access
- Prometheus metrics and monitoring
- Job status API endpoints
- Retry policies and dead letter queue
- Database replication for high availability
