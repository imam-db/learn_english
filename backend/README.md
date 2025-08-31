# Backend - FastAPI Application

English Learning Platform backend built with FastAPI, PostgreSQL, and Redis.

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache**: Redis 7+
- **Authentication**: JWT with bcrypt
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: Pytest with async support
- **Background Tasks**: Celery

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   │   ├── v1/           # API version 1
│   │   └── deps.py       # Dependencies
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings and configuration
│   │   ├── security.py   # Authentication and security
│   │   └── database.py   # Database connection
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic services
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI application entry point
├── tests/                # Test files
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
└── Dockerfile           # Docker configuration
```

## Development Setup

1. **Install Dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create new migration
   alembic revision --autogenerate -m "description"
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## API Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Security scan
bandit -r app/

# Type checking
mypy app/
```