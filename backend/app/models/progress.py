"""
Progress tracking and achievement models
"""

from sqlalchemy import (
    Boolean, Column, String, Text, Integer, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint,
    Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class LessonProgress(Base):
    """Track user progress through lessons"""
    
    __tablename__ = "lesson_progress"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Progress tracking
    sections_completed = Column(Integer, default=0, nullable=False)
    total_sections = Column(Integer, nullable=False)
    completion_percentage = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Time tracking
    time_spent = Column(Integer, default=0, nullable=False)  # seconds
    first_started_at = Column(String, nullable=True)
    last_accessed_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    
    # Performance metrics
    questions_attempted = Column(Integer, default=0, nullable=False)
    questions_correct = Column(Integer, default=0, nullable=False)
    accuracy_rate = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Section-specific progress (JSONB for flexibility)
    section_progress = Column(JSONB, default=dict)
    
    # Status
    is_completed = Column(Boolean, default=False, nullable=False)
    is_bookmarked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress_records")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="unique_user_lesson_progress"),
        CheckConstraint(
            "completion_percentage >= 0 AND completion_percentage <= 100",
            name="valid_completion_percentage"
        ),
        CheckConstraint(
            "accuracy_rate >= 0 AND accuracy_rate <= 100",
            name="valid_accuracy_rate"
        ),
        CheckConstraint(
            "sections_completed >= 0 AND sections_completed <= total_sections",
            name="valid_sections_completed"
        ),
        CheckConstraint(
            "questions_correct <= questions_attempted",
            name="valid_questions_correct"
        ),
        Index("idx_lesson_progress_user", "user_id"),
        Index("idx_lesson_progress_lesson", "lesson_id"),
        Index("idx_lesson_progress_completion", "user_id", "completion_percentage"),
        Index("idx_lesson_progress_bookmarked", "user_id", "is_bookmarked"),
    )


class QuestionAttempt(Base):
    """Track individual question attempts and performance"""
    
    __tablename__ = "question_attempts"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Attempt details
    user_answer = Column(JSONB, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=False)  # seconds
    attempt_number = Column(Integer, default=1, nullable=False)
    
    # Context
    context_type = Column(String(50))  # 'lesson', 'practice', 'tryout', 'srs'
    context_id = Column(UUID(as_uuid=True))  # ID of lesson, tryout session, etc.
    
    # Scoring
    points_earned = Column(Integer, default=0, nullable=False)
    max_points = Column(Integer, default=1, nullable=False)
    
    # Feedback
    hint_used = Column(Boolean, default=False, nullable=False)
    explanation_viewed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="question_attempts")
    question = relationship("Question", back_populates="attempts")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "context_type IN ('lesson', 'practice', 'tryout', 'srs', 'assessment')",
            name="valid_context_type"
        ),
        CheckConstraint(
            "attempt_number > 0",
            name="valid_attempt_number"
        ),
        CheckConstraint(
            "time_taken > 0",
            name="valid_time_taken"
        ),
        CheckConstraint(
            "points_earned >= 0 AND points_earned <= max_points",
            name="valid_points_earned"
        ),
        Index("idx_question_attempts_user", "user_id"),
        Index("idx_question_attempts_question", "question_id"),
        Index("idx_question_attempts_context", "context_type", "context_id"),
        Index("idx_question_attempts_user_question", "user_id", "question_id"),
        Index("idx_question_attempts_performance", "user_id", "is_correct", "created_at"),
    )


class UserAchievement(Base):
    """Track user achievements and badges"""
    
    __tablename__ = "user_achievements"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Achievement details
    achievement_type = Column(String(50), nullable=False)
    achievement_key = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Progress tracking
    current_progress = Column(Integer, default=0, nullable=False)
    target_progress = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    category = Column(String(50), nullable=False)
    difficulty = Column(String(20), default="bronze", nullable=False)
    points_reward = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    earned_at = Column(String, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="achievements")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_key", name="unique_user_achievement"),
        CheckConstraint(
            "achievement_type IN ('streak', 'completion', 'accuracy', 'speed', 'milestone', 'special')",
            name="valid_achievement_type"
        ),
        CheckConstraint(
            "category IN ('learning', 'social', 'progress', 'mastery', 'engagement')",
            name="valid_achievement_category"
        ),
        CheckConstraint(
            "difficulty IN ('bronze', 'silver', 'gold', 'platinum')",
            name="valid_achievement_difficulty"
        ),
        CheckConstraint(
            "current_progress >= 0 AND current_progress <= target_progress",
            name="valid_achievement_progress"
        ),
        Index("idx_user_achievements_user", "user_id"),
        Index("idx_user_achievements_type", "achievement_type"),
        Index("idx_user_achievements_completed", "user_id", "is_completed"),
    )