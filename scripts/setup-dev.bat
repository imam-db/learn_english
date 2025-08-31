@echo off
REM Development Environment Setup Script for Windows
REM This script sets up the complete development environment for the English Learning Platform

echo 🚀 Setting up English Learning Platform development environment...

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.11+ first.
    exit /b 1
)

echo ✅ All prerequisites are installed

REM Create environment files if they don't exist
echo 📝 Setting up environment files...

if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo ✅ Created backend\.env from example
) else (
    echo ℹ️  backend\.env already exists
)

if not exist "frontend\.env.local" (
    copy "frontend\.env.example" "frontend\.env.local"
    echo ✅ Created frontend\.env.local from example
) else (
    echo ℹ️  frontend\.env.local already exists
)

REM Start Docker services
echo 🐳 Starting Docker services...
docker-compose up -d postgres redis

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Setup backend
echo 🐍 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
    echo ✅ Created Python virtual environment
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo ✅ Installed Python dependencies

REM Run database migrations
echo 🗄️  Running database migrations...
alembic upgrade head
echo ✅ Database migrations completed

cd ..

REM Setup frontend
echo ⚛️  Setting up frontend...
cd frontend

REM Install dependencies
npm install
echo ✅ Installed Node.js dependencies

cd ..

REM Setup pre-commit hooks
echo 🔧 Setting up pre-commit hooks...
cd backend
call venv\Scripts\activate.bat
pre-commit install
cd ..

echo 🎉 Development environment setup completed!
echo.
echo 📚 Next steps:
echo 1. Start the development servers:
echo    Backend:  cd backend ^&^& venv\Scripts\activate.bat ^&^& uvicorn app.main:app --reload
echo    Frontend: cd frontend ^&^& npm run dev
echo.
echo 2. Or use Docker Compose:
echo    docker-compose up
echo.
echo 3. Access the applications:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Happy coding! 🚀

pause