"""
Authentication-related Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    current_level: str = Field(default="A1", pattern="^(A1|A2|B1|B2)$")
    learning_goals: List[str] = Field(default_factory=list)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)"""
    id: str
    is_active: bool
    is_verified: bool
    is_premium: bool
    is_staff: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    current_level: Optional[str] = Field(None, pattern="^(A1|A2|B1|B2)$")
    learning_goals: Optional[List[str]] = None


class UserPreferencesBase(BaseModel):
    """Base user preferences schema"""
    language_interface: str = Field(default="id", pattern="^(id|en)$")
    theme: str = Field(default="light", pattern="^(light|dark|auto)$")
    daily_goal: int = Field(default=3, ge=1, le=50)
    reminder_enabled: bool = True
    reminder_time: str = Field(default="19:00", pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    offline_content_enabled: bool = False
    auto_play_audio: bool = True
    show_translations: bool = True
    email_notifications: bool = True
    push_notifications: bool = True


class UserPreferencesUpdate(UserPreferencesBase):
    """Schema for updating user preferences"""
    language_interface: Optional[str] = Field(None, pattern="^(id|en)$")
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    daily_goal: Optional[int] = Field(None, ge=1, le=50)
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    offline_content_enabled: Optional[bool] = None
    auto_play_audio: Optional[bool] = None
    show_translations: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response"""
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    scopes: List[str] = []


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., min_length=1)


class ChangePassword(BaseModel):
    """Schema for changing password"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v