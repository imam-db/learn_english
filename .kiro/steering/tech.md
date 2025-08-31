# Technology Stack & Development Guidelines

## Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with Next.js, TypeScript
- **Database**: PostgreSQL 15+ (primary), Redis 7+ (caching/sessions)
- **Infrastructure**: Kubernetes on AWS/GCP, Terraform for IaC
- **Monitoring**: Prometheus + Grafana, ELK stack for logging

## Architecture Patterns
- **API-First Design**: RESTful APIs with OpenAPI documentation
- **Microservices Ready**: Modular monolith that can split into services
- **Event-Driven**: Kafka for real-time analytics and user events
- **Caching Strategy**: Multi-layer (CDN, Application, Database)
- **Mobile-First**: PWA with offline capability

## Development Standards
- **Code Coverage**: Minimum 85% for unit tests, 75% for integration tests
- **Performance**: API response time p95 < 400ms, page load < 2s on 3G
- **Security**: OWASP compliance, automated vulnerability scanning
- **Accessibility**: WCAG 2.1 AA compliance

## Common Commands
```bash
# Development setup
pip install -r requirements.txt
npm install
docker-compose up -d  # Start local services

# Testing
pytest tests/unit --cov=src --cov-fail-under=85
pytest tests/integration
npm run test:e2e

# Code quality
black src/  # Code formatting
flake8 src/  # Linting
bandit -r src/  # Security scan

# Database
alembic upgrade head  # Run migrations
alembic revision --autogenerate -m "description"  # Create migration

# Deployment
kubectl apply -f k8s/
terraform plan && terraform apply
```

## Content Validation
- **Automated Linting**: Grammar, CEFR level alignment, format validation
- **Expert Review**: Native speaker validation, pedagogical soundness
- **User Testing**: Comprehension and difficulty calibration

## Performance Requirements
- Mobile-optimized: Touch targets ≥44px, responsive design
- Offline support: Core lessons downloadable
- Load time: < 2s on 3G connections
- Scalability: Auto-scaling based on CPU/memory usage