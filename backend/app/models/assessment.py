"""
Assessment and tryout session models
"""

from sqlalchemy import (
    Boolean, Column, String, Text, Integer, 
    ForeignKey, Index, CheckConstraint,
    Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class TryoutSession(Base):
    """Tryout session for timed assessments and practice"""
    
    __tablename__ = "tryout_sessions"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    question_set_id = Column(
        UUID(as_uuid=True),
        ForeignKey("question_sets.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Session configuration
    title = Column(String(255), nullable=False)
    time_limit = Column(Integer, nullable=True)  # seconds, null for untimed
    total_questions = Column(Integer, nullable=False)
    
    # Session state
    status = Column(String(20), default="not_started", nullable=False)
    current_question_index = Column(Integer, default=0, nullable=False)
    
    # Timing
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    time_elapsed = Column(Integer, default=0, nullable=False)  # seconds
    time_remaining = Column(Integer, nullable=True)  # seconds
    
    # Results
    questions_answered = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    total_points = Column(Integer, default=0, nullable=False)
    max_possible_points = Column(Integer, nullable=False)
    
    # Performance metrics
    accuracy_percentage = Column(Numeric(5, 2), default=0, nullable=False)
    average_time_per_question = Column(Integer, default=0)  # seconds
    
    # Configuration
    shuffle_questions = Column(Boolean, default=False, nullable=False)
    shuffle_options = Column(Boolean, default=False, nullable=False)
    show_feedback = Column(String(20), default="after_completion", nullable=False)
    
    # Session data
    question_order = Column(JSONB, nullable=False)  # Array of question IDs in order
    session_data = Column(JSONB, default=dict)  # Additional session metadata
    
    # Relationships
    user = relationship("User", back_populates="tryout_sessions")
    question_set = relationship("QuestionSet", back_populates="tryout_sessions")
    answers = relationship("TryoutAnswer", back_populates="session", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'paused', 'completed', 'abandoned')",
            name="valid_session_status"
        ),
        CheckConstraint(
            "show_feedback IN ('immediate', 'after_question', 'after_completion', 'never')",
            name="valid_feedback_mode"
        ),
        CheckConstraint(
            "current_question_index >= 0 AND current_question_index <= total_questions",
            name="valid_question_index"
        ),
        CheckConstraint(
            "questions_answered >= 0 AND questions_answered <= total_questions",
            name="valid_questions_answered"
        ),
        CheckConstraint(
            "correct_answers >= 0 AND correct_answers <= questions_answered",
            name="valid_correct_answers"
        ),
        CheckConstraint(
            "accuracy_percentage >= 0 AND accuracy_percentage <= 100",
            name="valid_accuracy_percentage"
        ),
        Index("idx_tryout_sessions_user", "user_id"),
        Index("idx_tryout_sessions_question_set", "question_set_id"),
        Index("idx_tryout_sessions_status", "user_id", "status"),
        Index("idx_tryout_sessions_completed", "user_id", "completed_at"),
    )


class TryoutAnswer(Base):
    """Individual answers within a tryout session"""
    
    __tablename__ = "tryout_answers"
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tryout_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Answer details
    user_answer = Column(JSONB, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    points_earned = Column(Integer, default=0, nullable=False)
    max_points = Column(Integer, default=1, nullable=False)
    
    # Timing
    time_taken = Column(Integer, nullable=False)  # seconds
    answered_at = Column(String, nullable=False)
    
    # Question context
    question_index = Column(Integer, nullable=False)  # Position in the tryout
    
    # Feedback
    feedback_shown = Column(Boolean, default=False, nullable=False)
    explanation_viewed = Column(Boolean, default=False, nullable=False)
    
    # Flags
    is_flagged = Column(Boolean, default=False, nullable=False)  # User marked for review
    is_skipped = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    session = relationship("TryoutSession", back_populates="answers")
    question = relationship("Question")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "question_index >= 0",
            name="valid_question_index"
        ),
        CheckConstraint(
            "time_taken > 0",
            name="valid_time_taken"
        ),
        CheckConstraint(
            "points_earned >= 0 AND points_earned <= max_points",
            name="valid_points_earned"
        ),
        Index("idx_tryout_answers_session", "session_id"),
        Index("idx_tryout_answers_question", "question_id"),
        Index("idx_tryout_answers_session_index", "session_id", "question_index"),
    )