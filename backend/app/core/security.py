"""
Security utilities for authentication and authorization
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def generate_verification_token() -> str:
    """
    Generate a secure random token for email verification or password reset
    
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)


def create_token_response(user_id: str, email: str, scopes: Optional[list] = None) -> Dict[str, Any]:
    """
    Create a complete token response with access and refresh tokens
    
    Args:
        user_id: User ID
        email: User email
        scopes: User scopes/permissions
        
    Returns:
        Token response dictionary
    """
    if scopes is None:
        scopes = []
    
    # Create token data
    token_data = {
        "sub": user_id,
        "email": email,
        "scopes": scopes
    }
    
    # Create tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user_id, "email": email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


def extract_user_from_token(token: str) -> Dict[str, Any]:
    """
    Extract user information from a valid token
    
    Args:
        token: JWT token
        
    Returns:
        User information from token
    """
    payload = verify_token(token, "access")
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "scopes": payload.get("scopes", [])
    }


class RoleChecker:
    """
    Role-based access control checker
    """
    
    # Define role hierarchy (higher number = more permissions)
    ROLE_HIERARCHY = {
        "user": 1,
        "premium_user": 2,
        "author": 3,
        "moderator": 4,
        "admin": 5,
        "super_admin": 6
    }
    
    def __init__(self, required_role: str):
        self.required_role = required_role
        self.required_level = self.ROLE_HIERARCHY.get(required_role, 0)
    
    def __call__(self, user_scopes: list) -> bool:
        """
        Check if user has required role
        
        Args:
            user_scopes: List of user scopes/roles
            
        Returns:
            True if user has required role or higher
        """
        user_level = 0
        for scope in user_scopes:
            scope_level = self.ROLE_HIERARCHY.get(scope, 0)
            user_level = max(user_level, scope_level)
        
        return user_level >= self.required_level


def get_user_roles(is_premium: bool = False, is_staff: bool = False, is_admin: bool = False) -> list:
    """
    Get user roles based on their status
    
    Args:
        is_premium: Whether user has premium subscription
        is_staff: Whether user is staff (author/moderator)
        is_admin: Whether user is admin
        
    Returns:
        List of user roles/scopes
    """
    roles = ["user"]
    
    if is_premium:
        roles.append("premium_user")
    
    if is_staff:
        roles.append("author")
    
    if is_admin:
        roles.extend(["moderator", "admin"])
    
    return roles