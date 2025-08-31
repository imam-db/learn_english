"""
Debug router setup
"""

from app.main import app

print("App routes:")
for route in app.routes:
    print(f"  {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")

print("\nTesting auth module import:")
try:
    import app.api.v1.auth as auth_module
    print(f"Auth module imported: {auth_module}")
    if hasattr(auth_module, 'router'):
        print(f"Router found: {auth_module.router}")
        print(f"Router routes: {len(auth_module.router.routes)}")
        for route in auth_module.router.routes:
            print(f"  {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")
    else:
        print("No router found in auth module")
        print(f"Available attributes: {[attr for attr in dir(auth_module) if not attr.startswith('_')]}")
except Exception as e:
    print(f"Error importing auth module: {e}")
    import traceback
    traceback.print_exc()