"""
Content-related database models (lessons, questions, question sets)
"""

from sqlalchemy import (
    Boolean, Column, String, Text, Integer, 
    ForeignKey, Index, CheckConstraint, Table
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import relationship

from .base import Base


# Association table for many-to-many relationship between lessons and questions
lesson_questions = Table(
    'lesson_questions',
    Base.metadata,
    Column('lesson_id', UUID(as_uuid=True), ForeignKey('lessons.id', ondelete='CASCADE')),
    Column('question_id', UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE')),
    Column('section_order', Integer, nullable=False, default=1),
    Index('idx_lesson_questions_lesson', 'lesson_id'),
    Index('idx_lesson_questions_question', 'question_id'),
)

# Association table for many-to-many relationship between question sets and questions
questionset_questions = Table(
    'questionset_questions',
    Base.metadata,
    Column('question_set_id', UUID(as_uuid=True), ForeignKey('question_sets.id', ondelete='CASCADE')),
    Column('question_id', UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE')),
    Column('order_index', Integer, nullable=False, default=1),
    Index('idx_questionset_questions_set', 'question_set_id'),
    Index('idx_questionset_questions_question', 'question_id'),
)


class Lesson(Base):
    """Lesson model for structured learning content"""
    
    __tablename__ = "lessons"
    
    # Basic information
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Classification
    level = Column(String(10), nullable=False, index=True)
    skill = Column(String(50), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, default=3, nullable=False)
    
    # Content structure (JSONB for flexible lesson sections)
    sections = Column(JSONB, nullable=False)
    
    # Metadata
    estimated_duration = Column(Integer, default=15)  # minutes
    prerequisites = Column(JSONB, default=list)  # List of lesson IDs
    learning_objectives = Column(JSONB, default=list)  # List of objectives
    
    # Content management
    status = Column(String(20), default="draft", nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    published_at = Column(String, nullable=True)
    
    # SEO and search
    search_vector = Column(TSVECTOR)
    tags = Column(JSONB, default=list)
    
    # Statistics
    view_count = Column(Integer, default=0, nullable=False)
    completion_count = Column(Integer, default=0, nullable=False)
    average_rating = Column(Integer, default=0)  # 0-5 scale
    
    # Relationships
    questions = relationship("Question", secondary=lesson_questions, back_populates="lessons")
    progress_records = relationship("LessonProgress", back_populates="lesson")
    
    # Constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "level IN ('A1', 'A2', 'B1', 'B2')",
            name="valid_lesson_level"
        ),
        CheckConstraint(
            "skill IN ('grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking')",
            name="valid_skill_type"
        ),
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 5",
            name="valid_difficulty_range"
        ),
        CheckConstraint(
            "status IN ('draft', 'review', 'published', 'archived')",
            name="valid_lesson_status"
        ),
        CheckConstraint(
            "estimated_duration > 0 AND estimated_duration <= 120",
            name="valid_duration_range"
        ),
        Index("idx_lessons_level_skill", "level", "skill"),
        Index("idx_lessons_topic_difficulty", "topic", "difficulty"),
        Index("idx_lessons_status_published", "status", "published_at"),
        Index("idx_lessons_search", "search_vector", postgresql_using="gin"),
    )


class Question(Base):
    """Question model for practice and assessment"""
    
    __tablename__ = "questions"
    
    # Question content
    stem = Column(Text, nullable=False)  # The question text
    type = Column(String(50), nullable=False, index=True)
    
    # Answer structure (flexible JSONB for different question types)
    options = Column(JSONB)  # For MCQ, matching, etc.
    answer_key = Column(JSONB, nullable=False)  # Correct answer(s)
    explanation = Column(Text)  # Detailed explanation
    
    # Classification
    level = Column(String(10), nullable=False, index=True)
    skill = Column(String(50), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    subtopic = Column(String(100))
    difficulty = Column(Integer, default=3, nullable=False)
    
    # Metadata
    estimated_time = Column(Integer, default=30)  # seconds
    points = Column(Integer, default=1, nullable=False)
    hints = Column(JSONB, default=list)
    
    # Content management
    status = Column(String(20), default="draft", nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # SEO and search
    search_vector = Column(TSVECTOR)
    tags = Column(JSONB, default=list)
    
    # Analytics
    attempt_count = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    average_time = Column(Integer, default=0)  # Average time in seconds
    
    # Relationships
    lessons = relationship("Lesson", secondary=lesson_questions, back_populates="questions")
    question_sets = relationship("QuestionSet", secondary=questionset_questions, back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question")
    srs_cards = relationship("SRSCard", back_populates="question")
    
    # Constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "type IN ('mcq', 'cloze', 'ordering', 'error_detection', 'short_answer', 'matching', 'true_false')",
            name="valid_question_type"
        ),
        CheckConstraint(
            "level IN ('A1', 'A2', 'B1', 'B2')",
            name="valid_question_level"
        ),
        CheckConstraint(
            "skill IN ('grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking')",
            name="valid_question_skill"
        ),
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 5",
            name="valid_question_difficulty"
        ),
        CheckConstraint(
            "status IN ('draft', 'review', 'published', 'archived')",
            name="valid_question_status"
        ),
        CheckConstraint(
            "points > 0 AND points <= 10",
            name="valid_points_range"
        ),
        Index("idx_questions_type_level", "type", "level"),
        Index("idx_questions_skill_topic", "skill", "topic"),
        Index("idx_questions_difficulty_status", "difficulty", "status"),
        Index("idx_questions_search", "search_vector", postgresql_using="gin"),
    )


class QuestionSet(Base):
    """Question set model for custom collections and tryouts"""
    
    __tablename__ = "question_sets"
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Creator and visibility
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_official = Column(Boolean, default=False, nullable=False)
    
    # Configuration
    time_limit = Column(Integer)  # seconds, null for untimed
    shuffle_questions = Column(Boolean, default=False, nullable=False)
    shuffle_options = Column(Boolean, default=False, nullable=False)
    show_feedback = Column(String(20), default="immediate", nullable=False)
    
    # Filtering criteria (for dynamic sets)
    filter_criteria = Column(JSONB)  # Store filter parameters
    is_dynamic = Column(Boolean, default=False, nullable=False)
    
    # Statistics
    usage_count = Column(Integer, default=0, nullable=False)
    average_score = Column(Integer, default=0)  # Percentage
    
    # Relationships
    creator = relationship("User")
    questions = relationship("Question", secondary=questionset_questions, back_populates="question_sets")
    tryout_sessions = relationship("TryoutSession", back_populates="question_set")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "show_feedback IN ('immediate', 'after_question', 'after_completion', 'never')",
            name="valid_feedback_mode"
        ),
        CheckConstraint(
            "time_limit IS NULL OR time_limit > 0",
            name="valid_time_limit"
        ),
        Index("idx_question_sets_creator", "creator_id"),
        Index("idx_question_sets_public_official", "is_public", "is_official"),
    )