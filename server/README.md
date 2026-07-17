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
- Asynchronous SQLAlchemy database engine
- Async PostgreSQL sessions
- Supabase PostgreSQL connection
- Database dependency injection
- Database health-check endpoint
- Alembic migration environment
- User and profile ORM models
- Role and account-status enums
- One-to-one user profile relationship
- Database constraints and indexes
- Initial users and profiles migration
- User registration request validation
- Secure Argon2 password hashing
- Password verification
- User repository abstraction
- Case-insensitive email and username lookup
- Repository, schema, and security unit tests
- Transactional user registration
- Duplicate email and username detection
- Registration endpoint
- Secure password hashing before storage
- Registration service and API tests
- JWT access and refresh token generation
- Secure login endpoint
- Token expiration and claim validation
- Inactive-account login protection
- JWT and login unit tests
- Persistent refresh-token sessions
- Hashed refresh-token storage
- Refresh-token revocation support
- Per-user session revocation
- Refresh-token expiration indexes
- Refresh-token persistence during login
- Refresh-token rotation
- Session revocation during logout
- Replay protection for rotated tokens
- Database locking during token rotation

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

## Database Setup

SkillForge uses Supabase PostgreSQL together with SQLAlchemy's asynchronous engine.

Copy the database connection string from the Supabase dashboard and change its scheme to use SQLAlchemy's async driver.

Connection string format:

```text
postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE
```

Add the connection string only to your local `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://...
```

Never commit the real database URL to GitHub or to `.env.example`.

To verify the database connection:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/api/v1/health/database
```

---

## Database Migrations

Show the current migration:

```bash
alembic current
```

Show available migration heads:

```bash
alembic heads
```

---



## Initial Database Models

### Users

Stores authentication and account-level information:

- Email
- Hashed password
- Role
- Account status
- Email verification status

### Profiles

Stores public progress and profile information:

- Username
- Display name
- Biography and avatar
- Total XP
- Current level
- Current and longest streak

The `users` and `profiles` tables have a one-to-one relationship.

---

## Creating Migrations

Generate a migration after changing ORM models:

```bash
alembic revision --autogenerate -m "describe the database change"
```

Review the generated file, then apply it:

```bash
alembic upgrade head
```

---

## User Registration Validation

Registration data is validated before reaching the service layer.

Current validation rules include:

- A valid email address
- Username length between 3 and 30 characters
- Only lowercase letters, numbers, and underscores in usernames
- Password length between 8 and 128 characters
- At least one uppercase letter in the password
- At least one lowercase letter in the password
- At least one number in the password

Email addresses and usernames are normalized before processing to support
consistent, case-insensitive lookups.

Passwords are hashed using Argon2 before database storage. Plain-text passwords
are never stored in the database.

---

## Refresh Token Sessions

Refresh tokens are represented by database session records.

For security, the raw refresh token is returned to the client but is never
stored directly in PostgreSQL. SkillForge stores a SHA-256 hash that can be
used to identify and revoke the session.

Each session stores:

- User ID
- JWT ID (`jti`)
- Token hash
- Expiration time
- Revocation time
- Replacement token ID after rotation

## Repository Layer

The repository layer is responsible only for direct database operations and
does not contain business logic.

The user repository currently supports:

- Finding users by ID
- Finding users by email
- Finding users by username
- Case-insensitive email lookup
- Case-insensitive username lookup
- Creating a user and associated profile
- Flushing newly created records within the active database transaction

Business rules and transaction coordination will be handled by the service layer.

---


---

## Authentication Endpoints

### Register User

```http
POST /api/v1/auth/register
```

Example request:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123",
  "username": "skill_user",
  "display_name": "Skill User"
}
```

A successful request returns:

```http
HTTP/1.1 201 Created
```

The registration process performs the following steps:

- Validates the incoming request
- Checks for duplicate email addresses
- Checks for duplicate usernames
- Hashes the password using Argon2
- Creates the user and profile within a single database transaction
- Returns the created user information without exposing the password hash

Passwords are validated and hashed before database storage.

Password hashes are never included in API responses.

---
### Login

```http
POST /api/v1/auth/login
```

Example request:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123"
}
```

A successful request returns:

```http
HTTP/1.1 200 OK
```

Response example:

```json
{
  "user": {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "email": "user@example.com",
    "role": "user",
    "status": "active",
    "is_email_verified": false,
    "created_at": "2026-07-17T12:00:00Z",
    "updated_at": "2026-07-17T12:00:00Z",
    "profile": {
      "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "username": "skill_user",
      "display_name": "Skill User",
      "bio": null,
      "avatar_url": null,
      "total_xp": 0,
      "current_level": 1,
      "current_streak": 0,
      "longest_streak": 0,
      "created_at": "2026-07-17T12:00:00Z",
      "updated_at": "2026-07-17T12:00:00Z"
    }
  },
  "tokens": {
    "access_token": "<JWT_ACCESS_TOKEN>",
    "refresh_token": "<JWT_REFRESH_TOKEN>",
    "token_type": "bearer",
    "access_token_expires_in": 1800
  }
}
```

A successful login returns an access token and a refresh token.

Access tokens are short-lived and are used to authenticate API requests.

Refresh tokens are intended to obtain new access tokens without requiring the
user to sign in again.

Login requests are rejected when:

- The email does not exist
- The password is incorrect
- The account is inactive or suspended

Passwords are verified securely using Argon2.

JWT tokens include standard claims such as:

- Subject (`sub`)
- Token type (`type`)
- Token ID (`jti`)
- Issued at (`iat`)
- Expiration (`exp`)
- Issuer (`iss`)
- Audience (`aud`)

---

### Refresh Tokens

```http
POST /api/v1/auth/refresh
```

Example request:

```json
{
  "refresh_token": "<JWT_REFRESH_TOKEN>"
}
```

The supplied refresh token is validated against its hashed database session.

A successful request revokes the previous refresh-token session and returns a
new access and refresh token pair.

This rotation mechanism helps prevent reuse of an old refresh token.

---

### Logout

```http
POST /api/v1/auth/logout
```

Example request:

```json
{
  "refresh_token": "<JWT_REFRESH_TOKEN>"
}
```

A successful logout returns:

```http
HTTP/1.1 204 No Content
```

Logout revokes the supplied refresh-token session.

Subsequent attempts to use that token for rotation are rejected.

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

The backend foundation and initial user data layer have been completed.

Current progress includes:

- FastAPI application setup
- Modular project architecture
- Versioned API routing
- Environment-based configuration
- Health-check endpoints
- Standardized exception handling
- Request tracing middleware
- Structured JSON logging
- Configurable CORS policy
- Supabase PostgreSQL integration
- Asynchronous SQLAlchemy database engine
- Alembic migration environment
- User and profile ORM models
- Initial users and profiles migration
- User registration schema validation
- Secure Argon2 password hashing
- User repository implementation
- Automated testing infrastructure
- Code quality tooling
- Transactional user registration
- Duplicate email and username validation
- Registration API endpoint
- Registration service layer
- Repository and service unit tests
- JWT access and refresh token generation
- Login service implementation
- Secure login API endpoint
- JWT validation
- Login API and service tests

---

## Future Development

The project will continue with the implementation of:

- User management APIs
- Role-based authorization
- Service layer
- Skill assessment engine
- Personalized learning recommendations
- Redis caching
- Celery background workers
- Leaderboards
- Notifications
- Docker deployment
- GitHub Actions CI/CD
- Monitoring and observability