"""
Database models for English Learning Platform
"""

# Import all models to ensure they are registered with SQLAlchemy
from .base import Base
from .user import User, UserPreference
from .content import Lesson, Question, QuestionSet
from .progress import LessonProgress, QuestionAttempt, UserAchievement
from .srs import SRSCard
from .assessment import TryoutSession, TryoutAnswer
from .subscription import Subscription, PaymentTransaction

__all__ = [
    "Base",
    "User",
    "UserPreference", 
    "Lesson",
    "Question",
    "QuestionSet",
    "LessonProgress",
    "QuestionAttempt",
    "UserAchievement",
    "SRSCard",
    "TryoutSession",
    "TryoutAnswer",
    "Subscription",
    "PaymentTransaction",
]