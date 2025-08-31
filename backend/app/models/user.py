"""
User-related database models
"""

from sqlalchemy import (
    Boolean, Column, String, Text, Integer, 
    ForeignKey, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=False)
    current_level = Column(String(10), default="A1", nullable=False)
    learning_goals = Column(ARRAY(Text), default=list)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Verification tokens
    verification_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    lesson_progress = relationship("LessonProgress", back_populates="user")
    question_attempts = relationship("QuestionAttempt", back_populates="user")
    srs_cards = relationship("SRSCard", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    tryout_sessions = relationship("TryoutSession", back_populates="user")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "current_level IN ('A1', 'A2', 'B1', 'B2')",
            name="valid_cefr_level"
        ),
        Index("idx_users_email_active", "email", "is_active"),
        Index("idx_users_level", "current_level"),
    )


class UserPreference(Base):
    """User preferences and settings"""
    
    __tablename__ = "user_preferences"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    
    # Interface preferences
    language_interface = Column(String(10), default="id", nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    
    # Learning preferences
    daily_goal = Column(Integer, default=3, nullable=False)
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    reminder_time = Column(String(5), default="19:00", nullable=False)  # HH:MM format
    
    # Content preferences
    offline_content_enabled = Column(Boolean, default=False, nullable=False)
    auto_play_audio = Column(Boolean, default=True, nullable=False)
    show_translations = Column(Boolean, default=True, nullable=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="preferences")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "language_interface IN ('id', 'en')",
            name="valid_interface_language"
        ),
        CheckConstraint(
            "theme IN ('light', 'dark', 'auto')",
            name="valid_theme"
        ),
        CheckConstraint(
            "daily_goal > 0 AND daily_goal <= 50",
            name="valid_daily_goal"
        ),
    )