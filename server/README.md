# SkillForge Server

The SkillForge server is an asynchronous REST API built with FastAPI. It powers the backend of the SkillForge platform by providing secure, scalable, and versioned REST APIs.

---

## Current Features

- FastAPI application initialization
- Versioned API routing
- Environment-based configuration
- Application lifespan management
- Health-check endpoint
- Interactive Swagger documentation
- Automated API tests with Pytest
- Asynchronous test client
- Ruff linting and formatting
- Mypy static type checking
- Global exception handling
- Standardized API error responses
- Request ID middleware
- Request execution-time tracking
- Structured JSON logging
- Request and response tracing
- Configurable CORS policy
- Environment-based allowed frontend origins

---

## Requirements

- Python 3.11 or newer
- pip
- Git

---

## Local Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it (Git Bash):

```bash
source .venv/Scripts/activate
```

Activate it (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Testing

Run the automated test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

---

## Code Quality

Check code quality:

```bash
ruff check .
```

Automatically fix supported linting issues:

```bash
ruff check . --fix
```

Format the code:

```bash
ruff format .
```

Run static type checking:

```bash
mypy app
```

---

## Response Headers

Every API response includes tracing and performance headers.

| Header | Description |
|---------|-------------|
| `X-Request-ID` | Unique identifier used to trace each request |
| `X-Process-Time` | Total server-side processing time |

Clients may send their own `X-Request-ID`. If omitted, the server automatically generates one.

---

## Error Response Format

Expected API errors follow a standardized format.

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found.",
    "details": null
  },
  "request_id": "73d77803-0306-456d-87b5-40c863de64ce"
}
```

---

## Logging

Application logs use a structured JSON format.

Each request log may include:

- Request ID
- HTTP method
- Request path
- Response status
- Processing duration

The logging level is configured through:

```env
LOG_LEVEL=INFO
```

---

## CORS

Allowed frontend origins are configured through:

```env
CORS_ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

The default development configuration supports common React and Vite development servers.

Production frontend origins must be explicitly configured before deployment.

---

## Current Structure

```text
server/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── dependencies.py
│   │   │
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       │
│   │       └── routes/
│   │           ├── __init__.py
│   │           └── health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   ├── repositories/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── middleware/
│   │   └── __init__.py
│   │
│   ├── cache/
│   │   └── __init__.py
│   │
│   ├── workers/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_root.py
│   │   └── test_health.py
│   │
│   ├── repositories/
│   │   └── __init__.py
│   │
│   └── services/
│       └── __init__.py
│
├── alembic/
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
└── Dockerfile
```

---

## Project Status

The backend foundation has been completed.

Current progress includes:

- FastAPI application setup
- Modular project architecture
- Versioned API routing
- Environment-based configuration
- Health-check endpoint
- Standardized exception handling
- Request tracing middleware
- Structured JSON logging
- Configurable CORS policy
- Automated testing infrastructure
- Code quality tooling

---

## Future Development

The project will continue with the implementation of:

- JWT authentication
- User management
- Role-based authorization
- PostgreSQL integration
- SQLAlchemy ORM
- Alembic database migrations
- Redis caching
- Celery background workers
- Leaderboards
- Notifications
- Docker deployment
- GitHub Actions CI/CD
- Monitoring and observability