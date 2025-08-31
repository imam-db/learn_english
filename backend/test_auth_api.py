"""
Test authentication API endpoints
"""

import asyncio
import httpx
import json
from app.main import app


async def test_auth_endpoints():
    """Test authentication API endpoints"""
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        
        print("🧪 Testing Authentication API Endpoints")
        print("=" * 50)
        
        # Test user registration
        print("\n1. Testing User Registration...")
        registration_data = {
            "email": "test@example.com",
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
                print(f"   User ID: {data['user']['id']}")
                print(f"   Email: {data['user']['email']}")
                
                # Store tokens for further testing
                access_token = data["tokens"]["access_token"]
                refresh_token = data["tokens"]["refresh_token"]
                
            else:
                print(f"   ✗ Registration failed: {response.text}")
                return
                
        except Exception as e:
            print(f"   ✗ Registration error: {e}")
            return
        
        # Test user login
        print("\n2. Testing User Login...")
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        try:
            response = await client.post("/api/v1/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Login successful")
                print(f"   User: {data['user']['full_name']}")
                
                # Update tokens from login
                access_token = data["tokens"]["access_token"]
                refresh_token = data["tokens"]["refresh_token"]
                
            else:
                print(f"   ✗ Login failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Login error: {e}")
        
        # Test getting current user profile
        print("\n3. Testing Get Current User Profile...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get("/api/v1/auth/me", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Profile retrieval successful")
                print(f"   Name: {data['full_name']}")
                print(f"   Level: {data['current_level']}")
                print(f"   Verified: {data['is_verified']}")
                
            else:
                print(f"   ✗ Profile retrieval failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Profile retrieval error: {e}")
        
        # Test updating user profile
        print("\n4. Testing Update User Profile...")
        update_data = {
            "full_name": "Updated Test User",
            "current_level": "A2"
        }
        
        try:
            response = await client.put("/api/v1/auth/me", json=update_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Profile update successful")
                print(f"   New name: {data['full_name']}")
                print(f"   New level: {data['current_level']}")
                
            else:
                print(f"   ✗ Profile update failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Profile update error: {e}")
        
        # Test getting user preferences
        print("\n5. Testing Get User Preferences...")
        
        try:
            response = await client.get("/api/v1/auth/me/preferences", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Preferences retrieval successful")
                print(f"   Language: {data['language_interface']}")
                print(f"   Daily goal: {data['daily_goal']}")
                print(f"   Theme: {data['theme']}")
                
            else:
                print(f"   ✗ Preferences retrieval failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Preferences retrieval error: {e}")
        
        # Test updating user preferences
        print("\n6. Testing Update User Preferences...")
        preferences_update = {
            "language_interface": "en",
            "daily_goal": 5,
            "theme": "dark"
        }
        
        try:
            response = await client.put("/api/v1/auth/me/preferences", json=preferences_update, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Preferences update successful")
                print(f"   New language: {data['language_interface']}")
                print(f"   New daily goal: {data['daily_goal']}")
                print(f"   New theme: {data['theme']}")
                
            else:
                print(f"   ✗ Preferences update failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Preferences update error: {e}")
        
        # Test token refresh
        print("\n7. Testing Token Refresh...")
        
        try:
            response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Token refresh successful")
                print("   New tokens generated")
                
            else:
                print(f"   ✗ Token refresh failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Token refresh error: {e}")
        
        # Test logout
        print("\n8. Testing Logout...")
        
        try:
            response = await client.post("/api/v1/auth/logout", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✓ Logout successful")
                print(f"   Message: {data['message']}")
                
            else:
                print(f"   ✗ Logout failed: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Logout error: {e}")
        
        # Test unauthorized access
        print("\n9. Testing Unauthorized Access...")
        
        try:
            response = await client.get("/api/v1/auth/me")  # No token
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 401:
                print("   ✓ Unauthorized access properly blocked")
                
            else:
                print(f"   ✗ Unauthorized access not blocked: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Unauthorized access test error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Authentication API testing completed!")


if __name__ == "__main__":
    asyncio.run(test_auth_endpoints())