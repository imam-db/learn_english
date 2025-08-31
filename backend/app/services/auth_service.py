"""
Authentication service for user management and authentication
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import logging

from app.models.user import User, UserPreference
from app.schemas.auth import (
    UserCreate, UserLogin, UserUpdate, UserPreferencesUpdate,
    PasswordReset, PasswordResetConfirm, ChangePassword
)
from app.core.security import (
    verify_password, get_password_hash, generate_verification_token,
    create_token_response, get_user_roles
)

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and user management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            User data and authentication tokens
            
        Raises:
            HTTPException: If email already exists or registration fails
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            hashed_password = get_password_hash(user_data.password)
            verification_token = generate_verification_token()
            
            new_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                full_name=user_data.full_name,
                current_level=user_data.current_level,
                learning_goals=user_data.learning_goals,
                verification_token=verification_token,
                is_active=True,
                is_verified=False,  # Require email verification
                is_premium=False
            )
            
            self.db.add(new_user)
            await self.db.flush()  # Get the user ID
            
            # Create default user preferences
            user_preferences = UserPreference(
                user_id=new_user.id,
                language_interface="id",
                daily_goal=3,
                reminder_enabled=True,
                reminder_time="19:00",
                offline_content_enabled=False,
                auto_play_audio=True,
                show_translations=True,
                email_notifications=True,
                push_notifications=True
            )
            
            self.db.add(user_preferences)
            await self.db.commit()
            await self.db.refresh(new_user)
            
            # Generate authentication tokens
            user_roles = get_user_roles(
                is_premium=new_user.is_premium,
                is_staff=new_user.is_staff,
                is_admin=new_user.is_admin
            )
            
            tokens = create_token_response(
                user_id=str(new_user.id),
                email=new_user.email,
                scopes=user_roles
            )
            
            logger.info(f"User registered successfully: {new_user.email}")
            
            return {
                "user": {
                    "id": str(new_user.id),
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "current_level": new_user.current_level,
                    "learning_goals": new_user.learning_goals,
                    "is_active": new_user.is_active,
                    "is_verified": new_user.is_verified,
                    "is_premium": new_user.is_premium,
                    "is_staff": new_user.is_staff,
                    "is_admin": new_user.is_admin,
                    "created_at": new_user.created_at,
                    "updated_at": new_user.updated_at
                },
                "tokens": tokens,
                "verification_token": verification_token  # For email verification
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """
        Authenticate user and return tokens
        
        Args:
            login_data: User login credentials
            
        Returns:
            User data and authentication tokens
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Get user by email
            user = await self.get_user_by_email(login_data.email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )
            
            # Generate authentication tokens
            user_roles = get_user_roles(
                is_premium=user.is_premium,
                is_staff=user.is_staff,
                is_admin=user.is_admin
            )
            
            tokens = create_token_response(
                user_id=str(user.id),
                email=user.email,
                scopes=user_roles
            )
            
            logger.info(f"User authenticated successfully: {user.email}")
            
            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "current_level": user.current_level,
                    "learning_goals": user.learning_goals,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "is_premium": user.is_premium,
                    "is_staff": user.is_staff,
                    "is_admin": user.is_admin,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                },
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            update_data: Profile update data
            
        Returns:
            Updated user data
            
        Raises:
            HTTPException: If user not found or update fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields if provided
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"User profile updated: {user.email}")
            
            return {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "current_level": user.current_level,
                "learning_goals": user.learning_goals,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_premium": user.is_premium,
                "is_staff": user.is_staff,
                "is_admin": user.is_admin,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User profile update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profile update failed"
            )
    
    async def update_user_preferences(self, user_id: str, preferences_data: UserPreferencesUpdate) -> Dict[str, Any]:
        """
        Update user preferences
        
        Args:
            user_id: User ID
            preferences_data: Preferences update data
            
        Returns:
            Updated preferences data
            
        Raises:
            HTTPException: If user not found or update fails
        """
        try:
            # Get user preferences
            result = await self.db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            preferences = result.scalar_one_or_none()
            
            if not preferences:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User preferences not found"
                )
            
            # Update fields if provided
            update_dict = preferences_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(preferences, field, value)
            
            preferences.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(preferences)
            
            logger.info(f"User preferences updated for user: {user_id}")
            
            return {
                "user_id": str(preferences.user_id),
                "language_interface": preferences.language_interface,
                "theme": preferences.theme,
                "daily_goal": preferences.daily_goal,
                "reminder_enabled": preferences.reminder_enabled,
                "reminder_time": preferences.reminder_time,
                "offline_content_enabled": preferences.offline_content_enabled,
                "auto_play_audio": preferences.auto_play_audio,
                "show_translations": preferences.show_translations,
                "email_notifications": preferences.email_notifications,
                "push_notifications": preferences.push_notifications,
                "created_at": preferences.created_at,
                "updated_at": preferences.updated_at
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User preferences update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Preferences update failed"
            )
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences
        
        Args:
            user_id: User ID
            
        Returns:
            User preferences data
            
        Raises:
            HTTPException: If preferences not found
        """
        try:
            result = await self.db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            preferences = result.scalar_one_or_none()
            
            if not preferences:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User preferences not found"
                )
            
            return {
                "user_id": str(preferences.user_id),
                "language_interface": preferences.language_interface,
                "theme": preferences.theme,
                "daily_goal": preferences.daily_goal,
                "reminder_enabled": preferences.reminder_enabled,
                "reminder_time": preferences.reminder_time,
                "offline_content_enabled": preferences.offline_content_enabled,
                "auto_play_audio": preferences.auto_play_audio,
                "show_translations": preferences.show_translations,
                "email_notifications": preferences.email_notifications,
                "push_notifications": preferences.push_notifications,
                "created_at": preferences.created_at,
                "updated_at": preferences.updated_at
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get preferences"
            )
    
    async def request_password_reset(self, email: str) -> str:
        """
        Request password reset
        
        Args:
            email: User email
            
        Returns:
            Reset token (for email sending)
            
        Raises:
            HTTPException: If user not found
        """
        try:
            user = await self.get_user_by_email(email)
            if not user:
                # Don't reveal if email exists for security
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="If the email exists, a reset link has been sent"
                )
            
            # Generate reset token
            reset_token = generate_verification_token()
            user.reset_password_token = reset_token
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"Password reset requested for: {email}")
            return reset_token
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Password reset request failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset request failed"
            )
    
    async def confirm_password_reset(self, reset_data: PasswordResetConfirm) -> Dict[str, Any]:
        """
        Confirm password reset with token
        
        Args:
            reset_data: Password reset confirmation data
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If token invalid or reset fails
        """
        try:
            # Find user by reset token
            result = await self.db.execute(
                select(User).where(User.reset_password_token == reset_data.token)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )
            
            # Update password and clear reset token
            user.password_hash = get_password_hash(reset_data.new_password)
            user.reset_password_token = None
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"Password reset completed for: {user.email}")
            
            return {"message": "Password reset successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Password reset confirmation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset failed"
            )
    
    async def change_password(self, user_id: str, password_data: ChangePassword) -> Dict[str, Any]:
        """
        Change user password
        
        Args:
            user_id: User ID
            password_data: Password change data
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If current password wrong or change fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify current password
            if not verify_password(password_data.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Update password
            user.password_hash = get_password_hash(password_data.new_password)
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            
            return {"message": "Password changed successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Password change failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
    
    async def verify_email(self, token: str) -> Dict[str, Any]:
        """
        Verify user email with token
        
        Args:
            token: Email verification token
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If token invalid or verification fails
        """
        try:
            # Find user by verification token
            result = await self.db.execute(
                select(User).where(User.verification_token == token)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification token"
                )
            
            if user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already verified"
                )
            
            # Mark email as verified
            user.is_verified = True
            user.verification_token = None
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"Email verified for user: {user.email}")
            
            return {"message": "Email verified successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Email verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email verification failed"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access and refresh tokens
            
        Raises:
            HTTPException: If refresh token invalid
        """
        try:
            from app.core.security import verify_token
            
            # Verify refresh token
            payload = verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            email = payload.get("email")
            
            if not user_id or not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Get user to check if still active
            user = await self.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Generate new tokens
            user_roles = get_user_roles(
                is_premium=user.is_premium,
                is_staff=user.is_staff,
                is_admin=user.is_admin
            )
            
            tokens = create_token_response(
                user_id=str(user.id),
                email=user.email,
                scopes=user_roles
            )
            
            logger.info(f"Token refreshed for user: {user.email}")
            
            return tokens
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )