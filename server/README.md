# SkillForge Server

The SkillForge server is an asynchronous REST API built with FastAPI.

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

## Requirements

- Python 3.11 or newer

## Local Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment (Git Bash):

```bash
source .venv/Scripts/activate
```

Activate the virtual environment (Windows PowerShell):

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

## Testing

Run the automated test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

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

## Response Headers

Every API response includes tracing and performance headers:

| Header | Description |
|---|---|
| `X-Request-ID` | Unique identifier used to trace a request |
| `X-Process-Time` | Server-side request processing duration in seconds |

Clients may send their own `X-Request-ID`. Otherwise, the server generates one.

## Error Response Format

Expected API errors use a consistent structure:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found.",
    "details": null
  },
  "request_id": "73d77803-0306-456d-87b5-40c863de64ce"
}

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
│   │   ├── security.py          # Future
│   │   ├── logging.py           # Future
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
├── alembic/                     # Will be added later
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
└── Dockerfile                   # Will be added later
```

## Project Status

The FastAPI backend has been initialized with versioned routing, environment-based settings, health-check endpoints, automated testing, and a modular project architecture.

## Future Development

The backend will continue to evolve with support for:

- JWT authentication
- Role-based authorization
- PostgreSQL with SQLAlchemy
- Alembic database migrations
- Redis caching
- Celery background workers
- Leaderboards
- Notifications
- Docker deployment
- GitHub Actions CI/CD