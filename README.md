# SynChain-ERP

Standalone ERP backend for a Computer Science and Business Systems mini-project at **KIT Kolhapur**. The API is built with FastAPI and PostgreSQL so a separate system, **SynChain AI**, can call it over REST.

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Architecture

Router (controller) → Service → Repository → PostgreSQL (SQLAlchemy)

Change tracking is automatic: SQLAlchemy mapper events write `CREATE` / `UPDATE` / `DELETE` rows to `audit_logs` for business entities.

## Requirements

- Python 3.12+
- PostgreSQL 16 (or Docker Desktop)

## Configuration

Copy `.env.example` to `.env` and adjust if needed:

```bash
copy .env.example .env
```

Important variables:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `API_KEY` | Shared key for SynChain AI (`X-API-Key` header) |
| `SECRET_KEY` | JWT signing secret |

Demo users created by the seed script:

- Admin: `admin` / `admin123`
- Operations User: `ops` / `ops123`
- API key (default): `synchain-erp-dev-api-key`

Deletes on master data require the **Admin** role (or a valid API key, which is treated as a service account).

## Run with Docker

```bash
docker compose up --build
```

This starts PostgreSQL, runs Alembic migrations, seeds sample data, and serves the API on port 8000.

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

## Run locally (without Docker for the API)

1. Create a database `synchain_erp` owned by user `synchain` (password `synchain`), or change `DATABASE_URL`.
2. Install dependencies and migrate:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On macOS/Linux, activate with `source .venv/bin/activate` and copy env with `cp .env.example .env`.

You can also run only the database in Docker and the API on the host:

```bash
docker compose up db -d
```

Keep `DATABASE_URL` pointed at `localhost:5432`.

## Authentication

**Service-to-service (SynChain AI)**

```http
X-API-Key: synchain-erp-dev-api-key
```

**Human users**

`POST /api/v1/auth/login` returns a JWT. Send it as:

```http
Authorization: Bearer <access_token>
```

In Swagger UI, click **Authorize** and paste either the API key or the Bearer token.

## Example curl requests

Replace the API key if you changed `.env`.

### Health

```bash
curl http://localhost:8000/api/v1/health
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### Suppliers

```bash
curl http://localhost:8000/api/v1/suppliers?page=1&page_size=20&category=Packaging ^
  -H "X-API-Key: synchain-erp-dev-api-key"

curl -X POST http://localhost:8000/api/v1/suppliers ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Demo Metals\",\"contact_email\":\"demo@metals.example\",\"phone\":\"+91-231-0000000\",\"address\":\"Kolhapur\",\"category\":\"Raw Materials\",\"performance_rating\":4.0}"

curl -X PUT http://localhost:8000/api/v1/suppliers/1 ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"performance_rating\":4.8}"

curl -X DELETE http://localhost:8000/api/v1/suppliers/1 ^
  -H "X-API-Key: synchain-erp-dev-api-key"
```

### Warehouses

```bash
curl http://localhost:8000/api/v1/warehouses?location=Kolhapur ^
  -H "X-API-Key: synchain-erp-dev-api-key"

curl -X POST http://localhost:8000/api/v1/warehouses ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Satara Hub\",\"location\":\"Satara\",\"capacity\":2000}"
```

### Inventory

```bash
curl "http://localhost:8000/api/v1/inventory?warehouse_id=1&page=1&page_size=10" ^
  -H "X-API-Key: synchain-erp-dev-api-key"

curl -X POST http://localhost:8000/api/v1/inventory ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"sku\":\"TST-001\",\"name\":\"Test Fastener\",\"quantity\":50,\"unit\":\"pcs\",\"reorder_level\":10,\"warehouse_id\":1}"
```

### Purchase orders

```bash
curl "http://localhost:8000/api/v1/purchase-orders?status=draft" ^
  -H "X-API-Key: synchain-erp-dev-api-key"

curl -X POST http://localhost:8000/api/v1/purchase-orders ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"supplier_id\":1,\"status\":\"draft\",\"expected_date\":\"2026-04-20\",\"items\":[{\"sku\":\"STL-HR-001\",\"name\":\"HR Steel Coil 2mm\",\"quantity\":5,\"unit_price\":42500}]}"
```

### Orders

```bash
curl "http://localhost:8000/api/v1/orders?status=pending" ^
  -H "X-API-Key: synchain-erp-dev-api-key"

curl -X POST http://localhost:8000/api/v1/orders ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_name\":\"KIT Lab Store\",\"status\":\"pending\",\"order_date\":\"2026-04-09\",\"items\":[{\"sku\":\"PKG-TAP-48\",\"name\":\"Packing Tape 48mm\",\"quantity\":12,\"unit_price\":55}]}"
```

### Invoices

An invoice must reference **exactly one** of `order_id` or `purchase_order_id`.

```bash
curl "http://localhost:8000/api/v1/invoices?status=unpaid" ^
  -H "X-API-Key: synchain-erp-dev-api-key"

curl -X POST http://localhost:8000/api/v1/invoices ^
  -H "X-API-Key: synchain-erp-dev-api-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"order_id\":1,\"amount\":20892,\"status\":\"unpaid\",\"due_date\":\"2026-04-30\"}"
```

### Audit logs

```bash
curl "http://localhost:8000/api/v1/audit-logs?table_name=suppliers&page=1&page_size=20" ^
  -H "X-API-Key: synchain-erp-dev-api-key"
```

Supported filters: `table_name`, `record_id`, `action` (`CREATE` / `UPDATE` / `DELETE`), `from_date`, `to_date`.

## API prefix

All endpoints live under `/api/v1`. List endpoints use `page` and `page_size` (max 100) and return:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

Errors use a consistent body:

```json
{
  "status_code": 404,
  "message": "Supplier 99 not found",
  "detail": null
}
```

## Project layout

```
app/
  main.py
  core/           # settings, JWT, API key, dependencies
  db/             # engine, session, seed
  models/         # SQLAlchemy models
  schemas/        # Pydantic request/response models
  routers/        # HTTP layer
  services/       # business rules
  repositories/   # queries
  utils/          # audit listeners, pagination
alembic/          # migrations
docker-compose.yml
```

## Academic note

This repository is the ERP half of the SynChain project. SynChain AI should treat this service as the system of record and call the documented JSON APIs rather than the database directly.
