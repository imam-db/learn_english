"""
Authentication API endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user, get_current_verified_user, 
    get_current_user_token, AuthDependencies
)
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    UserPreferencesUpdate, UserPreferencesResponse,
    Token, PasswordReset, PasswordResetConfirm,
    EmailVerification, ChangePassword
)
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account
    
    - **email**: Valid email address (will be used for login)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **confirm_password**: Must match password
    - **full_name**: User's full name
    - **current_level**: CEFR level (A1, A2, B1, B2)
    - **learning_goals**: List of learning objectives
    
    Returns user data and authentication tokens.
    Email verification token is included for sending verification email.
    """
    auth_service = AuthService(db)
    result = await auth_service.register_user(user_data)
    
    # TODO: Add background task to send verification email
    # background_tasks.add_task(send_verification_email, result["user"]["email"], result["verification_token"])
    
    # Don't return verification token in production
    verification_token = result.pop("verification_token", None)
    
    logger.info(f"User registered: {result['user']['email']}")
    
    return {
        "message": "User registered successfully. Please check your email for verification.",
        "user": result["user"],
        "tokens": result["tokens"]
    }


@router.post("/login", response_model=Dict[str, Any])
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access tokens
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns user data and authentication tokens (access + refresh).
    """
    auth_service = AuthService(db)
    result = await auth_service.authenticate_user(login_data)
    
    logger.info(f"User logged in: {result['user']['email']}")
    
    return {
        "message": "Login successful",
        "user": result["user"],
        "tokens": result["tokens"]
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(refresh_token)
    
    return tokens


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user
    
    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing tokens from storage. This endpoint is provided for consistency
    and future token blacklisting implementation.
    """
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile information
    
    Returns complete user profile data for authenticated user.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        current_level=current_user.current_level,
        learning_goals=current_user.learning_goals,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_premium=current_user.is_premium,
        is_staff=current_user.is_staff,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile
    
    - **full_name**: Updated full name (optional)
    - **current_level**: Updated CEFR level (optional)
    - **learning_goals**: Updated learning goals list (optional)
    
    Returns updated user profile data.
    """
    auth_service = AuthService(db)
    updated_user = await auth_service.update_user_profile(
        str(current_user.id), 
        update_data
    )
    
    logger.info(f"User profile updated: {current_user.email}")
    
    return UserResponse(**updated_user)


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user preferences and settings
    
    Returns user preferences including interface language, notifications,
    learning settings, and other customization options.
    """
    auth_service = AuthService(db)
    preferences = await auth_service.get_user_preferences(str(current_user.id))
    
    return UserPreferencesResponse(**preferences)


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user preferences
    
    - **language_interface**: Interface language (id/en)
    - **theme**: UI theme (light/dark/auto)
    - **daily_goal**: Daily lesson goal (1-50)
    - **reminder_enabled**: Enable/disable reminders
    - **reminder_time**: Reminder time (HH:MM format)
    - **offline_content_enabled**: Enable offline content download
    - **auto_play_audio**: Auto-play audio content
    - **show_translations**: Show Indonesian translations
    - **email_notifications**: Enable email notifications
    - **push_notifications**: Enable push notifications
    
    Returns updated user preferences.
    """
    auth_service = AuthService(db)
    updated_preferences = await auth_service.update_user_preferences(
        str(current_user.id),
        preferences_data
    )
    
    logger.info(f"User preferences updated: {current_user.email}")
    
    return UserPreferencesResponse(**updated_preferences)


@router.post("/password/change")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user password
    
    - **current_password**: Current password for verification
    - **new_password**: New strong password
    - **confirm_password**: Must match new password
    
    Requires email verification. Returns success message.
    """
    auth_service = AuthService(db)
    result = await auth_service.change_password(
        str(current_user.id),
        password_data
    )
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return result


@router.post("/password/reset/request")
async def request_password_reset(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset via email
    
    - **email**: Email address of account to reset
    
    Sends password reset email if account exists.
    Always returns success for security (doesn't reveal if email exists).
    """
    auth_service = AuthService(db)
    
    try:
        reset_token = await auth_service.request_password_reset(reset_data.email)
        
        # TODO: Add background task to send reset email
        # background_tasks.add_task(send_password_reset_email, reset_data.email, reset_token)
        
        logger.info(f"Password reset requested for: {reset_data.email}")
        
    except HTTPException:
        # Always return success for security
        pass
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm password reset with token
    
    - **token**: Password reset token from email
    - **new_password**: New strong password
    - **confirm_password**: Must match new password
    
    Resets password if token is valid. Returns success message.
    """
    auth_service = AuthService(db)
    result = await auth_service.confirm_password_reset(reset_data)
    
    logger.info("Password reset completed successfully")
    
    return result


@router.post("/email/verify")
async def verify_email(
    verification_data: EmailVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email with token
    
    - **token**: Email verification token from registration email
    
    Marks email as verified if token is valid. Returns success message.
    """
    auth_service = AuthService(db)
    result = await auth_service.verify_email(verification_data.token)
    
    logger.info("Email verification completed successfully")
    
    return result


@router.post("/email/resend-verification")
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resend email verification
    
    Generates new verification token and sends verification email.
    Only available for unverified users.
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    from app.core.security import generate_verification_token
    
    auth_service = AuthService(db)
    
    # Update user with new verification token
    current_user.verification_token = generate_verification_token()
    db.add(current_user)
    await db.commit()
    
    # TODO: Add background task to send verification email
    # background_tasks.add_task(send_verification_email, current_user.email, current_user.verification_token)
    
    logger.info(f"Verification email resent to: {current_user.email}")
    
    return {"message": "Verification email sent"}


# Admin endpoints for user management
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    _: Dict[str, Any] = Depends(AuthDependencies.admin_required),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (Admin only)
    
    - **user_id**: Target user ID
    
    Returns user profile data. Requires admin privileges.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        current_level=user.current_level,
        learning_goals=user.learning_goals,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_premium=user.is_premium,
        is_staff=user.is_staff,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    _: Dict[str, Any] = Depends(AuthDependencies.admin_required),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user active status (Admin only)
    
    - **user_id**: Target user ID
    - **is_active**: New active status
    
    Activates or deactivates user account. Requires admin privileges.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = is_active
    db.add(user)
    await db.commit()
    
    action = "activated" if is_active else "deactivated"
    logger.info(f"User {action}: {user.email}")
    
    return {"message": f"User {action} successfully"}


# Token validation endpoint for other services
@router.get("/validate-token")
async def validate_token(
    user_token: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    Validate JWT token
    
    Returns token payload if valid. Used by other services for token validation.
    """
    return {
        "valid": True,
        "user_id": user_token["user_id"],
        "email": user_token["email"],
        "scopes": user_token["scopes"]
    }