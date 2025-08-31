"""
Test minimal authentication API
"""

import asyncio
import httpx
from app.main import app


async def test_minimal_auth():
    """Test minimal authentication endpoints"""
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        
        print("🧪 Testing Minimal Authentication API")
        print("=" * 40)
        
        # Test auth test endpoint
        print("\n1. Testing Auth Test Endpoint...")
        try:
            response = await client.get("/api/v1/auth/test")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Response: {data['message']}")
            else:
                print(f"   ✗ Failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test user registration
        print("\n2. Testing User Registration...")
        registration_data = {
            "email": f"test{asyncio.get_event_loop().time()}@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "full_name": "Test User",
            "current_level": "A1",
            "learning_goals": ["grammar", "vocabulary"]
        }
        
        try:
            response = await client.post("/api/v1/auth/register", json=registration_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("   ✓ Registration successful")
                print(f"   User: {data['user']['full_name']}")
                print(f"   Email: {data['user']['email']}")
                
                # Store tokens for login test
                access_token = data["tokens"]["access_token"]
                
            else:
                print(f"   ✗ Registration failed: {response.text}")
                return
                
        except Exception as e:
            print(f"   ✗ Registration error: {e}")
            return
        
        # Test user login
        print("\n3. Testing User Login...")
        login_data = {
            "email": registration_data["email"],
            "password": "TestPassword123"
        }
        
        try:
            response = await client.post("/api/v1/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Login successful")
                print(f"   Message: {data['message']}")
                print(f"   User: {data['user']['full_name']}")
                
            else:
                print(f"   ✗ Login failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Login error: {e}")
        
        print("\n" + "=" * 40)
        print("🎉 Minimal authentication testing completed!")


if __name__ == "__main__":
    asyncio.run(test_minimal_auth())