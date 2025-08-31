"""
Spaced Repetition System (SRS) models
"""

from sqlalchemy import (
    Boolean, Column, String, Integer, 
    ForeignKey, Index, CheckConstraint,
    Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class SRSCard(Base):
    """SRS card for spaced repetition learning"""
    
    __tablename__ = "srs_cards"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Item being learned (can be question, vocabulary, grammar rule, etc.)
    item_type = Column(String(50), nullable=False)
    item_id = Column(UUID(as_uuid=True), nullable=False)  # Generic reference
    
    # For questions specifically
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True
    )
    
    # SRS Algorithm parameters (Modified SM-2)
    interval = Column(Integer, default=1, nullable=False)  # Days until next review
    ease_factor = Column(Numeric(4, 2), default=2.5, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)
    
    # Scheduling
    next_review_date = Column(String, nullable=False)  # ISO date string
    last_reviewed_date = Column(String, nullable=True)
    
    # Performance tracking
    total_reviews = Column(Integer, default=0, nullable=False)
    correct_reviews = Column(Integer, default=0, nullable=False)
    consecutive_correct = Column(Integer, default=0, nullable=False)
    
    # Card state
    is_learning = Column(Boolean, default=True, nullable=False)  # New card vs review card
    is_suspended = Column(Boolean, default=False, nullable=False)
    is_buried = Column(Boolean, default=False, nullable=False)  # Temporarily hidden
    
    # Metadata
    card_data = Column(JSONB, default=dict)  # Additional card-specific data
    tags = Column(JSONB, default=list)
    
    # Performance metrics
    average_response_time = Column(Integer, default=0)  # milliseconds
    difficulty_rating = Column(Numeric(3, 2), default=0)  # 0-5 scale
    
    # Relationships
    user = relationship("User", back_populates="srs_cards")
    question = relationship("Question", back_populates="srs_cards")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "item_type IN ('question', 'vocabulary', 'grammar_rule', 'phrase', 'concept')",
            name="valid_srs_item_type"
        ),
        CheckConstraint(
            "interval > 0",
            name="valid_srs_interval"
        ),
        CheckConstraint(
            "ease_factor >= 1.3 AND ease_factor <= 5.0",
            name="valid_ease_factor"
        ),
        CheckConstraint(
            "repetitions >= 0",
            name="valid_repetitions"
        ),
        CheckConstraint(
            "correct_reviews <= total_reviews",
            name="valid_correct_reviews"
        ),
        CheckConstraint(
            "consecutive_correct >= 0",
            name="valid_consecutive_correct"
        ),
        CheckConstraint(
            "difficulty_rating >= 0 AND difficulty_rating <= 5",
            name="valid_difficulty_rating"
        ),
        Index("idx_srs_cards_user", "user_id"),
        Index("idx_srs_cards_item", "item_type", "item_id"),
        Index("idx_srs_cards_question", "question_id"),
        Index("idx_srs_cards_due", "user_id", "next_review_date"),
        Index("idx_srs_cards_learning", "user_id", "is_learning"),
        Index("idx_srs_cards_suspended", "user_id", "is_suspended"),
    )