"""
API v1 package
"""

from fastapi import APIRouter

# Create main API v1 router
api_router = APIRouter()

# Lazy import to avoid circular imports
def get_api_router():
    # Import routers only when needed
    try:
        from . import auth_complete as auth
        if hasattr(auth, 'router'):
            api_router.include_router(auth.router)
            print(f"✓ Auth router included with {len(auth.router.routes)} routes")
        else:
            print("✗ No router found in auth module")
    except ImportError as e:
        print(f"Warning: Could not import auth router: {e}")
    
    # Add other routers here as they are implemented
    # from . import content
    # api_router.include_router(content.router)
    
    return api_router