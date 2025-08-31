"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import extract_user_from_token, RoleChecker
from app.services.auth_service import AuthService
from app.models.user import User


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Extract and validate current user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User information from token
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials
        user_info = extract_user_from_token(token)
        return user_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_token: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user from database using token information
    
    Args:
        user_token: User information from token
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If user not found or inactive
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_token["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user for clarity)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current active user
    """
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current verified user (email verified)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current verified user
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


async def get_current_premium_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """
    Get current premium user
    
    Args:
        current_user: Current verified user
        
    Returns:
        Current premium user
        
    Raises:
        HTTPException: If user is not premium
    """
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    
    return current_user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control
    
    Args:
        required_role: Required role for access
        
    Returns:
        Dependency function that checks user role
    """
    role_checker = RoleChecker(required_role)
    
    async def check_role(
        user_token: Dict[str, Any] = Depends(get_current_user_token)
    ) -> Dict[str, Any]:
        """
        Check if user has required role
        
        Args:
            user_token: User information from token
            
        Returns:
            User token information if authorized
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_scopes = user_token.get("scopes", [])
        
        if not role_checker(user_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return user_token
    
    return check_role


def require_admin():
    """
    Dependency for admin-only access
    
    Returns:
        Admin role dependency
    """
    return require_role("admin")


def require_author():
    """
    Dependency for author-level access (content creators)
    
    Returns:
        Author role dependency
    """
    return require_role("author")


def require_premium():
    """
    Dependency for premium user access
    
    Returns:
        Premium user dependency
    """
    return require_role("premium_user")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    Useful for endpoints that work for both authenticated and anonymous users
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_info = extract_user_from_token(token)
        
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_info["user_id"])
        
        if user and user.is_active:
            return user
        
    except Exception:
        # Silently fail for optional authentication
        pass
    
    return None


class AuthDependencies:
    """
    Collection of authentication dependencies for easy import
    """
    
    # Basic authentication
    current_user_token = Depends(get_current_user_token)
    current_user = Depends(get_current_user)
    current_active_user = Depends(get_current_active_user)
    current_verified_user = Depends(get_current_verified_user)
    current_premium_user = Depends(get_current_premium_user)
    optional_user = Depends(get_optional_user)
    
    # Role-based access
    admin_required = require_admin()
    author_required = require_author()
    premium_required = require_premium()
    
    @staticmethod
    def role_required(role: str):
        """
        Create a role requirement dependency
        
        Args:
            role: Required role
            
        Returns:
            Role dependency
        """
        return Depends(require_role(role))