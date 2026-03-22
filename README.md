# Oban-Eats: FastAPI + Oban-py PoC

Welcome to the **Oban Eats kitchen**! This repository features a food ordering workflow to show off the power of Oban for asynchronous job processing.

Our Restaurant simulation is engaged by:

0. Place your order via REST API
1. Each `meal` is managed as an independent job
2. Worker(s) will prepare meals asynchronously, log when finished
3. For the minikube deployment, view Job executions via Oban Web.

## Quickstart

### Prerequisites
- Python 3.12
- Docker and Docker Compose (for PostgreSQL)

### Install

1. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment
```bash
cp .env.example .env
```

4. Start PostgreSQL
```bash
docker-compose up -d
```

5. Run database migrations
```bash
alembic upgrade head
```

### Run

For the end-to-end experience, we will deploy two services:

* `api` - HTTP API service, handles job enqueues ONLY
* `worker` - Async jobs processor, does not expose API routes

#### API Service (Terminal 1)

```bash
MODE=api uvicorn src.main:app --reload --port 8000
```

#### Worker Service (Terminal 2)

```bash
MODE=worker uvicorn src.main:app --reload --port 8001
```

## Usage - Your first order

```bash
curl -X POST http://localhost:8000/v1/order \
  -H "Content-Type: application/json" \
  -d '{
    "table_id": "table-42",
    "meals": [
      {"menu_item_id": "burger", "metadata": {"exclude": ["lettuce"]}},
      {"menu_item_id": "salad"},
      {"menu_item_id": "fries"}
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

Watch the service logs to see meals being prepared!

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

Configure your shell to use Minikube's Docker daemon, then build directly inside Minikube:

```bash
eval $(minikube docker-env)

docker build -t oban-eats:latest .
```

### Deploy to Kubernetes

Apply manifests in order (infrastructure first, then applications):

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# PostgreSQL
kubectl apply -f k8s/db.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n oban-eats --timeout=120s

# Application services
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
# oban-worker-xxx       1/1     Running
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
      {"menu_item_id": "burger", "metadata": {"exclude": ["onions"]}},
      {"menu_item_id": "fries", "metadata": {}}
    ]
  }'
```

Watch worker logs to see job processing:

```bash
kubectl logs -n oban-eats -l app=oban-worker -f
```

To debug DB:

```bash
kubectl exec -it -n oban-eats <postgres pod name> -- psql -U admin -d oban_eats
```

### Access Oban UI Dashboard

The Oban UI dashboard is available at:

```
http://localhost:8000/oban
```

For more info about Oban Web, [see here](https://hexdocs.pm/oban_web/overview.html).

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

Revert Docker to use your local daemon:

```bash
eval $(minikube docker-env -u)
```

## TODO 

- Prometheus metrics and monitoring
- Job status API endpoints
- Retry policies and dead letter queue
