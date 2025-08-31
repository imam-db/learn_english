#!/bin/bash

# Development Environment Setup Script
# This script sets up the complete development environment for the English Learning Platform

set -e  # Exit on any error

echo "🚀 Setting up English Learning Platform development environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ All prerequisites are installed"

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from example"
else
    echo "ℹ️  backend/.env already exists"
fi

if [ ! -f "frontend/.env.local" ]; then
    cp frontend/.env.example frontend/.env.local
    echo "✅ Created frontend/.env.local from example"
else
    echo "ℹ️  frontend/.env.local already exists"
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Setup backend
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "✅ Installed Python dependencies"

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head
echo "✅ Database migrations completed"

cd ..

# Setup frontend
echo "⚛️  Setting up frontend..."
cd frontend

# Install dependencies
npm install
echo "✅ Installed Node.js dependencies"

cd ..

# Setup pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
cd backend
source venv/bin/activate
pre-commit install
cd ..

echo "🎉 Development environment setup completed!"
echo ""
echo "📚 Next steps:"
echo "1. Start the development servers:"
echo "   Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "2. Or use Docker Compose:"
echo "   docker-compose up"
echo ""
echo "3. Access the applications:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🚀"