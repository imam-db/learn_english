"""
Comprehensive test suite for the authentication system
Tests all authentication and authorization functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import json

from app.main import app
from app.core.database import get_db
from app.core.config import settings
from app.models.base import Base
from app.models.user import User, UserPreference
from app.services.auth_service import AuthService
from app.core.security import (
    create_access_token, create_refresh_token, verify_token,
    get_password_hash, verify_password, generate_verification_token
)


# Test database URL (using in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database):
    """Create a test database session"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Create test client with database dependency override"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_service(db_session):
    """Create AuthService instance for testing"""
    return AuthService(db_session)


@pytest.fixture
async def test_user_data():
    """Test user registration data"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "confirm_password": "TestPassword123",
        "full_name": "Test User",
        "current_level": "A1",
        "learning_goals": ["grammar", "vocabulary"]
    }


@pytest.fixture
async def created_user(auth_service, test_user_data):
    """Create a test user in the database"""
    from app.schemas.auth import UserCreate
    user_create = UserCreate(**test_user_data)
    result = await auth_service.register_user(user_create)
    return result


class TestSecurityFunctions:
    """Test core security functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password("WrongPassword", hashed) is False
    
    def test_token_generation_and_verification(self):
        """Test JWT token generation and verification"""
        user_data = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "scopes": ["user"]
        }
        
        # Test access token
        access_token = create_access_token(user_data)
        assert access_token is not None
        
        payload = verify_token(access_token, "access")
        assert payload["sub"] == user_data["sub"]
        assert payload["email"] == user_data["email"]
        assert payload["type"] == "access"
        
        # Test refresh token
        refresh_token = create_refresh_token({"sub": user_data["sub"], "email": user_data["email"]})
        assert refresh_token is not None
        
        refresh_payload = verify_token(refresh_token, "refresh")
        assert refresh_payload["sub"] == user_data["sub"]
        assert refresh_payload["type"] == "refresh"
    
    def test_verification_token_generation(self):
        """Test verification token generation"""
        token1 = generate_verification_token()
        token2 = generate_verification_token()
        
        # Tokens should be different
        assert token1 != token2
        
        # Tokens should be strings
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        
        # Tokens should have reasonable length
        assert len(token1) > 20
        assert len(token2) > 20


class TestAuthService:
    """Test AuthService functionality"""
    
    async def test_user_registration(self, auth_service, test_user_data):
        """Test user registration"""
        from app.schemas.auth import UserCreate
        
        user_create = UserCreate(**test_user_data)
        result = await auth_service.register_user(user_create)
        
        # Check result structure
        assert "user" in result
        assert "tokens" in result
        assert "verification_token" in result
        
        # Check user data
        user = result["user"]
        assert user["email"] == test_user_data["email"]
        assert user["full_name"] == test_user_data["full_name"]
        assert user["current_level"] == test_user_data["current_level"]
        assert user["learning_goals"] == test_user_data["learning_goals"]
        assert user["is_active"] is True
        assert user["is_verified"] is False  # Should require verification
        assert user["is_premium"] is False
        
        # Check tokens
        tokens = result["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Verify tokens are valid
        access_payload = verify_token(tokens["access_token"], "access")
        assert access_payload["email"] == test_user_data["email"]
    
    async def test_duplicate_email_registration(self, auth_service, test_user_data):
        """Test that duplicate email registration fails"""
        from app.schemas.auth import UserCreate
        from fastapi import HTTPException
        
        # Register first user
        user_create = UserCreate(**test_user_data)
        await auth_service.register_user(user_create)
        
        # Try to register with same email
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register_user(user_create)
        
        assert exc_info.value.status_code == 400
        assert "already registered" in str(exc_info.value.detail)
    
    async def test_user_authentication(self, auth_service, created_user):
        """Test user authentication"""
        from app.schemas.auth import UserLogin
        
        login_data = UserLogin(
            email=created_user["user"]["email"],
            password="TestPassword123"
        )
        
        result = await auth_service.authenticate_user(login_data)
        
        # Check result structure
        assert "user" in result
        assert "tokens" in result
        
        # Check user data matches
        user = result["user"]
        assert user["email"] == created_user["user"]["email"]
        assert user["id"] == created_user["user"]["id"]
        
        # Check tokens are valid
        tokens = result["tokens"]
        access_payload = verify_token(tokens["access_token"], "access")
        assert access_payload["email"] == user["email"]
    
    async def test_invalid_login(self, auth_service, created_user):
        """Test authentication with invalid credentials"""
        from app.schemas.auth import UserLogin
        from fastapi import HTTPException
        
        # Test wrong password
        login_data = UserLogin(
            email=created_user["user"]["email"],
            password="WrongPassword"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(login_data)
        
        assert exc_info.value.status_code == 401
        
        # Test non-existent email
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="TestPassword123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(login_data)
        
        assert exc_info.value.status_code == 401
    
    async def test_get_user_by_id(self, auth_service, created_user):
        """Test getting user by ID"""
        user_id = created_user["user"]["id"]
        user = await auth_service.get_user_by_id(user_id)
        
        assert user is not None
        assert str(user.id) == user_id
        assert user.email == created_user["user"]["email"]
    
    async def test_get_user_by_email(self, auth_service, created_user):
        """Test getting user by email"""
        email = created_user["user"]["email"]
        user = await auth_service.get_user_by_email(email)
        
        assert user is not None
        assert user.email == email
        assert str(user.id) == created_user["user"]["id"]
    
    async def test_update_user_profile(self, auth_service, created_user):
        """Test updating user profile"""
        from app.schemas.auth import UserUpdate
        
        user_id = created_user["user"]["id"]
        update_data = UserUpdate(
            full_name="Updated Name",
            current_level="A2",
            learning_goals=["reading", "writing"]
        )
        
        result = await auth_service.update_user_profile(user_id, update_data)
        
        assert result["full_name"] == "Updated Name"
        assert result["current_level"] == "A2"
        assert result["learning_goals"] == ["reading", "writing"]
    
    async def test_password_reset_flow(self, auth_service, created_user):
        """Test password reset functionality"""
        from app.schemas.auth import PasswordResetConfirm
        
        email = created_user["user"]["email"]
        
        # Request password reset
        reset_token = await auth_service.request_password_reset(email)
        assert reset_token is not None
        
        # Confirm password reset
        new_password = "NewPassword123"
        reset_data = PasswordResetConfirm(
            token=reset_token,
            new_password=new_password,
            confirm_password=new_password
        )
        
        result = await auth_service.confirm_password_reset(reset_data)
        assert "message" in result
        
        # Verify old password no longer works
        from app.schemas.auth import UserLogin
        from fastapi import HTTPException
        
        old_login = UserLogin(email=email, password="TestPassword123")
        with pytest.raises(HTTPException):
            await auth_service.authenticate_user(old_login)
        
        # Verify new password works
        new_login = UserLogin(email=email, password=new_password)
        auth_result = await auth_service.authenticate_user(new_login)
        assert "tokens" in auth_result
    
    async def test_email_verification(self, auth_service, created_user):
        """Test email verification"""
        verification_token = created_user["verification_token"]
        
        result = await auth_service.verify_email(verification_token)
        assert "message" in result
        
        # Verify user is now verified
        user_id = created_user["user"]["id"]
        user = await auth_service.get_user_by_id(user_id)
        assert user.is_verified is True
    
    async def test_change_password(self, auth_service, created_user):
        """Test changing password for authenticated user"""
        from app.schemas.auth import ChangePassword
        
        user_id = created_user["user"]["id"]
        password_data = ChangePassword(
            current_password="TestPassword123",
            new_password="NewPassword456",
            confirm_password="NewPassword456"
        )
        
        result = await auth_service.change_password(user_id, password_data)
        assert "message" in result
        
        # Verify new password works
        from app.schemas.auth import UserLogin
        email = created_user["user"]["email"]
        login_data = UserLogin(email=email, password="NewPassword456")
        auth_result = await auth_service.authenticate_user(login_data)
        assert "tokens" in auth_result
    
    async def test_refresh_token(self, auth_service, created_user):
        """Test token refresh functionality"""
        refresh_token = created_user["tokens"]["refresh_token"]
        
        new_tokens = await auth_service.refresh_token(refresh_token)
        
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["token_type"] == "bearer"
        
        # Verify new access token is valid
        access_payload = verify_token(new_tokens["access_token"], "access")
        assert access_payload["email"] == created_user["user"]["email"]


class TestAuthAPI:
    """Test authentication API endpoints"""
    
    async def test_register_endpoint(self, client, test_user_data):
        """Test user registration endpoint"""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "message" in data
        assert "user" in data
        assert "tokens" in data
        
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["full_name"] == test_user_data["full_name"]
        assert user["is_verified"] is False
    
    async def test_login_endpoint(self, client, created_user):
        """Test user login endpoint"""
        login_data = {
            "email": created_user["user"]["email"],
            "password": "TestPassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "user" in data
        assert "tokens" in data
        
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
    
    async def test_me_endpoint(self, client, created_user):
        """Test getting current user profile"""
        access_token = created_user["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == created_user["user"]["email"]
        assert data["id"] == created_user["user"]["id"]
    
    async def test_update_profile_endpoint(self, client, created_user):
        """Test updating user profile"""
        access_token = created_user["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        update_data = {
            "full_name": "Updated Name",
            "current_level": "B1"
        }
        
        response = await client.put("/api/v1/auth/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "Updated Name"
        assert data["current_level"] == "B1"
    
    async def test_preferences_endpoints(self, client, created_user):
        """Test user preferences endpoints"""
        access_token = created_user["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get preferences
        response = await client.get("/api/v1/auth/me/preferences", headers=headers)
        assert response.status_code == 200
        
        preferences = response.json()
        assert preferences["language_interface"] == "id"
        assert preferences["daily_goal"] == 3
        
        # Update preferences
        update_data = {
            "language_interface": "en",
            "daily_goal": 5,
            "theme": "dark"
        }
        
        response = await client.put("/api/v1/auth/me/preferences", json=update_data, headers=headers)
        assert response.status_code == 200
        
        updated_preferences = response.json()
        assert updated_preferences["language_interface"] == "en"
        assert updated_preferences["daily_goal"] == 5
        assert updated_preferences["theme"] == "dark"
    
    async def test_password_reset_endpoints(self, client, created_user):
        """Test password reset endpoints"""
        email = created_user["user"]["email"]
        
        # Request password reset
        response = await client.post("/api/v1/auth/password/reset/request", json={"email": email})
        assert response.status_code == 200
        
        # Note: In a real test, we'd need to capture the reset token from email
        # For now, we'll test the endpoint structure
        data = response.json()
        assert "message" in data
    
    async def test_email_verification_endpoint(self, client, created_user):
        """Test email verification endpoint"""
        verification_token = created_user["verification_token"]
        
        response = await client.post("/api/v1/auth/email/verify", json={"token": verification_token})
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
    
    async def test_refresh_token_endpoint(self, client, created_user):
        """Test token refresh endpoint"""
        refresh_token = created_user["tokens"]["refresh_token"]
        
        response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_logout_endpoint(self, client, created_user):
        """Test logout endpoint"""
        access_token = created_user["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = await client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
    
    async def test_unauthorized_access(self, client):
        """Test that protected endpoints require authentication"""
        # Try to access protected endpoint without token
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        # Try with invalid token
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    async def test_validation_errors(self, client):
        """Test input validation errors"""
        # Test registration with invalid data
        invalid_data = {
            "email": "invalid-email",
            "password": "weak",
            "confirm_password": "different",
            "full_name": "",
            "current_level": "C1"  # Invalid level
        }
        
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Test login with missing data
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    async def test_user_roles(self, auth_service, db_session):
        """Test user role assignment and checking"""
        from app.core.security import get_user_roles, RoleChecker
        
        # Test basic user roles
        roles = get_user_roles(is_premium=False, is_staff=False, is_admin=False)
        assert "user" in roles
        assert "premium_user" not in roles
        
        # Test premium user roles
        roles = get_user_roles(is_premium=True, is_staff=False, is_admin=False)
        assert "user" in roles
        assert "premium_user" in roles
        
        # Test staff roles
        roles = get_user_roles(is_premium=False, is_staff=True, is_admin=False)
        assert "user" in roles
        assert "author" in roles
        
        # Test admin roles
        roles = get_user_roles(is_premium=False, is_staff=False, is_admin=True)
        assert "user" in roles
        assert "admin" in roles
        assert "moderator" in roles
    
    async def test_role_checker(self):
        """Test RoleChecker functionality"""
        from app.core.security import RoleChecker
        
        # Test basic user access
        user_checker = RoleChecker("user")
        assert user_checker(["user"]) is True
        assert user_checker([]) is False
        
        # Test admin access
        admin_checker = RoleChecker("admin")
        assert admin_checker(["admin"]) is True
        assert admin_checker(["user"]) is False
        assert admin_checker(["user", "admin"]) is True
        
        # Test premium access
        premium_checker = RoleChecker("premium_user")
        assert premium_checker(["premium_user"]) is True
        assert premium_checker(["user"]) is False


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])