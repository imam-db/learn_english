"""
Test imports
"""

try:
    print("Testing individual imports...")
    
    from fastapi import APIRouter
    print("✓ FastAPI imported")
    
    from app.core.database import get_db
    print("✓ Database imported")
    
    from app.schemas.auth import UserCreate
    print("✓ Schemas imported")
    
    from app.services.auth_service import AuthService
    print("✓ AuthService imported")
    
    from app.core.dependencies import get_current_user
    print("✓ Dependencies imported")
    
    print("\nTesting auth module...")
    import app.api.v1.auth as auth_module
    print("✓ Auth module imported")
    
    if hasattr(auth_module, 'router'):
        print("✓ Router found in auth module")
    else:
        print("✗ Router not found in auth module")
        print("Available attributes:", [attr for attr in dir(auth_module) if not attr.startswith('_')])
    
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()