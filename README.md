# English Learning Platform MVP

Bank Soal + Buku Digital Bahasa Inggris - An Indonesian English learning platform that combines interactive digital textbooks with a comprehensive question bank.

## Project Structure

```
├── backend/          # FastAPI backend application
├── frontend/         # Next.js frontend application
├── docker/           # Docker configuration files
├── .github/          # GitHub Actions CI/CD workflows
├── docs/             # Project documentation
└── scripts/          # Development and deployment scripts
```

## Quick Start

1. **Prerequisites**
   - Docker and Docker Compose
   - Node.js 18+ (for frontend development)
   - Python 3.11+ (for backend development)

2. **Development Setup**
   ```bash
   # Clone and setup
   git clone <repository-url>
   cd english-learning-platform

   # Start development environment
   docker-compose up -d

   # Backend development
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload

   # Frontend development
   cd frontend
   npm install
   npm run dev
   ```

3. **Access Applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

## Development Workflow

- **Code Quality**: Pre-commit hooks with Black, Flake8, ESLint, Prettier
- **Testing**: Pytest for backend, Jest/Playwright for frontend
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Documentation**: OpenAPI for backend, Storybook for frontend components

## Environment Configuration

The application supports multiple deployment stages:
- `development` - Local development with hot reload
- `staging` - Pre-production testing environment
- `production` - Production deployment

See individual README files in `backend/` and `frontend/` directories for detailed setup instructions.