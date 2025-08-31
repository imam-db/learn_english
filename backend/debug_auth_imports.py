"""
Debug auth imports
"""

print("Testing auth.py imports one by one...")

try:
    from typing import Dict, Any
    print("✓ typing imports")
except Exception as e:
    print(f"✗ typing imports: {e}")

try:
    from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
    print("✓ FastAPI imports")
except Exception as e:
    print(f"✗ FastAPI imports: {e}")

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    print("✓ SQLAlchemy imports")
except Exception as e:
    print(f"✗ SQLAlchemy imports: {e}")

try:
    from app.core.database import get_db
    print("✓ Database imports")
except Exception as e:
    print(f"✗ Database imports: {e}")

try:
    from app.core.dependencies import (
        get_current_user, get_current_verified_user, 
        get_current_user_token, AuthDependencies
    )
    print("✓ Dependencies imports")
except Exception as e:
    print(f"✗ Dependencies imports: {e}")

try:
    from app.services.auth_service import AuthService
    print("✓ AuthService import")
except Exception as e:
    print(f"✗ AuthService import: {e}")

try:
    from app.schemas.auth import (
        UserCreate, UserLogin, UserResponse, UserUpdate,
        UserPreferencesUpdate, UserPreferencesResponse,
        Token, PasswordReset, PasswordResetConfirm,
        EmailVerification, ChangePassword
    )
    print("✓ Schema imports")
except Exception as e:
    print(f"✗ Schema imports: {e}")

try:
    from app.models.user import User
    print("✓ User model import")
except Exception as e:
    print(f"✗ User model import: {e}")

try:
    import logging
    print("✓ Logging import")
except Exception as e:
    print(f"✗ Logging import: {e}")

print("\nTesting router creation...")
try:
    from fastapi import APIRouter
    router = APIRouter(prefix="/auth", tags=["Authentication"])
    print(f"✓ Router created: {router}")
except Exception as e:
    print(f"✗ Router creation failed: {e}")

print("\nTesting full auth module execution...")
try:
    with open('app/api/v1/auth.py', 'r') as f:
        content = f.read()
    
    # Create a namespace to execute the code
    namespace = {}
    exec(content, namespace)
    
    if 'router' in namespace:
        print(f"✓ Router found in executed namespace: {namespace['router']}")
    else:
        print("✗ Router not found in executed namespace")
        print(f"Available names: {[name for name in namespace.keys() if not name.startswith('_')]}")
        
except Exception as e:
    print(f"✗ Auth module execution failed: {e}")
    import traceback
    traceback.print_exc()