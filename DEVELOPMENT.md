# Development Guide

This document provides comprehensive instructions for setting up and developing the English Learning Platform.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (latest version)
- **Node.js** 18+ with npm
- **Python** 3.11+
- **Git**

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd english-learning-platform
```

### 2. Automated Setup (Recommended)

**For Linux/macOS:**
```bash
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh
```

**For Windows:**
```cmd
scripts\setup-dev.bat
```

### 3. Manual Setup

If the automated setup doesn't work, follow these manual steps:

#### Environment Files
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# Frontend  
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with your configuration
```

#### Start Infrastructure Services
```bash
docker-compose up -d postgres redis
```

#### Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Development Workflow

### Running the Application

#### Option 1: Docker Compose (Full Stack)
```bash
docker-compose up
```

#### Option 2: Local Development
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Code Quality

#### Backend (Python)
```bash
cd backend
source venv/bin/activate

# Format code
black app/ tests/
isort app/ tests/

# Lint code
flake8 app/ tests/
mypy app/

# Security scan
bandit -r app/

# Run tests
pytest tests/ --cov=app --cov-report=html
```

#### Frontend (TypeScript/React)
```bash
cd frontend

# Format code
npm run format

# Lint code
npm run lint
npm run type-check

# Run tests
npm run test
npm run test:coverage

# E2E tests
npm run test:e2e
```

### Database Management

#### Migrations
```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

#### Database Reset
```bash
# Stop containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Restart
docker-compose up -d
```

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/            # Backend tests
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── lib/          # Utilities
│   │   └── types/        # TypeScript types
│   ├── public/           # Static assets
│   └── package.json      # Node.js dependencies
├── docker/               # Docker configurations
├── .github/              # CI/CD workflows
└── scripts/              # Development scripts
```

## Testing

### Backend Testing
```bash
cd backend
source venv/bin/activate

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=app --cov-report=html --cov-fail-under=85
```

### Frontend Testing
```bash
cd frontend

# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Visual regression tests (if configured)
npm run test:visual
```

### Full E2E Testing
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run E2E tests
cd frontend
npm run test:e2e

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## Debugging

### Backend Debugging
```bash
# Enable debug mode in .env
DEBUG=true

# Run with debugger
python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload
```

### Frontend Debugging
```bash
# Enable debug mode
NODE_ENV=development

# Run with debugging
npm run dev
```

### Database Debugging
```bash
# Connect to PostgreSQL
docker exec -it english_learning_postgres psql -U postgres -d english_learning

# Connect to Redis
docker exec -it english_learning_redis redis-cli
```

## Performance Monitoring

### Backend Performance
```bash
# Install performance tools
pip install py-spy memory-profiler

# Profile CPU usage
py-spy record -o profile.svg -- python -m uvicorn app.main:app

# Profile memory usage
mprof run uvicorn app.main:app
mprof plot
```

### Frontend Performance
```bash
# Analyze bundle size
npm run analyze

# Lighthouse CI (if configured)
npm run lighthouse
```

## Deployment

### Staging Deployment
```bash
# Build and push images
docker build -t english-learning-backend:staging ./backend
docker build -t english-learning-frontend:staging ./frontend

# Deploy to staging (implementation depends on infrastructure)
# kubectl apply -f k8s/staging/
```

### Production Deployment
```bash
# Automated via GitHub Actions on main branch push
git push origin main
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :3000  # or :8000, :5432, :6379

# Kill process
kill -9 <PID>
```

#### Docker Issues
```bash
# Clean up Docker
docker system prune -a

# Rebuild containers
docker-compose build --no-cache
```

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs english_learning_postgres
```

#### Node Modules Issues
```bash
# Clean install
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Python Environment Issues
```bash
# Recreate virtual environment
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

1. Check the logs: `docker-compose logs <service-name>`
2. Verify environment variables in `.env` files
3. Ensure all prerequisites are installed
4. Check if ports are available
5. Review the GitHub Issues for known problems

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes following the code style guidelines
3. Run tests: `npm run test` and `pytest`
4. Commit with conventional commits: `git commit -m "feat: add new feature"`
5. Push and create a Pull Request

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)