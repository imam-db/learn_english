"""
Minimal authentication router for testing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    result = await auth_service.register_user(user_data)
    
    # Don't return verification token in production
    verification_token = result.pop("verification_token", None)
    
    return {
        "message": "User registered successfully. Please check your email for verification.",
        "user": result["user"],
        "tokens": result["tokens"]
    }


@router.post("/login")
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access tokens"""
    auth_service = AuthService(db)
    result = await auth_service.authenticate_user(login_data)
    
    return {
        "message": "Login successful",
        "user": result["user"],
        "tokens": result["tokens"]
    }


@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Auth router is working!"}