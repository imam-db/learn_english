"""
Database initialization script
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from .config import settings
from .database import engine, AsyncSessionLocal
from .database_utils import DatabaseUtils
from ..models.base import Base

logger = logging.getLogger(__name__)


async def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_url_parts = settings.DATABASE_URL.split('/')
    db_name = db_url_parts[-1]
    
    # Connect to postgres database to create our target database
    postgres_url = '/'.join(db_url_parts[:-1]) + '/postgres'
    postgres_engine = create_async_engine(
        postgres_url.replace("postgresql://", "postgresql+asyncpg://"),
        isolation_level="AUTOCOMMIT"
    )
    
    try:
        async with postgres_engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            
            if not result.fetchone():
                # Create database
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
                
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise
    finally:
        await postgres_engine.dispose()


async def create_tables():
    """Create all tables using SQLAlchemy metadata"""
    try:
        # Import all models to ensure they're registered
        from ..models import (
            User, UserPreference, Lesson, Question, QuestionSet,
            LessonProgress, QuestionAttempt, UserAchievement,
            SRSCard, TryoutSession, TryoutAnswer,
            Subscription, PaymentTransaction
        )
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All tables created successfully")
            
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


async def create_extensions():
    """Create required PostgreSQL extensions"""
    try:
        async with AsyncSessionLocal() as session:
            # Create UUID extension
            await session.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            
            # Create full-text search extension
            await session.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
            
            # Create unaccent extension for better search
            await session.execute(text('CREATE EXTENSION IF NOT EXISTS "unaccent"'))
            
            await session.commit()
            logger.info("PostgreSQL extensions created successfully")
            
    except Exception as e:
        logger.error(f"Failed to create extensions: {e}")
        raise


async def create_performance_indexes():
    """Create performance indexes"""
    try:
        async with AsyncSessionLocal() as session:
            await DatabaseUtils.create_indexes_if_not_exist(session)
            logger.info("Performance indexes created successfully")
            
    except Exception as e:
        logger.error(f"Failed to create performance indexes: {e}")
        raise


async def seed_initial_data():
    """Seed initial data for development"""
    try:
        async with AsyncSessionLocal() as session:
            from ..models.user import User, UserPreference
            from ..models.content import Lesson, Question
            import uuid
            from datetime import datetime
            
            # Check if we already have data
            existing_users = await session.execute(text("SELECT COUNT(*) FROM users"))
            if existing_users.scalar() > 0:
                logger.info("Database already has data, skipping seed")
                return
            
            # Create admin user
            admin_user = User(
                id=uuid.uuid4(),
                email="admin@englishlearning.com",
                password_hash="$2b$12$dummy_hash_for_development",  # Change in production
                full_name="Admin User",
                current_level="B2",
                is_active=True,
                is_verified=True,
                is_premium=True
            )
            session.add(admin_user)
            await session.flush()
            
            # Create admin preferences
            admin_prefs = UserPreference(
                user_id=admin_user.id,
                language_interface="en",
                daily_goal=10,
                reminder_enabled=True
            )
            session.add(admin_prefs)
            
            # Create sample lesson
            sample_lesson = Lesson(
                id=uuid.uuid4(),
                title="Simple Present Tense",
                slug="simple-present-tense",
                description="Learn the basics of simple present tense in English",
                level="A1",
                skill="grammar",
                topic="tenses",
                difficulty=2,
                sections={
                    "concept": {
                        "heading": "Simple Present Tense",
                        "content": {
                            "en": "The simple present tense is used for habits, facts, and general truths.",
                            "id": "Simple present tense digunakan untuk kebiasaan, fakta, dan kebenaran umum."
                        },
                        "examples": [
                            {
                                "en": "I eat breakfast every morning.",
                                "id": "Saya sarapan setiap pagi."
                            }
                        ]
                    }
                },
                status="published",
                author_id=admin_user.id,
                estimated_duration=15,
                view_count=0,
                completion_count=0
            )
            session.add(sample_lesson)
            await session.flush()
            
            # Create sample question
            sample_question = Question(
                id=uuid.uuid4(),
                stem="Choose the correct form: She _____ to school every day.",
                type="mcq",
                options={
                    "A": {"text": "go", "explanation": {"en": "Incorrect: Use 'goes' for third person singular", "id": "Salah: Gunakan 'goes' untuk orang ketiga tunggal"}},
                    "B": {"text": "goes", "explanation": {"en": "Correct: Third person singular form", "id": "Benar: Bentuk orang ketiga tunggal"}},
                    "C": {"text": "going", "explanation": {"en": "Incorrect: This is present continuous form", "id": "Salah: Ini bentuk present continuous"}},
                    "D": {"text": "gone", "explanation": {"en": "Incorrect: This is past participle", "id": "Salah: Ini bentuk past participle"}}
                },
                answer_key=["B"],
                explanation="In simple present tense, we add 's' or 'es' to the verb for third person singular subjects (he, she, it).",
                level="A1",
                skill="grammar",
                topic="tenses",
                difficulty=2,
                estimated_time=30,
                points=1,
                status="published",
                author_id=admin_user.id,
                attempt_count=0,
                correct_count=0
            )
            session.add(sample_question)
            
            await session.commit()
            logger.info("Initial seed data created successfully")
            
    except Exception as e:
        logger.error(f"Failed to seed initial data: {e}")
        raise


async def init_database():
    """Initialize the complete database setup"""
    logger.info("Starting database initialization...")
    
    try:
        # Step 1: Create database if it doesn't exist
        await create_database_if_not_exists()
        
        # Step 2: Create PostgreSQL extensions
        await create_extensions()
        
        # Step 3: Create tables (this will be done via Alembic in production)
        if settings.ENVIRONMENT == "development":
            await create_tables()
        
        # Step 4: Create performance indexes
        await create_performance_indexes()
        
        # Step 5: Seed initial data (development only)
        if settings.ENVIRONMENT == "development":
            await seed_initial_data()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def reset_database():
    """Reset database (development only)"""
    if settings.ENVIRONMENT != "development":
        raise ValueError("Database reset is only allowed in development environment")
    
    logger.warning("Resetting database - all data will be lost!")
    
    try:
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("All tables dropped")
            
        # Recreate everything
        await init_database()
        logger.info("Database reset completed")
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise


if __name__ == "__main__":
    # Run database initialization
    asyncio.run(init_database())