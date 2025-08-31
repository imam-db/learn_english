"""
Simple authentication system test
"""

import asyncio
import pytest
from app.core.security import (
    get_password_hash, verify_password, 
    create_access_token, verify_token,
    generate_verification_token
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    
    # Verification should work
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail
    assert verify_password("WrongPassword", hashed) is False
    print("✓ Password hashing test passed")


def test_token_generation():
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
    print("✓ Token generation test passed")


def test_verification_token():
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
    print("✓ Verification token test passed")


if __name__ == "__main__":
    test_password_hashing()
    test_token_generation()
    test_verification_token()
    print("\n🎉 All authentication security tests passed!")