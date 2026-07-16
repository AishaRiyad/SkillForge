# SkillForge

SkillForge is a gamified learning and skill development platform where users complete challenges, earn experience points, unlock achievements, maintain daily streaks, and compete on leaderboards.

The repository is organized as a monorepo containing a FastAPI backend and a future frontend application.

## Core Features

* User registration and authentication
* Role-based authorization
* Skill categories and challenges
* Challenge submissions and evaluation
* Experience points and levels
* Achievements and badges
* Daily and weekly missions
* User streaks
* Global and category leaderboards
* Notifications
* User progress reports
* Admin dashboard APIs
* Caching and rate limiting
* Background task processing

## Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

### Database

* Supabase
* PostgreSQL
* Row Level Security

### Background Processing

* Redis
* Celery
* Celery Beat

### Infrastructure and Testing

* Docker
* Docker Compose
* Pytest
* GitHub Actions
* Ruff
* Mypy

## Repository Structure

```text
SkillForge/
├── server/                 # FastAPI backend
├── client/                 # Future frontend application
├── docs/                   # Project documentation
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Project overview and documentation
```

## Project Status

The FastAPI backend has been initialized with versioned routing,
environment-based settings, and a health-check endpoint.

## Development Roadmap

- [x] Select the project idea
- [x] Create the initial repository structure
- [x] Initialize the FastAPI backend
- [x] Configure application settings
- [x] Configure initial testing tools
- [x] Configure linting and type checking
- [x] Configure Supabase PostgreSQL
- [x] Configure the Alembic migration environment
- [x] Add initial user and profile database models
- [x] Implement user registration
- [x] Implement login and JWT authentication
- [ ] Implement roles and permissions
- [ ] Implement categories
- [ ] Implement challenges
- [ ] Implement submissions
- [ ] Implement the XP and level system
- [ ] Implement achievements and badges
- [ ] Implement missions and streaks
- [ ] Configure Redis
- [ ] Implement leaderboards
- [ ] Configure Celery workers
- [ ] Configure Celery Beat scheduled tasks
- [ ] Add notifications
- [ ] Add user progress reports
- [ ] Add admin dashboard APIs
- [ ] Add audit logs
- [ ] Add automated tests
- [ ] Add Docker Compose services
- [ ] Add continuous integration with GitHub Actions
- [ ] Build the frontend application

## Project Documentation

Additional project documentation is available in the [`docs`](./docs) directory.

The project scope can be found in:

```text
docs/project-scope.md
```

## Main User Roles

### User

A regular user can:

* Create and manage a personal profile
* Browse available challenges
* Submit challenge answers
* Earn experience points
* Progress through levels
* Complete daily and weekly missions
* Unlock achievements and badges
* View personal progress
* Compete on leaderboards
* Receive notifications

### Moderator

A moderator can:

* Review reported content
* Review selected submissions
* Manage inappropriate or invalid challenges

### Admin

An administrator can:

* Manage users and roles
* Create and manage categories
* Create and manage challenges
* Create achievements and missions
* View platform statistics
* Review audit logs

## Technical Goals

SkillForge aims to include the following technical practices:

* Asynchronous FastAPI endpoints
* Pydantic request and response validation
* JWT authentication
* Role-based authorization
* Dependency injection
* Custom exception handling
* Middleware and structured logging
* PostgreSQL constraints and indexes
* Supabase Row Level Security
* Database migrations with Alembic
* Redis caching
* Redis rate limiting
* Redis leaderboards
* Celery background workers
* Celery scheduled tasks
* Unit and integration testing
* Docker Compose development environment
* Continuous integration using GitHub Actions

## Getting Started

### Prerequisites

Before running the project, make sure the following tools are installed:

* Python
* Git
* Docker
* Docker Compose
* PostgreSQL or a Supabase account
* Redis

### Clone the Repository

```bash
git clone https://github.com/your-username/SkillForge.git
cd SkillForge
```

Replace `your-username` with your GitHub username.

### Backend Setup

Navigate to the backend directory:

```bash
cd server
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Activate it using Git Bash:

```bash
source venv/Scripts/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

After starting the server, the API documentation should be available at:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

The project will use environment variables for configuration.

Create a `.env` file inside the backend directory and add the required settings.

Example:

```env
APP_NAME=SkillForge
APP_ENV=development
DEBUG=True

DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0
```

Do not commit the `.env` file to GitHub.

## Testing

The project uses Pytest for unit and integration testing.

Run the tests using:

```bash
pytest
```

Run the tests with detailed output:

```bash
pytest -v
```

## Docker

The project will support Docker and Docker Compose.

To start the project services:

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

## API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Contribution

This project is currently under development.

Contributions, suggestions, and feedback are welcome.

To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Push the branch.
6. Open a pull request.

Example:

```bash
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

## Author

**Aesha AbuJeeb**

Software Engineering Student and SkillForge Project Developer.

## License

This project is developed for educational and portfolio purposes.

Copyright © 2026 Aesha.
