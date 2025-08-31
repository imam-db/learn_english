"""
FastAPI application entry point for English Learning Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="English Learning Platform API - Bank Soal + Buku Digital Bahasa Inggris",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "English Learning Platform API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
        }
    )


# Include API routers when they are created
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )