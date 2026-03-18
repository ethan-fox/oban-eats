# Oban-Playground: FastAPI + Oban-py Minimal Demo

A minimal FastAPI application demonstrating asynchronous job processing with Oban-py and PostgreSQL.

## Domain Model

This application simulates a **Restaurant Kitchen** where:
- Orders are received from tables via REST API
- Each meal in an order becomes a separate background job
- Worker processes prepare meals asynchronously
- Both API and Worker services share the same codebase

## Architecture

### Two Services, One Codebase

**API Service** (`src/api.py`)
- Accepts restaurant orders via `POST /v1/order`
- Creates order records in database
- Enqueues meal preparation jobs
- Does NOT execute jobs
- Scales based on HTTP traffic

**Worker Service** (`src/worker_main.py`)
- Polls Oban queue for meal preparation jobs
- Executes jobs (logs + simulates 1s preparation)
- Does NOT handle HTTP requests
- Scales based on queue depth

### Layer Structure

```
src/
├── api.py                    # API service entry point
├── worker_main.py            # Worker service entry point
├── config/                   # Settings, DI, middleware
├── dao/                      # Database operations
├── service/                  # Business logic
├── router/                   # API endpoints
├── model/                    # Data models (api/, view/, db/)
├── worker/                   # Job workers
└── util/                     # Database, job managers
```

## Setup

### Prerequisites
- Python 3.11+
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
# Edit .env if needed (defaults work for local development)
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

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
oban-playground/
├── src/                      # Application source code
├── tests/                    # Test suite
├── alembic/                  # Database migrations
├── docker-compose.yml        # PostgreSQL container
├── requirements.txt          # Python dependencies
├── pytest.ini               # Test configuration
├── alembic.ini              # Migration configuration
├── .env.example             # Environment template
└── README.md                # This file
```

## Database Schema

**Tables:**
- `order` - Restaurant orders
- `oban_jobs` - Oban job queue
- `oban_peers` - Oban worker coordination

## Future Enhancements

- Kubernetes deployment manifests
- Prometheus metrics
- Job status API endpoints
- Retry policies and dead letter queue
